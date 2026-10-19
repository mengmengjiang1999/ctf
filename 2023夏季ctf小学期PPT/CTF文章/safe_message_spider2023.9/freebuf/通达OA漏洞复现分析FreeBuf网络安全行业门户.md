## **Part 1**

PS：本文仅用于技术讨论与分析，严禁用于任何非法用途，违者后果自负。

昨晚在朋友圈看到有人发了一个通达OA的0day，但是没有去验证，直接转到了绿帽子技术交流群里。

![](https://image.3001.net/images/20200819/1597834998.jpeg!small)

##  **Part 2**

今天抽空看了一下，

先到官网（https://www.tongda2000.com/）

提供的下载地址是：

![](https://image.3001.net/images/20200819/1597835018.png!small)

https://www.tongda2000.com/download/down.php?VERSION=2019&code=

默认提供的是11.7的最新版本，下载之后尝试失败。

##  **Part 3**

尝试更改参数下载。

![](https://image.3001.net/images/20200819/1597835041.png!small)

成功下载了四个版本，但是经过验证，全部不能上传webshell。在绿帽子群询问了一番，经过 和你 大佬的提醒，制定版本11.6

![](https://image.3001.net/images/20200819/1597835061.png!small)

​

下载地址：http://www.kxdw.com/soft/23114.html

部署成功之后，我使用burp代理抓包exp的请求。

![](https://image.3001.net/images/20200819/1597835072.png!small)

上传webshell成功，连接如图所示。

![](https://image.3001.net/images/20200819/1597835086.png!small)

##  **Part 4**

漏洞分析：

到目录

D:\MYOA\webroot\module\appbuilder\assets

查看print.php文件

打开网页：http://dezend.qiling.org/free.html 进行解密

![](https://image.3001.net/images/20200819/1597835099.png!small)

内容如下：

![](https://image.3001.net/images/20200819/1597835112.png!small)

    
    
    $s_tmp = __DIR__ . '/../../../../logs/appbuilder/logs';

对 $s_tmp 进行赋值。

    
    
    $s_tmp .= '/' . $_GET['guid'];

接着又对$s_tmp 进行累加赋值。

exp中 通过../../../webroot/inc/auth.inc.php，回到上层目录，然后通过unlink() 函数删除该参数传递的文件。

我们再看一下 auth.inc.php 文件 ，为什么上传webshell之前要先把他删除呢。

![](https://image.3001.net/images/20200819/1597835126.png!small)

看到开头应该猜到了，这个文件是判断用户是否登陆的文件， **如果没有登陆就不能上传，所以把这个文件删掉就可以成功上传webshell了** 。

