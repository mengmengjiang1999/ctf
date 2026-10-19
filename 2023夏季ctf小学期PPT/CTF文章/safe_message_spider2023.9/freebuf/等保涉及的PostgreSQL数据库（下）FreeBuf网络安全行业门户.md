文章仅代表个人观点，有更好的想法欢迎在评论区沟通。

之前文章：[等保2.0涉及的PostgreSQL数据库（上）](https://www.freebuf.com/articles/system/244463.html)、[等保2.0涉及的PostgreSQL数据库（中）](https://www.freebuf.com/articles/network/244882.html)

## 一、访问控制

### 1\. 应及时删除或停用多余的、过期的账户，避免共享账户的存在

查看当前已有账户，询问管理员是否存在多余过期账户![](https://image.3001.net/images/20201109/1604885764_5fa89d0440d9d761e650a.png!small)![](https://image.3001.net/images/20201109/1604885774_5fa89d0edc14ee005e9b3.png!small)

### 2\. 应授予管理用户所需的最小权限，实现管理用户的权限分离

这个管理用户的权限分离，像安全设备那种的三权分立用户，个人认为数据库层面不太好实现，一般不符合，要不就询问客户取证。

### 3\. 应由授权主体配置访问控制策略，访问控制策略规定主体对客体的访问规则

确认各用户的操作权限，例如：赋予zfy角色所有表的查询权限

![](https://image.3001.net/images/20201109/1604886021_5fa89e057206440043ad0.png!small)

然后查询这个用户对应表的权限，就均拥有了select权限。

![](https://image.3001.net/images/20201109/1604886028_5fa89e0c5470245f673cc.png!small)这里的授权主体一般为数据库管理员，对应的账户postgres，然后给zfy这个账户授予了select权限，也就是访问控制规则了。

### 4\. 访问控制的粒度应达到主体为用户级或进程级，客体为文件、数据库表级

这个感觉是流氓条款。。。不知道我的理解对不对

看字面意识就是要主体为用户，客体为数据库表级？所以就是需要每一张表单独给用户授权，不能授权整个库或者全局权限，就是权限这块需要做的更细致，这个感觉一般都做不到。

查看访问控制策略规则，确认是否达到用户级、数据库表级。

如果有多个角色super之类的肯定不符合，这样粒度就不是表级了。

### 5\. 应对重要主体和客体设置安全标记，并控制主体对有安全标记信息资源的访问

敏感标记，这个数据库应该没有自带这个功能。

  

## 二、安全审计

### 1\. 应启用安全审计功能，审计覆盖到每个用户，对重要的用户行为和重要安全事件进行审计

PostgreSQL有3种日志：

  * pg_log（数据库运行日志） 内容可读 默认关闭的，需要设置参数启动

  * pg_xlog（WAL 日志，即重做日志） 内容一般不具有可读性 强制开启

  * pg_clog（事务提交日志，记录的是事务的元数据） 内容一般不具有可读性 强制开启

1.1 pg_log

作用：
这个日志一般是记录服务器与DB的状态，比如各种Error信息，定位慢查询SQL，数据库的启动关闭信息，发生checkpoint过于频繁等的告警信息，诸如此类。该日志有.csv格式和.log。建议使用.csv格式，因为它一般会按大小和时间自动切割，毕竟查看一个巨大的日志文件比查看不同时间段的多个日志要难得多。pg_log是可以被清理删除，压缩打包或者转移，同时并不影响DB的正常运行。当我们有遇到DB无法启动或者更改参数没有生效时，第一个想到的就是查看这个日志。

日志配置文件

在$PGDATA/postgresql.conf文件：

![](https://image.3001.net/images/20201109/1604886760_5fa8a0e87fda11c871432.png!small)

![](https://image.3001.net/images/20201109/1604886768_5fa8a0f01b574210698b9.png!small)

涉及的参数：

涉及的参数有：

logging_collector --是否开启日志收集开关，默认off，开启要重启DB

log_destination --日志记录类型，默认是stderr，只记录错误输出

log_directory --日志路径，默认是$PGDATA/pg_log, 这个目录最好不要和数据文件的目录放在一起,
目录需要给启动postgres的操作系统用户写权限.

log_filename --日志名称，默认是postgresql-%Y-%m-%d_%H%M%S.log

log_file_mode －－日志文件类型，默认为0600

log_truncate_on_rotation
－－默认为off，设置为on的话，如果新建了一个同名的日志文件，则会清空原来的文件，再写入日志，而不是在后面附加。

log_rotation_age --保留单个文件的最大时长,默认是1d,也有1h,1min,1s,个人觉得不实用

log_rotation_size --保留单个文件的最大尺寸，默认是10MB

log_error_verbosity －－默认为default，verbose表示冗长的

log_connections --用户session登陆时是否写入日志，默认off

log_disconnections --用户session退出时是否写入日志，默认off

  

1.2 px_log

代表WAL日志，即重做日志

作用：这个日志是记录的Postgresql的WAL信息，也就是一些事务日志信息(transaction
log)。默认单个大小是16M，源码安装的时候可以更改其大小（./configure --with-wal-segsize=target_value
参数，即可设置）这些日志会在定时回滚恢复(PITR)， 流复制(Replication
Stream)以及归档时能被用到，这些日志是非常重要的，记录着数据库发生的各种事务信息，不得随意删除或者移动这类日志文件，不然你的数据库会有无法恢复的风险

WAL：PostgreSQL在将缓存的数据刷入到磁盘之前，先写日志, 这就是PostgreSQL WAL ( Write-Ahead Log
)方式，也就是预写日志方式

日志目录：

在$PGDATA目录下

![](https://image.3001.net/images/20201109/1604886948_5fa8a1a43bcb4ea8b578d.png!small)![](https://image.3001.net/images/20201109/1604886958_5fa8a1ae35f3a18eea193.png!small)

不可读

![](https://image.3001.net/images/20201109/1604886970_5fa8a1ba9e1fbc0694962.png!small)

1.3 pg_clog

pg_clog这个文件也是事务日志文件，但与pg_xlog不同的是它记录的是事务的元数据(metadata)，这个日志告诉我们哪些事务完成了，哪些没有完成。这个日志文件一般非常小，但是重要性也是相当高，不得随意删除或者对其更改信息。

![](https://image.3001.net/images/20201109/1604887017_5fa8a1e96a320fba5dd20.png!small)

1.4 等保查看点

那么在我们测评的时候，一般会查询以下参数：

1）开启数据库运行日志（pg_log）收集

show logging_collector; --是否开启日志收集，默认off

![](https://image.3001.net/images/20201109/1604887100_5fa8a23c2a45c5f78f1fc.png!small)

2）其他一些日志配置

show log_destionation; --日志记录类型，默认是stderr，只记录错误输出

![](https://image.3001.net/images/20201109/1604887135_5fa8a25f0ae8b59dfda49.png!small)

show log_directory; --日志路径，默认是$PGDATA/pg_log

![](https://image.3001.net/images/20201109/1604887164_5fa8a27c95bafdc878d02.png!small)

show log_filename; --日志名称，默认是postgresql-%Y-%m-%d_%H%M%S.log

![](https://image.3001.net/images/20201109/1604887183_5fa8a28fd17d4a19ba5e2.png!small)

show log_connections; --用户session登录时是否写入日志，默认off

![](https://image.3001.net/images/20201109/1604887215_5fa8a2afbe786e3883ef2.png!small)

show log_disconnections; --用户session退出时是否写入日志，默认off

![](https://image.3001.net/images/20201109/1604887243_5fa8a2cb4278bb61825e9.png!small)

show log_statement; --记录用户登录数据库后的各种操作

![](https://image.3001.net/images/20201109/1604887268_5fa8a2e475723aa7fd8d7.png!small)

log_statement参数值：

none，不记录

ddl，记录create，drop，和alter

mod，记录ddl+insert，delete，update和truncate

all，mod+select

### 2\. 审计记录应包括事件的日期和时间、用户、事件类型、事件是否成功及其他与审计相关的信息

2.1 查看数据库当前时间

![](https://image.3001.net/images/20201109/1604887941_5fa8a58525360d2f94809.png!small)

2.2 查看日志文件

1） 查看$PGDATA目录postgresql文件

log_line_prefix参数

![](https://image.3001.net/images/20201109/1604888035_5fa8a5e386609b9b9c266.png!small)

也可使用命令查看

![](https://image.3001.net/images/20201109/1604888053_5fa8a5f5dd05ade0ba16c.png!small)

2）位置：在$PGDATA目录下的：

![](https://image.3001.net/images/20201109/1604888105_5fa8a62905010a750ebc4.png!small)

查看其中一条日志，默认包含事件的时间、日期、主客体标识等：

![](https://image.3001.net/images/20201109/1604888249_5fa8a6b97a2388f08f997.png!small)

### 3\. 应对审计记录进行保护，定期备份，避免受到未预期的删除、修改或覆盖等

1）查看存储在本机的日志文件权限

查看log_file_mode参数：

![](https://image.3001.net/images/20201109/1604888370_5fa8a732cd533ecbf7b4f.png!small)

在操作系统本地生成的也就是600权限

![](https://image.3001.net/images/20201109/1604888435_5fa8a7737b8c3f68aeff4.png!small)

  

2）本机轮替规则

查看 log_truncate_on_rotation参数，需为开启状态

![](https://image.3001.net/images/20201109/1604888529_5fa8a7d171982a0161b05.png!small)

再查看log_filename参数，默认参数如下：

![](https://image.3001.net/images/20201109/1604888551_5fa8a7e799e9ff38f97e1.png!small)

产生的日志文件，每天产生一个，不轮替：

![](https://image.3001.net/images/20201109/1604888595_5fa8a8133b3219784af4d.png!small)

为了让日志文件自动覆盖，达到保留多少日志的目的，可以进行如下设置：

log_truncate_on_rotation = on

log_filename = 'postgresql-%I.log' #最多保存12小时的日志,每小时一个文件

log_filename = 'postgresql-%H.log' #最多保存24小时的日志,每小时一个文件

log_filename = 'postgresql-%w.log' #最多保存一周的日志,每天一个文件

log_filename = 'postgresql-%d.log' #最多保存一个月的日志,每天一个文件

log_filename = 'postgresql-%j.log' #最多保存一年的日志,每天一个文件

3）备份

现场核查用户是否有备份措施，日志保存时间是否达到6个月以上。

###

  

### 4\. 应对审计进程进行保护，防止未经授权的中断

审计进程的开关：

1）super权限账户

无法直接关闭，需要重启服务才行

![](https://image.3001.net/images/20201109/1604898592_5fa8cf20192fd9c5942ca.png!small)

其他一些参数能修改

![](https://image.3001.net/images/20201109/1604898689_5fa8cf81e2192d9948ac2.png!small)

2）普通账户无权限

![](https://image.3001.net/images/20201109/1604898759_5fa8cfc7979464bb7cd92.png!small)

给他授权super权限账户后即可

![](https://image.3001.net/images/20201109/1604898782_5fa8cfde91a176be4bb9b.png!small)

结论：

logging_collector仅具有重启服务权限的账户具有。

其余一些权限设置，查看用户权限，具有superuser权限用户可操作

![](https://image.3001.net/images/20201109/1604898821_5fa8d005228f05efd6206.png!small)

## 三、入侵防范

### 1\. 应遵循最小安装的原则，仅安装需要的组件和应用程序

不适用

### 2\. 应关闭不需要的系统服务、默认共享和高危端口

不适用

### 3\. 应通过设定终端接入方式或网络地址范围对通过网络进行管理的管理终端进行限制

1）确认监听地址

进入$PGDATA目录，查看postgresql.con文件，linsten addresses参数，* 代表监听所有地址。

![](https://image.3001.net/images/20201109/1604888831_5fa8a8ff4fd9708ba8085.png!small)

2）确认远程管理地址

查看$PGDATA目录下的pg_hba文件：

确认ADDRESS字段是否进行了地址限制

![](https://image.3001.net/images/20201109/1604888874_5fa8a92a30ae7ef2afdd1.png!small)

### 4\. 应提供数据有效性检验功能，保证通过人机接口输入或通过通信接口输入的内容符合系统设定要求

不适用

### 5\. 应能发现可能存在的已知漏洞，并在经过充分测试评估后，及时修补漏洞

![](https://image.3001.net/images/20201109/1604889125_5fa8aa25cf92d27923e26.png!small)

根据国标要求也就是要做两点：

1）需要对数据库进行漏洞扫描（其他发现风险的方式也行），确认是否存在高风险漏洞；

2）在对系统补丁进行更新时，需要进行充分的测试评估，也就是要留存相关测试评估证据，然后还要看是否及时对该漏洞进行修补。

### 6\. 应能够检测到对重要节点进行入侵的行为，并在发生严重入侵事件时提供报警

该测评点一般在数据库服务器上体现，数据库不适用

## 总结

该数据库的等保要求个人认为大致是这样的，剩下的还有数据完整性、保密性、个人信息保护相关条款，有时间再更吧。

