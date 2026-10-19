## NeuVector简介

NeuVector是一款开源容器网络安全平台，其主要功能如下：

  * 安全扫描包括镜像扫描、主机扫描、平台扫描、基线扫描、合规检查
  * 网络防火墙：可视化网络连接接图，支持一键隔离
  * 容器运行时安全：基于学习规则、自定义规则对容器运行时进行安全保护

部署要求（注意：部署前请设置好最高使用资源限制）：

 **Component**

|

 **# of Instances**

|

 **Recommended vCPU**

|

 **Minimum Memory**

|

 **Notes**  
  
---|---|---|---|---  
  
Controller

|

min. 1  
3 for HA (odd # only)

|

1

|

1GB

|

vCPU core may be shared  
  
Enforcer

|

1 per node/VM

|

1+

|

1GB

|

One or more dedicated vCPU for higher network throughput in Protect mode  
  
Scanner

|

min. 1  
2+ for HA/Performance

|

1

|

1GB

|

CPU core may be shared for standard workloads.  
Dedicate 1 or more CPU for high volume (10k+) image scanning.  
Registry image scanning is performed by the scanner and managed by the
controller and the image is pulled by the scanner and expanded in memory.  
The minimum memory recommendation assumes images to be scanned are not larger
than .5GB.  
When scanning images larger than 1GB, scanner memory should be calculated by
taking the largest image size and adding .5GB.  
Example - largest image size = 1.3GB, the scanner container memory should be
1.8GB  
  
Manager

|

min 12+ for HA

|

1

|

1GB

|

vCPU may be shared  
  
## 利用Rancher单集群部署NeuVector

> 备注：rancher搭建可以参考官方文档https://rancher.com/docs/rancher/latest/zh/

### 1.创建命名空间neuvector

实验环境为4nodes，设置命名空间资源最高限制，（8C8GB）

 **类型**

|

 **vCPU**

|

 **内存**

|

pod数量  
  
---|---|---|---  
  
控制器Controller

|

1C

|

1GB

|

1  
  
执行器Enforcer

|

1C*4

|

1GB*4

|

4  
  
扫描器Scanner

|

1*2

|

1GB*2

|

2  
  
管理器Manager

|

1C

|

1GB

|

1  
  
rancher创建命名空间neuvector，并做好资源限制

![1684894142_646d71be452cff891cfe8.png!small?1684894142749](https://image.3001.net/images/20230524/1684894142_646d71be452cff891cfe8.png!small?1684894142749)

### 2.打开rancher应用商店，搜索neuvector 直接启动

![1684894180_646d71e4d351bfab1b489.png!small?1684894181293](https://image.3001.net/images/20230524/1684894180_646d71e4d351bfab1b489.png!small?1684894181293)

### 3.稍等片刻，启动完成

![1684894215_646d720773d65458c6d58.png!small?1684894215863](https://image.3001.net/images/20230524/1684894215_646d720773d65458c6d58.png!small?1684894215863)

## 功能介绍

### 1 概览

包括风险评分、暴露pod统计、安全事件统计、漏洞统计、流量统计：

![1684894289_646d725171f7ea69929ef.png!small?1684894290083](https://image.3001.net/images/20230524/1684894289_646d725171f7ea69929ef.png!small?1684894290083)

### 2.网络活动

可视化网络连接图

![1684894375_646d72a759a056a675d3b.png!small?1684894375792](https://image.3001.net/images/20230524/1684894375_646d72a759a056a675d3b.png!small?1684894375792)

可设置pod防护策略（学习、观察、保护），支持一键网络隔离

![1684894398_646d72be14a0350ad4db6.png!small?1684894398405](https://image.3001.net/images/20230524/1684894398_646d72be14a0350ad4db6.png!small?1684894398405)

支持网络流量抓包，pcap格式下载

![1684894421_646d72d5b6c68c690f142.png!small?1684894422022](https://image.3001.net/images/20230524/1684894421_646d72d5b6c68c690f142.png!small?1684894422022)

### 3.资产管理

提供平台、命名空间、主机、容器、就镜像库、系统组件维度的资产管理

![1684894470_646d73063b4567439ccc5.png!small?1684894470732](https://image.3001.net/images/20230524/1684894470_646d73063b4567439ccc5.png!small?1684894470732)

在资产管理模块中支持相对应的安全扫描，如镜像扫描、宿主机扫描、容器平台扫描等

![1684894489_646d7319ed5a02fcffa36.png!small?1684894490393](https://image.3001.net/images/20230524/1684894489_646d7319ed5a02fcffa36.png!small?1684894490393)

![1684894519_646d7337cc625aec47ae5.png!small?1684894520153](https://image.3001.net/images/20230524/1684894519_646d7337cc625aec47ae5.png!small?1684894520153)

### 4 策略

策略模块主要提供策略配置、资产组管理（组）、网络规则、应对规则、DLP、WAF。

 **a.准入控制：** 可依据镜像漏洞情况、镜像仓库来源、容器启动权限等要求，设置容器部署准入权限，限制或监控不符合要求的pod部署启动

![1684894554_646d735ad1cb49993e286.png!small?1684894555176](https://image.3001.net/images/20230524/1684894554_646d735ad1cb49993e286.png!small?1684894555176)

  

 **b.组：** 系统默认生成不同维度的组：nodes、containers等，我们可以根据需求创建组，组内统一应用安全策略

![1684894585_646d7379dd31181630939.png!small?1684894586670](https://image.3001.net/images/20230524/1684894585_646d7379dd31181630939.png!small?1684894586670)

 **c.网络规则：** 此处可针对上述的组（可以是pod、ns、contains等）配置网络防火墙规则

![1684894614_646d739659751259ceb46.png!small?1684894614913](https://image.3001.net/images/20230524/1684894614_646d739659751259ceb46.png!small?1684894614913)

 **d.应对规则:** 针对安全事件、合规事件、注入控制等设置，应对处理规则，包括断网、告警、隔离

![1684894633_646d73a9e8c573b964e43.png!small?1684894635456](https://image.3001.net/images/20230524/1684894633_646d73a9e8c573b964e43.png!small?1684894635456)

 **e.DLP检测器：** 自定义规则检测网络流量中是否存在敏感数据

![1684894656_646d73c0bab0ed2fb7f57.png!small?1684894657153](https://image.3001.net/images/20230524/1684894656_646d73c0bab0ed2fb7f57.png!small?1684894657153)

 **f.WAF检测器** ：自定义规则检测网络流量中是否存在web攻击

![1684894676_646d73d4d088f79116161.png!small?1684894677786](https://image.3001.net/images/20230524/1684894676_646d73d4d088f79116161.png!small?1684894677786)

### 5 安全隐患

此模块记录各类安全扫描结果，包括漏洞、合规扫描等。

![1684894719_646d73ff8afaf89b11e8a.png!small?1684894720311](https://image.3001.net/images/20230524/1684894719_646d73ff8afaf89b11e8a.png!small?1684894720311)

### 6 通知

通知主要有安全事件、风险报告、事件，其中安全事件为容器运行时事件；风险报告为安全扫描报告以及基础监控告警；事件为NeuVector平台日志。

![1684894746_646d741ac11692568fd78.png!small?1684894747331](https://image.3001.net/images/20230524/1684894746_646d741ac11692568fd78.png!small?1684894747331)

### 7 设置

设置包括用户角色管理、第三方登录设置、系统配置

![1684894781_646d743d48d3c23a04bb8.png!small?1684894781535](https://image.3001.net/images/20230524/1684894781_646d743d48d3c23a04bb8.png!small?1684894781535)

系统配置：可对默认策略进行配置、系统日志收集配置、以及多集群使用配置等

![1684894804_646d7454dd568a9cae11d.png!small?1684894805395](https://image.3001.net/images/20230524/1684894804_646d7454dd568a9cae11d.png!small?1684894805395)

## 多集群统一管理

### 1.多集群配置

a.集群管理可选择接入主机群、也可以成为主集群

![1684894885_646d74a5720b1d7292fe5.png!small?1684894885756](https://image.3001.net/images/20230524/1684894885_646d74a5720b1d7292fe5.png!small?1684894885756)

b.升级主集群，对外提供11443端口通信

![1684894921_646d74c90ffef4805aa3b.png!small?1684894921348](https://image.3001.net/images/20230524/1684894921_646d74c90ffef4805aa3b.png!small?1684894921348)

c.生成令牌

![1684894958_646d74ee2addcd571f496.png!small?1684894958308](https://image.3001.net/images/20230524/1684894958_646d74ee2addcd571f496.png!small?1684894958308)

d.子集群加入到集群管理

![1684895031_646d75376952944687ce0.png!small?1684895031688](https://image.3001.net/images/20230524/1684895031_646d75376952944687ce0.png!small?1684895031688)

加入成功

![1684895069_646d755dd9979e9ef27d6.png!small?1684895070127](https://image.3001.net/images/20230524/1684895069_646d755dd9979e9ef27d6.png!small?1684895070127)

### 2.多集群管理功能

a.支持切换集群，实现统一入口管理多个集群NuaVector控制台

![1684895140_646d75a4852481e20e77d.png!small?1684895141066](https://image.3001.net/images/20230524/1684895140_646d75a4852481e20e77d.png!small?1684895141066)

b.集群全局策略管理

![1684895172_646d75c48fdce89bd2747.png!small?1684895172999](https://image.3001.net/images/20230524/1684895172_646d75c48fdce89bd2747.png!small?1684895172999)

## 事件统一订阅案例

下面举例如何统一订阅所有集群安全事件

![1684895227_646d75fb882bfd84cd81d.png!small?1684895227893](https://image.3001.net/images/20230524/1684895227_646d75fb882bfd84cd81d.png!small?1684895227893)

1.编写测试webhook，接受事件推送

> from flask import Flask, request
>
> app = Flask(__name__)
>
> @app.route('/webhook', methods=['POST'])  
> def webhook():  
> body = request.get_data().decode('utf-8')  
> print('Received webhook body:', body)  
> return 'Webhook received successfully'
>
> if __name__ == '__main__':  
> app.run(host='0.0.0.0', port=5000)

2.通过配置webhook获取全集群事件

![1684895539_646d77336c1fab51b2f63.png!small?1684895539700](https://image.3001.net/images/20230524/1684895539_646d77336c1fab51b2f63.png!small?1684895539700)

3.指定监听事件

![1684895563_646d774b113fa784620d7.png!small?1684895563512](https://image.3001.net/images/20230524/1684895563_646d774b113fa784620d7.png!small?1684895563512)

  

4.配置事件推送

![1684895630_646d778ec3d081359365f.png!small?1684895631021](https://image.3001.net/images/20230524/1684895630_646d778ec3d081359365f.png!small?1684895631021)

5.启动webhook脚本，完成事件监听

![1684895779_646d78237ecbb268e7b55.png!small?1684895781506](https://image.3001.net/images/20230524/1684895779_646d78237ecbb268e7b55.png!small?1684895781506)

以上是NeuVector集群事件推送的方法，在日常运营中我们可以推送到SIEM等安全平台，进行统一事件管理。

## 总结

  1. 安装和配置：NeuVector的安装和配置相对简单。如果是Rancher管理的集群支持应用市场一键部署。

  2. 安全扫描：NeuVector提个不同维度安全扫描，包括k8s平台、node节点、pod、镜像等

  3. 容器运行时保护：NeuVector使用行为学习和行为分析技术来识别并阻止恶意容器活动，如未经授权的网络通信、异常进程、文件篡改和攻击行为。

  4. 安全策略和规则：NeuVector自带多种安全规则，同事允许用户自定义规则，使用体验十分灵活。

本文主要记录笔者使用NueVector心得，如果疏漏欢迎指出，谢谢！

参考链接：：<https://open-docs.neuvector.com/>

