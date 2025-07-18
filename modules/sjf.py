import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
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

def sjf_non_preemptive(processes):
    processes.sort(key=lambda p: p.arrival)
    time = 0
    completed = 0
    n = len(processes)
    ready_queue = []
    timeline = []
    visited = set()

    while completed < n:
        for p in processes:
            if p.arrival <= time and p not in visited and p not in ready_queue:
                ready_queue.append(p)

        if ready_queue:
            ready_queue.sort(key=lambda p: p.burst)
            current = ready_queue.pop(0)
            visited.add(current)

            if time < current.arrival:
                for idle in range(time, current.arrival):
                    timeline.append((idle, idle + 1, None))
                time = current.arrival

            current.start = time
            for _ in range(current.burst):
                timeline.append((time, time + 1, f"P{current.pid}"))
                time += 1

            if current.io_burst > 0:
                for _ in range(current.io_burst):
                    timeline.append((time, time + 1, f"IO-P{current.pid}"))
                    time += 1

            current.completion = time
            current.turnaround = current.completion - current.arrival
            current.waiting = current.turnaround - (current.burst + current.io_burst)

            completed += 1
        else:
            timeline.append((time, time + 1, None))
            time += 1

    return processes, timeline


def visualize_timeline(timeline, processes, canvas_frame, dynamic=False, manual=False, app_ref=None):
    process_colors = {f"P{p.pid}": f"C{(p.pid - 1) % 10}" for p in processes}
    fig, ax = plt.subplots(figsize=(10, 2))
    canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack()

    max_time = max(end for _, end, _ in timeline)
    ax.set_xlim(0, max_time)
    ax.set_ylim(0, 1)
    ax.set_yticks([])
    ax.set_xticks(range(0, max_time + 1))
    ax.set_xlabel("Time")
    ax.set_title("Gantt Chart")

    index = {'i': 0}

    def draw_bar(i):
        start, end, label = timeline[i]

        if label is None:
            color = "lightgray"
            display = "IDLE"
        elif label.startswith("IO-"):
            color = "orange"
            display = "I/O"
        else:
            color = process_colors.get(label, "skyblue")
            display = label

        ax.barh(0, end - start, left=start, color=color, edgecolor="black")
        ax.text((start + end) / 2, 0, display, ha='center', va='center', fontsize=8)
        canvas.draw()

        app_ref.explanation_box.config(state="normal")
        app_ref.explanation_box.insert(tk.END, f"Time {start}-{end}: {display} executed.\n")
        app_ref.explanation_box.config(state="disabled")

    def animate_step():
        if index['i'] < len(timeline):
            draw_bar(index['i'])
            index['i'] += 1
            canvas_frame.after(500, animate_step)
        else:
            app_ref.explanation_box.config(state="normal")
            app_ref.explanation_box.insert(tk.END, "Execution complete.\n")
            app_ref.explanation_box.config(state="disabled")

    def manual_next():
        if index['i'] < len(timeline):
            draw_bar(index['i'])
            index['i'] += 1
            if index['i'] >= len(timeline):
                next_btn.config(state=tk.DISABLED)
                app_ref.explanation_box.config(state="normal")
                app_ref.explanation_box.insert(tk.END, "Execution complete.\n")
                app_ref.explanation_box.config(state="disabled")
        canvas.draw()

    if dynamic:
        animate_step()
    elif manual:
        app_ref.explanation_box.config(state="normal")
        app_ref.explanation_box.insert(tk.END, "Click 'Next' to start visualization.\n")
        app_ref.explanation_box.config(state="disabled")

        global next_btn
        next_btn = tk.Button(canvas_frame, text="Next ▶", font=("Helvetica", 10, "bold"),
                             bg="#3498db", fg="white", padx=10, pady=5, command=manual_next)
        next_btn.pack(pady=10)
    else:
        for i in range(len(timeline)):
            draw_bar(i)
        app_ref.explanation_box.config(state="normal")
        app_ref.explanation_box.insert(tk.END, "Static visualization complete.\n")
        app_ref.explanation_box.config(state="disabled")


class SJFApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SJF Non-Preemptive Scheduling - Interactive GUI")
        self.root.geometry("950x720")

        self.main_frame = tk.Frame(root, padx=20, pady=20)
        self.main_frame.pack()

        self.canvas_frame = tk.Frame(root)
        self.canvas_frame.pack(pady=10)

        self.explanation_box = tk.Text(root, height=10, state="disabled", bg="#f4f4f4")
        self.explanation_box.pack(fill=tk.BOTH, padx=20, pady=10)

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
                raise ValueError("Enter a number > 0")

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

            tk.Button(self.main_frame, text="Run SJF", command=self.run_sjf).grid(row=6, column=1, pady=10)

            self.output_label = tk.Label(self.main_frame, text="", justify='left', font=("Courier", 10))
            self.output_label.grid(row=7, column=0, columnspan=3)

            self.toggle_io_entry(self.include_io.get())

        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def toggle_io_entry(self, choice):
        if choice == "Yes":
            self.io_label.grid(row=4, column=0, sticky='w')
            self.io_entry.grid(row=4, column=1, columnspan=2, pady=5)
        else:
            self.io_label.grid_forget()
            self.io_entry.grid_forget()

    def run_sjf(self):
        try:
            self.explanation_box.config(state="normal")
            self.explanation_box.delete("1.0", tk.END)
            self.explanation_box.config(state="disabled")

            for widget in self.canvas_frame.winfo_children():
                widget.destroy()

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

            processes = [
                Process(pid=i + 1, arrival=arrival_times[i], burst=burst_times[i], io_burst=io_times[i])
                for i in range(self.num)
            ]

            final_processes, timeline = sjf_non_preemptive(processes)
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
            is_dynamic = vis_type == "Dynamic"
            is_manual = vis_type == "Manual"
            visualize_timeline(timeline, final_processes, self.canvas_frame, dynamic=is_dynamic, manual=is_manual, app_ref=self)

        except Exception as e:
            messagebox.showerror("Invalid Input", str(e))

def main():
    root = tk.Tk()
    app = SJFApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
