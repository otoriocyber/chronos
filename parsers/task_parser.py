import xmltodict
import os
from parsers.parser_base import ParserBase


class TaskParser(ParserBase):
    def __init__(self, config):
        super().__init__(config)

    def __parse_task(self, path):
        parsed_task = {}
        try:
            with open(path, "r", encoding="utf-16") as task:
                task_content = task.read()
                parsed_task = xmltodict.parse(task_content)
                try:
                    parsed_task["time"] = parsed_task["Task"]["RegistrationInfo"]["Date"].split(".")[0]
                except:
                    parsed_task["time"] = "1970-01-01T00:00:00"
        except Exception as e:
            self.log("{parser} Error occurred with the file {path} in task parsing".format(parser="TaskParser", path=path))

        return parsed_task

    def parse(self, path):
        parsed_tasks = []
        for root, dirs, files in os.walk(path, topdown=False):
            for file in files:
                full_path = os.path.join(root, file)
                parsed = self.__parse_task(full_path)
                parsed["task_name"] = os.path.split(path)[-1]
                parsed_tasks.append(parsed)
        self._write_results_tuple(("scheduledtasks", parsed_tasks))
