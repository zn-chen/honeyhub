from logging import getLogger
from json import loads, dumps
from tornado.web import RequestHandler

from model.node import Node, NodeExsit


class BeatHandler(RequestHandler):
    """
    节点心跳接口处理器
    """
    _logger = getLogger()

    async def get(self, ident: str):
        """
        心跳接口
        """
        await Node().flush_beat_timestamp(ident=ident)
        self.write({"result": True})
