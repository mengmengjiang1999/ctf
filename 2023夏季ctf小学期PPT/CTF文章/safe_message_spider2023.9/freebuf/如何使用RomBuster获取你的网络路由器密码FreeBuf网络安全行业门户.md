![](https://image.3001.net/images/20210722/1626953873_60f958911a0c9f380f1e9.png!small)

## 关于RomBuster

RomBuster是一款功能强大的针对网络路由器的漏洞利用工具，该工具能够帮助广大研究人员对网络路由器的安全性进行分析，并获取目标路由器的管理员密码。

## 功能介绍

> 能够利用大多数热门路由器中的安全漏洞，例如D-Link、Zyxel、TP-Link和华为等等。
>
> 经过优化处理，可从列表中读取多个目标路由器，并进行安全分析和漏洞利用。
>
> 简单的命令行接口和API用法。

## 工具安装

由于RomBuster使用Python3开发，因此首先需要在本地设备上安装并配置好Python3环境。接下来，广大研究人员可以使用下列命令下载并安装RomBuster：

    
    
    pip3 install git+https://github.com/EntySec/RomBuster

## 基础使用

RomBuster的使用非常简单，我们只需要在命令行终端中输入“rombuster”命令即可使用RomBuster：

    
    
    usage: rombuster [-h] [-o OUTPUT] [-i INPUT] [-a ADDRESS] [--shodan SHODAN]
    
                     [--zoomeye ZOOMEYE] [-p PAGES]
    
     
    
    RomBuster is a router exploitation tool that allows to disclosure network
    
    router admin password.
    
     
    
    optional arguments:
    
      -h, --help            显示这个帮助信息并退出
    
      -o OUTPUT, --output OUTPUT
    
                            将结果存储至文件
    
      -i INPUT, --input INPUT
    
                            地址列表输入文件
    
      -a ADDRESS, --address ADDRESS
    
                            提供单个地址
    
      --shodan SHODAN       通过网络利用远程设备所使用的Shodan API密钥
    
      --zoomeye ZOOMEYE     通过网络利用远程设备所使用的ZoomEye API密钥
    
      -p PAGES, --pages PAGES
    
                            需要通过ZoomEye获取的页面数量

## 工具使用样例

### 攻击单个路由器

下列命令可以攻击单个网络路由器：

    
    
    rombuster -a 192.168.99.1

### 通过网络攻击远程路由器

接下来，我们可以使用Shodan搜索引擎来搜索并攻击网络上的由器：

    
    
    rombuster --shodan PSKINdQe1GyxGgecYz2191H2JoS9qvgD

注意：项目中给出的Shodan
API密钥（PSKINdQe1GyxGgecYz2191H2JoS9qvgD）是开发人员自己的专业版API密钥，你可以使用你自己的密钥，当然了你想用开发人员的也没意见，大家资源共享嘛！

### 从输入文件获取目标路由器

我们还可以使用开放数据库中提供的摄像头地址：

    
    
    rombuster -i routers.txt -o passwords.txt

注意：此命令将会攻击routers.txt中给出的所有摄像头，并会将所有获取到的密码存储至passwords.txt文件中。

## API使用

RomBuster还提供了自己的Python API，可以将其导入至你们自己的项目代码中并调用其功能：

    
    
    from rombuster import RomBuster

### 基础函数

下面给出的是RomBuster支持的基础函数，可以用于利用指定路由器中的安全漏洞：

> exploit(address)：攻击指定地址的单个路由器

### 调用样例

 **攻击单个路由器：**

    
    
    from rombuster import RomBuster
    
     
    
    rombuster = RomBuster()
    
    creds = rombuster.exploit('192.168.99.1')
    
     
    
    print(creds)

## 项目地址

 **RomBuster：** 【[ _GitHub传送门_](https://github.com/EntySec/RomBuster)】

