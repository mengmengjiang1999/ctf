**注：本文上半部和等保联系不是很密切，还是说一了些linux里细节一些的东西，所以有可能会浪费你生命中的好几分钟，同时我使用的是centos6。**

## 一、登录失败处理功能参数详解

**首先贴上我的上一篇文章：[等保测评主机安全：CentOS密码修改周期与登录失败处理](https://www.freebuf.com/articles/terminal/206959.html)，登录失败处理功能的上半段内容在这篇文章的下半部分，本篇文章主要说pam_tally2的参数所代表的的意思。**

 **在测评时，设计登录失败处理功能，就少不了要使用pam_tally2（centos6和之后的版本），那么就有必要明白这个模块各个参数（选项）的意义。**

而网上对于pam_tally2参数资料，不能说不对，但是总觉得不够详细和全面，所以写了这篇文章说明说明。

首先，先贴上常用的参数解释，保证来源部分不会出错，同时给出中文解释，大家可以对照着看：

![图片.png](https://image.3001.net/images/20190712/1562902802_5d28011250b2a.png!small)

### 1.1. deny

这个就不用多说了，登录失败次数一旦大于等于该数值，所登录的账号就会被锁定。

### 1.2. lock_time

这个比较不常见，好像一般都不怎么说这个参数，这个参数的意思就是你每一次登录失败后，在尚未达到deny所设置的次数时，会限制你登录的时间。

举个例子，如果你设置deny是3，lock_time为10。那么你第1次和第2次登录失败时，在10s内的登录是无效的，输入啥都不会让你登进去的。

另外当你达到了第3次登录失败后，该参数失效，由unlock_time来接管。

### 1.3. unlock_time

这个就很常见了，意思就是当你登录失败的次数大于等于deny所设置的数值时，账号锁定的时间，就不必多解释了吧？

### 1.4. magic_root

这个的意思也很简单，如果不包含这个参数，则哪怕是root也会增加失败计数，但注意，增加失败计数不代表root就会被锁定，这是两码事。

在tally2的源代码中表示如下（c语言）：

    
    
        if (!(opts->ctrl & OPT_MAGIC_ROOT) || getuid()) {
          /* magic_root doesn't change tally */
          tally.fail_cnt += inc;
    
          if (tally.fail_cnt == TALLY_HI) { /* Overflow *and* underflow. :) */
              tally.fail_cnt -= inc;
              pam_syslog(pamh, LOG_ALERT, "Tally %sflowed for user %s",
                     (inc<0)?"under":"over",user);
          }
        }
    

if (!(opts->ctrl & OPT_MAGIC_ROOT) ||
getuid())很好解释，就是当你传入的参数中有magic_root选项且为root用户时，整个表达式的值才为false，才不会去执行if内的语句，也就是增加失败计数：tally.fail_cnt
+= inc。

传入的参数中有magic_root选项，则!(opts->ctrl &
OPT_MAGIC_ROOT)部分的bool值为false是root用户，而getuid()的返回值是当前用户的uid，所以该部分为0，转为bool类型则为false，则此时||运算符两边皆为false，所以不会执行。

而在源代码的另外一处，tally_check函数中，有这样的代码：

    
    
       if ((opts->ctrl & OPT_MAGIC_ROOT) && getuid() == 0) {
          return PAM_SUCCESS;
        }
        /* magic_root skips tally check */
    

这个就更好解释了，如果存在magic_root参数，且是root账号，就不经过执行下面的代码，直接返回成功了。

那么如果是root账号，但没有设置magic_root参数呢？其实也不一定会对root账号进行锁定设置，请看下一个参数。

### 1.5. even_deny_root

意思就是说，有这个参数，只要达到了deny设定的值，root账号照样也会被锁定。

在tally_check函数中，如果是root账号，但没有设置magic_root参数，则代码会往下执行，其中有一个if判断如下：

    
    
     if (opts->deny != 0 &&                        /* deny==0 means no deny        */
            tally->fail_cnt > opts->deny &&           /* tally>deny means exceeded    */
            ((opts->ctrl & OPT_DENY_ROOT) || uid)) {  /* even_deny stops uid check    */
    

注意看((opts->ctrl & OPT_DENY_ROOT) ||
uid))，意思如果没有设置even_deny_root选项，且uid为0也就是root账号的情况下，if语句块的代码就不会执行。

同样反过来，只要设置even_deny_root选项，无论啥账号，都会执行if语句块的代码。
或者没有设置even_deny_root选项，但不是root账号，也会执行if语句块的代码。

插一句，在tally2源代码中，对传入选项的解析阶段，有这么一段：

    
    
          else if ( ! strcmp( *argv, "even_deny_root_account" ) ||
                    ! strcmp( *argv, "even_deny_root" ) ) {
    	log_phase_no_auth(pamh, phase, *argv);
            opts->ctrl |= OPT_DENY_ROOT;
          }
    

也就是说传入even_deny_root_account好像也是可以的，可能是为了兼容以前的版本什么的？

### 1.6. root_unlock_time

这个就是和even_deny_root配合使用的，如果root账号被锁定，则它所锁定的时间。

这里就有一个问题，如果只有even_deny_root选项，没有设置root_unlock_time选项，root账号会被锁定多久？

解释中好像没说，直接看tally2解析传入选项的源代码的倒数第二句：

    
    
     if (opts->root_unlock_time == -1)
    	opts->root_unlock_time = opts->unlock_time;
    

root_unlock_time的默认值是-1，所以如果发现你没有给它进行设置，在最后，它就会等于unlock_time。

反过来，如果只有root_unlock_time而没有even_deny_root，又会怎么样？

可以看tally2解析传入选项的源代码：

    
    
          else if ( ! strncmp( *argv, "root_unlock_time=", 17 ) ) {
    	log_phase_no_auth(pamh, phase, *argv);	
            if ( sscanf((*argv)+17,"%ld",&opts->root_unlock_time) != 1 ) {
              pam_syslog(pamh, LOG_ERR, "bad number supplied: %s", *argv);
              return PAM_AUTH_ERR;
            }
            opts->ctrl |= OPT_DENY_ROOT; /* even_deny_root implied */
          }
    

好像是如果传入了root_unlock_time且可以转化为数字的话，就相当于传入了even_deny_root参数。

啰嗦了这么多，应该把常用参数解释清楚了。

对于这些参数，如果光看网上搜的资料，发现有不清楚的地方，就应该直接去看man里面的解释。 如果解释里面写得也不够明白，那么就直接看代码。

无论怎么说，代码总是功能的直接体现，是不会产生困惑的。

## 二、双因素认证

这一部分没有特别明确的标准，所以仅为个人经验，而我又没多少经验，所以如果有错误请见谅。

### 2.1. 堡垒机

其实常用的的做法就是，通过堡垒机来管理服务器。 同时，堡垒机使用双因素认证，从而间接的达到了服务器的双因素认证。

但是首先，这种方式似乎不能被认为是认证：  
![图片.png](https://image.3001.net/images/20190712/1562903050_5d28020ab9cbf.png!small)

不过如果就算被认为是双因素认证，也有两点值得注意。

 **第一点**

堡垒机必须强制使用双因素认证方式，而不是任选一种方式进行登录。

 **第二点**

堡垒机所管理的服务器，必须对连接方式进行限制，通过防火墙或者网络设备什么的，确保只能通过堡垒机进行连接。否则，就算堡垒机强制使用双因素认证，但服务器还是能通过远程桌面或者ssh连上去，那堡垒机的双因素认证就意义不大了。

### 2.2. VPN

VPN方式和堡垒机有点像，vpn本身也可以使用双因素进行身份鉴别，比如SANGFOR SSL
VPN，就可以在控制台中进行设置（功能好像挺多的，可以做很多设置）：  
![图片.png](https://image.3001.net/images/20190712/1562903104_5d280240e36ce.png!small)

但关键的还是要看配置有没有做全面：

 **第一点**

只能通过vpn连接服务器，有些单位的内网直接可以用wifi连上，防火墙那也没对访问服务器远程端口的ip做出限制，只要连上wifi就能连服务器，那这种vpn的双因素认证就不能认为是服务器的双因素认证。

或者如果对访问远程端口的ip没有做出限制，但是没有内网wifi，要连内网就得拿网线跑去机房连接的话，感觉也算是做了限制。

 **第二点**

那自然就是登录vpn要强制使用双因素认证啦。

### 2.3. pam插件

另外一种比较双因素认证的方式，对于centos等linux系统，就是通过使用pam组件。

关于pam，请看[等保测评主机安全：CentOS密码修改周期与登录失败处理](https://www.freebuf.com/articles/terminal/206959.html)中的登录失败处理功能部分，里面对pam做了一个比较清晰的介绍。

不过这里不妨可以再说下，pam全名是可插拔认证模块，比如登录linux系统时，验证用户名密码其实就是通过调用pam的一个验证模块——pam_unix。

而这个模块干的事情，也就是提示你输入用户名和密码，然后应该是分别和passwd以及shadow文件进行对比，最后返回成功或失败。

所以，想实现双因素认证，比如“用户名/口令”+“手机短信”的认证方式，完全可以直接修改pam_unix模块（c语言），增加“手机短信”验证功能。

又或者增加一个自定义验证模块，里面使用手机短信验证，然后通过配置文件中的控制标记，让这个自定义的模块和pam_unix模块都成功才验证成功，也能实现效果。

至于具体有没有这样的模块?大家百度搜索centos 双因素认证即可，具体就不说了，网上的资料介绍得还是很清晰的。

### 2.4. ssh密钥方式登录

这个我也不知道是不是啊，但是我感觉似乎可以算是？

简单来说就是对于centos等linux系统，在ssh的配置文件中，禁掉用户名、密码登录方式，使用密钥（公钥/私钥）+私钥密码的方式进行登录。

网上资料如下：

    
    
    [root@host ~]$ ssh-keygen  <== 建立密钥对
    Generating public/private rsa key pair.
    Enter file in which to save the key (/root/.ssh/id_rsa): <== 按 Enter
    Created directory '/root/.ssh'.
    Enter passphrase (empty for no passphrase): <== 输入密钥锁码，或直接按 Enter 留空
    Enter same passphrase again: <== 再输入一遍密钥锁码
    Your identification has been saved in /root/.ssh/id_rsa. <== 私钥
    Your public key has been saved in /root/.ssh/id_rsa.pub. <== 公钥
    The key fingerprint is:
    0f:d3:e7:1a:1c:bd:5c:03:f1:19:f1:22:df:9b:cc:08 root@host
    

注意，在建立密钥对的时候是可以设置私钥的密码的。

这样，你进行登录的时候，比如使用xshell进行远程连接，用户名本来就需要输入，私钥也要提供，私钥的密码也要提供。

这样应该算是双因素了吧？

 ***本文原创作者：起于凡而非于凡，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

