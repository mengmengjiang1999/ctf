**rsGen是一款基于Widows BAT
&JS混编实现的多功能反弹shell命令生成器。不仅支持生成原生反弹shell命令，还支持生成“命令中转”形式的一句话反弹shell命令，以及包含端口监听(调用powercat.ps1)等功能。**  

“中转命令” ：类似于远控上线找IP，将命令上传至pastebin类网站，然后使用curl/wget/certutil等工具远程请求执行命令。

## 主要代码流程及功能模块注解

rsGen 90%以上功能基于Windows内置命令实现，代码大约500行左右，为免篇幅过长，以下仅解释主要流程及功能，详请可查看源码。

    
    
    ::main函数
    :rs_main_start
    ::基本参数判断
    if (
        ...
        call :xxx
        ...
        echo
        ...
    ) else (
        ...
        错误处理
        call :xxx
        ...
    )
    :rs_main_end
    
    ::功能模块
    ::==============================================================================================
    ::检测系统版本是否支持ANSI彩显
    :rs_os_detect_start
        ...
    :rs_os_detect_end
    
    ::检查host格式
    :rs_check_host_start
        ...
    :rs_check_host_end
    
    ::检查port格式
    :rs_check_port_start
        ...
    :rs_check_prot_end
    
    ::寻找未占用端口,LAN模式需要用到
    :rs_set_webport_start
        ...
    :rs_set_webport_end
    
    ::base64编码,调用内置命令certutil实现，用于生成命令编码。
    :rs_base64_encode_start
        ...
    :rs_base64_encode_ende
    
    ::清理临时文件,执行过程在Windows Temp目录生成两个.rsg结尾的临时文件，不清理也可以，系统会自动清理。
    :rs_clean_tempfile_start
        ...
    :rs_clean_tempfile_end
    
    ::原生命令RAW格式输出,提供ip和port两个参数输出。
    :rs_command_raw_start
        ...
    :rs_command_raw_end
    
    ::核心功能：局域网"中转命令"生成,即“-lan”参数功能
    :rs_command_lan_start
        ...
    :rs_command_lan_end
    
    ::核心功能：中转命令生成，即“-pub”参数功能
    :rs_command_generate_pub_end
        ...
        call :rs_command_upload_start
        ...
    :rs_command_generate_pub_end
    ::上传命令至pastebin，以供远程请求执行，内嵌JS混编，调用cscript.exe解释执行
    :rs_command_upload_start
        ...    
    :rs_command_upload_end
    
    ::banner输出
    :rs_banner_start
    echo                   ______  ________  ____  _____  
    echo                 .' ___  ^|^|_   __  ^|^|_   \^|_   _^| 
    echo   _ .--.  .--. / .'   \_^|  ^| ^|_ \_^|  ^|   \ ^| ^|   
    echo  [ `/'`\]( (`\]^| ^|   ____  ^|  _^| _   ^| ^|\ \^| ^|   
    echo   ^| ^|     `'.'.\ `.___]  ^|_^| ^|__/ ^| _^| ^|_\   ^|_  
    echo  [___]   [\__) )`._____.'^|________^|^|_____^|\____^|  v1.0
    goto :eof
    :rs_banner_end
    
    ::帮助信息
    :rs_help_start
    echo,
    echo  An Universal Reserve Shell Command Genrator.(Notice: You need to provide at least host and port parameters,that is your shell ip and port.)
    echo,
    echo Usage: %~nx0 host port [options]
    echo Options:
    echo   -pub       Upload to pastebin to generate relay command.
    echo   -lan       Generate command for LAN only and enable a web service locally
    echo   -listen    Generate command and listen the shell port.
    ::echo   -ngrok     Use public ngrok tunnel to receive the shell
    echo,
    echo Examples: %~nx0 192.168.31.216 8888
    echo           %~nx0 192.168.31.216 8888 -pub
    echo           %~nx0 192.168.31.216 8888 -lan
    echo           %~nx0 192.168.31.216 8888 -listen
    echo           %~nx0 192.168.31.216 8888 -lan -listen
    exit /b 0
    :rs_help_end

## 开始使用

rsGen默认至少需要提供用于反弹接收的IP和端口两个参数，如若不提供任何参数，默认输出帮助信息。

![image.png](https://image.3001.net/images/20190527/15589236354250.png!small)

仅生成原生格式反弹shell命令。

![image.png](https://image.3001.net/images/20190527/15589236285313.png!small)

-pub 参数，生成“中转命令”。   

PS：使用该参数，将执行命令上传，并将编码后的命令上传至公共pastebin网站(目前提供了两个接口：p.ip.fi和dpaste.com)。

![image.png](https://image.3001.net/images/20190527/15589236626742.png!small)

-lan 参数，用于有些情况下目标机器无法请求外网。

PS：该参数会同时调用command目录下mongoose.exe(一个迷你的web服务器，仅144kb，详见官网：<https://cesanta.com/>)，在本地80端口启用一个web服务，用于命令请求执行。工具使用完后，需要手动退出。

![image.png](https://image.3001.net/images/20190527/15589236863525.png!small)

-listen 参数，在本地启用端口监听，用于接收反弹回来的shell。

PS：在本地启用端口监听，用于接收反弹回来的shell，功能等同于netcat(调用powercat.ps1)。

![image.png](https://image.3001.net/images/20190527/15589237214135.png!small)

## 环境需求

一台Windows 7以上的操作系统。

## Q&A

### Q：你这个工具包含了网上最全的反弹shell的XX中方法吗？

A：并没有，本工具仅用于生成常用的反弹shell命令，以及“中转命令”，各种lua、perl、java等少见或反弹命令较长的暂时没有添加。

### Q：“命令中转”的意义是什么？

A：缩短原生命令，同时有效避免在碰到一些代码执行接口/命令盲执行等情况下，原生命令中特殊字符因URL转码/应用接口转码报错等未知因素导致的命令执行失败。

### Q：你这个工具测试环境是什么？支持Windows 2003和Windows XP吗？

A：（1）关于工具：测试环境我用的Windows10 和Windows
7，同时建议使用Widows10以获得较佳体验(Win10支持ANSI彩显，Win7未全部使用彩色输出)。Windows
XP及2003未做兼容，理论上也可以用，但是“中转命令”肯定废了，因为该功能部分调用powershell实现。

（2）关于生成的命令：目前不支持WinXP和Win2003，已在存在Thinkphp5.x代码执行的Windows Server
2012、存在weblogic反序列命令盲执行的Linux服务器、Struts命令执行等环境进行测试，均可快速获得shell。

## TODO

添加更多的反弹命令；

代码优化&BUG修复；

尝试添加类似ngrok公共服务器，用于无NAT映射、无VPS亦可轻松接收shell。

## 下载地址

Github传送门：<https://github.com/FlyfishSec/rsGen>

 ***本文作者：Flyfish，转载请注明来自FreeBuf.COM**

