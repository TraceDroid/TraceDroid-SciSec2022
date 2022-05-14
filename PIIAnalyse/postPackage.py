import re
import os
import pathlib
import csv
import pymysql

device_info = re.compile(r'8BSX1EQGX|8A2X0KKKF|358123091482602|990012001490561|3C:28:6D:E9:EF:1|android_id|androidid|AndroidID|2028.*1080|1080.*2080|2160.*1080|1080.*2060|manufacturer|idfa=|"idfa"|imsi=|"imsi"')
location_info = re.compile(r"bid.*cid.*nid.*sid|116\.23.*39\.95|39\.95.*116\.23|%E5%8C%97%E4%BA%AC")
network_info = re.compile(r"NETGEAR67|TP-LINK_3F66|WIN-N1USSIJ01UP.*2755|DESKTOP-LP51G8E.*2199|HONOR-10F78E|192\.168\.[0-9]+\.[0-9]+|52:e0:85:c0:2d:e4|b6:6d:83:11:fa:30")

keyvalue = re.compile(r"=")
json = re.compile(r".*{.*:.*}.*")

privacy = re.compile(r'8BSX1EQGX|8A2X0KKKF|358123091482602|990012001490561|3C:28:6D:E9:EF:1|android_id|androidid|AndroidID|2028.*1080|1080.*2080|2160.*1080|1080.*2060|manufacturer|idfa=|"idfa"|imsi=|"imsi"|bid.*cid.*nid.*sid|116\.23.*39\.95|39\.95.*116\.23|%E5%8C%97%E4%BA%AC|NETGEAR67|TP-LINK_3F66|WIN-N1USSIJ01UP.*2755|DESKTOP-LP51G8E.*2199|HONOR-10F78E|192\.168\.[0-9]+\.[0-9]+|52:e0:85:c0:2d:e4|b6:6d:83:11:fa:30')


def get_db_connection(database_name) -> pymysql.Connection:
    host = "*"
    port = 3306
    user = "*"
    password = "*"
    db_connection = pymysql.connect(host=host, port=port, user=user, password=password, database=database_name)
    return db_connection


def get_request():
    select_sql = r"select stack, packageName from APKDB.HTTP where requestBody like '%com.google.android.googlequicksearchbox%'"
    db_connection = get_db_connection("APKDB")
    db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
    db_cursor.execute(select_sql)
    postfile_list = db_cursor.fetchall()
    db_connection.close()
    print("select done")
    return postfile_list


def get_lib():
    with open("lib_list.txt", "r") as f:
        lib_list = f.read().split(" \n")
    return lib_list


def count_app_lib():
    postfile_list = get_request()
    lib_list = get_lib()
    packageName_count = set()
    lib_count = set()
    for http_message in postfile_list:
        packageName_count.add(http_message["packageName"])
        if http_message["stack"] is None:
            continue
        if "None" in http_message["stack"]:
            continue
        for lib in lib_list:
            if lib in http_message["stack"]:
                lib_count.add(lib)

    print("app count:", len(packageName_count))
    print("lib count:", len(lib_count))

if __name__ == '__main__':
    count_app_lib()






