# -*- coding: utf-8 -*-
# @Time : 2021/5/27 17:14 
# @Author : *
# @File : HTTP2Analyse.py 
# @Software: PyCharm

import logging.config
import logging.handlers

import pathlib
import pcapkit

import DBUtils

logging.getLogger('chardet.charsetprober').setLevel(logging.INFO)
logging.getLogger('chardet.universaldetector').setLevel(logging.INFO)

logging.config.fileConfig('AnalyseLog.conf')
logger = logging.getLogger('AnalyseLog')

def http2Analyse(captureLog, db_connection):
    logger.debug("http2 analyse %s" % captureLog['pcapFilePath'])
    pcapFilePath = captureLog['pcapFilePath']

    path = pathlib.Path(pcapFilePath)
    if not path.exists():
        logger.warning("file not exists: %s" % pcapFilePath)
        return -1

    # http2计数
    http2Count = 0
    
    # 开启tcp流追踪
    trace = pcapkit.extract(fin=pcapFilePath, nofile=True, trace=True)

    # 遍历每一条tcp流
    for tcpFlow in trace.trace:
        tcpFlowIndex = list(tcpFlow.index)  # tcp流所有frame的编号
        # print(tcpFlowIndex)  # 控制台输出
        if len(tcpFlowIndex) > 0:
            frame = trace.frame[tcpFlowIndex[0]-1]  # frame编号-1是真实的frame
            try:
                if b'HTTP/2.0\r\n\r\n' in frame.info.packet and pcapkit.HTTP not in frame:
                    http2Count += 1
            except Exception:
                pass

    http2Message = {
        'APKName': captureLog['APKName'],
        # 'packageName': '',
        'HTTP2FlowNum': http2Count,
    }
    
    DBUtils.writeHTTP2Flow(http2Message, db_connection)
    

if __name__ == '__main__':
    logger.debug("starting HTTP2 analyse...")
    pcap_list = DBUtils.get_all_pcapfiles_for_http2_analyse()
    db_connection = DBUtils.get_db_connection()
    logger.debug("pcap_list size: {}".format(pcap_list.__len__()))
    # search HTTP2 flows and write it into HTTP2Flow table
    for pcap in pcap_list:
        try:
            http2Analyse(pcap, db_connection)
            DBUtils.updatehttp2Analyse(pcap["logID"], db_connection)
        except Exception as e:
            logger.error("extract error! logID %s" % pcap["logID"])
            logger.error(e)
            continue
    db_connection.close()
