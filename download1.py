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

def query_youtube_playlistitem(playlist_id):
	url= "/youtube/v3/playlistItems?part=snippet&playlistId="+playlist_id+"&key=AIzaSyCuYeQya-JMYpWHhK8kCQKxzlrQXam-b0k&maxResults=50"

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
	

if __name__ == "__main__":
	start_channel_id = 'UC26zQlW7dTNcyp9zKHVmv4Q'
	channel_limit = int(sys.argv[1])
	graph = nx.DiGraph()

	
	download_queue = Queue.Queue()
	download_queue.put(start_channel_id)

	while channel_limit > 0 and not download_queue.empty():
		print(str(channel_limit) + ' channels left...' )

		channel_id = download_queue.get()

		graph.add_node(channel_id, type='channel')

		playlists = query_youtube_playlists(channel_id)
		for playlist in playlists['items']:
			playlist_item = query_youtube_playlistitem(playlist['id'])
			if playlist_item['pageInfo']['totalResults'] > 50:
				continue

			for item in playlist_item['items']:
				v = item['snippet']['resourceId']['videoId']
				if not graph.has_node(v):
					graph.add_node(v, type='video', channelId=item['snippet']['channelId'],playlist=playlist['id'], title=item['snippet']['title'], description=item['snippet']['description'], publishedAt=item['snippet']['publishedAt'])
				graph.add_edge(channel_id, v, type='has')
				
				# related video part
				
				for related_video in query_youtube_page_for_related_videos(v):
					if not graph.has_node(related_video):
						p=re.compile('.*?watch\?v=(.*?)($|&)')
						s=p.search(related_video)
						related_video=s.group(1)
						video_info = query_youtube_video(related_video)
						v1=video_info['items'][0]['id']
				 		graph.add_node(v, type='video', channelId=video_info['items'][0]['snippet']['channelId'], title=video_info['items'][0]['snippet']['title'], description=video_info['items'][0]['snippet']['description'], publishedAt=video_info['items'][0]['snippet']['publishedAt'])


		#這個部分是原本學長寫拿 subscribed channel 的方法，因為會權限不足改成用我的方式去做暴力爬
		'''subscriptions = query_youtube_subscriptions(channel_id)
		if 'error' not in subscriptions:
			for item in subscriptions['items']:
				download_queue.put(item['snippet']['resourceId']['channelId'])'''
		#以下是我所新增的部分 2014/12/23
		subscriptions = get_subscribe_list(channel_id)
		for id in subscriptions:
			if not graph.has_node(id):
				graph.add_node(id,type='channel')
				graph.add_edge(channel_id,id,type="subscribed") # 這行有爭議性 畢竟我們不確定他的 feature channel 是不是就是我 subscribed 的 channel
				download_queue.put(id)

		channel_limit -= 1