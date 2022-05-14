import pymysql


def get_db_connection(database_name) -> pymysql.Connection:
    host = "*"
    port = 3306
    user = "*"
    password = "*"
    db_connection = pymysql.connect(host=host, port=port, user=user, password=password, database=database_name)
    return db_connection

def http_message2http_xdr(http_message_list):
    http_xdr_list = list()
    for http_message in http_message_list:
        http_xdr = {
            "ip_type": None,
            "vendor": None,
            "sip": None,
            "dip": None,
            "sport": None,
            "dport": None,
            "msg_type": None,
            "http_protocol": None,
            "method": None,
            "host": None,
            "uri": None,
            "referer": None,
            "user_agent": None,
            "proxy_authorization": None,
            "authorization": None,
            "cookies": None,
            "location": None,
            "x_forward_for": None,
            "accept_encoding": None,
            "date": None,
            "traile": None,
            "transfer_encoding": None,
            "via": None,
            "pragma": None,
            "connection": None,
            "cont_encoding": None,
            "cont_location": None,
            "cont_range": None,
            "cont_length": None,
            "cont_type": None,
            "charset": None,
            "transfer_length": None,
            "req_range": None,
            "http_request_body": None,
            "http_reply_body": None,
        }
        # http_xdr["version"] = ""
        # http_xdr["timestamp"] = ""
        http_xdr["ip_type"] = "IPv4"
        # http_xdr["dev_ip"] = ""  # 安全检测应用容器管理IP，一期不填
        # http_xdr["dev_id"] = ""  # 安全检测应用容器ID，一期不填
        http_xdr["vendor"] = "IIE"
        http_xdr["sip"] = http_message["srcAddr"]
        http_xdr["dip"] = http_message["dstAddr"]
        http_xdr["sport"] = http_message["srcPort"]
        http_xdr["dport"] = http_message["dstPort"]
        http_xdr["msg_type"] = "0001"
        # http_xdr["sid"] = ""  # 会话ID
        http_xdr["http_protocol"] = "HTTP/1.1"
        http_xdr["method"] = http_message["method"]
        http_xdr["host"] = http_message["host"]
        try:
            http_xdr["uri"] = "/" + http_message["URL"].split("://")[-1].split("/", 1)[1]
            http_xdr["uri"] = http_xdr["uri"][:1024]
        except Exception as e:
            http_xdr["uri"] = None
            # print(e)
            # print(http_message["URL"])

        try:
            requestHeaders = eval(http_message['requestHeaders'])
        except Exception:
            requestHeaders = dict()

        if "Referer" in requestHeaders:
            http_xdr["referer"] = ",".join(requestHeaders["Referer"])[:255]
        if "User-Agent" in requestHeaders:
            http_xdr["user_agent"] = ",".join(requestHeaders["User-Agent"])[:255]
        if "Proxy-Authorization" in requestHeaders:
            http_xdr["proxy_authorization"] = ",".join(requestHeaders["Proxy-Authorization"])[:255]
        if "Authorization" in requestHeaders:
            http_xdr["authorization"] = ",".join(requestHeaders["Authorization"])[:255]
        if "Cookie" in requestHeaders:
            http_xdr["cookies"] = ",".join(requestHeaders["Cookie"])[:1024]
        if "Location" in requestHeaders:
            http_xdr["location"] = ",".join(requestHeaders["Location"])[:255]
        # if "HTTP-Server" in requestHeaders:
        #     http_xdr["http_server"] = requestHeaders["HTTP-Server"]
        if "X-Forwarded-For" in requestHeaders:
            http_xdr["x_forward_for"] = ",".join(requestHeaders["X-Forwarded-For"])[:255]
        # http_xdr["ret_code"] = ""
        try:
            responseHeaders = eval(http_message['responseHeaders'])[:255]
        except Exception:
            responseHeaders = dict()
        if "Accept-Encoding" in requestHeaders:
            http_xdr["accept_encoding"] = ",".join(requestHeaders["Accept-Encoding"])[:255]
        if "Date" in responseHeaders:
            http_xdr["date"] = ",".join(responseHeaders["Date"])[:255]
        if "Trailer" in responseHeaders:
            http_xdr["traile"] = ",".join(responseHeaders["Trailer"])[:255]
        if "Transfer-Encoding" in responseHeaders:
            http_xdr["transfer_encoding"] = ",".join(responseHeaders["Transfer-Encoding"])[:255]
        if "Via" in responseHeaders:
            http_xdr["via"] = ",".join(responseHeaders["Via"])[:255]
        if "Pragma" in responseHeaders:
            http_xdr["pragma"] = ",".join(responseHeaders["Pragma"])[:255]
        if "Connection" in responseHeaders:
            http_xdr["connection"] = ",".join(responseHeaders["Connection"])[:255]
        if "Content-Encoding" in responseHeaders:
            http_xdr["cont_encoding"] = ",".join(responseHeaders["Content-Encoding"])[:255]
        # if "Language" in responseHeaders:
        #     http_xdr["language"] = responseHeaders["Language"]
        if "Content-Location" in responseHeaders:
            http_xdr["cont_location"] = ",".join(responseHeaders["Content-Location"])[:255]
        if "Content-Range" in responseHeaders:
            http_xdr["cont_range"] = ",".join(responseHeaders["Content-Range"])[:255]
        if "Content-Length" in responseHeaders:
            http_xdr["cont_length"] = ",".join(responseHeaders["Content-Length"])[:255]
        if "Content-Type" in responseHeaders:
            if len(responseHeaders["Content-Type"].split(";charset=")) == 2:
                http_xdr["cont_type"], http_xdr["charset"] = responseHeaders["Content-Type"].split(";charset=")
            else:
                http_xdr["cont_type"] = ",".join(responseHeaders["Content-Type"])
        # if "X-Flash-Version" in responseHeaders:
        #     http_xdr["x_flash_version"] = responseHeaders["X-Flash-Version"]
        if "Transfer-Length" in responseHeaders:
            http_xdr["transfer_length"] = ",".join(responseHeaders["Transfer-Length"])[:255]
        if "Range" in requestHeaders:
            http_xdr["req_range"] = ",".join(requestHeaders["Range"])[:255]
        # http_xdr["file_name"] = ""
        http_xdr["http_request_body"] = http_message["requestBody"][:40000]
        http_xdr["http_reply_body"] = http_message["responseBody"][:40000]
        
        http_xdr_list.append([
            http_xdr["ip_type"],
            http_xdr["vendor"],
            http_xdr["sip"],
            http_xdr["dip"],
            http_xdr["sport"],
            http_xdr["dport"],
            http_xdr["msg_type"],
            http_xdr["http_protocol"],
            http_xdr["method"],
            http_xdr["host"],
            http_xdr["uri"],
            http_xdr["referer"],
            http_xdr["user_agent"],
            http_xdr["proxy_authorization"],
            http_xdr["authorization"],
            http_xdr["cookies"],
            http_xdr["location"],
            http_xdr["x_forward_for"],
            http_xdr["accept_encoding"],
            http_xdr["date"],
            http_xdr["traile"],
            http_xdr["transfer_encoding"],
            http_xdr["via"],
            http_xdr["pragma"],
            http_xdr["connection"],
            http_xdr["cont_encoding"],
            http_xdr["cont_location"],
            http_xdr["cont_range"],
            http_xdr["cont_length"],
            http_xdr["cont_type"],
            http_xdr["charset"],
            http_xdr["transfer_length"],
            http_xdr["req_range"],
            http_xdr["http_request_body"],
            http_xdr["http_reply_body"]
        ])
    
    return http_xdr_list


if __name__ == '__main__':
    db_connection = get_db_connection("APKDB")
    db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
    select_sql = "SELECT * FROM APKDB.HTTP ORDER BY id"
    db_cursor.execute(select_sql)
    http_message_list = db_cursor.fetchall()
    http_xdr_list = http_message2http_xdr(http_message_list)
    # print(http_xdr_list)
    # print(len(http_xdr_list))
    

    insert_sql = "INSERT INTO HTTP_XDR (ip_type, vendor, sip, dip, sport, dport, msg_type, http_protocol, method, host, uri, referer, user_agent, proxy_authorization, authorization, cookies, location, x_forward_for, accept_encoding, date, traile, transfer_encoding, via, pragma, connection, cont_encoding, cont_location, cont_range, cont_length, cont_type, charset, transfer_length, req_range, http_request_body, http_reply_body) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    try:
        db_cursor.executemany(insert_sql, http_xdr_list)
        db_connection.commit()
        print("insert into HTTP_XDR ok")
    except Exception as e:
        print(e)
        db_connection.rollback()

    db_connection.close()
  
