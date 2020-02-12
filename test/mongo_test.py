import motor.motor_asyncio
from asyncio import get_event_loop


async def main():
    client = motor.motor_asyncio.AsyncIOMotorClient(
        host="127.0.0.1",
        port=27017,
        maxPoolSize=10,
        minPoolSize=5
    )
    db = client["testdb"]
    col = db["testcollection"]
    await col.insert_one({"jus": "fuck"})

if __name__ == "__main__":
    get_event_loop().run_until_complete(main())
