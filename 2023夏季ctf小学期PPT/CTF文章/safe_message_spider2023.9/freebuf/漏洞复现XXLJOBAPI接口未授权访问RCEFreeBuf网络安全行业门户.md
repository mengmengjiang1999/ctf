承影安全是齐安科技旗下安全研究团队专门负责的一个平台，专注于安全类攻防研究，会不定期输出一些相关的技术类文章，欢迎大家订阅！

## XXL-JOB描述

XXL-JOB是一个轻量级分布式任务调度平台，其核心设计目标是开发迅速、学习简单、轻量级、易扩展。现已开放源代码并接入多家公司线上产品线，开箱即用。

官方文档：https://www.xuxueli.com/xxl-job/

![](https://image.3001.net/images/20210205/1612510504_601cf5287d898d74e5f47.png!small)

##  **一、 漏洞详情**

此次漏洞核心问题是 GLUE 模式。XXL-JOB 通过“GLUE模式”支持多语言以及脚本任务，该模式任务特点如下：

> ● 多语言支持：支持 Java、Shell、Python、NodeJS、PHP、PowerShell……等类型。
>
> ● Web IDE：任务以源码方式维护在调度中心，支持通过 Web IDE 在线开发、维护。
>
> ● 动态生效：用户在线通过 Web IDE 开发的任务代码，远程推送至执行器，实时加载执行。

![](https://image.3001.net/images/20210205/1612510522_601cf53a0bf1a9573ef22.png!small)

如上图所示，如果在 GLUE 模式任务代码中写入攻击代码，推送到执行器执行即可造成远程攻击。

 **【漏洞描述】**

XXL-JOB的Restful API接口或RPC接口没有配置认证措施，未授权的攻击者可构造恶意请求，造成远程执行命令

 **【漏洞评级】**

高危

 **【受影响版本】**

XXL-JOB <= 2.2.0

##  **二、 环境搭建**

整体思路：源代码下载->Maven安装依赖->配置部署“调度中心”->配置部署“执行器项目”->完成部署

本地开发环境：Java8+Maven3.6

1\. Github下载源代码

地址：https://github.com/xuxueli/xxl-job/releases/tag/v2.2.0

![](https://image.3001.net/images/20210205/1612510539_601cf54b51baa7b0c2085.png!small)

 **2\. Maven下载所需要的依赖**

Idea打开解压后的源代码，自动会进行pom中的相关依赖安装，也可以在终端使用maven命令下载所需要的依赖

 **3\. 数据库配置**

调度数据库初始化SQL脚本位置为:

/xxl-job/doc/db/tables_xxl_job.sql

![](https://image.3001.net/images/20210205/1612510554_601cf55a41461b0da4e7b.png!small)

因为本地未安装mysql，故使用docker安装。

a) docker pull mysql:5.7

b) sudo docker run -p 3306:3306 --name mysql -e MYSQL_ROOT_PASSWORD=123456 -d
mysql:5.7

这样我们就启动了mysql容器，账号为root，密码为123456

使用navicat接连数据库

![](https://image.3001.net/images/20210205/1612510571_601cf56b1f54491d63a4a.png!small)可以点击左下角，完成测试连接。在导入的数据库右键，选择运行SQL文件，点击开始即可完成数据库的导入。

![](https://image.3001.net/images/20210205/1612510588_601cf57cd3f574b54fc06.png!small)

 **4\. 配置部署“调度中心”**

调度中心项目：xxl-job-admin

作用：统一管理任务调度平台上调度任务，负责触发调度执行，并且提供任务管理平台。可根据实际情况自行修改application.properties中的数据库配置

![](https://image.3001.net/images/20210205/1612510605_601cf58d92616bc0a0b41.png!small)

执行XxlJobAdminApplication启动调度中心

![](https://image.3001.net/images/20210205/1612510627_601cf5a3489011f782344.png!small)我们使用推荐的Springboot来管理执行器

![](https://image.3001.net/images/20210205/1612510641_601cf5b17701fc0fa47b2.png!small)查看配置文件，发现xxl.job.executor.logpath参数，我们可以新建或修改该路径，以防止程序执行出现问题。Mac新系统不存在data路径，发现使用mkdir创建路径发现失败，这是因为mac系统中关闭了Sip，使用sudo
mount -uw
/来解除Sip的限制。运行XxlJobExecutorApplication来启动执行器。浏览器打开//localhost:8080/，看到登入界面，确保启动成功，默认登录账号“admin/123456”

![](https://image.3001.net/images/20210205/1612510674_601cf5d26e264daec5f06.png!small)

注意点：

建议先创建/data/applogs/xxl-job，程序中多处配置文件使用该路径

修改调度中心数据库配置

Linux/Unix可使用lsof来查看端口占用情况，防止启动失败

调度中心和执行器可以根据实际情况分开部署

##  **三、漏洞复现**

查看官方文档可以看到执行器RESTful API中触发任务接口说明

![](https://image.3001.net/images/20210205/1612510696_601cf5e802e4f5bb18712.png!small)其中的任务运行模式有以下几种

![](https://image.3001.net/images/20210205/1612510711_601cf5f78948aff82c8c6.png!small)查看GulueTypeEnum源代码

![](https://image.3001.net/images/20210205/1612510726_601cf60648736d4cdb37a.png!small)所以我们利用Burpsuite构造我们的POC

![](https://image.3001.net/images/20210205/1612510740_601cf614ac6e657e616a1.png!small)

Tips：

修改glueSource时，如果执行未生效，请修改jobId

当重启项目时，发现端口启动异常，请关闭BurpSuite

由于 XXL-JOB 官方版本原生自带鉴权组件，开启后可保障系统底层通讯安全。XXL-JOB
作者表示正常情况下调度中心与执行器底层通讯是安全的，不存在远程命令漏洞。但如果执行器未开启访问令牌，会导致无法识别并拦截非法的调度请求。恶意请求方可以借助
GLUE 模式，推送恶意攻击代码实现远程攻击。因此，XXL-JOB 作者认为该问题本质上不属于 “漏洞”，官网版本提供了鉴权组件，开启即可进行防护。

##  **四、修复建议**

1\. 开启 XXL-JOB 自带的鉴权组件：官方文档中搜索 “xxl.job.accessToken”，按照文档说明启用即可。

2\. 端口访问限制：通过配置安全组限制只允许指定IP才能访问端口

##  **五、参考链接**

https://github.com/jas502n/xxl-job/tree/1.0

https://landgrey.me/blog/18/

https://mp.weixin.qq.com/s/jzXIVrEl0vbjZxI4xlUm-g

