![1.png](https://image.3001.net/images/20190517/1558024976_5cdd9310c09e9.png!small)

## 工具介绍

 **PacBot，全名为“Policy as Code
Bot”，它是一款针对云环境的持续性安全监控平台。在PacBot中，安全策略与合规性策略均通过代码实现。PacBot发现的所有资源都将根据这些策略来进行安全评估，以衡量策略的一致性。**

**PacBot的自动修复框架可以通过预定义操作来自动响应违规操作。PacBot具有强大的可视化功能，并简化了安全合规性方面的视图界面，以便研究人员分析和修正违反安全策略的行为。PacBot不仅是一个云环境配置检测工具，它更是一个通用平台，可以对任何域名进行持续的安全合规性监控并报告异常。**

## 额外功能

PacBot基于插件的数据收集架构允许我们从多个数据源收集数据，PacBot的插件系统可以从Qualys漏洞评估平台、BitBucket、趋势科技深度安全平台、TripWire、Venafi
Certificate
Management、RedhatSatellite、Spacewalk、ActiveDirectory以及其他一些自定义的内部解决方案中提取数据。当然了，我们也在致力于开源这些插件和相关工具。大家也可以根据这些插件来编写数据收集规则，以更加全面地了解自己的生态系统，而不仅限于云计算环境中的错误配置。

## 演示视频

## PacBot核心功能

1.持续安全合规性评估

2.详细的审计报告

3.自动修复策略冲突

4.全方位搜索/收集资源

5.简化策略冲突跟踪

6.自助服务门户站点

7.自定义策略和自动修复操作

8.动态资产分组检测

9.异常管理

10.电子邮件摘要

11.支持多个AWS账户

12.全自动安装程序

13.可定制的仪表盘

14.OAuth支持

15.集成Azure AD登录

16.基于角色的访问控制

17.资产360度安全评估

### 技术栈

1.前端：Angular

2.后端：API、任务

规则：Java

3.安装工具：Python和Terraform

## PocBot仪表盘&小工具

1.资产选择小工具

![2.png](https://image.3001.net/images/20190517/1558025005_5cdd932db6177.png!small)

2.安全合规性仪表盘

![3.png](https://image.3001.net/images/20190517/1558025023_5cdd933f61192.png!small)![4.png](https://image.3001.net/images/20190517/1558025023_5cdd933f58cd2.png!small)

3.策略合规性界面-S3 Bucket公共读取访问：

![5.png](https://image.3001.net/images/20190517/1558025037_5cdd934d4dd4b.png!small)

4.策略合规性趋势图：

![6.png](https://image.3001.net/images/20190517/1558025044_5cdd9354c487e.png!small)

5.资产仪表盘：

![7.png](https://image.3001.net/images/20190517/1558025058_5cdd9362c0f1e.png!small)![8.png](https://image.3001.net/images/20190517/1558025058_5cdd9362c5720.png!small)

6.资产细节：

![9.png](https://image.3001.net/images/20190517/1558025071_5cdd936f0cd7d.png!small)

7.Linux服务器季度补丁合规页面：

![10.png](https://image.3001.net/images/20190517/1558025080_5cdd93783a179.png!small)

8.Omni搜索页面：

![11.png](https://image.3001.net/images/20190517/1558025098_5cdd938a2df31.png!small)![12.png](https://image.3001.net/images/20190517/1558025096_5cdd93881553c.png!small)

9.小工具：

![13.png](https://image.3001.net/images/20190517/1558025107_5cdd939342c8f.png!small)

## 工具安装

1.克隆项目至本地：

    
    
    git clone git@github.com:tmobile/pacbot.git

2.切换至pacbot-installer目录；

3.创建settings/local.py文件（拷贝settings/default.local.py）

4.使用下列数据更新settings/local.py文件：

    
    
    VPCID
    
    VPCCIDR
    
    SUBNETIDS (2 Subnets are required. Both the subnets should not be in the same AZ.)

5.运行安装工具：

    
    
    sudo python3 manager.py install

### 默认用户凭证如下：

管理员用户：admin@pacbot.org / pacman

随机用户：user@pacbot.org / user

详细安装文档及依赖组件：【[安装文档](https://github.com/tmobile/pacbot/wiki/Install)】

## 项目地址

PacBot：【[GitHub传送门](https://github.com/tmobile/pacbot)】

***参考来源：[tmobile](https://github.com/tmobile/pacbot)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

