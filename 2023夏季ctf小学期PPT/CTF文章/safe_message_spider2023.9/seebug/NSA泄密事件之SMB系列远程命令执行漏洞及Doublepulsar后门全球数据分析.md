来源: [**ZoomEye**](https://www.zoomeye.org/lab/ms17-010)

[下载详细报告](https://www.zoomeye.org/static/articles/NSA%E6%B3%84%E5%AF%86%E4%BA%8B%E4%BB%B6%E4%B9%8BSMB%E7%B3%BB%E5%88%97%E8%BF%9C%E7%A8%8B%E5%91%BD%E4%BB%A4%E6%89%A7%E8%A1%8C%E6%BC%8F%E6%B4%9E%E5%8F%8ADoublepulsar%E5%90%8E%E9%97%A8%E5%85%A8%E7%90%83%E6%95%B0%E6%8D%AE%E5%88%86%E6%9E%90_v3.0.pdf)（版本：3.0）

### 背景

继去年 8 月份黑客组织 Shadow Brokers 放出第一批 NSA “方程式小组”内部黑客工具后，2017 年 4 月 14 日，Shadow
Brokers 再次公布了一批新的 NSA 黑客工具，其中包含了一个攻击框架和多个 Windows 漏洞利用工具。攻击者利用这些漏洞可以远程获取
Windows 系统权限并植入后门。

针对此次泄露的漏洞，微软提前发布了安全公告 MS17-010，修复了泄露的多个 SMB 远程命令执行漏洞。由于此次泄露的漏洞覆盖了大部分常见的
Windows 版本(包括微软不再提供更新服务的 Windows XP 和 Windows Server 2003)，网络空间中仍然存在大量可被入侵的设备。

### 数据分析

事件发生后，ZoomEye 网络空间探测引擎针对互联网空间中 MS17-010 SMB 远程命令执行漏洞影响及 Doublepulsar
后门植入的情况进行持续探测和跟踪，截至 2017 年 5 月 3 日，已完成两轮探测。

#### Doublepulsar 后门

##### 第一轮探测

2017 年 4 月 24 日，针对 Doublepulsar 后门植入情况的第一轮探测结束，全球共有 98,309 台设备被植入 Doublepulsar
后门，其国家分布如下:
![](https://images.seebug.org/content/images/2017/05/doublepulsar_geo_1.png-w331s)
受影响国家 TOP 10：
![](https://images.seebug.org/content/images/2017/05/doublepulsar_country_1.png-w331s)
受影响中国省市 TOP 10：
![](https://images.seebug.org/content/images/2017/05/doublepulsar_china_1.png-w331s)

##### 第二轮探测

2017 年 5 月 2 日，第二轮针对 Doublepulsar 后门植入情况的探测结束，全球共有 107,163 台设备被植入后门，其国家分布如下：
![](https://images.seebug.org/content/images/2017/05/doublepulsar_geo_2.png-w331s)
受影响国家 TOP 10：
![](https://images.seebug.org/content/images/2017/05/doublepulsar_country_2.png-w331s)
受影响中国省市 TOP 10：
![](https://images.seebug.org/content/images/2017/05/doublepulsar_china_2.png-w331s)

##### 第三轮探测

2017 年 5 月 7 日，第三轮针对 Doublepulsar 后门植入情况的探测结束，全球共有 26,975 台设备被植入后门，其国家分布如下：
![](https://images.seebug.org/content/images/2017/05/doublepulsar_geo_3.png-w331s)
受影响国家 TOP 10：
![](https://images.seebug.org/content/images/2017/05/doublepulsar_country_3.png-w331s)
受影响中国省市 TOP 10：
![](https://images.seebug.org/content/images/2017/05/doublepulsar_china_3.png-w331s)

##### 对比分析

各国被植入 Doublepulsar 后门的设备数量对比：
![](https://images.seebug.org/content/images/2017/05/doublepulsar_compare_world-1.png-w331s)
我国各省市被植入 Doublepulsar 后门的设备数量对比：
![](https://images.seebug.org/content/images/2017/05/doublepulsar_compare_china-1.png-w331s)

#### MS17-010 漏洞

##### 第一轮探测

2017 年 4 月 26 日，第一轮 MS17-010 SMB 远程命令执行漏洞探测结束，全球共有 101,821 台设备存在 MS17-010 SMB
远程命令执行漏洞。其全球分布如下：
![](https://images.seebug.org/content/images/2017/05/ms17-010_geo_1.png-w331s)
受影响国家 TOP 10：
![](https://images.seebug.org/content/images/2017/05/ms17-010_country_1.png-w331s)
受影响中国省市 TOP 10：
![](https://images.seebug.org/content/images/2017/05/ms17-010_china_1.png-w331s)

##### 第二轮探测

2017 年 5 月 2 日，第二轮针对 MS17-010 漏洞影响情况的探测结束，全球尚有 65,966 台设备受到，其分布如下：
![](https://images.seebug.org/content/images/2017/05/ms17-010_geo_2.png-w331s)
受影响国家 TOP 10：
![](https://images.seebug.org/content/images/2017/05/ms17-010_country_2.png-w331s)
受影响中国省市 TOP 10：
![](https://images.seebug.org/content/images/2017/05/ms17-010_china_2.png-w331s)

##### 第三轮探测

2017 年 5 月 7 日，第三轮针对 MS17-010 漏洞影响情况的探测结束，全球共有 40,347 台设备受到影响，其分布如下：
![](https://images.seebug.org/content/images/2017/05/ms17-010_geo_3.png-w331s)
受影响国家 TOP 10：
![](https://images.seebug.org/content/images/2017/05/ms17-010_country_3.png-w331s)
受影响中国省市 TOP 10：
![](https://images.seebug.org/content/images/2017/05/ms17-010_china_3.png-w331s)

##### 对比分析

各国存在 MS17-010 漏洞的设备数量对比：
![](https://images.seebug.org/content/images/2017/05/ms17-010_compare_world-1.png-w331s)
我国各省市存在 MS17-010 漏洞的设备数量对比：
![](https://images.seebug.org/content/images/2017/05/ms17-010_compare_china-1.png-w331s)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/299/>

