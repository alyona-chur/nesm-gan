import logging
from pathlib import Path
import sys


def configure_logger(log_file_path: Path, log_level: 'logging.LEVEL'):
    logging.basicConfig(filename=log_file_path,
                        stream=sys.stdout,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%y-%m-%d %H:%M:%S')
    logging.root.setLevel(log_level)


def get_logger_name(class_name: str) -> str:
    """Returns logger name based on a class name.

    Args:
        class_name: Class name.

    Returns:
        Logger name.
    """
    return f'[{class_name}]'
