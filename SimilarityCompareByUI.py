#!/usr/bin/env python
# encoding: utf-8

import os
import sys
import EditDistance as ED

def SimilarityCompare(filePath):
    dirList = os.listdir(filePath)
    for i in range(len(dirList)):
        fileList = os.listdir(filePath + "\\" + dirList[i])
        fileName1 = filePath + "\\" + dirList[i] + "\\" + fileList[0]
        fileName2 = filePath + "\\" + dirList[i] + "\\" + fileList[1]
        f1 = open(fileName1)
        contents_file1 = f1.readlines();
        f1.close()
        f2 = open(fileName2)
        contents_file2 = f2.readlines();
        f2.close()
        num = 0
        for msg1 in contents_file1:
            num = num + 1;
            maxSim = sys.float_info.min
            msg1 = msg1.strip('\n')
            for msg2 in contents_file2:
                msg2 = msg2.strip('\n')
                if (len(msg1) - len(msg2)) < 5:
                    maxSim = max(maxSim, ED.editDistanceSimilarity(msg1, msg2))
            print(maxSim)

