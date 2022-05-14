import re
import os
import pathlib
import csv
import pymysql


def get_db_connection(database_name) -> pymysql.Connection:
    host = "*"
    port = 3306
    user = "*"
    password = "*"
    db_connection = pymysql.connect(host=host, port=port, user=user, password=password, database=database_name)
    return db_connection

def get_stack(style):
    select_sql = "select id, packageName, host, URL, requestHeaders, requestBody, responseHeaders, responseBody, stack from HTTP where requestBody like '%.{}'".format(style)
    db_connection = get_db_connection("APKDB")
    db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
    db_cursor.execute(select_sql)
    stack_dict = db_cursor.fetchall()
    db_connection.close()
    return stack_dict

def get_privacy_message(stack_post_file):
    stack_privacy_message = dict()
    analyse_path = "/home/chj/APKTestEngine/PcapExtract/in/"
    unzip_path = "/home/chj/APKTestEngine/PcapExtract/in/unzip/"
    path = pathlib.Path(unzip_path)
    if not path.exists():
        path.mkdir()
    os.chdir(analyse_path)
    for stack, post_files in stack_post_file.items():
        privacy_message = dict()
        for file in post_files:
            try:
                if file[-3:] == ".gz":
                    unzip_file_path = unzip_path + file[:-3]
                    unzip_command = "gzip -d -c -q {} > {}".format(file, unzip_file_path)
                    os.system(unzip_command)

                    if os.path.exists(unzip_file_path):
                        content = open(unzip_file_path, "r", encoding="utf-8").readlines()
                        privacy = re.compile(r"imei|8BSX1EQGX|8A2X0KKKF|358123091482602|990012001490561|oaid|phoneNumber")
                        if privacy.findall(str(content)) != None:
                            # print(privacy_message[file])
                            privacy_message[file] = privacy.findall(str(content))
                if file[-4:] == ".zip":
                    unzip_file_path = unzip_path + file[:-4] + "/"
                    # print(unzip_file_path)
                    path = pathlib.Path(unzip_file_path)
                    if not path.exists():
                        path.mkdir()
                    unzip_command = "unzip -q -o {} -d {}".format(file, unzip_file_path)
                    os.system(unzip_command)

                    if os.path.exists(unzip_file_path):
                        for x in os.listdir(unzip_file_path):
                            # print(unzip_file_path + x)
                            content = open(unzip_file_path + x, "r", encoding="utf-8").readlines()
                            privacy = re.compile(r"imei|8BSX1EQGX|8A2X0KKKF|358123091482602|990012001490561|oaid|phoneNumber")
                            if privacy.findall(str(content)) != None:
                                # print(privacy_message[file])
                                privacy_message[file] = privacy.findall(str(content))
                if file[-4:] == ".log":
                    if os.path.exists(file):
                        content = open(file, "r", encoding="utf-8").readlines()
                        privacy = re.compile(r"imei|8BSX1EQGX|8A2X0KKKF|358123091482602|990012001490561|oaid|phoneNumber")
                        if privacy.findall(str(content)) != None:
                            # print(privacy_message[file])
                            privacy_message[file] = privacy.findall(str(content))
                if file[-4:] == ".txt":
                    if os.path.exists(file):
                        content = open(file, "r", encoding="utf-8").readlines()
                        privacy = re.compile(r"imei|8BSX1EQGX|8A2X0KKKF|358123091482602|990012001490561|oaid|phoneNumber")
                        if privacy.findall(str(content)) != None:
                            # print(privacy_message[file])
                            privacy_message[file] = privacy.findall(str(content))
            except Exception as e:
                # print(e)
                pass

        if stack not in stack_privacy_message:
            stack_privacy_message[stack] = list()
        for file, privacy in privacy_message.items():
            if len(privacy) > 0:
                # stack_privacy_message[stack].append([file, set(privacy)])
                for i in privacy:
                    stack_privacy_message[stack].append(i)
        stack_privacy_message[stack] = set(stack_privacy_message[stack])
        # print(stack_privacy_message[stack])
    return stack_privacy_message

def get_stack_info(stack_dict):
    stack_request_info = list()
    stack_request_count = dict()
    stack_package = dict()
    stack_host = dict()
    stack_url = dict()
    stack_post_file = dict()
    for http_message in stack_dict:
        http_message["requestHeaders"] = str(http_message["requestHeaders"]).replace(",", " ").replace("\n", "")[:1000]
        http_message["requestBody"] = str(http_message["requestBody"]).replace(",", " ").replace("\n", "")[:1000]
        http_message["responseHeaders"] = str(http_message["responseHeaders"]).replace(",", " ").replace("\n", "")[:1000]
        http_message["responseBody"] = str(http_message["responseBody"]).replace(",", " ").replace("\n", "")[:1000]
        stack = http_message["stack"].split("|")
        for tmp in stack[::1]:
            if str(tmp).startswith("java") \
                    or str(tmp).startswith("at com.android.okhttp") \
                    or str(tmp).startswith("at org.apache.http") \
                    or str(tmp).startswith("at okio") \
                    or str(tmp).startswith("at okhttp3") \
                    or str(tmp).startswith("at com.android.org") \
                    or str(tmp).startswith("at android.os") \
                    or str(tmp).startswith("at java") \
                    or str(tmp).startswith("at com.android.volley") \
                    or "retrofit2" in str(tmp) \
                    or "reactivex" in str(tmp) \
                    or "intercept" in str(tmp) \
                    or "None" in str(tmp):
                del stack[stack.index(tmp)]
        new_stack = list()
        for tmp in stack:
            tmp = tmp.replace("at ", "").split("(")[0]
            if len(tmp.split(".")) > 0 and "$" in tmp.split(".")[0]:
                continue
            if len(tmp.split(".")) > 1 and "$" in tmp.split(".")[1]:
                continue
            if len(tmp.split(".")) > 2 and "$" in tmp.split(".")[2]:
                continue
            if len(tmp.split(".")) > 0 and len(tmp.split(".")[0]) == 1:
                continue
            if len(tmp.split(".")) > 1 and len(tmp.split(".")[1]) == 1:
                continue
            if len(tmp.split(".")) > 2 and len(tmp.split(".")[2]) == 1:
                continue
            if len(tmp.split(".")) > 3:
                tmp = ".".join(tmp.split(".")[:3])
            new_stack.append(tmp)
            # request count
            if tmp in stack_request_count:
                stack_request_count[tmp] += 1
            else:
                stack_request_count[tmp] = 1
            # package
            if tmp not in stack_package:
                stack_package[tmp] = list()
            stack_package[tmp].append(http_message["packageName"])
            # host
            if tmp not in stack_host:
                stack_host[tmp] = list()
            stack_host[tmp].append(http_message["host"])
            # url
            if tmp not in stack_url:
                stack_url[tmp] = list()
            stack_url[tmp].append(http_message["URL"])
            # post file
            if tmp not in stack_post_file:
                stack_post_file[tmp] = list()
            stack_post_file[tmp].append(http_message["requestBody"])
            
        if len(new_stack) > 0:
            new_stack = "|".join(set(new_stack))
        else:
            new_stack = ""
        stack_request_info.append([http_message["id"], http_message["host"], http_message["URL"], http_message["requestHeaders"], http_message["requestBody"], http_message["responseHeaders"], http_message["responseBody"], new_stack])

    stack_privacy_message = get_privacy_message(stack_post_file)
    stack_info_list = list()
    for stack, value in stack_request_count.items():
        stack_info_list.append([
            stack,
            value,
            set(stack_package[stack]),
            len(set(stack_package[stack])),
            set(stack_host[stack]),
            len(set(stack_host[stack])),
            " ".join(set(stack_url[stack]))[:1000],
            len(set(stack_url[stack])),
            set(stack_post_file[stack]),
            stack_privacy_message[stack],
        ])
    return stack_info_list, stack_request_info


if __name__ == '__main__':
    styles = [
        "gz",
        "zip",
        "log",
        "txt",
    ]
    for style in styles:
        stack_dict = get_stack(style)
        stack_info_list, stack_request_info = get_stack_info(stack_dict)

        result_file_name = "{}AnalyseResult.csv".format(style)
        print(result_file_name)
        with open(result_file_name, "w", newline="", encoding="utf-8-sig") as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow(["stack", "request count", "package", "package count", "host", "host count", "url", "url count", "post file name"])
            csv_writer.writerows(stack_info_list)
            csv_writer.writerows([[], []])
            csv_writer.writerow(["id", "packageName", "host", "URL", "requestHeaders", "requestBody", "responseHeaders", "responseBody", "stack"])
            csv_writer.writerows(stack_request_info)




