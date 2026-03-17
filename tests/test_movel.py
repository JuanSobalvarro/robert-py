from robert.client import RobeRTClient
from robert.protocol import RobTarget, RobJoint, Zone

def draw_square(client: RobeRTClient, center_x: float, center_y: float, z: float, size: float):
    half_size = size / 2.0

    corners = [
        (center_x - half_size, center_y - half_size, z),  # Bottom-left
        (center_x + half_size, center_y - half_size, z),  # Bottom-right
        (center_x + half_size, center_y + half_size, z),  # Top-right
        (center_x - half_size, center_y + half_size, z),  # Top-left
        (center_x - half_size, center_y - half_size, z),  # Bottom-left to close the square
    ]

    for corner in corners:
        target = RobTarget(corner[0], corner[1], corner[2], 0.0, 0.0, -1.0, 0.0, 0, 0, -1, 0)
        response = client.movel(target)
        print(f"MoveL to {corner} Response: {response}")


def main():
    client = RobeRTClient("tcp://localhost:42069")

    client.connect()

    response = client.ping()
    print(f"Ping Response: {response}")

    response = client.set_speed(200.0)
    response = client.set_zone(Zone.Z10) 

    response = client.move_zero()
    print(f"Move Zero Response: {response}")

    client.movej(RobTarget(400.0, 0.0, 450.0, 0.0, 0.0, -1.0, 0.0, 0, 0, -1, 0))

    draw_square(client, center_x=400.0, center_y=0.0, z=400.0, size=50.0)

    response = client.move_zero()
    print(f"Move Zero Response: {response}")


if __name__ == "__main__":
    main()