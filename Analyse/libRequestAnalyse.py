import csv
import pymysql
import time


def get_db_connection(database_name) -> pymysql.Connection:
    host = "10.10.103.147"
    port = 3306
    user = "root"
    password = "iiewlz666"
    db_connection = pymysql.connect(host=host, port=port, user=user, password=password, database=database_name)
    return db_connection


def get_http_message(db_connection):
    select_sql = "SELECT id, host, URL, requestHeaders, protocol, method, stack FROM HTTP"
    db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
    db_cursor.execute(select_sql)
    http_message_dict = db_cursor.fetchall()
    return http_message_dict


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


def get_lib_pattern_dict(lib, http_message_dict):
    # 取出某个域名对应的所有http_message，返回http_message_list,每个元素是字典（dict）

    lib_pattern_dict = {}
    for http_message in http_message_dict:
        # print(http_message)
        if http_message["stack"] is None:
            continue
        if "None" in http_message["stack"]:
            continue
        if lib not in http_message["stack"]:
            continue
        # pattern: (method, protocol, path, host, key_list)
        pattern = convert_to_url_pattern(http_message)
        if pattern is None:
            continue
        message = [http_message["id"], http_message["method"], http_message["requestHeaders"]]
        if lib_pattern_dict.get(pattern, None) is None:
            lib_pattern_dict.update({pattern: [message]})
        else:
            lib_pattern_dict[pattern].append(message)
    print("lib_pattern_dict finished")
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    return lib_pattern_dict


def get_lib():
    with open("lib_list.txt", "r") as f:
        lib_list = f.read().split(" \n")
    return lib_list


if __name__ == '__main__':

    lib_list = get_lib()
    db_connection = get_db_connection("APKDB")
    http_message_dict = get_http_message(db_connection)
    with open("libRequestAnalyse.csv", "w", newline="", encoding="utf-8-sig") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(["lib", "pattern", "id", "method", "requestHeaders"])

        for lib in lib_list:
            lib_pattern_dict = get_lib_pattern_dict(lib, http_message_dict)
            for pattern, http_message_list in lib_pattern_dict.items():
                for http_message in http_message_list:
                    csv_writer.writerow([lib, pattern, http_message[0], http_message[1], http_message[2]])
                csv_writer.writerow([])
            # print(lib_pattern_dict)
            csv_writer.writerows([[], []])
  

    db_connection.close()

