# from   tkinter import messagebox, ttk
# import tkinter as tk
from tkinter     import *
from tkinter.ttk import *
from tkinter import messagebox
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
	def __init__(self, root: Tk):
		self.root= root
		self.root.title('TSP Solver')
		self.seed = time.time_ns()
		self.tsp = None
		self.nodes = []
		# Create UI components
		self.style= Style()
		# self.style.theme_use('clam')
		# print(self.style.theme_names())
		self.canvas= Canvas(root, width=600, height=400, bg='white')
		self.control_frame= Frame(root)
		self.button_run= Button(self.control_frame, text='Run', command=self.run)
		self.button_clear= Button(self.control_frame, text='Clear Graph', command=self.canvas_clear)
		self.button_rand_generation= Button(self.control_frame, text='Generate Graph', command=self.btn_rand_graph)
		self.button_rand_point= Button(self.control_frame, text='Random Point', command=self.btn_rand_point)
		
		
		self.textbox_seed_label= Label(self.control_frame, text='seed')
		self.seed_label_value = Variable(value=str(self.seed))
		self.textbox_seed= Entry(self.control_frame, textvariable=self.seed_label_value)
		
		self.textbox_node_label= Label(self.control_frame, text='inital number of nodes\n(may add more nodes after generation)', justify=CENTER)
		self.node_label_value = Variable(value=str(20))
		self.textbox_node= Entry(self.control_frame, textvariable=self.node_label_value)

		# self.textbox_num_ants_label= Label(self.control_frame, text='number of ants', justify=CENTER)
		# self.num_ants_label_value = Variable(value=str(50))
		# self.textbox_num_ants= Entry(self.control_frame, textvariable=self.num_ants_label_value)
		
		# self.textbox_alpha_label= Label(self.control_frame, text='alpha', justify=CENTER)
		# self.alpha_label_value = Variable(value=str(1.0))
		# self.textbox_alpha= Entry(self.control_frame, textvariable=self.alpha_label_value)

		# self.textbox_beta_label= Label(self.control_frame, text='beta', justify=CENTER)
		# self.beta_label_value = Variable(value=str(2.0))
		# self.textbox_beta= Entry(self.control_frame, textvariable=self.beta_label_value)
		
		# self.textbox_evap_rate_label= Label(self.control_frame, text='evaporation rate', justify=CENTER)
		# self.evap_rate_label_value = Variable(value=str(.1))
		# self.textbox_evap_rate= Entry(self.control_frame, textvariable=self.evap_rate_label_value)
		
		# self.textbox_q_label= Label(self.control_frame, text='Q', justify=CENTER)
		# self.q_label_value = Variable(value=str(100.0))
		# self.textbox_q= Entry(self.control_frame, textvariable=self.q_label_value)
		
		# self.textbox_pheromone_label= Label(self.control_frame, text='pheromones', justify=CENTER)
		# self.pheromone_label_value = Variable(value=str(1.0))
		# self.textbox_pheromone= Entry(self.control_frame, textvariable=self.pheromone_label_value)
		
		# self.textbox_iterations_label= Label(self.control_frame, text='iterations', justify=CENTER)
		# self.iterations_label_value = Variable(value=str(10))
		# self.textbox_iterations= Entry(self.control_frame, textvariable=self.iterations_label_value)
		
		# self.lines:list[tuple[int, int]]= []

		self.canvas.grid_rowconfigure(100)
		self.canvas.grid_columnconfigure(100)
		self.canvas.grid(column=10, row=10)
		print(self.canvas.grid_size())

		self.canvas.pack(side=LEFT)
		self.control_frame.pack(fill='y', padx=10)
		self.button_run.pack(pady=10)
		self.button_clear.pack(pady=10)
		self.button_rand_generation.pack(pady=10)
		self.button_rand_point.pack(pady=10)
		self.textbox_seed_label.pack()
		self.textbox_seed.pack(pady=10)
		self.textbox_node_label.pack()
		self.textbox_node.pack(pady=10)
		# self.textbox_num_ants_label.pack()
		# self.textbox_num_ants.pack(pady=10)
		# self.textbox_alpha_label.pack()
		# self.textbox_alpha.pack(pady=10)
		# self.textbox_beta_label.pack()
		# self.textbox_beta.pack(pady=10)
		# self.textbox_evap_rate_label.pack()
		# self.textbox_evap_rate.pack(pady=10)
		# self.textbox_q_label.pack()
		# self.textbox_q.pack(pady=10)
		# self.textbox_pheromone_label.pack()
		# self.textbox_pheromone.pack(pady=10)
		# self.textbox_iterations_label.pack()
		# self.textbox_iterations.pack(pady=10)


		self.canvas.bind('<Button-1>', self.mb_left)
		self.canvas.bind('<Button-3>', self.mb_right)
	
	def reseed(self):
		if self.seed_valid():
			self.seed = self.textbox_seed.get()
			random.seed(int(self.seed))
			return True
		return False

	def seed_valid(self):
		if not(self.textbox_seed.get().isdigit()):
			messagebox.showerror('Error', f'Seed must be a number.')
			return False
		return True

	def node_valid(self):
		if not(self.textbox_node.get().isdigit()):
			messagebox.showerror('Error', f'Node length must be a number.')
			return False
		return True

	# def parameters_valid(self):
		parameters = [(self.textbox_num_ants, self.textbox_num_ants_label),(self.textbox_alpha, self.textbox_alpha_label),
				(self.textbox_beta, self.textbox_beta_label),(self.textbox_evap_rate, self.textbox_evap_rate_label),
				(self.textbox_q, self.textbox_q_label),(self.textbox_pheromone, self.textbox_pheromone_label),
				(self.textbox_iterations, self.textbox_iterations_label)]
		valid = True
		for parameter, label in parameters:
			if not(parameter.get().isdigit() or parameter.get().isdecimal()):
				messagebox.showerror('Error',f'{label["text"]} should be a number!')
				valid = False
		return valid

	def rand_point(self, x_range, y_range):
		x_coord= random.uniform(x_range[0], x_range[1])
		y_coord= random.uniform(y_range[0], y_range[1])
		return Node(x_coord, y_coord)
	
	def btn_rand_point(self):
		# self.nodes.append(self.rand_point((self.canvas.winfo_x() + 20, self.canvas.winfo_width() - 20),
		# 							 (self.canvas.winfo_y() + 20, self.canvas.winfo_height() - 20)))
		
		self.nodes = self.tsp.get_cities()
		self.canvas_redraw()

	def btn_rand_graph(self):
		if self.reseed() and self.node_valid():
			if len(self.nodes) != 0:
				self.canvas_clear()

			self.nodes:list[Node]= [self.rand_point([self.canvas.winfo_x() + 20, self.canvas.winfo_width() - 20],
										[self.canvas.winfo_y() + 20, self.canvas.winfo_height() - 20]) for _ in range(int(self.textbox_node.get()))]
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

	def run(self, event = None):
		# if not(self.parameters_valid()):
		# 	return
		if len(self.nodes)<2:
			return
		
		colony= HybridACO(self.nodes, #TODO: it'll probably be better to pass the graph inside the main loop
			# lambda c1, c2: abs(c1.x-c2.x)+abs(c1.y-c2.y),		#l1_norm - Manhattan Distance
			lambda c1, c2: np.sqrt((c1.x-c2.x)**2+(c1.y-c2.y)**2),	#l2_norm - Euclidean Distance
			seed=self.seed,
		)

		# BEST ANT OF ALL ITERATIONS
		# ITERATIONS=	50
		# ga_interval=	1
		# loss= [0.0]*ITERATIONS
		# t0= time.time()
		# for iteration in range(ITERATIONS):
		# 	colony.update()
		# 	if iteration%ga_interval==0 and iteration!=0:
		# 		children_tours= generate_children(colony.get_best(10), num_children=10, mutation_rate=0.1)
		# 		colony.replace_worst(children_tours)
		# 	#animation system
		# 	best= colony.get_best()[0]
		# 	# best tour of each iteration
		# 	animation_delay = 0
		# 	lines = []
		# 	prev_i = None
		# 	for i in best.tour:
		# 		#node
		# 		self.nodes[i].color = 'orange'
		# 		#edge
		# 		if prev_i != None:
		# 			lines.append({"x0":self.nodes[prev_i].x,"y0":self.nodes[prev_i].y,"x1":self.nodes[i].x,"y1":self.nodes[i].y})	
		# 			#store node to be used as prev
		# 		prev_i = i
		# 		#redraw
		# 		self.canvas.delete('all')
		# 		for line in lines:
		# 			self.canvas.create_line(line["x0"], line["y0"], line["x1"], line["y1"], fill='orange', width=2)
		# 		for node in self.nodes:
		# 			node.draw(self.canvas)
		# 		self.canvas.update()		
		# 		#delay
		# 		time.sleep(animation_delay)
		# 	#clear for the next iteration
		# 	for node in self.nodes:
		# 		if node.color == "orange":
		# 			node.color="white" 
		# 	self.canvas_redraw()
		# 	print(f'Iteration {iteration+1:2d}/{ITERATIONS} - Best Distance: {best.cost}')
		# 	loss[iteration]= best.cost
		# dt= time.time()-t0
		
		# ALL ANTS OF FINAL ITERATION
		#old animation system
		# animation_delay = 0.05
		# for ant in colony.ants:
		# 	lines = []
		# 	prev_i = None
		# 	for i in ant.tour:
		# 		#node
		# 		self.nodes[i].color = 'orange'
		# 		#edge
		# 		if prev_i != None:
		# 			lines.append({"x0":self.nodes[prev_i].x,"y0":self.nodes[prev_i].y,"x1":self.nodes[i].x,"y1":self.nodes[i].y})	
		# 			#store node to be used as prev
		# 		prev_i = i
		# 		#redraw
		# 		self.canvas.delete('all')
		# 		for line in lines:
		# 			self.canvas.create_line(line["x0"], line["y0"], line["x1"], line["y1"], fill='orange', width=2)
		# 		for node in self.nodes:
		# 			node.draw(self.canvas)
		# 		self.canvas.update()
		# 		#delay
		# 		time.sleep(animation_delay)
		# 	#clear for next ant tour
		# 	for node in self.nodes:
		# 		if node.color == "orange":
		# 			node.color="white" 
		# 	self.canvas_redraw()

		# # ANTS OF EACH ITERATION
		# ITERATIONS=	10
		# ga_interval=	2
		# loss= [0.0]*ITERATIONS
		# t0= time.time()
		# for iteration in range(ITERATIONS):
		# 	colony.update()
		# 	if iteration%ga_interval==0 and iteration!=0:
		# 		children_tours= generate_children(colony.get_best(10), num_children=10, mutation_rate=0.1)
		# 		colony.replace_worst(children_tours)
		# 	#animation system
		# 	best= colony.get_best()[0]
		# 	# best tour of each iteration
		# 	animation_delay = 0
		# 	prev_i = None
		# 	for ant in colony.ants:
		# 		lines = []
		# 		for i in ant.tour:
		# 			#node
		# 			self.nodes[i].color = 'orange'
		# 			#edge
		# 			if prev_i != None:
		# 				lines.append({"x0":self.nodes[prev_i].x,"y0":self.nodes[prev_i].y,"x1":self.nodes[i].x,"y1":self.nodes[i].y})	
		# 				#store node to be used as prev
		# 			prev_i = i
		# 			#redraw
		# 			self.canvas.delete('all')
		# 			for line in lines:
		# 				self.canvas.create_line(line["x0"], line["y0"], line["x1"], line["y1"], fill='orange', width=2)
		# 			for node in self.nodes:
		# 				node.draw(self.canvas)
		# 			self.canvas.update()		
		# 			#delay
		# 			time.sleep(animation_delay)
		# 		#clear for the next iteration
		# 		for node in self.nodes:
		# 			if node.color == "orange":
		# 				node.color="white" 
		# 		self.canvas_redraw()
		# 	print(f'Iteration {iteration+1:2d}/{ITERATIONS} - Best Distance: {best.cost}')
		# 	loss[iteration]= best.cost
		# dt= time.time()-t0




		print(f'Best Tour: {[self.nodes[i].id for i in best.tour]}')
		print(f'Best Distance: {best.cost} km')
		print(f'Algorithm Time Taken: {dt} seconds')

		#REDRAW
		self.canvas.delete('all')
		for i in range(len(best.tour)-1):
			idx1 = best.tour[i]
			idx2 = best.tour[i+1]
			self.canvas.create_line(self.nodes[idx1].x, self.nodes[idx1].y, self.nodes[idx2].x, self.nodes[idx2].y, fill='red', width=2)
		self.canvas.create_line(self.nodes[best.tour[-1]].x, self.nodes[best.tour[-1]].y,
						   self.nodes[best.tour[0]].x, self.nodes[best.tour[0]].y, fill='red', width=2)
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
