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
	set1 = set(mygraph.node[node1]['title'].split())
	set2 = set(mygraph.node[node2]['title'].split())
	# if node1 != node2:
		# print(set.intersection(set2))
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


if __name__ == '__main__':
	mygraph = read_graph("/home/nkfly/firsttry.gpickle")
	for node in mygraph.nodes():
		if mygraph.node[node]['type'] == 'video':
			continue

		predict_candidates = list()
		for neighbor in mygraph.neighbors(node):
			if mygraph.node[neighbor]['type'] == 'video':
				predict_candidates.append(neighbor)

		if len(predict_candidates) == 0:
			continue

		peek_data_for_playlist_number = set()
		for node in predict_candidates:			
			peek_data_for_playlist_number.update(mygraph.node[node]['playlist'])
		# print(len(peek_data_for_playlist_number))
		n_clusters = len(peek_data_for_playlist_number)
		tfidf_vectors, dimension_max = convert_to_tfidf_bigram(mygraph, predict_candidates)

		tfidf_vectors = to_compact_vectors(tfidf_vectors, dimension_max)

		pca = PCA(n_components=n_clusters).fit(tfidf_vectors)
		estimator = KMeans(init=pca.components_, n_clusters=n_clusters, n_init=1)
		# estimator = KMeans(init='random', n_clusters=n_clusters, n_init=10)
		# estimator = KMeans(init='k-means++', n_clusters=n_clusters, n_init=10)
		
		estimator.fit(tfidf_vectors)
		labels = estimator.labels_

		# affinity_matrix = construct_affinity_matrix(mygraph,  predict_candidates)
		# cluster_centers_indices, labels = affinity_propagation(affinity_matrix)
		
		print(count_accuracy(mygraph, predict_candidates, labels))

