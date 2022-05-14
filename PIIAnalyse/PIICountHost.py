import csv
import re
import pymysql


device_info = re.compile(r'8BSX1EQGX|8A2X0KKKF|358123091482602|990012001490561|3C:28:6D:E9:EF:1F|android_id|androidid|AndroidID|2028.*1080|1080.*2080|2160.*1080|1080.*2060|manufacturer|idfa=|"idfa"|imsi=|"imsi"')
location_info = re.compile(r"bid.*cid.*nid.*sid|116\.23.*39\.95|39\.95.*116\.23|%E5%8C%97%E4%BA%AC")
network_info = re.compile(r"NETGEAR67|TP-LINK_3F66|WIN-N1USSIJ01UP.*2755|DESKTOP-LP51G8E.*2199|HONOR-10F78E|192\.168\.[0-9]+\.[0-9]+|52:e0:85:c0:2d:e4|b6:6d:83:11:fa:30")


def get_db_connection(database_name) -> pymysql.Connection:
    host = "*"
    port = 3306
    user = "*"
    password = "*"
    db_connection = pymysql.connect(host=host, port=port, user=user, password=password, database=database_name)
    return db_connection


def get_http_message(db_connection):
    select_sql = "select requestHeaders, requestBody, URL, host, packageName from HTTP"
    # print(select_sql)
    db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
    db_cursor.execute(select_sql)
    http_message_dict = db_cursor.fetchall()
    return http_message_dict


if __name__ == '__main__':
    db_connection = get_db_connection("APKDB")
    http_message_dict = get_http_message(db_connection)
    print("select done")

    result = {
        "device_location_network": 0,
        "device_location": 0,
        "device_network": 0,
        "location_network": 0,
        "device": 0,
        "location": 0,
        "network": 0,
        "all": 0
    }

    host_app = {}
    


    for http_message in http_message_dict:

        if (len(device_info.findall(http_message["requestHeaders"], re.IGNORECASE)) > 0 or len(device_info.findall(http_message["requestBody"], re.IGNORECASE)) > 0 or len(device_info.findall(http_message["URL"], re.IGNORECASE)) > 0) \
                or (len(location_info.findall(http_message["requestHeaders"], re.IGNORECASE)) > 0 or len(location_info.findall(http_message["requestBody"], re.IGNORECASE)) > 0 or len(location_info.findall(http_message["URL"], re.IGNORECASE)) > 0) \
                or (len(network_info.findall(http_message["requestHeaders"], re.IGNORECASE)) > 0 or len(network_info.findall(http_message["requestBody"], re.IGNORECASE)) > 0 or len(network_info.findall(http_message["URL"], re.IGNORECASE)) > 0):
            result["all"] += 1
            if http_message["host"] not in host_app:
                host_app[http_message["host"]] = set()
                host_app[http_message["host"]].add(http_message["packageName"])
            else:
                host_app[http_message["host"]].add(http_message["packageName"])

    with open("hostAPP.csv", "w", newline="", encoding="utf-8-sig") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(["host", "app", "app count"])
        for host, mes in host_app.items():
            result = [host, mes, len(mes)]
            csv_writer.writerow(result)


    db_connection.close()