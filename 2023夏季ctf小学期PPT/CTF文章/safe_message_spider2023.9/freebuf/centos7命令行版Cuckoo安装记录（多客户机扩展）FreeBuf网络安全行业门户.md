## 1.1 安装基本依赖

    
    
    yum update
    yum -y install epel-release
    yum install python python-pip python-dev libffi-dev libssl-dev -y
    yum install python-virtualenv python-setuptools -y 
    yum install libjpeg-dev zlib1g-dev swig libjpeg-turbo-devel -y
    yum install gcc-c++* -y
    yum install mongodb ##如果要用自带的基于Django的Web管理系统，需要安装 MongoDB（目前不用Web界面）
    
    pip install --upgrade pip==20.3.4
    pip install openpyxl
    pip install pycrypto
    pip install ujson 
    pip install distorm3
    pip install pytz
    pip install kafka-python
    

## 1.2 tcpdump

    
    
    yum install tcpdump apparmor-util
    sudo setcap cap_net_raw,cap_net_admin=eip /usr/sbin/tcpdump
    

## 1.3 volatility

    
    
    yum install git
    git clone https://github.com/volatilityfoundation/volatility.git
    cd volatility/
    python setup.py build
    python setup.py install
    

## 1.4 ssdeep

    
    
    wget http://sourceforge.net/projects/ssdeep/files/ssdeep-2.13/ssdeep-2.13.tar.gz/download -O ssdeep-2.13.tar.gz
    tar -zxf ssdeep-2.13.tar.gz
    cd ssdeep-2.13
    ./configure
    make
    sudo make install
    

## 1.5 cuckoo

    
    
    pip install -U pip setuptools
    pip install -U cuckoo
    

## 1.6 常见问题（版本问题以文档最后标注版本为准）

### 问题0：报错：找不到python-pip包

 **解决步骤** ：

  1. 首先检查linux有没有安装python-pip包，执行`yum -y install python-pip`

![img](https://image.3001.net/images/20220505/1651737315_627382e3b392f8740189c.png!small)

  1. 没有python-pip包，执行命令`yum -y install epel-release`

  2. 上条指令执行成功之后，再次执行`yum -y install python-pip`

  3. 对安装好的pip进行升级`pip install --upgrade pip==20.3.4`（为了避免后面安装出错，建议升级到指定版本20.3.4）

  4. 如果出现如下报错，需要进行pip换源![img](https://image.3001.net/images/20220505/1651737316_627382e465560e4b75379.png!small)

  5. 创建文件

    
    
    mkdir /root/.pip
    cd /root/.pip
    touch pip.conf
    

### 问题1：显示pyopenssl版本太低

![img](https://image.3001.net/images/20220505/1651737317_627382e5131202fbdac5b.png!small)

### 问题2：升级requests

![img](https://image.3001.net/images/20220505/1651737317_627382e5c8bea24a7709e.png!small)

执行`pip2.7 install --ignore-installed requests==2.13.0`

### 问题3：显示six 版本太低

![img](https://image.3001.net/images/20220505/1651737318_627382e654668766b5048.png!small)

执行`pip install six --upgrade --ignore-installed six`

### 问题4：卸载不了chardet

![img](https://image.3001.net/images/20220505/1651737320_627382e814a20bc290849.png!small)

到 https://pypi.org/project/chardet/#files 下载一个chardet3.0.4的whl包

执行`pip install chardet-3.0.4-py2.py3-none-any.whl --user`，添加--user选项赋予权限：

![img](https://image.3001.net/images/20220505/1651737320_627382e8a2c5d6c7df0da.png!small)

### 问题5：卸载不了ipaddress

![img](https://image.3001.net/images/20220505/1651737321_627382e936c5e4678b542.png!small)

    
    
    sudo pip install --ignore-installed ipaddress==1.0.23
    

### 问题6：安装pillow失败

![img](https://image.3001.net/images/20220505/1651737321_627382e9ba37350f4553f.png!small)

    
    
    yum -y install python-devel zlib-devel （~）libjpeg-turbo-devel
    

### 问题7：pyrsistent 版本不匹配

![img](https://image.3001.net/images/20220505/1651737322_627382ea46d58b19215da.png!small)

执行`pip install pyrsistent==0.16.1`

### 验证测试

执行cuckoo，出现以下界面表示初步安装成功

![img](https://image.3001.net/images/20220505/1651737322_627382eaba437fae81a5a.png!small)

## 1.7.a 搭建kvm虚拟机

### （1）关闭防火墙和selinux

    
    
    systemctl stop firewalld
    systemctl disable firewalld
    setenforce 0
    sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config
    

### （2）查看硬件是否支持虚拟化

    
    
    egrep '(vmx|svm)' /proc/cpuinfo
    

要有 vmx 或 svm 的标识才行，vmx标识intel，svm代表AMD

![img](https://image.3001.net/images/20220505/1651737323_627382eb4af6d13064b32.png!small)

如果没有，点击vm虚拟机设置-处理器-开启虚拟化引擎（关闭虚拟机才能设置）

![img](https://image.3001.net/images/20220505/1651737324_627382ec07a2cdff7d5fe.png!small)

如果失败，可能是因为冲突，需要去控制面板卸载虚拟机平台

![img](https://image.3001.net/images/20220505/1651737324_627382ec94c7dc9787e2a.png!small)

### （3）安装kvm

由于Linux内核已经将kvm收录了，在安装系统时已经加入了kvm，我们只需要在命令行模式下启用kvm即可：

    
    
    [root@ c7-41 ~] modprobe kvm
    [root@ c7-41 ~] lsmod |grep kvm
    kvm_intel             188644  0 
    kvm                   621480  1 kvm_intel
    irqbypass              13503  1 kvm
    

### （4）安装kvm所需组件

    
    
    [root@ c7-41 ~] yum -y install virt-* libvirt bridge-utils qemu-img qemu-kvm
    # 启动libvirtd服务
    
    [root@ c7-41 ~] systemctl start libvirtd
    # 查看是否安装正确
    [root@ c7-41 ~] ifconfig
    

![img](https://image.3001.net/images/20220505/1651737325_627382ed92bfbdd0dcda3.png!small)

### （5）创建客户机

  1. 在 /opt/ 路径下创建 kvm_data 文件夹用来保存数据

  2. 上传iso镜像文件到 /tmp/ 文件夹下（文件夹任意）

  3. 执行指令（以下给出基本参数注释，如有需要可自行增加）

    
    
    # --name 客户机名字(不能重复)
    # --cdrom 系统镜像路径
    # --disk path 数据保存路径(需要自己创建),指定大小(单位为G)
    # --graphics 图形界面指定vnc，端口号从5901开始递增
    virt-install --name=winxp --ram=1024 --cdrom=/tmp/winxpsp3.iso --disk path=/opt/kvm_data/winxp.raw,size=10 --graphics=vnc,port=5901,listen=0.0.0.0 --noautoconsole
    

**报错** ：

![img](https://image.3001.net/images/20220505/1651737326_627382ee9d80306152b80.png!small)

 **解决办法** ：重装urllib3库

    
    
    pip uninstall urllib3
    pip install urllib3==1.26.5
    

**报错** ：

![img](https://image.3001.net/images/20220505/1651737327_627382ef1c0419880c42b.png!small)

    
    
    pip install requests --upgrade
    

### （6）virsh工具常用指令

virsh help| 查看帮助  
---|---  
virsh help 命令| 查看具体命令的用法  
virsh list| 列出处于运行状态的虚拟机  
virsh list --all| 列出所有虚拟机  
virsh console winxp| 进入名为winxp的虚拟机  
快捷键 ctrl + ]| 退出虚拟机  
virsh start winxp| 开启虚拟机  
virsh shutdown winxp| 关闭虚拟机  
virsh destroy winxp| 销毁虚拟机  
virsh suspend winxp| 挂起虚拟机  
virsh autostart winxp| 让虚拟机随主机自动开启  
virsh autostart --disable winxp| 取消虚拟机自动开启  
virsh snapshot-create winxp| 虚拟机创建快照  
virsh snapshot-create-as winxp snapshot1| 创建名为snapshot1的快照  
virsh snapshot-list winxp| 查看虚拟机的快照  
virsh snapshot-delete winxp --snapshotname snapshot1| 删除winxp虚拟机名为snapshot1的快照  
  
#### 删除kvm客户机

  1. 强制停止虚拟机`virsh destroy winxp`可能会失败，不影响后面的步骤

  2. 删除虚拟机（需要先删除快照）`virsh undefine winxp`

  3. 查找与客户机相关的文件并删除

    
    
    # 可能需要用下面指令安装
    yum install mlocate
    # 更新本机文件
    updatedb
    # 查找winxp相关文件
    locate winxp
    

## 1.7.b VNC连接

### （1）安装依赖

    
    
    yum -y install libcanberra-gtk2 qemu-kvm.x84_64 qemu-kvm-tools.x86_64 libvirt.x86_64 libvirt-cim.x86_64 libvirt-client.x86_64 libvirt-java.noarch libvirt-python.x86_64 libiscsi-1.7.0-5.e16.x86_64 dbus-devel virt-clone tunctl virt-manager libvirt libvirt-python python-virtinst
    

### （2）启动libvirt并设置开机启动

    
    
    systemctl enable libvirtd
    systemctl start libvirtd
    

### （3）安装VNC server/VNC客户端

  1. 关闭防火墙和selinux

    
    
    systemctl stop firewalld
    setenforce 0
    

  1. vnc server安装

    
    
    yum -y install tigervnc-server tigervnc vnc vnc-server
    

  1. 在主机下载并安装，官网 https://www.realvnc.com/en/connect/download/viewer/

  2. 启动VNC并设置开机启动

    
    
    systemctl enable vncserver@:1.service
    systemctl start vncserver@:1.service
    

  1. 用客户端进行连接，输入ip和端口即可（注意关闭宿主机防火墙）

## 1.8.a 客户机和宿主机连通

### （1）客户机创建网卡

    
    
    virsh attach-interface winxp0 --type bridge --source virbr0 
    # 保存配置
    virsh dumpxml winxp > winxp.xml
    

查看验证

    
    
    virsh domiflist winxp0
    more /etc/libvirt/qemu/winxp.xml | grep mac
    

### （2）配置客户机IP

![img](https://image.3001.net/images/20220505/1651737327_627382efabc80ad240054.png!small)

## 1.8.b 创建共享文件夹

 **注** ：尽量不要把共享文件夹放在root下，会出现权限问题

### （1）安装依赖

Samba涉及到四个软件包，有些功能您可能用不上，但是安装了也不会有问题。

1）samba：Samba服务器。

2）samba-client：Samba客户端。

3）samba-common：Samba服务器和客户端相关的软件。

4）cifs-utils：通用的Internet文件系统实用程序，支持与Windows、OS X和其他Unix系统进行跨平台文件共享。

    
    
    yum -y install samba samba-client samba-common cifs-utils
    

### （2）修改系统配置

#### ① 关闭SELINUX

打开 /etc/selinux/config 文件，把SELINUX参数的值改为disabled

    
    
    SELINUX =disabled
    

重启linux系统或执行`setenforce 0`使修改马上生效。

#### ② 开通防火墙端口

Samba 涉及到以四个端口：UDP 137、UDP 138、TCP 139、TCP 445。

防火墙开通samba服务，重启防火墙生效

    
    
    firewall-cmd --zone=public --add-service=samba --permanent
    systemctl restart firewalld
    

#### ③ 启用smb服务

启动smb服务并设为开机自启。

    
    
    systemctl start smb 
    systemctl enable smb
    

### （3）配置smb文件系统

#### ① 创建测试目录和文件

    
    
    # 创建/tmp/docs目录,路径可随意指定
    mkdir /tmp/docs
    # 随意创建个测试文件
    ls /usr > /tmp/docs/usr.txt
    # 修改/tmp/docs目录及文件用户和组
    chown -R nobody:nobody /tmp/docs
    

#### ② 配置 /etc/samba/smb.conf 文件

在`[global]`组增加以下行：

    
    
    map to guest = Bad User
    

在文件末尾增加以下行：

    
    
    [docs]
    comment = Fully shared directory
    path = /tmp/docs
    public = yes
    read only = no
    

[docs]为待共享的文件系统起个名称，不要求与目录名相同，在客户机中将看到这个名称

comment参数是说明文字

path是待共享的Linux目录

public指定guest用户可以访问

read only是否为只读，yes或no

#### ③ 重启samba服务，验证结果

每次修改配置文件后，都要重启smb服务

    
    
    systemctl restart smb
    

在客户机中输入`\\服务器IP`，无需用户名和密码，即可访问共享文件系统

## 1.9 配置客户机

  1. 将python和pil安装包放到共享文件夹下，传给客户机。在客户机系统中安装python和pil（pil需要拷贝到共享文件夹外安装）

  2. 将 /root/.cuckoo/agent/agent.py 文件拷贝到客户机中，修改后缀名`.py`为`.pyw`。双击运行（没有界面，不会有反应）

  3. 客户机拍快照，名为snapshot1（快照名可以自定义，后面的配置会用到）

    
    
    virsh snapshot-create-as winxp0 snapshot0
    # 验证查看
    virsh snapshot-list winxp1
    

## 1.10 新增客户机

### 方式一：克隆客户机

  1. 克隆已有虚拟机（被克隆的客户机必须关闭）

    
    
    virt-clone -o winxp -n xp_clone -f /opt/kvm_data/xp_clone.raw
    

  1. 修改vnc端口（关闭客户机修改）

    
    
    virsh edit xp_clone
    # 修改port和autoport参数，参照下图
    

![img](https://image.3001.net/images/20220505/1651737328_627382f0a4d691fe71cfa.png!small)

### 方式二：新建客户机

命令说明详见部署文档，注意修改客户名称、镜像路径、保存路径及vnc端口

    
    
    virt-install --name=winxp --ram=1024 --cdrom=/tmp/winxpsp3.iso --disk path=/opt/kvm_data/winxp.raw,size=10 --graphics=vnc,port=5901,listen=0.0.0.0 --noautoconsole
    

#### 创建网卡（如果克隆可直接修改IP）

    
    
    virsh attach-interface winxp --type bridge --source virbr0 
    # 保存配置
    virsh dumpxml winxp > winxp.xml 
    # 查看是否保存成功
    more /etc/libvirt/qemu/winxp.xml | grep mac
    

修改客户机IP：从192.168.122.101开始递增，末尾和vnc端口匹配

#### 配置客户机

  1. 访问`\\主机IP`共享文件夹，在客户机系统中安装python和pil（pil需要拷贝到共享文件夹外安装）

  2. 执行agent.pyw，没有界面，不会有反应

  3. 完成后拍快照

    
    
    virsh snapshot-create-as winxp0 snapshot0
    # 验证查看
    virsh snapshot-list winxp1
    

## 1.11 修改配置文件

进入 /root/.cuckoo/conf/ 路径下

### cuckoo.conf

`[cuckoo]`标签下

    
    
    # Enable or disable startup version check. When enabled, Cuckoo will connect
    # to a remote location to verify whether the running version is the latest
    # one available.
    version_check = no
    
    # Cuckoo will stop at startup if the version check reports vulnerabilities in
    # one of Cuckoo's dependencies. This setting ignores the vulnerabilities
    # and starts anyway
    ignore_vulnerabilities = yes
    
    # Specify the name of the machinery module to use, this module will
    # define the interaction between Cuckoo and your virtualization software
    # of choice.
    machinery = kvm
    

`[resultserver]`标签下

    
    
    # The Result Server is used to receive in real time the behavioral logs
    # produced by the analyzer.
    # Specify the IP address of the host. The analysis machines should be able
    # to contact the host through such address, so make sure it's valid.
    # NOTE: if you set resultserver IP to 0.0.0.0 you have to set the option
    # `resultserver_ip` for all your virtual machines in machinery configuration.
    ip = 192.168.122.1
    

### kvm.conf

`[kvm]`标签下

    
    
    machines = winxp
    

`[cuckoo1]`标签下，需要修改的参数如下（包括标签本身也需要修改）

    
    
    [winxp]
    # Specify the label name of the current machine as specified in your
    # libvirt configuration.
    label = winxp
    
    # Specify the IP address of the current virtual machine. Make sure that the
    # IP address is valid and that the host machine is able to reach it. If not,
    # the analysis will fail. You may want to configure your network settings in
    # /etc/libvirt/<hypervisor>/networks/
    ip = 192.168.122.101
    
    # (Optional) Specify the snapshot name to use. If you do not specify a snapshot
    # name, the KVM MachineManager will use the current snapshot.
    # Example (Snapshot1 is the snapshot name):
    snapshot = snapshot1
    

## 12\. 测试启动

执行`cuckoo community`命令，下载社区signature

执行`cuckoo`，出现如下界面表示安装完成

![img](https://image.3001.net/images/20220505/1651737329_627382f12a28f7a7f0b79.png!small)

### 运行验证

执行`cuckoo`启动沙箱，如下图所示加载了两台客户机

![img](https://image.3001.net/images/20220505/1651737329_627382f1ca9bfa3b3d51b.png!small)

再开终端执行`cuckoo process instance1`，`cuckoo process instance2`... 需要多少开多少.

