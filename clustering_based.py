# -*- coding: utf-8 -*-
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
import community

def lcs_len(x, y):
    """This function returns length of longest common sequence of x and y."""
 
    if len(x) == 0 or len(y) == 0:
        return 0
 
    xx = x[:-1]   # xx = sequence x without its last element    
    yy = y[:-1]
 
    if x[-1] == y[-1]:  # if last elements of x and y are equal
        return lcs_len(xx, yy) + 1
    else:
        return max(lcs_len(xx, y), lcs_len(x, yy))

def lcs(a, b):
    lengths = [[0 for j in range(len(b)+1)] for i in range(len(a)+1)]
    # row 0 and column 0 are initialized to 0 already
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            if x == y:
                lengths[i+1][j+1] = lengths[i][j] + 1
            else:
                lengths[i+1][j+1] = \
                    max(lengths[i+1][j], lengths[i][j+1])
    # read the substring out from the matrix
    result = ""
    x, y = len(a), len(b)
    while x != 0 and y != 0:
        if lengths[x][y] == lengths[x-1][y]:
            x -= 1
        elif lengths[x][y] == lengths[x][y-1]:
            y -= 1
        else:
            assert a[x-1] == b[y-1]
            result = a[x-1] + result
            x -= 1
            y -= 1
    return len(result)


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

def read_graph(filename):
	graph=nx.DiGraph()
	graph=nx.read_gpickle(filename)
	return graph

def construct_affinity_matrix(mygraph, predict_candidates):
	matrix = list()
	i = 0;
	for node1 in predict_candidates:
		matrix.append([])
		for node2 in predict_candidates:
			matrix[i].append(affinity(mygraph, node1, node2))
		i += 1

	return matrix


def count_accuracy(mygraph, predict_candidates, labels):
	len_predict_candidates = len(predict_candidates)
	if len_predict_candidates <= 1:
		return 1
	correct = 0
	for i in range(len_predict_candidates):
		for j in range(i+1, len_predict_candidates):
			if (mygraph.node[predict_candidates[i]]['playlist'] == mygraph.node[predict_candidates[j]]['playlist']) == (labels[i] == labels[j]):
				correct += 1
	return correct/(len_predict_candidates*(len_predict_candidates-1)/2)

def isEnglish(s):
    try:
        s.encode('ascii')
    except UnicodeEncodeError:
        return False
    else:
        return True


def make_bigram_list(sentence):
	if isEnglish(sentence):
		return sentence.split()
	bigram_list = list()
	for i in range(len(sentence)-1):
		bigram_list.append(sentence[i:i+2])
	return bigram_list


def convert_to_tfidf_bigram(mygraph, predict_candidates):
	dimension_dic = dict()
	df_dic = dict()
	tfidf_vectors = []
	for node in predict_candidates:
		bigram_list = make_bigram_list(mygraph.node[node]['title'])
		bigram_set_for_df = set()
		vector = dict()
		for bigram in bigram_list:
			if bigram not in dimension_dic:
				dimension_dic[bigram] = len(dimension_dic)
			if dimension_dic[bigram] not in vector:
				vector[dimension_dic[bigram]] = 1
			else:
				vector[dimension_dic[bigram]] = vector[dimension_dic[bigram]] + 1
			bigram_set_for_df.add(bigram)
		for bigram in bigram_set_for_df:
			if dimension_dic[bigram] not in df_dic:
				df_dic[dimension_dic[bigram]] = 1
			else:
				df_dic[dimension_dic[bigram]] = df_dic[dimension_dic[bigram]] + 1
		tfidf_vectors.append(vector)


	number_of_documents = len(predict_candidates)

	for vector in tfidf_vectors:
		for dimension in vector:
			vector[dimension] = math.log(1+vector[dimension])*math.log(1+number_of_documents/df_dic[dimension])
	dimension_max = len(dimension_dic)
	return tfidf_vectors, dimension_max


def to_compact_vectors(tfidf_vectors, dimension_max):
	compact_vectors = []
	for vector in tfidf_vectors:
		v = []
		for i in range(dimension_max):
			if i not in vector:
				v.append(0)
			else:
				v.append(vector[i])
		compact_vectors.append(v)
	return compact_vectors

def get_playlist_number(mygraph, node):
	predict_candidates = list()
	for neighbor in mygraph.neighbors(node):
		if mygraph.node[neighbor]['type'] == 'video':
			predict_candidates.append(neighbor)
	peek_data_for_playlist_number = set()
	for node in predict_candidates:			
		peek_data_for_playlist_number.update(mygraph.node[node]['playlist'])
	return len(peek_data_for_playlist_number)
		


def get_average_playlist_number(mygraph):
	sample_number = 0
	sum_of_playlist = 0
	for node in mygraph.nodes():
		if mygraph.node[node]['type'] == 'video':
			continue

		
		playlist_number = get_playlist_number(mygraph, node)
		if playlist_number == 0:
			continue

		sum_of_playlist += playlist_number
		sample_number += 1
		
	return int(sum_of_playlist/sample_number)

def get_neighbor_average_playlist_number(mygraph, node):
	sample_number = 0
	sum_of_playlist = 0
	for neighbor in mygraph.neighbors(node):
		if mygraph.node[neighbor]['type'] == 'channel':
			playlist_number = get_playlist_number(mygraph, neighbor)
			if playlist_number == 0:
				continue
			sum_of_playlist += playlist_number
			sample_number += 1
	if sample_number == 0:
		return 11
	return int(sum_of_playlist/sample_number)

def construct_graph_from_affinity_matrix_and_community_label(affinity_matrix):
	size =  len(affinity_matrix)
	sum_affinity = 0
	for i in range(size):
		for j in range(i+1, size):
			sum_affinity += affinity_matrix[i][j]
	if size > 1:
		average_affinity = sum_affinity/(size*(size-1))
	else:
		average_affinity = sum_affinity

	graph = nx.Graph()
	for i in range(size):
		graph.add_node(i)
		for j in range(i+1, size):
			if affinity_matrix[i][j] >= average_affinity:
				graph.add_edge(i, j)
	
	partition = community.best_partition(graph)	
	labels = []
	for i in range(size):
		labels.append(partition[i])
	return labels

			

if __name__ == '__main__':
	mygraph = read_graph("./firsttry.gpickle")
	accuracy_from_kmeans = 0
	accuracy_from_affinity_propogation = 0
	accuracy_from_dbscsn = 0
	accuracy_from_community_detection = 0
	sample_number = 0
	# print(get_average_playlist_number(mygraph))
	for node in mygraph.nodes():
		if mygraph.node[node]['type'] == 'video':
			continue

		predict_candidates = list()
		for neighbor in mygraph.neighbors(node):
			if mygraph.node[neighbor]['type'] == 'video':
				predict_candidates.append(neighbor)

		if len(predict_candidates) == 0:
			continue

		sample_number += 1
		peek_data_for_playlist_number = set()
		for node in predict_candidates:			
			peek_data_for_playlist_number.update(mygraph.node[node]['playlist'])
		# print(len(peek_data_for_playlist_number))
		# n_clusters = len(peek_data_for_playlist_number)
		n_clusters = get_neighbor_average_playlist_number(mygraph, node)
		tfidf_vectors, dimension_max = convert_to_tfidf_bigram(mygraph, predict_candidates)

		tfidf_vectors = to_compact_vectors(tfidf_vectors, dimension_max)

		pca = PCA(n_components=n_clusters).fit(tfidf_vectors)
		estimator = KMeans(init=pca.components_, n_clusters=n_clusters, n_init=1)
		# estimator = KMeans(init='random', n_clusters=n_clusters, n_init=10)
		# estimator = KMeans(init='k-means++', n_clusters=n_clusters, n_init=10)
		
		estimator.fit(tfidf_vectors)
		labels = estimator.labels_
		accuracy_from_kmeans += count_accuracy(mygraph, predict_candidates, labels)







		affinity_matrix = construct_affinity_matrix(mygraph,  predict_candidates)
		cluster_centers_indices, labels = affinity_propagation(affinity_matrix)


		accuracy_from_affinity_propogation += count_accuracy(mygraph, predict_candidates, labels)


		labels = construct_graph_from_affinity_matrix_and_community_label(affinity_matrix)

		accuracy_from_community_detection += count_accuracy(mygraph, predict_candidates, labels)


		
		# db = DBSCAN(eps=0.8, min_samples=1)
		# X = np.array(tfidf_vectors)
		# db.fit(X)
		# labels = db.labels_
		# accuracy_from_dbscsn += count_accuracy(mygraph, predict_candidates, labels)


		print(' accuracy_from_affinity_propogation:'+str(accuracy_from_affinity_propogation/sample_number)+' accuracy_from_community_detection:'+str(accuracy_from_community_detection/sample_number))
		# print('accuracy_from_kmeans:'+str(accuracy_from_kmeans/sample_number) + ' accuracy_from_affinity_propogation:'+str(accuracy_from_affinity_propogation/sample_number)+ ' accuracy_from_dbscsn:'+str(accuracy_from_dbscsn/sample_number))
		# print('accuracy_from_kmeans:'+str(accuracy_from_kmeans/sample_number) + ' accuracy_from_affinity_propogation:'+str(accuracy_from_affinity_propogation/sample_number))


		# print(count_accuracy(mygraph, predict_candidates, labels))

