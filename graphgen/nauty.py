from graphgen._settings import RESOURCE_PATH, TEMP_PATH
from graphgen import _helpers

from subprocess import call
import os.path
import networkx as nx
import numpy as np

# The path of the installation folder of Nauty.
NAUTY_PATH = os.path.join(RESOURCE_PATH, 'nauty')

# If True, the caches will be allowed.
USE_CACHE = True

def canonically_label(graphs, file_id=''):
	"""
	Canonically label a list of NetowrkX graphs.
	This function calls some Nauty programs and uses files to store the temporary results.

	:graphs: A generator or a list of NetworkX graphs.
	:file_id: The identifier of temporary files. For example, if it set to '1', then each temporary files will be
		followed by '1'. It is for example very useful if you use multiple threads or multiple processes; each one has
		its own 'file_id' and therefore, there will be no conflict with the temporary files.
	:return: A generator of canonically labeled graphs (in graph6 format).
	"""

	# Define the path of all temporary files.
	file_id = str(file_id)
	graph_file_path = os.path.join(TEMP_PATH, 'graphs{}.txt'.format(file_id))
	g6_graph_file_path = os.path.join(TEMP_PATH, 'graphs{}.g6'.format(file_id))
	canonized_graph_file_path = os.path.join(TEMP_PATH, 'canonized_graphs{}.g6'.format(file_id))

	# Write graphs in the 'adj_mat_graph_file_path' file.
	write_graphs(graphs, graph_file_path)

	# Convert to the graph6 format.
	adj_mat_to_graph6_file(graph_file_path, g6_graph_file_path)

	# Canonically label all graphs.
	canonically_label_file(g6_graph_file_path, canonized_graph_file_path)

	# Read canonized graphs in the 'canonized_graph_file_path' file.
	canonized_graphs = read_graph6_file(canonized_graph_file_path)

	return canonized_graphs

def generate_all_graphs(num_vertices, use_cache=USE_CACHE):
	"""
	Generate all the different graphs following the number of vertices. All returned graphs are canonically labeled.

	:num_vertices: The number of vertices.
	:use_cache: If True, a cache will be used for more performance.
	:return: A generator of all different graph (canonically labeled, so in graph6 format).
	"""

	# The file path.
	all_graphs_file_path = os.path.join(TEMP_PATH, 'all_graphs_n{}.g6'.format(num_vertices))

	if use_cache and os.path.isfile(all_graphs_file_path):
		# All graphs have already been computed before.
		pass
	else:
		# Generate all graphs with 'num_vertices' vertices.
		generate_all_graphs_file(num_vertices, all_graphs_file_path)

	# Read all graphs.
	all_graphs = read_graph6_file(all_graphs_file_path)

	return all_graphs

def num_graphs(num_vertices, use_cache=USE_CACHE):
	"""
	Compute the number of all the different graphs following the number of vertices.

	:num_vertices: The number of vertices.
	:use_cache: If True, a cache will be used for more performance.
	:return: The number of all the different graphs.
	"""

	# The file path.
	all_graphs_file_path = os.path.join(TEMP_PATH, 'all_graphs_n{}.g6'.format(num_vertices))

	if use_cache and os.path.isfile(all_graphs_file_path):
		# All graphs have already been computed before.
		pass
	else:
		# Generate all graphs with 'num_vertices' vertices.
		generate_all_graphs_file(num_vertices, all_graphs_file_path)

	# Read all graphs.
	all_graphs = read_graph6_file(all_graphs_file_path)

	# Count the number of different graphs.
	num_graphs = sum(1 for graph in all_graphs)

	return num_graphs

def write_graphs(graphs, file_path):
	"""
	Write a list of NetworkX graphs into a file. The adjacency matrix of each one is stored in order to be used by the
	Nauty program afterwards.

	:graphs: A generator or a list of NetworkX graphs.
	:file_path: The path of the file to create.
	"""

	# Write graphs in the 'file_path' file.
	with open(file_path, 'w') as file:
		for graph in graphs:
			num_vertices = len(graph)
			graph_str = _helpers.graph_to_str(graph)

			file.write('\n'.join(['n={}'.format(num_vertices), graph_str, '']))

def read_graph6_file(file_path):
	"""
	Read a file in graph6 format that contains graphs.

	:file_path: The file path.
	:return: A generator of graphs in graph6 format.
	"""

	return _helpers.read_text_file(file_path)

def read_adj_mat_file(file_path):
	"""
	Read a file storing graphs using the adjacency matrix representation.

	:file_path: The file path.
	:return: A generator of NetworkX graphs.
	"""

	# Read the file.
	lines = _helpers.read_text_file(file_path)

	# Retrieve the graphs.
	num_vertices = 0
	i_graph_creation = 0 # The number of iterations required before creating the graph.
	graph_rows = [] # It is the list of rows of the current adjacency matrix.
	for line in lines:
		if not line: # Skip if the line is empty.
			continue

		if line[0] == 'n': # If this line represents the number of vertices.
			# Get The number of vertices.
			num_vertices = int(line.partition('n')[2][1:])

			# A new graph is found. It is going to be create in 'num_vertices' lines.
			i_graph_creation = num_vertices
		elif i_graph_creation > 0: # If 'i_graph_creation > 0', then a graph is being processed.
			graph_rows.append(line)
			i_graph_creation -= 1

			if i_graph_creation == 0:
				# Process the current graph.

				# Compute the adjacency matrix.
				adjacency_matrix = np.empty((num_vertices, num_vertices), dtype=int)
				for i, row in enumerate(graph_rows):
					adjacency_matrix[i] = [int(element) for element in row]

				# Create the NetworkX graph.
				graph = nx.from_numpy_matrix(adjacency_matrix)

				# Yield the graph.
				yield graph

				# Clear 'graph_rows'.
				graph_rows = []

def adj_mat_to_graph6_file(input_file_path, output_file_path):
	"""
	Convert graphs using the adjacency matrix representation to graphs using the graph6 format. The first ones are
	stored in the 'input_file_path' file and the second ones in the 'output_file_path' file (created by this function).

	:input_file_path: The path of the input file containing graphs using the adjacency matrix representation.
	:output_file_path: The path of the output file containing graph using the graph6 format.
	"""

	amtog_path = os.path.join(NAUTY_PATH, 'amtog')
	call([amtog_path, '-q', input_file_path, output_file_path])

def graph6_to_adj_mat_file(input_file_path, output_file_path, file_id=''):
	"""
	Convert graphs using the graph6 format to graphs using the adjacency matrix representation. The first ones are
	stored in the 'input_file_path' file and the second ones in the 'output_file_path' file (created by this function).

	:input_file_path: The path of the input file containing graph using the graph6 format.
	:output_file_path: The path of the output file using the adjacency matrix representation.
	:file_id: The identifier of temporary files. For example, if it set to '1', then each temporary files will be
		followed by '1'. It is for example very useful if you use multiple threads or multiple processes; each one has
		its own 'file_id' and therefore, there will be no conflict with the temporary files.
	"""

	def adjust_resulting_file(file_path):
		"""
		Adjust the file resulting from the conversion. Each "Graph X, order Y." line is replaced by "n=Y".

		:file_path: The path of the file resulting from the conversion.
		:return: A generator of new adjusted lines of the output file.
		"""

		lines = _helpers.read_text_file(file_path)
		for i, line in enumerate(lines):
			if not line: # Skip if the line is empty.
				continue

			if line[0] == 'G': # If this line represents the number of vertices.
				# Get The number of vertices.
				num_vertices = int(float(line.partition('order')[2]))

				# Replace the line.
				line = 'n={}'.format(num_vertices)

			# Append a carriage return.
			line = ''.join([line, '\n'])

			yield line

	temp_file_path = os.path.join(TEMP_PATH, 'adj_mat_graphs{}.txt'.format(file_id))

	# Convert the graph6 file to the adjacency matrix file.
	showg_path = os.path.join(NAUTY_PATH, 'showg')
	call([showg_path, '-a', input_file_path, temp_file_path])

	# Adjust the file resulting from the conversion.
	new_lines = adjust_resulting_file(temp_file_path)

	# Write new adjusted lines into the 'output_file_path' file.
	with open(output_file_path, 'w') as file:
		file.write(''.join(new_lines))

def canonically_label_file(input_file_path, output_file_path):
	"""
	Canonically label a file (in graph6 format).

	:input_file_path: The path of the input file.
	:output_file_path: The path of the output file.
	"""

	labelg_path = os.path.join(NAUTY_PATH, 'labelg')
	call([labelg_path, '-qg', input_file_path, output_file_path])

def generate_all_graphs_file(num_vertices, file_path):
	"""
	Generate a file containing all the different graphs following the number of vertices. All graphs in this file are
	canonically labeled.

	:num_vertices: The number of vertices.
	:file_path: The path of the file to create.
	"""

	geng_path = os.path.join(NAUTY_PATH, 'geng')
	call([geng_path, '-ql', str(num_vertices), file_path])

if __name__ == '__main__':
	import networkx as nx
	import numpy as np

	graph1 = nx.from_numpy_matrix(np.array([
		[0, 1, 1, 0],
		[1, 0, 1, 0],
		[1, 1, 0, 0],
		[0, 0, 0, 0]
	]))

	graph2 = nx.from_numpy_matrix(np.array([
		[0, 0, 1, 1],
		[0, 0, 0, 0],
		[1, 0, 0, 1],
		[1, 0, 1, 0]
	]))

	graph3 = nx.from_numpy_matrix(np.array([
		[0, 0, 0, 0, 0],
		[0, 0, 0, 1, 1],
		[0, 0, 0, 0, 1],
		[0, 1, 0, 0, 1],
		[0, 1, 1, 1, 0]
	]))

	graphs = [graph1, graph2, graph3]

	canonized_graphs = canonically_label(graphs)

	print('\n'.join(canonized_graphs))
