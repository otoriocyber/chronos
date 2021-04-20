import json
from parsers.parser_base import ParserBase


class PrefetchParser(ParserBase):
    PARSING_TOOL = "Tools\\PECmd.exe"
    TIME_FIELDS = ["SourceCreated", "SourceModified", "SourceAccessed", "LastRun"]

    def __init__(self, temp, config):
        super().__init__(config)
        self.PrefetchSubDir = temp

    def _separate_times(self, prefetch):
        times = []
        base_prefetch = {}
        time_fields = []
        for key, value in prefetch.items():
            if key not in self.TIME_FIELDS and not key.startswith("PreviousRun"):
                base_prefetch[key] = value
            else:
                time_fields.append(key)

        for time_field in time_fields:
            base_prefetch["time"] = prefetch[time_field].split(".")[0]
            base_prefetch["time_field"] = time_field
            times.append(base_prefetch)

        return times

    def _extract_data(self, prefetch_directory):
        command = "{tool} -d \"{prefetch_dir}\" --json {subdir} -q".format(
            tool=self.PARSING_TOOL,
            prefetch_dir=prefetch_directory,
            subdir=self.PrefetchSubDir
        )

        out, err = self._run_command(command)

        if not err:
            return out
        else:
            return ""

    def _extract_results_file(self, data):
        result_file = data.splitlines()[-1].split(("{subdir}\\".format(subdir=self.PrefetchSubDir))
                                                  .encode())[-1][:-1].decode()

        return result_file

    def _parse_results(self, filename):
        results = []
        full_path = "{subdir}\\{results}".format(subdir=self.PrefetchSubDir, results=filename)
        try:
            with open(full_path, "rb") as f:
                jsons_list = [json.loads(line) for line in f.readlines()]
        except:
            self.log("{parser} Failed to read the results file, is the folder empty or you are not running as administrator?".format(parser="PrefetchParser"))
            return results

        for prefetch_json in jsons_list:
            temp_array = []
            prefetch_json["FilesLoaded"] = prefetch_json["FilesLoaded"].split(", ")
            for file_loaded in prefetch_json["FilesLoaded"]:
                temp_array.append("C:\\" + "\\".join(file_loaded.split("\\")[2:]))
            prefetch_json["FilesLoaded"] = temp_array

            temp_array = []
            prefetch_json["Directories"] = prefetch_json["Directories"].split(", ")
            for file_loaded in prefetch_json["Directories"]:
                temp_array.append("C:\\" + "\\".join(file_loaded.split("\\")[2:]))
            prefetch_json["Directories"] = temp_array

            prefetch_json_times = self._separate_times(prefetch_json)

            results += prefetch_json_times

        return results

    def parse(self, prefetch_directory):
        extracted_data = self._extract_data(prefetch_directory)
        if extracted_data:
            extracted_filename = self._extract_results_file(extracted_data)
            self._write_results_tuple(("prefetch", self._parse_results(extracted_filename)))
        else:
            return
