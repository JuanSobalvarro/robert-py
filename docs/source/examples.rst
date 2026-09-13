Examples
========

This section provides practical examples of how to control the ABB IRB 140 robot and read its telemetry using the ``RobeRTClient``.

.. note::
    All examples below use the ``with`` statement (context manager) and set ``wait_for_all=True``. This ensures the script automatically waits for physical movements to finish before sending the next command, and guarantees the hardware lock is safely released when the script ends.

Relative Movements (Offsets)
----------------------------
The easiest way to move the robot is by applying offsets to its current position. This is highly useful for grid patterns, palletizing, or drawing shapes.

.. code-block:: python

    import robert as rb

    with rb.RobeRTClient("192.168.1.20", 42069, wait_for_all=True) as client:
        client.login("username", "password")
        client.acquire()

        client.set_speed(100) # 100 mm/s

        print("Drawing a 10cm square...")
        client.move_l_offs(x=0, y=100, z=0)
        client.move_l_offs(x=-100, y=0, z=0)
        client.move_l_offs(x=0, y=-100, z=0)
        client.move_l_offs(x=100, y=0, z=0)

        print("Returning to zero position...")
        client.move_zero()


Absolute Cartesian Movement (RobTarget)
---------------------------------------
To move the robot to a specific spatial coordinate, you must construct a ``RobTarget``. This requires defining the Position (x, y, z), Orientation (quaternions), Configuration Data, and External Joints.

.. code-block:: python

    import robert as rb

    # Define the target components
    position = rb.Position(x=450.0, y=0.0, z=500.0)
    orientation = rb.Orientation(q1=0.7071, q2=0.0, q3=0.7071, q4=0.0)
    config = rb.ConfData(cf1=0, cf4=0, cf6=0, cfx=0)

    # 9e9 is the standard RAPID value for unused external axes
    ext_joints = rb.ExtJoint(9e9, 9e9, 9e9, 9e9, 9e9, 9e9)

    # Assemble the final RobTarget
    target = rb.RobTarget(
        trans=position,
        rot=orientation,
        robconf=config,
        extax=ext_joints
    )

    with rb.RobeRTClient("192.168.1.20", 42069, wait_for_all=True) as client:
        client.login("username", "password")
        client.acquire()

        print("Moving to exact Cartesian coordinates via MoveJ...")
        client.movej(target)

        print("Moving to another Cartesian coordinate via MoveL (Linear)...")
        # You can also construct it inline:
        target.trans.z = 600.0
        client.movel(target)


Absolute Joint Movement (JointTarget)
-------------------------------------
Sometimes it is safer or necessary to move the robot by specifying the exact angle (in degrees) of its 6 internal axes using a ``JointTarget``.

.. code-block:: python

    import robert as rb

    # Define the angle for each of the 6 robot axes
    angles = rb.RobJoint(rax_1=45.0, rax_2=15.0, rax_3=0.0, rax_4=0.0, rax_5=30.0, rax_6=0.0)
    ext_joints = rb.ExtJoint(9e9, 9e9, 9e9, 9e9, 9e9, 9e9)

    joint_target = rb.JointTarget(robjoint=angles, extjoint=ext_joints)

    with rb.RobeRTClient("192.168.1.20", 42069, wait_for_all=True) as client:
        client.login("username", "password")
        client.acquire()

        print("Moving to specific joint angles...")
        client.moveabsj(joint_target)


Configuring Zones for Continuous Paths
--------------------------------------
By default, the robot stops exactly at each point (Zone FINE). If you want the robot to round the corners for a smoother, continuous path without stopping, you can change the Zone. Also remember that maybe you want to send asynchronous commands for this to work properly.

.. code-block:: python

    import robert as rb

    with rb.RobeRTClient("192.168.1.20", 42069, wait_for_all=False) as client:
        client.login("username", "password")
        client.acquire()

        # Set a 10mm fly-by zone. The robot will round the corner 10mm before reaching the exact point.
        client.set_zone(rb.Zone.Z10)
        client.set_speed(200)

        # These movements will blend together smoothly
        client.move_l_offs(x=50, y=0, z=0)
        client.move_l_offs(x=0, y=50, z=0)

        # Reset back to precise stops
        client.set_zone(rb.Zone.FINE)


Reading Telemetry & Robot Status
--------------------------------
You can retrieve the robot's real-time position and speed without moving it.

.. code-block:: python

    import robert as rb

    with rb.RobeRTClient("192.168.1.20", 42069) as client:
        client.login("username", "password")
        client.acquire()

        response = client.get_status()
        status = response.robot_status

        print("=== Robot Telemetry ===")
        print(f"Timestamp: {status.robot_date} {status.robot_time}")
        print(f"Current Speed: {status.current_speed} mm/s")

        pos = status.current_target.trans
        print(f"Cartesian Position -> X: {pos.x:.2f}, Y: {pos.y:.2f}, Z: {pos.z:.2f}")

        joints = status.current_joint_target.robjoint
        print(f"Axis 1 Angle: {joints.rax_1:.2f} degrees")
