import logging
import subprocess
from abc import ABC, abstractmethod
from collections import namedtuple
from infrastructure.result_writer import ResultWriter

ParserConfig = namedtuple('ParserConfig', ['eventname', 'hostname', 'date', 'indexer', 'executor', 'bulk', 'dump'])

logger = logging
logger.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


class ParserBase(ABC):

    def __init__(self, config):
        self.result_writer = ResultWriter(config)

    @abstractmethod
    def parse(self, paths):
        pass

    @staticmethod
    def _run_command(command):
        result = subprocess.Popen(command, stdin=-1, stdout=-1, stderr=-1, shell=True)
        out, err = result.communicate()
        return out, err

    def _write_results_list(self, results):
        self.result_writer.write_results_from_list(results)

    def _write_results_tuple(self, results):
        self.result_writer.write_results_from_tuple(results)

    @staticmethod
    def log(message):
        logger.info(message)
