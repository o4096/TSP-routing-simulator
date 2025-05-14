from tkinter     import messagebox
from tkinter     import *
from tkinter.ttk import *
from util import *
import time, random
import numpy as np

#Evolutionary Algorithms
from aco           import SystemACO
from aco_maxmin    import MaxMinACO
from aco_hybrid_ga import HybridACO_GA, generate_children
from ACO_hybrid_SA import HybridACO_SA, simulated_annealing

#Deterministic Algorithms (in case we need to validate optimal solution)
from astar import a_star_tsp

class Node:
	obj_count= 0
	def __init__(self, x, y):
		Node.obj_count+= 1
		self.id=     Node.obj_count
		self.x=      x
		self.y=      y
		self.radius= 5
		self.color=  'white'

	def draw(self, canvas:Canvas):
		canvas.create_oval(self.x-self.radius, self.y-self.radius, self.x+self.radius, self.y+self.radius, fill=self.color)
		canvas.create_text(self.x,             self.y+self.radius*2.5, text=str(self.id), fill='black')

class MainApp:
	def __init__(self, root:Tk):
		self.root= root
		self.root.title('Waste Point Collection (TSP) Solver')

		self.seed= time.time_ns()
		self.nodes= []
		self.anim_modes= ['No Animation', 'Best Ants Only', 'All Ants (long)']
		self.algorithms= ['Genetic', 'System', 'MaxMin', 'Simulated Annealing', 'A*']

		#Create UI components
		# self.style= Style()
		# self.style.theme_use('clam')
		# print(self.style.theme_names())

		#Variables
		self.var_animmode= StringVar(value=self.anim_modes[1])

		#CONTRUCT MENUBAR
		mb=      Menu(root)
		mb_file= Menu(mb, tearoff=0)
		mb_anim= Menu(mb, tearoff=0)
		mb_help= Menu(mb, tearoff=0)
		
		mb_file.add_command(label='Open...', command=None)
		mb_file.add_command(label='Save',    command=None);	mb_file.add_separator()
		mb_file.add_command(label='Exit',    command=root.destroy)
		mb.add_cascade(label='File', menu=mb_file) 
		
		for anim in self.anim_modes:
			mb_anim.add_radiobutton(label=anim, variable=self.var_animmode, value=anim)
		mb.add_cascade(label='Animation', menu=mb_anim)
		
		mb_help.add_command(label='About', command=lambda:messagebox.showinfo('About', 'Evolutionary Algorithms Project\nHelwan University 2025'))
		mb.add_cascade(label='Help', menu=mb_help)
		root.config(menu=mb)

		#UI Objects
		self.canvas=     Canvas(self.root, width=800, height=600, bg='white')
		self.frame_ctrl=  Frame(self.root)#control panel

		self.frame_graphconfig=         Frame(self.frame_ctrl)
		self.button_clear=             Button(self.frame_graphconfig, text='Clear Graph',  command=self.canvas_clear)
		self.button_rand_generation=   Button(self.frame_graphconfig, text='Random Graph', command=self.btn_rand_graph)
		self.button_rand_point=        Button(self.frame_graphconfig, text='Random Point', command=self.btn_rand_point)
		self.textbox_node=           IntEntry(self.frame_graphconfig, initvalue=10,        label='Nodes:')
		self.textbox_seed=           IntEntry(self.frame_graphconfig, initvalue=self.seed, label='Seed:', includes_buttons=False, width=None)

		self.frame_algolist=        Frame(self.frame_ctrl)
		self.label_combobox_aco=    Label(self.frame_algolist, text='Algorithm:')
		self.combobox_aco=       Combobox(self.frame_algolist, state='readonly', values=self.algorithms)
		self.combobox_aco.set(value=self.algorithms[0])

		self.frame_params=            Frame(self.frame_ctrl)
		self.label_parameters=        Label(self.frame_params, text='Algorithm Parameters')
		self.textbox_iter=         IntEntry(self.frame_params, initvalue=30, label='Iterations:')
		self.textbox_count_ants=   IntEntry(self.frame_params, initvalue=50, label='Number of Ants:')
		self.slider_alpha=           Slider(self.frame_params,     1, 0,   10, 'Pheromone influence (α)')
		self.slider_beta=            Slider(self.frame_params,     2, 0,   10, 'A priori influence (β)')
		self.slider_eva=             Slider(self.frame_params,   0.1, 0,    1, 'Pheromone Eva. Rate (ρ)')
		self.slider_sa_temp_alpha=   Slider(self.frame_params, 0.995, 0,    1, 'Temperature Alpha')
		self.slider_sa_temp_max=     Slider(self.frame_params,  1000, 0, 1000, 'Temperature Max')
		self.slider_sa_temp_min=     Slider(self.frame_params,     1, 0, 1000, 'Temperature Min')

		self.frame_run=     Frame(self.frame_ctrl)
		self.slider_delay= Slider(self.frame_run, 0, 0, 1, 'Animation Delay')
		self.button_run=   Button(self.frame_run, text='Run', command=self.run)
		
		#UI packing
		self.canvas.pack(side=RIGHT, expand=1)#TODO: find a way to resize all elements proportionally
		self.frame_ctrl.pack(fill=Y, padx=20)

		self.frame_graphconfig.pack(fill=Y, pady=20)
		self.button_clear.pack()
		self.button_rand_generation.pack()
		self.button_rand_point.pack()
		self.textbox_node.pack()
		self.textbox_seed.pack()

		self.frame_algolist.pack()
		self.label_combobox_aco.pack()
		self.combobox_aco.pack()

		self.frame_run.pack(side=BOTTOM, anchor=S)
		self.slider_delay.pack()
		self.button_run.pack(side=BOTTOM, anchor=S)

		#Bindings
		self.canvas.bind('<Button-1>', self.mb_left)
		self.canvas.bind('<Button-3>', self.mb_right)
		self.combobox_aco.bind("<<ComboboxSelected>>", self.algo_selected)
		self.algo_selected()
	
	def algo_selected(self, event=None):
		selected= self.combobox_aco.get()
		for widget in self.frame_params.winfo_children():#clear current param widgets
			widget.pack_forget()

		if   selected==self.algorithms[0]:#ACO w/Genetic Algorithms
			#TODO might separate algorithm seed from graph generation
			self.frame_params.pack(pady=10)
			self.label_parameters.pack()
			self.textbox_iter.pack()
			self.textbox_count_ants.pack()
			self.slider_alpha.pack()
			self.slider_beta.pack()
			self.slider_eva.pack()
			#TODO: ga_interval
		elif selected==self.algorithms[1]:#ACO system
			self.frame_params.pack(pady=10)
			self.label_parameters.pack()
			self.textbox_iter.pack()
			self.textbox_count_ants.pack()
			self.slider_alpha.pack()
			self.slider_beta.pack()
			self.slider_eva.pack()
		elif selected==self.algorithms[2]:#ACO w/MaxMin
			self.frame_params.pack(pady=10)
			self.label_parameters.pack()
			self.textbox_iter.pack()
			self.textbox_count_ants.pack()
			self.slider_alpha.pack()
			self.slider_beta.pack()
			self.slider_eva.pack()
			#TODO: add tau_max, tau_min
		elif selected==self.algorithms[3]:#ACO w/Simulated Annealing
			self.frame_params.pack(pady=10)
			self.label_parameters.pack()
			self.textbox_iter.pack()
			self.textbox_count_ants.pack()
			self.slider_alpha.pack()
			self.slider_beta.pack()
			self.slider_eva.pack()
			self.slider_sa_temp_alpha.pack()
			self.slider_sa_temp_max.pack()
			self.slider_sa_temp_min.pack()
		elif selected==self.algorithms[4]: pass #no params
		else:
			print(f'[INFO]: No parameters available for {selected}')

	def rand_point(self):
		x_coord= random.randint(20, self.canvas.winfo_width() -40)
		y_coord= random.randint(20, self.canvas.winfo_height()-40)
		return Node(x_coord, y_coord)
	
	def btn_rand_point(self):
		self.nodes.append(self.rand_point())
		self.canvas_redraw()

	def btn_rand_graph(self):
		self.seed= self.textbox_seed.get()
		random.seed(self.seed)
		if len(self.nodes)!=0:
			self.canvas_clear()
		self.nodes:list[Node]= [self.rand_point() for _ in range(self.textbox_node.get())]
		self.canvas_redraw()

	def mb_left(self, event=None):
		node_hit= self._get_mouse_collision(event.x, event.y)
		if not node_hit:
			self.nodes.append(Node(event.x, event.y))
		self.canvas_redraw()

	def mb_right(self, event=None):
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

	def run(self, event=None):
		if len(self.nodes)<2:
			messagebox.showerror('ERROR', 'Nodes count must be 2 or more!')
			return

		history= []
		count_iter= self.textbox_iter.get()
		t0= time.time()

		if self.combobox_aco.get()=='Genetic':
			colony= HybridACO_GA(self.nodes, #TODO: it'll probably be better to pass the graph inside the main loop
				# lambda c1, c2: abs(c1.x-c2.x)+abs(c1.y-c2.y),		#l1_norm - Manhattan Distance
				lambda c1, c2: np.sqrt((c1.x-c2.x)**2+(c1.y-c2.y)**2),	#l2_norm - Euclidean Distance
				alpha=            self.slider_alpha.get(),
				beta=             self.slider_beta.get(),
				evaporation_rate= self.slider_eva.get(),
				num_ants=         self.textbox_count_ants.get(),
			)
			ga_interval= 2
			loss= [0.0]*count_iter
			for iteration in range(count_iter):
				colony.update()
				if iteration%ga_interval==0 and iteration!=0:
					children_tours= generate_children(colony.get_best(10), num_children=10, mutation_rate=0.1)
					colony.replace_worst(children_tours)
				best= colony.get_best()[0]
				history.append([ant for ant in colony.ants])
				print(f'Iteration {iteration+1:2d}/{count_iter} - Best Distance: {best.cost}')
				loss[iteration]= best.cost

		elif self.combobox_aco.get()=='System':
			colony= SystemACO(self.nodes, #TODO: it'll probably be better to pass the graph inside the main loop
				# lambda c1, c2: abs(c1.x-c2.x)+abs(c1.y-c2.y),		#l1_norm - Manhattan Distance
				lambda c1, c2: np.sqrt((c1.x-c2.x)**2+(c1.y-c2.y)**2),	#l2_norm - Euclidean Distance
				alpha=            self.slider_alpha.get(),
				beta=             self.slider_beta.get(),
				evaporation_rate= self.slider_eva.get(),
				num_ants=         self.textbox_count_ants.get(),
			)
			loss=[0.0]*count_iter
			for iteration in range(count_iter):
				colony.update()
				best= colony.get_best()[0]
				history.append([ant for ant in colony.ants])
				print(f'Iteration {iteration+1:2d}/{count_iter} - Best Distance: {best.cost}')
				loss[iteration]= best.cost

		elif self.combobox_aco.get()=='MaxMin':
			colony= MaxMinACO(self.nodes, #TODO: it'll probably be better to pass the graph inside the main loop
				# lambda c1, c2: abs(c1.x-c2.x)+abs(c1.y-c2.y),		#l1_norm - Manhattan Distance
				lambda c1, c2: np.sqrt((c1.x-c2.x)**2+(c1.y-c2.y)**2),	#l2_norm - Euclidean Distance
				alpha=            self.slider_alpha.get(),
				beta=             self.slider_beta.get(),
				evaporation_rate= self.slider_eva.get(),
				num_ants=         self.textbox_count_ants.get(),
			)
			loss=[0.0]*count_iter
			for iteration in range(count_iter):
				colony.update()
				best= colony.get_best()[0]
				history.append([ant for ant in colony.ants])
				print(f'Iteration {iteration+1:2d}/{count_iter} - Best Distance: {best.cost}')
				loss[iteration]= best.cost

		elif self.combobox_aco.get()=='Simulated Annealing':
			if self.slider_sa_temp_max.get()<self.slider_sa_temp_min.get():
				messagebox.showerror('ERROR!', 'Minimum temperature must be less than maximum!')
				return

			colony= HybridACO_SA(self.nodes, #TODO: it'll probably be better to pass the graph inside the main loop
				# lambda c1, c2: abs(c1.x-c2.x)+abs(c1.y-c2.y),		#l1_norm - Manhattan Distance
				lambda c1, c2: np.sqrt((c1.x-c2.x)**2+(c1.y-c2.y)**2),	#l2_norm - Euclidean Distance
				alpha=            self.slider_alpha.get(),
				beta=             self.slider_beta.get(),
				evaporation_rate= self.slider_eva.get(),
				num_ants=         self.textbox_count_ants.get(),
			)
			for iteration in range(count_iter):
				colony.update()
				best= colony.get_best()[0]
				history.append([ant for ant in colony.ants])
				print(f'Iteration {iteration+1:2d}/{count_iter} - Best Distance: {best.cost}')
				new_tour, new_cost= simulated_annealing(best.tour, colony.cities, colony.objfunc,
				                                        T_start=self.slider_sa_temp_max.get(),
									T_end=  self.slider_sa_temp_min.get(),
									alpha=  self.slider_sa_temp_alpha.get(),
				)
				if new_cost<best.cost:#Refine best ant using Simulated Annealing
					best.tour= new_tour
					best.cost= new_cost
		elif self.combobox_aco.get()=='A*':
			start_city= 0
			best.tour, best.cost= a_star_tsp(self.nodes, start_city) #TODO: change result variables for better algorithms integration
		else:
			messagebox.showerror('ERROR!', 'No implementation for algorithm')
			return

		dt= time.time()-t0

		print(f'Best Tour: {[self.nodes[i].id for i in best.tour]}')
		print(f'Best Distance: {best.cost} km')
		print(f'Algorithm Time Taken: {dt} seconds')
		print('Done\n')

		if self.var_animmode.get()!=self.anim_modes[0]:#ANIMATION SYSTEM
			animation_delay= self.slider_delay.get()
			for iteration in history:
				lines = []
				prev_i = None
				if self.var_animmode.get()==self.anim_modes[1]:#BEST ANTS ONLY PER ITERATION
					sorted_ants= sorted(iteration, key=lambda a: a.cost)
					best_ant= sorted_ants[0]
					for i in best_ant.tour:
						#node
						self.nodes[i].color= 'orange'
						#edge
						if prev_i != None:
							lines.append({'x0':self.nodes[prev_i].x,'y0':self.nodes[prev_i].y,'x1':self.nodes[i].x,'y1':self.nodes[i].y})
							#store node to be used as prev
						prev_i = i
						#REDRAW
						self.canvas.delete('all')
						for line in lines:
							self.canvas.create_line(line['x0'], line['y0'], line['x1'], line['y1'], fill='orange', width=2)
						for node in self.nodes:
							node.draw(self.canvas)
						self.canvas.update()
						time.sleep(animation_delay)#delay
						#clear for the next iteration
						for node in self.nodes:
							if node.color=='orange':
								node.color= 'white'
						self.canvas_redraw()
				elif self.var_animmode.get()==self.anim_modes[2]:#ALL ANTS
					for ant in iteration:
						lines= []
						for i in ant.tour:
							#node
							self.nodes[i].color= 'orange'
							#edge
							if prev_i!=None:
								lines.append({'x0':self.nodes[prev_i].x,'y0':self.nodes[prev_i].y,'x1':self.nodes[i].x,'y1':self.nodes[i].y})	
							#store node to be used as prev
							prev_i= i
							# redraw
							self.canvas.delete('all')
							for line in lines:
								self.canvas.create_line(line['x0'], line['y0'], line['x1'], line['y1'], fill='orange', width=2)
							for node in self.nodes:
								node.draw(self.canvas)
							self.canvas.update()		
							#delay
							time.sleep(animation_delay)
							#clear for the next iteration
							for node in self.nodes:
								if node.color=='orange':
									node.color= 'white' 
							self.canvas_redraw()
		#DRAW RESULT
		self.canvas.delete('all')
		for i in range(len(best.tour)-1):
			idx1= best.tour[i]
			idx2= best.tour[i+1]
			self.canvas.create_line(self.nodes[idx1].x, self.nodes[idx1].y, self.nodes[idx2].x, self.nodes[idx2].y, fill='red', width=2)
		self.canvas.create_line(self.nodes[best.tour[-1]].x, self.nodes[best.tour[-1]].y,
		                        self.nodes[best.tour[ 0]].x, self.nodes[best.tour[ 0]].y, fill='red', width=2)
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
