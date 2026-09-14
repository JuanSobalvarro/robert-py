import pytest
import math
from robert.protocol import Position, Orientation, ConfData, ExtJoint, RobTarget, JointTarget

def test_orientation_validation():
    """Test that valid quaternions are accepted and invalid ones are rejected."""
    o_valid1 = Orientation(1.0, 0.0, 0.0, 0.0)
    assert o_valid1.q1 == 1.0

    o_valid2 = Orientation(0.707, 0.0, 0.707, 0.0)
    assert o_valid2.q1 == 0.707

    with pytest.raises(ValueError, match="Invalid quaternion: The norm must be 1.0"):
        Orientation(1.0, 1.0, 1.0, 1.0)

    with pytest.raises(ValueError, match="Invalid quaternion: The norm must be 1.0"):
        Orientation(0.0, 0.0, 0.0, 0.0)


def test_robtarget_defaults_and_assignment():
    """Test the UX improvements in RobTarget (defaults and magic list assignment)."""
    target = RobTarget(trans=Position(500, 0, 450))

    assert target.trans.x == 500.0
    assert target.rot.q1 == 0.707
    assert target.robconf.cf6 == -1
    assert target.extax.eax_a == 9e9

    target.rot = [0, 0, -1, 0]

    assert isinstance(target.rot, Orientation)
    assert target.rot.q3 == -1.0

    with pytest.raises(ValueError, match="exactly 4 elements"):
        target.rot = [1, 0, 0]

    with pytest.raises(ValueError, match="Invalid quaternion"):
        target.rot = [5.0, 0, 0, 0]


def test_protobuf_serialization():
    """Test that data serializes to protobuf and reconstructs perfectly."""
    original_target = RobTarget(
        trans=Position(123.4, 567.8, 910.11),
        rot=Orientation(1.0, 0.0, 0.0, 0.0),
        robconf=ConfData(1, 2, 3, 4),
        extax=ExtJoint(10.0, 20.0, 9e9, 9e9, 9e9, 9e9)
    )

    pb_obj = original_target.to_pb()

    assert math.isclose(pb_obj.trans.x, 123.4, rel_tol=1e-5)
    assert pb_obj.robconf.cf1 == 1

    reconstructed_target = RobTarget.from_pb(pb_obj)

    assert math.isclose(reconstructed_target.trans.y, original_target.trans.y, rel_tol=1e-5)
    assert math.isclose(reconstructed_target.extax.eax_b, original_target.extax.eax_b, rel_tol=1e-5)
