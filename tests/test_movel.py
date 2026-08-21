from robert.client import RobeRTClient
from robert.protocol import RobTarget, Zone, Position, Orientation, ConfData, ExtJoint

def draw_square(client: RobeRTClient, center_x: float, center_y: float, z: float, size: float):
    half_size = size / 2.0

    corners = [
        (center_x - half_size, center_y - half_size, z),  # Bottom-left
        (center_x + half_size, center_y - half_size, z),  # Bottom-right
        (center_x + half_size, center_y + half_size, z),  # Top-right
        (center_x - half_size, center_y + half_size, z),  # Top-left
        (center_x - half_size, center_y - half_size, z),  # Bottom-left to close the square
    ]

    target = RobTarget(
        trans=Position(corners[0][0], corners[0][1], corners[0][2]),
        rot=Orientation(0.0, 0.0, -1.0, 0.0),
        robconf=ConfData(0, 0, -1, 0),
        extax=ExtJoint(9e9, 9e9, 9e9, 9e9, 9e9, 9e9)
    )
    for corner in corners:
        target.trans.x = corner[0]
        target.trans.y = corner[1]
        target.trans.z = corner[2]
        response = client.movel(target)
        print(f"MoveL to {corner} Response: {response}")


def main():
    client = RobeRTClient("tcp://localhost:42069")

    client.connect()

    response = client.ping()
    print(f"Ping Response: {response}")

    response = client.set_speed(200.0)
    response = client.set_zone(Zone.FINE) 

    response = client.move_zero()
    print(f"Move Zero Response: {response}")

    client.movej(RobTarget(
        trans=Position(500.0, 0.0, 450.0),
        rot=Orientation(0.0, 0.0, -1.0, 0.0),
        robconf=ConfData(0, 0, -1, 0),
        extax=ExtJoint(9e9, 9e9, 9e9, 9e9, 9e9, 9e9)
    ))

    draw_square(client, center_x=400.0, center_y=0.0, z=400.0, size=50.0)

    response = client.set_zone(Zone.FINE)
    response = client.move_zero()
    print(f"Move Zero Response: {response}")


if __name__ == "__main__":
    main()