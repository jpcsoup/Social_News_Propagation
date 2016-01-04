# -*- coding: utf-8 -*-
"""
Created on Tue Nov 10 00:36:09 2015

@author: JonathanCampbell
"""
import datetime as dt
from time import sleep

class query_limits:
	def __init__(self, limit, n_min):
		self.limit = limit # n queries / time period
		self.minutes = n_min # time period
		self.start = dt.datetime.now()
		self.q_times = []
		self.q_count = 0

	def difftime(self):
		delta = dt.datetime.now() - self.start
		return(delta.seconds)

	def timecheck(self):
		# Assign times based on API query limits
		cycle_time = 60*self.minutes + 1 # minutes into seconds
		waittime = cycle_time - self.difftime()
		if self.q_count <= self.limit-1:
			return(sleep(0.1))
		else:
			# shift starttimes with query runs
			self.start = self.q_times[-self.limit]
			# Add in waittimes to avoid pull errors
			waittime = cycle_time - self.difftime()
			if waittime > 0:
				# Exceeded limit
				if self.q_count < self.limit:
					self.start = dt.datetime.now()
				print('Limit reached: %s s till next query' % waittime)
				return(sleep(waittime+1)) # Waittime + buffer
			else: # Within limit
				return(sleep(0.1))
	def query(self):
		self.timecheck()
		self.q_count += 1
		self.q_times.append(dt.datetime.now())

# Get info from user:
consumer_key = input('Enter your consumer key: ')
consumer_secret = input('Enter secret key: ') 
access_token = input('Enter your access token: ') 
access_token_secret = input('Enter secret token: ') 
user = input("Enter Twitter handle you'd like to search: ")

import tweepy

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

tmline = api.user_timeline(screen_name = user, count = 200)

q_retweet = query_limits(15, 15)
q_retweeters = query_limits(15,15)
retweets = {}
retweeters = {}
for tweet in reversed(tmline[-100:-1]):
	if tweet.retweet_count <= 100:
		q_retweet.query()
		resultset = api.retweets(id=tweet.id)
		retweets[tweet.id] = {}
		retweets[tweet.id]['id'] = []
		retweets[tweet.id]['tmd'] = []
		retweets[tweet.id]['user'] = []
		retweets[tweet.id]['tree'] = []
		retweets[tweet.id]['branch'] = []
		retweets[tweet.id]['text'] = []
		for result in resultset:
			retweets[tweet.id]['id'].append(result.id)
			retweets[tweet.id]['tmd'].append(result.created_at)
			retweets[tweet.id]['user'].append(result.user.id)
			retweets[tweet.id]['tree'].append(result.retweeted)
			retweets[tweet.id]['branch'].append(result.retweet_count)
			retweets[tweet.id]['text'].append(result.text[0:19])
	else:
		q_retweeters.query()
		c_query = api.retweeters(id=tweet.id, cursor = -1)
		retweeters[tweet.id] = c_query[0]
		next_c = c_query[1][1]
		while next_c != 0:
			q_retweeters.query()
			c_query = api.retweeters(id=tweet.id, cursor=next_c)
			retweeters[tweet.id] += c_query[0]
			next_c = c_query[1][1]

tweets = {}
for tweet in tmline:
    tweets[tweet.id] = tweet

retweets1 = {'NewsTweet': [],
		'tmd': [],
		'text': [],
		'retweet_id': [],
		'retweet_user': [],
		'tree': [],
		'branch': [],
		'difftime': []}

for retweet in retweets:
	retweets1['NewsTweet'] += [retweet]*len(retweets[retweet]['id'])
	retweets1['retweet_user'] += retweets[retweet]['user']
	retweets1['retweet_id'] += retweets[retweet]['id']
	retweets1['tmd'] += retweets[retweet]['tmd']
	retweets1['text'] += retweets[retweet]['text']
	retweets1['branch'] += retweets[retweet]['branch']
	retweets1['tree'] += retweets[retweet]['tree']
	mydate1 = retweets[retweet]['tmd']
	mydate2 = []
	for dtm in mydate1:
		x = tweets[retweet].created_at
		x = dtm - x
		mydate2.append(x)
	retweets1['difftime'] += mydate2

import numpy as np
import pandas as pd

df = pd.DataFrame(retweets1)
df.to_csv('/Users/JonathanCampbell/Desktop/Columbia/2_Thesis/2_DataCollection/pydata5.csv')
