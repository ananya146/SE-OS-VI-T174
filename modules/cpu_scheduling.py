import tkinter as tk
from tkinter import ttk, messagebox
import importlib

# Dictionary for linking algorithm display names to filenames
ALGORITHMS = {
    "FCFS (First Come First Serve)": "fcfs_dynamic",
    "SJF (Shortest Job First)": "sjf",
    "SRTF (Shortest Remaining Time First)": "srtf",
    "Round Robin": "round_robin",
    "Priority (Non-Preemptive)": "nonpremtive_prioority",
    "Priority (Preemptive)": "priority_preemptive",
    "Multilevel Queue": "multilevel",
    "Multilevel Feedback Queue": "multilevel_feedback_queue",
}

# Definitions (term: explanation)
# Definitions (term: explanation and how it's calculated)
DEFINITIONS = {
    "Arrival Time": (
        "Arrival Time is the moment when a process enters the Ready Queue.\n"
        "It tells us when the process is ready to be scheduled by the CPU."
    ),
    "Burst Time": (
        "Burst Time is the total time a process needs the CPU for execution.\n"
        "It's like the 'running time' required by that task to finish."
    ),
    "Turnaround Time": (
        "Turnaround Time = Completion Time - Arrival Time\n"
        "It shows the total time taken by a process from arrival to completion.\n"
        "Includes both waiting time and execution time."
    ),
    "Waiting Time": (
        "Waiting Time = Turnaround Time - Burst Time\n"
        "It tells us how long a process was waiting in the Ready Queue.\n"
        "It does not include the time spent on execution."
    ),
    "Preemptive Scheduling": (
        "In Preemptive Scheduling, a running process can be stopped anytime\n"
        "if another process with higher priority or shorter burst time arrives.\n"
        "Example: SRTF, Preemptive Priority Scheduling."
    ),
    "Non-Preemptive Scheduling": (
        "Once a process gets the CPU, it keeps running until it finishes.\n"
        "No other process can interrupt it midway.\n"
        "Example: FCFS, Non-Preemptive Priority Scheduling."
    ),
    "Quantum": (
        "Quantum (or Time Slice) is the fixed amount of CPU time given to each process\n"
        "in Round Robin Scheduling.\n"
        "After its time is over, the CPU moves to the next process."
    ),
    "Queue": (
        "A Queue is a level or stage where processes wait to be scheduled.\n"
        "In Multilevel or MLFQ (Multilevel Feedback Queue), each queue has its own rules.\n"
        "Example: High-priority processes in one queue, lower ones in another."
    ),
}
class SchedulerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CPU Scheduling Visualizer")
        # self.root.geometry("600x400")
        self.root.configure(bg="white")

        self.create_main_page()

    def create_main_page(self):
        # Define styles
        style = ttk.Style()
        style.configure("Title.TLabel", font=("Helvetica", 24, "bold"))
        style.configure("Subtitle.TLabel", font=("Helvetica", 18, "bold"))
        style.configure("Main.TButton", font=("Arial", 14), padding=10)
        style.configure("Term.TButton", font=("Arial", 12), padding=6)
                
        title = ttk.Label(self.root, text="CPU Scheduling Algorithms", style="Title.TLabel", background="white")
        title.pack(pady=20)

        # Algorithm dropdown
        self.selected_algo = tk.StringVar()
        algo_dropdown = ttk.Combobox(self.root, textvariable=self.selected_algo, state="readonly", width=50, font=("Arial", 12))
        algo_dropdown['values'] = list(ALGORITHMS.keys())
        algo_dropdown.pack(pady=10)
        algo_dropdown.set("Select an algorithm to visualize")

        # Start Simulation button
        ttk.Button(self.root, text="Start Simulation", command=self.run_selected_algorithm,
                style="Main.TButton").pack(pady=10)

        # Definitions section
        ttk.Label(self.root, text="Definitions", style="Subtitle.TLabel", background="white").pack(pady=10)

        defs_frame = tk.Frame(self.root, bg="white")
        defs_frame.pack()

        for term in DEFINITIONS:
            ttk.Button(defs_frame, text=term, style="Term.TButton",
                    command=lambda t=term: self.open_definition(t)).pack(pady=4, fill='x', padx=50)

    def open_definition(self, term):
        win = tk.Toplevel(self.root)
        win.title(term)
        win.geometry("450x250")
        tk.Label(win, text=term, font=("Helvetica", 16, "bold")).pack(pady=10)
        tk.Label(win, text=DEFINITIONS[term], wraplength=400, font=("Arial", 12)).pack(padx=20)

    def run_selected_algorithm(self):
        algo_name = self.selected_algo.get()
        if algo_name not in ALGORITHMS:
            messagebox.showerror("Error", "Please select a valid algorithm.")
            return

        module_name = ALGORITHMS[algo_name]
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, 'main'):
                module.main()  # assumes your script has a main() method to launch GUI
            else:
                messagebox.showerror("Error", f"The module '{module_name}' does not have a 'main()' function.")
        except ModuleNotFoundError:
            messagebox.showerror("File Not Found", f"The file '{module_name}.py' was not found in the directory.")
        except Exception as e:
            messagebox.showerror("Execution Error", str(e))

def main():
    root = tk.Tk()
    root.state('zoomed')  # Windows only
    root.resizable(True, True)
    app = SchedulerGUI(root)
    root.mainloop()
    
if __name__ == '__main__':
    main()