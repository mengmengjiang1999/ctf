![](https://image.3001.net/images/20210719/1626709779_60f59f1387e58b7087264.jpg!small)

## 关于IPinfoga

IPinfoga是一款功能强大的OSINT公开资源情报工具，该工具可以导出关于目标IP地址的相关信息，比如说包含国家、城市和经纬度的地理位置信息等等。

## 功能介绍

> 导出地理位置数据，例如国家、城市和经纬度等；
>
> 经过优化处理，一次支持导出多个IP地址的相关信息；
>
> 简单的命令行接口和API使用方法；

## 工具安装

由于IPinfoga使用Python3开发，因此首先需要在本地设备上安装并配置好Python3环境。接下来，广大研究人员可以使用下列命令下载并安装IPinfoga：

    
    
    pip3 install git+https://github.com/EntySec/IPinfoga

## 工具基础使用

IPinfoga的使用非常简单，我们只需要在命令行终端中输入“ipinfoga”命令即可使用IPinfoga：

    
    
    usage: ipinfoga [-h] [-t] [-o OUTPUT] [-i INPUT] [-a ADDRESS]
    
     
    
    IPinfoga is an OSINT tool that dumps all available IP address information such
    
    as location with country, city, and latitude with longitude.
    
     
    
    optional arguments:
    
      -h, --help            显示这个帮助信息并退出
    
      -t, --threads          启用多线程模式以获得更好的性能
    
      -o OUTPUT, --output OUTPUT
    
                            将结果存储至文件
    
      -i INPUT, --input INPUT
    
                            地址列表输入文件
    
      -a ADDRESS, --address ADDRESS
    
                            提供单个地址

## 工具使用样例

### 扫描单个IP地址

下列命令可以扫描Google的DNS地址：

    
    
    ipinfoga -a 8.8.8.8

### 从输入文件扫描多个IP地址

我们可以使用开放地址数据库进行扫描，并使用-t参数来设置多线程数量以获得更好的性能：

    
    
    ipinfoga -t -i addresses.txt -o results.txt

注意：上述命令将会扫描address.txt文件中所有给出的IP地址，并将所有的扫描结果存储至results.txt中。

## API使用

IPinfoga还提供了自己的Python API，可以将其导入至你们自己的项目代码中并调用其功能：

    
    
    from ipinfoga import IPinfoga

### 基础功能函数

下面给出的是IPinfoga所提供的基础功能函数，可以用于扫描指定的IP地址：

scan(address)：扫描单个IP地址

### 调用样例

 **扫描单个IP地址：**

    
    
    from ipinfoga import IPinfoga
    
     
    
    ipinfoga = IPinfoga()
    
    data = ipinfoga.scan('8.8.8.8')
    
     
    
    for field in data:
    
        print(field, data[field])

## 项目地址

 **IPinfoga：** 【[ _GitHub传送门_](https://github.com/EntySec/IPinfoga)】

