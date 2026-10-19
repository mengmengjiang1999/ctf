![](https://image.3001.net/images/20230508/1683513253_64585fa50fe60239d1bbf.jpg!small)

## 关于PyRexecd

PyRexecd是一款专为Windows设计的独立SSH服务器，在该工具的帮助下，广大研究人员可以轻松搭建和使用SSH服务器。

## 功能介绍

> 1、独立的Win32应用程序，而非服务，支持常驻系统托盘；
>
> 2、支持独立用户/公钥身份验证；
>
> 3、支持通过弹窗提醒传入的连接；
>
> 4、支持通过STDIN/STDOUT发送和接收剪贴板文字内容；

## 工具要求

> [ _Python 3_](http://www.python.org/)
>
> [ _Paramiko_](http://www.paramiko.org/)
>
> [ _PyWin32_](http://sourceforge.net/projects/pywin32/)
>
> [ _cx_Freeze_ _（_ _可选_ _）_](https://pypi.python.org/pypi/cx_Freeze)

## 工具安装

由于该工具基于Python 3开发，因此我们首先需要在本地设备上安装并配置好Python
3环境。接下来，广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/euske/pyrexecd.git

除此之外，我们也可以直接使用pip命令安装PyRexecd：

    
    
    pip install pyrexecd

## 工具运行

在命令行终端中切换到项目目录，运行下列命令即可启动PyRexecd：

    
    
    python3 PyRexec.pyw

上述命令将会生成一个新的主机密钥，并打开一个配置目录：

    
    
    AppData\Roaming\PyRexecd

然后使用下列命令将你的公共密钥写入到config目录中：

    
    
    > copy your\id_ed25519.pub authorized_keys

运行下列命令启动服务器：

    
    
    python3 PyRexec.pyw

最后，通过2200/tcp连接到目标设备即可：

    
    
    $ ssh -p 2200 windows

## 命令行语句

    
    
    > pyrexecd.exe [-d] [-l logfile] [-s sshdir] [-L addr] [-p port]
    
                   [-c cmdexe] [-u username] [-a authkeys] [-h homedir]
    
       ssh_host_key ...

### 参数解释

> -d : 打开调试模式；
>
> -l logfile : 日志文件路径(默认: pyrexecd.log)；
>
> -s sshdir : 配置文件目录路径(默认: AppData\Roaming\PyRexecd)；
>
> -L a.b.c.d : 指定监听地址 (默认: 127.0.0.1)；
>
> -p port : 指定监听端口 (默认: 2200)；
>
> -c cmdexe : cmd.exe 文件路径. (默认: cmd.exe)；
>
> -u username : 用户名；
>
> -a authkeys : authorized_keys密钥文件路径. (默认: authorized_keys)；
>
> -h homedir : 主目录路径 (默认: %UserProfile%)；

## 特殊命令

特定的SSH命令会被工具以特殊命令识别：

@clipget : 从Windows接收剪贴板文字数据；

    
    
    $ ssh windows @clipget > clipboard.txt

@clipset : 向Windows发送剪贴板文字数据；

    
    
    $ echo foo | ssh windows @clipset

@open, @edit, and @print : Windows shell 操作，需从STDIN提供目标参数名称；

    
    
    $ echo C:\User\euske\foo.txt | ssh windows @edit

## exe构建（需要cx_Freeze）

    
    
    > pip install cx_Freeze
    
    > python setup_exe.py build

## 工具使用演示

![](https://image.3001.net/images/20230508/1683513405_6458603d807f7c328d871.gif!small)

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/euske/pyrexecd/blob/master/LICENSE.txt)开源许可证协议。

## 项目地址

 **PyRexecd** ：【[ _GitHub传送门_](https://github.com/euske/pyrexecd)】

## 参考资料

> [
> _https://pypi.python.org/pypi/PyRexecd/_](https://pypi.python.org/pypi/PyRexecd/)
>
> [ _http://www.python.org/_](http://www.python.org/)
>
> [ _http://www.paramiko.org/_](http://www.paramiko.org/)
>
> [
> _http://sourceforge.net/projects/pywin32/_](http://sourceforge.net/projects/pywin32/)
>
> [
> _https://pypi.python.org/pypi/cx_Freeze_](https://pypi.python.org/pypi/cx_Freeze)

