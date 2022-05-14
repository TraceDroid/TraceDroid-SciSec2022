import csv
import re
import pymysql


device_info = re.compile(r'8BSX1EQGX|8A2X0KKKF|358123091482602|990012001490561|3C:28:6D:E9:EF:1F|android_id|androidid|AndroidID|2028.*1080|1080.*2080|2160.*1080|1080.*2060|manufacturer|idfa=|"idfa"|imsi=|"imsi"')
location_info = re.compile(r"bid.*cid.*nid.*sid|116\.23.*39\.95|39\.95.*116\.23|%E5%8C%97%E4%BA%AC")
network_info = re.compile(r"NETGEAR67|TP-LINK_3F66|WIN-N1USSIJ01UP.*2755|DESKTOP-LP51G8E.*2199|HONOR-10F78E|192\.168\.[0-9]+\.[0-9]+|52:e0:85:c0:2d:e4|b6:6d:83:11:fa:30")

keyvalue = re.compile(r"=")
json = re.compile(r".*{.*:.*}.*")

urlencoded = re.compile(r"%")
gzip = re.compile(r"gzip")


def get_db_connection(database_name) -> pymysql.Connection:
    host = "*"
    port = 3306
    user = "*"
    password = "*"
    db_connection = pymysql.connect(host=host, port=port, user=user, password=password, database=database_name)
    return db_connection


def get_http_message(db_connection):
    select_sql = "select packageName, requestHeaders, requestBody, URL from HTTP"
    # print(select_sql)
    db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
    db_cursor.execute(select_sql)
    http_message_dict = db_cursor.fetchall()
    return http_message_dict


if __name__ == '__main__':
    db_connection = get_db_connection("APKDB")
    http_message_dict = get_http_message(db_connection)
    print("select done")

    pii_count = {
        "headers": {},
        "body": {},
        "url": {}
    }

    pii_way_count = {
        "headers": {},
        "body": {},
        "url": {}
    }

    pii_code_count = {
        "headers": {},
        "body": {},
        "url": {}       
    }

    for position in pii_count.keys():
        pii_count[position] = {
            "device_info": 0,
            "location_info": 0,
            "network_info": 0
        }
    for position in pii_way_count.keys():
        pii_way_count[position] = {
            "all": 0,
            "json": 0,
            "keyvalue": 0   
        }
    for position in pii_code_count.keys():
        pii_code_count[position] = {
            "urlencoded": 0,
            "gzip": 0
        }


    for http_message in http_message_dict:
        if len(device_info.findall(http_message["requestHeaders"], re.IGNORECASE)) > 0:
            pii_count["headers"]["device_info"] += 1
        if len(device_info.findall(http_message["requestBody"], re.IGNORECASE)) > 0:
            pii_count["body"]["device_info"] += 1
        if len(device_info.findall(http_message["URL"], re.IGNORECASE)) > 0:
            pii_count["url"]["device_info"] += 1
        if len(location_info.findall(http_message["requestHeaders"], re.IGNORECASE)) > 0:
            pii_count["headers"]["location_info"] += 1
        if len(location_info.findall(http_message["requestBody"], re.IGNORECASE)) > 0:
            pii_count["body"]["location_info"] += 1
        if len(location_info.findall(http_message["URL"], re.IGNORECASE)) > 0:
            pii_count["url"]["location_info"] += 1
        if len(network_info.findall(http_message["requestHeaders"], re.IGNORECASE)) > 0:
            pii_count["headers"]["network_info"] += 1
        if len(network_info.findall(http_message["requestBody"], re.IGNORECASE)) > 0:
            pii_count["body"]["network_info"] += 1
        if len(network_info.findall(http_message["URL"], re.IGNORECASE)) > 0:
            pii_count["url"]["network_info"] += 1


        if len(device_info.findall(http_message["requestBody"], re.IGNORECASE)) > 0 or len(location_info.findall(http_message["requestBody"], re.IGNORECASE)) > 0 or len(network_info.findall(http_message["requestBody"], re.IGNORECASE)) > 0:
            pii_way_count["body"]["all"] += 1
            if len(json.findall(http_message["requestBody"])) > 0:
                pii_way_count["body"]["json"] += 1
            elif len(keyvalue.findall(http_message["requestBody"])) > 0:
                pii_way_count["body"]["keyvalue"] += 1
        if len(device_info.findall(http_message["URL"], re.IGNORECASE)) > 0 or len(location_info.findall(http_message["URL"], re.IGNORECASE)) > 0 or len(network_info.findall(http_message["URL"], re.IGNORECASE)) > 0:
            if len(keyvalue.findall(http_message["URL"])) > 0:
                pii_way_count["url"]["all"] += 1
                pii_way_count["url"]["keyvalue"] += 1
        

        if len(device_info.findall(http_message["requestBody"], re.IGNORECASE)) > 0 or len(location_info.findall(http_message["requestBody"], re.IGNORECASE)) > 0 or len(network_info.findall(http_message["requestBody"], re.IGNORECASE)) > 0:
            if len(urlencoded.findall(http_message["requestBody"])) > 0:
                pii_code_count["body"]["urlencoded"] += 1
            if len(gzip.findall(http_message["requestHeaders"])) > 0:
                pii_code_count["body"]["gzip"] += 1
        if len(device_info.findall(http_message["URL"], re.IGNORECASE)) > 0 or len(location_info.findall(http_message["URL"], re.IGNORECASE)) > 0 or len(network_info.findall(http_message["URL"], re.IGNORECASE)) > 0:
            if len(urlencoded.findall(http_message["URL"])) > 0:
                pii_code_count["url"]["urlencoded"] += 1



    with open("PIIAnalyse.csv", "w", newline="", encoding="utf-8-sig") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(["", "device info", "location info", "network info"])
        for position in pii_count.keys():
            result = [position]
            for count in pii_count[position].values():
                result.append(count)
            csv_writer.writerow(result)
        csv_writer.writerows([[], []])

        csv_writer.writerow(["", "key-value", "json", "plain txt"])
        for position in pii_way_count.keys():
            result = [position]
            result.append(pii_way_count[position]["keyvalue"])
            result.append(pii_way_count[position]["json"])
            result.append(pii_way_count[position]["all"] - pii_way_count[position]["json"] - pii_way_count[position]["keyvalue"])
            csv_writer.writerow(result)
        csv_writer.writerows([[], []])

        csv_writer.writerow(["", "urlencoded", "gzip"])
        for position in pii_code_count.keys():
            result = [position]
            result.append(pii_code_count[position]["urlencoded"])
            result.append(pii_code_count[position]["gzip"])
            csv_writer.writerow(result)
        csv_writer.writerows([[], []])
        


    
    db_connection.close()