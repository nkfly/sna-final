import sys
import os
import json
import io
import re
from pyquery import PyQuery as pq
from lxml import etree
import urllib
import networkx as nx
import datetime
import codecs
import math

import numpy as np
from numpy.testing import assert_equal, assert_array_equal

from sklearn.cluster.affinity_propagation_ import AffinityPropagation, \
									affinity_propagation
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.datasets.samples_generator import make_blobs
from sklearn.metrics import euclidean_distances
from sklearn.cluster import MeanShift, estimate_bandwidth
from sklearn.cluster import DBSCAN
from dateutil import parser


def read_graph(filename):
	graph=nx.DiGraph()
	graph=nx.read_gpickle(filename)
	return graph
def isEnglish(s):
    try:
        s.encode('ascii')
    except UnicodeEncodeError:
        return False
    else:
        return True

def affinity(mygraph, node1, node2):
	# return lcs(mygraph.node[node1]['title'], mygraph.node[node2]['title'])
	node1_isenglish = isEnglish(mygraph.node[node1]['title'])
	node2_isenglish = isEnglish(mygraph.node[node2]['title'])

	if (node1_isenglish and node2_isenglish):
		set1 = set(mygraph.node[node1]['title'].split())
		set2 = set(mygraph.node[node2]['title'].split())
		return len(set1.intersection(set2))
	elif not node1_isenglish and node2_isenglish:
		return 0
	elif node1_isenglish and not node2_isenglish:
		return 0
	else :
		set1 = set(list(mygraph.node[node1]['title']))
		set2 = set(list(mygraph.node[node2]['title']))
		return len(set1.intersection(set2))
def date_diff(mygraph, node1, node2):
	date1 = parser.parse(mygraph.node[node1]['publishedAt'])
	date2 = parser.parse(mygraph.node[node2]['publishedAt'])
	return abs(date1-date2).days

def convert_to_feature_vector(mygraph, node1, node2):
	aff = affinity(mygraph, node1, node2)
	df = date_diff(mygraph, node1, node2)
	return [aff, df]


if __name__ == '__main__':
	mygraph = read_graph("./firsttry.gpickle")
	x = []
	y = []

	for node in mygraph.nodes():
		if mygraph.node[node]['type'] == 'video':
			continue

		predict_candidates = list()
		for neighbor in mygraph.neighbors(node):
			if mygraph.node[neighbor]['type'] == 'video':
				predict_candidates.append(neighbor)

		if len(predict_candidates) == 0:
			continue

		for i in range(len(predict_candidates)):
			for j in range(i+1, len(predict_candidates)):
				if mygraph.node[predict_candidates[i]]['playlist'] == mygraph.node[predict_candidates[j]]['playlist']:
					
					y.append(1)
				else:
					y.append(-1)					
				x.append(convert_to_feature_vector(mygraph, predict_candidates[i], predict_candidates[j]))
	with open('training.txt', 'w') as w:
		w.write(str(y[i]) + ': ')
		for i in range(len(x)):
			w.write(str(1+i) + ':' + str(x[i]))
		w.write('\n')		
	


	



	print('hello')