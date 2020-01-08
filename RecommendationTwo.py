import xlrd
import math
import random
import pandas as pd
import pymysql
import xlwt
import numpy as np
import time
from tqdm import tqdm, trange

class  UserIIF():
    def __init__(self,train):
        self.user_news = train
    def Set(self):
        col = self.user_news.shape[1]
        row = self.user_news.shape[0]
        exist = (self.user_news != 0)*1.0
        One = np.ones(col)
        Sum = np.dot(exist, One)
        C = np.zeros((row,row))
        for i in range(row):
            for j in range(i + 1 , row):
                a = exist[i,:]
                b = exist[j,:]
                C[i,j] = np.dot(a,b.T)
                C[j,i] = C[i,j]
                C[i,j] = C[j, i] = C[i,j]/math.sqrt(Sum[i]*Sum[j])
        return C
    def GetRecommendation(self):
        W = self.Set()
        col, row = self.user_news.shape
        P = np.zeros((row,col))
        for i in range(row):
            for j in range(col):
                if data[i,j] != 0:
                    P[i,j] = -1000
                else:
                    a= np.array(data[:,j])
                    b = np.array(W[i])
                    P[i,j] = np.dot(b,a)
        return P

class ItemCF():
    #新闻之间的相似度
    def __init__(self,train):
        self.new_users = train

    def Set(self):
        col = self.new_users.shape[1]
        row = self.new_users.shape[0]
        exist = (self.new_users != 0)*1.0
        One = np.ones(row)
        Sum = np.dot(exist.T,One)
        C = np.zeros((col,col))
        for i in range(col):
            for j in range(i + 1, col):
                a = exist[:,i]
                b = exist[:,j]
                C[i,j] = np.dot(a,b.T)
                C[j,i] = C[i,j] = C[i,j]/math.sqrt(Sum[i]*Sum[j])
        return C
    def GetRecommendation(self):
        W = self.Set()
        row,col = data.shape
        P = np.zeros((row, col))

        for i in range(row):
            for j in range(i + 1, col):
                if self.new_users[i,j] != 0:
                    P[i,j] = -100
                else :
                    a = np.array(self.new_users[i])
                    b = np.array(W[:,j])
                    P[i,j] = np.dot(a,b)
        return P

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
        for new in self.news:
            if new not in seen_news:
                recs[new] = (self.P[user] * self.Q[new]).sum()
        recs = list(sorted(recs.items(), key=lambda x: x[1], reverse=True))[:N]
        return recs
user_news = []
num = 0
with open('test2.csv','r',3000,'utf-8') as f:
    l = f.readlines()
    for i in l:
        Rui = []
        tmp = i.split(',')
        for j in range(len(tmp)):
                Rui.append(int(float(tmp[j])))
        num += 1
        user_news.append(Rui)
data = np.array(user_news)

print("数据读取完毕，开始")

df1 = xlwt.Workbook()
sheet = df1.add_sheet("sheet1")
Bau = UserIIF(data)
ans = np.array(np.argsort(-Bau.GetRecommendation()))
for i in range(100):
    for j in range(10):
        sheet.write(i,j,int(ans[i,j]) + 1)
print('完毕1')

sheet = df1.add_sheet("sheet2")
Ite = ItemCF(data)
ans = np.array(np.argsort(-Ite.GetRecommendation()))
for i in range(100):
    for j in range(10):
        sheet.write(i, j , int(ans[i][j]) + 1)
print('完毕2')
df1.save('test4.xls')

