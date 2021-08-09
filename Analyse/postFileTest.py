import requests

url = "https://errlog.umeng.com/upload"
request_headers = {
    "Content-Type": "multipart/form-data; boundary=----------izQ290kHh6g3Yn2IeyJCoc",
    "Content-Disposition": "form-data; name=\"file\"; filename=598808188f4a9d654f000250_1.8_151c8d0c_Pixel-3_9_162147960490320427_20210520110033_fg_java.log.gz",
    "Content-Length": "13893",
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; Pixel 3 Build/PQ3A.190605.003)",
    "Host": "errlog.umeng.com",
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip",
}

request_data = b'------------izQ290kHh6g3Yn2IeyJCoc\r\nContent-Disposition: form-data; name="file"; filename="598808188f4a9d654f000250_1.8_151c8d0c_Pixel-3_9_162147960490320427_20210520110033_fg_java.log.gz"\r\nContent-Type: application/octet-stream\r\n\r\n'
with open("./598808188f4a9d654f000250_1.8_151c8d0c_Pixel-3_9_162147960490320427_20210520110033_fg_java.log.gz", "rb") as f:
    request_data += f.read()
request_data += b'\r\n------------izQ290kHh6g3Yn2IeyJCoc--\r\n'

# print(len(request_data))

response = requests.post(url=url, headers=request_headers, data=request_data)
print(response.text)