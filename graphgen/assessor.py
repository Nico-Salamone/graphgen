import numpy as np

def compute_mdod(graph_counts):
	"""
	Compute the mean of deviations with respect to the optimal distribution (MDOD) to assess a graph generator.
	More specifically, the first step is the normalization of counts: each one is converted into a probability
	(computation of the probability mass function (PMF) of graphs). In fact, it modifies the mean of counts by '1 / n',
	where 'n' is the number of different graphs. Then, for each normalized count (or probability), the deviation
	(distance) between it and the new mean of counts (which is actually the mean of the probabilities) is computed.
	Finally, the mean of all deviations is computed and returned by this function.
	
	:graph_counts: The counts of graphs (the distribution of these). It is a dictionary where, for each entry (key,
		value), the key is a graph (in graph6 format) and the value is the count of this graph. Make sure to generate
		enough graphs to get good results.
	:return: The mean of deviations with results to the optimal distribution (MDOD). The value is between 0 and '2 / n',
		where 'n' is the number of different graphs (it will rarely be close to '2 / n', extreme / worst case. The
		smaller it is, the more uniform the graph generator is. Be aware that when the number of different graphs
		(equal to 'len(graph_counts)') is very high, the returned value will be very close to 0 and does not mean that
		the graph generator is good. For information, when the number of vertices is equal to 10, the number of
		different graphs is roughly 12 million.
	"""

	# Compute the PMF (normalize counts, convert each count into a probability). With this, the mean of new counts
	# (probabilities) change. It is '1 / n', where 'n' is the number of different graphs.
	pmf = _compute_pmf(graph_counts)

	# Compute the deviations between counts (probabilities) and the probability mean.
	proba_mean = 1 / len(pmf) # It is equivalent to 'sum(pmf.values()) / len(pmf)'.
	deviations = _compute_deviations(pmf.values(), proba_mean)

	# Compute the MDOD.
	mdod = np.mean(deviations)

	return mdod

def compute_sdod(graph_counts):
	"""
	Compute the sum of deviations with respect to the optimal distribution (SDOD) to assess a graph generator.
	More specifically, the first step is the normalization of counts: each one is converted into a probability
	(computation of the probability mass function (PMF) of graphs). In fact, it modifies the mean of counts by '1 / n',
	where 'n' is the number of different graphs. Then, for each normalized count (or probability), the deviation
	(distance) between it and the new mean of counts (which is actually the mean of the probabilities) is computed.
	Finally, the sum of all deviations is computed and returned by this function.
	
	:graph_counts: The counts of graphs (the distribution of these). It is a dictionary where, for each entry (key,
		value), the key is a graph (in graph6 format) and the value is the count of this graph. Make sure to generate
		enough graphs to get good results.
	:return: The sum of deviations with results to the optimal distribution (SDOD). The value is between 0 and 2 (it
		will rarely be close to 2, extreme / worst case). The smaller it is, the more uniform the graph generator is.
	"""

	# Compute the PMF (normalize counts, convert each count into a probability). With this, the mean of new counts
	# (probabilities) change. It is '1 / n', where 'n' is the number of different graphs.
	pmf = _compute_pmf(graph_counts)

	# Compute the deviations between counts (probabilities) and the probability mean.
	proba_mean = 1 / len(pmf) # It is equivalent to 'sum(pmf.values()) / len(pmf)'.
	deviations = _compute_deviations(pmf.values(), proba_mean)

	# Compute the SDOD.
	sdod = sum(deviations)

	return sdod

def _compute_pmf(graph_counts):
	"""
	Compute the probability mass function (PMF) of graphs. It can be seen as a normalization between 0 and 1, where each
	count is converted into a probability.

	:graph_counts: The counts of graphs (the distribution of these). It is a dictionary where, for each entry (key,
		value), the key is a graph (in graph6 format) and the value is the count of this graph. Make sure to generate
		enough graphs to get good results.
	:return: The probability mass function (PMF) of graphs. It is a dictionary where, for each entry (key, value), the
		key is a graph (in graph6 format) and the value is probability to get this graph.
	"""

	# Compute the sum of all counts.
	count_sum = sum(graph_counts.values())

	# Compute the PMF.
	pmf = {graph: (count / count_sum) for graph, count in graph_counts.items()}

	return pmf

def _compute_deviations(counts, middle_value):
	"""
	For each count, compute the deviation (destance) between it and some value.

	:counts: The list of counts.
	:middle_value: The value used to compute the deviations.
	:return: A list of deviations.
	"""

	# For each count, compute the deviation (distance) between it and 'middle_value'.
	deviations = [abs(count - middle_value) for count in counts]

	return deviations

if __name__ == '__main__':
	graph_counts1 = {'g1': 10, 'g2': 8, 'g3': 8, 'g4': 14, 'g5': 4, 'g6': 12, 'g7': 11, 'g8': 18, 'g9': 6, 'g10': 9}
	graph_counts2 = {'g1': 12, 'g2': 8, 'g3': 11, 'g4': 9, 'g5': 12, 'g6': 10, 'g7': 8, 'g8': 10, 'g9': 11, 'g10': 9}
	graph_counts3 = {'g1': 100000, 'g2': 1, 'g3': 1, 'g4': 1, 'g5': 1, 'g6': 1, 'g7': 1, 'g8': 1, 'g9': 1, 'g10': 1}

	mdod = compute_mdod(graph_counts1)
	print("MDOD for 'graph_counts1': {}".format(round(mdod, 3)))
	sdod = compute_sdod(graph_counts1)
	print("SDOD for 'graph_counts1': {}\n".format(round(sdod, 3)))

	mdod = compute_mdod(graph_counts2)
	print("MDOD for 'graph_counts2': {}".format(round(mdod, 3)))
	sdod = compute_sdod(graph_counts2)
	print("SDOD for 'graph_counts2': {}\n".format(round(sdod, 3)))
	
	mdod = compute_mdod(graph_counts3)
	print("MDOD for 'graph_counts3': {}".format(round(mdod, 3)))
	sdod = compute_sdod(graph_counts3)
	print("SDOD for 'graph_counts3': {}".format(round(sdod, 3)))
