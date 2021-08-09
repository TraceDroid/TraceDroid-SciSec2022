import logging

global false, null, true
false = null = true = ''

from DBUtils import get_db_connection
import pymysql
import requests

logging.getLogger('chardet.charsetprober').setLevel(logging.INFO)
logging.getLogger('chardet.universaldetector').setLevel(logging.INFO)

logging.config.fileConfig('ExtractLog.conf')
logger = logging.getLogger('PcapExtractEngine')


def get_http_metadata():
    logger.debug('start getting HTTP metadata...')
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
    select_sql = "SELECT * FROM HTTP WHERE method='POST' ORDER BY id"
    db_cursor.execute(select_sql)
    http_message_dict = db_cursor.fetchall()
    logger.debug('http_message_dict size is: %d', http_message_dict.__len__())
    # logger.debug(http_message_dict)
    db_connection.close()
    return http_message_dict


def requests_replay(http_message_dict):
    url_list = list()
    requests_replay_count = 0
    requests_replay_url_list = list()
    for http_message in http_message_dict:
        URL = http_message['URL']
        if URL in url_list:
            continue
        else:
            url_list.append(URL)
        # print(URL)

        try:
            requestHeaders = eval(http_message['requestHeaders'])
        except Exception:
            requestHeaders = dict()
        # print(requestHeaders)

        try:
            requestBody = eval(http_message['requestBody'])
        except SyntaxError:
            requestBody = dict(list(body.split('=') for body in http_message['requestBody'].split('&') if len(body.split('=')) == 2))
        except Exception:
            requestBody = dict()
        # print(requestBody)
        
        try:
            response = requests.post(url=URL, headers=requestHeaders, json=requestBody, timeout=10)
        except Exception:
            continue
        

        if response.status_code != 200:
            continue
        else:
            if response.headers.get('Content-Type') is not None and 'json' in response.headers['Content-Type']:
                try:
                    responseBody = eval(http_message['responseBody'])
                    responseReplay = eval(response.text)
                except Exception:
                    continue
                # print(responseBody)
                # print(responseReplay)
                try:
                    if set(responseBody.keys()) == set(responseReplay.keys()):
                        requests_replay_count += 1
                        requests_replay_url_list.append(URL)
                        logger.debug("id:{}, url:{}, requestBody {}, response:{}".format(http_message['id'], URL, http_message['requestBody'], response.text))
                except Exception:
                    if http_message['responseBody'] in response.text:
                        requests_replay_count += 1
                        requests_replay_url_list.append(URL)
                        logger.debug("id:{}, url:{}, requestBody {}, response:{}".format(http_message['id'], URL, http_message['requestBody'], response.text))
            

            elif http_message['responseBody'] in response.text:
                requests_replay_count += 1
                requests_replay_url_list.append(URL)
                logger.debug("id:{}, url:{}, requestBody {}, response:{}".format(http_message['id'], URL, http_message['requestBody'], response.text))
            else:
                pass
                # print(http_message['id'], response.status_code, "False")

    logger.info("requests replay success count: {}".format(requests_replay_count))
    logger.info(requests_replay_url_list)


if __name__ == "__main__":
    http_message_dict = get_http_metadata()
    requests_replay(http_message_dict)
