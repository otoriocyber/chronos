import csv
import datetime
import random
import os
from parsers.parser_base import ParserBase

FILE_TIME_EPOCH = datetime.datetime(1601, 1, 1)
FILE_TIME_MICROSECOND = 10


def filetime_to_epoch_datetime(file_time):
    if isinstance(file_time, int):
        microseconds_since_file_time_epoch = file_time / FILE_TIME_MICROSECOND
    else:
        microseconds_since_file_time_epoch = int(file_time) / FILE_TIME_MICROSECOND
    return FILE_TIME_EPOCH + datetime.timedelta(microseconds=microseconds_since_file_time_epoch)


class SrumParser(ParserBase):
    CSV_FIELDS = {
        "Unknown1.csv": ["TimeStamp", "AppId", "UserId", "EndTime", "DurationMS"],
        "Unknown2.csv": [],
        "Unknown3.csv": [],
        "Unknown4.csv": ["TimeStamp", "AppId", "UserId"],
        "SruDbCheckpointTable.csv": [],
        "SruDbIdMapTable.csv": [],
        "Network Usage.csv": ["TimeStamp", "AppId", "UserId", "InterfaceLuid", "L2ProfileId", "BytesSent",
                              "BytesRecvd"],
        "Network Connections.csv": [],
        "Energy Usage.csv": [],
        "Energy Usage(Long - Term).csv": [],
        "Application Resources.csv": ["TimeStamp", "AppId", "UserId"],
        "Application Resource Usage.csv": ["TimeStamp", "AppId", "UserId"]
    }

    PARSING_TOOL = r"Tools\ese-analyst-master\ese2csv.exe"
    PARSE_COMMAND = "{parser_path} -o {output_path} -p srudb_plugin {srum_db} --plugin-args {software_hive}"

    def __init__(self, temp, config):
        super().__init__(config)
        self.temp_result_path = temp

    def parse(self, args):
        srum_db, software_hive = args
        output = r"{}\srum_{}".format(self.temp_result_path, random.randint(1, 1000000))
        os.mkdir(output)
        command = self.PARSE_COMMAND.format(parser_path=self.PARSING_TOOL, output_path=output, srum_db=srum_db,
                                            software_hive=software_hive)
        self._run_command(command)

        for csv_file in os.listdir(output):
            srum_records = []
            full_path = os.path.join(output, csv_file)
            headers = self.CSV_FIELDS.get(csv_file)
            if not headers:
                continue

            if csv_file == "Unknown1.csv":
                with open(full_path, "r") as f:
                    reader = csv.DictReader(f)
                    for line in reader:
                        cur_record = {}
                        endTime = line.get("EndTime")
                        duration = line.get("DurationMS")
                        if endTime and duration:
                            cur_record["time"] = filetime_to_epoch_datetime(int(endTime) - int(duration)).isoformat()
                            cur_record["EndTime"] = filetime_to_epoch_datetime(endTime).isoformat()
                            cur_record["DurationMS"] = duration
                        else:
                            cur_record["time"] = datetime.datetime(1970, 1, 1).isoformat()
                        cur_record["AppId"] = line.get("AppId")
                        cur_record["UserId"] = line.get("UserId")
                        srum_records.append(cur_record)


            else:
                with open(full_path, "r") as f:
                    reader = csv.DictReader(f)
                    for line in reader:
                        cur_record = {}
                        for header in headers:
                            if header == "TimeStamp":
                                cur_record["time"] = line.get("TimeStamp").replace(" ", "T")
                                line.pop("TimeStamp")
                            value = line.get(header)
                            if value:
                                if isinstance(value, bytes):
                                    cur_record[header.lower().replace(" ", "_")] = value.decode()
                                elif str.isdigit(value):
                                    cur_record[header.lower().replace(" ", "_")] = int(value)
                                else:
                                    cur_record[header.lower().replace(" ", "_")] = value
                            else:
                                cur_record[header.lower().replace(" ", "_")] = ""
                        srum_records.append(cur_record)

            self._write_results_list([("srum-{}".format(csv_file.split(".")[0].lower().replace(" ", "_")), srum_records)])
