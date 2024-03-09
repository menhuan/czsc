from enum import Enum
from typing import List

import requests

from loguru import logger
import pandas as pd

"""
startTime: 1674802800000，时间戳
"""
class BIFreq(Enum):
    F1 = "1m"
    F5 = "5m"
    F15 = "15m"
    F30 = "30m"
    F60 = "1h"
    F4H = "4h"
    D = "1d"
    W = "1w"
    M = "1M"

def binance_kline(request):
    response = requests.get("https://api4.binance.com/api/v3/klines", request)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("请求变binance数据失败！")
    
    
    


def kline(symbol: str = "BTCUSDT",
          interval: str = BIFreq.F5.value,
          startTime: int = None,
          endTime: int = None,
          limit: int = 1000) -> List[dict]:
    request_params = {"symbol": symbol, "interval": interval, "limit": limit, "startTime": startTime,
                      "endTime": endTime}
    logger.info(f"当前请求时间是参数是：{request_params}")
    binance_response = binance_kline(request_params)
    return binance_response

def transfrom_bian_kline_to_df(binance_response: dict) :
    bars = []
    for index, content in enumerate(binance_response):
        # 将每一根K线转换成 RawBar 对象
        bar = dict(symbol=symbol, dt=content[0] + 8 * 60 * 60 * 1000,
                    id=index, freq=interval, open=content[1], close=content[4],
                    high=content[2], low=content[3],
                    vol=content[5],  # 成交量，单位：股
                    amount=content[7],  # 成交额，单位：元
                    _id=(content[0] + 8 * 60 * 60 * 1000)
                    )
        bars.append(bar)
    if not bars:
        logger.info(f"查询数据有问题:request:{request_params},response :{response.json()},status_code :{response.status_code}")
    return bars