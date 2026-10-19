![](https://image.3001.net/images/20211227/1640600137_61c99249f0c07726bff38.jpg!small)

## 关于whoc

whoc是一个功能强大的容器镜像，它可以帮助广大研究人员将底层容器运行时环境提取并发送至远程服务器。在该工具的帮助下，我们可以轻松查看自己感兴趣的CSP容器平台的底层容器运行时环境！

## 运行机制

根据漏洞[ _CVE-2019-5736_](https://unit42.paloaltonetworks.com/breaking-docker-via-runc-explaining-cve-2019-5736/)的描述，传统的Linux容器运行时环境会将自身通过/proc/self/exe运行的这一个情况暴露给容器，让容器所知晓。而whoc可以使用这个链接来读取容器运行时环境并执行它。

### 动态模式

动态模式是whoc的默认模式，该模式主要针对的是动态链接容器运行时。

1、whoc镜像入口点设置为/proc/self/exe，镜像的动态链接器ld.so会被upload_runtime替换。

2、当镜像开始运行之后，容器运行时会在容器内进行重新执行。

3、考虑到运行时环境是动态链接的，内核会加载我们伪造的动态链接器（upload_runtime）至运行时进程，并传递执行命令给它。

4、upload_runtime将通过/proc/self/exe读取运行时代码，并将其发送至配置好的远程服务器。

![](https://image.3001.net/images/20211227/1640600152_61c99258b42ba60585d98.png!small)

### Wait-For-Exec模式（等待执行）

针对静态链接的容器运行环境，whoc也提供了相应的解决方案：whoc:waitforexec。

1、upload_runtime为镜像入口点，并以whoc容器PID 1运行。

2、用户需要在whoc容器中执行，并调用一个指向/proc/self/exe的文件（例如“docker exec whoc_ctr
/proc/self/exe”）。

3、执行发生之后，容器运行时环境会在容器内部重新执行。

4、upload_runtime通过/proc/$runtime-pid/exe读取运行时代码，并将其发送至配置好的远程服务器。

![](https://image.3001.net/images/20211227/1640600158_61c9925eac6f110c013be.png!small)

## 本地使用

我们首先需要在本地设备上安装并配置好Docker和Python3环境，接下来，再使用下列命令将该项目源码克隆至本地：

    
    
    $ git clone git@github.com:twistlock/whoc.git

配置一个文件服务器来接收提取到的容器运行时环境：

    
    
    $ cd whoc
    
    $ mkdir -p stash && cd stash
    
    $ ln -s ../util/fileserver.py fileserver
    
    $ ./fileserver

在另一个Shell中，切换到自己的容器环境并运行whoc镜像：

    
    
    $ cd whoc
    
    $ docker build -f Dockerfile_dynamic -t whoc:latest src  # or ./util/build.sh
    
    $ docker run --rm -it --net=host whoc:latest 127.0.0.1  # or ./util/run_local.sh

![](https://image.3001.net/images/20211227/1640600179_61c99273d3c5aa3cf475c.png!small)

我们可以看到，文件服务器接收到了容器运行时环境，如果你是在vanilla Docker中运行whoc的话，接收到的容器运行时环境应该为[
_runc_](https://github.com/opencontainers/runc)。

“--net=host”只适用于本地测试，因此whoc容器可以轻松通过“127.0.0.1”访问主机的文件服务器。

### 帮助信息

如需获取whoc的主要帮助信息，可以运行下列命令：

    
    
    Usage: upload_runtime [options] <server_ip>
    
     
    
    Options:
    
     -p, --port                 Port of remote server, defaults to 8080
    
     -e, --exec                 Wait-for-exec mode for static container runtimes, waits until an exec to the container occurred
    
     -b, --exec-bin             In exec mode, overrides the default binary created for the exec, default is /bin/enter
    
     -a, --exec-extra-argument  In exec mode, pass an additional argument to the runtime so it won't exit quickly
    
     -r, --exec-readdir-proc    In exec mode, instead of guessing the runtime pid (which gives whoc one shot of catching the runtime),
    
                                find the runtime by searching for new processes under '/proc'

## 项目地址

 **whoc：** 【[ _GitHub传送门_](https://github.com/twistlock/whoc)】

## 参考资料

> 1、[
> _https://www.you*tube.com/watch?v=DF0qoCsHKT4﻿_](https://www.youtube.com/watch?v=DF0qoCsHKT4)
>
> 2、[ _https://unit42.paloaltonetworks.com/azure-container-> instances/_](https://unit42.paloaltonetworks.com/azure-container-instances/)
>
> 3、[ _https://unit42.paloaltonetworks.com/breaking-docker-via-runc-> explaining-cve-2019-5736/_](https://unit42.paloaltonetworks.com/breaking-> docker-via-runc-explaining-cve-2019-5736/)
>
> 4、[
> _https://github.com/opencontainers/runc_](https://github.com/opencontainers/runc)

