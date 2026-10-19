![](https://image.3001.net/images/20230516/1684251245_6463a26d9f9add3daa839.jpg!small)

## 关于wa-tunnel

wa-tunnel是一款功能强大的TCP数据传输工具，在该工具的帮助下，广大研究人员可以在两个Whatsapp账号之间传输TCP数据。

该工具有很多的使用场景，并使用[
_Baileys_](https://github.com/adiwajshing/Baileys)项目构建功能。本质上来说，它是一个基于WS的多设备whatsapp库，因此可以同时也可以在Android设备上使用（需要使用Termux）。

## 工具运行机制

该工具可以通过WhatsApp文本和文件消息发送TCP网络包，此时它会将其拆分为不同文本消息或文件。为了不让WhatsApp发送超时，默认情况下，每条消息限制为2万个字符，目前它是用wasocket.js硬编码的。开发人员已经做了多次测试，任何超过8万个字符的消息都可能超时。

如果网络包超过限制（默认情况下为20k个字符），则如果启用，它将作为文件发送。此外，如果缓存了多个网络包，它将使用相同的cryteria。

文件消息以二进制文件的形式发送，TCP响应与分隔符连接，并使用brotli压缩以减少数据使用。

工具会缓存TCP套接字响应以将它们分组，并在消息中发送最大数量的数据，从而减少消息量，提高速度并降低被禁止的概率。

## 工具配置

在使用该工具时，我们必须拥有两个WhatsApp账号，一个用作服务器端，一个用作客户端，我们可以转发一个本地端口，或使用一个外部代理服务。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/aleixrodriala/wa-tunnel.git

### 服务器端

切换到项目目录下，并运行下列命令：

    
    
    cd wa-tunnel
    
    npm install

接下来使用下列命令启动服务器，其中port为代理端口，host为需要转发的代理主机，number为WhatsApp客户端号码：

    
    
    npm run server host port number

我们也可以使用一个本地代理服务器：

    
    
    npm run server localhost 3128 12345678901

或者使用一个普通的代理服务器：

    
    
    npm run server 192.168.0.1 3128 12345678901

### 客户端

切换到项目目录下，并运行下列命令：

    
    
    cd wa-tunnel
    
    npm install

接下来使用下列命令启动客户端，其中port为本地端口，number为客户端WhatsApp编号：

    
    
    npm run client port number

比如说：

    
    
    npm run client 8080 1234567890

## 工具使用

首次运行工具脚本时，Baileys将会要求我们扫描WhatsApp的二维码，并存储会话以便后续使用。

准备好客户端和服务器端之后，我们就可以使用curl并执行工具了：

    
    
    curl -v -x proxyHost:proxyPort https://httpbin.org/ip

样例命令如下：

    
    
    curl -v -x localhost:8080 https://httpbin.org/ip

我们还可以转发其他协议端口，例如SSH：

    
    
    npm run server localhost 22 12345678901

然后使用客户端连接到服务器端：

    
    
    ssh root@localhost -p 8080

## Android使用

如需在Android设备上使用该工具，我们还需要安装好[
_Termux_](https://play.google.com/store/apps/details?id=com.termux)，并运行下列命令即可：

    
    
    pkg update && pkg upgrade
    
    pkg install git nodejs -y
    
    git clone https://github.com/aleixrodriala/wa-tunnel.git
    
    cd wa-tunnel
    
    npm install

## 工具运行演示

![](https://image.3001.net/images/20230516/1684251387_6463a2fbc862cc3af2e6c.gif)

## 许可证协议

本项目的开发与发布遵循[ _MIT_](https://github.com/aleixrodriala/wa-tunnel/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **wa-tunnel** ：【[ _GitHub传送门_](https://github.com/aleixrodriala/wa-tunnel)】

## 参考资料

> [
> _https://github.com/adiwajshing/Baileys_](https://github.com/adiwajshing/Baileys)
>
> [
> _https://play.google.com/store/apps/details?id=com.termux_](https://play.google.com/store/apps/details?id=com.termux)

