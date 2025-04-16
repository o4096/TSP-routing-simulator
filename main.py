import  tkinter as tk
from    tkinter import messagebox
import  networkx as nx
import  os
#import matplotlib.pyplot as plt
#from   matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

NODE_RADIUS= 10

class GraphApp:
	def __init__(self, root):
		self.root= root
		self.root.title('Graph Drawing and TSP Solver')
		
		# Initialize graph
		self.graph= nx.Graph()
		self.nodes= []
		self.edges= []
		self.selected_node = None

		# Create UI components
		self.canvas= tk.Canvas(root, width=600, height=400, bg='white')
		self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		self.canvas.bind('<Button-1>', self.add_node)
		self.canvas.bind('<Button-3>', self.add_edge)

		self.control_frame = tk.Frame(root)
		self.control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

		self.run_tsp_button= tk.Button(self.control_frame, text='Run TSP Algorithm', command=self.run_tsp)
		self.run_tsp_button.pack(pady=10)

		self.clear_button= tk.Button(self.control_frame, text='Clear Graph', command=self.clear_graph)
		self.clear_button.pack(pady=10)

	def add_node(self, event):
		node_id = len(self.nodes)
		self.nodes.append((event.x, event.y))
		self.graph.add_node(node_id, pos=(event.x, event.y))
		self.selected_node= node_id
		self.redraw()

	def add_edge(self, event):
		node= self.find_closest_node(event.x, event.y)
		if not node:
			return
				
		self.selected_node= node
		if len(self.edges) > 0 and node in self.edges[-1]:
			return

		if len(self.edges) == 0 or len(self.edges[-1]) == 2:
			self.edges.append([node])
		else:
			self.edges[-1].append(node)
			self.graph.add_edge(self.edges[-1][0], self.edges[-1][1])
			self.redraw()

	def find_closest_node(self, x, y):
		min_dist = float('inf')
		closest_node = None
		os.system('cls')
		for node_id, (nx, ny) in enumerate(self.nodes):
			dist = (nx - x) ** 2 + (ny - y) ** 2
			print(f'click at ({x:4d}, {y:4d}), node: {node_id:2d} ({nx:4d}, {ny:4d}), distance: {dist}')
			if dist < min_dist and dist <= NODE_RADIUS*NODE_RADIUS:
				min_dist = dist
				closest_node= node_id
				self.selected_node= node_id
				self.redraw()
		return closest_node

	def run_tsp(self):
		if len(self.graph.nodes) < 2:
			messagebox.showerror('Error', 'Add at least two nodes to run TSP.')
			return

		# Placeholder for TSP algorithm
		messagebox.showinfo('TSP', 'TSP algorithm not implemented yet.')

	def clear_graph(self):
		self.graph.clear()
		self.nodes.clear()
		self.edges.clear()
		self.canvas.delete('all')

	def redraw(self):
		self.canvas.delete('all')
		for edge in self.edges:
			if len(edge) == 2:
				x1, y1 = self.graph.nodes[edge[0]]['pos']
				x2, y2 = self.graph.nodes[edge[1]]['pos']
				self.canvas.create_line(x1, y1, x2, y2, fill='black')

		for node_id, (x, y) in enumerate(self.nodes):
			self.canvas.create_oval(x-NODE_RADIUS, y-NODE_RADIUS, x+NODE_RADIUS, y+NODE_RADIUS, fill='white')
			self.canvas.create_text(x, y, text=str(node_id), fill='black')

		node= self.nodes[self.selected_node]
		self.canvas.create_oval(node[0]-NODE_RADIUS, node[1]-NODE_RADIUS, node[0]+NODE_RADIUS, node[1]+NODE_RADIUS, fill='grey')


if __name__ == '__main__':
	root = tk.Tk()
	app = GraphApp(root)
	root.mainloop()