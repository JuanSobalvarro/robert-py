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


class OpMode(IntEnum):
    OP_UNDEF = pb.OP_UNDEF
    OP_AUTO = pb.OP_AUTO
    OP_MAN_PROG = pb.OP_MAN_PROG
    OP_MAN_TEST = pb.OP_MAN_TEST


class ResponseStatus(IntEnum):
    SUCCESS = pb.SUCCESS
    ERROR = pb.ERROR


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
    
    @classmethod
    def from_pb(cls, pb_target: pb.RobTarget) -> "RobTarget":
        return cls(
            trans=Position(x=pb_target.trans.x, y=pb_target.trans.y, z=pb_target.trans.z),
            rot=Orientation(q1=pb_target.rot.q1, q2=pb_target.rot.q2, q3=pb_target.rot.q3, q4=pb_target.rot.q4),
            robconf=ConfData(cf1=pb_target.robconf.cf1, cf4=pb_target.robconf.cf4, cf6=pb_target.robconf.cf6, cfx=pb_target.robconf.cfx),
            extax=ExtJoint(eax_a=pb_target.extax.eax_a, eax_b=pb_target.extax.eax_b, eax_c=pb_target.extax.eax_c, eax_d=pb_target.extax.eax_d, eax_e=pb_target.extax.eax_e, eax_f=pb_target.extax.eax_f),
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
    
    @classmethod
    def from_pb(cls, pb_joint_target: pb.JointTarget) -> "JointTarget":
        return cls(
            robjoint=RobJoint(
                rax_1=pb_joint_target.robjoint.rax_1,
                rax_2=pb_joint_target.robjoint.rax_2,
                rax_3=pb_joint_target.robjoint.rax_3,
                rax_4=pb_joint_target.robjoint.rax_4,
                rax_5=pb_joint_target.robjoint.rax_5,
                rax_6=pb_joint_target.robjoint.rax_6,
            ),
            extjoint=ExtJoint(
                eax_a=pb_joint_target.extjoint.eax_a,
                eax_b=pb_joint_target.extjoint.eax_b,
                eax_c=pb_joint_target.extjoint.eax_c,
                eax_d=pb_joint_target.extjoint.eax_d,
                eax_e=pb_joint_target.extjoint.eax_e,
                eax_f=pb_joint_target.extjoint.eax_f,
            )
        )
    

@dataclass
class RobotStatus:
    op_mode: OpMode
    speed_override: float
    current_speed: float
    current_zone: Zone
    current_target: RobTarget
    current_joint_target: JointTarget
    robot_time: str
    robot_date: str

    @classmethod
    def from_pb(cls, pb_status: pb.RobotStatus) -> "RobotStatus":
        return cls(
            op_mode=OpMode(pb_status.op_mode),
            speed_override=pb_status.speed_override,
            current_speed=pb_status.current_speed,
            current_zone=Zone(pb_status.current_zone),
            current_target=RobTarget.from_pb(pb_status.current_target),
            current_joint_target=JointTarget.from_pb(pb_status.current_joint_target),
            robot_time=pb_status.robot_time,
            robot_date=pb_status.robot_date,
        )


@dataclass
class ServerResponse:
    status: ResponseStatus
    message: str
    robot_status: RobotStatus | None = None

    @classmethod
    def from_pb(cls, pb_response: pb.ServerResponse) -> "ServerResponse":
        status_obj = None
        # check if has robot_status field before trying to parse it
        if pb_response.HasField("robot_status"):
            status_obj = RobotStatus.from_pb(pb_response.robot_status)
            
        return cls(
            status=ResponseStatus(pb_response.status),
            message=pb_response.message,
            robot_status=status_obj
        )


def as_pb_robtarget(target: RobTarget | pb.RobTarget) -> pb.RobTarget:
    if isinstance(target, pb.RobTarget):
        return target

    if isinstance(target, RobTarget):
        return target.to_pb()

    raise TypeError(f"target must be RobTarget or pb.RobTarget, got {type(target)!r}")