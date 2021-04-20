import os
import json


class Paths:
    def __init__(self):
        pass

    @staticmethod
    def _get_significant_paths(evidences_path):
        """
        Create a mapping of all the paths you want to add to your timeline
        """
        paths = {}
        paths["root"] = evidences_path
        paths["activitiesCache"] = os.path.join(evidences_path, "Users", "*", "AppData", "Local",
                                                "ConnectedDevicesPlatform")
        paths["appCompatCache"] = os.path.join(evidences_path, "WINDOWS", "System32", "config", "SYSTEM")
        paths['bits'] = os.path.join(evidences_path, "ProgramData", "Microsoft", "Network", "Downloader", "qmgr.db")
        paths['browsing_history_chrome'] = os.path.join(evidences_path, 'Users', '*', "AppData", "Local", "Google",
                                                        "Chrome", "User Data", "Default", "History")
        paths['browsing_history_ie'] = os.path.join(evidences_path, 'Users', '*', "AppData", "Local", "Microsoft",
                                                    "Windows", "WebCache")
        paths['browsing_history_firefox'] = os.path.join(evidences_path, 'Users', '*', "AppData", "Roaming", "Mozilla",
                                                         "Firefox", "Profiles")
        paths["defender"] = os.path.join(evidences_path, "ProgramData", "Microsoft", "Windows Defender", "Support")
        paths["evtxs"] = os.path.join(evidences_path, "Windows", "system32", "winevt", "logs")
        paths["mft_file"] = os.path.join(evidences_path, "$MFT")
        paths["prefetch_path"] = os.path.join(evidences_path, "Windows", "prefetch")
        paths["scheduled_tasks"] = os.path.join(evidences_path, "Windows", "system32", "Tasks")
        paths['shellbags'] = os.path.join(evidences_path, 'Users', '*', 'AppData', 'Local', 'Microsoft', 'Windows')
        paths["reg_config_path"] = os.path.join(evidences_path, "Windows", "system32", "config")
        paths["srum"] = os.path.join(evidences_path,  "WINDOWS", "System32", "sru", "SRUDB.dat")
        paths["wmi_repository"] = os.path.join(evidences_path, "WINDOWS", "System32", "wbem", "Repository")
        paths['additional_data'] = os.path.join(evidences_path, 'additional_data')

        return paths

    @staticmethod
    def _get_significant_paths_from_file(evidences_path, path):
        try:
            with open(path, "r") as fp:
                data = json.load(fp)
        except Exception as e:
            print("There was an error with in your file {} - {}\nplease try again after you fix the error".format(path, e))
            exit(0)

        paths = {}
        for key, value in data.items():
            relative_path = os.path.splitdrive(value)[-1]
            if not relative_path.startswith("\\"):
                relative_path = "\\" + relative_path
            paths[key] = "".join([evidences_path, relative_path])

        return paths

    def get_paths(self, args, evidences_path, temp_path):
        # Mapping to the relevant paths in disk
        paths = {}
        if args.file_only:
            if not os.path.exists(args.file_only):
                print("The path specified at --file-only doesn't exist, please check the path and try again")
                exit(0)
            else:
                paths = self._get_significant_paths_from_file(evidences_path, args.file_only)
        else:
            paths = self._get_significant_paths(evidences_path)
            if args.file:
                if not os.path.exists(args.file):
                    print("The path specified at --file doesn't exist, please check the path and try again")

                paths += self._get_significant_paths_from_file(evidences_path, args.file)
        paths["temp_results"] = temp_path
        return paths
