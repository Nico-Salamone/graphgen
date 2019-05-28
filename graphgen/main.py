if __name__ == '__main__':
	import graphgen.assessor as ass
	import graphgen.graph_generators as gg
	import graphgen.generated_graph_distr as ggd
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

	# Compute the distribution of generated graphs.
	gen_graph_distr = ggd.generated_graph_distr(num_vertices, num_graphs_to_gen, graph_gen, gen_args,
		gen_kwargs=gen_kwargs, is_deterministic=True)
	
	# Print the result of metrics.
	mdod = ass.compute_mdod(gen_graph_distr)
	sdod = ass.compute_sdod(gen_graph_distr)
	print("MDOD: {}".format(round(mdod, 3)))
	print("SDOD: {}".format(round(sdod, 3)))

	# Plot a histogram of distribution of generated graphs.
	fig = plt.figure(figsize=(8, 8))
	ggd.draw_generated_graph_distr(gen_graph_distr, num_vertices=num_vertices)
	plt.savefig(os.path.join(PLOT_PATH, 'gen_graph_distr.eps'), format='eps', dpi=300)
	plt.show()
