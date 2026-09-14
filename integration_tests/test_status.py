import robert as rb

def main():

    with rb.RobeRTClient("localhost", 42069, wait_for_all=True) as client:
        client.login("uwunyaguy", "uwunyanichan")

        client.acquire()

        print(client.get_status())

if __name__ == "__main__":
    main()
