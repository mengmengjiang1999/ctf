## **一、说明**

###  **1.1** **相关概念说明**

SEM，security event management，安全事件管理，指对事件进行实时监控，收集信息差展生通知和告警的行为。

SIM，security information management，安全信息管理，指对SEM收集和产生的数据进行长期保存以供历史和趋势分析的行为。

SIEM，security information and event management，安全信息和事件管理，即SEM和SIM的结合体。

SOC，security operations center，安全运营中心。

TI，Threat Intelligence，威胁情报。SOC偏重内部网络态势感知，而TI偏重于外部网络态势感知比如新出了什么漏洞、病毒、安全事件等等。

SA，situational awareness，态势感知。

SRC，Security Response Center，安全响应中心。狭义上只是一个提交产品漏洞的入口，但广义上包含各种安全系统及系统维护人员。

他们的关系是：SRC > SA >= SOC [ + TI ] >= SIEM = SEM+SIM。

一款典型的SIEM产品具有以下功能：资产发现、漏洞扫描、入侵检测、日志存储分析和可视化展示。

### 1.2 OSSIM是什么

[OSSIM](https://www.alienvault.com/products/ossim)是SIEM的代表性产品，在产品形式上和Kali类似是一个基于Debain进行二次开发的Linux发行版，当前5.7.4版本基于Dibian
8(jessie)。

OSSIM使用Nmap等实现资产发现、使用Nessus等实现漏洞扫描、使用Snort等实现入侵检测、使用MySQL等进行数据存储，自己实现的部分主要是工具、数据整合和可视化展示。

## 二、OSSIM安装

### 2.1 下载

ISO文件下载地址：<https://www.alienvault.com/products/ossim/download>

### 2.2 硬件资源需求

基础配置：CPU----2*2，内存----8G，硬盘----20G以上

### 2.3 安装准备

VMware就和普通虚拟机一样，创建Linux虚拟机设置好ISO文件即可。不过要注意操作系统选Debian（第几版本倒影响不大）。

物理机安装用UltraISO等工具制作一下启动盘，然后从U盘启动即可，后续安装步骤就完全和虚拟机安装一样。

### 2.4 安装过程

Linux安装过程大同小异都是选语言、选时区、设密码这几步，下面简单截一下图。

选OSSIM。OSSIM包含服务器组件+Sensor，Sensor相当于一个Client。

![1628047945_610a0a49eaa589aaf77d8.png!small?1628047904513](https://image.3001.net/images/20210804/1628047945_610a0a49eaa589aaf77d8.png!small?1628047904513)

语言选择，简体中文支持似乎说不太好，直接英文即可。

![1628047971_610a0a631893315e9a222.png!small?1628047929611](https://image.3001.net/images/20210804/1628047971_610a0a631893315e9a222.png!small?1628047929611)

地区选择中国。

![1628047980_610a0a6c564ffb75489c2.png!small?1628047938848](https://image.3001.net/images/20210804/1628047980_610a0a6c564ffb75489c2.png!small?1628047938848)

操作系统编码，默认即可

![1628047987_610a0a73e8e8442440229.png!small?1628047946542](https://image.3001.net/images/20210804/1628047987_610a0a73e8e8442440229.png!small?1628047946542)

键盘，默认即可

![1628047997_610a0a7d350d68efdc944.png!small?1628047955728](https://image.3001.net/images/20210804/1628047997_610a0a7d350d68efdc944.png!small?1628047955728)

下几步是网络设置，为了避免安装完后还要手动纠正网络这里最好正确填写要设置的ip、掩码、网关。

![1628048010_610a0a8a3455772631125.png!small?1628047968744](https://image.3001.net/images/20210804/1628048010_610a0a8a3455772631125.png!small?1628047968744)

子网掩码

![1628048018_610a0a92dd549bab2e63b.png!small?1628047977469](https://image.3001.net/images/20210804/1628048018_610a0a92dd549bab2e63b.png!small?1628047977469)

网关

![1628048025_610a0a9985946550f7bec.png!small?1628047984051](https://image.3001.net/images/20210804/1628048025_610a0a9985946550f7bec.png!small?1628047984051)

DNS，最多可以设置3个，使用空格隔开即可

![1628048032_610a0aa06bc05440a43e4.png!small?1628047990933](https://image.3001.net/images/20210804/1628048032_610a0aa06bc05440a43e4.png!small?1628047990933)

root用户密码

![1628048039_610a0aa7dff43d056b0c0.png!small?1628047998444](https://image.3001.net/images/20210804/1628048039_610a0aa7dff43d056b0c0.png!small?1628047998444)

物理机安装时有划分磁盘的操作，虚拟机直接进入安装。

![1628048046_610a0aae02224c31f5d99.png!small?1628048004493](https://image.3001.net/images/20210804/1628048046_610a0aae02224c31f5d99.png!small?1628048004493)

上边的安装过程需要二三十分钟，安装过程可能会出现黑屏，敲击任意键唤醒屏幕即可。

安装的最后会运行cdsetup的程序，这个程序主要是创建OSSIM相关的数据库。

![1628048055_610a0ab77ab693bc86c49.png!small?1628048013987](https://image.3001.net/images/20210804/1628048055_610a0ab77ab693bc86c49.png!small?1628048013987)

## 三、登录使用

### 3.1 操作系统登录使用

系统安装完成后，自动重启进入界面如下，使用安装时自己设定的密码登录即可

（如果虚拟机没有安装过程而是直接运行了iso那默认是root/toor）

![1628048064_610a0ac01f0d86f872ef0.png!small?1628048022585](https://image.3001.net/images/20210804/1628048064_610a0ac01f0d86f872ef0.png!small?1628048022585)

登录后进入AlienVault Setup界面如下，这其实是一个名为ossim-setup的程序。

![1628048073_610a0ac9c2986838290ba.png!small?1628048032235](https://image.3001.net/images/20210804/1628048073_610a0ac9c2986838290ba.png!small?1628048032235)

基本配置在AlienVault Setup进行操作即可，如果想要进入系统，那就下移到”Jailbreak System“菜单进入

![1628048080_610a0ad07ec8d0ac05e35.png!small](https://image.3001.net/images/20210804/1628048080_610a0ad07ec8d0ac05e35.png!small)

选择Yes回车进入

![1628048137_610a0b09e15845f425eb9.png!small?1628048096408](https://image.3001.net/images/20210804/1628048137_610a0b09e15845f425eb9.png!small?1628048096408)

![1628048147_610a0b138be464b558734.png!small?1628048106083](https://image.3001.net/images/20210804/1628048147_610a0b138be464b558734.png!small?1628048106083)

如果想回到AlienVault Setup，退出重新登录即可，当然也可以直接输入ossim-setup。

### 2.2 Web登录使用

在登录界面和AlienVault Setup界面都可以看到有提示ossim的url，直接在浏览器访问该链接即可。

首次登录需要设置admin的密码，按照提示设置满足密码强度的密码即可

![1628048161_610a0b216940f21e25813.png!small?1628048120026](https://image.3001.net/images/20210804/1628048161_610a0b216940f21e25813.png!small?1628048120026)

然后会自动跳转登录界面，使用admin和上边设定的密码进入即可。

![1628048170_610a0b2a18e9ffebe5c72.png!small?1628048128587](https://image.3001.net/images/20210804/1628048170_610a0b2a18e9ffebe5c72.png!small?1628048128587)

首次登录需要进行几步设置，不过基本都直接NEXT即可。

![1628048175_610a0b2fd9f394902bee2.png!small?1628048134439](https://image.3001.net/images/20210804/1628048175_610a0b2fd9f394902bee2.png!small?1628048134439)

选择网卡，直接NEXT

![1628048183_610a0b37bc771244e3aa2.png!small?1628048142382](https://image.3001.net/images/20210804/1628048183_610a0b37bc771244e3aa2.png!small?1628048142382)

当前扫描到的资产，直接NEXT

![1628048198_610a0b46239cb70da4155.png!small?1628048156777](https://image.3001.net/images/20210804/1628048198_610a0b46239cb70da4155.png!small?1628048156777)

安装基于主机的入侵检测系统。windows主机需要输入域管理账号Linux机器需要输入主机账号，然后在在右边选中机器，然后点击DEPLOY进行安装。

我们不安装，直接NEXT。

![1628048205_610a0b4d5c1b3cf3cfd6d.png!small?1628048163977](https://image.3001.net/images/20210804/1628048205_610a0b4d5c1b3cf3cfd6d.png!small?1628048163977)

日志管理。可直接SKIP THIS STEEP，后期配置。

![1628048214_610a0b56ccd10af972720.png!small?1628048173391](https://image.3001.net/images/20210804/1628048214_610a0b56ccd10af972720.png!small?1628048173391)

OTX即Open Threat Exchange，威胁情报交换，自己注册个账号去登录即可。

![1628048222_610a0b5e8c5d6f305812b.png!small?1628048181175](https://image.3001.net/images/20210804/1628048222_610a0b5e8c5d6f305812b.png!small?1628048181175)

进入OSSIM

![1628048230_610a0b660257453a7b891.png!small?1628048188563](https://image.3001.net/images/20210804/1628048230_610a0b660257453a7b891.png!small?1628048188563)

此时进入OSSIM面板

![1628048236_610a0b6ccab403613e332.png!small?1628048195456](https://image.3001.net/images/20210804/1628048236_610a0b6ccab403613e332.png!small?1628048195456)

dashboards菜单----可视化图表

analysis----用于筛选查看收集到的数据

environment----资产清单、漏洞扫描、流量监控等重要功能就在这里

reports----顾名思义就是生成和查看各种报告的地方

configuration----web系统匹置菜单

