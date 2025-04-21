from   tkinter import messagebox
import tkinter as tk
import numpy as np
import time
from aco_hybrid import HybridACO, generate_children

class Node:
	obj_count= 0
	def __init__(self, x, y):
		Node.obj_count+= 1
		self.id=     Node.obj_count
		self.x=      x
		self.y=      y
		self.color=  'white'
		# self.data=   None
		self.radius= 10

	def draw(self, canvas):
		canvas.create_oval(self.x-self.radius, self.y-self.radius, self.x+self.radius, self.y+self.radius, fill=self.color)
		canvas.create_text(self.x,             self.y, text=str(self.id), fill='black')

class MainApp:
	def __init__(self, root):
		self.root= root
		self.root.title('TSP Solver')

		np.random.seed(time.localtime().tm_sec) #TODO: make this a seedable random number generator
		self.nodes:list[Node]= self.rand_points(20, (0, 600), (0, 400))
		# self.lines:list[tuple[int, int]]= []

		# Create UI components
		self.canvas= tk.Canvas(root, width=600, height=400, bg='white')
		self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		self.canvas.bind('<Button-1>', self.mb_left)
		self.canvas.bind('<Button-3>', self.mb_right)

		self.control_frame= tk.Frame(root)
		self.control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

		self.button_run= tk.Button(self.control_frame, text='Run', command=self.run)
		self.button_run.pack(pady=10)
		self.button_clear= tk.Button(self.control_frame, text='Clear Graph', command=self.canvas_clear)
		self.button_clear.pack(pady=10)
		self.button_rand_point= tk.Button(self.control_frame, text='Random Point', command=self.rand_point)
		self.button_rand_point.pack(pady=10)

		self.textbox_seed_label= tk.Label(self.control_frame, text='seed')
		self.textbox_seed_label.pack()
		self.textbox_seed= tk.Entry(self.control_frame)
		self.textbox_seed.pack(pady=10)
		self.canvas_redraw()
	
	def reseed(self):
		seed= self.textbox_seed.get()
		if seed.isdigit():
			np.random.seed(int(seed))
		else:
			messagebox.showerror('Error', 'Seed must be a number.')
			return

	def rand_points(self, num_points, x_range, y_range):
		x_coords= np.random.uniform(x_range[0], x_range[1], num_points)
		y_coords= np.random.uniform(y_range[0], y_range[1], num_points)
		nodes= [Node(x, y) for x, y in zip(x_coords, y_coords)]
		return nodes

	def rand_point(self):#TODO: make a seeded node generation system for consistent results
		x= np.random.randint(0, self.canvas.winfo_width())
		y= np.random.randint(0, self.canvas.winfo_height())
		self.nodes.append(Node(x, y))
		self.canvas_redraw()

	def mb_left(self, event):
		node_hit= self._get_mouse_collision(event.x, event.y)
		if not node_hit:
			self.nodes.append(Node(event.x, event.y))
		self.canvas_redraw()

	def mb_right(self, event):
		node_hit= self._get_mouse_collision(event.x, event.y)
		if node_hit:
			self.nodes.remove(node_hit)
		self.canvas_redraw()

	def _get_mouse_collision(self, x, y):
		hit= None
		min_dist= float('inf')

		for node in self.nodes:
			dist= np.sqrt((node.x-x)**2+(node.y-y)**2)
			if dist<min_dist and dist<=node.radius*2:
				min_dist= dist
				hit= node
		return hit

	def run(self):
		if len(self.nodes)<2:
			messagebox.showerror('Error', 'Add at least two nodes to run TSP.')
			return
		
		colony= HybridACO(self.nodes, #TODO: it'll probably be better to pass the graph inside the main loop
			# lambda c1, c2: abs(c1.x-c2.x)+abs(c1.y-c2.y),		#l1_norm - Manhattan Distance
			lambda c1, c2: np.sqrt((c1.x-c2.x)**2+(c1.y-c2.y)**2),	#l2_norm - Euclidean Distance
		)

		ITERATIONS=	10
		ga_interval=	10
		loss= [0.0]*ITERATIONS
		t0= time.time()
		for iteration in range(ITERATIONS):
			colony.update()

			if iteration%ga_interval==0 and iteration!=0:
				children_tours= generate_children(colony.get_best(10), num_children=10, mutation_rate=0.1)
				colony.replace_worst(children_tours)
			
			#TODO: intuitive animation system

			best= colony.get_best()[0]
			print(f'Iteration {iteration+1:2d}/{ITERATIONS} - Best Distance: {best.cost}')
			loss[iteration]= best.cost

		dt= time.time()-t0

		best= colony.get_best()[0]
		print(f'Best Tour: {[self.nodes[i].id for i in range(len(best.tour))]}')
		print(f'Best Distance: {best.cost} km')
		print(f'Algorithm Time Taken: {dt} seconds')

		#REDRAW
		self.canvas.delete('all')
		for i in range(len(best.tour)-1):
			self.canvas.create_line(self.nodes[i].x, self.nodes[i].y, self.nodes[i+1].x, self.nodes[i+1].y, fill='red', width=2)
		for node in self.nodes:
			node.draw(self.canvas)

	def canvas_clear(self):
		Node.obj_count = 0
		self.canvas.delete('all')
		self.nodes.clear()

	def canvas_redraw(self):
		self.canvas.delete('all')
		for node in self.nodes:
			node.draw(self.canvas)

def main():
	root= tk.Tk()
	app= MainApp(root)
	root.mainloop()

if __name__=='__main__':
	main()
