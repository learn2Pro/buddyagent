# coding=utf-8
from abc import abstractmethod
import yaml
import pathlib
from loguru import logger


class BaseLoader():

    @abstractmethod
    def __getitem__(self, key):
        """获取元素"""


class YamlLoader(BaseLoader):
    def __init__(self, file_name: str) -> None:
        super().__init__()
        with open(file_name, 'r') as file:
            self.data = yaml.safe_load(file)

    def __getitem__(self, key):
        return self.data[key]

    def get(self, key):
        return self.data[key]

CONFIG_PATH = pathlib.Path(__file__).parent.parent.resolve()
_CONFIG_YAML = f'{CONFIG_PATH}/llm.yaml'
logger.debug(f'load yaml config from path={_CONFIG_YAML}!')

config_data: BaseLoader = YamlLoader(_CONFIG_YAML)
