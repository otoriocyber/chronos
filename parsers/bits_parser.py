import json
import os

from parsers.parser_base import ParserBase


class BitsParser(ParserBase):
    PARSER_PATH = r"Tools\BitsParser-master\BitsParser.py"
    TEMP_RESULT_NAME = r"bits_db.json"
    PARSE_COMMAND = "python {parser_path} -i \"{bits_db}\" -o {output_path} --carveall"
    TIME_FIELD = "CreationTime"

    def __init__(self, temp, config):
        super().__init__(config)
        self.temp_result_path = temp

    def parse(self, bits_db_path):
        filename = self.TEMP_RESULT_NAME + "_" + bits_db_path.replace("\\", "_").replace(":", "").replace(" ", "_")
        fp = os.path.join(self.temp_result_path, filename)
        command = self.PARSE_COMMAND.format(parser_path=self.PARSER_PATH, bits_db=bits_db_path, output_path=fp)
        self._run_command(command)

        json_rows = []
        try:
            with open(fp, "r") as f:
                data = f.read()

            splitted = data.split("}\n{")

            splitted[0] = splitted[0] + "}"
            for i in range(1, len(splitted) - 1):
                splitted[i] = "{" + splitted[i] + "}"
            splitted[-1] = "{" + splitted[-1]

            for i in splitted:
                cur_json = json.loads(i)
                creationTime = cur_json.get(self.TIME_FIELD, None)
                if creationTime:
                    cur_json["time"] = creationTime.strip("Z")
                else:
                    cur_json["time"] = "1970-01-01T00:00:00"
                json_rows.append(cur_json)

        except Exception as e:
            self.log("{parser}: Unexpected exception occurred: {exception}".format(parser="BitsParser", exception=e))

        self._write_results_tuple(("bits", json_rows))
