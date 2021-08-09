import pandas
from pyecharts import options as opts
from pyecharts.charts import Sankey
from pyecharts.render import make_snapshot
from snapshot_selenium import snapshot

# 数据
data = dict()

with open("./libToHostMappingResult.txt", encoding="utf-8") as f:
    raw_data_list = f.read().split("\n\n\n\n\n")

for lib_host_value in raw_data_list:
    lib, host_value_list = lib_host_value.split("\n\n")
    if len(lib.split(".")) > 3:
        lib = ".".join(lib.split(".")[:3])
    if lib not in data:
        data[lib] = dict()
        # print(lib)
    for host_value in host_value_list.split("\n"):
        host, value = host_value.split(":")
        value = int(value)
        if len(host.split(".")) > 2:
            host = ".".join(host.split(".")[-2:])
            if host == "co.jp" or host == "com.cn" or (ord(host[-1]) >= 48 and ord(host[-1]) <= 57):
                continue
            # print(host)
        if host in data[lib]:
            data[lib][host] += value
        else:
            data[lib][host] = value

data_final = list()
special_lib = [
    "com.amazon.weblab",
    "com.flurry.sdk",
    "com.adobe.mobile",
    "com.appsflyer.AppsFlyerLibCore",
    "com.amazonaws.http",
    "com.vungle.publisher",
    "com.tapjoy.internal",
    "com.meizu.cloud",
    "com.qihoo.cloudisk",
    "com.qihoo.antispam",
    "com.qihoo.sdk",
    "com.fyber.fairbid",
    "com.ironsource.mediationsdk",
    "com.adcolony.sdk",
    "com.talkingdata.sdk",
    "com.tapjoy.TapjoyURLConnection",
    "com.kwad.sdk",
]
del_lib = [
    "com.tencent.android",
    "com.tencent.odk",
    "com.baidu.pass"
]

for lib in data.keys():
    if lib in del_lib:
        continue
    for host, value in data[lib].items():
        if lib in special_lib:
            if value >= 50:
                data_final.append([lib, host, value])
        else:
            if value >= 200:
                data_final.append([lib, host, value])

# print(len(data_final))

data_frame = pandas.DataFrame(data_final, columns=['source', 'target', 'value'])

# 生成节点，先合并源节点和目标节点，然后去除重复的节点，最后输出成dict形式
nn = pandas.concat([data_frame['source'], data_frame['target']])
nn = nn.drop_duplicates()
nodes = pandas.DataFrame(nn, columns=['name']).to_dict(orient='records')

# 生成连接，dict形式
links = data_frame.to_dict(orient='records')

sk =(
    # Sankey(init_opts=opts.InitOpts(width="1500px", height="2000px")) # 页面大小
    Sankey(init_opts=opts.InitOpts(width="1400px", height="2200px"))
    .add(
        series_name="",
        nodes=nodes,
        links=links,
        linestyle_opt=opts.LineStyleOpts(opacity=0.2, curve=0.5, color="source"), 
        label_opts=opts.LabelOpts(font_size=14, position='right'),
        # node_align="left",
        # pos_left="30%",
        pos_right="30%",
        node_gap=4,
        layout_iterations=180,
    )
    .set_global_opts(title_opts=opts.TitleOpts(title=""))
    # .render("sankey.html")
)

make_snapshot(snapshot, sk.render(), "libToHostMappingResult.png")