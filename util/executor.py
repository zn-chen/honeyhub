# -*- coding: utf-8 -*-
"""多线程 / 多进程 执行器模块"""
from shlex import quote
from functools import partial
from typing import Callable, Optional
from subprocess import getoutput, getstatusoutput
from asyncio import AbstractEventLoop, get_event_loop
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

from util.singleton import Singleton


class ProcessPoolDisabledException(Exception):
    """进程池已禁用异常"""


class AsyncExecutor(Singleton):
    """多线程 / 多进程 执行器"""

    def __init__(self, thread_workers: int = 0, process_workers: int = 0, ioloop: AbstractEventLoop = None):
        """构造器"""
        self._thread_pool = None
        self._process_pool = None
        self._ioloop = ioloop or get_event_loop()

        if thread_workers and thread_workers > 0:
            self._thread_pool = ThreadPoolExecutor(thread_workers)

        if process_workers and process_workers > 0:
            self._process_pool = ProcessPoolExecutor(process_workers)

    async def add_thread(self, _callable: Callable, *args: tuple, **kwargs: dict) -> Optional[object]:
        """将指定的函数添加至线程池中执行并等待完成后取得结果"""
        func = partial(_callable, *args, **kwargs)
        return await self._ioloop.run_in_executor(self._thread_pool, func)

    async def add_process(self, _callable: Callable, *args: tuple, **kwargs: dict) -> Optional[object]:
        """将指定的函数添加至进程池中执行并等待完成后取得结果"""
        if self._process_pool is None:
            raise ProcessPoolDisabledException()

        func = partial(_callable, *args, **kwargs)
        return await self._ioloop.run_in_executor(self._process_pool, func)

    async def shell(self, cmd: str, *params: tuple) -> str:
        """调用命令并获得输出

        ``params``：当命令存在参数时，可以将参数放入此变量中，函数将自动进行变量转义以保证安全。
        """
        cmd = self._quote_params(cmd, *params)
        return await self.add_thread(lambda: getoutput(cmd))

    async def shell_extend(self, cmd: str, *params: tuple) -> tuple:
        """调用命令并获得状态码与输出

        ``params``：当命令存在参数时，可以将参数放入此变量中，函数将自动进行变量转义以保证安全。
        """
        cmd = self._quote_params(cmd, *params)
        return await self.add_thread(lambda: getstatusoutput(cmd))

    def _quote_params(self, cmd: str, *params):
        """安全转义参数"""
        if params:
            params = (quote(param) for param in params)
            cmd = " ".join([cmd, *params])

        return cmd

    @classmethod
    def initialize(cls, thread_workers: int, process_workers: int):
        """初始化执行器

        执行器在启动前需要对内部线程池和进程池进行初始化
        """
        return cls(thread_workers, process_workers)
