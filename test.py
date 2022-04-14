from dataobjects import build_zone_data
from datamanager import get_format_ohlc
from datetime import datetime, timedelta
import MetaTrader5 as mt5

mt5.initialize()
symbols = mt5.symbols_total()
if symbols > 0:
    print("Total symbols =", symbols)
else:
    print("no symbols found")
data_raw = mt5.copy_ticks_from("EURUSD", datetime.utcnow()-timedelta(hours=6), 10000, mt5.COPY_TICKS_ALL)
columns = data_raw.dtype.names
print(data_raw[:1][0])
print(datetime.utcnow(), datetime.fromtimestamp(data_raw[0][0]), datetime.fromtimestamp(data_raw[-1][0]))