**作者：Ethan@知道创宇404实验室**  
**时间：2019年8月21日**  
**英文版本:<https://paper.seebug.org/1020/>**

### 漏洞概述

Webmin是一个基于Web的界面，用于Unix的系统管理。使用任何支持表和表单的浏览器，可以设置用户帐户，Apache，DNS，文件共享等。

2019年8月10日，在pentest上发布了Webmin CVE-2019-15107远程代码执行漏洞。

该漏洞由于`password_change.cgi`文件在重置密码功能中存在一个代码执行漏洞，该漏洞允许恶意第三方在缺少输入验证的情况下而执行恶意代码，后经知道创宇404实验室发现，该漏洞的存在实则是sourceforge上某些版本的安装包和源码被植入了后门导致的。

### 漏洞复现

官方给的漏洞影响版本为Webmin<=1.920，于是当晚我使用了Webmin 1.920的版本进行的测试。

在1.920版本中漏洞的触发需要开启密码重置功能，`“Webmin-> Webmin Configuration->
Authentication”`下把允许用户使用旧密码设置新密码的选项给选上，并保存！

![](https://images.seebug.org/content/images/2019/08/21/1566374306000-p6.png-w331s)

Webmin重启后，查看webmin的配置文件，可以发现`passwd_mode`的值已经从0变为了2

![](https://images.seebug.org/content/images/2019/08/21/1566374306000-p8.png-w331s)

然后在密码修改处执行抓包，然后在old参数上加上`|ifconfig`

![](https://images.seebug.org/content/images/2019/08/21/1566374306000-p21.png-w331s)

发现成功执行了命令！

想着换个用户试试吧，23333，结果出现下面的情况！

![](https://images.seebug.org/content/images/2019/08/21/1566374307000-p20.png-w331s)

为什么换个root用户就不行了，这里的root用户是Linux系统的root用户，我登陆使用的就是这个用户。。

我再随便使用个用户试试？

![](https://images.seebug.org/content/images/2019/08/21/1566374307000-p22.png-w331s)

经测试用户为空也可以，用户为webmin用户也可以，其创建方式如下：

![](https://images.seebug.org/content/images/2019/08/21/1566374307000-p19.png-w331s)

其中root是Linux系统账户，认证方式为`Unix authenticaton`，ethan账户是自己创建的webmin 账户，认证方式无。

这样问题就来了，为什么会有这样的区别？这就不得不开启一个perl菜鸟审计perl代码的道路，感谢@Longofo的帮助！

### 漏洞点分析

首先在`password_change.cgi`的第12行，我们可以得知想触发漏洞必须`passwd_mode=2`，也就必须开启密码重置功能。否则就会显示Password
changing is not enabled!

    
    
    $miniserv{'passwd_mode'} == 2 || die "Password changing is not enabled!";

接着分析`password_change.cgi`的12行到31行，如下：

    
    
    # Is this a Webmin user?
    if (&foreign_check("acl")) {
        &foreign_require("acl", "acl-lib.pl");
        ($wuser) = grep { $_->{'name'} eq $in{'user'} } &acl::list_users();
        if ($wuser->{'pass'} eq 'x') {
            # A Webmin user, but using Unix authentication
            $wuser = undef;
            }
        elsif ($wuser->{'pass'} eq '*LK*' ||
               $wuser->{'pass'} =~ /^\!/) {
            &pass_error("Webmin users with locked accounts cannot change ".
                        "their passwords!");
            }
        }

从注释看，这段代码主要判断是不是webmin user。并且请求了一个acl-lib.pl，看名字就知道是功能性文件，功能应该就是访问控制之类的。在第21~22行的作用是获取请求中的user，并且判断是否属于Webmin
user！但是这个x让我不知所然，为什么把`$wuser`和`x`这个值比较呢？。于是我把`acl::list_users()`的值尝试着打印出来！

![](https://images.seebug.org/content/images/2019/08/21/1566374307000-p23.png-w331s)

返回如下数据：

![](https://images.seebug.org/content/images/2019/08/21/1566374308000-p14.png-w331s)

![](https://images.seebug.org/content/images/2019/08/21/1566374308000-p24.png-w331s)

通过返回的数据，我们可以知道root用户并且使用`Unix
authenticaton`设置(默认)的pass的值为`x`，而我自己创建没有选择认证方式的用户，`pass`的值为一串加密的字符串。也就是说如果我们传进的`user`是系统用户登陆且认证方式为`Unix
authenticaton`的账户时，`$wuser` 的值会被赋值为`undef`。

在if条件语句外，我们把`$wuser`的值给打印下

![](https://images.seebug.org/content/images/2019/08/21/1566374308000-p28.png-w331s)

![](https://images.seebug.org/content/images/2019/08/21/1566374308000-p27.png-w331s)

在`if`条件语句里面把`$wuser` 的值打印出来印证一下

![](https://images.seebug.org/content/images/2019/08/21/1566374308000-p26.png-w331s)

![](https://images.seebug.org/content/images/2019/08/21/1566374308000-p25.png-w331s)

而在`perl`语言中`undef`是变量未初始化时的默认值，一般情况下，将其当作空或0就好了，在需要作为数值的时候，`undef`代表的就是0，需要字符串的时候，`undef`就是空字符串。这里应该是对系统用户密码的修改和其它用户进行了区分。

由我们上面的分析可知，在用户为root的情况下`$wuser`的值为`undef`。

    
    
    if ($wuser) {
        # Update Webmin user's password
        $enc = &acl::encrypt_password($in{'old'}, $wuser->{'pass'});
        $enc eq $wuser->{'pass'} || &pass_error($text{'password_eold'},qx/$in{'old'}/);
        $perr = &acl::check_password_restrictions($in{'user'}, $in{'new1'});
        $perr && &pass_error(&text('password_enewpass', $perr));
        $wuser->{'pass'} = &acl::encrypt_password($in{'new1'});
        $wuser->{'temppass'} = 0;
        &acl::modify_user($wuser->{'name'}, $wuser);
        &reload_miniserv();
        }

也就是说如果传入的`user`为系统用户无法进入第37行的`if`条件语句，从而无法执行第40行`qx/...../`的命令执行代码。当我们传入的用户为空或者不存在时，`$wuser`的值为`{}`，但是会进入`if`条件语句

![](https://images.seebug.org/content/images/2019/08/21/1566374308000-p29.png-w331s)

关于命令执行是否需要`|`，我们通过分析第207行到217行的`pass_error`可知，不需要`|`，亦可进行命令执行回显。

    
    
    sub pass_error
    {
    &header(undef, undef, undef, undef, 1, 1);
    print &ui_hr();
    
    print "<center><h3>",$text{'password_err'}," : ",@_,"</h3></center>\n";
    
    print &ui_hr();
    &footer();
    exit;
    }

![](https://images.seebug.org/content/images/2019/08/21/1566374308000-p31.png-w331s)

### 另有蹊跷

继续探究的原因是觉得`qx/..../`的蹊跷，因为官方给的修补是直接删除了`qx/..../`如图：

![](https://images.seebug.org/content/images/2019/08/21/1566374308000-p39.png-w331s)

是不是越看越感觉这个漏洞是被"加上去的"，在Github上下载的1.920版本并无`qx/..../`，啊咧咧，一头雾水啊。。。通过`git log
-p`命令并未发现与`qx/..../`相关的记录。而在sourceforge上下载的源码和安装包却有漏洞代码。后门？

2012年在网站SourceForge韩国CDN节点疑似被入侵，热门下载资源phpMyadmin被植入后门。在Seebug上有收录：<https://www.seebug.org/vuldb/ssvid-60402>

![](https://images.seebug.org/content/images/2019/08/21/1566374308000-p40.png-w331s)

在Github上找到另外一些讯息，<https://github.com/webmin/webmin/issues/947>

![](https://images.seebug.org/content/images/2019/08/21/1566374308000-p42.png-w331s)

在1.890版本中，同样存在漏洞代码，这一次简直是赤裸裸的后门。。。

我从sourceforge下载1.890版本，进行了探究。漏洞点如下：

![](https://images.seebug.org/content/images/2019/08/21/1566374308000-p43.png-w331s)

通过分析我们可以得知，这个漏洞点的触发只需要传一个`expired`参数执行命令即可。不需要之前的`passwd_mode=2`的必要条件。

![](https://images.seebug.org/content/images/2019/08/21/1566374309000-p34.png-w331s)

也就是说，在1.890版本中漏洞的触发不需要任何依赖。是代码疏漏还是恶意后门？

### 验证想法

这里我们通过更直观的方式来验证，通过把Github和sourceforge的源码下载下来，然后进行diff

Webmin 1.920版本的password_change.cgi文件

![](https://images.seebug.org/content/images/2019/08/21/1566374309000-p45.png-w331s)

Webmin 1.890版本的password_change.cgi文件

![](https://images.seebug.org/content/images/2019/08/21/1566374309000-p44.png-w331s)

通过Github和sourceforge的文件对比，我们可以发现，sourceforge的代码明显存在问题，极有可能是被植入了后门。

后经验证确认，只有sourceforge的代码和安装包存在后门漏洞。各版本的情况如下：

![](https://images.seebug.org/content/images/2019/08/21/1566374309000-p46.png-w331s)

其中以1.890版本的后门漏洞触发依赖最小，危害最大！猜测这应该是最初始的后门，后来植入后门的时候没有考虑到代码逻辑的问题，导致漏洞触发受到了限制！

### 漏洞修补

  * 直接升级到1.930版本

  * 临时修补方案，可以定位漏洞代码所在的行，然后剔除，下图为1.920版本：

![](https://images.seebug.org/content/images/2019/08/21/1566374309000-p47.png-w331s)

下图为1.890版本：

![](https://images.seebug.org/content/images/2019/08/21/1566374309000-p48.png-w331s)

将所示标注替换为`$miniserv{'passwd_mode'} == 2 || die "Password changing is not
enabled!";`即可，替换的代码为Github无后门代码。

### 事后感想

本来正常的一次应急没想到，发展成了对后门文件的探究。果然是生活不息，搞事不止啊！感谢@Longofo，帮忙测试大量文件和代码。黑哥也在medium上发表了The
stories behind Webmin
CVE-2019–15107这篇文章来描述后门发现的过程：<https://medium.com/@80vul/the-stories-behind-cve-2012-5159-198eaad2449d>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1019/>

