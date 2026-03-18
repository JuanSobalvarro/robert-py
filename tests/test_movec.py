from robert.client import RobeRTClient
from robert.protocol import RobTarget, RobJoint, Zone


def draw_circle(client: RobeRTClient, center_x: float, center_y: float, z: float, radius: float):
    init_point = (center_x + radius, center_y, z)
    mid_point_up = (center_x, center_y + radius, z)
    mid_point_down = (center_x, center_y - radius, z)
    left_point = (center_x - radius, center_y, z)

    client.movej(RobTarget(*init_point, 0.0, 0.0, -1.0, 0.0, 0, 0, -1, 0))

    # upper arc
    client.movec(RobTarget(*mid_point_up, 0.0, 0.0, -1.0, 0.0, 0, 0, -1, 0), RobTarget(*left_point, 0.0, 0.0, -1.0, 0.0, 0, 0, -1, 0))

    # lower arc
    client.movec(RobTarget(*mid_point_down, 0.0, 0.0, -1.0, 0.0, 0, 0, -1, 0), RobTarget(*init_point, 0.0, 0.0, -1.0, 0.0, 0, 0, -1, 0))

def main():

    client = RobeRTClient("tcp://localhost:42069")

    client.connect()

    response = client.ping_robot()
    print(f"Ping Response: {response}")
    if response[:3] == "ERR":
        print("Error pinging robot. Check connection and try again.")
        return

    response = client.set_speed(200.0)
    response = client.set_zone(Zone.Z30) 

    response = client.move_zero()
    print(f"Move Zero Response: {response}")

    client.movej(RobTarget(500.0, 0.0, 450.0, 0.0, 0.0, -1.0, 0.0, 0, 0, -1, 0))

    draw_circle(client, center_x=500.0, center_y=0.0, z=400.0, radius=100.0)

    client.set_zone(Zone.FINE)

    response = client.move_zero()
    print(f"Move Zero Response: {response}")

if __name__ == "__main__":
    main()