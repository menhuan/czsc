# -*- coding: utf-8 -*-
"""
author: zengbin93
email: zeng_bin8888@163.com
create_dt: 2023/1/30 13:32
describe: CzscTrader 使用案例
"""
import sys

sys.path.insert(0, '.')
sys.path.insert(0, '..')

import os
from examples.strategies.czsc_strategy_sma5 import CzscStrategySMA5

os.environ['czsc_verbose'] = '1'


def use_czsc_trader_by_tushare():
    from czsc.data.ts_cache import TsDataCache
    dc = TsDataCache(r'C:\ts_data', sdt='2010-01-01', edt='20211209')

    symbol = '000001.SZ'
    bars = dc.pro_bar_minutes(ts_code=symbol, asset='E', freq='5min',
                              sdt='20151101', edt='20210101', adj='hfq', raw_bar=True)

    tactic = CzscStrategySMA5(symbol=symbol)
    trader = tactic.init_trader(bars, sdt='20200801')
    # trader = tactic.replay(bars, res_path=r"C:\ts_data_czsc\trade_replay_test_c", sdt='20170101')
    print(trader.positions[0].evaluate_pairs())


def use_czsc_trader_by_qmt():
    from czsc.connectors import qmt_connector as qmc

    symbol = '000001.SZ'
    bars = qmc.get_kline(symbol, period='5m', start_time='20151101', end_time='20210101',
                         dividend_type='back', download_hist=True, df=False)
    tactic = CzscStrategySMA5(symbol=symbol)
    # 初始化交易对象
    # trader = tactic.init_trader(bars, sdt='20200801')

    # 执行策略回放，生成交易快照文件
    trader = tactic.replay(bars, res_path=r"C:\ts_data_czsc\trade_replay_test_c", sdt='20170101')
    print(trader.positions[0].evaluate_pairs())


def example_qmt_manager():
    """使用 QmtTradeManager 进行交易"""
    from czsc.connectors import qmt_connector as qmc

    symbols = ['600000.SH', '600004.SH', '600006.SH', '600007.SH']
    manager = qmc.QmtTradeManager(mini_qmt_dir=r'D:\国金QMT交易端模拟\userdata_mini', account_id='55002763',
                                  symbols=symbols, symbol_max_pos=0.3, strategy=CzscStrategySMA5, period='5m')
    manager.run()






