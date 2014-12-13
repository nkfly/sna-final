import sys
import os
import json
import io
import http.client;
from pyquery import PyQuery as pq
from lxml import etree
import urllib
import networkx as nx
import queue


def query_youtube_subscriptions(channel_id):
	url= "/youtube/v3/subscriptions?part=snippet&channelId="+channel_id+"&key=AIzaSyCuYeQya-JMYpWHhK8kCQKxzlrQXam-b0k&maxResults=50"

	connection = http.client.HTTPSConnection("www.googleapis.com")
	connection.request("GET", url)
	response = connection.getresponse()
	data = response.read().decode("utf-8")

	return json.loads(data)

def query_youtube_playlists(channel_id):
	url= "/youtube/v3/playlists?part=snippet&channelId="+channel_id+"&key=AIzaSyCuYeQya-JMYpWHhK8kCQKxzlrQXam-b0k&maxResults=50"

	connection = http.client.HTTPSConnection("www.googleapis.com")
	connection.request("GET", url)
	response = connection.getresponse()
	data = response.read().decode("utf-8")

	return json.loads(data)

def query_youtube_playlistitem(playlist_id):
	url= "/youtube/v3/playlistItems?part=snippet&playlistId="+playlist_id+"&key=AIzaSyCuYeQya-JMYpWHhK8kCQKxzlrQXam-b0k&maxResults=50"

	connection = http.client.HTTPSConnection("www.googleapis.com")
	connection.request("GET", url)
	response = connection.getresponse()
	data = response.read().decode("utf-8")

	return json.loads(data)

def query_youtube_page_for_related_videos(v):
	url= "/watch?v="+v

	connection = http.client.HTTPSConnection("www.youtube.com")
	connection.request("GET", url)
	response = connection.getresponse()
	data = response.read().decode("utf-8")
	d = pq(data)
	related_video = list()
	for li in d("#watch-related li"):
		a = pq(li).find('a').attr('href')
		if a != None:
			related_video.append(a)
	return related_video

def query_youtube_video(v):
	url= "/youtube/v3/videos?part=snippet&id="+v+"&key=AIzaSyCuYeQya-JMYpWHhK8kCQKxzlrQXam-b0k&maxResults=50"

	connection = http.client.HTTPSConnection("www.googleapis.com")
	connection.request("GET", url)
	response = connection.getresponse()
	data = response.read().decode("utf-8")

	return json.loads(data)

	

if __name__ == "__main__":	
	
	start_channel_id = sys.argv[1]
	channel_limit = int(sys.argv[2])
	graph = nx.DiGraph()

	
	download_queue = queue.Queue()
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

				# for related_video in query_youtube_page_for_related_videos(v):
				# 	if not graph.has_node(related_video):
				# 		video_info = query_youtube_video(related_video)
				# 		graph.add_node(v, type='video', channelId=video_info['snippet']['channelId'], title=video_info['snippet']['title'], description=video_info['snippet']['description'], publishedAt=video_info['snippet']['publishedAt'])



		subscriptions = query_youtube_subscriptions(channel_id)
		if 'error' not in subscriptions:
			for item in subscriptions['items']:
				download_queue.put(item['snippet']['resourceId']['channelId'])

		channel_limit -= 1


		
		




	# query_youtube_page('0DRW62VmxYU')
