import os
import csv
import json
from parsers.parser_base import ParserBase


# This script takes both NTUSER.DAT and UsrClass.DAT and extracts Shellbags to CSV,JSON and Elasticsearch
class shellbagsParser(ParserBase):
    PARSING_TOOL = r"Tools\ShellBagsExplorer\SBECmd.exe"
    TIME_FIELDS = ['CreatedOn', 'ModifiedOn', 'AccessedOn', 'LastWriteTime', 'FirstInteracted', 'LastInteracted']

    def __init__(self, temp, config):
        super().__init__(config)
        self.ShellbagSubDir = temp

    def parse(self, paths):
        rows = []
        for path in paths:
            user = path.split("\\Users\\")[-1].split("\\")[0]
            output = self.ShellbagSubDir
            command = self.PARSING_TOOL + r" -d " + path + r" --csv " + output
            command_output = os.popen(command).read().split("\n")
            output_csvs = []
            for i in command_output:
                if '.csv' in i and 'Exported' in i:
                    output_csvs.append(i.split('\'')[1])
            for csv_file in output_csvs:
                with open(csv_file, encoding="utf8") as csvf:
                    csvReader = csv.DictReader(csvf)
                    with open(csv_file + ".json", 'w', encoding="utf8") as jsonf:
                        for row in csvReader:
                            for i in self.TIME_FIELDS:
                                if row[i] != '':
                                    json_row = {}
                                    try:
                                        json_row["time"] = row[i].replace(" ", "T")
                                    except Exception as e:
                                        self.log(
                                            "{parser} There was a ({exception})problem with the time field at {row}".format(
                                                parser="shellbagsParser",
                                                exception=e, row=row[i]))
                                        continue
                                    json_row["Type"] = i.split()[0]

                                    for j in row.keys():
                                        if (j is not i) and (j not in self.TIME_FIELDS):
                                            json_row[j] = row[j]

                                    json_row['user'] = user
                                    rows.append(json_row)
                                    json.dump(json_row, jsonf)
                                    jsonf.write('\n')

        self._write_results_tuple(("shellbags", rows))
