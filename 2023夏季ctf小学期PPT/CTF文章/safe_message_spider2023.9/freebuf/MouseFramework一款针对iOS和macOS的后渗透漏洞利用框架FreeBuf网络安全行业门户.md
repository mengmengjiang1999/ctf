![](https://image.3001.net/images/20200301/1583055155_5e5b8133557c7.jpeg!small)

![](https://image.3001.net/images/20200301/1583055161_5e5b8139052a7.png!small)

## 关于Mouse Framework框架

 **Mouse
Framework是一款针对iOS和macOS的后渗透漏洞利用框架，它可以给安全研究人员提供一个带有数据提取功能的命令行会话，只需要使用一个简单的Mouse
Payload，我们就可以轻松在目标设备与分析主机之间建立一条命令行会话。不仅如此，Mouse
Framework还提供了强大且便捷的文件上传、文件下载、Tab命令补全、屏幕截图、定位追踪、Shell命令执行、权限提升以及密码检索与恢复等功能。**

## Mouse Framework框架的下载和安装

### 工具下载

广大研究人员可以使用下列命令将框架源码克隆至本地：

> git clone <https://github.com/entynetproject/mouse.git>

### 工具安装

    
    
    cd mouse
    
    chmod +x install.sh
    
    ./install.sh

### 工具卸载

    
    
    cd mouse
    
    chmod +x uninstall.sh
    
    ./uninstall.sh

### Mouse Framework框架执行

广大用户在框架安装完成之后，可以直接使用下列命令来执行Mouse Framework框架：

    
    
    mouse

## Mouse Payloads (macOS/iOS)

![](https://image.3001.net/images/20200301/1583055193_5e5b8159a5d7a.png!small)

运行之后，Mouse Payload将会尝试与远程设备进行连接，并获取远程设备会话。

### Bourne-Again Shell Payload

在Mouse框架的菜单中选择Bourne-Again Shell Payload之后，代码将会给我们提供一个1
liner，并在目标主机上执行后帮助我们与目标设备建立远程Mouse会话。

> 平台：iOS/macOS

### Teensy macOS Payload（USB 注入）

Teensy是一款提供了自定义开发功能的USB板，我们可以使用Arduino IDE来其进行编程。它可以快速模拟USB键盘击键操作，并在几秒内完成Mouse
Payload的注入。

> 平台：macOS

### Rubber Duck Payload（USB 注入）

USB Rubber DUck同样也是一款提供了自定义开发功能的USB板，它可以帮助我们在几秒钟之内成功注入.bin Payload。

> 平台：macOS

### Application macOS Payload

在Mouse框架的Payload菜单中选择Application macOS Payload之后，代码将会帮助我们将标准的Mouse
Payload转换为一个macOS应用程序。

> 平台：macOS

## 多处理器MultiHandler命令行接口

![](https://image.3001.net/images/20200301/1583055226_5e5b817a2ced2.png!small)

该框架提供的MultiHandler选项可以帮助我们同时处理多个目标设备会话，我们可以根据自己的需要选择与不同设备进行交互，并同时在后台监听新的连接。

### MultiHandler命令

> close：关闭活动会话
>
> exit：关闭所有的会话并退出
>
> help：显示所有可用的命令
>
> interact：与会话交互
>
> sessions：列出所有活动会话

## Mouse底层

Mouse Framework本质山是一个数据包，它可以直接在目标iOS设备上运行，在收到了远程控制会话后，便可以直接在目标设备上执行命令或运行服务了。

### 底层命令

> dhome：模拟home键双击
>
> home：模拟home键单机
>
> locat：切换位置服务
>
> mute：更新和查看静音状态

## Mouse命令行接口

![](https://image.3001.net/images/20200301/1583055251_5e5b81931bcee.png!small)

会话建立成功后，我们就可以通过Mouse命令行接口来在目标设备上执行命令了。我们可以通过输入“help”命令来查看所有可用指令。Mouse命令行接口允许我们直接通过命令来控制一台远程设备。

## 本地命令

![](https://image.3001.net/images/20200301/1583055259_5e5b819be8b7f.png!small)

> clear：清理终端窗口
>
> help：显示所有可用命令
>
> exec：执行本地Shell命令
>
> exit：关闭当前会话并退出

## 设置命令

![](https://image.3001.net/images/20200301/1583055269_5e5b81a57bb5c.png!small)

### macOS

> getpaste：获取剪切板内容
>
> getvol：获取扬声器输出音量
>
> idletime：获取用户活动时间
>
> setbright：设置屏幕亮度
>
> setvol：设置输出音量

### iOS

> battery：获取电池电量
>
> getvol：获取音量
>
> msub：Mouse底层
>
> setvol：设置输出音量
>
> sysinfo：显示系统信息

## 窃取命令

![](https://image.3001.net/images/20200301/1583055306_5e5b81ca25f97.png!small)

### macOS

> download：下载远程文件
>
> getfacebook：检索facebook会话cookies
>
> mic：录制麦克风声音
>
> picture：通过iSight拍摄
>
> prompt：提示用户键入密码
>
> screenshot：屏幕截图

### iOS

> download：下载远程文件
>
> getcontacts：下载通讯录
>
> getnotes：下载便签内容
>
> getpasscode：检索设备密码
>
> getsms：下载短信数据
>
> locate：获取设备位置坐标
>
> mic：录制麦克风声音
>
> picture：通过相机拍照

## 项目地址

Mouse Framework：【[ _GitHub传送门_](https://github.com/entynetproject/mouse)】

 *** 参考来源：[
_entynetproject_](https://github.com/entynetproject/mouse)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

