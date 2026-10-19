**今天给大家介绍的是一款名叫PocSuite3的开源漏洞测试框架，该工具由著名的Knownsec
404安全研究团队开发，广大安全人员可以利用该工具进行远程漏洞测试。**

![1.jpg](https://image.3001.net/images/20190428/1556421485_5cc51b6da3e1a.jpg!small)

## PocSuite3

PocSuite3是[Knownsec
404安全研究团队](http://www.knownsec.com/)设计的一款远程漏洞测试以及PoC开发框架，该框架使用了功能极其强大的概念验证引擎，并自带了大量渗透测试以及安全分析功能。

## 功能介绍

1、PoC脚本能够以attack、verify和shell等多种模式运行；

2、自带插件生态系统；

3、 可从本地文件、Redis和数据库等不同来源动态加载PoC脚本；

4、 可从CIDR、本地文件、Redis、数据库、Zoomeye和Shodan等来源加载多个测试目标；

5、 轻松导出测试结果；

6、 支持命令行工具和Python包导入；

7、 支持IPv6；

8、 支持全局HTTP/HTTPS/SOCKS代理；

9、 提供了强大的爬虫API；

10、整合[Seebug](https://www.seebug.org/)；

11、整合[ZoomEye](https://www.zoomeye.org/)；

12、整合[Shodan](https://www.shodan.io/)；

13、整合[Ceye](http://ceye.io/)；

14、等等…

## 工具运行

PocSuite3命令行模式

![2.png](https://image.3001.net/images/20190428/1556421518_5cc51b8e2a211.png!small)

> 演示视频：<https://asciinema.org/a/219356>

PocSuite3 Shell模式

![3.png](https://image.3001.net/images/20190428/1556421548_5cc51baca2c7e.png!small)  

> 演示视频：<https://asciinema.org/a/203101>

PocSuite3从Seebug加载PoC文件

![4.png](https://image.3001.net/images/20190428/1556421556_5cc51bb40e6a6.png!small)  

> 演示视频：<https://asciinema.org/a/207350>

PocSuite3从ZoomEye加载多个测试目标

![5.png](https://image.3001.net/images/20190428/1556421564_5cc51bbc93bc5.png!small)  

> 演示视频：<https://asciinema.org/a/207349>

PocSuite3从Shodan加载多个分析目标

![6.png](https://image.3001.net/images/20190428/1556421573_5cc51bc56f3c9.png!small)  

演示视频：<https://asciinema.org/a/207349>

### 工具要求

1、 Python 3.4+

2、 Linux、Windows、macOS和BSD

## 工具安装

运行下列命令使用pip安装：

    
    
    $ pip install pocsuite3

或点击【[这里](https://github.com/knownsec/pocsuite3/archive/master.zip)】直接下载源码ZIP压缩包并提取项目文件：

    
    
    $wget <https://github.com/knownsec/pocsuite3/archive/master.zip>
    
    $unzip master.zip

## 项目地址

【[GitHub传送门](https://github.com/knownsec/pocsuite3)】

【[官方网站](http://pocsuite.org/)】

【[参考文档](https://github.com/knownsec/pocsuite3/blob/master/docs)】

### 免责声明

未经事先双方同意，使用pocsuite攻击目标是非法的。

pocsuite仅用于安全测试目的。

***参考来源：[knownsec](https://github.com/knownsec/pocsuite3)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

