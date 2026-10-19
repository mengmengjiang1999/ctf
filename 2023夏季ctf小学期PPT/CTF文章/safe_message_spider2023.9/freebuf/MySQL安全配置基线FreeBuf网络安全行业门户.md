**实验测试版本：mysql5.7.35**

##  **一、数据备份**

 **描述**

数据库备份就是为了防止原数据丢失，保证数据的安全。当数据库因为某些原因造成部分或者全部数据丢失后，备份文件可以帮我们找回丢失的数据。因此，数据备份是很重要的工作。一般可采用本地备份和网络备份的形式，可采用MySQL本身自带的mysqldump的方式和直接复制备份形式。

 **参考配置操作**

定期对mysql进行异地备份。

##  **二、账户安全**

###  **2.1 删除默认数据库及账户**

 **描述**

MySQL 初始化后会自动生成空用户和 test 库，以进行安装时的测试，这些都是不需要的，有安全隐患，所以需要将他们全部删除。

 **参考配置操作**

在MySQL控制台中，执行查询数据库：

    
    
    mysql>use mysql;
    mysql>show databases;
    

![wKg0C2JQBbqADFKuAAAp784HJDg212.png](https://image.3001.net/images/20220516/1652681374_6281ea9e60044f45d6080.png!small)

然后将测试数据库删除。

 **注：此次实验版本无test数据库。**

    
    
    mysql> DROP DATABASE test;
    

### **2.2 删除匿名账户和废弃的账户**

 **描述**

依次检查所列出的账户是否为必要账户，删除无用户或过期账户。

DROP USER语句用于删除一个或多个MySQL账户。要使用DROP USER，必须拥有mysql数据库的全局CREATE
USER权限或DELETE权限。账户名称的用户和主机部分与用户表记录的User和Host列值相对应。

 **参考配置操作**

 **检侧操作：**  
mysql 查看所有用户的语句，输入指令

    
    
    select user();
    select user,host from mysql.user;
    

**注：此次实验版本无冗余账号。**

使用DROP USER，您可以取消一个账户和其权限，操作如下：

    
    
    DROP USER user;
    

该语句可以删除来自所有授权表的帐户权限记录。红色标识的无用账户都可以删除。

![wKg0C2JQBfWABTSLAAA7TQ7CYeI122.png](https://image.3001.net/images/20220516/1652681374_6281ea9e94bef30b97b52.png!small)

 **使用操作命令之后的结果**

    
    
    drop user ''@'mysql',''@'localhost','root'@'::1','root'@'mysql';
    

![wKg0C2JQBgSAFCgHAACNmeKj2js247.png](https://image.3001.net/images/20220516/1652681374_6281ea9ed6d3afcafb191.png!small)

### **2.3 默认账户（root）设置**

 **描述**

安装的 MySQL 的 root 用户默认是空密码，为了安全起见，需要把密码修改为强密码（包含数字、字母大小写、特殊字符，长度大于 8 个字符）。

MySQL 默认权限最高的用户是 root，由于其权限高，所以也是黑客最喜欢攻击的用户名，建议把 root 用户名改名。

 **注：此次测试为5.7.35版本，初始化后已经为复杂密码，非空密码。**

 **参考配置操作**

改变root的密码：

    
    
    mysql>use mysql;
    mysql>update mysql.user set authentication_string=password('sehidk12e342') where user='root';
    #或
    mysql>update user set authentication_string=password('zkSzf_Sg&2021')where user = 'root';
    mysql>flush privileges;
    mysql>exit;
    Bye
    #上面的sehidk12e342为root用户的密码，请更改密码为强密码
    

系统mysql的管理员名称是root，而一般情况下，数据库管理员都没进行修改，这一定程度上对系统用户穷举的恶意行为提供了便利，此时修改为复杂的用户名，请不要在设定为admin或者administraror的形式，因为它们也在易猜的用户字典中。

    
    
    mysql> update user set user="newroot" where user="root"; //改成不易被猜测的用户名
    mysql> flush privileges;
    

## **三、启用日志功能**

 **描述**

数据库应配置日志功能，启动Mysql的日志不仅可以为我们提供性能热点的分析，还可以帮助我们加固Mysql数据库的安全。

 **参考配置操作**

    
    
    mysql>show variables like '%log_%';查看所有的log命令 
    
    
    
    mysql> show variables like '%log_%';
    +--------------------------------------------+-------------------------------------------------+
    | Variable_name                              | Value                                           |
    +--------------------------------------------+-------------------------------------------------+
    | binlog_cache_size                          | 32768                                           |
    | binlog_checksum                            | CRC32                                           |
    | binlog_direct_non_transactional_updates    | OFF                                             |
    | binlog_error_action                        | ABORT_SERVER                                    |
    | binlog_format                              | ROW                                             |
    | binlog_group_commit_sync_delay             | 0                                               |
    | binlog_group_commit_sync_no_delay_count    | 0                                               |
    | binlog_gtid_simple_recovery                | ON                                              |
    | binlog_max_flush_queue_time                | 0                                               |
    | binlog_order_commits                       | ON                                              |
    | binlog_row_image                           | FULL                                            |
    | binlog_rows_query_log_events               | OFF                                             |
    | binlog_stmt_cache_size                     | 32768                                           |
    | binlog_transaction_dependency_history_size | 25000                                           |
    | binlog_transaction_dependency_tracking     | COMMIT_ORDER                                    |
    | expire_logs_days                           | 0                                               |
    | general_log_file                           | /usr/local/mysql/data/localhost.log             |
    | innodb_flush_log_at_timeout                | 1                                               |
    | innodb_flush_log_at_trx_commit             | 1                                               |
    | innodb_log_buffer_size                     | 16777216                                        |
    | innodb_log_checksums                       | ON                                              |
    | innodb_log_compressed_pages                | ON                                              |
    | innodb_log_file_size                       | 50331648                                        |
    | innodb_log_files_in_group                  | 2                                               |
    | innodb_log_group_home_dir                  | ./                                              |
    | innodb_log_write_ahead_size                | 8192                                            |
    | innodb_max_undo_log_size                   | 1073741824                                      |
    | innodb_online_alter_log_max_size           | 134217728                                       |
    | innodb_undo_log_truncate                   | OFF                                             |
    | innodb_undo_logs                           | 128                                             |
    | log_bin                                    | OFF                                             |
    | log_bin_basename                           |                                                 |
    | log_bin_index                              |                                                 |
    | log_bin_trust_function_creators            | OFF                                             |
    | log_bin_use_v1_row_events                  | OFF                                             |
    | log_builtin_as_identified_by_password      | OFF                                             |
    | log_error                                  | /var/log/mysqld.log                             |
    | log_error_verbosity                        | 3                                               |
    | log_output                                 | FILE                                            |
    | log_queries_not_using_indexes              | OFF                                             |
    | log_slave_updates                          | OFF                                             |
    | log_slow_admin_statements                  | OFF                                             |
    | log_slow_slave_statements                  | OFF                                             |
    | log_statements_unsafe_for_binlog           | ON                                              |
    | log_syslog                                 | OFF                                             |
    | log_syslog_facility                        | daemon                                          |
    | log_syslog_include_pid                     | ON                                              |
    | log_syslog_tag                             |                                                 |
    | log_throttle_queries_not_using_indexes     | 0                                               |
    | log_timestamps                             | UTC                                             |
    | log_warnings                               | 2                                               |
    | max_binlog_cache_size                      | 18446744073709547520                            |
    | max_binlog_size                            | 1073741824                                      |
    | max_binlog_stmt_cache_size                 | 18446744073709547520                            |
    | max_relay_log_size                         | 0                                               |
    | relay_log_basename                         | /usr/local/mysql/data/localhost-relay-bin       |
    | relay_log_index                            | /usr/local/mysql/data/localhost-relay-bin.index |
    | relay_log_info_file                        | relay-log.info                                  |
    | relay_log_info_repository                  | FILE                                            |
    | relay_log_purge                            | ON                                              |
    | relay_log_recovery                         | OFF                                             |
    | relay_log_space_limit                      | 0                                               |
    | slow_query_log_file                        | slow.log                                        |
    | sql_log_bin                                | ON                                              |
    | sql_log_off                                | OFF                                             |
    | sync_relay_log_info                        | 10000                                           |
    +--------------------------------------------+-------------------------------------------------+
    66 rows in set (0.00 sec)
    
    
    
    mysql>set global general_log_file=on;  //开启常规日志记录。
    
    mysql>show variables like 'general_log_file';查看常规日志开启情况的log命令
    
    +------------------+-------------------------------------+
    | Variable_name    | Value                               |
    +------------------+-------------------------------------+
    | general_log_file | /usr/local/mysql/data/localhost.log |
    +------------------+-------------------------------------+
    1 row in set (0.00 sec)
    

**注：set global general_log_file=on;
如果使用该方法设置的日志开启，当mysql服务重启后会失效，需要将以下两条参数添加到/etc/my.cnf文件中。**

    
    
    general_log_file = 1
    slow_query_log_file = localhost.log
    

## **四、安全补丁**

 **描述**

确保数据库版本为最新并修复已知的安全漏洞。攻击者可能会利用已知的漏洞对MySQL服务器进行攻击。

 **参考配置操作**

    
    
    mysql> show variables where variable_name like 'version';
    +---------------+--------+
    | Variable_name | Value  |
    +---------------+--------+
    | version       | 5.7.35 |
    +---------------+--------+
    1 row in set (0.00 sec)
    

显示当前的数据库版本，如果不是最新版本则安装最新版本的补丁或升级到最新版本。

##  **五、远程访问控制**

###  **5.1 禁用远程访问**

 **描述**

禁止网络连接，防止猜解密码攻击，溢出攻击和嗅探攻击。（仅限于应用和数据库在同一台主机）。

 **参考配置操作**

1.如果数据库不需远程访问，可以禁止远程tcp/ip连接：

通过在mysqld服务器中参数中添加 **\--skip-networking**
启动参数来使mysql不监听任何TCP/IP连接，增加安全性。强迫MySQL仅监听本机，方法是在my.cnf的 “[mysqld]” 部分增加下面一行：

    
    
    bind-address=127.0.0.1
    

在命令行netstat
-ant下看到，默认的3306端口是打开的，此时打开了mysqld的网络监听，允许用户远程通过帐号密码连接数本地据库，默认情况是允许远程连接数据的。为了禁止该功能，启动skip-networking，不监听sql的任何TCP/IP的连接，切断远程访问的权利，保证安全性。假如确实需要远程连接数据库，至少修改默认的监听端口，同时添加防火墙规则，只允许可信任的网络的mysql监听端口的数据通过。

    
    
    # vim /etc/my.cf
    将#skip-networking注释去掉。
    
    #/usr/local/mysql/bin/mysqladmin -u root -p shutdown //停止数据库
    #/usr/local/mysql/bin/mysqld_safe --user=mysql & //后台用mysql用户启动mysql
    

### **5.2 只允许某个IP进行远程访问**

 **描述**

限制远程访问，只允许某个IP地址访问数据库（应用和数据库不在同一台主机）。

 **参考配置操作**

检查是否存在host值为‘%’的账户，如果存在，删除该账户。

    
    
    mysql> select user,host from user;  //查询是否存在host值为‘%’的用户。
    +---------------+---------------+
    | user          | host          |
    +---------------+---------------+
    | newroot       | %             |
    | webuser       | 192.168.200.1 |
    | newroot       | localhost     |
    +---------------+---------------+
    3 rows in set (0.00 sec)
    
    mysql> drop user newroot@'%';       //删除用户
    mysql> flush privileges;            //刷新缓存
    

**命令如下：**

    
    
    mysql>GRANT ALL PRIVILEGES ON *.* TO 'webuser'@'192.168.200.1' IDENTIFIED BY 'sehidk12e342';#sehidk12e342为密码
    mysql>flush privileges;
    

## **六、权限控制**

###  **6.1 禁止 MySQL 对本地文件的读取**

 **描述**

禁用”LOAD DATA LOCAL
INFILE”命令，这有助于防止非授权用户访问本地文件。在PHP应用程序中发现有新的SQL注入漏洞时，这样做尤其重要。此外，在某些情况下，LOCAL
INFILE命令可被用于访问操作系统上的其它文件(如/etc/passwd)，若黑客读取 **`/etc/passwd`** 文件将非常危险。

 **参考配置操作**

 **应使用下面的命令：**

    
    
    mysql> SELECT load_file("/etc/passwd");
    
    
    
    mysql>load data local infile "/etc/passwd" into table teacher FIELDS TERMINATED BY '\n'; //读取/etc/passwd并导入到teacher表里。
    Query OK, 9 rows affected, 45 warnings (0.00 sec)
    Records: 9  Deleted: 0  Skipped: 0  Warnings: 45
    
    mysql> select * from teacher;  //查询表teacher内所有数据，已经读取到数据。
    +-----------+----------+------------+------------+------------------+
    | teacherno | tname    | major      | prof       | department       |
    +-----------+----------+------------+------------+------------------+
    | games:    | ftp:x:14 | nobody:x:9 | systemd-ne | dbus:x:81:81:Sys |
    | gluste    | saslauth | abrt:x:173 | setroubles | rtkit:x:172:172: |
    | ntp:x:    | gdm:x:42 | gnome-init | sshd:x:74: | avahi:x:70:70:Av |
    | polkit    | sssd:x:9 | libstorage | rpc:x:32:3 | colord:x:996:993 |
    | postfi    | tcpdump: | webuser:x: | mysql:x:98 |                  |
    | pulse:    | chrony:x | rpcuser:x: | nfsnobody: | unbound:x:991:98 |
    | root:x    | bin:x:1: | daemon:x:2 | adm:x:3:4: | lp:x:4:7:lp:/var |
    | sync:x    | shutdown | halt:x:7:0 | mail:x:8:1 | operator:x:11:0: |
    | tss:x:    | usbmuxd: | geoclue:x: | radvd:x:75 | qemu:x:107:107:q |
    +-----------+----------+------------+------------+------------------+
    9 rows in set (0.00 sec)
    

打开编辑/etc/my.cnf，添加local -infile=0。重新启动MySQL服务。

 **再次测试：**

    
    
    mysql> load data local infile "/etc/passwd" into table teacher FIELDS TERMINATED BY '\n';
    ERROR 1148 (42000): The used command is not allowed with this MySQL version
    mysql>
    

### **6.2 数据库目录权限控制**

 **描述**

默认的mysql是安装在/usr/local/mysql，而对应的数据库文件在/usr/local/mysql/var目录下，因此，必须保证该目录不能让未经授权的用户访问后把数据库打包拷贝走了，所以要限制对该目录的访问。确保mysqld运行时，只使用对数据库目录具有读或写权限的linux用户来运行。

 **参考配置操作**

    
    
    # chown -R root  /usr/local/mysql/  //mysql主目录给root
    # chown -R mysql.mysql /usr/local/mysql/var //确保数据库目录权限所属mysql用户
    

### **6.3 普通用户的数据库最小特权**

 **描述**

有些应用程序是通过一个特定数据库表的用户名和口令连接到MySQL的，安全人员不应当给予这个用户（普通用户）完全的访问权。  
如果攻击者获得了这个拥有完全访问权的用户，他也就拥有了所有的数据库。查看一个用户许可的方法是在MySQL控制台中使用命令SHOW GRANT

 **参考配置操作**

    
    
    >SHOW GRANTS FOR 'newroot'@'localhost';//查看newroot账户在本机授权访问情况。
    为定义用户的访问权，使用GRANT命令。在下面的例子中，newroot仅能从test数据库的user表中选择：
    > GRANT SELECT ON test.user TO 'newroot'@'localhost';
    > FLUSH PRIVILEGES;
    newroot用户就无法改变数据库中这个表和其它表的任何数据。
    如果你要从一个用户移除访问权，就应使用一个与GRANT命令类似的REVOKE命令：
    > REVOKE SELECT ON test.user FROM 'newroot'@'localhost';
    > FLUSH PRIVILEGES;
    

**权限**|  **权限范围**|  **给谁授权**|  **权限范围**  
---|---|---|---  
 **grant all**|  **ON ** **.**|  **to newroot**|  **授权newroot全库权限**  
 **grant select**|  **ON test.** *|  **to newroot**|  **授权newroot唐古拉数据库查看权限**  
 **grant create**|  **ON test.** *|  **to newroot**|  **授权newroot唐古拉数据库添加权限**  
  
 **授权并创建用户，并指定密码。**

    
    
    mysql>grant 权限 on 权限范围  to 用户 identified by '密码';
    例如：
    mysql>grant all on test  to mysql identified by 'sehidk12e342';
    

* * *

**回收权限**

    
    
    revoke 权限 on 范围 from 用户
    例如：
    revoke all on mysql from root@'192.168.1.3';
    

### **6.4 删除和禁用.mysql_history文件**

 **描述**

 **我们使用过的 shell 命令，都会保存在`~/.bash_history`里，通过 h**`istory`命令可以获得当前用户最近输入的 1000
条命令。虽然前面我们登陆数据库没有直接使用密码，但是以防万一，还是建议清空 **`~/.bash_history`** 文件。

数据库相关的shell操作命令都会分别记录在.bash_history，如果这些文件不慎被读取，会导致数据库密码和数据库结构等信息泄露，而登陆数据库后的操作将记录在.mysql_history文件中，如果使用update表信息来修改数据库用户密码的话，也会被读取密码，因此需要删除这两个文件，同时在进行登陆或备份数据库等与密码相关操作时，应该使用-p参数加入提示输入密码后，隐式输入密码，建议将以上文件置空。

 **参考配置操作**

    
    
    #cd ~    //打开HOME文件夹
    # rm .bash_history .mysql_history  //删除历史记录
    或者
    # cat /dev/null .bash_history   //将shell记录文件置空
    # cat /dev/null .mysql_history  //将mysql记录文件置空
    

> **通过`mysql -uroot -p`登陆 MySQL 是一个良好的习惯。**

###  **6.5 禁止以root用户权限启动mysqld系统进程**

 **描述**

以普通帐户安全运行mysqld，禁止mysql以root帐号权限运行，攻击者可能通过mysql获得系统root超级用户权限，完全控制系统。为数据库建立独立的linux中的mysql账户，该账户用来只用于管理和运行MySQL。

 **参考配置操作**

检查进程属主和运行参数是否包含--user=mysql类似语句：

    
    
    [root@localhost mysql]# ps -ef|grep mysql
    root       6870      1  0 19:42 pts/0    00:00:00 /bin/sh /usr/local/mysql/bin/mysqld_safe --datadir=/usr/local/mysql/data --pid-file=/tmp/mysqld/mysqld.pid
    mysql      7121   6870  5 19:42 pts/0    00:00:00 /usr/local/mysql/bin/mysqld --basedir=/usr/local/mysql --datadir=/usr/local/mysql/data --plugin-dir=/usr/local/mysql/lib/plugin --user=mysql --log-error=/var/log/mysqld.log --pid-file=/tmp/mysqld/mysqld.pid --socket=/tmp/mysql.sock --port=3306
    root       7161   3033  0 19:42 pts/0    00:00:00 grep --color=auto mysql
    [root@localhost mysql]#
    

**注：mysqld_safe是一个启动脚本，间接引用mysqld。在启动mysqldsafe脚本时，在启动MySQL服务器进程时，同时会启动一个守护进程，作用是监控mysqld。**

如mysqld服务挂了后，会立即重启一个mysqld服务。

另外，mysqld_safe启动方式也会把运行过程的报错日志和其它一些诊断信息输出到某一个文件中，这样方便我们排查解决问题。这个启动方式是最常用的方式。

###  **6.6 secure_file_priv参数应该为NULL**

 **描述**

secure_file_priv值不是NULL的时候可以通过数据库对服务器写入shell，因此需要将该参数值设置为NULL。

secure_file_priv 为 /tmp 时，表示限制mysqld只能在/tmp目录中执行导入导出，其他目录不能执行。

secure_file_priv 没有值时，表示不限制mysqld在任意目录的导入导出。

查看 secure_file_priv 的值，默认为NULL，表示限制不能导入导出。

 **参考配置操作**

登录mysql后输入以下命令查看：

    
    
    mysql> show variables like 'secure_file_priv';
    +------------------+-------+
    | Variable_name    | Value |
    +------------------+-------+
    | secure_file_priv | NULL  |
    +------------------+-------+
    1 row in set (0.00 sec)
    

**注：该实验版本的mysql默认配置参数secure_file_priv值为NULL，不需要做修改。**

##  **七、修改mysql的端口**

 **描述**

  * 使用默认端口，会更容易被黑客在网络中发现数据库，改成其他端口有助于隐藏数据库，对mysql端口的修改可以从一定程度上防止端口扫描工具的扫描，防止被黑客入侵。
  * windows下可以修改配置文件my.ini来实现，linux可以修改配置文件my.cnf来实现。

 **参考配置操作**

输入以下命令查看mysql默认端口号是不是3306：

    
    
    [root@localhost mysql]#cat /etc/my.cnf |grep 'port'
    port=3306
    [root@localhost mysql]#
    

**如果是3306则修改默认端口：**

  1. 修改配置文件vi /etc/my.cnf，

    
    
    port=5618 （除3306以外的较大值端口）
    

  2. 重启mysql服务

    
    
    [root@localhost mysql]# service mysql restart
    Shutting down MySQL.. SUCCESS! 
    Starting MySQL. SUCCESS! 
    [root@localhost mysql]#﻿

