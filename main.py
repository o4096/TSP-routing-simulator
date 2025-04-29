# from   tkinter import messagebox, ttk
# import tkinter as tk
from tkinter     import *
from tkinter.ttk import *
import numpy as np
import time, random
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
		self.radius= 5

	def draw(self, canvas:Canvas):
		canvas.create_oval(self.x-self.radius, self.y-self.radius, self.x+self.radius, self.y+self.radius, fill=self.color)
		canvas.create_text(self.x,             self.y+self.radius*2.5, text=str(self.id), fill='black')

class MainApp:
	def __init__(self, root):
		self.root= root
		self.root.title('TSP Solver')

		# np.random.seed(time.localtime().tm_sec) #TODO: make this a seedable random number generator
		random.seed(42) #TODO
		self.nodes:list[Node]= [self.rand_point((0, 600), (5, 300)) for _ in range(20)]
		# self.lines:list[tuple[int, int]]= []

		# Create UI components
		self.style= Style()
		self.style.theme_use('clam')
		# print(self.style.theme_names())

		self.canvas= Canvas(root, width=600, height=400, bg='white')
		self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
		self.canvas.bind('<Button-1>', self.mb_left)
		self.canvas.bind('<Button-3>', self.mb_right)
		self.canvas.grid_rowconfigure(100)
		self.canvas.grid_columnconfigure(100)
		self.canvas.grid(column=10, row=10)
		
		print(self.canvas.grid_size())

		# self.control_frame= Frame(root)
		# self.control_frame.pack(side=RIGHT, fill=Y, padx=10)

		# self.button_run= Button(self.control_frame, text='Run', command=self.run)
		# self.button_run.pack(pady=10)
		# self.button_clear= Button(self.control_frame, text='Clear Graph', command=self.canvas_clear)
		# self.button_clear.pack(pady=10)
		# self.button_rand_point= Button(self.control_frame, text='Random Point', command=self.btn_rand_point)
		# self.button_rand_point.pack(pady=10)

		# self.textbox_seed_label= Label(self.control_frame, text='seed')
		# self.textbox_seed_label.pack()
		# self.textbox_seed= Entry(self.control_frame)
		# self.textbox_seed.pack(pady=10)
		self.canvas_redraw()
	
	def reseed(self):
		seed= self.textbox_seed.get()
		if seed.isdigit():
			random.seed(int(seed))
		else:
			# messagebox.showerror('Error', 'Seed must be a number.')
			return

	def rand_point(self, x_range, y_range):#TODO: make sure to get consistent results!
		x_coord= random.uniform(x_range[0], x_range[1])
		y_coord= random.uniform(y_range[0], y_range[1])
		return Node(x_coord, y_coord)
	
	def btn_rand_point(self):
		self.nodes.append(self.rand_point((0, 600), (5, 300)))
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
			return
		
		colony= HybridACO(self.nodes, #TODO: it'll probably be better to pass the graph inside the main loop
			# lambda c1, c2: abs(c1.x-c2.x)+abs(c1.y-c2.y),		#l1_norm - Manhattan Distance
			lambda c1, c2: np.sqrt((c1.x-c2.x)**2+(c1.y-c2.y)**2),	#l2_norm - Euclidean Distance
			seed=42,
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


		#animation system
		animation_delay = 0.05
		for ant in colony.ants:
			lines = []
			prev_i = None
			for i in ant.tour:
				#node
				self.nodes[i].color = 'orange'
				#edge
				if prev_i != None:
					lines.append({"x0":self.nodes[prev_i].x,"y0":self.nodes[prev_i].y,"x1":self.nodes[i].x,"y1":self.nodes[i].y})	
					#store node to be used as prev
				prev_i = i

				#redraw
				self.canvas.delete('all')
				for line in lines:
					self.canvas.create_line(line["x0"], line["y0"], line["x1"], line["y1"], fill='orange', width=2)
				for node in self.nodes:
					node.draw(self.canvas)
				self.canvas.update()
				
				#delay
				time.sleep(animation_delay)
			#clear for next ant tour
			for node in self.nodes:
				if node.color == "orange":
					node.color="white" 
			self.canvas_redraw()


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
		self.canvas.delete('all')
		self.nodes.clear()
		Node.obj_count= 0

	def canvas_redraw(self):
		self.canvas.delete('all')
		for node in self.nodes:
			node.draw(self.canvas)

def main():
	root= Tk()
	app= MainApp(root)
	root.mainloop()

if __name__=='__main__':
	main()
