## 0x00 前言

由于在红日靶场03中遇到了反向代理这个知识点，特此将反向代理进行讲解。

如果我们对如何配置nginx反向代理都不熟悉，就更别提渗透了，所以从头到尾来搭建一遍吧。

## 0x01 理论知识

### 一、正向代理

渗透测试过程中常说的挂代理，其实是省略了两个字：正向，也就是挂正向代理。

客户端A由于某些原因不能直接访问服务端C，但是B可以直接访问C。所以我们就将发送给C的请求，先给B，B收到后**代替**A请求C，再将结果返回给我们。

所以相对于C来说，它一直以为是B请求的C，而不知道客户端真正的ip地址。

![image-20220508200556256](https://image.3001.net/images/20220620/1655717505_62b03e81170bb1ea69f69.png!small)

生活中有很多例子，例如A不认识中国首富，但是B认识首富，A想找首富借点钱，就会让B去找首富借钱。只要B肯保密，首富就只知道B找他借钱而不知道真正的其实是A。所以
**正向代理暴露的是代理服务器B的IP地址，隐藏了A的IP地址。**

在渗透测试过程中， **挂代理也不是百分百的安全，毕竟B可能不会替我们保密！**

### 二、反向代理

反向代理，A想要访问C，但是其实是访问的B，B收到A的请求后会转发给C。

生活中也有很多例子，A觉着B很有钱，找B借10万，B其实是个穷光蛋，碍于面子才说有钱的，于是找首富C借10万，B再把10万给A。

说穿了A是借的首富C的钱，但是他不知道，以为就是B的钱。

 **所以反向代理暴露的是代理服务器B的IP地址，隐藏了真实服务器C的IP地址。对于A来说是没有感觉的。**

![image-20220508200833667](https://image.3001.net/images/20220620/1655717506_62b03e825709dbff8523e.png!small)

那么反向代理怎么在渗透测试过程中识别出来呢？我们来搭建环境测试一下。

## 0x02 环境准备

环境准备工作可能时间较长，我会以最简便快速的方式介绍。

### 一、两台虚拟机的网络配置

先将两台机器上安装好docker，再配置网络哈。

![image-20220508194942260](https://image.3001.net/images/20220620/1655717507_62b03e8340120e955a599.png!small)

### 二、kali安装docker

    
    
    #添加Docker官方的GPG密钥
    curl  -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -    #更新源
    echo 'deb https://download.docker.com/linux/debian stretch stable'> /etc/apt/sources.list.d/docker.list
    #直接导入证书
    apt-get -yinstall apt-transport-https  ca-certificates  curl  gnupg2  software-properties-common
    #系统更新
    apt-get update 
    #安装docker
    apt install docker.io && docker -v
    

### 三、centos7安装docker

    
    
    curl -sSL https://get.daocloud.io/docker | sh
    
    service docker start && docker -v
    

如果下图遇到此情况，执行`rm -f /var/run/yum.pid `后再次运行即可

![image-20220508194443888](https://image.3001.net/images/20220620/1655717508_62b03e844ca851c7d868d.png!small)

### 四、Centos7 docker安装tomcat

原版docker 拉取的tomcat 中， webapps 这个目录里面是空的，没有任何内容。所以需要将其删除之后，将webapps.dist
改成webapps才能够成功，未免有些bug，我们使用别人制作好的一个无bug的镜像即可，很安全放心。

    
    
    docker pull billygoo/tomcat8-jdk8
    docker run -d -p 8080:8080 --name tomcat8 billygoo/tomcat8-jdk8
    

![image-20220508203007577](https://image.3001.net/images/20220620/1655717509_62b03e857ea3e2ec371d2.png!small)

### 五、Kali docker安装nginx

    
    
    docker pull nginx
    docker images 
    docker run --name nginx -d -p 80:80 niginx
    

### 六、物理机配置hosts文件

打开hosts文件添加一条语句，将kali的ip与域名进行对应。如果修改不了可能是hosts文件是只读的，去掉只读的勾选框即可。

![image-20220508210112699](https://image.3001.net/images/20220620/1655717510_62b03e86af7ee3d25701d.png!small)

![image-20220508210200707](https://image.3001.net/images/20220620/1655717511_62b03e8790a7b9edd5eb1.png!small)

## 0x03 配置nginx反向代理

== **因为centos7是仅主机内网机器，我们这里就不做防火墙配置了，假设物理机无法直接访问内网centos7的tomcat。** ==

我们可以直接访问kali的nginx，也就是www.nginx.com，我们想要达到的效果是：访问www.nginx.com，会自动跳转到内网centos7机器的tomcat上。

![image-20220508211228351](https://image.3001.net/images/20220620/1655717512_62b03e88689a58995a67a.png!small)

### 一、kali docker的nginx容器安装vim编辑器

![image-20220508211459340](https://image.3001.net/images/20220620/1655717513_62b03e89557f24e8bc3a7.png!small)

    
    
    docker ps -n 2
    docker exec -it nginx /bin/bash
    	apt update 			#在容器里运行
    	apt -y install vim		#在容器里运行
    

### 二、配置nginx反向代理单个服务器单个端口

下面的命令均在docker nginx容器中运行

    
    
    cd /etc/nginx/conf.d
    vim default.conf
    

![image-20220508211937873](https://image.3001.net/images/20220620/1655717514_62b03e8a791204c056adc.png!small)

在下图位置添加一句话，随后保存退出`default.conf`文件。

    
    
    proxy_pass http://192.168.111.5:8080
    

![image-20220508212514317](https://image.3001.net/images/20220620/1655717515_62b03e8b83ef52f8a34a5.png!small)

使用`nginx -t`验证有无配置错误

![image-20220508212550568](https://image.3001.net/images/20220620/1655717516_62b03e8c7addc81955c07.png!small)

确认无误后重新加载nginx的配置，或者重启docker容器

    
    
    #容器内运行
    nginx -s reload
    #重启docker容器，在容器外运行
    docker restart <容器ID>
    

随后我们再次访问`www.nginx.com`，就会发现跳转到了`tomcat`的页面（火狐浏览器需要清理浏览器缓存）

![image-20220508213156607](https://image.3001.net/images/20220620/1655717517_62b03e8d69c901cfdf4f4.png!small)

 **对比一下，配置反向代理的前后使用火狐wappalyzer插件的信息收集效果**

![image-20220508213044555](https://image.3001.net/images/20220620/1655717518_62b03e8e6334a2d168afb.png!small)

### 三、配置nginx反向代理实现访问多个URL

实现效果：访问`www.nginx.com`是tomcat页面，也就是centos7的8080端口；

而访问`www.nginx.com/XSS`，则是访问的centos7的80端口下的XSS目录

![image-20220508214929395](https://image.3001.net/images/20220620/1655717519_62b03e8f4270e90e7efd5.png!small)

我们给centos7添加个网卡，安装一下apache服务，并在网站根目录放点东西。

![image-20220508213846967](https://image.3001.net/images/20220620/1655717520_62b03e900f3dafbf06c66.png!small)

如法炮制，我在这里再添加一个`location`，后面跟了个`XSS`。因为在`location`字段后的路径不能重复。

![image-20220508213726347](https://image.3001.net/images/20220620/1655717520_62b03e90e534e2ea4aa22.png!small)

测试nginx配置和刷新nginx配置后，访问`www.nginx.com/XSS`，可以看到成功访问到了内网`centos7`的`XSS`目录

![image-20220508214149718](https://image.3001.net/images/20220620/1655717521_62b03e91be5d83af09611.png!small)

### 四、渗透测试效果

那么我在centos7的XSS目录下放入一个`shell.php`，并修改`kali`的`hosts`文件

![image-20220508215456139](https://image.3001.net/images/20220620/1655717522_62b03e928aa04c655b893.png!small)

使用蚁剑链接，

![image-20220508215639637](https://image.3001.net/images/20220620/1655717523_62b03e936afe32c0cf501.png!small)

可以看到，我们看到的信息中，上方为反向代理服务器的ip，而收集到的都是内网centos7的信息。

![image-20220508215946727](https://image.3001.net/images/20220620/1655717524_62b03e9478d95da0952c4.png!small)

### 五、关于上线被反向代理的机器

思考一下，我们是直接获得到的内网一台被反向代理的centos7机器的webshell，我们的kali无法直连centos7，centos7也不无法直连kali，也就是说我们无论使用msf或者cs生成正反向木马都不能让机器上线。

而想要上线，就必须通过反向代理服务器这台边界机。

拿到边界机后，进行端口转发或者代理隧道等，实现内网穿透，从而让被反向代理的机器上线。

