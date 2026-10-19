# 一、安装docker、docker-compose

这部分我是根据这个教程安装的，一遍成功：[kali安装docker环境 - 知乎
(zhihu.com)](https://zhuanlan.zhihu.com/p/82361096)

# 二、下载vulhub

有那啥啥的可以用git下

    
    
    git clone https://github.com/vulhub/vulhub.git

我没有那啥啥，用git下载特别特别特别慢，而且总是中断。

vulhub官网（[Vulhub - Docker-Compose file for vulnerability
environment](https://vulhub.org/#/docs/download-vulhub/)）还给了master分支压缩包的下载链接（<https://github.com/vulhub/vulhub/archive/master.zip>）

直接点击下载的话。。。一样下载不下来。。

 **复制链接，然后随便找个github下载加速器，把链接往里面一丢~**

我比较常用的加速器<https://d.serctl.com/>

下载完成后解压压缩包，给文件夹起个自己喜欢的名字，然后随便丢到哪里去都行，比如我这里就不太专业地丢到了桌面上

![](https://image.3001.net/images/20210504/1620135375_60914dcf6276a7f6717ea.png!small)

# 三、启动和移除

### 1、启动漏洞环境

（1）启动docker服务

    
    
    sudo service docker start

其实后来发现执行sudo service docker stop之后，后面的docker功能也不受影响，所以是不是必须start存疑。

（2）启动漏洞环境

进入特定漏洞地目录，然后执行

  

    
    
    sudo docker-compose up -d

然后等待一会儿就好啦~比如像下图这样

![](https://image.3001.net/images/20210504/1620135376_60914dd08ef96c952d14e.png!small)​

[Vulhub - Docker-Compose file for vulnerability
environment](https://vulhub.org/#/environments/)指示了如何验证各种漏洞环境是否创建成功。比如下图就表示上图中activemq
CVE-2015-5254的漏洞环境已经创建成功。![1620136012_6091504cb6cc54566cdf2.png!small?1620136015496](https://image.3001.net/images/20210504/1620136012_6091504cb6cc54566cdf2.png!small?1620136015496)​​​

（3）常见问题

  * ERROR: Can't find a suitable configuration file in this directory or any parent. Are you in the right directory?

![](https://image.3001.net/images/20210504/1620135377_60914dd190c069b87be91.png!small)​

出现这个问题大概率是没有进对目录，用ll命令看一下是否当前目录下还有子目录

![](https://image.3001.net/images/20210504/1620135378_60914dd249873e5e3734f.png!small)​比如这个例子中其实应该进入CVE-2015-5254目录才对

  * ERROR: Couldn't connect to Docker daemon at http+docker://localhost - is it running?

![](https://image.3001.net/images/20210504/1620135379_60914dd31e82ce594c5d9.png!small)​出现这个问题就在命令前面加个sudo吧。。sudo
docker-compose up -d

### 2、移除漏洞环境

官方给的命令是

    
    
    sudo docker-compose down

但官方也说了，这个命令它会关闭正在运行的容器，删除所有相关容器，移除NAT，但是 **不会移除编译好的漏洞镜像** 。。长期会不会有问题就看个人造化了

在网上查到个命令说是可以彻底清除所有容器，试了一下可以用来 **删除漏洞镜像**

    
    
    sudo docker system prune -a -f

下面是对这个命令的验证，不看也行

仅用sudo docker-compose down不用sudo docker system prune -a -f，再次启动环境没有编译镜像的过程

![](https://image.3001.net/images/20210504/1620135379_60914dd3ea08a97bf1779.png!small)​

使用sudo docker system prune -a -f命令

![](https://image.3001.net/images/20210504/1620135380_60914dd4edc0618e395e2.png!small)​

再次启动环境有编译镜像的过程

![](https://image.3001.net/images/20210504/1620135382_60914dd62f40ef6ec7675.png!small)

  

