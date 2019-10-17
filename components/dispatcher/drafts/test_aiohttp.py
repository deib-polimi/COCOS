from aiohttp import web
import asyncio


async def handle(request):
    my_task = asyncio.Event()
    loop = asyncio.get_event_loop()
    loop.call_later(10, done, my_task)
    print("Before await")

    await my_task.wait()  # await until event would be .set()

    print("After await")

    name = request.match_info.get('name', "Anonymous")
    text = "Hello, " + name
    return web.Response(text=text)


async def wait_until_done():
    await my_task.wait()  # await until event would be .set()
    print("Finally, the task is done")


def done(my_task):
    my_task.set()


app = web.Application()
app.add_routes([web.get('/', handle),
                web.get('/{name}', handle)])


if __name__ == '__main__':
    web.run_app(app)