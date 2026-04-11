from packet import ParsedPacket
from collections import deque
class GraphDataInterface():
    def __init__(self, parsedPackets: deque[ParsedPacket], maxLength: int) -> None:
        self.parsedPackets = parsedPackets
        self.maxLength = maxLength
        self.data = deque()
        for el in self.parsedPackets:
            self.addData(el)

    def addElement(self, el: ParsedPacket):
        """
        adds an element to the deque. Removes the leftmost element if necessary.
        """
        if(len(self.parsedPackets) == self.maxLength):
            self.parsedPackets.popleft()
            self.data.popleft()
        self.parsedPackets.append(el)
        self.addData(el)
    
    def addData(self, el: ParsedPacket):
        pass
    
    def getData(self):
        return self.data

class GraphDataCockpit(GraphDataInterface):
    def __init__(self, parsedPackets: deque[ParsedPacket], maxLength: int) -> None:
        super().__init__(parsedPackets, maxLength)
    
    def addData(self, el: ParsedPacket):
        self.data.append(el.therm_temp)

class GraphDataPOV(GraphDataInterface):
    def __init__(self, parsedPackets: deque[ParsedPacket], maxLength: int) -> None:
        super().__init__(parsedPackets, maxLength)
    
    def addData(self, el: ParsedPacket):
        self.data.append(el.bms_open_voltage)

class GraphDataCurrent(GraphDataInterface):
    def __init__(self, parsedPackets: deque[ParsedPacket], maxLength: int) -> None:
        super().__init__(parsedPackets, maxLength)
    
    def addData(self, el: ParsedPacket):
        self.data.append(el.bms_current)

class GraphDataHighest(GraphDataInterface):
    def __init__(self, parsedPackets: deque[ParsedPacket], maxLength: int) -> None:
        super().__init__(parsedPackets, maxLength)
    
    def addData(self, el: ParsedPacket):
        self.data.append(el.bms_high_temp)