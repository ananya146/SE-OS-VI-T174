import tkinter as tk
from tkinter import messagebox, scrolledtext
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches

class Process:
    def __init__(self, pid, arrival, burst, queue_type):
        self.pid = pid
        self.arrival = arrival
        self.burst = burst
        self.remaining = burst
        self.queue_type = queue_type  # 0 = System (FCFS), 1 = User (RR)
        self.start = None
        self.completion = None
        self.executions = []

def multilevel_queue(processes, quantum_rr=4):
    processes.sort(key=lambda p: p.arrival)
    time = 0
    timeline = []
    queue0 = []
    queue1 = []
    i = 0
    n = len(processes)
    log = []

    while i < n or queue0 or queue1:
        while i < n and processes[i].arrival <= time:
            log.append(f"Time {time}: Process P{processes[i].pid} arrived (Queue: {processes[i].queue_type})")
            if processes[i].queue_type == 0:
                queue0.append(processes[i])
            else:
                queue1.append(processes[i])
            i += 1

        if queue0:
            curr = queue0.pop(0)
            if curr.start is None:
                curr.start = time
            explanation = f"At time {time}: P{curr.pid} selected from Queue 0 (FCFS)"
            for _ in range(curr.burst):
                timeline.append((time, curr.pid, explanation))
                time += 1
            curr.remaining = 0
            curr.completion = time
            curr.executions.append((curr.start, curr.completion))

        elif queue1:
            curr = queue1.pop(0)
            if curr.start is None:
                curr.start = time
            explanation = f"At time {time}: P{curr.pid} selected from Queue 1 (Round Robin)"
            exec_time = min(quantum_rr, curr.remaining)
            for _ in range(exec_time):
                timeline.append((time, curr.pid, explanation))
                time += 1
            curr.remaining -= exec_time
            if curr.remaining > 0:
                queue1.append(curr)
            else:
                curr.completion = time
            curr.executions.append((time - exec_time, time))

        else:
            timeline.append((time, None, "CPU Idle (No process available)"))
            time += 1

    return processes, timeline, log

def visualize_timeline(timeline):
    fig, ax = plt.subplots(figsize=(max(10, len(timeline) // 2), 3.5))
    final_time = max(time for time, _, _ in timeline) + 1
    ax.set_xlim(0, final_time)
    ax.set_ylim(-0.5, 1.5)
    ax.axis('off')

    explanation_box = ax.text(0, 1.2, "", fontsize=12, ha='left', wrap=True)

    def animate(i):
        if i >= len(timeline):
            return
        time, pid, explanation = timeline[i]
        color = "#bbbbbb" if pid is None else f"C{pid % 10}"
        rect = patches.Rectangle((time, 0), 1, 1, facecolor=color, edgecolor='black', linewidth=1.5)
        ax.add_patch(rect)
        label = "Idle" if pid is None else f"P{pid}"
        ax.text(time + 0.5, 0.5, label, ha='center', va='center', fontsize=12, fontweight='bold', color='white')
        explanation_box.set_text(explanation)

    ani = animation.FuncAnimation(fig, animate, frames=len(timeline), interval=600, repeat=False)
    plt.title("Multilevel Queue Scheduling", fontsize=15, fontweight='bold')
    plt.tight_layout()
    plt.show()

# --- GUI Section ---

def run_scheduler():
    try:
        num = int(entry_num.get())
        arrivals = list(map(int, entry_arrival.get().split()))
        bursts = list(map(int, entry_burst.get().split()))
        queues = list(map(int, entry_queue.get().split()))

        if not (len(arrivals) == len(bursts) == len(queues) == num):
            messagebox.showerror("Error", "Input lengths do not match number of processes.")
            return

        processes = [Process(i+1, arrivals[i], bursts[i], queues[i]) for i in range(num)]
        scheduled, timeline, log = multilevel_queue(processes)

        output.delete(1.0, tk.END)
        output.insert(tk.END, "--- Execution Log ---\n")
        for entry in log:
            output.insert(tk.END, entry + "\n")

        output.insert(tk.END, "\nPID | Arrival | Burst | Queue | Completion | Turnaround | Waiting\n")
        total_tat = total_wt = 0
        for p in scheduled:
            tat = p.completion - p.arrival
            wt = tat - p.burst
            total_tat += tat
            total_wt += wt
            output.insert(tk.END, f"{p.pid:3} | {p.arrival:7} | {p.burst:5} | {p.queue_type:^5} | {p.completion:10} | {tat:10} | {wt:7}\n")

        avg_tat = total_tat / num
        avg_wt = total_wt / num
        output.insert(tk.END, f"\nAverage Turnaround Time: {avg_tat:.2f}\n")
        output.insert(tk.END, f"Average Waiting Time: {avg_wt:.2f}\n")

        visualize_timeline(timeline)

    except Exception as e:
        messagebox.showerror("Error", str(e))

# Build GUI
root = tk.Tk()
root.title("Multilevel Queue Scheduling GUI")
root.geometry("700x650")
root.configure(bg="#f0f0f0")

tk.Label(root, text="Enter Number of Processes:", bg="#f0f0f0", font=("Arial", 11)).pack()
entry_num = tk.Entry(root, width=50)
entry_num.pack()

tk.Label(root, text="Enter Arrival Times (space separated):", bg="#f0f0f0", font=("Arial", 11)).pack()
entry_arrival = tk.Entry(root, width=50)
entry_arrival.pack()

tk.Label(root, text="Enter Burst Times (space separated):", bg="#f0f0f0", font=("Arial", 11)).pack()
entry_burst = tk.Entry(root, width=50)
entry_burst.pack()

tk.Label(root, text="Enter Queue Types (0 for FCFS, 1 for RR):", bg="#f0f0f0", font=("Arial", 11)).pack()
entry_queue = tk.Entry(root, width=50)
entry_queue.pack()

tk.Button(root, text="Run Scheduler", font=("Arial", 12, "bold"), bg="#4caf50", fg="white", command=run_scheduler).pack(pady=10)

output = scrolledtext.ScrolledText(root, width=80, height=20, font=("Courier", 10))
output.pack(pady=10)

root.mainloop()
def main():
    root = tk.Tk()
    app = Process(root)
    root.mainloop()

if __name__ == "__main__":
    main()