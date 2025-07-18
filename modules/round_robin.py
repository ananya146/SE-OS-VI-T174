import tkinter as tk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Patch
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class Process:
    def __init__(self, pid, arrival, burst, io_burst=0):
        self.pid = pid
        self.arrival = arrival
        self.burst = burst
        self.io_burst = io_burst
        self.remaining = burst
        self.completion = 0
        self.waiting = 0
        self.turnaround = 0
        self.timeline = []


def round_robin_with_io(processes, quantum):
    time = 0
    queue = []
    completed = 0
    n = len(processes)
    arrival_index = 0
    processes.sort(key=lambda x: x.arrival)

    timeline = []
    log = []

    while completed < n:
        while arrival_index < n and processes[arrival_index].arrival <= time:
            log.append(f"Time {time}: Process P{processes[arrival_index].pid} arrived and added to queue.")
            queue.append(processes[arrival_index])
            arrival_index += 1

        if not queue:
            timeline.append((time, None, "CPU Idle (No process available)"))
            time += 1
            continue

        curr = queue.pop(0)
        exec_time = min(curr.remaining, quantum)
        start = time
        end = time + exec_time
        curr.timeline.append((start, end))
        curr.remaining -= exec_time

        for t in range(start, end):
            explanation = f"At time {start}: P{curr.pid} executes for {exec_time} units (Remaining: {curr.remaining})"
            timeline.append((t, curr.pid, explanation))

        time = end

        if curr.remaining == 0 and curr.io_burst > 0:
            for i in range(curr.io_burst):
                explanation = f"At time {time}: I/O in progress for Process P{curr.pid}"
                timeline.append((time, None, explanation))
                time += 1

        while arrival_index < n and processes[arrival_index].arrival <= time:
            log.append(f"Time {time}: Process P{processes[arrival_index].pid} arrived and added to queue.")
            queue.append(processes[arrival_index])
            arrival_index += 1

        if curr.remaining > 0:
            queue.append(curr)
        else:
            curr.completion = time
            curr.turnaround = curr.completion - curr.arrival
            curr.waiting = curr.turnaround - (curr.burst + curr.io_burst)
            completed += 1

    return processes, timeline, log


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


def static_gantt_chart(timeline, processes):
    win = tk.Toplevel()
    win.title("Static Gantt Chart")
    win.geometry("1100x450")

    fig, ax = plt.subplots(figsize=(14, 3.5))
    canvas = FigureCanvasTkAgg(fig, master=win)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    ax.set_xlim(0, len(timeline))
    ax.set_ylim(-0.5, 1.5)
    ax.axis('off')

    color_map = ['#5DADE2', '#58D68D', '#F4D03F', '#E59866', '#AF7AC5', '#85C1E9', '#F1948A']
    legend_patches = [Patch(color=color_map[p.pid % len(color_map)], label=f'P{p.pid}') for p in processes]
    ax.legend(handles=legend_patches, title='Processes', bbox_to_anchor=(1.01, 1), loc='upper left')

    for time, pid, explanation in timeline:
        color = "#bbbbbb" if pid is None else color_map[pid % len(color_map)]
        rect = plt.Rectangle((time, 0), 1, 1, facecolor=color, edgecolor='black', linewidth=1.5)
        ax.add_patch(rect)
        label = "Idle" if pid is None and "I/O" not in explanation else ("I/O" if "I/O" in explanation else f"P{pid}")
        ax.text(time + 0.5, 0.5, label, ha='center', va='center', fontsize=12, fontweight='bold', color='white')
        ax.text(time, -0.2, str(time), ha='center', fontsize=9)

    canvas.draw()


def dynamic_gantt_chart(timeline, processes):
    win = tk.Toplevel()
    win.title("Dynamic Gantt Chart")
    win.geometry("1100x450")

    fig, ax = plt.subplots(figsize=(14, 3.5))
    canvas = FigureCanvasTkAgg(fig, master=win)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    ax.set_xlim(0, len(timeline))
    ax.set_ylim(-0.5, 1.5)
    ax.axis('off')

    color_map = ['#5DADE2', '#58D68D', '#F4D03F', '#E59866', '#AF7AC5', '#85C1E9', '#F1948A']
    legend_patches = [Patch(color=color_map[p.pid % len(color_map)], label=f'P{p.pid}') for p in processes]
    ax.legend(handles=legend_patches, title='Processes', bbox_to_anchor=(1.01, 1), loc='upper left')

    time_text = ax.text(0, 1.2, '', fontsize=12, ha='left')

    def animate(i):
        if i >= len(timeline):
            return
        t, pid, explanation = timeline[i]
        color = "#bbbbbb" if pid is None else color_map[pid % len(color_map)]
        rect = plt.Rectangle((t, 0), 1, 1, facecolor=color, edgecolor='black', linewidth=1.5)
        ax.add_patch(rect)
        label = "Idle" if pid is None and "I/O" not in explanation else ("I/O" if "I/O" in explanation else f"P{pid}")
        ax.text(t + 0.5, 0.5, label, ha='center', va='center', fontsize=12, fontweight='bold', color='white')
        ax.text(t, -0.2, str(t), ha='center', fontsize=9)
        time_text.set_text(explanation)

    ani = animation.FuncAnimation(fig, animate, frames=len(timeline), interval=500, repeat=False)
    canvas.draw()


def visualize_timeline(timeline, processes, mode):
    if mode == "Manual":
        manual_gantt_stepper(timeline, processes)
    elif mode == "Static":
        static_gantt_chart(timeline, processes)
    elif mode == "Dynamic":
        dynamic_gantt_chart(timeline, processes)
    else:
        messagebox.showerror("Error", f"Invalid Gantt chart mode: {mode}")



def main():
    root = tk.Tk()
    root.title("Round Robin Scheduler with I/O")
    root.geometry("750x700")
    tk.Label(root, text="Round Robin Scheduling with I/O Burst", font=('Helvetica', 16, 'bold')).pack(pady=10)

    input_frame = tk.Frame(root)
    input_frame.pack(pady=10)

    entry_num = tk.Entry(input_frame, width=30)
    entry_arrival = tk.Entry(input_frame, width=30)
    entry_burst = tk.Entry(input_frame, width=30)
    entry_io = tk.Entry(input_frame, width=30)
    entry_quantum = tk.Entry(input_frame, width=30)

    label_io = tk.Label(input_frame, text="I/O Bursts (space separated, 0 if none):", font=('Arial', 11))

    io_choice = ttk.Combobox(input_frame, values=["No", "Yes"], state="readonly", width=27)
    io_choice.set("No")

    chart_choice = ttk.Combobox(input_frame, values=["Manual", "Static", "Dynamic"], state="readonly", width=27)
    chart_choice.set("Manual")

    def toggle_io_field(event):
        if io_choice.get() == "Yes":
            label_io.grid(row=3, column=0, sticky='e', padx=5, pady=5)
            entry_io.grid(row=3, column=1, padx=5, pady=5)
        else:
            label_io.grid_forget()
            entry_io.grid_forget()

    io_choice.bind("<<ComboboxSelected>>", toggle_io_field)

    labels = [
        "Number of Processes:",
        "Arrival Times (space separated):",
        "Burst Times (space separated):",
        "Include I/O Burst:",
        "Time Quantum:",
        "Gantt Chart Mode:"
    ]
    entries = [entry_num, entry_arrival, entry_burst, io_choice, entry_quantum, chart_choice]

    for i in range(len(labels)):
        tk.Label(input_frame, text=labels[i], font=('Arial', 11)).grid(row=i if i < 3 else i+1, column=0, sticky='e', padx=5, pady=5)
        entries[i].grid(row=i if i < 3 else i+1, column=1, padx=5, pady=5)

    table_frame = tk.Frame(root)
    table_frame.pack(pady=10)

    label_avg = tk.Label(root, text="", font=('Arial', 12, 'bold'))
    label_avg.pack(pady=5)

    def run_simulation():
        try:
            num_processes = int(entry_num.get())
            arrival_times = list(map(int, entry_arrival.get().split()))
            burst_times = list(map(int, entry_burst.get().split()))
            quantum = int(entry_quantum.get())
            chart_mode = chart_choice.get()

            if io_choice.get() == "Yes":
                io_bursts = list(map(int, entry_io.get().split()))
            else:
                io_bursts = [0] * num_processes

            if not (len(arrival_times) == len(burst_times) == len(io_bursts) == num_processes):
                messagebox.showerror("Input Error", "Mismatch in number of processes and inputs")
                return

            processes = [Process(i + 1, arrival_times[i], burst_times[i], io_bursts[i]) for i in range(num_processes)]
            scheduled, timeline, log = round_robin_with_io(processes, quantum)

            for widget in table_frame.winfo_children():
                widget.destroy()

            headers = ["PID", "Arrival", "Burst", "I/O Burst", "Completion", "Turnaround", "Waiting"]
            for col, header in enumerate(headers):
                tk.Label(table_frame, text=header, font=('Arial', 11, 'bold')).grid(row=0, column=col)

            total_tat = 0
            total_wt = 0
            for i, p in enumerate(scheduled):
                values = [p.pid, p.arrival, p.burst, p.io_burst, p.completion, p.turnaround, p.waiting]
                for j, val in enumerate(values):
                    tk.Label(table_frame, text=val, font=('Arial', 10)).grid(row=i + 1, column=j)
                total_tat += p.turnaround
                total_wt += p.waiting

            avg_tat = total_tat / num_processes
            avg_wt = total_wt / num_processes
            label_avg.config(text=f"Average Turnaround Time: {avg_tat:.2f} | Average Waiting Time: {avg_wt:.2f}")

            visualize_timeline(timeline, scheduled, chart_mode)

        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid integers.")

    tk.Button(root, text="Run Simulation", font=('Arial', 12, 'bold'), bg='lightblue', command=run_simulation).pack(pady=10)
    root.mainloop()


if __name__ == "__main__":
    main()
