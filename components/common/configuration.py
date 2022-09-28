from typing import Any, Dict


class DataPathsConfiguration:
    def __init__(self, config_data: Dict[str, Any]):
        self.original_data_path = config_data['original_data_path']
        self.train_data_path = config_data['train_data_path']

        self.checkpoints_results_path = config_data['checkpoints_results_path']
        self.results_path = config_data['results_path']

    def __repr__(self) -> str:
        return str(self.__dict__)


class DataProcessorConfiguration:
    def __init__(self, config_data: Dict[str, Any]):
        pass

    def __repr__(self) -> str:
        return str(self.__dict__)


class ModelConfiguration:
    def __init__(self, config_data: Dict[str, Any]):
        pass

    def __repr__(self) -> str:
        return str(self.__dict__)
