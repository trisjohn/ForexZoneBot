from collections import deque
from dataclasses import dataclass
import pandas as pd
from datetime import datetime, timedelta
from enum import Enum, auto
import numpy as np

class Price(Enum):
    Open = auto()
    High = auto()
    Low = auto()
    Close = auto()
    Volume = auto()
    Time = auto()

def price_string(name:Price):
    string = "open"
    if name == Price.High:
        string = "high"
    elif name == Price.Low:
        string = "low"
    elif name == Price.Close:
        string = "close"
    elif name == Price.Volume:
        string = "volume"
    elif name == Price.Time:
        string = "time"
    return string

@dataclass
class Bar:
    """
    Class for holding a piece of open, high, low, close, volume (tick_volume) data
    for a specific piece of time
    """
    open: float
    high: float
    low: float
    close: float
    volume: float
    time: datetime
    switch = {}

    def get(self,name:Price):
        """
        Returns the correct value given the type Price Enum
        """
        if not self.switch:
            self.switch = {
                Price.Open : self.open,
                Price.High : self.high,
                Price.Low : self.low,
                Price.Close : self.close,
                Price.Volume : self.volume,
                Price.Time : self.time
            }

        return self.switch.get(name)
    
    def is_valid(self, most_recent, tf):
        """
        Determine if this bar is valid by checking it against the most recent
        its time must be greater than or equal most_recent + tf
        if nothing is passed in most_recent, returns true
        """
        if not most_recent:
            return True
        return self.time >= most_recent.time + timedelta(minutes=tf)
    
        
@dataclass
class BarQueue:
    """
    Class for holding bars, and performing various operations on them
    """
    symbol: str
    bars: deque
    maxlen: int
    timeframe: int #In minutes

    def get_column(self,name:Price,count=0,as_df=False):
        """
        Return count or all values of a column, if count is 0, within the bar queue, ie. Close or Open, etc.
        Optional as a panda dataframe, where time becomes the index
        """
        arr = []
        i = 0
        for b in self.bars:
            arr.append(b.get(name))
            i+=1
            if count > 0 and i >= count:
                break
        if as_df:
            return pd.DataFrame(
                arr,
                columns=[price_string(name)],
                index=[pd.to_datetime(self.get_column("time",count), unit='s')]
            )
        return arr

    def add(self,val:np.ndarray):
        """
        Given a numpy array of the new values, build a new bar for each row and add it to the left of the deque
        """
        for x in np.nditer(val):
            df = pd.DataFrame(x)
            new_bar = Bar(df['open'],df['high'],df['low'],df['close'],df['tocl_volume'], df.index)
            if new_bar.is_valid(self.deque[0],self.timeframe):
                self.bars.appendleft(new_bar)




    # REFACTOR COLUMN QUEUE CLASS

def build_zone_data(data_tuple):
    """
    Build a zone data object given a tuple of columns and a numpy object
    """
    print(datetime.utcnow())
    cols, data = data_tuple
    print(datetime.fromtimestamp(data[0][0]))

@dataclass
class ZoneData:
    """
    Class for organizing the data passed to zone manager
    """
    symbol: str
    ohlc: BarQueue
    atr: float
    time_updated: datetime

@dataclass
class TwinData:
    """
    Class that holds the combined data of a larger and smaller term time frame for a
    specific symbol
    """
    large: ZoneData
    small: ZoneData

    def is_empty(self):
        return self.large == None or self.small == None

    def update(self, long_data, short_data):
        # Given the new long and short datas
        # Try to append to existing, or build new
        pass
