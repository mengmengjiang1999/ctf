# 前言

因为团队要搭建自己的靶场，所以去学习了下如何搭建CTFD。这里主要参考的是鲸猫的文章：[ctfd使用ctfd-whale动态靶机插件搭建靶场指南](https://vaala.cat/2020/09/21/ctfd%E4%BD%BF%E7%94%A8ctfd-whale%E5%8A%A8%E6%80%81%E9%9D%B6%E6%9C%BA%E6%8F%92%E4%BB%B6%E6%90%AD%E5%BB%BA%E9%9D%B6%E5%9C%BA%E6%8C%87%E5%8D%97/)，在这里非常感谢！

注意：某些步骤需要使用梯子（会标注），请提前自备

# 部署

这里我使用的是[鲸猫的仓库](https://github.com/VaalaCat/CTFd)，已经进行了一些配置和换源工作，比较方便部署

## 准备工作

### 安装环境

操作系统：  
使用unbuntu 20.4 64位，CentOS版本的可以参考这篇文章：[CTFD支持动态靶机的搭建笔记（docker：ctfd+ctf-whale）](https://err0r.top/article/CTFD/)

动态靶机通过`docker，docker-compose,docker-swarm`实现，没有docker基础的可以看一下这个视频了解一下:[【docker入门】10分钟，快速学会docker](https://www.bilibili.com/video/BV1R4411F7t9)，这里是docker-compose的基础讲解：[【docker入门2】实战~如何组织一个多容器项目docker-compose](https://www.bilibili.com/video/BV1Wt411w72h?t=1257)，至于docker-swarm我们只需要使用其中的一两个命令，这里就不过多赘述

#### docker 的安装

使用官方安装脚本自动安装  
安装命令如下：

    
    
    curl -fsSL https://get.docker.com | bash -s docker --mirror aliyun
    

这里使用ubuntu的话是默认没有root用户的，所以普通用户需要添加docker组的权限,这样每次用docker就不需要再加sudo。此处[username]填自己的用户名

    
    
    sudo usermod -aG docker [username]
    

#### docker-compose的安装

    
    
    sudo pip3 install docker-compose -i https://pypi.tuna.tsinghua.edu.cn/simple
    

### 配置环境

插件使用的是集群模式，要创建一个单个服务器的集群

    
    
    docker swarm init
    

然后将这个服务器加入集群

    
    
    docker node update --label-add='name=linux-1' $(docker node ls -q)
    

接下来需要进行docker的换源工作（使用aliyun）

  1. 进入阿里云容器镜像服务的控制台，选择下方的镜像加速器  
![在这里插入图片描述](https://image.3001.net/images/20210622/1624325715_60d13e5313b4e8870978c.png!small)

  2. 将下列加速器地址复制下来  
![图片.png](https://image.3001.net/images/20210622/1624325923_60d13f23020cd8ab3aaf3.png!small)

  3. 修改文件`/etc/docker/daemon.json`(若没有自行创建)

    
    
    {
        "registry-mirrors": ["此处填镜像加速器的地址"]
    }
    

  4. 重启docker服务生效

    
    
    sudo systemctl daemon-reload
    sudo systemctl restart docker
    

## 安装

### 下载

首先使用仓库中的 ctfd，若下载速度过慢可用梯子，注意此步尽量使用命令进行，若直接下载源代码会导致插件安装命令无法进行。

    
    
    cd (你要下载的位置)
    git clone https://github.com/VaalaCat/CTFd.git --depth=1
    

### 配置

修改下列文件中的token一行的值

    
    
    cd CTFd
    vim conf/frp/frps.ini # token 一定要随机
    vim conf/frp/frpc.ini # token 一定要随机
    

接着安装插件，并启动（第一次启动尽量挂梯子运行）

    
    
    git submodule update --init
    docker-compose up -d
    

启动成功后，通过命令

    
    
    docker ps -a
    

查看是否启动镜像

# 总结

本文仅仅简单介绍了CTFD的部署流程，详细的题目上传和平台设置会逐步更新。本文在CSDN的连接：[零基础教你搭建一个自己的靶场！](https://blog.csdn.net/LSForever_/article/details/118032402)，欢迎各位大佬指导斧正！

