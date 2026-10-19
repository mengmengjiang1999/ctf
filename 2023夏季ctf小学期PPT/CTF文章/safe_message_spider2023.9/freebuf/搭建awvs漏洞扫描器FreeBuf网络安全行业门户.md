## ubuntu搭建awvs扫描器

AWVS是一款常用的漏洞扫描工具，全称为Acunetix Web Vulnerability
Scanner，它能通过网络爬虫测试你的网站安全，检测流行安全漏洞，大大提高了渗透效率。

### 1.安装docker

执行安装命令：apt install docker和apt install docker.io

### 2.安装awvs

1.通过以下命令查看镜像

    
    
    docker search awvs
    

![1667801551426.png](https://image.3001.net/images/20221107/1667801557_6368a1d5e5600a5df6b48.png!small)

2.使用以下命令安装awvs

    
    
    docker pull secfa/docker-awvs
    

![1667801568283.png](https://image.3001.net/images/20221107/1667801589_6368a1f517ec6ae871396.png!small)

3.使用以下命令查看下载的镜像

    
    
    docker images
    

![1667801596521.png](https://image.3001.net/images/20221107/1667801604_6368a204bfc808787db20.png!small)

4.启动awvs

    
    
    docker run -d -p 3443:3443 --name my-awvs secfa/docker-awvs
    

![1667801615843.png](https://image.3001.net/images/20221107/1667801623_6368a21755865ded18e49.png!small)

**至此安装完成**

### 3.访问

    
    
    https://localhost:3443
    username:admin@admin.com password:Admin123
    

![1667801632604.png](https://image.3001.net/images/20221107/1667801640_6368a22855201ff530891.png!small)

