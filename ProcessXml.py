#!/usr/bin/env python
# encoding: utf-8


import xml.etree.ElementTree as ET
import ElementMappedToCharacter as EMTC
import glob
import os
import hashlib

# 遍历所有的节点
def walkData(root_node, level, result_list):
    key = '{http://schemas.android.com/apk/res/android}visibility'
    if root_node.attrib.__contains__(key) and (                #过滤掉不可见的点
            root_node.attrib[key] == 'invisible' or root_node.attrib[key] == 'gone'):
        return
    temp_list = [level, root_node.tag]
    result_list.append(temp_list)

    # 遍历每个子节点
    children_node = root_node.getchildren()
    if len(children_node) == 0:
        return
    for child in children_node:
        walkData(child, level + 1, result_list)
    return


def getXmlData(file_name):
    level = 1  # 节点的深度从1开始
    result_list = []
    root = ET.parse(file_name).getroot()
    walkData(root, level, result_list)
    return result_list


def getMapTreeFromXmlPath(filePath,txtOutputPath):
    dirList = os.listdir(filePath)
    for i in range(len(dirList)-1):
        apkPath1 = filePath + "\\" + dirList[i]
        Ele_list1 = readTextToList(apkPath1)
        for j in range(i+1,len(dirList)):
            apkPath2 = filePath + "\\" + dirList[j]
            Ele_list2 = readTextToList(apkPath2)
            EleDict = EMTC.getElementDictionary(Ele_list1, Ele_list2)   #映射字典

            category_output = txtOutputPath + "\\" + dirList[i] + "&" + dirList[j]
            if not os.path.exists(category_output):  # 如果输出的路径不存在那么就创建一个路径
                os.makedirs(category_output)
            fileName1 = category_output + "\\" + dirList[i]+".txt"       #映射文件的输出名
            fileName2 = category_output + "\\" + dirList[j] + ".txt"  # 映射文件的输出名
            if os.path.exists(fileName1):
                os.remove(fileName1)
            if os.path.exists(fileName2):
                os.remove(fileName2)
            xmlInputPath1 = apkPath1 + "\\res\\layout"
            xmlInputPath2 = apkPath2 + "\\res\\layout"
            writeElementMapToTxt(xmlInputPath1, fileName1, EleDict)
            writeElementMapToTxt(xmlInputPath2, fileName2, EleDict)


#元素映射写入txt文件中
def writeElementMapToTxt(filePath,fileName, EleDict):
    if os.path.exists(fileName):
        os.remove(fileName)
    wrong_cnt = 0
    for anno_xml in glob.glob(os.path.join(filePath, '*')):
        if anno_xml.endswith('.xml'):
            try:
                strXml = getStrXmlMap(anno_xml, EleDict)
                ############过滤掉其中的映射完成之后长度小于5#################
                if len(strXml) > 5:
                    writeToTxt(strXml, fileName)
                # print(strXml)
            except Exception as e:
                print("Error: cannot parse file: %s" % anno_xml)
                wrong_cnt += 1
                continue

def getStrXmlMap(file_name, EleDict):
    StrXml = ""
    level = 1
    for node in getXmlData(file_name):
        str = node[1]
        if str.find(".") != -1 and str.find('android.support.') != -1:
            str = str.split('.')[-1]
        if level < node[0]:
            level = node[0]
            StrXml = StrXml + "(" + elementMap(str, EleDict)
        elif level > node[0]:
            for i in range(level - node[0]):
                StrXml = StrXml + ")"
            level = node[0]
            StrXml = StrXml + "," + elementMap(str, EleDict)
        else:
            if StrXml.strip() != '':
                StrXml = StrXml + "," + elementMap(str, EleDict)
            else:
                StrXml = elementMap(str, EleDict)
    for i in range(level - 1):
        StrXml = StrXml + ")"
    return StrXml


#计算字符串的hash值
def getStrHash(str):
    md5 = hashlib.md5()
    md5.update(bytes(str, encoding='utf-8'))
    return md5.hexdigest()


# 元素映射
def elementMap(str, EleDict):
    if EleDict.get(str) is not None:
        return EleDict.get(str)
    elif (str.find('.') != -1 and str.find('android.support')== -1):
        return "&"
    else:
        return "%"

def writeToTxt(str,fileName):
    f = open(fileName, 'a')
    f.write(  str +'\n')  # 这里的\n的意思是在源文件末尾换行，即新加内容另起一行插入。
    f.close()  # 特别注意文件操作完毕后要close

def readTextToList(filePath):
    # 读取文件
    res_list = []
    fileName = filePath + "\\elementFrequency.txt"
    if os.path.exists(fileName):
        file_handler = open(fileName)
        contents = file_handler.readlines()
        for msg in contents:
            msg = msg.strip('\n')
            # # split() 通过某个字符分割字符串,返回的是分割完成后的列表
            list_1 = msg.split(' ')
            list_1[1] = float(list_1[1])
            res_list.append(list_1)
        file_handler.close()
    else:
        print("There is no elementFrequency.txt ")
    return res_list




