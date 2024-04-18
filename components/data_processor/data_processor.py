"""This module contains classes to manage data processing"""
from enum import Enum
import logging
from multiprocessing import Pool
from pathlib import Path
import pickle
import subprocess

import cv2
import numpy as np

from components.common.configuration import DataProcessorConfiguration
from components.common.constants import LOGGER_NAME
from components.common.constants import NOISE_MAX_VAL
from components.common.constants import NOISE_MIN_VAL
from components.common.constants import SEPRSCO_DATASET_DOWNLOAD_LINK
from components.common.constants import PULSES12_MAX_VAL
from components.common.constants import PULSES12_MIN_VAL
from components.common.constants import TRIANGLE_MAX_VAL
from components.common.constants import TRIANGLE_MIN_VAL
from components.common.logger_manager import LoggerManager
from components.common.logger_manager import LogWritingClass


class OriginalDataFormat(Enum):
    """A class to define supported original data formats."""
    # - 'seprsco', Separated Score Format. Contains Note information only,
    #  for 4 instruments for N number for timestamps at 24Hz.
    SEPRSCO = 'seprsco'


class RepresentationFormat(Enum):
    """A class to define supported data representation formats."""
    ROLL = 'roll'


# TODO: Use pytorch transform.
class DataProcessor(LogWritingClass):
    """A class to manage data processing.

    Attributes:
        _original_format: OriginalDataFormat, original data format to work with.
        _representation: RepresentationFormat, representation format to work with.
        _sample_len: Int, length of song fragment. In timestamps for scores formats.
        _cutting_step: Int, distance between starts of song fragments.
            In timestamps for scores formats.
        _rows: Int, number of rows for stacking.

    Note:
        Forward processing: original -> scaled -> cut -> represented (used for training).
                                |                                  |
                                v                                  v
                     wav (when original is not wav)             visible (png)
        Backward processing: represented -> scaled -> original.
                                |                        |
                                v                        v
                           visible (png)           wav (when original is not wav)
    """
    def __init__(self, config: DataProcessorConfiguration, logger_manager: LoggerManager):
        """Initializes an instance of the class.

        Args:
            config: Configuration.
            logger_manager: Logger manager for logging to std.out / std.err or / and files.
        """
        LogWritingClass.__init__(self,
                                 LOGGER_NAME.format(class_name=self.__class__.__name__),
                                 logger_manager)
        self._original_format = OriginalDataFormat.SEPRSCO
        self._representation = RepresentationFormat(config.representation)
        self._sample_len = config.sample_len
        self._cutting_step = config.cutting_step
        self._rows = config.rows

        self._log(logging.INFO, 'Initialized Data Processor.')

    def _download_sepsco_data(self, download_to_dir: Path):
        """Downloads and extracts data.

        Args:
            download_to_dir: Where to download.
        """
        tmp_file = Path('./nesmdb24_seprsco.tar.gz')
        subprocess.check_call(['wget', '--no-check-certificate', SEPRSCO_DATASET_DOWNLOAD_LINK],
                               '-O', './nesmdb24_seprsco.tar.gz')
        subprocess.check_call(['tar', 'xvfz', str(tmp_file), '-C', './tmp'])
        subprocess.check_call(['mv', './tmp/train/*', str(download_to_dir.resolve())])
        subprocess.check_call(['mv', './tmp/test/*', str(download_to_dir.resolve())])
        subprocess.check_call(['mv', './tmp/valid/*', str(download_to_dir.resolve())])
        subprocess.check_call(['rm', './tmp', '-r'])
        subprocess.check_call(['rm', 'nesmdb24_seprsco.tar.gz'])

        # for path in (download_to_dir / Path('train')).iterdir():
        #     if path.is_file():
        #         with open(path, 'rb') as bin_file:
        #             rate, nsamps, seprsco = pickle.load(bin_file)
        #             self._log(logging.INFO,
        #                       f'Downloaded sepsco data. Example: rate={rate}, '
        #                       f'nsamps={nsamps}, seprsco={seprsco.T}.')
        #     break

    def download_data(self, download_to_dir: Path):
        """Downloads original data.

        Args:
            download_to_dir: A path to download and unpack all data to.
        """
        if self._original_format == OriginalDataFormat.SEPRSCO:
            self._download_sepsco_data(download_to_dir)
        else:
            raise ValueError(f'Unsupported original format: {self._original_format} '
                             f'in download_data method.')

    # Forward

    def scale(self, original_data_dir: Path, scaled_data_dir: Path):
        """Scales data using min-max scaling according to instruments range."""
        if self._original_format == OriginalDataFormat.SEPRSCO:
            scaled_data_dir.mkdir(parents=True, exist_ok=True)
            with Pool() as pool:
                pool.starmap(scale_seprsco_song_min_max,
                             [(file, original_data_dir)
                              for file in list(original_data_dir.iterdir())])
        else:
            raise ValueError(f'Unsupported original format: {self._original_format} '
                             f'in scale method.')

    def cut(self, songs_dir: Path, cuts_dir: Path):
        """Cuts songs into fragments."""
        with Pool() as pool:
            cuts_dir.mkdir(parents=True, exist_ok=True)
            pool.starmap(cut_song, [(file, cuts_dir, self._sample_len, self._cutting_step)
                                    for file in list(songs_dir.iterdir())])

    def represent(self, songs_dir: Path, represented_data_dir: Path):
        """Represents fragments by stacking scaled and cut data."""
        with Pool() as pool:
            represented_data_dir.mkdir(parents=True, exist_ok=True)
            pool.starmap(represent_as_piano_roll_stack,
                         [(file, represented_data_dir, self._rows)
                          for file in list(songs_dir.iterdir())])

    # Backward

    def unrepresent(self, represented_data_dir: Path, songs_dir: Path):
        """Changes stacked data into song fragments."""
        with Pool() as pool:
            songs_dir.mkdir(parents=True, exist_ok=True)
            pool.starmap(unrepresent_as_piano_roll_stack,
                         [(file, songs_dir, self._rows)
                          for file in list(represented_data_dir.iterdir())])

    def unscale(self, scaled_data_dir: Path, result_data_dir: Path):
        """Unscales data."""
        if self._original_format == OriginalDataFormat.SEPRSCO:
            result_data_dir.mkdir(parents=True, exist_ok=True)
            with Pool() as pool:
                pool.starmap(unscale_seprsco_song_min_max,
                             [(file, result_data_dir)
                              for file in list(scaled_data_dir.iterdir())])
        else:
            raise ValueError(f'Unsupported original format: '
                             f'{self._original_format} in unscale method.')

    # Conversion

    def convert_npy_to_png(self, npy_dir: Path, png_dir: Path):
        """Converts npy files to png."""
        with Pool() as pool:
            png_dir.mkdir(parents=True, exist_ok=True)
            pool.starmap(convert_npy_to_png,
                         [(file, png_dir, self._rows)
                          for file in list(npy_dir.iterdir())])

    def convert_to_wav(self, data_dir: Path, wav_dir: Path):
        """Converts original data to wav."""
        if self._original_format == OriginalDataFormat.SEPRSCO:
            pass
        else:
            raise ValueError(f'Unsupported original format: '
                             f'{self._original_format} in convert_to_wav method.')


def check_file_exists_and_not_empty(file_path: Path):
    path = Path(file_path)
    return path.is_file() and path.stat().st_size > 0


def read_seprsco_song(song_path: Path):
    with open(song_path, 'rb') as f:
        _, _, seprsco = pickle.load(f)
    return seprsco.T


def save_seprsco_song(song_data: np.ndarray, song_path: Path):
    with open(song_path, 'wb') as f:
        pickle.dump(song_data, f, protocol=2)


def scale_instrument_min_max(inst_data: np.ndarray, inst_min: float, inst_max: float):
    inst_data[inst_data == 0] = inst_min
    inst_data -= inst_min
    inst_data /= (inst_max - inst_min)


def scale_seprsco_song_min_max(input_path: Path, output_dir: Path):
    song = read_seprsco_song(input_path).astype(np.float)
    scale_instrument_min_max(song[:2, :], PULSES12_MIN_VAL, PULSES12_MAX_VAL)
    scale_instrument_min_max(song[2, :], TRIANGLE_MIN_VAL, TRIANGLE_MAX_VAL)
    scale_instrument_min_max(song[3, :], NOISE_MIN_VAL, NOISE_MAX_VAL)
    np.save(str(output_dir / input_path.stem), song)


def unscale_instrument_min_max(inst_data: np.ndarray, inst_min: float, inst_max: float):
    inst_data *= (inst_max - inst_min)
    inst_data += inst_min
    inst_data[inst_data == inst_min] = 0


def unscale_seprsco_song_min_max(input_path: Path, output_dir: Path):
    song = np.load(str(input_path)).astype(np.float)

    unscale_instrument_min_max(song[:2, :], PULSES12_MIN_VAL, PULSES12_MAX_VAL)
    unscale_instrument_min_max(song[2, :], TRIANGLE_MIN_VAL, TRIANGLE_MAX_VAL)
    unscale_instrument_min_max(song[3, :], NOISE_MIN_VAL, NOISE_MAX_VAL)

    save_seprsco_song(song, output_dir / f'{input_path.stem}.pkl')


def cut_song(input_path: Path, output_dir: Path, sample_len: int, cutting_step: int):
    song = np.load(str(input_path)).astype(np.float)
    for i, start in enumerate(range(0, len(song[0]) - sample_len + 1, cutting_step)):
        end = start + sample_len
        np.save(str(output_dir / Path(f'{input_path.stem}__{i}')), song[:, start:end])


def represent_as_piano_roll_stack(input_path: Path, output_dir: Path, rows: int):
    song = np.load(str(input_path)).astype(np.float)
    if song.shape[1] % rows != 0:
        raise ValueError(f'song.shape[1] % rows != 0: {song.shape}, {rows} for {input_path}.')

    delta = song.shape[1] // rows
    stack_list = []
    for ri in range(1, rows + 1):
        stack_list.append(song[:, (ri-1) * delta : ri * delta])

    np.save(str(output_dir / input_path.stem), np.stack(stack_list).reshape(4 * rows, delta, 1))


def unrepresent_as_piano_roll_stack(input_path: Path, output_dir: Path, rows: int):
    song = np.load(str(input_path)).astype(np.float)
    stack_list = np.split(song, rows)
    np.save(str(output_dir / input_path.stem), np.concatenate(stack_list, axis=1))


def convert_npy_to_png(input_path: Path, output_path: Path):
    song = np.load(str(input_path)).astype(np.float)
    array_normalized = cv2.normalize(array, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
    array_normalized = array_normalized.astype('uint8')
    cv2.imwrite(output_dir / f'{input_path.stem}.png', array_normalized)
