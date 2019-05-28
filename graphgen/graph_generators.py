from graphgen import _helpers
from graphgen.analysis import edge_num_distr

import networkx as nx
import random
import numpy as np
import math

UNIFORM = -1
NORMAL = -2

def naive_random_graph(num_vertices, num_edges=UNIFORM, seed=None):
	"""
	Generate a random undirected graph in a naive way.
	First, a random number of edges is generated from a uniform or normal distribution (see below) if this one
	('num_edges') is not specified in parameter. Second, the list of all edges is generated, suffled and the 'num_edges'
	first edges are selected. Third, the adjacency matrix is created thanks to these edges and then the NetworkX graph.

	You can specify the number of edges ('num_edges') or choose to generate it from a uniform or normal distribution
	(with graph_generators.UNIFORM and graph_generators.NORMAL). The normal distribution will give better results
	because it fits with the real distribution of numbers of edges of all different graphs with 'num_vertices' vertices.

	:num_vertices: The number of desired vertices.
	:num_edges: The number of the desired edges. If 'num_edges' is set to graph_generators.UNIFORM, then the number of
		edges will be randomly generated from a uniform distribution. If it set to graph_generators.NORMAL, then this
		number will be generated from a normal distribution. The number of edges generated will be between 0 and
		n * (n - 1) / 2, where n is 'num_vertices'.
	:seed: The seed of the random generator for the reproducibility.
	:return: A random NetworkX graph.
	"""

	# Set the seed.
	if seed:
		random.seed(seed)

	# The maximum number of edges.
	edge_max_num = _helpers.compute_edge_max_num(num_vertices)

	if not(0 <= num_edges <= edge_max_num) and (num_edges != UNIFORM) and (num_edges != NORMAL):
		raise ValueError("Error: 'num_edges' must be between -1 and n * (n - 1) / 2, where n is the number of vertices "
			"('num_vertices').")

	# Generate the number of edges.
	if num_edges == UNIFORM:
		num_edges = generate_uniform_num_edges(num_vertices, seed=seed)
	elif num_edges == NORMAL:
		num_edges = generate_normal_num_edges(num_vertices, seed=seed)

	# The list of indexes of all edges.
	edge_indexes = list(range(edge_max_num))

	# Randomly select 'num_edges' edges.
	random.shuffle(edge_indexes)
	selected_edges = edge_indexes[:num_edges]

	# Create the adjacency matrix.
	adjacency_matrix = np.zeros((num_vertices, num_vertices), dtype=int)
	for edge_index in selected_edges:
		# 'edge_index' is an index of the upper triangle of the adjacency matrix
		# Get the coordinates from this index.
		# Source: https://gist.github.com/PhDP/2358809
		i = int(-0.5 + 0.5 * math.sqrt(1 + 8 * edge_index)) + 1
		j = int((i + 1) * (2 - i) / 2 + edge_index) - 1

		adjacency_matrix[i][j] = 1
		adjacency_matrix[j][i] = 1

	return nx.from_numpy_matrix(adjacency_matrix)

def gnm_random_graph(num_vertices, num_edges=UNIFORM, seed=None):
	"""
	Call the 'gnm_random_graph' function from NetworkX, except that this function generates a random number of edges
	from a uniform or normal distribution (see below) if this one ('num_edges') is not specified in parameter.

	You can specify the number of edges ('num_edges') or choose to generate it from a uniform or normal distribution
	(with graph_generators.UNIFORM and graph_generators.NORMAL). The normal distribution will give better results
	because it fits with the real distribution of numbers of edges of all different graphs with 'num_vertices' vertices.

	:num_vertices: The number of desired vertices.
	:num_edges: The number of the desired edges. If 'num_edges' is set to graph_generators.UNIFORM, then the number of
		edges will be randomly generated from a uniform distribution. If it set to graph_generators.NORMAL, then this
		number will be generated from a normal distribution. The number of edges generated will be between 0 and
		n * (n - 1) / 2, where n is 'num_vertices'.
	:seed: The seed of the random generator for the reproducibility.
	:return: A random NetworkX graph.
	"""

	# The maximum number of edges.
	edge_max_num = _helpers.compute_edge_max_num(num_vertices)

	if not(0 <= num_edges <= edge_max_num) and (num_edges != UNIFORM) and (num_edges != NORMAL):
		raise ValueError("Error: 'num_edges' must be between -1 and n * (n - 1) / 2, where n is the number of vertices "
			"('num_vertices').")

	# Generate the number of edges.
	if num_edges == UNIFORM:
		num_edges = generate_uniform_num_edges(num_vertices, seed=seed)
	elif num_edges == NORMAL:
		num_edges = generate_normal_num_edges(num_vertices, seed=seed)

	return nx.gnm_random_graph(num_vertices, num_edges, seed=seed)

def generate_uniform_num_edges(num_vertices, seed=None):
	"""
	Generate a number of edges from a uniform distribution between 0 and the maximum number of edges.

	:num_vertices: The number of vertices.
	:seed: The seed of the random generator for the reproducibility.
	:return: The number of edges generated.
	"""

	# Set the seed.
	if seed:
		random.seed(seed)

	# The maximum number of edges.
	edge_max_num = _helpers.compute_edge_max_num(num_vertices)

	# Generate the number of edges.
	num_edges = random.randint(0, edge_max_num)

	return num_edges

def generate_normal_num_edges(num_vertices, seed=None):
	"""
	Generate a number of edges from a normal distribution between 0 and the maximum number of edges. The mean and the
	standard deviation of the normal distribution are automaticlly computed from the number of vertices (thanks to the
	distribution of numbers of edges of all different graphs with 'num_vertices' vertices).

	:num_vertices: The number of vertices.
	:seed: The seed of the random generator for the reproducibility.
	:return: The number of edges generated.
	"""

	# Compute the mean and standard deviation of numbers of edges of all graphs with 'num_vertices' vertices.
	mean = edge_num_distr.compute_mean(num_vertices)
	std = edge_num_distr.compute_std(num_vertices)

	# Set the seed.
	if seed:
		np.random.seed(seed)

	# The maximum number of edges.
	edge_max_num = _helpers.compute_edge_max_num(num_vertices)

	# Generate the number of edges.
	num_edges = round(np.random.normal(mean, std))

	if num_edges < 0:
		num_edges = 0
	elif num_edges > edge_max_num:
		num_edges = edge_max_num

	return num_edges

if __name__ == '__main__':
	import matplotlib.pyplot as plt

	# Parameters.
	num_vertices = 4
	seed = 42

	# Generate a graph.
	graph = naive_random_graph(num_vertices, seed=seed)

	nx.draw(graph)
	plt.show()
