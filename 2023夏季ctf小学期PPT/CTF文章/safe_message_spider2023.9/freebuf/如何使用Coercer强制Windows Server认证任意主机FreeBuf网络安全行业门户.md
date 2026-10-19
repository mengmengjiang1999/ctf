![](https://image.3001.net/images/20220913/1663036882_631fedd29976c66d5bb76.png!small)

## 关于Coercer

Coercer是一款功能强大的Python脚本，该工具可以通过九种不同的方法来强制让一台Windows Server认证任意主机。

## 功能介绍

> 1、自动检测远程设备的开放SMP管道；
>
> 2、一一调用存在安全漏洞的RPC功能来强制一台Windows Server认证任意主机；
>
> 3、支持使用--analyze参数开启分析模式，该模式只会枚举存在漏洞的协议和监听的函数，而不会执行强制认证；
>
> 4、支持使用--targets-file参数从文件读取需要执行强制认证的目标列表；
>
> 5、支持使用--webdav-host和--webdav-port针对WebDAV目标执行强制认证；

## 工具安装

由于该工具基于Python 3开发，因此我们首先需要在本地设备上安装并配置好Python 3环境。接下来，使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/p0dalirius/Coercer.git

除此之外，我们也可以使用[
_PyPi_](https://camo.githubusercontent.com/de6b4c68bd84dd5d67a60bac23feb82cb2fef75209139179b636a4167484dcd6/68747470733a2f2f696d672e736869656c64732e696f2f707970692f762f636f6572636572)来直接安装最新版本的Coercer：

    
    
    sudo python3 -m pip install coercer

## 工具使用

    
    
    $ ./Coercer.py -h                                                                                                  
    
     
    
           ______                              
    
          / ____/___  ___  _____________  _____
    
         / /   / __ \/ _ \/ ___/ ___/ _ \/ ___/
    
        / /___/ /_/ /  __/ /  / /__/  __/ /      v1.6
    
        \____/\____/\___/_/   \___/\___/_/       by @podalirius_
    
     
    
    usage: Coercer.py [-h] [-u USERNAME] [-p PASSWORD] [-d DOMAIN] [--hashes [LMHASH]:NTHASH] [--no-pass] [-v] [-a] [-k] [--dc-ip ip address] [-l LISTENER] [-wh WEBDAV_HOST] [-wp WEBDAV_PORT]
    
                      (-t TARGET | -f TARGETS_FILE) [--target-ip ip address]
    
     
    
    Automatic windows authentication coercer over various RPC calls.
    
     
    
    options:
    
      -h, --help            显示工具帮助信息和退出
    
      -u USERNAME, --username USERNAME
    
                          用于终端认证的用户名
    
      -p PASSWORD, --password PASSWORD
    
                          用于终端认证的密码
    
      -d DOMAIN, --domain DOMAIN
    
                          用于终端认证的密码Windows域名称
    
      --hashes [LMHASH]:NTHASH
    
                            NT/LM 哈希(LM哈希可以为空)
    
      --no-pass             不询问密码
    
      -v, --verbose          开启Verbose模式(默认: False)
    
      -a, --analyze          工具分析模式 (默认: Attack mode)
    
      -k, --kerberos        使用Kerberos认证，根据目标参数从ccache文件中获取凭证
    
      --dc-ip ip address     域控制器的IP地址
    
      -t TARGET, --target TARGET
    
                           目标设备的IP地址或主机名称
    
      -f TARGETS_FILE, --targets-file TARGETS_FILE
    
                           包含目标设备IP地址或主机名称的列表文件
    
      --target-ip ip address
    
                           目标设备的IP地址
    
     
    
      -l LISTENER, --listener LISTENER
    
                            监听设备的IP地址和主机名称
    
      -wh WEBDAV_HOST, --webdav-host WEBDAV_HOST
    
                            待认证的服务器WebDAV IP地址 
    
      -wp WEBDAV_PORT, --webdav-port WEBDAV_PORT
    
                            待认证的服务器WebDAV端口

## 工具使用演示

### 强制SMB认证演示

下面给出的视频将演示如何针对一个目标执行各种模式的攻击测试：

 **视频地址** ：【[ _点我观看_](https://user-images.githubusercontent.com/79218792/177647814-bb04f728-96bb-4048-a3ad-f83b250c05bf.mp4)】

### 强制WebDAV认证演示

如果你想触发一次HTTP认证，我们可以使用--webdav-host选项来使用WebDAV并设置目标设备的NetdBIOS名称：

 **视频地址** ：【[ _点我观看_](https://user-images.githubusercontent.com/79218792/178027554-a0b084d8-10af-401a-b54c-f33bec011fe2.mp4)】

## 工具输出样例

攻击模式中（未使用--analyze选项）我们可以获取下列输出信息：

![](https://image.3001.net/images/20220913/1663036936_631fee083ae14dd8f0699.png!small)

所有的RPC调用结束后，我们将在Responder中获取到认证信息：

![](https://image.3001.net/images/20220913/1663036942_631fee0ea7ace020b59e2.png!small)

## 项目地址

 **Coercer** ：【[ _GitHub传送门_](https://github.com/p0dalirius/Coercer)】

## 参考资料

> [ _https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-> rprn/d42db7d5-f141-4466-8f47-0a4be14e2fc1_](https://docs.microsoft.com/en-> us/openspecs/windows_protocols/ms-rprn/d42db7d5-f141-4466-8f47-0a4be14e2fc1)
>
> [ _https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-> efsr/08796ba8-01c8-4872-9221-1000ec2eff31_](https://docs.microsoft.com/en-> us/openspecs/windows_protocols/ms-efsr/08796ba8-01c8-4872-9221-1000ec2eff31)
>
> [ _https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-> fsrvp/dae107ec-8198-4778-a950-faa7edad125b_](https://docs.microsoft.com/en-> us/openspecs/windows_protocols/ms-> fsrvp/dae107ec-8198-4778-a950-faa7edad125b)
>
> [ _https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-> dfsnm/95a506a8-cae6-4c42-b19d-9c1ed1223979_](https://docs.microsoft.com/en-> us/openspecs/windows_protocols/ms-> dfsnm/95a506a8-cae6-4c42-b19d-9c1ed1223979)

