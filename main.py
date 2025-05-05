# from   tkinter import messagebox, ttk
# import tkinter as tk
from tkinter     import *
from tkinter.ttk import *
from tkinter import messagebox
import numpy as np
import time, random
from aco_hybrid import HybridACO, generate_children
from aco import SystemACO
from aco_maxmin import MaxMinACO

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
		self.seed_label_value = IntVar(value=str(self.seed))
		self.textbox_seed= Entry(self.control_frame, textvariable=self.seed_label_value)
		
		self.textbox_node_label= Label(self.control_frame, text='inital number of nodes\n(may add more nodes after generation)', justify=CENTER)
		self.node_label_value = IntVar(value=str(20))
		self.textbox_node= Entry(self.control_frame, textvariable=self.node_label_value)

		

		# self.textbox_num_ants_label= Label(self.control_frame, text='number of ants', justify=CENTER)
		# self.num_ants_label_value = Variable(value=str(50))
		# self.textbox_num_ants= Entry(self.control_frame, textvariable=self.num_ants_label_value)
		
		self.combobox_aco_label = Label(self.control_frame, text= "ACO Algorithm:", justify=CENTER)
		self.combobox_aco = Combobox(self.control_frame, state='readonly',
								 values=["Hybrid ACO", "ACO"])
		self.combobox_aco.set(value="Hybrid ACO")
		
		self.combobox_animation_label = Label(self.control_frame, text= "Animation:", justify=CENTER)
		self.combobox_animation = Combobox(self.control_frame, state='readonly',
								 values=["Best Ants", "All Ants"])
		self.combobox_animation.set(value="Best Ants")

		self.textbox_iterations_label= Label(self.control_frame, text='Iterations', justify=CENTER)
		self.iterations_label_value = IntVar(value=str(10))
		self.textbox_iterations= Entry(self.control_frame, textvariable=self.iterations_label_value)
		
		self.delay_label_value = DoubleVar(value=0.000)
		self.scale_delay_label= Label(self.control_frame,
									   text=f'Animation Delay: {self.delay_label_value.get()}',
										 justify=CENTER)
		self.scale_delay= Scale(self.control_frame, variable=self.delay_label_value,
								from_= 0.000, to= 0.500, orient="horizontal")

		self.alpha_label_value = DoubleVar()
		self.scale_alpha_label= Label(self.control_frame,
									   text=f'Alpha: {self.alpha_label_value.get()}',
										 justify=CENTER)
		self.scale_alpha= Scale(self.control_frame, variable=self.alpha_label_value,
								from_= 0.0, to= 10.0, orient="horizontal")
		
		self.beta_label_value = DoubleVar()
		self.scale_beta_label= Label(self.control_frame,
									   text=f'Beta: {self.beta_label_value.get()}',
										 justify=CENTER)
		self.scale_beta= Scale(self.control_frame, variable=self.beta_label_value,
								from_= 0.0, to= 10.0, orient="horizontal")
		
		self.evap_rate_label_value = DoubleVar()
		self.scale_evap_rate_label= Label(self.control_frame,
									   text=f'Evaporation Rate: {self.evap_rate_label_value.get()}',
										 justify=CENTER)
		self.scale_evap_rate= Scale(self.control_frame, variable=self.evap_rate_label_value,
								from_= 0.00, to= 1.00, orient="horizontal")
		
		# self.textbox_q_label= Label(self.control_frame, text='Q', justify=CENTER)
		# self.q_label_value = Variable(value=str(100.0))
		# self.textbox_q= Entry(self.control_frame, textvariable=self.q_label_value)
		
		# self.textbox_pheromone_label= Label(self.control_frame, text='pheromones', justify=CENTER)
		# self.pheromone_label_value = Variable(value=str(1.0))
		# self.textbox_pheromone= Entry(self.control_frame, textvariable=self.pheromone_label_value)
		
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

		self.combobox_animation_label.pack()
		self.combobox_animation.pack(pady=10)
		
		self.combobox_aco_label.pack()
		self.combobox_aco.pack(pady=10)
		
		self.textbox_seed_label.pack()
		self.textbox_seed.pack(pady=10)
		self.textbox_node_label.pack()
		self.textbox_node.pack(pady=10)
		# self.textbox_num_ants_label.pack()
		# self.textbox_num_ants.pack(pady=10)
		self.textbox_iterations_label.pack()
		self.textbox_iterations.pack(pady=10)

		self.scale_delay_label.pack()
		self.scale_delay.pack(pady=10)
		self.scale_alpha_label.pack()
		self.scale_alpha.pack(pady=10)
		self.scale_beta_label.pack()
		self.scale_beta.pack(pady=10)
		self.scale_evap_rate_label.pack()
		self.scale_evap_rate.pack(pady=10)
		# self.textbox_q_label.pack()
		# self.textbox_q.pack(pady=10)
		# self.textbox_pheromone_label.pack()
		# self.textbox_pheromone.pack(pady=10)


		self.canvas.bind('<Button-1>', self.mb_left)
		self.canvas.bind('<Button-3>', self.mb_right)
		self.scale_evap_rate.bind('<B1-Motion>', self.show_slider)
		self.scale_alpha.bind('<B1-Motion>', self.show_slider)
		self.scale_beta.bind('<B1-Motion>', self.show_slider)
		self.scale_delay.bind('<B1-Motion>', self.show_slider)
	
	def reseed(self):
		if self.seed_valid():
			self.seed = self.textbox_seed.get()
			random.seed(int(self.seed))
			return True
		return False

	def show_slider(self, event):
		self.scale_evap_rate_label.config(text=f'Evaporation Rate: {self.evap_rate_label_value.get():.1f}')
		self.scale_alpha_label.config(text=f'Alpha: {self.alpha_label_value.get():.1f}')
		self.scale_beta_label.config(text=f'Beta: {self.beta_label_value.get():.1f}')
		self.scale_delay_label.config(text=f'Animation Delay: {self.delay_label_value.get():.3f}')

	def seed_valid(self):
		if (not self.textbox_seed.get().isdigit()) or self.seed_label_value.get() <= 0:
			messagebox.showerror('Error', f'Seed must be a proper number.')
			return False
		return True

	def node_valid(self):
		if (not self.textbox_node.get().isdigit()) or int(self.textbox_iterations.get()) <= 0:
			messagebox.showerror('Error', f'Node length must be a proper number.')
			return False
		return True

	def iterations_valid(self):
		if (not self.textbox_iterations.get().isdigit()) or int(self.textbox_iterations.get()) <= 0 :
			messagebox.showerror('Error',f'iterations should be a proper digit!')
			return False
		return True
	
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
		if len(self.nodes) < 2 or not(self.iterations_valid()) :
			return



		## choose aco algo type
		history = []
		ITERATIONS=	int(self.textbox_iterations.get())
		t0= time.time()
		if self.combobox_aco.get() == "Hybrid ACO":
			colony= HybridACO(self.nodes, #TODO: it'll probably be better to pass the graph inside the main loop
				# lambda c1, c2: abs(c1.x-c2.x)+abs(c1.y-c2.y),		#l1_norm - Manhattan Distance
				lambda c1, c2: np.sqrt((c1.x-c2.x)**2+(c1.y-c2.y)**2),	#l2_norm - Euclidean Distance
				seed=self.seed,
				alpha= self.alpha_label_value.get(),
				beta= self.beta_label_value.get(),
				evaporation_rate= self.evap_rate_label_value.get()
			)
			ga_interval=	2
			loss= [0.0]*ITERATIONS
			for iteration in range(ITERATIONS):
				colony.update()
				if iteration%ga_interval==0 and iteration!=0:
					children_tours= generate_children(colony.get_best(10), num_children=10, mutation_rate=0.1)
					colony.replace_worst(children_tours)
				best= colony.get_best()[0]
				history.append([ant for ant in colony.ants])
				print(f'Iteration {iteration+1:2d}/{ITERATIONS} - Best Distance: {best.cost}')
				loss[iteration]= best.cost

		elif self.combobox_aco.get() == "ACO":
			colony= SystemACO(self.nodes, #TODO: it'll probably be better to pass the graph inside the main loop
				# lambda c1, c2: abs(c1.x-c2.x)+abs(c1.y-c2.y),		#l1_norm - Manhattan Distance
				lambda c1, c2: np.sqrt((c1.x-c2.x)**2+(c1.y-c2.y)**2),	#l2_norm - Euclidean Distance
				seed=self.seed,
				alpha= self.alpha_label_value.get(),
				beta= self.beta_label_value.get(),
				evaporation_rate= self.evap_rate_label_value.get()
			)

			loss=[0.0]*ITERATIONS
			for iteration in range(ITERATIONS):
				colony.update()
				best= colony.get_best()[0]
				history.append([ant for ant in colony.ants])
				print(f'Iteration {iteration+1:2d}/{ITERATIONS} - Best Distance: {best.cost}')
				loss[iteration]= best.cost

		dt= time.time()-t0

		print(f'Best Tour: {[self.nodes[i].id for i in best.tour]}')
		print(f'Best Distance: {best.cost} km')
		print(f'Algorithm Time Taken: {dt} seconds')


		#animation system
		animation_delay = self.delay_label_value.get()
		for iteration in history:
			lines = []
			prev_i = None
			if self.combobox_animation.get() == "Best Ants":
				sorted_ants= sorted(iteration, key=lambda a: a.cost)
				best_ant= sorted_ants[0]
				for i in best_ant.tour:
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
					#clear for the next iteration
					for node in self.nodes:
						if node.color == "orange":
							node.color="white" 
					self.canvas_redraw()
			elif self.combobox_animation.get() == "All Ants":
				for ant in iteration:
					lines = []
					for i in ant.tour:
						#node
						self.nodes[i].color = 'orange'
						#edge
						if prev_i != None:
							lines.append({"x0":self.nodes[prev_i].x,"y0":self.nodes[prev_i].y,"x1":self.nodes[i].x,"y1":self.nodes[i].y})	
						#store node to be used as prev
						prev_i = i
						# redraw
						self.canvas.delete('all')
						for line in lines:
							self.canvas.create_line(line["x0"], line["y0"], line["x1"], line["y1"], fill="orange", width=2)
						for node in self.nodes:
							node.draw(self.canvas)
						self.canvas.update()		
						#delay
						time.sleep(animation_delay)
						#clear for the next iteration
						for node in self.nodes:
							if node.color == "orange":
								node.color="white" 
						self.canvas_redraw()


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
