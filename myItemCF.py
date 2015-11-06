
# -*- coding=utf-8 -*-

import math
import sys
import random
import operator

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

############################################
#      recall = sum(R(u) & T(u))/len(T(u)) #
#      input:train, test, N                #
#      output: recall rate                 #
#      train: dict[userid] = item          #
#      test: dict[userid] = item           #
############################################
def Recall(train, test, itemMatch, N):
	hit = 0
	all = 0
#	print train
	for user in train.keys():
		if user not in test.keys():
			continue
		tu = test[user]
		rank = GetRecommendation(user, train, itemMatch)[:N]
#		print rank
#		print tu
#		print "======================="
		for item, pui in rank:
			if item in tu:
				hit += 1
		all += len(tu)
	return hit / (all * 1.0)

#############################################
#    precision = sum(R(u) & T(u))/len(R(u)) #
#    input: train, test, N                  #
#    output: precision rate                 #
#    input: dict[userid] = item             #
#    output: dict[userid] = item            #
#    N: number itmes in recommendation list #
#############################################
def Precision(train, test, itemMatch, N):
	hit = 0
	all = 0
	for user in train.keys():
		if user not in test.keys():
			continue
		tu = test[user]
		rank = GetRecommendation(user, train, itemMatch)[:N]
		for item, pui in rank:
			if item in tu:
				hit += 1
		all += N
	return hit / (all * 1.0)

#############################################
#   Coverage = len(U R(u))/len(all_items)   #
#    input: train, test, N                  #
#    output: precision rate                 #
#    input: dict[userid] = item             #
#    output: dict[userid] = item            #
#    N: number itmes in recommendation list #
#############################################
def Coverage(train, test, itemMatch, N):
	recommend_items = set()
	all_items = set()
	for user in train.keys():
		for item in train[user]:
			all_items.add(item[0])
		rank = GetRecommendation(user, train, itemMatch)[:N]
		for item in rank:
			recommend_items.add(item)
	return len(recommend_items) / (len(all_items) * 1.0)

#############################################
#    Popularity:用推荐列表中物品的平均流    #
#    行都度量推荐结果的新颖度,如果推荐出的  #
#    物品都很热门，则说明推荐的新颖度低     #
#    否则，说明推荐结果比较新颖             #
#    input: train, test, N                  #
#    output: precision rate                 #
#    input: dict[userid] = item             #
#    output: dict[userid] = item            #
#    N: number itmes in recommendation list #
#############################################
def Popularity(train, test, itemMatch, N):
	item_popularity = dict()
	for user, items in train.items():
		for item in items:
			if item[0] not in item_popularity.keys():
				item_popularity[item[0]] = 0
			item_popularity[item[0]] += 1
	ret = 0
	n = 0
	for user in train.keys():
		rank = GetRecommendation(user, train, itemMatch)
		for item, pui in rank:
			ret += math.log(1 + item_popularity[item])
			n += 1
	if n == 0:
		return 0
	ret /= n * 1.0
	return ret

#######################################################
#       生成用户评分数据结构                          #
#       input:评分数据[[2,1,5], [2,4,2]...]           #
#       output: 1.用户打分字典，2.电影字典            #
#######################################################
def CreateUserRankDic(train):
	#print train
	user_rate_dic = {}
	item_to_user = {}
	for user, items in train.items():
		if user not in user_rate_dic:
			user_rate_dic[user] = items
		else:
			user_rate_dict.append(items)
		for i in items:
			if i[0] not in item_to_user:
				item_to_user[i[0]] = set()
			item_to_user[i[0]].add(user)
#	print "Dic ok\n"
	return user_rate_dic, item_to_user

#################################################################
#			计算与指定用户距离最近的邻居						#
#			input:指定用户id,所有用户字典数据，所有物品字典数据 #
#			output:与指定用户最相邻的邻居列表					#
#################################################################
def CalcNearestNeighbor(userid, users_dic, item_dic):
	neighbors = []
	for item in users_dic[userid]:
		for neighbor in item_dic[item[0]]:
			if neighbor != userid and neighbor not in neighbors:
				neighbors.append(neighbor)

	neighbors_dist = []
	for neighbor in neighbors:
		dist = CalcSimlaryCosDist(users_dic[userid], users_dic[neighbor])
		neighbors_dist.append([dist, neighbor])
	neighbors_dist.sort(reverse=True)
	return neighbors_dist

###################################################
#          余弦相似度                             #
###################################################
def CalcSimlaryCosDist(user1, user2):
	sum_x = 0.0
	sum_y = 0.0
	sum_xy = 0.0
	avg_x = 0.0
	avg_y = 0.0

	for key in user1:
		sum_x += key[1]
	avg_x = sum_x/len(user1)

	for key in user2:
		sum_y += key[1]
	avg_y = sum_y/len(user2)

	for key1 in user1:
		for key2 in user2:
			if key1[0] == key2[0]:
				sum_xy += (key1[1] - avg_x) * (key2[1] - avg_y)
				sum_x += (key1[1] - avg_x) * (key1[1] - avg_x)
				sum_y += (key2[1] - avg_y) * (key2[1] - avg_y)
	if sum_xy == 0.0:
		return 0
	sx_sy = math.sqrt(sum_x * sum_y)
	return sum_xy/sx_sy

def RecommendByUserCF(user, train, K, N):
	user_rate_dic, item_to_user = CreateUserRankDic(train)
	neighbors = CalcNearestNeighbor(user, user_rate_dic, item_to_user)[:K]
	
	recommend_dic = {}
	for neighbor in neighbors:
		neighbor_user_id = neighbor[1]
		items = user_rate_dic[neighbor_user_id]
		for item in items:
			if item not in recommend_dic:
				recommend_dic[item[0]] = neighbor[0] * item[1]
			else:
				recommend_dic[item[0]] += neighbor[0] * item[1]

	recommend_list = []
	for key in recommend_dic.keys():
		recommend_list.append([recommend_dic[key], key])

	rank = recommend_list.sort(reverse=True)[:N]
	user_items = [i[0] for i in user_rate_dic[user]]
	return [[i[1], i[0]] for i in recommend_list]

def GetRecommendation(user, train, itemMatch):
	userRatings = train[user]
	scores = {}
	totalSim = {}

	for item, rating in userRatings:
		for similarity, item2 in itemMatch[item]:
			if item2 in userRatings:
				continue
			if similarity == 0 or rating == 0:
				continue
			scores.setdefault(item2, 0)
			scores[item2] += similarity * rating
			
			totalSim.setdefault(item2, 0)
			totalSim[item2] += similarity

	rankings = [(score/totalSim[item], item) for item, score in scores.items()]
	rankings.sort(reverse = True)
	return [(item, pui) for pui, item in rankings]


def CalculateSimilarItems(item_rate_dic, user_to_item, K):
	result = {}

	for item in item_rate_dic.keys():
		neighbors = CalcNearestNeighbor(item, item_rate_dic, user_to_item)[:K]
		result[item] = neighbors
	return result

if __name__ == '__main__':
	reload(sys)
	sys.setdefaultencoding('utf-8')
	contents = ReadFile("/home/hangc/Downloads/datasets/ml-1m/ratings.dat")

	M = int(sys.argv[1])
	K = int(sys.argv[2])
	N = int(sys.argv[3])

	recall = 0.0
	precision = 0.0
	coverage = 0.0
	popularity = 0.0	

	for i in range(1):
		print i
		random.seed(42)
		k = random.randint(0, M)
		t = random.randint(21, 56)
		tr, te = SplitData(contents, M, k, t)
		
		train = {}
		train_t = {}
		test = {}
		#construct train dic
		for line in tr:
			rate = line.split("::")
			if rate[0] not in train.keys():
				train[rate[0]] = []
			train[rate[0]].append([rate[1], int(rate[2])])
			
			if rate[1] not in train_t.keys():
				train_t[rate[1]] = []
			train_t[rate[1]].append([rate[0], int(rate[2])])
		
		#construct test dic
		for line in te:
			rate = line.split("::")
			if rate[0] not in test.keys():
				test[rate[0]] = []
			test[rate[0]].append([rate[1], int(rate[2])])
		
		#print "train ok\n"
		item_rate_dic, user_to_item = CreateUserRankDic(train_t)
		itemMatch = CalculateSimilarItems(item_rate_dic, user_to_item, K)
		
		recall += Recall(train, test, itemMatch, N)
		precision += Precision(train, test, itemMatch, N)
		coverage += Coverage(train, test, itemMatch, N)
		popularity += Popularity(train, test, itemMatch, N)
	
	recall = recall / (M * 1.0)
	precision = precision / (M * 1.0)
	coverage = coverage / (M * 1.0)
	popularity = popularity / (M * 1.0)

	print "Recall: %.6f" % recall
	print "Precision: %.6f" % precision
	print "Coverage: %.6f" % coverage
	print "Popularity: %.6f" % popularity
