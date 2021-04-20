import json
import os


INDEX_FORMAT = "{eventname}-{hostname}-{logs}-{date}"


class ResultWriter:
    def __init__(self, config):
        self.config = config

    def write_results_from_list(self, results):
        if not results:
            return

        dump_dir = None
        if self.config.dump:
            dir_name = results[0][0].split("-")[0]
            dump_dir = os.path.join(self.config.dump, dir_name)
            if not os.path.exists(dump_dir):
                os.makedirs(dump_dir)

        for entry in results:
            self._save_result(self.config.eventname, self.config.hostname, entry, self.config.date,
                              self.config.indexer, self.config.executor, self.config.bulk, dump_dir)

    def write_results_from_tuple(self, results):
        if not results:
            return
        self._save_result(self.config.eventname, self.config.hostname, results, self.config.date,
                          self.config.indexer, self.config.executor, self.config.bulk, self.config.dump)

    # Send data to DB
    @staticmethod
    def __send_to_db(eventname, hostname, entry, date, indexer, executor, bulk):
        """Add the index to DB function to the threadpool

        Args:
            eventname: The incident the evidences related to
            hostname: The hostname the evidences acquired from
            entry: The result of the function
            date: The indexing date
            indexer: Instance of the DB uploading object
            executor: Instance of the threadpool manager
            bulk: Amount of jsons to upload per sent
        """
        index_name, data = entry
        _index = INDEX_FORMAT.format(eventname=eventname, hostname=hostname, logs=index_name,
                                     date=date).lower().replace(' ', '_')
        executor.submit(indexer.index, _index, data, int(bulk))

    @staticmethod
    def __dump_to_disk(eventname, hostname, entry, date, dump_path):
        """ Dump the results to disk

        Args:
            eventname: The incident the evidences related to
            hostname: The hostname the evidences acquired from
            entry: The result of the function
            date: The indexing date
            dump_path: The path to save the results to
        """
        index_name, data = entry
        # Don't dump the mft as list of jsons as the result is too big and time consuming
        # check the csv created during the parsing under the temp directory
        if index_name == "mft":
            return
        file_name = INDEX_FORMAT.format(eventname=eventname, hostname=hostname, logs=index_name, date=date).lower() \
            .replace(' ', '_')

        if not os.path.exists(dump_path):
            os.makedirs(dump_path)

        full_path = os.path.join(dump_path, file_name)

        with open(full_path, "w") as f:
            json.dump(data, f)

    def _save_result(self, eventname, hostname, returned, date, indexer, executor, bulk_size, dump):
        if dump:
            executor.submit(self.__dump_to_disk, eventname, hostname, returned, date, dump)

        if indexer:
            self.__send_to_db(eventname, hostname, returned, date, indexer, executor, bulk_size)
