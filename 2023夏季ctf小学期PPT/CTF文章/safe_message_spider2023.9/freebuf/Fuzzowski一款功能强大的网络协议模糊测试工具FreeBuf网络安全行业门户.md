![](https://image.3001.net/images/20200220/1582206825_5e4e8f6937dca.png!small)

##  Fuzzowski

**Fuzzowski的设计核心理念，就是想让任何一个网络安全从业人员都会第一选择去使用它，该工具可以帮助研究人员对网络协议进行模糊测试，并且能够在整个测试过程中给我们提供帮助。除此之外，该工具还允许研究人员定义链接，并帮助识别服务的崩溃。**

##  功能介绍

> 1、基于Sulley Fuzzer实现数据收集功能【[GitHub传送门](https://github.com/OpenRCE/sulley)】
>
> 2、基于BooFuzz部分功能【[GitHub传送门](https://github.com/jtpereyda/boofuzz)】
>
> 3、Python3
>
> 4、非随机性
>
> 5、需要指定创建数据包的类型（SPIKE fuzzer风格）
>
> 6、允许使用参数创建元数据包，可指定注入点
>
> 7、提供功能强大的命令行终端
>
> 8、允许跳过引起错误的参数
>
> 9、自动化
>
> 10、提供完整可视化的可疑数据包内容
>
> 11、可将PoC存储为Python脚本
>
> 12、提供监控模块帮助实现数据收集

##  协议实现

> 1、LPD(Line Printing Daemon)：完整实现
>
> 2、IPP (Internet Printing Protocol)：部分实现
>
> 3、BACnet(Building Automation&Control networks Protocol)：部分实现
>
> 4、Modbus(ICS communication protocol)：部分实现

![](https://image.3001.net/images/20200220/1582206842_5e4e8f7a05853.png!small)

##  工具安装

> virtualenv venv -p python3
>
> source venv/bin/activate
>
> pip install -r requirements.txt

###  工具使用帮助

> usage: python -m fuzzowski [-h] [-p {tcp,udp,ssl}] [-b BIND] [-st
> SEND_TIMEOUT]
>
> [-rt RECV_TIMEOUT] [--sleep-time SLEEP_TIME] [-nc] [-tn]
>
> [-nr] [-nrf] [-cr]
>
> [--threshold-request CRASH_THRESHOLD_REQUEST]
>
> [--threshold-element CRASH_THRESHOLD_ELEMENT]
>
> [--ignore-aborted] [--ignore-reset] [--error-fuzz-issues]
>
> [-c CALLBACK | --file FILENAME] -f
>
> {cops,dhcp,ipp,lpd,netconf,telnet_cli,tftp,raw}
>
> [-r FUZZ_REQUESTS [FUZZ_REQUESTS ...]]
>
> [--restart module_name [args ...]]
>
> [--restart-sleep RESTART_SLEEP_TIME]
>
> [--monitors {IPPMon} [{IPPMon} ...]] [--path PATH]
>
> [--document_url DOCUMENT_URL]
>
> host port
>
> █ █
>
> ████████
>
> ██████████
>
> ██ ████ ██
>
> ██ ████ ██
>
> ████ ████
>
> █ ████████████ █
>
> █ ██████████ █ Fuzzowski Network Fuzzer
>
> █ █ █ █ � Fuzzers, inc.
>
> ██ ██

位置参数:

> host 目的主机
>
> port 目的端口

可选参数:

> -h, --help 显示帮助信息与退出

连接参数:

> -p {tcp,udp,ssl}, --protocol {tcp,udp,ssl}
>
> 协议(默认为tcp)
>
> -b BIND, --bind BIND 端口绑定
>
> -st SEND_TIMEOUT, --send_timeout SEND_TIMEOUT
>
> 设置send() 超时(默认为5s)
>
> -rt RECV_TIMEOUT, --recv_timeout RECV_TIMEOUT
>
> 设置recv() 超时(默认为5s)
>
> \--sleep-time SLEEP_TIME
>
> 测试睡眠间隔 (默认为0)
>
> -nc, --new-conns 数据包测试后建林新的连接
>
> -tn, --transmit-next-node
>
> 发送模糊节点图中的下一个节点

崩溃选项:

> \--threshold-request CRASH_THRESHOLD_REQUEST
>
> 在跳过请求之前设置请求中允许的崩溃数 (默认为9999)
>
> \--threshold-element CRASH_THRESHOLD_ELEMENT
>
> 在跳过原语之前，设置该原语中允许的崩溃次数 (默认为3)
>
> \--ignore-aborted 忽略ECONNABORTED 错误
>
> \--ignore-reset 忽略ECONNRESET 错误
>
> \--error-fuzz-issues 当模糊节点中存在任何连接问题时作为错误记录

模糊测试选项:

> -c CALLBACK, --callback CALLBACK
>
> 用回调生成器将回调地址设置为fuzz而不是普通的突变
>
> \--file FILENAME 使用文件内容进行模糊变异

模糊测试器:

> -f {cops,dhcp,ipp,lpd,netconf,telnet_cli,tftp,raw}, --fuzz
> {cops,dhcp,ipp,lpd,netconf,telnet_cli,tftp,raw}
>
> 可用协议
>
> -r FUZZ_REQUESTS [FUZZ_REQUESTS ...], --requests FUZZ_REQUESTS
> [FUZZ_REQUESTS ...]
>
> 待测协议，默认为全部
>
> dhcp: [opt82]
>
> ipp: [http_headers, get_printer_attribs, print_uri_message, send_uri,
> get_jobs, get_job_attribs]
>
> lpd: [long_queue, short_queue, ctrl_file, data_file, remove_job]
>
> telnet_cli: [commands]
>
> tftp: [read]
>
> raw: ['\x01string\n' '\x02request2\x00' ...]

重启选项:

> \--restart module_name [args ...]
>
> 重启模块:
>
> run: '<executable> [<argument> ...]' smartplug: 开启或关闭smartplug
>
> teckin: <PLUG_IP>
>
> \--restart-sleep RESTART_SLEEP_TIME
>
> 设置崩溃后的睡眠秒数 (默认为5)

监控器选项:

> \--monitors {IPPMon} [{IPPMon} ...], -m {IPPMon} [{IPPMon} ...]
>
> 监控器模块:
>
> IPPMon: 向目标发送get-attributes IPP消息

其它选项:

> \--path PATH 设置基于HTTP的待测协议路径 (默认为/)
>
> \--document_url DOCUMENT_URL
>
> 为print_uri设置Document URL

##  工具使用样例

**使用默认参数，对get_printer_attribs IPP操作进行模糊测试：**

    
    
    python -m fuzzowski printer1 631 -f ipp -r get_printer_attribs --restart smartplug

演示视频：<https://asciinema.org/a/0RMDMrJWiFo4RoRwAjx61BXDY>

**使用IPP的元功能来对指纹协议（Finger Protocol）进行模糊测试：**

    
    
    python -m fuzzowski printer 79 -f raw -r '{{root}}\n'

演示视频：<https://asciinema.org/a/Pch0JbkNK97dgrCUMK8iIfJv5>

**使用IPP的元功能来对指纹协议（Finger Protocol）进行模糊测试，但使用的是一个文件：**

    
    
    python -m fuzzowski printer 79 -f raw -r '{{root}}\n' --file 'path/to/my/fuzzlist'

##  项目地址

> Fuzzowski：【[GitHub传送门](https://github.com/nccgroup/fuzzowski)】

 ***
参考来源：[nccgroup](https://github.com/nccgroup/fuzzowski)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

