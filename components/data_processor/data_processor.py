from copyreg import pickle
from enum import Enum
import logging
from pathlib import Path
from webbrowser import get
from components.common.logging_lib import get_logger_name

import numpy as np

from components.common.configuration import DataPathsConfiguration, DataProcessorConfiguration


class OriginalDataFormat(Enum):
    # - 'seprsco', Separated Score Format. Contains Note information only,
    #  for 4 instruments for N number for timestamps at 24Hz.
    SEPRSCO = 'seprsco'


class RepresentationFormat(Enum):
    MEL = 'mel'
    ROLL = 'roll'


class DataProcessor:
    '''
    original -> scaled -> represented
    represented -> scaled -> original
    '''
    def __init__(self, config: DataProcessorConfiguration, ):
        self._original_format = OriginalDataFormat.SEPRSCO
        self._representation = RepresentationFormat(config.representation)
        self._scaling = config.scaling
        self._replace_if_exists = config.replace_if_exists

        self._download_if_missing = config.download_if_missing
        self._dataset_sample_rate = config.dataset_sample_rate
        self._sample_len = config.sample_len
        self._cutting_step = config.cutting_step

        self._logger = get_logger_name(self.__class__.__name__)

    # Forward

    def _read_original(self, path: Path) -> np.ndarray:
        if self._original_format == OriginalDataFormat.SEPRSCO:
            return read_seprsco(path)
        raise ValueError(f'Not supported original data format: {self._original_format}')

    def _scale(self, original_song: np.ndarray) -> np.ndarray:
        pass

    def _cut(self, song: np.ndarray) -> np.ndarray:
        pass

    def _represent(self, scaled_song: np.ndarray):
        pass

    def _save_represented(self, repr_song: np.ndarray, path: Path):
        pass

    # Backward

    def _read_represented(self, path: Path):
        pass

    def _unrepresent(self, repr_song: np.ndarray):
        pass

    def _unscale(self, scaled_song: np.ndarray):
        pass

    def _save_original(self, orig_song: np.ndarray, path: Path):
        pass

    def _save_wav(self, orig_song: np.ndarray, path: Path):
        pass

    def process_forward(self, orig_dir: Path, repr_dir: Path):
        for child_file in orig_dir.iterdir():
            self._logger.info(f'Processing {child_file}')

            full_song = self._read_original(child_file)



    def process_backward(self, repr_dir: Path, orig_dir: Path, save_wav: bool = False):
        pass


def download_data():
    pass


# def read_seprsco(path: Path):
#     with open(path, 'rb') as bin_file:
#         rate, nsamps, seprsco = pickle.load(bin_file)
#         print()
