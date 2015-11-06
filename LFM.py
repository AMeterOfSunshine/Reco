#!/usr/bin/python 
# -*- coding=utf-8 -*-

import math
import sys
import random
import operator
from basic import AddToMat

class Record:
	def __init__(self, item, user, rate):
		self.item = item
		self.user = user
		self.rate = rate

#########################
#      read file        #
#########################
def ReadFile(file_name):
	contents_lines = []
	f = open(file_name, 'r')
	contents_lines = f.readlines()
	f.close()
	return contents_lines

###############################
#    split data               #
#    input: data, M, k, seed  #
#    output: trainset, testset#
###############################
def SplitData(data, M, k, seed):
	train = []
	test = []
	
	random.seed(seed)
	for t in data:
		if random.randint(0, M) == k:
			test.append(t)
		else:
			train.append(t)
	return train, test

def GetRecord(data):
	record = set()
	for line in data:
		rate = line.split("::")
		t = Record(rate[0], rate[1], int(rate[2]))
		record.add(t)
	return record

def RandSelectNegativeSamples(items_pool, items):
	ret = dict()
	#print items
	for item, rui in items.items():
		ret[item] = rui

	n = 0
	for i in range(0, len(items)*3):
		item = items_pool[random.randint(0, len(items_pool) - 1)]
		if item in ret:
			continue
		ret[item] = 0
		n += 1
		if n > len(items):
			break
	return ret


def LearningLFM(train, F, N, alpha, lambdas):
	user_items = dict()
	items_pool = list()
	for t in train:
		AddToMat(user_items, t.user, t.item, int(t.rate))
		if t.item not in items_pool:
			items_pool.append(t.item)

	[P, Q] = InitLFM(user_items, F)
	
	for step in range(0, N):
		for user, items in user_items.items():
			samples = RandSelectNegativeSamples(items_pool, items)
			for item, rui in samples.items():
				pui = Predict(user, item, P, Q)
				eui = rui - pui
				for f in range(0, F):
					P[user][f] += alpha * (Q[item][f] * eui - lambdas * P[user][f])
					Q[item][f] += alpha * (P[user][f] * eui - lambdas * Q[item][f])
		alpha *= 0.9
	return P, Q

def InitLFM(user_items, F):
	P = dict()
	Q = dict()
	
	for user, items in user_items.items():
		if user not in P:
			P[user] = [random.random() / math.sqrt(F) for x in range(0, F)]
		for item, rui in items.items():
			if item not in Q:
				Q[item] = [random.random() / math.sqrt(F) for x in range(0, F)]
	return P, Q

def Predict(user, item, P, Q):
	return sum(P[user][f] * Q[item][f] for f in range(0, len(P[user])))

###########################################
#  Recommend result to user               #
#  input:                                 #
#  @param user: user to recommned         #
#  @param items: item set for dataset     #
#  @param P:                              #
#  @param Q:                              #
#  output:                                #
#     recommend list[item, rate] for user #
###########################################
def Recommend(user, items, P, Q):
	rank = dict()
	for f, puf in P[user].items():
		for item in items:
			if item not in rank:
				rank[item] += puf * Q[item][f]
	return rank

def RMSE(records, P, Q):
	user_item = dict()
	res = 0.0

	for r in records:
		AddToMat(user_item, r.user, r.item, int(r.rate))
	
	for user, items in user_item.items():
		for item, rui in items.items():
			if user not in P or item not in Q:
				continue
			predict = Predict(user, item, P, Q)
			res += (int(rui) - predict) * (int(rui) - predict)

	return math.sqrt(res / (1.0 * len(records)))

if __name__ == '__main__':
	reload(sys)
	sys.setdefaultencoding('utf-8')
	contents = ReadFile("/home/hangc/Downloads/datasets/ml-1m/ratings.dat")

	M = int(sys.argv[1])
	F = int(sys.argv[2])
	alpha = float(sys.argv[3])
	lambdas = float(sys.argv[4])
	ratio = int(sys.argv[5])
	N = int(sys.argv[6])
	n = int(sys.arvg[7])

	rmse_train = 0.0
	rmse_test = 0.0

	for i in range(0, n):
		print i
		random.seed(42)
		k = random.randint(0, M)
		t = random.randint(21, 56)
		tr, te = SplitData(contents, M, k, t)
		
		train = set()
		test = set()
		
		train = GetRecord(tr)
		test = GetRecord(te)	
		
		#print "train ok\n"
		[P, Q] = LearningLFM(train, F, N, alpha, lambdas)

		print "=================================="
		print P
		print "//////////////////////////////////"
		print Q
		print "=================================="
		rmse_train += RMSE(train, P, Q) 
		rmse_test += RMSE(test, P, Q)
		print "----------------------------------"
	
	rmse_train /= n
	rmse_test /= n

	print "rmse_train: %.6f" % rmse_train
	print "rmse_test: %.6f" % rmse_test
