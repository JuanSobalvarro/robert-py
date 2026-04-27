from dataclasses import dataclass
from enum import IntEnum

import robert.generated.protocol_pb2 as pb


class Zone(IntEnum):
    FINE = pb.FINE
    Z1 = pb.Z1
    Z5 = pb.Z5
    Z10 = pb.Z10
    Z15 = pb.Z15
    Z20 = pb.Z20
    Z30 = pb.Z30


@dataclass
class Position:
    x: float
    y: float
    z: float

    def to_pb(self) -> pb.Position:
        return pb.Position(x=self.x, y=self.y, z=self.z)
    

@dataclass
class Orientation:
    q1: float
    q2: float
    q3: float
    q4: float

    def to_pb(self) -> pb.Orientation:
        return pb.Orientation(q1=self.q1, q2=self.q2, q3=self.q3, q4=self.q4)


@dataclass
class ConfData:
    cf1: int
    cf4: int
    cf6: int
    cfx: int

    def to_pb(self) -> pb.ConfData:
        return pb.ConfData(cf1=self.cf1, cf4=self.cf4, cf6=self.cf6, cfx=self.cfx)


@dataclass
class RobJoint:
    rax_1: float
    rax_2: float
    rax_3: float
    rax_4: float
    rax_5: float
    rax_6: float

    def to_pb(self) -> pb.RobJoint:
        return pb.RobJoint(
            rax_1=self.rax_1,
            rax_2=self.rax_2,
            rax_3=self.rax_3,
            rax_4=self.rax_4,
            rax_5=self.rax_5,
            rax_6=self.rax_6,
        )


@dataclass
class ExtJoint:
    eax_a: float
    eax_b: float
    eax_c: float
    eax_d: float
    eax_e: float
    eax_f: float

    def to_pb(self) -> pb.ExtJoint:
        return pb.ExtJoint(
            eax_a=self.eax_a,
            eax_b=self.eax_b,
            eax_c=self.eax_c,
            eax_d=self.eax_d,
            eax_e=self.eax_e,
            eax_f=self.eax_f,
        )


@dataclass
class RobTarget:
    trans: Position
    rot: Orientation
    robconf: ConfData
    extax: ExtJoint

    def to_pb(self) -> pb.RobTarget:
        return pb.RobTarget(
            trans=self.trans.to_pb(),
            rot=self.rot.to_pb(),
            robconf=self.robconf.to_pb(),
            extax=self.extax.to_pb(),
        )


@dataclass
class JointTarget:
    robjoint: RobJoint
    extjoint: ExtJoint

    def to_pb(self) -> pb.JointTarget:
        return pb.JointTarget(
            robjoint=self.robjoint.to_pb(),
            extjoint=self.extjoint.to_pb(),
        )


def as_pb_robtarget(target: RobTarget | pb.RobTarget) -> pb.RobTarget:
    if isinstance(target, pb.RobTarget):
        return target

    if isinstance(target, RobTarget):
        return target.to_pb()

    raise TypeError(f"target must be RobTarget or pb.RobTarget, got {type(target)!r}")