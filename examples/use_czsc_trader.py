# -*- coding: utf-8 -*-
"""
author: zengbin93
email: zeng_bin8888@163.com
create_dt: 2023/1/30 13:32
describe: CzscTrader 使用案例
"""
import random
import sys

from czsc.objects import BiFreq,Freq
from data.coin_cache import BiAnDataCache
from utils import BarGenerator

sys.path.insert(0, '.')
sys.path.insert(0, '..')

import os
from examples.strategies.czsc_strategy_sma5 import CzscStrategySMA5
from czsc.strategies import CzscStrategyCoin

os.environ['czsc_verbose'] = '1'


def use_czsc_trader_by_tushare():
    from czsc.data.ts_cache import TsDataCache
    dc = TsDataCache(r'C:\ts_data', sdt='2010-01-01', edt='20211209')

    symbol = '000001.SZ'
    bars = dc.pro_bar_minutes(ts_code=symbol, asset='E', freq='15min',
                              sdt='20151101', edt='20210101', adj='hfq', raw_bar=True)

    tactic = CzscStrategySMA5(symbol=symbol)
    # trader = tactic.init_trader(bars, sdt='20200801')
    trader = tactic.replay(bars, res_path=r"C:\ts_data_czsc\trade_replay_test_c", sdt='20170101', refresh=True)
    print(trader.positions[0].evaluate_pairs())


def use_czsc_trader_by_qmt():
    from czsc.connectors import qmt_connector as qmc

    symbol = '000001.SZ'
    tactic = CzscStrategySMA5(symbol=symbol)
    bars = qmc.get_raw_bars(symbol, freq=tactic.sorted_freqs[0], sdt='20151101', edt='20210101', fq="后复权")
    print(bars[-1])

    # 初始化交易对象
    # trader = tactic.init_trader(bars, sdt='20200801')

    # 执行策略回放，生成交易快照文件
    trader = tactic.replay(bars, res_path=r"C:\ts_data_czsc\trade_replay_test", sdt='20170101', refresh=True)
    print(trader.positions[0].evaluate_pairs())


def example_qmt_manager():
    """使用 QmtTradeManager 进行交易"""
    from czsc.connectors import qmt_connector as qmc

    symbols = ['600000.SH', '600004.SH', '600006.SH', '600007.SH']
    manager = qmc.QmtTradeManager(mini_qmt_dir=r'D:\国金QMT交易端模拟\userdata_mini', account_id='55002763',
                                  symbols=symbols, symbol_max_pos=0.3, strategy=CzscStrategySMA5)
    manager.run()




if __name__ == '__main__':
    data_path1 = "/Users/ruiqi/data/code/czsc/examples/data_path" + "4"
    if os.path.exists(data_path1):
        import shutil
        shutil.rmtree(data_path1)
    from czsc.data.ts_cache import TsDataCache
    data_path = r'./cache_data1'
    dc = BiAnDataCache(data_path, sdt='2010-01-01', edt='20211209')

    symbol = 'BNBUSDT'
    bars = dc.bian_btc_daily(ts_code=symbol, raw_bar=True, interval=BiFreq.F30.value, frep=Freq.F30)

    tactic = CzscStrategyCoin(symbol=symbol)
    # K线合成器，这是多级别联立分析的数据支撑。从30分钟线合成4小时,日线
    # bg = BarGenerator(base_freq=Freq.F30.value, freqs=[Freq.F4H.value, Freq.D.value], max_count=5000)
    # for bar in bars:
    #     bg.update(bar)

    tactic.replay(bars,res_path=data_path1,sdt="2023-02-21 12:00:00",n=500,refresh=True,exist_ok=True)



    # trader = tactic.replay(bars, res_path=r"C:\ts_data_czsc\trade_replay_test_c", sdt='20170101')

