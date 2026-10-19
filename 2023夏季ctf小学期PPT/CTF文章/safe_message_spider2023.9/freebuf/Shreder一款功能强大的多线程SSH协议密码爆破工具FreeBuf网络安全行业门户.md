![](https://image.3001.net/images/20210717/1626455298_60f1bd0228bb699958277.jpg!small)

## 关于Shreder

Shreder是一款功能强大的多线程SSH协议密码爆破工具，广大研究人员可以使用Shreder对SSH协议的安全性进行探究。

## 功能介绍

> 能够快速执行密码爆破，每个密码仅需1秒；
>
> 经过优化处理，支持大型密码字典，Shreder尝试1000个密码仅需1分40秒；
>
> 简单的命令行接口和API使用方法；

## 工具安装

由于Shreder使用Python3开发，因此首先需要在本地设备上安装并配置好Python3环境。接下来，广大研究人员可以使用下列命令下载并安装Shreder：

    
    
    pip3 install git+https://github.com/EntySec/Shreder

## 工具基础使用

Shreder的使用非常简单，我们只需要在命令行终端中输入“shreder”命令即可使用Shreder：

    
    
    usage: shreder [-h] [-p PORT] [-u USERNAME] [-l LIST] target
    
     
    
    Shreder is a powerful multi-threaded SSH protocol password brute-force tool.
    
     
    
    positional arguments:
    
      target
    
     
    
    optional arguments:
    
      -h, --help            显示这个帮助信息并退出
    
      -p PORT, --port PORT   设置SSH端口
    
      -u USERNAME, --username USERNAME
    
                          设置SSH用户名
    
      -l LIST, --list LIST       设置密码字典列表路径

## 工具使用样例

### 针对单个目标执行爆破

下列命令可以针对单个目标执行爆破任务：

    
    
    shreder 192.168.2.109 -u mobile -l passwords.txt

## API使用

Shreder还提供了自己的Python API，可以将Shreder导入至你们自己的项目代码中并调用其功能：

    
    
    from shreder import Shreder

### 基础函数

> connect(host, port, username, password)：根据给定的地址与单个目标建立连接；

> brute(host, port, username, dictionary)：根据给定的地址针对单个目标执行爆破任务；

### 调用样例

 **针对单个目标执行爆破：**

    
    
    from shreder import Shreder
    
     
    
    shreder = Shreder()
    
    password = shreder.brute('192.168.2.109', 22, 'mobile', 'passwords.txt')
    
     
    
    print(password)

## 项目地址

 **Shreder：** 【[ _GitHub传送门_](https://github.com/EntySec/Shreder)】

