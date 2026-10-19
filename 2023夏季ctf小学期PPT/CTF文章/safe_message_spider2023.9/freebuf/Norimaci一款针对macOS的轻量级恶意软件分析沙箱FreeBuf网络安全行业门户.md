![](https://image.3001.net/images/20220706/1657104357_62c567e5060b923e564a1.png!small)

## 关于Norimaci

Norimaci是一款针对macOS的轻量级恶意软件分析沙箱，Norimaci使用了OpenBSM和Monitor.app的功能来监控macOS操作系统的活动（没有使用Sysinternals进程监视器procmon。在该工具的帮助下，广大研究人员可以轻松监控macOS下的恶意软件活动情况。

Norimaci主要由下列三个Python脚本组成：

> norimaci.py : 主功能脚本
>
> openbsmconv.py : OpenBSM审计日志转换器
>
> monitorappconv.py : Monitor.app日志转换器

[ _OpenBSM_](http://www.trustedbsd.org/openbsm.html)是一个专门用于审计macOS互动的框架，而[
_Monitor_
_.app_](https://www.fireeye.com/services/freeware/monitor.html)这是FireEye开发的一款免费工具。

## 工具要求

> OS X 10.6或更高版本（已在macOS 10.13 - 10.15上进行过测试）
>
> VMware Fusion、Parallels、VirtualBox等
>
> Python 3.5或更高版本
>
> [ _Monitor_
> _.app_](https://www.fireeye.com/services/freeware/monitor.html)（可选）
>
> [ _py-applescript_](https://github.com/rdhyee/py-applescript)
>
> [ _PyObjC_](https://bitbucket.org/ronaldoussoren/pyobjc)
>
> [ _dnslib_](https://bitbucket.org/paulc/dnslib/)

## 准备工作

### 构建虚拟机来执行恶意软件

我们需要构建一个macOS虚拟机来执行恶意软件样本。除此之外，我们建议构建另一个虚拟机来建立伪造的网络连接。此时可以使用PolarProxy和INetSim可以提供伪造的HTTP/HTTPS以及DNS服务。

### 编辑/etc/security/audit_control

如果你使用OpenBSM来监控系统活动，则需要按照下列方式修改/etc/security/audit_control文件：

    
    
    #
    
    # $P4: //depot/projects/trustedbsd/openbsm/etc/audit_control#8 $
    
    #
    
    dir:/var/audit
    
    flags:lo,aa,fc,fd,pc,nt,ex      <- edit here like this
    
    minfree:5
    
    naflags:lo,aa,fc,fd,pc,nt,ex    <- edit here like this
    
    policy:cnt,argv
    
    filesz:2M
    
    expire-after:10M
    
    superuser-set-sflags-mask:has_authenticated,has_console_access
    
    superuser-clear-sflags-mask:has_authenticated,has_console_access
    
    member-set-sflags-mask:
    
    member-clear-sflags-mask:has_authenticated

## 工具安装

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/mnrkbys/norimaci.git

## 工具使用

### 结合OpenBSM使用

> 1、使用sudo运行norimaci.py；
>
> 2、运行恶意软件样本；
>
> 3、等待一会儿...；
>
> 4、适当的时候在Norimaci运行的终端窗口中按下Ctrl+C；
>
>
> 5、此时将生成两类报告，即Norimaci_dd_Mon_yy__hh_mm_ffffff.txt和Norimaci_dd_Mon_yy__hh_mm_ffffff_timeline.csv；
>
> 6、确认报告可用；
    
    
    $ sudo python3 ./norimaci.py -m openbsm -o ./out/
    
    Password:
    
     
    
    --===[ Norimaci v0.1.0
    
    --===[ Minoru Kobayashi [@unkn0wnbit]
    
    [*] Launching OpenBSM agent...
    
    [*] When runtime is complete, press CTRL+C to stop logging.
    
    ^C
    
    [*] Termination of OpenBSM agent commencing... please wait
    
    [*] Converting OpenBSM data ...
    
    [*] Loading converted macOS activity data ...
    
    [*] Saving report to: /Users/macforensics/tools/norimaci/out/Norimaci_14_Jan_20__15_55_093219.txt
    
    [*] Saving timeline to: /Users/macforensics/tools/norimaci/out/Norimaci_14_Jan_20__15_55_093219_timeline.csv

### 结合Monitor.app使用

注意：Monitor.app无法在macOS 10.15上运行，但支持macOS 10.14及之前版本。

> 1、使用sudo运行norimaci.py；
>
> 2、Norimaci启动Monitor.py后输入密码，因为Monitor.app需要密码来安装它的kext文件；
>
> 3、运行一个恶意软件样本；
>
> 4、等待一段时间...；
>
> 5、适当的时候在Norimaci运行的终端窗口中按下Ctrl+C；
>
>
> 6、此时将生成两类报告，即Norimaci_dd_Mon_yy__hh_mm_ffffff.txt和Norimaci_dd_Mon_yy__hh_mm_ffffff_timeline.csv；
>
> 7、确认报告可用；

## 脚本帮助信息

### norimaci.py

    
    
    $ python3 ./norimaci.py -h
    
     
    
    --===[ Norimaci v0.1.0
    
    --===[ Minoru Kobayashi [@unkn0wnbit]
    
    usage: norimaci.py [-h] [-m MONITOR] [-j JSON] [-bl OPENBSM_LOG] [-p PROCLIST]
    
                       [-ml MONITORAPP_LOG] [-o OUTPUT] [--force] [--debug]
    
     
    
    Light weight sandbox which works with OpenBSM or Fireeye's Monitor.app
    
     
    
    optional arguments:
    
      -h, --help            show this help message and exit
    
      -m MONITOR, --monitor MONITOR
    
                            Specify a program to monitor macOS activity. You can
    
                            choose 'openbsm' or 'monitorapp'.
    
      -j JSON, --json JSON  Path to a JSON file which is converted by
    
                            'openbsmconv.py' or 'monitorappconv.py'.
    
      -bl OPENBSM_LOG, --openbsm-log OPENBSM_LOG
    
                            Path to an OpenBSM log file.
    
      -p PROCLIST, --proclist PROCLIST
    
                            Path to a process list file to process OpenBSM log
    
                            file. A file which has ".proclist" extnsion would be
    
                            used, if this option is not specified.
    
      -ml MONITORAPP_LOG, --monitorapp-log MONITORAPP_LOG
    
                            Path to a Monitor.app data file.
    
      -o OUTPUT, --output OUTPUT
    
                            Path to an output directory.
    
      --force               Enable to overwrite output files.
    
      --debug               Enable debug mode.

### openbsmconv.py

    
    
    $ python3 ./openbsmconv.py -h
    
    usage: openbsmconv.py [-h] [-f FILE] [-p PROCLIST] [-o OUT] [-c] [-rp]
    
                          [--with-failure] [--with-failure-socket] [--force]
    
                          [--debug]
    
     
    
    Converts OpenBSM log file to JSON format.
    
     
    
    optional arguments:
    
      -h, --help            show this help message and exit
    
      -f FILE, --file FILE  Path to a bsm log file
    
      -p PROCLIST, --proclist PROCLIST
    
                            Path to a process list file
    
      -o OUT, --out OUT     Path to an output file
    
      -c, --console         Output JSON data to stdout.
    
      -rp, --use-running-proclist
    
                            Use current running process list instead of a existing
    
                            process list file. And, the process list is saved to a
    
                            file which places in the same directory of '--file' or
    
                            to a file which specified '--proclist'.
    
      --with-failure        Output records which has a failure status too.
    
      --with-failure-socket
    
                            Output records which has a failure status too (related
    
                            socket() syscall only).
    
      --force               Enable to overwrite an existing output file.
    
      --debug               Enable debug mode.

### monitorappconv.py

    
    
    $ python3 ./monitorappconv.py -h
    
    usage: monitorappconv.py [-h] [-f FILE] [-o OUT] [-c] [--force] [--debug]
    
     
    
    Parses data of Fireeye Monitor.app and converts it to JSON format. Please note
    
    that strings in JSON data are saved as UTF-8.
    
     
    
    optional arguments:
    
      -h, --help            show this help message and exit
    
      -f FILE, --file FILE  Path to a saved data of Monitor.app.
    
      -o OUT, --out OUT     Path to an output file.
    
      -c, --console         Output JSON data to stdout.
    
      --force               Enable to overwrite an output file.
    
      --debug               Enable debug mode.

## 工具使用演示

![](https://image.3001.net/images/20220706/1657104485_62c568657f6e4a6d413ac.gif)

## 许可证协议

本项目的开发与发布遵循[ _Apache_ _-2_ _._
_0_](http://www.apache.org/licenses/LICENSE-2.0)开源许可证协议。

## 项目地址

 **Norimaci** ：【[ _GitHub传送门_](https://github.com/mnrkbys/norimaci)】

## 参考资料

> [ _https://github.com/Rurik/Noriben_](https://github.com/Rurik/Noriben)
>
> [
> _http://www.trustedbsd.org/openbsm.html_](http://www.trustedbsd.org/openbsm.html)
>
> [
> _https://www.fireeye.com/services/freeware/monitor.html_](https://www.fireeye.com/services/freeware/monitor.html)
>
> [ _https://github.com/rdhyee/py-applescript_](https://github.com/rdhyee/py-> applescript)
>
> [
> _https://bitbucket.org/ronaldoussoren/pyobjc_](https://bitbucket.org/ronaldoussoren/pyobjc)
>
> [
> _https://bitbucket.org/paulc/dnslib/_](https://bitbucket.org/paulc/dnslib/)
>
> [ _https://www.netresec.com/?page=Blog &month=2019-12&post=Installing-a-> Fake-Internet-with-INetSim-and-> PolarProxy_](https://www.netresec.com/?page=Blog&month=2019-12&post=Installing-> a-Fake-Internet-with-INetSim-and-PolarProxy)

