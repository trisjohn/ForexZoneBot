from datetime import datetime
from dataobjects import TwinData, build_zone_data
import numpy as np
import MetaTrader5 as mt5

def get_format_ohlc(symbol, timeframe, n, curr_time:datetime):
    """
    Pulls from the data server to construct bars out of ticks
    """
    data_raw = mt5.copy_rates_from_pos(symbol, timeframe, 0, n)
    columns = data_raw.dtype.names
    print(data_raw)
    # data['time'] = pd.to_datetime(data['time'], unit='s')
    return columns, np.flip(data_raw)

class DataManager:
    """
    Responsible for all data fethcing, processing, handling, and saving
    """
    def __init__(self, data_size=100):
        self.data = dict() # Dictionary that where key is Symbol and value is data
        self.long_tf = 0
        self.short_tf = 0
        self.data_size = data_size

    def set_time_frames(self,long_tf:int, short_tf:int):
        """
        Sets the time frames for the data to be loaded
        """
        self.long_tf = long_tf
        self.short_tf = short_tf

    def set_symbols(self,symbols):
        for s in symbols:
            self.data[s] = TwinData()

    def reload_data(self):
        """
        Reach out to the MT5 server and grab the necessary data
        then process and format it
        """
        for s in self.data:
            # Grab all new data
            if self.data[s].is_empty():
                long_data = build_zone_data(get_format_ohlc(s,self.long_tf,self.data_size, datetime.utcnow()))
                self.data[s]
            else:

                self.data[s].try_update()
        
