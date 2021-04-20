import sqlite3
import datetime
import os
from parsers.parser_base import ParserBase


class ActivitiesCacheParser(ParserBase):
    def __init__(self, config):
        super().__init__(config)

    @staticmethod
    def __dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def __parse_db(self, path, profile):
        con = sqlite3.connect(path)
        con.row_factory = self.__dict_factory
        cur = con.cursor()
        rows = cur.execute(
            r"SELECT AppId, PackageIdHash, AppActivityId, ActivityType, ActivityStatus, PlatformDeviceId, StartTime, EndTime, Payload, ClipboardPayload, ETag FROM Activity").fetchall()
        for row in rows:
            for key, value in row.items():
                if key == "Id":
                    continue
                if isinstance(value, bytes):
                    try:
                        row[key] = value.decode()
                    except UnicodeDecodeError:
                        self.log("{parser}: There was decoding exception at {row}".format(parser="ActivitiesCacheParser",
                                                                                         row=row))

            row["time"] = datetime.datetime.fromtimestamp(row["StartTime"]).isoformat()
            row.pop("StartTime")
            row["endTime"] = datetime.datetime.fromtimestamp(row["EndTime"]).isoformat()
            row.pop("EndTime")
            row["activity_profile_user"] = profile

        return rows

    def parse(self, paths):
        rows = []
        for path in paths:
            username = path.split("\\Users\\")[-1].split("\\")[0]
            for luser in os.listdir(path):
                luser_path = os.path.join(path, luser)
                if os.path.isdir(luser_path):
                    activities_path = os.path.join(luser_path, "ActivitiesCache.db")
                    profile = "{user}_{luser}".format(user=username, luser=luser)
                    rows += self.__parse_db(activities_path, profile)

        self._write_results_tuple(("activitiesCache", rows))
