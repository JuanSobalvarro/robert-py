import time
import robert as rb

def test_resilience():
    print("[*] Starting resilience test...")

    with rb.RobeRTClient("localhost", 42069, timeout=2000) as client:
        client.login("uwunyaguy", "uwunyanichan")
        client.acquire()

        print("\n[!] INSTRUCTION: Turn down the server or disconnect the network in the next 10 seconds.")

        for i in range(1, 21):
            try:
                start_req = time.perf_counter()
                client.get_status()
                rtt = (time.perf_counter() - start_req) * 1000
                print(f"[{i}/20] Request successful. RTT: {rtt:.2f} ms")
                time.sleep(1)

            except RuntimeError as e:
                error_msg = str(e)
                print(f"\n[FAULT DETECTED] Attempt {i} failed: {error_msg}")

                # If the server rejected our token, we need to log back in!
                if "Invalid token" in error_msg or "Unauthorized" in error_msg:
                    print("[*] Server reset detected. Attempting to re-authenticate...")
                    try:
                        client.login("uwunyaguy", "uwunyanichan")
                        client.acquire()
                        print("[+] Successfully re-authenticated and acquired lock!")
                    except Exception as login_err:
                        print(f"[-] Re-authentication failed: {login_err}")

                print("[*] Resuming test in 2 seconds...")
                time.sleep(2)

        print("\n[*] Resilience test finished.")

if __name__ == "__main__":
    test_resilience()
