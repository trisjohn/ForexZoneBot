import MetaTrader5 as mt5
from dataclasses import dataclass

@dataclass
class Account:
    """
    Class for keeping track of, and logging into an mt5 account
    """
    number: int
    password: str
    description: str = ""

    def login(self):
        # establish connection to the MetaTrader 5 terminal
        if not mt5.initialize():
            print("initialize() failed, error code =",mt5.last_error())
            quit()
        authorized = mt5.login(self.number, password=self.password, server=self.description)
        if not authorized:
            raise Exception(f"Login failed for account {self.number} error: {mt5.last_error()}")
        print(f"Login={authorized}")


class AccountManager:
    """
    Holds all account information, including passwords
    """
    def __init__(self):
        self.accounts = [
            Account(1088545,"pork5659", "TradersWay-Demo"),
        ]
        self.index = 0
        self.accounts[0].login()
    def switch(self, num=0, descrip="") -> bool:
        """
        Find an account from given number or description, then attempt to login. In case of multiple accounts
        matching the parameters, logins in  to the last account matched. If no parameters are supplied, login
        to the next account in the list. If parameters are supplied that do not match, returns without login
        """
        if num == 0 and descrip == "":
            print("[ACCOUNT MANAGER] Loging into next account in list.")
            self.index = 0 if self.index + 1 >= len(self.accounts) else self.index + 1
            self.accounts[self.index].login()
            return
        account = None
        for acc in self.accounts:
            if num != 0 and num in acc.number:
                account = acc
            elif descrip != "" and descrip in acc.description:
                account = acc
        if not account:
            print("[ACCOUNT MANAGER] No account found to login to.")
            return
        self.index = self.accounts.index(account)
        account.login()
    def relog(self):
        self.accounts[self.index].login()
        
