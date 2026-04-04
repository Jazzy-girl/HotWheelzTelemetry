from Telemetry.packet import RawPacket

class SensorBase:
    def update_packet(self, packet: RawPacket) -> RawPacket:
        return packet