import csv
import re
import pymysql
import re
import csv
import operator
import pymysql
from pyecharts import options as opts
from pyecharts.charts import HeatMap, Grid
from pyecharts.commons.utils import JsCode
from pyecharts.render import make_snapshot
from snapshot_selenium import snapshot


app_cate_list = [
    'ART_AND_DESIGN', 'AUTO_AND_VEHICLES', 'BEAUTY', 'BOOKS_AND_REFERENCE', 'BUSINESS',
    'COMICS', 'COMMUNICATION', 'DATING', 'EDUCATION', 'ENTERTAINMENT', 'EVENTS', 'FINANCE',
    'FOOD_AND_DRINK', 'GAME', 'GAMES', 'HEALTH_AND_FITNESS', 'HOUSE_AND_HOME', 'LIBRARIES_AND_DEMO', 'LIFESTYLE',
    'MAPS_AND_NAVIGATION', 'MEDICAL', 'MUSIC_AND_AUDIO', 'NEWS_AND_MAGAZINES', 'PARENTING',
    'PERSONALIZATION', 'PHOTOGRAPHY', 'PRODUCTIVITY', 'SHOPPING', 'SOCIAL', 'SPORTS', 'TOOLS',
    'TRANSPORTATION', 'TRAVEL_AND_LOCAL', 'VIDEO_PLAYERS', 'WEATHER'
]
host_cate_list = [
    'web infrastructure', 'personals and dating', 'peer-to-peer file sharing', 'internet radio and tv',
    'marketing', 'collaboration - office', 'blogs and personal sites', 'personal network storage and backup',
    'media file download', 'reference materials', 'Malware Sites', 'entertainment', 'real estate', 'onlineshop',
    'social web - facebook', 'instant messaging', 'vehicles', 'general email', 'portals', 'education', 'travel',
    'educational institutions', 'malicious web sites. mobile malware', 'entertainment video', 'advertisements',
    'financial data and services', 'streaming media', 'content delivery', 'pay-to-surf', 'parked domain',
    'parked', 'message boards and forums', 'hobbies', 'search engines and portals', 'private ip addresses',
    'searchengines', 'financial services', 'Business and Economy', 'web and email marketing', 'internet auctions',
    'suspicious content', 'games', 'educational materials', 'sex', 'news and media', 'information technology',
    'content delivery networks', 'illegal or questionable', 'uncategorized', 'general business', 'government',
    'web analytics', 'sports', 'web images', 'restaurants and dining', 'job search', 'business',
    'social networking', 'computersandsoftware', 'Entertainment and Arts', 'malicious web sites. mobile malware. business and economy',
    'elevated exposure', 'adult content', 'hosted business applications', 'media sharing', 'shopping', 'health',
    'application and software download', 'Games', 'society and lifestyles', 'business and economy', 'unknown'
]

app_cate_list = ['ART_AND_DESIGN', 'AUTO_AND_VEHICLES', 'BEAUTY', 'BOOKS_AND_REFERENCE', 'BUSINESS', 'COMICS', 'COMMUNICATION', 'DATING', 'EDUCATION', 'ENTERTAINMENT', 'EVENTS', 'FINANCE', 'FOOD_AND_DRINK', 'GAME', 'GAMES', 'HEALTH_AND_FITNESS', 'LIFESTYLE', 'MUSIC_AND_AUDIO', 'NEWS_AND_MAGAZINES', 'PERSONALIZATION', 'PHOTOGRAPHY', 'PRODUCTIVITY', 'SHOPPING', 'SOCIAL', 'SPORTS', 'TOOLS', 'TRAVEL_AND_LOCAL', 'VIDEO_PLAYERS', 'WEATHER']
host_cate_list = ['personal network storage and backup', 'reference materials', 'entertainment', 'advertisements', 'financial data and services', 'streaming media', 'search engines and portals', 'internet auctions', 'games', 'news and media', 'information technology', 'uncategorized', 'web analytics', 'adult content', 'media sharing', 'shopping', 'application and software download', 'society and lifestyles', 'business and economy']

device_info = re.compile(r'8BSX1EQGX|8A2X0KKKF|358123091482602|990012001490561|3C:28:6D:E9:EF:1|android_id|androidid|AndroidID|2028.*1080|1080.*2080|2160.*1080|1080.*2060|manufacturer|idfa=|"idfa"|imsi=|"imsi"')
location_info = re.compile(r"bid.*cid.*nid.*sid|116\.23.*39\.95|39\.95.*116\.23|%E5%8C%97%E4%BA%AC")
network_info = re.compile(r"NETGEAR67|TP-LINK_3F66|WIN-N1USSIJ01UP.*2755|DESKTOP-LP51G8E.*2199|HONOR-10F78E|192\.168\.[0-9]+\.[0-9]+|52:e0:85:c0:2d:e4|b6:6d:83:11:fa:30")

print(len(app_cate_list))
print(len(host_cate_list))

def get_db_connection(database_name) -> pymysql.Connection:
    host = "cdb-faqfehvo.bj.tencentcdb.com"
    port = 10172
    user = "*"
    password = "chj901002"
    db_connection = pymysql.connect(host=host, port=port, user=user, password=password, database=database_name)
    return db_connection


def get_db_connection2(database_name) -> pymysql.Connection:
    host = "*"
    port = 3306
    user = "*"
    password = "*"
    db_connection = pymysql.connect(host=host, port=port, user=user, password=password, database=database_name)
    return db_connection


def get_app_cate():
    app_cate_dict = dict() # app: cate
    db_connection = get_db_connection("APKDB")
    select_sql = "select packageName, category from APKMetadata where category!=''"
    db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
    db_cursor.execute(select_sql)
    http_message_dict = db_cursor.fetchall()
    db_connection.close()

    db_connection = get_db_connection("APKDB2")
    select_sql = "select packageName, category from APKMetadata where category!=''"
    db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
    db_cursor.execute(select_sql)
    http_message_dict += db_cursor.fetchall()
    db_connection.close()
    print("app cate select done")

    for http_message in http_message_dict:
        app_cate_dict[http_message["packageName"]] = http_message["category"]
    
    print(len(app_cate_dict))
    return app_cate_dict


def get_host_cate():
    # cate_set = set()
    host_cate_dict = dict() # host: cate
    with open("libcate.csv", "r", newline="", encoding="utf-8-sig") as f:
        csv_reader = csv.reader(f)
        message = list(csv_reader)
        for host_cate in message:
            host = host_cate[0]
            for cate in host_cate[1:]:
                if len(cate) > 0:
                    host_cate_dict[host] = cate
                    # cate_set.add(cate)
                    break
    # print(cate_set)
    print(len(host_cate_dict))
    print("host cate select done")
    return host_cate_dict


def get_http_message():
    db_connection = get_db_connection2("APKDB")
    select_sql = "select packageName, host, requestHeaders, requestBody, URL from HTTP"
    db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
    db_cursor.execute(select_sql)
    http_message_dict = db_cursor.fetchall()
    db_connection.close()
    print("http message select done")
    return http_message_dict


def get_data():
    app_cate_dict = get_app_cate()
    host_cate_dict = get_host_cate()
    http_message_dict = get_http_message()
    data = {}
    for x in app_cate_list:
        data[x] = {}
        for y in host_cate_list:
            data[x][y] = set()

    for http_message in http_message_dict:
        if http_message["packageName"] not in app_cate_dict or http_message["host"] not in host_cate_dict:
            continue
        else:
            app_cate = app_cate_dict[http_message["packageName"]]
            host_cate = host_cate_dict[http_message["host"]]
            if app_cate not in app_cate_list or host_cate not in host_cate_list:
                continue
            # if (len(device_info.findall(http_message["requestHeaders"], re.IGNORECASE)) > 0 or len(device_info.findall(http_message["requestBody"], re.IGNORECASE)) > 0 or len(device_info.findall(http_message["URL"], re.IGNORECASE)) > 0) \
            #         or (len(location_info.findall(http_message["requestHeaders"], re.IGNORECASE)) > 0 or len(location_info.findall(http_message["requestBody"], re.IGNORECASE)) > 0 or len(location_info.findall(http_message["URL"], re.IGNORECASE)) > 0) \
            #         or (len(network_info.findall(http_message["requestHeaders"], re.IGNORECASE)) > 0 or len(network_info.findall(http_message["requestBody"], re.IGNORECASE)) > 0 or len(network_info.findall(http_message["URL"], re.IGNORECASE)) > 0):
            data[app_cate][host_cate].add(http_message["host"])
            # print(data) 

    z_data = []
    for x in data.keys():
        tmp = []
        for y, z in data[x].items():
            tmp.append(len(z))
        z_data.append(tmp)
    print(z_data)
    
    result = [
        [x, y, z]
        for x in range(len(app_cate_list))
        for y in range(len(host_cate_list))
        for z in z_data
    ]

    # print(result)
    return result


def create_heatmap():
    # value = get_data()
    value = [[1, 0, 0, 2, 0, 0, 0, 0, 0, 0, 6, 0, 0, 1, 0, 0, 0, 0, 2, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 2, 0, 0, 0, 0, 0, 2, 0], [1, 0, 0, 5, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 1, 0], [0, 0, 0, 8, 0, 0, 1, 0, 0, 0, 5, 0, 3, 1, 0, 1, 0, 0, 0, 0], [1, 2, 2, 6, 0, 0, 7, 2, 0, 1, 12, 0, 9, 1, 3, 0, 0, 0, 3, 2], [0, 0, 0, 7, 0, 0, 1, 0, 0, 0, 8, 0, 3, 0, 0, 0, 0, 0, 0, 0], [1, 3, 5, 1, 6, 2, 21, 2, 1, 2, 22, 2, 9, 1, 1, 6, 0, 3, 13, 2], [0, 0, 0, 6, 0, 0, 0, 0, 1, 0, 9, 0, 1, 0, 0, 0, 0, 0, 1, 0], [1, 6, 3, 6, 3, 3, 17, 2, 0, 1, 28, 1, 12, 1, 0, 2, 1, 0, 12, 2], [0, 0, 0, 13, 0, 1, 0, 0, 0, 0, 17, 0, 5, 1, 0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 1, 0, 0, 0, 0, 0, 0, 0], [0, 3, 2, 0, 8, 0, 6, 2, 0, 0, 10, 0, 4, 0, 0, 3, 0, 0, 5, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 8, 0, 7, 0, 0, 0, 0, 0, 1, 0], [0, 2, 2, 1, 1, 0, 8, 2, 1, 0, 6, 0, 3, 1, 3, 2, 0, 1, 5, 1], [0, 0, 0, 12, 0, 0, 0, 0, 3, 0, 16, 0, 3, 1, 0, 0, 0, 0, 3, 0], [1, 1, 0, 6, 0, 0, 0, 0, 0, 0, 7, 0, 5, 0, 0, 0, 0, 0, 2, 0], [0, 10, 4, 12, 3, 2, 12, 5, 1, 3, 36, 0, 10, 1, 2, 13, 5, 3, 31, 2], [4, 2, 18, 4, 1, 34, 26, 2, 4, 0, 24, 1, 10, 1, 3, 16, 1, 0, 22, 1], [3, 5, 44, 7, 11, 10, 63, 4, 3, 24, 77, 8, 9, 1, 7, 7, 4, 4, 58, 5], [0, 0, 0, 5, 0, 0, 2, 1, 0, 0, 6, 0, 3, 0, 0, 0, 0, 0, 1, 0], [4, 3, 3, 5, 2, 0, 16, 2, 0, 0, 24, 0, 7, 1, 1, 4, 1, 2, 15, 0], [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 4, 0, 3, 1, 0, 0, 0, 0, 2, 0], [1, 6, 2, 7, 3, 1, 13, 5, 0, 0, 18, 1, 8, 1, 0, 32, 0, 2, 13, 2], [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 6, 0, 0, 0, 0, 0, 0, 0, 1, 0], [0, 4, 1, 0, 2, 0, 12, 2, 0, 0, 7, 1, 5, 1, 0, 1, 0, 8, 4, 1], [4, 8, 13, 31, 7, 10, 37, 5, 9, 3, 102, 12, 13, 1, 27, 9, 7, 5, 64, 3], [0, 9, 2, 1, 2, 0, 15, 2, 0, 1, 19, 1, 8, 1, 0, 2, 0, 0, 20, 1], [0, 0, 0, 4, 0, 0, 0, 1, 0, 0, 4, 0, 3, 0, 0, 0, 1, 0, 1, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 2, 0, 0, 0, 0, 0, 0, 0]]
    result = [
        [x, y, value[x][y] or '-']
        for x in range(len(app_cate_list))
        for y in range(len(host_cate_list))
    ]
    print(result)
    grid = Grid(init_opts=opts.InitOpts(width="1000px"))
    heatmap = (
        HeatMap()
        .add_xaxis(app_cate_list)
        .add_yaxis(
            "",
            host_cate_list,
            result,
            label_opts=opts.LabelOpts(
                font_size=8,
                is_show=True,
                position="inside",
            ),
        )
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(
                type_="category",
                splitarea_opts=opts.SplitAreaOpts(
                    is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
                ),
                name="APP category",
                axislabel_opts=opts.LabelOpts(
                    font_size=6,
                    rotate=-30,
                    interval=0,
                    font_style="normal",
                )
            ),
            yaxis_opts=opts.AxisOpts(
                type_="category",
                splitarea_opts=opts.SplitAreaOpts(
                    is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
                ),
                name="host category",
                axislabel_opts=opts.LabelOpts(
                    font_size=8,
                    font_style="normal",
                )
            ),
            title_opts=opts.TitleOpts(title="", subtitle=""),
            visualmap_opts=opts.VisualMapOpts(
                pos_left="2%",
                pos_bottom="10%",
            ),
        )
        # .render()
    )
    grid.add(heatmap, grid_opts=opts.GridOpts(pos_left="22%", pos_bottom="20%"))
    # grid.render()
    make_snapshot(snapshot, grid.render(), "444.png")


if __name__ == '__main__':
    # get_data()
    create_heatmap()