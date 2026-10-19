## 一、CobaltStrike简介

Cobalt
Strike是一款基于java的内网渗透测试神器，常被业界人称为CS神器。自3.0以后已经不在使用Metasploit框架而作为一个独立的平台使用，分为客户端与服务端，服务端是一个，客户端可以有多个，非常适合团队协同作战，多个攻击者可以同时连接到一个团队服务器上，共享攻击资源与目标信息和sessions，可模拟APT做模拟对抗，进行内网渗透。
Cobalt Strike集成了端口转发、服务扫描，socket代理，多模式端口监听，win exe木马生成，win
dll木马生成，java木马生成，office宏病毒生成，木马捆绑；钓鱼攻击包括：站点克隆，目标信息获取，java执行，浏览器自动攻击等等。

### 1.1服务端

团队服务器最好运行在Linux平台上，服务端的关键文件是teamserver和cobaltstrike.jar，将这两个文件放在同一目录下运行：![1625652484_60e57d046256676b0f7bb.png!small?1625652485311](https://image.3001.net/images/20210707/1625652484_60e57d046256676b0f7bb.png!small?1625652485311)

团队服务器默认连接端口为50050，如果你想修改端口只需修改teamserver文件。![1625652541_60e57d3d93f72c7de567f.png!small?1625652542363](https://image.3001.net/images/20210707/1625652541_60e57d3d93f72c7de567f.png!small?1625652542363)

### 1.2客户端

Linux：./cobaltstrike或 java -XX:+AggressiveHeap -XX:+UseParallelGC -jar
cobaltstrike.jar

Windows：双击cobaltstrike.exe![1625652624_60e57d903768237c27bb1.png!small?1625652625048](https://image.3001.net/images/20210707/1625652624_60e57d903768237c27bb1.png!small?1625652625048)

## 二、生成木马

### 2.1创建监听器

点击Cobalt Strike -> Listeners->Add，其中内置了八种监听器。

其中windows/beacon为内置监听器，包括dns、http、https、smb、tcp、extc2六种方式的监听器；windows/foreign为外部监听器，配合Metasploit或者Armitage的监听器。![1625652739_60e57e03ec9bfbb972481.png!small?1625652741113](https://image.3001.net/images/20210707/1625652739_60e57e03ec9bfbb972481.png!small?1625652741113)

### 2.2hta文件木马

hta木马是 http
application的缩写是一种独立的程序跟c++写的程序没啥区别。可以被windows电脑的mshta命令直接执行。可更改任意后缀名。点Attacks->Packages->HTML
Application，选择对应的监听器，选择powershell即可生成。![1625653017_60e57f19ccbddf301174a.png!small?1625653018610](https://image.3001.net/images/20210707/1625653017_60e57f19ccbddf301174a.png!small?1625653018610)

目标主机访问到木马文件并执行，返回CS就可以看到受害者上线。![1625653057_60e57f41281b9ac096a99.png!small?1625653057996](https://image.3001.net/images/20210707/1625653057_60e57f41281b9ac096a99.png!small?1625653057996)

![1625653065_60e57f49025a77d66cc13.png!small?1625653065756](https://image.3001.net/images/20210707/1625653065_60e57f49025a77d66cc13.png!small?1625653065756)

目标主机使用dos命令访问到木马文件并执行，返回CS就可以看到受害者上线。![1625653098_60e57f6ab4a4e6a7bff61.png!small?1625653099468](https://image.3001.net/images/20210707/1625653098_60e57f6ab4a4e6a7bff61.png!small?1625653099468)

![1625653113_60e57f793aa6abfc67d65.png!small?1625653113959](https://image.3001.net/images/20210707/1625653113_60e57f793aa6abfc67d65.png!small?1625653113959)

### 2.3EXE文件木马

点击Attacks->Packages->Windows Executable，选择对应的监听器，这里可生成（PowerShell,Raw,Windows
EXE,Windows DLL(32-bit),Windows DLL(64-bit)）选择Windows
EXE，点击Generate生成，选择生成的路径及文件名保存即可。![1625653227_60e57feba346a8b1e90d3.png!small?1625653228329](https://image.3001.net/images/20210707/1625653227_60e57feba346a8b1e90d3.png!small?1625653228329)

将生成的exe文件投递到目标主机，目标主机运行。![1625653245_60e57ffd8362674ab5a63.png!small?1625653246519](https://image.3001.net/images/20210707/1625653245_60e57ffd8362674ab5a63.png!small?1625653246519)

### 2.4DLL文件木马

DLL是编译好的代码，与一般程序没什么大差别，只是它不能独立运行，需要程序调用。DLL的代码和其他程序几乎没什么两样，仅仅是接口和启动模式不同，只要改动一下代码入口，DLL就变成一个独立的程序。![1625653307_60e5803b32fea3a864f1a.png!small?1625653307980](https://image.3001.net/images/20210707/1625653307_60e5803b32fea3a864f1a.png!small?1625653307980)

将生成的dll文件投递到目标主机，目标主机运行。![1625653324_60e5804c81de63bc9f6f1.png!small?1625653325506](https://image.3001.net/images/20210707/1625653324_60e5804c81de63bc9f6f1.png!small?1625653325506)

DLL文件下载过程中对应数据包![1625653392_60e580904756a60286507.png!small?1625653393471](https://image.3001.net/images/20210707/1625653392_60e580904756a60286507.png!small?1625653393471)

### 2.5shellcode

CS可以生成很多类型的shellcode，如c、c#、java、python、powershell、ruby、raw等

点击Attacks->package->paylaod generator
这里以powershell为例。将生成的payload.ps1复制到目标系统并执行以![1625653503_60e580ff0e8bbfd648f59.png!small?1625653503963](https://image.3001.net/images/20210707/1625653503_60e580ff0e8bbfd648f59.png!small?1625653503963)

## 三、SOCKS4代理

### 3.1SOCKS概念

目前利用网络防火墙将组织内部的网络结构与外部网络如 INTERNET
中有效地隔离开来，这种方法正变得逐渐流行起来。这些防火墙系统通常以应用层网关的形式工作在网络之间，提供受控的 TELNET 、 FTP 、 SMTP
等的接入。SOCKS 提供一个通用框架来使这些协议安全透明地穿过防火墙。
说的简单明了一点，在渗透测试中，我们使用socks技术，可以穿透进入目标机的内网，从而扩大我们的战果

CobaltStrike自带Socks功能，开启Socks server 配置一个代理端口，成功开启socks4后，即可
成功进入目标内网。![1625653786_60e5821ad572c6875247d.png!small?1625653787653](https://image.3001.net/images/20210707/1625653786_60e5821ad572c6875247d.png!small?1625653787653)

### 3.2socks4代理

开启socks4代理，通过代理进行内网渗透 开启socks，可以通过命令，也可以通过右键Pivoting->SOCKS
Server![1625653842_60e582526a87a27307aac.png!small?1625653843144](https://image.3001.net/images/20210707/1625653842_60e582526a87a27307aac.png!small?1625653843144)

修改vim /etc/proxychains.conf
，在文件末尾添加socks4代理服务器![1625653876_60e582745562a1083341a.png!small?1625653877120](https://image.3001.net/images/20210707/1625653876_60e582745562a1083341a.png!small?1625653877120)

使用proxychains代理扫描内网主机![1625653918_60e5829e41f7b932c822c.png!small?1625653919121](https://image.3001.net/images/20210707/1625653918_60e5829e41f7b932c822c.png!small?1625653919121)

### 3.3内网扫描

我们还可以通过隧道将整个msf带进目标内网 点击View->Proxy Pivots，选择Socks4a
Proxy,点击Tunnel:![1625653976_60e582d8c314e533b291d.png!small?1625653977849](https://image.3001.net/images/20210707/1625653976_60e582d8c314e533b291d.png!small?1625653977849)

  

## 四、Cobalt Strike与Metasploit联动

### 4.1msf开启接听模式

创建两个监听器，一个使用windows/beacon_http/reverse_http来监听肉鸡，另一个使用windows/foreign/reverse_http来将获取到的控制权传给msf(注意：这里的端口要与msf监听的端口一致)。![1625654069_60e5833528674607bc033.png!small?1625654070068](https://image.3001.net/images/20210707/1625654069_60e5833528674607bc033.png!small?1625654070068)

![1625654074_60e5833aa29ff7e253a4b.png!small?1625654075390](https://image.3001.net/images/20210707/1625654074_60e5833aa29ff7e253a4b.png!small?1625654075390)

### 4.2生成链接

利用HTML
Application来生成链接使得目标设备上线，右击选择spwan，选择msf监听器，点击Choose，返回msf查看，成功获取meterpreter会话（此方法获取到的会话并不稳定。）![1625654162_60e58392d6b652ea1c301.png!small?1625654163839](https://image.3001.net/images/20210707/1625654162_60e58392d6b652ea1c301.png!small?1625654163839)

###
4.3Metasploit生成木马，CS发布![1625654215_60e583c7c70f202a853b5.png!small?1625654216797](https://image.3001.net/images/20210707/1625654215_60e583c7c70f202a853b5.png!small?1625654216797)

![1625654223_60e583cf91e20d1ed7082.png!small?1625654224301](https://image.3001.net/images/20210707/1625654223_60e583cf91e20d1ed7082.png!small?1625654224301)

## 五、钓鱼攻击

### 5.1网站克隆

点击Attacks->Web Driver-by->Clone site，输入想要克隆的网址，这里需要勾选上Log
keystrokes来记录输入![1625654263_60e583f73d9d5d47b2db7.png!small?1625654264025](https://image.3001.net/images/20210707/1625654263_60e583f73d9d5d47b2db7.png!small?1625654264025)

当受害者输入了用户名密码，CS在日志里会有记录![1631956971_6145afebd9bd942f73cb4.png!small?1631956971758](https://image.3001.net/images/20210918/1631956971_6145afebd9bd942f73cb4.png!small?1631956971758)

### 5.2网站跳转

我们发现即使受害者输入正确的账号密码系统也会提示用户名密码错误，然后会自动跳转到正确的登录界面，事实上我们还可以实现主动跳转到任意界面。
为了防止没有主动跳转到正确的页面我们可以选择主动跳转到正确页面 点击 Attacks->Web Driver-by->System
Profiler![1631956995_6145b00384f96ad64ddc6.png!small?1631956995299](https://image.3001.net/images/20210918/1631956995_6145b00384f96ad64ddc6.png!small?1631956995299)

## 六、提权

### 6.1导入cna文件

点击Cobalt Strike->Script Manager来导入elevate.cna
文件![1625654383_60e5846f016c08a73d572.png!small?1625654383805](https://image.3001.net/images/20210707/1625654383_60e5846f016c08a73d572.png!small?1625654383805)

选中目标机器右击选择Access->Elevate，选择相应的漏洞即可提权![1625654399_60e5847f9d55024857689.png!small?1625654400303](https://image.3001.net/images/20210707/1625654399_60e5847f9d55024857689.png!small?1625654400303)

## 七、权限维持

### 7.1服务后门

打开beacon
shell并执行命令![1625654513_60e584f1136b77e0ab9b2.png!small?1625654513835](https://image.3001.net/images/20210707/1625654513_60e584f1136b77e0ab9b2.png!small?1625654513835)

查看受害机器服务，发现名为name的服务项创建成功![1625654529_60e585015ef02d514fa66.png!small?1625654530296](https://image.3001.net/images/20210707/1625654529_60e585015ef02d514fa66.png!small?1625654530296)

### 7.2修改启动类型

不过此时该服务启动类型为手动，我们需要将其设置为自动![1625654555_60e5851b94dc0ce4799b3.png!small?1625654556265](https://image.3001.net/images/20210707/1625654555_60e5851b94dc0ce4799b3.png!small?1625654556265)

这样一个service后门就设置成功了，即使目标机器重启后依旧可以拿到控制权限。![1625654568_60e58528487518a4d1300.png!small?1625654569113](https://image.3001.net/images/20210707/1625654568_60e58528487518a4d1300.png!small?1625654569113)

### 7.3注册表后门

打开beacon
shell并执行命令![1625654619_60e5855b8740f2d225015.png!small?1625654620277](https://image.3001.net/images/20210707/1625654619_60e5855b8740f2d225015.png!small?1625654620277)

![1625654624_60e58560bd5b6ec620a09.png!small?1625654625567](https://image.3001.net/images/20210707/1625654624_60e58560bd5b6ec620a09.png!small?1625654625567)

这样一个注册表自启动后门已经设置成功了![1625654634_60e5856aae75c202820bb.png!small?1625654635490](https://image.3001.net/images/20210707/1625654634_60e5856aae75c202820bb.png!small?1625654635490)

