## 背景概述

近日，深信服安全团队通过深信服安全设备发现一起安全事件，感染主机引发了下载恶意Powershell脚本（160001） 的安全告警。

经过研究发现该病毒名为“匿影”木马，主要目的是进行挖矿，并在内网使用永恒之蓝进行横向传播，感染后在本机创建计划任务、WMI等进行持久化，通过组建大量僵尸网络、多个钱包并行挖矿以提高收益。

## ****母体脚本分析与溯源****

1、安全事件告警的url均为http://mywebsaat.xyz/kp.txt，下载的ip地址为：67.216.77、104.27.190.32，从不同的目的主机下载的恶意文件的MD5不同。![](https://image.3001.net/images/20200814/1597389231.png!small)

2、通过访问http://app.mywebsaat.xyz:8175/kill.txt获取要关闭的进程的。进程列表如下：

![](https://image.3001.net/images/20200814/1597389253.png!small)

先停止进程，然后再进行删除：

![](https://image.3001.net/images/20200814/1597389274.png!small)

3、通过http://ip.tool.chinaz.com网站查询受害主机的公网ip地址。然后通过正则表达式，获取页面中的ip地址：

![](https://image.3001.net/images/20200814/1597389295.png!small)

4、获取进程的路径和进程执行的命令，操作系统的版本，内存的信息以及CPU的信息：

![](https://image.3001.net/images/20200814/1597389321.png!small)

5、用公网ip地址，本地IP地址，系统版本号，CPU利用率命名文件名。

![](https://image.3001.net/images/20200814/1597389351.png!small)

6、通过ftp协议上传系统信息的文件 到 16.63.149，用户名为：liujunbd， 密码为：hxlj19760304。

![](https://image.3001.net/images/20200814/1597389372.png!small)

7、通过链接 http://www.worldyou.top/images/5555.jpg 下载恶意伪造文件 jpg
放在C:\Users\Public\windesktopggh.dll，

文件的sha256为：

    
    
    9d5ab1547ac84d2e94647b430be3feb97b89a70ea993a42c04db8290848bf3c1

下载该文件，在沙箱中运行，为伪造的PE文件，并存在恶意行为：

![](https://image.3001.net/images/20200814/1597389403.png!small)

![](https://image.3001.net/images/20200814/1597389413.png!small)

![](https://image.3001.net/images/20200814/1597389438.png!small)

![](https://image.3001.net/images/20200814/1597389447.png!small)

8、运行挖矿程序，其挖矿的地址为：f2pool.com:6000，钱包为：

    
    
    hs1qu8xtcklt3mujrcw2er785jelk22udgpkxq0qjx。

![](https://image.3001.net/images/20200814/1597389481.png!small)

在[ _https://www.f2pool.com/_](https://www.f2pool.com/)网站 通过其钱包查询其挖矿情况：

![](https://image.3001.net/images/20200814/1597389496.png!small)

计算每天的收益，约为68元；

![](https://image.3001.net/images/20200814/1597389507.png!small)

另一个xmr 的钱包：

    
    
    456jdPdTxbuixumJ2NiDhYgRs2GSBAFwa2hkYu1gpPHtRhz3mnJigeqWW1dRTeSiHBbHc2f18vc5VgiX9ofccGDQ6NVVkVV

每天收益大概在62元。目前来看，其每天的总收益在130左右，一个月的收益在3900左右。

![](https://image.3001.net/images/20200814/1597389526.png!small)![](https://image.3001.net/images/20200814/1597389536.png!small)

9、访问其ftp的地址：16.63.149，可以发现其作案证据。里面约有3500个的记录信息文件。日期从2020-06-05开始：![](https://image.3001.net/images/20200814/1597389569.png!small)

并且在其收集的信息中，发现还有其他的钱包：地址

    
    
    hs1qqx8dlhtxqnny4a8jdkxge9u7qu5er4j863d5x2

![](https://image.3001.net/images/20200814/1597389582.png!small)

10、其中还是以powershell作为主要的工具。其中每80分钟会去下载一次病毒样本：

![](https://image.3001.net/images/20200814/1597389622.png!small)

11、通过永恒之蓝在内网进行横向传播

![](https://image.3001.net/images/20200814/1597389632.png!small)

12、发现一个txt命名的文件，里面存放两个ip地址，均为河北保定的。

![](https://image.3001.net/images/20200814/1597389653.png!small)![](https://image.3001.net/images/20200814/1597389668.png!small)

13、查询hs1qqx8dlhtxqnny4a8jdkxge9u7qu5er4j863d5x2钱包的收益，发现最早收益的日期为2020-03-28。![](https://image.3001.net/images/20200814/1597389699.png!small)

从目前已知的钱包的收益记录中，发现该病毒最早在2020-03-28就已经开始进行挖矿活动。

## ****windesktopggh.dll分析****

1、windesktopggh是母体脚本加载运行的功能dll文件，会先检验自身后缀是否为HLP,INI：

![](https://image.3001.net/images/20200814/1597389729.png!small)

2、解密出一个PE文件，据悉：

![](https://image.3001.net/images/20200814/1597389775.png!small)

3、创建新cmd进程，写入解密的PE文件并进行调用：

![](https://image.3001.net/images/20200814/1597389802.png!small)

4、恶意文件中的API都是通过即时获取地址的方式进行调用：

![](https://image.3001.net/images/20200814/1597389814.png!small)

5、检测是否存在C:\ProgramData\googlp.txt文件：

![](https://image.3001.net/images/20200814/1597389827.png!small)

如不存在该文件，则弹出报错窗口，结束进程：

![](https://image.3001.net/images/20200814/1597389846.png!small)

如存在则继续，注册一个窗口类，创建Windows窗口，利用Windows消息机制调用消息处理函数，执行恶意代码：

![](https://image.3001.net/images/20200814/1597389915.png!small)

6、再次创建cmd进程进行注入，根据系统选择注入x64还是x86的PE文件：

![](https://image.3001.net/images/20200814/1597389931.png!small)

7、在新进程中再次使用创建Windows窗口利用消息处理机制调用恶意代码：

![](https://image.3001.net/images/20200814/1597389948.png!small)

8、创建服务相关注册表键值SYSTEM\CurrentControlSet\Services\FileDriver.sys，并设置各项相关值：

![](https://image.3001.net/images/20200814/1597389964.png!small)

9、创建服务，Image Path对应释放的恶意驱动文件，恶意驱动用于实现Rootkit功能：

![](https://image.3001.net/images/20200814/1597389982.png!small)

10、读取自身母体到内存：

![](https://image.3001.net/images/20200814/1597389994.png!small)

11、向驱动程序发送指令：

![](https://image.3001.net/images/20200814/1597390005.png!small)

## ****基础加固建议****

1、避免打开来历不明的邮件、链接和网址附件等，尽量不要在非官方渠道下载非正版的应用软件，发现文件类型与图标不相符时应先使用安全软件对文件进行查杀；

2、使用高强度的主机密码和数据库密码，并避免多台设备使用相同密码，尽量关闭不必要的共享；

3、定期检测系统漏洞并且及时进行补丁修复，常见易被木马家族利用进行横向传播的漏洞补丁包括MS17-010、MS08-067等。

