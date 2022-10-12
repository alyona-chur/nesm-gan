# TODO: Add docstrings
from distutils.command.config import config
from pathlib import Path
from typing import Any, Dict

import yaml


class DataPathsConfiguration:
    def __init__(self, config_data: Dict[str, Any]):
        self.original_data_path = str(config_data['original_data_path'])
        self.train_data_path = str(config_data['train_data_path'])

        self.checkpoints_results_path = str(config_data['checkpoints_results_path'])
        self.results_path = str(config_data['results_path'])

    def __repr__(self) -> str:
        return str(self.__dict__)


class DataProcessorConfiguration:
    def __init__(self, config_data: Dict[str, Any]):
        self.representation = str(config_data['representation'])
        self.scaling = str(config_data['scaling'])
        self.replace_if_exists = config_data['replace_if_exists']

        self.download_if_missing = config_data['download_if_missing'] \
            if 'download_if_missing' in config_data else None
        self.dataset_sample_rate = float(config_data['dataset_sample_rate']) \
            if 'dataset_sample_rate' in config_data else None
        self.sample_len = int(config_data['sample_len']) if 'sample_len' in config_data else None
        self.cutting_step = int(config_data['cutting_step']) \
            if 'cutting_step' in config_data else None

    def __repr__(self) -> str:
        return str(self.__dict__)


class ModelInferencerConfiguration:
    def __init__(self, config_data: Dict[str, Any]):
        self.model_path = str(config_data['model_path'])
        self.num_of_samples = int(config_data['num_of_samples'])

    def __repr__(self) -> str:
        return str(self.__dict__)

# class ModelTrainingConfiguration:
#     def __init__(self, config_data: Dict[str, Any]):
#         self.discriminator_model = config_data['discriminator_model']
#         self.adversarial_model = config_data['adversarial_model']


class ModelTrainerConfiguration:
    def __init__(self, config_data: Dict[str, Any]):
        self.save_models_path = config_data['save_models_path']
        self.generator = config_data['generator']
        self.discriminator = config_data['discriminator']

        # self.training_config = ModelTrainingConfiguration(config_data['training'])
        # TODO: self.resume_training

    def __repr__(self) -> str:
        return str(self.__dict__)


class Configuration:
    def __init__(self, config_path: Path):
        config_data = read_yaml(config_path)

        self.data_paths_config = DataPathsConfiguration(config_data['data_paths'])
        self.data_processor_config = DataProcessorConfiguration(config_data['data_processor'])
        self.model_inferencer_config = ModelInferencerConfiguration(
            config_data['model_inferencer'])  if 'model_inferencer' in config_data \
                else None
        self.model_inferencer_config = ModelInferencerConfiguration(
            config_data['model_inferencer'])  if 'model_inferencer' in config_data \
                else None

    def __repr__(self) -> str:
        return str(self.__dict__)


def read_yaml(config_path: Path) -> Dict[str, Any]:
    loader = yaml.FullLoader
    with open(config_path):
        return yaml.load(config_path, Loader=loader)
