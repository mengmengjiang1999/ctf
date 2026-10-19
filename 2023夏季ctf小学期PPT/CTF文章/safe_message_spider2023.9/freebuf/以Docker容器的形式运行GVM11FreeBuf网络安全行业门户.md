##  一、 **操作目的和应用场景**

 **大家好，我是彭瑞。**

**前面我发表了一篇关于OpenVAS的文章，讲述如何以docker容器的方式运行OpenVAS进行漏洞扫描。随着OpenVAS软件的不断升级，从版本10开始，OpenVAS被改名为GVM-10（Greenbone
Vulnerability Management）。下面我给大家介绍一下docker版本的GVM-11的使用方法。**

OpenVAS（Open Vulnerability Assessment
System）是在nessus基础上发展起来的一个开源的漏洞扫描程序，其核心部件是一套漏洞测试程序，可以检测远程系统和应用程序中的安全问题。

##  二、 **平台及工具版本**

> host系统：linux mint 19.3
>
> 软件：GVM 11、docker
>
> 计算机硬件：笔记本电脑

##  三、 **操作步骤**

（一） **在linux mint系统中安装docker**

apt install docker.io //在线安装docker

systemctl start docker //启动docker服务

systemctl enable docker //设置开机自动启动

![](https://image.3001.net/images/20200516/1589572036_5ebef1c4dfa45.png!small)docker
version //查看docker版本

![](https://image.3001.net/images/20200516/1589572048_5ebef1d0eb53d.png!small)可以正常显示版本信息，说明安装成功。

（二） **下载和运行GVM的docker镜像**

**1、** **下载GVM 11的docker镜像**

docker search gvm

![](https://image.3001.net/images/20200516/1589572079_5ebef1ef8a86f.png!small)

第一个镜像是我们需要的。

docker pull securecompliance/gvm //将镜像pull到本地

![](https://image.3001.net/images/20200516/1589572106_5ebef20ab8ac7.png!small)docker
search gvm //查看本地的docker镜像

![](https://image.3001.net/images/20200516/1589572119_5ebef2175b61b.png!small)

**2、运行GVM 11镜像**

docker run -d -p 8080:9392 --name gvm securecompliance/gvm

run命令装载docker镜像到内存，形成容器。

> -d //后台运行容器
>
> -p //将host的8080端口映射到容器的9392端口
>
> \--name //给容器起个名字

docker ps //查看正在运行的docker容器，可以看到GVM容器已经运行起来了

![](https://image.3001.net/images/20200516/1589572135_5ebef227dcbe5.png!small)根据计算机配置的不同，容器启动后需要几秒到几十分钟左右的时间进行初始化，主要工作是NVT特征苦更新和数据库构建。在宿主机上抓包得到的信息：

![](https://image.3001.net/images/20200516/1589572148_5ebef23438fd9.png!small)

这个工作完成后会创建默认的admin账户。如果无法访问web界面，则说明容器还在准备中。如果想知道容器的准备工作到了什么阶段，可以使用下面的命令：

docker logs gvm

![](https://image.3001.net/images/20200516/1589572160_5ebef24068672.png!small)若看到“our
GVM 11 container is now ready to use!”，就可以使用了。（时间较长，请耐心等待）

![](https://image.3001.net/images/20200516/1589572170_5ebef24ad193e.png!small)

（三） **使用GVM进行漏洞扫描**

**1、登录**

浏览器打开GVM的控制台界面：

> <http://192.168.1.7:8080/login>

![](https://image.3001.net/images/20200516/1589572187_5ebef25b9e373.png!small)用户名/口令：admin/admin，点击login按钮登录。

注意，这里用：

> [https://localhost:8080](https://localhost:8080/)

是无法访问GVM控制台的。

**2、创建扫描任务**

下面创建简单的扫描任务，对metasploitable 2靶机进行漏洞扫描。

（1）创建扫描任务

Scans—Tasks

![](https://image.3001.net/images/20200516/1589572210_5ebef27259047.png!small)点击左侧带有五角星的方框，点击弹出的“New
Tasks”项：

![](https://image.3001.net/images/20200516/1589572237_5ebef28dd6481.png!small)

在“New task”窗口，填写下面的信息：

> Name：指定扫描名称，如“metasploitable 2”
>
> Comment：填写关于扫描任务的描述文字（可选）
>
> Scan Targets：点击右侧五角星，弹出New Target表单。指定目标IP地址，填写完成后点击Save按钮提交：

![](https://image.3001.net/images/20200516/1589572257_5ebef2a18a741.png!small)其它的选项保持默认即可：

![](https://image.3001.net/images/20200516/1589572268_5ebef2acbcb21.png!small)

点击下方的Save按钮，创建扫描任务。

**3、** **开始扫描**

在任务列表中，点击右侧Actions中的Start按钮，开始扫描。

![](https://image.3001.net/images/20200516/1589572281_5ebef2b92903c.png!small)在靶机上抓包，可以看到GVM扫描所产生的流量：

![](https://image.3001.net/images/20200516/1589572292_5ebef2c477303.png!small)

**4、** **下载扫描报告**

点击Scans—Reports

![](https://image.3001.net/images/20200516/1589572311_5ebef2d7d073c.png!small)点击“metasploitable
2”任务对应的日期：

![](https://image.3001.net/images/20200516/1589572322_5ebef2e2a42f7.png!small)点击左上角一排小图标中的向下小箭头，弹出“Component
Content for Scan Report”表单。选择报告类型，如PDF：

![](https://image.3001.net/images/20200516/1589572334_5ebef2ee3d204.png!small)点击OK按钮，下载漏洞扫描报告。

报告中对某漏洞的描述：

![](https://image.3001.net/images/20200516/1589572347_5ebef2fb61ae7.png!small)

**5、** **GVM-11扫描结果与OpenVAS-9的对比**

![](https://image.3001.net/images/20200516/1589572412_5ebef33c45a36.png!small)

在同一台机器上先后运行容器版的GVM-11和OpenVAS-9，NVT都更新到最新，扫描相同的virtualbox虚拟机。从结果看，GVM-11与openvas-9相比在扫描效率和扫描到的漏洞数量上都有所提升。

**6、更新NVT**

重启GVM容器即可更新NVT特征库，无需单独运行命令。

（四） **管理容器**

**1、** **查看容器内运行的进程**

docker top gvm

![](https://image.3001.net/images/20200516/1589572451_5ebef363bd115.png!small)

**2、** **进入容器内的命令行**

docker exec -it gvm bash

![](https://image.3001.net/images/20200516/1589572468_5ebef374775bf.png!small)

**3、** **设置** **admin（管理员）** **口令**

在运行镜像时，通过修改环境变量PASSWORD来指定admin口令：

docker run -d -p 8080:9392 -e PASSWORD="Your admin password here" --name gvm
securecompliance/gvm

-e PASSWORD //设置环境变量PASSWORD，用自定义的口令替换“Your admin password here”

![](https://image.3001.net/images/20200516/1589572484_5ebef38402875.png!small)

经测试，在命令行指定口令后，admin用户可以使用新口令登录GVM。

**4、使用数据卷**

在运行镜像时，将宿主机的/gvm-data目录映射到容器的/share目录：

mkdir /gvm-data //宿主机创建本地目录，容器中的目录无需手工创建

docker run -d -p 8080:9392 -v /gvm-data:/shared --name gvm-2
securecompliance/gvm

![](https://image.3001.net/images/20200516/1589572511_5ebef39f57438.png!small)docker
exec -it gvm-2 bash //进入容器，将文件复制到容器内的/shared目录中，该文件立刻就会出现在宿主机的/gvm-data目录中

![](https://image.3001.net/images/20200516/1589572529_5ebef3b16343c.png!small)

**5、** **停止容器**

docker stop gvm

![](https://image.3001.net/images/20200516/1589572541_5ebef3bdb46e0.png!small)

**6、删除容器**

不再需要容器了，可以将其删除。删除容器不会影响到镜像，使用前面运行镜像的命令可以创建新的容器。

> docker ps --all //查看全部容器，包括运行的和已停止的
>
> docker rm gvm //删除名为gvm的容器

（五） **管理镜像**

**1、导出镜像**

docker save -o gvm-11-image.tar securecompliance/gvm
//将镜像导出到当前目录，名为gvm-11-image.tar

![](https://image.3001.net/images/20200516/1589572566_5ebef3d639717.png!small)

2、删除镜像

docker rmi securecompliance/gvm

![](https://image.3001.net/images/20200516/1589572577_5ebef3e1d1927.png!small)

//删除镜像时，不能存在由该镜像创建的容器

**3、导入镜像**

docker rmi securecompliance/gvm //删除镜像

docker load < gvm-11-image.tar //导入镜像

![](https://image.3001.net/images/20200516/1589572606_5ebef3fed0937.png!small)

##  **四、注意事项**

GVM-11容器启动后默认不像OpenVAS那样监听本地环回地址，而是监听物理网卡地址。这样即提供了远程访问功能。因此应使用防火墙对访问GVM的源地址进行限制：

> iptables -A INPUT -p tcp -s 192.168.1.100 --dport 8080 -j ACCEPT
> //允许192.168.1.100访问本地的GVM控制台
>
> iptables -A INPUT -p tcp --dport 8080 -j REJECT //拒绝访问本地8080端口

 ***本文作者：regitnew，转载请注明来自FreeBuf.COM**

