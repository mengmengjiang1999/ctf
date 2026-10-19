**注：本文和等保联系不是很密切，还是说一了些linux里细节一些的东西，所以有可能会浪费你生命中的好几分钟，同时我使用的是centos6。**

## 一、密码修改周期策略

首先贴上我的上一篇文章，和本篇有些关联，大家有兴趣可以去看一看：[等保测评主机安全之centos之密码长度](https://www.freebuf.com/articles/rookie/205077.html)。

在《等级测评师初级教程》里说/etc/login.defs是登录程序的配置文件，同时说：

>
> 由于该文件里的配置对root用户无效，如果/etc/shadow文件里有相同的选项，则以/etc/shadow里的设置为准，也就是说/etc/shadow的配置优先级高于/etc/login.defs。

说实话，我没看懂这个因果关系，login.defs和shadow本质上就不是一个优先级的关系。

在shadow文件中，存有用户的密码和一系列的字段，其中包括对用户的上一次修改密码的日期、下一次需要修改密码的日期等等，这些内容《等级测评师初级教程》说得比较清楚，我就直接截图了：

![图片.png](https://image.3001.net/images/20190627/1561564878_5d1396ced80bf.png!small)![图片.png](https://image.3001.net/images/20190627/1561564889_5d1396d910c70.png!small)

其实这里面就说得很清楚了，对于“两次修改口令间隔最少的天数”、“两次修改口令间隔最多的天数”、“提前多少天警告用户口令将过期”这三个字段，其实都是当你添加用户时，从login.defs里读取相关配置项，然后生成相应的值放置在shadow文件的相关字段中，而真正生效的实际上只是shadow文件存储的这些字段。

所以login.defs能够规定你添加的新用户的相关策略，本质上就是一个“策略生成文件”或“默认策略生成文件”，里面的配置项本身并不能对当前用户起什么效果，实际生效的策略比如密码更换周期策略是由shadow相关字段值决定的。

所以书中所谓的/etc/shadow的配置优先级高于/etc/login.defs这句话，虽然结果是正确的，但是描述却并不准确，因为本质就不是啥优先级的关系。

顺便说一句，shadow第七字段和第八字段在login.defs文件中是没有相关定义的，所以当然这两个字段也不是从login.defs中读取生成的，实际上是从/etc/defualt/useradd文件中读取的，当然此文件还有一些其他的配置项，这里就不多说了。

其实，做两个简答的实验即可证明，比如用chage命令修改某用户的密码更换策略，你会发现该用户在shadow文件中的相关字段值也随之发生改变。而你跑去修改login.defs中的密码更换策略，你再用chage
-l 用户名去查询某用户的密码更换策略或去查看shadow文件，你会发现是不会有什么变化的。

所以从这一点可以得知，如果较真的话，在进行检查时，仅仅按照《等级测评师初级教程》的方法去查询login.defs中的值那其实远远不够的。

如果login.defs文件中的配置项符合要求，不代表现存用户的密码更换策略就符合要求（因为login.defs仅仅是策略生成文件，实际生效的策略在shadow那呢，两者并不肯定相等，比如可以用chage命令对shadow进行修改），仅能代表这个系统新添加的用户的密码更换策略会符合要求。

所以实际应该连同shadow文件一起查看，嗯，有两种方法，一种是直接去看shadow文件，不过这种格式稍微有点不友好。所以另一种就是用chage -l
用户名的方式查看，内容容易理解：

    
    
    [root@centos01 ~]# chage -l root
    Last password change					: Mar 11, 2019
    Password expires					: never
    Password inactive					: never
    Account expires						: never
    Minimum number of days between password change		: 0
    Maximum number of days between password change		: 99999
    Number of days of warning before password expires	: 7
    
    

这里插句话，我实际上还遇上过另外一种情况，但这主要是对windows系统而言，就是windows系统策略中的密码更换策略符合要求（密码最长使用期限：40天），但是对方上次修改密码却在两年前（用net
user用户名的命令可以看到）

因为，这个策略的强制性真正起效的时刻我猜应该是当你重新登录这个账户时，也就是说，就算你一直没改密码，就算超过了期限，但只要你不退出登录，你就根本不用搭理这个策略，你也并不会被直接强制登出。linux应该也是这样，因为将密码过期时间设置在以前的时间，也并不会把我强制登出。而对于承载业务的服务器，极有可能长时间不重启。

而windows和linux不同之处在于，windows系统一般使用远程桌面进行远程管理时，它的默认设置为断开会话但不会结束会话：  
![图片.png](https://image.3001.net/images/20190627/1561564951_5d13971757e89.png!small)也就是说会话虽然断开，但是这个用户其实仍然处于登录状态，会话并没有结束。用远程桌面进行登录时，你输入用户名、密码只是为连接这个会话，而不是连接会话再在系统中进行登录，所以可以实现长时间不改密码。

linux则不同，用ssh连接，每次应该都要在系统中重新登录，因为每次断开会话后，会话实际就结束了。

## 二、登录失败处理功能

一般来说这个测评项有两个内容，一个是账户登录多次后进行锁定，另一个就是长时间不进行活动就将之登出。

### 2.1. 账户锁定策略

嗯~《等级测评师初级教程》让我们直接去查找/etc/pam.d/system-auth，其实这是不够全面的。  
在[等保测评主机安全之centos之密码长度](https://www.freebuf.com/articles/rookie/205077.html)中我就有说过，除了比较老的centos版本，现在都是使用pam认证机制，pam认证机制大概是什么样，看上面的文章即可。

具体到登录验证这一块，linux至少有3种登录方式：

> 1.本地tty登录，这里是使用login命令，所以从而调用/etc/pam.d/login配置文件，最终调用底层的组件进行密码验证等；
>
> 2.本地图形化界面，比如我用gdm，那么我在图形化登录界面时，就会调用/etc/pam.d/gdm配置文件；
>
> 3.ssh远程登录，就会调用/etc/pam.d/sshd配置文件。

然后再看看这三个配置文件的内容：

 **/etc/pam.d/login**

    
    
    #%PAM-1.0
    auth [user_unknown=ignore success=ok ignore=ignore default=bad] pam_securetty.so
    auth       include      system-auth
    account    required     pam_nologin.so
    account    include      system-auth
    password   include      system-auth
    # 3. pam_selinux.so close should be the first session rule
    #session    required     pam_selinux.so close
    session    required     pam_loginuid.so
    session    optional     pam_console.so
    # 4. pam_selinux.so open should only be followed by sessions to be executed in the user context
    session    required     pam_selinux.so open
    session    required     pam_namespace.so
    session    optional     pam_keyinit.so force revoke
    session    include      system-auth
    -session   optional     pam_ck_connector.sozz
    

**/etc/pam.d/gdm**

    
    
    #%PAM-1.0
    auth     [success=done ignore=ignore default=bad] pam_selinux_permit.so
    auth       required    pam_succeed_if.so user != root quiet
    auth       required    pam_env.so
    auth       substack    system-auth
    auth       optional    pam_gnome_keyring.so
    account    required    pam_nologin.so
    account    include     system-auth
    password   include     system-auth
    session    required    pam_selinux.so close
    session    required    pam_loginuid.so
    session    optional    pam_console.so
    session    required    pam_selinux.so open
    session    optional    pam_keyinit.so force revoke
    session    required    pam_namespace.so
    session    optional    pam_gnome_keyring.so auto_start
    session    include     system-auth
    

**/etc/pam.d/sshd**

    
    
    #%PAM-1.0
    auth	   required	pam_sepermit.so
    auth       include      password-auth
    account    required     pam_nologin.so
    
    account    include      password-auth
    password   include      password-auth
    # 3. pam_selinux.so close should be the first session rule
    session    required     pam_selinux.so close
    session    required     pam_loginuid.so
    # 4. pam_selinux.so open should only be followed by sessions to be executed in the user context
    session    required     pam_selinux.so open env_params
    session    optional     pam_keyinit.so force revoke
    session    include      password-auth
    

可以看到这三个配置文件使用include或substack又引用了其他的配置文件，具体下来则是：

> 1.login引用system-auth
>
> 2.gdm引用system-auth
>
> 3.sshd引用password-auth  
>

所以，如果你要用pam_tally2组件（书里说的pam_tally组件过老，至少在centos6开始就不适用了）进行登录锁定策略设置，那么如果仅仅放置在system-auth文件中，实际上就只对本地tty和本地图形化界面登录方式进行了限制，虽然这也是一种防护，但是我想更多的人都是用ssh远程连接的吧？要攻击也是先从远程连接下手吧？

如果别人都能跑到你的机房去多次尝试登录或者进行攻击，那？？？？？？

另外，这个策略语句究竟放置在配置文件中的哪个位置，会对是否生效造成影响，网上的回答往往就是说一句，把账号锁定策略放在最上面就没了，虽然效果是有的，但是却不知其所以然。

以system-auth文件进行举例：

    
    
    #%PAM-1.0
    # 5. This file is auto-generated.
    # 6. User changes will be destroyed the next time authconfig is run.
    auth        required      pam_env.so
    auth        sufficient    pam_fprintd.so
    auth        sufficient    pam_unix.so nullok try_first_pass
    auth        requisite     pam_succeed_if.so uid >= 500 quiet
    auth        required      pam_deny.so
    
    account     required      pam_unix.so
    account     sufficient    pam_localuser.so
    account     sufficient    pam_succeed_if.so uid < 500 quiet
    account     required      pam_permit.so
    
    password    requisite     pam_cracklib.so try_first_pass retry=300 type= minlen=8 minclass=4 enforce_for_root
    password    sufficient    pam_unix.so sha512 shadow nullok try_first_pass use_authtok
    password    required      pam_deny.so
    
    session     optional      pam_keyinit.so revoke
    session     required      pam_limits.so
    session     [success=1 default=ignore] pam_succeed_if.so service in crond quiet use_uid
    session     required      pam_unix.so
    

说明pam的资料很多，我这里只是不准确的大致描述下。

auth、account、password、session，auth是一个标识符，说明要干的事情，auth处理登录时验证方面的事，account、password、session和登录时验证没啥关系，比如password是处理更改密码时的事情。

这里是一些猜测（毕竟没有直接去看源代码）：

然后呢，调用配置文件里的组件时，是顺序往下调用的，但是每次调用应该是一个类型一个类型的调用的（一共4个类型嘛），所以语句的顺序应该指的是同一个类型的语句中的相对顺序。

比如登录验证的时候，至少犯不着调用password这个类型吧？而具体调用的方式我猜应该是用字符串查找某个类型的行，比如我就要验证功能的话，我就只找以auth开头的行，而其余类型的行都不搭理。

所以如果你添加一个auth语句，你放在auth类型行的最后一行的下一行，和直接放在整个配置文件的最后一行应该没啥区别，都是auth类型行的最后一行。

比如我这么改：

    
    
    #%PAM-1.0
    # 7. This file is auto-generated.
    # 8. User changes will be destroyed the next time authconfig is run.
    auth        required      pam_env.so
    auth        sufficient    pam_fprintd.so
    
    
    account     required      pam_unix.so
    account     sufficient    pam_localuser.so
    account     sufficient    pam_succeed_if.so uid < 500 quiet
    account     required      pam_permit.so
    
    password    requisite     pam_cracklib.so try_first_pass retry=300 type= minlen=8 minclass=4 enforce_for_root
    password    sufficient    pam_unix.so sha512 shadow nullok try_first_pass use_authtok
    password    required      pam_deny.so
    
    session     optional      pam_keyinit.so revoke
    session     required      pam_limits.so
    session     [success=1 default=ignore] pam_succeed_if.so service in crond quiet use_uid
    session     required      pam_unix.so
    
    auth        sufficient    pam_unix.so nullok try_first_pass
    auth        requisite     pam_succeed_if.so uid >= 500 quiet
    auth        required      pam_deny.so
    

本地登录功能没有任何变化，完全正常运行。

好，扯远了，那么pam_tally2的相关语句应该放置在哪才会有效果呢？

先把auth类型的行列出来：

    
    
    auth        required      pam_env.so
    auth        sufficient    pam_fprintd.so
    auth        sufficient    pam_unix.so nullok try_first_pass
    auth        requisite     pam_succeed_if.so uid >= 500 quiet
    auth        required      pam_deny.so
    

required大概意思就是，如果失败了也继续往下走，无论下面的语句成功与否，都会返回失败值，一般是为了不告诉你具体失败的原因。（如果成功，则应该继续往下走）

sufficient的大概意思是，如果失败了也继续往下走，且本次失败完全不影响最终结果。如果成功，且前面的required没有过失败，则立刻返回成功，不继续往下走了。

特别注意的是，网上一般对sufficient的解释很多都是错的，变成了只要它成功了，无论前面是否有过失败，都返回成功，比如：  
![图片.png](https://image.3001.net/images/20190627/1561565331_5d1398938f622.png!small)

实际上看man中的解释，就能知道其错误处了：

> if such a module succeeds and no prior required module has failed the PAM
> framework returns success to the application or to the superior PAM stack
> immediately without calling any further modules in the stack. A failure of a
> sufficient module is ignored and processing of the PAM module stack
> continues unaffected.

好，pam_env好像和环境什么的有关，不用管。pam_fprintd好像是什么指纹验证，而其控制标记是sufficient，所以失败也无所谓。重要的是pam_unix，这个就是真正验证你输入的用户名和密码是否正确的组件了，很简单的，如果它成功了，下面的语句一概不执行。

所以关键的地方来了，如果你想对登录失败次数过多的账户进行锁定让其不能登录进去，那么你就得放在pam_unix.so的前面，否则只要输入了正确的用户名密码就直接返回成功登入系统了，压根不会执行pam_tally2……

这下大家对语句放置点有个大概的把握了吧？网上资料虽多，但是很少有讲明白的（至少我是真没看得很明白，因为有些东西压根就没讲），比如required和requisite如果执行成功，就一路往下走，而required如果执行失败，也一路往下走。可到底走到哪是头？是走到整个配置文件的终点？还是到哪？反正如果是跨越这4个类型走到配置文件的话，很多事根本没法解释，所以我只能认为是走到这个类型的最后一行（猜测啊，没看过源码）。

又回来，如果是本地tty登录方式，那么login被调用，login中也引用了system-auth，这两个都属于被使用到的配置文件。所以对于本地tty登录方式而言，把pam_tally2放在login文件里也是可以的，login文件如下：

    
    
    #%PAM-1.0
    auth [user_unknown=ignore success=ok ignore=ignore default=bad] pam_securetty.so
    auth       include      system-auth
    account    required     pam_nologin.so
    account    include      system-auth
    password   include      system-auth
    # 3. pam_selinux.so close should be the first session rule
    #session    required     pam_selinux.so close
    session    required     pam_loginuid.so
    session    optional     pam_console.so
    # 4. pam_selinux.so open should only be followed by sessions to be executed in the user context
    session    required     pam_selinux.so open
    session    required     pam_namespace.so
    session    optional     pam_keyinit.so force revoke
    session    include      system-auth
    -session   optional     pam_ck_connector.sozz
    

这里说明一下include，应该是仅仅引用include前面类型的system-auth中的类型行， 比如auth include system-auth，意思就是引用system-auth中的auth行。 否则的话，那不全乱套了，因为login文件中引用了system-auth4次！

同样，substack应该也是这样，它和include的有一点点区别，这里我就直接引用别人的资料吧：  
![图片.png](https://image.3001.net/images/20190627/1561565412_5d1398e43c609.png!small)

注意，requesite一旦失败就会直接让结束流程，返回失败，所以这里是用它举例substack的作用，但并不仅仅只有它会这样，（如果前面required语句没有过失败）一旦成功就会终止流程返回成功的sufficient也同样会受到影响，不会影响到母栈。

所以，由于这里用的是include，而system-auth的pam_unix.so的控制符是sufficient，所以，pam_tally2应该放置于include语句之前才能起效果。

同样的，对于gdm文件，用substack引用system-auth，所以pam_tally2放在substack之前还是之后都可以。

就先写到这了，夜深了……

pam_tally2的具体参数的意义，和长时间不活动被强制登出的内容就放在下篇文章里写吧，文章太长也不好，容易丧失阅读兴趣，更何况我的思路跳得比较厉害……

 ***本文原创作者：起于凡而非于凡，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

