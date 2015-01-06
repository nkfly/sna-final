# -*- coding: utf-8 -*-
import sys
import os
import json
import io
import httplib
import re
from pyquery import PyQuery as pq
from lxml import etree
import urllib
import networkx as nx
import Queue
import datetime
import codecs

# Usage : python download1.py {CHANNEL_LIMIT}

# need to run with python 2.7

def query_youtube_subscriptions(channel_id):
	url= "/youtube/v3/subscriptions?part=snippet&channelId="+channel_id+"&key=AIzaSyCuYeQya-JMYpWHhK8kCQKxzlrQXam-b0k&maxResults=50"

	connection = httplib.HTTPSConnection("www.googleapis.com")
	connection.request("GET", url)
	response = connection.getresponse()
	data = response.read().decode("utf-8")

	return json.loads(data)

def query_youtube_playlists(channel_id):
	url= "/youtube/v3/playlists?part=snippet&channelId="+channel_id+"&key=AIzaSyCuYeQya-JMYpWHhK8kCQKxzlrQXam-b0k&maxResults=50"

	connection = httplib.HTTPSConnection("www.googleapis.com")
	connection.request("GET", url)
	response = connection.getresponse()
	data = response.read().decode("utf-8")

	return json.loads(data)

def query_youtube_playlistitem(playlist_id,token=None):
	if token == None:
		url= "/youtube/v3/playlistItems?part=snippet&playlistId="+playlist_id+"&key=AIzaSyCuYeQya-JMYpWHhK8kCQKxzlrQXam-b0k&maxResults=50"
	else:
		url= "/youtube/v3/playlistItems?part=snippet&playlistId="+playlist_id+"&&pageToken="+token+"&key=AIzaSyCuYeQya-JMYpWHhK8kCQKxzlrQXam-b0k&maxResults=50"

	connection = httplib.HTTPSConnection("www.googleapis.com")
	connection.request("GET", url)
	response = connection.getresponse()
	data = response.read().decode("utf-8")

	return json.loads(data)

def query_youtube_page_for_related_videos(v):
	url= "/watch?v="+v

	connection = httplib.HTTPSConnection("www.youtube.com")
	connection.request("GET", url)
	response = connection.getresponse()
	data = response.read().decode("utf-8")
	d = pq(data)
	related_video = list()
	for li in d("#watch-related li"):
		# a 的格式要小心
		# related video 有可能有
		a = pq(li).find('a').attr('href')
		if a != None:
			related_video.append(a)
	return related_video

def query_youtube_video(v):
	url= "/youtube/v3/videos?part=snippet&id="+v+"&key=AIzaSyCuYeQya-JMYpWHhK8kCQKxzlrQXam-b0k&maxResults=50"
	connection = httplib.HTTPSConnection("www.googleapis.com")
	connection.request("GET", url)
	response = connection.getresponse()
	data = response.read().decode("utf-8")

	return json.loads(data)

#主要是配合  get_subscribe_list 使用	
def get_youtube_subscribe_page(channel_id):	 #subscribed page部分，function 會回傳一個 Url 可以直接接在 www.youtube.com 後面連到那個 channel 的 feature channel 區
	url= "/channel/"+channel_id

	connection = httplib.HTTPSConnection("www.youtube.com")
	connection.request("GET", url)
	response = connection.getresponse()
	data = response.read().decode("utf-8")
	d = pq(data)
	index=0
	for ul in d(".appbar-nav-menu li"):
		a = pq(ul).find('a').attr('href')
		if index == 3:
			break
		index=index+1
	return a
#取得這個 channel 他的 feature channel 內 所有 channel 的 id，需要注意的是有些 channel 在台灣地區 不是 available 所以可能拿到 id 也沒有用
def get_subscribe_list(channel_id):
	url=get_youtube_subscribe_page(channel_id)
	connection = httplib.HTTPSConnection("www.youtube.com")
	connection.request("GET", url)
	response = connection.getresponse()
	data = response.read().decode("utf-8")
	d = pq(data)
	subscribed_id=list()
	for span in d('span.g-hovercard'):
		subscribed_id.append(pq(span).attr('data-ytid'))
	return subscribed_id
	
def creating_graph(start_id,channel_limit):
	channel_count =  channel_limit-1 # channel count 是要算我還有幾個 channel left
	graph = nx.DiGraph()
	download_queue = Queue.Queue()
	download_queue.put(start_channel_id)

	while not download_queue.empty():
		print(str(channel_count) + ' channels left...' )

		channel_id = download_queue.get()
		graph.add_node(channel_id, type='channel')

		playlists = query_youtube_playlists(channel_id)
		for playlist in playlists['items']:
			playlist_item = query_youtube_playlistitem(playlist['id'])
			totalitems = playlist_item['pageInfo']['totalResults']
			print("Playlist : "+playlist['id']+" : "+str(totalitems)+" video(s)")
			if playlist_item['pageInfo']['totalResults'] > 500:
				continue
			#iterate through the list
			end = False
			while not end:
				for item in playlist_item['items']:
					v = item['snippet']['resourceId']['videoId']
					if not graph.has_node(v):
						if item['snippet']['title'] == 'Deleted video' or item['snippet']['title'] == 'Private video':
							print("Found Deleted or Private Video, not added")
						else :
							#print('add play_list video')
							graph.add_node(v, type='video', channelId=item['snippet']['channelId'],playlist=list(), title=item['snippet']['title'], description=item['snippet']['description'], publishedAt=item['snippet']['publishedAt'])
							graph.node[v]['playlist'].append(playlist['id'])
							graph.add_edge(channel_id, v, type='has')
					else:
						if playlist['id'] not in graph.node[v]['playlist']:
							graph.node[v]['playlist'].append(playlist['id'])
					# related video part
					
					'''for related_video in query_youtube_page_for_related_videos(v):
						if not graph.has_node(related_video):
							p=re.compile('.*?watch\?v=(.*?)($|&)')
							s=p.search(related_video)
							related_video=s.group(1)
							video_info = query_youtube_video(related_video)
							v1=video_info['items'][0]['id']
							if not graph.has_node(v1):
								if video_info['items'][0]['snippet']['title'] == 'Deleted video' or video_info['items'][0]['snippet']['title'] == 'Private video':
									print("Found Deleted or Private Video, not added")
								else:
									#print('add related_video')	
									graph.add_node(v, type='video', channelId=video_info['items'][0]['snippet']['channelId'], title=video_info['items'][0]['snippet']['title'], description=video_info['items'][0]['snippet']['description'], publishedAt=video_info['items'][0]['snippet']['publishedAt'])
									channel_tmp = video_info['items'][0]['snippet']['channelId']
									if not graph.has_node(channel_tmp):
										graph.add_node(channel_tmp, type = 'channel')
									graph.add_edge(channel_id, v, type='has')'''
				#確認list 已經跑完
				try:
					nextToken = playlist_item['nextPageToken']
					playlist_item = query_youtube_playlistitem(playlist['id'],token = nextToken)
				except:
					end = True

		#這個部分是原本學長寫拿 subscribed channel 的方法，因為會權限不足改成用我的方式去做暴力爬
		'''subscriptions = query_youtube_subscriptions(channel_id)
		if 'error' not in subscriptions:
			for item in subscriptions['items']:
				download_queue.put(item['snippet']['resourceId']['channelId'])'''
		#以下是我所新增的部分 2014/12/23
		if channel_limit > 0 :
			subscriptions = get_subscribe_list(channel_id)
			for id in subscriptions:
				if not graph.has_node(id):
					graph.add_node(id,type='channel')
					graph.add_edge(channel_id,id,type="subscribed") # 這行有爭議性 畢竟我們不確定他的 feature channel 是不是就是我 subscribed 的 channel
					download_queue.put(id)
					channel_count = channel_count + 1
			channel_limit -= 1
		channel_count = channel_count - 1
	return graph
	
#把圖片存起來名字會依照現在的時間命名 例如 "2014-12-23_17:42:17_Network.gpickle"
#會回傳我現在存好的 filename 以後方便 read
def store_graph(graph,name=None):
	filename=datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')+"_Network.gpickle"
	if name != None:
		filename=name+".gpickle"
	nx.write_gpickle(graph,filename)
	print("Finish storing the graph"+" "+filename)
	return filename

#讀取graph
def read_graph(filename):
	graph=nx.DiGraph()
	graph=nx.read_gpickle(filename)
	return graph

def browse_graph(mygraph,filename=None,output=False):
	if filename == None:
		name= datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')+"_browse_graph_output.txt"
	if output:
		fd = codecs.open(name, "w" , "utf-8")
	list=mygraph.nodes()
	for node in list:		
		if mygraph.node[node]['type'] == 'video':
			print("A video : "+mygraph.node[node]['title']+" pid : "+str(mygraph.node[node]['playlist']))
			string_tmp = "A video : "+mygraph.node[node]['title']+" pid : "+str(mygraph.node[node]['playlist'])+"\n"
			if output:
				fd.write(string_tmp)
		#else:
			#print("A channel : "+node)
	try:
		fd.close()
	except:
		pass

def count_graph(mygraph):
	list=mygraph.nodes()
	channel_count=0
	video_count=0
	for node in list:
		try:
			if mygraph.node[node]['type'] == 'video':
				video_count+=1
			else:
				channel_count+=1
		except:
			pass
	print("The graph has "+str(video_count)+" video(s)\nThe graph has "+str(channel_count)+" channel(s)")

def add_related_video(mygraph):
	list = mygraph.nodes()
	for node in list:
		if mygraph.node[node]['type'] == 'video':
			# 需要增加新的	related video part
			try:
				returna = query_youtube_page_for_related_videos(node)
				for video_link in returna:
					p=re.compile('.*?watch\?v=(.*?)($|&)')
					s=p.search(video_link)
					related_video=s.group(1)
					video_info = query_youtube_video(related_video)
					if video_info['items'][0]['snippet']['channelId'] == mygraph.node[node]['channelId']:
						if related_video in list:
							mygraph.add_edge(node,video_info['items'][0]['id'])
							#print("add edge")
						else:
							mygraph.add_node(related_video, type = 'video', channelId = video_info['items'][0]['snippet']['id'], playlist = list(), title = video_info['items'][0]['snippet']['title'], description = video_info['items'][0]['snippet']['description'], publishedAt = video_info['items'][0]['snippet']['publishedAt'])
							#print("Unexcepecrted stuff, the video has same author but not in the graph 0.0 ?")
			except:
				pass
		else:
			print("\nchange channel\n")
#取得觀看次數，由於沒有辦法使用
def get_view_number(v):
	url= "/watch?v="+v
	connection = httplib.HTTPSConnection("www.youtube.com")
	connection.request("GET", url)
	response = connection.getresponse()
	data = response.read().decode("utf-8")
	print(data.encode("utf8"))
	#return int(a.replace(',',''))
			
if __name__ == "__main__":
	#可以用 nx.compose 合併 graph
	'''start_channel_id = 'UCKBIWLnzHg9QZzhxUb5eLJw' # 這部分要再看怎麼print implement 之類的 有點煩 www
	channel_limit = int(sys.argv[1])
	mygraph = nx.DiGraph();
	mygraph = creating_graph(start_channel_id,channel_limit)
	store_graph(mygraph,'secondtry')'''
	#mygraph = nx.DiGraph()
	#mygraph = read_graph("firsttry.gpickle")
	'''mygraph1 = nx.DiGraph()
	mygraph1 = read_graph("firstRelated.gpickle")
	for node in mygraph1.nodes():
		if mygraph.node[node]['type'] == 'video':
			print("video :"+str(node))
			print(str(get_view_number(node)))
			break'''
	print(str(get_view_number('mxorHPrUyvs')))
	#count_graph(mygraph)
	#count_graph(mygraph1)
	#print("Nodes: "+str(mygraph.number_of_nodes())+"   Edges: "+str(mygraph.number_of_edges()))
	#print("Nodes: "+str(mygraph1.number_of_nodes())+"   Edges: "+str(mygraph1.number_of_edges()))
	