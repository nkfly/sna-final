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

import numpy as np
from numpy.testing import assert_equal, assert_array_equal

from sklearn.cluster.affinity_propagation_ import AffinityPropagation, \
									affinity_propagation
from sklearn.datasets.samples_generator import make_blobs
from sklearn.metrics import euclidean_distances

if __name__ == '__main__':
	n_clusters = 3
	centers = np.array([[1, 1], [-1, -1], [1, -1]]) + 10
	X, _ = make_blobs(n_samples=60, n_features=2, centers=centers,cluster_std=0.4, shuffle=True, random_state=0)
	
	# Compute similarities
	S = -euclidean_distances(X, squared=True)
	print(len(S))
	preference = np.median(S) * 10
	print(preference)
	# Compute Affinity Propagation
	cluster_centers_indices, labels = affinity_propagation(S,
			preference=preference)
	print(labels)
	n_clusters_ = len(cluster_centers_indices)

	assert_equal(n_clusters, n_clusters_)

	af = AffinityPropagation(preference=preference, affinity="precomputed")
	labels_precomputed = af.fit(S).labels_

	af = AffinityPropagation(preference=preference)
	labels = af.fit(X).labels_

	assert_array_equal(labels, labels_precomputed)

	cluster_centers_indices = af.cluster_centers_indices_

	n_clusters_ = len(cluster_centers_indices)
	assert_equal(np.unique(labels).size, n_clusters_)
	assert_equal(n_clusters, n_clusters_)

	# Test also with no copy
	_, labels_no_copy = affinity_propagation(S, preference=preference,
			copy=False)
	assert_array_equal(labels, labels_no_copy)

