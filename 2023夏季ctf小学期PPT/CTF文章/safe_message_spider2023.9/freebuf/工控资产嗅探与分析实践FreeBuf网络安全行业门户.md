*** 本工具仅供技术分享、交流讨论，严禁用于非法用途。**

1.本文章结合作者在平时工作中经历,对工控资产嗅探所使用的工具进行简单分析与验证，工控资产地址可以通过shodan、fofa、zoomeye等网站进行收集。

2.利用Nmap工具可以对S7、modbus的plc设备进行扫描探测

Nmap 6.4 脚本目录位于：/usr/share/nmap/scripts, 共有448个脚本 如下所示：

![](https://image.3001.net/images/20190729/1564399742_5d3ed87e8145c.png!small)

脚本分类如下：

![](https://image.3001.net/images/20190729/1564399749_5d3ed885b33ec.png!small)

脚本参数：

> -sC: 等价于 --script=default，使用默认类别的脚本进行扫描。
>
> \--script=<Lua scripts>: <Lua scripts>使用某个或某类脚本进行扫描，支持通配符描述
>
> \--script-args=<n1=v1,[n2=v2,...]>: 为脚本提供默认参数
>
> \--script-args-file=filename: 使用文件来为脚本提供参数
>
> \--script-trace: 显示脚本执行过程中发送与接收的数据
>
> \--script-updatedb: 更新脚本数据库
>
> \--script-help=<Lua scripts>: 显示脚本的帮助信息，其中<Luascripts>部分可以逗号分隔的文件或脚本类别。

脚本使用方式：

执行单个脚本：nmap --script /path/to/script.nse <target>

执行多个脚本：nmap --script /path/to/script.nse,/another/path/script2.nse <target>

执行文件夹包含的所有脚本：nmap --script/path/to/folder/ <target>

描述：探测modbus协议的设备

输入：nmap -sV --script modbus-discover 166.169.57.136 -p 502

输出：

![](https://image.3001.net/images/20190729/1564399758_5d3ed88e6f584.png!small)

描述：探测EthernetIP协议的设备

输入：nmap -p 44818 --script enip-enumerate.nse 221.206.153.114

输出：

![](https://image.3001.net/images/20190729/1564399763_5d3ed893e0945.png!small)

描述：探测CoDeSyS协议的设备

输入：nmap -p 1200,2455 --script codesys-v2-discover 178.242.1.44

输出：

![](https://image.3001.net/images/20190729/1564399770_5d3ed89a02620.png!small)

描述：探测NiagaraFox协议的设备

输入：nmap -p 1911 --script fox-info 67.176.19.167

输出：

![](https://image.3001.net/images/20190729/1564399776_5d3ed8a0c7195.png!small)

描述：探测S7协议的设备

输入：nmap -p 102 --script s7-enumerate.nse 79.135.33.188

输出：

![](https://image.3001.net/images/20190729/1564399786_5d3ed8aa3bf33.png!small)

...

其它工控组件如下，使用参考：<https://github.com/digitalbond/Redpoint#bacnet-discover-enumeratense>

![](https://image.3001.net/images/20190729/1564399799_5d3ed8b79ce01.png!small)

3.用plcscan工具可以对S7、modbus的plc设备进行扫描探测

S7协议plc设备探测

第一步：新建ip.list，将要扫描的ip写入其中

第二步：在plcscan目录下输入python plcscan.py --hosts-list=ip.list --ports=102命令进行扫描并观察结果

![](https://image.3001.net/images/20190729/1564399814_5d3ed8c6df04d.png!small)

备注：也可以通过输入python plcscan.py 178.139.130.34 --ports=102 进行指定ip扫描，如下图所示

![](https://image.3001.net/images/20190729/1564399822_5d3ed8ce94a0b.png!small)

modbus协议设备探测

第一步：新建ip.list，将要扫描的ip写入其中

第二步：在plcscan目录下输入python plcscan.py --hosts-list=ip.list --ports=502命令进行扫描并观察结果

![](https://image.3001.net/images/20190729/1564399857_5d3ed8f1636ac.png!small)

备注：也可以通过输入python plcscan.py 178.139.130.34 --ports=502 进行指定ip扫描，如下图所示

![](https://image.3001.net/images/20190729/1564399865_5d3ed8f951525.png!small)

nS7和modbus协议设备探测

第一步：新建ip.list，将要扫描的ip写入其中

第二步：在plcscan目录下输入python plcscan.py --hosts-list=ip.list 命令进行扫描并观察结果

![](https://image.3001.net/images/20190729/1564399872_5d3ed900150b7.png!small)

4.利用ISF工具对s7、cip、enip、profine-dcp协议工控设备进行资产探测

首先在isf目录下执行以下命令，并进入python环境，如下图所示：

![](https://image.3001.net/images/20190729/1564399878_5d3ed90692dc6.png!small)

S7

目标：扫描S7-300/S7-400设备(开放端口102)

第一步：输入 scanners/s7comm_scan 选择S7扫描插件

第二步：输入 show info 查看插件描述信息

第三步：输入 show options 查看插件使用信息

第四步：设定目标如set target ip

第五步：执行 run 命令开始扫描并查看扫描结果

操作过程如下图所示：

![](https://image.3001.net/images/20190729/1564399886_5d3ed90e2549b.png!small)

![](https://image.3001.net/images/20190729/1564399890_5d3ed912d56f1.png!small)

Vxworks6

目标：扫描vxworks 6.x 设备并且wdbrpc v2版本协议（开放端口17185）

目标：扫描Vxworks6设备

第一步：输入 scanners/vxworks_6_scan 选择vxworks扫描插件

第二步：输入 show info 查看插件描述信息

第三步：输入 show options 查看插件使用信息

第四步：设定目标如set target ip

第五步：执行 run 命令开始扫描并查看扫描结果

操作过程如下图所示：

![](https://image.3001.net/images/20190729/1564399899_5d3ed91bcde1c.png!small)

EnthernetIP

目标：扫描ethernetIP协议设备(开放端口44818)

第一步：输入 scanners/cip_scan 选择cip_scan扫描插件

第二步：输入 show info 查看插件描述信息

第三步：输入 show options 查看插件使用信息

第四步：设定目标如set target ip

第五步：执行 run 命令开始扫描并查看扫描结果

操作过程如下图所示：

![](https://image.3001.net/images/20190729/1564399907_5d3ed92351b4b.png!small)

![](https://image.3001.net/images/20190729/1564399913_5d3ed92944dd3.png!small)

 ***本文作者：yy0308，转载请注明来自FreeBuf.COM**

