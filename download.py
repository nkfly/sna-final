import sys
import os
import json
import io
import http.client;
from pyquery import PyQuery as pq
from lxml import etree
import urllib


def query_youtube_subscriptions(channel_id):
	url= "/youtube/v3/subscriptions?part=snippet&channelId="+channel_id+"&key=AIzaSyCuYeQya-JMYpWHhK8kCQKxzlrQXam-b0k&maxResults=50"

	connection = http.client.HTTPSConnection("www.googleapis.com")
	connection.request("GET", url)
	response = connection.getresponse()
	data = response.read().decode("utf-8")

	for item in json.loads(data)['items']:
		print(item['snippet']['resourceId']['channelId'])

def query_youtube_playlists(channel_id):
	url= "/youtube/v3/playlists?part=snippet&channelId="+channel_id+"&key=AIzaSyCuYeQya-JMYpWHhK8kCQKxzlrQXam-b0k&maxResults=50"

	connection = http.client.HTTPSConnection("www.googleapis.com")
	connection.request("GET", url)
	response = connection.getresponse()
	data = response.read().decode("utf-8")

	print(json.loads(data))

	# for item in json.loads(data)['items']:
	# 	print(item['snippet']['resourceId']['channelId'])
def query_youtube_playlistitem(playlist_id):
	url= "/youtube/v3/playlistItems?part=snippet&playlistId="+playlist_id+"&key=AIzaSyCuYeQya-JMYpWHhK8kCQKxzlrQXam-b0k&maxResults=50"

	connection = http.client.HTTPSConnection("www.googleapis.com")
	connection.request("GET", url)
	response = connection.getresponse()
	data = response.read().decode("utf-8")

	print(json.loads(data))

def query_youtube_page(v):
	url= "/watch?v="+v

	connection = http.client.HTTPSConnection("www.youtube.com")
	connection.request("GET", url)
	response = connection.getresponse()
	data = response.read().decode("utf-8")
	d = pq(data)
	for li in d("#watch-related li"):
		a = pq(li).find('a').attr('href')
		if a != None:
			print(a)
	

if __name__ == "__main__":
	# query_youtube_subscriptions('UCFqAAh4Tuy_wXWsUAIAVcLQ')
	# query_youtube_playlists('UCFqAAh4Tuy_wXWsUAIAVcLQ')
	# query_youtube_playlistitem('PL93UDiO6Kicxy7hipVOqtNGpdn7xGRsIw')
	query_youtube_page('0DRW62VmxYU')
