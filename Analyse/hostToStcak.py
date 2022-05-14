import csv
import logging.config
import logging.handlers
import os
import pymysql
import DBUtils
import xlwt
import json


logging.config.fileConfig('log.conf')
logger = logging.getLogger('APKTestEngine')

rootPath = "G:\\Chrome downloads\\HTTPAnalysisCSV"
# rootPath = "/home/chj/APKTestEngine"
os.chdir(rootPath)
fr = open("hostToPackage.txt", 'r+')
dic = eval(fr.read())   #读取的str转换为字典
fr.close()

import numpy

def find_lcseque(s1, s2):
    # 生成字符串长度加1的0矩阵，m用来保存对应位置匹配的结果
    m = [ [ 0 for x in range(len(s2)+1) ] for y in range(len(s1)+1) ]
    # d用来记录转移方向
    d = [ [ None for x in range(len(s2)+1) ] for y in range(len(s1)+1) ]

    for p1 in range(len(s1)):
        for p2 in range(len(s2)):
            if s1[p1] == s2[p2]:            #字符匹配成功，则该位置的值为左上方的值加1
                m[p1+1][p2+1] = m[p1][p2]+1
                d[p1+1][p2+1] = 'ok'
            elif m[p1+1][p2] > m[p1][p2+1]:  #左值大于上值，则该位置的值为左值，并标记回溯时的方向
                m[p1+1][p2+1] = m[p1+1][p2]
                d[p1+1][p2+1] = 'left'
            else:                           #上值大于左值，则该位置的值为上值，并标记方向up
                m[p1+1][p2+1] = m[p1][p2+1]
                d[p1+1][p2+1] = 'up'
    (p1, p2) = (len(s1), len(s2))
    #print(numpy.array(d))
    s = []
    while m[p1][p2]:    #不为None时
        c = d[p1][p2]
        if c == 'ok':   #匹配成功，插入该字符，并向左上角找下一个
            s.append(s1[p1-1])
            p1-=1
            p2-=1
        if c =='left':  #根据标记，向左找下一个
            p2 -= 1
        if c == 'up':   #根据标记，向上找下一个
            p1 -= 1
    s.reverse()
    result = ''.join(s)
    print(result)
    return len(result)

def getNumofCommonSubstr(str1, str2):

    lstr1 = len(str1)
    lstr2 = len(str2)
    record = [[0 for i in range(lstr2+1)] for j in range(lstr1+1)] # 多一位
    maxNum = 0   # 最长匹配长度
    p = 0    # 匹配的起始位

    for i in range(lstr1):
        for j in range(lstr2):
            if str1[i] == str2[j]:
                # 相同则累加
                record[i+1][j+1] = record[i][j] + 1
                if record[i+1][j+1] > maxNum:
                    # 获取最大匹配长度
                    maxNum = record[i+1][j+1]
                    # 记录最大匹配长度的终止位置
                    p = i + 1
    return maxNum

if __name__ == '__main__':
    stackList = []
    hostList = []

    # DBConnection = DBUtils.getDBConnection()
    # DBCursor = DBConnection.cursor(pymysql.cursors.DictCursor)

    for key1, value1 in dic.items():
        packageStackList = []
        if value1 >= 10:
            findIpSql = 'SELECT * FROM HTTP WHERE host= %s'
            print('=============================%s=============================' % key1)
            try:
                DBConnection = DBUtils.getDBConnection()
                DBCursor = DBConnection.cursor(pymysql.cursors.DictCursor)
                DBCursor.execute(findIpSql, key1)
                matchDictList = DBCursor.fetchall()
                # print(len(matchDictList))
                for matchItem in matchDictList:
                    for key, value in matchItem.items():
                        if key == 'srcAddr':
                            srcAddr = value
                        elif key == 'srcPort':
                            srcPort = value
                        elif key == 'dstAddr':
                            dstAddr = value
                        elif key == 'dstPort':
                            dstPort = value
                        else:
                            continue
                    findStackSql = 'SELECT packageName, stack FROM Stack WHERE (srcAddr = %s and srcPort = %s and dstAddr = %s and dstPort = %s)'
                    DBCursor.execute(findStackSql, (srcAddr, srcPort, dstAddr, dstPort))
                    resultDictList = DBCursor.fetchall()
                    # print(len(resultDictList))
                    packageStackList.extend(resultDictList)

                # print(len(packageStackList))
                packageList = []
                for ps in packageStackList:
                    for psTmp in packageStackList[packageStackList.index(ps)+1:]:
                        if ps['packageName'] != psTmp['packageName'] and ps['stack'] != 'None' and psTmp['stack'] != 'None' and ps['packageName'] not in packageList and psTmp['packageName'] not in packageList:
                            # ins = ps['stack'].intersection(psTmp['stack'])
                            # uni = ps['stack'].union(psTmp['stack'])
                            ins = getNumofCommonSubstr(ps['stack'], psTmp['stack'])
                            #ins = find_lcseque(ps['stack'], psTmp['stack'])
                            if len(ps['stack']) >= len(psTmp['stack']):
                                similarity = ins/len(ps['stack'])
                            else:
                                similarity = ins/len(psTmp['stack'])
                            #print(similarity)
                            if similarity >= 0.8:
                                packageList.append(ps['packageName'])
                                packageList.append(psTmp['packageName'])
                                print(similarity)
                                print(ps)
                                print(psTmp)
                                if key1 not in hostList:
                                    hostList.append(key1)
                            else:
                                continue
                        else:
                            continue
            except Exception as e:
                print(e)

    f = open('hostList.txt', 'w')
    f.write(str(hostList))
    f.close()
