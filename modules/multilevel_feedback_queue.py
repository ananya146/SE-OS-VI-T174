import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches
from matplotlib.patches import Patch
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Process:
    def __init__(self, pid, arrival, burst):
        self.pid = pid
        self.arrival = arrival
        self.burst = burst
        self.remaining = burst
        self.queue_level = 0
        self.start = None
        self.completion = None
        self.turnaround = None
        self.waiting = None

def mlfq_custom_scheduler(processes, config):
    processes.sort(key=lambda p: p.arrival)
    time = 0
    completed = 0
    arrival_index = 0
    timeline = []
    queues = [[] for _ in range(len(config))]
    n = len(processes)

    while completed < n:
        while arrival_index < n and processes[arrival_index].arrival <= time:
            queues[0].append(processes[arrival_index])
            timeline.append((time, None, f"Time {time}: Process P{processes[arrival_index].pid} arrived and added to Queue 0."))
            arrival_index += 1

        queue_found = False

        for level, queue in enumerate(queues):
            if not queue:
                continue

            queue_found = True
            level_cfg = config[level]
            sched_type = level_cfg["type"]

            if sched_type == "RR":
                queue.sort(key=lambda p: p.arrival)
                curr = queue.pop(0)
                quantum = level_cfg["quantum"]
                exec_time = min(curr.remaining, quantum)
            elif sched_type == "SJF":
                queue.sort(key=lambda p: (p.remaining, p.arrival))
                curr = queue.pop(0)
                exec_time = curr.remaining
            elif sched_type == "FCFS":
                queue.sort(key=lambda p: p.arrival)
                curr = queue.pop(0)
                exec_time = curr.remaining

            if curr.start is None:
                curr.start = time

            explanation = f"Time {time}: Executing P{curr.pid} from Queue {level} ({sched_type}) for {exec_time} units."

            for _ in range(exec_time):
                timeline.append((time, curr.pid, explanation))
                time += 1
                while arrival_index < n and processes[arrival_index].arrival <= time:
                    queues[0].append(processes[arrival_index])
                    timeline.append((time, None, f"Time {time}: Process P{processes[arrival_index].pid} arrived and added to Queue 0."))
                    arrival_index += 1

            curr.remaining -= exec_time

            if curr.remaining == 0:
                curr.completion = time
                curr.turnaround = curr.completion - curr.arrival
                curr.waiting = curr.turnaround - curr.burst
                completed += 1
            else:
                if level + 1 < len(queues):
                    curr.queue_level = level + 1
                    queues[level + 1].append(curr)
                    timeline.append((time, None, f"Time {time}: P{curr.pid} demoted to Queue {level + 1}."))
                else:
                    queues[level].append(curr)
            break

        if not queue_found:
            timeline.append((time, None, "CPU Idle"))
            time += 1

    return processes, timeline

def visualize_queues(timeline, queue_config, processes, avg_tat, avg_wt):
    num_levels = len(queue_config)
    fig, ax = plt.subplots(figsize=(16, 3 + num_levels))
    ax.set_xlim(0, len(timeline))
    ax.set_ylim(-1.5, num_levels + 2)
    ax.axis('off')

    color_map = ['#5DADE2', '#58D68D', '#F4D03F', '#E59866', '#AF7AC5', '#85C1E9', '#F1948A']
    legend_patches = [Patch(color=color_map[p.pid % len(color_map)], label=f'P{p.pid}') for p in processes]
    ax.legend(handles=legend_patches, title='Process Color Legend', bbox_to_anchor=(1.01, 1), loc='upper left')

    for i in range(num_levels):
        ax.text(-1, num_levels - i - 0.5, f"Queue {i} ({queue_config[i]['type']})", va='center', fontsize=11, fontweight='bold')

    explanation_box = ax.text(0, num_levels + 0.4, "", fontsize=12, ha='left', wrap=True)

    def animate(i):
        if i >= len(timeline): return
        time, pid, explanation = timeline[i]
        explanation_box.set_text(explanation)

        if pid is None:
            ax.text(time + 0.5, num_levels + 0.2, "Idle" if "Idle" in explanation else "", ha='center', fontsize=8, color='gray')
        else:
            queue_level = 0
            for lvl in range(num_levels):
                if f"Queue {lvl}" in explanation:
                    queue_level = lvl
                    break
            y = num_levels - queue_level - 1
            color = color_map[pid % len(color_map)]
            rect = patches.Rectangle((time, y), 1, 1, facecolor=color, edgecolor='black', linewidth=1.5)
            ax.add_patch(rect)
            ax.text(time + 0.5, y + 0.5, f"P{pid}", ha='center', va='center', fontsize=11, fontweight='bold', color='white')

        ax.text(time + 0.5, -0.5, str(time), ha='center', va='top', fontsize=9)

    ani = animation.FuncAnimation(fig, animate, frames=len(timeline), interval=500, repeat=False)
    plt.title("Multilevel Feedback Queue - Dynamic Queue Panel", fontsize=15, fontweight='bold')
    plt.figtext(0.5, 0.01, f"Average Turnaround Time: {avg_tat:.2f}   |   Average Waiting Time: {avg_wt:.2f}", ha="center", fontsize=12)
    plt.tight_layout()
    plt.show()

# GUI Components
class MLFQApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MLFQ Scheduler GUI")

        self.process_entries = []
        self.queue_config_entries = []

        self.create_widgets()

    def create_widgets(self):
        frame = tk.Frame(self.root, padx=20, pady=20)
        frame.pack()

        tk.Label(frame, text="Number of Processes:").grid(row=0, column=0)
        self.num_proc_entry = tk.Entry(frame)
        self.num_proc_entry.grid(row=0, column=1)

        tk.Label(frame, text="Arrival Times (space-separated):").grid(row=1, column=0)
        self.arrival_entry = tk.Entry(frame, width=40)
        self.arrival_entry.grid(row=1, column=1)

        tk.Label(frame, text="Burst Times (space-separated):").grid(row=2, column=0)
        self.burst_entry = tk.Entry(frame, width=40)
        self.burst_entry.grid(row=2, column=1)

        tk.Label(frame, text="Number of Queues:").grid(row=3, column=0)
        self.num_queue_entry = tk.Entry(frame)
        self.num_queue_entry.grid(row=3, column=1)

        tk.Button(frame, text="Configure Queues", command=self.configure_queues).grid(row=4, column=0, columnspan=2, pady=5)
        tk.Button(frame, text="Run Scheduler", command=self.run_scheduler).grid(row=5, column=0, columnspan=2, pady=5)

        self.queue_frame = tk.Frame(self.root, padx=20, pady=10)
        self.queue_frame.pack()

    def configure_queues(self):
        for widget in self.queue_frame.winfo_children():
            widget.destroy()

        try:
            num_queues = int(self.num_queue_entry.get())
        except:
            messagebox.showerror("Error", "Enter valid number of queues")
            return

        self.queue_config_entries = []
        for i in range(num_queues):
            row_frame = tk.Frame(self.queue_frame)
            row_frame.pack(anchor='w')

            tk.Label(row_frame, text=f"Queue {i} Scheduling (RR/SJF/FCFS):").pack(side='left')
            algo_entry = ttk.Combobox(row_frame, values=["RR", "SJF", "FCFS"], width=5)
            algo_entry.set("FCFS")
            algo_entry.pack(side='left')

            quantum_entry = tk.Entry(row_frame, width=5)
            quantum_entry.pack(side='left')

            def toggle_quantum(event, qe=quantum_entry, ae=algo_entry):
                if ae.get() == "RR":
                    qe.config(state='normal')
                else:
                    qe.delete(0, tk.END)
                    qe.config(state='disabled')

            algo_entry.bind("<<ComboboxSelected>>", toggle_quantum)
            toggle_quantum(None)
            self.queue_config_entries.append((algo_entry, quantum_entry))


    def run_scheduler(self):
        try:
            num_processes = int(self.num_proc_entry.get())
            arrival_times = list(map(int, self.arrival_entry.get().split()))
            burst_times = list(map(int, self.burst_entry.get().split()))
            if len(arrival_times) != num_processes or len(burst_times) != num_processes:
                raise ValueError
        except:
            messagebox.showerror("Error", "Invalid process input")
            return

        processes = [Process(i + 1, arrival_times[i], burst_times[i]) for i in range(num_processes)]

        config = []
        for algo_entry, quantum_entry in self.queue_config_entries:
            algo = algo_entry.get()
            if algo not in ["RR", "SJF", "FCFS"]:
                messagebox.showerror("Error", f"Invalid scheduling algorithm: {algo}")
                return
            quantum = int(quantum_entry.get()) if algo == "RR" else None
            config.append({"type": algo, "quantum": quantum})

        completed_processes, timeline = mlfq_custom_scheduler(processes, config)
        avg_tat = sum(p.turnaround for p in completed_processes) / len(completed_processes)
        avg_wt = sum(p.waiting for p in completed_processes) / len(completed_processes)

        self.display_result_table(completed_processes, avg_tat, avg_wt)
        visualize_queues(timeline, config, completed_processes, avg_tat, avg_wt)

    def display_result_table(self, processes, avg_tat, avg_wt):
        if hasattr(self, 'tree'):
            self.tree.destroy()
        if hasattr(self, 'result_label'):
            self.result_label.destroy()

        result_frame = tk.Frame(self.root, padx=10, pady=10)
        result_frame.pack()

        cols = ("PID", "Arrival", "Burst", "Completion", "Turnaround", "Waiting", "Queue Level")
        self.tree = ttk.Treeview(result_frame, columns=cols, show='headings')
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor='center', width=100)

        for p in processes:
            self.tree.insert('', 'end', values=(f"P{p.pid}", p.arrival, p.burst, p.completion, p.turnaround, p.waiting, p.queue_level))

        self.tree.pack()

        self.result_label = tk.Label(result_frame, text=f"Average Turnaround Time: {avg_tat:.2f} | Average Waiting Time: {avg_wt:.2f}",
                                     font=("Arial", 12, "bold"))
        self.result_label.pack()

# Main Execution
def main():
    root = tk.Tk()
    app = MLFQApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
