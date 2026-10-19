本文由东塔网络安全学院-10期班学员-lwy投稿

## 漏洞简介

由于Tomcat默认开启的AJP服务（8009端口）存在一处文件包含缺陷，攻击者可构造恶意的请求包进行文件包含操作，进而读取受影响Tomcat服务器上的Web目录文件。

https://cve.mitre.org/cgi-bin/cvename.cgi?name=2020-1938

## 影响范围

Apache Tomcat 6

Apache Tomcat 7 < 7.0.100

Apache Tomcat 8 < 8.5.51

Apache Tomcat 9 < 9.0.31

1\. 先装docker 环境

1.1 apt-get update

1.2 apt-get install -y apt-transport-https ca-certificates

1.3 apt-get install dirmngr

1.4 curl -fsSL https://mirrors.tuna.tsinghua.edu.cn/docker-ce/linux/debian/gpg
| sudo apt-key add -
1.5 echo 'deb https://mirrors.tuna.tsinghua.edu.cn/docker-ce/linux/debian/
buster stable' | sudo tee /etc/apt/sources.list.d/docker.list

1.6 apt-get update

1.7 apt install docker-ce

1.8 service docker status~

1.9 service docker status

2.0 service docker start

2.1 service docker version

2.2 docker version

2.3 docker run hello-world

![](https://image.3001.net/images/20210107/1610000546_5ff6a8a29c1f5d6f0d4ac.png!small)

环境搭建：

下载镜像 docker pull negoowen/ghostcat:1.0

![](https://image.3001.net/images/20210107/1610000554_5ff6a8aae02cf516853d5.png!small)

启动镜像

docker run -d -p 8080:8080 -p 8009:8009 --name ghostcat negoowen/ghostcat:1.0

![](https://image.3001.net/images/20210107/1610000562_5ff6a8b27b71f24692abf.png!small)

![](https://image.3001.net/images/20210107/1610000576_5ff6a8c072eb9a280ad76.png!small)

  

## 漏洞复现

读取文件

镜像里已经写入一个test.txt文件,以此文件做测试

![](https://image.3001.net/images/20210107/1610000584_5ff6a8c8a9c97368979d7.png!small)

python CVE-2020-1938.py -p 8009 -f test.txt 192.168.195.133

![](https://image.3001.net/images/20210107/1610000593_5ff6a8d1163a1ee5e4123.png!small)

## 修复建议

1.官方升级

Apache Tomcat 7.0.100

Apache Tomcat 8.5.51

Apache Tomcat 9.0.31

2\. 关闭AJP默认开启端口（这里是8009）或只监听本地

