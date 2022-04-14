from enum import Enum, auto
from log import Log
import pandas as pd
import random

# Given a df of ohlc, determine if bar is a hammer candle
def is_hammer(ohlc):
    full = ohlc['high'] - ohlc['low']
    a = ohlc['close'] if ohlc['close'] > ohlc['open'] else ohlc['open']
    b = ohlc['close'] if ohlc['close'] < ohlc['open'] else ohlc['open']
    body = a - b
    upper = ohlc['high'] - a
    lower = b - ohlc['low']
    return lower >= full * .5 and lower > body and lower > upper

# Given a df of ohlc, determine if bar is a pin candle
def is_pin(ohlc):
    full = ohlc['high'] - ohlc['low']
    a = ohlc['close'] if ohlc['close'] > ohlc['open'] else ohlc['open']
    b = ohlc['close'] if ohlc['close'] < ohlc['open'] else ohlc['open']
    body = a - b
    upper = ohlc['high'] - a
    lower = b - ohlc['low']
    return upper >= full * .5 and upper > body and upper > lower
    
class Zone:
    def __init__(self, symbol, price, atr):
        self.symbol = symbol
        self.anchor = price
        zone = atr
        self.upper = price + zone
        self.lower = price - zone
        self.expire_dist = 2 * atr
    
    def __str__(self) -> str:
        return f"Zone: [{self.anchor} u: {self.upper} l: {self.lower} exp: {self.expire_dist}]"

    def in_zone(self, price):
        """
        Return true if price is within the bounds of the zone
        """
        return price >= self.lower and price <= self.upper
    
    def above_zone(self,price):
        """
        Return true if price above the upper zone bound
        """
        return price > self.upper
    
    def below_zone(self,price):
        """
        Return true if price below the lower zone bound
        """
        return price < self.lower 
    
    def zone_expired(self, close):
        """
        Return true if close price is far away from zone
        """
        return abs(close - self.anchor) >= self.expire_dist

class RetCode(Enum):
    NO_ENTRY = auto()
    ENTRY = auto()
    BAD_ZONE = auto()

class DemandZone (Zone):
    def __init__(self, symbol, price, atr):
        super().__init__(symbol, price,atr)
    
    def __str__(self) -> str:
        return super().__str__()

    def is_entry(self, ohlc):
        """
        Given the last bar, a pandas DF of ohlc, determine if price is an entry or not.
        An entry is determined by a hammer candle whose high above zone and low is in zone.
        If zone is expired, it will automatically delete itself.
        """

        # Feed data into neural network

        close = ohlc['close']
        if self.zone_expired(close):
            print("Demand Zone epxired.")

            # RE-RE-RE-RE-RE-RE-RE = RE-RE-RE-RE-RE-RE-RE     
            # [TO DO ] Record Special information about the zone and why it became obsolete
            # To be used within a neural network for it to predict when a zone is no longer needed

            # Log("Demand Zone Expired", f"{self.symbol}_Zone", self.__str__())
            del self
            return RetCode.BAD_ZONE

        isEntry = (( self.in_zone(ohlc['low']) and self.above_zone(ohlc['high'])) or self.in_zone(close)) and is_hammer(ohlc)
        if isEntry:
            Log("Demand Zone signaled entry", f"{self.symbol}_Zone", self.__str__())
            return RetCode.ENTRY
        return RetCode.NO_ENTRY

class SupplyZone (Zone):
    def __init__(self,symbol,price,atr):
        super().__init__(symbol,price,atr)

    def __str__(self) -> str:
        return super().__str__()
    
    def is_entry(self, ohlc):
        """
        Given the last bar, a pandas DF of ohlc, determine if price is an entry or not.
        An entry is determined by a pin candles whose low is below zone and high is in zone.
        If zone is expired, it will automatically delete itself.
        """

        # Feed data into neural network

        close = ohlc['close']
        if self.zone_expired(close):
            print("Supply Zone expired.")
            # RE-RE RE-RE-RE-RE-RE-RE-RE RE-RE-RE-RE-RE-RE-RE 
            # READ ABOVE
            del self
            return RetCode.BAD_ZONE

        isEntry = ( (self.below_zone(ohlc['low']) and self.in_zone(ohlc['high'])) or self.in_zone(close)) and is_pin(ohlc)

        if isEntry:
            Log("Supply Zone signaled entry", f"{self.symbol}_Zone", self.__str__())
            return RetCode.ENTRY
        return RetCode.NO_ENTRY


def is_buy(ohlc):
    """
    Given an ohlc bar, determine if it is a buy bar or sell bar
    """
    return ohlc['open'] < ohlc['close']


# Given a direction (1:buy -1:sell) and bars, try to construct a new zone
# Supply zones need 3 cons red bars
# Demand zones need 3 cons green bars
# zone anchor is mid point of the 4th bar in history after the above is discovered
def try_build_zone(symbol, dir, ohlc: pd.DataFrame, atr):
    new_zone = None
    anchor = 0.0 # Anchor for the zone
    # Loop through ohlc
    print(f"Trying to build zone {dir} out of {len(ohlc)} bars....")
    i = 0
    for _, _ in ohlc.iterrows():
        if i >= len(ohlc) - 3: break
        # Find 3 consec bars
        if dir == 1:
            # buy
            imp1 = is_buy(ohlc.iloc[i])
            imp2 = is_buy(ohlc.iloc[i+1])
            imp3 = is_buy(ohlc.iloc[i+2])
            # print(f"[DEMAND ZONE] Attempt: {i} {imp1} {imp2} {imp3}")
            if imp1 and imp2 and imp3:
                # Demand zone at i+3
                anchor = (ohlc.iloc[i+3]['high'] + ohlc.iloc[i+3]['low']) / 2
        else:
            # sell
            imp1 = not is_buy(ohlc.iloc[i])
            imp2 = not is_buy(ohlc.iloc[i+1])
            imp3 = not is_buy(ohlc.iloc[i+2])
            # print(f"[SUPPLY ZONE] Attempt: {i} {imp1} {imp2} {imp3}")
            if imp1 and imp2 and imp3:
                # Supply zone at i+3
                anchor = (ohlc.iloc[i+3]['high'] + ohlc.iloc[i+3]['low']) / 2
        i+=1
        # Use mid point as anchor for new zone
    if anchor == 0:
        print("[ZONE BUILD] No Zone discovered.")
        return new_zone
    elif abs(anchor - ohlc.iloc[0]['close']) >= 2 * atr:
        print("[ZONE BUILD] Zone found, but it is already invalidated due to distance.")
        return new_zone
    new_zone = DemandZone(symbol,anchor,atr) if dir == 1 else SupplyZone(symbol, anchor, atr)
    print("[ZONE ENTRY] New Zone found @",new_zone.anchor, dir)
    return new_zone

