![](https://image.3001.net/images/20210914/1631619934_61408b5e6ba403d3ef0d9.png!small)

## 关于REW-sploit

 **REW-sploit是一款功能强大的攻击分析工具** ，它可以帮助我们 **分析Windows
Shellcode或其他来自Metasploit/Cobalt Strike的攻击活动。**

不仅如此，REW-sploit还可以帮助广大研究人员 **检测其他恶意代码或经过混淆处理的代码** 。

REW-sploit还可以 **使用简单的脚本代码来自动化分析任务** 。除此之外，REW-sploit甚至可以从Payload中提取密钥以解密那些由MSF生成的加密流量。

REW-sploit基于很多现有的优秀框架实现其功能，比如说Unicorn和speakeasy-emulator等等。总而言之， **REW-sploit就是为蓝队研究人员设计的** ，可以帮助广大研究人员在分析攻击活动的过程中提供帮助。

## 功能支持

REW-sploit可以获取Shellcode/DLL/EXE，模拟恶意代码的执行，并给我们提供关于当前安全现状的信息。支持提取的信息包括：

> API调用
>
> MSF Payload所使用的加密密钥
>
> 解密来自MSF的流量
>
> Cobalt-Strike配置（需安装[ _Cobalt-Strike解析器_](https://github.com/Sentinel-> One/CobaltStrikeParser)）

## 工具安装

REW-sploit安装过程非常简单，我们强烈建议大家在Python虚拟环境中使用该工具。

 **安装命令如下：**

    
    
    # python -m venv <your-env-path>/rew-sploit
    
    # source <your-env-path>/bin/activate
    
    # git clone https://github.com/REW-sploit/REW-sploit.git
    
    # cd REW-sploit
    
    # pip install -r requirements.txt
    
    # ./apply_patch.py -f
    
    # ./rew-sploit

如果你习惯使用Docker的话，大家也可以使用Dockerfile来创建REW-sploit镜像：

    
    
    docker build -t rew-sploit/rew-sploit .

接下来，使用下列命令启动REW-sploit：

    
    
    docker run --rm -it --name rew-sploit -v /tmp:/tmp rew-sploit/rew-sploit

安装过程中你将会看到一个名为apply_patch.py的脚本，这个脚本是一个针对[ _speakeasy-emulator_](https://github.com/fireeye/speakeasy/)的修复脚本，可以实现跟REW-sploit的兼容。

【可选项】你还可以安装Cobalt Stike解析器：

    
    
    # cd REW-sploit/extras
    
    # git clone https://github.com/Sentinel-One/CobaltStrikeParser.git

## 自定义YARA规则

modules/emulate_rules.py文件中包含了可以用来拦截恶意代码中有趣部分的YARA谷子额，不过大家也可以根据自己的需要来创建自定义YARA规则：

    
    
    #
    
    # Payload Name: [MSF] windows/meterpreter/reverse_tcp_rc4
    
    # Search for  : mov esi,dword ptr [esi]
    
    #               xor esi,0x<const>
    
    # Used for    : this xor instruction contains the constant used to
    
    #               encrypt the lenght of the payload that will be sent as 2nd
    
    #               stage
    
    # Architecture: x32
    
    #
    
    yara_reverse_tcp_rc4_xor_32 = 'rule reverse_tcp_rc4_xor {                \
    
                                   strings:                                  \
    
                                       $opcodes_1 = { 8b 36                  \
    
                                                      81 f6 ?? ?? ?? ?? }    \
    
                                   condition:                                \
    
                                       $opcodes_1 }'

## 工具演示

 **视频地址：** 【[ _点我观看_](https://asciinema.org/a/ln8tkJH7bOhACFRMdnPmk2i1o)】

## 项目地址

 **REW-sploit：** 【[ _GitHub传送门_](https://github.com/REW-sploit/REW-sploit)】

## 参考资料

> [ _https://www.blackhat.com/us-21/arsenal/schedule/index.html#rew-sploit-> dissecting-metasploit-> attacks-24086_](https://www.blackhat.com/us-21/arsenal/schedule/index.html#rew-> sploit-dissecting-metasploit-attacks-24086)
>
> [ _https://github.com/REW-sploit/REW-sploit_docs_](https://github.com/REW-> sploit/REW-sploit_docs)
>
> [ _https://github.com/Sentinel-> One/CobaltStrikeParser_](https://github.com/Sentinel-One/CobaltStrikeParser)
>
> [
> _https://github.com/fireeye/speakeasy/﻿_](https://github.com/fireeye/speakeasy/)

