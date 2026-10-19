**大家好，我是独立团孙德胜！**

![](https://image.3001.net/images/20191106/1573026221_5dc279ad5b99d.png!small)

CTF，是最近大火的一个IP……

**![](https://image.3001.net/images/20191106/1573026232_5dc279b890b16.png!small)**

随之而来的是大批CTF训练平台和CTF比赛的到来。

**![](https://image.3001.net/images/20191106/1573026238_5dc279bee9753.png!small)**

这其中呢，具有代表的CTF比赛有老牌的WCTF、XCTF，还有各大厂所举办的数不清的CTF比赛，这里为了避免广告嫌疑， 不写上了。

![](https://image.3001.net/images/20191106/1573026255_5dc279cf2acf6.png!small)

但是呢，可以给大家安利个好的CTF训练平台，老牌的Bugku咱不提，基本上都知道。

**![](https://image.3001.net/images/20191106/1573026263_5dc279d7936ae.png!small)**

但新起之秀的圈子的砺剑CTF平台、BUUCTF 以及未来我朋友的超级平台（字节脉搏）也即将上线了。

![](https://image.3001.net/images/20191106/1573026270_5dc279de8d02a.png!small)

**![](https://image.3001.net/images/20191106/1573026273_5dc279e1013f0.png!small)**

这些平台无疑都采用了动态靶场 + 丰富的CTF题目，更有的还有今年各大比赛的原题，实属“牛批”……

**![](https://image.3001.net/images/20191106/1573026279_5dc279e76205f.png!small)**

那你想不想做一个，一样的CTF平台呢？

**![](https://image.3001.net/images/20191106/1573026285_5dc279ed48ee6.png!small)**

那就由孙德胜，来教大家如何搭建CTF的训练平台，以及炫酷的CTF比赛平台！

**![](https://image.3001.net/images/20191106/1573026291_5dc279f3b5f96.png!small)**

_训练平台，感谢琴里大佬提供_

**![](https://image.3001.net/images/20191106/1573026298_5dc279fa5f5f4.png!small)**

_比赛平台，感谢琴里大佬提供_

## 训练平台搭建方法（CTFd）

安装git

    
    
    sudo apt-get install git

下载ctfd

    
    
    sudo git clone<https://github.com/isislab/CTFd.git>

[](https://github.com/isislab/CTFd.git)

安装pip

    
    
    sudo apt-get install python-pip

安装pip

    
    
    sudo apt-get install python-pip

安装Flask

    
    
    sudo pip2 install Flask

到 CTFd的路径下，运行prepare.sh

    
    
    sudo ./prepare.sh

运行CTFd目录下的serve.py

    
    
    sudo python serve.py 

安装完成

![](https://image.3001.net/images/20191106/1573026378_5dc27a4a97718.png!small)

访问IP

**![](https://image.3001.net/images/20191106/1573026380_5dc27a4cda71b.png!small)**

**步骤太繁琐？网上同类文章太多？想一键获取搭建好的CTF平台？刚好，你认识孙德胜，文章结尾提供建好的镜像！**

**一键部署，快人一步！**

##  比赛平台搭建

安装Git

    
    
    git clone [https://github.com/facebook/fbct](https://github.com/facebook/fbctf)

[](https://github.com/facebook/fbctf)

进入FBCTF文件夹

    
    
    cd fbctf

安装Virtualbox和Vagrant

    
    
    apt-get install virtualbox vagrant

查看Vagrant版本

    
    
    vagrant -v

下载安装Ubuntu14.04（需要安装Virtualbox）

    
    
    vagrant box add ubuntu/trusty64   

通过Vagrant开启虚拟机

    
    
    vagrant up

开启成功后，可以通过浏览器访问 [https://10.10.10.5](https://10.10.10.5/) 使用平台，并且可以通过‘vagrant
ssh’命令连接Ubuntu14.04，连接后源代码位置：/var/www/fbctf/，做二次开发可以直接修改源代码，修改后重启服务即可。

![](https://image.3001.net/images/20191106/1573026413_5dc27a6d9c0e9.png!small)

**什么？还是不想搭建?想一键获取搭建好的CTF平台？那么，巧了！因为你认识孙德胜，所以依旧在文章的结尾提供建好的镜像。**

**![](https://image.3001.net/images/20191106/1573026422_5dc27a76218cf.png!small)**

## 现在，我们讨论如何生成动态靶机。

利用大佬开发的CTFd-Whale：

1、在机器上安装好 Docker 和 Docker-Compose，并且启用 Docker Swarm。

> Docker Swarm 参考：<https://www.jianshu.com/p/77c4c62d9afe>

注意需要用以下命令来标记节点：

> docker node ls #检查节点 ID
>
> docker node update --label-add name=linux-1 <节点 ID>

参考链接：

> <https://docs.docker.com/install/linux/docker-ce/ubuntu/>
>
> <https://docs.docker.com/compose/install/>

2、在机器上下载代码。

> git clone -b single <https://github.com/glzjin/CTFd.git>

3、进入目录，编辑 frp 两端配置文件，使 token 随机，再使用 docker-compose 启动相关组件。

    
    
    cd CTFd
    
        vi frp/frps.ini # token 一定要随机
    
        vi frp/frpc.ini # token 一定要随机
    
        git submodule update --init
    
        docker-compose up -d

4、启动完毕，打开 [http://ip:8000](http://ip:8000/) 安装 CTFd。

5、进入系统后台设置，打开插件设置页面，按照如下指导进行设置。点击可看大图。

**![](https://image.3001.net/images/20191106/1573026436_5dc27a84dea49.png!small)**

**![](https://image.3001.net/images/20191106/1573026439_5dc27a87641ba.png!small)**

Frp Config Template，记得修改 token:

    
    
     [common]
    
        token = randomme
    
        server_addr = 172.1.0.4
    
        server_port = 6490
    
        pool_count = 200
    
        tls_enable = true
    
        admin_addr = 172.1.0.3
    
        admin_port = 7400

其他内容无特殊情况无需修改。

6、添加一个题目，进行测试。

**![](https://image.3001.net/images/20191106/1573026474_5dc27aaa8af08.png!small)**

**![](https://image.3001.net/images/20191106/1573026479_5dc27aaf911fd.png!small)**

**具体可以参照这位大佬的博客：**

> <https://www.zhaoj.in/read-6333.html>  
>

##  当你做完了以上的所有步骤，恭喜你，你已经成功搭建CTF平台了！

最后，我要感谢以下的几位大佬：

> **@圈子社区 国士无双**
>
> **@圈子社区 段鹏**
>
> **@Tone**
>
> **@glzjin**
>
> **@admin-琴里**

##  **没有你们，就没有德胜的这篇文章，非常感谢！**

![](https://image.3001.net/images/20191106/1573026511_5dc27acf01258.png!small)

> **比赛平台：链接：**[
> **https://pan.baidu.com/s/1BWPGqLRUAyBcl-81c3xKGg**](https://pan.baidu.com/s/1BWPGqLRUAyBcl-81c3xKGg)[#](https://www.freebuf.com/wp-> admin/post.php?post=219255&action=edit#%E6%AF%94%E8%B5%9B%E5%B9%B3%E5%8F%B0%EF%BC%9A%E9%93%BE%E6%8E%A5%EF%BC%9Ahttps://pan.baidu.com/s/1BWPGqLRUAyBcl-81c3xKGg-)
>
> **提取码：zcfr**[#](https://www.freebuf.com/wp-> admin/post.php?post=219255&action=edit#%E6%8F%90%E5%8F%96%E7%A0%81%EF%BC%9Azcfr-)
>
> **训练平台：链接：**[
> **https://pan.baidu.com/s/1N_IBcgH5lUpoUzrwC7_ifg**](https://pan.baidu.com/s/1N_IBcgH5lUpoUzrwC7_ifg)[#](https://www.freebuf.com/wp-> admin/post.php?post=219255&action=edit#%E8%AE%AD%E7%BB%83%E5%B9%B3%E5%8F%B0%EF%BC%9A%E9%93%BE%E6%8E%A5%EF%BC%9Ahttps://pan.baidu.com/s/1N_IBcgH5lUpoUzrwC7_ifg-)
>
> **提取码：zvz6**[#](https://www.freebuf.com/wp-> admin/post.php?post=219255&action=edit#%E6%8F%90%E5%8F%96%E7%A0%81%EF%BC%9Azvz6-)

 ***本文作者：独立团孙德胜，转载请注明来自FreeBuf.COM**

