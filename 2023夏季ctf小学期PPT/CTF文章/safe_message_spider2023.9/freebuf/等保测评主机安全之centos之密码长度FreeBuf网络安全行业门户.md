***本文原创作者：起于凡而非于凡，本文属FreeBuf原创奖励计划，未经许可禁止转载**  

 ** _注：本文和等保联系其实并不大，主要还是说一些linux里细节一些的东西，而且很有可能会浪费你生命中的好几分钟……_**

 **密码长度，作为等级保护主机测评项里中密码复杂度要求之一，是必须要查的。**

在《等级测评师初级教程》里，对于密码长度的设置指向了/etc/login.defs里的PASS_MIN_LEN字段。

    
    
    #  PASS_MIN_LEN    Minimum acceptable password length.
    
    PASS_MIN_LEN    5

简单明了，对新密码的长度最小值做出了限制。

不过，实际上这个参数是无效的，至少在centos6以及以上版本里，这个参数对新密码长度没有一点点的制约。

比如大家可以试一试，给`PASS_MIN_LEN  
`设一个值，再用 **非root账户** 去改改密码，看看对新密码长度有没有影响。甚至，还可以直接删除login.defs文件，试一试。

反正，我的测试结果是：这个参数没有起到作用。

结果是出来了，至于原因，我没找到，网上也没有相关的资料。或许该参数在centos以前的某个老版本里是有作用的，但随着版本更新，特别估计是开始使用`PAM认证机制`后，该参数就无效化了，仅仅作为一个迷惑人的参数放置在login.defs文件里。

实际上真正起作用的，是一个`pam`模块，具体点，也就是`pam_cracklib.so`模块。

`PAM认证机制`个人感觉就是一个模块化、组件化的机制，一些人把一些认证、验证以及其他功能实现好了，然后上层的应用去调用配置文件（接口），而配置文件呢再调用底层的实现，大概就是下图这个样子：

![Image](https://image.3001.net/images/20190604/15596462817766.png!small)所谓的应用程序，就包括在linux里使用的命令，好，回到密码长度这个话题。

修改密码时对于密码的一系列验证由`pam_cracklib.so`模块实现，那么谁去调用？那当然就是passwd了（修改密码的命令）。

passwd怎么调用的？是通过配置文件（接口）做到的。

在centos6以及以上版本中，这个配置文件就是`/etc/pam.d`中与passwd同名的文件，也就是`/etc/pam.d/passwd`。

顺便一提，`/etc/pam.d`中基本都是这类同名文件：

    
    
    [root@centos01 ~]# ls /etc/pam.d
    
    atd               fingerprint-auth-ac  password-auth      smtp            system-config-authentication
    
    authconfig        gdm                  password-auth-ac   smtp.postfix    system-config-date
    
    authconfig-gtk    gdm-autologin        polkit-1           smtp.sendmail   system-config-kdump
    
    authconfig-tui    gdm-fingerprint      poweroff           sshd            system-config-keyboard
    
    chfn              gdm-password         ppp                sshd~           system-config-network
    
    chsh              gnome-screensaver    reboot             ssh-keycat      system-config-network-cmd
    
    config-util       halt                 remote             su              system-config-users
    
    crond             ksu                  run_init           sudo            vmtoolsd
    
    cups              login                runuser            sudo-i          xserver
    
    cvs               login~               runuser-l          su-l
    
    dovecot           newrole              setup              system-auth
    
    eject             other                smartcard-auth     system-auth~
    
    fingerprint-auth  passwd               smartcard-auth-ac  system-auth-ac
      
    

`/etc/pam.d/passwd`的内容如下：

    
    
    [root@centos01 ~]# cat /etc/pam.d/passwd
    #%PAM-1.0
    auth       include    system-auth
    account    include    system-auth
    password   substack    system-auth
    -password   optional    pam_gnome_keyring.so  
    

对于配置文件，具有一定的规范，第一列代表模块类型，类型分为4种：

auth: 用来对用户的身份进行识别.如:提示用户输入密码,或判断用户是否为root

account:对帐号的各项属性进行检查.如:是否允许登录,是否达到最大用户数,或是root用户是否允许在这个终端登录等

session:这个模块用来定义用户登录前的,及用户退出后所要进行的操作.如:登录连接信息,用户数据的打开与关闭,挂载文件系统等.

passwd:使用用户信息来更新.如:修改用户密码.

这里，由于是修改密码，所以会使用passwd类型的模块。

配置文件是可以互相调用的，passwd文件里的第三行  

    
    
    password   substack    system-auth

就调用了`system-auth`配置文件。

这里的substack和include都是引用的意思，只是稍微有点区别（具体百度就知道了）。

然后这个`system-auth`文件也在`/etc/pam.d`的文件夹中，内容为

    
    
    [root@centos01 ~]# cat /etc/pam.d/system-auth
    
    #%PAM-1.0
    
    # This file is auto-generated.
    
    # User changes will be destroyed the next time authconfig is run.
    
    auth        required      pam_env.so
    
    auth        sufficient    pam_fprintd.so
    
    auth        sufficient    pam_unix.so nullok try_first_pass
    
    auth        requisite     pam_succeed_if.so uid >= 500 quiet
    
    auth        required      pam_deny.so
    
    account     required      pam_unix.so
    
    account     sufficient    pam_localuser.so
    
    account     sufficient    pam_succeed_if.so uid < 500 quiet
    
    account     required      pam_permit.so
    
    password    requisite     pam_cracklib.so try_first_pass retry=3 type=
    
    password    sufficient    pam_unix.so sha512 shadow nullok try_first_pass use_authtok
    
    password    required      pam_deny.so
    
    session     optional      pam_keyinit.so revoke
    
    session     required      pam_limits.so
    
    session     [success=1 default=ignore] pam_succeed_if.so service in crond quiet use_uid
    
    session     required      pam_unix.so
    

其中，具体被引用（使用）到的是：

    
    
    password    requisite     pam_cracklib.so try_first_pass retry=3 type=
    
    password    sufficient    pam_unix.so sha512 shadow nullok try_first_pass use_authtok
    
    password    required      pam_deny.so
    

`pam_cracklib.so`模块有不少参数，主要常用的有这几个（摘抄于网上）：

    
    
    minlen=N：最小密码长度。
    dcredit=N：当N>=0时，N代表新密码最多可以有多少个阿拉伯数字。当N<0时，N代表新密码最少要有多少个阿拉伯数字。
    ucredit=N：和dcredit差不多，但是这里说的是大写字母。
    lcredit=N：和dcredit差不多，但是这里说的是小写字母。
    ocredit=N：和dcredit差不多，但是这里说的是特殊字符。
    

似乎到这里就差不多了，因为都找到了实际控制新密码最小长度的地方了，但其实还没完呢。

因为网上关于pam_cracklib模块中这几个参数的解释，可以说，基本上都是不准确的。

那当然，我都这么说了，我这里自然会给一个准确的解释（我觉得这应该是 **全网唯一清楚且准确的中文解释了**
，因为我自己在查找资料的时候完全没有搜到，有些资料比较接近，但实际还是没说清楚）。

准确的解释来man命令输出的说明文档：<https://linux.die.net/man/8/pam_cracklib>

其实写得还是比较清楚的，但是还是有点抽象，我稍微解释下。

minlen确实有最小长度的意思，但是当dcredit、ucredit、lcredit、ocredit的值（N）大于等于零的时候，情况就不同了。

N大于零的时候，完全不是网上说的“最多可以有多少个数字或大小写字母或特殊字符”的意思，而是计算长度的时候会有变化。

比如ocredit（特殊字符）的值是2的时候，就代表有最多有2个特殊字符的长度额外能加1。

当你设置的密码是：@#￥，它的长度被算作是5，而不是3。因为有2个特殊字符的长度被看做是2（额外加了个1），而第3个特殊字符没有此类变化，长度仍被视作是1，所以总共长度时（2+2）+1=5。

所以，如果ocredit的值是4，那么@#￥%&的长度就是（4+4）+1=9。

其余的大小写字母和数字的值大于零时，也是这个意思。而他们的默认值都是1，也就是会有1个字符的长度额外加1。

所以如果你什么都不设置，就设置minlen=8的话，理论上你的新密码只要4类字符都包含，那么4个字符就够了，比如：1Aa@

当然，如果你真这么设置，实际上是不行的，因为除了minlen对长度有限制，cracklib内部有代码对其有限制，而且优先级高于minlen。

解释如下：Note that there is a pair of length limits in Cracklib itself, a "way too
short" limit of 4 which is hard coded in and a defined limit (6) that will be
checked without reference to minlen。

大概的代码如下：

    
    
    #define MINLEN 6
    　　
    　　char *
    　　FascistLook(pwp, instring)
    　　 PWDICT *pwp;
    　　 char *instring;
    　　{
    　　 int ii;
    　　 char *ptr;
    　　 char *jptr;
    　　 char junk[STRINGSIZE];
    　　 char *password;
    　　 char rpassword[STRINGSIZE];
    　　 int32 notfound;
    　　
    　　 notfound = PW_WORDS(pwp);
    　　 /* already truncated if from FascistCheck() */
    　　 /* but pretend it wasn't ... */
    　　 strncpy(rpassword, instring, TRUNCSTRINGSIZE);
    　　 rpassword[TRUNCSTRINGSIZE - 1] = '';
    　　 password = rpassword;
    　　
    　　 if (strlen(password) < 4)
    　　 {
    　　 return ("it's WAY too short");
    　　 }
    　　 if (strlen(password) < MINLEN)
    　　 {
    　　 return ("it is too short");
    　　 }
    　　
    　　 jptr = junk;
    　　 *jptr = '';
    　　
    　　 for (ii = 0; ii < STRINGSIZE && password[ii]; ii++)
    　　 {
    　　 if (!strchr(junk, password[ii]))
    　　 {
    　　 *(jptr++) = password[ii];
    　　 *jptr = '';
    　　 }
    　　 }
    　　
    　　 if (strlen(junk) < MIND

所以说，如果长度小于4，会输出it's WAY too short，如果大于4小于6，会输出it is too short。

当然，超过了6之后，就是由minlen控制了。

嗯……扯了这么久，大概把修改密码时密码长度的事情说完了。

正如前言所说，和等保关系不大。

不过如果在检查的时候看到PASS_MIN_LEN 8 的时候，是给这1分还是不给分呢？

我想大家在心里都是有答案的，嘿嘿。

另外，这个pam认证机制还是经常会碰到的，比如在登录失败处理功能中，是用pam_tally或者pam_tally2模块去实现。

所以聪明的你一定知道具体应该去哪个配置文件里查看是否进行设置了。

比如远程ssh连接的登录失败处理功能，自然就是去pam.d文件夹中的sshd文件查看，sshd又引用passwd-auth，所这两个文件都可以实现失败处理（所以初级教程让你去system-auth里查看配置，其实是管不了ssh远程连接登录的，实际上管的是本地tty终端登录）。

而本地tty终端登录，也就是使用login命令，是去pam.d文件夹中的login文件查看，login则引用system-auth文件，同理，这两个文件都可以实现。

至于su命令和图形化界面窗口登录（比如gdm-password）也是按照这种方法去查看有效配置文件在哪儿。

就先写到这了，以后有空再写一写其他的。  

 ***本文原创作者：起于凡而非于凡，本文属FreeBuf原创奖励计划，未经许可禁止转载**

