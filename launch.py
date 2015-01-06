import networkx as nx
import Demon as D
import sys

'''file = open(sys.argv[1], "r")
for row in file:
    part = row.strip().split()
    G.add_edge(int(part[0]), int(part[1]))

# Example use of DEMON. Parameter discussed in the paper.'''
def ego(n,graph):
	tmp_list = mygraph.successors(node)
	for node_tmp in tmp_list:
		if mygraph.node[node_tmp]['type'] != 'video':
			tmp_list.remove(node_tmp)
	tmp_list.append(n)
	subGraph = mygraph.subgraph(tmp_list)
	return subGraph

def egoMinusEgo(n,graph):
	tmp_list = mygraph.successors(node)
	for node_tmp in tmp_list:
		if mygraph.node[node_tmp]['type'] != 'video':
			tmp_list.remove(node_tmp)
	subGraph = mygraph.subgraph(tmp_list)
	return subGraph	
	
if __name__ == "__main__":
	mygraph = nx.DiGraph()
	mygraph = nx.read_gpickle("firstRelated.gpickle")
	CD = D.Demon()
	for node in mygraph.nodes() :
			if mygraph.node[node]['type'] != 'video':
				video_network = egoMinusEgo(node,mygraph)
				if video_network.number_of_edges() == 0:
					video_network = ego(node,mygraph)
					if video_network.number_of_edges() == 0:
						continue
				#print("video_network has "+str(video_network.number_of_nodes())+" "+str(video_network.number_of_edges()))
				#start the DEMON algorithm find it on the web 0w0 we need to calculate the episilon however
				CD.execute(video_network)
				print("\n")