### **一、身份鉴别**

####  **1.1 应对登录的用户进行身份标识和鉴别，身份标识具有唯一性，身份鉴别信息具有复杂度要求并定期更换；**

建议操作系统对登录的用户进行身份标识和鉴别，身份鉴别信息配置复杂度要求开启定期更换策略，避免使用弱口令，至少包含字母和数字，密码长度至少8位。密码最长使用90天，5次内不重复。整改方案如下：

  * 1.修改 /etc/login.defs 文件内容即可，加入如下

    
    
    # 密码最大有效期PASS_MAX_DAYS   90# 两次修改密码的最小间隔时间PASS_MIN_DAYS   1# 密码最小长度，对于root无效PASS_MIN_LEN    8# 密码过期前 7 天开始提示PASS_WARN_AGE   7

  * 2.对于密码的强度要求可以修改system-auth文件，vim /etc/pam.d/system-auth，修改如下：

    
    
    # 添加以下内容password    requisite     pam_cracklib.so retry=5 difok=3 minlen=10 ucredit=-1 lcredit=-3 dcredit=-3 dictpath=/usr/share/cracklib/pw_dict# remember=5 5次内密码不重复# retry=3 输入错误重试3次# difok=3 # minlen=10表示最小密码长度为 10 类型数量# ucredit=-1表示密码必须至少包含1个大写字母# lcredit=-3表示密码必须至少包含3个小写字母# dcredit=-3表示密码必须至少包含3个数字

####  **1.2 应具有登录失败处理功能，应配置并启用结束会话、限制非法登录次数和当登录连接超时自动退出等相关措施；**

1.登录失败 建议操作系统开启登录失败处理功能配置登录失败5次及锁定时间30分钟；输入命令vim /etc/pam.d/system-auth

    
    
    # 添加以下内容auth        required      pam_tally2.so onerr=fail deny=5 unlock_time=1800 even_deny_root root_unlock_time=1800# 参数含义： 密码错误 5 次锁定 1800 秒

  * 2.会话过期，修改 /etc/profile 文件，输入命令vim /etc/profile

    
    
    # 单位秒 1800秒export TMOUT=1800source /etc/profile

###  **二、访问控制**

####  **2.1 应对登录的用户分配账户和权限；**

建议操作系统对登录的用户分配账户和权限；整改方案：组 系统表示 作用 数据库 db 只负责管理数据库的用户 服务 server 负责业务服务或其他组件的用户
安全 security 负责系统安全，日志审计登的用户，命令如下：

    
    
    #列出所有组cat /etc/group# 删除组groupdel xulei# 添加组groupadd  dbgroupadd  servergroupadd  security# 查看所有用户cat /etc/passwd# 查看用户所属组groups db# 删除用户userdel -rf xulei# 添加用户到某个组，并指定用户的所属目录useradd xulei -d /home/users/xulei –N# 改变用户组usermod -g db xulei# 修改文件属性只能某个组的成员操作chown :server /home/server# 修改密码passwd xulei# 用户名  所属组  密码dbuser  db  Dbuser@2021secuser  security  Secuser@2021serveruser  server  Serveruser@2021

####  **2.2 修改root的默认账户信息**

    
    
    # 修改用户名，这种修改不能修改rootusermod -l 新用户  旧用户# 如下可以修改root账号1、vim /etc/passwd 将第一行的第一个root替换为重命名的用户2、vim /etc/shadow 将这一行中的root 替换为重命名# 密码为：SuperAdmin@2021# 三、安全审计# 3.1 应启用安全审计功能，审计覆盖到每个用户，对重要的用户行为和重要安全事件进行审计；# 建议操作系统启用安全审计功能，审计覆盖到每个用户，对重要的用户行为和重要安全事件进行审计；# 整改方案：service auditd start# 查看是否开启，只要enable=1即可，这个 – 有问题 需要在命令行自己重新打auditctl –s# 同时根据需求可以添加新规则vim /etc/audit/audit.rules# 监控 /etc/my.cnf 文件，只要在文件加入以下内容-w /etc/my.cnf  -p wa# -w 路径 # -p 权限  如果没有 -p 选项，则默认监视所有动作 rwxa(读、写、执行、修改文件属性)# -k 关键字# 监控系统调用行为，监视文件权限变化，因为改变权限必须调用umask-a entry,always -S umask -S chown# -a always 总是记录审计；none 不记录；exit 行为完成后记录审计；entry 行为刚刚开始                                                                                         时记录审计# -S 系统调用名称 # -F 字段=值 # -k 关键字

####  **三、安全审计**

####  **3.2 审计记录应包括事件的日期和时间、用户、事件类型、事件是否成功及其他与审计相关的信息；**

#### 建议操作系统启用安全审计功能审计记录包括事件的日期和时间、用户、事件类型、事件是否成功及其他与审计相关的信息；

    
    
    # 整改方案：# 包含了以上所有条件cat /var/log/audit/audit.log

####  **3.3 应对审计记录进行保护，定期备份，避免受到未预期的删除、修改或覆盖等；**

建议操作系统启用安全审计功能并部署日志审计系统并对审计记录进行保护，定期备份，避免受到未预期的删除、修改或覆盖等；

    
    
    # 整改方案：# 输入以下脚本，并添加到定时器中#!/bin/bash# 日志位置FILE=/var/log/audit/audit.logcurrent_time=`date +%y%m%d`cat $FILE |while  read LINEdoUdate=`echo $LINE|awk -F'[(.]+'  '{print $2}'`#Udate=`echo $LINE|awk -F. '{print $1}' | awk -F'(' '{print $2}'`Cdate=`date -d @$Udate`echo $LINE|sed "s/[0-9]\{10\}/$Cdate/"  >> /home/sh/log/audit${current_time}.logdone

####  **3.4 应对审计进程进行保护，防止未经授权的中断。**

建议操作系统启用安全审计功能对审计进程进行保护，防止未经授权的中断，限制除审计员外的审计控制权限。

    
    
    # 整改方案：# 给输出的日志只允许 security 组可读即可。# 其他日志方式vi /etc/syslog.conf 加入 # The authpriv file has restricted access. authpriv.* /var/log/secure # 开启安全日志，日志文件位置/var/log/secure # 没有 syslog.conf 文件，只有 rsyslog.conf。rsyslog.conf 本身就具有该语句# 修改所属组chown :security /var/log

###  **四、入侵防范**

####  **4.1 应遵循最小安装的原则，仅安装需要的组件和应用程序；**

建议操作系统遵循最小安装的原则，仅安装需要的组件和应用程序；整改方案：按照部署方案，删除每台机器上多余的应用即可。

####  **4.2 应关闭不需要的系统服务、默认共享和高危端口；**

建议操作系统关闭不需要的系统服务、默认共享和高危端口，如FTP、DHCP等不必要服务，整改方案：FTP
目前不能关闭还需要上传文件，还有根据部署方案多余的都可以关闭。systemctl list-units 查看所有服务 快照 建议
备份半年，可以登录到物理机上配分。

####  **4.3 设置登录地址限制(重启生效)，通过设定终端接入方式、网络地址范围等条件限制终端登录；**

    
    
    # 修改文件vi /etc/hosts.allow# 加入如下sshd:10.1.10.11:allow# 允许这个段 使用 telnet访问in.telnetd:192.168.1.2#修改文件vi /etc/hosts.deny# 修改如下sshd:all:deny示例允许 10.1.10.11  ssh登录系统有效，优先级为先检查 hosts.deny , hosts.allow 后者设定可越过前者限制 在 hosts.deny 中加入 sshd:all:deny。在 Hosts.allow 加入允许的 ip 或者 ip 网段 sshd:ip:allow。

####  **4.4 高危端口管理**

    
    
    # 永久禁用，需要重启生效# 用 iptables 来控制端口和防火墙管理yum install iptables-services# 设置开机自启动systemctl enable iptables# 启动停止命令systemctl [stop|start|restart] iptables# 状态查看service iptables status# 禁用端口# 先打开文件编辑vim /etc/sysconfig/iptables# 添加禁止端口访问-A INPUT -p tcp --dport 445 -j DROP-A INPUT -p tcp --dport 139 -j DROP-A INPUT -p tcp --dport 3389 -j DROP# 查看开放端口iptables -nL# -A 参数就看成是添加一条 INPUT 或 OUTPUT 的规则。# -p 指定是什么协议 我们常用的tcp 协议，当然也有udp 例如53端口的DNS，到时我们要配置DNS用到53端口 大家就会发现使用udp协议的。# --dport 就是目标端口，当数据从外部进入服务器为目标端口(INPUT)，反之数据从服务器出去(OUTPUT)，则为数据源端口使用 --sport# -j 就是指定是 ACCEPT 接收 或者 DROP 不接收# 禁止IP访问-A INPUT -p tcp -s 192.168.1.2 -j DROP# 我们就用 -p tcp , 如果是 udp 就写udp，这里就用tcp了， -s就是 来源的意思，# ip来源于 192.168.1.2 ，-j 怎么做 我们拒绝它 这里应该是 DROP# 快速生效方式，也会添加到文件中(不建议)# 禁用端口访问/sbin/iptables -A INPUT -p tcp --dport  8080 -j DROP/sbin/iptables -A OUTPUT -p tcp --sport  8080 -j DROP# 允许端口/sbin/iptables -A INPUT -p tcp --dport  8080 -j ACCEPT/sbin/iptables -A OUTPUT -p tcp --sport  8080 -j ACCEPT# 禁用IP访问，可以ping通 但无法通过shh访问/sbin/iptables -A INPUT -p tcp -s 192.168.200.16 -j DROP# 保存到文件,会改变默认规则，所有端口可以访问service iptables save# 基础设置# 禁止所有端口访问，但允许22 端口访问,因为是立即生效，最好使用主机修改iptables -P INPUT ACCEPTiptables -P FORWARD DROPiptables -P OUTPUT ACCEPT-A INPUT –m state --state RELATED,ESTABLISHED –j ACCEPT-A INPUT –p icmp –j ACCEPT-A INPUT –i lo –j ACCEPT-A INPUT –p tcp –m state --state NEW –m tcp --dport 22 –j ACCEPT-A INPUT –j REJECT --reject-with icmp-host-prohibited-A FORWARD –j REJECT --reject-with icmp-host-prohibited# 清除规则# 先查看行号iptables -nL --line-number# 删除iptables -D INPUT 1# -D 是删除的意思# INPUT 指定删除INPUT的规则# 1 是行号# 注意事项，需要关闭firewalld# systemctl status firewalld# systemctl stop firewalld#systemctl disable firewalld  
    

