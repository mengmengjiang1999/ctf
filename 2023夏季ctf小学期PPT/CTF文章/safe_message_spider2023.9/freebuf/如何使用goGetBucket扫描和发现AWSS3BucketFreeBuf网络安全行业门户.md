![](https://image.3001.net/images/20230703/1688386655_64a2bc5fa6f28a0ad23b6.png!small)

## 关于goGetBucket

goGetBucket是一款针对AWS S3 Bucket的渗透测试与安全研究工具，在该工具的帮助下，广大研究人员可以快速扫描和发现AWS S3
Bucket。

在针对一个域名执行网络侦查任务的时候，了解目标组织所拥有的资产是非常重要的。AWS S3
Bucket的权限问题一直都是困扰大家的一个麻烦事，而这一个麻烦则有可能进一步导致敏感数据的泄漏。

因此goGetBucket便应运而生，该工具可以使用常见的模式来枚举S3 Bucket名称，并通过使用自定义列表实现根域名置换的形式来枚举更多的S3
Bucket。

## 功能介绍

该工具支持扫描并返回下列关于每一个Bucket的信息：

> 1、列表权限；
>
> 2、写入权限；
>
> 3、Bucket所在的区域；
>
> 4、目标Bucket是否禁用了全部的访问权限；

## 工具安装

由于该工具基于Go语言开发，因此广大研究人员需要在本地设备上安装并配置好Go语言环境。

接下来，我们可以直接使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/glen-mac/goGetBucket.git

除此之外，我们也可以使用go get命令来安装goGetBucket：

    
    
    go get -u github.com/glen-mac/goGetBucket

## 工具使用

    
    
    goGetBucket -m ~/tools/altdns/words.txt -d <domain> -o <output> -i <wordlist>

## 工具帮助信息

    
    
    Usage of ./goGetBucket:
    
      -d string
    
            提供目标域名
    
      -f string
    
            测试文件路径 (默认"/tmp/test.file")
    
      -i string
    
            要枚举的输入字典文件路径
    
      -k string
    
            关键词列表
    
      -m string
    
            变异字典路径
    
      -o string
    
            输入文件/日志路径
    
      -t int
    
            并发线程数量 (默认为100)

## 工具运行截图

![](https://image.3001.net/images/20230703/1688386731_64a2bcabc31947f69d51f.png!small)

## 许可证协议

本项目的开发与发布遵循GPL-3.0开源许可证协议。

## 项目地址

 **goGetBucket** ：【[ _GitHub传送门_](https://github.com/glen-mac/goGetBucket)】

## 参考资料

> [ _https://github.com/infosec-au/altdns_](https://github.com/infosec-> au/altdns)

