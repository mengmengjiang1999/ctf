## 系列文章

> [自己动手搭建信息安全可视化平台](https://www.freebuf.com/articles/es/251427.html)

续文1，小z介绍了最基础的资产模块 基本完成了一个完整的从数据输入到可视化呈现的最简单过程。就如同下图介绍，splunk支持几乎所有可以产生数据的地方。

![](https://image.3001.net/images/20201208/1607412016_5fcf2930a7566b68cec3c.png!small)

后续将介绍几种接入平台的方式及简单的可视化效果及安全场景，本文介绍Missle Map的搭建过程。

syslog是很多设备都支持的 小z先拿这个进行测试。作为可视化平台，小z想到了<https://www.fireeye.com/cyber-map/threat-map.html>，能否尝试实现这种类似的动态效果呢？这个比资产模块略微复杂一些。

场景，服务器外联

1.场景说明:服务器由于各种各样的原因允许外联，这是是内网安全很大的一个风险点。

2.数据源：出口负载均衡syslog

3.app插件:<https://splunkbase.splunk.com/app/3511/>

![](https://image.3001.net/images/20201201/1606804008_5fc5e228cd0c5cc88ab3a.png!small)

4.配置流程:解析过程

新建index 设置-索引-新建索引-输入索引名称ad

![](https://image.3001.net/images/20201201/1606803959_5fc5e1f74ad716dcf39c4.png!small)

配置syslog:这个每个设备大同小异，配置日志服务器的ip及日志收集端口号，这里用的udp

配置数据输入udp新增 这里设置udp的578端口作为接收syslog的端口

![](https://image.3001.net/images/20201201/1606804204_5fc5e2ec270bf8fa7e13e.png!small)

索引选择ad用于接收来自出口负载均衡的syslog

![](https://image.3001.net/images/20201201/1606804144_5fc5e2b01664abf66b543.png!small)

搜索 index=ad 关键字过滤

导入后原始的数据格式 自动过滤出原始数据

![](https://image.3001.net/images/20201201/1606804426_5fc5e3ca09a6b4876c9b3.png!small)

有了数据怎样展示出来？假设已经安装了missle map的app，参考missle map的语法规则

语法规则

![](https://image.3001.net/images/20201201/1606801877_5fc5d9d510b726b489cc5.png!small)

start_lat 起

