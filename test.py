import praw
import numpy as np
import scipy as sp
import scipy.optimize
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid.axislines import SubplotZero
import sys
import getopt
import time

def main():
	opts, args = getopt.getopt(sys.argv[1:], 'u:', ['URL='])
	print("Number of arguments: " + str(len(sys.argv)))

	if len(sys.argv) > 1:
		threadID = str(sys.argv[1])
	else:
		threadID = '3jms68'

	print("Using thread: " + threadID)

	r = praw.Reddit(user_agent='test script /u/Speff')
	#r.set_oauth_app_info(client_id='aDjUAlJ0Cb17pA',
	#						client_secret='AeJjd7CLEUt7wyMmTVhP6kidhLc',
	#						redirect_uri='http://127.0.0.1:65010/'
	#						'authorize_callback')
	#url = r.get_authorize_url('uniqueKey', 'identity', True)
	#print(url)
	#access_information = r.get_access_information('lfJfhgKEDDUzgwY9a2tcVtVYMnc')
	#r.set_access_credentials(**access_information)
	#authenticated_user = r.get_me()
	#print(authenticated_user.name, authenticated_user.link_karma)

	start = float(time.time())
	submission = r.get_submission(submission_id=threadID, comment_sort="confidence")
	submission.replace_more_comments(limit=None, threshold=1)
	print("Seconds to process thread: " + str(time.time()-start))
	flat_comments = praw.helpers.flatten_tree(submission.comments)

	submission_score = submission.score
	submission_time = submission.created_utc

	comment_score = []
	comment_time = []
	commentInfo = []
	#comment_body = []

	print("Number of comments: " + str(len(flat_comments)))

	for x in flat_comments:
	#	print(x.body + "\n")
		comment_score.append(abs(x.score-1)+1)
		comment_time.append((x.created_utc - submission_time)/(60))
	#	comment_body.append(x.body)


	data = np.column_stack((comment_time, comment_score))

	uniques, count = np.unique(data[:,1], return_counts=True)
	unvoted = 0.0
	for x in range(0, len(uniques)):
		if(uniques[x]) == 1:
			unvoted = count[x]

	unvoted = unvoted / len(comment_time)

	if 1:
		fig = plt.figure(1)
		ax = SubplotZero(fig, 111)
		fig.add_subplot(ax)

		ax.axis["left"].set_label('Points')
		ax.axis["bottom"].set_label('Time (minutes)')

		xRange = np.amax(data[:,0]) - np.amin(data[:,0])
		yRange = np.amax(data[:,1]) - np.amin(data[:,1])

		plt.axhline(1, color='gray', linestyle='--')
		plt.axhline(0, color='black')
		plt.axvline(0, color='black')

		xFit = np.linspace(np.amin(data[:,0]) - xRange*0.1, np.amax(data[:,0]) + xRange*0.1, 1000)

		A, K, C = fit_exp_nonlinear(data[:,0], data[:,1])
		fit_y = 2*model_func(xFit, A, K, C)


		print("Best-fit polynomial coefficient(s): " + str((A, K, C)))

		ax.axis([np.amin(data[:,0]) - xRange*0.1, np.amax(data[:,0]) + xRange*0.1, np.amin(data[:,1]) - yRange*0.1, np.amax(data[:,1]) + yRange*0.1])
		ax.plot(data[:,0], data[:,1], '.')
		ax.plot(xFit, fit_y, '-', color='darkred')

		ax.text(0.75*xRange + np.amin(data[:,0]), 0.9*yRange + np.amin(data[:,1]), str(round(unvoted,3)*100) + '% unvoted \n', fontsize=15)

		plt.show()


def model_func(t, A, K, C):
    #return A * np.exp(K * t) + C
    #return A*t*t + K*t + C
    n = 0;
    for n in range(0, len(t)):
    	if(t[n] == 0):
    		t[n] = 1
    	n = n + 1

    return A/(t*t*t) + K/(t*t) + C/t + 1

def fit_exp_nonlinear(t, y):
    opt_parms, parm_cov = sp.optimize.curve_fit(model_func, t, y, maxfev=1000)
    A, K, C = opt_parms
    return A, K, C

if __name__ == '__main__':
    main()