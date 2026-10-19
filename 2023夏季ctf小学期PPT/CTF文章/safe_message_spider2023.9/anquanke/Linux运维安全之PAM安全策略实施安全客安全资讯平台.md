# Linux运维安全之PAM安全策略实施

阅读量 **261490**

发布时间 : 2018-09-29 18:30:02

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t019bba3bd7ee61846c.jpg)

> 可插拔认证模块PAM-Pluggable Authentication
> Modules是一套共享库，用来对应用程序或服务的使用进行认证授权以及提供其他安全服务。起初它是由美国Sun公司为Solaris操作系统开发的，后来，很多操作系统都实现了对它的支持，Red
> hat 5.0后的发行版在默认基础安装包中都包括了PAM。
>
> PAM的优点是它的实用性和灵活性，对于Linux服务器上的应用程序或服务，可以根据需求实施各种安全策略，甚至可以自己编写认证模块进行调用。
>
> 本期安仔课堂，ISEC实验室的张老师为大家详解PAM。

## 一、PAM的认证机制

图1

当User访问一个Service或者Program，应用程序需要进行认证服务，会根据自身定义认证的PAM配置文件来调用PAM相关模块进行验证，最后将验证结果返回给应用程序，应用程序再产生相应的动作。

## 二、PAM的配置

PAM主要的文件为 /usr/lib/security或
/usr/lib64/security目录下的pam_*.so模块文件，以及/etc/pam.d目录下的特定应用程序的PAM配置文件。

![](https://p4.ssl.qhimg.com/t016b502b48f50adfae.png)

图2

![](https://p4.ssl.qhimg.com/t01f80481a4d25064c2.png)

图3

以passwd为例，我们看一下当执行passwd时，PAM进行了哪些处理。查看passwd的PAM配置文件：

![](https://p1.ssl.qhimg.com/t018521639467ed14c9.png)

图4

PAM的配置文件以如下空白分隔的字段组成：

module_type control_flag module_path module_options

module_type:为服务指定模块类型。有效模块类型是 auth、account、session 或
password，给定的模块将提供对一个或多个模块类型的支持。

control_flag:为模块指定堆栈行为。受支持的控制标志是 required、requisite、sufficient 或 optional。

module_path:指定为服务装入的模块。

module_option:指定能够发送到服务模块的空格划定的选项列表。该字段的值取决于在 module_path
字段中定义的模块支持的选项，此字段是可选的。

passwd的PAM配置应用了system-auth配置：

![](https://p1.ssl.qhimg.com/t012ccaa9294fd95a03.png)

图5

pam_env模块将根据管理员在/etc/security/pam_env.conf中设置的内容设置环境变量，pam_faildelay模块设置了失败delay时间为2s。

pam_fprintd模块是进行指纹验证，由于控制标志为sufficient，验证失败并不影响继续验证。Pam_unix
nullok参数允许空密码，try_first_pass使用先前模块的密码进习惯验证。

pam_succeed_if设置了当uid大于1000时，不记录登录信息到系统日志中。当前面模块没有验证成功，最后的pam_deny模块将直接拒绝
OTHER的默认动作。关于PAM模块的详细信息可以通过man 模块名进行查询：

![](https://p1.ssl.qhimg.com/t01da025f42d4e749a1.png)

图6

## 三、PAM后门

通过在pam_unix下的pam_unix_auth.c源码中添加判断条件，使得_unix_verify_password返回值为PAM_SUCCESS。这样就可以在用系统存在的任意用户名与设置的后门密码进行登录。

首先查看服务器PAM的版本信息：

![](https://p5.ssl.qhimg.com/t012326cb8708ffe3d4.png)

图7

安装之前需要先安装flex flex-deve，否则在64位系统上编译PAM的时候会遇到yywrap()函数未定义错误。

![](https://p1.ssl.qhimg.com/t0179ae6c27412a5536.png)

图8

下载指定版本的PAM进行修改然后编译成so文件，再复制到系统pam模块目录下替换原文件，这样就造好后门了。

关于PAM后门的排查：

如果添加的是自定义的PAM模块，那么只要查询模块所属的包就可以发现PAM后门：

  
图9

对于通过修改原PAM模块，可以通过计算MD5值与原来进行diff

图10

![](https://p5.ssl.qhimg.com/t012bf2c808d0e68fdc.png)

图11

## 四、PAM实现双因子认证

买了台ECS/VPS，设置密码太复杂了不方便记住也不方便输入，用证书登录得y用证书也不方便。何不设置个弱口令外加个动态验证码？

双因子可以使用Google动态令牌，也可以使用Duo Unix，Duo Unix支持App动态口令、短信口令以及电话。

首先需要到DUO官网注册账号，新建一个UNIX Application保护应用，获得Integration key、Secret key、API
hostname。

![](https://p5.ssl.qhimg.com/t012cd764cb2a536517.png)

图12

然后安装pam_duo

![](https://p4.ssl.qhimg.com/t0141c2a30913df71df.png)

图13

安装后修改配置文件/etc/duo/pam_duo.conf

![](https://p4.ssl.qhimg.com/t01030d289019e37a6f.png)

图14

然后在配置文件中添加该模块，SSH需要在配置文件开启USE PAM以及USE DNS

![](https://p1.ssl.qhimg.com/t01f9e84b3ad8a8601b.png)

图15

接着登录服务器，这时会出现一个url让你进行注册

![](https://p4.ssl.qhimg.com/t01ef4e569c3573f17a.png)

图16

访问url绑定注册完成后再次登录时就可以选择动态验证码了

![](https://p3.ssl.qhimg.com/t0109c5755dad645e91.png)

图17

## 五、PAM_DUO源码浅析

DUO_UNIX项目地址：<https://github.com/duosecurity/duo_unix>

PAM_DUO认证中主要就是pam_sm_authenticate函数的处理,处理时首先会读取DUO的配置文件，之后检测是否配置了其他config文件，有则更新conf的值。此外，也将检测是否配置了debug参数。

![](https://p2.ssl.qhimg.com/t01f9ea4d1d9ddf494f.png)

图19

![](https://p2.ssl.qhimg.com/t01323998d5adcaa958.png)

图20

然后调用duo_parse_config检查配置文件的读写权限，当返回值为-2时抛出错误“config文件应仅root可读”，当返回值为-1时抛出文件不可打开错误：

![](https://p1.ssl.qhimg.com/t0119e631e472af71cd.png)

图21

![](https://p0.ssl.qhimg.com/t014cbd0d3377e8efbe.png)

图22

然后检查是否开启fips_mode：

![](https://p1.ssl.qhimg.com/t01fcf61e9f99f040aa.png)

图23

调用pam_get_user获取认证用户信息，检查用户密码信息：

![](https://p5.ssl.qhimg.com/t01c9bb33d4b2fbf2e8.png)

图24

对于SSH服务，关闭增量状态信息提示：

![](https://p4.ssl.qhimg.com/t0156d43ecef3f07e0b.png)

图25

调用duo_check_groups检查认证用户是否是否在DUO认证的配置组中：

![](https://p2.ssl.qhimg.com/t018526eb996164a46e.png)

图26

检查获取用户/etc/passwd的GECOS信息并进行转换：

![](https://p2.ssl.qhimg.com/t01d97505f609a03bad.png)

图27

调用duo_local_ip解析本机ip地址：

![](https://p3.ssl.qhimg.com/t01a315fbda009fc9b0.png)

图28

这边开始进行DUO认证过程。使用pam_duo.conf配置的ikey、skey、apihost调用DUO
API接口，检测API接口连接，当处理错误返回DUO服务错误：

![](https://p1.ssl.qhimg.com/t01ae5a71d34e176a55.png)

图29

接着调用duo_login进行登录，在duo_login函数中会POST一个BOSN格式的认证信息到服务器，当返回错误为NULL则认证成功。

![](https://p2.ssl.qhimg.com/t01c8dcbd2c35fbb44f.png)

图30

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **安胜ANSCEN** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/160999](/post/id/160999)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [linux](/tag/linux)
  * [PAM](/tag/PAM)

 **+1** __1赞

 __收藏

![](https://p5.ssl.qhimg.com/t01d62256b77945b669.png) 安胜ANSCEN

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

