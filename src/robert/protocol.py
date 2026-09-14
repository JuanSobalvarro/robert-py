from dataclasses import dataclass, field
import math
from enum import IntEnum

import robert.generated.protocol_pb2 as pb


class Zone(IntEnum):
    """
    Represents the fly-by zone of the robot during motion.

    The zone dictates how closely the robot must approach a target before continuing
    to the next instruction. A `FINE` zone forces the robot to come to a complete
    stop at the exact coordinates. Larger zones (e.g., `Z10`, `Z20`) allow the robot
    to round corners, resulting in smoother and faster continuous paths.
    """
    FINE = pb.FINE
    Z1 = pb.Z1
    Z5 = pb.Z5
    Z10 = pb.Z10
    Z15 = pb.Z15
    Z20 = pb.Z20
    Z30 = pb.Z30


class OpMode(IntEnum):
    """
    Represents the current operation mode of the physical robot controller.

    Note: This is read-only telemetry data.
    """
    OP_UNDEF = pb.OP_UNDEF
    OP_AUTO = pb.OP_AUTO
    OP_MAN_PROG = pb.OP_MAN_PROG
    OP_MAN_TEST = pb.OP_MAN_TEST


class ResponseStatus(IntEnum):
    """
    Represents the immediate network and validation status of a server response.

    This indicates whether the middleware successfully received and parsed the command.
    It does NOT indicate if a physical robot movement has finished.
    """
    SUCCESS = pb.SUCCESS
    ERROR = pb.ERROR
    WARNING = pb.WARNING

class TaskStatus(IntEnum):
    """
    Represents the physical execution state of a task queued on the robot controller.

    - TASK_UNKNOWN: The task ID does not exist or has expired.
    - TASK_PENDING: The task is queued in the middleware but not yet executing on the robot.
    - TASK_IN_PROGRESS: The physical robot is currently executing the task.
    - TASK_COMPLETED: The robot has successfully reached the target.
    - TASK_FAILED: The robot failed to execute the task (e.g., kinematic limit reached).
    """
    TASK_UNKNOWN = pb.TASK_UNKNOWN
    TASK_PENDING = pb.TASK_PENDING
    TASK_IN_PROGRESS = pb.TASK_IN_PROGRESS
    TASK_COMPLETED = pb.TASK_COMPLETED
    TASK_FAILED = pb.TASK_FAILED

@dataclass
class Position:
    """
    Represents a Cartesian position in 3D space.

    Coordinates are measured in millimeters (mm) relative to the active Work Object (WObj)
    or the robot's base frame if no custom WObj is defined.

    :param x: Distance along the X-axis (mm).
    :param y: Distance along the Y-axis (mm).
    :param z: Distance along the Z-axis (mm).
    """
    x: float = 500.0
    y: float = 0.0
    z: float = 700.0

    def to_pb(self) -> pb.Position:
        return pb.Position(x=self.x, y=self.y, z=self.z)


@dataclass
class Orientation:
    """
    Represents the orientation of the Tool Center Point (TCP) in 3D space.

    Orientation is strictly defined using unit quaternions (q1, q2, q3, q4) to avoid
    gimbal lock. This determines the exact angle at which the end-effector approaches
    the target position.

    :param q1: Real/Scalar part of the quaternion.
    :param q2: i vector component.
    :param q3: j vector component.
    :param q4: k vector component.
    """
    q1: float = 0.707
    q2: float = 0.0
    q3: float = 0.707
    q4: float = 0.0

    def __post_init__(self):
            """
            Validates the quaternion on the client side. The norm of a unit quaternion
            must always be 1.0. We use a small tolerance to allow for truncated values
            like 0.707 (instead of 0.707106...).
            """
            norm = math.sqrt(self.q1**2 + self.q2**2 + self.q3**2 + self.q4**2)
            if not math.isclose(norm, 1.0, abs_tol=1e-3):
                raise ValueError(
                    f"Invalid quaternion: The norm must be 1.0, but got {norm:.4f}. "
                    f"Values: [{self.q1}, {self.q2}, {self.q3}, {self.q4}]"
                )

    def to_pb(self) -> pb.Orientation:
        return pb.Orientation(q1=self.q1, q2=self.q2, q3=self.q3, q4=self.q4)


@dataclass
class ConfData:
    """
    Represents the axis configuration data of the robot.

    When multiple joint configurations can reach the same Cartesian target, ConfData
    forces the robot to use a specific posture (e.g., elbow up vs. elbow down) to
    prevent unpredictable movements or singularities.

    Note: If you are working with an IRB 140 (Type C) and orientation does not matter
    for your current task, the default safe configuration is usually (cf1=0, cf4=0, cf6=-1, cfx=0).
    """
    cf1: int = 0
    cf4: int = 0
    cf6: int = -1
    cfx: int = 0

    def to_pb(self) -> pb.ConfData:
        return pb.ConfData(cf1=self.cf1, cf4=self.cf4, cf6=self.cf6, cfx=self.cfx)

@dataclass
class RobJoint:
    """
    Represents the absolute angular position of the robot's six internal axes.
    """
    rax_1: float = 0.0
    rax_2: float = 0.0
    rax_3: float = 0.0
    rax_4: float = 0.0
    rax_5: float = 0.0
    rax_6: float = 0.0

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
    """
    Represents the position of external mechanical axes synchronized with the robot controller.

    This is used when the robot is mounted on a linear track or controls external rotary tables.
    If your robotic cell does not use external axes, all values MUST be set to `9e9`, which
    is the standard RAPID convention for "unused axis".
    """
    eax_a: float = 9e9
    eax_b: float = 9e9
    eax_c: float = 9e9
    eax_d: float = 9e9
    eax_e: float = 9e9
    eax_f: float = 9e9

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
    """
    Represents a complete Cartesian target definition for linear and circular movements.

    A valid RobTarget completely defines where the TCP should go (trans), how the tool
    should be rotated (rot), what posture the arm should assume (robconf), and the state
    of any external axes (extax).

    :param trans: The target XYZ coordinates (Position).
    :param rot: The tool orientation (Orientation/Quaternion).
    :param robconf: The specific joint posture (ConfData).
    :param extax: Positions for external axes, use 9e9 if unused (ExtJoint).
    """
    trans: Position | list[float] | tuple[float, ...] = field(default_factory=Position)
    rot: Orientation | list[float] | tuple[float, ...] = field(default_factory=Orientation)
    robconf: ConfData | list[float] | tuple[float, ...] = field(default_factory=ConfData)
    extax: ExtJoint | list[float] | tuple[float, ...] = field(default_factory=ExtJoint)

    def __setattr__(self, name, value):
        """
        Intercepts assignments. If the user assigns a list or tuple to 'rot',
        it automatically converts it into an Orientation object and validates it.
        """
        if name == "trans" and isinstance(value, (list, tuple)):
            if len(value) != 3:
                raise ValueError("Position list must have exactly 3 elements: [x, y, z]")
            value = Position(*value)

        if name == "rot" and isinstance(value, (list, tuple)):
            if len(value) != 4:
                raise ValueError("Orientation list must have exactly 4 elements: [q1, q2, q3, q4]")
            value = Orientation(*value)

        if name == "robconf" and isinstance(value, (list, tuple)):
            if len(value) != 4:
                raise ValueError("ConfData list must have exactly 4 elements: [cf1, cf4, cf6, cfx]")
            value = ConfData(*value)

        if name == "extax" and isinstance(value, (list, tuple)):
            if len(value) != 3:
                raise ValueError("ExtJoint list must have exactly 3 elements: [e1, e2, e3]")
            value = ExtJoint(*value)

        super().__setattr__(name, value)

    def to_pb(self) -> pb.RobTarget:

        if not isinstance(self.trans, Position):
            raise TypeError("trans must be a Position object")
        if not isinstance(self.rot, Orientation):
            raise TypeError("rot must be an Orientation object")
        if not isinstance(self.robconf, ConfData):
            raise TypeError("robconf must be a ConfData object")
        if not isinstance(self.extax, ExtJoint):
            raise TypeError("extax must be an ExtJoint object")

        return pb.RobTarget(
            trans=self.trans.to_pb(),
            rot=self.rot.to_pb(),
            robconf=self.robconf.to_pb(),
            extax=self.extax.to_pb(),
        )

    @classmethod
    def from_pb(cls, pb_target: pb.RobTarget) -> RobTarget:
        return cls(
            trans=Position(x=pb_target.trans.x, y=pb_target.trans.y, z=pb_target.trans.z),
            rot=Orientation(q1=pb_target.rot.q1, q2=pb_target.rot.q2, q3=pb_target.rot.q3, q4=pb_target.rot.q4),
            robconf=ConfData(cf1=pb_target.robconf.cf1, cf4=pb_target.robconf.cf4, cf6=pb_target.robconf.cf6, cfx=pb_target.robconf.cfx),
            extax=ExtJoint(eax_a=pb_target.extax.eax_a, eax_b=pb_target.extax.eax_b, eax_c=pb_target.extax.eax_c, eax_d=pb_target.extax.eax_d, eax_e=pb_target.extax.eax_e, eax_f=pb_target.extax.eax_f),
        )


@dataclass
class JointTarget:
    """
    Represents a complete Joint target definition for non-linear movements (MoveAbsJ).

    Unlike a RobTarget, a JointTarget defines the final destination purely by the
    angular degrees of the 6 internal motors, ignoring Cartesian space entirely.

    :param robjoint: The specific angles for the 6 robot axes (RobJoint).
    :param extjoint: Angles/Positions for external axes, use 9e9 if unused (ExtJoint).
    """
    robjoint: RobJoint | list[float] | tuple[float, ...] = field(default_factory=RobJoint)
    extjoint: ExtJoint | list[float] | tuple[float, ...] = field(default_factory=ExtJoint)

    def __setattr__(self, name, value) -> None:

        if isinstance(value, (list, tuple)):
            value = RobJoint(*value) if name == "robjoint" else ExtJoint(*value)

        if not isinstance(value, (RobJoint, ExtJoint)):
            raise TypeError(f"Invalid type for {name}: {type(value)}")

        super().__setattr__(name, value)

    def to_pb(self) -> pb.JointTarget:

        if not isinstance(self.robjoint, RobJoint):
            raise TypeError(f"Invalid type for robjoint: {type(self.robjoint)}")
        if not isinstance(self.extjoint, ExtJoint):
            raise TypeError(f"Invalid type for extjoint: {type(self.extjoint)}")

        return pb.JointTarget(
            robjoint=self.robjoint.to_pb(),
            extjoint=self.extjoint.to_pb(),
        )

    @classmethod
    def from_pb(cls, pb_joint_target: pb.JointTarget) -> JointTarget:
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
    """
    Encapsulates all real-time telemetry gathered from the robot controller.

    :param op_mode: Indicates if the controller is in Auto or Manual mode.
    :param speed_override: The global speed percentage set on the FlexPendant.
    :param current_speed: The active TCP translation speed (mm/s).
    :param current_zone: The active fly-by zone configuration.
    :param current_target: The exact Cartesian position and orientation of the TCP.
    :param current_joint_target: The exact angular degrees of the 6 motors.
    :param robot_time: Internal controller clock time (HH:MM:SS).
    :param robot_date: Internal controller clock date (YYYY-MM-DD).
    """
    op_mode: OpMode
    speed_override: float
    current_speed: float
    current_zone: Zone
    current_target: RobTarget
    current_joint_target: JointTarget
    robot_time: str
    robot_date: str

    @classmethod
    def from_pb(cls, pb_status: pb.RobotStatus) -> RobotStatus:
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
    """
    The core response object returned by every API call to the RobeRT Middleware.

    Because movements on physical hardware are slow, the middleware uses an asynchronous
    task system. When you request a movement, the middleware instantly returns a
    ServerResponse containing a `task_id` with a status of `TASK_PENDING`.
    You must use this `task_id` to poll the server until the physical movement finishes.

    :param status: Indicates if the middleware successfully received the request (SUCCESS, ERROR).
    :param task_status: The physical execution state of the command (e.g., TASK_IN_PROGRESS).
    :param task_id: Unique identifier for the queued physical movement. None for instant commands.
    :param error_message: Details about what went wrong if status is ERROR.
    :param text_payload: String data (e.g., session tokens) returned by specific commands.
    :param robot_status: Telemetry data, populated only when calling `get_status()`.
    """
    status: ResponseStatus
    task_status: TaskStatus
    task_id: int | None = None
    error_message: str | None = None
    text_payload: str | None = None
    robot_status: RobotStatus | None = None

    @classmethod
    def from_pb(cls, pb_response: pb.ServerResponse) -> ServerResponse:
        status_obj = None
        text_content = None

        payload_type = pb_response.WhichOneof("payload")

        if payload_type == "robot_status":
            status_obj = RobotStatus.from_pb(pb_response.robot_status)
        elif payload_type == "text_payload":
            text_content = pb_response.text_payload

        err_msg = pb_response.error_message if pb_response.error_message else None

        return cls(
            status=ResponseStatus(pb_response.status),
            task_status=TaskStatus(pb_response.task_status),
            task_id=pb_response.task_id if pb_response.task_id != 0 else None,
            error_message=err_msg,
            text_payload=text_content,
            robot_status=status_obj
        )


def as_pb_robtarget(target: RobTarget | pb.RobTarget) -> pb.RobTarget:
    """
    Helper function to safely extract or convert a Protocol Buffer RobTarget.
    """
    if isinstance(target, pb.RobTarget):
        return target

    if isinstance(target, RobTarget):
        return target.to_pb()

    raise TypeError(f"target must be RobTarget or pb.RobTarget, got {type(target)!r}")


def as_pb_jointtarget(target: JointTarget | pb.JointTarget) -> pb.JointTarget:
    """
    Helper function to safely extract or convert a Protocol Buffer JointTarget.
    """
    if isinstance(target, pb.JointTarget):
        return target

    if isinstance(target, JointTarget):
        return target.to_pb()

    raise TypeError(f"target must be JointTarget or pb.JointTarget, got {type(target)!r}")
