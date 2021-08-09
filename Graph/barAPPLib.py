import csv
import re
import pymysql
import re
import csv
import operator
import pymysql
from pyecharts import options as opts
from pyecharts.charts import Bar, Grid, Line
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


def get_http_message(db_connection, host):
    select_sql = "select id, packageName, srcAddr, srcPort, dstAddr, dstPort, host, URL, requestHeaders, requestBody, protocol, method, stack from HTTP where host='{}'".format(host)
    # print(select_sql)
    db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
    db_cursor.execute(select_sql)
    http_message_dict = db_cursor.fetchall()
    return http_message_dict


if __name__ == '__main__':

    lib_app = {}

    with open("appLibAnalyse.csv", "r", newline="", encoding="utf-8-sig") as f:
        csv_reader = csv.reader(f)
        message = list(csv_reader)
        for x in message:
            if x[1] == "set()":
                # print(x[1])
                continue
            lib = x[1].replace("{", "").replace("'", "").replace("}", "").split(", ")
            if len(lib) in lib_app:
                lib_app[len(lib)] += 1
            else:
                lib_app[len(lib)] = 1

    unsorted = []
    for lib_count, app_count in lib_app.items():
        unsorted.append({"lib_count": lib_count, "app_count": app_count})
    sorted_lib_app = sorted(unsorted, key=operator.itemgetter("lib_count"))

    x_data = []
    y_data = []
    for tmp in sorted_lib_app[:10]:
        x_data.append(tmp["lib_count"])
        y_data.append(tmp["app_count"])
    
    
    sum_ = 0
    for tmp in sorted_lib_app[10:]:
       sum_ += tmp["app_count"]

    x_data.append(">10")
    y_data.append(sum_)


    # grid = Grid(init_opts=opts.InitOpts(width="600px", height="500px"))
    bar = (
        Bar(init_opts=opts.InitOpts(width="600px", height="500px"))
        .add_xaxis(x_data)
        .add_yaxis("", y_data)

        
        # .set_series_opts(
        #     label_opts=opts.LabelOpts(
        #         position="inside",
        #         font_size=8,
        #         formatter=JsCode(
        #         r"function (params) {if (params.value > 0) {return params.value;} else {return '';}}"
        #         ),
        #     )
        # )
        # .reversal_axis()
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(name="Library", axislabel_opts=opts.LabelOpts(font_size=8)), # , axislabel_opts=opts.LabelOpts(rotate=-30, font_size=8)
            yaxis_opts=opts.AxisOpts(name="APP", axislabel_opts=opts.LabelOpts(font_size=8)),
            # yaxis_opts=opts.AxisOpts(name="library", axislabel_opts=opts.LabelOpts(font_size=8)),
            title_opts=opts.TitleOpts(title="", subtitle=""),
        )
        .render()
    )
    # grid.add(bar, grid_opts=opts.GridOpts(pos_left="22%", pos_bottom="5%"))
    # grid.render("bar_rotate_xaxis_label.html")
    # make_snapshot(snapshot, bar.render(), "111.png")


