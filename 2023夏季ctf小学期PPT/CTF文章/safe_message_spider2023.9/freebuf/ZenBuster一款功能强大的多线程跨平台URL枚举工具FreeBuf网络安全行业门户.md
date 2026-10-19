![](https://image.3001.net/images/20220808/1659962219_62f1036bf3dded81ae131.jpg!small)

## 关于ZenBuster

ZenBuster是一款功能强大的多线程跨平台URL枚举工具，该工具基于Python开发，同时还具备暴力破解功能。

该工具适用于安全专业人员，可以在渗透测试或CTF比赛中为广大研究人员提供帮助，并收集和目标相关的各种信息。

## 工具功能

> 1、该工具能够对子域名和URI资源（目录/文件）进行爆破和枚举；
>
> 2、需要使用适当的字典文件；
>
> 3、主机名格式支持标准格式、IPv4和IPv6；
>
> 4、支持将结果记录到文件中（-o [filename]）；
>
> 5、使用-p选项为非标准Web服务器指定自定义端口；
>
> 6、支持静默模式（-q）；
>
> 7、可以指定需要忽略的HTTP状态码；
>
> 8、测试Python版本为3.9和3.10，理论上支持3.6及更高版本Python；

## 工具安装

首先，我们需要确保本地设备上已经安装并配置好了Python 3.6+环境，接下来，可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/0xTas/zenbuster.git

### 依赖组件

安装完成后，使用cd命令切换到项目目录下，并利用pip命令和项目提供的requirements.txt文件来安装该工具所需的依赖组件：

    
    
    cd zenbuster
    
    pip install -r requirements.txt

## 工具使用

安装好该工具所需的依赖组件之后，我们就可以通过下列方式来运行ZenBuster了。

 **Linux（macOS）** ：

    
    
    ./zenbuster.py [options]
    
    python3 zenbuster.py [options]

 **Windows** ：

    
    
    python zenbuster.py [options]

## 工具参数选项

 ** **命令缩写****

|

 ** **完整命令****

|

 ** **命令描述****  
  
---|---|---  
  
-h

|

\--help

|

显示工具帮助信息  
  
-d

|

\--dirs

|

启用目录枚举模式  
  
-s

|

-ssl

|

强制使用HTTPS  
  
-v

|

\--verbose

|

启用Verbose模式  
  
-q

|

\--quiet

|

开启静默模式运行  
  
-nc

|

\--no-color

|

禁用颜色高亮显示  
  
-ic <codes>

|

\--ignore-codes

|

查看需要排除的状态码列表  
  
-u <hostname>

|

\--host

|

待扫描的目标主机  
  
-w <wordlist>

|

\--wordlist

|

字典文件路径  
  
-p <port#>

|

\--port

|

针对非标准Web服务器的自定义端口选项  
  
-o [filename]

|

\--out-file

|

扫描结果输出文件路径  
  
  

## 工具使用演示

![](https://image.3001.net/images/20220808/1659962272_62f103a050f5133010572.png!small)

    
    
    ./zenbuster.py -d -w /usr/share/wordlists/dirb/common.txt -u target.thm -v
    
    
    python3 zenbuster.py -w ../subdomains.txt --host target.thm --ssl -O myResults.log
    
    
    zenbuster -w subdomains.txt -u target.thm --quiet -ic 400, 403

## 工具更新

    
    
    cd zenbuster
    
    git pull

## 许可证协议

本项目的开发与发布遵循[
_GPL-3.0_](https://github.com/0xTas/zenbuster/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **ZenBuster** ：【[ _GitHub传送门_](https://github.com/0xTas/zenbuster)】

## 参考资料

    
    
    https://twitter.com/0xTas
    
    http://www.asciiworld.com/+-joan_stark_jgs-+.html
    
    http://www.asciiworld.com/+-hayley_jane_wakenshaw_hjw-+.html

  

