import logging.config
import logging.handlers
import configparser
import platform

import pymysql  # pip install pymysql

logging.config.fileConfig('AnalyseLog.conf')
logger = logging.getLogger('AnalyseLog')


def get_db_config() -> object:
    """

    :return: 数据库配置信息
    """
    config = configparser.ConfigParser()
    if platform.system().lower() == "windows":
        config.read("config.conf")
        db_config = config["database"]
        return db_config
    elif platform.system().lower() == "linux":
        config.read("/home/chj/APKTestEngine/Analyse/config.conf")
        db_config = config['database']
        return db_config


def get_db_connection() -> pymysql.Connection:
    """

    :return: 数据库连接
    """
    db_config = get_db_config()
    host = db_config['host']
    port = int(db_config['port'])
    user = db_config['user']
    password = db_config['password']
    database = db_config['database']
    db_connection = pymysql.connect(host=host, port=port, user=user, password=password, database=database)
    return db_connection


def get_all_pcapfiles_for_http2_analyse() -> list:
    """

    Returns: list of dict, each dict is a CaptureLog

    """
    logger.debug('start getting all pcapFiles Dict...')
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
    select_sql = "SELECT * FROM CaptureLog  where http2Analyse = 0 ORDER BY APKID ASC"
    db_cursor.execute(select_sql)
    pcap_file_list = db_cursor.fetchall()
    db_connection.close()
    return pcap_file_list

def writeHTTP2Flow(http2Message, db_connection):
    logger.debug('start writing HTTP2Flow...')
    db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
    try:
        insertSql = "INSERT INTO HTTP2Flow (APKName, HTTP2FlowNum, createTime, lastModifyTime) VALUES (%s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
        db_cursor.execute(insertSql, (http2Message['APKName'], http2Message['HTTP2FlowNum']))
        db_connection.commit()
        logger.debug("writeHTTP2Flow OK")
    except Exception as e:
        logger.error("Exception: %s" % e)
        db_connection.rollback()


def updatehttp2Analyse(logID, db_connection):
    logger.info('update http2Analyse, logID: %s', logID)
    db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
    updateSql = "UPDATE CaptureLog SET http2Analyse = 1 WHERE logID = %s"
    try:
        db_cursor.execute(updateSql, logID)
        db_connection.commit()
        logger.debug("http2Analyse OK, logID: %s" % logID)
    except Exception as e:
        logger.error("Exception: %s" % e)
        db_connection.rollback()
        logger.error('http2Analyse failed. logID: %s', logID)
