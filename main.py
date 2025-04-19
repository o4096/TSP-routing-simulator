import  tkinter as tk
from    tkinter import messagebox
import  networkx as nx

class Node:
	obj_count= 0
	def __init__(self, id, x, y):
		Node.obj_count+= 1
		self.id=     Node.obj_count-1
		self.x=      x
		self.y=      y
		self.color=  'white'
		self.data=   None
		self.radius= 10

	def draw(self, canvas, color =None):
		canvas.create_oval(self.x-self.radius, self.y-self.radius, self.x+self.radius, self.y+self.radius, fill=color if color else self.color)
		canvas.create_text(self.x,             self.y, text=str(self.id), fill='black')

class MainApp:
	def __init__(self, root):
		self.root= root
		self.root.title('Graph Drawing and TSP Solver')
		self.selected_node= None
		self.inital_nodes= []
		
		# Initialize graph
		self.graph= nx.Graph()

		# Create UI components
		self.canvas= tk.Canvas(root, width=600, height=400, bg='white')
		self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		self.canvas.bind('<Button-1>', self.mb_left)
		self.canvas.bind('<Button-3>', self.mb_right)

		self.control_frame= tk.Frame(root)
		self.control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

		self.run_tsp_button= tk.Button(self.control_frame, text='Run TSP Algorithm', command=self.run)
		self.run_tsp_button.pack(pady=10)

		self.clear_button= tk.Button(self.control_frame, text='Clear Graph', command=self.canvas_clear)
		self.clear_button.pack(pady=10)


		self.input_weight_label= tk.Label(self.control_frame,text='weight')
		self.input_weight_label.pack()
		self.input_weight= tk.Entry(self.control_frame)
		self.input_weight.pack(pady=10)

	def mb_left(self, event):
		node_hit= self._get_mouse_collision(event.x, event.y)
		if node_hit:
			if not self.selected_node: # no selected nodes
				self.selected_node = node_hit
			elif self.selected_node == node_hit and node_hit not in self.inital_nodes: #add to inital nodes
				self.inital_nodes.append(node_hit)
			else:#link nodes
				if(self.weight_valid()):
					self.graph.add_edge(self.selected_node, node_hit, weight = int(self.input_weight.get()))
					print(nx.adjacency_matrix(self.graph,weight='weight'))
				else:
					messagebox.showerror('error','weight should be numbers!')
		else:
			self.graph.add_node(Node(len(self.graph.nodes), event.x, event.y))
		self.canvas_redraw()

	def mb_right(self, event):
		node_hit= self._get_mouse_collision(event.x, event.y)
		if node_hit:
			if node_hit is self.selected_node:
				self.selected_node= None
			else:
				self.inital_nodes.remove(node_hit)
				self.graph.remove_node(node_hit)
		else:
			self.selected_node= None
		self.canvas_redraw()

	def weight_valid(self):
		return self.input_weight.get().isdigit()

	def _get_mouse_collision(self, x, y):
		hit= None
		min_dist= float('inf')

		for node in self.graph.nodes():
			dist= abs(node.x-x)+abs(node.y-y)
			if dist<min_dist and dist<=node.radius:
				min_dist= dist
				hit= node
		return hit

	def run(self):
		if len(self.graph.nodes) < 2:
			messagebox.showerror('Error', 'Add at least two nodes to run TSP.')
			return
		
		messagebox.showinfo('TSP', 'Algorithm not implemented yet.')#TODO: Implement TSP algorithm

	def canvas_clear(self):
		Node.obj_count = 0
		self.selected_node = None
		self.inital_nodes = []
		self.canvas.delete('all')
		self.graph.clear()

	def canvas_redraw(self):
		self.canvas.delete('all')
		for edge in self.graph.edges:	#draw edges
			n1, n2= edge
			self.canvas.create_line(n1.x, n1.y, n2.x, n2.y, fill='black')
			self.canvas.create_text((n1.x+n2.x)/2 - 5, (n1.y+n2.y)/2 - 5, text=str(self.graph.edges[n1,n2]['weight']))

		for node in self.graph.nodes:	#draw nodes
			node.draw(self.canvas, 'orange' if node in self.inital_nodes else None)

		# selection rendering is separate from all other node rendering to separate UI interaction from any graph animation
		if self.selected_node:		#if there's selected node, highlight it
			self.canvas.create_oval(self.selected_node.x-self.selected_node.radius, self.selected_node.y-self.selected_node.radius, #top left
			   			self.selected_node.x+self.selected_node.radius, self.selected_node.y+self.selected_node.radius, #bottom right
						outline='red', width=2, fill= 'orange' if (self.selected_node in self.inital_nodes) else 'grey')
			self.canvas.create_text(self.selected_node.x,             self.selected_node.y, text=str(self.selected_node.id), fill='black')

if __name__=='__main__':
	root= tk.Tk()
	app= MainApp(root)
	root.mainloop()
