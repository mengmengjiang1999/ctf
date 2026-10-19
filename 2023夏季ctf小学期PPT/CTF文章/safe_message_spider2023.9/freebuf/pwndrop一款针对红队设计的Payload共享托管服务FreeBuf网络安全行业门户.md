![](https://image.3001.net/images/20200423/1587637851_5ea16e5b798ba.png!small)

## pwndrop

**pwndrop是一款支持自主部署的文件托管服务，在pwndrop的帮助下，红队研究人员将能够通过HTTP、HTTPS或WebDAV来发送、上传或共享Payload以及各种机密文件。**

如果你需要快速地去设置一台Nginx或Apache
Web服务器来托管自己的机密文件，并且不想去做复杂的环境搭建/配置的话，那么pwndrop绝对能够满足你的需求。

## pwndrop功能

> 1、使用我们自己的私人VPS并通过拖拽来上传或共享多个机密文件；
>
> 2、简单操作即可设置目标文件是否可下载；
>
> 3、为共享文件设置自定义下载URL，而不需要修改/暴露目录结构；
>
> 4、可设置facade虚拟文件，而无需提供原始文件下载；
>
> 5、设置自动重定向以隐藏共享连接中的文件扩展名；
>
> 6、更改托管文件的MIME类型，以更改单击下载链接时浏览器的行为；
>
> 7、通过HTTP、HTTPS和WebDAV托管文件；
>
> 8、使用Bash oneliner安装和设置所有内容；
>
> 9、将pwndrop设置为域名服务器，可向任何子域名响应有效的DNS A记录；
>
> 10、使用自定义秘密URL路径保护后台管理系统的安全，并使用用户名和密码进行登录；
>
> 11、无需担心HTTPS证书，因为pwndrop会帮我们在后**成所有配置及续订操作；

该工具的主要功能就是以最简单最便捷的方式帮助我们完成文件的共享，并给红队安全研究人员提供额外的辅助性功能。

pwndrop的前端基于纯Vue.js + Bootstrap开发，并且不需要任何npm或webpack依赖。pwndrop后台提供了REST
API接口，并整合了本地数据库，后台由Go语言程序驱动。

> 更多功能介绍，请参考pwndrop的官方手册：【[ _点我获取_](https://breakdev.org/pwndrop)】。

### 工具依赖

搭建一台自己的VPS服务器，注册一个新的域名，然后将域名的DNS
A记录指向你VPS服务器的IP地址。或者，你也可以注册一个域名，然后让其ns1和ns2域名服务器指向pwndrop实例的IP地址。服务器至少要求512MB的内存RAM。

如果你不想注册域名，你也可以设置一个本地实例，但此时你将无法自动生成HTTPS证书。

## 工具安装

搜先，请确保在尝试安装pwndrop之前没有DNS或HTTP(S)服务器正处于运行状态。

### Oneliner

我个人不建议大家使用Oneliner，但如果你一定要的话：

    
    
    curl https://raw.githubusercontent.com/kgretzky/pwndrop/master/install_linux.sh | sudo bash

上述命令将会下载最新版本的AMD64发布代码，并安装一个运行在后台的守护进程。

### 包安装

首先你需要从pwndrop的[ _GitHub
Release页面_](https://github.com/kgretzky/pwndrop/releases)下载最新版本的代码包，或使用下列命令将项目源码客隆至本地：

    
    
    git clone https://github.com/kgretzky/pwndrop.git

然后运行下列命令：

    
    
    tar zxvf pwndrop-linux-amd64.tar.gz
    
    ./pwndrop stop
    
    ./pwndrop install
    
    ./pwndrop start
    
    ./pwndrop status

### 源码安装

首先，确保你的设备上已搭建好[ _Go v1.13+_](https://golang.org/doc/install)环境，然后运行下列命令：

    
    
    git clone<https://github.com/kgretzky/pwndrop>
    
    cd pwndrop
    
    make
    
    make install

## 快速使用

确保pwndrop已处于运行状态。

> 1、访问秘密URL地址并授权浏览器访问：<https://yourdomain.com/pwndrop>；（这是一个默认地址，确保之后使用秘密路径）
>
> 2、在浏览器中访问管理后台的URL路径：<https://yourdomain.com/>；（授权浏览器之后，你将能访问后台管理登录页面）
>
> 3、创建一个管理员账号并登录；
>
> 4、点击左上角配置按钮，修改后台路径地址；

## 从命令行运行

如果你没有将pwndrop以守护进程的方式安装，那么你仍可以通过命令行来使用pwndrop。

    
    
    usage: pwndrop [start|stop|install|remove|status] [-config <config_path>] [-debug] [-no-autocert] [-no-dns] [-h]
    
    daemon management:
    
    start : start the daemon
    
    stop : stop the daemon
    
    install : install the daemon using the available system manager (systemd, systemv and upstart supported)
    
    remove : uninstall the daemon
    
    status : check status of the installed daemon
    
    parameters:
    
    -config : specify a custom path to a config file (def. 'pwndrop.ini' in same directory as the executable)
    
    -debug : enable debug output
    
    -no-autocert : disable automatic TLS certificate retrieval from LetsEncrypt; useful when you want to connect over IP or/and in a local network
    
    -no-dns : do not run a DNS server on port 53 UDP; use this if you don't want to use pwndrop as a nameserver
    
    -h : usage help

## 工具配置

首次启动，pwndrop将会创建一个名为pwndrop.ini的新配置文件，之后你可以根据自己的需要来对其进行修改。下面给出的是一份样本配置文件：

    
    
    [pwndrop]
    
    listen_ip = "190.33.86.22" # the external IP of your pwndrop instance (must be set if you want to use the nameserver feature)
    
    http_port = 80 # listening port for HTTP and WebDAV
    
    https_port = 443 # listening port for HTTPS
    
    data_dir = "./data" # directory path where data storage will reside (relative paths are from executable directory path)
    
    admin_dir = "./admin" # directory path where the admin panel files reside (relative paths are from executable directory path)
    
    [setup] # optional: put in if you want to pre-configure pwndrop (section will be deleted from the config file on first run)
    
    username = "admin" # username of the admin account
    
    password = "secretpassword" # password of the admin account
    
    redirect_url = "[https://www.somedomain.com](https://www.somedomain.com/)" # URL to which visitors will be redirected to if they supply a path, which doesn't point to any shared file (put blank if you want to return 404)
    
    secret_path = "/pwndrop" # secret URL path, which upon visiting will allow your browser to access the login page of the admin panel (make sure to change the default value)

## 工具使用演示

### 项目地址

> pwndrop：【[ _GitHub传送门_](https://github.com/kgretzky/pwndrop)】

* 参考来源：[ _kgretzky_](https://github.com/kgretzky/pwndrop)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM

