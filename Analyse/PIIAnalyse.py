# -*- coding: utf-8 -*-
# @Time : 2021/6/16 14:44 
# @Author : *
# @File : PIIAnalyse.py 
# @Software: PyCharm

import time

import pymysql
import csv


def get_db_connection(database_name) -> pymysql.Connection:
    host = "10.10.103.147"
    port = 3306
    user = "root"
    password = "iiewlz666"
    db_connection = pymysql.connect(host=host, port=port, user=user, password=password, database=database_name)
    return db_connection


if __name__ == '__main__':
    sn_149 = "8A2X0KKKF"
    imei_149 = "990012001490561"
    sn_248 = "8BSX1EQGX"
    imei_248 = "358123091482602"

    PII_request_count = 0
    PII_requestBody_count = 0
    PII_requestHeaders_count = 0

    db_connection = get_db_connection("APKDB")
    db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
    select_sql = "select id, host, URL, requestHeaders, requestBody, responseHeaders, responseBody from HTTP"

    db_cursor.execute(select_sql)
    http_message_list = db_cursor.fetchall()
    http_message_special = list()

    for http_message in http_message_list:
        # print(http_message["responseBody"])
        http_message["requestHeaders"] = str(http_message["requestHeaders"]).replace(",", " ").replace("\n", "")[:1000]
        http_message["requestBody"] = str(http_message["requestBody"]).replace(",", " ").replace("\n", "")[:1000]
        http_message["responseHeaders"] = str(http_message["responseHeaders"]).replace(",", " ").replace("\n", "")[:1000]
        http_message["responseBody"] = str(http_message["responseBody"]).replace(",", " ").replace("\n", "")[:1000]
        if (sn_149 in http_message["requestHeaders"] and sn_149 in http_message["requestBody"]) \
            or (imei_149 in http_message["requestHeaders"] and imei_149 in http_message["requestBody"]):
            # 如果设备信息同时出现在header和body
            PII_request_count += 1
            http_message_special.append([http_message["id"], http_message["host"], http_message["URL"], http_message["requestHeaders"], http_message["requestBody"], http_message["responseHeaders"], http_message["responseBody"], "requestHeaders and requestBody"])
        elif (sn_248 in http_message["requestHeaders"] and sn_248 in http_message["requestBody"]) \
            or (imei_248 in http_message["requestHeaders"] and imei_248 in http_message["requestBody"]):
            # 如果设备信息同时出现在header和body
            PII_request_count += 1
            http_message_special.append([http_message["id"], http_message["host"], http_message["URL"], http_message["requestHeaders"], http_message["requestBody"], http_message["responseHeaders"], http_message["responseBody"], "requestHeaders and requestBody"])
        elif (sn_149 in http_message["requestHeaders"] or imei_149 in http_message["requestHeaders"]) \
            or (sn_248 in http_message["requestHeaders"] or imei_248 in http_message["requestHeaders"]):
            # 如果设备信息只出现在header
            PII_requestHeaders_count += 1
            http_message_special.append([http_message["id"], http_message["host"], http_message["URL"], http_message["requestHeaders"], http_message["requestBody"], http_message["responseHeaders"], http_message["responseBody"], "requestHeaders"])
        elif (sn_149 in http_message["requestBody"] or imei_149 in http_message["requestBody"]) \
            or (sn_248 in http_message["requestBody"] or imei_248 in http_message["requestBody"]):
            # 如果设备信息只出现在body
            PII_requestBody_count += 1
            http_message_special.append([http_message["id"], http_message["host"], http_message["URL"], http_message["requestHeaders"], http_message["requestBody"], http_message["responseHeaders"], http_message["responseBody"], "requestBody"])

    with open("PIIAnalyseResult.csv", "w", newline="", encoding="utf-8-sig") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(["id", "host", "URL", "requestHeaders", "requestBody", "responseHeaders", "responseBody", "way"])
        csv_writer.writerows(http_message_special)
        csv_writer.writerow([])
        csv_writer.writerow(["requestHeaders and requestBody", "requestHeaders", "requestBody"])
        csv_writer.writerow([PII_request_count, PII_requestHeaders_count, PII_requestBody_count])
        
    # print(http_message_special)
    # print(PII_request_count)
    # print(PII_requestHeaders_count)
    # print(PII_requestBody_count)

    db_connection.close()