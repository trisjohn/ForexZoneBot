from account import AccountManager
from zonemanager import ZoneManager
from datamanager import DataManager

# Build Zone based on bias

# Take trade

# Manage trade by closing early on certain trades

VERSION = """
          V 0.04
          Now trades off supply and demand zones, with a stop loss at last high/low +/- atr, max of 1.5 atr
          Take is now 3 * atr, which a runner that closes out when break even (+1 *Atr) is hit or when ema
          direction changes
          """

# Array of all symbols
SYMBOLS = [
    "USDJPY","GBPJPY", "EURJPY",
    "GBPUSD", "EURUSD", "AUDUSD",
    "USDCAD", "XAUUSD", "EURGBP",
    "NZDUSD", "NZDJPY", "NZDCAD",
]

if __name__ == "__main__":
    print(f"Begin LittleZoneBoi \r\n{VERSION}")
    
    # Log in to accounts
    acc_manager = AccountManager()
    # Set up zone manager
    zone_manager:ZoneManager = ZoneManager()
    data_manager = DataManager()
    data_manager.set_time_frames(60,15)
    data_manager.set_symbols(SYMBOLS)
    positions = PositionManager()
    risk = 0.02
    # Begin Loop
    while True:
        # Grab data
        data_manager.reload_data()
        if data_manager.ready():
            # Determine bias
            data_manager.load_bias()
            # Update/Build zone
            zone_manager.update_zones(data_manager.data_for_zones())
            # Entry based on zone calculation
            new_entries = zone_manager.get_entry_signals()
            EntryManager(new_entries)
            # Manage open positions
            positions.Update(data_manager.data_for_pos())
            # Close positions or move virtual stops
            positions.Handle()

