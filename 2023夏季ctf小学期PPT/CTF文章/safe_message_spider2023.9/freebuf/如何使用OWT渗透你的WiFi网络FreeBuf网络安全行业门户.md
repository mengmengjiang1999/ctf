![](https://image.3001.net/images/20210930/1632951234_6154dbc2c3a52db215f48.png!small)

## 关于OWT

OWT是一款功能强大的攻击性WiFi渗透测试套件，该工具可以利用一个Unix
Bash脚本来帮助广大研究人员编译某些针对WiFi安全审计的必要工具，并且提供了非常友好的用户接口，以辅助广大研究人员进行WiFi安全测试。OWT工具的主要目标是在保证文件大小尽可能小的情况下，给广大研究人员提供最大程度的功能性保证。

当前版本的OWT工具已添加了免费的短信消息服务。

## 工具依赖组件

> aircrack-ng
>
> mdk3
>
> xterm
>
> macchanger
>
> OWT工具在运行时会提醒用户下载上述依赖组件

## 工具安装&运行

广大研究人员可以使用下列命令下载、安装并运行OWT工具：

    
    
    ~ $ git clone https://github.com/clu3bot/OWT.git
    ~ $ cd owt
    ~ $ sudo bash owt.sh
    

注意：OWT的运行需要我们拥有ROOT权限，请确保定期更新该工具。

## 工具使用

运行该工具之后，OWT首先会弹出更新检测提醒，并提醒用户更新脚本。我们可以按下回车键来检测更新：![](https://image.3001.net/images/20210930/1632951261_6154dbdd0a6f3c9ef2c22.png!small)

接下来，用户将查看到工具基本信息以及权限状态，以及当前检测到的接口和正在使用的Linux发行版系统信息。我们可以按下回车键来让OWT自动下载任何的依赖组件：

![](https://image.3001.net/images/20210930/1632951267_6154dbe341828ad1ee861.png!small)

检测完工具所需依赖组件之后，我们需要将接口设置为监控器模式，按下回车键即可：

![](https://image.3001.net/images/20210930/1632951273_6154dbe9e7f0019d5ef34.png!small)

接下来，脚本将会进入OWT的主菜单，并给广大研究人员提供八个操作选项：

![](https://image.3001.net/images/20210930/1632951279_6154dbef8ae3304c2cf6c.png!small)

选择扫描网络，将扫描我们所要攻击的目标网络：

![](https://image.3001.net/images/20210930/1632951286_6154dbf6d02d3400c16c9.png!small)

扫描完成后工具将返回扫描结果，此时我们将能够选择需要攻击的网络，选择完成之后工具将返回主菜单：

![](https://image.3001.net/images/20210930/1632951295_6154dbffb42f2c7ab011c.png!small)

选择好目标网络之后，我们将进入WiFi攻击菜单，即菜单中的选项5.在攻击菜单中，OWT提供了六种攻击模式：

![](https://image.3001.net/images/20210930/1632951303_6154dc0744c76c1e799be.png!small)

如果没有选择目标网络，但又选择了攻击模式的话，工具将会重新进行网络扫描：

![](https://image.3001.net/images/20210930/1632951309_6154dc0d1e7dcaab7934c.png!small)

## 问题解决

Troubleshoot.sh脚本可以帮助我们检测OWT工具的运行问题，并尝试解决相关问题：

    
    
    ~ $ cd owt
    ~ $ sudo bash troubleshoot.sh
    

## 项目地址

 **OWT：** 【[GitHub传送门](https://github.com/clu3bot/owt)】

## 参考资料

> [
> _https://github.com/clu3bot/owt/wiki/Usage_](https://github.com/clu3bot/owt/wiki/Usage)
>
> [
> _https://github.com/clu3bot/owt/wiki/Help_](https://github.com/clu3bot/owt/wiki/Help)
>
> [
> _https://github.com/clu3bot/owt/wiki/Versions﻿_](https://github.com/clu3bot/owt/wiki/Versions)

