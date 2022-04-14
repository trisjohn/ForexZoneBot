from zone import *
from dataobjects import ZoneData

class ZoneEntry:
    """
    Holds logic for each zone entry. Update every new bar and enter order accordingly based on update return bool.
    """
    def __init__(self, symbol, dir, recursive=False):
        self.zone = None
        self.symbol = symbol
        self.entry_dir = dir # When this is either 1 or -1, begin exercising entry logic
        self.recursing = recursive
    
    def __str__(self) -> str:
        zone = self.zone if self.zone != None else "(zone unfound)"
        return f"{'Supply' if self.entry_dir == -1 else 'Demand'} {zone}"
    
    def update(self, ohlc: pd.DataFrame, atr) -> bool:
        """
        Update the Entry with the bars (ohlc pandas df)
        A higher number of bars will cause the manager to look further back in time for a zone, this could lead to some issues
        Returns true if entry is detected, false other wise.
        Also if there is no entry (entry_dir == 0) will just return false
        """
        print("Zone updating:",self.entry_dir)
        if self.entry_dir == 0: return False

        if self.zone == None:
            self.zone = try_build_zone(self.symbol, self.entry_dir, ohlc, atr)
            if self.zone == None:
                # No zone found, still keep trying to find zone
                print("[ZONE] No zone found, continuing to look...")
                return False
            else:
                Log("New Zone built", f"{self.symbol}_Zone", self.zone.__str__())
        
        action = self.zone.is_entry(ohlc.iloc[0])
        if action == RetCode.BAD_ZONE:
            print("[ZONE ENTRY] Deleting zone entry due to expiration.")
            del self
        elif action == RetCode.ENTRY:
            return True
        
        return False

class ZoneManager:
    def __init__(self):
        print("Zone manager initalized.")
        self.zones = {}
    
    def __str__(self) -> str:
        s = "Zone Manager:\t"
        
        for sym, z in self.zones.items():
            s += f" {sym} {z}"
        
        return s

    def update_zones(self, data:list(ZoneData) ):
        """
        Given a data object, a map [symbol]: (ohlc, atr), update all the zones
        """
        for d in data:
            if d.symbol in self.zones:
                self.update(d.symbol, d.ohlc, d.atr)
            else:
                # This should never happen
                Log("Passing in Zone data for a zone that no longer exists.", f"{d.symbol}_Zone")

    def update(self, symbol, ohlc, atr):
        """
        Pass in the symbol and the bars from its data keep and the current atr to update zones
        Returns true if the zone for the given symbol signals an entry, false otherwise
        """
        print("[ZONE MANAGER] Updating zone on",symbol)
        if symbol in self.zones:
            is_entry = self.zones[symbol].update(ohlc,atr)
            if is_entry:
                Log("Zone Deleted.", f"{symbol}_Zone")
            return is_entry
    
    def get_dir(self, symbol):
        """
        Given a symbol, return the zone entry direction, or 0 if the symbol doesnt exist
        """
        if symbol not in self.zones:
            return 0
        dir = self.zones[symbol].entry_dir
        dir = 0 if dir == 1 else 1
        return dir
    
    def new_zone(self, symbol, dir, is_recursive=False):
        """
        Create a new zone entry, given the symbol and the direction. A recursive entry continously builds new zones and looks for entries until:
        Two entries have been created or a zone expires.
        """
        self.zones[symbol] = ZoneEntry(symbol, dir, is_recursive)
        print("[ZONE MANAGER] New Entry Zone",self.zones[symbol])
    
    def new_random_zone(self, symbol):
        """
        Takes a symbol and builds a new zone of a random direction
        """
        dir = 1
        if random.random() < .5:
            dir = -1
        self.new_zone(symbol,dir)
    
    def has_zone(self, symbol):
        """
        Check if a zone exists for the given symbol
        """
        return symbol in self.zones

    def symbols(self):
        """
        Return all symbols of the existing zone entries
        """
        return list(self.zones.keys())
    
    def has_none(self):
        return len(self.zones) < 1
    
    def delete_zone(self, symbol):
        """
        Force a zone to delete on the given symbol
        """
        if symbol in self.zones:
            del self.zones[symbol]
            print(f"[ZONE MANAGER] zone on {symbol} deleted successfully.")