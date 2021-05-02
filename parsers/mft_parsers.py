import os
import csv
from parsers.parser_base import ParserBase


class MFTParser(ParserBase):
    PARSING_TOOL = r"Tools\MFTECmd.exe"
    TEMP_RESULT_NAME = r"mft.csv"
    PARSE_COMMAND = "{parser_path} -f \"{mft_file}\" --csv {output_dir} --csvf {output_filename}"

    TIME_FIELDS = ['Created0x10', 'Created0x30', 'LastModified0x10', 'LastModified0x30', 'LastRecordChange0x10',
                   'LastRecordChange0x30', 'LastAccess0x10', 'LastAccess0x30']

    def __init__(self, temp, config):
        super().__init__(config)
        self.temp_result_path = temp

    @staticmethod
    def get_time_type(field_name):
        time_type = ""
        time_attr, time_kind = field_name.split("0x")
        if time_kind == "10":
            time_type += "si"
        elif time_kind == "30":
            time_type += "fn"

        if time_attr == "Created":
            time_type += "CreateTime"
        elif time_attr == "LastModified":
            time_type += "ModTime"
        elif time_attr == "LastRecordChange":
            time_type += "MFTModTime"
        elif time_attr == "LastAccess":
            time_type += "AccessTime"

        return time_type

    def parse(self, mft_path):
        filename = self.TEMP_RESULT_NAME + "_" + mft_path.replace("\\", "_").replace(":", "").replace(" ", "_")
        command = self.PARSE_COMMAND.format(parser_path=self.PARSING_TOOL, mft_file=mft_path,
                                            output_dir=self.temp_result_path, output_filename=filename)
        self._run_command(command)

        fp = os.path.join(self.temp_result_path, filename)

        json_rows = []
        try:
            with open(fp, "r", encoding='utf-8-sig') as csv_file:
                reader = csv.DictReader((line.replace('\0', '') for line in csv_file))
                for line in reader:
                    for i in self.TIME_FIELDS:
                        json_row = {}
                        try:
                            if line[i]:
                                json_row["time"] = line[i].replace(" ", "T")
                            else:
                                continue
                        except Exception as e:
                            self.log("{parser}: Unexpected exception occurred {exception}, at field - {field}".format(
                                parser="MFTParser",
                                exception=e,
                                field=i))
                            continue
                        json_row["Type"] = self.get_time_type(i)

                        for key in line:
                            used_key = key
                            if key in self.TIME_FIELDS:
                                continue
                            value = line.get(key)
                            if value.lower() == "true":
                                value = True
                            elif value.lower() == "false":
                                value = False
                            if "<" in key:
                                used_key = key.replace("<", "_smaller_than_")

                            json_row[used_key] = value

                        json_rows.append(json_row)

                        if len(json_rows) > 5000:
                            self._write_results_tuple(("mft", json_rows))
                            json_rows = []

        except Exception as e:
            self.log("Some critical exception occurred with the mft - {exception}".format(exception=e))

        if json_rows:
            self._write_results_tuple(("mft", json_rows))
            json_rows = []

        return json_rows
