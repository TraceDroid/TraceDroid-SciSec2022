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

def get_file():
    select_sql = "select requestBody from HTTP where requestBody like '%.gz' or requestBody like '%.log' or requestBody like '%.zip' or requestBody like '%.txt'"
    db_connection = get_db_connection("APKDB")
    db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
    db_cursor.execute(select_sql)
    postfile_list = db_cursor.fetchall()
    db_connection.close()
    return postfile_list

def get_privacy_message(postfile_list):
    analyse_path = "/home/chj/APKTestEngine/PcapExtract/in/"
    unzip_path = "/home/chj/APKTestEngine/PcapExtract/in/unzip/"
    path = pathlib.Path(unzip_path)
    if not path.exists():
        path.mkdir()
    os.chdir(analyse_path)

    device_count = 0
    location_count = 0
    network_count = 0

    keyvalue_count = 0
    json_count = 0

    gzip = 0

    for postfiles in postfile_list:
        for file in postfiles.values():
            # print(file)
            try:
                if file[-3:] == ".gz":
                    unzip_file_path = unzip_path + file[:-3]
                    unzip_command = "gzip -d -c -q {} > {}".format(file, unzip_file_path)
                    os.system(unzip_command)
                    if os.path.exists(unzip_file_path):
                        content = open(unzip_file_path, "r", encoding="utf-8").readlines()
                        # print(content)
                        if len(device_info.findall(str(content))) > 0:
                            device_count += 1
                        if len(location_info.findall(str(content))) > 0:
                            location_count += 1
                        if len(network_info.findall(str(content))) > 0:
                            network_count += 1
                        if len(privacy.findall(str(content))) > 0:
                            gzip += 1
                            if len(json.findall(str(content))) > 0:
                                json_count += 1
                            elif len(keyvalue.findall(str(content))) > 0:
                                keyvalue_count += 1
                            
                if file[-4:] == ".zip":
                    unzip_file_path = unzip_path + file[:-4] + "/"
                    path = pathlib.Path(unzip_file_path)
                    if not path.exists():
                        path.mkdir()
                    unzip_command = "unzip -q -o {} -d {}".format(file, unzip_file_path)
                    os.system(unzip_command)

                    if os.path.exists(unzip_file_path):
                        for x in os.listdir(unzip_file_path):
                            content = open(unzip_file_path + x, "r", encoding="utf-8").readlines()
                            if len(device_info.findall(str(content))) > 0:
                                device_count += 1
                            if len(location_info.findall(str(content))) > 0:
                                location_count += 1
                            if len(network_info.findall(str(content))) > 0:
                                network_count += 1
                            if len(privacy.findall(str(content))) > 0:
                                if len(json.findall(str(content))) > 0:
                                    json_count += 1
                                elif len(keyvalue.findall(str(content))) > 0:
                                    keyvalue_count += 1
                if file[-4:] == ".log":
                    if os.path.exists(file):
                        content = open(file, "r", encoding="utf-8").readlines()
                        if len(device_info.findall(str(content))) > 0:
                            device_count += 1
                        if len(location_info.findall(str(content))) > 0:
                            location_count += 1
                        if len(network_info.findall(str(content))) > 0:
                            network_count += 1
                        if len(privacy.findall(str(content))) > 0:
                            if len(json.findall(str(content))) > 0:
                                json_count += 1
                            elif len(keyvalue.findall(str(content))) > 0:
                                keyvalue_count += 1
                if file[-4:] == ".txt":
                    if os.path.exists(file):
                        content = open(file, "r", encoding="utf-8").readlines()
                        if len(device_info.findall(str(content))) > 0:
                            device_count += 1
                        if len(location_info.findall(str(content))) > 0:
                            location_count += 1
                        if len(network_info.findall(str(content))) > 0:
                            network_count += 1
                        if len(privacy.findall(str(content))) > 0:
                            if len(json.findall(str(content))) > 0:
                                json_count += 1
                            elif len(keyvalue.findall(str(content))) > 0:
                                keyvalue_count += 1
            except Exception as e:
                # print(e)
                pass

    return {
        "device info": device_count,
        "location info": location_count,
        "network info": network_count,
        "keyvalue": keyvalue_count,
        "json": json_count,
        "gzip": gzip
    }


if __name__ == '__main__':
    postfile_list = get_file()
    # print(postfile_list)
    result = get_privacy_message(postfile_list)
    print(result)





