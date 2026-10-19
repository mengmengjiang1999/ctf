![](https://image.3001.net/images/20200322/1584868878_5e772e0e74d93.jpg!small)

##  Lazydocker

 **Lazydocker是一款专为懒人设计的Docker以及Docker-Compose终端管理工具，该工具采用Go语言开发，基于gocui实现。**

如果你发现自己的项目出了问题，或者是服务down掉了，那么Lazydocker就可以立刻给你提供帮助。Lazydocker可以帮助我们调试自己的项目或者服务，并且在出现问题时立刻重启所有组件，然后给我们提供详细的日志流。其中，日志流还会进行细项分类，并允许我们了解特定服务中发生的所有事情。

除此之外，想要记住所有的Docker命令其实是很麻烦的，而且跨多个终端窗口跟踪容器也几乎是无法做到的。但是在Lazydocker的帮助下，我们就可以在一个终端窗口中查看到所有你所需要的信息，而且常用的命令仅需按下一个键即可实现。毫无疑问，Lazydocker绝对是懒人们的福音！

##  功能介绍

Lazydocker的所有功能均可一键实现，你只需按下相应按键即可：

> 1、查看Docker或Docker-Compose容器环境的状态；
>
> 2、查看容器/服务日志；
>
> 3、查看容器ASCII图；
>
> 4、定制图表以查看更详细的信息；
>
> 5、绑定容器/服务；
>
> 6、重启/移除/重建容器或服务；
>
> 7、查看给定镜像的父层；
>
> 8、修改占用磁盘空间的容器、镜像或卷；

##  工具要求

> Docker >= 1.13 (API >= 1.25)
>
> Docker-Compose >= 1.23.2 (可选)

##  工具安装

###  Homebrew

目前，我们可以在Homebrew中找到Lazydocker项目，我们建议广大用户每次使用该工具前先进行项目更新。安装命令如下：

    
    
    brew install jesseduffield/lazydocker/lazydocker

**Core：**

    
    
    brew install lazydocker

###  Windows安装（Scoop）

你可以使用scoop在Windows平台上安装Lazydocker：

    
    
    scoop install lazydocker

###  源码安装（Linux/OSX/Windows）

当然了，你也可以直接从该项目的Release页面获取最新版本的源码。

运行下列命令，安装和更新都是自动完成的：

    
    
    curl https://raw.githubusercontent.com/jesseduffield/lazydocker/master/scripts/install_update_linux.sh | bash

###  Go安装

要求Go版本 >= 1.8

    
    
    go get github.com/jesseduffield/lazydocker

###  Arch Linux AUR

你也可以使用你的AUR包管理器来安装Lazydocker，命令如下：

    
    
    git clone <https://aur.archlinux.org/lazydocker.git> ~/lazydocker
    
        cd ~/lazydocker
    
        makepkg --install

###  Docker

1、选取ARM设备，如果你有的话。

2、运行容器：

    
    
    docker run --rm -it -v \
    
        /var/run/docker.sock:/var/run/docker.sock \
    
        -v /yourpath:/.config/jesseduffield/lazydocker \
    
        lazyteam/lazydocker

别忘了在运行之前修改Lazydocker的配置文件。如果你想要创建别名的话，可以这样：

    
    
    echo "alias lzd='docker run --rm -it -v /var/run/docker.sock:/var/run/docker.sock -v /yourpath/config:/.config/jesseduffield/lazydocker lazyteam/lazydocker'" >> ~/.zshrc

比如说，我们可以使用下列命令构建镜像：

    
    
    git clone <https://github.com/jesseduffield/lazydocker.git>
    
        cd lazydocker
    
        docker build -t lazyteam/lazydocker \
    
            --build-arg BUILD_DATE=`date -u +"%Y-%m-%dT%H:%M:%SZ"` \
    
            --build-arg VCS_REF=`git rev-parse --short HEAD` \
    
            --build-arg VERSION=`git describe --abbrev=0 --tag` \

##  工具使用

你可以直接在终端调用Lazydocker，我个人使用的别名如下：

    
    
    echo "alias lzd='lazydocker'" >> ~/.zshrc

##  工具运行截图

![](https://image.3001.net/images/20200322/1584868951_5e772e57e04af.png!small)![](https://image.3001.net/images/20200322/1584868952_5e772e5800c31.jpg!small)

##  项目地址

> Lazydocker：【[GitHub传送门](https://github.com/jesseduffield/lazydocker)】

 ***
参考来源：[jesseduffield](https://github.com/jesseduffield/lazydocker)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

