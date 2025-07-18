import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math


class MemoryAllocationVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Memory Allocation Visualizer")

        self.allocation_type = tk.StringVar(value="First Fit")
        self.block_input = tk.StringVar()
        self.process_input = tk.StringVar()
        self.page_size_input = tk.StringVar(value="4")

        self.original_blocks = []
        self.blocks = []
        self.processes = []
        self.allocations = []
        self.block_allocations = []
        self.current_step = 0

        self.setup_ui()

    def setup_ui(self):
        font_large = ("Arial", 16)
        font_medium = ("Arial", 14)
        font_small = ("Arial", 12)
    # Style configuration for consis
    # tent large UI
        style = ttk.Style()
        style.configure("TLabel", font=font_large)
        style.configure("TEntry", font=font_medium)
        style.configure("TCombobox", font=font_medium)

        padding = {"padx": 20, "pady": 10}

        ttk.Label(self.root, text="Select Allocation Type:").pack(**padding)
        algo_dropdown = ttk.Combobox(
            self.root,
            textvariable=self.allocation_type,
            values=["First Fit", "Best Fit", "Worst Fit", "Paging", "Segmentation"],
            state="readonly",
            justify="center",
            font=font_medium,
            width=20
        )
        algo_dropdown.pack()

        ttk.Label(self.root, text="\nEnter Memory Block Sizes (space separated):").pack(**padding)
        self.block_entry = ttk.Entry(self.root, textvariable=self.block_input, font=font_medium, width=60, justify="center")
        self.block_entry.pack()

        ttk.Label(self.root, text="\nEnter Process Sizes (space separated):").pack(**padding)
        self.process_entry = ttk.Entry(self.root, textvariable=self.process_input, font=font_medium, width=60, justify="center")
        self.process_entry.pack()

        ttk.Label(self.root, text="\nEnter Page Size (Only for Paging):").pack(**padding)
        self.page_entry = ttk.Entry(self.root, textvariable=self.page_size_input, font=font_medium, width=20, justify="center")
        self.page_entry.pack()

        self.visualize_button = tk.Button(
            self.root, text="Visualize Allocation", bg="green", fg="white",
            font=font_medium, command=self.visualize_initial, height=2, width=30
        )
        self.visualize_button.pack(pady=20)

        self.fig, self.ax = plt.subplots(figsize=(14, 5))  # Wider plot for better view
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.status_label = tk.Label(self.root, text="Stepwise Allocation", font=("Arial", 14, "italic"), fg="gray")
        self.status_label.pack(pady=10)

        self.next_button = tk.Button(
            self.root, text="Next Step", bg="blue", fg="white",
            font=font_medium, command=self.allocate_next, height=2, width=20
        )
        self.next_button.pack(pady=15)

    def reset(self):
        self.original_blocks = []
        self.blocks = []
        self.processes = []
        self.allocations = []
        self.block_allocations = []
        self.current_step = 0
        self.ax.clear()
        self.canvas.draw()
        self.status_label.config(text="Stepwise Allocation", fg="gray")

    def visualize_initial(self):
        self.reset()
        try:
            self.original_blocks = [int(x) for x in self.block_input.get().split()]
            self.blocks = self.original_blocks.copy()
            self.block_allocations = [[] for _ in self.original_blocks]
            self.processes = [int(x) for x in self.process_input.get().split()]
            self.allocations = [-1] * len(self.processes)
        except:
            self.status_label.config(text="Invalid input format.", fg="red")
            return
        self.draw_blocks()

    def draw_blocks(self, highlight_idx=None, highlight_process=None):
        self.ax.clear()
        start = 0
        for i, block_size in enumerate(self.original_blocks):
            remaining = self.blocks[i]
            allocated_segments = self.block_allocations[i]
            current_pos = start
            total_used = 0
            for pid, psize in allocated_segments:
                color = 'orange' if pid == highlight_process else 'lightblue'
                self.ax.barh(0, psize, left=current_pos, height=0.5, color=color, edgecolor='black')
                self.ax.text(current_pos + psize / 2, 0, f"P{pid}\n{psize}K", ha='center', va='center', fontsize=9)
                current_pos += psize
                total_used += psize
            if remaining > 0:
                self.ax.barh(0, remaining, left=current_pos, height=0.5, color='lightgray', edgecolor='black')
                self.ax.text(current_pos + remaining / 2, 0, f"Free\n{remaining}K", ha='center', va='center', fontsize=9)
            start += block_size + 5
        self.ax.axis('off')
        self.canvas.draw()

    def allocate_next(self):
        if self.current_step >= len(self.processes):
            self.status_label.config(text="All processes allocated.", fg="green")
            return

        process_size = self.processes[self.current_step]
        allocation_type = self.allocation_type.get()
        idx_to_allocate = -1

        if allocation_type in ["First Fit", "Best Fit", "Worst Fit"]:
            if allocation_type == "First Fit":
                for i, block in enumerate(self.blocks):
                    if block >= process_size:
                        idx_to_allocate = i
                        break
            elif allocation_type == "Best Fit":
                best = float('inf')
                for i, block in enumerate(self.blocks):
                    if process_size <= block < best:
                        best = block
                        idx_to_allocate = i
            elif allocation_type == "Worst Fit":
                worst = -1
                for i, block in enumerate(self.blocks):
                    if block >= process_size and block > worst:
                        worst = block
                        idx_to_allocate = i

            if idx_to_allocate != -1:
                self.allocations[self.current_step] = idx_to_allocate
                self.block_allocations[idx_to_allocate].append((self.current_step, process_size))
                self.blocks[idx_to_allocate] -= process_size
                self.status_label.config(text=f"Allocated P{self.current_step}", fg="green")
            else:
                self.status_label.config(text=f"Cannot allocate P{self.current_step}", fg="red")

        elif allocation_type == "Paging":
            try:
                page_size = int(self.page_size_input.get())
            except ValueError:
                self.status_label.config(text="Invalid page size", fg="red")
                return

            num_pages = math.ceil(process_size / page_size)
            allocated_pages = 0

            for i, block in enumerate(self.blocks):
                while self.blocks[i] >= page_size and allocated_pages < num_pages:
                    self.block_allocations[i].append((self.current_step, page_size))
                    self.blocks[i] -= page_size
                    allocated_pages += 1
                if allocated_pages == num_pages:
                    break

            if allocated_pages == num_pages:
                self.status_label.config(text=f"Paged P{self.current_step}", fg="green")
            else:
                self.status_label.config(text=f"Cannot page P{self.current_step}", fg="red")

        elif allocation_type == "Segmentation":
            # Assume each process has 2 segments (for simplicity, 60%-40%)
            seg1 = int(process_size * 0.6)
            seg2 = process_size - seg1
            allocated = []

            for seg in [seg1, seg2]:
                found = False
                for i, block in enumerate(self.blocks):
                    if block >= seg:
                        self.block_allocations[i].append((self.current_step, seg))
                        self.blocks[i] -= seg
                        allocated.append(True)
                        found = True
                        break
                if not found:
                    allocated.append(False)
                    break

            if all(allocated):
                self.status_label.config(text=f"Segmented P{self.current_step}", fg="green")
            else:
                self.status_label.config(text=f"Cannot segment P{self.current_step}", fg="red")

        self.draw_blocks(highlight_process=self.current_step)
        self.current_step += 1

def main():
    root = tk.Tk()
    root.state('zoomed')  # Windows only
    root.resizable(True, True)
    app = MemoryAllocationVisualizer(root)
    root.mainloop()




if __name__ == "__main__":
    main()