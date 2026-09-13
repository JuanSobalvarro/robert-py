import time
import statistics
import robert as rb

def run_latency_test(client, test_name, command_func, iterations=100, delay=0.05):
    """
    Executes a function repeatedly and calculates latency statistics.
    """
    print(f"\nStarting {test_name} ({iterations} iterations)...")
    latencies = []
    failed_requests = 0

    # warm up tcp (yes, warm up hah)
    for _ in range(5):
        try:
            command_func()
        except Exception:
            pass

    # Testing phase
    for i in range(iterations):
        try:
            start_time = time.perf_counter()
            command_func()
            end_time = time.perf_counter()

            latencies.append((end_time - start_time) * 1000)
        except Exception as e:
            failed_requests += 1
            print(f"Request {i} failed: {e}")

        time.sleep(delay) # prevent TCP buffer flooding

    if not latencies:
        print("Test failed: All requests timed out or errored.")
        return None

    stats = {
        "Name": test_name,
        "Min (ms)": min(latencies),
        "Max (ms)": max(latencies),
        "Avg (ms)": statistics.mean(latencies),
        "Jitter (ms)": statistics.stdev(latencies) if len(latencies) > 1 else 0,
        "Packet Loss (%)": (failed_requests / iterations) * 100
    }
    return stats

def print_results_table(results):
    print("\n" + "="*85)
    print(f"{'ROBERT TESTING UWU':<25} | {'MIN (ms)':<10} | {'MAX (ms)':<10} | {'AVG (ms)':<10} | {'JITTER':<10} | {'LOSS (%)':<10}")
    print("-" * 85)
    for res in results:
        if res:
            print(f"{res['Name']:<25} | {res['Min (ms)']:<10.3f} | {res['Max (ms)']:<10.3f} | {res['Avg (ms)']:<10.3f} | {res['Jitter (ms)']:<10.3f} | {res['Packet Loss (%)']:<10.1f}")
    print("="*85 + "\n")

def main():
    HOST = "localhost"
    PORT = 42069
    ITERATIONS = 100

    # wait_for_all=True makes sure we wait for all tasks to complete before returning
    # this means if we send a full end-to-end request, we will wait for the robot to complete the task and return the data we want not just the task id
    with rb.RobeRTClient(HOST, PORT, timeout=2000, wait_for_all=True) as client:
        try:
            client.login("uwunyaguy", "uwunyanichan")
            client.acquire()

            results = []

            # First test: middleware performance on processing pings
            # isolate middleware response from the robot hardware
            res_mid = run_latency_test(client, "Server ping", client.ping, ITERATIONS)
            results.append(res_mid)

            # Second test: full end-to-end latency
            # tests robert-py -> robert-middleware -> RAPID server -> robert-middleware -> robert-py
            res_bot = run_latency_test(client, "Full communication", client.ping_robot, ITERATIONS)
            results.append(res_bot)

            # Third test: status retrieval latency
            # how fast the middleware can serialize and transmit the complex RobotStatus Protobuf
            res_status = run_latency_test(client, "Robot Status payload", client.get_status, ITERATIONS)
            results.append(res_status)

            print_results_table(results)

        except Exception as e:
            print(f"\nfailure during testing: {e}")

if __name__ == "__main__":
    main()
