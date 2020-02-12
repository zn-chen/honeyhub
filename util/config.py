# -*- coding: utf-8 -*-
"""配置文件基类"""
import os
import sys
from io import BytesIO
from json import loads
from configparser import ConfigParser

from util.singleton import Singleton


class AttributeDict:
    """属性字典

    此类继承于字典但相较于原生字典，有以下几个主要不同点：
        1.可以使用属性的方式来获取字典中的值；
        2.不允许从构造器以外的地方新增或修改键和值。
    """

    def __init__(self, *args, **kwargs):
        """构造器"""
        self._dict = dict(*args, **kwargs)

    def __getattr__(self, name: str) -> object:
        """获取属性 特殊方法"""
        result = self._dict[name]

        if isinstance(result, dict):
            result = AttributeDict(result)

        return result


class ConfigParserEx:
    """配置文件基类"""

    def __init__(self):
        """构造器"""
        self._parser = ConfigParser()
        self._SUPPORT_TYPE = {
            r"int": self._get_int,
            r"str": self._get_str,
            r"bool": self._get_bool,
            r"json": self._get_json,
            r"float": self._get_float,

            r"file": self._get_file,
            r"file_str": self._get_file_str,
            r"file_bytes": self._get_file_bytes
        }

    def read(self, path: str, model: dict) -> dict:
        """读取配置文件"""
        self._parser.clear()
        self._parser.read(path, r"utf-8")

        return self._init_options(model)

    def read_string(self, string: str, model: dict) -> dict:
        """从字符串中读取配置信息"""
        self._parser.clear()
        self._parser.read_string(string)

        return self._init_options(model)

    def _init_options(self, model: dict) -> None:
        """初始化配置文件"""
        result = {}
        for section in model:
            result[section] = {
                key: self._SUPPORT_TYPE.get(value, self._get_str)(section, key)
                for key, value in model[section].items()
            }

        return result

    def _get_int(self, section: str, option: str) -> int:
        """获得配置文件中指定节下的指定配置项的值，并以 ``int`` 形式返回。"""
        return self._parser.getint(section, option)

    def _get_str(self, section: str, option: str) -> str:
        """获得配置文件中指定节下的指定配置项的值，并以 ``str`` 形式返回。"""
        return self._parser.get(section, option) or None

    def _get_bool(self, section: str, option: str) -> bool:
        """获得配置文件中指定节下的指定配置项的值，并以 ``bool`` 形式返回。"""
        return self._parser.getboolean(section, option)

    def _get_json(self, section: str, option: str) -> dict:
        """获得配置文件中指定节下的指定配置项的值，并进行Json反序列化后返回。"""
        return loads(self._get_str(section, option))

    def _get_float(self, section: str, option: str) -> float:
        """获得配置文件中指定节下的指定配置项的值，并以 ``float`` 形式返回。"""
        return self._parser.getfloat(section, option)

    def _get_file(self, section: str, option: str) -> BytesIO:
        """获得配置文件中指定节下的指定配置项的值，以此值为路径读取对应文件并以 ``ByteIO`` 形式返回。"""
        path = self._get_str(section, option)
        if path is None:
            return None

        with open(path, r"rb") as file:
            return BytesIO(file.read())

    def _get_file_bytes(self, section: str, option: str) -> bytes:
        """获得配置文件中指定节下的指定配置项的值，以此值为路径读取对应文件并以 ``bytes`` 形式返回。"""
        path = self._get_str(section, option)
        if path is None:
            return None

        with open(path, r"rb") as file:
            return file.read()

    def _get_file_str(self, section: str, option: str, encoding=r"utf-8") -> str:
        """获得配置文件中指定节下的指定配置项的值，以此值为路径读取对应文件并以 ``str`` 形式返回。"""
        path = self._get_str(section, option)
        if path is None:
            return None

        with open(path, r"r", encoding=encoding) as file:
            return file.read()


class ConfigBase(AttributeDict, Singleton):
    """插件配置基类

    此插件配置基类将默认使用
    """

    _CONFIG = None

    def __init__(self):
        """构造器"""
        options = ConfigParserEx().read_string(
            self._CONFIG, self._get_model()
        )

        super().__init__(options)

    def _get_model(self) -> dict:
        """获取配置文件模型"""
        raise NotImplementedError()

    @classmethod
    def initialize(cls, path: str, encoding: str = "utf-8") -> None:
        """读取配置文件内容"""
        with open(path, "r", encoding=encoding) as file:
            cls._CONFIG = file.read()


def get_config_default_dir():
    """
    获取默认的配置文件所在的目录
    """
    py_dir = os.path.dirname(__file__)
    exec_dir = os.path.dirname(sys.executable)
    now_dir = os.getcwd()

    if os.path.isfile(os.path.join(py_dir, '..', 'config.ini')):
        return os.path.join(py_dir, '..')
    elif os.path.isfile(os.path.join(exec_dir, 'config.ini')):
        return os.path.join(exec_dir)
    elif os.path.isfile(os.path.join(now_dir, 'config.ini')):
        return os.path.join(now_dir)
    else:
        return None


ROOT_DIR = get_config_default_dir()
