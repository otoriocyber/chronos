import datetime
from parsers.parser_base import ParserBase


class MPLog(ParserBase):
    def __init__(self, config):
        super().__init__(config)

    @staticmethod
    def __get_data(path):
        with open(path, "r", encoding="utf16") as f:
            data = f.read()
            return data

    @staticmethod
    def __split_to_chunks(data):
        return data.split("\n\n")

    @staticmethod
    def __get_detection_details(event):
        details = {}
        detected = False
        s_event = event.splitlines()
        for line in s_event:
            if detected:
                if ":" in line:
                    try:
                        parts = line.split(":")
                        key = parts[0].lower().replace(" ", "_")
                        value = ":".join(parts[1:])
                        details[key] = value
                    except:
                        pass
            if "Begin Resource Scan" in line:
                detected = True

        details["event"] = "detection"
        return details

    def __detection_event(self, event):
        detection = None
        s_event = event.splitlines()
        for line in s_event:
            if "DETECTIONEVENT" in line:
                detection = line
                break
        assert detection, "DETECTIONEVENT event expected but not found"
        scan_time = detection.split()[0]
        detection_type = detection.split()[2]
        detection_details = self.__get_detection_details(event)
        detection_details["time"] = datetime.datetime.strptime(scan_time[:-5], "%Y-%m-%dt%H:%M:%S").isoformat()
        detection_details["Type"] = detection_type
        return detection_details

    # EMS scan for process:
    @staticmethod
    def __ems_scan(event):
        lines = event.splitlines()
        for line in lines:
            if "EMS scan for process" in line:
                s_events = line.split(",")
                scan = {"time": datetime.datetime.strptime(line.split()[0][:-5], "%Y-%m-%dt%H:%M:%S").isoformat(),
                        "process_name": line[line.index("process"):line.index("pid")].split()[-1],
                        "pid": line[line.index("pid"):line.index("sigseq")].split()[-1].strip(",")
                        }
                for field in s_events[1:]:
                    vals = field.split(":")
                    key = vals[0].lower().replace(" ", "_")
                    value = ":".join(vals[1:])
                    scan[key] = value
                scan["event"] = "ems_scan"
                return scan

    # ProcessImageName
    @staticmethod
    def __process_image(event):
        for line in event.splitlines():
            if line and str.isdigit(line[:-4]):
                fields = line.lower().split(",")
                first = fields[0].split()
                scan = {"time": datetime.datetime.strptime(first[0][:-5], "%Y-%m-%dt%H:%M:%S").isoformat(),
                        " ".join(first[1:]).split(":")[0].strip(): " ".join(first[1:]).split(":")[1].strip()}
                for field in fields[1:]:
                    vals = field.split(":")
                    key = vals[0].strip().lower().replace(" ", "_")
                    value = ":".join(vals[1:]).strip()
                    scan[key] = value
                scan["event"] = "process_image"

                return scan

    def __event_filter(self, event):
        if "DETECTIONEVENT" in event:
            return self.__detection_event(event)
        elif "EMS scan for process:" in event:
            return self.__ems_scan(event)
        elif "ProcessImageName" in event:
            return self.__process_image(event)
        else:
            return {}

    def parse(self, path):
        results = []
        data = self.__get_data(path)
        chunks = self.__split_to_chunks(data)
        for chunk in chunks:
            try:
                result = self.__event_filter(chunk)
                if result:
                    results.append(result)
            except:
                # Some unexpected problem during the parsing
                continue

        self._write_results_tuple(("defender", results))
        return results
