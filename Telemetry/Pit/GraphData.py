from packet import ParsedPacket
from collections import deque
class GraphInputInterface():
    def __init__(self, parsedPackets: deque[ParsedPacket], maxLength: int) -> None:
        self.parsedPackets = parsedPackets
        self.maxLength = maxLength

    def addElement(self, el: ParsedPacket):
        """
        adds an element to the deque. Removes the leftmost element if necessary.
        """
        if(len(self.parsedPackets) == self.maxLength):
            self.parsedPackets.popleft()
        self.parsedPackets.append(el)
    
    def getDeque(self):
        return self.parsedPackets