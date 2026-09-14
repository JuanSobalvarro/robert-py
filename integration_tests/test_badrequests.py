import robert as rb

def draw_squares(client: rb.RobeRTClient, center: tuple[float, float, float], square_size: float = 100, n_squares: int = 1):
    client.movej(rb.RobTarget(center, (0, 0, 1, 0)))

    client.move_j_offs(x=square_size/2, y=square_size/2)

    client.move_l_offs(z=-50)

    for _ in range(n_squares):
        client.move_l_offs(x=-square_size, y=0)
        client.move_l_offs(x=0, y=-square_size)
        client.move_l_offs(x=square_size, y=0)
        client.move_l_offs(x=0, y=square_size)

    # return to original position
    client.move_l_offs(z=50)
    client.movej(rb.RobTarget(center, (0, 0, 1, 0)))

def draw_circles(client: rb.RobeRTClient):
    pass

def wave(client: rb.RobeRTClient, n_waves: int = 3):
    client.move_zero()

    client.set_speed(200)

    current_target = client.get_status().robot_status.current_target

    # set orientation to face the wave direction
    client.movej(rb.RobTarget(current_target.trans, (0.707, 0, 0.707, 0)))

    # now do arcs to the left and right
    for _ in range(n_waves):
        client.move_j_offs(y=-100, z=-50)
        client.move_j_offs(y=100, z=50)
        client.move_j_offs(y=100, z=-50)
        client.move_j_offs(y=-100, z=50)

    client.set_speed(100)
    client.move_zero()


def main():
    target = rb.RobTarget((500, 0, 500), (0, 0, 1, 0))

    print(f"Default target: {target}")

    with rb.RobeRTClient("127.0.0.1", 42069, wait_for_all=True) as client:
        client.login("uwunyaguy", "uwunyanichan")
        client.acquire()

        client.set_speed(100)
        client.set_zone(rb.Zone.FINE)

        client.movej(target)

        draw_squares(client, (500, 0, 500), square_size=100, n_squares=2)

        draw_circles(client)

        wave(client)

        client.move_zero()

if __name__ == "__main__":
    main()
