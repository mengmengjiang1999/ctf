![kali-digital-ocean.png](https://image.3001.net/images/20190723/1563838847_5d36497f0f421.png!small)

**[DigitalOcean](https://www.digitalocean.com/)是一家类似于AWS，Microsoft
Azure，Google Cloud
Platform等的云提供商。他们提供不同的Linux发行版实例，这些实例被称之为“droplets”。与AWS类似，DigitalOcean在世界各地都有数据中心，甚至在有的国家拥有多个数据中心。**

然而在不久前，DigitalOcean添加了一项非常有特色的功能，即对[自定义镜像](https://blog.digitalocean.com/custom-images/)的支持允许用户导入虚拟机磁盘并将其作为“droplets”来使用。这意味着我们可以在他们的云中用官方Kali镜像构建我们自己的系统。

虽然，可以加载[官方的kali-linux虚拟镜像](https://www.offensive-security.com/kali-linux-vm-vmware-virtualbox-image-download/)，但它的效率并不是很高。因此，我们将构建一个轻量级的Kali
installation，并将其最小化以使其正常工作。

## 生成 ISO

默认情况下，Kali Linux
ISO已为我们提供了一个GUI的安装界面，虽然它非常的易于使用，但我们必须尽可能的减少上传到DigitalOcean的数据量，至于原因我们稍后讨论。在无头系统（headless
system）上运行GUI同样也非常的浪费资源，所以我们需要卸载或禁用它，我们只会生[成一个没有安装GUI或任何其他工具的自定义Kali
ISO](https://docs.kali.org/kali-dojo/02-mastering-live-build)。构建ISO将需要大约5
GB的硬盘空间，因此请确保你有足够的空间。

首先，我们要确保当前系统为最新版本：

    
    
    apt update
    apt -y full-upgrade

如果你安装了新内核，请在执行下一步操作之前重启系统，然后再开始构建。

    
    
    apt -y install git live-build cdebootstrap devscripts
    git clone https://gitlab.com/kalilinux/build-scripts/live-build-config.git
    cd live-build-config
    ./build.sh --variant minimal --verbose

构建ISO可能需要一段时间，因为它需要下载大量的软件包并进行组装（assemble）。在此期间，你可以尽情的享受一杯美味的咖啡或茶。

verbose选项将在屏幕上显示构建日志。但可以将其删除，你可以在build.log文件中执行以下操作：

    
    
    tail -f build.log

一旦我们的提示返回到启动build.sh的终端上，ISO就准备好了，你可以在images/目录中找到它。

## 创建虚拟机

现在我们可以开始构建我们的虚拟机了。创建一个新的虚拟机，将操作系统设置为最新的Debian 64位并分配其20
GB的硬盘空间（详细的设置信息，可在[Kali Trainingde](https://kali.training/topic/booting-kali-in-live-mode/)的站点上找到）。将虚拟磁盘存储为动态分配的单个文件，这一点非常重要。剩下的像CPU和RAM的数量这些你可以不用管它，因为只有磁盘文件才会上传到DigitalOcean。

磁盘大小也很重要，因为费用是基于自定义镜像的磁盘大小来计算的。它还将影响我们可以创建的实例的选择。假设创建的硬盘为40
GB，那么将无法在每月5美元的级别创建实例，因为它的最大硬盘大小为25
GB。在这种情况下，对于具有50GB磁盘的实例，我们将被迫使用10美元每月的选项。不过不用担心，即使磁盘是20 GB，它也会根据所选的droplet
plan进行扩展。

在安装过程中，选择手动分区并按如下所示进行设置，所有文件都在一个分区中，没有swap文件。

![1.png](https://image.3001.net/images/20190723/1563838905_5d3649b9cee86.png!small)

## 更新系统

安装完成并重启后，我们在控制台登录并更新系统：

    
    
    apt update
    apt -y full-upgrade

有时你可能会在安装过程中忘记添加网络镜像。如果出现这种情况，你只需按照[Kali
Docs站点](https://docs.kali.org/general-use/kali-linux-sources-list-repositories)上的说明进行修复，然后再次运行这两个命令即可。

## 安装所需软件包

为了让DigitalOcean为我们配置系统，我们需要安装cloud-init软件包：

    
    
    apt -y install cloud-init
    echo 'datasource_list: [ ConfigDrive, DigitalOcean, NoCloud, None ]' > /etc/cloud/cloud.cfg.d/99_digitalocean.cfg
    systemctl enable cloud-init

## 更新 GRUB

引导时，磁盘已连接并映射为sda1。然而，这里droplets却显示为vda1。要解决这个问题，我们需要在/boot/grub/grub.cfg中将sda1的所有实例更改为vda1：

    
    
    sed -i 's/sda1/vda1/g' /boot/grub/grub.cfg

更新配置文件后，我们可以运行update-grub来更新系统：

    
    
    update-grub
    

## 准备 SSH

由于我们需要使用SSH连接到DigitalOcean上的系统，因此还需要安装（并启用）openssh-server软件包：

    
    
    apt -y install openssh-server
    systemctl enable ssh.service

创建标准Droplet时，你可以选择是否使用SSH密钥。但是，使用自定义镜像时，将强制使用SSH密钥。出于这个原因，DigitalOcean要求我们删除root密码：

    
    
    passwd -d root

我们还需要创建一个/root/.ssh文件夹：

    
    
    mkdir /root/.ssh

## Cleanup

在完成虚拟机的安装之前，我们运行一些命令将一些多余的东西清理掉：

    
    
    apt autoremove
    apt autoclean
    rm -rf /var/log/*
    history -c

此时，我们的虚拟机已准备就绪，我们运行poweroff来关闭系统。

    
    
    poweroff

## 上传

在虚拟机文件夹中，找到.vmdk文件，然后使用bzip2，gzip或zip压缩它以准备上传到DigitalOcean。

    
    
    bzip2 kali.vmdk

登录你的DigitalOcean帐户。在左侧的“Manage”部分中，单击“Images”，然后选择“Custom Images”选项。

![2.png](https://image.3001.net/images/20190723/1563838935_5d3649d7b9610.png!small)

我们在此处上传已压缩的磁盘映像。我们将其命名为Kali，标记为Debian，并选择要将其上传到的区域和数据中心。注意，一旦上传到某个位置，就只能在该位置启动droplets，这是自定义镜像当前的一个限制。另一个需要提醒大家的是上传的镜像会消耗你的磁盘空间，而DigitalOcean将根据磁盘使用情况计费。

![3.png](https://image.3001.net/images/20190723/1563838955_5d3649ebd9761.png!small)

## 启动 Droplet

完成后，“Uploaded”列将显示上传的时间。现在，我们将单击image的“More”选项并选择“Start a droplet”。

![4.png](https://image.3001.net/images/20190723/1563838975_5d3649ffcf1d8.png!small)

你将进入Droplet的设置，你可以在其中选择droplet
plan，SSH密钥和项目来启动它。由于这是一个自定义映像，因此需要使用SSH密钥。你可以通过单击“New SSH
key”来选择现有密钥或上传新密钥，这将打开以下界面，你可以在其中粘贴公钥并为其命名：

![5.png](https://image.3001.net/images/20190723/1563838988_5d364a0c14fc7.png!small)

完成后，单击“Create”，如下所示。然后，它将返回仪表板（Manage >
Droplets），其中列出了当前所有的droplet。由于我们使用的是SSH密钥，因此DigitalOcean不会发送包含Droplet凭据的电子邮件。

![6.png](https://image.3001.net/images/20190723/1563839000_5d364a18b570a.png!small)

只需几秒钟在显示IP后，我们的droplet将准备就绪。为了连接它，我们需要使用我们创建的私有SSH密钥（在本例中为MY_KEY）：

    
    
    user@computer:~$ ssh -i MY_KEY root@192.168.1.1
    The authenticity of host '192.168.1.1 (192.168.1.1)' can't be established.
    ECDSA key fingerprint is SHA256:d83fcd43d25e2a7edd291666160b47360cc85870ded.
    Are you sure you want to continue connecting (yes/no)? yes
    Warning: Permanently added 'IP' (ECDSA) to the list of known hosts.
    Linux kali-s-1vcpu-1gb-nyc3-01 4.19.0-kali5-amd64 #1 SMP Debian 4.19.37-2kali1 (2019-05-15) x86_64
    The programs included with the Kali GNU/Linux system are free software;
    the exact distribution terms for each program are described in the
    individual files in /usr/share/doc/*/copyright.
    Kali GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
    permitted by applicable law.

现在，我们已经有了一个轻量级的最小化的Kali Linux installation，我们可以根据需要对其进行部署和定制。

    
    
    root@kali-s-1vcpu-1gb-nyc3-01:~# lsb_release -a
    No LSB modules are available.
    Distributor ID: Kali
    Description: Kali GNU/Linux Rolling
    Release: 2019.2
    Codename: n/a
    
    root@kali-s-1vcpu-1gb-nyc3-01:~# uname -a
    Linux kali-s-1vcpu-1gb-nyc3-01 4.19.0-kali5-amd64 #1 SMP Debian 4.19.37-2kali1 (2019-05-15) x86_64 GNU/Linux
    
    root@kali-s-1vcpu-1gb-lon1-01:~# free -h
    total used free shared buff/cache available
    Mem: 987Mi 51Mi 527Mi 1.0Mi 407Mi 790Mi
    Swap: 0B 0B 0B

## 相关文章

> [我的自定义Kali Linux发行版](https://www.kali.org/tutorials/my-custom-kali-linux-> distribution/)
>
> [在基于Debian的系统使用Live-Build构建Kali](https://www.kali.org/tutorials/build-kali-> with-live-build-on-debian-based-systems/)
>
> [Kali Linux Amazon EC2 AMI](https://www.kali.org/news/kali-linux-amazon-> ec2-ami/)

 ***参考来源：[kali](https://www.kali.org/news/kali-linux-in-the-digitalocean-cloud/)，FB小编secist编译，转载请注明来自FreeBuf.COM**

