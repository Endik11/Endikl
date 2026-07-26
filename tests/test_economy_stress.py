from pathlib import Path
from game.economy import Wallet,Catalog,EconomyManager
def test_repeated_transaction_id_does_not_double_spend():
    economy=EconomyManager(Wallet(10000),Catalog.load(Path("data/shop_catalog.json")));assert economy.purchase("ember_palette","stable").success
    for _ in range(1000):assert not economy.purchase("ember_palette","stable").success
    assert economy.wallet.points==9860 and len(economy.transactions)==1
