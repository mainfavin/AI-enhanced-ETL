import asyncio
from multiprocessing import freeze_support
from src.application.multipipelines.multipipeline import MultiplePipeline



async def main():
    freeze_support()
    multipi = MultiplePipeline("config/multipipeline.yaml")
    await multipi.run()
asyncio.run(main())