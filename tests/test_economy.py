from pathlib import Path
from game.economy import *
def setup(points=500,save=lambda:True,unlocks=()):return EconomyManager(Wallet(points),Catalog.load(Path("data/shop_catalog.json")),save=save,unlocks=unlocks)
def test_purchase_success_failures_and_idempotency():
    economy=setup();assert economy.purchase("ember_palette","tx1").success and economy.wallet.points==360;assert not economy.purchase("ember_palette","tx2").success and not economy.purchase("missing","tx3").success and not economy.purchase("ember_palette","tx1").success
    poor=setup(1);assert poor.purchase("boundary_emblem","p").code=="insufficient" and poor.wallet.points==1
    locked=setup();assert locked.purchase("storm_trail","l").code=="locked"
def test_atomic_rollback_equip_and_no_combat_properties():
    economy=setup(save=lambda:False);result=economy.purchase("ember_palette","tx");assert result.code=="save_failed" and economy.wallet.points==500 and not economy.inventory
    economy=setup();economy.purchase("ember_palette","ok");equipped={};assert economy.equip("ember_palette",equipped) and equipped["palettes"]=="ember_palette"
    assert all(not hasattr(item,name) for item in economy.catalog.items.values() for name in ("health","damage","speed","meter","stun"))
def test_negative_wallet_is_repaired():assert Wallet(-99).points==0
