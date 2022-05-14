import csv
import re
import pymysql
import urllib.parse


def get_db_connection(database_name) -> pymysql.Connection:
    host = "*"
    port = 3306
    user = "*"
    password = "*"
    db_connection = pymysql.connect(host=host, port=port, user=user, password=password, database=database_name)
    return db_connection


def get_http_message(db_connection):
    select_sql = "SELECT * FROM APKDB.HTTP"
    db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
    db_cursor.execute(select_sql)
    http_message_dict = db_cursor.fetchall()
    hexcode = re.compile(r"\\x..\\x..\\x..\\x..")
    http_message_list = list()
    for http_message in http_message_dict:
        http_message["URL"] = urllib.parse.unquote(http_message["URL"])
        http_message["requestHeaders"] =  urllib.parse.unquote(http_message["requestHeaders"])
        http_message["requestBody"] = urllib.parse.unquote(http_message["requestBody"])
        if len(http_message["requestBody"]) == 0:
            http_message["requestBody"] = None
        if http_message["requestBody"] is not None:
            if len(hexcode.findall(http_message["requestBody"])) > 0:
                http_message["requestBody"] = None
        http_message["responseHeaders"] = urllib.parse.unquote(http_message["responseHeaders"])
        http_message["responseBody"] = urllib.parse.unquote(http_message["responseBody"])
        if len(http_message["responseBody"]) == 0:
            http_message["responseBody"] = None
        if http_message["responseBody"] is not None:
            if len(hexcode.findall(http_message["responseBody"])) > 0:
                http_message["responseBody"] = None

        http_message_list.append((
            http_message["id"],
            http_message["packageName"],
            http_message["srcAddr"],
            http_message["srcPort"],
            http_message["dstAddr"],
            http_message["dstPort"],
            http_message["host"],
            http_message["URL"],
            http_message["requestHeaders"],
            http_message["requestBody"],
            http_message["responseHeaders"],
            http_message["responseBody"],
            http_message["protocol"],
            http_message["method"],
            http_message["contentType"],
            http_message["four_tuple_hash"],
            http_message["stack"],
        ))
    return http_message_list


def insert_HTTP_urldecoded(db_connection, http_message_list):
    db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)

    try:
        insert_sql = "INSERT INTO APKDB.HTTP_urldecoded (id, packageName, srcAddr, srcPort, dstAddr, dstPort, host, URL, requestHeaders, requestBody, responseHeaders, responseBody, protocol, method, contentType, four_tuple_hash, stack) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        db_cursor.executemany(insert_sql, http_message_list)
        db_connection.commit()
    except Exception as e:
        print(e)
        db_connection.rollback()    


if __name__ == '__main__':

    db_connection = get_db_connection("APKDB")
    http_message_list = get_http_message(db_connection)
    print("select done")
    insert_HTTP_urldecoded(db_connection, http_message_list)
  
    db_connection.close()