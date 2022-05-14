import sys
import pymysql

import DBUtils


def init_http_dict():
    DBConnection = DBUtils.get_db_connection()
    select_sql = "select * from HTTP"
    DBCursor = DBConnection.cursor(pymysql.cursors.DictCursor)
    DBCursor.execute(select_sql)
    http_dict = {}
    http_message_list = DBCursor.fetchall()
    i = 1
    print("http_message_list size is: %s " % http_message_list.__len__())
    print("http_message_list memory size is %s" % sys.getsizeof(http_message_list))
    for httpMessage in http_message_list:
        if httpMessage["four_tuple_hash"] not in http_dict:
            http_dict[httpMessage["four_tuple_hash"]] = httpMessage
        else:
            host = http_dict[httpMessage["four_tuple_hash"]]["host"]
            if host != httpMessage["host"]:
                print(str(i))
                print(host)
                print(httpMessage["host"])
                print(httpMessage["four_tuple_hash"])

                print()
                i = i + 1
            #print(httpMessage["four_tuple_hash"] + " host: " + httpMessage["host"])


    print("http_dict size is: %s " % len(http_dict))
    print("http_dict memory size is: %s" % sys.getsizeof(http_dict))
    return http_dict

if __name__ == '__main__':
    init_http_dict()