## 工具介绍

 **ArmourBird CSF是一款针对容器实例服务的安全框架，ArmourBird
CSF基于模块化实现，并且具有高度可扩展的特性，支持API自定义开发，可用于针对Docker容器环境(Docker安装)以及容器实例服务执行常规的安全监控以及其他自定义类型的安全检测。**

ArmourBird CSF基于客户端-服务器架构实现，因此ArmourBird CSF分别由两部分组成：

### CSF客户端

1、该组件负责监控目标设备上的Docker安装、容器环境以及Docker镜像状态；

2、在组件初始化过程中，它还会检测DOcker CIS分支；

3、CSF客户端所进行的安全检测任务是完全可根据用户需求来配置的，我们也会定期更新和增添CSF客户端支持的检测功能；

4、该组件核心在于保护Docker分支安全；

### CSF服务器

1、CSF服务器将作为接收端代理，主要用于接收来自于大量分布式CSF客户端生成的安全日志；

2、CSF服务器端还带有一个UI子控件，可用于统一管理和查看CSF客户端发送过来的安全漏洞以及安全问题；

3、CSF服务器端还提供了API接口以便研究人员与其他系统进行功能整合；

## 工具架构图

![1.png](https://image.3001.net/images/20190924/1569293307_5d8983fb801b1.png!small)

## CSF服务器API

### 安全问题报告API

    
    
    POST /issues：用于通过CSF客户端报告安全问题；
    
    GET /issues/{issueId}：枚举特定安全问题，带{id}；
    
    GET /issues：枚举全部CSF客户端报告的所有安全问题；
    
    PUT /issues/{issueId}：更新特定安全问题，例如漏洞威胁等级和注释等；
    
    DELETE /issues/{issueId}：删除特定问题；

### 客户端API

    
    
    POST /clients：添加一个CSF客户端；
    
    GET /clients/{clientId}：查看CSF客户端；
    
    GET /clients/：枚举所有的CSF客户端
    
    PUT /clients/{clientId}：更新CSF客户端；
    
    DELETE /clients/{clientId}：通过网络删除特定CSF客户端；

### 客户端组API

    
    
    POST /clientGroup：将客户端添加至特定的组，例如product1, HRNetwork, product2等；
    
    GET /clientGroup/{groupID}：查看客户端组详情；
    
    GET /clientGroup/：枚举所有的客户端组；
    
    PUT /clientGroup/{groupID}：更新客户端组；
    
    DELETE /clientGroup/{groupId}：删除客户端组；

## 工具安装和使用

CSF客户端将会以Docker容器的形式在运行了Docker环境的计算机实例上工作，运行命令如下：

    
    
    docker run -it --net host --pid host --userns host --cap-add audit_control \
    
    -e DOCKER_CONTENT_TRUST=$DOCKER_CONTENT_TRUST \
    
    -e CSF_CDN='<TO-UPDATE>' \
    
    -v /etc:/etc \
    
    -v /usr/bin/docker-containerd:/usr/bin/docker-containerd \
    
    -v /usr/bin/docker-runc:/usr/bin/docker-runc \
    
    -v /usr/lib/systemd:/usr/lib/systemd \
    
    -v /var/lib:/var/lib \
    
    -v /var/run/docker.sock:/var/run/docker.sock \
    
    --label csf_client \
    
    -d armourbird/csf_client

在运行上述命令之前，请确保已将命令中的CSF_CDN环境变量值修改为正确的CSF服务器地址。当容器开始运行之后，CSF客户端将会以固定时间周期向CSF服务器端发送安全日志报告。

CSF服务器端能够以Docker容器运行，或直接在Web服务器上运行，我们可以直接使用托管在hub.docker.com上的Docker镜像并利用下列命令在本地服务器上运行CSF服务器端：

    
    
    docker run -p 80:8000 -d armourbird/csf_server

### 用户可通过下列链接查看CSF服务器端：

> 仪表盘: http://< your-domain >/dashboard/
>
> API: http://< your-domain >/api/

## 构建Docker镜像

为CSF客户端构建Docker镜像：

    
    
    git clone git@github.com:armourbird/csf.git
    
    cd csf_client
    
    docker build . -t csf_client

为CSF服务器端构建Docker镜像：

    
    
    git clone git@github.com:armourbird/csf.git
    
    cd csf_server
    
    docker build . -t csf_server

## 工具运行截图

### 工具仪表盘

![2.png](https://image.3001.net/images/20190924/1569293385_5d898449737dd.png!small)

### 工具API

![3.png](https://image.3001.net/images/20190924/1569293397_5d8984558951f.png!small)

### 项目官网

Armourbird：[ _https://www.armourbird.com/_](https://www.armourbird.com/)

### 项目地址

ArmourBird CSF：【[ _GitHub传送门_](https://github.com/armourbird/csf)】

 ***参考来源：[
_armourbird_](https://github.com/armourbird/csf)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

