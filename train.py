def train(config_path: str):
    config = Configuration(Path(config_path))

    data_processor = DataProcessor(config.data_processor_config)
    data_processor.process_data_forward(config.data_paths_config)
    model = ModelTrainer(config.model_config)



if __name__ == '__main__':
    train()
