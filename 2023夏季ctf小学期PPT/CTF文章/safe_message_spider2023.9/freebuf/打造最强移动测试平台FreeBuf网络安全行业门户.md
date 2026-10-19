笔者今年换掉了服役N年的旧手机，新手机12G的RAM，比自用的本子内存都大，如果只是玩游戏感觉不能完全发挥出全部机能，但又因为怕影响日常使用没有进行root，经过一番折腾，发现即使不root也不影响把它变成一款测试利器，有同类需求的可以参考此文。

![](https://image.3001.net/images/20200806/1596677940.jpg!small)

## 安卓虚拟机

移动应用测试肯定是需要一个root环境，很多人选择用安卓模拟器，笔者为了使用WSL2启用了Hyper-V，导致与绝大多数的安卓模拟器冲突，从此告别安卓模拟器。笔者也尝试用了VirtualXposed、太极等免root的Xposed框架，发现兼容性不是太好，app容易闪退崩溃。后来发现安卓平台也有虚拟机，目前共有VMOS、光速虚拟机、X8沙箱三款产品。其中VMOS分普通版和Pro版，Pro版非会员支持选择ROM，也可以导入网友提供的ROM，其他虚拟机皆内置ROM无法修改。

经过笔者一番测试，对比如下

| VMOS| VMOS PRO| 光速虚拟机| X8沙箱  
---|---|---|---|---  
内存占用| 186MB| 233MB| 188MB| 181MB  
提供root| 提供| 提供| 提供| 提供  
提供XP| 提供| 提供| 不支持| 提供  
提供Play| 提供| 提供| 提供| 无  
程序兼容| 差| 好| 好| 好  
安卓版本| 5.1.1| 5.1.1 / 7.1.2| 7.1.2| 5.1.1  
是否含广告| 是| 是| 无| 视频广告  
权限要求| 电话、位置、相机、录音、存储| 无| 电话、位置、存储、录音、| 存储  
  
综合来说，光速虚拟机最快，干净无广告，遗憾的是目前版本不支持xposed框架，VMOS
Pro自带rom兼容性比较差，使用酷安网友提供的ROM兼容性较好，而且关闭所有应用权限也不影响虚拟机使用，很不错。

想一下手机里跑个虚拟的安卓系统，带root环境且与本机隔离，简直是移动测试的最佳方式。

下图是笔者四个虚拟机同时小窗开启的，独立互不冲突，加起来内存占用可能还不到1G，毫无压力。

![](https://image.3001.net/images/20200806/1596677861.jpg!small)

## Kali Nethunter

官方文档提供一种 **NetHunter Rootless**
的方式，即免root安装，同样也是支持KeX的，所以可以实现下图的效果，外接显示器获得完整的桌面体验。

![](https://image.3001.net/images/20200806/1596685142.png!small)

与其他版本的Nethunter差别参见下图，能够实现绝大部分功能。

Feature| NetHunter Rootless| NetHunter Lite| NetHunter  
---|---|---|---  
App Store| Yes| Yes| Yes  
Kali cli| Yes| Yes| Yes  
All Kali packages| Yes| Yes| Yes  
KeX| Yes| Yes| Yes  
Metasploit w/o DB| Yes| Yes| Yes  
Metasploit with DB| No| Yes| Yes  
NetHunter App| No| Yes| Yes  
Requires TWRP| No| Yes| Yes  
Requires Root| No| No| Yes  
WiFi Injection| No| No| Yes  
HID attacks| No| No| Yes  
  
主要原理基于Termux+Kex实现的，Termux真的是一款神器，一款不需要Root的神器，具体介绍参见国光前辈的文章[https://www.freebuf.com/geek/170510.html](../geek/170510.html)

NethunterRootless安装方法可以参考官方文档<https://www.kali.org/docs/nethunter/nethunter-rootless/>

建议termux通过f-droid下载<https://f-droid.org/packages/com.termux/>

实际效果如下图，具体就不展开讲了，国光大佬那篇文章写的很详细

![](https://image.3001.net/images/20200806/1596685243.jpg!small)

题外话，wsl2现在也支持kex了，效果如下图，美滋滋！<https://www.kali.org/docs/wsl/win-kex/>

![](https://image.3001.net/images/20200806/1596685193.png!small)![](https://image.3001.net/images/20200806/1596681667.png!small)

## Docker环境

虚拟的安卓有了，虚拟的kali有了，想搭靶机了，能不能有个Docker呢，答案是肯定的！

虽然Termux很强大，可以安装各种linux，但基于termux版linux还是不能运行Docker，需要Termux上装Qemu虚拟机，Qemu装alpine
linux，这个时候才是原汁原味的x86 linux。

这种套娃的操作可能会劝退不少人，幸运的是有人把Termux+Qemu+Alpine整合好了，名为alpine-term，开箱即用，安装一个apk打开就是配置完全的alpine
linux，项目地址为：<https://github.com/xeffyr/alpine-term/releases>

你需要做的只是手动装一个docker

    
    
    #更新apk软件源  
    apk update  
    #安装docker  
    apk add docker  
    #使docker开机启动  
    rc-update add docker  
    #开启docker服务  
    service docker start  
    #后台启动  
    setsid containerd  
    setsid dockerd

内置用户alpine初始配置存在一些限制，可以使用sudo -s 切换root用户操作。

docker起来后还需要手动配置下Qemu的网络映射，在termux导航栏选择QEMU，执行以下操作添加端口映射。

    
    
    #映射手机10022端口到虚拟机22端口  
    (qemu)hostfwd_add tcp::10022-:22  
    #删除到10022的端口映射  
    (qemu)hostfwd_remove tcp::10022  
    #查看端口映射和网络连接  
    (qemu)info usernet

详细帮助文档参见<https://xeffyr.github.io/alpine-term/docs/help.html>

## 代理抓包

最后推荐一个移动端的抓包工具HttpCanary，支持HTTP、HTTPS、HTTP2和WebSocket等多种协议。基于[NetBare](https://github.com/MegatronKing/NetBare)框架的虚拟网关-拦截器设计，可以非常方便的对单个app进行抓包、修改、重放等操作。完全脱离电脑对某个app进行抓包分析。详细使用可参考作者写的系列文章<https://juejin.im/post/6844903745562607624>

## 结束

到这里本文就结束了，希望能起到抛砖引玉的效果，如果你还有更好用的移动平台安全工具，欢迎在评论区补充。

