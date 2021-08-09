import csv
import re
import pymysql
import re
import csv
import operator
import pymysql
from pyecharts import options as opts
from pyecharts.charts import Grid, Boxplot, Scatter
from pyecharts.commons.utils import JsCode
from pyecharts.render import make_snapshot
from snapshot_selenium import snapshot


device_info = re.compile(r'8BSX1EQGX|8A2X0KKKF|358123091482602|990012001490561|3C:28:6D:E9:EF:1F|android_id|androidid|AndroidID|2028.*1080|1080.*2080|2160.*1080|1080.*2060|manufacturer|idfa=|"idfa"|imsi=|"imsi"')
location_info = re.compile(r"bid.*cid.*nid.*sid|116\.23.*39\.95|39\.95.*116\.23|%E5%8C%97%E4%BA%AC")
network_info = re.compile(r"NETGEAR67|TP-LINK_3F66|WIN-N1USSIJ01UP.*2755|DESKTOP-LP51G8E.*2199|HONOR-10F78E|192\.168\.[0-9]+\.[0-9]+|52:e0:85:c0:2d:e4|b6:6d:83:11:fa:30")


def get_db_connection(database_name) -> pymysql.Connection:
    host = "10.10.103.147"
    port = 3306
    user = "root"
    password = "iiewlz666"
    db_connection = pymysql.connect(host=host, port=port, user=user, password=password, database=database_name)
    return db_connection


def get_http_message():
    db_connection = get_db_connection("APKDB")
    select_sql = "select packageName, URL, requestHeaders, requestBody from HTTP"
    # print(select_sql)
    db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
    db_cursor.execute(select_sql)
    http_message_dict = db_cursor.fetchall()
    db_connection.close()
    print("select done")
    return http_message_dict


def get_lib_app():
    lib_app = {}
    with open("appLibAnalyse.csv", "r", newline="", encoding="utf-8-sig") as f:
        csv_reader = csv.reader(f)
        message = list(csv_reader)
        for x in message:
            if x[1] == "set()":
                continue
            lib = x[1].replace("{", "").replace("'", "").replace("}", "").split(", ")
            if len(lib) not in lib_app:
                lib_app[len(lib)] = [x[0]]
            else:
                lib_app[len(lib)].append(x[0])
    # print(lib_app)
    return lib_app


def get_count(lib_app):
    count = {}
    for lib_len, app_list in lib_app.items():
        count[lib_len] = {}

    http_message_dict = get_http_message()

    for http_message in http_message_dict:
        for lib_len, app_list in lib_app.items():
            if http_message["packageName"] in app_list:
                if (len(device_info.findall(http_message["requestHeaders"], re.IGNORECASE)) > 0 or len(device_info.findall(http_message["requestBody"], re.IGNORECASE)) > 0 or len(device_info.findall(http_message["URL"], re.IGNORECASE)) > 0) \
                        or (len(location_info.findall(http_message["requestHeaders"], re.IGNORECASE)) > 0 or len(location_info.findall(http_message["requestBody"], re.IGNORECASE)) > 0 or len(location_info.findall(http_message["URL"], re.IGNORECASE)) > 0) \
                        or (len(network_info.findall(http_message["requestHeaders"], re.IGNORECASE)) > 0 or len(network_info.findall(http_message["requestBody"], re.IGNORECASE)) > 0 or len(network_info.findall(http_message["URL"], re.IGNORECASE)) > 0):
                    if http_message["packageName"] not in count[lib_len]:
                        count[lib_len][http_message["packageName"]] = 1
                    else:
                        count[lib_len][http_message["packageName"]] += 1
                break

    print(count)

    y_data = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    for lib_len, app_pii_count in count.items():
        for tmp in app_pii_count.values():
            y_data[lib_len-1].append(tmp)
    return y_data


if __name__ == '__main__':
    # lib_app = get_lib_app()
    # y_data = get_count(lib_app)
    # print(y_data)

    x_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
    y_data = [
        [2, 8, 46, 6, 1, 2, 3, 2, 36, 1, 46, 2, 7, 1, 7, 3, 1, 1, 4, 1, 38, 1, 9, 8, 5, 1, 44, 5, 1, 2, 1, 5, 3, 2, 8, 3, 2, 4, 7, 4, 1, 1, 27, 147, 179, 1, 1, 1, 4, 2, 1, 2, 2, 1, 27, 2, 57, 2, 4, 272, 7, 7, 614, 73, 86, 1, 40, 65, 186, 1, 54, 1, 1, 3, 1, 37, 1, 9, 1, 1, 216, 2, 1, 3, 3, 3, 6, 2, 5, 2, 6, 12, 5, 7, 3, 1, 1, 1, 2, 10, 1, 4, 1, 4, 143, 2, 14, 1, 9, 13, 1, 2, 1, 1, 2, 4, 1, 1, 2, 2, 1, 1, 3, 1, 2, 2, 1, 1, 25, 1, 2, 3, 120, 9, 2, 132, 195, 2, 13, 6, 1, 2, 23, 1, 2, 4, 8, 4, 3, 13, 6, 2, 2, 31, 1, 28, 1, 2, 4, 183, 14, 1, 1, 127, 1, 4, 3, 7, 8, 27, 4, 17, 2, 47, 1, 8, 1, 2, 1, 1, 1, 8, 4, 1, 3, 2, 2, 1, 1, 2, 4, 3, 1, 5, 1, 1, 1, 1, 2, 41, 2, 4, 3, 3, 2, 1, 1, 1, 2, 6, 2, 1, 4, 1, 1, 7, 2, 1, 3, 3, 1, 2, 3, 6, 1, 1, 9, 3, 2, 3, 1, 1, 1, 10, 4, 13, 15, 6, 1, 1, 3, 1, 38, 1, 2, 2, 3, 2, 5, 1, 1, 18, 45],
        [1, 53, 5, 8, 4, 26, 28, 7, 2, 2, 12, 4, 2, 2, 4, 118, 1, 18, 8, 1, 4, 2, 1, 7, 13, 73, 2, 1, 1, 2, 3, 1, 1, 2, 2, 3, 1, 3, 1, 13, 13, 2, 3, 10, 1, 19, 1, 5, 3, 19, 1, 6, 65, 27, 156, 11, 2, 1, 2, 46, 3, 106, 535, 1, 6, 1, 3, 1, 12, 20, 3, 3, 14, 2, 2, 2, 3, 1, 44, 4, 2, 4, 74, 1, 1, 1, 3, 6, 2, 19, 1, 9, 19, 6, 19, 6, 1, 2, 12, 2, 4, 4, 1, 47, 34, 4, 1, 2, 12, 34, 6, 1, 1, 3, 3, 1, 2, 1, 6, 4, 1, 7, 2, 1, 1, 2, 2, 13, 5, 2, 9, 2, 8, 7, 6, 1, 34, 124, 47, 1, 7, 1, 2, 76, 2, 1, 21, 4, 1, 2, 2, 1, 2, 1, 2, 1, 1, 29, 1, 1, 1, 2, 1, 6, 8, 2, 65, 2, 1, 9, 1, 3, 149, 20, 1, 49, 46, 1, 3, 1, 2, 18, 1, 4, 1, 1, 2, 4, 3, 1, 13, 1, 2, 2, 1, 24, 8, 4, 1, 7, 6, 1, 3, 2, 1, 1, 8, 18, 13, 2, 1, 19, 1, 2, 4, 2, 2, 4, 1, 1, 10, 1, 1, 1, 3, 3, 2, 1, 2, 35, 7, 6, 4, 6, 2, 27, 2, 1, 7, 11, 4, 7, 2, 3, 3, 2, 1, 2, 1, 38, 28, 4, 14, 5, 6, 17, 1, 7, 16, 5, 1, 1],
        [3, 3, 7, 2, 1, 2, 13, 44, 13, 31, 2, 2, 2, 2, 3, 2, 1, 5, 87, 13, 4, 49, 7, 1, 7, 1, 1, 1, 1, 1, 1, 2, 7, 15, 1, 10, 4, 2, 18, 1, 7, 1, 1, 1, 1, 5, 1, 4, 10, 1, 24, 14, 1, 3, 6, 4, 3, 1, 1, 3, 4, 6, 1, 645, 18, 9, 6, 9, 1, 3, 528, 53, 7, 6, 1, 17, 1, 1, 1, 1, 155, 47, 85, 27, 2, 7, 1, 14, 2, 2, 1, 2, 1, 11, 3, 3, 4, 1, 7, 166, 111, 16, 1, 1, 44, 13, 15, 4, 57, 3, 1, 1, 11, 82, 38, 1, 7, 13, 1, 4, 1, 83, 1, 1, 3, 60, 30, 7, 31, 10, 3, 1, 17, 7, 4, 7, 15, 5, 2, 2, 5, 10, 20, 8, 2, 203, 4, 8, 32, 7, 3, 13, 4, 4, 6, 4, 4, 28, 282, 7, 4, 6, 1, 27, 4, 2, 1, 16, 1, 4, 12, 2, 2, 5, 378, 379, 17, 383, 1, 1, 9, 33, 15, 42, 1, 17, 2, 1, 10, 1, 1, 1, 4, 1, 33, 54, 1, 12, 3, 2, 12, 4, 18, 38, 50, 178, 1, 3, 1, 1, 1, 8, 2, 1, 3, 18, 6, 5, 11, 69, 1, 8, 6, 2, 1, 345, 2, 8, 14, 53, 17, 1, 257, 1, 3, 87, 1, 3, 2, 2, 1, 9, 22, 1, 1, 3, 3, 2, 1, 6, 4, 4, 15, 8, 2, 6, 1, 1, 2, 2, 2, 1, 3, 22, 4, 2, 4, 38, 12, 4, 4, 2, 2],
        [20, 5, 1, 1, 2, 1, 5, 35, 1, 2, 1, 10, 10, 1, 15, 4, 1, 23, 2, 3, 9, 1, 1, 13, 3, 20, 1, 1, 25, 1, 14, 1, 16, 2, 1, 5, 10, 7, 1, 126, 4, 3, 5, 2, 1, 43, 11, 4, 2, 1, 1, 1, 1, 1, 38, 2, 135, 2, 58, 1, 1, 13, 1, 1, 2, 4, 90, 4, 4, 41, 2, 10, 7, 3, 5, 2, 9, 1, 1, 7, 3, 52, 366, 17, 119, 1, 5, 12, 2, 2, 178, 1, 1, 1, 9, 21, 1, 8, 1, 1, 7, 2, 1, 1, 1, 1, 2, 1, 2, 3, 1, 1, 44, 20, 10, 4, 10, 9, 1, 1, 119, 3, 1, 1, 11, 2, 3, 1, 5, 7, 2, 26, 103, 1, 1, 11, 3, 50, 7, 25, 4, 51, 2, 6, 8, 3, 1, 5, 4, 3, 24, 5, 10, 30, 81, 6, 2, 2, 5, 11, 3, 1, 1, 11, 18, 53, 1, 9, 8, 1, 3, 1, 7, 6, 6, 32, 17, 6, 136, 11, 11, 9, 1, 203, 1, 3, 1, 3, 10, 2, 145, 57, 37, 20, 2, 2, 7, 4, 2, 3, 2, 1, 1, 3, 1, 35, 2, 1, 2, 1, 2, 1, 8, 9, 1, 2, 15, 16, 1, 1, 21, 4, 5, 3, 9, 2, 6, 3, 36, 19, 158, 1, 11, 6, 7, 35],
        [20, 11, 100, 9, 82, 1, 9, 4, 47, 1, 4, 9, 1, 1, 40, 79, 2, 1, 2, 2, 1, 4, 1, 5, 15, 3, 1, 1, 1, 1, 7, 2, 18, 3, 1, 2, 51, 6, 3, 1, 134, 18, 2, 5, 7, 3, 1, 1, 12, 1, 91, 2, 5, 3, 5, 1, 139, 1, 20, 1, 17, 5, 17, 1, 1, 5, 7, 4, 1, 6, 2, 2, 1, 6, 105, 18, 3, 7, 2, 4, 4, 394, 6, 30, 3, 1, 41, 3, 1, 2, 1, 1, 15, 1, 1, 5, 32, 3, 8, 14, 9, 117, 133, 5, 4, 2, 2, 22, 43, 54, 3, 2, 3, 10, 1, 34, 23, 4, 4, 5, 3, 6, 3, 1, 1, 16, 15, 216, 47, 2, 28, 82, 121, 1, 2, 1, 45, 1, 2, 1, 334, 11, 5, 2, 3, 20, 6, 115, 4, 57, 2, 1, 6, 5, 2, 7, 10, 1, 3, 5, 13, 8, 158, 2, 2, 4, 1, 6, 1, 7, 1, 96, 19, 20, 2, 1, 4, 7, 8, 1, 6, 7],
        [18, 98, 180, 37, 1, 13, 4, 28, 16, 5, 2, 1, 38, 5, 7, 17, 1, 1, 417, 115, 1, 1, 18, 3, 1, 1, 2, 18, 1, 41, 4, 2, 5, 4, 22, 2, 1, 2, 3, 29, 1, 10, 6, 4, 5, 1, 74, 16, 2, 3, 2, 26, 2, 19, 9, 1, 5, 5, 8, 1, 1, 1, 1, 2, 2, 1, 80, 2, 1, 30, 10, 10, 28, 1, 1, 3, 5, 14, 8, 2, 40, 4, 1, 12, 1, 3, 75, 5, 1, 34, 2, 5, 3, 16, 1, 1, 6, 8, 2, 122, 10, 6, 2, 2, 5, 4, 21, 1, 2, 2, 3, 15, 3, 5, 5, 138, 3, 2, 5, 11, 6, 37, 12, 4, 1, 2, 1, 60, 6, 8, 17, 26, 5, 20, 1, 2, 47, 1, 13, 6, 41, 1, 4, 45, 1, 1, 56, 7, 9, 4, 12, 16, 6, 4, 27, 10, 3, 2, 3, 2, 3, 21, 89, 19, 1, 19],
        [42, 1, 6, 3, 11, 23, 40, 24, 3, 18, 1, 1, 20, 1, 13, 15, 81, 1, 1, 47, 1, 22, 29, 34, 33, 1, 8, 1, 29, 1, 1, 3, 12, 82, 48, 65, 2, 70, 1, 521, 2, 1, 4, 28, 126, 98, 49, 1, 14, 45, 1, 1, 143, 26, 3, 1, 125, 4, 15, 13, 51, 21, 2, 1, 10, 136, 8, 223, 7, 4, 78, 3, 2, 5, 16, 1, 207, 2, 233, 3, 2, 129, 3, 5, 1, 7, 7, 1, 6, 4, 12, 15, 8, 3, 2, 77, 6, 2, 170, 137, 10, 1, 5, 1, 1, 57, 122, 1, 1, 2, 29, 4, 1, 2, 11],
        [26, 4, 4, 115, 87, 2, 4, 2, 6, 2, 8, 1, 7, 22, 2, 1, 17, 11, 14, 3, 1, 14, 8, 15, 17, 5, 12, 5, 8, 19, 1, 2, 86, 6, 10, 41, 1, 16, 11, 337, 33, 3, 22, 49, 41, 6, 9, 65, 17, 1, 191, 6, 2, 6, 34, 1, 86, 12, 30, 1, 326, 4, 10, 2, 194, 1, 49, 4, 3, 1, 5, 10, 3, 6, 7, 17, 401, 1, 1, 93, 14, 2, 15, 1, 49, 231, 3, 50, 2, 3, 65, 3, 219, 2, 9, 4, 36, 11, 6, 4, 6],
        [9, 3, 22, 72, 3, 1, 13, 19, 3, 2, 1, 4, 17, 4, 6, 1, 14, 9, 61, 14, 23, 51, 13, 8, 7, 22, 2, 1, 4, 1, 98, 25, 21, 11, 2, 181, 16, 2, 10, 1, 5, 1, 1, 6, 12, 9, 1, 5, 75, 1, 1, 9, 5, 1, 124, 1, 1, 8, 18, 153, 1, 11, 2],
        [20, 16, 3, 10, 2, 2, 24, 30, 15, 37, 2, 1, 31, 1, 15, 105, 160, 6, 4, 33, 4, 17, 2, 8, 5, 1, 3, 18, 36, 10, 27, 1, 261, 2, 173, 4, 35, 25, 10, 4, 6, 14, 4, 10, 52, 2, 4, 12, 1, 6, 1, 110, 11],
        [8, 2, 5, 95, 1, 22, 33, 20, 3, 216, 15, 6, 2, 394, 4, 879, 19, 4, 217, 3, 9, 6, 18, 81, 162, 2, 37, 4, 1, 31, 12, 4, 20, 2, 5, 34, 4, 2, 3, 6],
        [214, 17, 8, 6, 2, 294, 13, 25, 4, 1, 160, 1, 7, 161, 15, 13, 5, 27, 6, 87],
        [84, 15, 29, 3, 1, 9, 6, 2, 4, 129, 2, 34],
        [39, 51, 1, 14, 280, 57, 4, 74, 169, 105, 1, 23, 11, 2, 2],
        [2, 73],
        [1, 6, 51, 156, 24, 15],
        [189],
        [],
        [31],
        [],
        [19]
    ]


    box_plot = Boxplot()
    box_plot = (
        box_plot.add_xaxis(x_data)
        .add_yaxis("", box_plot.prepare_data(y_data))
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(name="Library count"),
            yaxis_opts=opts.AxisOpts(name="PII Request count"),
        )
    )


    scatter_min = [None, None, None, None, None, None, None, None, None, None, None, None, None, 2, None, 189, None, 31, None, 19]
    scatter_max = [None, None, None, None, None, None, None, None, None, None, None, None, None, 73, None, None, None, None, None, None]
    
    scatter = (
        Scatter()
        .add_xaxis(x_data)
        .add_yaxis("", scatter_min)
        .add_yaxis("", scatter_max)
        .set_global_opts(
            yaxis_opts=opts.AxisOpts(
                max_=1000,
                axislabel_opts=opts.LabelOpts(is_show=False),
                axistick_opts=opts.AxisTickOpts(is_show=False),
            ),
        )
    )

    grid = (
        Grid()
        .add(
            box_plot,
            grid_opts=opts.GridOpts(pos_left="10%", pos_right="10%", pos_bottom="15%"),
        )
        .add(
            scatter,
            grid_opts=opts.GridOpts(pos_left="10%", pos_right="10%", pos_bottom="15%"),
        )
        # .render()
    )
    make_snapshot(snapshot, grid.render(), "111.png")
