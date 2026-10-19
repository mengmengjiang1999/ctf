### ****![](https://image.3001.net/images/20200807/1596779005.jpg!small)****

## ************Harbian-Audit**** ** **工具介绍****

Harbian-Audit是一款针对Debian GNU / Linux和CentOS 8发行版的强化安全审计工具。

该工具主要的测试环境是在debian GNU / Linux 9/10和CentOS
8中进行的，其他版本目前还没有经过全面的测试。该发行版中还没有实现桌面端和SELinux相关的东西。

该代码框架基于[ _OVH-debian-cis_](https://github.com/ovh/debian-cis)项目实现，根据Debian
9/10和CentOS 8的功能特点修改了原有的一些实现，添加并实现了[ _STIG
Red_Hat_Enterprise_Linux_7_V2R5_](https://github.com/hardenedlinux/STIG-OS-mirror/blob/master/redhat-STIG-DOCs/U_Red_Hat_Enterprise_Linux_7_V2R5_STIG.zip)[ _STIG Ubuntu
V1R2_](https://dl.dod.cyber.mil/wp-content/uploads/stigs/zip/U_Canonical_Ubuntu_16-04_LTS_V1R2_STIG.zip)和[
_cisecurity.org_](https://www.cisecurity.org/)网站建议的检查项，此外，HardenedLinux社区还添加并实现了一些检查项。实现了基础设施结构的审计和应用功能，对可以自动修复的项目实现了自动修复功能。

    
    
    # bash bin/hardening.sh --audit-all
    
    [...]
    
    hardening                 [INFO] Treating /home/test/harbian-audit/bin/hardening/13.15_check_duplicate_gid.sh
    
    13.15_check_duplicate_gid [INFO] Working on 13.15_check_duplicate_gid
    
    13.15_check_duplicate_gid [INFO] Checking Configuration
    
    13.15_check_duplicate_gid [INFO] Performing audit
    
    13.15_check_duplicate_gid [ OK ] No duplicate GIDs
    
    13.15_check_duplicate_gid [ OK ] Check Passed
    
    [...]
    
    ################### SUMMARY ###################
    
          Total Available Checks : 278
    
             Total Runned Checks : 278
    
             Total Passed Checks : [ 239/278 ]
    
             Total Failed Checks : [  39/278 ]
    
       Enabled Checks Percentage : 100.00 %
    
           Conformity Percentage : 85.97 %

## ****快速启动**** ** **Harbian-Audit**** ** **工具****

广大研究人员可以使用下列命令将该项目源码克隆至本地，并进行项目部署和使用：

    
    
    $ git clone https://github.com/hardenedlinux/harbian-audit.git && cd harbian-audit
    
    # cp etc/default.cfg /etc/default/cis-hardening
    
    # sed -i "s#CIS_ROOT_DIR=.*#CIS_ROOT_DIR='$(pwd)'#" /etc/default/cis-hardening
    
    # bin/hardening.sh --init
    
    # bin/hardening.sh --audit-all
    
    hardening                 [INFO] Treating /home/test/harbian-audit/bin/hardening/1.1_install_updates.sh
    
    1.1_install_updates       [INFO] Working on 1.1_install_updates
    
    1.1_install_updates       [INFO] Checking Configuration
    
    1.1_install_updates       [INFO] Performing audit
    
    1.1_install_updates       [INFO] Checking if apt needs an update
    
    1.1_install_updates       [INFO] Fetching upgrades ...
    
    1.1_install_updates       [ OK ] No upgrades available
    
    1.1_install_updates       [ OK ] Check Passed
    
    [...]
    
    ################### SUMMARY ###################
    
          Total Available Checks : 278
    
             Total Runned Checks : 278
    
             Total Passed Checks : [ 239/278 ]
    
             Total Failed Checks : [  39/278 ]
    
       Enabled Checks Percentage : 100.00 %
    
           Conformity Percentage : 85.97 %
    
    # bin/hardening.sh --set-hardening-level 5
    
    # bin/hardening.sh --apply
    
    hardening                 [INFO] Treating /home/test/harbian-audit/bin/hardening/1.1_install_updates.sh
    
    1.1_install_updates       [INFO] Working on 1.1_install_updates
    
    1.1_install_updates       [INFO] Checking Configuration
    
    1.1_install_updates       [INFO] Performing audit
    
    1.1_install_updates       [INFO] Checking if apt needs an update
    
    1.1_install_updates       [INFO] Fetching upgrades ...
    
    1.1_install_updates       [ OK ] No upgrades available
    
    1.1_install_updates       [INFO] Applying Hardening
    
    1.1_install_updates       [ OK ] No Upgrades to apply
    
    1.1_install_updates       [ OK ] Check Passed
    
    [...]

## ****Harbian-Audit**** ** **工具使用方法****

### ****预安装**** ** **Harbian-Audit**** ** **工具****

如果使用网络安装到Debian GNU / Linux上，则需要在使用该工具之前安装下列软件包：

    
    
    # apt-get install -y bc net-tools pciutils network-manager

Redhat / CentOS平台则需要在使用该工具之前安装下列软件包：

    
    
    # yum install -y bc net-tools pciutils NetworkManager epel-release

### ****工具预配置****

首先，我们必须为所有用户设置密码。否则，在开始操作之后将无法登录。示例如下（操作系统用户：root和test）：

    
    
    # passwd
    
    # passwd test

### ****工具配置****

该工具的安全强化脚本在bin/hardening文件中。每个脚本在etc/conf.d/[script_name].cfg中都有相应的配置文件。

每个强化脚本都可以通过其配置文件单独启用。比如说，下面给出的是disable_system_accounts的默认配置文件：

    
    
    # Configuration for script of same name
    
    status=disabled
    
    # Put here your exceptions concerning admin accounts shells separated by spaces
    
    EXCEPTIONS=""

状态参数可以取3个值：

> -disabled （不执行任何操作）：该脚本将无法运行。
>
> -audit（RO）：该脚本将检查是否应该更改任何应用。
>
> -enabled （RW）：该脚本将检查是否应该进行任何更改，并自动应用它可以执行的操作。

您还可以通过修改级别来将配置项设置为启用，命令如下：

1、首次使用时，通过audit-all命令生成etc / conf.d / [script_name] .cfg文件。

    
    
    # bash bin/hardening.sh --audit-all

2、通过set-hardening-level启用[script_name] .cfg文件来使用命令设置强化级别，以使相应级别的审核条目生效。

    
    
    # bash bin/hardening.sh --set-hardening-level <level>

全局配置在etc/hardening.cfg中，该文件可以控制日志级别和备份目录，每当脚本被指示编辑文件时，它就会在该目录中创建一个带有时间戳的备份。

## ****执行安全强化****

要运行检查并应用修复程序，请运行bin/hardening.sh文件。

此命令有2种主要操作模式：

> \--audit：使用所有已启用和审核模式的脚本来审核系统
>
> \--apply：使用所有已启用和审核模式的脚本来审核系统，并对已启用的脚本应用进行更改

此外，--audit-all可用于强制运行所有审核脚本，包括已禁用的脚本。这不会改变整个系统。

\--audit-all-enable-passed可以用作启动配置的快速方法。它将以审核模式运行所有脚本。如果脚本通过，它将自动为以后的运行启用。如果已经开始自定义配置，请不要使用此选项。

使用以下命令来强化您的操作系统安全：

    
    
    # bash bin/hardening.sh --apply

## ****执行安全强化**** ** **后（非常重要）****

当exec --apply和set-hardening-level设置为5（最高级别）时，您需要执行以下操作：

1、在应用9.5（限制对su命令的访问）时，由于普通用户无法执行后续操作，因此必须使用root帐户登录到操作系统。如果只能使用ssh进行远程登录，则必须在普通用户登录时使用su命令。然后执行以下操作：

    
    
    # sed -i '/^[^#].*pam_wheel.so.*/s/^/# &/' /etc/pam.d/su

临时注释掉包含pam_wheel.so的行。使用完su命令后，请取消该行的注释。

2、当应用7.4.4_hosts_deny.sh时，无法通过ssh服务连接到操作系统，因此需要在/etc/hosts.allow上设置允许访问主机列表，例如：

    
    
    # echo "ALL: 192.168.1. 192.168.5." >> /etc/hosts.allow

此示例仅允许IP地址为192.168.1.[1-255] 和192.168.5.[1-255]的用户来访问该系统。需要根据您的情况进行配置。

3、为普通用户设置功能，例如（用户名为test）：

    
    
    # sed -i "/^root/a\test    ALL=(ALL:ALL) ALL" /etc/sudoers

4、设置基本防火墙规则，根据所使用的应用程序设置相应的防火墙规则。增强Debian GNU / LinuxHardened社区的基本防火墙规则的：

### ****Iptabels格式规则：****

[_etc.iptables.rules.v4.sh_](https://github.com/hardenedlinux/harbian-audit/blob/master/docs/configurations/etc.iptables.rules.v4.sh)将执行以下操作：

    
    
    $ INTERFACENAME="your network interfacename(Example eth0)"
    
    # bash docs/configurations/etc.iptables.rules.v4.sh $INTERFACENAME
    
    # iptables-save > /etc/iptables/rules.v4
    
    # ip6tables-save > /etc/iptables/rules.v6

### ****nft格式规则：****

[_nftables.conf_](https://github.com/hardenedlinux/harbian-audit/blob/master/docs/configurations/etc.nftables.conf)
将执行以下操作（您的网络接口名称（示例eth0））：

    
    
    $ sed -i 's/^define int_if = ens33/define int_if = eth0/g' etc.nftables.conf
    
    # nft -f ./etc.nftables.conf

5、当所有操作完成后。--final方法将执行下列任务：

首先，使用passwd命令更改普通用户和root用户的密码，以应用pam_cracklib模块配置的密码复杂性和健壮性。

其次，对项目状态重新初始化。

    
    
    # bin/hardening.sh --final

## ****特别提示****

一些检查项会检查各种情况，并且是相互依赖的，它们必须被应用（修复）多次，并且每次应用（修复）后，必须重新启动操作系统。

## ****参考资料****

****用于**** ** **Debian GNU / Linux 9的Harbian审计基准****

本文件是对CIS参考文件中未包含的各节所增加的内容的补充说明。包括STIG参考文档和HardenedLinux社区推荐的其他附加检查。

> [_CIS Debian GNU/Linux 8 Benchmark
> v1.0.0_](https://benchmarks.cisecurity.org/downloads/show-> single/index.cfm?file=debian8.100)
>
> [_CIS Debian GNU/Linux 9 Benchmark
> v1.0.0_](https://benchmarks.cisecurity.org/downloads/show-> single/index.cfm?file=debian8.100)
>
> [_harbian audit Debian Linux 9
> Benchmark_](https://github.com/hardenedlinux/harbian-> audit/blob/master/docs/harbian_audit_Debian_9_Benchmark_v0.1.mkd)

****手动操作文档****

> [_如何配置_ _grub2密码保护_](https://github.com/hardenedlinux/harbian-> audit/blob/master/docs/configurations/manual-operation-> docs/how_to_config_grub2_password_protection.mkd)
>
> [_如何使用_ _debian 9持久化iptables规则_](https://github.com/hardenedlinux/harbian-> audit/blob/master/docs/configurations/manual-operation-> docs/how_to_persistent_iptables_rules_with_debian_9.mkd)
>
> [_如何部署_ _audisp-remote auditd 日志_](https://github.com/hardenedlinux/harbian-> audit/blob/master/docs/configurations/manual-operation-> docs/how_to_deploy_audisp_remote_for_audit_log.mkd)
>
>
> [_如何在debian10中从iptables迁移到nftables_](https://github.com/hardenedlinux/harbian-> audit/blob/master/docs/configurations/manual-operation-> docs/how_to_migrating_from_iptables_to_nftables_in_debian10.md)
>
> [_如何使用debian 10持久化nft_ _规则_](https://github.com/hardenedlinux/harbian-> audit/blob/master/docs/configurations/manual-operation-> docs/how_to_persistent_nft_rules_with_debian_10.mkd)

****用例文档****

> [_Nodejs + redis + mysql demo_](https://github.com/hardenedlinux/harbian-> audit/blob/master/docs/use-cases/nodejs-redis-mysql-usecase/README.md)
>
> [_deploy-hyperledger-cello-on-> debian-9_](https://github.com/hardenedlinux/harbian-> audit/blob/master/docs/use-cases/hyperledger-cello-usecase/README.mkd)
>
> [_nginx-mutual-ssl-proxy-http_](https://github.com/hardenedlinux/harbian-> audit/blob/master/docs/use-cases/tls-transmission-usecase/nginx-mutual-ssl-> proxy-http-service/Readme.mkd)
>
> [_nginx-mutual-ssl-proxy-tcp-udp_](https://github.com/hardenedlinux/harbian-> audit/blob/master/docs/use-cases/tls-transmission-usecase/using-Nginx-as-> SSL-tunnel-4TCP-UDP-service/Readme.mkd)

**其他**

> 互联网安全中心：[ _https：//www.cisecurity.org_](https://www.cisecurity.org/)
>
> STIG V1R4：[
> _https://iasecontent.disa.mil/stigs/zip/U_Red_Hat_Enterprise_Linux_7_V1R4_STIG.zip_](https://iasecontent.disa.mil/stigs/zip/U_Red_Hat_Enterprise_Linux_7_V1R4_STIG.zip)
>
> 防火墙规则：[ _https : //github.com/citypw/arsenal-4-sec-> testing/blob/master/bt5_firewall/debian_fw_](https://github.com/citypw/arsenal-4-sec-> testing/blob/master/bt5_firewall/debian_fw)

## _项目地址_

Harbian-Audit：【[ _GitHub传送门_](https://github.com/hardenedlinux/harbian-audit)】

