## 一、前言

**JIRA是Atlassian公司出品的项目与事务跟踪工具，是目前比较流行的基于JAVA架构的管理系统。被广泛应用于缺陷跟踪、客户服务、需求收集、流程审批、任务跟踪、项目跟踪和敏捷管理等工作领域。**

## 二、漏洞简介

JIRA Server和 Data
Center在ContactAdministrators和SendBulkMail操作中存在服务器端模板注入漏洞。若满足以下条件之一，即可触发该漏洞：

> 当JIRA中配置了SMTP，并且启用了联系人管理员表单时；
>
> 当JIRA中配置了SMTP，并且攻击者拥有“JIRA管理员”访问权限时。

网藤CRS/ARS产品已全面支持该漏洞的检测与验证，网藤用户可直接登陆[www.riskivy.com](http://www.riskivy.com)
进行验证。

## 三、漏洞危害

经斗象安全应急响应团队分析，在任意一种情况下成功利用该漏洞，攻击者即可在运行易受攻击版本的JIRA Server或Data
Center的系统上远程执行代码。

## 四、影响范围

产品

> JIRA Server和JIRA Data Center

版本

> 4.4.x
>
> 5.x.x
>
> 6.x.x
>
> 7.0.x
>
> 7.1.x
>
> 7.2.x
>
> 7.3.x
>
> 7.4.x
>
> 7.5.x
>
> 7.6.14之前的7.6.x版本（7.6.x的固定版本）
>
> 7.7.x
>
> 7.8.x
>
> 7.9.x
>
> 7.10.x
>
> 7.11.x
>
> 7.12.x
>
> 7.13.5之前的7.13.x版本（7.13.x的固定版本）
>
> 8.0.3之前的8.0.x版本（8.0.x的固定版本）
>
> 8.1.2之前的8.1.x版本（8.1.x的固定版本）
>
> 8.2.3之前的8.2.x版本（8.2.x的固定版本）

组件

> JIRA Server和JIRA Data Center

## 五、修复方案

1、更新JIRA版本至8.2.3、8.1.2、8.0.3、7.13.5、7.6.14中的任一版本

8.2.3下载链接：

<https://www.atlassian.com/software/jira/download>

8.1.2下载链接：

<https://www.atlassian.com/software/jira/update>

8.0.3下载链接：

<https://www.atlassian.com/software/jira/update>

7.13.5下载链接：

<https://www.atlassian.com/software/jira/update>

7.6.14下载链接：

<https://www.atlassian.com/software/jira/update>

2、禁用联系人管理员表单。

3、通过直接拒绝反向代理，负载均衡器或Tomcat中的访问来实现阻止/secure/admin/SendBulkMail!default.jspa
访问端点。

## 六、参考

> <https://confluence.atlassian.com/jira/jira-security-> advisory-2019-07-10-973486595.html>

以上是本次高危漏洞预警的相关信息，如有任何疑问或需要更多支持，可通过以下方式与我们取得联系。

联系电话：400-156-9866

Email：help@tophant.com

