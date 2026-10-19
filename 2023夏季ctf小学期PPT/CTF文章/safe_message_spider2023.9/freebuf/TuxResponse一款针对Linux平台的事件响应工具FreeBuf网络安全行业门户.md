![](https://image.3001.net/images/20200111/1578724579_5e196ce38e698.png!small)

##  TuxResponse

**TuxResponse是一款采用Bash语言开发编写的专门针对Linux系统平台的事件响应脚本。它可以在Linux系统上以自动化的形式执行各种事件响应任务，以帮助安全分析人员快速对系统中的安全应急事件进行分类，同时不会影响最终的处理结果。当然了，通常情况下公司或企业的系统中都会部署一些安全监视和控制软件，但由于存在各种非标准镜像以及其他网络组件，因此TuxResponse便应运而生。在TuxResponse的帮助下，研究人员只需按一下按钮，就可以完成10个命令的输入和测试。**

当前版本的TuxResponse已在Ubuntu 14+和CentOS 7+上进行了测试。

##  功能特性

> 1、利用了Linux的内置工具以及各种功能，其中包括但不限于dd、awk、grep、cat和netstat等。
>
> 2、减少了事件响应工具所需的命令数量。
>
> 3、自动化任务实现。

除了Linux内置工具即功能组件之外，TuxResponse还引入了下列外部工具包：

> -LiME
>
> -Exif
>
> -Chckrootkit
>
> -Yara + Linux扫描规则

##  工具下载

广大用户可以直接使用下列命令将项目代码克隆至本地:

    
    
    git clone https://github.com/la3ar0v/TuxResponse.git

##  工具使用样例

    
    
    INSTALL LiME
    
        function init_lime(){
    
          if [ -f /usr/bin/yum ]; then
    
            yum -y install make kernel-headers kernel-devel gcc
    
          elif [ -f /usr/bin/apt-get ]; then
    
            apt-add-repository universe
    
            apt-get -y install make linux-headers-$(uname -r) gcc
    
          fi
    
          rm -f /tmp/v1.8.1.zip
    
          wget -P/tmp https://github.com/504ensicsLabs/LiME/archive/v1.8.1.zip
    
          unzip /tmp/v1.8.1.zip
    
          rm -f /tmp/v1.8.1.zip
    
          pushd LiME-1.8.1/src
    
            make
    
            mv lime-*.ko /tmp/lime.ko
    
          popd
    
          rm -rf LiME-1.8.1
    
        }

在对某个安全事件进行应急响应处理时，如果你还要手动输入所有命令来安装LiME的话，肯定会花费你大量的时间，这样一来效率就非常低了。

##  功能介绍

###  一、实时响应

**（1）足迹系统**

    
    
    System info, IP, Date, Time, local TZ, last boot - 'hostnamectl; who -b; uname -a; uptime; ifconfig; date; last reboot'

**（2）文件系统工具**

    
    
     'df -h'：检查已加载的文件系统 -    
        'find /usr/bin -type f -exec file "{}" \; | grep -i "elf" | cut -f1 -d: | xargs -I "{}" -n 1 md5sum {}'：可执行文件哈希 (MD5)  
    
        'modified_files_period_select' (调用tuxresponse.sh中的函数)：修改文件
    
        'find / -type d -name "\.*"'：枚举所有的隐藏目录
    
        'find / \( -nouser -o -nogroup \) -exec ls -l {} \; 2>/dev/null'：枚举无用户/组名的文件/目录
    
        'packaged_files_changed' (calling a function in tuxresponse.sh)：修改包内文件

**（3）YARA, CHKROOTKIT, EXIFTool**

    
    
     'chkrootkit'：检查rootkits 
    
        'yara_select'：Yara扫描
    
        'exiftool_select'：EXIFTool

**（4）处理分析工具**

    
    
     'ps -axu'：枚举运行进程
    
        'ls -alR /proc/*/exe 2> /dev/null | grep deleted'：删除仍在运行的代码
    
        'ss -tunap | sed "s/[ \t]\+/|/g"'：活动网络连接-TCP或UDP
    
        'dump_process_select'：根据PID导出进程信息
    
        'ls -alR /proc/*/cwd 2> /dev/null | grep -E "tmp|dev"'：从/tmp或/dev运行进程

**（5）网络连接分析**

    
    
    'netstat -nalp; netstat -plant'：枚举所有活动的网络连接/元套接字

**（6）用户**

> 'w' ：枚举当前接入的用户
>
> 'getent passwd'：使用密码获取用户信息

**（7）Bash**

    
    
    'cat ~/.bash_history | nl'：检查Bash历史文件

**（8）持久化痕迹**

    
    
     'list_all_crontab'：枚举所有的Cron任务
    
        'list_all_onstartup'：枚举所有的自启动程序

**（9）导出所有日志（/var/log）**

    
    
     'cat_all_bash_history'：导出用户的.bash_history
    
        'grep [[:cntrl:]] /var/log/*.log'：查找日志

###  二、建立连接，使用SSH传输脚本并分析远程系统

该选项允许您连接到远程系统，复制所有脚本和工具并分析系统。

###  三、导出内存（LKM LiME）

该选项可以让我们从源代码处编译LiME，并将RAM内存转储到系统之外，这是最简单的方法。因为另一种方法是从源代码编译所有主要内核版本，并插入LKM。

###  四、获取磁盘镜像（DD）

该选项可以帮助我们使用著名的工具-dd来获取目标系统的完整磁盘映像。该函数将源地址和目的地址作为参数，并将它们插入以下命令之中：

    
    
    'dd if=${image_in}pv | dd of='${image_OUT}'bs=4K conv=noerror，sync'

如果您正在调查和分析一个远程系统，那么脚本首先会在远程系统中进行自我复制。如果你设置了参数${TARGET_HOST}，那么脚本将使用以下命令将镜像下载到分析系统中

    
    
    >>“ssh-p${TARGET_PORT}${TARGET_USER}@${TARGET_HOST}”dd if=${image_IN}bs=4K conv=noerror，sync'{pv|dd of='${image_OUT}'

注意：pv的使用可以帮助我们跟踪进度。

###  五、生成HTML报告

我们所有的操作记录以及分析结果都将存储在一个文本文件中，因此我们可以轻松返回并查看输出。这样做的好处是，我们可以将它上传到任何一个日志分析工具中，并在后期加以解析。除此之外，我们还可以使用该函数来生成HTML格式的分析报告，并以可读性更高的形式查看工具生成的事件响应结果。

##  项目地址

> TuxResponse：【[GitHub传送门](https://github.com/la3ar0v/TuxResponse)】

 ***
参考来源：[la3ar0v](https://github.com/la3ar0v/TuxResponse)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

