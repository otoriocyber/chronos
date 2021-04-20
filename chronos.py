import datetime
import os
import shutil
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED

from parsers.parser_base import ParserConfig

from infrastructure.args import Args
from infrastructure.paths import Paths
from infrastructure.utils import get_all_funcs, create_temp_dir
from infrastructure.indexer import get_indexer


def main():
    args = Args()
    args.validate()
    args = args.parser.parse_args()
    evidences_path = args.evidences
    dump = args.dump
    if dump == args.host is None:
        print("[!] Neither --host nor --dump mentioned, results will be saved to a temp directory under the project")
        dump = "temp"

    hostname = evidences_path.split(os.sep)[-2]
    date = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  # Temporary time format
    temp_path = create_temp_dir(date, hostname)
    all_functions = get_all_funcs()
    paths = Paths().get_paths(args, evidences_path, temp_path)
    indexer = get_indexer(args)

    with ThreadPoolExecutor() as executor:
        # Run all the different functions (which run the parsers)
        config = ParserConfig(eventname=args.eventname, hostname=hostname, date=date, indexer=indexer,
                              executor=executor, bulk=args.bulk, dump=dump)
        future_funcs = { executor.submit(func, paths, config): func for func in all_functions }
        print("[+] Created all funcs")

        wait(future_funcs, timeout=None, return_when=ALL_COMPLETED)

    if not dump:
        shutil.rmtree(temp_path)


if __name__ == '__main__':
    import time
    start = time.time()
    main()
    end = time.time()
    print("!"*30 + "\nThe run took {} seconds\n".format(end-start) + "!"*30)