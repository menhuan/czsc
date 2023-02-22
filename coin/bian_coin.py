# 币安数据获取
from typing import List

import requests

from czsc.objects import Freq,RawBar
import pandas as pd



"""
startTime: 1674802800000，时间戳
"""
def kline(symbol: str = "BTCUSDT",
          interval: str = Freq.F5.val,
          startTime: int = None,
          endTime: int = None,
          limit: int = 1000) -> List[RawBar]:
    request_params = {"symbol": symbol, "interval": interval, "limit": limit, "startTime": startTime,
                      "endTime": endTime}
    response = requests.get("https://api4.binance.com/api/v3/klines", request_params)
    bars = []
    for index, content in enumerate(response.json()):
        # 将每一根K线转换成 RawBar 对象
        bar = RawBar(symbol="BTCUSDT", dt=pd.to_datetime(content[0]),
                     id=index, freq="5min", open=content[1], close=content[4],
                     high=content[2], low=content[3],
                     vol=content[5],  # 成交量，单位：股
                     amount=content[7],  # 成交额，单位：元
                     )
        bars.append(bar)
    return bars
