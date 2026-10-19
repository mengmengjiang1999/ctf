## **一、** ** **操作目的和应用场景****

###  **（一）** ** **目的****

CentOS 8系统启用selinux并实施强制访问控制。

###  **（二）** ** **简介****

安全增强型 Linux（Security-Enhanced Linux）简称 SELinux，它是一个 Linux 内核模块，也是 Linux
的一个安全子系统。SELinux主要由美国国家安全局开发。2.6 及以上版本的 Linux 内核都已经集成了 SELinux 模块。

SELinux 主要作用就是最大限度地减小系统中服务进程可访问的资源（最小权限原则）。

设想一下，如果一个以 root 身份运行的网络服务存在 0day 漏洞，黑客就可以利用这个漏洞，以 root
的身份在您的服务器上为所欲为了。是不是很可怕？SELinux 就是来解决这个问题的。

##  **二、** ** **操作步骤****

###  **（一）** ** **selinux**** ** **的工作模式****

 **1、** ** **selinux的三种工作模式****

SELinux 有三种工作模式，分别是：

> enforcing //强制模式。违反 SELinux 规则的行为将被阻止并记录到日志中
>
> permissive //宽容模式。违反 SELinux 规则的行为只会记录到日志中。一般为调试用
>
> disabled //关闭 SELinux

SELinux 工作模式可以在/etc/selinux/config中设置。

如果想从disabled切换到enforcing或者permissive的话，需要重启系统。反过来也一样。

enforcing 和 permissive 模式可以通过 setenforce 1|0 命令快速切换。

 **2、** ** **启用selinux****

####  **(1)** ** **临时启用**** ** **selinux****

setenforce 1

####  **(2)** ** **永久启用**** ** **selinux****

vi /etc/selinux/config //编辑配置文件

将

SELINUX=disabled

改为

SELINUX=enforcing

保存退出。重启后生效。

> reboot //重启计算机
>
> getenforce //查看selinux工作模式
>
> /usr/sbin/sestatus -v //查看selinux工作状态详情

![1615877678_6050562ebd7cb1451a7ca.png!small?1615877761433](https://image.3001.net/images/20210316/1615877678_6050562ebd7cb1451a7ca.png!small?1615877761433)

当前selinux的状态为enabled，工作模式为enforcing，策略为targeted，说明selinux已经正常工作了。

反之，如果要禁用selinux，临时的方法是setenforce 0，持久化的方法是修改配置文件，设置SELINUX=disabled，并重启使之生效。

###  **（二）** ** **selinux的策略**** ** **和规则****

 **1、** ** **selinux的策略****

系统中通常有大量的文件和进程，为了节省时间和开销，通常我们只是选择性地对某些进程进行管制。而哪些进程需要管制、要怎么管制是由策略决定的。

在 CentOS系统中，有三套策略，分别是：

> targeted //对大部分网络服务进程进行管制，是默认的策略
>
> minimum //以targeted为基础，仅对选定的网络服务进程进行管制。一般不用。
>
> mls //多级安全保护。对所有的进程进行管制，这是最严格的策略，配置难度非常大。一般不用，除非对安全性有极高的要求。

策略可以在/etc/selinux/config文件中指定。

 **2、** ** **selinux的规则****

一套策略里面有许多规则，其中部分规则可以按照需求启用或禁用，这些规则称为布尔型规则。规则是模块化、可扩展的。在安装新的应用程序时，应用程序可通过添加新的模块来添加规则。用户也可以手动地增减规则。

 **3、** ** **使用seinfo查看selinux的策略信息****

seinfo - SELinux policy information tool

seinfo //不加参数运行，查看策略文件以及文件所包含的内容

![1615877722_6050565a5b84a55beef46.png!small?1615877804794](https://image.3001.net/images/20210316/1615877722_6050565a5b84a55beef46.png!small?1615877804794)

从输出可以看到，策略中包含Users、Roles、Types、Boleans，它们分别是用户、角色、类型和布尔型规则。下面分别查看：

seinfo -r //查看selinux的所有角色（role）

![1615877733_60505665378b7b0813377.png!small?1615877815573](https://image.3001.net/images/20210316/1615877733_60505665378b7b0813377.png!small?1615877815573)

当前有14个selinux角色。

seinfo -u //列出selinux的所有身份表示（user）

![1615877747_605056736625fe252c5d0.png!small?1615877829879](https://image.3001.net/images/20210316/1615877747_605056736625fe252c5d0.png!small?1615877829879)

当前有8个selinux用户

seinfo -t //查看selinux的所有类型（type）

![1615877758_6050567e7dbd6344fc672.png!small?1615877841056](https://image.3001.net/images/20210316/1615877758_6050567e7dbd6344fc672.png!small?1615877841056)

可以看到，当前系统中selinux的类型有4940个。

seinfo -b //列出所有布尔型规则

![1615877770_6050568a5948dd5288787.png!small?1615877853029](https://image.3001.net/images/20210316/1615877770_6050568a5948dd5288787.png!small?1615877853029)

当前有330条布尔型selinux规则。

seinfo -b | grep nfs //-b --bool，查看与nfs相关的布尔型规则

![1615877781_605056952cacb67ffa5ef.png!small?1615877863728](https://image.3001.net/images/20210316/1615877781_605056952cacb67ffa5ef.png!small?1615877863728)

 **4、** ** **使用sesearch查询selinux策略的详情****

sesearch是SELinux的策略查询工具，使用方法如下：

sesearch --allow | grep \ cluster_t\ //查看主体类型为cluster_t的allow规则

![1615877839_605056cf6d47ec99eac91.png!small?1615877922148](https://image.3001.net/images/20210316/1615877839_605056cf6d47ec99eac91.png!small?1615877922148)

sesearch --allow | grep \ cluster_t: //查看客体类型为cluster_d的allow规则

![1615877848_605056d82ae0926546255.png!small?1615877930578](https://image.3001.net/images/20210316/1615877848_605056d82ae0926546255.png!small?1615877930578)

 **5、** ** **使用**** ** **setsebool**** ** **开关一个布尔规则****

setsebool [选项] <规则名称> <on|off>

setsebool -P httpd_anon_write on

![1615877862_605056e62df931c283307.png!small?1615877944535](https://image.3001.net/images/20210316/1615877862_605056e62df931c283307.png!small?1615877944535)

开关代表切换selinux规则的生效状态。运行成功后不显示任何信息。

###  **（三）** ** **selinux的**** ** **安全上下文****

 **1、** ** **什么是安全上下文？****

安全上下文分为“进程安全上下文”和“文件安全上下文”。一个“进程安全上下文”一般对应多个“文件安全上下文”。只有两者的安全上下文对应上了，进程才能访问文件。它们的对应关系由策略中的规则决定。

文件安全上下文由文件创建的位置和创建文件的进程所决定。而且系统有一套默认值，用户也可以对默认值进行设定。

需要注意的是，单纯的移动文件操作并不会改变文件的安全上下文。

 **2、** ** **安全上下文间结构和含义****

安全上下文有四个字段，分别用冒号隔开。形如：system_u:object_r:admin_home_t:s0。

![1615877879_605056f7010f3255304e3.png!small?1615877961775](https://image.3001.net/images/20210316/1615877879_605056f7010f3255304e3.png!small?1615877961775)

 **3、** ** **查看安全上下文****

 **(1)** ** **查看文件的安全上下文****

ls -Z /var/www/htmp //查看目录的安全上下文

![1615877891_60505703e0b28c76529a2.png!small?1615877974374](https://image.3001.net/images/20210316/1615877891_60505703e0b28c76529a2.png!small?1615877974374)

可以看到/var/www/html/目录的selinux类型为http_sys_content_t

 **(2)** ** **查看进程的安全上下文****

ps auxZ | grep -v grep | grep httpd

![1615877904_6050571064fc17a28648b.png!small?1615877986963](https://image.3001.net/images/20210316/1615877904_6050571064fc17a28648b.png!small?1615877986963)

可以看到，httpd进程的selinux类型为http_t，且存在多个httpd进程，具有相同的安全上下文。注意，进程的安全上下文不同于其可执行文件的安全上下文。

为什么httpd进程可以访问/var/www/html目录？因为当前存在着相应的允许主体httpd_t访问客体http_sys_content_t进行相关操作的的selinux规则。

 **4、** ** **修改文件安全上下文****

下面通过一个例子了解修改文件安全上下文的方法：

 **(1)** ** **创建测试文件****

//在/var/www/html目录中创建测试文件：

echo index.html > /var/www/html/index.html

//查看文件的安全上下文

ls -Z /var/www/html/index.html

![1615878064_605057b06e85c0deed31b.png!small?1615878146779](https://image.3001.net/images/20210316/1615878064_605057b06e85c0deed31b.png!small?1615878146779)

可以看到，文件的selinux type为httpd_sys_content_t

//在/root目录创建另一个测试文件

echo index1.html > /root/index1.html

//将测试文件移动到/var/www/html/目录中

mv /root/index1.html /var/www/html/index1.html

//查看测试文件的安全上下文

ls -Z /var/www/html/index1.html

![1615878078_605057be1a8d7d6ed9fd5.png!small?1615878160404](https://image.3001.net/images/20210316/1615878078_605057be1a8d7d6ed9fd5.png!small?1615878160404)可以看到，index1.html文件的selinux类型为admin_home_t。这是因为文件的安全上下文不会因为文件被移动而发生变化。

//使用links远程访问index.html文件

links 192.168.242.164/index.html

![1615878093_605057cd30f1b39f2e8d1.png!small?1615878175602](https://image.3001.net/images/20210316/1615878093_605057cd30f1b39f2e8d1.png!small?1615878175602)

访问成功。

//远程主机使用links访问index1.html文件

links 192.168.242.164/index1.html

![1615878103_605057d7afea879e24f0c.png!small?1615878186070](https://image.3001.net/images/20210316/1615878103_605057d7afea879e24f0c.png!small?1615878186070)提示没有权限访问index1.html。

这是因为不存在允许类型为httpd_t的主体访问类型为admin_home_t的客体文件并进行读取操作的规则。可使用下面的命令查找符合条件的规则：

sesearch -s httpd_t -t admin_home_t -c file -p read --allow

![1615878165_60505815cec51a820d9a9.png!small?1615878248215](https://image.3001.net/images/20210316/1615878165_60505815cec51a820d9a9.png!small?1615878248215)

找不到符合要求的规则条目。

要想解决这个问题，要么修改/var/www/html/index1.html文件的安全上下文，将类型修改为httpd_sys_content_t或其它已经被允许访问的类型；要么新建一条规则，允许httpd_t类型的主体对admin_home_t类型的客体文件进行读取操作。这里介绍第一种方式，即修改文件的安全上下文。

 **(2)** ** **使用chcon修改文件的安全上下文****

//使用chcon命令指定文件上下文中的类型，chcon命令的使用方法如下：

chcon <选项> <文件或目录1> [<文件或目录n>]

选项

|

功能  
  
---|---  
  
-u <值>

|

修改安全上下文的用户字段  
  
-r <值>

|

修改安全上下文的角色字段  
  
-t <值>

|

修改安全上下文的类型字段  
  
-l <值>

|

修改安全上下文的级别字段  
  
\--reference <文件或目录>

|

将文件/目录的安全上下文修改为与指定的文件/目录一致  
  
-R

|

递归操作  
  
-h

|

修改符号链接的安全上下文，不加选项则修改符号链接所对应的文件  
  
//一种方法是使用-t选项直接指定类型

chcon -t httpd_sys_content_t /var/www/html/index1.html

![1615878198_6050583663489eac81fa0.png!small?1615878280796](https://image.3001.net/images/20210316/1615878198_6050583663489eac81fa0.png!small?1615878280796)

//尝试远程访问index1.html文件

links 192.168.242.164/index1.html

![1615878211_605058436e28bfb694ece.png!small?1615878293804](https://image.3001.net/images/20210316/1615878211_605058436e28bfb694ece.png!small?1615878293804)访问成功。说明index1.html文件安全上下文的修改生效了。

另一种方法是使用--reference选项复制其它文件的安全上下文

//再次将index1.html文件的type修改为admin_home_t

chcon -t admin_home_t /var/www/html/index1.html

chcon --referece=/var/www/html/index.html /var/www/html/index1.html

![1615878227_60505853f379fbcc9341e.png!small?1615878310486](https://image.3001.net/images/20210316/1615878227_60505853f379fbcc9341e.png!small?1615878310486)

文件的安全上下文修改成功。文件安全上下文中的类型设置成了httpd_sys_content_t，自然可以被httpd进程访问，因此不再使用links验证。

 **(3)** ** **使用restorecon自动为文件设置正确的安全上下文****

ls -Z /var/www/html/index1.html //查看安全上下文

restorecon /var/www/html/index1.html //自动设置安全上下文

![1615878248_605058684042e6bcc8df8.png!small?1615878330588](https://image.3001.net/images/20210316/1615878248_605058684042e6bcc8df8.png!small?1615878330588)

文件安全上下文修改成功。

 **5、** ** **修改目录的安全上下文****

通过一个例子了解修改目录及其中文件的安全上下文的方法。

 **(1)** ** **创建测试目录和网页****

//在/root目录创建目录

mkdir /root/myweb/

//创建网页

echo myweb > /root/myweb/myweb.html

//测试目录移动到/var/www/html/

mv /root/myweb /var/www/html/

//查看移动后的测试目录的安全上下文

ls -dZ /var/www/html/myweb/

//查看移动后的测试目录中网页的安全上下文

ls -Z /var/www/html/myweb/myweb.html

![1615878262_60505876a7d330c222d0d.png!small?1615878345141](https://image.3001.net/images/20210316/1615878262_60505876a7d330c222d0d.png!small?1615878345141)

//使用links远程访问index.html文件

links 192.168.242.164/myweb/myweb.html

![1615878275_60505883629f3f49389f0.png!small?1615878357964](https://image.3001.net/images/20210316/1615878275_60505883629f3f49389f0.png!small?1615878357964)

产生错误的原因和前面的例子一样，都是因为没有相应的selinux规则。像上面一样，我们修改文件的安全上下文中的类型。

chcon -t httpd_sys_content_t /var/www/html/myweb/myweb.html

![1615878314_605058aa4c1009604761a.png!small?1615878397268](https://image.3001.net/images/20210316/1615878314_605058aa4c1009604761a.png!small?1615878397268)

成功。

//创建新的网页文件

echo myweb1 > /var/www/html/myweb/myweb1.html

![1615878336_605058c0df6bd26770bc1.png!small?1615878419289](https://image.3001.net/images/20210316/1615878336_605058c0df6bd26770bc1.png!small?1615878419289)新建文件的安全上下文还是admin_home_t，这是因为文件所在的目录的安全上下文中的类型还是admin_home_t，没有被改变。因此我们需要修改目录的安全上下文，这样在此目录中新建的文件将具有新的安全上下文。

chcon -t httpd_sys_content_t /var/www/html/myweb/

![1615878366_605058de6377826242c5a.png!small?1615878448978](https://image.3001.net/images/20210316/1615878366_605058de6377826242c5a.png!small?1615878448978)

之后再创建新的文件，安全上下文的类型就变成httpd_sys_content_t了。

 **(2)** ** **使用**** ** **semanage**** ** **命令修改目录的默认安全上下文****

semanage-fcontext - SELinux Policy Management file context tool

看下面的例子：

//在/root目录创建目录

mkdir /root/newweb/

//创建网页

echo newweb > /root/newweb/newweb.html

//测试目录移动到/var/www/html/

mv /root/newweb /var/www/html/

//查看移动后的测试目录的安全上下文

ls -dZ /var/www/html/newweb/

//查看移动后的测试目录中网页的安全上下文

ls -Z /var/www/html/newweb/newweb.html

![1615878385_605058f10ff0ea9eeb5cf.png!small?1615878467561](https://image.3001.net/images/20210316/1615878385_605058f10ff0ea9eeb5cf.png!small?1615878467561)

可以看到，移动后目录和其中的文件的安全上下文中的类型都是admin_home_t

//修改目录及其中全部文件的安全上下文，添加httpd_sys_content_t类型

semanage fcontext -a -t httpd_sys_content_t "/var/www/html/newweb(/.*)?"

//修改之后的安全上下文并未生效，需要使用restorecon命令使其生效：

restorecon -Rv /var/www/html/newweb/

//查看目录和文件的安全上下文

ls -dZ /var/www/html/newweb/ /var/www/html/newweb/newweb.html

![1615878397_605058fd63ef7cd92abf7.png!small?1615878479729](https://image.3001.net/images/20210316/1615878397_605058fd63ef7cd92abf7.png!small?1615878479729)

安全上下文的修改生效了。

//查看测试目录和文件的默认安全上下文

semanage fcontext -l | grep /var/www/html/

![1615878410_6050590a9bd0907166f33.png!small?1615878493220](https://image.3001.net/images/20210316/1615878410_6050590a9bd0907166f33.png!small?1615878493220)

可以看到，/var/www/html/newweb目录和其中的文件又默认的安全上下文，而前面的myweb目录没有设置默认安全上下文，因此没有处现在结果中。

默认安全上下文的作用是什么？设置了默认安全上下文后，不管如何修改安全上下文中的属性，只要运行restorecon命令，就可以将默认安全上下文恢复到当前配置中。

//使用chcon修改安全上下文

chcon -t admin_home_t /var/www/html/newweb/newweb.html

//使用restorecon命令恢复默认安全上下文

restorecon /var/www/html/newweb/newweb.html

![1615878426_6050591a8d8f2c7ae6082.png!small?1615878509008](https://image.3001.net/images/20210316/1615878426_6050591a8d8f2c7ae6082.png!small?1615878509008)

当前的安全上下文已恢复为默认。

###  **（四）** ** **selinux的日志****

 **1、** ** **查看日志文件****

selinux阻止进程访问的记录保存在/var/log/audit/audit.log文件中。

    
    
    tail -n 3 /var/log/audit/audit.log
    
    type=*VC msg=audit(1615342682.388:139): *vc:  denied  { getattr } for  pid=2632 comm="httpd" path="/var/www/html/index1.html" dev="sda1" ino=67619205 scontext=system_u:system_r:httpd_t:s0 tcontext=unconfined_u:object_r:admin_home_t:s0 tclass=file permissive=0
    
    type=SYSCALL msg=audit(1615342682.388:139): arch=c000003e syscall=6 success=no exit=-13 a0=7f261c043dc8 a1=7f261b7fd8d0 a2=7f261b7fd8d0 a3=1 items=0 ppid=2307 pid=2632 auid=4294967295 uid=48 gid=48 euid=48 suid=48 fsuid=48 egid=48 sgid=48 fsgid=48 tty=(none) ses=4294967295 comm="httpd" exe="/usr/sbin/httpd" subj=system_u:system_r:httpd_t:s0 key=(null)ARCH=x86_64 SYSCALL=lstat AUID="unset" UID="apache" GID="apache" EUID="apache" SUID="apache" FSUID="apache" EGID="apache" SGID="apache" FSGID="apache"
    
    type=PROCTITLE msg=audit(1615342682.388:139): proctitle=2F7573722F7362696E2F6874747064002D44464F524547524F554E44

在日志中详细记录了selinux的主体和客体的信息。

 **2、** ** **使用sealert程序**** ** **对日志**** ** **进行分析****

将上面的日志信息复制到新建的文件中，之后使用sealert程序分析。

sealert -a se.txt //-a参数指定文件

![1615878441_60505929c52dba2d889bd.png!small?1615878524465](https://image.3001.net/images/20210316/1615878441_60505929c52dba2d889bd.png!small?1615878524465)

sealert给出了事件的解释：

SELinux is preventing /usr/sbin/httpd from getattr access on the 文件
/var/www/html/index1.html.

之后给出了两个修复建议，一个是使用restorecon插件进行修复，置信度为99.5：

/sbin/restorecon -v /var/www/html/index1.html

另一个是使用catchall插件进行修复，置信度为1.49：

ausearch -c 'httpd' --raw | audit2allow -M my-httpd

semodule -i my-httpd.pp

使用restorecon可以完美地解决问题，但是使用catchall只能满足读取文件属性的要求，无法读取文件内容。这样还是会出现selinux的错误日志：

![1615878526_6050597e8d960d5429ee9.png!small?1615878609659](https://image.3001.net/images/20210316/1615878526_6050597e8d960d5429ee9.png!small?1615878609659)

日志内容是拒绝读取文件。

###  **（五）** ** **为自定义程序创建selinux策略****

 **1、** ** **创建测试程序****

在这个例子中，创建一个打开/var/log/messages文件并执行写入操作的程序。

    
    
    //安装policycoreutils-devel包
    
    yum install policycoreutils-devel
    
    vi mydaemon.c  //创建并编辑代码文件，加入下面的内容
    
    #include <unistd.h>
    
    #include <stdio.h>
    
    FILE *f;
    
    int main(void)
    
    {
    
    while(1) {
    
    f = fopen("/var/log/messages","w");
    
    sleep(5);
    
    fclose(f);
    
    }
    
    }
    
    保存退出
    
    
    
    
    //编译文件
    
    gcc -o mydaemon mydaemon.c
    
    
    
    
    vi mydaemon.service  //创建并编辑服务配置文件，加入下面的内容
    
    [Unit]
    
    Description=Simple testing daemon
    
    
    
    
    [Service]
    
    Type=simple
    
    ExecStart=/usr/local/bin/mydaemon
    
    
    
    
    [Install]
    
    WantedBy=multi-user.target
    
    保存退出
    
    
    
    
    //安装为服务并启动
    
    cp mydaemon /usr/local/bin/
    
    cp mydaemon.service /usr/lib/systemd/system
    
    systemctl start mydaemon
    
    systemctl status mydaemon

![1615878526_6050597ebe74767def45d.png!small?1615878609662](https://image.3001.net/images/20210316/1615878526_6050597ebe74767def45d.png!small?1615878609662)

//查看进程

ps -efZ | grep mydaemon

![1615878563_605059a31f7f9077e4103.png!small?1615878645481](https://image.3001.net/images/20210316/1615878563_605059a31f7f9077e4103.png!small?1615878645481)

可以看到，新的进程尚未设置selinux安全上下文。

 **2、** ** **生成自定义策略****

sepolicy generate --init /usr/local/bin/mydaemon

![1615878572_605059ac6379c7fb63e94.png!small?1615878655009](https://image.3001.net/images/20210316/1615878572_605059ac6379c7fb63e94.png!small?1615878655009)

生成了多个文件。

运行生成的shell脚本，使用新的策略模块重新构建新的系统策略。

/mydaemon.sh

![1615878585_605059b90ba9536b43c7b.png!small?1615878668314](https://image.3001.net/images/20210316/1615878585_605059b90ba9536b43c7b.png!small?1615878668314)

//设置可执行文件的安全上下文

restorecon -v /usr/local/bin/mydaemon /usr/lib/systemd/system

//重启进程并查看安全上下文

systemctl restart mydaemon

ps -efZ | grep mydaemon

![1615878596_605059c4b7c0980374552.png!small?1615878679221](https://image.3001.net/images/20210316/1615878596_605059c4b7c0980374552.png!small?1615878679221)

进程的安全上下文已经设置好了。

此进程由于受到selinux的限制，无法写入/var/log/messages文件。

//查看审计日志中记录的错误（将*VC中的*改为A）

ausearch -m *VC -ts recent
![1615878607_605059cfe2f78df76b1ec.png!small?1615878690323](https://image.3001.net/images/20210316/1615878607_605059cfe2f78df76b1ec.png!small?1615878690323)

返回了最近产生的错误，mydaemon进程作为主体无法open和write客体/var/log/messages文件。

//使用sealert命令查看更详细的信息

sealert

//使用audit2allow提出整改建议（将*VC中的*改为A）

ausearch -m *VC -ts recent | audit2allow -R

![1615878624_605059e024887fffd0196.png!small?1615878706464](https://image.3001.net/images/20210316/1615878624_605059e024887fffd0196.png!small?1615878706464)

返回的结果表示，需要将mydaemon_t作为参数带入到logging_write_generic_logs接口中。

由于audit2allow输出的结果可能不准确，所以需要去找对应的策略接口，确认其存在：

grep -r "logging_write_generic_logs" /usr/share/selinux/devel/include/ | grep
.if

![1615878637_605059ed7e0c5455e36d2.png!small?1615878719833](https://image.3001.net/images/20210316/1615878637_605059ed7e0c5455e36d2.png!small?1615878719833)

找到了策略接口文件。

查看策略接口文件的内容

cat /usr/share/selinux/devel/include/system/logging.if

![1615878648_605059f898e39255eb4e2.png!small?1615878731116](https://image.3001.net/images/20210316/1615878648_605059f898e39255eb4e2.png!small?1615878731116)

上面是logging_write_generic_logs接口的配置，可以使用这个接口。

//将接口写入te文件

echo "logging_write_generic_logs(mydaemon_t)" >> mydaemon.te

//重新执行脚本，构建新的selinux策略

./mydaemon.sh

//查看审计日志中记录的错误（将*VC中的*改为A）

ausearch -m *VC -ts recent

![1615878675_60505a135ba544dcb8415.png!small?1615878757928](https://image.3001.net/images/20210316/1615878675_60505a135ba544dcb8415.png!small?1615878757928)

程序仍在运行，但是没有产生新的错误，说明新的selinux规则生效了。

##  **三、** ** **参考**** ** **网址****

[
_https://zhuanlan.zhihu.com/p/30483108_](https://zhuanlan.zhihu.com/p/30483108)

[
_https://www.cnblogs.com/zhongguiyao/p/13955398.html_](https://www.cnblogs.com/zhongguiyao/p/13955398.html)

[ _https://www.cnblogs.com/liujiaxin2018/p/14021870.htm_
_l_](https://www.cnblogs.com/liujiaxin2018/p/14021870.html)

[ _https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/8/html/using_selinux/writing-a-custom-selinux-policy_using-selinux_](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/8/html/using_selinux/writing-a-custom-selinux-policy_using-selinux)

