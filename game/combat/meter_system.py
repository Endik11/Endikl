from .constants import MAX_METER
class MeterSystem:
    @staticmethod
    def add(value,amount):return min(MAX_METER,max(0,value+amount))
    @staticmethod
    def spend(value,cost):return (value-cost,True) if value>=cost else (value,False)
