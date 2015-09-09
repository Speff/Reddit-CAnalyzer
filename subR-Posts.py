import praw
import OAuth2Util

import numpy as np
import scipy as sp
import scipy.optimize
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.colors import Normalize

from mpl_toolkits.axes_grid.axislines import SubplotZero

import sys
import getopt
import time

secInDay = 86400
secInHour = 3600
sr = "wtf"



def main():
	getSRData()
	#getFileData()

	PPP = np.linspace(0,0,24)
	for post in postData:
		PPP[int(post[0])] += post[1]

	PPP = PPP/postInHourData

	bgC = '#050505'
	barC = '#151515'
	dotC = '#AFAFAF'
	lineC = '#7F7F7F'
	ticC = '#CECECE'

	colors  = np.multiply(.1,postData[:,1])
	norm = MidpointNormalize(midpoint=1)



	fig, ax1 = plt.subplots()
	ax1.set_axis_bgcolor(bgC)
	ax1.bar(np.linspace(0, 23, 24), postInHourData, color = barC, width = 1)
	ax2 = ax1.twinx()
	ax2.scatter(postData[:,0], postData[:,1], 
				s = 10,
				c = colors,
				cmap = cm.gray,
				norm = norm,
				edgecolor = '',
				marker=".")
	#ax2.plot(postData[:,0], postData[:,1], '.', color = dotC)
	ax3 = ax2.twinx()
	ax3.plot(np.linspace(0, 24, 24), PPP, '-', color = lineC)
	#ax3.axis('off')

	ax1.yaxis.tick_right()
	ax2.yaxis.tick_left()
	#ax3.yaxis.tick_left()
	ax3.axis('off')

	plt.gca().set_xlim(left=0)
	plt.gca().set_xlim(right=24)
	ax1.set_ylim(bottom=0)
	ax2.set_ylim(bottom=0)
	ax3.set_ylim(bottom=0)
	plt.show()

def getFileData():
	global postData, postInHourData

	postData = [0, 0]
	postInHourData = np.linspace(0,0,24)

	f = open("Post-list.txt", "r",  encoding="utf-8")

	for line in f.read().split('\n'):
		fileScoreString, fileTimeString, fileTitle = line.split("\t")
		fileScore = int(fileScoreString)
		fileTime = ((float(fileTimeString) - 3600*5)%secInDay)/3600
		postData = np.vstack((postData, [fileTime%secInDay, int(fileScore)]))
		postInHourData[int(fileTime%3600)] += 1

	f.close()

def getSRData():
	global postData, postInHourData, r

	signIn()

	subreddit = r.get_subreddit(sr)
	postData = [0, 0]
	postInHourData = np.linspace(0,0,24)
	startTime = int(utc_mktime((2015,9,4,0,0,0)) + 5*secInHour)
	daysToRecord = 1

	signIn()

	f = open("Post-list.txt", "w",  encoding="utf-8")

	for days in range(0, daysToRecord):
		# Search (Start UTC + currentForLoopDay + redditSearchOffsetBug) to (Start UTC + currentForLoopDay+1 + redditSearchOffsetBug)
		for post in r.search("timestamp:" + str(startTime + secInDay*days + 8*secInHour) + ".." + str(startTime + secInDay*(days+1) + 8*secInHour),
								sr, sort="new", syntax='cloudsearch', limit=1000):
			f.write(str(post.score) + "\t" + str(post.created_utc) + "\t" + post.title + "\n")
			postData = np.vstack((postData, [(post.created_utc - (startTime + secInDay*days))/secInHour, post.score]))
			postInHourData[int((post.created_utc - (startTime + secInDay*days))/secInHour)] += 1

		print("Day " + str(days+1))

	f.close()

def signIn():
	global r, o

	r = praw.Reddit(user_agent='test script /u/Speff')
	o = OAuth2Util.OAuth2Util(r)
	r.config.api_request_delay = 1

def utc_mktime(utc_tuple):
    """Returns number of seconds elapsed since epoch

    Note that no timezone are taken into consideration.

    utc tuple must be: (year, month, day, hour, minute, second)

    """

    if len(utc_tuple) == 6:
        utc_tuple += (0, 0, 0)
    return time.mktime(utc_tuple) - time.mktime((1970, 1, 1, 0, 0, 0, 0, 0, 0))

class MidpointNormalize(Normalize):
    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        self.midpoint = midpoint
        Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        # I'm ignoring masked values and all kinds of edge cases to make a
        # simple example...
        x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y))

if __name__ == '__main__':
    main()