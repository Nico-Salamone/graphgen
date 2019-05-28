if __name__ == '__main__':
	import graphgen.assessor as ass
	import graphgen.graph_generators as gg
	import graphgen.graph_counts as gc
	from graphgen import nauty

	import random
	import numpy as np
	import networkx as nx
	import matplotlib.pyplot as plt
	import os
	import os.path

	# The path containing all plots.
	PLOT_PATH = 'plots'
	if not os.path.exists(PLOT_PATH):
		os.makedirs(PLOT_PATH)

	# Parameters.
	num_vertices = 4
	num_graphs_to_gen = 1000

	#graph_gen = gg.naive_random_graph
	#graph_gen = gg.gnm_random_graph
	graph_gen = nx.gnp_random_graph
	gen_args = [num_vertices, 0.5]
	gen_kwargs = {}

	# Compute the graph counts.
	graph_counts = gc.compute_graph_counts(num_graphs_to_gen, graph_gen, gen_args, gen_kwargs=gen_kwargs,
		is_deterministic=True)

	# For each graph that is not in 'graph_counts', add it with a value of 0.
	all_graphs = nauty.generate_all_graphs(num_vertices)
	for graph in all_graphs:
		graph_counts[graph] = graph_counts.get(graph, 0)
	
	# Print the result of metrics.
	mdod = ass.compute_mdod(graph_counts)
	sdod = ass.compute_sdod(graph_counts)
	print("MDOD: {}".format(round(mdod, 3)))
	print("SDOD: {}".format(round(sdod, 3)))

	# Plot a histogram of graph counts.
	fig = plt.figure(figsize=(8, 8))
	gc.draw_graph_counts(graph_counts, num_vertices=num_vertices)
	plt.savefig(os.path.join(PLOT_PATH, 'graph_counts.eps'), format='eps', dpi=300)
	plt.show()
