***本工具仅供技术分享、交流讨论，严禁用于非法用途**

![](https://image.3001.net/images/20190809/1565320862_5d4ce69ed2127.png!small)

 **usbrip（是“USB Ripper”的简写，而不是“USB
R.I.P.”）是一个带有CLI接口的开源取证工具，可用于跟踪/监控Linux机器上的USB设备连接事件（即USB事件历史记录，“已连接”和“已断开连接”事件）。**

## 描述

usbrip是纯Python
3编写的一个小软件（使用一些外部模块，参见[Dependencies/PIP](https://github.com/snovvcrash/usbrip#pip-packages)），它会通过解析Linux的日志文件（/var/log/syslog*or/var/log/messages*取决于发行版本）
来构建USB事件历史表格，其中可能包含的内容有：“已连接”（日期和时间），“User”，“VID”（供应商ID），“PID”（产品ID），“Product”，“制造商”，“序列号”，
“端口”和“断开连接”（日期和时间）。

此外，它还可以：

> 将收集到的信息导出为JSON转储文件；
>
> 生成一个授权（可信）USB设备列表作为JSON（称之为auth.json）;
>
> 基于auth.json搜索“违规事件”：显示（或生成另一个JSON）USB设备，这些设备出现在历史记录中但不会出现在auth.json中；
>
> *当使用-s标志安装时*创建加密存储（7zip存档）以在crontab调度程序的帮助下自动备份和积累USB事件；
>
> 根据特定USB设备的VID和/或PID搜索其他详细信息。

## 快速开始

usbrip可在[PyPI](https://pypi.org/project/usbrip/)下载和安装：

    
    
    $ pip3 install usbrip

## 截图

![40887882-e00d4d3a-6757-11e8-962c-c77331782b19.png](https://image.3001.net/images/20190809/1565320887_5d4ce6b709bcb.png!small)![40886876-46c349d6-6748-11e8-92cf-0b0790ea9505.png](https://image.3001.net/images/20190809/1565320898_5d4ce6c2e1401.png!small)

## Git Clone

为简单起见，让我们同意所有出现~/usbrip$前缀的命令都在~/usbrip目录中执行，该目录是由git clone创建的：

    
    
    ~$ git clone https://github.com/snovvcrash/usbrip.git usbrip && cd usbrip
    ~/usbrip$

## 依赖

usbrip仅适用于未修改的系统日志文件结构。因此，如果更改syslogs的格式（如，使用syslog-ng或rsyslog），它将无法解析USB历史记录。这就是为什么“Connected”和“Disconnected”字段的时间戳没有年份的原因。

## deb 包

> python3.6 (或更新) interpreter
>
> python3-venv
>
> p7zip-full（由storages模块使用）
    
    
    ~$ sudo apt install python3-venv p7zip-full -y

## PIP 包

usbrip使用以下外部模块：

> [terminaltables](https://github.com/Robpol86/terminaltables)
>
> [termcolor](https://pypi.org/project/termcolor)

## 手动

手动解析Python依赖关系（实际上并不需要pip或setup.py，可以自动化该过程，请参阅安装部分）创建虚拟环境（可选）并从内部运行pip：

    
    
    ~/usbrip$ python3 -m venv venv && source venv/bin/activate
    (venv) ~/usbrip$ pip install -r requirements.txt

或者你可以通过下面的[pipenv](https://github.com/pypa/pipenv)单行命令为你完成所有的工作：

    
    
    ~/usbrip$ pipenv install && pipenv shell

之后你就可以非常轻松的运行usbrip了：

    
    
    (venv) ~/usbrip$ python -m usbrip -h
    Or
    (venv) ~/usbrip$ python __main__.py -h

## 安装

有两种方法可以将usbrip安装到你的系统中：pip或setup.py。

## pip 或 setup.py

首先，usbrip是pip可安装的。这意味着在git
cloning了repo之后，你可以简单地启动pip安装过程，然后在终端的任何地方运行usbrip，如下所示：

    
    
    ~/usbrip$ python3 -m venv venv && source venv/bin/activate
    (venv) ~/usbrip$ pip install .
    
    (venv) ~/usbrip$ usbrip -h

或者，如果你想在本地解析Python依赖关系，请使用setup.py：

    
    
    ~/usbrip$ python3 -m venv venv && source venv/bin/activate
    (venv) ~/usbrip$ python setup.py install
    
    (venv) ~/usbrip$ usbrip -h

 **注意：** 你可能希望在Python虚拟环境处于活动状态时运行安装过程（如上所示）。

## install.sh

其次，usbrip也可以使用./installers/install.sh脚本安装到系统中。

当使用./installers/install.sh时，可以使用一些额外的功能：

> 自动创建虚拟环境；
>
> 存储模块变为可用：你可以设置crontab job，按计划备份USB事件（你可以在usbrip/cron/usbrip.cron中找到crontab
> job的示例）。

 **警告：** 如果你使用的是crontab计划任务，则需要使用sudo crontab -e配置cron job，以强制storage
update子模块以root用户身份运行，并保护USB事件存储的密码。存储密码保存在/var/opt/usbrip/usbrip.ini中。

./installers/uninstall.sh脚本会从系统中删除所有安装项。

要安装usbrip命令如下：

    
    
    ~/usbrip$ chmod +x ./installers/install.sh
    ~/usbrip$ sudo -H ./installers/install.sh [-l/--local] [-s/--storages]
    ~/usbrip$ cd
    
    ~$ usbrip -h

启用-l开关后，将从本地.tar包（./3rdPartyTools/）而不是PyPI解析Python依赖项。

启用-s开关后，不仅会安装usbrip项目，还会创建受信任的USB设备，历史记录和违规存储列表。

 **注意：** 在安装期间使用-s选项时，请确保系统日志至少包含一个外部USB设备条目。这是usbrip成功创建受信任设备列表（并因此成功创建违规存储）的必要条件。

安装完成后，你可以删除usbrip文件夹。

 **路径**

安装后，usbrip的文件存放分布路径如下：

> /opt/usbrip/— 项目的主目录；
>
> /var/opt/usbrip/usbrip.ini—usbrip配置文件：保存7zip存储的密码；
>
> /var/opt/usbrip/storage/—USB事件存储：history.7z和violation.7z（在安装过程中创建）；
>
> /var/opt/usbrip/log/—
> usbrip日志（建议在使用crontab时记录usbrip活动，参见usbrip/cron/usbrip.cron）；
>
> /var/opt/usbrip/trusted/— 受信任USB设备列表（在安装过程中创建）；
>
> /usr/local/bin/usbrip— 符号链接（symlink）到/opt/usbrip/venv/bin/usbrip脚本。

 **cron**

Cron jobs可以设置如下：

    
    
    ~/usbrip$ sudo crontab -l > tmpcron && echo "" >> tmpcron
    ~/usbrip$ cat usbrip/cron/usbrip.cron | tee -a tmpcron
    ~/usbrip$ sudo crontab tmpcron
    ~/usbrip$ rm tmpcron

 **uninstall.sh**

卸载usbrip：

    
    
    ~/usbrip$ chmod +x ./installers/uninstall.sh
    ~/usbrip$ sudo ./installers/uninstall.sh [-a/--all]

> 启用-a开关后，不仅会删除usbrip项目目录，还会删除所有存储和usbrip日志。  
>

还有就是不要忘记删除cron job。

## 使用

    
    
    # ---------- BANNER ----------    
    $ usbrip banner
    Get usbrip banner.
    
    # ---------- EVENTS ----------    
    $ usbrip events history [-t | -l] [-e] [-n <NUMBER_OF_EVENTS>] [-d <DATE> [<DATE> ...]] [--user <USER> [<USER> ...]] [--vid <VID> [<VID> ...]] [--pid <PID> [<PID> ...]] [--prod <PROD> [<PROD> ...]] [--manufact <MANUFACT> [<MANUFACT> ...]] [--serial <SERIAL> [<SERIAL> ...]] [--port <PORT> [<PORT> ...]] [-c <COLUMN> [<COLUMN> ...]] [-f <FILE> [<FILE> ...]] [-q] [--debug]
    Get USB event history.
    
    $ usbrip events open <DUMP.JSON> [-t | -l] [-e] [-n <NUMBER_OF_EVENTS>] [-d <DATE> [<DATE> ...]] [--user <USER> [<USER> ...]] [--vid <VID> [<VID> ...]] [--pid <PID> [<PID> ...]] [--prod <PROD> [<PROD> ...]] [--manufact <MANUFACT> [<MANUFACT> ...]] [--serial <SERIAL> [<SERIAL> ...]] [--port <PORT> [<PORT> ...]] [-c <COLUMN> [<COLUMN> ...]] [-f <FILE> [<FILE> ...]] [-q] [--debug]
    Open USB event dump.
    
    $ usbrip events gen_auth <OUT_AUTH.JSON> [-a <ATTRIBUTE> [<ATTRIBUTE> ...]] [-e] [-n <NUMBER_OF_EVENTS>] [-d <DATE> [<DATE> ...]] [--user <USER> [<USER> ...]] [--vid <VID> [<VID> ...]] [--pid <PID> [<PID> ...]] [--prod <PROD> [<PROD> ...]] [--manufact <MANUFACT> [<MANUFACT> ...]] [--serial <SERIAL> [<SERIAL> ...]] [--port <PORT> [<PORT> ...]] [-f <FILE> [<FILE> ...]] [-q] [--debug]
    Generate a list of trusted (authorized) USB devices.
    
    $ usbrip events violations <IN_AUTH.JSON> [-a <ATTRIBUTE> [<ATTRIBUTE> ...]] [-t | -l] [-e] [-n <NUMBER_OF_EVENTS>] [-d <DATE> [<DATE> ...]] [--user <USER> [<USER> ...]] [--vid <VID> [<VID> ...]] [--pid <PID> [<PID> ...]] [--prod <PROD> [<PROD> ...]] [--manufact <MANUFACT> [<MANUFACT> ...]] [--serial <SERIAL> [<SERIAL> ...]] [--port <PORT> [<PORT> ...]] [-c <COLUMN> [<COLUMN> ...]] [-f <FILE> [<FILE> ...]] [-q] [--debug]
    Get USB violation events based on the list of trusted devices.
    
    # ---------- STORAGE ----------    
    $ usbrip storage list <STORAGE_TYPE> [-q] [--debug]
    List contents of the selected storage (7zip archive). STORAGE_TYPE is "history" or "violations".
    
    $ usbrip storage open <STORAGE_TYPE> [-t | -l] [-e] [-n <NUMBER_OF_EVENTS>] [-d <DATE> [<DATE> ...]] [--user <USER> [<USER> ...]] [--vid <VID> [<VID> ...]] [--pid <PID> [<PID> ...]] [--prod <PROD> [<PROD> ...]] [--manufact <MANUFACT> [<MANUFACT> ...]] [--serial <SERIAL> [<SERIAL> ...]] [--port <PORT> [<PORT> ...]] [-c <COLUMN> [<COLUMN> ...]] [-q] [--debug]
    Open selected storage (7zip archive). Behaves similary to the EVENTS OPEN submodule.
    
    $ usbrip storage update <STORAGE_TYPE> [-a <ATTRIBUTE> [<ATTRIBUTE> ...]] [-e] [-n <NUMBER_OF_EVENTS>] [-d <DATE> [<DATE> ...]] [--user <USER> [<USER> ...]] [--vid <VID> [<VID> ...]] [--pid <PID> [<PID> ...]] [--prod <PROD> [<PROD> ...]] [--manufact <MANUFACT> [<MANUFACT> ...]] [--serial <SERIAL> [<SERIAL> ...]] [--port <PORT> [<PORT> ...]] [--lvl <COMPRESSION_LEVEL>] [-q] [--debug]
    Update storage — add USB events to the existing storage (7zip archive). COMPRESSION_LEVEL is a number in [0..9].
    
    $ usbrip storage create <STORAGE_TYPE> [-a <ATTRIBUTE> [<ATTRIBUTE> ...]] [-e] [-n <NUMBER_OF_EVENTS>] [-d <DATE> [<DATE> ...]] [--user <USER> [<USER> ...]] [--vid <VID> [<VID> ...]] [--pid <PID> [<PID> ...]] [--prod <PROD> [<PROD> ...]] [--manufact <MANUFACT> [<MANUFACT> ...]] [--serial <SERIAL> [<SERIAL> ...]] [--port <PORT> [<PORT> ...]] [--lvl <COMPRESSION_LEVEL>] [-q] [--debug]
    Create storage — create 7zip archive and add USB events to it according to the selected options.
    
    $ usbrip storage passwd <STORAGE_TYPE> [--lvl <COMPRESSION_LEVEL>] [-q] [--debug]
    Change password of the existing storage.
    
    # ---------- IDs ----------    
    $ usbrip ids search [--vid <VID>] [--pid <PID>] [--offline] [-q] [--debug]
    Get extra details about a specific USB device by its <VID> and/or <PID> from the USB ID database.
    
    $ usbrip ids download [-q] [--debug]
    Update (download) the USB ID database.

## Help

获取模块名称列表：

    
    
    $ usbrip -h

获取特定模块的子模块名称列表：

    
    
    $ usbrip <module> -h

获取特定子模块的所有开关列表：

    
    
    $ usbrip <module> <submodule> -h

## 示例

显示所有USB设备的事件历史记录，banner输出，信息消息和用户交互（-q，--quiet），（-l,--list）表示为列表包含最新的100个条目（
-n NUMBER，--number NUMBER）：

    
    
    $ usbrip events history -ql -n 100

显示外部USB设备的事件历史记录（-e，--external，实际上已断开连接），表示为包含“Connected”，“VID”，“PID”，“Disconnected”的表（-t，--table）
和“序列号”列（-c COLUMN [COLUMN],--column COLUMN [COLUMN]）按日期过滤从外部文件中获取的日志（-f FILE
[FILE ...],--file FILE [FILE ...]）：

    
    
    $ usbrip events history -et -c conn vid pid disconn serial -d "Dec  9" "Dec 10" -f /var/log/syslog.1 /var/log/syslog.2.gz

构建所有USB设备的事件历史记录，并将输出重定向到文件以进一步的分析。当输出流不是终端stdout（如 | 或
>）时，输出中将没有ANSI转义字符，因此可以随意使用它。另外需要注意的是，usbrip使用了一些UNICODE符号，因此将生成的文件转换为UTF-8编码（如使用encov），以及将换行符更改为Windows样式会更方便（如使用awk）。

    
    
    usbrip history events -t | awk '{ sub("$", "\r"); print }' > usbrip.out && enconv -x UTF8 usbrip.out

 **备注：** 即使已经将输出发送到stdout，也可以自己去掉转义字符。你只需将输出数据复制到usbrip.out并添加一条awk指令：

    
    
    awk '{ sub("$", "\r"); gsub("\\x1B\\[[0-?]*[ -/]*[@-~]", ""); print }' usbrip.out && enconv -x UTF8 usbrip.out

将受信任的USB设备列表生成为json文件（trusted/auth.json），其中包含9月26日连接的前三个设备的“VID”和“PID”属性：

    
    
    $ usbrip events gen_auth trusted/auth.json -a vid pid -n 3 -d "Sep 26"

 **警告：**
有时不同的USB闪存驱动器可能具有相同的序列号。到目前为止，usbrip还没有办法处理这种情况，也就是说它将把一对具有相同SN（如果存在）的设备视为与可信设备列表和gen_auth模块相同的设备。

根据“PID”属性的可信USB设备列表（trusted/auth.json）搜索外部USB设备的事件历史记录，并将结果事件限定为“Bob”作为用户，“EvilUSBManufacturer”为制造商，“1234567890”为序列号，并将输出表示为具有“Connected”，“VID”和“PID”列的表：

    
    
    $ usbrip events violations trusted/auth.json -a pid -et --user Bob --manufact EvilUSBManufacturer --serial 1234567890 -c conn vid pid

通过VID（--vid VID）和PID（--pid PID）搜索特定USB设备的详细信息：

    
    
    $ usbrip ids search --vid 0781 --pid 5580

下载最新版本的usb_ids/usb.ids数据库（源码可[在此处查看](http://www.linux-usb.org/usb.ids)）：

    
    
    $ usbrip ids download

## 参考文献

> [Linux-форензика в лице трекинга истории подключений USB-устройств /
> Хабр](https://habr.com/ru/post/352254/)
>
> [usbrip: USB-форензика для Линуксов, или Как Алиса стала
> Евой](https://codeby.net/threads/usbrip-usb-forenzika-dlja-linuksov-ili-kak-> alisa-stala-evoj.63644/)

***参考来源：[GitHub](https://github.com/snovvcrash/usbrip)，FB小编secist编译，转载请注明来自FreeBuf.COM**  

