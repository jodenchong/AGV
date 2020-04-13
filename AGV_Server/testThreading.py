import asyncio
import threading
testEve1 = threading.Event()
testEve2 = threading.Event()
async def test1():
    while testEve1.is_set():
        await asyncio.sleep(1)
        print("test1")


async def test2():
    while testEve2.is_set():
        await asyncio.sleep(1)
        print("test2...")


loop = asyncio.get_event_loop()
try:
    testEve1.set()
    testEve2.set()
    asyncio.ensure_future(test1())
    asyncio.ensure_future(test2())
    loop.run_forever()
except KeyboardInterrupt:
    testEve1.clear()
    testEve2.clear()
finally:
    print("close")
    loop.close()