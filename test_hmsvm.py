import cvxopt as co
import numpy as np
import pylab as pl
import matplotlib.pyplot as plt

from ssvm import SSVM
from latentsvdd import LatentSVDD
from structured_ocsvm import StructuredOCSVM
from structured_pca import StructuredPCA
from toydata import ToyData

from so_hmm import SOHMM

if __name__ == '__main__':
	DIMS = 2
	LENS = 150
	EXMS = 200

	# training data
	mean = 0.0
	cnt = 0 
	trainX = []
	trainY = []
	for i in range(EXMS):
		(exm,lbl) = ToyData.get_2state_gaussian_seq(LENS,dims=DIMS)
		if i<4:
			(exm,lbl) = ToyData.get_2state_gaussian_seq(LENS,dims=DIMS,means1=[1,-3],means2=[3,7],vars1=[1,1],vars2=[1,1])
		mean += co.matrix(1.0, (1,LENS))*exm.trans()
		cnt += LENS
		trainX.append(exm)
		trainY.append(lbl)

	mean = mean / float(cnt)
	print mean
	#mean = co.matrix([0,0])
	for i in range(EXMS):
		if (i<10):
			pos = int(np.single(co.uniform(1))*float(LENS)*0.8 + 4.0)
			print pos
			trainX[i][1,pos] = 100.0
		for d in range(DIMS):
			trainX[i][d,:] = trainX[i][d,:]-mean[d]

	hmm = SOHMM(trainX,trainY,num_states=2)

	ssvm = SSVM(hmm)
	(sol, slacks) = ssvm.train()
	jfm = hmm.get_joint_feature_map(0)
	#print jfm


	#print '----------'
	#print hmm.get_jfm_norm2(0,trainY[0])
	#print hmm.get_jfm_norm2(0,trainY[1])
	#print '----------'

	lsvm = StructuredOCSVM(hmm, C=1.0/(EXMS*0.9))
	#(lsol, lats, thres) = lsvm.train_dc_svm()
	(lsol, lats, thres) = lsvm.train_dc(max_iter=40)


	# test data
	#(exm,lbl) = ToyData.get_2state_gaussian_seq(LENS,dims=DIMS)
	(vals, pred) = ssvm.apply(SOHMM([exm],num_states=2))

	plt.figure()
	for d in range(DIMS):
		plt.plot(range(LENS),exm[d,:].trans() + 5.0*d,'-r')
	
	(anom_score, scores) = hmm.get_scores(lsol,EXMS-1)
	plt.plot(range(LENS),scores.trans() + 5.0,'-b')

	plt.plot(range(LENS),pred[0].trans() - 5,'-g')
	plt.plot(range(LENS),lats[EXMS-1].trans() - 7.5,'-r')
	plt.plot(range(LENS),lbl.trans() - 10,'-b')
	plt.show()

	for i in range(20):
		plt.plot(range(LENS),lats[i].trans() + i*4,'-r')
		plt.plot(range(LENS),trainY[i].trans() + i*4,'-b')
		
		(anom_score, scores) = hmm.get_scores(lsol,i,lats[i])
		plt.plot(range(LENS),scores.trans() + i*4,'-g')
	plt.show()

	print('finished')