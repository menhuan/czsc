

"""
币安数据会存在很多个币种，虽然很多，但是我们并不是所有都需要。
如果我们可以配置多个自己选的币种。这里主要是采集数据。

"""
import os
import time
from loguru import logger
from czsc.objects import  BiFreq
from bian_coin import kline
from db.mongo_db import binance_mongo
import json

def get_time(freq):
    return {
        BiFreq.F1: 60 * 1000,
        BiFreq.F5: 5 * 60 * 1000,
        BiFreq.F15: 15 * 60 * 1000,
        BiFreq.F30: 30 * 60 * 1000,
        BiFreq.F60: 60 * 60 * 1000,
        BiFreq.F4H: 4 * 60 * 60 * 1000,
        BiFreq.D: 24 * 60 * 60 * 1000,
    }.get(freq)

# 用来计算时间间隔，每次调用的时间间隔数据,按照一次500来计算吧
def interval_time_end_time(start_time,freq):
    interval_times = os.getenv("times_interval",500)
    end_time = start_time + 500 * get_time(freq)
    return end_time

def run():
    symbols = os.getenv("symbols","BTCUSDT,ETHUSDT,DYDXUSDT")
    # 采集的开始时间，后面需要更换时间
    start_time = os.getenv("collect_time",1512057600000)
    # 当前时间
    end_time = time.time() * 1000

    # 这个时间戳下面的才进行数据采集
    for k,v in BiFreq.__members__.items():
        if k not in (BiFreq.M,BiFreq.W,BiFreq.F1):
            # 小于这个时间就继续获取数据
            interval_time = interval_time_end_time(start_time, k)
            if interval_time < end_time:
                # 根据时间戳获取数据
                for symbol in symbols.split(","):
                    bars = kline(symbol,interval=k,startTime=start_time,endTime=interval_time)
                    #获取币种
                    binance_mongo.insert(json.dumps(bars))

                    pass
            else:
                logger.info(f"该币种{symbol}在该时间{v}数据爬取完毕,")
            # 请求有时间限制
            time.sleep(1)

    pass
