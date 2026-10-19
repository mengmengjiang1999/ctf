**Usbrip（源自“USB Ripper”，而不是“USB
RIP”惊人）是一个开源取证工具，带有CLI界面，可让您跟踪USB设备工件（即USB事件历史记录，“已连接”和“已断开连接”事件） Linux机器。**

![](https://image.3001.net/images/20190806/1565064955_5d48fefb39064.png!small)

它是用纯Python 3编写的一小块软件（使用一些外部模块，参见[Dependencies /
PIP](https://github.com/snovvcrash/usbrip#pip-packages)），它解析Linux日志文件（/var/log/syslog **或** /var/log/messages
取决于发行版）以构建USB事件历史表。此类表格可能包含以下列：“
已连接”（日期和时间），“用户”，“VID”（供应商ID），“PID”（产品ID），“产品”，“制造商”，“序列号”，
“端口”和“断开连接”（日期和时间）。此外，它还可以：

> 导出收集的信息作为JSON转储（当然，打开这样的转储）;
>
> 生成一个授权（可信）USB设备列表作为JSON（称之为auth.json）;
>
> 根据以下内容搜索“违规事件” auth.json：show（或生成另一个JSON）USB设备出现在历史记录中并且不会出现在auth.json;
>
> 使用-sflag 安装时，创建加密存储（7zip存档），以便在crontab调度程序的帮助下自动备份和累积USB事件;
>
> 根据其VID和/或PID搜索有关特定USB设备的其他详细信息。

##  **开始**

usbrip可在[PyPI](https://pypi.org/project/usbrip/)下载和安装： $ pip3 install usbrip

###  **Git Clone**

为简单起见，让我们同意所有~/usbrip$出现前缀的命令都在~/usbrip由git clone创建的目录中执行：

    
    
    ~ $ git clone [<https://github.com/snovvcrash/usbrip.git>](<https://github.com/snovvcrash/usbrip.git>) usbrip&& cd usbrip~/usbrip$

由于usbrip仅适用于系统日志文件的 **非修改** 结构，因此，如果更改syslogs的格式（例如，syslog-ng或者）rsyslog，它将无法解析USB历史记录，这就是为什么“Connected”和“Disconnected”字段的时间戳没有年份，这个得记在脑子里。

###  **DEB包**

> python3.6（或更新）解释器
>
> python3-VENV
>
> p7zip-full（由storages模块使用）`~$ sudo apt install python3-venv p7zip-full -y`

###  **PIP包**

usbrip使用以下外部模块：

> [terminaltables](https://github.com/Robpol86/terminaltables)
>
> [termcolor](https://pypi.org/project/termcolor)

###  **手动解决依赖关系**

要手动解决Python依赖关系（实际上不必因为pip或者setup.py可以自动化该过程，请参阅[安装](https://github.com/snovvcrash/usbrip#installation)）

创建一个虚拟环境（可选）并pip从内部运行：

    
    
    ~/usbrip$ python3 -m venv venv && source venv/bin/activate (venv)
    
     ~/usbrip$ pip install -r requirements.txt

或者让[pipenv](https://github.com/pypa/pipenv)one-liner做所有不太干净的事：

    
    
    ~/usbrip$ pipenv install && pipenv shell

之后你可以便携式运行usbrip：

    
    
    ~/usbrip$ python -m usbrip -h Or (venv) ~/usbrip$ python **main**.py -h

##  安装

有两种方法可以将usbrip安装到系统中：pip或setup.py。

    
    
    ‘pip or setup.py’

首先，usbrip是pip可安装的。这意味着在git克隆了repo之后你可以简单地启动pip安装过程，然后在终端的任何地方运行usbrip，如下所示：

    
    
    ~/usbrip$ pip install . (venv) ~/usbrip$ usbrip -h

或者，如果要在本地解析Python依赖关系（不打扰PyPI），请使用setup.py：

    
    
    ~/usbrip$ python3 -m venv venv && source venv/bin/activate (venv)
    
     ~/usbrip$ python setup.py install (venv)
    
     ~/usbrip$ usbrip -h

**注意** ：您可能希望在Python虚拟环境处于活动状态时运行安装过程（如上所示）。

##路径安装后，usbrip使用以下路径：

> /opt/usbrip/ - 项目的主目录;
>
> /var/opt/usbrip/usbrip.ini - usbrip配置文件：保留7zip存储的密码;
>
> /var/opt/usbrip/storage/- USB事件存储：history.7z和violations.7z（在安装过程中创建）;
>
> /var/opt/usbrip/log/-> usbrip日志（建议在使用crontab时记录usbrip活动，参见参考资料+usbrip/cron/usbrip.cron）;
>
> /var/opt/usbrip/trusted/ - 可信USB设备列表（在安装过程中创建）;
>
> /usr/local/bin/usbrip- /opt/usbrip/venv/bin/usbrip脚本的符号链接。

###  **CronCron作业可以设置如下：**

    
    
     ~/usbrip$ sudo crontab -l > tmpcron && echo “” >> tmpcron
    
     ~/usbrip$ cat usbrip/cron/usbrip.cron | tee -a tmpcron
    
     ~/usbrip$ sudo crontab tmpcron
    
     ~/usbrip$ rm tmpcron

###
**截图**![](https://image.3001.net/images/20190806/1565066168_5d4903b833c38.png!small)![](https://image.3001.net/images/20190806/1565066187_5d4903cbcbc82.png!small)

 ***本文作者：线性代数lzh，转载请注明来自FreeBuf.COM**  

