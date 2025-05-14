import numpy as np
import heapq

class Node:
	def __init__(self, city, path, cost):
		self.city = city
		self.path = path
		self.cost = cost

	def __lt__(self, other):
		return self.cost<other.cost

def euclidean_distance(point1, point2):
	return np.sqrt((point1.x-point2.x)**2+(point1.y-point2.y)**2)

def heuristic(current_city, unvisited, points):
	# Example heuristic: minimum distance to the nearest unvisited city
	return min(euclidean_distance(points[current_city], points[city]) for city in unvisited)

def a_star_tsp(points, start_city):
	num_cities= len(points)
	initial_path= [start_city]
	initial_cost= 0
	priority_queue= []
	heapq.heappush(priority_queue, Node(start_city, initial_path, initial_cost))

	best_cost= float('inf')
	best_path= None

	while priority_queue:
		current_node = heapq.heappop(priority_queue)
		current_city = current_node.city
		current_path = current_node.path
		current_cost = current_node.cost

		if len(current_path) == num_cities:
			# Complete tour, return to start
			total_cost = current_cost + euclidean_distance(points[current_city], points[start_city])
			if total_cost < best_cost:
				best_cost = total_cost
				best_path = current_path + [start_city]
			continue

		unvisited = set(range(num_cities)) - set(current_path)

		for next_city in unvisited:
			new_cost = current_cost + euclidean_distance(points[current_city], points[next_city])
			h = heuristic(next_city, unvisited, points)
			total_cost = new_cost + h
			new_path = current_path + [next_city]
			heapq.heappush(priority_queue, Node(next_city, new_path, total_cost))

	return best_path, best_cost

def main():
	'''Example Usage of A-Star Search Algorithm'''
	points= [
		(0, 0), #city0
		(1, 2), #city1
		(2, 4), #city2
		(3, 1), #city3
		(4, 3), #city4
	]
	print(points)

	start_city= 0
	path, cost= a_star_tsp(points, start_city)
	
	print('Best path:', path)
	print('Best cost:', cost)

if __name__=='__main__':
	main()
