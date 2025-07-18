import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches

# Process class
class Process:
    def __init__(self, pid, arrival, burst, priority):
        self.pid = pid
        self.arrival = arrival
        self.burst = burst
        self.priority = priority
        self.remaining = burst
        self.start = None
        self.completion = 0
        self.waiting = 0
        self.turnaround = 0

# Scheduling algorithm
def priority_preemptive(processes):
    time = 0
    completed = 0
    n = len(processes)
    timeline = []
    log = []
    ready_queue = []
    current = None

    processes.sort(key=lambda p: p.arrival)

    while completed < n:
        for p in processes:
            if p.arrival == time:
                ready_queue.append(p)
                log.append(f"Time {time}: Process P{p.pid} (Priority {p.priority}) arrived.")

        ready_queue = [p for p in ready_queue if p.remaining > 0]
        ready_queue.sort(key=lambda p: (p.priority, p.arrival))

        if ready_queue:
            if current != ready_queue[0]:
                current = ready_queue[0]
                if current.start is None:
                    current.start = time
                log.append(f"Time {time}: Switched to P{current.pid} (Priority {current.priority}).")
            else:
                log.append(f"Time {time}: Continuing P{current.pid}.")

            current.remaining -= 1
            timeline.append((time, current.pid, f"Executing P{current.pid} (Priority {current.priority})"))

            if current.remaining == 0:
                current.completion = time + 1
                current.turnaround = current.completion - current.arrival
                current.waiting = current.turnaround - current.burst
                log.append(f"Time {time+1}: Process P{current.pid} completed.")
                completed += 1
                current = None
        else:
            timeline.append((time, None, "CPU Idle"))

        time += 1

    return processes, timeline, log

# Timeline Visualizer
def visualize_dynamic_timeline(timeline):
    fig, ax = plt.subplots(figsize=(16, 3.5))
    ax.set_xlim(0, len(timeline) + 1)
    ax.set_ylim(-0.5, 1.5)
    ax.axis('off')

    explanation_box = ax.text(0, 1.2, "", fontsize=12, ha='left', wrap=True)

    def animate(i):
        if i >= len(timeline): return
        time, pid, explanation = timeline[i]
        color = "#cccccc" if pid is None else f"C{pid % 10}"
        rect = patches.Rectangle((time, 0), 1, 1, facecolor=color, edgecolor='black', linewidth=1.5)
        ax.add_patch(rect)
        label = "Idle" if pid is None else f"P{pid}"
        ax.text(time + 0.5, 0.5, label, ha='center', va='center', fontsize=11, fontweight='bold')
        ax.text(time, -0.3, f"{time}", ha='center', fontsize=9)
        explanation_box.set_text(explanation)

    ani = animation.FuncAnimation(fig, animate, frames=len(timeline), interval=600, repeat=False)
    plt.title("Priority Scheduling (Preemptive) - Gantt Chart", fontsize=15, fontweight='bold')
    plt.tight_layout()
    plt.show()

# GUI Class
class PriorityGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Priority Scheduling (Preemptive)")
        self.root.geometry("780x600")
        self.root.configure(bg="#f2f2f2")

        title = tk.Label(root, text="Preemptive Priority Scheduling", font=("Arial", 18, "bold"), bg="#f2f2f2")
        title.pack(pady=10)

        input_frame = tk.Frame(root, bg="#f2f2f2")
        input_frame.pack(pady=10)

        self.entries = {}
        fields = ["Number of Processes", "Arrival Times", "Burst Times", "Priorities"]
        for i, label_text in enumerate(fields):
            label = tk.Label(input_frame, text=label_text + ":", font=("Arial", 12), bg="#f2f2f2")
            label.grid(row=i, column=0, sticky='e', padx=5, pady=5)
            entry = tk.Entry(input_frame, width=50)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.entries[label_text] = entry

        run_btn = tk.Button(root, text="Run Scheduler", font=("Arial", 12, "bold"),
                            bg="#4CAF50", fg="white", command=self.run_scheduler)
        run_btn.pack(pady=10)

        self.result_frame = tk.Frame(root, bg="#f2f2f2")
        self.result_frame.pack(pady=10)

    def run_scheduler(self):
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        try:
            n = int(self.entries["Number of Processes"].get())
            arrival = list(map(int, self.entries["Arrival Times"].get().split()))
            burst = list(map(int, self.entries["Burst Times"].get().split()))
            priority = list(map(int, self.entries["Priorities"].get().split()))

            if not (len(arrival) == len(burst) == len(priority) == n):
                raise ValueError
        except:
            messagebox.showerror("Input Error", "Please check the entered values.")
            return

        processes = [Process(i + 1, arrival[i], burst[i], priority[i]) for i in range(n)]
        scheduled, timeline, log = priority_preemptive(processes)

        # Table
        cols = ("PID", "Arrival", "Burst", "Priority", "Start", "Completion", "Turnaround", "Waiting")
        tree = ttk.Treeview(self.result_frame, columns=cols, show='headings')
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, anchor='center', width=90)
        tree.pack()

        total_tat, total_wt = 0, 0
        for p in scheduled:
            total_tat += p.turnaround
            total_wt += p.waiting
            tree.insert('', 'end', values=(p.pid, p.arrival, p.burst, p.priority, p.start,
                                           p.completion, p.turnaround, p.waiting))

        avg_tat = total_tat / n
        avg_wt = total_wt / n

        avg_label = tk.Label(self.result_frame,
                             text=f"Average Turnaround Time: {avg_tat:.2f}    Average Waiting Time: {avg_wt:.2f}",
                             font=("Arial", 12, "bold"), bg="#f2f2f2", pady=10)
        avg_label.pack()

        visualize_dynamic_timeline(timeline)

# Main
def main():
    root = tk.Tk()
    app = PriorityGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
