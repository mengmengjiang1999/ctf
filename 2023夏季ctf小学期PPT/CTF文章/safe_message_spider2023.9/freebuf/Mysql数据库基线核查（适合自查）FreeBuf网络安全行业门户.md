# **一、** ** **身份鉴别****

###  ** **1.1**** **
**应提供用户身份标识唯一和鉴别信息复杂度检查功能，保证应用系统中不存在重复用户身份标识，身份鉴别信息不易被冒用****

A.应按用户分配账号，避免不同用户间共享账号

B.检查是否存在匿名账户：

mysql>use mysql;

mysql>delete from user where User = '';

mysql> flush privileges;

C.检查是否存在空密码：若存在则执行

修改帐户弱密码 如要修改密码，执行如下命令：

mysql> update user set password=password('新密码') where user='root'; mysql>
flush privileges;

 **检查是否存在空密码(版本5.7)在MySQL5.7之前**
，User表中的口令字段为Password，从MySQL5.7开始，口令字段变成了authentication_string。

D.应该更改默认管理原账号，防止对系统用户穷举的恶意行为

mysql> update user set user="newname" where user="root";

mysql> flush privileges; newname为管理员账号的新名称，改成不易被猜测的用户名。

#  **二、** ** **访问控制****

###  ** **2.1应提供访问控制功能，依据安全策略控制用户对文件、数据库表等客体的访问****

A.检查是否删除测试安装的test库（应该删除进行安装测试的test库）

mysql> show databases;

mysql> drop database test; mysql> flush privileges;

 **检查是否禁止mysql对本地文件存取**

应禁止mysql对本地文件存取

方法一：在my.cnf的mysql字段下加local-infile=0

方法二：启动mysql时加参数local-infile=0 /etc/init.d/mysql start --local-infile=0
假如需要获取本地文件，需要打开此功能，但出于安全考虑建议关闭 重新打开命令/etc/init.d/mysql start --local-infile=1
修改后需要重新启动mysql 备注：可通过mysql --help 命令提示查询my.cnf路径

 **检查是否禁止mysql以管理员账号权限运行**

方法一：启动mysql 时加上--user=user-name eg: /etc/init.d/mysql start --user=user-name

方法二：在mysql安装目录下，修改配置文件my.cnf(使用rpm包安装的请修改安装目录下的my-medium.cnf文件)中[mysqld]配置段中添加user=mysql。

#  **三、** ** **安全审计****

###  ** **3.1应提供覆盖到每个用户的安全审计功能，对应用系统重要安全事件进行审计****

A.检查是否配置日志功能

B.检查是否配置错误日志

参考配置操作

  * 在mysql的安装目录下，修改my.cnf配置文件，增加log_error = /home/mysql.err
  * 重启mysql，可执行命令/etc/init.d/mysql restart 补充说明：具体log_error存放路径请参照自身环境配置。

C.检查是否配置通用查询日志

参考配置操作

  * 在mysql的安装目录下，修改my.cnf配置文件，增加general_log = 1
  * 重启mysql，可执行命令/etc/init.d/mysql restart 备注：可通过mysql --help 命令提示查询my.cnf路径。

  1. 检查是否配置慢查询日志

参考配置操作

(1) 在mysql的安装目录下，修改my.cnf配置文件，增加slow_query_log = 1 (2)
重启mysql，可执行命令/etc/init.d/mysql restart 备注：可通过mysql --help 命令提示查询my.cnf路径。

E.检测是否配置更新日志

参考配置操作

(1) 在my.cnf的mysqld 下面添加 log_slave_updates

(2) 重启mysql，可执行命令/etc/init.d/mysql restart 备注：可通过mysql --help 命令提示查询my.cnf路径。

F.检查是否配置二进制日志

参考配置操作

  * 在mysql的安装目录下，修改my.cnf配置文件，增加log_bin = mysql-bin (2) 重启mysql，可执行命令/etc/init.d/mysql restart 5.7.3以后的版本，修改my.cnf配置文件，在【mysqld】下增加log_bin = 文件名 server_id = 序列号。

#  ** **四、恶意代码防范****

###  ** **4.1应安装防恶意代码软件或加固具有相应功能的软件，并定期进行升级和更新防恶意代码库****

安装最新补丁，确保系统安装了最新的安全补丁。

注意： 在保证业务及网络安全的前提下，并经过兼容性测试后，安装更新补丁。

#  ** **五、资源控制****

###  ** **5**** ** **.1应提供覆盖到每个用户的安全审计功能，对应用系统重要安全事件进行审计****

A.应能够对一个访问帐户或一个请求进程占用的资源分配最大限额和最小限额

根据机器性能和业务需求，设置最大连接数，在mysql的安装目录下，在my.cnf中在[mysqld]配置段添加： max_connections =
1000，重启mysql服务 备注：可通过mysql --help 命令提示查询my.cnf路径。

#  ** **六、数据备份恢复****

###  ** **6.1应提供重要数据的本地数据备份与恢复功能****

查看是否有备份文件，以及了解备份机制和恢复机制

若无，需要建立备份文件，进行每日增量、每周全量的备份策略。

###  ** **6.2应提供异地数据备份功能，利用通信网络将重要数据定时批量传送至备用场地****

将备份文件存放异地且确保其有效性，避免出现单点故障后不具备恢复的风险。

