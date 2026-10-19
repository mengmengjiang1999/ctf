**近日，深信服安全团队捕获到一款新型的Linux挖矿木马，该木马通过bash命令下载执行多个功能模块，通过SSH暴力破解、SSH免密登录利用、Hadoop
Yarn未授权访问漏洞和自动化运维工具内网扩散，且该木马的文件下载均利用暗网代理，感染后会清除主机上的其他挖矿木马，以达到资源独占的目的。**

![](https://image.3001.net/images/20200113/1578881370_5e1bd15a03f3c.png!small)

##  **感染现象**

被感染的Linux服务器上，可以明显看到一个CPU占用率很高的进程，名字为随机字符：

![](https://image.3001.net/images/20200113/1578881374_5e1bd15e7fdd0.png!small)

查看进程对应的可执行文件，是以一串疑似MD5的字符命名（并非文件真实MD5），但已经被删除：

![](https://image.3001.net/images/20200113/1578881378_5e1bd162e891d.png!small)

通过crontab –l命令可以看到可疑的定时任务：

![](https://image.3001.net/images/20200113/1578881382_5e1bd166c7e64.png!small)

定时任务对应的sh脚本内容为base64编码过的命令：

![](https://image.3001.net/images/20200113/1578881386_5e1bd16acf9e0.png!small)

##  **病毒母体-** **int**

该ELF文件是作为病毒的母体和守护进程，运行后会将自身进程名重命名为一个随机的字符串：

![](https://image.3001.net/images/20200113/1578881393_5e1bd17112695.png!small)

删除自身对应的可执行文件：

![](https://image.3001.net/images/20200113/1578881398_5e1bd1760b036.png!small)

解码并创建目录/tmp/.X11-unix，检测目录中是否存在00文件，该文件是用于记录进程的pid：

![](https://image.3001.net/images/20200113/1578881401_5e1bd1797f0fe.png!small)

创建子进程：

![](https://image.3001.net/images/20200113/1578881406_5e1bd17e830f1.png!small)

通过setsid，将子进程脱离当前会话并且创建新的会话

![](https://image.3001.net/images/20200113/1578881410_5e1bd1820b4cb.png!small)

并将新的会话进程ID写入/tmp/.X11-unix/00文件：

![](https://image.3001.net/images/20200113/1578881413_5e1bd185a8c8e.png!small)

执行base64编码的bash命令，共有5个不同的bash命令，分别用于下载不同模块和执行不同的功能：

![](https://image.3001.net/images/20200113/1578881417_5e1bd1893588d.png!small)

###  **bash-** **01** **本机持久化**

解码后的内容如下，功能是用于创建定时任务.xzfix.sh：

![](https://image.3001.net/images/20200113/1578881421_5e1bd18d32616.png!small)

定时任务的内容解码后如下，功能为下载int文件：

![](https://image.3001.net/images/20200113/1578881426_5e1bd1921a45e.png!small)

###  **bash** **-02** **内网传播**

主要功能为下载脚本卸载安防产品（其中阿里云的安骑士、腾讯云的云镜等产品）：

![](https://image.3001.net/images/20200113/1578881430_5e1bd1960922d.png!small)

下载可执行文件trc和bot：

![](https://image.3001.net/images/20200113/1578881434_5e1bd19a974d8.png!small)

其中trc文件用于Hadoop Yarn未授权访问漏洞利用，运行时会将自身进程ID写入/tmp/.X11-unix/2文件中：

![](https://image.3001.net/images/20200113/1578881438_5e1bd19e4d9f5.png!small)

获取当前所有的节点，并且对本地网络进行漏洞攻击

![](https://image.3001.net/images/20200113/1578881441_5e1bd1a19df74.png!small)

其漏洞执行命令如下，该命令会下载病毒程序hd进行进一步感染：

![](https://image.3001.net/images/20200113/1578881445_5e1bd1a52495e.png!small)

除漏洞利用外，该挖矿木马还会通过ssh暴力破解进行内网传播：

![](https://image.3001.net/images/20200113/1578881448_5e1bd1a8a6e56.png!small)

利用运维工具（ansible、knife、salt）对内网服务器进行批量感染，利用ssh远程执行命令，命令通过base64解码后是下载病毒母体int：

![](https://image.3001.net/images/20200113/1578881453_5e1bd1ad1abe1.png!small)

###  **bash-** **03** **竞争对手清理**

清除服务器上其他的挖矿木马，改写hosts文件让其他挖矿无法访问对应的域名，以达到独占的目的：

![](https://image.3001.net/images/20200113/1578881458_5e1bd1b23b88b.png!small)

###  **bash-** **04** **下载挖矿**

下载可执行文件cpu：

![](https://image.3001.net/images/20200113/1578881462_5e1bd1b6ad5fc.png!small)

该文件为挖矿程序：

![](https://image.3001.net/images/20200113/1578881466_5e1bd1bada215.png!small)

###  **bash-** **05** **状态控制**

下载cmd脚本：

![](https://image.3001.net/images/20200113/1578881471_5e1bd1bf9f6a7.png!small)

cmd脚本中的命令功能是当主机网络无法连接到矿池时，会结束掉自身的挖矿进程，增强隐蔽性：

![](https://image.3001.net/images/20200113/1578881475_5e1bd1c3ab67e.png!small)

##  **解决方案**

> 1\. 服务器使用复杂密码，且避免与其他密码重复；
>
> 2\. 如无必要，不要将接口开放在公网，改为本地或者内网调用；
>
> 3\. 升级Hadoop到2.x版本以上，并启用Kerberos认证功能，禁止匿名访问；
>
> 4\. 清理随机字符名的可疑进程和高CPU占用进程；
>
> 5\. 清理恶意定时任务，删除/tmp/.X11-unix目录。

 ***本文作者： 深信服千里目安全实验室，转载请注明来自FreeBuf.COM**  

