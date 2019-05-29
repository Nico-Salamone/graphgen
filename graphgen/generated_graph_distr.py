from graphgen import nauty
from graphgen import _helpers

from collections import Counter, OrderedDict
from multiprocessing import cpu_count
from multiprocessing.pool import Pool
import random
import numpy as np

# The size of a chunck. Each one generate '_CHUNCK_SIZE' graphs, canonically label them and count the different graphs.
# It avoids that the temporary files use too much space disk. With '_CHUNCK_SIZE' sets to 1000000, they will take up
# about (3 + 'n' * 'n' + 'n') * 1000000 * 'p' bytes of space, where 'n' is the number of vertices and 'p' is
# 'num_processes', that is the number of processes created.
_CHUNCK_SIZE = 1000000

def generated_graph_distr(num_vertices, num_graphs, graph_gen, gen_args, gen_kwargs={}, is_deterministic=False,
	num_processes=cpu_count()):
	"""
	Compute the distribution of generated graphs by a graph generator. This function first generates some graphs with
	'num_vertices' vertices. Then, it canonically label each one. Next, it computes the counts af all canonically
	labeled graphs. Finally, it generate all different graphs and, for each graph, if it is in the counts, then
	(graph, 0) is added tothe counts.

	:num_vertices: The number of vertices of graphs to generate.
	:num_graphs: The number of graphs to generate.
	:graph_gen: The generator of graphs (a Python function).
	:gen_args: The list of requiered arguments to send to the graph generator.
	:gen_kwargs: The dictionary of optional arguments to send to the graph generator. For each entry (key, value)
		of this dictionary, the key is the parameter name and the value is the value to set to this parameter.
	:is_deterministic: If True, makes this function deterministic. Otherwise, it will not be deterministic.
	:num_processes: The number of processes to create. By default, it is set to 'n', where 'n' is the number of CPUs in
		the system.
	:return: The distribution of generated graphs by the generator. It is a Counter object (as a dictionary) where, for
		each entry (key, value), the key is a graph (in graph6 format) and and the value is its count.
	"""

	# Compute the counts of graphs.
	graph_counts = compute_graph_counts(num_graphs, graph_gen, gen_args, gen_kwargs=gen_kwargs,
		is_deterministic=is_deterministic, num_processes=num_processes)

	# For each graph that is not in 'graph_counts', add it with a value of 0.
	gen_graph_distr = graph_counts
	all_graphs = nauty.generate_all_graphs(num_vertices)
	for graph in all_graphs:
		gen_graph_distr[graph] = gen_graph_distr.get(graph, 0)

	return gen_graph_distr

def compute_graph_counts(num_graphs, graph_gen, gen_args, gen_kwargs={}, is_deterministic=False,
	num_processes=cpu_count()):
	"""
	Compute the counts of graphs from a graph generator. This function first generates some graphs. Then, it canonically
	label each one. Finally, it computes and returns the counts of all canonically labeled graphs.

	:num_graphs: The number of graphs to generate.
	:graph_gen: The generator of graphs (a Python function).
	:gen_args: The list of requiered arguments to send to the graph generator.
	:gen_kwargs: The dictionary of optional arguments to send to the graph generator. For each entry (key, value)
		of this dictionary, the key is the parameter name and the value is the value to set to this parameter.
	:is_deterministic: If True, makes this function deterministic. Otherwise, it will not be deterministic.
	:num_processes: The number of processes to create. By default, it is set to 'n', where 'n' is the number of CPUs in
		the system.
	:return: The graph counts. It is a Counter object (as a dictionary) where, for each entry (key, value), the key is
		a graph (in graph6 format) and and the value is its count.
	"""

	# Compute the graph counts.
	with Pool(processes=num_processes) as pool:
		# Run all processes.
		processes = []
		for i in range(num_processes):
			num_graphs_to_gen = int(num_graphs / num_processes)
			if i == 0:
				num_graphs_to_gen += (num_graphs % num_processes)

			process = pool.apply_async(_compute_graph_counts, (i, num_graphs_to_gen, graph_gen, gen_args, gen_kwargs,
				is_deterministic))
			processes.append(process)

		# Gather the results.
		graph_counts = Counter()
		for process in processes:
			graph_counts += process.get()

	return graph_counts

def _compute_graph_counts(process_id, num_graphs, graph_gen, gen_args, gen_kwargs={}, is_deterministic=False):
	"""
	Compute the counts of graphs from a graph generator. This function first generates some graphs. Then, it
	canonically label each one. Finally, it computes and returns the counts of all canonically labeled graphs.

	:process_id: The identifier of the process (used for the temporary files).
	:num_graphs: The number of graphs to generate.
	:graph_gen: The generator of graphs (a Python function).
	:gen_args: The list of requiered arguments to send to the graph generator.
	:gen_kwargs: The dictionary of optional arguments to send to the graph generator. For each entry (key, value)
		of this dictionary, the key is the parameter name and the value is the value to set to this parameter.
	:is_deterministic: If True, makes this process deterministic. Otherwise, it will not be deterministic. The seed is
		set to the identifier of the process.
	:return: The graph counts. It is a Counter object (as a dictionary) where, for each entry (key, value), the key is
		a graph (in graph6 format) and and the value is its count.
	"""

	# If deterministic is True, set a seed for this process (equal to its identifier).
	if is_deterministic:
		seed = process_id
		random.seed(seed)
		np.random.seed(seed)

	# Create chuncks.
	num_chuncks_with_equal_size, remaining_chunck_size = divmod(num_graphs, _CHUNCK_SIZE)
	chuncked_num_graphs = [_CHUNCK_SIZE] * num_chuncks_with_equal_size
	if remaining_chunck_size > 0:
		chuncked_num_graphs.append(remaining_chunck_size)

	graph_counts = Counter()
	for num_graphs_to_gen in chuncked_num_graphs:
		# Generate graphs.
		graphs = _helpers.generate_graphs(num_graphs_to_gen, graph_gen, gen_args, gen_kwargs=gen_kwargs)

		# Canonically label the graphs.
		canonized_graphs = nauty.canonically_label(graphs, file_id=process_id)

		# Count the different graphs.
		chuncked_graph_counts = Counter(canonized_graphs)

		# Gather the results.
		graph_counts += chuncked_graph_counts
	
	return graph_counts

def draw_generated_graph_distr(gen_graph_distr, num_vertices=None):
	"""
	Draw the counts of graphs with Matplolib.

	:gen_graph_distr: The distribution of generated graphs (or the counts of graphs). It is a dictionary where, for
		each entry (key, value), the key is a graph (in graph6 format) and the value is the count of this graph.
	:num_vertices: The number of vertices used to generate the counts. It is only used for the title of the plot.
	"""

	# Create the title.
	title = 'Distribution of generated graphs'
	if num_vertices:
		title = ' '.join([title, 'with {} vertices'.format(num_vertices)])

	# Order the distribution of generated graphs to better visualize the plot.
	gen_graph_distr = OrderedDict(sorted(gen_graph_distr.items()))

	# Draw the histogram.
	_helpers.draw_hist(gen_graph_distr, title=title, xlabel='Graph', ylabel='Count', legend_label='Counts')
