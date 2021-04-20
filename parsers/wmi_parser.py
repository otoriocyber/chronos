import subprocess
from parsers.parser_base import ParserBase


class WmiParser(ParserBase):
    PARSING_TOOL = r"python Tools/flare-wmi-master/python-cim/samples/timeline.py"

    def __init__(self, config):
        super().__init__(config)

    def parse(self, path):
        entries = []
        command = "{} {}".format(self.PARSING_TOOL, path)
        out, _ = subprocess.Popen(command.format(self.PARSING_TOOL, path), stdin=-1, stdout=-1, stderr=-1,
                                  shell=True).communicate()
        for line in out.splitlines():
            s_line = line.decode().split("\t")
            data = {"time": s_line[0].strip("Z"),
                    "label": s_line[1],
                    "key": s_line[2]
                    }
            entries.append(data)

        self._write_results_tuple(("wmi_records", entries))
