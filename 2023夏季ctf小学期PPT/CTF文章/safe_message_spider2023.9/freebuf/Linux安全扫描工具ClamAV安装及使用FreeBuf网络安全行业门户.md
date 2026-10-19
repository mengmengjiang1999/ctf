# 导语

Clam
AntiVirus（ClamAV）是免费而且开放源代码的防毒软件，软件与病毒码的更新皆由社群免费发布。ClamAV在命令行下运行，它不将杀毒作为主要功能，默认只能查出系统内的病毒，但是无法清除。需要用户自行对病毒文件进行处理。

我们可以到ClamAV官网http://www.clamav.net/download.html下载最新版安装包安装，也可以使用linux系统自带安装包进行安装。

# centos系统安装步骤

1、执行 yum install clamav-server clamav-data clamav-update clamav-filesystem
clamav clamav-scanner-systemd clamav-devel clamav-lib clamav-server-systemd -y

2、安装完成后执行freshclam命令更新病毒库

 **ubuntu系统安装步骤**

1、执行 apt-get install clamav -y

2、安装完成后执行freshclam命令更新病毒库

# 扫描病毒

如果不知道病毒所处位置，使用命令clamscan -r / 命令进行全盘扫描，注意全盘扫描对系统资源消耗较大，耗时较长，建议在系统业务低峰时使用。

也可以针对某个路径进行扫描，如clamscan -r /usr/lib命令仅扫描/usr/lib路径下的文件和目录。

clamscan -r -i /lib

命令仅列出/lib目录下扫描发现的有问题的文件名称和病毒类型，如图

![1683785720_645c87f839a553f8236c2.png!small](https://image.3001.net/images/20230511/1683785720_645c87f839a553f8236c2.png!small)

如果不使用-i参数，则会输出目录下所有文件的扫描结果，如图（如果文件较多不易快速发现问题文件，所以建议使用-i参数）

![1683785730_645c8802f1bd85207d949.png!small](https://image.3001.net/images/20230511/1683785730_645c8802f1bd85207d949.png!small)

如果不使用-r参数，则只扫描指定路径下的文件，对于目录和子目录不做递归扫描，如图：

![1683785743_645c880f98d34a62ce34d.png!small](https://image.3001.net/images/20230511/1683785743_645c880f98d34a62ce34d.png!small)

