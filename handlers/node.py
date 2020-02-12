from time import time, strftime, localtime
from json import loads, dumps
from logging import getLogger
from tornado.web import RequestHandler

from config import Config
from model.node import Node, NodeExsit


class NodesHandler(RequestHandler):
    """
    多节点操作处理器
    """
    _logger = getLogger()

    async def post(self):
        """
        节点注册
        """
        register_info = self.request.body.decode(encoding="utf-8")
        register_info = loads(register_info)

        await Node().add_node(
            ident=register_info["ident"],
            name=register_info["name"],
            addr=register_info["addr"],
            port=register_info["port"],
            describe=register_info["describe"],
        )

        self._logger.info("Ident: %s create success", register_info["ident"])
        self.write({"result": True})

    async def get(self):
        """
        查询多个节点信息
        """
        beat_interval = Config().Manager.beat_interval
        rst_list = await Node().get_infos()
        rst_dic = {"result": []}
        for i in rst_list:
            rst_dic["result"].append({
                "ident": i["ident"],
                "name": i["name"],
                "statue": "inactive" if (time() - i["beat_timestamp"] > beat_interval) else "active",
                "addr": i["addr"],
                "port": str(i["port"])+"/tcp",
                "describe": i["describe"],
                "create_time": strftime("%Y-%m-%d %H:%M:%S", localtime(int(i["create_time"]))),
            })
        self.write(rst_dic)


class NodeHandler(RequestHandler):
    """
    单节点操作处理器
    """
    _logger = getLogger()

    async def delete(self, ident):
        await Node().delete(ident=ident)

        self._logger.info("Ident: %s delete success", ident)
        self.write({"result": True})

    async def get(self, ident):
        beat_interval = Config().Manager.beat_interval
        info = await Node().get_info(ident=ident)
        self.write({
            "ident": info["ident"],
            "name": info["name"],
            "statue": "inactive" if (time() - info["beat_timestamp"] > beat_interval) else "active",
            "addr": info["addr"],
            "port": info["port"],
        })
