# A framework to capture and analyse network traffic for Android
> Python version：Python 3.8

TraceDroid is a lightweight framework for Android traffic collection and analysis.
TraceDroid hook the key functions responsible for sending HTTP/HTTPS requests in the Android framework
layer and native layer, saving the corresponding call stacks, parsing network traffic and recovering files transmitted 
in the traffic. Then build the connections among these three components (network traffic, call stack and files).
#### requirements.txt

Generating requirements.txt

```
pip freeze > requirements.txt
```

install dependencies in requirements.txt
```
pip install -r requirements.txt
```


#### Dependent tables

##### APKMetadata

| Field            | Type          | Null | Key  | Default           | Extra          |
| ---------------- | ------------- | ---- | ---- | ----------------- | -------------- |
| APKID            | bigint(20)    | NO   | PRI  |                   | auto_increment |
| APPName          | varchar(1024) | NO   |      |                   |                |
| APKName          | varchar(1024) | NO   |      |                   |                |
| APKFilePath      | varchar(1024) | NO   |      |                   |                |
| APKStoreName     | varchar(1024) | NO   |      |                   |                |
| createTime       | datetime      | NO   |      | CURRENT_TIMESTAMP |                |
| lastModifiedTime | datetime      | NO   |      |                   |                |
| needAnalyse      | int(11)       | NO   |      | 1                 |                |

##### CaptureLog

| Field         | Type          | Null | Key  | Default           | Extra          |
| ------------- | ------------- | ---- | ---- | ----------------- | -------------- |
| logID         | bigint(20)    | NO   | PRI  |                   | auto_increment |
| APKID         | varchar(1024) | NO   |      |                   |                |
| APKName       | varchar(1024) | NO   |      |                   |                |
| APPName       | varchar(1024) | NO   |      |                   |                |
| createTime    | datetime      | NO   |      | CURRENT_TIMESTAMP |                |
| pcapFilePath  | varchar(1024) | NO   |      |                   |                |
| stackFilePath | varchar(1024) | NO   |      |                   |                |
| needExtract   | int(11)       | NO   |      |                   |                |
| extractTime   | datetime      | NO   |      |                   |                |

##### PreProcessLog

| Field       | Type          | Null | Key  | Default           | Extra          |
| ----------- | ------------- | ---- | ---- | ----------------- | -------------- |
| logID       | bigint(20)    | NO   | PRI  |                   | auto_increment |
| APKID       | bigint(20)    | NO   |      |                   |                |
| APKName     | varchar(1024) | NO   |      |                   |                |
| APPName     | varchar(1024) | NO   |      |                   |                |
| processTime | datetime      | NO   |      | CURRENT_TIMESTAMP |                |

##### HTTP

| Field           | Type                | Null | Key  | Default | Extra          |
| --------------- | ------------------- | ---- | ---- | ------- | -------------- |
| id              | bigint(20) unsigned | NO   | PRI  | None    | auto_increment |
| packageName     | varchar(1024)       | YES  |      |         |                |
| srcAddr         | varchar(1024)       | YES  |      |         |                |
| srcPort         | int(11)             | YES  |      | None    |                |
| dstAddr         | varchar(1024)       | YES  |      |         |                |
| dstPort         | int(11)             | YES  |      | None    |                |
| host            | varchar(1024)       | YES  |      |         |                |
| URL             | varchar(1024)       | YES  |      |         |                |
| requestTime     | timestamp           | YES  |      | None    |                |
| requestHeaders  | varchar(1024)       | YES  |      |         |                |
| requestBody     | varchar(1024)       | YES  |      |         |                |
| responseHeaders | varchar(1024)       | YES  |      |         |                |
| responseBody    | varchar(1024)       | YES  |      |         |                |
| protocol        | varchar(1024)       | YES  |      |         |                |
| method          | varchar(1024)       | YES  |      |         |                |
| content-type    | varchar(1024)       | YES  |      |         |                |