本文由东塔网络安全学院-10期班学员-yzj投稿。

条件：

1、需要74CMS_v5.0.1版本环境

2、需要登录后台管理账户

## 一、搭建环境

1、下载74CMS_v5.0.1安装包：

![](https://image.3001.net/images/20210108/1610090190_5ff806ce45fbc54eb33f8.png!small)

2、在本地使用PHPstudy搭建环境

a.访问upload/install.php

![](https://image.3001.net/images/20210108/1610090198_5ff806d677f770a743363.png!small)

b.点击同意后，查看所有权限都为可读写后直接点击下一步

![](https://image.3001.net/images/20210108/1610090210_5ff806e2ee65de19b96d0.png!small)

c.点击下一步后，设置对应用户名，密码和数据库名称，地区，邮箱之类的信息即可

![](https://image.3001.net/images/20210108/1610090219_5ff806eb2769c7cc0cae1.png!small)

![](https://image.3001.net/images/20210108/1610090257_5ff807115c24b07fac22f.png!small)

![](https://image.3001.net/images/20210108/1610090266_5ff8071a09e8aadfe9653.png!small)

d.环境配置完成

![](https://image.3001.net/images/20210108/1610090272_5ff80720a430dd03fd6f2.png!small)

## 二、漏洞利用

1、登录后台，找到网站配置的域名配置

![](https://image.3001.net/images/20210108/1610090286_5ff8072eee5acb93a033b.png!small)

![](https://image.3001.net/images/20210108/1610090294_5ff80736e27749f12b6b3.png!small)

2、打开brup抓包工具并保存配置

![](https://image.3001.net/images/20210108/1610090302_5ff8073e05351cd2cb4b0.png!small)

3、抓到包之后放到重放模块

![](https://image.3001.net/images/20210108/1610090315_5ff8074b567d94e9a7602.png!small)

4、将对应的site_domain配置修改为base64编码的phpinfo文件

![](https://image.3001.net/images/20210108/1610090375_5ff8078700c3aee271e73.png!small)

![](https://image.3001.net/images/20210108/1610090384_5ff8079001b7185db6718.png!small)

5、发送成功后访问http://127.0.0.1/upload/Application/Common/Conf/url.php的文件，访问
后就会自动写入403.php文件

![](https://image.3001.net/images/20210108/1610090392_5ff8079845e20d803fde7.png!small)

6、访问该文件就能获取到phpinfo的信息，上传一句话木马也是同理

![](https://image.3001.net/images/20210108/1610090916_5ff809a4db6442085d69f.png!small)

3、 一句话木马上传

1、先抓包修改

![](https://image.3001.net/images/20210108/1610090841_5ff80959b52b8997a0b4b.png!small)

2、再去访问http://127.0.0.1/upload/Application/Common/Conf/url.php生成1.php文件

生成后尝试访问1.php

![](https://image.3001.net/images/20210108/1610090832_5ff809504662031e88ca0.png!small)

3、使用蚁剑连接，连接成功

![](https://image.3001.net/images/20210108/1610090813_5ff8093df1bb765dee9a5.png!small)

参考文章：https://xz.aliyun.com/t/8021

  

