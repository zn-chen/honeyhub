from asyncio import get_event_loop, ensure_future

from aio_pika import IncomingMessage

from util import RabbitmqPool

def handle(msg: IncomingMessage):
    print(msg.info())
    print(msg.body)

async def main():
    pool = RabbitmqPool()
    await pool.init(
        addr="127.0.0.1",
        port="5672",
        vhost="message",
        username="guest",
        password="guest",
        max_size=10,
    )
    pool.subscribe("test", handle)

async def publish():
    pool = RabbitmqPool()
    await pool.init(
        addr="127.0.0.1",
        port="5672",
        vhost="message",
        username="guest",
        password="guest",
        max_size=10,
    )
    pool.publish("test", b"F@ck the world")

if __name__ == "__main__":
    ensure_future(publish())
    get_event_loop().run_forever()

    
