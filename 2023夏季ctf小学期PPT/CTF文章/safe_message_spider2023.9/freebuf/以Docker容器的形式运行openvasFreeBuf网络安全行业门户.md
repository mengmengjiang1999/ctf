##  一、 **操作目的和应用场景**

 **大家好，我是彭瑞。**

OpenVAS（Open Vulnerability Assessment
System）是在nessus基础上发展起来的一个开源的漏洞扫描程序，其核心部件是一套漏洞测试程序，可以检测远程系统和应用程序中的安全问题。

一般来说，使用openvas可以有几种方法：一是使用安装了openvas的linux发行版，如parrotsec、backbox等，二是使用openvas官方制作的虚拟机，三是在linux系统中手动安装openvas，四是使用docker版本的openvas。其中最方便、效率最高的就是docker了，所以今天为大家介绍一下使用docker运行openvas进行漏洞扫描的方法。

##  二、 **平台及工具版本**

> host系统：linux mint
>
> 软件：docker、openvas
>
> 计算机硬件：小米笔记本电脑

##  三、 **操作步骤**

###  （一） **在linux mint系统中安装docker**

apt install docker.io //在线安装docker

systemctl start docker //启动docker服务

systemctl enable docker //设置开机自动启动

![](https://image.3001.net/images/20200418/1587204881_5e9ad3111b9ef.png!small)

docker version //查看docker版本

![](https://image.3001.net/images/20200418/1587204887_5e9ad31772b0e.png!small)
可以正常显示版本信息，说明安装成功。

###  （二） **下载和运行openvas的docker镜像**

**1、下载openvas镜像**

docker search openvas //在docker hub上搜索openvas镜像

![](https://image.3001.net/images/20200418/1587204898_5e9ad3226f14d.png!small)第一个镜像是我们需要的。

docker pull mikesplain/openvas //下载openvas镜像到本地

docker images | grep openvas //查看本地的docker镜像

![](https://image.3001.net/images/20200418/1587204920_5e9ad338c6bb2.png!small)

**2、运行openvas镜像**

docker run -d -p 443:443 --name openvas mikesplain/openvas

run命令装载docker镜像到内存，形成容器。

-d //后台运行容器

-p //将host的443端口映射到容器的443端口

\--name //给容器起个名字

镜像初次运行后，稍等几分钟再访问，因为openvas要进行NVT扫描和数据库构建。

docker ps //查看正在运行的docker容器，可以看到openvas容器已经运行起来了

![](https://image.3001.net/images/20200418/1587204935_5e9ad347ed5fe.png!small)

###  （三） **使用openvas进行漏洞扫描**

**1、登录**

浏览器打开openvas的操作界面：[https://127.0.0.1](https://127.0.0.1/)

用户名/口令：admin/admin

![](https://image.3001.net/images/20200418/1587204950_5e9ad356a4097.png!small)

**2、创建扫描任务**

下面创建简单的扫描任务，对metasploitable 2靶机进行漏洞扫描。

（1）创建扫描任务

Scans—Tasks

![](https://image.3001.net/images/20200418/1587204963_5e9ad3630f8b8.png!small)
点击左侧带有五角星的方框，点击弹出的“New Tasks”项：

![](https://image.3001.net/images/20200418/1587204973_5e9ad36d4997a.png!small)

Name：指定扫描名称，如扫描metasploitable 2

Comment：填写关于扫描任务的描述文字（可选）

Scan Targets：点击右侧五角星，弹出New Target表单，指定目标IP地址，填写完成后点击Create按钮提交：

![](https://image.3001.net/images/20200418/1587204988_5e9ad37c54953.png!small)

其它的选项保持默认即可：

![](https://image.3001.net/images/20200418/1587204998_5e9ad3864efdd.png!small)

点击下方的Create按钮，创建扫描任务。

**3、** **开始扫描**

在任务列表中，点击右侧Actions中的Start按钮，开始扫描。

![](https://image.3001.net/images/20200418/1587205010_5e9ad392657c5.png!small)

在靶机上抓包，可以看到openvas扫描所产生的流量：

![](https://image.3001.net/images/20200418/1587205021_5e9ad39ddedef.png!small)

**4、** **下载扫描报告**

点击Scans—Reports

点击左下角日期，例如点击“扫描metasploitable2靶机”任务对应的日期：

![](https://image.3001.net/images/20200418/1587205033_5e9ad3a9141ae.png!small)

在Results页面，点击Report：Results文字左边的向下小箭头，选择报告的内容，如Report：Summary and
Download。在页面下方有两种格式的报告，一种是完整报告（Full report），另一种是节选报告（filtered
report），根据需要进行选择。点击右侧Download下面的下拉列表框，选择报告文件的格式，如PDF。点击右侧向下的小箭头，下载文档：

![](https://image.3001.net/images/20200418/1587205044_5e9ad3b4a2d94.png!small)

###  （四） **管理容器**

**1、** **查看容器内运行的进程**

docker top openvas

![](https://image.3001.net/images/20200418/1587205055_5e9ad3bf1d73d.png!small)

**2、** **进入容器内的命令行**

docker exec -it openvas bash

![](https://image.3001.net/images/20200418/1587205063_5e9ad3c7e75a5.png!small)

**3、** **使用数据卷**

将数据目录挂载到/var/lib/openvas/mgr/:

mkdir data

docker run -d -p 443:443 -v $(pwd)/data:/var/lib/openvas/mgr/ --name openvas
mikesplain/openvas

注意，启动容器之前，本地目录必须存在。

**4、** **设置管理员口令**

通过修改环境变量OV_PASSWORD，在运行时指定admin口令：

docker run -d -p 443:443 -e OV_PASSWORD=securepassword41 --name openvas
mikesplain/openvas

**5、** **更新NVT**

openvas使用漏洞特征进行扫描，因此需要定期更新特征库。

docker exec -it openvas bash //进入容器，在容器中执行下面的命令

greenbone-nvt-sync

openvasmd --rebuild --progress

greenbone-certdata-sync

greenbone-scapdata-sync

openvasmd --update --verbose --progress

/etc/init.d/openvas-manager restart

/etc/init.d/openvas-scanner restart

**6、** **停止容器**

docker stop openvas

![](https://image.3001.net/images/20200418/1587205078_5e9ad3d648101.png!small)

**7、删除容器**

不再需要容器了，可以将其删除。删除容器不会影响到镜像，使用前面运行镜像的命令可以创建新的容器。

docker ps --all //查看全部容器，包括运行的和已停止的

docker rm openvas //删除名为openvas的容器

![](https://image.3001.net/images/20200418/1587205092_5e9ad3e49a349.png!small)

###  （五） **管理镜像**

**1、导出镜像**

docker save -o openvas-image.tar mikesplain/openvas //导出到当前目录，名为openvas-image.tar

**2、导入镜像**

docker load < openvas-image.tar

**3、删除镜像**

docker rmi mikesplain/openvas

![](https://image.3001.net/images/20200418/1587205103_5e9ad3efbd3dd.png!small)

//删除镜像时，不能存在由该镜像创建的容器

##  **四、总结**

我曾在乙方安全公司工作多年，在风险评估工作中常使用openvas进行漏洞扫描，它的扫描结果是令人满意的。希望今天的文章能给大家的工作带来帮助。也欢迎大家关注我的微信公众号“新蜂网络安全实验室”。

 ***本文作者： regitnew，转载请注明来自FreeBuf.COM**  
  
  

