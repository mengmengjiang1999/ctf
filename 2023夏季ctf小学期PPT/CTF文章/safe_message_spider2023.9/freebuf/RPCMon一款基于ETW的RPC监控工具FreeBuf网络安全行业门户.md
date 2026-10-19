![](https://image.3001.net/images/20220830/1661864632_630e0ab88f52bcde46358.png!small)

## 关于RPCMon

RPCMon是一款基于事件跟踪的WindowsRPC监控工具，该工具是一款GUI工具，可以帮助广大研究人员通过ETW（Event Tracing for
Windows）扫描RPC通信。

RPCMon能够为广大研究人员提供进程之间RPC通信的高级视图，该工具功能类似Procmon，且易于使用，并利用了James Forshaw
.NET库来处理RPC连接。RPCMon能够显示被调用的RPC功能，以及调用它们的进程和相关信息。

RPCMon使用了硬编码的RPC字典（包含了关于RPC模块的信息）来快速处理RPC信息，并提供了选项来辅助构建一个RPC数据库，因此我们可以随时更新相关信息以便填充硬编码的RPC字典。

## 功能介绍

> 1、提供RPC功能活动的详细信息；
>
> 2、支持构建RPC数据库以解析RPC模块或使用硬编码数据库；
>
> 3、支持筛选或高亮显示每行单元格信息；
>
> 4、指定行粗体显示；

## 工具下载

### 源码获取

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/cyberark/RPCMon.git

接下来，在Visual Studio中打开项目源码并进行编译即可。

### 预编译下载

除此之外，广大研究人员也可以直接访问该项目【[Releases页面](https://github.com/cyberark/RPCMon/releases)】下载预编译的RPCMon：

![](https://image.3001.net/images/20220830/1661864681_630e0ae9c484142b27be1.png!small)

## 工具使用

双击RPCMon的EXE可执行文件，便可以打开RPCMon的GUI窗口。

RPCMon还需要一个数据库来获取RPC功能的详细信息，如果没有数据库的话，可能会导致某些数据丢失。

如需加在数据库，请点击“DB -> Load DB...”，然后选择你说要使用的数据库即可。你也可以选择项目提供的数据库文件：

    
    
    /DB/RPC_UUID_Map_Windows10_1909_18363.1977.rpcdb.json

接下来，你就可以开始使用RPCMon了。

## 工具使用演示

 **视频地址** ：【[ _点我观看_](https://user-images.githubusercontent.com/11998736/165285471-e143eebd-bfbf-49a2-8e70-107f083c60fc.mp4)】

## 许可证协议

本项目的开发与发布遵循[ _Apache_
_-2.0_](https://github.com/cyberark/RPCMon/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **RPCMon** ：【[ _GitHub传送门_](https://github.com/cyberark/RPCMon)】

## 参考资料

> [ _https://github.com/tyranid_](https://github.com/tyranid)
>
> [ _https://github.com/googleprojectzero/sandbox-attacksurface-analysis-> tools/tree/main/NtApiDotNet_](https://github.com/googleprojectzero/sandbox-> attacksurface-analysis-tools/tree/main/NtApiDotNet)
>
> [ _https://twitter.com/g3rzi_](https://twitter.com/g3rzi)

