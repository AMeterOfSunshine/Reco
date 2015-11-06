#!/usr/bin/python
# -*- coding=utf-8 -*-
import math
import sys
from texttable import Texttable


###############################################
#				计算相似余弦				  #
###############################################
def calcSimlaryCosDist(user1, user2):
	sum_x = 0.0
	sum_y = 0.0
	sum_xy = 0.0
	avg_x = 0.0
	avg_y = 0.0
	
	for key in user1:
		avg_x += key[1]
	avg_x = avg_x/len(user1)

	for key in user2:
		avg_y += key[1]
	avg_y = avg_y/len(user2)

	for key1 in user1:
		for key2 in user2:
			if key1[0] == key2[0]:
				sum_xy += (key1[1]-avg_x) * (key2[1]-avg_y)
				sum_y += (key2[1]-avg_y) * (key2[1]-avg_y)
				sum_x += (key1[1]-avg_x) * (key1[1]-avg_x)

	if sum_xy == 0.0:
		return 0

	sx_sy = math.sqrt(sum_x*sum_y)
	return sum_xy/sx_sy

#################################################################
#			计算与指定用户距离最近的邻居						#
#			input:指定用户id,所有用户字典数据，所有物品字典数据 #
#			output:与指定用户最相邻的邻居列表					#
#################################################################
def calcNearestNeighbor(userid, users_dic, item_dic):
	#取出目标用户看过的所有电影,对于与该用户看过相同电影的用户，均将其加入到
	#neighbors列表中
	neighbors = []
	for item in users_dic[userid]:
		for neighbor in item_dic[item[0]]:
			if neighbor != userid and neighbor not in neighbors:
				neighbors.append(neighbor)

	#遍历neighbors列表，计算所有用户与目标用户的相似度
	neighbors_dist = []
	for neighbor in neighbors:
		dist = calcSimlaryCosDist(users_dic[userid], users_dic[neighbor])
		neighbors_dist.append([dist, neighbor])
	neighbors_dist.sort(reverse=True)
	return neighbors_dist

#######################################################
#		生成用户评分数据结构						  #
#		input:评分数据[[2,1,5], [2,4,2]...]			  #
#		output: 1.用户打分字典，2.电影字典			  #
#######################################################
def createUserRankDic(rates):
	user_rate_dic = {}
	item_to_user = {}
	for i in rates:
		user_rank = (i[1], i[2])
		if i[0] in user_rate_dic:
			user_rate_dic[i[0]].append(user_rank)
		else:
			user_rate_dic[i[0]] = [user_rank]

		if i[1] in item_to_user:
			item_to_user[i[1]].append(i[0])
		else:
			item_to_user[i[1]] = [i[0]]

	return user_rate_dic, item_to_user

##################################################################
#    解压rating信息，格式:用户id::电影id::用户rating::timestamp  #
#    input: 信息集合											 #
#    output: 已解压的排名信息									 #
##################################################################
def getRatingInformation(ratings):
	rates = []
	for line in ratings:
		rate = line.split("::")
		rates.append([int(rate[0]), int(rate[1]), int(rate[2])])
	return rates

####################################################
#    使用UserCF算法进行推荐                        #
#    input: filename, user_id, number of neighbor  #
#    output: 推荐的电影ID, 输入用户的电影列表，    #
#            电影对应用户的反序表，邻居列表        #
####################################################
def recommendByUserCF(file_name, userid, k=5):
	# read data
	test_contents = readFile(file_name)
	#将数据格式化为二维数组List[[用户id，电影id, 电影评分]...]
	test_rates = getRatingInformation(test_contents)

	#格式化为字典数据
	#	1. 用户字典：dic[用户id] = [(电影id, 电影评分)...]
	#	2. 电影字典：dic[电影id] = [user_id1, user_id2...]
	test_dic, test_item_to_user = createUserRankDic(test_rates)

	neighbors = calcNearestNeighbor(userid, test_dic, test_item_to_user)[:k]

	#生成{movie:dist}推荐字典
	recommend_dic = {}
	for neighbor in neighbors:
		neighbor_user_id = neighbor[1]
		movies = test_dic[neighbor_user_id]
		for movie in movies:
			if movie[0] not in recommend_dic:
				recommend_dic[movie[0]] = neighbor[0]*movie[1]
			else:
				recommend_dic[movie[0]] += neighbor[0]*movie[1]

	#根据推荐字典生成推荐列表
	recommend_list = []
	for key in recommend_dic:
		recommend_list.append([recommend_dic[key], key])
	
	recommend_list.sort(reverse=True)
	
	user_movies = [i[0] for i in test_dic[userid]]
	
	return [i[1] for i in recommend_list], user_movies, test_item_to_user, neighbors

#############################
#     read file             #
#############################
def readFile(file_name):
	contents_lines = []
	f = open(file_name, 'r')
	contents_lines = f.readlines()
	f.close()
	return contents_lines

def getMoviesList(file_name):
	movies_contents = readFile(file_name)
	movies_info = {}
	for movie in movies_contents:
		movie_info = movie.split("::")
		#print movie_info
		movies_info[int(movie_info[0])] = movie_info[1:]
	return movies_info


if __name__ == '__main__':
	reload(sys)
	sys.setdefaultencoding('utf-8')
	movies = getMoviesList("/home/hangc/Downloads/datasets/ml-1m/movies.dat")	
	recommend_list, user_movie, items_movie, neighbors = recommendByUserCF("/home/hangc/Downloads/datasets/ml-1m/ratings.dat", 179, 80)
	neighbors_id = [i[1] for i in neighbors]
	table = Texttable()
	table.set_deco(Texttable.HEADER)
	table.set_cols_dtype(['t',	#text
						  't',	#float (decimal)
						  't',])#automatic
	table.set_cols_align(["1", "1", "1"])
	rows = []
	rows.append([u"movie name", u"release", u"from userid"])
	for movie_id in recommend_list[:20]:
		from_user = []
		for user_id in items_movie[movie_id]:
			if user_id in neighbors_id:
				from_user.append(user_id)
		rows.append([movies[movie_id][0], movies[movie_id][1], ""])
	table.add_rows(rows)
	print table.draw()
