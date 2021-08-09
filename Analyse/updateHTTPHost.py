import pymysql  # pip install pymysql


def get_db_connection() -> pymysql.Connection:
    """

    :return: 数据库连接
    """
    host = "10.10.103.147"
    port = 3306
    user = "root"
    password = "iiewlz666"
    database = "APKDB"
    db_connection = pymysql.connect(host=host, port=port, user=user, password=password, database=database)
    return db_connection


def execute_sql():
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)

    host_id_list = list()
    select_sql = "SELECT id, host FROM HTTP where host like '%:%' ORDER BY id"
    # select_sql = "describe CaptureLog"
    # select_sql = "show tables"
    # print(1)
    db_cursor.execute(select_sql)
    results = db_cursor.fetchall()
    for i in results:
        # print(i)
        host = i['host'].split(':')[0]
        host_id_list.append([host, i['id']])
    # print("host_id_list", host_id_list)

    try:
        update_sql = "UPDATE HTTP set host=%s where id=%s"
        db_cursor.executemany(update_sql, host_id_list)
        db_connection.commit()
    except Exception as e:
        print(e)
        db_connection.rollback()

    db_connection.close()


if __name__ == "__main__":
    execute_sql()
