"""
The custom wrappers to the parsers
"""
import os
from parsers.activities_cache import ActivitiesCacheParser
from parsers.app_compact_cache_parser import AppCompatCacheParser
from parsers.bits_parser import BitsParser
from parsers.browsing_history_parser import BrowsingHistoryParser
from parsers.evtx_parser import EvtxRustJson
from parsers.mft_parsers import MFTParser
from parsers.mplog_parser import MPLog
from parsers.prefetch_parser import PrefetchParser
from parsers.shellbags_parser import shellbagsParser
from parsers.srum_parser import SrumParser
from parsers.task_parser import TaskParser
from parsers.usn_parser import UsnParser
from parsers.wmi_parser import WmiParser


def __get_possible_paths(path):
    """
    Get all the possible paths from a base path
    """
    possibilities = set()
    if "*" not in path:
        return {path}
    base_path = path.split("*")[0][:-1]
    for entry in os.listdir(base_path):
        full_path = os.path.join(base_path, entry, "*".join(path.split("*")[1:])[1:])
        if os.path.exists(full_path):
            possibilities.add(full_path)

    return possibilities


def get_scheduled_tasks(paths, config):
    try:
        sched_path = paths.get("scheduled_tasks")
        if not sched_path:
            return None
        if not os.path.exists(sched_path):
            raise Exception("scheduled_tasks path doesn't exist")
        parser = TaskParser(config)
        parser.parse(sched_path)
    except Exception as e:
        print("[!] Scheduled Tasks - {}".format(e))


def get_mft(paths, config):
    try:
        mft_path = paths.get("mft_file")
        if not mft_path:
            return None
        if not os.path.exists(mft_path):
            raise Exception("mft_file path doesn't exist")
        temp_path = paths.get("temp_results")
        parser = MFTParser(temp_path, config)
        parser.parse(mft_path)
    except Exception as e:
        print("[!] MFT - {}".format(e))


def get_prefetches(paths, config):
    try:
        path = paths.get("prefetch_path")
        if not path:
            return None
        if not os.path.exists(path):
            raise Exception("prefetch path doesn't exist")
        temp_path = paths.get("temp_results")
        parser = PrefetchParser(temp_path, config)
        parser.parse(path)
    except Exception as e:
        print("[!] Prefetch - {}".format(e))


def get_evtx_threaded(paths, config):
    try:
        evtxs_path = paths.get("evtxs")
        if not evtxs_path:
            return None
        if not os.path.exists(evtxs_path):
            raise Exception("evtxs path doesn't exist")
        temp_path = paths.get("temp_results")
        parser = EvtxRustJson(temp_path, config)
        for name in os.listdir(evtxs_path):
            if not name.endswith(".evtx"):
                continue
            fp = os.path.join(evtxs_path, name)
            parser.parse(fp)
    except Exception as e:
        print("[!] Evtx - {}".format(e))


def get_shellbags(paths, config):
    try:
        path = paths.get('shellbags')
        if not path:
            return None
        possible_paths = __get_possible_paths(path)
        if not possible_paths:
            raise Exception("Shellbags paths doesn't exist")
        temp_path = paths.get("temp_results")
        parser = shellbagsParser(temp_path, config)
        parser.parse(possible_paths)
    except Exception as e:
        print("[!] Shellbags - {}".format(e))


def get_browsing_history(paths, config):
    try:
        possible_paths = set()
        paths_count = 0
        chrome_path = paths.get('browsing_history_chrome')
        if chrome_path:
            possible_paths |= __get_possible_paths(chrome_path)
        else:
            paths_count += 1
        ie_path = paths.get('browsing_history_ie')
        if ie_path:
            possible_paths |= __get_possible_paths(ie_path)
        else:
            paths_count += 1
        firefox_path = paths.get('browsing_history_firefox')
        if firefox_path:
            possible_paths |= __get_possible_paths(firefox_path)
        else:
            paths_count += 1

        if paths_count == 3:
            return None

        if not possible_paths:
            raise Exception("No supported browsing history found")

        temp_path = paths.get("temp_results")
        parser = BrowsingHistoryParser(temp_path, config)
        parser.parse(possible_paths)
    except Exception as e:
        print("[!] Browsing History - {}".format(e))


def get_usnjournal(paths, config):
    try:
        path = paths.get('UsnJrnl')
        if not path:
            return None
        paths = __get_possible_paths(path)
        if not paths:
            raise Exception("usnjrnl path doesn't exist")
        parser = UsnParser(config)
        for usn_path in paths:
            parser.parse(usn_path)
    except Exception as e:
        print("[!] UsnJrnl - {}".format(e))


def get_defender(paths, config):
    try:
        path = paths.get("defender")
        if not path:
            return None
        if not os.path.exists(path):
            raise Exception("windows defender path doesn't exist")
        parser = MPLog(config)
        for filename in os.listdir(path):
            if filename.lower().startswith("mplog"):
                full_path = os.path.join(path, filename)
                parser.parse(full_path)
    except Exception as e:
        print("[!] Defender - {}".format(e))


def get_wmi_records(paths, config):
    try:
        path = paths.get("wmi_repository")
        if not path:
            return None
        if not os.path.exists(path):
            raise Exception("wmi_repository path doesn't exist")
        parser = WmiParser(config)
        parser.parse(path)
    except Exception as e:
        print("[!] Wmi - {}".format(e))


def get_app_compat_cache(paths, config):
    try:
        path = paths.get("appCompatCache")
        if not path:
            return None
        if not os.path.exists(path):
            raise Exception("appCompatCache path doesn't exist")
        temp_path = paths.get("temp_results")
        parser = AppCompatCacheParser(temp_path, config)
        parser.parse(path)
    except Exception as e:
        print("[!] AppCompactCache - {}".format(e))


def get_activities_cache(paths, config):
    try:
        path = paths.get("activitiesCache")
        if not path:
            return None
        possible_paths = __get_possible_paths(path)
        if not possible_paths:
            raise Exception("activitiesCache path doesn't exist")
        parser = ActivitiesCacheParser(config)
        parser.parse(possible_paths)

    except Exception as e:
        print("[!] ActivitiesCache - {}".format(e))


def get_srum_data(paths, config):
    try:
        srum_path = paths.get("srum")
        software_hive_path = paths.get("reg_config_path")
        if not srum_path or not software_hive_path:
            return None
        if not os.path.exists(srum_path):
            raise Exception("SRUM: srum path doesn't exist")
        software_hive_path = os.path.join(software_hive_path, "software")
        if not os.path.exists(software_hive_path):
            raise Exception("SURM: software hive path doesn't exist")

        temp_path = paths.get("temp_results")
        parser = SrumParser(temp_path, config)
        parser.parse((srum_path, software_hive_path))
    except Exception as e:
        print("[!] Srum - {}".format(e))


def get_bits(paths, config):
    try:
        bits_path = paths.get("bits")
        if not bits_path:
            return None
        if not os.path.exists(bits_path):
            raise Exception("Bits DB path doesn't exist")
        temp_path = paths.get("temp_results")

        parser = BitsParser(temp_path, config)
        parser.parse(bits_path)
    except Exception as e:
        print("[!] Bits - {}".format(e))
