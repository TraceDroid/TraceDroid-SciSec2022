import re
import os
import pathlib
import csv
import pymysql
import time

# 生成csv，展示每个app集成的第三方库

def get_db_connection(database_name) -> pymysql.Connection:
    host = "*"
    port = 3306
    user = "*"
    password = "*"
    db_connection = pymysql.connect(host=host, port=port, user=user, password=password, database=database_name)
    return db_connection


def get_http_message(db_connection):
    select_sql = "SELECT packageName, stack FROM HTTP"
    db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
    db_cursor.execute(select_sql)
    http_message_dict = db_cursor.fetchall()
    return http_message_dict


def get_lib():
    with open("lib_list.txt", "r") as f:
        lib_list = f.read().split(" \n")
    return lib_list


if __name__ == '__main__':
 

    lib_list = get_lib()
    db_connection = get_db_connection("APKDB")
    http_message_dict = get_http_message(db_connection)
    app_lib = {}
    

    for http_message in http_message_dict:
        if http_message["packageName"] not in app_lib:
            app_lib[http_message["packageName"]] = set()
        for lib in lib_list:
            if http_message["stack"] is None:
                continue
            if "None" in http_message["stack"]:
                continue
            if lib in http_message["stack"]:
                app_lib[http_message["packageName"]].add(lib)
            
    with open("appLibAnalyse.csv", "w", newline="", encoding="utf-8-sig") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(["packageName", "lib"])
        for app, lib in app_lib.items():
            csv_writer.writerow([app, lib])  

    db_connection.close()

