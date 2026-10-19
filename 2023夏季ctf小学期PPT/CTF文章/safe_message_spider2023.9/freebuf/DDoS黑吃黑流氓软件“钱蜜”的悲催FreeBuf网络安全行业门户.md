## 背景描述  

**近期，毒霸监测到一款DDOS木马的感染量呈现出上升趋势，而同时呈现出相同增长趋势的，还有部分流氓软件。经过溯源分析，我们发现上述2类软件均来自上海奇陆网络科技有限公司的一款叫做“钱蜜省钱助手”的软件。**

![logo.png](https://image.3001.net/images/20190506/1557123846_5ccfd3061aee8.png!small)

该软件除了根据云端配置文件，下载推广流氓软件外，还会劫持主页、篡改浏览器收藏夹、盗取QQ的Token在QQ部落发广告，使目标电脑变成肉鸡，进行DDOS攻击。有趣的是，该病毒下载的DDOS木马内部竟还包含一个后门，猜测该DDOS样本是在某个木马生成器中生成的，而生成器的作者又在其内部留下了后门。

## 技术分析

该病毒的主要运行流程如下：

![image1.png](https://image.3001.net/images/20190506/1557123858_5ccfd31212a9b.png!small)

当钱蜜安装完成后，会在安装目录释放以下文件：

![image2.png](https://image.3001.net/images/20190506/1557123883_5ccfd32b78ff2.png!small)

qm.exe为软件主程序，该程序根据启动参数的不同，激活不同的功能：

![image3.png](https://image.3001.net/images/20190506/1557123892_5ccfd33471f50.png!small)

若启动参数为/from=qm_azb，则从down.qm188.com/updatecfg2.ini下载配置文件，程序根据配置文件中的标志指令，下载安装不同的文件，以我们当前分析的程序为例，该程序获取到的标志为1，根据这个标志从down.qm188.com/updateall.7z下载得到了一个加密的压缩包文件updateall.7z：

![image4.png](https://image.3001.net/images/20190506/1557123902_5ccfd33e2b533.png!small)

该压缩包经过解密后，解压释放出demo.dll，该文件会继续从down.qm188.com/check.7z下载一个加密的压缩包，包内包含一个lock.dll，该DLL文件封装了针对市面上常见浏览器的劫持修改函数：

![image5.png](https://image.3001.net/images/20190506/1557123915_5ccfd34b6fac1.png!small)

而demo.dll则主要执行：

> 1.篡改浏览器收藏夹，静默替换收藏项链接；
>
> 2.安装浏览器插件；
>
> 3.锁定主页为hao.360.cn/?src=lm&ls=n42a7fc6c92。

被针对进行篡改的浏览器如下：

![image6.png](https://image.3001.net/images/20190506/1557123950_5ccfd36e292f9.png!small)

在劫持完浏览器之后，还会安装ebuyast40510.exe和MyThirdDemo.exe，前者主是另一个助手类软件，而后者则会根据云端test.ini的配置文件，下载运行：ServiceDemo.exe、ServiceSecondDemo.exe、ServiceThirdDemo.exe，这三个程序最终通过testconfig.ini文件，下载安装所需要推广的软件以及DDOS木马、盗号木马等程序：

![image7.png](https://image.3001.net/images/20190506/1557123963_5ccfd37b1cd9f.png!small)

以下载的灭神7777.exe为例，首先从作者的网站[www.wu52q.cn/?c=Public&a=get_config](http://www.wu52q.cn/?c=Public&a=get_config)获得相关配置属性（猜测是接下来要刷回复的QQ部落信息），然后通过获取本机登录的QQ的Cookie以及Token，获得ClientKey之后构建对应的URL，快速登录QQ部落成功后，往指定bid的部落内回复指定帖子：

![image8.png](https://image.3001.net/images/20190506/1557123979_5ccfd38b348fb.png!small)

实际效果如下：

![image9.png](https://image.3001.net/images/20190506/1557123990_5ccfd396227b7.png!small)

而下载运行DDOS木马，通过读取Nationalessgf服务是否存在来判断是否已经被感染运行。若未运行，则会连接黑客的远程服务器104.233.231.199:6366接收指令。

![image10.png](https://image.3001.net/images/20190506/1557123999_5ccfd39f6ec06.png!small)

该DDOS木马具体接收的指令和用途如下，从部分错误的代码书写方式（指令16）来看，病毒本身还存在一些问题：

![image11.png](https://image.3001.net/images/20190506/1557124009_5ccfd3a90fc9e.png!small)

我们经过分析后发现，该木马除了常规的远控功能（DDOS攻击、远程执行文件、自更新、隐藏窗口打开浏览器等）外，其内部还竟然包含了一个额外的远控后门：

![image12.png](https://image.3001.net/images/20190506/1557124058_5ccfd3dade62b.png!small)当系统时间大于2013年9月20日时，则会创建线程执行远控，远控地址为：xl.mrdarkddos.com，猜测病毒作者可能只是在网上查找到了某个远控程序的代码或者生成器，而生成的DDOS木马本身却包含了后门，可谓是忙活了半天，却为别人做了“嫁衣”：

![image13.png](https://image.3001.net/images/20190506/1557124068_5ccfd3e47c76b.png!small)

## 附录IOC  

hxxp://down.qm188.com/update/Setup_1000.exe

hxxp://down.qm188.com/update/Setup_2000.exe

hxxp://down.qm188.com/qd/Setup_1001.exe

hxxp://down.qm188.com/qd/Setup_1002.exe

hxxp://down.qm188.com/qd/Setup_1003.exe

hxxp://down.qm188.com/qd/Setup_1004.exe

hxxp://down.qm188.com/qd/Setup_1005.exe

hxxp://down.qm188.com/updatecfg.ini

hxxp://down.qm188.com/updatecfg2.ini

hxxp://down.qm188.com/updatecfg3.ini

hxxp://down.qm188.com/demo/testconfig.ini

hxxp://down.qm188.com/demo/ServiceDemo.exe

hxxp://down.qm188.com/demo/ServiceSecondDemo.exe

hxxp://down.qm188.com/demo/ServiceThirdDemo.exe

hxxp://down.qm188.com/updateall.7z

hxxp://down.qm188.com/updatenopage.7z

hxxp://down.qm188.com/updatekz.7z

hxxp://down.qm188.com/updatefav.7z

hxxp://down.qm188.com/check.7z

hxxp://down.qm188.com/demo/MyThirdDemo.exe

hxxp://down.qm188.com/demo/MySecondDemo.exe

hxxp://down.qm188.com/demo/todayhot.exe

hxxp://183.61.164.130:8019/7777/7777.exe

5eafa08f426975b3f865f794650fb416

ddeac3d82b058b6b7826ff4d5a3ffe16

cd2b9531efce483b9f22896435a943dc

 ***本文作者：安全豹，转载请注明来自FreeBuf.COM**

