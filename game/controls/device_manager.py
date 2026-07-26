class DeviceManager:
    def __init__(self):self.assignments={"p1":"keyboard","p2":"keyboard"};self.connected=set()
    def connected_device(self,device_id):self.connected.add(device_id)
    def disconnected_device(self,device_id):self.connected.discard(device_id);return [p for p,d in self.assignments.items() if d==device_id]
    def assign(self,player,device_id):self.assignments[player]=device_id
