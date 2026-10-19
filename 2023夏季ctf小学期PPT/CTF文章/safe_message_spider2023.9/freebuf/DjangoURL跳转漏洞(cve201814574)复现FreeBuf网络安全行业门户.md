Django是一个开放源代码的Web应用框架，由Python写成。采用了MTV的框架模式，即模型M，视图V和模版T。它最初是被开发来用于管理劳伦斯出版集团旗下的一些以新闻内容为主的网站的，即是CMS软件。并于2005年7月在BSD许可证下发布。

漏洞产生原因是如果设置了APPEND_SLASH=True并且初始URL没有以斜杠结尾，且在urlpatterns中找不到它，则通过在末尾附加斜杠来形成新的URL。简单来说就对于末尾没有添加
/ 的url且在urlpatterns中定义的url都匹配不上，就会添加上 / 后重新请求。

漏洞影响版本: Django1.11.15之前的1.11.x版本以及Django2.0.8之前的Django2.0.x版本

本文仅作漏洞复现记录与实现，利用流程如下:

1.漏洞环境

本环境采用vulhub搭建

执行以下命令完成环境搭建

cd vulhub/django/CVE-2018-14574/

docker-compose up -d

启动完毕后信息如下

漏洞链接: <http://192.168.101.152:8000/>

访问后如下图

![1616669183_605c69ff5a5b4cb2eb003.png!small](https://image.3001.net/images/20210325/1616669183_605c69ff5a5b4cb2eb003.png!small)

2.利用流程

直接访问链接 http://192.168.101.152:8000//www.baidu.com

![1616669377_605c6ac130c9599d45eeb.png!small](https://image.3001.net/images/20210325/1616669377_605c6ac130c9599d45eeb.png!small)

访问后就会跳转至百度

![1616669428_605c6af494bd1ec88129b.png!small](https://image.3001.net/images/20210325/1616669428_605c6af494bd1ec88129b.png!small)

结束。

