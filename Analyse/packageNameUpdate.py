import os
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

    root_path = '/home/chj/APKTestEngine2/APKFileDir/totalAPK/'
    os.chdir(root_path)

    db_connection = get_db_connection("APKDB")
    db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)

    select_sql = 'SELECT packageName FROM HTTP group by packageName'

    select_sql_2 = "select * from HTTP where host like "

    update_sql = 'UPDATE HTTP SET packageName = %s, host = %s WHERE id = %s'

    apk_package_dict = {}

    print("START!")
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    db_cursor.execute(select_sql)
    http_message_list_by_packageName = db_cursor.fetchall()
    print("http_message_list_by_packageName len is: %s " % http_message_list_by_packageName.__len__())
    with open("failedAPK", "w", encoding="utf-8") as failedAPKS:
        for hm in http_message_list_by_packageName:
            try:
                apk = hm["packageName"]
                find_package_name_command = 'aapt dump badging %s' % apk
                output = os.popen(find_package_name_command).read()
                packageName_tmp = output.split("package: name='", 1)[1]
                packageName = packageName_tmp.split("'", 1)[0]
                apk_package_dict[apk] = packageName
            except Exception as e:
                print(e)
                failedAPKS.write(apk)
                failedAPKS.write("\r")

    with open("apk_package_dict", "w", encoding="utf-8") as apk_package_dict_file:
        apk_package_dict_file.write(str(apk_package_dict))
    print(apk_package_dict)
    print("apk_package_dict size is: %s" % len(apk_package_dict))

    update_package_sql = "update HTTP set packageName = %s where packageName = %s"
    sql_list = []
    for apk, packageName in apk_package_dict.items():
        sql_list.append((packageName, apk))
    print(sql_list)
    print("sql_list size is: %s" % sql_list.__len__())

    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    print("begin update packageName......")
    # try:
    #     db_cursor.executemany(update_package_sql, sql_list)
    #     db_connection.commit()
    # except Exception as e:
    #     print(e)
    #     db_connection.rollback()
    ii = 1
    for item in sql_list:
        try:
            print("package num: %s " % ii)
            db_cursor.execute(update_package_sql, item)
            db_connection.commit()
            ii = ii + 1
        except Exception as e:
            print("update error: " + str(item))
            print(e)

    db_connection.close()
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    print("end update packageName.")
