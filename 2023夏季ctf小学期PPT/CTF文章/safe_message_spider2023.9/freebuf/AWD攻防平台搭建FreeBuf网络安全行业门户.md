## AWD攻防平台搭建

网络安全攻防对抗比赛（AWD，Attack With
Defence），是一种攻防兼备的比赛模式，综合考核参赛团队攻击、防御技术能力、即时策略的比赛模式。在AWD攻防模式中，参赛队伍分别防守同样配置的虚拟靶机，并在有限的博弈时间内，找到其他战队的薄弱环节进行攻击，同时要对自己的靶机环境进行加固防守。在模拟演练中，比赛选手全身投入，互相学习，不断完善自编代码，进一步提示了攻防比赛能力。

## 一、安装docker

 **1\. 卸载旧版本docker**

全新安装时，可忽略此步骤

执行命令：sudo apt-get remove docker docker-engine docker.io

 **2\. 更新系统软件**

执行命令：sudo apt-get update

![1667802317134.png](https://image.3001.net/images/20221107/1667802324_6368a4d471d735ed214da.png!small)

 **3\. 安装依赖包**

执行命令：

    
    
    sudo apt-get install
    apt-transport-https
    ca-certificates
    curl
    software-properties-common

![1667802340574.png](https://image.3001.net/images/20221107/1667802347_6368a4eb415ad6ef6506d.png!small)

 **4\. 添加官方密钥**

执行命令：

    
    
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
![1667802358281.png](https://image.3001.net/images/20221107/1667802364_6368a4fcc91914f22e5f4.png!small)

 **5.添加仓库**

执行命令：

    
    
    sudo add-apt-repository
    "deb [arch=amd64] https://download.docker.com/linux/ubuntu
    $(lsb_release -cs)
    stable"

![1667802371336.png](https://image.3001.net/images/20221107/1667802394_6368a51ad31330c1e55e7.png!small)

 **6\. 再次更新软件**

执行命令：sudo apt-get update

![1667802411572.png](https://image.3001.net/images/20221107/1667802416_6368a5303561365ce8bbb.png!small)

 **7\. 安装docker**

如果想指定安装某一版本，可使用 sudo apt-get install docker-ce=命令，把替换为具体版本即可。

以下命令没有指定版本，默认就会安装最新版

执行命令：sudo apt-get install docker-ce

![1667802426239.png](https://image.3001.net/images/20221107/1667802433_6368a54128ca0f1a71e52.png!small)

 **8\. 查看docker版本**

执行命令：docker -v

![1667802439900.png](https://image.3001.net/images/20221107/1667802452_6368a554547a556ff9bce.png!small)

到这里表示docker安装成功。

### 二、安装docker-compose

俩种安装docker-compose的方式，分别是github安装和pip安装。

 **1.从GitHub上安装**

（1）下载最新的docker-compose文件

`执行命令：`

    
    
    sudo curl -L https://github.com/docker/compose/releases/download/1.16.1/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
    

![1667802466107.png](https://image.3001.net/images/20221107/1667802471_6368a567d21886160a8b8.png!small)

（2）添加可执行权限

执行命令：

    
    
    sudo chmod +x /usr/local/bin/docker-compose

![1667802481517.png](https://image.3001.net/images/20221107/1667802487_6368a577d8b63fc572740.png!small)

（3）测试安装结果

执行命令：docker-compose --version

![1667802495453.png](https://image.3001.net/images/20221107/1667802502_6368a586982b0699b111e.png!small)

 **2\. 使用pip安装**

执行命令：sudo pip install docker-compose

不演示了奥，嗯哼。

## 三、安装docker-machine

 **1\. 安装virtualBox**

登陆官网：https://www.virtualbox.org/wiki/Linux_Downloads

下载下图这个版本

![1667802518229.png](https://image.3001.net/images/20221107/1667802524_6368a59c09dc226732093.png!small)

下载后，执行以下命令进行安装：  
sudo dpkg -i virtualbox-5.2_5.2.0-118431_Ubuntu_xenial_amd64.deb

 **2\. 下载并安装docker-machine**

`执行命令：`

    
    
    curl -L https://github.com/docker/machine/releases/download/v0.13.0/docker-machine-`uname -s`-`uname -m` >/tmp/docker-machine && chmod +x /tmp/docker-machine && sudo cp /tmp/docker-machine /usr/local/bin/docker-machine
    

![1667802538373.png](https://image.3001.net/images/20221107/1667802544_6368a5b0a8ddc3b19c159.png!small)

也许会报错说连接不上github

![1667802552234.png](https://image.3001.net/images/20221107/1667802558_6368a5bec3444882ee58d.png!small)

解决办法：更改/etc/文件夹下的的hosts文件添加如下内容

本机IP github.com git  
13.250.177.223 github.com  
#github.com  
192.30.253.112 github.com  
192.30.253.119 gist.github.com  
151.101.100.133 assets-cdn.github.com  
151.101.100.133 raw.githubusercontent.com  
151.101.100.133 gist.githubusercontent.com  
151.101.100.133 cloud.githubusercontent.com  
151.101.100.133 camo.githubusercontent.com  
151.101.100.133 avatars0.githubusercontent.com  
151.101.100.133 avatars1.githubusercontent.com  
151.101.100.133 avatars2.githubusercontent.com  
151.101.100.133 avatars3.githubusercontent.com  
151.101.100.133 avatars4.githubusercontent.com  
151.101.100.133 avatars5.githubusercontent.com  
151.101.100.133 avatars6.githubusercontent.com  
151.101.100.133 avatars7.githubusercontent.com  
151.101.100.133 avatars8.githubusercontent.com  
185.199.108.153 assets-cdn.github.com  
185.199.109.153 assets-cdn.github.com  
185.199.110.153 assets-cdn.github.com  
185.199.111.153 assets-cdn.github.com  
151.101.113.194 github.global.ssl.fastly.net

![1667802591351.png](https://image.3001.net/images/20221107/1667802598_6368a5e606ccf3c769c84.png!small)

 **3\. 查看版本信息**

执行命令：docker-machine version

![1667802607237.png](https://image.3001.net/images/20221107/1667802614_6368a5f6aff930cad4b3e.png!small)

到这里docker-machine安装成功

## 四、AWD攻防平台部署

 **1\. 进入awd项目**

执行命令：cd awd-platform-master/

![1667802622204.png](https://image.3001.net/images/20221107/1667802628_6368a604d080a0c881491.png!small)

 **2\. 下载docker镜像**

执行命令：docker pull zhl2008/web_14.04

![1667802636324.png](https://image.3001.net/images/20221107/1667802650_6368a61aa4c4a2ccd4137.png!small)

 **3\. 下载完成后更改镜像名**

执行命令：docker tag zhl2008/web_14.04 web_14.04

![1667802658261.png](https://image.3001.net/images/20221107/1667802664_6368a62854e79e6942611.png!small)

 **4.根据当前队伍数量copy所有的队伍的比赛文件夹: python batch.py web_dir team_number**

创建5个访问组

执行命令：python batch.py web_server 5

![1667802670763.png](https://image.3001.net/images/20221107/1667802677_6368a635e1700590ac2a8.png!small)

其中web_server是项目下的ls查看，用任意一个都可以。

![1667802684678.png](https://image.3001.net/images/20221107/1667802692_6368a644424d3e339b49a.png!small)

 **4\. 启动比赛：python start.py ./ team_number**

需要启动多少个

执行命令：例如：python start.py ./ 5

![1667802702670.png](https://image.3001.net/images/20221107/1667802709_6368a6554dc8c0f7015d6.png!small)

 **5.启动check脚本**

执行命令：

    
    
    docker attach check_server
    python check.py

![1667802718219.png](https://image.3001.net/images/20221107/1667802725_6368a6651aeb9c5510a2b.png!small)

 **6\. 搞事吧**

访问IP+8801五个队端口递推就可以了

![1667802732455.png](https://image.3001.net/images/20221107/1667802738_6368a6727a353c9f7d2a0.png!small)

 **7\. 清除队伍**

执行命令：python stop_clean.py

![1667802744722.png](https://image.3001.net/images/20221107/1667802751_6368a67fd050dc487b6e9.png!small)

 **8.查看分数**

http://10.0.210.17:8080/scorecard.php

![1667802760259.png](https://image.3001.net/images/20221107/1667802767_6368a68f01af388d679ec.png!small)

 **9.提交flag方法**

http://10.0.210.17:8080/flag_file.php?token=teamX&flag=xxxx

 **10.攻击情况**

http://10.0.210.17:8080/result.txt

