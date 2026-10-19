## 一、项目地址

QingLong
framework（青龙框架）由本人独立研发并持续维护，它是一个专注于内网渗透的轻量级框架。目前青龙有6大功能模块，分别是信息收集模块、漏洞扫描模块、密码破解模块、恶意攻击模块、拒绝服务攻击模块、内网渗透模块。

青龙框架的使命是为研究人员提供一个强大、灵活且持续更新的工具。

热烈欢迎各位黑客大师下载体验，也十分欢迎大家提出宝贵意见！

下面是该项目的地址，如果大家觉得该框架对你们有帮助，请高抬贵手给个star支持一下，比心~：

<https://github.com/ShadowMusk/QingLong-framework>

给所有支持与提出建议的黑客大师们致以最深的感谢！

## 二、框架启动

框架的启动非常简单，把项目下载后，解压，然后进入QingLong-framework-main目录，首先运行如下命令来安装框架依赖：

    
    
    python3 dependencies.py

![](https://image.3001.net/images/20230811/1691723118_64d5a56ebb47cd7117e93.png!small)然后运行如下命令即可运行框架：

    
    
    python3 index.py

![](https://image.3001.net/images/20230811/1691723209_64d5a5c904138d11a2800.png!small)我们敲击tab键，命令行会显示可选命令，我们选择命令“let's
start”即可进入框架的功能模块模式：

![](https://image.3001.net/images/20230811/1691723376_64d5a670a91ba9ca52f3d.png!small)![](https://image.3001.net/images/20230811/1691723440_64d5a6b063377f876c351.png!small)我们选择序号4，即可进入恶意攻击模块。敲击tab键命令，然后选择“show
functions”命令即可查看该功能模块下的所有子功能：

![](https://image.3001.net/images/20230811/1691723606_64d5a756a9deb425e4c8c.png!small)可以知道，目前恶意攻击模块的子功能有邮件钓鱼和邮件轰炸。恶意功能模块的其他功能以后会陆陆续续更新哦！

## 三、邮件钓鱼

我们选择序号1，即可注入邮件钓鱼模块：

![](https://image.3001.net/images/20230811/1691723815_64d5a827a3570c2b46e1e.png!small)usage就是该功能的使用命令，命令里面有许多参数，我们可以通过“show
params”命令来查看这些参数是什么意思：

![](https://image.3001.net/images/20230811/1691723916_64d5a88ca67f9f0967998.png!small)这里的钓鱼模板需要我们自己的制作，并且模板的格式必须要是html格式。

我们根据参数其usage和参数说明，执行该功能命令：

![](https://image.3001.net/images/20230811/1691724171_64d5a98be8c364dbcc8de.png!small)可以知道，邮件已经发送成功。受害者成功收到该邮件：

![](https://image.3001.net/images/20230811/1691724270_64d5a9eedba2e2f0954d9.png!small)

在这里，我只是用了一个很粗糙的模板来做演示。大家在真实的攻击中，可以把模板制作得更加具有诱惑性。

## 四、邮件轰炸

根据上述操作步骤，我们继续看看邮件轰炸功能：

![](https://image.3001.net/images/20230811/1691724428_64d5aa8c2f0e687ade74f.png!small)通过“show
params”命令来查看这些参数是什么意思：

![](https://image.3001.net/images/20230811/1691724470_64d5aab6b0f2af28ac5f0.png!small)我们同时用30封邮件轰炸对方邮箱：

![](https://image.3001.net/images/20230811/1691725270_64d5add650882336b5005.png!small)成功轰炸：

![](https://image.3001.net/images/20230811/1691725284_64d5ade4318509a36a78e.png!small)

  

