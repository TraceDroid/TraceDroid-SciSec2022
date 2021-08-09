import time

import pymysql


def get_db_connection(database_name) -> pymysql.Connection:
    host = "10.10.103.147"
    port = 3306
    user = "root"
    password = "iiewlz666"
    db_connection = pymysql.connect(host=host, port=port, user=user, password=password, database=database_name)
    return db_connection


if __name__ == '__main__':

    db_connection = get_db_connection("APK_BlcDing")
    db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)

    id_four_tuple_list = []

    # begin_id = 1
    # end_id = 201450

    # select_sql = "SELECT * FROM HTTP WHERE id >= %s and id <= %s"
    select_sql = "SELECT * FROM HTTP"

    update_sql = "UPDATE HTTP SET four_tuple_hash = %s WHERE id = %s"

    db_cursor.execute(select_sql)
    http_message_list = db_cursor.fetchall()
    for http_message in http_message_list:
        id = http_message["id"]
        packageName = http_message["packageName"]
        srcAddr = http_message["srcAddr"]
        srcPort = http_message["srcPort"]
        dstAddr = http_message["dstAddr"]
        dstPort = http_message["dstPort"]
        four_tuple_str = str(packageName) + str(dstAddr) + str(dstPort) + str(srcAddr) + str(srcPort)
        id_four_tuple_list.append((four_tuple_str, id))
    print("select finished!")
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    try:
        print("update start")
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        db_cursor.executemany(update_sql, id_four_tuple_list)
        db_connection.commit()
        print("update finished!")
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    except Exception as e:
        print(e)
        db_connection.rollback()

    db_connection.close()
