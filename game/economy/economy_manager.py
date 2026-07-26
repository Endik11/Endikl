from .purchase_result import PurchaseResult
class EconomyManager:
    def __init__(self,wallet,catalog,inventory=None,transactions=None,save=None,unlocks=None):self.wallet=wallet;self.catalog=catalog;self.inventory=set(inventory or ());self.transactions=set(transactions or ());self.save=save or (lambda:True);self.unlocks=set(unlocks or ())
    def purchase(self,item_id,transaction_id):
        if transaction_id in self.transactions:return PurchaseResult(False,"duplicate_transaction",transaction_id,item_id)
        item=self.catalog.items.get(item_id)
        if item is None:return PurchaseResult(False,"unknown_item",transaction_id,item_id)
        if item_id in self.inventory:return PurchaseResult(False,"already_owned",transaction_id,item_id)
        if any(req not in self.unlocks for req in item.requirements):return PurchaseResult(False,"locked",transaction_id,item_id)
        if not self.wallet.can_spend(item.price):return PurchaseResult(False,"insufficient",transaction_id,item_id)
        before=self.wallet.points;self.wallet.spend(item.price);self.inventory.add(item_id)
        try:
            if self.save() is False:raise OSError("save failed")
        except Exception:
            self.wallet.points=before;self.inventory.discard(item_id);return PurchaseResult(False,"save_failed",transaction_id,item_id)
        self.transactions.add(transaction_id);return PurchaseResult(True,"purchased",transaction_id,item_id)
    def equip(self,item_id,equipped):
        if item_id not in self.inventory:return False
        equipped[self.catalog.items[item_id].category]=item_id;return True
