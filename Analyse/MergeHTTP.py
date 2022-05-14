import time
import pymysql


def get_db_connection(database_name) -> pymysql.Connection:
    host = "*"
    port = 3306
    user = "*"
    password = "*"
    db_connection = pymysql.connect(host=host, port=port, user=user, password=password, database=database_name)
    return db_connection


if __name__ == '__main__':
    # db_connection1 = get_db_connection("APKDB")
    # db_connection2 = get_db_connection("APKDB2")
    db_connection1 = get_db_connection("APKDB")
    db_connection2 = get_db_connection("APKDB_BlcDing2")
    db_cursor1 = db_connection1.cursor(pymysql.cursors.DictCursor)
    db_cursor2 = db_connection2.cursor(pymysql.cursors.DictCursor)

    http_list = []

    # begin_id = 1
    # end_id = begin_id + 10000

    begin_id = 465292
    end_id = begin_id + 10000

    select_sql = "SELECT * FROM HTTP WHERE id >= %s AND id < %s"

    insert_sql = "INSERT INTO HTTP (packageName, srcAddr, srcPort, dstAddr, dstPort, host, URL, requestTime, " \
                 "requestHeaders, requestBody, responseHeaders, responseBody, protocol, method, contentType, " \
                 "four_tuple_hash) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "

    #  循环6次
    for i in range(1, 7):
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        print("round: %s" % i)
        http_list = []

        db_cursor2.execute(select_sql, (begin_id, end_id))
        http_message_list = db_cursor2.fetchall()
        if http_message_list.__len__() == 0:
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            print("task finished")
        print("http_message_list size: %s" % http_message_list.__len__())
        for http_message in http_message_list:
            srcAddr = http_message["srcAddr"]
            srcPort = http_message["srcPort"]
            dstAddr = http_message["dstAddr"]
            dstPort = http_message["dstPort"]
            four_tuple_str = str(srcAddr) + str(srcPort) + str(dstAddr) + str(dstPort)

            http_list.append((http_message["packageName"], srcAddr, srcPort,
                              dstAddr, dstPort, http_message["host"], http_message["URL"],
                              http_message["requestTime"], http_message["requestHeaders"], http_message["requestBody"],
                              http_message["responseHeaders"], http_message["responseBody"], http_message["protocol"],
                              http_message["method"], http_message["contentType"], four_tuple_str))
        try:
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            print("inserting http_list, size: %s" % http_list.__len__())
            db_cursor1.executemany(insert_sql, http_list)
            db_connection1.commit()
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            print("insert finished")
        except Exception as e:
            print(e)
            # logger.error(stack[8])
            db_connection1.rollback()

        begin_id = begin_id + 10000
        end_id = end_id + 10000

    db_connection1.close()
    db_connection2.close()



