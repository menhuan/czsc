# -*- coding: utf-8 -*-
"""
author: zengbin93
email: zeng_bin8888@163.com
create_dt: 2021/12/13 17:48
describe: 验证信号计算的准确性，仅适用于缠论笔相关的信号，
          技术指标构建的信号，用这个工具检查不是那么方便
"""
import sys

from signals.bxt import get_s_three_bi, check_five_bi, get_s_like_bs
from traders import check_signals_acc

sys.path.insert(0, '..')
import os
from typing import List
from collections import OrderedDict
from czsc.data.coin_cache import BiAnDataCache
from czsc import CZSC, CzscSignals
from czsc.objects import Signal, Freq, RawBar,BiFreq
from czsc.utils import get_sub_elements


os.environ['czsc_verbose'] = '1'

data_path = r'./cache_data'
dc = BiAnDataCache(data_path, sdt='2010-01-01', edt='20211209')

symbol = 'BNBUSDT'
bars = dc.bian_btc_daily(ts_code=symbol, raw_bar=True,interval=BiFreq.F30.value,frep=Freq.F30)


def zhen_cang_tu_po_V230204(c: CZSC, **kwargs) -> OrderedDict:
    """震仓突破形态信号

    **信号描述：**
        -多头描述（空头反之）：
        大实体阴线破小级别中枢
        大实体阳线快速拉回

    **信号列表：**

    - Signal('1分钟_震仓_突破_向上_任意_任意_0')
    - Signal('1分钟_震仓_突破_向下_任意_任意_0')

    :param c: CZSC 对象
    :return: 信号字典

    **处理流程：**

    1. 往前取20k，取成功则继续 and 本k是阳线，成功则继续
    2. 包括本k在内，最近3k 有一条大实体阳线，成功则继续
    3. 大实体阳线左边3k内，有一条大实体阴线(这条大阴线不一定是下穿低级别中枢的，这里只是过滤)，成功则继续
    4. 从当前位置（4找到的大实体阴线）开始往左，2k内，看能否找到 包含左边全部3k 的实体阴线
      5.1. 如果下穿成立，记录所有下穿成立的k的high的最大值maxgg
    6. 如果有找到maxgg，且本k的收盘价大于maxgg，则发出信号（这里没有要求本k是大实体阳线，只要阳线，按第4条要求，近3k有大实体阳线就可）

    **处理流程：**

    1. 往前取20k，取成功则继续 and 本k是阳线
    2. 小窗口N，大窗口M，


    """
    n = kwargs.get('n', 20)
    m = kwargs.get('m', 3)

    v1 = '其他'
    last_bars: List[RawBar] = get_sub_elements(c.bars_raw, di=1, n=n)

    def __is_overlap(_bars):
        if min([bar.high for bar in _bars]) > max([bar.low for bar in _bars]):
            return True, min([bar.low for bar in _bars])
        else:
            return False, None

    if len(last_bars) == 20 and last_bars[-1].close > last_bars[-1].open:
        c1_a = last_bars[-1].high == max([bar.high for bar in last_bars])
        c1_b = last_bars[-1].close == max([bar.close for bar in last_bars])
        c1 = c1_a or c1_b

        c2 = False
        right_bars = []
        dd = 0
        for i in range(m, n-m):
            c2, dd = __is_overlap(last_bars[-i-m:-i])
            if c2:
                right_bars = last_bars[-i:]
                break

        c3 = min([bar.low for bar in right_bars]) < dd if right_bars else False

        if c1 and c2 and c3:
            v1 = "满足"

    s = OrderedDict()
    k1, k2, k3 = f"{c.freq.value}_N{n}M{m}_震仓突破".split("_")
    v = Signal(k1=k1, k2=k2, k3=k3, v1=v1)
    s[v.key] = v.value
    return s


def get_signals(cat: CzscSignals) -> OrderedDict:
    s = OrderedDict({"symbol": cat.symbol, "dt": cat.end_dt, "close": cat.latest_price})
    # 使用缓存来更新信号的方法
    s.update(zhen_cang_tu_po_V230204(cat.kas[Freq.F30.value], di=1,n=10))
    s.update(get_s_three_bi(cat.kas[Freq.F30.value], di=1))
    s.update(get_s_three_bi(cat.kas[Freq.F30.value], di=1))
    #s.update(zhen_cang_tu_po_V230204(cat.kas['5分钟'], di=1,n=10))
    #s.update(zhen_cang_tu_po_V230204(cat.kas['30分钟'], di=1,n=10))
    return s


def trader_strategy_base(symbol):
    tactic = {
        "symbol": symbol,
        "base_freq": Freq.F30.value,
        "freqs": [Freq.F60.value, Freq.F4H.value,Freq.D.value],
        "get_signals": get_signals,
        "signals_n": 0,
    }
    return tactic


if __name__ == '__main__':
    # 直接查看全部信号的隔日快照
    for symbol in ["BTCUSDT"]:
        dc = BiAnDataCache(data_path, sdt='2010-01-01', edt='20211209')
        bars = dc.bian_btc_daily(ts_code=symbol, raw_bar=True, interval=BiFreq.F30.value, frep=Freq.F30)
        check_signals_acc(bars,get_signals=get_signals,strategy=trader_strategy_base)
# 查看指定信号的隔日快照
    # signals = [
    #     Signal('5分钟_N10M3_震仓突破_向上_任意_任意_0'),
    #     Signal("15分钟_N10M3_震仓突破_向上_任意_任意_0"),
    # ]
    # check_signals_acc(bars, signals=signals, strategy=trader_strategy_base)






