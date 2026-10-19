![](https://image.3001.net/images/20210309/1615304055_604795777bda0a1b44424.jpg!small)

## Gatekeeper是什么？

Gatekeeper是目前第一个开源的DoS拒绝服务攻击防护系统。该系统被设计成可以扩展到任何峰值的带宽，因此它可以抵御目前的DoS拒绝服务攻击攻击。尽管Gatekeeper的体系结构在地理上是分布式的，但描述所有传入流量的网络策略必须是集中式的。这种集中化策略使网络运营商能够利用在很高延迟下不可行的分布式算法（例如分布式数据库），并同时抵御DoS拒绝服务攻击。

Gatekeeper是预期用户是机构、服务和内容提供商、企业网络等的网络运营商，因此暂不打算由个人互联网用户使用。

## 工具安装与配置

### 配置Hugepages

DPDK需要使用到Hugepages，关于如何挂载Hugepages，可以参考这篇【
_文档_】。在很多系统上，我们可以按照下列方式快速有效地配置Hugepages：

    
    
    $ echo 256 | sudo tee /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages

### 选项1：获取工具包

Gatekeeper的Debian包可以点击该项目的【[
_Releases_](https://github.com/AltraMayor/gatekeeper/releases)】页面获取。

 **安装**

下载好安装包之后，我们可以通过下列命令来完成工具的安装：

    
    
    $ tar -zxvf gatekeeper-ubuntu-18.04-packages.tar.gz
    
    $ cd gatekeeper-ubuntu-18.04-packages
    
    $ sudo dpkg -i libgkrte-*.deb \
    
        libgkdpdk-dev_*_amd64.deb \
    
        gatekeeper-dpdk_*_amd64.deb \
    
        gatekeeper-dpdk-dev_*_amd64.deb \
    
        gatekeeper-dpdk-igb-uio-dkms_*_amd64.deb \
    
        gatekeeper-dpdk-rte-kni-dkms_*_amd64.deb \
    
        gatekeeper-bird_*_amd64.deb \
    
    gatekeeper_*_amd64.deb

gatekeeper-dpdk-dev包是DKMS包所需的依赖包，它负责在包安装和内核更新的过程中构建对应的内核模块。

 **配置网络适配器**

编辑/etc/gatekeeper/envvars文件，然后输入需要跟DPDK绑定的网络适配器名称。比如说：

    
    
    GATEKEEPER_INTERFACES="eth0 eth1"

或者，我们还可以指定接口的PCI地址：

    
    
    GATEKEEPER_INTERFACES="0000:00:07.0 0000:00:08.0"

在相同文件中，我们可以在DPDK_ARGS变量中指定“[
_环境抽象层选项_](https://doc.dpdk.org/guides/linux_gsg/linux_eal_parameters.html)”，或在GATEKEEPER_ARGS中指定关于
_Gatekeeper的特定选项_。

 **如何运行**

直接执行下列命令即可运行Gatekeeper，并且确保设备重启之后将会自动运行：

    
    
    $ sudo systemctl start gatekeeper
    
    $ sudo systemctl enable gatekeeper

### 选项2：源码构建

 **安装依赖**

首先，我们需要安装下列软件依赖：

    
    
    $ sudo apt-get update
    
    $ sudo apt-get -y -q install git clang devscripts doxygen hugepages \
    
    build-essential linux-headers-`uname -r` libmnl0 libmnl-dev \
    
    libkmod2 libkmod-dev libnuma-dev libelf1 libelf-dev libc6-dev-i386 \
    
    autoconf flex bison libncurses5-dev libreadline-dev

如需使用DPDK，确保已经安装好了所有的 _环境依赖_。

 **克隆代码库**

克隆Gatekeeper代码库，其中包括涵盖了Gatekeeper依赖的子模块：

    
    
    $ git clone --recursive http://github.com/AltraMayor/gatekeeper.git

如果没有使用--recursive克隆选项，你则需要在gatekeeper目录下获取包含了依赖的子模块：

    
    
    $ git submodule init
    
    $ git submodule update

 **编译**

切换到gatekeeper目录下，然后运行安装脚本：

    
    
    $ . setup.sh

运行好安装脚本之后，你还需要在你的shell配置文件中存储环境变量。比如说，在Bash中，你需要：

    
    
    $ echo "export RTE_SDK=${RTE_SDK}" >> ${HOME}/.profile
    
    $ echo "export RTE_TARGET=${RTE_TARGET}" >> ${HOME}/.profile

当DPDK编译完成并且配置好环境变量后，就可以对gatekeeper进行编译了：

    
    
    $ make

 **配置网络适配器**

在使用Gatekeeper之前，需要给DPDK绑定网络适配器。这里，我们可以使用dependencies/dpdk/usertools/dpdk-devbind.py脚本：

    
    
    $ sudo dependencies/dpdk/usertools/dpdk-devbind.py --bind=uio_pci_generic enp131s0f0

 **如何运行**

正确配置好环境变量并等待Gatekeeper编译完成之后，我们就可以通过下列命令运行该工具了：

    
    
    $ sudo build/gatekeeper [EAL OPTIONS] -- [GATEKEEPER OPTIONS]

## 项目地址

Gatekeeper：【[ _GitHub传送门_](https://github.com/AltraMayor/gatekeeper)】

