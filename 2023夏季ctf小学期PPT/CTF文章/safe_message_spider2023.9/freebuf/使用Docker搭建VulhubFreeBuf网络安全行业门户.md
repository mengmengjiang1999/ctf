tips：主要总结一下安装中存在的一些问题，因为[教程官网](https://vulhub.org/#/docs/)都有。

## 简单介绍

docker是一种容器化管理技术，类似于虚拟机，都是一种虚拟化的环境，你可以看成箱子做的房子；

docker-compose：docker的一种编排技术，直接通过docker来管理容器的内容，比如端口、配置等等。简洁版：教docker做事的，docker他儿子，但是比他会教docker做事。。

vulhub: 一个漏洞项目，里面包含了很多类型的漏洞，用docker来还原。

## 安装docker

    
    
    curl -s https://get.docker.com/ | sh
    

问题：如果没有curl，安装一下就好。如果curl安不上，可能是软件源的问题。

查看docker状态

    
    
    systemctl enable docker #启动一下
    systemctl status docker #查看状态
    

![图片.png](https://image.3001.net/images/20230718/1689610775_64b56a17a9caf0a2b66e9.png!small)

## 安装docker-compose

这个使用

    
    
    sudo apt install docker-compose
    

docker-compose安装完成  
![图片.png](https://image.3001.net/images/20230718/1689610795_64b56a2b3d5cbf47f43d8.png!small)

## 搭建vulhub

github直接克隆下载，卡的姚明

    
    
    git clone https://github.com/vulhub/vulhub.git
    

问题：国内无法访问github

解决：

  1. clash局域网代理，让虚拟机linux设置proxy代理，代理IP为物理机在局域网中ip，端口为7890

  2. 同1，局域网可以换成wifi

  3. 物理机下载之后传过去

  4. 配置代理软件，过程比较繁琐

## 使用vulhub

进入到具体某个漏洞，看有没有yml配置文件就知道了。使用命令

    
    
    docker-compose up -d
    

查看开放的端口

![图片.png](https://image.3001.net/images/20230718/1689610815_64b56a3f48c93ff5cd369.png!small)

## 报错

    
    
    # Couldn't connect to Docker daemon at http+docker://localhost - is it running?
    

原因：用户组问题

解决：添加用户组

    
    
    sudo gpasswd -a ${USER} docker 
    docker-compose up
    

## 总结

还是windows用docker部署vulhub方便，不用代理啥的，而且docer和compose是一块安装的（exe版本）。

> 两部曲
>
>   1. 下载docker.exe 安装时候包含docker以及compose
>
>   2. 下载vulhub，部署即可
>
>

# 参考

  1. https://vulhub.org/#/docs/

