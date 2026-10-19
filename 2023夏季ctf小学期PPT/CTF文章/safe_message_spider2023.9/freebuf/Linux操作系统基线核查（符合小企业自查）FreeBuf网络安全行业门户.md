# **一、** ** **身份鉴别****

序号

|

要求项/控制点

|

是否满足

|

加固方法  
  
---|---|---|---  
  
1

|

应对登录的用户进行身份标识和鉴别，身份标识具有唯一性，身份鉴别信息具有复杂度要求并定期更换；

| |

密码复杂度: 字母/数字/特殊符号,不小于8位; 用户密码 5 次不能重复

vim /etc/pam.d/system-auth

auth required pam_tally2.so onerr=fail deny=3 unlock_time=1200even_deny_root
root_unlock_time=1200

Auth sufficient pam_unix.so nullok try_first_pass remember=5

Password requisite pam_cracklib.so retry=3 difork=3 minlen=8 lcredit=-1
dcredit=-1 ocredit=-1

设置定期修改密码时间

vim /etc/login.defs

PASS_MAX_DAYS 90

PASS_MIN_DAYS 0

PASS_MIN_LEN 8

PASS_WARN_AGE 7  
  
2

|

应具有登录失败处理功能，应加固并启用结束会话、限制非法登录次数和当登录连接超时自动退出等相关措施；

| |

设置连续输错三次密码，账号锁定五分钟。

使用命令 vi /etc/pam.d/common-auth修改配置文件，在配置文件中添加 auth required pam_tally.so
onerr=fail deny=3 unlock_time=300  
  
3

|

当进行远程管理时，应采取必要措施防止鉴别信息再网络传输过程中被窃听。

| |

禁止使用telnet协议，可选用ssh协议进行远程管理

利用命令rpm -qa |grep telnet查看是否安装telnet 和telnet server 如果安装的话  
1、编辑/etc/xinetd.d/telnet, 修改 disable = yes。  
2.激活xinetd服务。命令如下：  
# service xinetd restart  
如果没安装则说明禁用telnet服务；

对于使用IP协议进行远程维护的设备,应配置使用SSH协议

在网站上免费获取OpenSSH http://www.openssh.com/,并根据安装文件说明执行安装步骤  
  
#  **二、** ** **访问控制****

序号

|

要求项/控制点

|

是否满足

|

加固方法  
  
---|---|---|---  
  
1

|

应对登录的用户分配账户与权限；

| |

查看是否存在root账户一号通用多用的情况，若存在，则需要建立若干符合实际情况的普通账号，每个普通账号都得遵循最小权限原则并且禁止直接使用root账户。

创建普通权限账号并配置密码,防止无法远程登录;

使用命令 vi /etc/ssh/sshd_config修改配置文件将PermitRootLogin的值改成no，并保存，然后使用service sshd
restart重启服务。  
  
2

|

应重命名或删除默认账户，修改默认账户的默认口令；

| |

查看空口令和root权限账号，确认是否存在异常账号

使用命令 awk -F: '($2=="")' /etc/shadow 查看空口令账号；

使用命令 awk -F: '($3==0)' /etc/passwd 查看UID为零的账号；

使用命令 passwd <用户名> 为空口令账号设定密码；

检查是否存在除root之外UID为0的用户。  
  
3

|

应及时删除或停用多余的、过期的账户，避免共享账户的存在；

| |

删除用户:#userdel username;  
锁定用户：  
#usermod -L username  
只有具备超级用户权限的使用者方可使用  
#usermod –U username可以解锁。  
补充操作说明  
需要锁定的用户：

adm,lp,mail,uucp,operator,games,gopher,ftp,nobody,nobody4,noaccess,listen,webservd,rpm,dbus,avahi,mailnull,smmsp,nscd,vcsa,rpc,rpcuser,nfs,sshd,pcap,ntp,haldaemon,distcache,apache,webalizer,squid,xfs,gdm,sabayon,named  
  
4

|

用授予管理用户所需的最小权限，实现管理用户的权限分离

| |

查看是否存在权限过大的用户，是否能操作其应当访问的范围之外的系统资源。若存在，需要降低其权限，使其仅仅能操作应当访问的系统资源。

创建普通权限账号并配置密码,防止无法远程登录

限制root用户直接登录

使用命令 vi /etc/ssh/sshd_config修改配置文件将PermitRootLogin的值改成no，并保存，然后使用service sshd
restart重启服务。

限制能su到root的用户

编辑su文件(vi /etc/pam.d/su)，在开头添加下面两行：  
auth sufficient pam_rootok.so 和  
auth required pam_wheel.so group=wheel 这表明只有wheel组的成员可以使用su命令成为root用户。  
你可以把用户添加到wheel组，以使它可以使用su命令成为root用户。  
添加方法为：usermod –G wheel username  
  
#  **三、** ** **安全审计****

序号

|

要求项/控制点

|

是否满足

|

加固方法  
  
---|---|---|---  
  
1

|

应启用安全审计功能，审计覆盖到每个用户，对重要的用户行为和重要安全事件进行审计；

| |

启用系统本身的syslog日志功能和auditd审计功能, 审计覆盖到服务器及用户的行为

记录用户的登录与操作

vim /etc/profile

USER_IP=`who -u am i 2>/dev/null| awk '{print $NF}'|sed -e 's/[()]//g'`

if [ "$USER_IP" = "" ]

then

USER_IP=`hostname`

fi

if [ ! -d /tmp/dbasky ]

then

mkdir /tmp/dbasky

chmod 755 /tmp/dbasky

fi

if [ ! -d /tmp/dbasky/${LOGNAME} ]

then

mkdir /tmp/dbasky/${LOGNAME}

chmod 300 /tmp/dbasky/${LOGNAME}

fi

export HISTSIZE=4096

DT=`date "+%Y-%m-%d_%H-%M-%S"`

export HISTFILE="/tmp/dbasky/${LOGNAME}/${USER_IP}-dbasky.$DT"  
export HISTTIMEFORMAT="[%Y.%m.%d %H:%M:%S]"  
chmod 600 /tmp/dbasky/${LOGNAME}/*dbasky* 2>/dev/null  
  
2

|

审计记录应包括事件的日期、用户、事件类型、事件是否成功及其它与审计相关的信息；

| |

查看审计内容，是否包含事件的日期、用户、事件类型、事件是否成功等关键信息  
  
3

|

应对审计记录进行保护，定期备份，避免受到未预期的删除、修改或覆盖等。

| |

更改所有日志文件属性，使文件只可追加不可修改：

Chattr +a /var/log/messages /var/log/secure /var/log/maillog /var/log/cron

定期导出备份，审计记录至少保留6个月以上  
  
#  **四、** ** **入侵防范****

序号

|

要求项/控制点

|

是否满足

|

加固方法  
  
---|---|---|---  
  
1

|

应遵循最小安装的原则，仅安装需要的组件和应用程序；

| |

遵循最小安装原则，禁止“夹带”现象  
  
2

|

应关闭不需要的系统服务、默认共享和高危端口；

| |

查看监听端口

Netstat -an

查看开启服务

Chkconfig -list |grep on

要直接关闭某个服务，如sshd可用如下命令:  
# /etc/init.d/sshd stop #关闭正在运行的sshd服务  
  
关闭下列不必要的基本网络服务。  
chargen-dgram daytime-stream echo-streamklogin tcpmux-server chargen-stream
discard-dgram eklogin krb5-telnet tftp cvs discard-stream ekrb5-telnet kshell
time-dgram daytime-dgram echo-dgram gssftp rsync time-stream  
  
3

|

应通过设定终端接入方式或网络地址范围对通过网络进行管理的管理终端进行限制；

| |

通过vpn连接内网环境，再利用堡垒机进行统一管理登录  
  
#  **五、** ** **恶意代码防范****

序号

|

要求项/控制点

|

是否满足

|

加固方法  
  
---|---|---|---  
  
1

|

应安装防恶意代码软件或加固具有相应功能的软件，并定期进行升级和更新防恶意代码库；

| |

查看当前杀毒软件，记录版本，是否升级为最新  
  
#  **六、** ** **数据备份恢复****

序号

|

要求项/控制点

|

是否满足

|

加固方法  
  
---|---|---|---  
  
1

|

应提供重要数据的本地数据备份与恢复功能；

| |

查看是否有备份文件，以及了解备份机制和恢复机制

若无，需要建立备份文件，进行每日增量、每周全量的备份策略。  
  
2

|

应提供异地数据备份功能，利用通信网络将重要数据定时批量传送至备用场地。

| |

将备份文件存放异地且确保其有效性，避免出现单点故障后不具备恢复的风险。  
  
#  **七、** ** **资源控制****

序号

|

要求项/控制点

|

是否满足

|

加固方法  
  
---|---|---|---  
  
1

|

应确保系统磁盘根分区已使用空间维持在80%以下。

| |

如果磁盘动态分区空间不足，建议管理员扩充磁盘容量  
  
2

|

应设置命令行界面超时退出

| |

以root账户执行，vi /etc/profile,增加 export
TMOUT=600(单位：秒，可根据具体情况设定超时退出时间，要求不小于600秒),注销用户，再用该用户登录激活该功能  
  
3

|

应限制远程登录IP范围

| |

检查/etc/hosts.allow配置

编辑/etc/hosts.allow  
增加一行 <service>: 允许访问的IP；举例如下：  
all:192.168.4.44:allow #允许单个IP；  
sshd:192.168.1.:allow #允许192.168.1的整个网段的PC通过SSH来访问本机  
重启进程：  
#/etc/init.d/xinetd restart

检查/etc/hosts.deny配置

编辑/etc/hosts.deny  
增加一行 all:all  
重启进程：  
#/etc/init.d/xinetd restart  
  
4

|

应配置用户所需最小权限

| |

配置/etc/passwd文件权限

chmod 644 /etc/passwd

配置/etc/group文件权限

chmod 644 /etc/group

配置/etc/shadow文件权限

chmod 600 /etc/shadow

