import csv
import pymysql
import time
import re


device_info = re.compile(r'8BSX1EQGX|8A2X0KKKF|358123091482602|990012001490561|3C:28:6D:E9:EF:1|android_id|androidid|AndroidID|2028.*1080|1080.*2080|2160.*1080|1080.*2060|manufacturer|idfa=|"idfa"|imsi=|"imsi"')
location_info = re.compile(r"bid.*cid.*nid.*sid|116\.23.*39\.95|39\.95.*116\.23|%E5%8C%97%E4%BA%AC")
network_info = re.compile(r"NETGEAR67|TP-LINK_3F66|WIN-N1USSIJ01UP.*2755|DESKTOP-LP51G8E.*2199|HONOR-10F78E|192\.168\.[0-9]+\.[0-9]+|52:e0:85:c0:2d:e4|b6:6d:83:11:fa:30")


def get_db_connection(database_name) -> pymysql.Connection:
    host = "*"
    port = 3306
    user = "*"
    password = "*"
    db_connection = pymysql.connect(host=host, port=port, user=user, password=password, database=database_name)
    return db_connection


def get_http_message():
    db_connection = get_db_connection("APKDB")
    select_sql = "SELECT packageName, host, URL, requestHeaders, requestBody, stack FROM HTTP"
    db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
    db_cursor.execute(select_sql)
    http_message_dict = db_cursor.fetchall()
    db_connection.close()
    print("select done")
    return http_message_dict


def get_lib():
    with open("lib_list.txt", "r") as f:
        lib_list = f.read().split(" \n")
    return lib_list


def get_lib_host_app():
    http_message_dict = get_http_message()

    lib_list = get_lib()
    lib_host_app = {}
    for lib in lib_list:
        lib_host_app[lib] = {}

    for http_message in http_message_dict:
        if http_message["stack"] is None:
            continue
        if "None" in http_message["stack"]:
            continue
        for lib in lib_list:
            if lib in http_message["stack"]:
                if (len(device_info.findall(http_message["requestHeaders"], re.IGNORECASE)) > 0 or len(device_info.findall(http_message["requestBody"], re.IGNORECASE)) > 0 or len(device_info.findall(http_message["URL"], re.IGNORECASE)) > 0) \
                        or (len(location_info.findall(http_message["requestHeaders"], re.IGNORECASE)) > 0 or len(location_info.findall(http_message["requestBody"], re.IGNORECASE)) > 0 or len(location_info.findall(http_message["URL"], re.IGNORECASE)) > 0) \
                        or (len(network_info.findall(http_message["requestHeaders"], re.IGNORECASE)) > 0 or len(network_info.findall(http_message["requestBody"], re.IGNORECASE)) > 0 or len(network_info.findall(http_message["URL"], re.IGNORECASE)) > 0):
                    if http_message["host"] not in lib_host_app[lib]:
                        lib_host_app[lib][http_message["host"]] = set()
                        lib_host_app[lib][http_message["host"]].add(http_message["packageName"])
                    else:
                        lib_host_app[lib][http_message["host"]].add(http_message["packageName"])
    return lib_host_app

if __name__ == '__main__':

    lib_host_app = get_lib_host_app()

    with open("libHostAPP.csv", "w", newline="", encoding="utf-8-sig") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(["lib", "host", "host count", "app", "app count"])
        result = []
        for lib in lib_host_app.keys():
            for host, app in lib_host_app[lib].items():
                result.append([lib, host, len(lib_host_app[lib]), app, len(app)])
        csv_writer.writerows(result)
