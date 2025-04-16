import networkx as nx
import tkinter as tk
from   tkinter import messagebox

import matplotlib.pyplot as plt
from   matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class GraphApp:
        def __init__(self, root):
                self.root = root
                self.root.title("Graph Drawing and TSP Solver")
                
                # Initialize graph
                self.graph = nx.Graph()
                self.nodes = []
                self.edges = []

                # Create UI components
                self.canvas = tk.Canvas(root, width=600, height=400, bg="white")
                self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                self.canvas.bind("<Button-1>", self.add_node)
                self.canvas.bind("<Button-3>", self.add_edge)

                self.control_frame = tk.Frame(root)
                self.control_frame.pack(side=tk.RIGHT, fill=tk.Y)

                self.run_tsp_button = tk.Button(self.control_frame, text="Run TSP Algorithm", command=self.run_tsp)
                self.run_tsp_button.pack(pady=10)

                self.clear_button = tk.Button(self.control_frame, text="Clear Graph", command=self.clear_graph)
                self.clear_button.pack(pady=10)

        def add_node(self, event):
                node_id = len(self.nodes) + 1
                self.nodes.append((event.x, event.y))
                self.graph.add_node(node_id, pos=(event.x, event.y))
                self.canvas.create_oval(event.x - 5, event.y - 5, event.x + 5, event.y + 5, fill="blue")
                self.canvas.create_text(event.x, event.y - 10, text=str(node_id), fill="black")

        def add_edge(self, event):
                if len(self.nodes) < 2:
                        messagebox.showerror("Error", "Add at least two nodes before creating an edge.")
                        return

                closest_node = self.find_closest_node(event.x, event.y)
                if len(self.edges) > 0 and closest_node in self.edges[-1]:
                        return

                if len(self.edges) == 0 or len(self.edges[-1]) == 2:
                        self.edges.append([closest_node])
                else:
                        self.edges[-1].append(closest_node)
                        self.graph.add_edge(self.edges[-1][0], self.edges[-1][1])
                        x1, y1 = self.graph.nodes[self.edges[-1][0]]['pos']
                        x2, y2 = self.graph.nodes[self.edges[-1][1]]['pos']
                        self.canvas.create_line(x1, y1, x2, y2, fill="black")

        def find_closest_node(self, x, y):
                min_dist = float('inf')
                closest_node = None
                for node_id, (nx, ny) in enumerate(self.nodes, start=1):
                        dist = (nx - x) ** 2 + (ny - y) ** 2
                        if dist < min_dist:
                                min_dist = dist
                                closest_node = node_id
                return closest_node

        def run_tsp(self):
                if len(self.graph.nodes) < 2:
                        messagebox.showerror("Error", "Add at least two nodes to run TSP.")
                        return

                # Placeholder for TSP algorithm
                messagebox.showinfo("TSP", "TSP algorithm not implemented yet.")

        def clear_graph(self):
                self.graph.clear()
                self.nodes.clear()
                self.edges.clear()
                self.canvas.delete("all")

if __name__ == "__main__":
        root = tk.Tk()
        app = GraphApp(root)
        root.mainloop()
