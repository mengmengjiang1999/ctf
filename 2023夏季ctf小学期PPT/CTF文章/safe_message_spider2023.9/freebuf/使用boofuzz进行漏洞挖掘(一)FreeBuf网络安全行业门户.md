> boofuzz采用python开发的一款fuzz工具,对协议fuzz有着良好的支持。对二次开发和插件的编写都有非常好的API支持

Fuzz的原理和如何安装boofuzz在这里不再阐述我们直接进入正题。

 ** _发现第一个漏洞_**

从github上clone下代码会发现有examples目录

![image.png](https://image.3001.net/images/20180927/1538039602_5bac9f325cfe0.png!small)

进入examples中我们先编辑和运行第一个例子(FUZZ ftp服务)就像你第一次写代码那样hello world!那样。

vim ftp-simple.py

![image.png](https://image.3001.net/images/20180927/1538039809_5baca001054ea.png!small)

修改红色框框中的一些基本信息改为你的需要挖掘的IP地址

然后我们python ftp-simple.py....... N个时间点后

![image.png](https://image.3001.net/images/20180927/1538050382_5bacc94ec390a.png!small)

fuzz中断了， 发现了一个case，同时，ftp程序也停止了服务....

![image.png](https://image.3001.net/images/20180927/1538050471_5bacc9a71de63.png!small)
至此，我们已经发现了第一个漏洞，由这个case可见，是由于这个ftp服务器没有处理好stor命令导致的缓存区溢出漏洞。

> **下一篇** _分析 ftp-simple.py代码 _

