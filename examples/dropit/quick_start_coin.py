# -*- coding: utf-8 -*-
"""
author: zengbin93
email: zeng_bin8888@163.com
create_dt: 2022/4/27 21:51
describe: 以 Tushare 数据为例编写快速入门样例
"""
import os
import pandas as pd
from collections import OrderedDict
from czsc import  Freq, BiFreq
from czsc.traders.base import CzscAdvancedTrader
from czsc.utils import BarGenerator
from czsc import signals
from data.coin_cache import BiAnDataCache
from strategies import CzscStrategyCoin

os.environ['czsc_verbose'] = "1"        # 是否输出详细执行信息，0 不输出，1 输出
os.environ['czsc_min_bi_len'] = "6"     # 通过环境变量设定最小笔长度，6 对应新笔定义，7 对应老笔定义
pd.set_option('mode.chained_assignment', None)
pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns', 20)


# 在浏览器中查看单标的单级别的分型、笔识别结果
data_path = r'./cache_data1'
dc = BiAnDataCache(data_path, sdt='2010-01-01', edt='20211209')

symbol = 'DYDXUSDT'
bars = dc.bian_btc_daily(ts_code=symbol, raw_bar=True, interval=BiFreq.F30.value, frep=Freq.F30)

tactic = CzscStrategyCoin(symbol=symbol)
# K线合成器，这是多级别联立分析的数据支撑。从30分钟线合成4小时,日线
bg = BarGenerator(base_freq=Freq.F30.value, freqs=[Freq.F4H.value, Freq.D.value], max_count=5000)
for bar in bars:
    bg.update(bar)

# K线逐K合成结束后，通过 bg.bars 可以获取各周期K线
print("K线合成器中存下来的K线周期列表：", list(bg.bars.keys()))

# 通过K线合成器获取周线
bars_4h = bg.bars[Freq.F4H.value]


# 定义一些需要观察的信号，可以是多级别同时计算
def get_simple_signals(cat: CzscAdvancedTrader) -> OrderedDict:
    s = OrderedDict({"symbol": cat.symbol, "dt": cat.end_dt, "close": cat.latest_price})
    for _, c in cat.kas.items():
        if c.freq == Freq.F4H:
            s.update(signals.bxt.get_s_three_bi(c, di=1))
            s.update(signals.bxt.get_s_base_xt(c, di=1))

        if c.freq == Freq.D:
            s.update(signals.bxt.get_s_three_bi(c, di=1))
            s.update(signals.bxt.get_s_base_xt(c, di=1))

        if c.freq == Freq.W:
            s.update(signals.ta.get_s_macd(c, di=1))
            s.update(signals.ta.get_s_sma(c, di=1, t_seq=(5, 20, 60)))
    return s


def simple_strategy(symbol):
    return {"symbol": symbol, "get_signals": get_simple_signals}


cat = CzscAdvancedTrader(bg, simple_strategy)
cat.open_in_browser()

