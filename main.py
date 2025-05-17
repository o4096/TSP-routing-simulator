from tkinter     import messagebox
from tkinter     import *
from tkinter.ttk import *
from util import *
import time, random
import numpy as np
import matplotlib.pyplot as plt

#Evolutionary Algorithms
from aco_system      import SystemACO
from aco_maxmin      import MaxMinACO
from aco_hybrid_ga   import HybridACO_GA, generate_children
from aco_hybrid_sa   import HybridACO_SA, simulated_annealing
from aco_distributed import DistributedACO
from tsp import TSP #for DistributedACO

# #Deterministic Algorithms (in case we need to validate optimal solution) (scrapped, focused more on bringing in more EA algorithms)
# from astar import a_star_tsp

ANIM_DISABLED= 'No Animation'
ANIM_BEST=     'Animate Best Ants'
ANIM_ALL=      'Animate All Ants (long)'

ALGO_ACO_SYSTEM=      'ACO System'
ALGO_ACO_MAXMIN=      'ACO MaxMin'
ALGO_ACO_HYBRID_GA=   'ACO Genetics'
ALGO_ACO_HYBRID_SA=   'ACO Simulated Annealing'
ALGO_ACO_DISTRIBUTED= 'ACO Distributed'
# ALGO_ACO_TIMED=       'ACO Timed'
# ALGO_ASTAR=           'A* Search (deterministic)'

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

class Ant:
	def __init__(self, cost=0.0, tour=None):
		self.cost= cost
		if tour==None: self.tour= []
		else:          self.tour= tour[:]

	def clear(self):
		self.cost= 0.0
		self.tour= []

class MainApp:
	def __init__(self, root:Tk):
		self.root= root
		self.root.title('Waste Point Collection (TSP) Solver')

		self.seed= time.time_ns()
		self.nodes= []
		self.anim_modes= [ANIM_DISABLED, ANIM_BEST, ANIM_ALL]
		self.algorithms= [
			ALGO_ACO_SYSTEM,
			ALGO_ACO_MAXMIN,
			ALGO_ACO_HYBRID_GA,
			ALGO_ACO_HYBRID_SA,
			ALGO_ACO_DISTRIBUTED,
			# ALGO_ACO_TIMED,
			# ALGO_ASTAR,
		]

		#Create UI components
		# self.style= Style()
		# self.style.theme_use('clam')
		# print(self.style.theme_names())

		#Variables
		self.var_animmode= StringVar(value=ANIM_BEST)

		#CONTRUCT MENUBAR
		mb=      Menu(root)
		# mb_file= Menu(mb, tearoff=0)
		mb_anim= Menu(mb, tearoff=0)
		mb_help= Menu(mb, tearoff=0)

		# mb_file.add_command(label='Open...', command=None)	#TODO: add extra feature that saves program state and config for convenience (scrapped due to tight project time)
		# mb_file.add_command(label='Save',    command=None);	mb_file.add_separator()
		# mb_file.add_command(label='Exit',    command=root.destroy)
		# mb.add_cascade(label='File', menu=mb_file)

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
		self.button_clear=             Button(self.frame_graphconfig, text='Clear Graph',    command=self.canvas_clear)
		self.button_rand_generation=   Button(self.frame_graphconfig, text='Generate Graph', command=self.btn_rand_graph)
		self.button_rand_point=        Button(self.frame_graphconfig, text='Random Point',   command=self.btn_rand_point)
		self.textbox_node=           IntEntry(self.frame_graphconfig, initvalue=50,        label='Nodes:')
		self.textbox_seed_gen=       IntEntry(self.frame_graphconfig, initvalue=self.seed, label='Seed:', includes_buttons=False, width=None)

		self.frame_algolist=        Frame(self.frame_ctrl)
		self.label_combobox_aco=    Label(self.frame_algolist, text='Algorithm:')
		self.combobox_aco=       Combobox(self.frame_algolist, state='readonly', values=self.algorithms)
		self.combobox_aco.set(value=self.algorithms[0])

		self.frame_params=            Frame(self.frame_ctrl)
		self.label_parameters=        Label(self.frame_params, text='Algorithm Parameters')
		self.textbox_seed_algo=    IntEntry(self.frame_params, initvalue=self.seed, label='Seed:', includes_buttons=False, width=None)
		self.textbox_iter=         IntEntry(self.frame_params, initvalue=30,        label='Iterations:')
		self.textbox_count_ants=   IntEntry(self.frame_params, initvalue=50,        label='Number of Ants:')
		self.textbox_ga_interval=  IntEntry(self.frame_params, initvalue=10,        label='Genetics Interval:')
		self.textbox_dis_colony=   IntEntry(self.frame_params, initvalue=4,         label='Number of Colonies:')
		self.textbox_dis_ants=     IntEntry(self.frame_params, initvalue=100,       label='Ants per Colony:')
		self.textbox_dis_xchgf=    IntEntry(self.frame_params, initvalue=10,        label='Exchange Frequency:')
		self.textbox_dis_maxiter=  IntEntry(self.frame_params, initvalue=100,       label='Max Iterations:')
		self.slider_alpha=           Slider(self.frame_params,     1,  0,    10, 'Pheromone influence (α)')
		self.slider_beta=            Slider(self.frame_params,     2,  0,    10, 'A priori influence (β)')
		self.slider_eva=             Slider(self.frame_params,   0.1,  0, 0.999, 'Pheromone Eva. Rate (ρ)')
		self.slider_q=               Slider(self.frame_params,   100, 50,   150, 'Pheromone Deposit (Q)')
		self.slider_sa_temp_alpha=   Slider(self.frame_params, 0.995,  0,     1, 'Cooling Rate (α)')
		self.slider_sa_temp_max=     Slider(self.frame_params,  1000,  0,  1000, 'Temperature Start')
		self.slider_sa_temp_min=     Slider(self.frame_params,     1,  0,  1000, 'Temperature End')
		self.combobox_dis_xchgs=   Combobox(self.frame_params, state='readonly', values=['random', 'best'])
		self.combobox_dis_xchgs.set('random')

		self.frame_run=     Frame(self.frame_ctrl)
		self.slider_delay= Slider(self.frame_run, 0, 0, 0.02, 'Animation Delay')
		self.button_run=   Button(self.frame_run, text='Run', command=self.run)

		#UI packing
		self.canvas.pack(side=RIGHT, expand=1)#TODO: find a way to resize all elements proportionally
		self.frame_ctrl.pack(fill=Y, padx=20)

		self.frame_graphconfig.pack(fill=Y, pady=20)
		self.button_clear.pack()
		self.button_rand_generation.pack()
		self.button_rand_point.pack()
		self.textbox_node.pack()
		self.textbox_seed_gen.pack()

		self.frame_algolist.pack()
		self.label_combobox_aco.pack()
		self.combobox_aco.pack()

		self.frame_run.pack(side=BOTTOM, anchor=S)
		self.slider_delay.pack()
		self.button_run.pack(side=BOTTOM, anchor=S)

		#Bindings
		self.canvas.bind('<Button-1>', self.mb_left)
		self.canvas.bind('<Button-3>', self.mb_right)
		self.combobox_aco.bind('<<ComboboxSelected>>', self.algo_selected)
		self.algo_selected()

	def algo_selected(self, event=None):
		selected= self.combobox_aco.get()
		for widget in self.frame_params.winfo_children():#clear current param widgets
			widget.pack_forget()

		def _show_aco_params(self):
			self.frame_params.pack(pady=10)
			self.label_parameters.pack()
			self.textbox_seed_algo.pack()
			self.textbox_iter.pack()
			self.textbox_count_ants.pack()
			self.slider_alpha.pack()
			self.slider_beta.pack()
			self.slider_eva.pack()
			self.slider_q.pack()

		if   selected==ALGO_ACO_HYBRID_GA:
			_show_aco_params(self)
			self.textbox_ga_interval.pack()
		elif selected==ALGO_ACO_SYSTEM or selected==ALGO_ACO_MAXMIN:
			_show_aco_params(self)
		elif selected==ALGO_ACO_HYBRID_SA:
			_show_aco_params(self)
			self.slider_sa_temp_alpha.pack()
			self.slider_sa_temp_max.pack()
			self.slider_sa_temp_min.pack()
		elif selected==ALGO_ACO_DISTRIBUTED:
			_show_aco_params(self)
			self.textbox_dis_colony.pack()
			self.textbox_dis_ants.pack()
			self.textbox_dis_xchgf.pack()
			self.combobox_dis_xchgs.pack()
			self.textbox_dis_maxiter.pack()

		# elif selected==ALGO_ASTAR: pass #no params
		else:
			print(f'[INFO]: No parameters available for {selected}')

	def rand_point(self):
		x_coord= random.randint(20, self.canvas.winfo_width() -40)
		y_coord= random.randint(20, self.canvas.winfo_height()-40)
		for i in range(len(self.nodes)):
			d = np.sqrt((x_coord-self.nodes[i].x)**2+(y_coord-self.nodes[i].y)**2)
			if d <= 10:
				x_coord= random.randint(20, self.canvas.winfo_width() -40)
				y_coord= random.randint(20, self.canvas.winfo_height()-40)
				i = 0
		return Node(x_coord, y_coord)

	def btn_rand_point(self):
		self.nodes.append(self.rand_point())
		self.canvas_redraw()

	def btn_rand_graph(self):
		self.seed= self.textbox_seed_gen.get()
		random.seed(self.seed)
		if len(self.nodes)!=0:
			self.canvas_clear()
		# self.nodes:list[Node]= [self.rand_point() for _ in range(self.textbox_node.get())]
		for _ in range((self.textbox_node.get())):
				# if _ == 285:
					# self.nodes.append(self.rand_point())
				self.nodes.append(self.rand_point())
		self.canvas_redraw()

	def mb_left(self, event=None):
		print(f"x={event.x} y={event.y}")
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

		self.button_clear.config(state='disabled')
		self.button_rand_generation.config(state='disabled')
		self.button_rand_point.config(state='disabled')
		
		history= []
		count_iter= self.textbox_iter.get()
		best_path= []
		best_cost= float('inf')
		t0= time.time()

		if   self.combobox_aco.get()==ALGO_ACO_HYBRID_GA:
			colony= HybridACO_GA(self.nodes,
				# lambda c1, c2: abs(c1.x-c2.x)+abs(c1.y-c2.y),		#l1_norm - Manhattan Distance
				lambda c1, c2: np.sqrt((c1.x-c2.x)**2+(c1.y-c2.y)**2),	#l2_norm - Euclidean Distance
				alpha=            self.slider_alpha.get(),
				beta=             self.slider_beta.get(),
				evaporation_rate= self.slider_eva.get(),
				Q=                self.slider_q.get(),
				num_ants=         self.textbox_count_ants.get(),
				seed=             self.textbox_seed_algo.get(),
			)
			ga_interval= self.textbox_ga_interval.get()
			loss= [0.0]*count_iter
			for iteration in range(count_iter):
				colony.update()
				if iteration%ga_interval==0 and iteration!=0:
					children_tours= generate_children(colony.get_best(10), num_children=10, mutation_rate=0.1)
					colony.replace_worst(children_tours)

				for ant in colony.ants:
					if best_cost>ant.cost:
						best_cost=ant.cost
						best_path=ant.tour
				
				history.append({
					'ants': [Ant(ant.cost, ant.tour) for ant in colony.ants],
					'best_tour': best_path,
					'best_cost': best_cost,
				})
				print(f'Iteration {iteration+1:2d}/{count_iter} - Best Distance: {best_cost}')
		
		elif self.combobox_aco.get()==ALGO_ACO_SYSTEM:
			colony= SystemACO(self.nodes,
				# lambda c1, c2: abs(c1.x-c2.x)+abs(c1.y-c2.y),		#l1_norm - Manhattan Distance
				lambda c1, c2: np.sqrt((c1.x-c2.x)**2+(c1.y-c2.y)**2),	#l2_norm - Euclidean Distance
				alpha=            self.slider_alpha.get(),
				beta=             self.slider_beta.get(),
				evaporation_rate= self.slider_eva.get(),
				Q=                self.slider_q.get(),
				num_ants=         self.textbox_count_ants.get(),
				seed=             self.textbox_seed_algo.get(),
			)
			loss=[0.0]*count_iter
			for iteration in range(count_iter):
				colony.update()
				for ant in colony.ants:
					if best_cost>ant.cost:
						best_cost=ant.cost
						best_path=ant.tour
				history.append({
					'ants': [Ant(ant.cost, ant.tour) for ant in colony.ants],
					'best_tour': best_path,
					'best_cost': best_cost,
				})
				print(f'Iteration {iteration+1:2d}/{count_iter} - Best Distance: {best_cost}')
			
		elif self.combobox_aco.get()==ALGO_ACO_MAXMIN:
			colony= MaxMinACO(self.nodes,
				# lambda c1, c2: abs(c1.x-c2.x)+abs(c1.y-c2.y),		#l1_norm - Manhattan Distance
				lambda c1, c2: np.sqrt((c1.x-c2.x)**2+(c1.y-c2.y)**2),	#l2_norm - Euclidean Distance
				alpha=            self.slider_alpha.get(),
				beta=             self.slider_beta.get(),
				evaporation_rate= self.slider_eva.get(),
				Q=                self.slider_q.get(),
				num_ants=         self.textbox_count_ants.get(),
				seed=             self.textbox_seed_algo.get(),
			)
			loss=[0.0]*count_iter
			for iteration in range(count_iter):
				colony.update()
				for ant in colony.ants:
					if best_cost>ant.cost:
						best_cost=ant.cost
						best_path=ant.tour
				history.append({
					'ants': [Ant(ant.cost, ant.tour) for ant in colony.ants],
					'best_tour': best_path,
					'best_cost': best_cost,
				})
				print(f'Iteration {iteration+1:2d}/{count_iter} - Best Distance: {best_cost}')
	
		elif self.combobox_aco.get()==ALGO_ACO_HYBRID_SA:
			if self.slider_sa_temp_max.get()<self.slider_sa_temp_min.get():
				messagebox.showerror('ERROR!', 'Minimum temperature must be less than maximum!')
				return

			colony= HybridACO_SA(self.nodes,
				# lambda c1, c2: abs(c1.x-c2.x)+abs(c1.y-c2.y),		#l1_norm - Manhattan Distance
				lambda c1, c2: np.sqrt((c1.x-c2.x)**2+(c1.y-c2.y)**2),	#l2_norm - Euclidean Distance
				alpha=            self.slider_alpha.get(),
				beta=             self.slider_beta.get(),
				evaporation_rate= self.slider_eva.get(),
				Q=                self.slider_q.get(),
				num_ants=         self.textbox_count_ants.get(),
				seed=             self.textbox_seed_algo.get(),
			)
			for iteration in range(count_iter):
				colony.update()
				for ant in colony.ants:
					if best_cost>ant.cost:
						best_cost=ant.cost
						best_path=ant.tour

				print(f'Iteration {iteration+1:2d}/{count_iter} - Best Distance: {best_cost}')
				new_path, new_cost= simulated_annealing(best_path, colony.cities, colony.objfunc,
				                                        T_start=self.slider_sa_temp_max.get(),
									T_end=  self.slider_sa_temp_min.get(),
									alpha=  self.slider_sa_temp_alpha.get(),
				)
				if new_cost<best_cost:#Refine best ant using Simulated Annealing
					best_path= new_path
					best_cost= new_cost
				
				history.append({
					'ants': [Ant(ant.cost, ant.tour) for ant in colony.ants],
					'best_tour': best_path,
					'best_cost': best_cost,
				})
		elif self.combobox_aco.get()==ALGO_ACO_DISTRIBUTED:
			tsp= TSP(len(self.nodes), self.canvas.winfo_width()-40, self.canvas.winfo_height()-40, self.textbox_seed_gen.get())
			solver= DistributedACO(tsp=tsp,
			                       num_colonies=      self.textbox_dis_colony.get(),
			                       ants_per_colony=   self.textbox_dis_ants.get(),
			                       alpha=             self.slider_alpha.get(),
			                       beta=              self.slider_beta.get(),
			                       rho=               self.slider_eva.get(),
			                       q=                 self.slider_q.get(),
			                       exchange_freq=     self.textbox_dis_xchgf.get(),
			                       exchange_strategy= self.combobox_dis_xchgs.get(),
			                       max_iterations=    self.textbox_dis_maxiter.get(),
			                       seed=              self.textbox_seed_algo.get(),
				)
			best_path= solver.solve()
			solver.plot_convergence()
			solver.plot_solution()
			print(best_path)
		# elif self.combobox_aco.get()==ALGO_ASTAR:
		# 	best_path, best_cost= a_star_tsp(self.nodes, 0)
		# 	dt= time.time()-t0
		# 	print(f'Optimal Distance: {best_cost}')
		# 	print(f'Algorithm Time Taken: {dt} seconds')
		# 	self.canvas.delete('all')
		# 	for i in range(len(best_path)-1):
		# 		idx1= best_path[i]
		# 		idx2= best_path[i+1]
		# 		self.canvas.create_line(self.nodes[idx1].x, self.nodes[idx1].y, self.nodes[idx2].x, self.nodes[idx2].y, fill='red', width=2)
		# 	self.canvas.create_line(self.nodes[best_path[-1]].x, self.nodes[best_path[-1]].y,
		# 				self.nodes[best_path[ 0]].x, self.nodes[best_path[ 0]].y, fill='red', width=2)
		# 	for node in self.nodes:
		# 		node.draw(self.canvas)
		# 	return
		else:
			messagebox.showerror('ERROR!', 'No implementation for algorithm')
		
		dt= time.time()-t0

		print(f'Best Tour: {[self.nodes[i].id for i in best_path]}')
		print(f'Best Distance: {best_cost} km')
		print(f'Algorithm Time Taken: {dt} seconds')
		print('Done\n')

		if self.var_animmode.get()!=ANIM_DISABLED:#ANIMATION SYSTEM
			# animation_delay= self.slider_delay.get()
			for iteration in history:
				lines = []
				prev_i = None
				if self.var_animmode.get()==ANIM_BEST:#BEST ANTS ONLY PER ITERATION
					# sorted_ants= sorted(iteration, key=lambda a: a.cost)
					# best_ant= sorted_ants[0]
					for i in iteration['best_tour']:
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
						time.sleep(self.slider_delay.get())#delay
						#clear for the next iteration
						for node in self.nodes:
							if node.color=='orange':
								node.color= 'white'
						self.canvas_redraw()
				elif self.var_animmode.get()==ANIM_ALL:#ALL ANTS
					for ant in iteration['ants']:
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
							time.sleep(self.slider_delay.get())
							#clear for the next iteration
							for node in self.nodes:
								if node.color=='orange':
									node.color= 'white'
							self.canvas_redraw()
		#DRAW RESULT
		self.canvas.delete('all')
		for i in range(len(best_path)-1):
			idx1= best_path[i]
			idx2= best_path[i+1]
			self.canvas.create_line(self.nodes[idx1].x, self.nodes[idx1].y, self.nodes[idx2].x, self.nodes[idx2].y, fill='red', width=2)
		self.canvas.create_line(self.nodes[best_path[-1]].x, self.nodes[best_path[-1]].y,
		                        self.nodes[best_path[ 0]].x, self.nodes[best_path[ 0]].y, fill='red', width=2)
		for node in self.nodes:
			node.draw(self.canvas)

		self.button_clear.config(state='enabled')
		self.button_rand_generation.config(state='enabled')
		self.button_rand_point.config(state='enabled')

		loss= [history[i]['best_cost'] for i in range(len(history))]
		plt.plot(range(count_iter), loss, 'b-')
		plt.title('Total Distance Over Iterations')
		plt.xlabel('Iteration')
		plt.ylabel('Total Distance')
		plt.tight_layout()
		plt.show()

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
