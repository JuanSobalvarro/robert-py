from robert.client import RobeRTClient
from robert.protocol import RobTarget, RobJoint

import time
 
def main():
    client = RobeRTClient("tcp://localhost:42069")
    client.connect()

    response = client.ping()

    print(f"Ping Response: {response}")

    print(f"Sending setspeed at time: {time.strftime('%H:%M:%S', time.localtime())}")
    response = client.set_speed(150.0)
    
    response = client.movej(RobTarget(400.0, 0.0, 400.0, 0.0, 0.0, -1.0, 0.0, 0, 0, -1, 0))
    print(f"MoveJ Response: {response}")

    response = client.movej(RobTarget(450.0, 0.0, 450.0, 0.0, 0.0, -1.0, 0.0, 0, 0, -1, 0))
    print(f"MoveJ Response: {response}")

    # response = client.moveabsj(RobJoint(0.0, 0.0, 0.0, 0.0, 0.0, 0.0))
    # print(f"MoveAbsJ Response: {response}")

    # print(f"Last execution at time: {time.strftime('%H:%M:%S', time.localtime())}")
    response = client.set_speed(1000.0)
    print(f"Set Speed Response: {response}")

    response = client.moveabsj(RobJoint(0.0, 0.0, 0.0, 0.0, 0.0, 0.0))
    print(f"MoveAbsJ Response: {response}")

if __name__ == "__main__":
    main()