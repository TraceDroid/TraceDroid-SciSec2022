import re
import os
import pathlib
import csv
import pymysql

# lib、app上传文件统计分析

device_info = re.compile(r'8BSX1EQGX|8A2X0KKKF|358123091482602|990012001490561|3C:28:6D:E9:EF:1|android_id|androidid|AndroidID|2028.*1080|1080.*2080|2160.*1080|1080.*2060|manufacturer|idfa=|"idfa"|imsi=|"imsi"')
location_info = re.compile(r"bid.*cid.*nid.*sid|116\.23.*39\.95|39\.95.*116\.23|%E5%8C%97%E4%BA%AC")
network_info = re.compile(r"NETGEAR67|TP-LINK_3F66|WIN-N1USSIJ01UP.*2755|DESKTOP-LP51G8E.*2199|HONOR-10F78E|192\.168\.[0-9]+\.[0-9]+|52:e0:85:c0:2d:e4|b6:6d:83:11:fa:30")

keyvalue = re.compile(r"=")
json = re.compile(r".*{.*:.*}.*")

privacy = re.compile(r'8BSX1EQGX|8A2X0KKKF|358123091482602|990012001490561|3C:28:6D:E9:EF:1|android_id|androidid|AndroidID|2028.*1080|1080.*2080|2160.*1080|1080.*2060|manufacturer|idfa=|"idfa"|imsi=|"imsi"|bid.*cid.*nid.*sid|116\.23.*39\.95|39\.95.*116\.23|%E5%8C%97%E4%BA%AC|NETGEAR67|TP-LINK_3F66|WIN-N1USSIJ01UP.*2755|DESKTOP-LP51G8E.*2199|HONOR-10F78E|192\.168\.[0-9]+\.[0-9]+|52:e0:85:c0:2d:e4|b6:6d:83:11:fa:30')


def get_db_connection(database_name) -> pymysql.Connection:
    host = "10.10.103.147"
    port = 3306
    user = "root"
    password = "iiewlz666"
    db_connection = pymysql.connect(host=host, port=port, user=user, password=password, database=database_name)
    return db_connection


# 获取post文件的请求
def get_file():
    select_sql = "select packageName, requestBody, stack from HTTP where requestBody like '%.pcap__%'"
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


# 获取文件是lib发的还是app发的
# 获取每个lib发出的文件名
def postfile_way_count():
    postfile_list = get_file()
    lib_list = get_lib()
    print(len(lib_list))
    packageName = set()
    lib_count = set()
    result = {
        "app" : 0,
        "lib" : 0,
    }
    lib_file = {}
    for http_message in postfile_list:
        packageName.add(http_message["packageName"])
        if http_message["stack"] is None:
            continue
        if "None" in http_message["stack"]:
            continue
        for lib in lib_list:
            if lib in http_message["stack"]:
                # lib_count.add(lib)
                # result["lib"] += 1
                file = http_message["requestBody"].split(".pcap__")[-1]
                file = file.split("__", 2)[-1]
                if lib not in lib_file:
                    lib_file[lib] = [http_message["requestBody"]]
                    # lib_file[lib] = set()
                    # lib_file[lib].add(file)
                else:
                    # lib_file[lib].add(file)
                    lib_file[lib].append(http_message["requestBody"])
                break
    
    result["app"] = len(postfile_list) - result["lib"]
    # print(result)
    # print("package count:", len(packageName))
    # print("lib count:", len(lib_count))

    with open("libFile.csv", "w", newline="", encoding="utf-8-sig") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(["lib", "filecount", "file"])
        result = []
        for lib, file in lib_file.items():
                result.append([lib, len(file), file])
        csv_writer.writerows(result)
    # print(lib_file)


# 获取lib发出的文件计数
def lib_postfile_count():
    postfile_list = get_file()
    lib_list = get_lib()
    print(len(lib_list))
    result = {}
    for http_message in postfile_list:
        if http_message["stack"] is None:
            continue
        if "None" in http_message["stack"]:
            continue
        for lib in lib_list:
            if lib in http_message["stack"]:
                if lib not in result:
                    result[lib] = 1
                else:
                    result[lib] += 1
    
    with open("lib_postfile_count.csv", "w", newline="", encoding="utf-8-sig") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(["lib", "count"])
        for lib, count in result.items():
            csv_writer.writerow([lib, count])


# 文件类型（后缀）统计
def postfile_analyse():
    postfile_list = get_file()
    result = {
        "none": 0,
    }
    for http_message in postfile_list:
        res = http_message["requestBody"].rsplit(".", 1)[-1]
        if "__" in res:
            result["none"] += 1
        elif res not in result:
            result[res] = 1
        else:
            result[res] += 1
    print(result)

if __name__ == '__main__':
    postfile_way_count()
    # lib_postfile_count()
    # postfile_analyse()
