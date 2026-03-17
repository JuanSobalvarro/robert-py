from dataclasses import dataclass
from enum import Enum


class Commands(Enum):
    MOVEL = "MOVEL"
    MOVEJ = "MOVEJ"
    MOVEC = "MOVEC"
    MOVEABSJ = "MOVEABSJ"
    SETSPEED = "SETSPEED"
    SETZONE = "SETZONE"
    EXIT = "EXIT"
    PING = "PING"
    PINGR = "PINGR"
    ZERO = "ZERO"

    def __str__(self):
        return self.value

@dataclass
class RobTarget:
    x: float
    y: float
    z: float
    q1: float
    q2: float
    q3: float
    q4: float
    cf1: int
    cf4: int
    cf6: int
    cfx: int

    def to_list(self):
        return [self.x, self.y, self.z, self.q1, self.q2, self.q3, self.q4,
                self.cf1, self.cf4, self.cf6, self.cfx]
    
    def to_csv(self):
        return ",".join(str(value) for value in self.to_list())

    def __str__(self):
        return self.to_csv()


@dataclass
class RobJoint:
    j1: float
    j2: float
    j3: float
    j4: float
    j5: float
    j6: float

    def to_list(self):
        return [self.j1, self.j2, self.j3, self.j4, self.j5, self.j6]
    
    def to_csv(self):
        return ",".join(str(value) for value in self.to_list())

    def __str__(self):
        return self.to_csv()
    

class Zone(Enum):
    FINE = 0
    Z1 = 1
    Z5 = 2
    Z10 = 3
    Z15 = 4
    Z20 = 5
    Z30 = 6

    def __str__(self):
        return str(self.value)