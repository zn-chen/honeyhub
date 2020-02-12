# -*- coding: utf-8 -*-
from logging import getLogger
from inspect import isawaitable
from functools import wraps, partial
from asyncio import ensure_future, Future
from concurrent.futures import CancelledError

from util.executor import AsyncExecutor


def launcher(func):
    """
    协程启动器
    """

    def coro_logger(func_name: str, future: Future) -> None:
        """协程异常捕获器"""
        try:
            future.result()
        except (ConnectionError, CancelledError):
            pass
        except Exception as ex:
            getLogger().exception(r"Uncaught exception in async function %s! %s", func_name, ex.__str__())

    @wraps(func)
    def wrapper(*args, **kwargs) -> object:
        """装饰器创建的新方法"""
        result = func(*args, **kwargs)
        if isawaitable(result):
            task = ensure_future(result)
            task.add_done_callback(partial(coro_logger, func.__name__))

            result = task

        return result

    return wrapper


def async_threading(func):
    """
    在已经初始化了的线程池中运行一个阻塞函数
    ps: 注意线程安全,注意不要大量使用, 注意不要用于cpu密集型工作
    """

    @wraps(func)
    async def wrapper(*args, **kwargs) -> object:
        result = await AsyncExecutor().add_thread(func, *args, **kwargs)
        return result

    return wrapper
