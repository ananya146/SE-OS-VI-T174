import tkinter as tk
from tkinter import Label, ttk, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import MaxNLocator
import textwrap
import tkinter.font as tkFont

class DiskSchedulingVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Disk Scheduling Algorithm Visualizer")
        self.root.geometry("1400x900")
        self.root.configure(bg="#f0f0f0")
        title = ttk.Label(self.root, text="DISK Scheduling Algorithms", style="Title.TLabel", background="white",font=("Helvetica", 20,"bold"))
        title.pack(pady=20)
        # Algorithm documentation
        self.algo_docs = {
            "FCFS": {
                "description": "First-Come, First-Served - Services requests in the order they arrive",
                "algorithm": "1. Start from initial head position\n2. Service requests in the order they were received\n3. Calculate total head movement",
                "advantages": "• Simple to implement\n• Fair to all requests",
                "disadvantages": "• Poor performance with scattered requests\n• High seek times",
                "complexity": "Time: O(n)\nSpace: O(1)"
            },
            "SSTF": {
                "description": "Shortest Seek Time First - Services the nearest request first",
                "algorithm": "1. Start from initial head position\n2. Find request with minimum seek time\n3. Service that request\n4. Repeat until all requests are serviced",
                "advantages": "• Better performance than FCFS\n• Reduces average seek time",
                "disadvantages": "• Can cause starvation\n• Not optimal for all cases",
                "complexity": "Time: O(n^2)\nSpace: O(1)"
            },
            "SCAN": {
                "description": "Elevator Algorithm - Moves back and forth across the disk",
                "algorithm": "1. Start from initial head position\n2. Move in a direction (left/right)\n3. Service all requests along the way\n4. Reverse direction at end of disk\n5. Repeat until all requests serviced",
                "advantages": "• No starvation\n• Good for heavy loads",
                "disadvantages": "• Long wait times for some requests",
                "complexity": "Time: O(n log n)\nSpace: O(1)"
            },
            "C-SCAN": {
                "description": "Circular SCAN - Services requests in one direction only",
                "algorithm": "1. Start from initial head position\n2. Move in one direction (e.g., right)\n3. Service requests along the way\n4. Jump to start (without servicing)\n5. Repeat",
                "advantages": "• More uniform wait times\n• Better than SCAN for some workloads",
                "disadvantages": "• Wastes time returning to start",
                "complexity": "Time: O(n log n)\nSpace: O(1)"
            },
            "LOOK": {
                "description": "Improved SCAN - Only goes as far as last request",
                "algorithm": "1. Start from initial head position\n2. Move in a direction\n3. Service requests until last request\n4. Reverse direction\n5. Repeat",
                "advantages": "• More efficient than SCAN\n• Doesn't go to disk ends unnecessarily",
                "disadvantages": "• Still has some unnecessary movement",
                "complexity": "Time: O(n log n)\nSpace: O(1)"
            },
            "C-LOOK": {
                "description": "Circular LOOK - Services requests in one direction only",
                "algorithm": "1. Start from initial head position\n2. Move in one direction\n3. Service requests until last request\n4. Jump to first request in opposite end\n5. Repeat",
                "advantages": "• Most efficient of SCAN variants\n• Minimal wasted movement",
                "disadvantages": "• Slightly more complex to implement",
                "complexity": "Time: O(n log n)\nSpace: O(1)"
            }
        }

        # Main container
        main_frame = tk.Frame(root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Header Frame (Input controls)
        header_frame = tk.Frame(main_frame, bg="#f0f0f0", bd=1, relief=tk.RIDGE)
        header_frame.pack(fill=tk.X, padx=5, pady=5)

        # Algorithm Selection
        tk.Label(header_frame, text="Algorithm:", font=("Helvetica", 16, "bold"), bg="#f0f0f0").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.algo_var = tk.StringVar(value="FCFS")
        self.algo_menu = ttk.Combobox(header_frame, textvariable=self.algo_var, 
                                     values=list(self.algo_docs.keys()), width=15)
        self.algo_menu.grid(row=0, column=1, padx=5, pady=5)
        self.algo_menu.bind("<<ComboboxSelected>>", self.update_documentation)

        # Initial Position
        tk.Label(header_frame, text="Initial Position:", font=("Helvetica", 12), bg="#f0f0f0").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.init_pos_entry = tk.Entry(header_frame, width=15)
        self.init_pos_entry.grid(row=0, column=3, padx=5, pady=5)
        self.init_pos_entry.insert(0, "50")

        # Requests
        tk.Label(header_frame, text="Requests:", font=("Helvetica", 12), bg="#f0f0f0").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.requests_entry = tk.Entry(header_frame, width=15)
        self.requests_entry.grid(row=0, column=5, padx=5, pady=5)
        self.requests_entry.insert(0, "90,12,56,77")

        # Direction (for SCAN/C-SCAN)
        tk.Label(header_frame, text="Direction:", font=("Helvetica", 12), bg="#f0f0f0").grid(row=0, column=6, padx=5, pady=5, sticky="w")
        self.direction_var = tk.StringVar(value="right")
        ttk.Radiobutton(header_frame, text="Right", variable=self.direction_var, value="right").grid(row=0, column=7, padx=5, sticky="w")
        ttk.Radiobutton(header_frame, text="Left", variable=self.direction_var, value="left").grid(row=0, column=8, padx=5, sticky="w")

        # Disk Size
        tk.Label(header_frame, text="Disk Size:", font=("Helvetica", 12), bg="#f0f0f0").grid(row=0, column=9, padx=5, pady=5, sticky="w")
        self.disk_size_entry = tk.Entry(header_frame, width=15)
        self.disk_size_entry.grid(row=0, column=10, padx=5, pady=5)
        self.disk_size_entry.insert(0, "200")

        # Visualization Mode
        tk.Label(header_frame, text="Mode:", font=("Helvetica", 12), bg="#f0f0f0").grid(row=0, column=11, padx=5, pady=5, sticky="w")
        self.viz_mode = tk.StringVar(value="auto")
        ttk.Radiobutton(header_frame, text="Auto", variable=self.viz_mode, value="auto").grid(row=0, column=12, padx=5, sticky="w")
        ttk.Radiobutton(header_frame, text="Manual", variable=self.viz_mode, value="manual").grid(row=0, column=13, padx=5, sticky="w")

        # Run Button
        run_btn = tk.Button(header_frame, text="Visualize", font=("Helvetica", 12, "bold"),
                          bg="#4CAF50", fg="white", command=self.visualize)
        run_btn.grid(row=0, column=14, padx=10, pady=5)

        # Visualization Frame (Main content)
        viz_container = tk.Frame(main_frame, bg="#ffffff")
        viz_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Visualization Frame
        self.viz_frame = tk.Frame(viz_container, bg="#ffffff")
        self.viz_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Control buttons for manual mode
        self.control_frame = tk.Frame(viz_container, bg="#f0f0f0")
        self.control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.next_btn = tk.Button(self.control_frame, text="Next", font=("Helvetica", 10),
                                bg="#2196F3", fg="white", command=self.next_step)
        self.next_btn.pack(side=tk.RIGHT, padx=5)
        self.next_btn.pack_forget()  # Hide initially
        
        self.reset_btn = tk.Button(self.control_frame, text="Reset", font=("Arial", 10),
                                 bg="#f44336", fg="white", command=self.reset_visualization)
        self.reset_btn.pack(side=tk.RIGHT, padx=5)
        self.reset_btn.pack_forget()  # Hide initially

        bottom_container = tk.Frame(main_frame, bg="#f0f0f0")
        bottom_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Results Frame - left side (50%)
        self.results_frame = tk.Frame(bottom_container, bg="#f0f0f0", height=200)
        self.results_frame.grid(row=0, column=0, sticky="nsew", padx=(10,5), pady=5)
        self.results_frame.grid_propagate(False)

        # Footer Frame (Documentation) - right side (50%)
        footer_frame = tk.Frame(bottom_container, bg="#f0f0f0", bd=1, relief=tk.RIDGE)
        footer_frame.grid(row=0, column=1, sticky="nsew", padx=(5,10), pady=5)

        # Configure equal column weights
        bottom_container.grid_columnconfigure(0, weight=1, uniform="half")
        bottom_container.grid_columnconfigure(1, weight=1, uniform="half")
        bottom_container.grid_rowconfigure(0, weight=1)
 
        # Documentation Title
        tk.Label(footer_frame, text="Algorithm Documentation", font=("Arial", 14, "bold"), 
                bg="#f0f0f0").pack(pady=5)

        # Documentation Text
        self.doc_text = scrolledtext.ScrolledText(footer_frame, wrap=tk.WORD, width=150, height=10,
                                               font=("Arial", 11), bg="white", bd=0)
        self.doc_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        custom_font = tkFont.Font(family="Helvetica", size=11)

        self.doc_text.configure(
            font=custom_font,
            bg="#f4f7fb",
            fg="#2e2e2e",
            wrap="word",
            relief="flat",
            padx=10,
            pady=10
        )

        self.doc_text.tag_configure("title", font=("Helvetica", 14, "bold"), foreground="#1f4e79", spacing3=10)
        self.doc_text.tag_configure("section_header", font=("Helvetica", 12, "bold"), foreground="#003366", spacing1=5, spacing3=5)
        self.doc_text.tag_configure("section_text", font=("Helvetica", 11), foreground="#333333", lmargin1=10, lmargin2=10)

        # Initialize plot and manual mode variables
        self.fig = None
        self.ax_disk = None
        self.ax_chart = None
        self.canvas = None
        self.animation = None
        self.current_step = 0
        self.sequence = []
        self.disk_size = 0
        self.initial_pos = 0
        self.requests = []

        # Initialize documentation
        self.update_documentation()


    def update_documentation(self, event=None):
        algo = self.algo_var.get()
        doc = self.algo_docs.get(algo, {})

        self.doc_text.config(state=tk.NORMAL)
        self.doc_text.delete(1.0, tk.END)

        self.doc_text.insert(tk.END, f"Algorithm Selected: {algo.upper()}\n", "title")

        sections = [
            ("Description", doc.get("description", ""), True),
            ("Algorithm Steps", doc.get("algorithm", ""), False),
            ("Advantages", doc.get("advantages", ""), False),
            ("Disadvantages", doc.get("disadvantages", ""), True),
            ("Complexity", doc.get("complexity", ""), False)
        ]

        for header, content, wrap in sections:
            if content:
                self.doc_text.insert(tk.END, f"\n\n{header}:\n", "section_header")
                final_content = textwrap.fill(content.strip(), width=100) if wrap else content.strip()
                self.doc_text.insert(tk.END, final_content, "section_text")

        self.doc_text.config(state=tk.DISABLED)




    def visualize(self):
        try:
            # Get inputs
            algorithm = self.algo_var.get()
            self.initial_pos = int(self.init_pos_entry.get())
            self.requests = [int(x.strip()) for x in self.requests_entry.get().split(",")]
            self.disk_size = int(self.disk_size_entry.get())
            direction = self.direction_var.get()
            mode = self.viz_mode.get()
            
            # Validate inputs
            if self.initial_pos < 0 or self.initial_pos >= self.disk_size:
                raise ValueError(f"Initial position must be between 0 and {self.disk_size-1}")
            for req in self.requests:
                if req < 0 or req >= self.disk_size:
                    raise ValueError(f"Request {req} is outside disk range (0-{self.disk_size-1})")
                    
            # Clear previous visualization
            if self.canvas:
                self.canvas.get_tk_widget().destroy()
            if self.animation:
                self.animation.event_source.stop()
                
            # Calculate sequence based on algorithm
            self.sequence, total_movement, metrics = self.calculate_sequence(
                algorithm, self.initial_pos, self.requests, self.disk_size, direction)
            
            # Update results
            self.update_results(algorithm, self.sequence, total_movement, metrics)
            
            # Create visualization
            self.create_dual_visualization(self.disk_size, self.initial_pos, self.requests, self.sequence)
            
            # Show control buttons for manual mode
            if mode == "manual":
                self.current_step = 0
                self.next_btn.pack(side=tk.RIGHT, padx=5)
                self.reset_btn.pack(side=tk.RIGHT, padx=5)
                self.update_manual_step(0)  # Show initial state
            else:
                # Start automatic animation
                self.animation = FuncAnimation(self.fig, self.update_frame, frames=len(self.sequence), 
                                             interval=1100, blit=True, repeat=False)
                self.canvas.draw()

        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
            
    def next_step(self):
        """Advance to the next step in manual mode"""
        if self.current_step < len(self.sequence) - 1:
            self.current_step += 1
            self.update_manual_step(self.current_step)
            
    def reset_visualization(self):
        """Reset the visualization to initial state"""
        self.current_step = 0
        self.update_manual_step(0)
        
    def update_manual_step(self, step):
        """Update visualization for the current manual step"""
        # Update disk visualization
        if step == 0:
            prev_pos = self.sequence[0]
        else:
            prev_pos = self.sequence[step-1]
            
        current_pos = self.sequence[step]
        
        # Calculate angles (convert to radians)
        angle = 2 * np.pi * current_pos / self.disk_size
        prev_angle = 2 * np.pi * prev_pos / self.disk_size
        
        # For smooth movement along circumference
        if abs(current_pos - prev_pos) > self.disk_size/2:  # Handle wrap-around
            if current_pos > prev_pos:
                # Moving left through 0
                angles = np.linspace(prev_angle, 2*np.pi, 10)
                angles = np.concatenate([angles, np.linspace(0, angle, 10)])
            else:
                # Moving right through end
                angles = np.linspace(prev_angle, 0, 10)
                angles = np.concatenate([angles, np.linspace(2*np.pi, angle, 10)])
        else:
            angles = np.linspace(prev_angle, angle, 20)
        
        # Update disk path
        self.disk_path.set_data(angles, np.ones_like(angles))
        self.disk_pointer.set_data([angle], [1])
        
        # Highlight current position on disk
        for i, txt in enumerate(self.ax_disk.texts):
            if txt.get_text() == str(current_pos):
                txt.set_color('red')
                txt.set_fontweight('bold')
            else:
                txt.set_color('black')
                txt.set_fontweight('normal')
        
        # Update chart visualization
        x_data = [pos for pos in self.sequence[:step+1]]
        y_data = list(range(step+1))
        self.chart_line.set_data(x_data, y_data)
        self.chart_points.set_data(x_data, y_data)
        self.chart_current.set_data([current_pos], [step])
        
        # Adjust chart limits if needed
        if step > self.ax_chart.get_xlim()[1] - 2:
            self.ax_chart.set_xlim(0, len(self.sequence))
        
        self.canvas.draw()
        
    def update_frame(self, frame):
        """Update function for automatic animation"""
        if frame == 0:
            return self.disk_path, self.disk_pointer, self.chart_line, self.chart_points, self.chart_current
        
        # Update disk visualization
        current_pos = self.sequence[frame]
        prev_pos = self.sequence[frame-1]
        
        # Calculate angles (convert to radians)
        angle = 2 * np.pi * current_pos / self.disk_size
        prev_angle = 2 * np.pi * prev_pos / self.disk_size
        
        # For smooth movement along circumference
        if abs(current_pos - prev_pos) > self.disk_size/2:  # Handle wrap-around
            if current_pos > prev_pos:
                # Moving left through 0
                angles = np.linspace(prev_angle, 2*np.pi, 10)
                angles = np.concatenate([angles, np.linspace(0, angle, 10)])
            else:
                # Moving right through end
                angles = np.linspace(prev_angle, 0, 10)
                angles = np.concatenate([angles, np.linspace(2*np.pi, angle, 10)])
        else:
            angles = np.linspace(prev_angle, angle, 20)
        
        # Update disk path
        self.disk_path.set_data(angles, np.ones_like(angles))
        self.disk_pointer.set_data([angle], [1])
        
        # Highlight current position on disk
        for i, txt in enumerate(self.ax_disk.texts):
            if txt.get_text() == str(current_pos):
                txt.set_color('red')
                txt.set_fontweight('bold')
            else:
                txt.set_color('black')
                txt.set_fontweight('normal')
        
        # Update chart visualization
        x_data = [pos for pos in self.sequence[:frame+1]]
        y_data = list(range(frame+1))
        self.chart_line.set_data(x_data, y_data)
        self.chart_points.set_data(x_data, y_data)
        self.chart_current.set_data([current_pos], [frame])
        
        # Adjust chart limits if needed
        if frame > self.ax_chart.get_xlim()[1] - 2:
            self.ax_chart.set_xlim(0, len(self.sequence))
        
        return self.disk_path, self.disk_pointer, self.chart_line, self.chart_points, self.chart_current
            
    def calculate_sequence(self, algorithm, initial_pos, requests, disk_size, direction):
        sequence = [initial_pos]
        reqs = requests.copy()
        current_pos = initial_pos
        total_movement = 0
        metrics = {
            "total_requests": len(requests),
            "throughput": 0,
            "avg_seek_time": 0
        }
        
        if algorithm == "FCFS":
            for req in reqs:
                total_movement += abs(req - current_pos)
                current_pos = req
                sequence.append(req)
                
        elif algorithm == "SSTF":
            while reqs:
                closest = min(reqs, key=lambda x: abs(x - current_pos))
                total_movement += abs(closest - current_pos)
                current_pos = closest
                sequence.append(closest)
                reqs.remove(closest)
                
        elif algorithm == "SCAN":
            if direction == "right":
                reqs_sorted = sorted([r for r in reqs if r >= current_pos])
                reqs_sorted += [disk_size - 1] + sorted([r for r in reqs if r < current_pos], reverse=True)
            else:
                reqs_sorted = sorted([r for r in reqs if r <= current_pos], reverse=True)
                reqs_sorted += [0] + sorted([r for r in reqs if r > current_pos])
                
            for pos in reqs_sorted:
                total_movement += abs(pos - current_pos)
                current_pos = pos
                sequence.append(pos)
                
        elif algorithm == "C-SCAN":
            if direction == "right":
                reqs_sorted = sorted([r for r in reqs if r >= current_pos])
                reqs_sorted += [disk_size - 1, 0] + sorted([r for r in reqs if r < current_pos])
            else:
                reqs_sorted = sorted([r for r in reqs if r <= current_pos], reverse=True)
                reqs_sorted += [0, disk_size - 1] + sorted([r for r in reqs if r > current_pos], reverse=True)
                
            for pos in reqs_sorted:
                total_movement += abs(pos - current_pos)
                current_pos = pos
                sequence.append(pos)
                
        elif algorithm == "LOOK":
            if direction == "right":
                reqs_sorted = sorted([r for r in reqs if r >= current_pos])
                reqs_sorted += sorted([r for r in reqs if r < current_pos], reverse=True)
            else:
                reqs_sorted = sorted([r for r in reqs if r <= current_pos], reverse=True)
                reqs_sorted += sorted([r for r in reqs if r > current_pos])
                
            for pos in reqs_sorted:
                total_movement += abs(pos - current_pos)
                current_pos = pos
                sequence.append(pos)
                
        elif algorithm == "C-LOOK":
            if direction == "right":
                reqs_sorted = sorted([r for r in reqs if r >= current_pos])
                reqs_sorted += sorted([r for r in reqs if r < current_pos])
            else:
                reqs_sorted = sorted([r for r in reqs if r <= current_pos], reverse=True)
                reqs_sorted += sorted([r for r in reqs if r > current_pos], reverse=True)
                
            for pos in reqs_sorted:
                total_movement += abs(pos - current_pos)
                current_pos = pos
                sequence.append(pos)
        
        # Calculate metrics
        metrics["throughput"] = len(requests) / (total_movement if total_movement > 0 else 1)
        metrics["avg_seek_time"] = total_movement / len(requests) if requests else 0
        
        return sequence, total_movement, metrics
        
    def update_results(self, algorithm, sequence, total_movement, metrics):
        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        # Create main grid with 2 columns
        results_grid = tk.Frame(self.results_frame, bg="#f0f0f0")
        results_grid.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left column - Algorithm info
        algo_frame = tk.Frame(results_grid, bg="#f0f0f0")
        algo_frame.grid(row=0, column=0, sticky="nsew", padx=5)
        
        tk.Label(algo_frame, text=f"Algorithm: {algorithm}", 
                font=("Arial", 12, "bold"), bg="#f0f0f0").pack(anchor="w", pady=2)
                
        seq_text = " → ".join(map(str, sequence))
        seq_label = tk.Label(algo_frame, text=f"Sequence: {seq_text}", 
                            font=("Arial", 12), bg="#f0f0f0", wraplength=300, justify="left")
        seq_label.pack(anchor="w", pady=2)
        
        # Right column - Metrics (now in vertical layout)
        metrics_frame = tk.Frame(results_grid, bg="#f0f0f0")
        metrics_frame.grid(row=0, column=1, sticky="nsew", padx=5)
        
        tk.Label(metrics_frame, text="Performance Metrics:", 
                font=("Arial", 12, "bold"), bg="#f0f0f0").pack(anchor="w", pady=2)
        
        # Metrics in vertical layout
        metrics_data = [
            f"Total Head Movement: {total_movement} cylinders",
            f"Throughput: {metrics['throughput']:.2f} requests/cylinder",
            f"Avg Seek Time: {metrics['avg_seek_time']:.2f} cylinders/request"
        ]
        
        for metric in metrics_data:
            tk.Label(metrics_frame, text=metric, 
                    font=("Arial", 12), bg="#f0f0f0").pack(anchor="w", pady=2)
        
        # Configure grid weights
        results_grid.grid_columnconfigure(0, weight=1)
        results_grid.grid_columnconfigure(1, weight=1)
        results_grid.grid_rowconfigure(0, weight=1)

    def create_dual_visualization(self, disk_size, initial_pos, requests, sequence):
        # Create figure with two subplots with more spacing
        self.fig = plt.figure(figsize=(12, 6))
        gs = GridSpec(1, 2, width_ratios=[1, 1.5], wspace=0.4)  # Increased wspace for more separation
        self.ax_disk = self.fig.add_subplot(gs[0], polar=True)
        self.ax_chart = self.fig.add_subplot(gs[1])
        
        # Disk visualization setup
        self.setup_disk_visualization(disk_size, initial_pos, requests)
        
        # Chart visualization setup
        self.setup_chart_visualization(sequence)
        
        # Create animation objects for disk
        self.disk_path, = self.ax_disk.plot([], [], 'r-', linewidth=2, alpha=0.7)
        self.disk_pointer, = self.ax_disk.plot([], [], 'ro', markersize=10)
        
        # Create animation objects for chart
        self.chart_line, = self.ax_chart.plot([], [], 'b-', linewidth=2)
        self.chart_points, = self.ax_chart.plot([], [], 'bo', markersize=8)
        self.chart_current, = self.ax_chart.plot([], [], 'ro', markersize=10)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.viz_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def setup_disk_visualization(self, disk_size, initial_pos, requests):
        self.ax_disk.clear()
        self.ax_disk.set_theta_zero_location('N')
        self.ax_disk.set_theta_direction(-1)
        self.ax_disk.set_ylim(0, 1.2)
        self.ax_disk.set_xticks([])
        self.ax_disk.set_yticks([])
        self.ax_disk.set_title("Disk Head Movement (Circumference Path)", pad=20)
        
        # Draw disk outline with better colors
        theta = np.linspace(0, 2*np.pi, 100)
        radius = np.ones(100)
        self.ax_disk.plot(theta, radius, '#4682B4', linewidth=3, alpha=0.7)
        
        # Mark only important positions (0, disk_size-1, initial, and requests)
        important_positions = {0, disk_size-1, initial_pos}
        important_positions.update(requests)
        
        for pos in sorted(important_positions):
            angle = 2 * np.pi * pos / disk_size
            color = '#FF6347' if pos in requests else '#2E8B57' if pos == initial_pos else '#4682B4'
            marker = 'o'
            size = 8 if pos in (0, disk_size-1, initial_pos) else 6
            self.ax_disk.plot(angle, 1, marker=marker, color=color, markersize=size)
            self.ax_disk.text(angle, 1.1, str(pos), ha='center', va='center', 
                             color=color, fontweight='bold' if pos in (0, disk_size-1, initial_pos) else 'normal')
        
        # Add legend
        self.ax_disk.plot([], [], 'o', color='#2E8B57', markersize=8, label='Initial Position')
        self.ax_disk.plot([], [], 'o', color='#FF6347', markersize=6, label='Request')
        self.ax_disk.plot([], [], 'o', color='#4682B4', markersize=8, label='Boundary')
        self.ax_disk.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        
    def setup_chart_visualization(self, sequence):
        self.ax_chart.clear()
        self.ax_chart.set_ylim(0, len(sequence)-1)
        self.ax_chart.set_xlim(min(sequence)-10, max(sequence)+10)
        self.ax_chart.set_ylabel("Step Number")
        self.ax_chart.set_xlabel("Track Number")
        self.ax_chart.set_title("Head Movement Sequence", pad=20)
        self.ax_chart.grid(True, alpha=0.3)
        
        self.ax_chart.yaxis.set_major_locator(MaxNLocator(integer=True))
        # Add vertical lines for each unique position
        for pos in sorted(set(sequence)):
            self.ax_chart.axvline(x=pos, color='gray', linestyle='--', alpha=0.3)
        
        # Add initial point
        self.ax_chart.plot(sequence[0], 0, 'yo', markersize=8, label='Start')
        self.ax_chart.legend()

def main():
    root = tk.Tk()
    root.state('zoomed')  # Windows only
    root.resizable(True, True)
    app = DiskSchedulingVisualizer(root)
    root.mainloop()

if __name__ == "__main__":
    main()