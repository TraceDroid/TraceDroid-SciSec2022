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
    # end_id = 263784

    select_sql = "SELECT * FROM Stack"

    update_sql = "UPDATE Stack SET four_tuple_hash = %s WHERE id = %s"

    db_cursor.execute(select_sql)
    stack_message_list = db_cursor.fetchall()
    for stack_message in stack_message_list:
        id = stack_message["id"]
        packageName = stack_message["packageName"]
        srcAddr = stack_message["srcAddr"]
        srcPort = stack_message["srcPort"]
        dstAddr = stack_message["dstAddr"]
        dstPort = stack_message["dstPort"]
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
