import networkx as nx
import numpy as np
import math

def to_adjacency_matrix(graph):
	"""
	Convert a NetworkX graph to a adjacency matrix.

	:graph: The NetworkX graph.
	:return: The adjacency matrix as a Numpy matrix.
	"""

	return nx.adjacency_matrix(graph).todense().astype(int)

def graph6_to_networkx(graph):
	"""
	Convert a graph6 graph to a NetworkX graph.

	:graph: The graph6 graph.
	:return: The corresponding NetworkX graph.
	"""

	return nx.from_graph6_bytes(str.encode(graph))

def graph_to_str(graph):
	"""
	Convert a NetworkX graph to a string. This one represents its adjacency matrix.

	:graph: The NetworkX graph.
	:return: The string of the graph.
	"""

	adjacency_matrix = np.array(to_adjacency_matrix(graph))

	graph_row_str = []
	for row in adjacency_matrix:
		graph_row_str.append(''.join(map(str, row)))
	graph_str = '\n'.join(graph_row_str)

	return graph_str

def generate_graphs(num_graphs, graph_gen, gen_args, gen_kwargs={}):
	"""
	Generate several graphs.

	:num_graphs: The number of graphs to generate.
	:graph_gen: The generator of graphs (a Python function).
	:gen_args: The list of requiered arguments to send to the graph generator.
	:gen_kwargs: The dictionary of optional arguments to send to the graph generator. For each entry (key, value)
		of this dictionary, the key is the parameter name and the value is the value to set to this parameter.
	:return: A generator of generated graphs.
	"""

	for i in range(num_graphs):
		graph = graph_gen(*gen_args, **gen_kwargs)

		yield graph

def counter_to_list(counter):
	"""
	Convert a Counter object to a list of elements. For each entry (element, count), the element 'element' is added
	'count' times to the list.

	:counter: The Counter object.
	:return: The list of elements.
	"""

	return list(counter.elements())

def compute_mean_std_dict(dictionary):
	"""
	Compute the mean and the standard deviation of a "weighted" dictionary (as a Counter object). It actually computes
	the weighted mean and the weighted standard deviation: the keys of dictionary are considered as values and the
	values of dictionary as weights.

	:dictionary: A "weighted" dictionary where the keys and the values are integers. The keys are considered as values
		and the values a weihgts.
	:return: The weighted mean and the weighted standard deviation of the dictionary.
	"""

	# Convert the keys and the values to Numpy arrays.
	values = np.array(list(dictionary.keys()))
	weights = np.array(list(dictionary.values()))

	# Compute the weighted mean.
	weighted_mean = np.average(values, weights=weights)

	# Computed the weighted standard deviation.
	weighted_std = math.sqrt(np.average((values - weighted_mean)**2, weights=weights))

	return weighted_mean, weighted_std

def compute_edge_max_num(num_vertices):
	"""
	Compute the maximum possible number of edges for a undirected graph (in the upper triangle of the adjacency matrix).

	:num_vertices: The number of vertices.
	:return: The maximum possible number of edges.
	"""

	edge_max_num = int(num_vertices * (num_vertices - 1) / 2)

	return edge_max_num

def draw_hist(counts, title='', xlabel='', ylabel='', legend_label=''):
	"""
	Draw a histogram with Matplotlib.

	:counts: The counts (the distribution table). It is a dictionary where, for each entry (key,
		value), the key is a graph (in graph6 format) and the value is the count of this graph. Make sure to generate
		enough graphs to get good results.
	:title: The title of the histogram.
	:xlabel: The label text for the abscissa axis.
	:ylabel: The label text for the ordinate axis.
	:legend_label: The label of the histogram for the legend.
	"""

	import matplotlib.pyplot as plt

	opacity = 1
	color = '#FED487'
	edge_color = 'black'

	x_pos = range(len(counts))
	plt.bar(x_pos, counts.values(), align='center', color=color, edgecolor=edge_color, alpha=opacity,
		label=legend_label)
	plt.xticks(x_pos, counts.keys())
	plt.title(title)
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	plt.tight_layout()

def read_text_file(file_path):
	"""
	Read a text file.

	:file_path: The file path.
	:return: A generator of each line of the text file.
	"""

	with open(file_path) as file:
		for line in file.readlines():
			yield line.rstrip('\n')

if __name__ == '__main__':
	graph = nx.gnp_random_graph(4, 0.5)

	adjacency_matrix = to_adjacency_matrix(graph)
	print(adjacency_matrix)

	graph_str = graph_to_str(graph)
	print(graph_str)
