import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches
from matplotlib.patches import Patch
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class Process:
    def __init__(self, pid, arrival, burst, io_burst=0):
        self.pid = pid
        self.arrival = arrival
        self.burst = burst
        self.io_burst = io_burst
        self.start = None
        self.completion = None
        self.turnaround = None
        self.waiting = None


def fcfs_dynamic(processes):
    processes.sort(key=lambda p: (p.arrival, p.pid))
    time = 0
    timeline = []

    for p in processes:
        if time < p.arrival:
            for idle in range(time, p.arrival):
                timeline.append((idle, None, "CPU Idle (No process has arrived yet)"))
            time = p.arrival

        p.start = time
        for _ in range(p.burst):
            explanation = f"At time {time}: Process P{p.pid} selected (Arrival: {p.arrival})"
            timeline.append((time, p.pid, explanation))
            time += 1

        if p.io_burst > 0:
            for _ in range(p.io_burst):
                explanation = f"At time {time}: I/O in progress for Process P{p.pid}"
                timeline.append((time, None, explanation))
                time += 1

        p.completion = time
        p.turnaround = p.completion - p.arrival
        p.waiting = p.turnaround - (p.burst + p.io_burst)

    return processes, timeline


def manual_gantt_stepper(timeline, processes):
    step_window = tk.Toplevel()
    step_window.title("Manual Gantt Chart (Step by Step)")
    step_window.geometry("1100x450")

    fig, ax = plt.subplots(figsize=(14, 3.5))
    canvas = FigureCanvasTkAgg(fig, master=step_window)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    ax.set_xlim(0, len(timeline))
    ax.set_ylim(-0.5, 1.5)
    ax.axis('off')

    explanation_box = ax.text(0, 1.2, "", fontsize=12, ha='left', wrap=True)
    color_map = ['#5DADE2', '#58D68D', '#F4D03F', '#E59866', '#AF7AC5', '#85C1E9', '#F1948A']
    legend_patches = [Patch(color=color_map[p.pid % len(color_map)], label=f'P{p.pid}') for p in processes]
    ax.legend(handles=legend_patches, title='Processes', bbox_to_anchor=(1.01, 1), loc='upper left')

    current_step = [0]

    def draw_next_step():
        if current_step[0] >= len(timeline):
            return

        time, pid, explanation = timeline[current_step[0]]
        color = "#bbbbbb" if pid is None else color_map[pid % len(color_map)]
        rect = plt.Rectangle((time, 0), 1, 1, facecolor=color, edgecolor='black', linewidth=1.5)
        ax.add_patch(rect)
        label = "Idle" if pid is None and "I/O" not in explanation else ("I/O" if "I/O" in explanation else f"P{pid}")
        ax.text(time + 0.5, 0.5, label, ha='center', va='center', fontsize=12, fontweight='bold', color='white')
        ax.text(time, -0.2, str(time), ha='center', fontsize=9)
        explanation_box.set_text(explanation)
        canvas.draw()
        current_step[0] += 1

    tk.Button(step_window, text="Next", command=draw_next_step, font=('Arial', 12), padx=10, pady=4).pack(pady=10)


def visualize_timeline(timeline, processes, dynamic=True, manual=False):
    if manual:
        manual_gantt_stepper(timeline, processes)
        return

    fig, ax = plt.subplots(figsize=(16, 3.5))
    ax.set_xlim(0, len(timeline))
    ax.set_ylim(-0.5, 1.5)
    ax.axis('off')

    explanation_box = ax.text(0, 1.2, "", fontsize=12, ha='left', wrap=True)
    color_map = ['#5DADE2', '#58D68D', '#F4D03F', '#E59866', '#AF7AC5', '#85C1E9', '#F1948A']
    legend_patches = [Patch(color=color_map[p.pid % len(color_map)], label=f'P{p.pid}') for p in processes]
    ax.legend(handles=legend_patches, title='Processes', bbox_to_anchor=(1.01, 1), loc='upper left')

    def draw_bar(i):
        if i >= len(timeline): return
        time, pid, explanation = timeline[i]
        color = "#bbbbbb" if pid is None else color_map[pid % len(color_map)]
        rect = patches.Rectangle((time, 0), 1, 1, facecolor=color, edgecolor='black', linewidth=1.5)
        ax.add_patch(rect)
        label = "Idle" if pid is None and "I/O" not in explanation else ("I/O" if "I/O" in explanation else f"P{pid}")
        ax.text(time + 0.5, 0.5, label, ha='center', va='center', fontsize=12, fontweight='bold', color='white')
        ax.text(time, -0.2, str(time), ha='center', fontsize=9)
        explanation_box.set_text(explanation)

    if dynamic:
        ani = animation.FuncAnimation(fig, draw_bar, frames=len(timeline), interval=600, repeat=False)
        plt.title("FCFS Scheduling - Gantt Chart (Dynamic)", fontsize=15, fontweight='bold')
        plt.tight_layout()
        plt.show()
    else:
        for i in range(len(timeline)):
            draw_bar(i)
        plt.title("FCFS Scheduling - Gantt Chart (Static)", fontsize=15, fontweight='bold')
        plt.tight_layout()
        plt.show()


# --------------------------- GUI CLASS ---------------------------
class FCFSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FCFS Scheduling - Interactive GUI")
        self.root.geometry("740x620")
        self.root.resizable(False, False)

        self.main_frame = tk.Frame(root, padx=20, pady=20)
        self.main_frame.pack()

        self.build_initial_inputs()

    def build_initial_inputs(self):
        tk.Label(self.main_frame, text="Enter Number of Processes:").grid(row=0, column=0, sticky='w')
        self.num_processes_entry = tk.Entry(self.main_frame)
        self.num_processes_entry.grid(row=0, column=1, pady=10)

        tk.Button(self.main_frame, text="Submit", command=self.setup_fields).grid(row=0, column=2, padx=10)

    def setup_fields(self):
        try:
            self.num = int(self.num_processes_entry.get())
            if self.num <= 0:
                raise ValueError("Enter a number greater than 0.")

            for widget in self.main_frame.winfo_children()[1:]:
                widget.destroy()

            tk.Label(self.main_frame, text=f"Enter {self.num} Arrival Times:").grid(row=1, column=0, sticky='w')
            self.arrival_entry = tk.Entry(self.main_frame, width=50)
            self.arrival_entry.grid(row=1, column=1, columnspan=2, pady=5)

            tk.Label(self.main_frame, text=f"Enter {self.num} Burst Times:").grid(row=2, column=0, sticky='w')
            self.burst_entry = tk.Entry(self.main_frame, width=50)
            self.burst_entry.grid(row=2, column=1, columnspan=2, pady=5)

            tk.Label(self.main_frame, text="Include I/O Burst?").grid(row=3, column=0, sticky='w')
            self.include_io = tk.StringVar(value="No")
            tk.OptionMenu(self.main_frame, self.include_io, "Yes", "No", command=self.toggle_io_entry).grid(row=3, column=1, pady=5)

            self.io_label = tk.Label(self.main_frame, text=f"Enter {self.num} I/O Burst Times:")
            self.io_entry = tk.Entry(self.main_frame, width=50)

            tk.Label(self.main_frame, text="Visualization Type:").grid(row=5, column=0, sticky='w')
            self.visualization_type = tk.StringVar(value="Dynamic")
            tk.OptionMenu(self.main_frame, self.visualization_type, "Dynamic", "Static", "Manual").grid(row=5, column=1, pady=10)

            tk.Button(self.main_frame, text="Run FCFS", command=self.run_fcfs).grid(row=6, column=1, pady=10)

            self.output_label = tk.Label(self.main_frame, text="", justify='left', font=("Courier", 10))
            self.output_label.grid(row=7, column=0, columnspan=3)

            self.toggle_io_entry(self.include_io.get())

        except ValueError as e:
            messagebox.showerror("Input Error", str(e))

    def toggle_io_entry(self, choice):
        if choice == "Yes":
            self.io_label.grid(row=4, column=0, sticky='w')
            self.io_entry.grid(row=4, column=1, columnspan=2, pady=5)
        else:
            self.io_label.grid_forget()
            self.io_entry.grid_forget()

    def run_fcfs(self):
        try:
            arrival_times = list(map(int, self.arrival_entry.get().strip().split()))
            burst_times = list(map(int, self.burst_entry.get().strip().split()))

            if len(arrival_times) != self.num or len(burst_times) != self.num:
                raise ValueError("Mismatch in arrival or burst time entries.")

            if self.include_io.get() == "Yes":
                io_times = list(map(int, self.io_entry.get().strip().split()))
                if len(io_times) != self.num:
                    raise ValueError("Mismatch in I/O burst time entries.")
            else:
                io_times = [0] * self.num

            for time in arrival_times + burst_times + io_times:
                if time < 0:
                    raise ValueError("Negative values are not allowed.")

            processes = [
                Process(pid=i + 1, arrival=arrival_times[i], burst=burst_times[i], io_burst=io_times[i])
                for i in range(self.num)
            ]

            final_processes, timeline = fcfs_dynamic(processes)

            result = "PID | Arrival | Burst | I/O | Start | Completion | Turnaround | Waiting\n"
            result += "-" * 75 + "\n"
            total_tat = total_wt = 0
            for p in final_processes:
                total_tat += p.turnaround
                total_wt += p.waiting
                result += f"{p.pid:3} | {p.arrival:7} | {p.burst:5} | {p.io_burst:3} | {p.start:5} | {p.completion:10} | {p.turnaround:10} | {p.waiting:7}\n"

            result += f"\nAverage Turnaround Time: {total_tat / self.num:.2f}"
            result += f"\nAverage Waiting Time   : {total_wt / self.num:.2f}"

            self.output_label.config(text=result)

            vis_type = self.visualization_type.get()
            if vis_type == "Manual":
                visualize_timeline(timeline, final_processes, dynamic=False, manual=True)
            else:
                visualize_timeline(timeline, final_processes, dynamic=(vis_type == "Dynamic"))

        except Exception as e:
            messagebox.showerror("Execution Error", str(e))


# -------------------------- MAIN ----------------------------
def main():
    root = tk.Tk()
    app = FCFSApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
