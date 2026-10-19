## 1\. 简介

本文是在linux系统下，安装新版博客程序（WordPress 6.0）的入门教程。从零开始，想拥有自己的小站，通过华为云，如何做到？大致需要如下步骤：

域名

注册华为云账号

域名注册

购买云服务器

添加域名解析

备案

安装环境

登录华为云

安装基础环境

创建虚拟主机

安装wordpres

其他说明

## 2\. 域名(若有，可以跳过此步骤)

注册华为云账号，并通过实名认证，过程略，可以参考[官方文档](https://support.huaweicloud.com/usermanual-account/account_auth_00001.html)

域名注册

在华为云控制台，

`服务列表`

里面输入

`域名注册`

搜索，如下图，点击搜索出来的结果：

`域名注册 Domains`

![image.png](https://image.3001.net/images/20220817/1660714273_62fc7d218c2eb5d8c4202.png!small)

创建域名信息模板：根据工信部域名实名认证要求，在注册域名时需要填写用户信息。 在左侧树状导航栏中，选择

`信息模板`

。在页面右上角，单击

`创建信息模板`

，根据要求填写

`个人用户`

或

`企业用户`

信息。  
![image.png](https://image.3001.net/images/20220817/1660714274_62fc7d220f886bd79d359.png!small)![image.png](https://image.3001.net/images/20220817/1660714274_62fc7d229bbe9506a9302.png!small)

点击左侧

`域名列表`

，然后选择右侧的

`注册域名`

![image.png](https://image.3001.net/images/20220817/1660714275_62fc7d2337affbd1a87cf.png!small)

输入理想的域名，然后点击

`查询`

，如果没有被占用，选择

`加入清单`

，之后选择右侧的

`立即购买`

，在打开的页面里面选择了

`已实名认证`

的信息模板，然后点击

`立即支付`

域名实名认证(可选，此处非域名备案)：由于支持“.com”、“.cn”、“.net”以及“.中国”后缀的域名关联信息模板的实名认证状态，因此，无需再次进行域名的实名认证，此时域名的“服务状态”为“已实名认证”。如果注册域名的后缀类型不支持关联信息模板的实名认证状态，可参考[官方文档](https://support.huaweicloud.com/qs-domain/zh-cn_topic_0122928879.html)处理。

## 3\. 购买云服务器(若有，可以跳过此步骤)

登录华为云控制台，在左侧选择`弹性云服务器 ECS`。  
![image.png](https://image.3001.net/images/20220817/1660714275_62fc7d23b24833e32bb19.png!small)

右侧选择`购买弹性云服务器`。  
![image.png](https://image.3001.net/images/20220817/1660714276_62fc7d246864816ac6bf8.png!small)

根据自己实际情况，购买服务器。  
![image.png](https://image.3001.net/images/20220817/1660714277_62fc7d253ae644a8c8a8c.png!small)  
![image.png](https://image.3001.net/images/20220817/1660714278_62fc7d26528837c8da37d.png!small)  
特别注意:

如果你的站点是放国内，需要对域名备案，备案需要包月购买ecs服务器3个月及以上，详情请参考[官方文档](https://support.huaweicloud.com/prepare-icp/icp_02_0003.html)的要求，注意`备案前准备`的里面的`可备案的域名`（不是所有域名都可以备案）和`可备案的服务器`（注意购买时长）等内容。

根据当前新版本WordPress(6.0)的系统要求，需要PHP7.4或更高版本，MySQL5.7或更高版本或者MariaDB
10.3或更高版本，HTTPS支持，由于是一台服务器上安装php，mysql，故建议内存至少2G。

如果对linux命令不熟悉，还可以选择如下所示的`市场镜像`，市场镜像已经集成安装好了环境，不需要命令操作，需要注意的是有些镜像是需要付费的。如果选择`市场镜像`里面的镜像，后续步骤可参考[官方文档](https://support.huaweicloud.com/bestpractice-ecs/zh-cn_topic_0119863154.html)。  
![image.png](https://image.3001.net/images/20220817/1660714278_62fc7d26e62e1758dc3ce.png!small)

网络选择了默认的，安全组选择了`Sys-WebServer`开头的，此安全组默认开通了ssh默认的22端口，以及web服务需要的80和443端口。由于服务器需要远程连接访问服务器，故此处选择了购买`弹性公网IP`。  
![image.png](https://image.3001.net/images/20220817/1660714279_62fc7d27c3bcbd17de180.png!small)

设置弹性云服务器ecs的密码，选择了默认的云备份  
![image.png](https://image.3001.net/images/20220817/1660714280_62fc7d285c8a02097a9e8.png!small)

根据自己实际情况，选择是否开启服务器`自动续费`功能(即每个月自动购买：按月购买：每次续费1个月，次数不限；按年购买：每次续费1年，次数不限)。  
![image.png](https://image.3001.net/images/20220817/1660714280_62fc7d28dc6c50cfc9449.png!small)

## 4\. 添加域名解析

登录华为云控制台，在服务列表中，选择`网络`> `云解析服务`，进入`云解析`页面。在左侧树状导航栏，选择`公网域名`,选择你的域名，点击`解析`  
![image.png](https://image.3001.net/images/20220817/1660714281_62fc7d297d4265710c2e4.png!small)  
如对外提供的域名`www.domain.com`，那就请添加一条A记录，主机记录是`www`,类型`A -将域名指向IPv4地址`,值填写服务器的`外网ip`。如下所示。如遇问题或者对域名解析不熟悉，可参考华为云[官方文档](https://support.huaweicloud.com/qs-dns/dns_qs_0002.html)  
![image.png](https://image.3001.net/images/20220817/1660714281_62fc7d29ec43b2122996b.png!small)

## 5\. 备案(服务器在非大陆地区，此步骤可以跳过)

如果你的站点放在国内，需要对域名进行备案，准备好服务器之后,根据[官网文档](https://support.huaweicloud.com/qs-icp/icp_07_0002.html)完成备案操作。备案通过之后就可以继续下面的步骤了。

## 6\. 安装环境

登录华为云控制台，在`服务列表`里面选择`弹性服务器 ECS`，使用服务器ip登录服务器。  
![image.png](https://image.3001.net/images/20220817/1660714282_62fc7d2a8dc7d41147055.png!small)  
![image.png](https://image.3001.net/images/20220817/1660714283_62fc7d2b02225a1c3acc5.png!small)  
 **注：**

登录涉及到一些基础知识，不会也没有关系，可以参考华为云[官方文档](https://support.huaweicloud.com/usermanual-ecs/zh-cn_topic_0017955380.html)，详细讲解了如何登录linux服务器。

如遇问题无法登录服务器，请检查安全组设置是否开启了22端口访问权限，可以参考[配置安全组规则](https://support.huaweicloud.com/usermanual-ecs/zh-cn_topic_0030878383.html)，一般情况下22端口默认是开通所有人访问的。

如还有问题，可以提交工单寻求帮助(如下:登录控制台之后，点击

`新建工单`

)。  
![image.png](https://image.3001.net/images/20220817/1660714283_62fc7d2b70061fc18212a.png!small)

安装基础环境，为了追求简单入门，这里采取了`lnmp环境一键安装包`，lnmp软件的安装要求如下，更多信息可以参考官网文档`https://lnmp.org/install.html`

    
    
    1. CentOS/RHEL/Fedora/Debian/Ubuntu/Raspbian/Deepin/Aliyun/Amazon/Mint Linux发行版
    2. 需要5GB以上可用空间，MySQL 5.7,MariaDB 10至少9GB剩余空间,MySQL8.0最新版至少25GB以上
    3. 需要128MB以上内存(128MB小内存,Xen需有SWAP,OpenVZ至少要有128MB以上的vSWAP或突发内存)，注意小内存请勿使用64位系统！
    4. 安装MySQL 5.6或5.7及MariaDB 10必须1G以上内存，更高版本至少要2G内存!。
    5. 安装PHP 7及以上版本必须1G以上内存!。
    6. VP,s或服务器必须设置好可用的yum或apt-get源并确保能正常工作，离线安装需要增加 CheckMirror=n 参数！
    7. Linux下区分大小写，输入命令时请注意！
    8. 如有通过yum或apt-get安装的MySQL/MariaDB请自行备份数据等相关文件！
    9. CentOS 5、6、8,Debian 6、7、8或更低版本官网已经结束支持无法直接使用，需自行更换vault或archive源！
    10. CentOS 6、8请用lnmp 1.9+版本进行安装！
    11. Ubuntu 18+,Debian 9+,Mint 19+,Deepin 15.7+及所有新的Linux发行版只能使用1.7+进行安装！
    12. PHP 7.1.*以下版本不支持Ubuntu 19+、Debian 10等等非常新的Linux发行版！
    13. 阿里云Ubuntu 14.04系统模版有问题不要用！！！
    14. PHP 7.4升级或安装必须CentOS 7+,Debian 8+,Ubuntu 16.04+且必须使用1.7+！！！
    15. MySQL 8.0.23以下版本升级或安装必须CentOS 8+,Debian 9+,Ubuntu 16.04+且必须使用1.7+！！！
    16. MySQL 8.0.24以上版本升级或安装必须Debian 11+,Ubuntu 20.04+,Fedora 33+且必须使用1.8！！！
    

使用到如下命令开始安装,如提示`-bash: wget: command not found`，使用`yum install wget
-y`命令安装wget，然后重新执行下面的命令。

    
    
    wget http://soft.vp,ser.net/lnmp/lnmp1.9.tar.gz -cO lnmp1.9.tar.gz && tar zxf lnmp1.9.tar.gz && cd lnmp1.9 && ./install.sh lnmp
    

运行上述LNMP安装命令后，会出现如下提示：  
![image.png](https://image.3001.net/images/20220817/1660714283_62fc7d2be2a974a8e05f4.png!small)选择你需要安装的MySQL/MariaDB版本（注:新版wordpress
6.0的系统要求：MySQL5.7或更高版本或者MariaDB 10.3或更高版本），如果选择MySQL
5.7、8.0且是x86或x86_64架构会提示：”Using Generic Binaries [y/n]:“ 这一步是提示是否使用二进制安装，输入 y
为使用二进制安装，输入 n 为使用源码编译安装。根据官方文档的介绍，这个地方可以输入`n`，采用编译安装的方式。

设置mysql的root管理员密码(请牢记)  
![image.png](https://image.3001.net/images/20220817/1660714284_62fc7d2c62f853b157286.png!small)  
如果输入有错误需要删除时，可以按住Ctrl再按Backspace键进行删除(个别情况下是只需按Backspace键)

询问是否需要启用MySQL InnoDB，InnoDB引擎默认为开启，一般建议开启，直接回车或输入`y`  
![image.png](https://image.3001.net/images/20220817/1660714284_62fc7d2cc87b0d5b7b839.png!small)

安装php，自行选择安装的版本（注:新版wordpress 6.0的系统要求：PHP7.4或更高版本）  
![image.png](https://image.3001.net/images/20220817/1660714285_62fc7d2d3af82badb1bbf.png!small)

选择是否安装内存优化,输入对应序号回车,可以选择 不安装、Jemalloc或TCmalloc，直接回车为默认为不安装。  
![image.png](https://image.3001.net/images/20220817/1660714285_62fc7d2da1b645459e049.png!small)

按任意键开始安装  
![image.png](https://image.3001.net/images/20220817/1660714286_62fc7d2e1cf7984897ca3.png!small)

如果提示`Install lnmp V1.9 completed! enjoy it.`，说明已经安装成功了。  
![image.png](https://image.3001.net/images/20220817/1660714286_62fc7d2ebb82d6fa7e734.png!small)

创建网站的根目录，如果不熟悉linux命令，可以直接执行下面的命令

    
    
    mkdir -pv /home/wwwroot/
    cd /home/wwwroot/
    wget https://cn.wordpress.org/latest-zh_CN.tar.gz
    tar zxvf latest-zh_CN.tar.gz
    chown -R www.www wordpress
    

添加网站，执行如下命令

    
    
    lnmp vhost add
    

出现如下界面：  
![image.png](https://image.3001.net/images/20220817/1660714287_62fc7d2f34a0a71f2f4ff.png!small)这里要输入要添加网站的域名，我们以添加`www.domain.com`域名为例，如下图输入域名
`www.domain.com`回车后提示如下  
![image.png](https://image.3001.net/images/20220817/1660714287_62fc7d2faaeea7e78c4ec.png!small)

添加更多域名  
![image.png](https://image.3001.net/images/20220817/1660714288_62fc7d302075032104838.png!small)是否添加更多域名，再输入要绑定的域名，这里我们将`domain.com`也绑上，多个域名空格隔开，如不需要绑其他域名就直接回车。  
(注：带www和不带www的是不同的域名，如需带www和不带的www的域名都访问同一个网站需要同时都绑定)。

指定网站的根目录  
![image.png](https://image.3001.net/images/20220817/1660714288_62fc7d3098b0fd437c04f.png!small)如果你完全按照本文档操作的，这里请输入`/home/wwwroot/wordpress`，然后回车，网站目录不存在的话会自动创建目录。不输入直接回车的话，采用默认目录：/home/wwwroot/域名，作为网站的根目录

设置伪静态  
![image.png](https://image.3001.net/images/20220817/1660714289_62fc7d3188e9c307f792a.png!small)输入`y`，然后输入`wordpress`后回车。如下：  
![image.png](https://image.3001.net/images/20220817/1660714289_62fc7d31f25691e714627.png!small)

是否启用pathinfo ，直接输入`n`，或者回车（默认回车不启用）  
![image.png](https://image.3001.net/images/20220817/1660714290_62fc7d3272283771adbf0.png!small)

是否启用日志，如启用日志输入`y`，不启用输入`n`回车。可以自行选择。  
![image.png](https://image.3001.net/images/20220817/1660714290_62fc7d32dfae1c7d51bf8.png!small)如果启用需要再输入要设置的日志的名称，默认日志目录为：/home/wwwlogs/
,默认文件名为：域名.log  
![image.png](https://image.3001.net/images/20220817/1660714291_62fc7d33562058125910b.png!small)

是否启用IPV6  
![image.png](https://image.3001.net/images/20220817/1660714291_62fc7d33c1ac7f5145bda.png!small)

给wordpress程序建立一个要使用的数据库，下面询问是否创建数据库名称和mysql用户使用同一个名字，为了简单，请输入`y`，  
![image.png](https://image.3001.net/images/20220817/1660714292_62fc7d3438c0170c81db2.png!small)先输入MySQL的root管理员密码(注：输入密码将不显示，输入完成之后回车)，然后会提示`Enter
database
name:`，请输入要创建的数据库名称（自定义输入名称，此名称将作为wordpress数据库的用户和数据库名），回车确认。提示`Please enter
password for mysql user`,
后输入要设置的密码，回车确认。注此处一共设置了数据库的名字和mysql用户名（使用同一个名字）和此数据库的密码，记住此这些信息，后续安装wordpress会使用到。

添加SSL功能,输入`y`添加证书，这里选择`2`最为简单，将使用免费SSL证书提供商Letsencrypt的证书，自动生成SSL证书等信息。需要输入一个邮箱回车确认。  
![image.png](https://image.3001.net/images/20220817/1660714292_62fc7d34b3d394c617d3f.png!small)

是否强制将http连接跳转到https上，选择`y`  
![image.png](https://image.3001.net/images/20220817/1660714293_62fc7d35630f491de6c6f.png!small)  
提示`Press any key to start create virtul host...`之后按任意键继续，等待完成。

## 7\. 安装wordpres

访问你的域名，如https://www.domain.com ,点击`现在就开始！`  
![image.png](https://image.3001.net/images/20220817/1660714293_62fc7d35d7e2ed7e59020.png!small)

输入自定义创建的wordpres数据库名，mysql用户和密码（上面19步设置的信息），之后点击`提交`。  
![image.png](https://image.3001.net/images/20220817/1660714294_62fc7d36675e2813d6325.png!small)

点击`运行安装程序`  
![image.png](https://image.3001.net/images/20220817/1660714296_62fc7d387d667ac475916.png!small)

输入你的`站点标题`，这个就是站点的title，创建登录后台的`用户名`和`密码`，输入`您的电子邮箱地址`，之后点击`安装wordpres`。  
![image.png](https://image.3001.net/images/20220817/1660714296_62fc7d38f1608d199bd47.png!small)

安装成功  
![image.png](https://image.3001.net/images/20220817/1660714297_62fc7d398b3719b4d5045.png!small)

可以点击‘登录’登录wordpres的后台(记住此地址，登录管理后台需要输入此地址)  
![image.png](https://image.3001.net/images/20220817/1660714298_62fc7d3a0f913f2fc4a2f.png!small)

也可以浏览器输入你的域名如‘https://www.domain.com’打开你的站点。

至此完成完成。

## 8\. 其他说明：

lnmp一键安装包，安装完成之后，会自动创建一个默认的虚拟主机（站点），通过浏览器直接访问你的服务器ip就可以访问到，下面有`phpmyadmin`，`phpinfo`探针这些信息比较敏感，如果你不清楚这些东西的用途，建议执行如下命令来关闭这些访问

    
    
    #关闭访问
    mv /home/wwwroot/default  /home/wwwroot/default_bak/
    #如果要恢复，执行如下命令
    mv /home/wwwroot/default_bak  /home/wwwroot/default/
    

如果觉得过程繁琐，不想操作服务器，也不会linux命令，只会打字
，那有没有比较简单的建站方法呢？其实也有，华为云的`云速建站`，你值得拥有，会打字就会做网站，[官方地址点此直达](https://www.huaweicloud.com/product/cloudsite.html)。

