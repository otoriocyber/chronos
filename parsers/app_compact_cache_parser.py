import os
import csv
from parsers.parser_base import ParserBase


class AppCompatCacheParser(ParserBase):
    PARSER_PATH = r"Tools\AppCompatCacheParser.exe"
    RESULTS_FILE = "appCompatCache.csv"
    PARSE_COMMAND = "{parser_path} --csv {csv_path} --csvf {csv_name} -f \"{system_hive}\""
    TIME_FIELD = "LastModifiedTimeUTC"

    def __init__(self, temp, config):
        super().__init__(config)
        self.ShimSubDir = temp

    def parse(self, system_hive):
        post = system_hive.replace("\\", "_").replace(":", "").replace(" ", "_")
        result_file = self.RESULTS_FILE + "_" + post

        command = self.PARSE_COMMAND.format(parser_path=self.PARSER_PATH,
                                            system_hive=system_hive,
                                            csv_path=self.ShimSubDir,
                                            csv_name=result_file)
        self._run_command(command)

        fp = os.path.join(self.ShimSubDir, result_file)

        rows = []
        try:
            with open(fp, "r") as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    time_field = row.get(self.TIME_FIELD, None)
                    if time_field:
                        row["time"] = time_field.replace(" ", "T")
                    else:
                        row["time"] = "1970-01-01T00:00:00"
                    row.pop(self.TIME_FIELD)
                    row.pop("SourceFile", None)

                    rows.append(dict(row))
        except Exception as e:
            self.log("{parser}: There was a problem with the result file - {exception}".format(parser="AppCompatCacheParser", exception=e))

        self._write_results_tuple(("activitiesCache", rows))
