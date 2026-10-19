## 关于GodGenesis

GodGenesis是一款基于纯Python
3开发的C2服务器，该工具旨在帮助广大红队研究人员完成渗透测试任务。当前版本的GodGenesis仅支持TCP反向Shell，不过别担心，该工具还可以帮助我们从任意目标Windows设备上获取到管理员Shell。

## 功能介绍

> 1、纯Python 3开发；
>
> 2、C2服务器；
>
> 3、提供TCP反向Shell；
>
> 4、从任意Windows设备获取管理员Shell；

## 工具安装

由于该工具基于纯Python 3开发，因此我们首先需要在设备上安装并配置好Python 3环境。接下来，使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/SaumyajeetDas/GodGenesis.git

接下来，使用pip3和requirements.txt安装并配置工具所需的依赖组件：

    
    
    pip3 install -r requirements.txt
    
    python3 c2c.py

## 支持的命令

### 基础命令

    
    
    help：显示工具帮助信息；
    
    terminate：完全终止并退出Shell；
    
    exit：让Shell在后台执行，并显示C2服务器命令行；
    
    clear：清理命令行输出； 

### 系统命令

    
    
    cd：修改当前目录；
    
    pwd：显示当前工作目录；
    
    mkdir *dir_name*：创建一个目录；
    
    rm *dir_name*：删除一个目录；
    
    powershell [command]：运行PowerShell命令；
    
    start *exe_name*：启动一个可执行程序；

### 信息收集命令

    
    
    env：检查环境变量；
    
    sc：查看所有正在运行的进程；
    
    user：显示当前用户；
    
    info：显示目标系统的所有信息；
    
    av：显示目标系统的所有反病毒产品；

### 数据提取命令

    
    
    download *file_name*：从目标系统下载文件；
    
    upload *file_name*：向目标系统上传文件；

### 漏洞利用命令

    
    
    persistence1：通过方法1实现持久化；
    
    persistence2：通过方法2实现持久化；
    
    get：从任意URL下载文件；
    
    chrome_pass_dump：从Chrome浏览器导出所有存储的密码；
    
    wifi_password：导出所有存储的WiFi网络密码；
    
    keylogger：开启键盘记录工具；
    
    dump_keylogger：导出所有键盘记录；
    
    python_install：在目标设备上安装Python（无UI）；

## 工具使用演示

 **视频地址** ：【[ _点我观看_](https://user-images.githubusercontent.com/66937297/175561859-a0e9f9dd-1e59-46da-a8e9-197d800bee37.mp4)】

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/SaumyajeetDas/GodGenesis/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **GodGenesis** ：【[ _GitHub传送门_](https://github.com/SaumyajeetDas/GodGenesis)】

## 参考资料

> [ _https://github.com/ANON4MOUS﻿_](https://github.com/ANON4MOUS)

