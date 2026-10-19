在网上看到reGeorg+Proxifier正向代理的文章很多，于是自己也尝试复现复现，结果经历了一个多星期都没有成功，先来看看我是怎么操作的！！！

##  **1.** **实验环境** **介绍**

客户机192.168.218.20-----192.168.218.201服务器------公网

说明：客户机只有一个接口并且不能出网，服务器没有提供路由转发功能，客户机只有代理成功才能上网。

##  **2.客户端配置**

安装python2.7 ；上传reGeorgSocksProxy.py文件

![1639633686_61bad3163ff314a866a8c.png!small](https://image.3001.net/images/20211216/1639633686_61bad3163ff314a866a8c.png!small)

安装配置Proxifier客户端软件

![1639633700_61bad324b172993d999b0.png!small](https://image.3001.net/images/20211216/1639633700_61bad324b172993d999b0.png!small)

python.exe和访问本地127.0.0.1的需要放行，其他流量可以走代理

![1639633724_61bad33c8d55add806e30.png!small](https://image.3001.net/images/20211216/1639633724_61bad33c8d55add806e30.png!small)

##  **3.服务器搭建web网站(phpstudy方式)**

注意：php需要使用低版本

![1639633732_61bad344b1b87289b5968.png!small](https://image.3001.net/images/20211216/1639633732_61bad344b1b87289b5968.png!small)

将tunnel.nosocket.php或者tunnel.php放到网站根目录，再使用客户机访问该页面，如果出现下图所示字样表示可以进行漏洞利用

![1639633739_61bad34b7edfe2a73f1ee.png!small](https://image.3001.net/images/20211216/1639633739_61bad34b7edfe2a73f1ee.png!small)

##  **4.客户机建立隧道**

![1639633767_61bad367ac75da8c967b4.png!small](https://image.3001.net/images/20211216/1639633767_61bad367ac75da8c967b4.png!small)

cd c:\

cd reGeorg-master

python reGeorgSocksProxy.py -p 9999 -u
http://192.168.218.201:8003/hackable/uploads/tunnel.nosocket.php

出现下图字样表示隧道建立成功

![1639633780_61bad3744f55328efbe9a.png!small](https://image.3001.net/images/20211216/1639633780_61bad3744f55328efbe9a.png!small)

##  **5.客户机进行访问**

客户机始终无法访问成功，代理一直报错

![1639633831_61bad3a7316011de81a2e.png!small](https://image.3001.net/images/20211216/1639633831_61bad3a7316011de81a2e.png!small)

在服务端抓包查看，服务器已经收到代理报文，但是没有转发出去，问题应该出在服务器上

![1639633855_61bad3bfe111bcfb4281b.png!small](https://image.3001.net/images/20211216/1639633855_61bad3bfe111bcfb4281b.png!small)

翻阅了很多文章，做了N种尝试，始终没有解决，后来再高人指点下，建议使用其他服务器。

\-----------------------------分割线----------------------------------
让我们忘记前面的操作，从新开始

##  **6.** **使用Docker搭建DVWA环境** **进行测试**

下载dvwa镜像

cd /home/

git clone https://hub.fastgit.org/MyKings/docker-vulnerability-environment.git

cd docker-vulnerability-environment/DVWA

创建dvwa容器

docker build -t dvwa .

交互创建一个容器, 本容器 80 端口映射到宿主机的 8003 端口上，端口根据需要修改

docker run -d --name dvwa_vul -p 0.0.0.0:8003:80 dvwa

登录DVWA 账号密码：admin/password

![1639634067_61bad4930d38870763d69.png!small](https://image.3001.net/images/20211216/1639634067_61bad4930d38870763d69.png!small)

登录DVWA，第一次需要创建数据库

![1639634034_61bad472b6998082205d9.png!small](https://image.3001.net/images/20211216/1639634034_61bad472b6998082205d9.png!small)

搭建成功

![1639634115_61bad4c38c4bdced01372.png!small](https://image.3001.net/images/20211216/1639634115_61bad4c38c4bdced01372.png!small)

##  **7.在dvwa中上传tunnel.nosocket.php文件**

![1639634123_61bad4cb3e22acd4de456.png!small](https://image.3001.net/images/20211216/1639634123_61bad4cb3e22acd4de456.png!small)

客户机访问http://192.168.218.201:8003/hackable/uploads/tunnel.nosocket.php出现下图所示字样表示可以利用

![1639634138_61bad4da0cdeeac2b37ec.png!small](https://image.3001.net/images/20211216/1639634138_61bad4da0cdeeac2b37ec.png!small)

##  **8.客户机(安装python2.7)，上传reGeorgSocksProxy.py文件**

![1639634151_61bad4e7dc54116e84f9c.png!small](https://image.3001.net/images/20211216/1639634151_61bad4e7dc54116e84f9c.png!small)

##  **9.客户机建立隧道**

cd c:\

cd reGeorg-master

python reGeorgSocksProxy.py -p 9999 -u
http://192.168.218.201:8003/hackable/uploads/tunnel.nosocket.php

出现下图字样表示隧道建立成功

![1639634161_61bad4f1423062b35c3e8.png!small](https://image.3001.net/images/20211216/1639634161_61bad4f1423062b35c3e8.png!small)

##  **10.安装配置Proxifier_setup_v3.31客户端代理软件**

python.exe和访问本地127.0.0.1的需要放行，其他流量可以走代理

![1639634173_61bad4fd8d6762679e86a.png!small](https://image.3001.net/images/20211216/1639634173_61bad4fd8d6762679e86a.png!small)

![1639634180_61bad5040befece161f76.png!small](https://image.3001.net/images/20211216/1639634180_61bad5040befece161f76.png!small)

## 6.代理通信测试

通信测试成功

![1639634187_61bad50b35161c7ea3ad5.png!small](https://image.3001.net/images/20211216/1639634187_61bad50b35161c7ea3ad5.png!small)

## 7.写在后面

这个实验本身比较简单，就是工具的使用，但是由于未知原因，导致服务端不转发数据，从而导致实验失败，发现服务端存在问题后，若无法解决，就解决服务端，及时更换服务端即可！！

