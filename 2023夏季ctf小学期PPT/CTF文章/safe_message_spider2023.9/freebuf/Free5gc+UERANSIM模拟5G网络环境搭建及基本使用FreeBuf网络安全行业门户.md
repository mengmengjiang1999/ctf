**HW期间，为防范钓鱼，即日起FreeBuf将取消投稿文章的一切外部链接。给您带来的不便，敬请谅解~**

## 0x00 前言

而在众多研究者打算投身于5G网络安全研究的时候，一个难题自然而然的摆在大家眼前：5G网络对于一些基本设施、专业设施有着极高的要求，由此成为了一道研究5G安全的门槛所在。

因此，找到一种简单的5G网络模拟方式，用以进行5G网络的学习进而发现5G网络可能存在的安全问题成为了必须工作。

下文介绍了 **基于free5gc模拟5G核心网和UERANSIM模拟5G用户设备的模拟5G网络环境的部署搭建方法**
，并且通过完成相关配置，简单实现测试5G用户设备接入核心网的注册流程、去注册流程，模拟了一个用户设备通过模拟核心网进行实际的数据业务的过程。

这样一套模拟5G环境，可以有效缓解研究者所面临的没有实际5G环境可用以及实际环境过于复杂等问题，为5G安全研究提供一个可行的途径。

## 0x01 安装前准备工作

### 0x011 确认Linux内核版本

使用命令：`uname -a`

此命令用于确认安装的虚拟机内核版本，要求的内核版本为 **5.0.0-23-generic** 或 **5.4.0及之后** 的版本 ：

![1.1-1确认内核版本.PNG](https://image.3001.net/images/20210402/1617344734_6066b8de3d2a7613e7f89.png!small)

若当前虚拟机内核版本不符合要求，则需要更换内核，使用以下命令安装`5.0.0-23-generic`的内核：

    
    
    sudo apt install 'linux-image-5.0.0-23-generic'
    sudo apt install 'linux-headers-5.0.0-23-generic
    

安装完成后，需要重启虚拟机，并在启动时 **连按shift** 键，进入 **grub** 引导页，更换启动的Linux内核

### 0x012 通过apt安装部分基础支持组件

    
    
    sudo apt install git-all
    sudo apt-get install curl
    sudo apt install make
    sudo apt -y install gcc
    sudo apt -y install g++
    sudo apt -y install autoconf
    sudo apt -y install libtool
    sudo apt -y install pkg-config
    sudo apt -y install libmnl-dev
    sudo apt -y install libyaml-dev
    

**！安装完成后，需要执行以下命令：**

    
    
    git config --global url."https://hub.fastgit.org".insteadOf https://github.com
    

**此命令可以使得之后的`git clone`下载时，可以通过国内镜像源下载，以回避github不稳定的问题**

### 0x013 安装go语言环境

 **！注意安装go语言环境时必须为普通用户安装，否则会导致后续安装出现问题**

输入命令`go`以确认是否存在其他版本的go，若存在，则通过以下命令删除：

    
    
    sudo rm -rf /usr/local/go
    

之后开始安装需要的go语言环境：

    
    
    cd ~
    wget https://dl.google.com/go/go1.15.7.linux-amd64.tar.gz 
    sudo tar -C /usr/local -zxvf go1.15.7.linux-amd64.tar.gz
    

安装完成后，需要通过以下命令配置环境变量：

    
    
    mkdir -p ~/go/{bin,pkg,src}
    echo 'export GOPATH=$HOME/go' >> ~/.bashrc
    echo 'export GOROOT=/usr/local/go' >> ~/.bashrc
    echo 'export PATH=$PATH:$GOPATH/bin:$GOROOT/bin' >> ~/.bashrc
    source ~/.bashrc
    

之后，需要通过以下命令配置go语言模块下载代理，默认的模块下载地址由于国内网络原因，不可用：

    
    
    #下面三条配置用于保证在不同go语言版本中配置代理一定生效，建议都执行
    export GOPROXY=https://goproxy.io
    export GO111MODULE=on
    go env -w GOPROXY=https://goproxy.io
    

安装完成后，以普通用户权限运行命令`go`，确认是否安装成功，若安装成功，再补充安装以下模块，该模块为free5gc独立部署的
**日志模块，独立部署时必须安装** ：

    
    
    go get -u github.com/sirupsen/logrus
    

注：此步为 **free5gc独立部署** 的必须步骤

### 0x014 安装docker环境

通过官方安装脚本安装docker：

    
    
    curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun
    

安装完成后，运行命令`docker --version`验证

之后需要安装docker-compose，通过以下命令完成：

    
    
    sudo curl -L "https://github.com/docker/compose/releases/download/1.28.5/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    

再之后，我们需要更换docker源，默认源下载速度过慢，会导致之后部署时出现下载超时错误：

    
    
    sudo vim /etc/docker/daemon.json
    

写入内容：

    
    
    {"registry-mirrors": ["https://docker.mirrors.ustc.edu.cn"]}
    

之后重启docker服务即可完成docker的部署：

    
    
    systemctl restart docker
    

完成后，需要将当前 **普通用户** 加入docker用户组，docker用户组在上述安装时自动创建，无需手动创建：

    
    
    sudo gpasswd -a $USER docker #将当前普通用户加入docker用户组
    newgrp docker                #更新docker用户组
    

此步目的在于防止后续free5gc容器化部署时，到`make base`步骤，出现以下错误：

![1.4-1make
base报错0.PNG](https://image.3001.net/images/20210402/1617344768_6066b9004a2a36ecd5ccd.png!small)

注：此步为 **free5gc容器化部署** 的必须步骤

### 0x015 安装cmake

 **！此处装的cmake，需要3.17及以上版本，否则后续UERANSIM环境搭建会出错。**

方法 1：

    
    
    wget https://cmake.org/files/v3.20/cmake-3.20.0-rc3-linux-x86_64.tar.gz
    tar zxvf cmake-3.20.0-rc3-linux-x86_64.tar.gz
    sudo mv cmake-3.20.0-rc3-linux-x86_64 /opt/cmake-3.20.0
    sudo ln -sf /opt/cmake-3.20.0/bin/*  /usr/bin/
    

此方法优势在于安装的cmake版本可控，其中第一步的wget建议手动下载，wget方式下载速度比较慢

方法 2：

    
    
    sudo snap install cmake --classic
    

此方法优势在于简单，一条命令执行即可

### 0x016 安装mongodb

    
    
    sudo apt -y update
    sudo apt -y install mongodb wget git
    sudo systemctl start mongodb
    

注：此组件为free5gc的数据库组件，为 **free5gc独立部署** 的必须步骤

### 0x017 安装yarn

    
    
    curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -    echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
    sudo apt update && sudo apt install yarn
    

注：此组件为free5gc的webui支持组件，为 **free5gc独立部署** 的必须步骤

## 0x02 free5gc容器化部署

### 0x021 构建GTP5G模块

 **！注意构建GTP5G模块时，需要用普通用户构建，否则后续使用时会出错**

首先，通过git clone下载项目代码：

    
    
    cd ~
    git clone https://github.com/PriczOwO/gtp5g.git
    cd gtp5g
    

编译代码：

    
    
    make
    sudo make install
    

注：gtp5g模块是free5gc模拟核心网的内核模块，无论何种部署方案，都 **必须安装**

### 0x022 容器化部署free5gc模拟核心网

首先，通过git clone下载项目代码：

    
    
    cd ~
    git clone https://github.com/free5gc/free5gc-compose.git
    cd free5gc-compose
    

按照官网提示的安装流程，此时应该执行`make base`容器化安装free5gc核心网，但是由于国内网络问题，在执行make
base时，会导致脚本中`git clone`还有`go get`安装模块时出现超时错误，所以这里需要修改make base时执行的脚本，添加设置代理步骤：

    
    
    cd base
    vim Dockerfile
    

找到 **`# Get Free5GC`**一行，在此行之前添加以下代码：

    
    
    RUN git config --global url."https://hub.fastgit.org".insteadOf https://github.com
    #下面三条配置用于保证在不同go语言版本中配置代理一定生效，建议都写上
    RUN export GOPROXY=https://goproxy.io
    RUN export GO111MODULE=on
    RUN go env -w GOPROXY=https://goproxy.io
    

如果不执行此步，直接运行`make base`，会报git下载失败，如下图：

![2.2-1make
base报错1.PNG](https://image.3001.net/images/20210402/1617344798_6066b91e30d471bc22682.png!small)

出现此错误原因在于`make
base`一步实际上是指导一个docker镜像去安装部署free5gc环境，而此镜像中我们并没有配置代理，配置方法只能在指导文件Dockerfile中添加

 **！此步不可通过手动 git clone到/go/src中，原因在于虚拟机中的go环境并非docker镜像容器的go环境，手动git
clone的代码并不能被docker镜像获得并用于构建环境**

完成上述步骤后，后续即可继续执行：

    
    
    cd ~/free5gc-compose
    make base
    docker-compose build
    

其中`docker-compose build`一步可能报版本错误，原因在于上面安装`docker、docker-compose`时可能安装了较低版本的`docker、docker-compose`，此时可以选择重装`docker、docker-compose`或者修改`docker-compose.yaml`文件中第一行版本号3.8为当前版本，建议优先选择重装`docker、docker-compose`，以回避未知错误

通过命令`docker --version`命令查询当前版本，并对应下面链接中的表格：

 **Compose file format**|  **Docker Engine release**  
---|---  
Compose specification| 19.03.0+  
3.8| 19.03.0+  
3.7| 18.06.0+  
3.6| 18.02.0+  
3.5| 17.12.0+  
3.4| 17.09.0+  
3.3| 17.06.0+  
3.2| 17.04.0+  
3.1| 1.13.1+  
3.0| 1.13.0+  
2.4| 17.12.0+  
2.3| 17.06.0+  
2.2| 1.13.0+  
2.1| 1.12.0+  
2.0| 1.10.0+  
1.0| 1.9.1.+  
  
至此，free5gc容器化部署完成

### 0x023 独立部署free5gc模拟核心网（可选项）

free5gc另外还存在一种直接独立部署在虚拟机环境中的方案，采用此方案，可以跳过上述安装docker的步骤以及容器化部署free5gc的步骤，此文重点关注容器化部署的方案，独立部署方案此处仅做简单介绍：

首先通过以下命令下载并获取源码：

    
    
    cd ~
    git clone --recursive -b v3.0.5 -j `nproc` https://github.com/free5gc/free5gc.git
    

之后编译源码：

    
    
    cd ~/free5gc
    make all
    

源码编译完成后，独立部署的free5gc的基本构建就已经完成了，关于和UERANSIM的联动使用，这一点容器化部署和独立部署的区别只在配置文件的编写，而其余部分使用独立部署和容器化部署并没有太大差异，独立部署方案中，通过以下命令启动模拟核心网：

    
    
    cd ~/free5gc
    ./run.sh
    

启动模拟核心网后，独立部署方案中提供了一些可独立运行的测试脚本以供测试，如测试注册流程：

    
    
    cd ~/free5gc
    ./test.sh TestRegistration
    

如果需要使用独立部署方案结合UERANSIM测试，则首先需要运行独立部署方案的webserver：

    
    
    cd ~/free5gc/webconsole
    go run server.go
    

之后配置UERANSIM的部分两种方案差别不大，差别产生原因在于独立部署方案的UERANSIM需要部署在另一台虚拟机上，这样会使得一些ip地址配置会有差异，另外，独立部署的情况下需要配置以下规则，用以使得free5gc可以访问互联网：

    
    
    sudo sysctl -w net.ipv4.ip_forward=1
    sudo iptables -t nat -A POSTROUTING -o <dn_interface（用以访问互联网的网卡名）> -j MASQUERADE
    sudo iptables -A FORWARD -p tcp -m tcp --tcp-flags SYN,RST SYN -j TCPMSS --set-mss 1400
    sudo systemctl stop ufw
    

至此，free5gc独立部署完成

注：两种部署方案各有优劣，可按实际需要选用不同方案，另外不建议将两种方案安装在同一个虚拟机中，这样可能会产生一些冲突问题

## 0x03 UERANSIM模拟设备安装

### 0x031 源代码下载

    
    
    cd ~
    git clone https://github.com/aligungr/UERANSIM
    

### 0x032 依赖下载

    
    
    sudo apt update
    sudo apt upgrade
    sudo apt install make
    sudo apt install g++
    sudo apt install libsctp-dev
    sudo apt install lksctp-tools
    sudo apt install iproute2
    

### 0x033 编译源代码

    
    
    cd ~/UERANSIM
    make
    

## 0x04 全套环境配置并运行

### 0x041 启动free5gc环境

    
    
    cd ~/free5gc-compose
    docker-compose up -d
    

### 0x042 UERANSIM配置设置

查看并记录虚拟机网卡地址：

    
    
    ifconfig
    

注：上一步启动free5gc后，会在本地虚拟化出一系列的网卡，这一步需要关注的是原先虚拟机自带的网卡，通常这类网卡的ip地址均处于192.168.*.*网段，网卡名类似ens33，eth0之类，可以以此特征区分出来

![4.2-1ifconfig打印出的部分网卡信息.PNG](https://image.3001.net/images/20210402/1617344828_6066b93c70149bbc2e290.png!small)

接下来需要查看并记录amf网元的ip地址：

    
    
    docker inspect amf
    

找到上面记录有"IPAddress": 的一行，后面记录的即是amf的ip地址：

![4.2-2
amf的ip地址.PNG](https://image.3001.net/images/20210402/1617344841_6066b949da0ad5648cbbf.png!small)

记录下这两个ip地址后，就可以完成UERANSIM中gnb的配置了，通过修改free5gc-gnb.yaml配置文件完成这一步操作：

    
    
    cd ~/UERANSIM/config/
    vim free5gc-gnb.yaml
    

需要修改其中的 **ngapIp** 、 **gtpIp** 为 **本机ip**

修改其中的 **amfconfig** 一项下的 **address** 为 **amf的ip**

 **！每次重启机器后，amf地址可能改变，注意更改**

至此，UERANSIM的基站配置完成，接下来需要在free5gc中注册UERANSIM的UE部分：

访问地址 http://localhost:5000/可进入到free5gc的webui处，登录：

    
    
    用户名：admin
    密码：free5gc
    

之后通过free5gc的webui新增一个ue的注册信息：

![4.2-3核心网处记录注册ue信息.PNG](https://image.3001.net/images/20210402/1617344859_6066b95b1ed7a6041277e.png!small)

注：此处配置的UE信息原则上需要和~/UERANSIM/config/free5gc-ue.yaml中的信息一致，但由于此处UERANSIM的代码作者已经设置好，所以实际上无需做任何更改

### 0x043 启动UERANSIM模拟设备

    
    
    #启动一个shell，执行启动gnb的流程
    cd ~/UERANSIM/build
    #通过nr-gnb程序，指定使用的gnb配置文件，启动模拟基站
    ./nr-gnb -c ../config/free5gc-gnb.yaml
    
    #另起一个shell，执行启动UE的流程
    cd ~/UERANSIM/build
    #通过nr-ue程序，指定使用的ue配置文件，启动模拟用户设备
    sudo ./nr-ue -c ../config/free5gc-ue.yaml
    #此处因为需要虚拟出一张ue的网卡，所以需要root权限执行
    

启动完成后，执行`ifconfig`可以看到多了一张名为 **uesimtun0** 的网卡；另外，在 **free5gc** 的 **webui**
处，查看 **REALTIME STATUS** 可以看到有一个UE处于连接状态，此时即证明UERANSIM的环境启动成功：

![4.3-1UERANSIM启动成功.PNG](https://image.3001.net/images/20210402/1617344870_6066b966d476675b4d86a.png!small)

注：启动的 **两个shell不可关闭** ，可以后台执行，但建议前台执行方便实时查看状态信息

## 0x05 模拟5g网络基本使用演示

### 0x051 free5gc模拟核心网基本信息查看

上述环境搭建完成，并且启动free5gc容器后，我们可以通过以下命令查看free5gc单个容器的一些状态信息：

    
    
    docker inspect <容器名(如amf)>
    

查询效果如下：

![5.1-1docker
inspect查询效果.PNG](https://image.3001.net/images/20210402/1617344881_6066b9713c8871cc050d2.png!small)

可以通过下面一条命令，查询出所有容器及其对应的ip地址：

    
    
    docker inspect -f '{{.Name}} - {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(docker ps -aq)
    

查询效果如下：

![5.1-2查询所有ip.PNG](https://image.3001.net/images/20210402/1617344892_6066b97ce2fbbac7030c2.png!small)

通过下面一条命令，可以查询出所有容器及其对应的mac地址：

    
    
    docker inspect -f '{{.Name}} - {{range .NetworkSettings.Networks}}{{.MacAddress}}{{end}}' $(docker ps -aq)
    

查询效果如下：

![5.1-3查询所有mac地址.PNG](https://image.3001.net/images/20210402/1617344906_6066b98a861530e230101.png!small)

如果我们期望进入到各个容器的交互界面，则可以通过以下命令实现：

    
    
    docker exec -it  <容器ID或容器名(如amf)> sh
    

运行效果如下：

![5.1-4进入容器环境.PNG](https://image.3001.net/images/20210402/1617344913_6066b991f3428b7e5d405.png!small)

### 0x052 free5gc模拟核心网基本网络结构分析

free5gc模拟环境搭建完成后，其会虚拟出一个网桥，以及数个和网元对应的虚拟端口，网元通过这些端口和网桥、gnb连接，可以安装 **bridge-utils** 工具，以使用`brctl`命令查看相关信息：

    
    
    brctl show
    

此命令可用于查看当前网桥信息及对应端口号，可以看到，之前ifconfig查询出来的虚拟网卡，实际上都是网桥的虚拟端口：

![5.2-1brctl
show.PNG](https://image.3001.net/images/20210402/1617344924_6066b99cd17821b46ce36.png!small)

通过以下命令，可以看到网桥上连接设备的mac地址信息：

    
    
    brctl showmacs <网桥名>
    

查询结果如下，其中排在前面的几个mac地址实际上是网元的mac地址，下面的则是虚拟端口的mac地址：

![5.2-2组网简单示意图.PNG](https://image.3001.net/images/20210402/1617344933_6066b9a53aa2cd90f8a81.png!small)

在此基础上经过一定分析后，可画出当前free5gc+ueransim模拟5g网络的组网图大致如下：

![5.2-3free5GC组网示意图.png](https://image.3001.net/images/20210402/1617344940_6066b9acf021f7c0f7dec.png!small)

### 0x053 UERANSIM模拟gnb建立

通过以下命令即可建立起虚拟的gnb，并且可以在前台看到相关的建立信息：

    
    
    cd ~/UERANSIM/build
    ./nr-gnb -c ../config/free5gc-gnb.yaml
    

查看效果如下，同时我们可以看到ue接入（图中黄方框内部分）时，gnb处打印出了相关信息：

![5.3-1基站建立.PNG](https://image.3001.net/images/20210402/1617344951_6066b9b7bed84dde5fb76.png!small)

### 0x054 UERANSIM模拟ue建立与注册、去注册

通过以下命令即可建立出虚拟的ue设备，同时该命令还会将ue设备在核心网处注册：

    
    
    cd ~/UERANSIM/build
    sudo ./nr-ue -c ../config/free5gc-ue.yaml
    

运行后，可以看到ue成功完成注册，而且虚拟化出了一张属于ue的虚拟网卡，也因此，此命令必须用root权限执行：

![5.4-1UE建立与注册.PNG](https://image.3001.net/images/20210402/1617344966_6066b9c64575ef0445482.png!small)

根据上面的分析，我们可以在 **网桥**
处抓到尽可能完整的数据包，在ue注册前启动`wireshark`抓包，可以抓取到ue注册时的交互数据包（通过ngap规则过滤）：

![5.4-2在RAN的NG口抓取到UE接入流程如下：.PNG](https://image.3001.net/images/20210402/1617344974_6066b9ce77b17562dd943.png!small)

此后，我们测试去注册的流程，通过以下命令，可以进入到ue的命令行交互界面：

    
    
    cd ~/UERANSIM/build
    #这一步可以用于查询当前正在运行的gnb和ue的名称
    ./nr-cli -d
    #这一步指定ue名称，即可进入ue的命令行交互界面，同理，也可以指定gnb名称进入gnb的交互界面
    ./nr-cli imsi-208930000000003
    

进入交互界面后，可以通过以下命令去注册：

    
    
    #此步用于查询可用命令
    commands
    #此步可以查看去注册相关命令选项
    deregister
    #此步以正常情况去注册
    deregister normal
    

执行效果如下：

![5.4-3UE去注册演示1.PNG](https://image.3001.net/images/20210402/1617344986_6066b9da993a8d7d3d516.png!small)

此时，wireshake抓包处可以捕获到去注册相关的部分数据包（通过ngap规则过滤）：

![5.4-4UE去注册演示2.PNG](https://image.3001.net/images/20210402/1617344996_6066b9e4313b1516b2d8d.png!small)

至此，我们完成了5g网络中简单的UE注册和去注册的流程测试，并抓取到了部分交互数据包进行分析。

### 0x055 free5gc实际数据业务模拟

如果需要实现实际数据业务，则首先需要配置出核心网的Internet接口，通过虚拟机软件，在物理机上虚拟化出一张虚拟网卡（此处为Vnet3），用作Internet的接口：

![5.5-1物理机上新建一张虚拟网卡.PNG](https://image.3001.net/images/20210402/1617345008_6066b9f054cc4ba5f70be.png!small)

此网卡的IP地址配置为和核心网一致网段，并且在虚拟机环境中，再虚拟化一张网卡（此处为ens34），与上面的网卡作桥接：

![5.5-2虚拟机处虚拟化一张网卡与之桥接.PNG](https://image.3001.net/images/20210402/1617345019_6066b9fb2df30b80324ab.png!small)

之后需要在物理机中配置UE所在网段的路由，图中10.100.200.5网段为upf1（对应UPF
anchor-1）的地址，该值视实际中数据包的出口upf确定：

![5.5-3物理机配置路由.PNG](https://image.3001.net/images/20210402/1617345040_6066ba109c82edbbca682.png!small)

此外，还需要在虚拟机中，将虚拟机中新虚拟化出的网卡与网桥进行桥接：

    
    
    #此前需要安装bridge-utils工具
    sudo brctl addif <网桥名称，如br-1ddc4e374522> <上步中虚拟化出的网卡名，如ens34>
    #通过以下命令查看是否添加成功
    brctl show
    

上述配置完成后，在虚拟机中指定UE网卡向外发送ping包，即可看到ping包正常收发：

![5.5-4测试业务数据.PNG](https://image.3001.net/images/20210402/1617345050_6066ba1a76025a7d40c08.png!small)

网桥上抓包查看ping包情况，可以看到数据包确实是经过核心网后再发送的：

![5.5-5测试成功.PNG](https://image.3001.net/images/20210402/1617345567_6066bc1f14c2cfcc6f6e3.png!small)

仔细分析这部分ping数据包，可以发现，原始载荷在网元upfb（对应UPF branch）处封装后，由某种路由规则发送给了upf1（对应UPF
anchor-1），之后再从upf1处发送到互联网；互联网处的回包经过upf1到upfb封装后，再回到ue侧，数据载荷成功通过核心网。

注：上处提到的某种路由规则在~/free5gc-compose/config/uerouting.yaml中有所体现

## 0x06 总结与后记

全文介绍了基于free5gc+ueransim的模拟5G网络环境搭建，实现5G网络的简单研究：实现模拟ue注册、去注册、模拟数据业务。

实际中的5G网络情况自然是要远比上文所述的复杂的，但是对于5G本身而言，这样一套模拟系统足以模拟研究绝大部分情况；这套系统针对于5G协议实现了5G核心网的部分网元功能，所以可以用以研究5G协议本身可能存在的一些问题。

最后，本文所研究的5G模拟网络搭建及实现，实际上只是整一个5G模拟网络的一小部分，整个5G模拟网络的功能远不止于此，仍然有着更多的功能等待着各位研究者深入探索发现。

 **参考文献：**

> free5gc官方网站的独立部署教程：
>
> https://www.free5gc.org/installations/stage-3-sim-install-tw/
>
> UERANSIM官方github文档：
>
> https://github.com/aligungr/UERANSIM/wiki/Configuration
>
> free5gc主干项目github地址
>
> https://github.com/free5gc/free5gc
>
> free5gc容器化部署项目github地址：
>
> https://github.com/free5gc/free5gc-compose
>
> free5gc官方论坛：
>
> https://forum.free5gc.org/search?q=free5gc-compose

