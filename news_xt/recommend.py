# -*- coding: utf-8 -*-

#import xlrd
import math
import random
#import pandas as pd
import numpy as np
#import time
from tqdm import trange
#import pymysql

#基于用户的推荐
#算出new_users倒排表
#计算出每个用户之间的相似度矩阵
class  UserIIF():
    def __init__(self,train):
        self.user_news = train
        self.C = {}

    # 算出new_users倒排表
    def Set(self):
        num = {}
        new_users = {}
        for user in self.user_news:
            for item in self.user_news[user]:
                if item not in new_users:
                    new_users[item] = []
                new_users[item].append(user)
        #算出相似度矩阵
        for new in new_users:
            users = new_users[new]
            for i in range(len(users)):
                u = users[i]
                if u not in num:
                    num[u] = 0;
                num[u] += 1
                if u not in self.C:
                    self.C[u] = {}
                for j in range(len(users)):
                    if j == i: continue
                    v = users[j]
                    if v not in self.C[u]:
                        self.C[u][v] = 0
                    self.C[u][v] += 1 / math.log(1 + len(users))
        for u in self.C:
            for v in self.C[u]:
                self.C[u][v] /= math.sqrt(num[u]*num[v])
        sorted_user_news = {k : list(sorted(v.items(), key = lambda x :x[1], reverse = True)) for k , v in self.C.items()}
        return sorted_user_news
#推荐前N个新闻
    def GetRecommendation(self,user, K, N):
        news = {}#要推荐的全部新闻
        seen_news = set(self.user_news[user])#看过的新闻
        
        sorted_user_news = self.Set()
        for u,_ in sorted_user_news[user][:K]:
            for new in self.user_news[u]:
                if new not in seen_news:
                    if new not in news:
                        news[new] = 0
                    news[new] += self.C[user][u]#每个新闻的推荐度
        recs = list(sorted(news.items(), key=lambda x: x[1], reverse=True))[:N]
        return recs
    
#基于新闻的推荐
class ItemCF():
    #新闻之间的相似度
    def __init__(self,train):
        self.user_news = train
        self.C = {}
    def Set(self):
        num= {}
        for user in self.user_news:
            news = self.user_news[user]
            for i in range(len(news)):
                u = news[i]
                if u not in num:
                    num[u] = 0
                num[u] += 1
                if u not in self.C:
                    self.C[u] = {}
                for j in range(len(news)):
                    if i == j : continue
                    v = news[j]
                    if v not in self.C[u]:
                        self.C[u][v] = 0
                    self.C[u][v] += 1
        for u in self.C:
            for v in self.C[u]:
                self.C[u][v] /= math.sqrt(num[u]*num[v])
        # 对每个新闻和他相似的新闻进行相似度排序
        sorted_user_news = {k: list(sorted(v.items(), key= lambda x:x[1], reverse = True)) for k, v in self.C.items()}
        return sorted_user_news
    def GetRecommendation(self,user, K, N):
        news = {}
        sorted_user_news = self.Set()
        seen_news = set(self.user_news[user])
        for new in self.user_news[user]:
            for u,_ in sorted_user_news[new][:K]:#每个新闻取出前K大的新闻
                if u not in seen_news:
                    if u not in news:
                        news[u] = 0
                    news[u] += self.C[new][u]
        rest = list(sorted(news.items(), key = lambda x : x[1], reverse= True))[:N]
        return rest
    
#基于热度的推荐
#class MostPopular():
#    def __init__(self,train):
#        self.user_news = train
#    def Set(self):
#        news = {}
#        for user in self.user_news:
#            for new in self.user_news[user]:
#                if new not in news:
#                    news[new] = 0
#                news[new] += 1
#        return news
#    def GetRecommendation(self ,user, K, N):
#        news = set(self.user_news[user])
#        News = self.Set()
#        rec_news = {k:News[k] for k in News if k not in news}
#        rec_news = list(sorted(rec_news.items(), key = lambda x:x[1], reverse= True))
#        return rec_news[:N]


# 随机推荐：针对没有任何历史记录的用户
class Random():
    def __init__(self,train):
        self.user_news = train
        self.news = {}
    def Set(self):
        for user in self.user_news:
            for new in self.user_news[user]:
                self.news[new] = 1
    def GetRecommendation(self,user,K,N):
        # 随机推荐N个未见过的
        self.Set()
        user_new = set(self.user_news[user])
        rec_news = {k: self.news[k] for k in self.news if k not in user_new}
        rec_news = list(rec_news.items())
        random.shuffle(rec_news)
        return rec_news[:N]

# 基于SVD的协同过滤算法推荐
class LFM():
    def __init__(self,train,ratio,lr,step,K, lmbda):
        self.user_news = train
        self.ratio = ratio
        self.lr = lr
        self.step = step
        self.K = K
        self.lmbda = lmbda
        self.P = {}
        self.Q = {}
        self.news = []
        self.pops =[]
    '''
    :params: train, 训练数据
    :params: ratio, 负采样的正负比例
    :params: K, 隐语义个数
    :params: lr, 初始学习率
    :params: step, 迭代次数
    :params: lmbda, 正则化系数
    :params: N, 推荐TopN物品的个数
    :return: GetRecommendation, 获取推荐结果的接口
    '''
    def Set(self):
        all_news = {}
        for user in self.user_news:
            for new in self.user_news[user]:
                if new not in all_news:
                    all_news[new] = 0
                all_news[new] += 1
        all_news = list(all_news.items())
        self.news = [x[0] for x in all_news]
        self.pops = [x[1] for x in all_news]
    # 负采样函数(注意！！！要按照流行度进行采样)
    def nSample(self,data):
        self.Set()
        new_data = {}
        # 正样本
        for user in data:
            if user not in new_data:
                new_data[user] = {}
            for new in data[user]:
                new_data[user][new] = 1
        # 负样本
        for user in new_data:
            seen = set(new_data[user])
            pos_num = len(seen)
            new = np.random.choice(self.news, int(pos_num * self.ratio * 3), self.pops)
            new = [x for x in new if x not in seen][:int(pos_num * self.ratio)]
            new_data[user].update({x: 0 for x in new})

        return new_data

    # 训练
    def train(self):
        self.Set()
        for user in self.user_news:
            self.P[user] = np.random.random(self.K)
        for new in self.news:
            self.Q[new] = np.random.random(self.K)
        for s in trange(self.step):
            data = self.nSample(self.user_news)
            for user in data:
                for new in data[user]:
                    eui = data[user][new] - (self.P[user] * self.Q[new]).sum()
                    self.P[user] += self.lr * (self.Q[new] * eui - self.lmbda * self.P[user])
                    self.Q[new] += self.lr * (self.P[user] * eui - self.lmbda * self.Q[new])
            self.lr *= 0.9  # 调整学习率

    # 获取接口函数
    def GetRecommendation(self,user,N):
        self.train()
        seen_news = set(self.user_news[user])
        recs = {}
        print(1)
        for new in self.news:
            if new not in seen_news:
                recs[new] = (self.P[user] * self.Q[new]).sum()
        recs = list(sorted(recs.items(), key=lambda x: x[1], reverse=True))[:N]
        return recs

'''
if __name__ == '__main__':
    #读取文件
    
    df = xlrd.open_workbook('test1.xlsx')
    sheet = df.sheets()[0]
    user_news = {}
    nrows = sheet.nrows
    for i in range(nrows):
        u = int(sheet.row_values(i)[0])
        if u not in user_news:
            user_news[u] = []
        v = sheet.row_values(i)[1:len(sheet.row_values(i))]
        for i in v:
            user_news[u].append(int(i))
    
    dbconn = pymysql.connect(
        host = "127.0.0.1",
        database = 'news_db',
        user = 'root',
        password = 'tzm112528',
        port = 3306
    )
    sqlcmd = 'select username_id,news_id_id from front_user_center'
    a = pd.read_sql(sqlcmd, dbconn)
    user_name = {}
    for i in range(a.__len__()):
        u = a['username_id'][i]
        if u not in user_name:
            user_name[u] = []
        v = a['news_id_id'][i]
        user_name[u].append(v)
#    BaU = UserIIF(user_name)
#    print(BaU.GetRecommendation('0001',3,2))


#    MoP = MostPopular(user_name)
#    print(MoP.GetRecommendation('0001',3,2))

    IT = ItemCF(user_name)
    print(IT.GetRecommendation('0002', 4,2))
#
#    Ro = Random(user_name)
#    print(Ro.GetRecommendation('0001',3,2))
    lmf = LFM(user_name,5,0.02,100,100,0.01)
    print(lmf.GetRecommendation('0002',2))

'''    

