from graphgen import nauty
from graphgen import _helpers
from graphgen._settings import RESOURCE_PATH

import networkx as nx
from collections import Counter, OrderedDict
import pickle
from scipy import stats
import os
import os.path

# The path of files containing the counts of numbers of edges (kind of cache).
_EDGE_NUM_COUNT_PATH = os.path.join(RESOURCE_PATH, 'edge_num_counts')
if not os.path.exists(_EDGE_NUM_COUNT_PATH):
	os.makedirs(_EDGE_NUM_COUNT_PATH)

def compute_mean(num_vertices):
	"""
	Compute the mean of numbers of edges of all graphs with 'num_vertices' vertices.

	:num_vertices: The number of vertices.
	:return: The mean of numbers of edges of graphs with 'num_vertices' vertices.
	"""

	return _helpers.compute_edge_max_num(num_vertices) / 2

def compute_std(num_vertices):
	"""
	Compute the standard deviation of numbers of edges of all graphs with 'num_vertices' vertices.

	:num_vertices: The number of vertices.
	:return: The standard deviation of numbers of edges of graphs with 'num_vertices' vertices.
	"""

	# This function was computed using a linear	regression.
	return (0.3375899521271764 * num_vertices) + 0.1575828904704868

def compute_edge_num_counts(num_vertices):
	"""
	Compute the counts of numbers of edges (the distribution of numbers of edges) of all graphs with 'num_vertices'
	vertices.

	:num_vertices: The number of vertices.
	:return: The counts of numbers of edges. It is a Counter object (as a dictionary) where, for each entry (key,
		value), the key is a number of edges and and the value is its count.
	"""

	# Get the file path containing the counts of numbers of edges for 'num_vertices' vertices. It is considered as a
	# cache.
	cache_path = _get_edge_num_count_file_path(num_vertices)

	try:
		# Read the file.
		with open(cache_path, 'rb') as cache:
			edge_num_counts = pickle.load(cache)

		return edge_num_counts
	except FileNotFoundError:
		pass

	# If the '_get_edge_num_count_file_path(num_vertices)' file does not exist.

	# Generate all graphs with 'num_vertices' vertices and convert them into a NetworkX object.
	all_graphs = [_helpers.graph6_to_networkx(graph) for graph in nauty.generate_all_graphs(num_vertices)]

	# Compute the number of edges of each graph.
	edge_num_list = [graph.number_of_edges() for graph in all_graphs]

	# Count the different numbers of edges.
	edge_num_counts = Counter(edge_num_list)

	# Write the counts of numbers of edges in the cache file.
	with open(cache_path, 'wb') as cache:
		pickle.dump(edge_num_counts, cache)

	return edge_num_counts

def perform_normality_test(edge_num_counts):
	"""
	Test if the numbers of edges follow a normal distribution. A Chi-squared test is performed.

	:edge_num_counts: The counts of numbers of edges (Counter object).
	:return: The chi-squared test statistic and the p-value of the statistical test.
	"""

	# Compute the parameters of the normal distribution and the normal distribution.
	mean, std = _helpers.compute_mean_std_dict(edge_num_counts)

	# Compute the normal distribution and its probability distribution.
	normal_dist = stats.norm(mean, std)
	probability_distr = lambda num_edges: normal_dist.cdf(num_edges + 0.5) - normal_dist.cdf(num_edges - 0.5)
	# 'probability_distr' is the probability distribution of the number of edges.

	# Perform the Chi-squared test.
	chi_squared_test_stat, p_value = _perform_chi_squared_test(edge_num_counts, probability_distr)

	return chi_squared_test_stat, p_value

def perform_binomial_test(edge_num_counts):
	"""
	Test if the numbers of edges follow a binomial distribution. A Chi-squared test is performed.

	:edge_num_counts: The counts of numbers of edges (Counter object).
	:return: The chi-squared test statistic and the p-value of the statistical test.
	"""

	# Compute the parameters of the binomial distribution.
	mean, std = _helpers.compute_mean_std_dict(edge_num_counts)
	var = std ** 2
	n = (mean ** 2) / (mean - var)
	p = 1 - (var / mean)

	# Compute the binomial distribution and its probability distribution.
	binom_dist = stats.binom(n, p)
	probability_distr = binom_dist.pmf # Probability distribution of the number of edges.

	# Perform the Chi-squared test.
	chi_squared_test_stat, p_value = _perform_chi_squared_test(edge_num_counts, probability_distr)

	return chi_squared_test_stat, p_value

def draw_edge_num_counts(edge_num_counts, num_vertices=None):
	"""
	Draw the counts of numbers of edges with Matplolib.

	:edge_num_counts: The counts of numbers of edges (the distribution of these). It is a dictionary where, for each
		entry (key, value), the key is a number of edges and and the value is its count.
	:num_vertices: The number of vertices used to generate the counts. It is only used for the title of the plot.
	"""

	# Create the title.
	title = 'Counts of numbers of edges'
	if num_vertices:
		title = ' '.join([title, 'of graphs with {} vertices'.format(num_vertices)])

	# Order the counts of numbers of edges to better visualize the plot.
	edge_num_counts = OrderedDict(sorted(edge_num_counts.items()))

	# Draw the histogram.
	_helpers.draw_hist(edge_num_counts, title=title, xlabel='Number of edges', ylabel='Count', legend_label='Counts')

def _get_edge_num_count_file_path(num_vertices):
	"""
	Get the file path containing the counts of numbers of edges for 'num_vertices' vertices. These files can be
	considered as a cache.
	
	:num_vertices: The number of vertices.
	:return: The file path containing the counts of numbers of edges.
	"""

	return os.path.join(_EDGE_NUM_COUNT_PATH, 'enc_{}'.format(num_vertices))

def _perform_chi_squared_test(edge_num_counts, probability_distr, thres_deleting_elements=5):
	"""
	Test if the numbers of edges follow a distribution. A Chi-squared test is performed.

	:edge_num_counts: The counts of numbers of edges (Counter object).
	:probability_distr: A probability distribution of the number of edges. More formally, for a number of edges 'm',
		'probability_distr(m)' is equal to P(m), where P(m) is the probability that the number of edges is 'm'.
	:thres_deleting_elements: The threshold for deleted elements. When an expected element is smaller than this value,
		then, it is removed and the corresponding observed element is also deleted. In fact, Chi-squared test fails with
		small classes (elements), hence it is usefull to delete them.
	:return: The chi-squared test statistic and the p-value of the statistical test.
	"""

	# Compute the number of elements (numbers of edges) in the counter.
	num_elements = sum(edge_num_counts.values()) # It is equivalent to 'len(_helpers.counter_to_list(edge_num_counts))'.

	# Compute the observed counts of numbers of edges. 
	observed_edge_num_counts = list(edge_num_counts.values())

	# Compute the expected counts of numbers of edges.
	expected_edge_num_counts = []
	for num_edges in list(edge_num_counts.keys()):
		expected_edge_num_counts.append(num_elements * probability_distr(num_edges))

	# Remove elements (classes) when the expected value is smaller than a threshold (Chi-squared test fails with small
	# classes).
	index_to_remove = []
	for i, (observed, expected) in enumerate(zip(observed_edge_num_counts, expected_edge_num_counts)):
		if expected < thres_deleting_elements:
			index_to_remove.append(i)
	index_to_remove = set(index_to_remove)
	observed_edge_num_counts = [
		observed for i, observed in enumerate(observed_edge_num_counts)
		if i not in index_to_remove
	]
	expected_edge_num_counts = [
		expected for i, expected in enumerate(expected_edge_num_counts)
		if i not in index_to_remove
	]

	# Compute the chi-squared test statistic and the p-value of the statistical test.
	chi_squared_test_stat, p_value = stats.chisquare(observed_edge_num_counts, expected_edge_num_counts)

	return chi_squared_test_stat, p_value

if __name__ == '__main__':
	import matplotlib.pyplot as plt
	import numpy as np

	# The path containing all plots.
	PLOT_PATH = 'plots'
	if not os.path.exists(PLOT_PATH):
		os.makedirs(PLOT_PATH)

	# Parameters.
	num_vertices = 8

	# Compute the counts of numbers of edges.
	edge_num_counts = compute_edge_num_counts(num_vertices)

	# Compute the list of numbers of edges (convert the Counter object to a list), its size, its mean and its standard
	# deviation.
	edge_num_list = _helpers.counter_to_list(edge_num_counts)
	edge_num_list_size = len(edge_num_list) # The number of elements (numbers of edges) in 'edge_num_counts'.
	# Parameters of the corresponding normal distribution.
	edge_num_mean, edge_num_std = _helpers.compute_mean_std_dict(edge_num_counts)
	edge_num_var = edge_num_std ** 2
	# Parameters of the corresponding binomial distribution.
	binom_n = (edge_num_mean ** 2) / (edge_num_mean - edge_num_var)
	binom_p = 1 - (edge_num_var /edge_num_mean)

	# Perform normality tests.
	print("Normality tests\np-value for")
	print("\tchi-squared test: {}".format(perform_normality_test(edge_num_counts)[1]))
	print("\tKolmogorov–Smirnov test: {}".format(stats.kstest(edge_num_list, lambda x: stats.norm.cdf(x, edge_num_mean,
		edge_num_std))[1]))
	print("\tD'Agostino's K-squared test: {}".format(stats.normaltest(edge_num_list)[1]))
	print("\tShapiro–Wilk test: {}".format(stats.shapiro(edge_num_list)[1]))

	# Perform binomial test.
	print("Binomial test\np-value for")
	print("\tchi-squared test: {}".format(perform_binomial_test(edge_num_counts)[1]))

	# Plot a histogram of counts of numbers of edges and the corresponding normal distribution.
	fig = plt.figure(figsize=(8, 8))
	# Draw the histogram.
	draw_edge_num_counts(edge_num_counts, num_vertices=num_vertices)
	# Draw the corresponding normal distribution and plot the plot.
	norm_x = np.linspace(min(edge_num_counts.keys()), max(edge_num_counts.keys()), 1000)
	norm_y = edge_num_list_size * stats.norm.pdf(norm_x, edge_num_mean, edge_num_std)
	plt.plot(norm_x, norm_y, color='tomato', label='Corresponding\nnormal distribution')
	# Draw the corresponding binomial distribution and plot the plot.
	binom_x = list(range(len(edge_num_counts)))
	binom_y = edge_num_list_size * stats.binom.pmf(binom_x, binom_n, binom_p)
	#plt.plot(norm_x, norm_y, color='tomato', label='Corresponding\nnormal distribution')
	plt.bar(binom_x, binom_y, align='center', color='lightskyblue', edgecolor='black', alpha=0.5,
		label='Corresponding\nbinomal distribution')
	plt.legend(loc='best')
	plt.savefig(os.path.join(PLOT_PATH, 'edge_num_counts.eps'), format='eps', dpi=300)
	plt.show()

	##########
	
	# Compute the mean and the standard deviation of the numbers of eages for each number of vertices.
	print ("\nFor each number of vertices, compare the estimated mean (standard deviation respectively) of the " \
		"numbers of edges with the real mean (standard deviation respectively) of these ones.\nFormat:\nNumber of "\
		"vertices: 'n'\nMean: 'estimated' ('real')\n Standard deviation: 'estimated' ('real')\n")
	edge_num_mean_std_dict = {}
	for i in range(16):
		num_vertices = i + 1
		edge_num_counts = compute_edge_num_counts(num_vertices)
		edge_num_mean, edge_num_std = _helpers.compute_mean_std_dict(edge_num_counts)

		edge_num_mean_std_dict[num_vertices] = (edge_num_mean, edge_num_std)

		# Compare the approximate mean (standard deviation respectively) with the real mean (standard deviation
		# respectively).
		print("Number of vertices: {}".format(num_vertices))
		print("Mean: {} ({})".format(compute_mean(num_vertices), edge_num_mean))
		print("Standard deviation: {} ({})\n".format(compute_std(num_vertices), edge_num_std))

	vertice_num_list = list(edge_num_mean_std_dict.keys()) # List of numbers of vertices [1, 2, 3, ...].
	mean_list, std_list = list(zip(*edge_num_mean_std_dict.values()))
	
	# Compute a linear regression for the standard deviation of numbers of edges.
	slope, intercept, r_value, p_value, std_err = stats.linregress(vertice_num_list, std_list)
	print("\nstd(n) = {}n + {}, where n is the number of vertices".format(slope, intercept))
	print("r-value: {}".format(r_value))
	print("p-value: {}".format(p_value))
	print("Standard error: {}".format(std_err))

	# Plot a scatter plot of the mean of numbers of edges by the number of vertices.
	fig = plt.figure(figsize=(8, 8))
	plt.scatter(vertice_num_list, mean_list)
	plt.title('Mean of numbers of edges by number of vertices')
	plt.xlabel('Number of vertices')
	plt.ylabel('Mean of numbers of edges')
	plt.tight_layout()
	plt.savefig(os.path.join(PLOT_PATH, 'edge_num_mean_by_num_vertice.eps'), format='eps', dpi=300)
	plt.show()

	# Plot a scatter plot of the standard deviation of numbers of edges by the number of vertices and the corresponding
	# linear regression.
	regres_x = np.linspace(0, len(vertice_num_list), 100)
	regres_y = slope * regres_x + intercept
	fig = plt.figure(figsize=(8, 8))
	plt.scatter(vertice_num_list, std_list, label='Standard deviation')
	plt.plot(regres_x, regres_y, color='tomato', label='Corresponding regression')
	plt.title('Standard deviation of numbers of edges by number of vertices')
	plt.xlabel('Number of vertices')
	plt.ylabel('Standard deviation of numbers of edges')
	plt.legend(loc='best')
	plt.tight_layout()
	plt.savefig(os.path.join(PLOT_PATH, 'edge_num_std_by_num_vertice.eps'), format='eps', dpi=300)
	plt.show()
