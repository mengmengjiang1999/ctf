# ****1**** ** **账号**** ** **和密码管理**** ** **的**** ** **现状****

账号和密码是我们每天工作和生活中，一定要用到的。

当一个人要记忆自己的多个银行卡、网站、手机APP的密码时，是一件非常让人头疼的问题，因为很容易忘记，或者因混淆而记错。

关于账号和密码的记忆，通常有几种方法：

第一种：用脑背下来

虽然是最好的方法，但除非是记忆力非常好的人，这个方法显然不太实际。

第二：用纸质笔记本记录下来

俗话说：好记性不如烂笔头。但是，这也不是最佳方案，因为如下问题：

问题1、对于复杂的账号和密码，很可能在使用人查阅和输入的过程中，纸质笔记本上的账号和密码被别人偷窥而泄露。

问题2、不便于在电脑端和手机端录入密码，尤其是密码复杂度很强时。

问题3、一旦记录账号和密码的纸质笔记本发生丢失、被盗、损毁、着火等等意外情况时，使用人将面临更棘手的账号和密码找回问题。

第三：采用电子文件格式，记录账号和密码，例如：使用电脑和手机中的记事本，这存在的问题是，通常记事本都是明文存放账号+密码，也容易被别人偷窥，恶意查阅，黑客盗取而泄露。

第四：采用密码管理软件，存放账号和密码，使用过程中仅需要【复制】+【粘贴】账号和密码就可以了，极大的避开上述密码管理方法的不足。

#  ** **2 使用密码管理软件就没有问题**** ** **了**** ** **吗？****

在实际的工作和生活中，我们可以借助一些第三方的密码管理软件来帮助自己管理账号、密码及其他信息，例如KeePass、Lastpass、1Password等密码管理软件，以提高输入密码的效率、安全性、也为了避免自己遗忘密码。

然而，相信聪明的读者和笔者一样，对第三方密码管理软件也不是完全信任，担心这类密码管理软件仍有泄露账号和密码的风险。

笔者将不信任第三方密码管理软件的原因，归结如下：

1、第三方闭源的密码管理软件，不论是共享软件，还是免费软件，其内部逻辑不得知，在用户使用期间，它们是否静默式联接互联网，是否向国外、国内的服务器发送已经存储的账号和密码，均不得知！

2、即使是第三方开源的密码管理软件，如果是采用公有云存储的方法，因为用户不可控，个人的账号和密码也并非是安全的。

#  ** **3 到底如何才能安全的管理**** ** **账号**** ** **和密码？****

按照本文前述，笔者建议使用开源的密码管理软件，并且在本地的计算机或服务器搭建一个私有化的密码管理平台，来代替1Password及Lastpass这类第三方密码管理软件。这样就规避了对上述第三方开源密码管理软件不能自主控制的问题。

笔者经过分析数种可以免费使用的开源密码管理软件，最后推荐Bitwarden 免费密码管理软件，它开源、免费，跨平台支持
Windows、Mac、Linux、iOS、Android 平台，同时也提供了 Chrome、Edge、Firefox、Safari
等浏览器扩展可实现快速填充账号密码一键登录网站。

本文是笔者基于开源密码管理软件，搭建的密码管理平台的实战类文章，目的是抛砖引玉，供读者学习参考。

 ** **实战环境介绍：****

 ** **1、宿主机Windows 11****

 ** **2、虚拟机软件Vmware workstation 16+NAT模式****

 ** **3、虚拟机实例ubuntu 2022****

 ** **4、虚拟机实例上采用docker+docker compose模式****

 ** **安装配置bitwarden(开源密码管理软件+自建密码服务器+浏览器插件)****

 ** **注：作者假定本文的读者是**** ** **具备L**** ** **inux**** ** **系统使用知识的专家，并且也熟悉W**** **
**indows**** ** **11和V**** ** **mware W**** ** **orkstation虚拟机的使用。****

##  ** **3.1**** ** **安装**** ** **docker****

//在线安装docker

# apt install docker.io

//启动 docker服务

# systemctl start docker

//设置 docker开机自动启动

# systemctl enable docker

//查看 docker版本

# docker version

##  ** **3.2 安装docker compose****

访问https://github.com/docker/compose/releases

下载docker-compose-linux-x86_64

Mv docker-compose-linux-x86_64 /usr/local/bin/docker-compose

chmod +x /usr/local/bin/docker-compose

docker-compose -v //测试是否安装成功

##  ** **3.3 安装bitwarden****

1、获取bitwarden一键安装脚本

curl -Lso bitwarden.sh https://go.btwrdn.co/bw-sh && chmod 700 bitwarden.sh

2、执行安装程序

./bitwarden.sh install

输入域名：Bitwarden.sy.cn

ssl证书全部选择no

数据库实例名：c9t9h5vault

Installation id 从bitwarden官网获取

[ _https://bitwarden.com/host_](https://bitwarden.com/host)

![](https://image.3001.net/images/20230719/1689747781_64b78145987791d2f4320.jpg!small)

图片1

使用SSL自签名证书 yes

3、设置虚拟机本地解析

$ vim /etc/hosts

追加一行

192.168.190.130 bitwarden.sy.cn //192.168.190.130为vmware 虚拟机的NAT地址

##  ** **3.4 启动bitwarden****

$ ./bitwarden.sh start

//ubuntu虚拟机打开防火墙

firewall-cmd --permanent --zone=public --add-port=443/tcp

firewall-cmd --permanent --zone=public --add-port=80/tcp

firewall-cmd --reload

##  ** **3.5 访问 bitwarden****

[ _https://bitwarden.sy.cn_](https://bitwarden.sy.cn)

![](https://image.3001.net/images/20230719/1689747802_64b7815a41f9b0e68765f.jpg!small)

图片2

或者

https://192.168.190.130

![](https://image.3001.net/images/20230719/1689747816_64b78168775630f193af6.jpg!small)

图片3

##  ** **3.6 浏览器安装bitwarden插件并设置****

以firefox为例：

![](https://image.3001.net/images/20230719/1689747832_64b78178261dc2109e5bb.jpg!small)

图片4

设置为自己的服务器

自托管环境

服务器url

[ _https://bitwarden.sy.cn_](https://bitwarden.sy.cn)

##  ** **3.7 局域网访问虚拟机的配置****

宿主机IP地址 10.3.1.46

虚拟机IP地址192.168.190.130

vmware 虚拟网络配置

![](https://image.3001.net/images/20230719/1689747849_64b7818926644ae56ae26.jpg!small)

图片5

![](https://image.3001.net/images/20230719/1689747862_64b781962595b25332155.jpg!small)

图片6

宿主机IP地址 10.3.1.46

上图设置了虚拟机192.168.190.130的443端口映射到宿主机的10.3.1.46的8888端口

windows11开放进站防火墙端口

![](https://image.3001.net/images/20230719/1689747875_64b781a314bea6d5f5694.jpg!small)

图片7

局域网内其他主机访问https://10.3.1.46:8888

![](https://image.3001.net/images/20230719/1689747888_64b781b0b9a93fef8b411.jpg!small)

图片8

至此，局域网内的人都可以用这个开源密码管理平台了。

##  ** **3.8 升级bitwarden****

随着开源软件的不断迭代更新，读者后期可以自行升级到最新版的bitwarden

$ sudo ./bitwarden.sh updateself

$ sudo ./bitwarden.sh update

#  ** **4**** ** **总结与体会****

通过使用第三方开源的密码管理软件bitwarden，在本地的计算机或服务器搭建一个私有化的密码管理平台，来代替1Password及Lastpass这类第三方密码管理软件。既做到了账号和密码管理的易用性，又做到私有化部署的安全性，不但自己可以用，自己的亲人和朋友都可以用，他们可以自助创建自己在密码管理平台的账户，然后管理自己的各类密码，再也不用担心忘记各个银行卡、网络平台、手机APP的密码，不用担心账号和密码非授权泄露给任何第三方。

