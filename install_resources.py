import asyncio
import tornado
from tornado import ioloop

from worker.core.config import ConfigManager


async def main():
    # resources = ResourcesSingleton()
    # await resources.initialize(overwrite=True)
    print("Hello from {}".format(__file__))
    await asyncio.sleep(1)


if __name__ == "__main__":
    tornado.log.enable_pretty_logging()
    tornado.options.parse_command_line()
    io_loop = ioloop.IOLoop.current()
    io_loop.run_sync(main)
