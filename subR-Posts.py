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

DARK_THEME = 0

SEC_IN_DAY = 86400
SEC_IN_HOUR = 3600
CST_OFFSET = 5
PD_TIMESTAMP_INDEX = 0
PD_VOTE_INDEX = 1
PD_COMMENT_INDEX = 2
PD_CODE_INDEX = 3

def main():
	sr = "anime"
	timeTup = (2015,2,2,0,0,0)
	nDays = 1
	fileAccess = 1

	if not fileAccess:
		postData = getSRData(sr, timeTup, nDays)
		postData = convertPostDataUTCtoRelativeHours(postData, timeTup)
	else:
		postData = getFileData()

	

	postsPerHour, avgPostPointsPerHour = processPostData(postData)

	plotEverything(postData, postsPerHour, avgPostPointsPerHour)

def plotEverything(postData, postsPerHour, avgPostPointsPerHour):
	# Set up color schema ----------------------------
	if DARK_THEME:
		bgC = '#050505'
		barC = '#151515'
		dotC = '#AFAFAF'
		lineC = '#7F7F7F'
		ticC = '#CECECE'
		dotSize = 10
		normMid = 1
	else:
		bgC = '#FFFFFF'
		barC = '#AAAAAA'
		dotC = '#202020'
		lineC = '#202020'
		ticC = '#202020'
		dotSize = 100
		normMid = 7000

	colors  = np.multiply(.1,postData[:,1])
	norm = MidpointNormalize(midpoint=1)

	# Plot initialization -------------------------------
	fig, ax1 = plt.subplots()

	# ax1 = Bar plot displaying # posts per hour --------
	ax1.set_axis_bgcolor(bgC)
	ax1.bar(np.linspace(0, 23, 24), postsPerHour, color = barC, width = 1)

	# ax2 = Scatter plot displaying points per post -----
	ax2 = ax1.twinx()
	if DARK_THEME:
		ax2.scatter(postData[:,0], postData[:,1], 
				s = dotSize,
				c = colors,
				cmap = cm.gray,
				norm = norm,
				edgecolor = '',
				marker=".")
	else:
		ax2.plot(postData[:,0], postData[:,1], ".", color = dotC)

	# ax3 = Average points per post per hour ------------
	ax3 = ax2.twinx()
	ax3.plot(np.linspace(0, 24, 24), avgPostPointsPerHour, '-', color = lineC)

	# Axis settings -------------------------------------
	ax1.yaxis.tick_right()
	ax2.yaxis.tick_left()
	#ax3.yaxis.tick_left()
	ax3.axis('off')

	plt.gca().set_xlim(left=0)
	plt.gca().set_xlim(right=24)
	ax1.set_ylim(bottom=0)
	ax2.set_ylim(bottom=0)
	ax3.set_ylim(bottom=0)

	# Display everything ---------------------------------
	plt.show()

def getFileData():
	postData = [0,0,0]

	f = open("Post-list.txt", "r",  encoding="utf-8")

	for line in f.read().split('\n'):
		fileScoreString, fileTimeString, fileTitle, fileNumCommentsString = line.split("\t")
		fileTime = ((float(fileTimeString) - SEC_IN_HOUR*CST_OFFSET)%SEC_IN_DAY)/SEC_IN_HOUR
		postData = np.vstack((postData, [fileTime, int(fileScoreString), int(fileNumCommentsString)]))

	f.close()

	return postData

def getSRData(sr, timeTuple, daysToRecord):
	postData = (0,0,0)

	r = signIn()

	subreddit = r.get_subreddit(sr)
	startTime = convertToUTC(timeTuple)

	#signIn()

	f = open("Post-list.txt", "w",  encoding="utf-8")

	for days in range(0, daysToRecord):
		# Search (Start UTC + currentForLoopDay + redditSearchOffsetBug) to (Start UTC + currentForLoopDay+1 + redditSearchOffsetBug)
		for post in r.search("timestamp:" + str(startTime + SEC_IN_DAY*days + 8*SEC_IN_HOUR) + ".." + str(startTime + SEC_IN_DAY*(days+1) + 8*SEC_IN_HOUR),
								sr, sort="new", syntax='cloudsearch', limit=1000):
			f.write(str(post.score) + "\t" + str(post.created_utc) + "\t" + post.title +
						"\t" + str(post.num_comments) + "\n")
			# postData[time, upmods]
			### time content has time in hour units starting at tuple startTime
			postData = np.vstack((postData, [post.created_utc, post.score, post.num_comments]))
			#print(type(post.created_utc))
		print("Day " + str(days+1))

	f.close()

	return postData

def convertPostDataUTCtoRelativeHours(postData, timetup):
	startTime = convertToUTC(timetup)

	for post in postData:
		print(type(post[PD_TIMESTAMP_INDEX]))
		# Normalize UTC to startTime
		post[PD_TIMESTAMP_INDEX] = post[PD_TIMESTAMP_INDEX] - startTime
		# Days elapsed = (Normalized UTC - [Normalized UTC % Seconds in a day]) / Seconds in a day
		daysElapsed = (post[PD_TIMESTAMP_INDEX] - ((post[PD_TIMESTAMP_INDEX])%SEC_IN_DAY))/SEC_IN_DAY
		# Timestamp in normalized (24hr) hours = (Normalized UTC - #SecondsElapsed(per day passed))/seconds in an hour
		post[PD_TIMESTAMP_INDEX] = (post[PD_TIMESTAMP_INDEX] - SEC_IN_DAY*daysElapsed)/SEC_IN_HOUR

	return postData

def processPostData(postData):
	postsPerHour = np.linspace(0,0,24)
	avgPostPointsPerHour = np.linspace(0,0,24)

	for post in postData:
		postsPerHour[int(post[PD_TIMESTAMP_INDEX])] += 1
		avgPostPointsPerHour[int(post[PD_TIMESTAMP_INDEX])] += post[PD_VOTE_INDEX]

	avgPostPointsPerHour = avgPostPointsPerHour/postsPerHour

	return postsPerHour, avgPostPointsPerHour

def signIn():
	r = praw.Reddit(user_agent='test script /u/Speff')
	o = OAuth2Util.OAuth2Util(r)
	r.config.api_request_delay = 1

	return r

def convertToUTC(utc_tuple):
	return int(utc_mktime(utc_tuple) + CST_OFFSET*SEC_IN_HOUR)

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