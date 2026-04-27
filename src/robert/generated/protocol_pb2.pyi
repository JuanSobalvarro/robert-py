from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CommandType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PING: _ClassVar[CommandType]
    PINGR: _ClassVar[CommandType]
    ZERO: _ClassVar[CommandType]
    EXIT: _ClassVar[CommandType]
    MOVEL: _ClassVar[CommandType]
    MOVEJ: _ClassVar[CommandType]
    MOVEC: _ClassVar[CommandType]
    MOVEABSJ: _ClassVar[CommandType]
    SETSPEED: _ClassVar[CommandType]
    SETZONE: _ClassVar[CommandType]

class Zone(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FINE: _ClassVar[Zone]
    Z1: _ClassVar[Zone]
    Z5: _ClassVar[Zone]
    Z10: _ClassVar[Zone]
    Z15: _ClassVar[Zone]
    Z20: _ClassVar[Zone]
    Z30: _ClassVar[Zone]

class ResponseStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SUCCESS: _ClassVar[ResponseStatus]
    ERROR: _ClassVar[ResponseStatus]
PING: CommandType
PINGR: CommandType
ZERO: CommandType
EXIT: CommandType
MOVEL: CommandType
MOVEJ: CommandType
MOVEC: CommandType
MOVEABSJ: CommandType
SETSPEED: CommandType
SETZONE: CommandType
FINE: Zone
Z1: Zone
Z5: Zone
Z10: Zone
Z15: Zone
Z20: Zone
Z30: Zone
SUCCESS: ResponseStatus
ERROR: ResponseStatus

class Position(_message.Message):
    __slots__ = ("x", "y", "z")
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    Z_FIELD_NUMBER: _ClassVar[int]
    x: float
    y: float
    z: float
    def __init__(self, x: _Optional[float] = ..., y: _Optional[float] = ..., z: _Optional[float] = ...) -> None: ...

class Orientation(_message.Message):
    __slots__ = ("q1", "q2", "q3", "q4")
    Q1_FIELD_NUMBER: _ClassVar[int]
    Q2_FIELD_NUMBER: _ClassVar[int]
    Q3_FIELD_NUMBER: _ClassVar[int]
    Q4_FIELD_NUMBER: _ClassVar[int]
    q1: float
    q2: float
    q3: float
    q4: float
    def __init__(self, q1: _Optional[float] = ..., q2: _Optional[float] = ..., q3: _Optional[float] = ..., q4: _Optional[float] = ...) -> None: ...

class ConfData(_message.Message):
    __slots__ = ("cf1", "cf4", "cf6", "cfx")
    CF1_FIELD_NUMBER: _ClassVar[int]
    CF4_FIELD_NUMBER: _ClassVar[int]
    CF6_FIELD_NUMBER: _ClassVar[int]
    CFX_FIELD_NUMBER: _ClassVar[int]
    cf1: int
    cf4: int
    cf6: int
    cfx: int
    def __init__(self, cf1: _Optional[int] = ..., cf4: _Optional[int] = ..., cf6: _Optional[int] = ..., cfx: _Optional[int] = ...) -> None: ...

class RobJoint(_message.Message):
    __slots__ = ("rax_1", "rax_2", "rax_3", "rax_4", "rax_5", "rax_6")
    RAX_1_FIELD_NUMBER: _ClassVar[int]
    RAX_2_FIELD_NUMBER: _ClassVar[int]
    RAX_3_FIELD_NUMBER: _ClassVar[int]
    RAX_4_FIELD_NUMBER: _ClassVar[int]
    RAX_5_FIELD_NUMBER: _ClassVar[int]
    RAX_6_FIELD_NUMBER: _ClassVar[int]
    rax_1: float
    rax_2: float
    rax_3: float
    rax_4: float
    rax_5: float
    rax_6: float
    def __init__(self, rax_1: _Optional[float] = ..., rax_2: _Optional[float] = ..., rax_3: _Optional[float] = ..., rax_4: _Optional[float] = ..., rax_5: _Optional[float] = ..., rax_6: _Optional[float] = ...) -> None: ...

class ExtJoint(_message.Message):
    __slots__ = ("eax_a", "eax_b", "eax_c", "eax_d", "eax_e", "eax_f")
    EAX_A_FIELD_NUMBER: _ClassVar[int]
    EAX_B_FIELD_NUMBER: _ClassVar[int]
    EAX_C_FIELD_NUMBER: _ClassVar[int]
    EAX_D_FIELD_NUMBER: _ClassVar[int]
    EAX_E_FIELD_NUMBER: _ClassVar[int]
    EAX_F_FIELD_NUMBER: _ClassVar[int]
    eax_a: float
    eax_b: float
    eax_c: float
    eax_d: float
    eax_e: float
    eax_f: float
    def __init__(self, eax_a: _Optional[float] = ..., eax_b: _Optional[float] = ..., eax_c: _Optional[float] = ..., eax_d: _Optional[float] = ..., eax_e: _Optional[float] = ..., eax_f: _Optional[float] = ...) -> None: ...

class RobTarget(_message.Message):
    __slots__ = ("trans", "rot", "robconf", "extax")
    TRANS_FIELD_NUMBER: _ClassVar[int]
    ROT_FIELD_NUMBER: _ClassVar[int]
    ROBCONF_FIELD_NUMBER: _ClassVar[int]
    EXTAX_FIELD_NUMBER: _ClassVar[int]
    trans: Position
    rot: Orientation
    robconf: ConfData
    extax: ExtJoint
    def __init__(self, trans: _Optional[_Union[Position, _Mapping]] = ..., rot: _Optional[_Union[Orientation, _Mapping]] = ..., robconf: _Optional[_Union[ConfData, _Mapping]] = ..., extax: _Optional[_Union[ExtJoint, _Mapping]] = ...) -> None: ...

class JointTarget(_message.Message):
    __slots__ = ("robjoint", "extjoint")
    ROBJOINT_FIELD_NUMBER: _ClassVar[int]
    EXTJOINT_FIELD_NUMBER: _ClassVar[int]
    robjoint: RobJoint
    extjoint: ExtJoint
    def __init__(self, robjoint: _Optional[_Union[RobJoint, _Mapping]] = ..., extjoint: _Optional[_Union[ExtJoint, _Mapping]] = ...) -> None: ...

class ClientRequest(_message.Message):
    __slots__ = ("command", "target", "extra_target", "joint_target", "speed", "zone")
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    EXTRA_TARGET_FIELD_NUMBER: _ClassVar[int]
    JOINT_TARGET_FIELD_NUMBER: _ClassVar[int]
    SPEED_FIELD_NUMBER: _ClassVar[int]
    ZONE_FIELD_NUMBER: _ClassVar[int]
    command: CommandType
    target: RobTarget
    extra_target: RobTarget
    joint_target: JointTarget
    speed: float
    zone: Zone
    def __init__(self, command: _Optional[_Union[CommandType, str]] = ..., target: _Optional[_Union[RobTarget, _Mapping]] = ..., extra_target: _Optional[_Union[RobTarget, _Mapping]] = ..., joint_target: _Optional[_Union[JointTarget, _Mapping]] = ..., speed: _Optional[float] = ..., zone: _Optional[_Union[Zone, str]] = ...) -> None: ...

class ServerResponse(_message.Message):
    __slots__ = ("status", "message")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    status: ResponseStatus
    message: str
    def __init__(self, status: _Optional[_Union[ResponseStatus, str]] = ..., message: _Optional[str] = ...) -> None: ...
