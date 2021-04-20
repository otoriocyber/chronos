from datetime import datetime
import xmltodict

from parsers.parser_base import ParserBase

"""
Parses browser history

HistorySource <Source>	Specifies the type of history data source (this parser uses Source 6)
 1 - Load history from the current running system (All users).
 2 - Load history from the current running system (Only current user).
 3 - Load history from the specified profiles folder (/HistorySourceFolder command-line parameter).
 4 - Load history from the specified profile (/HistorySourceFolder command-line parameter).
 5 - Load history from the specified custom folders (/CustomFolderAppData , /CustomFolderIEHistory , /CustomFolderLocalAppData).
 6 - Load history from the specified history files (/CustomFiles.IEFolders , /CustomFiles.IE10Files , /CustomFiles.FirefoxFiles, /CustomFiles.ChromeFiles , /CustomFiles.SafariFiles ).
 7 - Load history from remote computer (Use with /ComputerName command-line parameter).

"""


class BrowsingHistoryParser(ParserBase):
    PARSING_TOOL = r"Tools\BrowsingHistoryView.exe"
    OUTPUT = "browsing_output.xml"
    HISTORY_FILES = {"chrome": r"\AppData\Local\Google\Chrome\User Data\Default\History",
                     "ie": r"\AppData\Local\Microsoft\Windows\WebCache",
                     "firefox": r"\AppData\Roaming\Mozilla\Firefox\Profiles"}
    HISTORY_COMMANDS = {"chrome": "/CustomFiles.ChromeFiles", "ie": "/CustomFiles.IE10Files",
                        "firefox": "/CustomFiles.FirefoxFiles"}
    COMMAND_LINE_CONFIGS = " /VisitTimeFilterType 1 /SaveDirect /scomma "
    TIME_FIELDS = ["visit_time"]

    def __init__(self, temp, config):
        super().__init__(config)
        self.out_path = temp

    def __parse_file(self, filename, user):
        rows = []
        with open(filename, encoding="utf-16") as f:
            try:
                browsing_dict_list = xmltodict.parse(f.read())['browsing_history_items']['item']
            except:
                # Couldn't convert the browsing history xml to dict
                return []
            for diction in browsing_dict_list:
                for i in self.TIME_FIELDS:
                    if diction[i] != '':
                        json_row = {}
                        try:
                            diction["time"] = datetime.strptime(diction[i], "%d-%b-%y %H:%M:%S").isoformat()
                        except:
                            try:
                                diction["time"] = datetime.strptime(diction[i], "%d/%m/%Y %H:%M:%S").isoformat()
                            except:
                                self.log("{parser}: Couldn't parse the time to the right format - {time}".format(parser="BrowsingHistoryParser", time=diction[i]))
                                continue
                        json_row["Type"] = i.split("_")[0]

                        for j in diction.keys():
                            if (j is not i) and (j not in self.TIME_FIELDS):
                                json_row[j] = diction[j]

                        json_row['user'] = user
                        rows.append(json_row)
        return rows

    def parse(self, paths):
        rows = []

        for path in paths:
            to_parse = ""
            user = path.split("\\Users\\")[-1].split("\\")[0]

            for key, value in self.HISTORY_FILES.items():
                if value in path:
                    to_parse += self.HISTORY_COMMANDS[key] + " \"" + path + "\" "

            output = self.out_path + "\\" + self.OUTPUT
            filename = output + "_" + path.replace("\\", "_").replace(":", "").replace(" ", "_")
            command = self.PARSING_TOOL + r" /HistorySource 6 " + to_parse + self.COMMAND_LINE_CONFIGS + "/sxml " + filename
            self._run_command(command)

            rows += self.__parse_file(filename, user)

        self._write_results_tuple(("browsing_history", rows))
