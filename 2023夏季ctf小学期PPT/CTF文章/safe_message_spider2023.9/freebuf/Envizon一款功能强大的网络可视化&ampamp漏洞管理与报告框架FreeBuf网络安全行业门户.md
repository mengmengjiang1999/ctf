![图片1.png](https://image.3001.net/images/20200404/1585984937_5e8835a99c18c.png!small)  

**Envizon是一款功能强大的网络可视化 &漏洞管理与报告框架，该工具由Evait
Security团队负责设计、开发和维护。为了回报安全社区，我们发布了我们内部使用和开发的最先进的网络可视化和漏洞报告工具“Envizon”。我们希望您的反馈将有助于改进和进一步完善Envizon的功能。**

## 使用场景

在渗透测试过程中，我们可以使用Envizon以便快速获取目标网络的概述情况，并确定最有可能存在安全问题的潜在目标。Envizon
v3.0版本引入了很多新的功能，比如说Web服务截屏、漏洞组织与分类和使用自定义docx模板生成报告等等。

## 核心功能

> 1、使用预定义或自定义nmap查询来扫描目标网络；
>
> 2、使用与配置或自定义组对客户端进行分类和排序；
>
> 3、搜索目标客户端所有属性并创建复杂的链接查询；
>
> 4、在渗透测试过程中，使用预定义安全标签获取目标概述情况；
>
> 5、使用chrome-headless（selenium）-VNC获取类http应用程序的可视化截图；
>
> 6、保存或复用nmap扫描；
>
> 7、实时项目团队协同合作；
>
> 8、将选择的客户端导出为文本文件，以快速与其他工具整合；
>
> 9、管理问题模板，创建主机漏洞数据库；
>
> 10、以docx模板创建客户报告；

## 工具使用

为了避免依赖和兼容性问题，并方便广大用户安装和使用Envizon，我们选择使用Docker环境。你可以构建你自己的镜像，或从Docker
Hub获取和使用预构建的镜像。

## 使用Docker

Docker和Docker Compose是必须的。

## 预构建Docker镜像

使用docker/envizon_prod目录中的docker-compose.yml文件，然后使用下列命令运行：

    
    
    docker-compose up

Docker镜像将会从evait/envizon中拖出。

如果你想要更新应用镜像，或手动配置，你可以运行下列命令：

    
    
    docker pull evait/envizon

如果你想要提供自己的SSL证书，请根据自己的需要修改docker-compose.yml文件，否则工具将会自动生成一份配置文件。

    
    
    wget https://raw.githubusercontent.com/evait-security/envizon/master/docker/envizon_prod/docker-compose.yml
    
    echo SECRET_KEY_BASE="$(echo $(openssl rand -hex 64) | tr -d '\n')" > .envizon_secret.env
    
    sudo docker-compose up

使用本地git运行检测：

    
    
    git clone https://github.com/evait-security/envizon
    
    cd envizon/docker/envizon_local
    
    echo SECRET_KEY_BASE="$(echo $(openssl rand -hex 64) | tr -d '\n')" > .envizon_secret.env
    
    sudo docker-compose up

## 开发环境部署

如果你想要运行产品的开发环境，你还需要修改`config/secrets.yml`中的数据，并手动激活SSL：

    
    
    git clone https://github.com/evait-security/envizon
    
    cd envizon/docker/envizon_dev
    
    sudo docker-compose up

## 设置密码

启动Docker镜像之后，访问下列地址：

    
    
    https://localhost:3000/

或

    
    
    http://localhost:3000/

你需要为你的Envizon实例设置一个密码，在登录之后，可以在设置接口中修改这个密码。

## 扫描接口

在扫描接口中，你可以使用与配置的参数来执行新的网络扫描，你甚至还可以上传之前使用过的nmap扫描（使用-oX参数）。

扫描任务会进行自动化拆分，以降低等待时间。

我们可以使用主机名或IP地址来指定扫描目标，IP地址可以带子网掩码或CIDR前缀。如需指定地址范围，可以用`-`或`,`来分隔IP地址：

    
    
    scanme.nmap.org
    
    192.168.1.1
    
    192.168.1.0/24
    
    192.168.1.0/255.255.255.0
    
    192.168.1.1-192.168.1.10
    
    192.168.1.1-192.168.10.254
    
    192.168.1.0-192.168.10.0/24
    
    192.168.1.0-192.168.10.0/255.255.255.0
    
    192.168.1.1-10
    
    192.168.1-10.1-10
    
    192.168.1-10.0/24
    
    192.168.1-10.0/255.255.255.0
    
    192.168.1,2.1
    
    192.168.1,2.1-10
    
    192.168.1,2.0/24
    
    192.168.1,2.0/255.255.255.0

## 导入/导出

完整的项目数据库可以在设置中进行导出。导出文件格式为zip压缩文件格式，我们也可以在设置接口中进行上传和下载。

在导入项目时，将会在你的Envizon容器中创建一个临时文件，并且在容器重启之后会完成整个导入过程：

    
    
    docker-compose restart envizon

## 项目地址

【[ _GitHub传送门_](https://github.com/evait-security/envizon)】

【[ _官方网站_](https://evait-security.github.io/envizon/)】

 *** 参考来源：[ _evait-security_](https://github.com/evait-security/envizon)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

