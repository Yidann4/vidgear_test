import asyncio

from stages.fanout import Hub, pack, unpack


def test_pack_unpack_roundtrip():
    assert unpack(pack({"seq": 1}, b"jpg")) == ({"seq": 1}, b"jpg")


def test_hub_keeps_only_latest():
    async def run():
        hub = Hub()
        q = hub.subscribe()
        for i in range(3):
            hub.publish(bytes([i]))
        assert await q.get() == b"\x02"
        assert q.empty()

    asyncio.run(run())


def test_hub_fans_out_to_all_subscribers():
    async def run():
        hub = Hub()
        a, b = hub.subscribe(), hub.subscribe()
        hub.publish(b"x")
        assert await a.get() == await b.get() == b"x"

    asyncio.run(run())
