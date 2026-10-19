## 一、漏洞简介

通达OA（Office
Anywhere网络智能办公系统）是由北京通达信科科技有限公司自主研发的协同办公自动化软件，是与中国企业管理实践相结合形成的综合管理办公平台。3月13日，通达OA在官方论坛发布通告称，近日接到用户反馈遭到勒索病毒攻击，攻击者通过构造恶意请求，上传webshell等恶意文件，并对入侵的服务器进行文件加密，勒索高额匿名货币赎金。笔者长期从事二进制漏洞的研究，写此文旨在学习web漏洞的研究方法并以此漏洞为实践，强化对web漏洞利用技术的认识，记录之。

## 二、漏洞分析

资料显示，该漏洞影响范围较广，影响的版本有：V11版、2017版、2016版、2015版、2013增强版、2013版。

本文为了复现方便，下载使用了通达OA V11.3版本。下载链接：

> <https://pan.baidu.com/s/1QFAoLxj9pD1bnnq3f4I8lg>
>
> 提取码：ousi

### 2.1 初步的代码审计

安装好通达OA
v11.3版本，安装后在webroot目录下找到源代码，查看源码，发现都是乱码，都是经过zend加密的，需要解密。解密工具可使用SeayDzend，因为源码是php写的，最简单的是用seay源码审计工具粗略筛选一下，查找潜在的漏洞，代码审计时间较长，审计结果取了开头一小段，说明思路而已。如图1所示：

![](https://image.3001.net/images/20200509/1589032007_5eb6b447ad631.png!small)

图1：代码审计

### 2.2 文件上传漏洞

根据网上公开资料，直接定位到源码路径
C:\phpStudy\WWW\tongdaoa\webroot\ispirit\im\upload.php，查看源码,如图2：

![](https://image.3001.net/images/20200508/1588906201_5eb4c8d9c7561.png!small)

图2：upload.php文件上传漏洞源码

该段源码黑框内部分，传入参数p,当参数p非空时进入会话页面，否则就进入认证页面。该处漏洞比较明显，只要参数p非空就可以绕过认证。继续阅读该段代码，绕过认证后就可以直接上传文件。如图3所示：

![](https://image.3001.net/images/20200508/1588906240_5eb4c9000f782.png!small)

图3：文件上传

跟进inc\utility_file.php
的upload方法,发现有个文件名校验函数is_uploadable。查看该函数的代码逻辑，如果文件名从最后一个位置倒数三个是“php”，那么返回false，也就是不可以上传以php结尾的文件。参考源码，这里也有多种黑名单绕过的方法，略过。源码如下图4：

![](https://image.3001.net/images/20200508/1588906252_5eb4c90c96da9.png!small)

图4：文件名黑名单

### 2.3 文件包含漏洞

参考资料，该文件包含漏洞存在于源码ispirit/interface/gateway.php。查看该处源码，如图5：

![](https://image.3001.net/images/20200508/1588906265_5eb4c919a70ce.png!small)

图5：文件包含漏洞代码

通过foreach
循环解析json，如果key和url相等，那么获得url,判断url是否为空，如果不为空且url中包含general/、ispirit/、module/，就调用include_once函数。试想，如果url构造成../../类型，执行完文件包含后，就可以访问到我们之前上传的文件了，一个../向上一级目录移动一下，两个../刚好退到tongdaoa的安装目录,后面紧接着之前上传的文件目录就可以。此处漏洞关键就在于构造url。

## 三、漏洞复现

### 3.1 复现环境

测试主机：Win10 x64 english

通达OA 11.3

抓包软件： Burpsuite v1.737

浏览器Firefox 41.0

下面我们分别对两个漏洞分别进行复现。

### 3.2 复现文件上传漏洞

通过通读upload.php源码，复现该漏洞需要满足以下条件：

> （1）参数p 非空；
>
> （2）DEST_UID非空且为数字；
>
> （3）UPLOAD_MODE 为1 或者2 或者3；
>
> （4）attachment的文件名不可以为php；

构造文件上传payload1 如图6：

![](https://image.3001.net/images/20200508/1588906347_5eb4c96b3cd14.png!small)

图6：文件上传payload1

用Burpsuite抓包，修改当前payload为payload1并重放，文件上传成功。如图7所示：

![](https://image.3001.net/images/20200508/1588906360_5eb4c97844719.png!small)

图7：文件上传复现

上传的文件保存在目录c:\phpstudy/www/tongdaoa/attach/im/2005/路径下，如图8所示：

![](https://image.3001.net/images/20200508/1588906373_5eb4c98566211.png!small)

图8：上传成功

验证文件上传成功。此时有一个问题，就是上传的文件不在webroot目录下，远程是访问不了的。这是需要配合另一个漏洞-文件包含漏洞来完成路径穿越，访问到上传的文件。

### 3.3 复现文件包含漏洞

按照之前代码分析，主要是构造url的payload。假设访问<http://localhost/ispirit/interface/gateway.php,>用burpsuite截包，发送到repeater,构造文件包含漏洞的payload2，payload2里注意两处，一处是增加Content-Type: application/x-www-form-urlencoded，另一处是json处url的构造。如图9所示，文件包含漏洞执行成功。

![](https://image.3001.net/images/20200508/1588906386_5eb4c992eb8f4.png!small)

图9：文件包含漏洞复现

### 3.4 获取目标shell

两个漏洞结合使用，可以远程获取shell。提前准备好php木马以及冰蝎等远程连shell工具。思路：利用文件上传漏洞上传php木马，然后再利用文件包含漏洞，使得web访问到该php文件，再用冰蝎连接。(注意：不可以直接为.php,根据代码分析结果，结尾为php的文件上传不上去）如图10所示：

![](https://image.3001.net/images/20200508/1588906403_5eb4c9a397f64.png!small)

图10：获取shell步骤1

在文件夹路径“C:\phpStudy\WWW\tongdaoa\attach\im\2005”下找到了该文件，上传成功。如图11：

![](https://image.3001.net/images/20200508/1588906418_5eb4c9b2dc831.png!small)

图11：上传成功

然后通过文件包含漏洞访问到刚刚上传的2125745527.test.php文件。如图12所示：

![](https://image.3001.net/images/20200508/1588906428_5eb4c9bc3b875.png!small)

图12：访问已上传的文件

访问成功后，在\ispirit\interface\ 目录下会生成readme.php ,用冰蝎webshell连接，成功获取shell。如图13：

![](https://image.3001.net/images/20200508/1588906442_5eb4c9ca1bff4.png!small)

图13：成功获取shell1

![](https://image.3001.net/images/20200508/1588906467_5eb4c9e39e0f0.png!small)

图14：成功获取shell2

最后剩下的就是构造exploit了，网上已经给出很多该漏洞远程利用程序，大家可以用来测试。

## 四、补丁比较&加固建议

### 4.1补丁比较

笔者本着学习的目的，下载了通达OAv11.3的补丁，并做了补丁比较，比较的结果如下：

第一处补丁补上了文件上传漏洞，无论参数是否为空，都要进行认证。如图15所示：

![](https://image.3001.net/images/20200508/1588906478_5eb4c9eeb12bf.png!small)

图15：第一处补丁

第二处补丁将“..”过滤掉了，如果url中出现该符号，认为是错误的url。这样就不可以执行路径穿越，也就访问不到非webroot目录下的文件了。如图16所示：

![](https://image.3001.net/images/20200508/1588906493_5eb4c9fd4aa11.png!small)

图16：第二处补丁

### 4.2 加固建议

建议使用受影响版本的通达OA用户登录通达OA官网，获取最新补丁。请根据当前OA版本选择所对应的程序文件，运行前请先做好备份。安全更新下载地址：[http://www.tongda2000.com/news/673.php](https://links.jianshu.com/go?to=http://www.tongda2000.com/news/673.php)

本文仅是记录一次对通达OA漏洞的分析利用过程，不当的地方请大牛们指点纠正。从逆向思维的角度出发，如何自主发现该类型的漏洞并能快速形成利用思路，构建exploit?这是笔者想在后续深入学习web漏洞时想着重提高的。有对代码审计有经验的大牛或者对代码审计感兴趣想一起学习的，可站内联系，一起进步！

## 五、参考

[ _https://www.cnblogs.com/yuyan-sec/p/12549237.html_](https://www.cnblogs.com/yuyan-sec/p/12549237.html)

 ***本文作者：elvadisas，转载请注明来自FreeBuf.COM**

