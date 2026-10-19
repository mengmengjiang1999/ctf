![](https://image.3001.net/images/20201027/1603809935_5f98328fe42afe25feb6c.png!small)

## NERVE

我们认为，安全扫描应当是一件需要持续去做的事情，这种持续性并不是指每天、每周、每个月或每个季度，我们指的是每一分每一秒！这种持续性的安全扫描方式适用于以下几种场景：

> 假设你拥有一个动态环境，并且每分每秒都可能有新的基础设施被创建；
>
> 你想要比任何人都提前捕捉到异常安全问题；
>
> 你想要构建快速的安全响应措施；

NERVE就是针对上述几种场景而开发出来的，商业工具虽好，但这些工具往往非常“笨重”，不易扩展，而且还很费钱。

![](https://image.3001.net/images/20201027/1603809954_5f9832a20a5379fd17570.png!small)

本质上来说，NERVE是一款漏洞扫描工具，可以帮助研究人员来寻找特定应用程序的配置缺陷、网络服务楼哦那个以及各种未修复的安全漏洞。

## NERVE的检测功能

> 感兴趣的管理面板（例如Solr、Django和PHPMyAdmin等）
>
> 子域名接管
>
> 开放代码库
>
> 信息披露
>
> 废弃/默认Web页面
>
> 服务中的错误配置（Nginx、Apache和IIS等）
>
> SSH服务器
>
> 开放数据库
>
> 开放Cache
>
> 目录索引
>
> 最佳实践方案

注意事项，该工具并非Qualys、Nessus或OpenVAS等工具的代替品，因为NERVE无法进行认证扫描，并且只能在黑盒模式下执行操作。

## 工具依赖

NERVE将会自动帮助我们安装好相应的依赖组件，除此之外，该工具还带有一个Dockerfile以供广大研究人员使用。

请注意，NERVE在初始安装过程中需要用到root访问权限。

NERVE需要的依赖服务和依赖包如下：

> Web服务器（Flask）
>
> Redis服务器
>
> Nmap包（源码或Python nmap库）
>
> HTTP/S访问端口（可在py文件中定义）

安装脚本会帮助我们自动化安装配置好一切，但如果你想要自己安装的话，可能就需要花点时间了。

## 工具安装-Docker

克隆代码库：

    
    
    git clone git@github.com:PaytmLabs/nerve.git && cd nerve

构建Docker镜像：

    
    
    docker build -t nerve

使用镜像创建容器：

    
    
    docker run -e username="YOUR_USER" -e password="YOUR_PASSWORD" -d -p 80:8080 nerve

接下来打开你的浏览器，然后访问http://ip.add.re.ss:80，使用之前在命令中定义的登录凭证进行登录即可。

## 服务器端安装&配置

    
    
    cd /opt/
    
    git clone git@github.com:PaytmLabs/nerve.git && cd nerve
    
    bash install/setup.sh
    
    systemctl status nerve

接下来打开你的浏览器，然后访问http://ip.add.re.ss:80，使用终端窗口中输出的凭证进行登录即可。

## 工具运行

GUI文档：

![](https://image.3001.net/images/20201027/1603809996_5f9832ccc7f521ebdc5aa.png!small)

API文档：

![](https://image.3001.net/images/20201027/1603810003_5f9832d3d2bb83fe50014.png!small)

登录界面：

![](https://image.3001.net/images/20201027/1603810010_5f9832da85004eb61f641.png!small)

仪表盘界面：

![](https://image.3001.net/images/20201027/1603810016_5f9832e0b90bb83ff22ad.png!small)

安全评估配置：

![](https://image.3001.net/images/20201027/1603810023_5f9832e798ad77feae9da.png!small)

扫描报告：

![](https://image.3001.net/images/20201027/1603810030_5f9832eec43233003abc6.png!small)

网络映射：

![](https://image.3001.net/images/20201027/1603810038_5f9832f60dfaf368cc250.png!small)

漏洞管理页面：

![](https://image.3001.net/images/20201027/1603810045_5f9832fd7e46b1526261f.png!small)

日志终端：

![](https://image.3001.net/images/20201027/1603810053_5f9833050c183d665c261.png!small)

HTML报告：

![](https://image.3001.net/images/20201027/1603810059_5f98330b877d23fa6ce99.png!small)

## 许可证协议

NERVE项目的开发与发布遵循MIT开源许可证协议。

## 项目地址

NERVE：【[ _GitHub传送门_](https://github.com/PaytmLabs/nerve)】

