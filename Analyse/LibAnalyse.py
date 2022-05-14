import csv
import logging.config
import logging.handlers
import os
import time

import pymysql
import DBUtils
import xlwt
import json

logging.config.fileConfig('AnalyseLog.conf')
logger = logging.getLogger('AnalyseLog')


# rootPath = "G:\\Chrome downloads\\HTTPAnalysisCSV\\"
# rootPath = "/home/chj/APKTestEngine"
# os.chdir(rootPath)


def find_lcsubstr(s1, s2):
    m = [[0 for i in range(len(s2) + 1)] for j in range(len(s1) + 1)]  # 生成0矩阵，为方便后续计算，比字符串长度多了一列
    mmax = 0  # 最长匹配的长度
    p = 0  # 最长匹配对应在s1中的最后一位
    for i in range(len(s1)):
        for j in range(len(s2)):
            if s1[i] == s2[j]:
                m[i + 1][j + 1] = m[i][j] + 1
                if m[i + 1][j + 1] > mmax:
                    mmax = m[i + 1][j + 1]
                    p = i + 1
    return s1[p - mmax:p]  # 返回最长子串


def compute_url_dis(stack_list):
    if len(stack_list) == 0:
        return 0
    else:
        ans = stack_list[0]
        for stack in stack_list[1:]:
            # if stack["stack"] != "None" and stack_list.index(stack) == 0:
            #    ans = stack["stack"]
            # elif stack["stack"] != "None":
            ans = find_lcsubstr(ans, stack)
            # else:
            #    continue
        return ans


def preprocess_stack_list(stack_all_list, pattern):
    #  stack_all_list: 一个pattern下所有url对应的stack的列表
    try:
        pattern_to_lib_count_dict = {}
        pattern_to_lib_list = []
        pattern_to_lib_set = set()
        #  每个value对应着HTTP表的一个stack
        for value in stack_all_list:
            single_stack_to_lib_list = []
            if '|None' in str(value):
                continue
            else:
                print("stack %s: %s" % (stack_all_list.index(value), value))
                tmp_list = str(value).split('|')

                for tmp in tmp_list[1:]:
                    #  java.***   netease.java.sdk   bytedance.android.adsdk.net.**.**
                    if str(tmp).startswith('java') or str(tmp).startswith('at com.android.okhttp') or str(
                            tmp).startswith('at org.apache.http') \
                            or 'retrofit2' in str(tmp) or 'reactivex' in str(tmp) or str(tmp).startswith(
                        'at okio') or str(tmp).startswith('at okhttp3') \
                            or str(tmp).startswith('at com.android.org') or str(tmp).startswith('at android.os') or str(
                        tmp).startswith('at java') or 'intercept' in str(tmp):
                        del tmp_list[tmp_list.index(tmp)]
                        continue
                    else:
                        lib_tmp = tmp.split('at ', 1)[1]
                        lib_tmp = lib_tmp.split('(', 1)[0]
                        verify_list = lib_tmp.split('.')

                        if '$' in verify_list[0]:
                            del tmp_list[tmp_list.index(tmp)]
                            continue
                        elif len(verify_list) == 1:
                            del tmp_list[tmp_list.index(tmp)]
                            continue
                        elif len(verify_list) == 2 and len(verify_list[1]) == 1:
                            del tmp_list[tmp_list.index(tmp)]
                            continue
                        elif len(verify_list) == 3 and len(verify_list[1]) == 1 and len(verify_list[2]) == 1:
                            del tmp_list[tmp_list.index(tmp)]
                            continue
                        elif len(verify_list) == 4 and len(verify_list[1]) == 1 and len(verify_list[2]) == 1 and len(
                                verify_list[3]) == 1:
                            del tmp_list[tmp_list.index(tmp)]
                            continue

                        if len(verify_list) >= 4:
                            # if len(verify_list[3]) == 1 or '$' in verify_list[3]:
                            #     lib_real = verify_list[0] + '.' + verify_list[1] + '.' + verify_list[2]
                            # else:
                            lib_real = verify_list[0] + '.' + verify_list[1] + '.' + verify_list[2] + '.' + \
                                       verify_list[3]
                            # tmp_tuple = (lib_real,)
                            # single_stack_to_lib_set.add(lib_real)
                            if lib_real not in single_stack_to_lib_list:
                                single_stack_to_lib_list.append(lib_real)
                        else:
                            lib_real = verify_list[0]
                            for i in verify_list[1:]:
                                lib_real = lib_real + '.' + i
                            # single_stack_to_lib_set.add(lib_real)
                            if lib_real not in single_stack_to_lib_list:
                                single_stack_to_lib_list.append(lib_real)

                if single_stack_to_lib_list.__len__() > 0:
                    single_stack_to_lib_str = str(single_stack_to_lib_list[0])
                    if single_stack_to_lib_list.__len__() >= 2:
                        for lib in single_stack_to_lib_list[1:]:
                            single_stack_to_lib_str = single_stack_to_lib_str + '|' + str(lib)
                    else:
                        pass
                else:
                    continue

                print("\t stack to lib_list: %s" % tmp_list)
                print("\t stack to lib_list_str: %s\n" % single_stack_to_lib_str)
                pattern_to_lib_set.add(single_stack_to_lib_str)
                pattern_to_lib_list = pattern_to_lib_list + single_stack_to_lib_list
                # stack_real_list.append(value['stack'])

        for lib in pattern_to_lib_list:
            if pattern_to_lib_count_dict.get(lib, None) is None:
                pattern_to_lib_count_dict.update({lib: 1})
            else:
                pattern_to_lib_count_dict[lib] = pattern_to_lib_count_dict[lib] + 1

    except Exception as e:
        print(value)
        print(e)

    print("pattern %s to lib finished" % str(pattern))
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    return pattern_to_lib_set, pattern_to_lib_count_dict


def convert_to_url_pattern(http_message):
    host = http_message.get('host')
    protocol = http_message.get('protocol')
    method = http_message.get('method')

    key_list = []
    try:
        URL = http_message['URL']
        after_protocol = URL.split("://")[1]
        after_host = str(after_protocol).split("/", 1)[1]
        if "?" in after_host:
            key_value_pair_str = after_host.split("?")[1]
            if "&" in key_value_pair_str:
                key_value_pair_list = key_value_pair_str.split("&")
                for key_value_pair in key_value_pair_list:
                    key_list.append(key_value_pair.split("=")[0])
            path = after_host.split("?")[0]
        else:
            path = after_host
    except Exception as e:
        print(http_message)
        print(e)
        return None

    return method, protocol, path, host, tuple(key_list)


def get_url_pattern_dict(host, DBConnection) -> {str, list}:
    #  取出某个域名对应的所有http_message，返回http_message_list,每个元素是字典（dict）
    host_find_http_message_sql = 'SELECT * FROM HTTP WHERE host = %s'
    DBCursor = DBConnection.cursor(pymysql.cursors.DictCursor)
    DBCursor.execute(host_find_http_message_sql, host)
    http_message_list = DBCursor.fetchall()
    URL_pattern_dict = {}
    URL_list = []
    URL_pattern = []

    for http_message in http_message_list:
        # pattern: (method, protocol, path, host, key_list)
        pattern = convert_to_url_pattern(http_message)
        if pattern is None:
            continue
        id_stack = str(http_message['id']) + '|' + str(http_message['stack'])
        if URL_pattern_dict.get(pattern, None) is None:
            URL_pattern_dict.update({pattern: [id_stack]})
        else:
            URL_pattern_dict[pattern].append(id_stack)

    print("URL_pattern_dict finished")
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    return URL_pattern_dict


def four_tuple_hash_match_stack(four_tuple_hash_list, DBConnection):
    four_tuple_find_stack_sql = 'SELECT id,stack FROM Stack WHERE four_tuple_hash = %s'
    DBCursor = DBConnection.cursor(pymysql.cursors.DictCursor)
    DBCursor.executemany(four_tuple_find_stack_sql, four_tuple_hash_list)
    stack_list = DBCursor.fetchall()
    stack_id_list = []
    for item in stack_list:
        value = str(item['id']) + '|' + item['stack']
        stack_id_list.append(value)
    # print("stack_match_list length is %s" % len(stack_match_list))
    print("four_tuple_hash match stack_list finished")
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    return stack_id_list


def from_url_get_four_tuple_hash(url, DBConnection):
    four_tuple_stack_dict = {}
    url_find_four_tuple_sql = 'SELECT * FROM HTTP WHERE URL = %s'
    DBCursor = DBConnection.cursor(pymysql.cursors.DictCursor)
    DBCursor.execute(url_find_four_tuple_sql, url)
    four_tuple_list = DBCursor.fetchall()
    four_tuple_hash_list = []
    for match in four_tuple_list:
        four_tuple_hash = match['four_tuple_hash']
        # srcAddr = match['srcAddr']
        # srcPort = match['srcPort']
        # dstAddr = match['dstAddr']
        # dstPort = match['dstPort']
        four_tuple_hash_list.append(four_tuple_hash)
        # four_tuple_stack_dict_tmp = {(srcAddr, srcPort, dstAddr, dstPort):stack_list}
    # return srcAddr, srcPort, dstAddr, dstPort
    # print("stack_list length is %s" % len(stack_list))
    print("SELECT four_tuple_hash_list finished!!!")
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    return four_tuple_hash_list


if __name__ == '__main__':
    # str_test = 'w'
    # print(len(str_test))
    third_host_list = []
    host_to_stack_dict = {}
    host_to_lib_dict = {}
    host_to_lib_count_dict = {}
    with open("hostToPackageALL.txt", "r", encoding="utf-8") as hpn:
        host_rank_dict = eval(hpn.read())
        # print(type(host_rank_dict))
        # print(len(host_rank_dict))
        host_ranking_list = sorted(host_rank_dict.items(), key=lambda item: item[1], reverse=True)

    for host_ranking in host_ranking_list:
        host_count = 0
        count = host_ranking[1]
        host = host_ranking[0]
        host_to_lib_set = set()
        lib_count_dict = {}
        if count >= 10:
            print("++++++++++++++++++++++++++++++start host %s" % host)
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            DBConnection = DBUtils.get_db_connection()

            #  返回字典，key是pattern，
            URL_pattern_dict = get_url_pattern_dict(host, DBConnection)

            for pattern, id_stack_list in URL_pattern_dict.items():
                print("pattern: " + str(pattern))
                pattern_to_lib_set, pattern_to_lib_count_dict = preprocess_stack_list(id_stack_list, pattern)

                host_to_lib_set = host_to_lib_set | pattern_to_lib_set

                for key, value in pattern_to_lib_count_dict.items():
                    if key in lib_count_dict:
                        lib_count_dict[key] = lib_count_dict[key] + value
                    else:
                        lib_count_dict[key] = value

            host_to_lib_count_list = sorted(host_to_lib_count_dict.items(), key=lambda item: item[1], reverse=True)
            host_to_lib_count_dict.update({host: host_to_lib_count_list})
            host_to_lib_dict.update({host: host_to_lib_set})
            host_count = host_count + 1
            print("******************************host %s finished ranking %s" % (host, host_count))
            print('++++++++++++++++++++++++++++++host %s to libraries are %s' % (host, host_to_lib_set))
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    with open('hostToLibraries.txt', 'w+', encoding='utf-8') as f:
        for host, lib_set in host_to_lib_dict.items():
            f.write(str(host))
            f.write(":\r\n")
            for lib in lib_set:
                f.write(lib)
                f.write(";")
                f.write("\r\n")
            f.write("\r\n")
            f.write("\r\n")

    #host_to_lib_count_list = sorted(host_to_lib_count_dict.items(), key=lambda item: item[1], reverse=True)
    with open('hostToLibrariesCount.txt', 'w+', encoding='utf-8') as f:
        for host, lib_count_list in host_to_lib_count_dict.items():
            f.write(str(host))
            f.write(":\r\n")
            for lib_name_count in lib_count_list:
                lib_name = lib_name_count[0]
                lib_count = lib_name_count[1]
                f.write(str(lib_name) + ": " + str(lib_count))
                f.write("\r\n")
            f.write("\r\n")
            f.write("\r\n")

    #print("hostToLibraries.txt finished!!!")
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
