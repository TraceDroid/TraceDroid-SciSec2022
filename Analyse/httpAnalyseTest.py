import csv
import logging.config
import logging.handlers
import os
import time
from typing import Set, Optional, Dict, Any

import matplotlib.pyplot as plt
import pymysql
import DBUtils
import xlwt
import json

logging.config.fileConfig('AnalyseLog.conf')
logger = logging.getLogger('AnalyseLog')


def HTTPAnalyse():
    # logger.info('Analyse HTTP data')
    DBConnection = DBUtils.get_db_connection()
    DBCursor = DBConnection.cursor(pymysql.cursors.DictCursor)
    # rootPath = 'G:\\Chrome downloads\\HTTPAnalysisCSV\\'
    # os.chdir(rootPath)
    hostToPackageList = []
    packageTypeNumList = []
    hostToPackageDict: Dict[Any, Optional[Set[Any]]] = {}

    selectHostSql = "SELECT host FROM HTTP GROUP BY host"

    select_all_sql = "select * from HTTP"
    logger.debug("starting fetch all HTTP records...")
    DBCursor.execute(select_all_sql)
    http_message_list = DBCursor.fetchall()
    logger.debug("fetch ok")
    logger.debug("http_message_list size %s " % http_message_list.__len__())

    i = 0
    for http_message in http_message_list:
        logger.debug("*"*20 + str(i))
        host = http_message["host"]
        if host not in hostToPackageDict.keys():
            package_name_set = set()
            package_name_set.add(http_message["packageName"])
            hostToPackageDict[host] = package_name_set
        else:
            hostToPackageDict[host].add(http_message["packageName"])
        i = i + 1

    hostToPackageDict_final = {}
    for host, package_name_set in hostToPackageDict.items():
        hostToPackageDict_final[host] = len(package_name_set)

    logger.debug("hostToPackageDict_final size %s " % len(hostToPackageDict))
    with open('hostToPackageALL.txt', 'w+', encoding='utf-8') as f:
        f.write(str(hostToPackageDict_final))
    logger.debug("txt finished!!!")
    #print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))




    # try:
    #     logger.debug("selecting host group by host...")
    #     DBCursor.execute(selectHostSql)
    #     hostListDict = DBCursor.fetchall()
    #     hostList = [item[key] for item in hostListDict for key in item]
    #     logger.debug('hostList length is %s' % len(hostList))
    #     #logger.debug(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    #     hostCount = 0
    #
    #     for host in hostList:
    #         selectSql = "SELECT packageName FROM HTTP WHERE host = %s GROUP BY packageName"
    #         DBCursor.execute(selectSql, host)
    #         resultDict = DBCursor.fetchall()
    #         packageNameTypeCount = len(resultDict)
    #         tmp = {host: packageNameTypeCount}
    #         hostToPackageDict.update(tmp)
    #         hostCount = hostCount + 1
    #         logger.debug('hostCount is %s' % hostCount)
    #
    #     with open('hostToPackageALL.txt', 'w+', encoding='utf-8') as f:
    #         f.write(str(hostToPackageDict))
    #     logger.debug("txt finished!!!")
    #     #print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    #
    # except Exception as e:
    #     DBConnection.rollback()
    #     logger.error('Fail To Analyse')
    #     logger.error(e)
    DBConnection.close()


if __name__ == '__main__':
    # logger.info('\n==========Analyse starting==========')
    HTTPAnalyse()
