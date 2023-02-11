import requests
import pandas as pd 


from czsc.objects import RawBar

def test_kline():
    request_params ={"symbol": "BTCUSDT","interval":"5m","limit":500, "startTime":1674802800000, "endTime":1674889200000}
    response = requests.get("https://api4.binance.com/api/v3/klines",request_params)
    print("输出k线数据",response.json())
    bars = []
    for index, content in enumerate(response.json()):
        # 将每一根K线转换成 RawBar 对象
        bar = RawBar(symbol="BTCUSDT", dt=pd.to_datetime(content[0]),
                        id=index,freq="5min", open=content[1], close=content[4],
                        high=content[2], low=content[3],
                        vol=content[5],          # 成交量，单位：股
                        amount=content[7],    # 成交额，单位：元
                        )
        bars.append(bar)
    print(bars)
if __name__ == '__main__':
    test_kline()