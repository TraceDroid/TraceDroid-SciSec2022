import configparser
import os
import platform
import pymysql  # pip install pymysql
import logging.config
import logging.handlers

import DBUtils

logging.config.fileConfig('StackExtract.conf')
logger = logging.getLogger('StackExtract')


def get_db_config() -> object:
    """

    :return: 数据库配置信息
    """
    config = configparser.ConfigParser()
    if platform.system().lower() == "windows":
        config.read("config.conf")
        db_config = config["database"]
        return db_config
    elif platform.system().lower() == "linux":
        config.read("//home/chj/APKTestEngine/stackDir/StackExtract/config.conf")
        db_config = config['database']
        return db_config


def write_to_mysql(stack_result_file_path):
    db_connection = DBUtils.get_db_connection()
    db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
    sql = "INSERT INTO Stack (packageName, requestTime, SSL_Session, function, srcAddr, srcPort, dstAddr, dstPort,  stack) VALUES (%s, %s, %s, %s, %s, %s,%s, %s, %s)"

    with open(stack_result_file_path, "r", encoding="utf-8") as input_file:
        stack_dict = {}
        stack_dict_result = {}
        stack_list = []
        while True:
            line = input_file.readline()
            if line == "":
                break
            if line != "\n":
                line_split_list = line.split(" ")
                if line_split_list[6] == "tcs.py:168":
                    stack_dict["package_name"] = line_split_list[7].strip()
                    stack_dict["requestTime"] = line_split_list[0] + " " + line_split_list[1].replace(",", ".")
                    continue
                elif line_split_list[6] == "tcs.py:169":
                    if str(line_split_list[7]).split(":").__len__() > 2:
                        stack_dict["SSL_Session"] = str(line_split_list[7]).split(":")[1]
                    else:
                        stack_dict["SSL_Session"] = "None"
                    continue
                elif line_split_list[6] == "tcs.py:170":
                    stack_dict["function"] = line_split_list[7].strip()
                    stack_dict["srcAddr"] = str(line_split_list[8]).split(":")[0]
                    stack_dict["srcPort"] = str(line_split_list[8]).split(":")[1]
                    stack_dict["dstAddr"] = str(line_split_list[10]).split(":")[0]
                    stack_dict["dstPort"] = str(line_split_list[10]).split(":")[1].strip()
                    continue
                elif line.split(" ")[6] == "tcs.py:177":
                    stack_dict["stack"] = line[50:].strip()
                    continue
            else:
                #logger.debug("stack_dict: ")
                #logger.debug(stack_dict)
                stack_key = stack_dict["package_name"] + stack_dict["srcAddr"] + stack_dict["srcPort"] + stack_dict["dstAddr"] + stack_dict["dstPort"]
                if stack_key not in stack_dict_result:
                    # stack_value = [stack_dict["package_name"], stack_dict["requestTime"], stack_dict["SSL_Session"], stack_dict["function"],
                    #                stack_dict["srcAddr"], stack_dict["srcPort"], stack_dict["dstAddr"], stack_dict["dstPort"], stack_dict["stack"]]
                    stack_list.append((stack_dict["package_name"], stack_dict["requestTime"], stack_dict["SSL_Session"], stack_dict["function"],
                                    stack_dict["srcAddr"], stack_dict["srcPort"], stack_dict["dstAddr"], stack_dict["dstPort"], stack_dict["stack"]))
                    stack_dict_result[stack_key] = 0
                stack_dict.clear()

        # write to MySQL
        logger.debug("stack_list len: %s" % stack_list.__len__())

        try:
            db_cursor.executemany(sql, stack_list)
            #db_cursor.execute(sql, (stack[0], stack[1], stack[2], stack[3], stack[4], stack[5], stack[6], stack[7], stack[8]))
            db_connection.commit()
        except Exception as e:
            logger.error(e)
            #logger.error(stack[8])
            db_connection.rollback()

    db_connection.close()


if __name__ == '__main__':
    if platform.system().lower() == 'windows':
        stack_file_path = "E:\\Stack.log"
        stack_result_file_path = "E:\\StackResult.log"
    elif platform.system().lower() == 'linux':
        stack_file_path = "/home/chj/APKTestEngine/stackDir/Stack.log_xiaomi"
        stack_result_file_path = "/home/chj/APKTestEngine/stackDir/Stack.log_xiaomi_result"
    if os.path.exists(stack_result_file_path) is not True:
        with open(stack_result_file_path, "a", encoding="utf-8") as output:
            with open(stack_file_path, encoding="utf-8") as file:
                stack_begin = False
                stack_begin_stack = False
                # lets_start = False
                stack = ''
                while True:
                    line = file.readline()

                    # #跳过第一个回车换行，因为第一个格式有些问题
                    # if lets_start is False and line != "\n":
                    #     continue
                    # else:
                    #     lets_start = True

                    if line == '':
                        break
                    if stack_begin is True:
                        if line != "\n":
                            line_split_list2 = line.split(" ")

                            if line_split_list2.__len__() > 7 and line_split_list2[7].strip() == "None":
                                # print(line)
                                stack_begin = False
                                stack_begin_stack = False
                                stack = stack + line
                                output.write(stack)
                                output.write("\n")
                                stack = ''
                                continue

                            if line_split_list2.__len__() > 6 and line_split_list2[6] == "tcs.py:177":
                                stack_begin_stack = True
                                stack = stack + line.strip()
                            elif stack_begin_stack:
                                stack = stack + "|" + line.strip()
                            else:
                                stack = stack + line
                            continue
                        else:
                            stack_begin = False
                            stack_begin_stack = False
                            output.write(stack)
                            output.write("\n\n")
                            stack = ''
                            continue

                    line_split_list = line.split(" ")
                    # print(line_split_list.__len__())
                    if line_split_list.__len__() == 8:
                        if line_split_list[6] == "tcs.py:168":
                            stack = stack + line
                            stack_begin = True

    write_to_mysql(stack_result_file_path)
    logger.debug("write to MySQL OK!")
