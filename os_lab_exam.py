#!/usr/bin/env python3
"""
Operating Systems Laboratory Exam
CPU Scheduling + Banker's Algorithm

Algorithms implemented:
1. FCFS (First Come First Serve) - Non-Preemptive
2. Round Robin - Preemptive
3. Banker's Algorithm - Deadlock Avoidance
"""

from collections import deque


def read_nonnegative_int(prompt):
    """Read an integer that is zero or greater."""
    while True:
        try:
            value = int(input(prompt))
            if value >= 0:
                return value
            print("Please enter a non-negative integer.")
        except ValueError:
            print("Invalid input. Please enter an integer.")


def read_positive_int(prompt):
    """Read an integer greater than zero."""
    while True:
        value = read_nonnegative_int(prompt)
        if value > 0:
            return value
        print("Please enter a value greater than zero.")


def get_process_input():
    """Get process arrival and burst times from the user."""
    n = read_positive_int("Enter number of processes: ")
    processes = []

    print("\nEnter arrival time and burst time for each process.")
    for i in range(n):
        pid = f"P{i + 1}"
        arrival = read_nonnegative_int(f"{pid} Arrival Time: ")
        burst = read_positive_int(f"{pid} Burst Time: ")
        processes.append({
            "pid": pid,
            "arrival": arrival,
            "burst": burst,
            "index": i
        })

    return processes


def merge_gantt(gantt):
    """
    Merge consecutive Gantt entries having the same process.
    Each entry has the form: [process_name, start_time, end_time].
    """
    if not gantt:
        return []

    merged = [gantt[0][:]]
    for pid, start, end in gantt[1:]:
        if merged[-1][0] == pid and merged[-1][2] == start:
            merged[-1][2] = end
        else:
            merged.append([pid, start, end])
    return merged


def print_gantt_chart(gantt):
    """Display a simple text-based Gantt chart with time markers."""
    gantt = merge_gantt(gantt)

    print("\nGANTT CHART")
    print("-" * 60)

    # Process execution row
    print(" | ".join(f"{pid} [{start}-{end}]" for pid, start, end in gantt))
    print("-" * 60)


def print_scheduling_results(title, processes, completion, gantt):
    """Calculate and display CT, TAT, WT, averages, and Gantt chart."""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

    print_gantt_chart(gantt)

    total_waiting = 0
    total_turnaround = 0

    print("\nPROCESS TABLE")
    print(f"{'Process':<10}{'AT':<8}{'BT':<8}{'CT':<8}{'TAT':<10}{'WT':<8}")
    print("-" * 52)

    # Keep output in original process order.
    for p in sorted(processes, key=lambda x: x["index"]):
        pid = p["pid"]
        at = p["arrival"]
        bt = p["burst"]
        ct = completion[pid]
        tat = ct - at
        wt = tat - bt

        total_turnaround += tat
        total_waiting += wt

        print(f"{pid:<10}{at:<8}{bt:<8}{ct:<8}{tat:<10}{wt:<8}")

    n = len(processes)
    avg_waiting = total_waiting / n
    avg_turnaround = total_turnaround / n

    print("-" * 52)
    print(f"Average Waiting Time    : {avg_waiting:.2f}")
    print(f"Average Turnaround Time : {avg_turnaround:.2f}")


def fcfs(processes):
    """
    First Come First Serve (FCFS)
    Non-preemptive: once a process gets the CPU, it runs until completion.
    """
    # For equal arrival times, preserve the user's original process order.
    order = sorted(processes, key=lambda p: (p["arrival"], p["index"]))

    time = 0
    completion = {}
    gantt = []

    for p in order:
        # CPU is idle if the next process has not arrived yet.
        if time < p["arrival"]:
            gantt.append(["IDLE", time, p["arrival"]])
            time = p["arrival"]

        start = time
        time += p["burst"]
        gantt.append([p["pid"], start, time])
        completion[p["pid"]] = time

    print_scheduling_results(
        "FCFS - NON-PREEMPTIVE CPU SCHEDULING",
        processes,
        completion,
        gantt
    )


def round_robin(processes, quantum):
    """
    Round Robin Scheduling
    Preemptive: each ready process receives at most one time quantum.
    New arrivals are added to the ready queue as time advances.
    """
    n = len(processes)
    ordered = sorted(processes, key=lambda p: (p["arrival"], p["index"]))

    remaining = {p["pid"]: p["burst"] for p in processes}
    completion = {}
    gantt = []

    ready = deque()
    time = 0
    next_arrival_index = 0
    completed = 0

    while completed < n:
        # If no process is ready, jump to the next arrival.
        if not ready:
            if next_arrival_index < n and time < ordered[next_arrival_index]["arrival"]:
                next_time = ordered[next_arrival_index]["arrival"]
                gantt.append(["IDLE", time, next_time])
                time = next_time

            # Add every process that has arrived by the current time.
            while (
                next_arrival_index < n
                and ordered[next_arrival_index]["arrival"] <= time
            ):
                ready.append(ordered[next_arrival_index])
                next_arrival_index += 1

        current = ready.popleft()
        pid = current["pid"]

        run_time = min(quantum, remaining[pid])
        start = time
        time += run_time
        remaining[pid] -= run_time
        gantt.append([pid, start, time])

        # Processes that arrived during this time slice enter the queue first.
        while (
            next_arrival_index < n
            and ordered[next_arrival_index]["arrival"] <= time
        ):
            ready.append(ordered[next_arrival_index])
            next_arrival_index += 1

        # If the current process is unfinished, put it at the back of the queue.
        if remaining[pid] > 0:
            ready.append(current)
        else:
            completion[pid] = time
            completed += 1

    print_scheduling_results(
        f"ROUND ROBIN - PREEMPTIVE CPU SCHEDULING (Quantum = {quantum})",
        processes,
        completion,
        gantt
    )


def read_vector(prompt, size):
    """Read exactly 'size' non-negative integers from one line."""
    while True:
        try:
            values = list(map(int, input(prompt).split()))
            if len(values) != size:
                print(f"Please enter exactly {size} values.")
                continue
            if any(v < 0 for v in values):
                print("Values cannot be negative.")
                continue
            return values
        except ValueError:
            print("Invalid input. Enter integers separated by spaces.")


def bankers_algorithm():
    """
    Banker's Algorithm safety check.

    Need = Maximum - Allocation

    A process can finish if Need <= Work (currently available resources).
    After it finishes, its allocated resources are returned to Work.
    If all processes can finish, the system is safe.
    """
    print("\n" + "=" * 70)
    print("BANKER'S ALGORITHM - DEADLOCK AVOIDANCE")
    print("=" * 70)

    n = read_positive_int("Enter number of processes: ")
    m = read_positive_int("Enter number of resource types: ")

    print("\nEnter the ALLOCATION matrix.")
    print(f"Enter {m} integers per process, separated by spaces.")
    allocation = []
    for i in range(n):
        allocation.append(read_vector(f"P{i} Allocation: ", m))

    print("\nEnter the MAXIMUM matrix.")
    print(f"Enter {m} integers per process, separated by spaces.")
    maximum = []
    for i in range(n):
        maximum.append(read_vector(f"P{i} Maximum: ", m))

    # Maximum demand should never be less than current allocation.
    for i in range(n):
        for j in range(m):
            if maximum[i][j] < allocation[i][j]:
                print(
                    f"\nInvalid data: P{i} maximum for resource R{j} "
                    "is less than its current allocation."
                )
                return

    available = read_vector(
        f"\nEnter AVAILABLE resources ({m} integers): ",
        m
    )

    # Compute remaining resources each process may still request.
    need = [
        [maximum[i][j] - allocation[i][j] for j in range(m)]
        for i in range(n)
    ]

    work = available[:]
    finish = [False] * n
    safe_sequence = []

    while len(safe_sequence) < n:
        progress = False

        for i in range(n):
            if not finish[i]:
                can_finish = all(need[i][j] <= work[j] for j in range(m))

                if can_finish:
                    # Simulate process completion and resource release.
                    for j in range(m):
                        work[j] += allocation[i][j]

                    finish[i] = True
                    safe_sequence.append(f"P{i}")
                    progress = True

        # If no unfinished process can run, no safe sequence exists.
        if not progress:
            break

    print("\nNEED MATRIX")
    header = "       " + " ".join(f"R{j:<4}" for j in range(m))
    print(header)
    print("-" * len(header))
    for i, row in enumerate(need):
        print(f"P{i:<5} " + " ".join(f"{value:<5}" for value in row))

    print("\nRESULT")
    print("-" * 40)

    if len(safe_sequence) == n:
        print("The system is in a SAFE STATE.")
        print("Safe Sequence: " + " -> ".join(safe_sequence))
    else:
        print("The system is in an UNSAFE STATE.")
        print("Safe Sequence: None")


def cpu_scheduling_menu():
    """CPU scheduling submenu."""
    while True:
        print("\n" + "=" * 70)
        print("CPU SCHEDULING")
        print("=" * 70)
        print("1. FCFS (Non-Preemptive)")
        print("2. Round Robin (Preemptive)")
        print("3. Back to Main Menu")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            processes = get_process_input()
            fcfs(processes)

        elif choice == "2":
            processes = get_process_input()
            quantum = read_positive_int("\nEnter Time Quantum: ")
            round_robin(processes, quantum)

        elif choice == "3":
            return

        else:
            print("Invalid option. Please choose 1, 2, or 3.")


def main():
    """Main menu for the complete Operating Systems lab program."""
    while True:
        print("\n" + "=" * 70)
        print("OPERATING SYSTEMS LAB EXAM")
        print("=" * 70)
        print("1. CPU Scheduling")
        print("2. Banker's Algorithm")
        print("3. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            cpu_scheduling_menu()

        elif choice == "2":
            bankers_algorithm()

        elif choice == "3":
            print("\nProgram terminated. Thank you!")
            break

        else:
            print("Invalid option. Please choose 1, 2, or 3.")


if __name__ == "__main__":
    main()
