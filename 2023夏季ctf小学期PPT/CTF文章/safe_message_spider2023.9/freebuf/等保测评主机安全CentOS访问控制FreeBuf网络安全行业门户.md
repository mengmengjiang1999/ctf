## 一、说明

 **权限控制在等保测评里仅仅说了要求，但是怎么落地却基本没写，怎么说呢，比较抽象。**

 **所以，我觉得还是有必要了解一下centos系统大概有什么方法可以实现对用户的权限控制，不至于测评的时候完全不知道怎么测。**

这里我把我现在知道的关于权限控制的方法都列举出来，供大家参考参考。

另外，我使用的是centos6。

## 二、查看

无论针对什么权限，以下三个文件至少需要查看的：

    
    
    /etc/passwd
    /etc/shadwo
    /etc/group
    

通过这三个文件可以知道可登录的普通账户有哪些，以及用户组的情况，毕竟要判断用户的权限，至少应该知道用户的情况吧。

### 2.1. passwd

通过passwd文件，首先判断出哪些是普通用户、系统用户和超级用户（root）系统用户的uid在centos6中是大于0小于500的，500这个值的设置应该是在`login.defs`文件中。

然后判断出哪些用户不能登录，比如最后是`/sbin/nologin`以及`/bin/false`就不可登录。

### 2.2. shadow

通过shadow判断出哪些用户已经被不登录了。

2.2.1. 锁定或密码不可用

这里可以用passwd命令进行判断：

    
    
    [root@centos01 ~]# passwd -S cx
    cx PS 2019-03-26 0 9999 7 99 (密码已设置，使用 SHA512 加密。)
    

里面的PS意思就是密码已设置。

然后shadow中可能的情况有（每一段的第一句是shadow中实际的行，第二句是用passwd -S username 查询出来的值）：

    
    
    games:*:15980:0:99999:7:::
    games LK 2013-10-02 0 99999 7 -1 (更改当前使用的认证方案。)
    
    cx:*:17970:0:99999:7:::
    cx LK 2019-03-15 0 99999 7 -1 (更改当前使用的认证方案。)
    
    dbus:!!:17966::::::
    dbus LK 2019-03-11 0 99999 7 -1 (密码已被锁定。)
    
    cx:!:17970:0:99999:7:::
    cx LK 2019-03-15 0 99999 7 -1 (密码已被锁定。)
    
    cx::17970:0:99999:7:::
    cx NP 2019-03-15 0 99999 7 -1 (密码为空。)
    

上面除了最后一段也就是空密码是可以登录外，其余的都不可以。

密码字符串开头，也就是第一个`:`的右边加上`!`或`!!`字符串，无论`!`或`!!字符串`的后面有或没有密码字符串（这里没有，都是空密码），都代表被锁定。

至于`(更改当前使用的认证方案。)`，也是不能登录，这里的意思应该是因为密码字符串也是按照一定的格式存储的，比如告诉了系统用了哪种加密算法。

这样系统才知道当你输入密码后，要怎么对你输入的字符串进行加密，然后才能能拿来和shadow中的加密字符串进行对比。

你随便乱填的话，系统就认不出来了，也没法进行对比然后让你登录了。

比如你随便在密码字符串那输入一些字符串，其结果会显示为`(更改当前使用的认证方案。)`：

    
    
    cx:djfhjdhfs:17970:0:99999:7:::
    cx LK 2019-03-15 0 99999 7 -1 (更改当前使用的认证方案。)
    

2.2.2. 密码已经过期且已过宽恕期

如果设置了密码最长使用时间，且宽恕期也设置了，那么当密码过期，且宽恕期也过去了的话。

则该账号也无法登录，只有等具有权限的用户比如root来修改shadow文件了。

注意：如果仅仅是密码过期，则该账号仍然可登录，只要登录的时候修改密码即可。

虽然可以直接从shadow文件中进行判断，但是那个格式太不友好了，可以用chage命令：

    
    
    [root@centos01 ~]# chage -l cx
    Last password change					: Jun 28, 2019
    Password expires					: never
    Password inactive					: never
    Account expires						: Jan 20, 11761191
    Minimum number of days between password change		: 0
    Maximum number of days between password change		: 99999
    Number of days of warning before password expires	: 7
    
    

密码过期时间和宽恕时间都可以看到。

2.2.3. 账号已过期

账号过期的话也没法登录，也可以直接从shadow文件中进行判断，但还是用chage命令看比较好：

    
    
    [root@centos01 ~]# chage -l cx
    Last password change					: Jun 28, 2019
    Password expires					: never
    Password inactive					: never
    Account expires						: Jan 20, 11761191
    Minimum number of days between password change		: 0
    Maximum number of days between password change		: 99999
    Number of days of warning before password expires	: 7
    
    

其中的`Account expires`就是账号过期时间，注意，这个和密码过期后又过了宽恕期后不能登录，不是一回事，虽然都不能登录。

### 2.3. group

    
    
    cx:x:500:cx,cv
    cv:x:501:
    

这个很简单，唯一需要说的就是，最后一个`:`的右边，即为把这个组当成附加组的用户的用户名，可以有很多个，用`,`隔开。

所以`cx:x:500:cx,cv`的意思就是cx、cv用户的附加组中有cx组。

那把cx组当成基本组的用户是哪个呢？这里一般默认来说就是和cx组同名的用户，但是用户的基本组是可以改的，比如可以设置cx的基本组是cv组，而实际上从group文件中并不能确认用户的基本组到底是哪一个用户组，因为这文件里没有这样的信息。

所以最确切的方法是看passwd里的：

    
    
    cx:x:500:500:cx:/home/cx:/bin/bash
    

这里cx用户的基本组的id是500，所以cx用户的基本组也是cx组。

所以cx组是cx用户的基本组，也同时是cx用户的附加组。

其实这里可以直接用命令查看：

    
    
    [root@centos01 ~]# id cx
    uid=500(cx) gid=500(cx) 组=500(cx)
    

这里就表明了，cx的基本组的id是500，同时cx的所在的组（包括附加组和基本组）有id为500这个组，因为附加组和基本组是同一个组，所以不会重复排列。

而cv用户，就很简单了：

    
    
    [root@centos01 ~]# id cv
    uid=501(cv) gid=501(cv) 组=501(cv),500(cx)
    

cv的基本组是cv组，附加组是cx组。

那么cv的基本组cv组是不是也是cv的附加组呢？答案为不是，因为在group文件里最后一个`:`的右边，并没有cv（用户名）。

## 三、目录和文件权限

这个其实没啥好说的，目录和文件的创建者、所属组、其他用户的`rwx`属性，代表某用户是否具有读、写、执行权限。

所以通过对目录和文件进行设置，就能控制用户的对目录和文件的行为。

比如oracle数据库安装时，你用哪个用户去启动安装脚本，oracle的数据库目录的owner就会是这个用户（但root用户不能执行这个安装脚本）。

所以该用户才能够启动数据库，然后对数据库文件进行读和写。当然这里并不是直接用cat等命令读或者其他命令进行写，而是在sqlplus中用执行sql语句，但本质上，还是要拥有读写权限才可以的。

### 3.1. 文件

如果对文件具有`读r`权限， 就代表可以使用`cat、head、tail`等命令查看文件内容。

如果对文件具有`写w`权限，就代表可以使用`vim`等命令修改文件内容，这里稍微注意下，
**可以修改文件内容不代表你能够直接删除文件，因为这需要具有上级目录的权限** 。

如果对文件具有`执行x`权限，就代表可以执行该文件，当然，这需要这个文件是可执行文件比如脚本才行（对于目录执行权限也具有意义）。

### 3.2. 目录

目录的权限有点点复杂，原理嘛，大家去网上搜一搜“linux目录的x权限”就知道了，网上说得非常详细，我这里只说结果。

如果对目录具有`读r`权限，看上去应该是可以使用`ls`命令查看目录下文件的信息（名字、大小、权限等），但实际上如果只具有读权限，那么你用`ls`命令能看到的信息就只有目录下的文件名，目录下文件的其余信息看不到。你必须同时具有`执行x`权限，才可以正常查看目录下文件的信息。

如果对目录具有`写w`权限，看上去你就可以用`rm`等命令操作目录下的文件，但实际上如果只具有写权限，那么你用`rm`是删除不了目录下的文件的，你也必须同时具有`执行x`权限才能删除目下的文件。

如果对目录具有`执行x`权限，你就可以用`cd`命令进入目录，然后读取或写入目录下的文件（如果你对该文件具有相应的权限的话）。

所以，对于目录的`纯读`权限和`纯写`权限几乎没有任何意义。

### 3.3. umask

3.3.1. 说明

文件和目录创建出来就具有一个默认的权限，通过umask就可以设置默认的权限到底是多少，所以这个肯定也算是访问控制的一种。

首先，如果用户创建的是目录，则默认所有权限都开放，为777，也就是：`rwxrwxrwx`，至于文件，则是`rw-rw-rw-` 。

然后umask的作用就是从默认权限里拿掉一些权限，最后的结果就是实际的权限了。

查看umask的值：

    
    
    [root@centos01 ~]# umask
    0022
    

第一位0和网上说和SUID，SGID和SBIT这三特殊权限有关，SUID 对应4，SGID对应2，sticky 粘位对应1，不过我还没实验过，先不管它。

后面三位就代表着从owner、group、other那拿掉什么权限：

    
    
    新建文件：666-022=644；
    新建目录：777-022=755. 
    

注意， **这里是拿掉权限，而不是直接做减法** 。

想象一下，如果umask的值是0111（拿掉owner、group、other的执行权限），那么对于文件而言其实没有拿掉任何权限。

因为文件默认为666，本来就没有执行权，所以执行umask后还是666，而不是变成`666-111=555`（执行+阅读）

3.3.2. 配置文件

而umask主要应该在`etc/profile`和`etc/bashrc`文件中进行配置，他们的默认值都一样：

    
    
    if ($uid > 199 && "`id -gn`" == "`id -un`") then
        umask 002
    else
        umask 022
    endif
    

如果uid大于199，且用户名等于基本组的组名则为002，否则就是022，区别就是group的w权限有没有被拿走。  
`etc/profile`在每次登录的时执行，`etc/bashrc`是在登录后调用`bash shell`时执行。
所以，一般来说，`etc/bashrc`中的umask语句会覆盖`etc/profile`中的。

另外，如果你用的不是`bash shell`，比如修改了/etc/passwd里的值，让用户使用`csh
shell`，那么在执行`etc/profile`后接着执行的就应该是`csh.cshrc`。

另外，在`/etc/login.defs`里有这么一段：

    
    
    #The permission mask is initialized to this value. If not specified, 
    #the permission mask will be initialized to 022.
    UMASK           077
    

其实这个是针对用户的home目录的，当设置CREATE_HOME为yes的时候
，创建用户时就会自动创建用户的home目录，这里就是专门对home目录设置的umask。

## 四、进程权限

### 4.1. 说明

进程启动后，肯定是被某个用户所启动的，或者是以某用户的身份所启动的，那么进程所具有的权限（比如该进程能否读写某文件），也是由这个用户决定的。

网上资料如下（具体可看：[https://blog.csdn.net/bluemickey/article/details/22940873）：](https://blog.csdn.net/bluemickey/article/details/22940873%EF%BC%89%EF%BC%9A)  
![图片.png](https://image.3001.net/images/20190717/1563365720_5d2f11585827a.png!small)

大概意思就是说，调用进程时进程会涉及到这些id，而进程是否能够对文件和目录进行操作，则是由有效用户Id、有效组Id以及附加组Id去判断的。

正常情况下，有效用户Id、有效组Id就等于实际用户Id和实际组Id。

### 4.2. SUID、SGID

但如果对该执行文件设置了`SUID`，又如果该用户和该执行文件的owner都具有这个执行文件的x权限，则这个用户在运行这个执行文件时，产生的 **进程**
的 **有效用户ID** 是该执行文件的 **Owner Id** 。

而类似的还有`SGID`，也具有和`SUID`一样的功能，不过是针对可执行文件的`Group Id`（GUID还有其他的作用，这里就不说了）。

一般都会用passwd命令来进行说明，passwd命令设置了`SUID`，如下（rws中的s）：

    
    
    -rwsr-xr-x 1 root root 47032 Jul 16  2015 /usr/bin/passwd
    

故而其他非root用户可以用passwd命令修改自己的密码，因为进程的有效用户id变成了root的id，所以才能修改shadow文件：

    
    
    -rw-r----- 1 root shadow 1292 Aug 25 16:56 /etc/shadow
    

但是，有一个问题，网上没怎么说，既然非root用户都可以调用passwd命令去修改shadow文件，为啥还是只能修改自己的密码呢？其他用户的密码为啥还是修改不了？

### 4.3. 代码的判断

所以这里实际上是passwd内部进行了判断，源代码如下（c语言）：

    
    
    /* Only root gets to specify a user name. */
            username = NULL;
            if ((extraArgs != NULL) && (extraArgs[0] != NULL)) {
                    if (getuid() != 0) {
                            /* The invoking user was not root. */
                            audit_log_acct_message(audit_fd,  AUDIT_USER_CHAUTHTOK,
                                    NULL, "password change", extraArgs[0],
                                    getuid(), NULL, NULL, NULL, 0);
                            fprintf(stderr,
                                    _("%s: Only root can specify a user name.\n"),
                                    progname);
                            exit(-3);
                    } else {
                            /* The invoking user was root. */
                            username = extraArgs[0];
                            /* Sanity-check the user name */
                            if (strlen(username) > MAX_USERNAMESIZE) {
                                    fprintf(stderr,
                                            _("%s: The user name supplied is too long.\n"),
                                            progname);
                                    exit(-3);
                            }
                    }
     
                    /* If there is more than one unrecognized argument, we suddenly
                     * get confused. */
                    if (extraArgs[1] != NULL) {
                            fprintf(stderr,
                                    _("%s: Only one user name may be specified.\n"),
                                    progname);
                            exit(-3);
                    }
            }
    

意思很简单，判断passwd后是否带有参数，如果带有参数就判断`getuid()`的值是否等于0，不等于0它就不是root用户，不是root用户就别想修改别人的密码了，该干嘛干嘛去……

这里的`getuid()`的返回值是 **实际用户id** ，所以非root用户到这就“原形毕露”了。

相对应的，也存在一个`geteuid()`函数，它的返回值就是 **有效用户id** 。

所以如果一个用户对一个可执行文件有x权限，不代表就万事大吉了。

> 第一：你可以运行这个可执行文件，但是这个进程可能会涉及到的对其他文件的操作（读、写、执行等）不一定具备足够的权限。
>
> 第二： 可能在代码里又对你进行了限制，比如iptables这个文件
    
    
    -rwxr-xr-x. 1 root root 10688 11月 23 2013 /etc/init.d/iptables
    

other拥有x权限，但是一个非root用户传入status参数想查看iptables的状态时，却不会有反应。

那是因为iptables在一开头就进行了判断：

    
    
    #only usable for root
    [ $EUID = 0 ] || exit 4
    

### 4.4. root的权限

root拥有最高权限，但是这不是一句空话，它表现为在linux里root确实可以对任何文件、目录做几乎任何事情，而实现的机制是因为linux的代码是这样规定的。

但是如果我自己写一个脚本，里面的代码逻辑是如果uid不为0才能往下执行，root的“最高权限”就没了吧？（当然root直接修改脚本那另说）。

类似的比如oracle的安装过程中，如果你用root账号去执行安装脚本，就会是这样：  
![图片.png](https://image.3001.net/images/20190717/1563365732_5d2f1164807d0.png!small)

这估计也是在脚本里写的一个逻辑判断。

## 五、结尾

先写到这，其余部分放下篇文章写，还有几种访问控制的方法没写。

其实访问控制不很好弄，因为不太清楚实际业务中，被测评单位会用什么方式进行访问控制，也就是不知道会用什么技术。更何况，很多被测评单位自己压根就没做权限控制……

不过无论如何，访问控制必然要用某些方法实现，那么其中用户、用户组，目录、文件的基础知识是怎么也绕不过去的。比如涉及到用户，你肯定要判断他有没有被禁用吧？
说句不好听的，如果通过访谈，被测评单位说他做了访问控制，你至少也得知道怎么去取证吧？

最后，因为涉及的都是基础知识，所以就概括的写了下，想详细的了解的话，建议去网上找找资料，这部分的知识网上还是写得很详细和清晰的。

 ***本文作者：起于凡而非于凡，本文属 FreeBuf 原创奖励计划，未经许可禁止转载**

