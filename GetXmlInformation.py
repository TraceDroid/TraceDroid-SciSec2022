#!/usr/bin/env python
# encoding: utf-8

import xml.etree.ElementTree as ET
import logging.config
import logging.handlers
from os import path

#log_file_path = path.join(path.dirname(path.abspath(__file__)), 'TestEngine.conf')
logging.config.fileConfig("TestEngine.conf")
logger = logging.getLogger('TestEngine')

# 获取XML的root，并将root传递给walkData进行遍历
def getXmlData(file_name):
    """

    :param file_name:
    :return: result_list, list of [level, node_attrib]
    each line in xml has these fileds：
    index、text、resource-id、class、package、content-desc、checkable、checked、clickable、
    enabled、focusable、focused、scrollable、long-clickable、password、selected、visible-to-user、bounds
    """
    level = 0  # 节点的深度从1开始
    result_list = []
    try:
        root = ET.parse(file_name).getroot()
    except ET.ParseError as pe:
        print(pe)
        exit(1)
    walkData(root, level, result_list)
    logger.debug("#"*20 + "result_list: " + str(result_list) + "#"*20)
    return result_list


# 遍历xml
def walkData(root_node, level, result_list):
    if (root_node.attrib.__contains__('class')):  #attrib代表xml node中的所有属性，此处依次获取相关属性值
        if root_node.attrib['visible-to-user'] == 'false':
            return
        temp_list = [level, root_node.attrib['class']]
        #logger.debug("root_node.attrib['class']： " + root_node.attrib['class'])
        if (root_node.attrib.__contains__('clickable')):
            temp_list.append(root_node.attrib['clickable'])
        if (root_node.attrib.__contains__('checkable')):
            temp_list.append(root_node.attrib['checkable'])
        if (root_node.attrib.__contains__('bounds')):
            temp_list.append(root_node.attrib['bounds'])
        result_list.append(temp_list)  #temp_list本身是一个list，每个temp_list的格式是 [level,class,clickable,checkable,bounds]result_list中的元素是temp_list，其中bounds的格式为“[x1.y1][x2,y2]”

    # 遍历每个子节点
    children_node = root_node.getchildren()
    if len(children_node) == 0:
        return
    for child in children_node:
        if child.tag == 'node':
            walkData(child, level + 1, result_list)
    return


#  获取可点击元素的坐标
#  [level,class,clickable,checkable,bounds], bounds:[x1,y1][x2,y2]
def getClickableCoordinate(ele_list):
    coord = []  #列表
    for e in ele_list:
        if e[2] == 'true' and (not e[1].__contains__('EditText')) and e[3] == 'false':
            # if e[4]!='[0,72][168,240]':      #一般是左上角的返回键类似于'<----'的，点击之后会返回上一级页面，直接先过滤掉
            helpCoord = stringArrayToIntegerArray(e[4])
            if not (helpCoord[0] >= 0 and helpCoord[0] <= 170 and helpCoord[1] >= 70 and helpCoord[1] <= 240):
                if helpCoord not in coord:
                    coord.append(helpCoord)
    return coord


# 字符串转换为整型数组
def stringArrayToIntegerArray(s):
    res = []
    s = s.replace("[", "")
    s = s.replace("]", " ")
    s = s.replace(",", " ")
    s = s.split(" ")
    res.append(int(s[0]) + int(abs(int(s[2]) - int(s[0])) / 2))
    res.append(int(s[1]) + int(abs(int(s[3]) - int(s[1])) / 2))
    logger.debug("res: " + str(res))
    return res


# xml树映射成字符串
def getXmlTreeMapToStr(Node_list):
    str_xml = ""
    level = 1
    for node in Node_list:
        str = node[1]
        if level < node[0]:
            level = node[0]
            str_xml = str_xml + "(" + str
        elif level > node[0]:
            for i in range(level - node[0]):
                str_xml = str_xml + ")"
            level = node[0]
            str_xml = str_xml + "," + str
        else:
            if str_xml.strip() != '':
                str_xml = str_xml + "," + str
            else:
                str_xml = str
    for i in range(level - 1):
        str_xml = str_xml + ")"
    logger.debug("str_xml: " + str_xml)
    return str_xml

