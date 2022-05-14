import xml.etree.ElementTree as ET
import time
import subprocess


# 遍历所有的节点
def walkData(root_node, level, result_list):
    key = '{http://schemas.android.com/apk/res/android}visibility'
    if root_node.attrib.__contains__(key) and (
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

if __name__ == "__main__":
    strs = "adaaaadedacd"
    print(strs.count('a'),1,2)

