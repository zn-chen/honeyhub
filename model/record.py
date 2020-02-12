from typing import Dict
from util import Singleton

from util import MongoPool


class Record(Singleton):
    def __init__(self):
        self._mongo_pool = MongoPool().collector
        self._node_collection = "record"

    async def get_record(self, num: int, start: int = 0, rule: Dict[str, int] = {"_id": 0}):
        """
        获取从指定条数开始的指定数量的攻击, 默认不返回 _id
        """
        cursor = self._mongo_pool[self._node_collection].find({}, rule)
        cursor.skip(start)
        return [i for i in await cursor.to_list(num)]
