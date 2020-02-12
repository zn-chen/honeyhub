from json import loads
from typing import Dict
from asyncio import Task
from logging import getLogger

from aio_pika import IncomingMessage

from config import Config
from model.node import Node
from util import MongoPool, RabbitmqPool, launcher


class Collector:
    def __init__(self, warehouse: str = "collector"):
        """
        数据采集任务
        """
        self._config = Config()
        self._logger = getLogger()

        self._mongo_pool = MongoPool()[warehouse]
        self._rabbitmq_pool = RabbitmqPool()

        self._task: Task = None
        self._nodes = Node()

    def start(self) -> None:
        """
        启动数采模块
        """
        self._rabbitmq_pool.subscribe("collector", self.warehousing)
        self._logger.debug("Collector start")

    def close(self) -> None:
        """
        关闭数采模块
        """
        if self._task:
            self._task.cancel()
            self._logger.debug("Collector stop")

    @launcher
    async def warehousing(self, msg: IncomingMessage) -> None:
        """
        记录入库
        """
        msg = msg.body
        if not msg:
            return

        msg = loads(msg)

        ident = msg["ident"]
        if not await self._nodes.exist(ident):
            return

        await self._mongo_pool["record"].insert_one(msg)
        self._logger.debug(
            "Warehousing a message from ident: %s", msg["ident"])
 