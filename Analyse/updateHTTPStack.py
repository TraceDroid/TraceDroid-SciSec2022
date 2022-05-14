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

    db_connection = get_db_connection("APKDB")
    db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)

    id_stack_list = list()

    select_sql = "SELECT id, four_tuple_hash FROM HTTP ORDER BY id"
    db_cursor.execute(select_sql)
    http_message_list = db_cursor.fetchall()
    print("select HTTP finished!", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    select_sql_Stack = "SELECT stack, four_tuple_hash FROM Stack"
    db_cursor.execute(select_sql_Stack)
    results = db_cursor.fetchall()
    stack_four_tuple_hash_dict = dict()
    for stack_four_tuple_hash in results:
        # print(stack_four_tuple_hash)
        four_tuple_hash = stack_four_tuple_hash['four_tuple_hash']
        stack = stack_four_tuple_hash['stack']
        stack_four_tuple_hash_dict[four_tuple_hash] = stack
    print("select Stack finished!", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    
    # print(stack_four_tuple_hash_dict)

    for http_message in http_message_list:
        id = http_message["id"]
        four_tuple_hash = http_message["four_tuple_hash"]
        # print(id, four_tuple_hash)
        if stack_four_tuple_hash_dict.get(four_tuple_hash) is not None:
            stack = stack_four_tuple_hash_dict[four_tuple_hash]
            if stack is not None:
                id_stack_list.append((stack, id))
    # print(id_stack_list)

    update_sql = "UPDATE HTTP SET stack=%s WHERE id=%s"
    try:
        print("update start", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        db_cursor.executemany(update_sql, id_stack_list)
        db_connection.commit()
        print("update finished!", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    except Exception as e:
        print(e)
        db_connection.rollback()

    db_connection.close()
