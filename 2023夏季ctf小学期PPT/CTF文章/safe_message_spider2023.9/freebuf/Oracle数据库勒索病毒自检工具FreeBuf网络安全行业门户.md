## 前言

**近日，Oracle数据库勒索病毒又活跃了，其实这并非新病毒，早在2年前，即2016年11月就发现了，深信服一直持续关注此病毒。我们提醒用户，无需过度恐慌，只要不要乱下载PL/SQL破解版工具就不会中招！不确认是否中招的用户，我们这里率先提供简单！有效！的自检工具，一键运行，无需安装，即可快速判断是否感染了Oracle数据库勒索病毒。**

话不多说，直接上Oracle勒索病毒自检工具：

> <http://edr.sangfor.com.cn/tool/SfCheckPLSQL.zip>

中毒截图证明如下：

![中毒截图](https://image.3001.net/images/20181120/1542677274_5bf3631a3f9ea.jpg!small)

深信服安全团队早在5月28号就接到多起Oracle数据库被勒索的案例，中毒之后数据库显示如下勒索信息：

![勒索信息](https://image.3001.net/images/20181120/1542677284_5bf363243799c.jpg!small)

提取到相应的样本之后，经过深入分析，EDR安全团队确认该病毒是RushQL数据库勒索病毒，是由于使用了破解版的PL/SQL导致的。

## 一、样本分析

1、样本是一个PL/SQL自带的AfterConnect.sql自动运行脚本，此文件在官司PL/SQL软件中为空文件，该勒索病毒就是利用了这个文件，相应的样本，如下所示：

![样本分析](https://image.3001.net/images/20181120/1542677323_5bf3634b5f077.png!small)

脚本的关键代码，采用了Oracle数据库专用加密工具wrap进行了加密，如下所示：

![脚本的关键代码](https://image.3001.net/images/20181120/1542677333_5bf36355a5f5d.png!small)

2、对代码进行解密，得到相应的四个存储过程和三个触发器，四个存储过程，如下所示：

![对代码进行解密](https://image.3001.net/images/20181120/1542677343_5bf3635f637fe.png!small)

以上DBMS_SUPPORT_INTERNAL存储器的主要功能：

如果数据库创建日期 >1200 天之后则：

> (1)创建并备份sys.tab$表的数据到表 ORACHK || SUBSTR(SYS_GUID,10)
>
> (2)删除sys.tab$中的数据，条件是所有表的创建者ID 在（0,38）范围
>
> (3)通过SYS.DBMS_BACKUP_RESTORE.RESETCFILESECTION清理掉备份信息
>
> (4)通过DBMS_SYSTEM.KSDWRT在你的alert日志中写上2046次勒索信息
>
> (5)抛出一个警告提示勒索信息

![数据库创建日期](https://image.3001.net/images/20181120/1542677354_5bf3636a4e519.png!small)

以上DBMS_SYSTEM_INTERNAL存储器的主要功能：

> 如果当前日期 – 数据表(不含SYSTEM, SYSAUX, EXAMPLE)的最小分析日期 > 1200
> 天，且当前客户端程序进程名不是“C89239.EXE”,则触发警告提示勒索信息。

![主要功能](https://image.3001.net/images/20181120/1542677365_5bf363753dd87.png!small)

以上DBMS_CORE_INTERNAL存储器的主要功能：

>
> 把表名不含$，不含ORACHK，不是cluster的表放到一个游标里面，然后取非SYSTEM,SYSAUX,EXAMPLE之外的表空间的表的最小统计信息收集时间和当前时间比较如果大于1200天就执行truncate
> table操作，操作完成之后判断如果登录程序不为C89239.EXE，则触发警告提示勒索信息。

![主要功能](https://image.3001.net/images/20181120/1542677376_5bf3638085d5e.png!small)

以上DBMS_STANDARD_FUN9存储器的主要功能：

> 动态执行PL/SQL脚本

3、三个触发器的相应内容，如下所示：

> 在数据库启动时执行存储过程DBMS_SUPPORT_INTERNAL。

![三个触发器的相应内容](https://image.3001.net/images/20181120/1542677388_5bf3638c140c4.png!small)

> 在登录数据库时执行存储过程DBMS_SYSTEM_INTERNAL。

![三个触发器的相应内容](https://image.3001.net/images/20181120/1542677397_5bf36395f27b5.png!small)

> 在登录数据库时执行存储过程DBMS_CORE_INTERNAL。

![三个触发器的相应内容](https://image.3001.net/images/20181120/1542677407_5bf3639fe0c4e.png!small)

## 二、解决方案

1、删除被恶意篡改的客户端软件

2、根据不同的情况进行不同处理：

### 情况一：

> SYSDATE- MIN(LAST_ANALYZED) 小于1200天

数据库损坏情况：未损坏

处理办法：

a. 删除三个触发器：

    
    
    "DBMS_SUPPORT_INTERNAL"
    
    "DBMS_SYSTEM_INTERNAL"
    
    "DBMS_CORE_INTERNAL"

b.删除四个存储过错：

    
    
    "DBMS_SUPPORT_INTERNAL"
    
    "DBMS_SYSTEM_INTERNAL"
    
    "DBMS_CORE_INTERNAL"
    
    "DBMS_STANDARD_FUN9"

### 情况二：

> SYSDATE- MIN(LAST_ANALYZED) 大于1200天，并且SYSDATE- CREATED大于1200天但未重启 或者
> SYSDATE- CREATED 小于1200天

数据库损坏情况：某些表被truncate

处理方法：

a、删除三个触发器和四个存储过程

b、使用备份把表恢复到truncate之前

c、使用DUL恢复(不一定能恢复所有的表，如truncate的空间已被使用)

### 情况三：

> SYSDATE- CREATED 大于1200天

数据库损坏情况：某些表被truncate以及tab$被删除

处理方法：

a. 删除三个触发器和四个存储过程

b. 使用备份把表恢复到truncate之前

c. 使用ORACHK开头的表恢复tab$

d. 使用DUL恢复（不一定能恢复所有的表，如truncate的空间已被使用）

3、检查相关登录工具的自动化脚本，清理有风险的脚本：

SQL*PLUS中的glogin.sql/login.sql

Toad 中的toad.ini

PL/SQLDeveloper中的ogin.sql/AfterConnect.sql

4、建议从官网下载工具，不要使用绿色版/破解版等

三、参考链接

>
> <https://blogs.oracle.com/cnsupport_news/%E5%AF%B9%E6%95%B0%E6%8D%AE%E5%BA%93%E7%9A%84%E2%80%9C%E6%AF%94%E7%89%B9%E5%B8%81%E6%94%BB%E5%87%BB%E2%80%9D%E5%8F%8A%E9%98%B2%E6%8A%A4>

 ***本文作者：千里目安全实验室，转载请注明来自FreeBuf.COM**

