# -*- coding: utf-8 -*-
"""
author: zengbin93
email: zeng_bin8888@163.com
create_dt: 2021/10/24 16:12
describe:
币安数据 数据缓存，这是用pickle缓存数据，是临时性的缓存。
单次缓存，多次使用，但是不做增量更新，适用于研究场景。
数据缓存是一种用空间换时间的方法，需要有较大磁盘空间，跑全市场至少需要50GB以上。
后面这里会换成从数据库读取数据，外部有专门存储数据到mong中供自己使用。
"""
import os.path
import shutil

import loguru
import pandas as pd
from tqdm import tqdm
from typing import List
from deprecated import deprecated
from datetime import timedelta, datetime
from czsc import envs
from czsc.enums import BiFreq, Freq
from czsc.objects import RawBar
from czsc.data.ts import pro
import requests


class BiAnDataCache:
    """币安数据 数据缓存"""

    def __init__(self, data_path, refresh=False, sdt="20120101", edt=datetime.now()):
        """
        :param data_path: 数据路径
        :param refresh: 是否刷新缓存
        :param sdt: 缓存开始时间
        :param edt: 缓存结束时间
        """
        self.date_fmt = "%Y%m%d"
        self.verbose = envs.get_verbose()
        self.refresh = refresh
        self.sdt = pd.to_datetime(sdt).strftime(self.date_fmt)
        self.edt = pd.to_datetime(edt).strftime(self.date_fmt)
        self.data_path = data_path
        self.prefix = "TS_CACHE"
        self.cache_path = os.path.join(self.data_path, self.prefix)
        os.makedirs(self.cache_path, exist_ok=True)
        self.pro = pro
        self.__prepare_api_path()

        self.freq_map = {
            "1min": Freq.F1,
            "5min": Freq.F5,
            "15min": Freq.F15,
            "30min": Freq.F30,
            "60min": Freq.F60,
            "4h": Freq.F4H,
            "D": Freq.D,
            "W": Freq.W,
            "M": Freq.M,
        }

    def __prepare_api_path(self):
        """给每个tushare数据接口创建一个缓存路径"""
        cache_path = self.cache_path
        self.api_names = [
            'ths_daily', 'ths_index', 'ths_member', 'pro_bar',
            'hk_hold', 'cctv_news', 'daily_basic', 'index_weight',
            'pro_bar_minutes', 'limit_list', 'bak_basic',

            # CZSC加工缓存
            "stocks_daily_bars", "stocks_daily_basic", "stocks_daily_bak",
            "daily_basic_new", "stocks_daily_basic_new"
        ]
        self.api_path_map = {k: os.path.join(cache_path, k) for k in self.api_names}

        for k, path in self.api_path_map.items():
            os.makedirs(path, exist_ok=True)

    def clear(self):
        """清空缓存"""
        for path in os.listdir(self.data_path):
            if path.startswith(self.prefix):
                path = os.path.join(self.data_path, path)
                shutil.rmtree(path)
                if self.verbose:
                    print(f"clear: remove {path}")
                if os.path.exists(path):
                    print(f"Tushare 数据缓存清理失败，请手动删除缓存文件夹：{self.cache_path}")

    # ------------------------------------币安原生接口---------------------------------------------------
    """s -> 秒; m -> 分钟; h -> 小时; d -> 天; w -> 周; M -> 月
    1s  1m  3m  5m 15m 30m 1h 2h 4h 6h 8h 12h 1d 3d 1w 1M
    BTCUSDT,这样形式的内容输出.

    """

    def bian_btc_daily(self, ts_code, start_date=None, end_date=None, raw_bar=True, interval=BiFreq.F5.value, limit=1000,
                       frep=Freq.F5):
        cache_path = self.api_path_map['ths_daily']
        file_cache = os.path.join(cache_path, f"ths_daily_{ts_code}_sdt{self.sdt}.feather")
        bars = []
        if not self.refresh and os.path.exists(file_cache):
            bars = pd.read_feather(file_cache)
            if self.verbose:
                print(f"ths_daily: read cache {file_cache}")
        else:
            request_params = {"symbol": ts_code, "interval": interval, "startTime": start_date, "endTime": end_date,
                              "limit": limit}
            response = requests.get("https://api4.binance.com/api/v3/klines", request_params)
            #print("接收到的数据为",response.json(),"请求数据是",request_params)
            if response.status_code == 200 :
                for index, content in enumerate(response.json()):
                    # 将每一根K线转换成 RawBar 对象
                    bar = RawBar(symbol="BTCUSDT", dt=pd.to_datetime(content[0] / 1000, unit="s"),
                                 id=index, freq=frep, open=float(content[1]), close=float(content[4]),
                                 high=float(content[2]), low=float(content[3]),
                                 vol=content[5],  # 成交量
                                 amount=content[7],  # 成交额，默认单位
                                 )
                    bars.append(bar)
            else:
                loguru.Logger.info(f"请求接口失败，return response:{response.json()}")
            # df = pd.array(bars)
            # df.to_feather(bars)
        #print(f"转换完k线结果输出{bars}")
        return bars



