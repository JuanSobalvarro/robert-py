from dataclasses import dataclass


class Commands:
    MOVEL = "MOVEL"
    MOVEJ = "MOVEJ"
    MOVEABSJ = "MOVEABSJ"
    MOVEC = "MOVEC"
    PING = "PING"
    PINGR = "PINGR"
    EXIT = "EXIT"


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