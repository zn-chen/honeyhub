from motor.motor_asyncio import AsyncIOMotorClient

from util.singleton import Singleton


class Pool(AsyncIOMotorClient, Singleton):
    """
    全局mongo连接池
    """
    pass
