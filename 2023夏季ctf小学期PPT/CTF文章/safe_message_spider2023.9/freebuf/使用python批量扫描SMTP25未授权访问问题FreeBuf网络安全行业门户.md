# 使用python实现SMTP 25未授权访问批量扫描

测试某系统过程中发现很多服务器都开了25和110端口，但是不确定是不是真的邮件服务端口，所以打算尝试复现下漏洞。

## SMTP匿名邮件

SMTP(Simple Mail Transfer Protocol)，简单邮件传输协议是一种可靠且有效的电子邮件传输协议。

但是在设计之初，他并没有添加身份验证的机制，导致任意用户可以连接到SMTP服务器进行邮件发送的操作。当然经过这么多年，已经有了SMTP-AUTH扩展来保证其安全性。

由于其巨大的基数，导致大量因为设置导致未开启验证或者旧版不支持SMTP-AUTH的STMP仍在现网环境运行，导致大量的垃圾/诈骗邮件依然在网上传播，于是有了这篇文章来记录下学习的过程。

## 漏洞准备

为了保证环境真实可控，还是自己搭一个吧。

系统环境选择了kali 2020.1，毕竟省事，还能点到专栏名字，血赚。

现在最简单安装这些服务环境的方法就是docker了。

    
    
    sudo systemctl daemon-reload
    sudo systemctl restart docker.service   //重启docker服务，不然可能会Cannot connect to the Docker 错误
    sudo docker search smtp //搜索smtp服务的镜像
    

![image-20200323190434208.png](https://image.3001.net/images/20200324/1585018054_5e7974c6bc7bb.png!small)

选一个STARS最多的就好了。

    
    
    sudo docker pull namshi/smtp
    

这个时候如果你条件有限用的是公司小水管，就可能会发现下载很慢很慢，这时候要切一下国内源：

    
    
    sudo vi /etc/docker/daemon.json   //没有内容就创建一下，不用慌
    

然后添加如下内容：

    
    
    {
        "registry-mirrors": ["http://hub-mirror.c.163.com"]
    }
    

添加后重启docker：

    
    
    sudo systemctl restart docker.service
    

下载就起飞了

![image-20200323195507765.png](https://image.3001.net/images/20200324/1585018093_5e7974ed1336e.png!small)  

然后开启docker：

    
    
    sudo docker run --restart=always -d -e "RELAY_NETWORKS=:0.0.0.0/0" --name smtp -p 25:25 namshi/smtp
    

![image-20200323195924763.png](https://image.3001.net/images/20200324/1585018119_5e797507476de.png!small)

尝试使用telnet或者nc连接一下（系统里有哪个就用哪个，都行）

![image-20200323202929232.png](https://image.3001.net/images/20200324/1585018141_5e79751d43f9e.png!small)

可以看到返回了220，说明了连接成功

输入HELP可以看到支持的指令

![image-20200323203121900.png](https://image.3001.net/images/20200324/1585018157_5e79752db5383.png!small)

使用EHLO或者HELO对服务器打个招呼~

![image-20200323203252061.png](https://image.3001.net/images/20200324/1585018168_5e797538348b6.png!small)  

可以看到服务器返回了250。

继续编写 MAIL FROM:< XX@XX.Xx > 这是指定发件人：

![image-20200323203434889.png](https://image.3001.net/images/20200324/1585018177_5e7975417dcf4.png!small)

然后编写RCPT TO:< 118xxxxx@qq.com > 这是指定收件人：

![image-20200323203620917.png](https://image.3001.net/images/20200324/1585018186_5e79754a558d3.png!small)

然后输入DATA开始编写内容，并且以单独的一行中只有一个"."来标识邮件内容结束:

![image-20200323203758487.png](https://image.3001.net/images/20200324/1585018193_5e797551149e0.png!small)  

可以看到最后依然是250 OK，id后面是邮件的队列，说明添加邮件成功。

可以用QUIT来退出连接了。（小写也可以呦）

![image-20200323203857000.png](https://image.3001.net/images/20200324/1585018201_5e797559906b1.png!small)

这样就是一个完整的连接流程了。

总结一下：

  1. 使用telnet或者nc连接smtp服务的25端口，连接成功返回220
  2. 使用EHLO xxxx 或者 HELO xxxx ，连接成功返回250
  3. 使用MAIL FROM:< xx@xx > 指定发件人，设置成功返回250
  4. 使用RCPT TO:< XX@XX > 指定收件人，设置成功返回250
  5. 使用DATA写入邮件内容，以单行的“.”结束，编写成功返回250，并且返回队列id
  6. 使用QUIT退出连接

## 网络实战

为了获取存在问题的环境，在FOFA中搜索

    
    
    "SMTP" && port="25" && country="CN"
    

可以获取到国内的开启默认端口的主机IP地址，选国内是为了连接速度快。

![13.png](https://image.3001.net/images/20200324/1585018267_5e79759b3d645.png!small)

##开始利用尝试使用telnet连接

    
    
    telnet 1xxxxxx7 25
    

可以连接成功

![image-20200324100744020.png](https://image.3001.net/images/20200324/1585018294_5e7975b65b729.png!small)

尝试使用EHLO命令，看看会不会返回支持的扩展：

![image-20200324100838807.png](https://image.3001.net/images/20200324/1585018307_5e7975c3411f1.png!small)

然后，继续MAIL FROM和RCPT TO，

![image-20200324095619257.png](https://image.3001.net/images/20200324/1585018320_5e7975d0c4a2e.png!small)

会发现需要认证。哦吼吼，继续看看别的。

看到一个没有AUTH扩展的，尝试连接一下：

![image-20200324100424896.png](https://image.3001.net/images/20200324/1585018337_5e7975e15c824.png!small)

一套操作下来，稳健：

![image-20200324100514763.png](https://image.3001.net/images/20200324/1585018349_5e7975ed8a49c.png!small)  

## 批量检测

可能批量扫描扫描出的25端口很多，一个一个测过去很麻烦，需要一个方法进行批量扫描。

这里需要解决两个问题，

  1. 确定NMAP没有误报，扫描出的25端口的确是smtp服务
  2. 尝试获取smtp服务能否匿名发送邮件，判断的依据就是不会返回553代码

如果用python调用telnet，虽然subprocess可以直接调用telnet，但是执行时不能正确返回telnet命令的结果（处理起来太麻烦了）。所以只能用python
telnetlib的库来实现（直接调用shell里的命令有时候真的弱爆了）

导入的格式目前是 xx.xx.xx.xx:xx 但是目前只写了针对25默认端口

    
    
    import telnetlib
    import time
    
    
    class TelnetClient():
        def __init__(self,):
            self.tn = telnetlib.Telnet()
    
        # 此函数实现telnet连接对应服务器25端口
        def login_host(self,host_ip):
            try:
                # self.tn = telnetlib.Telnet(host_ip,port=23)
                self.tn.open(host_ip,port=25)
            except:
                print('%s网络连接失败'%host_ip)
                return False
            else:
                time.sleep(5)
            # read_very_eager()获取到的是的是上次获取之后本次获取之前的所有输出
                try:
                    command_result = self.tn.read_very_eager().decode('ascii')
                except:
                    print('%s smtp端口连接失败' % host_ip)
                    return False
                else:
                    # 等待返回Mail Server ESMTP ready,返回该信息说明登陆成功
                    if '220'in command_result:
                        print('%s smtp登录成功'%host_ip)
                        self.tn.write("EHLO localhost\n")
                        command_result = self.tn.read_very_eager().decode('ascii')
                        if "553" not in command_result and "connection closed" not in command_result:
                            self.tn.write("MAIL TO:<123@QQ.COM>\n")
                            print("输入MAIL TO内容")
                            command_result = self.tn.read_very_eager().decode('ascii')
                            if "553" not in command_result and "connection closed" not in command_result:
                                self.tn.write("RCPT TO:<456@QQ.COM>\n")
                                print("输入MAIL TO内容")
                                command_result = self.tn.read_very_eager().decode('ascii')
                                if "553" not in command_result:
                                    print("可能存在未授权问题")
                                    return True
                    else:
                        print('%s smtp登录失败'%host_ip)
                        return False
    
        # 退出telnet
        def logout_host(self):
            self.tn.write(b"quit\n")
    
    
    if __name__ == '__main__':
        ip_list = open("iplist1.txt", 'r')
        for line in ip_list.readlines():
            target=line.split(":",1)
    
            if ":25" in line:
                print("-----------------------------")
                print(target[0])
                telnet_client = TelnetClient()
                # 如果登录结果返加True，则执行命令，然后退出
                if telnet_client.login_host(target[0]):
                    telnet_client.logout_host()
                print("-----------------------------")
    

导入的需要是一个格式为 ip:port 的文件,因为懒，所以只写了25端口，机智如你，肯定可以随便改好的。

## 题外话

检测smtp其实nmap有对应的脚本，只是没有看到匿名模式的，所以才自己尝试写了一下，其他的可以参考这些：

![image-20200324103544938.png](https://image.3001.net/images/20200324/1585018364_5e7975fc7e656.png!small)  

