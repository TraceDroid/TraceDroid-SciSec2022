import logging.config
import logging.handlers


logging.config.fileConfig('AnalyseLog.conf')
logger = logging.getLogger('AnalyseLog')


if __name__ == '__main__':
    logger.info('\n==========Host Ranking==========')
    result = {}
    with open("hostToPackageALL.txt", "r", encoding="utf-8") as hpn:
        host_rank_dict = eval(hpn.read())
        print(type(host_rank_dict))
        print(len(host_rank_dict))
        result = sorted(host_rank_dict.items(), key=lambda item:item[1], reverse=True)
        print(result)
    with open("host_ranking", "w", encoding="utf-8") as hr:
        for item in result:
            hr.write(str(item[0]) + ":" + str(item[1]))
            hr.write("\r")

