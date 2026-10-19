原创： SkyBlue永恒  合天智汇

  

01简介

RhinOS是一个使用最新功能开发网站的框架，可以为Web门户提供最快的访问和管理。RhinOSCMS对于网站管理功能十分强劲，内置允许使用数据库进程和解析器模块快速访问数据库，xml和其他资源，购物车，标签和参数化文件，配置参数，Intranet访问，数据库会话，电子邮件发送，验证码安全系统，快速过滤，列表和详细信息的模块，功能可谓是非常之多了。RhinOSCMS的download.php文件存在任意文件下载漏洞，通过漏洞能够下载任意的文件。

02环境搭建

RhinOS
CMS下载地址为：https://sourceforge.net/projects/rhinos/。下载完成后，打开文件，一直点下一步就能够完成安装，如图1所示。

  
![图片.png](https://image.3001.net/images/20181220/1545289488_5c1b3f10ad468.png!small)  

图1完成安装

由于一些编码原因，安装成功后的的信息会显示一些乱码，如果使用西班牙语的系统就能正常显示了。然后需要将httpd.conf中的端口修改为8080端口，修改端口是为了避免和WINDOWS本身一些服务冲突，http.conf所在路径为：C:\rhinos\httpd\conf\httpd.conf。如图2所示。

![图片.png](https://image.3001.net/images/20181220/1545289497_5c1b3f1933cae.png!small)  

图2httpd.conf所在路径

右键编辑将文件中的80端口修改为8080端口，如图3所示。

![图片.png](https://image.3001.net/images/20181220/1545289504_5c1b3f206fb69.png!small)  

图3修改端口

修改端口后需要重启阿帕奇服务，重启服务后访问http://127.0.0.1:8080。就能够访问到已经搭建好的CMS了，如图4所示。

![图片.png](https://image.3001.net/images/20181220/1545289526_5c1b3f368bf52.png!small)  

图4重启阿帕奇服务后访问

03漏洞代码审计

漏洞存在于C:\rhinos\demo\admin\php\download.php中，在第30行代码，能够看到文件读取的路径拼接操作，如图5所示。

  
![图片.png](https://image.3001.net/images/20181220/1545289520_5c1b3f30aca44.png!small)  

图5download.php

看到getParam()，查找这个方法是如何实现的。

这个函数存在于：C:\rhinos\demo\admin\php\connect.php。第88行，如图6所示。

  
![图片.png](https://image.3001.net/images/20181220/1545289529_5c1b3f39bb0b9.png!small)  

图6connect.php

这个函数中获取了”file”的参数，通过POST或者GET提交都是可以的。然后根据图5所示第41行触发文件读取操作，如果控制参数file则能够成为任意文件读取漏洞或者为任意文件下载漏洞。

04漏洞复现

在复现之前需要找到从什么地方调用到了download.php,在经过测试之后发现通过这个URL提交就能够利用漏洞下载到config.php文件,但是首先需要登录后台。URL如下:

http://127.0.0.1:8080/admin/inicio.php?include=php/download.php&name=efe.php&file=../config.php，如图7所示。

![图片.png](https://image.3001.net/images/20181220/1545289546_5c1b3f4a6d98e.png!small)  

图7下载config.php

当然既然是任意文件下来漏洞肯定可以下载windows目录下面的win.ini文件，使用URL为:

http://127.0.0.1:8080/admin/inicio.php?include=php/download.php&name=efe.php&file=../../../../Windows/win.ini。执行后就能够下载文件了。如图8所示。

  
![图片.png](https://image.3001.net/images/20181220/1545289548_5c1b3f4c22da3.png!small)  

图8下载win.ini

05修复建议

根据前文的描述能够看出，漏洞存在一定的危害。应该对于漏洞进行修复，关于如何去修复漏洞。

  1. 过滤点[.]要求用户在url中不能回溯上级目录。

  2. 正则严格判断用户输入参数的格式，保证输入参数的准确性。

  3. 将下载区独立放在项目路径外，分配每个下载资源固定的URL,不能是所有的下载资源都是统一的URL：

http://127.0.0.1:8080/admin/inicio.php?include=php/download.php&name=efe.php&file=文件名

  
  

