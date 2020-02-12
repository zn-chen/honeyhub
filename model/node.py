from time import time
from typing import Dict

from config import Config
from util import MongoPool, Singleton


class Node(Singleton):
    def __init__(self):
        """
        蜜罐节点模型
        """
        self._mongo_pool = MongoPool()[Config().Base.db_name]
        self._node_collection = "node"

    async def get_info(self, ident: str):
        """
        获取节点信息
        节点信息：
            ident: 节点的唯一标识 32位长string
            name: 节点名称
            addr: ipv4地址
            port: 服务的端口格式,如有多个则逗号分隔  8080/tcp
            describe: 节点描述
            create_time: 节点创建时间戳
            beat_timestamp: 用于心跳检测的戳
        """
        return await self._mongo_pool[self._node_collection].find_one({"ident": ident})
    
    async def get_infos(self):
        """
        获取多个节点信息，至多100
        """
        cursor  = self._mongo_pool[self._node_collection].find()
        return [i for i in await cursor.to_list(100)]

    async def exist(self, ident: str) -> bool:
        """
        判断该节点是否存在
        """
        if await self.get_info(ident):
            return True
        else:
            return False

    async def add_node(self, ident: str, name: str, addr: str, port: int, describe: str):
        """
        新增节点信息
        """
        if await self.exist(ident=ident):
            raise NodeExsit()

        await self._mongo_pool[self._node_collection].insert_one({
            "ident": ident,
            "name": name,
            "addr": addr,
            "port": port,
            "describe": describe,
            "create_time": time(),
            "beat_timestamp": -1,
        })

    async def delete(self, ident: str):
        """
        删除节点信息
        """
        await self._mongo_pool[self._node_collection].delete_many({"ident": ident})

    async def update(self, ident: str, **kwarge):
        """
        更新节点信息
        """
        await self._mongo_pool[self._node_collection].update_one({"ident": ident}, {'$set': kwarge})

    async def get_beat_timestamp(self, ident: str) -> int:
        """
        获得上一次心跳检测的时间戳
        """
        rst = await self.get_info(ident=ident)
        beat_timestamp = rst.get("beat_timestamp")

        if beat_timestamp:
            return beat_timestamp
        else:
            raise Exception("Recode not beat_timestamp")
    
    async def flush_beat_timestamp(self, ident: str):
        """
        刷新一个节点的时间戳
        """
        await self.update(ident=ident, beat_timestamp=time())


class NodeExsit(Exception):
    """
    新增节点已经存在异常
    """
    def __str__(self):
        return "The node already exists"
