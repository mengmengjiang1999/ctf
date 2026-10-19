![](https://image.3001.net/images/20220906/1662430322_6316ac72ac25791e53ea6.jpg!small)  

## 关于Chisel-Strike

Chisel-Strike是一款功能强大的.NET异或XOR加密CobaltStrike Aggressor实现，该工具主要针对的是[
_Chisel_](https://www.freebuf.com/articles/network/267887.html)（一个通过HTTP实现的快速TCP/UDP信道），旨在实现运行速度更快的代理以及更加高级的Socks5功能。

根据目前的情况来看，socks4/socks4a代理与其对应的socks5相比相当慢，并且在大多数C2框架中缺乏socks5的实现。社区有一个Chisel的C#封装版本，名为SharpChisel，但这个工具仍然存在一些未解决的问题。为了解决此前遗留的各种问题，Chisel-Strike便应运而生。在该工具的帮助下，我们可以实现更快速的代理以及更加高级的Socks5功能。

## 工具安装

注意：如果你使用了Windows Teamserver版本的CobaltStrike，请跳过第二步和第三步。

第一步，使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/m3rcer/Chisel-Strike.git

第二步，使用下列命令将所有的代码转变为可执行文件：

    
    
    cd Chisel-Strike
    
    chmod +x -R chisel-modules
    
    chmod +x -R tools

第三步，安装Mingw-w64和mono：

    
    
    sudo apt-get install mingw-w64
    
    sudo apt install mono-complete

第四步，在CobaltStrike中使用脚本管理器将ChiselStrike.cna导入进去。

如果有需要的话，请重新编译src目录中的代码。

## 工具使用

[ _Chisel_](https://www.freebuf.com/articles/network/267887.html)可以在CS
Teamserver客户端（Windows/Linux）和Beacon中分别以服务器端和客户端的身份运行。在常规执行流中，我们首先需要在CS
Teamserver客户端中搭建一台Chisel服务器，然后在Beacon中创建一个客户端，并回连CS Teamserver客户端。

### 命令执行

在Beacon中运行Chisel：

    
    
    chisel <client/server> <command>

在CS Teamserver客户端运行Chisel：

    
    
    chisel-tms <client/server> <command>

使用选择的密码对SharpChisel.exe进行异或加密：

    
    
    chisel-enc

查看CS Teamserver客户端和Beacon中所有的活动Chisel任务：

    
    
    chisel-jobs

终止一个Beacon中的Chisel活动任务：

    
    
    chisel-kill

终止CS Teamserver客户端中的Chisel活动任务：

    
    
    chisel-tms-kill

## 工具使用演示

![](https://image.3001.net/images/20220906/1662430372_6316aca483636812caa63.png!small)

![](https://image.3001.net/images/20220906/1662430380_6316acacf2197773872a4.png!small)

![](https://image.3001.net/images/20220906/1662430389_6316acb5ebc4b60cb4433.png!small)

![](https://image.3001.net/images/20220906/1662430398_6316acbe501003fd98cdf.png!small)  

## 许可证协议

本项目的开发与发布遵循[ _GPL_ _-3.0_](https://github.com/m3rcer/Chisel-Strike/blob/main/LICENSE.md)开源许可证协议。

## 项目地址

 **Chisel-Strike** ：【[ _GitHub传送门_](https://github.com/m3rcer/Chisel-Strike)】

## 参考资料

> [
> _https://www.freebuf.com/articles/network/267887.html_](https://www.freebuf.com/articles/network/267887.html)
>
> [ _https://github.com/jpillora/chisel_](https://github.com/jpillora/chisel)
>
> [
> _https://github.com/shantanu561993/SharpChisel_](https://github.com/shantanu561993/SharpChisel)
>
> [ _https://github.com/latortuga71/SharpChisel-> NG_](https://github.com/latortuga71/SharpChisel-NG)
>
> [
> _https://github.com/nettitude/SharpSocks_](https://github.com/nettitude/SharpSocks)
>
> [
> _https://gist.github.com/Arno0x/2b223114a726be3c5e7a9cacd25053a2_](https://gist.github.com/Arno0x/2b223114a726be3c5e7a9cacd25053a2)
>
> [ _https://github.com/Flangvik_](https://github.com/Flangvik)

