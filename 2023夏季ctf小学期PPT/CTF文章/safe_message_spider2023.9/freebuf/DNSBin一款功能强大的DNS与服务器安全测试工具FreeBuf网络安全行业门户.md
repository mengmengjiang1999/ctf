![](https://image.3001.net/images/20230827/1693138340_64eb3da4e1bb9b2e7c827.png!small)

## 关于DNSBin

DNSBin是一款功能强大的DNS与服务器安全测试工具，该工具可以通过DNS来测试数据泄露，并在目标环境部署了严苛网络安全限制的场景下帮助广大研究人员测试远程代码执行（RCE）和XML外部实体注入（XXE）等安全漏洞。

该项目由两个部分组成，第一个部分是Web服务器及其相关组件，它提供了一个基本的Web
UI，这也适用于绝大多数的使用场景了。第二部分则是客户端组件，客户端提供了一个Python脚本，可以允许使用Web服务器并通过DNS实现双向数据传输。

## 工具安装

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/ettic-team/dnsbin.git

## 工具配置

### DNS

工具演示Demo所使用的服务器当前DNS配置如下。请注意，该配置已经过了长时间的反复测试，因此设置的可能过于复杂：

> 1、为域名“dns1.zhack.ca”添加一条指向“192.99.55.194”的“a”记录；
>
> 2、为域名“ns1.zhack.ca”添加一个指向“192.99.55.194”的“a”记录；
>
> 3、为域名“d.zhack.ca”添加一条“NS”记录，值为“dns1.zhack.ca”；
>
> 4、为域名“d.zhack.ca”添加一个值为“ns1.zhack.cab”的“NS”记录；

### Web托管

强烈建议使用Node.JS模块“forever”来启动DNS接收器和WebSocket端点：

    
    
    forever start index.js

对于前端，文件“index.html”可以托管在你选择的Web服务器上，请确保WebSocket URL指向你的服务器即可。

### 客户端

客户端脚本要求在两端都安装“[
_dnspython_](https://github.com/rthalley/dnspython)”。无论是发送还是接收数据，都必须首先在受限区域外的计算机上启动脚本。脚本将为广大研究人员提供一个唯一的令牌，当你在受限区域内的计算机上运行脚本时，必须传递该令牌。

## 工具使用

### 发送数据使用样例

设备外：

    
    
    echo test12345 | python main.py -f- -d out -t-
设备内：

    
    
    python main.py -f- -d in -t TOKEN_THE_FIRST_COMMAND_GAVE_YOU

### 接收数据使用样例

设备外：

    
    
    python main.py -f- -d in -t-
设备内：

    
    
    echo test12345 | python main.py -f- -d out -t TOKEN_THE_FIRST_COMMAND_GAVE_YOU

## 工具使用Demo

 **使用Demo** ：【[ _点我尝试_](http://dnsbin.zhack.ca/)】

## 项目地址

 **DNSBin** ：【[ _GitHub传送门_](https://github.com/ettic-team/dnsbin)】

## 参考资料

> [ _http://dnsbin.zhack.ca/_](http://dnsbin.zhack.ca/)
>
> [
> _https://www.npmjs.com/package/forever_](https://www.npmjs.com/package/forever)
>
> [
> _https://github.com/rthalley/dnspython_](https://github.com/rthalley/dnspython)

