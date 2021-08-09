import logging
import pathlib

import pcapkit
import gzip

import DBUtils
import emoji


logging.getLogger('chardet.charsetprober').setLevel(logging.INFO)
logging.getLogger('chardet.universaldetector').setLevel(logging.INFO)

logging.config.fileConfig('ExtractLog.conf')
logger = logging.getLogger('PcapExtractEngine')

requestFileSavePath = './in/'
responseFileSavePath = './out/'
path = pathlib.Path(requestFileSavePath)
if not path.exists():
    path.mkdir()
path = pathlib.Path(responseFileSavePath)
if not path.exists():
    path.mkdir()


# HTTP chunked decode
def decodeChunked(content):
    newcont = b''
    while True:
        temp = content.find(b'\r\n')
        if temp == -1:
            return newcont
        strtemp = str(content[0:temp])[2:-1]
        try:
            readbytes = int('0x'+strtemp, 16)
        except Exception:
            return b''
        if readbytes == 0:
            break
        else:
            offset = temp + 2 
            newcont += content[offset:readbytes+offset]
            offset += readbytes
            content = content[offset+2:]
    return newcont



def extractHTTPMetadata(captureLog, db_connection):
    '''

    :param APK:
    :return: json file named according by APKName, contain: srcIP, dstIP, srcPort, dstPort, Host, URL, HTTP request Headers, Method, POST Body, HTTP response headers, HTTP response body
    '''

    logger.debug("extracting pcapFile %s" % captureLog['pcapFilePath'])
    pcapFilePath = captureLog['pcapFilePath']

    path = pathlib.Path(pcapFilePath)
    if not path.exists():
        logger.warning("file not exists: %s" % pcapFilePath)
        return -1

    # pcap所有http流信息列表
    httpMessageList = list()

    # http2计数
    http2Count = 0

    # 开启tcp流追踪
    trace = pcapkit.extract(fin=pcapFilePath, nofile=True, trace=True)

    # 遍历每一条tcp流
    for tcpFlow in trace.trace:
        tcpFlowIndex = list(tcpFlow.index)  # tcp流所有frame的编号
        print(tcpFlowIndex)  # 控制台输出

        # tcp流的每个frame的遍历
        while len(tcpFlowIndex) > 0:
            # 每一条http流的信息
            httpMessage = {'srcAddr': '', 'srcPort': None, 'dstAddr': '', 'dstPort': None,
                           'host': '', 'URL': '', 'requestHeaders': '', 'requestBody': b'',
                           'responseHeaders': '', 'responseBody': b'', 'protocol': '',
                           'method': '', 'contentType': '', 'packageName': ''}
            # 偏移量
            index = 0
            requestBodyLength = 0
            responseBodyLength = 0
            chunkedFlag = 0

            # 每次重新进入循环遍历一条http流
            while True:

                if index >= len(tcpFlowIndex):
                    httpMessageList.append(httpMessage)
                    break
                frame = trace.frame[tcpFlowIndex[index]-1]  # frame编号-1是真实的frame
                try:
                    if b'HTTP/2.0\r\n\r\n' in frame.info.packet and pcapkit.HTTP not in frame:
                        http2Count += 1
                        tcpFlowIndex = []
                        break
                except Exception:
                    pass
                    
                # print(tcpFlowIndex)
    
                if pcapkit.HTTP in frame:
                    # 获取到下一条request
                    if frame[pcapkit.HTTP].info.receipt == 'request' and len(httpMessage['requestHeaders']) > 0:
                        index += 1
                        continue
                    # 获取到下一条response，上一条http流一定结束了
                    if frame[pcapkit.HTTP].info.receipt == 'response' and len(httpMessage['responseHeaders']) > 0:
                        httpMessageList.append(httpMessage)
                        break
                
                if pcapkit.HTTP in frame:
                    http = frame[pcapkit.HTTP]
                    # 获取到第一条request
                    if http.info.receipt == 'request' and len(httpMessage['requestHeaders']) == 0:
                        tcpFlowIndex.pop(index)  # 除去当前http流的请求
                        # packageName
                        httpMessage['packageName'] = captureLog['APKName']
                        # srcAddr & srcPort & dstAddr & dstPort
                        httpMessage['srcAddr'] = str(frame[pcapkit.IP].info.src)
                        httpMessage['srcPort'] = frame[pcapkit.TCP].info.srcport
                        httpMessage['dstAddr'] = str(frame[pcapkit.IP].info.dst)
                        httpMessage['dstPort'] = frame[pcapkit.TCP].info.dstport
                        # requestHeaders
                        requestHeaders = http.info.header.info2dict()
                        requestHeaders.pop('request')
                        httpMessage['requestHeaders'] = str(requestHeaders).replace("'", '"')
                        # host
                        if 'Host' in requestHeaders:
                            httpMessage['host'] = requestHeaders['Host']
                        elif 'host' in requestHeaders:
                            httpMessage['host'] = requestHeaders['host']
                        # url & protocol
                        if httpMessage['dstPort'] == 443:
                            httpMessage['URL'] = "https://" + httpMessage['host'] + http.info.header.request.target
                            httpMessage['protocol'] = "HTTPS"
                        else:
                            httpMessage['URL'] = "http://" + httpMessage['host'] + http.info.header.request.target
                            httpMessage['protocol'] = "HTTP"
                        # method
                        httpMessage['method'] = str(http.info.header.request.method)
                        if 'Content-Type' in requestHeaders and httpMessage['method'] == 'POST':
                            httpMessage['contentType'] = requestHeaders['Content-Type']
                        if 'Content-Length' in requestHeaders and httpMessage['method'] == 'POST':
                            if type(requestHeaders['Content-Length']) in (tuple, list):
                                requestBodyLength = int(requestHeaders['Content-Length'][0])
                            else:
                                requestBodyLength = int(requestHeaders['Content-Length'])  
                            if http.info.body is None:
                                continue
                            elif len(http.info.body) < requestBodyLength:
                                requestBodyLength -= len(http.info.body)
                                httpMessage['requestBody'] = http.info.body
                                continue
                            else:
                                requestBodyLength -= len(http.info.body)
                                httpMessage['requestBody'] = http.info.body
                                continue
                        else:
                            chunkedFlag = 1
                            if http.info.body is None:
                                continue
                            else:
                                httpMessage['requestBody'] = http.info.body
                                if httpMessage['requestBody'][-5:] == b'0\r\n\r\n':
                                    chunkedFlag = 0
                                continue
                    elif http.info.receipt == 'response' and len(httpMessage['responseHeaders']) == 0:
                        tcpFlowIndex.pop(index)  # 除去当前http流的响应
                        httpMessage['srcAddr'] = str(frame[pcapkit.IP].info.dst)
                        responseHeaders = http.info.header.info2dict()
                        responseHeaders.pop('response')
                        httpMessage['responseHeaders'] = str(responseHeaders).replace("'", '"')
                        if 'Content-Type' in responseHeaders:
                            httpMessage['contentType'] = responseHeaders['Content-Type']
                        if 'Content-Length' in responseHeaders:
                            if type(responseHeaders['Content-Length']) in (tuple, list):
                                responseBodyLength = int(responseHeaders['Content-Length'][0])
                            else:
                                responseBodyLength = int(responseHeaders['Content-Length'])   
                            # responseBodyLength = int(responseHeaders['Content-Length'])
                            if responseBodyLength == 0:
                                httpMessageList.append(httpMessage)
                                break
                            if http.info.body is None:
                                continue
                            elif len(http.info.body) < responseBodyLength:
                                responseBodyLength -= len(http.info.body)
                                httpMessage['responseBody'] = http.info.body
                            elif len(http.info.body) == responseBodyLength:
                                responseBodyLength -= len(http.info.body)
                                httpMessage['responseBody'] = http.info.body
                                httpMessageList.append(httpMessage)
                                break
                        else:
                            if http.info.body is None and '"Transfer-Encoding": "chunked"' in httpMessage['responseHeaders']:
                                continue
                            elif http.info.body is None:
                                continue
                            httpMessage['responseBody'] = http.info.body
                            if httpMessage['responseBody'][-5:] == b'0\r\n\r\n':
                                httpMessageList.append(httpMessage)
                                break
                elif pcapkit.TCP in frame:
                    if index > 0 and httpMessage['srcAddr'] == str(frame[pcapkit.IP].info.src):
                        index += 1
                        continue
                    tcpFlowIndex.pop(index)
                    # 根据content-length拼接body
                    if requestBodyLength > 0 and httpMessage['srcAddr'] == str(frame[pcapkit.IP].info.src):
                        try:
                            requestBodyLength -= len(frame[pcapkit.TCP].info.raw.packet)
                            httpMessage['requestBody'] += frame[pcapkit.TCP].info.raw.packet
                        except Exception:
                            continue
                    if responseBodyLength > 0 and httpMessage['srcAddr'] == str(frame[pcapkit.IP].info.dst):
                        try:
                            if 'octet-stream' in httpMessage['responseHeaders']:
                                responseBodyLength -= len(frame[pcapkit.TCP].info.raw.packet)
                            else:
                                responseBodyLength -= len(frame[pcapkit.TCP].info.raw.packet)
                                httpMessage['responseBody'] += frame[pcapkit.TCP].info.raw.packet
                            if responseBodyLength == 0:
                                httpMessageList.append(httpMessage)
                                break
                        except Exception:
                            continue
        
                    # 根据chunked拼接body
                    if '"Transfer-Encoding": "chunked"' in httpMessage['requestHeaders'] and chunkedFlag == 1 and httpMessage['srcAddr'] == str(frame[pcapkit.IP].info.src):
                        try:
                            httpMessage['requestBody'] = b''.join((httpMessage['requestBody'], frame[pcapkit.TCP].info.raw.packet))
                            # httpMessage['requestBody'] += frame[pcapkit.TCP].info.raw.packet
                        except Exception:
                            pass
                        if httpMessage['requestBody'][-5:] == b'0\r\n\r\n':
                            chunkedFlag = 0
                    if '"Transfer-Encoding": "chunked"' in httpMessage['responseHeaders'] and httpMessage['srcAddr'] == str(frame[pcapkit.IP].info.dst):
                        try:
                            httpMessage['responseBody'] = b''.join((httpMessage['responseBody'], frame[pcapkit.TCP].info.raw.packet))
                            # httpMessage['responseBody'] += frame[pcapkit.TCP].info.raw.packet
                        except Exception:
                            pass
                        if httpMessage['responseBody'][-5:] == b'0\r\n\r\n':
                            httpMessageList.append(httpMessage)
                            break

    # print(httpMessageList)
    # print(http2Count)
    httpMessageListFinal = list()
    for httpMessage in httpMessageList:
        # print(httpMessage)

        # 跳过http2，信息全为空的情况
        if len(httpMessage['requestHeaders']) == 0 and len(httpMessage['responseHeaders']) == 0:
            continue

        # request decode & decompress
        if 'octet-stream' in httpMessage['requestHeaders']:
            httpMessage['requestBody'] = b''
        if '"Transfer-Encoding": "chunked"' in httpMessage['requestHeaders'] and len(httpMessage['requestBody']) > 0:
            httpMessage['requestBody'] = decodeChunked(httpMessage['requestBody'])
        if '"Content-Type": "application/x-gzip"' in httpMessage['requestHeaders'] and len(httpMessage['requestBody']) > 0:
            try:
                httpMessage['requestBody'] = gzip.decompress(httpMessage['requestBody']).decode('utf-8')
            except Exception:
                pass
        if '"Content-Encoding": "gzip"' in httpMessage['requestHeaders'] and len(httpMessage['requestBody']) > 0:
            try:
                httpMessage['requestBody'] = gzip.decompress(httpMessage['requestBody']).decode('utf-8')
            except Exception:
                pass

        # response decode & decompress
        if 'octet-stream' in httpMessage['responseHeaders']:
            httpMessage['responseBody'] = b''
        if '"Transfer-Encoding": "chunked"' in httpMessage['responseHeaders'] and len(httpMessage['responseBody']) > 0:
            httpMessage['responseBody'] = decodeChunked(httpMessage['responseBody'])
        if '"Content-Type": "application/x-gzip"' in httpMessage['responseHeaders'] and len(httpMessage['responseBody']) > 0:
            try:
                httpMessage['responseBody'] = gzip.decompress(httpMessage['responseBody']).decode('utf-8')
            except Exception:
                pass
        if '"Content-Encoding": "gzip"' in httpMessage['responseHeaders'] and len(httpMessage['responseBody']) > 0:
            try:
                httpMessage['responseBody'] = gzip.decompress(httpMessage['responseBody']).decode('utf-8')
            except Exception:
                pass

        # request file save
        try:
            if '"Content-Type": "multipart/form-data' in httpMessage['requestHeaders']:
                boundary = '--' + httpMessage['requestHeaders'].split('boundary=')[-1].split('"')[0]
                requestBody = httpMessage['requestBody'].split(bytes(boundary, encoding='utf-8'))
                httpMessage['requestBody'] = ''
                for x in requestBody:
                    if b'filename' in x:
                        filename = x.split(b'filename="', 1)[-1].split(b'"')[0]
                        filename = str(filename)[2:-1].split('\\')[-1]
                        filename = pcapFilePath.split('/')[-1] + '__' + httpMessage['srcAddr'] + '_' + str(httpMessage['srcPort']) + '__' + httpMessage['dstAddr'] + '_' + str(httpMessage['dstPort']) + '__' + filename
                        httpMessage['requestBody'] += filename
                        with open(requestFileSavePath + filename, "wb") as f:
                            f.write(x.split(b'\r\n\r\n', 1)[-1])
            if '"Content-Type": "video/mp4"' in httpMessage['requestHeaders']:
                filename = pcapFilePath.split('/')[-1] + '__' + httpMessage['srcAddr'] + '_' + str(httpMessage['srcPort']) + '__' + httpMessage['dstAddr'] + '_' + str(httpMessage['dstPort']) + '__' + httpMessage['URL'].split('/')[-1].split('?')[0] + '.mp4'
                with open(requestFileSavePath + filename, "wb") as f:
                    f.write(httpMessage['requestBody'])
                httpMessage['requestBody'] = filename
            if '"Content-Type": "image/png"' in httpMessage['requestHeaders']:
                filename = pcapFilePath.split('/')[-1] + '__' + httpMessage['srcAddr'] + '_' + str(httpMessage['srcPort']) + '__' + httpMessage['dstAddr'] + '_' + str(httpMessage['dstPort']) + '__' + httpMessage['URL'].split('/')[-1].split('?')[0] + '.png'
                with open(requestFileSavePath + filename, "wb") as f:
                    f.write(httpMessage['requestBody'])
                httpMessage['requestBody'] = filename
            if '"Content-Type": "image/gif"' in httpMessage['requestHeaders']:
                filename = pcapFilePath.split('/')[-1] + '__' + httpMessage['srcAddr'] + '_' + str(httpMessage['srcPort']) + '__' + httpMessage['dstAddr'] + '_' + str(httpMessage['dstPort']) + '__' + httpMessage['URL'].split('/')[-1].split('?')[0] + '.gif'
                with open(requestFileSavePath + filename, "wb") as f:
                    f.write(httpMessage['requestBody'])
                httpMessage['requestBody'] = filename
            if '"Content-Type": "image/jpeg"' in httpMessage['requestHeaders']:
                filename = pcapFilePath.split('/')[-1] + '__' + httpMessage['srcAddr'] + '_' + str(httpMessage['srcPort']) + '__' + httpMessage['dstAddr'] + '_' + str(httpMessage['dstPort']) + '__' + httpMessage['URL'].split('/')[-1].split('?')[0] + '.jpg'
                with open(requestFileSavePath + filename, "wb") as f:
                    f.write(httpMessage['requestBody'])
                httpMessage['requestBody'] = filename
            if '"Content-Type": "application/zip"' in httpMessage['requestHeaders']:
                filename = pcapFilePath.split('/')[-1] + '__' + httpMessage['srcAddr'] + '_' + str(httpMessage['srcPort']) + '__' + httpMessage['dstAddr'] + '_' + str(httpMessage['dstPort']) + '__' + httpMessage['URL'].split('/')[-1].split('?')[0] + '.zip'
                with open(requestFileSavePath + filename, "wb") as f:
                    f.write(httpMessage['requestBody'])
                httpMessage['requestBody'] = filename
            if '"Content-Type": "audio/"mpeg"' in httpMessage['requestHeaders']:
                filename = pcapFilePath.split('/')[-1] + '__' + httpMessage['srcAddr'] + '_' + str(httpMessage['srcPort']) + '__' + httpMessage['dstAddr'] + '_' + str(httpMessage['dstPort']) + '__' + httpMessage['URL'].split('/')[-1].split('?')[0] + '.mp3'
                with open(requestFileSavePath + filename, "wb") as f:
                    f.write(httpMessage['requestBody'])
                httpMessage['requestBody'] = filename
        except Exception:
            httpMessage['requestBody'] = b''

        # response file download
        try:
            if '"Content-Type": "video/mp4"' in httpMessage['responseHeaders']:
                filename = pcapFilePath.split('/')[-1] + '__' + httpMessage['srcAddr'] + '_' + str(httpMessage['srcPort']) + '__' + httpMessage['dstAddr'] + '_' + str(httpMessage['dstPort']) + '__' + httpMessage['URL'].split('/')[-1].split('?')[0] + '.mp4'
                with open(responseFileSavePath + filename, "wb") as f:
                    f.write(httpMessage['responseBody'])
                httpMessage['responseBody'] = filename
            if '"Content-Type": "image/png"' in httpMessage['responseHeaders']:
                filename = pcapFilePath.split('/')[-1] + '__' + httpMessage['srcAddr'] + '_' + str(httpMessage['srcPort']) + '__' + httpMessage['dstAddr'] + '_' + str(httpMessage['dstPort']) + '__' + httpMessage['URL'].split('/')[-1].split('?')[0] + '.png'
                with open(responseFileSavePath + filename, "wb") as f:
                    f.write(httpMessage['responseBody'])
                httpMessage['responseBody'] = filename
            if '"Content-Type": "image/gif"' in httpMessage['responseHeaders']:
                filename = pcapFilePath.split('/')[-1] + '__' + httpMessage['srcAddr'] + '_' + str(httpMessage['srcPort']) + '__' + httpMessage['dstAddr'] + '_' + str(httpMessage['dstPort']) + '__' + httpMessage['URL'].split('/')[-1].split('?')[0] + '.gif'
                with open(responseFileSavePath + filename, "wb") as f:
                    f.write(httpMessage['responseBody'])
                httpMessage['responseBody'] = filename
            if '"Content-Type": "image/jpeg"' in httpMessage['responseHeaders']:
                filename = pcapFilePath.split('/')[-1] + '__' + httpMessage['srcAddr'] + '_' + str(httpMessage['srcPort']) + '__' + httpMessage['dstAddr'] + '_' + str(httpMessage['dstPort']) + '__' + httpMessage['URL'].split('/')[-1].split('?')[0] + '.jpg'
                with open(responseFileSavePath + filename, "wb") as f:
                    f.write(httpMessage['responseBody'])
                httpMessage['responseBody'] = filename
            if '"Content-Type": "application/zip"' in httpMessage['responseHeaders']:
                filename = pcapFilePath.split('/')[-1] + '__' + httpMessage['srcAddr'] + '_' + str(httpMessage['srcPort']) + '__' + httpMessage['dstAddr'] + '_' + str(httpMessage['dstPort']) + '__' + httpMessage['URL'].split('/')[-1].split('?')[0] + '.zip'
                with open(responseFileSavePath + filename, "wb") as f:
                    f.write(httpMessage['responseBody'])
                httpMessage['responseBody'] = filename
            if '"Content-Type": "audio/"mpeg"' in httpMessage['responseHeaders']:
                filename = pcapFilePath.split('/')[-1] + '__' + httpMessage['srcAddr'] + '_' + str(httpMessage['srcPort']) + '__' + httpMessage['dstAddr'] + '_' + str(httpMessage['dstPort']) + '__' + httpMessage['URL'].split('/')[-1].split('?')[0] + '.mp3'
                with open(responseFileSavePath + filename, "wb") as f:
                    f.write(httpMessage['responseBody'])
                httpMessage['responseBody'] = filename
            if '"Content-Type": "application/vnd.android.package-archive"' in httpMessage['responseHeaders']:
                filename = pcapFilePath.split('/')[-1] + '__' + httpMessage['srcAddr'] + '_' + str(httpMessage['srcPort']) + '__' + httpMessage['dstAddr'] + '_' + str(httpMessage['dstPort']) + '__' + httpMessage['URL'].split('/')[-1].split('?')[0] + '.apk'
                with open(responseFileSavePath + filename, "wb") as f:
                    f.write(httpMessage['responseBody'])
                httpMessage['responseBody'] = filename
        except Exception:
            httpMessage['responseBody'] = b''

        if len(httpMessage['URL']) > 1024:
            httpMessage['URL'] = httpMessage['URL'][:1024]
        if len(httpMessage['requestHeaders']) > 1024:
            httpMessage['requestHeaders'] = httpMessage['requestHeaders'][:1024]
        if len(httpMessage['responseHeaders']) > 1024:
            httpMessage['responseHeaders'] = httpMessage['responseHeaders'][:1024]
        
        if type(httpMessage['requestBody']) is bytes:
            httpMessage['requestBody'] = str(httpMessage['requestBody'])[2:-1]
        else:
            httpMessage['requestBody'] = str(httpMessage['requestBody'])
        if type(httpMessage['responseBody']) is bytes:
            httpMessage['responseBody'] = str(httpMessage['responseBody'])[2:-1]
        else:
            httpMessage['responseBody'] = str(httpMessage['responseBody'])

        
        #logger.debug(httpMessage)
        httpMessage['requestBody'] = emoji.demojize(httpMessage['requestBody'])
        httpMessage['responseBody'] = emoji.demojize(httpMessage['responseBody'])
        if len(httpMessage['requestBody']) > 40000:
            httpMessage['requestBody'] = httpMessage['requestBody'][:40000]
        if len(httpMessage['responseBody']) > 40000:
            httpMessage['responseBody'] = httpMessage['responseBody'][:40000]

        httpMessageListFinal.append([httpMessage['packageName'], httpMessage['srcAddr'], httpMessage['srcPort'], httpMessage['dstAddr'], httpMessage['dstPort'], httpMessage['host'], httpMessage['URL'], httpMessage['requestHeaders'], httpMessage['requestBody'], httpMessage['responseHeaders'], httpMessage['responseBody'], httpMessage['protocol'], httpMessage['method'], httpMessage['contentType']])

        # 写入数据库
        # DBUtils.writeHTTPMetaData(httpMessage, db_connection)
        #print("logging success", httpMessageList.index(httpMessage))  # 控制台输出
    
    DBUtils.writeHTTPMetaData(httpMessageListFinal, db_connection)

    # 日志记录pcap中http2的数量
    logger.info('pcap:{}, http2:{}'.format(pcapFilePath.split('/')[-1], http2Count))

