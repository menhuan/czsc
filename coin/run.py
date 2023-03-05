
"""
币安数据会存在很多个币种，虽然很多，但是我们并不是所有都需要。
如果我们可以配置多个自己选的币种。这里主要是采集数据。

"""
import os
import time
from collections import OrderedDict
import threading

from loguru import logger
from czsc.objects import  BiFreq ,Freq
from bian_coin import kline
from czsc.data.coin_cache import BiAnDataCache
from db.mongo_db import binance_mongo
import json

from czsc.traders import check_signals_acc
from czsc.traders.base import CzscTraderBICoin
from czsc.signals.bxt import get_s_like_bs


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
def interval_time_end_time(start_time ,freq):
    interval_times = os.getenv("times_interval" ,500)
    end_time = start_time + 500 * get_time(freq)
    return end_time

symbols = os.getenv("symbols" ,"BTCUSDT")
def run():
    # 采集的开始时间，后面需要更换时间
    sleep_time = os.getenv("sleep_time" ,10)
    # 当前时间
    end_time = time.time() * 1000
    # 这个时间戳下面的才进行数据采集
    for symbol in symbols.split(","):
        for _,v in BiFreq.__members__.items():
            data_count = 0
            start_time = os.getenv("collect_time", 1512057600000)
            if v not in (BiFreq.M ,BiFreq.W  ,BiFreq.F1):
                collect_name = symbol + "_" + v.value

                doucments = binance_mongo.find_all_sort_by__id(collect_name,-1)
                if doucments and len(doucments) > 0  :
                    start_time = doucments[0].get("_id")

                # 小于这个时间就继续获取数据
                # 获取开始时间
                while start_time < end_time:
                    interval_time = interval_time_end_time(start_time, v)
                    # 根据时间戳获取数据
                    bars = kline(symbol ,interval=v.value,startTime=start_time ,endTime=interval_time)

                    for bar in bars:
                        update = {"$set": bar}
                        document = binance_mongo.find_one_and_update(collect_name,{"_id": bar.get("_id")},update)
                        if document:
                            logger.error(f"更新和查询数据失败，请检查:{update}")
                    data_count = data_count + len(bars)
                    time.sleep(sleep_time)
                    start_time = interval_time
                    logger.info(f"更新数据进行到{data_count},当前时间是:{start_time},结束时间是：{end_time}")
                else:
                    logger.info(f"该币种{symbol}在该时间{v}数据爬取完毕,数据总条数是:{data_count}")


def get_signals(cat: CzscTraderBICoin) -> OrderedDict:
    s = OrderedDict({"symbol": cat.symbol, "dt": cat.end_dt, "close": cat.latest_price})
    # 使用缓存来更新信号的方法
    s.update(get_s_like_bs(cat.kas[Freq.F30.value], di=1))
    #s.update(zhen_cang_tu_po_V230204(cat.kas['5分钟'], di=1,n=10))
    #s.update(zhen_cang_tu_po_V230204(cat.kas['30分钟'], di=1,n=10))
    return s

def trader_strategy_base(symbol):
    tactic = {
        "symbol": symbol,
        "base_freq": '15分钟',
        "freqs": ['30分钟', '60分钟',Freq.F4H.value ,Freq.D.value,Freq.W.value],
        "get_signals": get_signals,
        "signals_n": 0,
    }
    return tactic



def notice():
    # 通知，判断是否是要检测的新号，然后发送通知。
    for symbol in symbols.split(","):
        data_path = os.path.join(f"./{symbol}")
        dc = BiAnDataCache(data_path, sdt='2010-01-01', edt='20211209')
        bars = dc.bian_btc_daily(ts_code=symbol, raw_bar=True, interval=BiFreq.F30.value, frep=Freq.F30)
        check_signals_acc(bars,get_signals=get_signals,time_delay=24*60*60,strategy=trader_strategy_base)

if __name__ == '__main__':
    t1 = threading.Thread(target=run)
    t2 = threading.Thread(target=notice)
    t1.start()
    t2.start()
