![](https://image.3001.net/images/20210902/1630578194_6130a612a0c0c35e718b8.jpeg!small)

## 关于Solitude

Solitude是一款功能强大的隐私安全分析工具，可以帮助广大研究人员根据自己的需要来进行隐私问题调查。无论是好奇的新手还是更高级的研究人员，Solitude可以帮助每一名用户分析和研究应用程序中的用户隐私安全问题。

值得一提的是，Solitude因在一个受信的专用网络上运行，即用户需要在私有可信网络上运行该工具。

## 关于证书绑定

如何你打算使用Solitude来测试移动应用程序的话，对于非越狱设备，如果应用程序或嵌入应用程序的第三方SDK使用了证书绑定，那么你可能无法捕捉到所有的HTTP流量。因为证书绑定是一种安全机制，可确保应用程序与之通信的服务器是其预期的服务器。但是，Solitude目前还不支持证书绑定绕过。

## 工具安装

### macOS-Docker安装

首先，我们需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/nccgroup/Solitude

接下来，我们需要安装[ _Docker_](https://docs.docker.com/docker-for-mac/install/)：

    
    
    docker-compose -f docker-compose-prod.yml build
    docker-compose -f docker-compose-prod.yml up

然后，打开浏览器并访问http://localhost:5000，按照操作指引开启虚拟专用服务器，并配置好你的移动设备和中间人攻击MitM代理证书。

### macOS本地安装（无需Docker-Compose）

首先，我们需要安装好Docker。

接下来，运行下列命令：

    
    
    brew install mysql

然后运行MySQL Docker容器：

    
    
    docker run -p 3306:3306 -d --name mysql -e MYSQL_ROOT_PASSWORD=solitude mysql

接下来，将该项目源码克隆至本地，安装好依赖组件之后，就可以直接运行工具脚本了：

    
    
    git clone https://github.com/nccgroup/Solitude
    cd Solitude && python3 -m venv venv
    source venv/bin/activate
    pip3 install -r requirements.txt
    python3 run.py

安装完成后，打开浏览器并访问http://localhost:5000，配置你的浏览器通过localhost:8080代理所有的HTTP流量即可。

### Linux安装

首先，我们需要安装并配置好[ _Docker_](https://docs.docker.com/engine/install/ubuntu/)和[
_Docker-compose_](https://docs.docker.com/compose/install/)：

    
    
    docker-compose -f docker-compose-prod.yml build
    docker-compose -f docker-compose-prod.yml up

接下来，将该项目源码克隆至本地，安装好依赖组件之后，就可以直接运行工具脚本了：

    
    
    git clone https://github.com/nccgroup/Solitude
    cd Solitude && python3 -m venv venv
    source venv/bin/activate
    sudo apt-get install libmysqlclient-dev
    pip3 install -r requirements.txt
    python3 run.py

安装完成后，打开浏览器并访问http://localhost:5000，配置你的浏览器通过localhost:8080代理所有的HTTP流量即可。

## 数据库配置

我们还需要修改Solitude的数据库默认密码，编辑.env文件中的密码即可。

## 项目地址

 **Solitude：** 【[ _GitHub传送门_](https://github.com/nccgroup/Solitude)】

