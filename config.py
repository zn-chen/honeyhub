from typing import Dict

from util import ConfigBase


class Config(ConfigBase):
    def _get_model(self) -> Dict:
        """
        配置文件模型
        """
        return {
            "Base": {
                "level": "str",
                "db_name": "str",
                "addr": "str",
                "port": "int",
            },
            "RabbitMQ": {
                "addr": "str",
                "port": "int",
                "vhost": "str",
                "username": "str",
                "password": "str",
                "max_pool_size": "int",
            },
            "MongoDB": {
                "addr": "str",
                "port": "int",
                "max_pool_size": "int",
                "min_pool_size": "int",
            },
            "Collector": {
                "warehouse": "str"
            },
            "Manager": {
                "beat_interval": "int"
            }
        }
