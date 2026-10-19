## 关于Web-Hacking-ToolKit

Web-Hacking-ToolKit是一款功能强大的Web安全测试工具，Web-Hacking-ToolKit以Docker镜像的形式提供给广大安全研究人员使用，并且带有完整的图形化用户界面支持。

## 工具安装

### Docker

广大研究人员可以使用下列命令将该项目的Docker镜像拉取到本地：

    
    
    docker pull signedsecurity/web-hacking-toolkit

下列命令可以运行一个容器并绑定一个Shell：

    
    
    docker run \
    
    -it \
    
    --rm \
    
    --shm-size="2g" \
    
    --name web-hacking-toolkit \
    
    --hostname web-hacking-toolkit \
    
    -p 22:22 \
    
    -v $(pwd)/data:/root/data \
    
    signedsecurity/web-hacking-toolkit \
    
    /bin/bash

### Docker Compose

我们还可以使用Docker Compose：

    
    
    version: "3.9"
    
     
    
    services:
    
        web-hacking-toolkit:
    
            image: signedsecurity/web-hacking-toolkit
    
            container_name: web-hacking-toolkit
    
            hostname: web-hacking-toolkit
    
            stdin_open: true
    
            shm_size: 2gb
    
            ports:
    
                - "22:22" # exposed for GUI support sing SSH with X11 forwarding
    
            volumes:
    
                - ./data:/root/data
    
            restart: unless-stopped

构建并运行容器：

    
    
    docker-compose up

绑定Shell：

    
    
    docker-compose exec web-hacking-toolkit /bin/bash

## 源码构建Web-Hacking-ToolKit

广大研究人员可以使用下列命令将该项目源码克隆至本地，并构建工具镜像：

    
    
    git clone https://github.com/signedsecurity/web-hacking-toolkit.git && \
    
    cd web-hacking-toolkit && \
    
    make build-images

运行一个容器并绑定一个Shell：

    
    
    make run

## 图形化用户界面GUI支持

默认配置下，Docker容器是无法运行GUI工具的，主要是因为X11服务器不可用。如果想要使用的话，你必须修改相关的配置。在主机设备上你需要满足下列条件：

如果你使用的是Linux，你必须安装并运行X11；

如果你使用的是macOS，你必须安装并运行Xquartz：

    
    
    brew install Xquartz

## 使用SSH和X11转发

通过SSH使用X11转发功能，需要在容器中运行下列命令来开启服务器：

    
    
    start_ssh

确保你在开启容器的时候打开了22端口：

    
    
    docker run -p 127.0.0.1:22:22 ...

接下来，在连接过程中使用下列命令即可：

    
    
    ssh -X ...

## 工具组件

Amass

anew

Arjun

Burp Suite Community

curl

dnsx

ffuf

findomain

firefox

gowitness

html-tool

httpx

masscan

naabu

nmap

nuclei

sh

sigsubfind3r

sigurlfind3r

sh

subfinder

tmux

vim

wappalyzer

wuzz

## 字典文件

[ _SecLists_](https://github.com/danielmiessler/SecLists)

[ _jhaddix_](https://gist.github.com/jhaddix)/
[_txt﻿_](https://gist.github.com/jhaddix/b80ea67d85c13206125806f0828f4d10)

## 项目地址

 **Web-Hacking-ToolKit：** 【[
_GitHub传送门_](https://github.com/signedsecurity/web-hacking-toolkit)】

  

