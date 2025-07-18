import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.patches import Patch, Rectangle
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Process:
    def __init__(self, pid, arrival, burst, priority, io_burst=0):
        self.pid = pid
        self.arrival = arrival
        self.burst = burst
        self.priority = priority
        self.io_burst = io_burst
        self.completion = 0
        self.turnaround = 0
        self.waiting = 0
        self.timeline = []

def priority_non_preemptive(processes):
    time = 0
    completed = 0
    n = len(processes)
    ready_queue = []
    timeline = []

    processes.sort(key=lambda p: p.arrival)

    while completed < n:
        for p in processes:
            if p.arrival <= time and p.completion == 0 and p not in ready_queue:
                ready_queue.append(p)

        ready_queue = [p for p in ready_queue if p.completion == 0]

        if ready_queue:
            ready_queue.sort(key=lambda p: (p.priority, p.arrival))
            current = ready_queue.pop(0)

            # CPU Execution
            start = time
            end = time + current.burst
            timeline.append((current.pid, start, end, "CPU"))
            current.timeline.append((start, end, "CPU"))
            time = end

            # I/O Execution if exists
            if current.io_burst > 0:
                io_start = time
                io_end = time + current.io_burst
                timeline.append((current.pid, io_start, io_end, "IO"))
                current.timeline.append((io_start, io_end, "IO"))
                time = io_end

            current.completion = time
            current.turnaround = current.completion - current.arrival
            current.waiting = current.turnaround - (current.burst + current.io_burst)
            completed += 1
        else:
            upcoming = [p.arrival for p in processes if p.completion == 0]
            if upcoming:
                time = min(upcoming)

    return processes, timeline

class GanttChartVisualizer:
    def __init__(self, root, processes, timeline):
        self.root = root
        self.processes = processes
        self.timeline = timeline
        self.current_step = 0
        self.color_map = ['#5DADE2', '#58D68D', '#F4D03F', '#E59866', '#AF7AC5', '#85C1E9', '#F1948A']
        
        self.top = tk.Toplevel(root)
        self.top.title("Gantt Chart Visualization")
        self.top.geometry("800x500")
        
        # Create frame for canvas
        self.canvas_frame = tk.Frame(self.top)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create frame for controls
        self.control_frame = tk.Frame(self.top)
        self.control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Initialize figure
        self.fig, self.ax = plt.subplots(figsize=(10, 3))
        self.ax.set_xlim(0, max(e for _, _, e, _ in timeline) + 1)
        self.ax.set_ylim(-1, 2)
        self.ax.set_title("Priority Non-Preemptive Scheduling - Gantt Chart")
        self.ax.set_xlabel("Time")
        self.ax.set_yticks([])
        
        # Create legend
        legend_patches = [Patch(color=self.color_map[p.pid % len(self.color_map)], label=f'P{p.pid}') for p in processes]
        self.ax.legend(handles=legend_patches, title='Processes', bbox_to_anchor=(1.01, 1), loc='upper left')
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
        
        # Add explanation text
        self.explanation = tk.StringVar()
        self.explanation.set("Click 'Next' to start visualization")
        self.explanation_label = tk.Label(self.control_frame, textvariable=self.explanation, font=("Arial", 10), wraplength=700, justify='left')
        self.explanation_label.pack(side=tk.LEFT)
        
        # Add next button
        self.next_btn = tk.Button(self.control_frame, text="Next", command=self.next_step)
        self.next_btn.pack(side=tk.RIGHT)
        
        # Draw initial state
        self.draw_step()
    
    def draw_step(self):
        self.ax.clear()
        self.ax.set_xlim(0, max(e for _, _, e, _ in self.timeline) + 1)
        self.ax.set_ylim(-1, 2)
        self.ax.set_title("Priority Non-Preemptive Scheduling - Gantt Chart")
        self.ax.set_xlabel("Time")
        self.ax.set_yticks([])
        
        # Draw completed steps
        for i in range(self.current_step):
            pid, start, end, ptype = self.timeline[i]
            color = self.color_map[pid % len(self.color_map)]
            height = 0.5 if ptype == "CPU" else 0.3
            y_pos = 0 if ptype == "CPU" else -0.5
            
            rect = Rectangle((start, y_pos), end-start, height, facecolor=color, edgecolor='black')
            self.ax.add_patch(rect)
            
            label = f"P{pid}" if ptype == "CPU" else f"P{pid}(IO)"
            self.ax.text((start + end)/2, y_pos + height/2, label, va='center', ha='center', fontsize=9)
            
            # Draw time markers
            if i == 0 or (i > 0 and self.timeline[i-1][1] != start):
                self.ax.text(start, y_pos - 0.2, f"{start}", ha='center', fontsize=8)
        
        # Draw final time marker if at end
        if self.current_step >= len(self.timeline):
            last_end = self.timeline[-1][2]
            self.ax.text(last_end, -0.2, f"{last_end}", ha='center', fontsize=8)
        
        self.canvas.draw()
    
    def next_step(self):
        if self.current_step < len(self.timeline):
            pid, start, end, ptype = self.timeline[self.current_step]
            self.explanation.set(f"Time {start}-{end}: Process P{pid} {'executing' if ptype == 'CPU' else 'in I/O'}")
            self.current_step += 1
            self.draw_step()
            
            if self.current_step == len(self.timeline):
                self.next_btn.config(state=tk.DISABLED)
                self.explanation.set(f"Visualization complete. Final time: {end}")

def show_gantt_chart(processes, timeline, mode="static", root=None):
    if mode == "static":
        fig, ax = plt.subplots(figsize=(12, 3.5))
        color_map = ['#5DADE2', '#58D68D', '#F4D03F', '#E59866', '#AF7AC5', '#85C1E9', '#F1948A']

        ax.set_xlim(0, max(e for _, _, e, _ in timeline) + 1)
        ax.set_ylim(-1, 2)
        ax.set_title("Priority Non-Preemptive Scheduling - Gantt Chart")
        ax.set_xlabel("Time")
        ax.set_yticks([])

        legend_patches = [Patch(color=color_map[p.pid % len(color_map)], label=f'P{p.pid}') for p in processes]
        ax.legend(handles=legend_patches, title='Processes', bbox_to_anchor=(1.01, 1), loc='upper left')

        for pid, start, end, ptype in timeline:
            color = color_map[pid % len(color_map)]
            height = 0.5 if ptype == "CPU" else 0.3
            y_pos = 0 if ptype == "CPU" else -0.5
            
            ax.barh(y_pos, end-start, left=start, height=height, color=color, edgecolor='black')
            label = f"P{pid}" if ptype == "CPU" else f"P{pid}(IO)"
            ax.text((start + end)/2, y_pos + height/2, label, va='center', ha='center', fontsize=9)
            
            # Mark time points
            if timeline.index((pid, start, end, ptype)) == 0 or (timeline.index((pid, start, end, ptype)) > 0 and timeline[timeline.index((pid, start, end, ptype))-1][1] != start):
                ax.text(start, y_pos - 0.2, f"{start}", ha='center', fontsize=8)
        
        ax.text(timeline[-1][2], -0.2, f"{timeline[-1][2]}", fontsize=8, ha='center')

        plt.tight_layout()
        plt.show()
    elif mode == "dynamic":
        fig, ax = plt.subplots(figsize=(12, 3.5))
        color_map = ['#5DADE2', '#58D68D', '#F4D03F', '#E59866', '#AF7AC5', '#85C1E9', '#F1948A']

        ax.set_xlim(0, max(e for _, _, e, _ in timeline) + 1)
        ax.set_ylim(-1, 2)
        ax.set_title("Priority Non-Preemptive Scheduling - Gantt Chart")
        ax.set_xlabel("Time")
        ax.set_yticks([])

        legend_patches = [Patch(color=color_map[p.pid % len(color_map)], label=f'P{p.pid}') for p in processes]
        ax.legend(handles=legend_patches, title='Processes', bbox_to_anchor=(1.01, 1), loc='upper left')

        def animate(i):
            ax.clear()
            ax.set_xlim(0, max(e for _, _, e, _ in timeline) + 1)
            ax.set_ylim(-1, 2)
            ax.set_title("Priority Non-Preemptive Scheduling - Gantt Chart")
            ax.set_xlabel("Time")
            ax.set_yticks([])
            
            for j in range(i+1):
                pid, start, end, ptype = timeline[j]
                color = color_map[pid % len(color_map)]
                height = 0.5 if ptype == "CPU" else 0.3
                y_pos = 0 if ptype == "CPU" else -0.5
                
                ax.barh(y_pos, end-start, left=start, height=height, color=color, edgecolor='black')
                label = f"P{pid}" if ptype == "CPU" else f"P{pid}(IO)"
                ax.text((start + end)/2, y_pos + height/2, label, va='center', ha='center', fontsize=9)
                
                if j == 0 or (j > 0 and timeline[j-1][1] != start):
                    ax.text(start, y_pos - 0.2, f"{start}", ha='center', fontsize=8)
            
            if i == len(timeline)-1:
                ax.text(timeline[-1][2], -0.2, f"{timeline[-1][2]}", fontsize=8, ha='center')

        ani = animation.FuncAnimation(fig, animate, frames=len(timeline), interval=500, repeat=False)
        plt.tight_layout()
        plt.show()
    elif mode == "manual":
        GanttChartVisualizer(root, processes, timeline)

class PrioritySchedulerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Priority Non-Preemptive Scheduling")
        self.root.geometry("600x550")

        self.frame_num = tk.Frame(root, pady=20)
        self.frame_num.pack()

        tk.Label(self.frame_num, text="Enter number of processes:", font=("Arial", 12)).pack(side=tk.LEFT)
        self.num_entry = tk.Entry(self.frame_num, width=5, font=("Arial", 12))
        self.num_entry.pack(side=tk.LEFT, padx=10)

        self.btn_next = tk.Button(self.frame_num, text="Next", font=("Arial", 12), command=self.get_num_processes)
        self.btn_next.pack(side=tk.LEFT)

        self.input_frame = None
        self.result_frame = None
        self.io_entry = None
        self.io_label = None
        self.include_io = tk.StringVar(value="No")
        self.visualization_type = tk.StringVar(value="static")

    def get_num_processes(self):
        try:
            self.num_processes = int(self.num_entry.get())
            if self.num_processes <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid positive integer for number of processes.")
            return

        self.frame_num.pack_forget()
        self.show_inputs()

    def show_inputs(self):
        self.input_frame = tk.Frame(self.root, padx=20, pady=20)
        self.input_frame.pack()

        tk.Label(self.input_frame, text=f"Enter arrival times (space separated):", font=("Arial", 12)).grid(row=0, column=0, sticky='w')
        self.arrival_entry = tk.Entry(self.input_frame, width=50, font=("Arial", 12))
        self.arrival_entry.grid(row=1, column=0, pady=5)

        tk.Label(self.input_frame, text=f"Enter burst times (space separated):", font=("Arial", 12)).grid(row=2, column=0, sticky='w')
        self.burst_entry = tk.Entry(self.input_frame, width=50, font=("Arial", 12))
        self.burst_entry.grid(row=3, column=0, pady=5)

        tk.Label(self.input_frame, text=f"Enter priorities (space separated, lower number = higher priority):", 
                font=("Arial", 12), wraplength=500, justify='left').grid(row=4, column=0, sticky='w')
        self.priority_entry = tk.Entry(self.input_frame, width=50, font=("Arial", 12))
        self.priority_entry.grid(row=5, column=0, pady=5)

        # I/O Burst option
        tk.Label(self.input_frame, text="Include I/O Burst?", font=("Arial", 12)).grid(row=6, column=0, sticky='w')
        tk.OptionMenu(self.input_frame, self.include_io, "No", "Yes", command=self.toggle_io_entry).grid(row=6, column=1, sticky='w')

        self.io_label = tk.Label(self.input_frame, text="Enter I/O burst times (space separated):", font=("Arial", 12))
        self.io_entry = tk.Entry(self.input_frame, width=50, font=("Arial", 12))

        # Visualization type option
        tk.Label(self.input_frame, text="Visualization Type:", font=("Arial", 12)).grid(row=8, column=0, sticky='w')
        tk.OptionMenu(self.input_frame, self.visualization_type, "static", "dynamic", "manual").grid(row=8, column=1, sticky='w')

        self.btn_submit = tk.Button(self.input_frame, text="Schedule", font=("Arial", 12), command=self.schedule_processes)
        self.btn_submit.grid(row=9, column=0, columnspan=2, pady=10)

    def toggle_io_entry(self, value):
        if value == "Yes":
            self.io_label.grid(row=7, column=0, sticky='w')
            self.io_entry.grid(row=7, column=1, pady=5)
        else:
            self.io_label.grid_forget()
            self.io_entry.grid_forget()

    def schedule_processes(self):
        try:
            arrival_times = list(map(int, self.arrival_entry.get().strip().split()))
            burst_times = list(map(int, self.burst_entry.get().strip().split()))
            priorities = list(map(int, self.priority_entry.get().strip().split()))
            
            if len(arrival_times) != self.num_processes or len(burst_times) != self.num_processes or len(priorities) != self.num_processes:
                raise ValueError("Mismatched input lengths")
                
            io_times = [0] * self.num_processes
            if self.include_io.get() == "Yes":
                io_times = list(map(int, self.io_entry.get().strip().split()))
                if len(io_times) != self.num_processes:
                    raise ValueError("Mismatched I/O burst times length")
                    
        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Please enter valid inputs: {str(e)}")
            return

        self.processes = [Process(i + 1, arrival_times[i], burst_times[i], priorities[i], io_times[i]) for i in range(self.num_processes)]
        scheduled, timeline = priority_non_preemptive(self.processes)

        if self.result_frame:
            self.result_frame.destroy()
        self.result_frame = tk.Frame(self.root, padx=20, pady=20)
        self.result_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("PID", "Arrival", "Burst", "Priority", "I/O", "Completion", "Turnaround", "Waiting")
        tree = ttk.Treeview(self.result_frame, columns=columns, show="headings", height=self.num_processes)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor='center', width=80 if col != "Priority" else 60)
        tree.pack(fill=tk.X)

        total_tat, total_wt = 0, 0
        for p in scheduled:
            total_tat += p.turnaround
            total_wt += p.waiting
            tree.insert("", "end", values=(p.pid, p.arrival, p.burst, p.priority, p.io_burst, p.completion, p.turnaround, p.waiting))

        avg_tat = total_tat / self.num_processes
        avg_wt = total_wt / self.num_processes

        avg_label = tk.Label(self.result_frame, 
                           text=f"Average Turnaround Time: {avg_tat:.2f} | Average Waiting Time: {avg_wt:.2f}", 
                           font=("Arial", 12, "bold"), pady=10)
        avg_label.pack()

        # Show Gantt chart based on selected visualization type
        show_gantt_chart(scheduled, timeline, mode=self.visualization_type.get(), root=self.root)
class GanttChartVisualizer:
    def __init__(self, root, processes, timeline):
        self.root = root
        self.processes = processes
        self.timeline = timeline
        self.current_step = 0
        self.color_map = ['#5DADE2', '#58D68D', '#F4D03F', '#E59866', '#AF7AC5', '#85C1E9', '#F1948A']
        
        self.top = tk.Toplevel(root)
        self.top.title("Gantt Chart Visualization")
        self.top.geometry("900x500")
        
        # Create frame for canvas
        self.canvas_frame = tk.Frame(self.top)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create frame for controls
        self.control_frame = tk.Frame(self.top)
        self.control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Initialize figure
        self.fig, self.ax = plt.subplots(figsize=(12, 3))
        self.ax.set_xlim(0, max(e for _, _, e, _ in timeline) + 1)
        self.ax.set_ylim(-0.5, 1.5)
        self.ax.set_title("Priority Non-Preemptive Scheduling - Gantt Chart")
        self.ax.set_xlabel("Time")
        self.ax.set_yticks([])
        
        # Create legend
        legend_patches = [Patch(color=self.color_map[p.pid % len(self.color_map)], label=f'P{p.pid}') for p in processes]
        legend_patches.append(Patch(color="#bbbbbb", label='Idle'))
        self.ax.legend(handles=legend_patches, title='Processes', bbox_to_anchor=(1.01, 1), loc='upper left')
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
        
        # Add explanation text
        self.explanation = tk.StringVar()
        self.explanation.set("Click 'Next' to start visualization")
        self.explanation_label = tk.Label(self.control_frame, textvariable=self.explanation, 
                                        font=("Arial", 10), wraplength=800, justify='left')
        self.explanation_label.pack(side=tk.LEFT)
        
        # Add next button
        self.next_btn = tk.Button(self.control_frame, text="Next", command=self.next_step)
        self.next_btn.pack(side=tk.RIGHT)
        
        # Draw initial state
        self.draw_step()
    
    def draw_step(self):
        self.ax.clear()
        self.ax.set_xlim(0, max(e for _, _, e, _ in self.timeline) + 1)
        self.ax.set_ylim(-0.5, 1.5)
        self.ax.set_title("Priority Non-Preemptive Scheduling - Gantt Chart")
        self.ax.set_xlabel("Time")
        self.ax.set_yticks([])
        
        # Redraw legend
        legend_patches = [Patch(color=self.color_map[p.pid % len(self.color_map)], label=f'P{p.pid}') for p in self.processes]
        legend_patches.append(Patch(color="#bbbbbb", label='Idle'))
        self.ax.legend(handles=legend_patches, title='Processes', bbox_to_anchor=(1.01, 1), loc='upper left')
        
        # Draw completed steps
        for i in range(self.current_step):
            pid, start, end, ptype = self.timeline[i]
            color = self.color_map[pid % len(self.color_map)] if ptype == "CPU" else "#bbbbbb"
            
            # Draw the process block
            rect = Rectangle((start, 0), end-start, 1, facecolor=color, edgecolor='black')
            self.ax.add_patch(rect)
            
            # Add process label
            label = f"P{pid}" if ptype == "CPU" else "Idle"
            self.ax.text((start + end)/2, 0.5, label, va='center', ha='center', 
                        fontsize=10, fontweight='bold', color='white')
            
            # Draw time markers
            if i == 0 or (i > 0 and self.timeline[i-1][1] != start):
                self.ax.text(start, -0.2, f"{start}", ha='center', fontsize=8)
        
        # Draw final time marker if at end
        if self.current_step >= len(self.timeline):
            last_end = self.timeline[-1][2]
            self.ax.text(last_end, -0.2, f"{last_end}", ha='center', fontsize=8)
        
        self.canvas.draw()
    
    def next_step(self):
        if self.current_step < len(self.timeline):
            pid, start, end, ptype = self.timeline[self.current_step]
            self.explanation.set(f"At time {start}: P{pid} executes for {end-start} units (Remaining: {end-start})" if ptype == "CPU" 
                               else f"At time {start}: P{pid} in I/O for {end-start} units")
            self.current_step += 1
            self.draw_step()
            
            if self.current_step == len(self.timeline):
                self.next_btn.config(state=tk.DISABLED)
                self.explanation.set(f"Visualization complete. Final time: {end}")

def show_gantt_chart(processes, timeline, mode="static", root=None):
    if mode == "static":
        fig, ax = plt.subplots(figsize=(12, 3))
        color_map = ['#5DADE2', '#58D68D', '#F4D03F', '#E59866', '#AF7AC5', '#85C1E9', '#F1948A']

        ax.set_xlim(0, max(e for _, _, e, _ in timeline) + 1)
        ax.set_ylim(-0.5, 1.5)
        ax.set_title("Priority Non-Preemptive Scheduling - Gantt Chart")
        ax.set_xlabel("Time")
        ax.set_yticks([])

        legend_patches = [Patch(color=color_map[p.pid % len(color_map)], label=f'P{p.pid}') for p in processes]
        legend_patches.append(Patch(color="#bbbbbb", label='Idle'))
        ax.legend(handles=legend_patches, title='Processes', bbox_to_anchor=(1.01, 1), loc='upper left')

        for pid, start, end, ptype in timeline:
            color = color_map[pid % len(color_map)] if ptype == "CPU" else "#bbbbbb"
            
            # Draw the process block
            rect = Rectangle((start, 0), end-start, 1, facecolor=color, edgecolor='black')
            ax.add_patch(rect)
            
            # Add process label
            label = f"P{pid}" if ptype == "CPU" else "Idle"
            ax.text((start + end)/2, 0.5, label, va='center', ha='center', 
                   fontsize=10, fontweight='bold', color='white')
            
            # Draw time markers
            if timeline.index((pid, start, end, ptype)) == 0 or (timeline.index((pid, start, end, ptype)) > 0 and timeline[timeline.index((pid, start, end, ptype))-1][1] != start):
                ax.text(start, -0.2, f"{start}", ha='center', fontsize=8)
        
        ax.text(timeline[-1][2], -0.2, f"{timeline[-1][2]}", fontsize=8, ha='center')

        plt.tight_layout()
        plt.show()
    elif mode == "dynamic":
        fig, ax = plt.subplots(figsize=(12, 3))
        color_map = ['#5DADE2', '#58D68D', '#F4D03F', '#E59866', '#AF7AC5', '#85C1E9', '#F1948A']

        ax.set_xlim(0, max(e for _, _, e, _ in timeline) + 1)
        ax.set_ylim(-0.5, 1.5)
        ax.set_title("Priority Non-Preemptive Scheduling - Gantt Chart")
        ax.set_xlabel("Time")
        ax.set_yticks([])

        legend_patches = [Patch(color=color_map[p.pid % len(color_map)], label=f'P{p.pid}') for p in processes]
        legend_patches.append(Patch(color="#bbbbbb", label='Idle'))
        ax.legend(handles=legend_patches, title='Processes', bbox_to_anchor=(1.01, 1), loc='upper left')

        def animate(i):
            ax.clear()
            ax.set_xlim(0, max(e for _, _, e, _ in timeline) + 1)
            ax.set_ylim(-0.5, 1.5)
            ax.set_title("Priority Non-Preemptive Scheduling - Gantt Chart")
            ax.set_xlabel("Time")
            ax.set_yticks([])
            
            # Redraw legend
            ax.legend(handles=legend_patches, title='Processes', bbox_to_anchor=(1.01, 1), loc='upper left')
            
            for j in range(i+1):
                pid, start, end, ptype = timeline[j]
                color = color_map[pid % len(color_map)] if ptype == "CPU" else "#bbbbbb"
                
                # Draw the process block
                rect = Rectangle((start, 0), end-start, 1, facecolor=color, edgecolor='black')
                ax.add_patch(rect)
                
                # Add process label
                label = f"P{pid}" if ptype == "CPU" else "Idle"
                ax.text((start + end)/2, 0.5, label, va='center', ha='center', 
                       fontsize=10, fontweight='bold', color='white')
                
                # Draw time markers
                if j == 0 or (j > 0 and timeline[j-1][1] != start):
                    ax.text(start, -0.2, f"{start}", ha='center', fontsize=8)
            
            if i == len(timeline)-1:
                ax.text(timeline[-1][2], -0.2, f"{timeline[-1][2]}", fontsize=8, ha='center')

        ani = animation.FuncAnimation(fig, animate, frames=len(timeline), interval=500, repeat=False)
        plt.tight_layout()
        plt.show()
    elif mode == "manual":
        GanttChartVisualizer(root, processes, timeline)
        
def main():
    root = tk.Tk()
    app = PrioritySchedulerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()