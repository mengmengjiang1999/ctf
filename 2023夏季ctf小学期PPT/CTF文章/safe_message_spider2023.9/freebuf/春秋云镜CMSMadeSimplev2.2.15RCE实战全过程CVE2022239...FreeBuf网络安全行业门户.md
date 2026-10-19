## 漏洞简介：

CMS Made Simple v2.2.15 被发现包含通过上传图片功能的远程命令执行 (RCE) 漏洞。此漏洞通过精心制作的图像文件被利用。

## 漏洞环境：

春秋云镜中的漏洞靶标，CVE编号为CVE-2022-23906

## 漏洞复现：

### 访问漏洞环境

![](https://image.3001.net/images/20230611/1686445258_64851ccaa919bf3ab3e76.png!small)

寻找网站可以利用的点，没有发现可以利用的点

  

这里我使用目录扫描器扫描网站目录，扫出了后台登录url

![](https://image.3001.net/images/20230611/1686445317_64851d05e6f879d63eb2c.png!small)

访问网站后台

![](https://image.3001.net/images/20230611/1686445387_64851d4bae9a19077277b.png!small)

尝试登录，发现网站存在弱口令账户密码 admin/123456

  

登录到后台界面

![](https://image.3001.net/images/20230611/1686445617_64851e310ed548e98d4de.png!small)

寻找发现 内容-File Manager 处有上传点，并且点击copy发现能改文件名猜测可能包含文件扩展名

![](https://image.3001.net/images/20230611/1686445644_64851e4c7fc3d1d6e8a17.png!small)![](https://image.3001.net/images/20230611/1686445662_64851e5e84e51fa51e64d.png!small)

先随便上传一个图片文件看看 ，发现直接上传的根目录

![](https://image.3001.net/images/20230611/1686445806_64851eeee70901c1ee420.png!small)

现在写一个一句话木马把扩展名改成图片格式上传

![](https://image.3001.net/images/20230611/1686445857_64851f21d0b3fecc8abe9.png!small)![](https://image.3001.net/images/20230611/1686445869_64851f2dd99479aa73f21.png!small)

选中上传的图片点击copy，把copy的文件改成 shell.php

![](https://image.3001.net/images/20230611/1686445900_64851f4ccc7ea9e7848f4.png!small)![](https://image.3001.net/images/20230611/1686445912_64851f58a847dc3a31e06.png!small)

访问文件执行命令，文件可执行命令

![](https://image.3001.net/images/20230611/1686445952_64851f8027291d30c4ee1.png!small)

接下来就可以执行想执行的命令了。

我们这里要找flag

![](https://image.3001.net/images/20230611/1686446097_6485201136afd5bd880cb.png!small)

  

  

  

  

