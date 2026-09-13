import time
import concurrent.futures
import robert as rb

HOST = "localhost"
PORT = 42069
DURATION_SECONDS = 10
NUM_CONCURRENT_CLIENTS = 5

USERS = [
    ("uwunyaguy", "uwunyanichan"),
    ("chicojava", "tenesqueprobarnixos"),
    ("ariari", "iraira"),
    ("donbigo", "perosiesdonbigo"),
    ("skibidi", "toilet"),
]

def stress_client_task(client_id, username, password):
    request_count = 0
    failed_count = 0

    with rb.RobeRTClient(HOST, PORT, timeout=2000, wait_for_all=False) as client:
        try:
            client.login(username, password)

            end_time = time.time() + DURATION_SECONDS

            while time.time() < end_time:
                try:
                    client.ping()
                    request_count += 1
                except Exception:
                    failed_count += 1

        except Exception as e:
            print(f"Critical error at client {username}: {e}")

    return request_count, failed_count

def test_response_capacity():
    print(f"[*] Starting stress test ({NUM_CONCURRENT_CLIENTS} threads for {DURATION_SECONDS} s)...")

    total_requests = 0
    total_failed = 0

    start_time = time.perf_counter()

    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_CONCURRENT_CLIENTS) as executor:
        futures = [executor.submit(stress_client_task, i, *USERS[i]) for i in range(NUM_CONCURRENT_CLIENTS)]

        for future in concurrent.futures.as_completed(futures):
            reqs, fails = future.result()
            total_requests += reqs
            total_failed += fails

    real_duration = time.perf_counter() - start_time
    rps = total_requests / real_duration

    print("\n" + "="*50)
    print(" Stress Test Results ")
    print("="*50)
    print(f"Concurrent clients : {NUM_CONCURRENT_CLIENTS}")
    print(f"Duration : {real_duration:.2f} seconds")
    print(f"Successful requests : {total_requests}")
    print(f"Failed requests : {total_failed}")
    print(f"Capacity (RPS) : {rps:.2f} requests/second")
    print("="*50)

if __name__ == "__main__":
    test_response_capacity()
