**Mondoo是一个Cloud-Native安全和漏洞风险管理系统且开箱即用。Mondoo集成了主要的云环境，CI/CD环境和构建工具（如packer）以及资源调配工具[Terraform](https://mondoo.io/docs/integration/terraform)，[Ansible](https://mondoo.io/docs/agent/ansible)和[Chef](https://mondoo.io/docs/agent/chef)等。**

![](https://image.3001.net/images/20190906/1567731975_5d71b107d1a6a.png!small)

Mondoo支持以下操作系统的漏洞扫描：

> Amazon Linux 1 & 2
>
> RedHat 6,7,8
>
> CentOS 6,7
>
> Oracle Linux 6,7,8
>
> Ubuntu 14.04, 16.04, 18.04
>
> Suse 12
>
> openSUSE leap

Mondoo的报告可以直接打印在终端：

![](https://image.3001.net/images/20190906/1567731992_5d71b1181ff2f.png!small)

在你的Mondoo仪表板中：

![](https://image.3001.net/images/20190906/1567732005_5d71b125359af.png!small)

或在你的CI/CD环境中：

![](https://image.3001.net/images/20190906/1567732017_5d71b131db2cc.png!small)

## 快速入门

使用Mondoo的最简单方法是在你的工作站本地安装agent，或使用我们的Docker容器mondoolabs/mondoo。

## 安装

Windows workstation

![](https://image.3001.net/images/20190906/1567732074_5d71b16acc651.png!small)

  

    
    
    iex (new-object net.webclient).downloadstring('https://mondoo.io/download.ps1')

有关详细信息，请参阅在Windows工作站安装Mondoo Agent部分。

 **macOS Workstation**

**![6.JPG](https://image.3001.net/images/20190906/1567732131_5d71b1a3b7099.jpg!small)**

    
    
    brew tap mondoolabs/mondoo
    brew install mondoo

有关详细信息，请参阅在MacOS工作站安装Mondoo Agent部分。

 **Linux Workstation**

    
    
    curl -sSL https://mondoo.io/download.sh | bash

 **注意：**
Mondoo支持广泛的[Linux操作系统（../agent）。我们建议你为服务器环境安装软件包，以确保始终检索最近更新。对于工作站，我们还提供了一个与mondoo二进制文件一起发布的脚本。

## 注册

    
    
    mondoo register --token 'ey...FlP'
      ✔  agent //agents.api.mondoo.app/spaces/dazzling-hermann-857694/agents/1NmZG4Mt2fKXRrYGvUPiyLG7JyQ registered successfully

## 扫描你的第一个目标

    
    
    mondoo scan -t ssh://ec2-user@54.205.49.51
    Start vulnerability scan:
      →  verify platform access to ssh://ec2-user@54.205.49.51
      →  gather platform details
      →  detected amzn 2
      →  gather platform packages for vulnerability scan
      →  found 435 packages
      →  analyse packages for vulnerabilities
    Advisory Report:
      ■   SCORE  PACKAGE       INSTALLED               VULNERABLE (<)          **AILABLE               ADVISORY                                 
      ■   7.8    curl          7.61.1-9.amzn2.0.1      7.61.1-11.amzn2.0.2     7.61.1-11.amzn2.0.2     https://mondoo.app/vuln/ALAS2-2019-1233  
      ■   7.8    libcurl       7.61.1-9.amzn2.0.1      7.61.1-11.amzn2.0.2     7.61.1-11.amzn2.0.2     https://mondoo.app/vuln/ALAS2-2019-1233  
      ■   6.9    kernel        4.14.123-111.109.amzn2  4.14.133-113.112.amzn2  4.14.133-113.112.amzn2  https://mondoo.app/vuln/ALAS2-2019-1253  
      ╰─  6.5    kernel        4.14.123-111.109.amzn2  4.14.133-113.105.amzn2  4.14.133-113.112.amzn2  https://mondoo.app/vuln/ALAS2-2019-1232  
      ■   6.9    kernel-tools  4.14.133-113.105.amzn2  4.14.133-113.112.amzn2  4.14.133-113.112.amzn2  https://mondoo.app/vuln/ALAS2-2019-1253  
      →  ■ found 3 advisories: ■ 0 critical, ■ 1 high, ■ 2 medium, ■ 0 low, ■ 0 none, ■ 0 unknown
      →  report is available at https://mondoo.app/v/tender-elbakyan-495615/gallant-kilby-587371/reports/1P4JUZrB1n6rkKU5J5JthPtP42Q

## 尝试使用 Docker

1\. 启动mondoo容器

在容器中启动mondoo非常简单：

    
    
    $ docker run -it --entrypoint /bin/sh mondoolabs/mondoo
    / $ mondoo
    
    _____ ______   ________  ________   ________  ________  ________
    |\   _ \  _   \|\   __  \|\   ___  \|\   ___ \|\   __  \|\   __  \
    \ \  \\\__\ \  \ \  \|\  \ \  \\ \  \ \  \_|\ \ \  \|\  \ \  \|\  \
     \ \  \\|__| \  \ \  \\\  \ \  \\ \  \ \  \ \\ \ \  \\\  \ \  \\\  \
      \ \  \    \ \  \ \  \\\  \ \  \\ \  \ \  \_\\ \ \  \\\  \ \  \\\  \
       \ \__\    \ \__\ \_______\ \__\\ \__\ \_______\ \_______\ \_______\
        \|__|     \|__|\|_______|\|__| \|__|\|_______|\|_______|\|_______|
    
    
    Mondoo scans operating systems for known vulnerabilities
    
    Usage:
      mondoo [command]
    
    Available Commands:
      help        Help about any command
      register    Registers Mondoo agent with Mondoo Cloud
      scan        Scans an asset for known vulnerabilities
      status      Verifies the access to Mondoo Cloud
      unregister  Unregister Mondoo agent from Mondoo Cloud
      version     Displays the Mondoo agent version
    
    Flags:
          --config string   config file (default is $HOME/.mondoo.yaml)
      -h, --help            help for mondoo
    
    Use "mondoo [command] --help" for more information about a command.

2\. 注册代理

    
    
    / $ mondoo register --token 'ey...FlP'
      ✔  agent //agents.api.mondoo.app/spaces/dazzling-hermann-857694/agents/1NmZG4Mt2fKXRrYGvUPiyLG7JyQ registered successfully

3\. 扫描本地容器

    
    
    / $ mondoo scan
    Start vulnerability scan:
      →  verify platform access to local://
      →  gather platform details
      →  detected alpine 3.10.0
      →  gather platform packages for vulnerability scan
      →  found 38 packages
      →  analyse packages for vulnerabilities
    Advisory Report:
      →  ■ found no advisories
      →  report is available at https://mondoo.app/v/tender-elbakyan-495615/dazzling-hermann-857694/reports/1NmZH5j4FEusxhzN6QsPeniuJJB

4\. 从容器内扫描远程容器镜像：

    
    
    / $ mondoo scan -t docker://centos:7
    Start vulnerability scan:
      →  verify platform access to docker://centos:7
      →  gather platform details
      →  detected centos 7.6.1810
      →  gather platform packages for vulnerability scan
      →  found 146 packages
      →  analyse packages for vulnerabilities
    Advisory Report:
      ■        PACKAGE       INSTALLED          VULNERABLE (<)       ADVISORY                                                                                     
      ■   9.8  python        2.7.5-76.el7       0:2.7.5-77.el7_6     https://mondoo.app/advisories/RHSA-2019%3A0710  
      ╰─  9.8  python        2.7.5-76.el7       0:2.7.5-80.el7_6     https://mondoo.app/advisories/RHSA-2019%3A1587  
      ■   9.8  python-libs   2.7.5-76.el7       0:2.7.5-77.el7_6     https://mondoo.app/advisories/RHSA-2019%3A0710  
      ╰─  9.8  python-libs   2.7.5-76.el7       0:2.7.5-80.el7_6     https://mondoo.app/advisories/RHSA-2019%3A1587  
      ■   8.8  libssh2       1.4.3-12.el7       0:1.4.3-12.el7_6.2   https://mondoo.app/advisories/RHSA-2019%3A0679  
      ■   8.6  bind-license  32:9.9.4-73.el7_6  32:9.9.4-74.el7_6.1  https://mondoo.app/advisories/RHSA-2019%3A1294  
      ■   4.7  openssl-libs  1:1.0.2k-16.el7    1:1.0.2k-16.el7_6.1  https://mondoo.app/advisories/RHSA-2019%3A0483  
      →  ■ found 5 advisories: 2 critical, 2 high, 1 medium, 0 low, 0 none, 0 unknown
      →  report is available at https://mondoo.app/v/tender-elbakyan-495615/dazzling-hermann-857694/reports/1NmZUg5URmOErNRqjxmLiOJsip1

## 从你的工作站扫描目标

虽然Mondoo
agent被设计为在你的服务器基础架构上连续运行，但使用CLI进行快速漏洞扫描也很容易。这允许任何人收集特定资产的快速风险评估。通过使用Mondoo的代理，你可以扫描：

> Ssh 目标
>
> Docker images
>
> Running Docker containers
>
> Stopped Docker containers
>
> Local system（代理运行的位置）

以下示例假定你已在工作站上安装了Mondoo。

## SSH 目标

mondoo代理具有完整的ssh支持，并会自动从ssh配置和ssh-agent的凭据中获取配置。因此，你不需要将密码作为明文传递，以避免在shell历史记录中存储凭据。另外，它更方便:-)

    
    
    # scan ssh target with default port 22
    $ mondoo scan -t ssh://ec2-user@52.51.185.215
    
    # scan ssh target on a custom port  
    $ mondoo scan -t ssh://ec2-user@52.51.185.215:2222

![88.JPG](https://image.3001.net/images/20190906/1567732235_5d71b20b0ff7a.jpg!small)

mondoo代理使用~/.ssh/config中的定义。以下定义了ssh的host shorty：

    
    
    Host shorty
      HostName 54.205.49.51
      User ec2-user

你可以使用shorty作为monndoo的主机标识符：

    
    
    # use hosts defined in ~/.ssh/config 
    $ mondoo scan -t ssh://shorty

 **身份验证**

你可以通过-i选项传递未加密的密钥：

    
    
    mondoo scan -t ssh://vagrant@192.168.100.70 -i /path/to/private_key

 **注意：** 我们建议使用ssh-agent作为身份密钥，因为mondoo无法自行解密密钥

 **Agent 验证**

由于mondoo与ssh-agent集成，因此你无需提供身份密钥。这也是加密身份密钥的推荐解决方案：

    
    
    ssh-add /path/to/private_key
    mondoo scan -t ssh://vagrant@192.168.100.70

 **密码验证**

 **注意：** 我们不建议将此方法用于任何生产工作负载，因为它可能会在日志中将密码公开为明文

    
    
    mondoo scan -t ssh://vagrant:vagrant@192.168.100.70

## Docker Images

![99.JPG](https://image.3001.net/images/20190906/1567732271_5d71b22fca159.jpg!small)

Mondoo可以通过其注册表名称直接扫描Docker容器镜像：

    
    
    $ mondoo scan -t docker://ubuntu:latest
    $ mondoo scan -t docker://elastic/elasticsearch:7.2.0
    $ mondoo scan -t docker://gcr.io/google-containers/ubuntu:14.04
    $ mondoo scan -t docker://registry.access.redhat.com/ubi8/ubi

如果安装了Docker代理，你可以按其id扫描镜像：

    
    
    $ mondoo scan -t docker://docker-image-id

## Docker Container

![1010.JPG](https://image.3001.net/images/20190906/1567732319_5d71b25f31d6a.jpg!small)

你可以通过id轻松扫描正在运行的容器：

    
    
    $ mondoo scan -t docker://docker-container-id

扫描也可用于已停止的容器。

![1111.JPG](https://image.3001.net/images/20190906/1567732357_5d71b28547849.jpg!small)

 **注意：** 只有安装了Docker引擎才能扫描Docker容器

## 本地系统

基于Linux的系统也可以在本地扫描：

    
    
    $ mondoo scan

## Mondoo Agent

Mondoo
agent是一个小型的跨平台二进制文件，可轻松评估系统漏洞。其主要职责是确定已安装的软件包，并将包括其版本的软件包列表发送到Mondoo的漏洞数据库进行进一步分析。

![12.png](https://image.3001.net/images/20190906/1567732398_5d71b2ae01fb6.png!small)

## 在 Windows 工作站安装 Mondoo Agent  

 **Powershell**

运行此powershell脚本将Mondoo安装到C:\Users\<user>\mondoo中的默认位置。

    
    
    iex (new-object net.webclient).downloadstring('https://mondoo.io/download.ps1')

![13.png](https://image.3001.net/images/20190906/1567732449_5d71b2e18090a.png!small)

安装代理后，你可以注册代理

    
    
    $MONDOO_REGISTRATION_TOKEN="pastetokenhere"
    mondoo register --token $MONDOO_REGISTRATION_TOKEN
      ✔  agent //agents.api.mondoo.app/spaces/peaceful-burnell-555533/agents/1ON7UPoNpkKxkMncKTFUcwZLVrt registered successfully

 **Binary 下载**

Mondoo为Windows分发二进制文件。要安装代理，请下载相应的软件包。Windows系统的存档文件使用.zip。下载完成后提取内容。Mondoo代理是一个名为mondoo的二进制代码。
最后一步是将mondoo二进制文件添加到路径中。你可以通过控制面板配置路径：

> 转到控制面板 - >系统 - >系统设置 - >环境变量
>
> 在系统变量部分向下滚动，找到Path。
>
> 单击编辑并添加新路径，确保以分号分隔路径，即C:\path1;C:\path2
>
> 启动新控制台以使更改生效

 **WSL**

如果你使用的是WSL，则可以使用我们的Linux Bash安装程序：

    
    
    MONDOO_REGISTRATION_TOKEN='ey...ax'
    curl -sSL https://mondoo.io/install.sh | bash

##
**![14.png](https://image.3001.net/images/20190906/1567732466_5d71b2f299cf2.png!small)**

##  **在 macOS 工作站安装 Mondoo Agent**

![15.JPG](https://image.3001.net/images/20190906/1567732523_5d71b32b591a5.jpg!small)

首先，添加mondoo brew tap：

    
    
    brew tap mondoolabs/mondoo

然后，安装mondoo代理：

    
    
    brew install mondoo

向你的mondoo云组织注册代理

    
    
    mondoo register --token 'TOKEN'

##  **在 RedHat & CentOS ****安装 Mondoo Agent**

首先，添加mondoo签名的apt存储库：

    
    
    curl --silent --location https://releases.mondoo.io/rpm/mondoo.repo | tee /etc/yum.repos.d/mondoo.repo

然后，安装mondoo代理：

    
    
    yum install -y mondoo

向你的mondoo云组织注册代理

    
    
    mondoo register --config /etc/opt/mondoo/mondoo.yml --token 'TOKEN'

启动代理：

    
    
    systemctl enable mondoo.timer && systemctl start mondoo.timer
    systemctl daemon-reload

代理状态可以通过以下方式显示：

    
    
    systemctl list-timers
    systemctl status mondoo.timer

 **更新**

mondoo代理可以通过以下方式轻松更新：

    
    
    yum clean expire-cache && yum update mondoo

## 在 Amazon Linux **安装 Mondoo Agent**

首先，添加mondoo签名的apt存储库：

    
    
    curl --silent --location https://releases.mondoo.io/rpm/mondoo.repo | tee /etc/yum.repos.d/mondoo.repo

然后，安装mondoo代理：

    
    
    yum install -y mondoo

向你的mondoo云组织注册代理

    
    
    mondoo register --config /etc/opt/mondoo/mondoo.yml --token 'TOKEN'

启动代理：

    
    
    systemctl enable mondoo.timer && systemctl start mondoo.timer
    systemctl daemon-reload

代理状态可以通过以下方式显示：

    
    
    systemctl list-timers
    systemctl status mondoo.timer

 **更新**

mondoo代理可以通过以下方式轻松更新：

    
    
    yum clean expire-cache && yum update mondoo

## 在 Ubuntu & Debian **安装 Mondoo Agent**

首先，添加mondoo签名的apt存储库：

    
    
    curl -sS https://releases.mondoo.io/debian/pubkey.gpg | apt-key add -    echo "deb https://releases.mondoo.io/debian/ stable main" | tee /etc/apt/sources.list.d/mondoo.list

然后，安装mondoo代理：

    
    
    apt-get update && apt-get install mondoo

向你的mondoo云组织注册代理

    
    
    mondoo register --config /etc/opt/mondoo/mondoo.yml --token 'TOKEN'

启动代理：

    
    
    systemctl enable mondoo.timer && systemctl start mondoo.timer
    systemctl daemon-reload

代理状态可以通过以下方式显示：

    
    
    systemctl list-timers
    systemctl status mondoo.timer

 **更新**

mondoo代理可以通过以下方式轻松更新：

    
    
    apt-get update && apt-get install -y mondoo

## 在 RedHat & CentOS **安装 Mondoo Agent**

首先，添加mondoo签名的apt存储库：

    
    
    curl --silent --location https://releases.mondoo.io/rpm/mondoo.repo | tee /etc/yum.repos.d/mondoo.repo

然后，安装mondoo代理：

    
    
    yum install -y mondoo

向你的mondoo云组织注册代理

    
    
    mondoo register --config /etc/opt/mondoo/mondoo.yml --token 'TOKEN'

启动代理：

    
    
    systemctl enable mondoo.timer && systemctl start mondoo.timer
    systemctl daemon-reload

代理状态可以通过以下方式显示：

    
    
    systemctl list-timers
    systemctl status mondoo.timer

 **更新**

mondoo代理可以通过以下方式轻松更新：

    
    
    yum clean expire-cache && yum update mondoo

## 在 Ubuntu & Debian **安装 Mondoo Agent**

首先，添加mondoo签名的apt存储库：

    
    
    curl -sS https://releases.mondoo.io/debian/pubkey.gpg | apt-key add -    echo "deb https://releases.mondoo.io/debian/ stable main" | tee /etc/apt/sources.list.d/mondoo.list

然后，安装mondoo代理：

    
    
    apt-get update && apt-get install mondoo

向你的mondoo云组织注册代理

    
    
    mondoo register --config /etc/opt/mondoo/mondoo.yml --token 'TOKEN'

启动代理：

    
    
    systemctl enable mondoo.timer && systemctl start mondoo.timer
    systemctl daemon-reload

代理状态可以通过以下方式显示：

    
    
    systemctl list-timers
    systemctl status mondoo.timer

 **更新**

mondoo代理可以通过以下方式轻松更新：

    
    
    apt-get update && apt-get install -y mondoo

## 在 Suse & openSUSE **安装 Mondoo Agent**

首先，添加mondoo签名的apt存储库：

    
    
    curl --silent --location https://releases.mondoo.io/rpm/mondoo.repo | tee /etc/zypp/repos.d/mondoo.repo

然后，安装mondoo代理：

    
    
    zypper -n --gpg-auto-import-keys install mondoo

向你的mondoo云组织注册代理

    
    
    mondoo register --config /etc/opt/mondoo/mondoo.yml --token 'TOKEN'

启动代理：

    
    
    systemctl enable mondoo.timer && systemctl start mondoo.timer
    systemctl daemon-reload

代理状态可以通过以下方式显示：

    
    
    systemctl list-timers
    systemctl status mondoo.timer

 **更新**

mondoo代理可以通过以下方式轻松更新：

    
    
    zypper update mondoo

## 通过 Ansible 安装

我们发布了官方[Mondoo role](https://galaxy.ansible.com/mondoolabs/mondoo)。

 **示例：** 将Ansible Playbook应用于Amazon EC2实例

此playbook演示了如何使用Mondoo role在许多实例上安装代理：

1\. 创建新的主机清单。将你的主机添加到该组。

    
    
    [mondoo-agents]
    54.172.7.243  ansible_user=ec2-user

2\. 创建一个playbook.yml并更改mondoo_registration_token：

    
    
    ---    - hosts: mondoo-agents
      become: yes
      roles:
        - role: mondoolabs.mondoo
          vars:
            mondoo_registration_token: "changeme"

3\. 使用本地hosts文件运行playbook

    
    
    # download mondoo role
    ansible-galaxy install mondoolabs.mondoo
    # apply the playbook
    ansible-playbook -i hosts playbook.yml

4\. 所有实例都[报告了其漏洞状态](https://mondoo.app/)

## 通过 Chef 安装

我们在Chef Supermarket上发布了官方[mondoo
cookbook](https://supermarket.chef.io/cookbooks/mondoo)。你可以在自己的[wrapper
cookbooks](https://blog.chef.io/2017/02/14/writing-wrapper-cookbooks/) 或 [Chef
Roles](https://www.digitalocean.com/community/tutorials/how-to-use-roles-and-environments-in-chef-to-control-server-configurations)中使用此cookbook

应用cookbook，请通过以下方式设置Mondoo注册令牌：

    
    
    default['mondoo']['registration_token'] = "changeme"

 **示例：** 将Cookbook应用于Amazon EC2实例

  1. 在[AWS](https://console.aws.amazon.com/console/home)上启动新的Linux机器
  2. 如我们的[示例](https://github.com/mondoolabs/mondoo/tree/master/examples/chef-aws-ec2)中所述，创建运行wrapper cookbook
  3. 运行chef-run ssh://user@host ./run
  4. 所有实例都[报告了其漏洞状态](https://mondoo.app/)

## 它是如何工作的？

代理通过持续评估已安装的软件包，并通过HTTPS将包元数据提交到Mondoo API来工作。在你的Mondoo Space注册后，代理已准备好进行漏洞评估。

CLI专为两种用例而设计：

> 作为持续漏洞评估的服务运行
>
> 在工作站上运行以评估远程系统或docker镜像的漏洞
>
> 将docker镜像扫描作为CI/CD的一部分运行

**使用案例：服务**

你希望持续查看服务器的漏洞评估。代理程序在后台运行并提交已安装软件包的更改以进行漏洞分析。通过使用此方法，你始终可以获得基础架构的最新视图。

 **使用案例：工作站或CI/CD**

你想评估可通过SSH访问的系统的漏洞。

    
    
    mondoo scan -t ssh://ec2-user@54.146.196.40
    Start vulnerability scan:
      →  verify platform access to ssh://ec2-user@54.146.196.40
      →  gather platform details
      →  detected amzn 2
      →  gather platform packages for vulnerability scan
      →  found 433 packages
      →  analyse packages for vulnerabilities
    Advisory Report:
      →  ■ found no advisories
      →  report is available at https://mondoo.app/v/goofy-hofstadter-187738/gallant-payne-155889/reports/1NmpiPcVfQZLT2GDylRjOc1wSMh

另一种选择是快速扫描存储在docker注册表中的docker镜像：

    
    
    mondoo scan -t docker://centos:7
    Start vulnerability scan:
      →  verify platform access to docker://centos:7
      →  gather platform details
      →  detected centos 7.6.1810
      →  gather platform packages for vulnerability scan
      →  found 146 packages
      →  analyse packages for vulnerabilities
    Advisory Report:
      ■        PACKAGE       INSTALLED          VULNERABLE (<)       ADVISORY                                                                                     
      ■   9.8  python        2.7.5-76.el7       0:2.7.5-77.el7_6     https://mondoo.app/advisories/RHSA-2019%3A0710  
      ╰─  9.8  python        2.7.5-76.el7       0:2.7.5-80.el7_6     https://mondoo.app/advisories/RHSA-2019%3A1587  
      ■   9.8  python-libs   2.7.5-76.el7       0:2.7.5-77.el7_6     https://mondoo.app/advisories/RHSA-2019%3A0710  
      ╰─  9.8  python-libs   2.7.5-76.el7       0:2.7.5-80.el7_6     https://mondoo.app/advisories/RHSA-2019%3A1587  
      ■   8.8  libssh2       1.4.3-12.el7       0:1.4.3-12.el7_6.2   https://mondoo.app/advisories/RHSA-2019%3A0679  
      ■   8.6  bind-license  32:9.9.4-73.el7_6  32:9.9.4-74.el7_6.1  https://mondoo.app/advisories/RHSA-2019%3A1294  
      ■   4.7  openssl-libs  1:1.0.2k-16.el7    1:1.0.2k-16.el7_6.1  https://mondoo.app/advisories/RHSA-2019%3A0483  
      →  ■ found 5 advisories: 2 critical, 2 high, 1 medium, 0 low, 0 none, 0 unknown
      →  report is available at https://mondoo.app/v/goofy-hofstadter-187738/gallant-payne-155889/reports/1NmZsWAQUmlXGtf5dqt083hfRJx
    exit status 104

代理可以扫描以下资产：

> 本地操作系统
>
> 通过SSH远程操作系统
>
> Docker镜像（本地或远程）
>
> Docker容器（运行或停止）

## 使用

    
    
    mondoo help
    
    _____ ______   ________  ________   ________  ________  ________
    |\   _ \  _   \|\   __  \|\   ___  \|\   ___ \|\   __  \|\   __  \
    \ \  \\\__\ \  \ \  \|\  \ \  \\ \  \ \  \_|\ \ \  \|\  \ \  \|\  \
     \ \  \\|__| \  \ \  \\\  \ \  \\ \  \ \  \ \\ \ \  \\\  \ \  \\\  \
      \ \  \    \ \  \ \  \\\  \ \  \\ \  \ \  \_\\ \ \  \\\  \ \  \\\  \
       \ \__\    \ \__\ \_______\ \__\\ \__\ \_______\ \_______\ \_______\
        \|__|     \|__|\|_______|\|__| \|__|\|_______|\|_______|\|_______|
    
    
    Mondoo scans operating systems for known vulnerabilities
    
    Usage:
      mondoo [command]
    
    Available Commands:
      help        Help about any command
      register    Registers Mondoo agent with Mondoo Cloud
      status      Verifies the access to Mondoo Cloud
      unregister  Unregister Mondoo agent from Mondoo Cloud
      version     Displays the Mondoo agent version
      vuln        Scans an asset for known vulnerabilities
    
    Flags:
          --config string   config file (default is $HOME/.mondoo.yaml)
      -h, --help            help for mondoo
    
    Use "mondoo [command] --help" for more information about a command.

请参阅[Mondoo CLI](https://mondoo.io/docs/agent/mondoo)使用说明。

## 配置

代理使用yaml配置文件。有关详细信息，请参阅[配置文档](https://mondoo.io/docs/agent/configuration)。

## 帮助

有关安装的帮助，请访问[诊断文档](https://mondoo.io/docs/agent/diagnosing)或联系[Mondoo支持](https://mondoo.io/docs/help)。

## 自动化安装

通过 Bash 脚本安装 Mondoo 代理

![16.JPG](https://image.3001.net/images/20190906/1567732670_5d71b3bee07fa.jpg!small)

此单行脚本安装正在为服务器安装和配置Mondoo代理。其执行以下操作：

> 检测操作系统
>
> 安装Mondoo包
>
> 如果提供了MONDOO_REGISTRATION_TOKEN，则注册代理
>
> 如果代理已注册，则配置服务

**注意：**
我们建议你在使用之前熟悉我们的脚本。源代码可以在我们的公共[github存储库](https://github.com/mondoolabs/mondoo/blob/master/install.sh)中找到

它没有下载最新的二进制文件，而是配置gpg签名的Mondoo软件包存储库。这样可以方便地安装/更新/删除Mondoo代理。

 **注意：**
如果你正在寻找binary下载（例如，我们建议将其用于工作站设置），请按照我们的[binary安装说明](https://mondoo.io/docs/agent/binaries)进行操作

## 示例

 **安装包和注册代理**

安装包后，安装脚本将查找MONDOO_REGISTRATION_TOKEN环境变量。如果设置了，则启动注册过程。

    
    
    export MONDOO_REGISTRATION_TOKEN='ey...ax'
    curl -sSL https://mondoo.io/install.sh | bash

 **安装包并手动注册**

如果未设置环境变量，则可以轻松地执行注册作为第二步：

    
    
    curl -sSL https://mondoo.io/install.sh | bash
    MONDOO_REGISTRATION_TOKEN='ey...ax'
    mondoo register --config /etc/opt/mondoo/mondoo.yml --token 'MONDOO_REGISTRATION_TOKEN'

 **systemd 配置**

mondoo包附带了systemd配置。默认情况下，不启用mondoo服务。你可以通过以下方式启用和启动服务：

    
    
    $ systemctl enable mondoo.timer
    $ systemctl start mondoo.timer
    $ systemctl daemon-reload

##  **通过 cloud-init 安装 Mondoo 代理**

大多数云环境都支持在启动期间配置操作系统。在大多数情况下都使用cloud-init。对于Linux系统，[cloud-init](https://cloudinit.readthedocs.io/en/latest/)支持bash脚本。

我们只是将Mondoo [Bash
installer](https://mondoo.io/docs/agent/bash)[脚本](https://mondoo.io/docs/agent/bash)用于cloud-init。要使用cloud-init部署代理，请通过[Mondoo Dashboard](https://mondoo.app/) -> Select
Space -> Agents -> New Agent获取注册令牌，并将其粘贴到以下代码片段中：

    
    
    #!/bin/bash
    export MONDOO_REGISTRATION_TOKEN='ey..gg'
    curl -sSL https://mondoo.io/install.sh | bash

一旦机器准备就绪，第一次扫描将在机器启动后约30秒执行。

## 示例

 **AWS EC2 实例用户数据**

1\. 将上面显示的代码片段保存到mondoo-cloudinit.sh，并粘贴到你的注册令牌中：

    
    
    cat > mondoo-cloudinit.sh << EOF
    #!/bin/bash
    export MONDOO_REGISTRATION_TOKEN='eyJhbG..bn'
    curl -sSL https://mondoo.io/install.sh | bash
    EOF

2\. 启动一个新实例

    
    
    # Note: you need to adapt the image-id, security-group-ids, key-name to your region and account
    aws ec2 run-instances --region us-east-1 --image-id  ami-0ad82a384c06c911e --security-group-ids sg-903004f8 --count 1 --instance-type t2.micro --key-name chris-rock --user-data file://mondoo-cloudinit.sh

![17.JPG](https://image.3001.net/images/20190906/1567732735_5d71b3ff39e2c.jpg!small)

安装完成后，你可以在Mondoo仪表板中查看漏洞扫描的结果：

![18.png](https://image.3001.net/images/20190906/1567732758_5d71b416a6bdd.png!small)

一旦机器启动并运行，它将自动向Mondoo报告漏洞。有关AWS CLI的更多文档，请参阅[启动，列出和终止Amazon
EC2实例](https://docs.aws.amazon.com/cli/latest/userguide/cli-services-ec2-instances.html)以及[启动时在Linux实例上运行命令](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/user-data.html)

如要进行故障排除，请查看/var/log/cloud-init-output.log中的cloudinit运行输出。

## CLI 相关

## mondoo

Mondoo CLI

### Synopsis

    
    
    _____ ______   ________  ________   ________  ________  ________
    |\   _ \  _   \|\   __  \|\   ___  \|\   ___ \|\   __  \|\   __  \
    \ \  \\\__\ \  \ \  \|\  \ \  \\ \  \ \  \_|\ \ \  \|\  \ \  \|\  \
     \ \  \\|__| \  \ \  \\\  \ \  \\ \  \ \  \ \\ \ \  \\\  \ \  \\\  \
      \ \  \    \ \  \ \  \\\  \ \  \\ \  \ \  \_\\ \ \  \\\  \ \  \\\  \
       \ \__\    \ \__\ \_______\ \__\\ \__\ \_______\ \_______\ \_______\
        \|__|     \|__|\|_______|\|__| \|__|\|_______|\|_______|\|_______|

Mondoo扫描操作系统是否存在已知漏洞

 **选项**

    
    
     --config string   config file (default is $HOME/.mondoo.yaml)
    -h, --help            help for mondoo

##  **mondoo 注册**

使用Mondoo Cloud注册Mondoo代理

### Synopsis

此命令使用Mondoo Cloud注册mondoo代理。它需要'--token'参数。

你可以通过 Mondoo Dashboard [https://mondoo.app](https://mondoo.app/) -> Space ->
Agents -> New生成新的注册令牌。复制令牌并将其作为'--token'参数传递：

    
    
    mondoo register [flags]

 **选项**

    
    
     --api-endpoint string   mondoo api url
    -h, --help                  help for register
    -t, --token string          agent registration token

 **从父命令继承的选项**

    
    
    --config string   config file (default is $HOME/.mondoo.yaml)

##  **mondoo 状态**

验证对Mondoo Cloud的访问

### Synopsis

Status向Mondoo Cloud发送ping以验证凭据。

    
    
    mondoo status [flags]

 **选项**

    
    
    -h, --help   help for status

 **从父命令继承的选项**

    
    
    --config string   config file (default is $HOME/.mondoo.yaml)

## mondoo 扫描

扫描资产查找已知漏洞

### Synopsis

此命令会触发漏洞扫描。

默认情况下，扫描本地系统：

    
    
    $ mondoo scan

此外，mondoo可以扫描远程ssh目标。Mondoo使用ssh agent和ssh config作为默认值来检索目标的凭据。

    
    
    $ mondoo scan -t ssh://ec2-user@52.51.185.215
    $ mondoo scan -t ssh://ec2-user@52.51.185.215:2222

你还可以访问位于docker registries中的docker镜像：

    
    
    $ mondoo scan -t docker://ubuntu:latest
    $ mondoo scan -t docker://elastic/elasticsearch:7.2.0
    $ mondoo scan -t docker://gcr.io/google-containers/ubuntu:14.04
    $ mondoo scan -t docker://registry.access.redhat.com/ubi8/ubi

如果在本地安装docker，也可以通过其id访问容器和镜像：

    
    
    $ mondoo scan -t docker://docker-image-id
    $ mondoo scan -t docker://docker-container-id

如果你希望在本地存储报告，请将输出通过管道传输到文件中：

    
    
    $ mondoo scan --format yaml > myreport.yaml

scan子命令返回以下退出代码：

    
    
    * 0 - scan completed successfully with no vulnerabilities found
    * 1 - error during execution
    * 101 - scan completed successfully with low vulnerabilities found
    * 102 - scan completed successfully with medium vulnerabilities found
    * 103 - scan completed successfully with high vulnerabilities found
    * 104 - scan completed successfully with critical vulnerabilities found

有关更多文档，请访问<https://mondoo.io/docs/>

    
    
    mondoo scan [flags]

 **选项**

    
    
    --assetmrn string         Optional override of the  asset mrn for the asset
        --collector string        The collector reports the packages to Mondoo cloud only and does not print the result on CLI. This is useful for automated environments. Supported values are 'http' and 'awssns'.
        --color string            Highlights text and vulnerability output with colors. The possible values of when can be 'never', 'always' or 'auto'. (default "always")
    -t, --connection string       The connection is the identifier a way to reach the asset. Supported connections are 'local://', 'docker://' and 'ssh://' (default "local://")
        --exit-0-on-success       Returns 0 as exit code of the scan was successful. It ignores the severity of the vulnerability assessment.
        --format string           Set the output format for the vulnerability report. Available options are 'cli' and 'yaml'. (default "cli")
    -h, --help                    help for scan
        --id-detector string      Set the assset id detector (eg. awsec2, hostname)
    -i, --identity-file string    Selects a file from which the identity (private key) for public key authentication is read.
        --labels stringToString   Additional labels enrich the asset with additional information. Multiple labels can be passed in via --labels key=value). (default [])
    -p, --password string         ssh password (not recommended in production)
        --referenceid string      Optional override of the reference id for the target

 **从父命令继承的选项**

    
    
    --config string   config file (default is $HOME/.mondoo.yaml)

## mondoo 取消注册

从Mondoo Cloud取消注册Mondoo代理

### Synopsis

通过调用mondoo unregister，代理将与Mondoo Cloud分离。此过程还将启动代理证书的重新确认，以确保以后不再使用代理凭据。

    
    
    mondoo unregister [flags]

 **选项**

    
    
    --force   force new registration
    -h, --help    help for unregister

 **从父命令继承的选项**

    
    
    --config string   config file (default is $HOME/.mondoo.yaml)

## Mondoo 集成

Mondoo为主要的CI/CD和云环境提供了开箱即用的集成。具体请参阅：

> <https://mondoo.io/docs/integration/aws-ec2>
>
> <https://mondoo.io/docs/integration/cicd?id=azure-devops>
>
> <https://mondoo.io/docs/integration/cicd?id=circle-ci>
>
> <https://mondoo.io/docs/integration/cicd?id=gcp-cloudbuild>
>
> <https://mondoo.io/docs/integration/cicd?id=gitlab>
>
> <https://mondoo.io/docs/integration/packer>
>
> <https://mondoo.io/docs/integration/terraform>

## 帮助

你可以通过邮件（[hello@mondoo.io](mailto:hello@mondoo.io)）与我们取得联系。或在[我们的社区](https://spectrum.chat/mondoo)中提出你的问题。如果你发现了bug，你可以向我们提交[issue](https://github.com/mondoolabs/mondoo/issues)。

 ***参考来源：[mondoo](https://mondoo.io/docs/get-started/)，FB小编secist编译，转载请注明来自FreeBuf.COM**

