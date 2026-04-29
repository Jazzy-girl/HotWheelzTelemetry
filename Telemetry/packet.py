import struct
import functools
import math
import time
from typing import NamedTuple, Generator

PACKET_ORDER = "little" # little | big
PACKET_ORDER_STRUCT = '<' if PACKET_ORDER == "little" else '>' if PACKET_ORDER == "big" else ''

PACKET_FORMAT = PACKET_ORDER_STRUCT + "xxHI dd H Hf Ih5H8B"

PULSES_PER_ROTATION = 48

KM_TO_MI = 0.6213712

WHEEL_DIAMETER_IN = 21
WHEEL_CIRCUMFERENCE_FT = WHEEL_DIAMETER_IN * math.pi / 12
FT_TO_MI = 1 / 5280
S_TO_HR = 3600

PULSE_SPEED_MUL = WHEEL_CIRCUMFERENCE_FT / PULSES_PER_ROTATION * FT_TO_MI * S_TO_HR

PACKET_LEN = 56

def thermistor_temp(reading: int) -> tuple[float, float, float]:
    LOW_SIDE_RESISTOR = 10000
    Ro = 10000.0
    To = 25.0
    beta = 3950.0
    voltage = reading / 1024
    resistance = LOW_SIDE_RESISTOR / voltage - LOW_SIDE_RESISTOR
    steinhart = math.log(resistance / Ro) / beta
    steinhart += 1.0 / (To + 273.15)
    return voltage * 3.3, resistance, (1.0 / steinhart) - 273.15

def checksum_of_data(data: bytes | bytearray) -> int:
    return functools.reduce(int.__xor__, struct.unpack(PACKET_ORDER_STRUCT + "4x26H", data))

def write_checksum(data: bytearray):
    cs = checksum_of_data(data)
    data[2:4] = cs.to_bytes(2, "little")

class FaultSet(int):
    FAULTS: list[str] = [
        "Internal Communication Fault",
        "Internal Conversion Fault",
        "Weak Cell Fault",
        "Low Cell Voltage Fault",
        "Open Wiring Fault",
        "Current Sensor Fault",
        "Pack Voltage Sensor Fault",
        "Weak Pack Fault",
        "Voltage Redundancy Fault",
        "Fan Monitor Fault",
        "Thermistor Fault",
        "CANBus Communications Fault",
        "Always-On Supply Fault",
        "High Voltage Isolation Fault",
        "12V Power Supply Fault",
        "Charge Limit Enforcement Fault",
        "Discharge Limit Enforcement Fault",
        "Charger Safety Relay Fault",
        "Internal Memory Fault",
        "Internal Thermistor Fault",
        "Internal Logic Fault"
    ]
    """
    A set of fault bits packed into a single integer
    """
    def bits(self) -> Generator[int, None, None]:
        bits = int(self)
        i = 0
        while bits:
            yield i
            bits >>= 1
            i += 1
    def list_faults(self) -> list[str]:
        """
        Return a list of faults as strings
        """
        return [FaultSet.FAULTS[i] for i in self.bits()]
    def __str__(self) -> str:
        return "; ".join(FaultSet.FAULTS[i] for i in self.bits())

    

class RawPacket(NamedTuple):
    """
    A raw packet, with fields in the same format that they're passed in the packed format
    """
    checksum: int
    timestamp: int
    gps_lon: float
    gps_lat: float
    temp: int
    motor_speed: int
    gps_speed: float
    faults: int
    curr: int
    open_volt: int
    summed_volt: int
    supply_12v: int
    high_cell_volt: int
    low_cell_volt: int
    high_cell_id: int
    low_cell_id: int
    high_temp: int
    low_temp: int
    high_therm_id: int
    low_therm_id: int
    soc: int
    fan_speed: int
    @staticmethod
    def without_bms(timestamp: int, gps_lon: float, gps_lat: float, temp: int, gps_speed: float, motor_speed: int) -> 'RawPacket':
        """
        Create a RawPacket with all BMS data zeroed
        """
        return RawPacket(
            checksum=0,
            timestamp=timestamp,
            gps_lon=gps_lon,
            gps_lat=gps_lat,
            temp=temp,
            motor_speed=motor_speed,
            gps_speed=gps_speed,
            faults=0,
            curr=0,
            open_volt=0,
            summed_volt=0,
            supply_12v=0,
            high_cell_volt=0,
            low_cell_volt=0,
            high_cell_id=0,
            low_cell_id=0,
            high_temp=0,
            low_temp=0,
            high_therm_id=0,
            low_therm_id=0,
            soc=0,
            fan_speed=0
        )
    @staticmethod
    def new() -> 'RawPacket':
        """
        Create a new packet without any fields
        """
        return RawPacket(0, time.monotonic_ns() // 1000, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    def update_from_bms(self, data: bytes | bytearray) -> 'RawPacket':
        """
        Update the packet with BMS data
        """
        faults, curr, open_volt, summed_volt, supply_12v, high_cell_volt, low_cell_volt, high_cell_id, low_cell_id, high_temp, low_temp, high_therm_id, low_therm_id, soc, fan_speed = struct.unpack(PACKET_ORDER_STRUCT + "Ih5H8B", data)
        return self._replace(
            faults=faults,
            curr=curr,
            open_volt=open_volt,
            summed_volt=summed_volt,
            supply_12v=supply_12v,
            high_cell_volt=high_cell_volt,
            low_cell_volt=low_cell_volt,
            high_cell_id=high_cell_id,
            low_cell_id=low_cell_id,
            high_temp=high_temp,
            low_temp=low_temp,
            high_therm_id=high_therm_id,
            low_therm_id=low_therm_id,
            soc=soc,
            fan_speed=fan_speed
        )
    @staticmethod
    def unpack_bytes(data: bytes | bytearray) -> 'RawPacket':
        """
        Unpack data in bytes into a packet
        """
        return RawPacket(*struct.unpack(PACKET_FORMAT, data))
    def pack_bytes(self, with_checksum = False) -> bytearray:
        """
        Pack data in a packet into bytes, maybe overwriting the checksum
        """
        data = bytearray(struct.pack(PACKET_FORMAT, *self))
        data[0:2] = b"HW"
        if with_checksum:
            write_checksum(data)
        return data
    def calc_checksum(self) -> int:
        """
        Calculate the checksum of this data
        """
        data = struct.pack(PACKET_FORMAT, *self)
        return checksum_of_data(data)
    def with_checksum(self) -> 'RawPacket':
        """
        Overwrite the checksum with the calculated checksum
        """
        return self._replace(checksum=self.calc_checksum())
    def parse(self) -> 'ParsedPacket':
        """
        Parse this data into a ParsedPacket
        """
        tv, tr, tt = thermistor_temp(self.temp)
        return ParsedPacket(
            checksum=self.checksum,
            timestamp=self.timestamp,
            gps_lon=self.gps_lon,
            gps_lat=self.gps_lat,
            therm_reading=self.temp,
            therm_voltage=tv,
            therm_resistance=tr,
            therm_temp=tt,
            motor_speed=self.motor_speed * PULSE_SPEED_MUL,
            gps_speed=self.gps_speed * KM_TO_MI,
            bms_faults=FaultSet(self.faults),
            bms_current=self.curr * 0.1,
            bms_open_voltage=self.open_volt * 0.1,
            bms_summed_voltage=self.open_volt * 0.1,
            bms_supply_12v=self.supply_12v * 0.1,
            bms_high_cell_volt=self.high_cell_volt * 0.0001,
            bms_low_cell_volt=self.high_cell_volt * 0.0001,
            bms_high_cell_id=self.high_cell_id,
            bms_low_cell_id=self.low_cell_id,
            bms_high_temp=self.high_temp - 40,
            bms_low_temp=self.low_temp - 40,
            bms_high_therm_id=self.high_therm_id,
            bms_low_therm_id=self.low_therm_id,
            bms_soc=self.soc * 0.5,
            bms_fan_speed=self.fan_speed,
        )
    def apply(self, *sensors) -> 'RawPacket':
        for sensor in sensors:
            self = sensor.update_packet(self)
        return self

class ParsedPacket(NamedTuple):
    """
    The packet data, with all of the fields parsed to more useful units
    """
    checksum: int
    timestamp: int
    gps_lon: float
    gps_lat: float
    therm_reading: int
    therm_voltage: float
    therm_resistance: float
    therm_temp: float
    motor_speed: float
    gps_speed: float
    bms_faults: FaultSet
    bms_current: float
    bms_open_voltage: float
    bms_summed_voltage: float
    bms_supply_12v: float
    bms_high_cell_volt: float
    bms_low_cell_volt: float
    bms_high_cell_id: int
    bms_low_cell_id: int
    bms_high_temp: int
    bms_low_temp: int
    bms_high_therm_id: int
    bms_low_therm_id: int
    bms_soc: float
    bms_fan_speed: int
    def to_raw(self) -> RawPacket:
        """
        Convert this data to a RawPacket
        """
        return RawPacket(
            checksum=self.checksum,
            timestamp=self.timestamp,
            gps_lon=self.gps_lon,
            gps_lat=self.gps_lat,
            temp=self.therm_reading,
            motor_speed=self.motor_speed / PULSE_SPEED_MUL,
            gps_speed=self.gps_speed / KM_TO_MI,
            faults=int(self.bms_faults),
            curr=int(self.bms_curr * 10),
            open_volt=int(self.bms_open_volt * 10),
            summed_volt=int(self.bms_open_volt * 10),
            supply_12v=int(self.bms_supply_12v * 10),
            high_cell_volt=int(self.bms_high_cell_volt * 10000),
            low_cell_volt=int(self.bms_high_cell_volt * 10000),
            high_cell_id=self.bms_high_cell_id,
            low_cell_id=self.bms_low_cell_id,
            high_temp=self.bms_high_temp + 40,
            low_temp=self.bms_low_temp + 40,
            high_therm_id=self.bms_high_therm_id,
            low_therm_id=self.bms_low_therm_id,
            soc=int(self.bms_soc * 2),
            fan_speed=self.bms_fan_speed,
        )
