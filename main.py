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
		self.graph = nx.Graph()
		self.adjacency_matrix = None
		self.selected_node_id = None
		self.node_id_counter = 0

		# Create UI components
		self.canvas= tk.Canvas(root, width=600, height=400, bg='white')
		self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

		self.canvas.bind("<Button-1>", self.left_click)
		self.canvas.bind("<Button-3>", self.right_click)

		self.control_frame = tk.Frame(root)
		self.control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

		self.run_tsp_button= tk.Button(self.control_frame, text='Run TSP Algorithm', command=self.run_tsp)
		self.run_tsp_button.pack(pady=10)

		self.clear_button= tk.Button(self.control_frame, text='Clear Graph', command=self.clear_graph)
		self.clear_button.pack(pady=10)

	def add_node(self, event):
		node_id = self.node_id_counter
		self.node_id_counter += 1
		self.graph.add_node(node_id, id= node_id, x= event.x, y= event.y, color= 'white')
		self.adjacency_matrix = nx.adjacency_matrix(self.graph)
		self.redraw()

	def delete_node(self, note_to_be_deleted_id):
		for _, node in self.graph.nodes.items():
			if(node['id'] == note_to_be_deleted_id):
				self.graph.remove_node(node['id'])
				self.adjacency_matrix(self.graph)
				self.redraw()
				break


	def add_edge(self, prev_node_id):
		pass
			
			# self.edges[-1].append(node)
			# self.graph.add_edge(self.edges[-1][0], self.edges[-1][1])
			# self.redraw()

	

	def mouse_collision(self, event):
		min_dist = float('inf')
		closest_node_id = None
		os.system('cls')
		for _,node in self.graph.nodes.items():
			dist = (node['x'] - event.x) ** 2 + (node['y'] - event.y) ** 2
			print(f'click at ({event.x:4d}, {event.y:4d}), node: {node['id']:2d} ({node['x']:4d}, {node['y']:4d}), distance: {dist}')
			if dist < min_dist and dist <= NODE_RADIUS*NODE_RADIUS:
				min_dist = dist
				closest_node_id= node['id']
		return closest_node_id

	def left_click(self, event):
		node_hit_id = self.mouse_collision(event)
		if(node_hit_id == None ):
			# self.selected_node_id = None
			self.add_node(event)
		elif(self.selected_node_id == None):
			self.selected_node_id = node_hit_id
			self.redraw()
		else:
			prev_selected_node_id = self.selected_node_id
			self.selected_node_id = node_hit_id
			self.add_edge(prev_selected_node_id)
			self.redraw()
			# self.add_edge(prev_selected_node_id)

	def right_click(self,event):
		node_hit_id = self.mouse_collision(event)
		if(node_hit_id == None):
			self.selected_node_id = None
			self.redraw()
		else:
			if(self.selected_node_id == node_hit_id):
				self.selected_node_id = None
			self.delete_node(node_hit_id)

	def run_tsp(self):
		if len(self.graph.nodes) < 2:
			messagebox.showerror('Error', 'Add at least two nodes to run TSP.')
			return

		# Placeholder for TSP algorithm
		messagebox.showinfo('TSP', 'TSP algorithm not implemented yet.')

	def clear_graph(self):
		self.graph.clear()
		self.adjacency_matrix = None
		self.selected_node_id = None
		self.node_id_counter = 0
		self.canvas.delete('all')

	def redraw(self):
		self.canvas.delete('all')
		for edge in self.graph.edges:
			if len(edge) == 2:
				x1, y1 = self.graph.nodes[edge[0]]['pos']
				x2, y2 = self.graph.nodes[edge[1]]['pos']
				self.canvas.create_line(x1, y1, x2, y2, fill='black')


		for _, node in self.graph.nodes.items():
			self.canvas.create_oval(node['x']-NODE_RADIUS, node['y']-NODE_RADIUS, node['x']+NODE_RADIUS, node['y']+NODE_RADIUS, fill= node['color'])
			self.canvas.create_text(node['x'], node['y'], text=str(node['id']), fill='black')

		if(self.selected_node_id != None):
			node= self.graph.nodes[self.selected_node_id]
			self.canvas.create_oval(node['x']-NODE_RADIUS, node['y']-NODE_RADIUS, node['x']+NODE_RADIUS, node['y']+NODE_RADIUS, fill= 'grey')


if __name__ == '__main__':
	root = tk.Tk()
	app = GraphApp(root)
	root.mainloop()