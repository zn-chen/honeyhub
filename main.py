import sys
import logging
from os.path import join, dirname
from asyncio import get_event_loop
from signal import signal, SIGINT, SIGTERM

from config import Config
from tornado.web import Application, StaticFileHandler, RequestHandler

from route import url
from collector import Collector
from util import ConfigBase, ROOT_DIR, RabbitmqPool, launcher, MongoPool


class Entry:
    def __init__(self):
        # 配置文件初始化
        ConfigBase.initialize(path=join(ROOT_DIR, "config.ini"))
        self._config = Config()

        # 日志初始化
        self._logger = logging.getLogger()
        logging.basicConfig(
            level=getattr(
                logging, (self._config.Base.level or "").upper(), logging.INFO),
            format="[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d]%(message)s",
            datefmt="%y%m%d %H:%M:%S"
        )

        self._loop = get_event_loop()

        signal(SIGINT, self.stop)
        signal(SIGTERM, self.stop)

    @launcher
    async def init(self):
        # rabbitmq消息队列连接池初始化
        try:
            await RabbitmqPool().init(
                addr=self._config.RabbitMQ.addr,
                port=self._config.RabbitMQ.port,
                username=self._config.RabbitMQ.username,
                password=self._config.RabbitMQ.password,
                vhost=self._config.RabbitMQ.vhost,
                max_size=self._config.RabbitMQ.max_pool_size
            )
        except Exception as ex:
            self._logger.error("Rabbitmq connection faild, %s. exit 1", ex)
            sys.exit(1)

        # 初始化mongodb连接池
        MongoPool(
            host=self._config.MongoDB.addr,
            port=self._config.MongoDB.port,
            maxPoolSize=self._config.MongoDB.max_pool_size,
            minPoolSize=self._config.MongoDB.min_pool_size,
        )

        # 启动数采模块
        Collector(warehouse=self._config.Collector.warehouse).start()

        # 启动api接口
        application = Application(url)
        addr = self._config.Base.addr
        port = self._config.Base.port
        application.listen(address=addr, port=port)
        self._logger.debug("Http api server start %s:%s", addr, port)

    def start(self):
        self.init()
        self._logger.info("Centor server running...")
        self._loop.run_forever()

    def stop(self, sign: int, _):
        self._loop.stop()
        self._logger.info("Centor server stop with %s", sign)
        sys.exit(sign)


if __name__ == "__main__":
    Entry().start()
