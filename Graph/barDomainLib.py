import csv
import re
import pymysql
import re
import csv
import operator
import pymysql
from pyecharts import options as opts
from pyecharts.charts import Bar, Grid
from pyecharts.commons.utils import JsCode
from pyecharts.render import make_snapshot
from snapshot_selenium import snapshot


device_info = re.compile(r'8BSX1EQGX|8A2X0KKKF|358123091482602|990012001490561|3C:28:6D:E9:EF:1F|android_id|androidid|AndroidID|2028.*1080|1080.*2080|2160.*1080|1080.*2060|manufacturer|idfa=|"idfa"|imsi=|"imsi"')
location_info = re.compile(r"bid.*cid.*nid.*sid|116\.23.*39\.95|39\.95.*116\.23|%E5%8C%97%E4%BA%AC")
network_info = re.compile(r"NETGEAR67|TP-LINK_3F66|WIN-N1USSIJ01UP.*2755|DESKTOP-LP51G8E.*2199|HONOR-10F78E|192\.168\.[0-9]+\.[0-9]+|52:e0:85:c0:2d:e4|b6:6d:83:11:fa:30")


def get_db_connection(database_name) -> pymysql.Connection:
    host = "*"
    port = 3306
    user = "*"
    password = "*"
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
    host_list = [
        "api.vungle.com",
        "adashbc.ut.taobao.com",
        "req.startappservice.com",
        "api1.zongheng.com",
        "collectionpv.che168.com",
        "msg.qy.net",
        "api2.branch.io",
        "aa.tangdou.com",
        "click.btime.com",
        "r.inews.qq.com",
        "ads.mopub.com",
        "ad.cread.com",
        "report.meituan.com",
        "druidv6.if.qidian.com",
        "api.branch.io",
        "log1.cmpassport.com",
        "service.winbaoxian.com",
        "www.lingeye.com",
        "rl.go2yd.com",
        "mi.gdt.qq.com"
    ]

    device_info_ = [1497, 0, 732, 612, 0, 410, 292, 555, 0, 248, 500, 466, 178, 397, 196, 191, 377, 0, 0, 371]
    location_info_ = [0, 0, 0, 0, 0, 0, 0, 0, 88, 31, 0, 0, 116, 0, 0, 0, 0, 0, 0, 0]
    network_info_ = [0, 1030, 91, 0, 603, 190, 305, 0, 455, 241, 0, 0, 121, 0, 196, 190, 0, 374, 373, 0]

    library_list = [
        "com.vungle.publisher",
        "com.startapp.android",
        "com.umeng.common",
        "com.qq.e",
        "org.qiyi.net",
        "com.bytedance.sdk",
        "com.networkbench.agent",
        "com.tencent.renews",
        "com.hoge.android",
        "com.umeng.umzid",
        "com.alibaba.mtl",
        "cz.msebera.android",
        "com.google.firebase",
        "com.mopub.volley",
        "com.tuan800.zhe800",
        "cn.com.modernmedia",
        "com.cmic.sso",
        "com.meituan.metrics",
        "com.zol.android",
        "com.newshunt.app",
    ]

    # device_info_ = [1482, 882, 523, 588, 486, 407, 381, 261, 0, 272, 69, 456, 290, 335, 358, 345, 156, 101, 228, 201]
    # location_info_ = [0, 0, 79, 2, 22, 9, 2, 41, 516, 219, 3, 0, 0, 0, 2, 6, 5, 90, 0, 0]
    # network_info_ = [0, 70, 140, 90, 151, 162, 169, 235, 13, 18, 410, 0, 147, 77, 12, 0, 146, 85, 0, 0]

    # print(len(library_list))
    # print(len(device_info_))
    # print(len(location_info_))
    # print(len(network_info_))

    # db_connection = get_db_connection("APKDB")

    # for host in host_list:
    #     http_message_dict = get_http_message(db_connection, host)
    #     result = {
    #         "device": 0,
    #         "location": 0,
    #         "network": 0,
    #     }

    #     for http_message in http_message_dict:
    #         if len(device_info.findall(http_message["requestHeaders"], re.IGNORECASE)) > 0 or len(device_info.findall(http_message["requestBody"], re.IGNORECASE)) > 0 or len(device_info.findall(http_message["URL"], re.IGNORECASE)) > 0:
    #             result["device"] += 1
            
    #         if len(location_info.findall(http_message["requestHeaders"], re.IGNORECASE)) > 0 or len(location_info.findall(http_message["requestBody"], re.IGNORECASE)) > 0 or len(location_info.findall(http_message["URL"], re.IGNORECASE)) > 0:
    #             result["location"] += 1

    #         if len(network_info.findall(http_message["requestHeaders"], re.IGNORECASE)) > 0 or len(network_info.findall(http_message["requestBody"], re.IGNORECASE)) > 0 or len(network_info.findall(http_message["URL"], re.IGNORECASE)) > 0:
    #             result["network"] += 1

    #     device_info_.append(result["device"])
    #     location_info_.append(result["location"])
    #     network_info_.append(result["network"])
    #     print(device_info_)
    #     print(location_info_)
    #     print(network_info_)

    # db_connection.close()

    
    grid = Grid(init_opts=opts.InitOpts(width="600px", height="500px"))
    bar = (
        Bar()
        .add_xaxis(host_list[::-1])
        # .add_xaxis(library_list[::-1])
        .add_yaxis("device info", device_info_[::-1], stack="stack1")
        .add_yaxis("location info", location_info_[::-1], stack="stack1")
        .add_yaxis("network info", network_info_[::-1], stack="stack1")
        
        .set_series_opts(
            label_opts=opts.LabelOpts(
                position="inside",
                font_size=8,
                formatter=JsCode(
                r"function (params) {if (params.value > 0) {return params.value;} else {return '';}}"
                ),
            )
        )
        .reversal_axis()
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(name="count", axislabel_opts=opts.LabelOpts(font_size=8)), # , axislabel_opts=opts.LabelOpts(rotate=-30, font_size=8)
            yaxis_opts=opts.AxisOpts(name="domain", axislabel_opts=opts.LabelOpts(font_size=8)),
            # yaxis_opts=opts.AxisOpts(name="library", axislabel_opts=opts.LabelOpts(font_size=8)),
            title_opts=opts.TitleOpts(title="", subtitle=""),
        )
    )
    grid.add(bar, grid_opts=opts.GridOpts(pos_left="22%", pos_bottom="5%"))
    # grid.render("bar_rotate_xaxis_label.html")
    make_snapshot(snapshot, grid.render(), "libHostStatistics.png")

