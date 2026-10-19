## 漏洞简介：

Subrion CMS 4.2.1 中的 /panel/uploads 允许远程攻击者通过 .pht 或 .phar 文件执行任意 PHP 代码，因为
.htaccess 文件省略了这些代码。

## 漏洞环境：

春秋云镜中的漏洞靶标，CVE编号为CVE-2018-19422

## 漏洞复现：

打开漏洞环境

![](https://image.3001.net/images/20230616/1686908426_648c2e0ad8dfb084a36e1.png!small)

看到有转至管理仪表板

  

发现要登陆，试试常用弱口令，发现账号密码为admin/admin，登录进后台

![](https://image.3001.net/images/20230616/1686908467_648c2e336bde67770b40e.png!small)![](https://image.3001.net/images/20230616/1686908483_648c2e43dd34f4c0e0963.png!small)

  

查看有没有可利用的地方，找到了一个上传点 content-uploads

![](https://image.3001.net/images/20230616/1686908503_648c2e573d5ef4bc4627c.png!small)

  

制作一句话木马，并根据漏洞介绍把文件后缀为pht或者phar

![](https://image.3001.net/images/20230616/1686908523_648c2e6b47d412649dfdd.png!small)

  

上传文件，可以看到文件路径

![](https://image.3001.net/images/20230616/1686908538_648c2e7ab4454f059a11c.png!small)

  

访问上传的文件，用phpinfo();测试文件是否可用

![](https://image.3001.net/images/20230616/1686908567_648c2e97e11d78d076785.png!small)

  

  

发现可用就可以执行想要的命令了，这里需要获取flag

![](https://image.3001.net/images/20230616/1686908616_648c2ec85f77058593997.png!small)

> flag{ee609eef-5aee-49c5-b161-f2b84f3a96a5}

