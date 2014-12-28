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


def count_graph(mygraph):
	list=mygraph.nodes()
	channel_count=0
	video_count=0
	for node in list:
		if mygraph.node[node]['type'] == 'video':
			video_count+=1
		else:
			channel_count+=1
	print("The graph has "+str(video_count)+" video(s)\nThe graph has "+str(channel_count)+" channel(s)")

def read_graph(filename):
	graph=nx.DiGraph()
	graph=nx.read_gpickle(filename)
	return graph

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

if __name__ == '__main__':
	mygraph = read_graph("/home/nkfly/firsttry.gpickle")


	sum_accuracy = 0
	sum_channel = 0

	for node in mygraph.nodes():
		if mygraph.node[node]['type'] == 'video':
			continue

		predict_candidates = list()
		bin_candidates = dict()
		for neighbor in mygraph.neighbors(node):
			if mygraph.node[neighbor]['type'] == 'video':
				predict_candidates.append(neighbor)
			elif mygraph.node[neighbor]['type'] == 'channel':
				for neighbor_s_video in mygraph.neighbors(neighbor):
					if mygraph.node[neighbor_s_video]['type'] == 'video':
						if str(neighbor)+mygraph.node[neighbor_s_video]['playlist'][0] not in bin_candidates:
							bin_candidates[str(neighbor)+mygraph.node[neighbor_s_video]['playlist'][0]] = [neighbor_s_video]
						else:
							bin_candidates[str(neighbor)+mygraph.node[neighbor_s_video]['playlist'][0]].append(neighbor_s_video)
		
		bin_features = dict()

		for bin in bin_candidates:
			feature = list()
			for video in bin_candidates[bin]:
				feature.append(mygraph.node[video]['title'])
				# feature += mygraph.node[video]['description']
			bin_features[bin] = feature

		predict_answer = dict()
		for predict_candidate in predict_candidates:
			# print(mygraph.node[predict_candidate]['title'])
			predict_feature = mygraph.node[predict_candidate]['title']
			# predict_feature .union(mygraph.node[predict_candidate]['description'])

			max_intersection = -1
			choose_bin = ''
			for bin in bin_features:
				for feautre in bin_features[bin]:
				# intersection = len(predict_feature.intersection(bin_features[bin]))
					longest_common_subsequence = lcs(predict_feature, feautre)
					if longest_common_subsequence > max_intersection:
						max_intersection = longest_common_subsequence
						choose_bin = bin

			if choose_bin not in predict_answer:
				predict_answer[choose_bin] = [predict_candidate]
			else :
				predict_answer[choose_bin].append(predict_candidate)
		print('channel ' + node + ' ' +  str(len(predict_candidates)) +' videos in '+ str(len(predict_answer)) + ' playlists')









