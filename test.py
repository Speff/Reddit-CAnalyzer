import praw
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid.axislines import SubplotZero

r = praw.Reddit(user_agent='test script /u/Speff')
submission = r.get_submission(submission_id='3c4gnt', comment_sort="confidence")

submission.replace_more_comments(limit=0, threshold=0)
flat_comments = praw.helpers.flatten_tree(submission.comments)

submission_score = submission.score
submission_time = submission.created_utc

comment_score = []
comment_time = []
commentInfo = []
#comment_body = []



for x in flat_comments:
#	print(x.body + "\n")
	comment_score.append(x.score)
	comment_time.append((x.created_utc - submission_time)/60)
#	comment_body.append(x.body)


#f = open('out.txt', 'w', encoding='utf-8')

#for x in range(0,len(comment_time)):
#	f.write(str(comment_time[x] - submission_time) + "\t" + str(comment_score[x]))
#	f.write("\n")
#	f.write("str(comment_body[x]")
#	f.write("\n")

#f.close()

data = np.column_stack((comment_time, comment_score))

uniques, count = np.unique(data[:,1], return_counts=True)
unvoted = 0.0
for x in range(0, len(uniques)):
	if(uniques[x]) == 1:
		unvoted = count[x]

unvoted = unvoted / len(comment_time)

font = {'family' : 'serif',
		'color'  : 'darkred',
		'weight' : 'normal',
		'size'   : 16,
		}

if 1:
	fig = plt.figure(1)
	ax = SubplotZero(fig, 111)
	fig.add_subplot(ax)

	ax.axis["left"].set_label('Points')
	ax.axis["bottom"].set_label('Time (minutes)')

	xRange = np.amax(data[:,0]) - np.amin(data[:,0])
	yRange = np.amax(data[:,1]) - np.amin(data[:,1])

	ax.axis([np.amin(data[:,0]) - xRange*0.1, np.amax(data[:,0]) + xRange*0.1, np.amin(data[:,1]) - yRange*0.1, np.amax(data[:,1]) + yRange*0.1])

	plt.axhline(1, color='gray', linestyle='--')
	plt.axhline(0, color='black')
	plt.axvline(0, color='black')

	fitted = np.polyfit(data[:,0], data[:,1], 3)
	xFit = np.linspace(np.amin(data[:,0]) - xRange*0.1, np.amax(data[:,0]) + xRange*0.1, 100)
	yFit = np.poly1d(fitted)

	ax.plot(data[:,0], data[:,1], '.')
	ax.plot(xFit, yFit(xFit), '-', color='darkred')

	ax.text(0.75*xRange + np.amin(data[:,0]), 0.9*yRange + np.amin(data[:,1]), str(round(unvoted,3)*100) + '% unvoted', fontsize=15)

	plt.show()

