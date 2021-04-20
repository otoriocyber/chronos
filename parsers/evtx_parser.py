import os
import json
import random
from parsers.parser_base import ParserBase


class EvtxRustJson(ParserBase):
    PARSING_TOOL = r"Tools\evtx_dump.exe\evtx_dump.exe"
    OUTPUT = "evtx_output.json_" + str(random.random())
    COMMAND_LINE_CONFIGS = " -o jsonl -f "

    def __init__(self, temp, config):
        super().__init__(config)
        self.TempDir = temp

    @staticmethod
    def __parse_powershell_log(data):
        data_vals = {}
        for dataitem in data["#text"]:
            try:
                if len(dataitem) > 20:
                    split_data = dataitem.split("\r\n\t")
                    for dat in split_data:
                        dat = dat.strip("\t").strip("\r\n")
                        if len(dat) < 50:
                            dat = dat.split("=")
                        if len(dat) == 2:
                            if isinstance(dat[1], str):
                                data_vals[dat[0]] = dat[1]
                            elif dat[1] == 1 | dat[1] == 0:
                                data_vals[dat[0]] = json.dumps(bool(dat[1]))
                            else:
                                data_vals[dat[0]] = json.dumps(str(dat[1]))
                        else:
                            data_vals[dat.split("=")[0]] = ' '.join(dat.replace("\n", "").split()).split("=", 1)[1]
                else:
                    data_vals[dataitem] = json.dumps(True)

            except:
                # Couldn't parse this part as expected
                pass

        return data_vals

    @staticmethod
    def __get_event_id(log_line):
        event_id = log_line.get("Event").get("System").get("EventID")
        if isinstance(event_id, int):
            event_id = str(event_id)
        elif isinstance(event_id, dict):
            event_id = str(event_id.get("#text"))
        else:
            event_id = log_line["Event"]["System"]["EventID"]

        return event_id

    def __parse_data(self, log_line):
        data = log_line.get("Event").get("EventData").get("Data")
        if isinstance(data, list):
            data_vals = {}
            for dataitem in data:
                try:
                    name = dataitem.get("@Name", None)
                    if name is not None:
                        text = dataitem.get("#text", None)
                        if text is not None:
                            data_vals[str(name)] = str(text)
                except:
                    # Couldn't parse this part as expected
                    pass

            log_line["Event"]["EventData"]["Data"] = data_vals
        elif isinstance(data, dict):
            if '#text' in data.keys():
                log_line["Event"]["EventData"]["RawData"] = json.dumps(data['#text'])
                if isinstance(data["#text"], list):
                    if log_line["Event"]["System"]["Channel"] == "Windows PowerShell":
                        data_vals = self.__parse_powershell_log(data)
                        log_line["Event"]["EventData"]["Data"] = data_vals
            else:
                log_line["Event"]["EventData"]["RawData"] = json.dumps(data)
        else:
            log_line["Event"]["EventData"]["RawData"] = json.dumps(data)
            del log_line["Event"]["EventData"]["Data"]

    def parse(self, path):
        rows = []
        output = os.path.join(self.TempDir, self.OUTPUT + "_" + os.path.split(path)[-1].replace(" ", "_").replace("-", "_"))
        command = self.PARSING_TOOL + " \"" + path + "\"" + self.COMMAND_LINE_CONFIGS + output + " --no-confirm-overwrite"
        self._run_command(command)
        log_line = {}
        try:
            with open(output, "r", encoding="utf-8-sig") as json_file:
                for line in json_file:
                    log_line = json.loads(line)
                    date = log_line.get("Event").get("System").get("TimeCreated").get("#attributes").get("SystemTime")
                    date = date.replace(" ", "T")
                    log_line['time'] = date
                    log_line["Event"]["System"]["TimeCreated"]["time"] = date

                    if log_line.get("Event") is not None:
                        data = log_line.get("Event")
                        log_line["Event"]["System"]["EventID"] = self.__get_event_id(log_line)
                        if log_line.get("Event").get("EventData") is not None:
                            data = log_line.get("Event").get("EventData")
                            if log_line.get("Event").get("EventData").get("Data") is not None:
                                self.__parse_data(log_line)
                            else:
                                if isinstance(data, dict):
                                    data_vals = {}
                                    for k,v in data.items():
                                        if isinstance(v, bool):
                                            data_vals[k] = json.dumps(v)
                                        elif isinstance(v, str):
                                            data_vals[k] = v
                                        else:
                                            data_vals[k] = str(v)
                                    log_line["Event"]["RawData"] = json.dumps(data)
                                else:
                                    log_line["Event"]["RawData"] = json.dumps(data)
                                del log_line["Event"]["EventData"]
                                log_line['Event']['System']['Data'] = data_vals
                        else:
                            if isinstance(data, dict):
                                log_line['Event'] = dict(data)
                                log_line['time'] = date
                            else:
                                log_line["RawData"] = json.dumps(data)
                                del log_line["Event"]
                    else:
                        pass

                    rows.append(log_line)
        except Exception as e:
            self.log("{parser}: Some error during evtx parsing - {error}".format(parser="EvtxParser", error=e))

        os.remove(output)

        if log_line:
            self._write_results_list([("evtx-{}".format(log_line["Event"]["System"]["Channel"].replace("/", "-")), rows)])
        else:
            self._write_results_list([("evtx-{}".format(os.path.split(path)[-1].split(".")[0]), [])])
