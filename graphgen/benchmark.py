import graphgen.graph_counts as gc
from graphgen import nauty

from multiprocessing import cpu_count
from collections.abc import Iterable

def benchmark_generator(graph_gen, gen_args, assessors, vertex_num_list, gen_kwargs={}, factor_num_graphs=1000,
	num_processes=cpu_count(), verbose=True):
	"""
	From an assessor, benchmark a graph generator for several numbers of vertices.
	More specifically, for each number of vertices, the counts of graphs is computed and all assesors assesses the
	generator from the counts.

	:graph_gen: The generator of graphs (a Python function) whose the first argument is the number of vertices.
	:gen_args: The list of requiered arguments to send to the graph generator (not to mention the number of vertices).
	:assessors: An assessor or a list of assessors of graph generator (a Python function). Each one assesses it using
		the counts of graphs. You can use 'assessor.compute_mdod' or 'assessor.compute_sdod' for example.
	:vertex_num_list: The list of numbers of vertices. If one of these is greater than 9, it can be slow to compute.
	:gen_kwargs: The dictionary of optional arguments to send to the graph generator. For each entry (key, value)
		of this dictionary, the key is the parameter name and the value is the value to set to this parameter.
	:factor_num_graphs: It defines the number of graphs to generate from the number of all different graphs. For
		example, suppose that in the current iteration the number of vertices is 'n' and suppose taht there are 'k'
		different graphs with 'n' vertices. Then, for this iteration, 'factor_num_graphs' * 'k' graphs will be generate
		in order to compute the counts of graphs (see graph_counts.compute_graph_counts). The higher 'factor_num_graphs'
		will be and the more accurate the assessment will be (and the slower this function will run).
	:num_processes: The number of processes to create. By default, it is set to 'n', where 'n' is the number of CPUs in
		the system.
	:verbose: If True, some logs will be print, otherwise nothing will be print.
	:return: A dictionary containing the assessments of each assessor for each number of vertices. For each entry
		(key, value), the key is the assessor function and the value is a list of size 'len(vertex_num_list)' where the
		ith element is the assessment of this assessor for 'vertex_num_list[i]' vertices.
	"""

	# If there is only one assessor, put it in a list.
	if not isinstance(assessors, Iterable):
		assessors = [assessors]

	assessments = {}
	for assessor in assessors:
		assessments[assessor] = []
	for num_vertices in vertex_num_list:
		if verbose:
			print("Current number of vertices: {}".format(num_vertices))

		# Compute all graphs with 'num_vertices' vertices.
		num_all_graphs = nauty.num_graphs(num_vertices)

		# Compute the number of graphs to generate.
		num_graphs_to_gen = factor_num_graphs * num_all_graphs

		# Compute the graph counts.
		graph_counts = gc.compute_graph_counts(num_graphs_to_gen, graph_gen, [num_vertices, *gen_args],
			gen_kwargs=gen_kwargs, is_deterministic=True, num_processes=num_processes)

		# For each graph that is not in 'graph_counts', add it with a value of 0.
		all_graphs = nauty.generate_all_graphs(num_vertices)
		for graph in all_graphs:
			graph_counts[graph] = graph_counts.get(graph, 0)

		# Assess the generator from the counts of graphs.
		if verbose:
			print("\tAssessments:")
		for assessor in assessors:
			assessment = assessor(graph_counts)
			assessments[assessor].append(assessment)

			if verbose:
				print("\t\t{}: {}".format(assessor.__name__, assessment))

	return assessments

if __name__ == '__main__':
	import graphgen.graph_generators as gg
	import graphgen.assessor as ass

	import networkx as nx

	# Parameters.
	vertex_num_list = list(range(1, 10))
	assessors = [ass.compute_mdod, ass.compute_sdod]

	# Assess the G(n, p) model.
	print("G(n, p) model")
	graph_gen = nx.gnp_random_graph
	gen_args = [0.5]

	benchmark_generator(graph_gen, gen_args, assessors, vertex_num_list)

	# Assess the G(n, m) model where 'm' follows an uniform distribution.
	print("\nG(n, m) model where 'm' is uniform")
	graph_gen = gg.gnm_random_graph
	gen_args = []
	gen_kwargs = {'num_edges': gg.UNIFORM}

	benchmark_generator(graph_gen, gen_args, assessors, vertex_num_list, gen_kwargs=gen_kwargs)

	# Assess the G(n, m) model where 'm' follows an normal distribution.
	print("\nG(n, m) model where 'm' is normal")
	graph_gen = gg.gnm_random_graph
	gen_args = []
	gen_kwargs = {'num_edges': gg.NORMAL}

	benchmark_generator(graph_gen, gen_args, assessors, vertex_num_list, gen_kwargs=gen_kwargs)
