import logging.config
import logging.handlers
import configparser
import platform

import pymysql  # pip install pymysql

logging.config.fileConfig('ExtractLog.conf')
logger = logging.getLogger('PcapExtractEngine')

config = configparser.ConfigParser()
config.read('./config.conf')
deviceConfig = config['device']
fileConfig = config["filePath"]


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
        config.read("/home/chj/APKTestEngine/PcapExtract/config.conf")
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


def get_unextracted_pcaps():
    logger.debug('start getting unextracted pcapFile Dict...')
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
    select_sql = "SELECT * FROM CaptureLog WHERE needExtract = 1 ORDER BY createTime ASC"
    db_cursor.execute(select_sql)
    pcap_file_dict = db_cursor.fetchall()
    #logger.debug('pcapFileDict size is: %d', len(pcap_file_dict))
    #logger.debug(pcap_file_dict)
    # for APK in APKDict:
    #    print(APK["APKName"])
    db_connection.close()

    return pcap_file_dict

def writeHTTPMetaData(httpMessageListFinal, db_connection):
    logger.debug('start writeing HTTP metadata...')
    db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)

    try:
        insertSql = "INSERT INTO HTTP (packageName, srcAddr, srcPort, dstAddr, dstPort, host, URL, requestHeaders, requestBody, responseHeaders, responseBody, protocol, method, contentType) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        db_cursor.executemany(insertSql, httpMessageListFinal)
        # db_cursor.execute(insertSql, (httpMessage['packageName'], httpMessage['srcAddr'], httpMessage['srcPort'], httpMessage['dstAddr'], httpMessage['dstPort'], httpMessage['host'], httpMessage['URL'], httpMessage['requestHeaders'], httpMessage['requestBody'], httpMessage['responseHeaders'], httpMessage['responseBody'], httpMessage['protocol'], httpMessage['method'], httpMessage['contentType']))
        db_connection.commit()
        logger.debug("writeHTTPMetaData OK")
    except Exception as e:
        logger.error(e)
        db_connection.rollback()



# set CaptureLog "needExtract" 0, "extractTime" CURRENT_TIMESTAMP
def updateCaptureLogFlag(logID):

    logger.info('update extract flag, logID: %s', logID)
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
    updateSql = "UPDATE CaptureLog SET needExtract = 0, extractTime = CURRENT_TIMESTAMP WHERE logID = %s"
    try:
        db_cursor.execute(updateSql, logID)
        db_connection.commit()
        logger.debug("updateCaptureLogFlag OK, logID: %s" % logID)
    except Exception as e:
        logger.error("Exception: %s" % e)
        db_connection.rollback()
        logger.error('updateCaptureLogFlag failed. logID: %s', logID)
    db_connection.close()