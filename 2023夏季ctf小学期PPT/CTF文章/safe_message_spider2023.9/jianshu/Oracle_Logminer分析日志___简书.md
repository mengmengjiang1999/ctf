Oracle Logminer分析日志

[ 左轮Lee](https://www.jianshu.com/u/06b7a375a146)关注赞赏支持

# Oracle Logminer分析日志

官方地址：<https://docs.oracle.com/cd/E11882_01/server.112/e22490/logminer.htm#SUTIL019>  
版本： oracle 11.2.0.4

# 官方资料

### LogMiner Configuration

包含以下部分：

  * The source database is the database that produces all the redo log files that you want LogMiner to analyze.  
source database是你需要分析的产生所有redo log的库。

  * The mining database is the database that LogMiner uses when it performs the analysis.  
mining database 是执行logminer分析的库。

  * The LogMiner dictionary allows LogMiner to provide table and column names, instead of internal object IDs, when it presents the redo log data that you request.
  * The redo log files contain the changes made to the database or database dictionary.

  

sample logminer database configuration.jpg

### Requirements

The following are requirements for the source and mining database, the data
dictionary, and the redo log files that LogMiner will mine:

###### Source and mining database

  * Both the source database and the mining database must be running on the same hardware platform.
  * The mining database can be the same as, or completely separate from, the source database.
  * The mining database must run the same release or a later release of the Oracle Database software as the source database.
  * The mining database must use the same character set (or a superset of the character set) used by the source database.

###### LogMiner dictionary

  * The dictionary must be produced by the same source database that generates the redo log files that LogMiner will analyze. 字典信息必须是产生redo log的源库的信息，不然无法获取字典数据。

###### All redo log files

  * Must be produced by the same source database. 必须是同一个库产生；
  * Must be associated with the same database RESETLOGS SCN.
  * Must be from a release 8.0 or later Oracle Database. However, several of the LogMiner features introduced as of release 9.0.1 work only with redo log files produced on an Oracle9i or later database. See ["Supported Databases and Redo Log File Versions"](https://docs.oracle.com/cd/E11882_01/server.112/e22490/logminer.htm#i1031050). 必须是8以后的版本，有些特性需要9i之后的版本才支持。

###### 开启supplemental logging

ALTER DATABASE ADD SUPPLEMENTAL LOG DATA;  
SELECT SUPPLEMENTAL_LOG_DATA_MIN FROM V$DATABASE; 如果是 YES or IMPLICIT
这两个状态，就表示已开启。

### LogMiner主要步骤：

###### 1.Specify a LogMiner dictionary.

Use the DBMS_LOGMNR_D.BUILD procedure or specify the dictionary when you start
LogMiner (in Step 3), or both, depending on the type of dictionary you plan to
use.

###### 2.Specify a list of redo log files for analysis.

Use the DBMS_LOGMNR.ADD_LOGFILE procedure, or direct LogMiner to create a list
of log files for analysis automatically when you start LogMiner (in Step 3).

###### 3.Start LogMiner.

Use the DBMS_LOGMNR.START_LOGMNR procedure.

###### 4.Request the redo data of interest.

Query the V$LOGMNR_CONTENTS view. (You must have the SELECT ANY TRANSACTION
privilege to query this view.)

###### 5.End the LogMiner session.

Use the DBMS_LOGMNR.END_LOGMNR procedure.  
You must have been granted the EXECUTE_CATALOG_ROLE role to use the LogMiner
PL/SQL packages and to query the V$LOGMNR_CONTENTS view.

### LogMiner Dictionary Files and Redo Log Files

使用哪种字典文件

  * [Using the Online Catalog](https://docs.oracle.com/cd/E11882_01/server.112/e22490/logminer.htm#i1014720)

Oracle recommends that you use this option when you will have access to the
source database from which the redo log files were created and when no changes
to the column definitions in the tables of interest are anticipated. This is
the most efficient and easy-to-use option.

  * [Extracting a LogMiner Dictionary to the Redo Log Files](https://docs.oracle.com/cd/E11882_01/server.112/e22490/logminer.htm#i1014735)

Oracle recommends that you use this option when you do not expect to have
access to the source database from which the redo log files were created, or
if you anticipate that changes will be made to the column definitions in the
tables of interest.

  * [Extracting the LogMiner Dictionary to a Flat File](https://docs.oracle.com/cd/E11882_01/server.112/e22490/logminer.htm#i1014763)

This option is maintained for backward compatibility with previous releases.
This option does not guarantee transactional consistency. Oracle recommends
that you use either the online catalog or extract the dictionary from redo log
files instead.

下图展示选择哪种字典文件：

  

Choosing a Logminer Dictionary.jpg

# 实操案例

#### 用Online catalog 作为字典方式分析：

以下操作均在 PL/SQL 软件中执行

    
    
    *** 打开附加日志
    select SUPPLEMENTAL_LOG_DATA_MIN from v$database;  
    alter database add supplemental log data;  
    
    *** 模拟修改数据
    SELECT * FROM v$log;      # 查看当前的活动redo
    UPDATE system.test_logmin SET status='TEST' WHERE ROWNUM < 10;
    
    *** 开始分析
    BEGIN dbms_logmnr.add_logfile('/u01/app/oracle/oradata/testdb/redo01.log', dbms_logmnr.new); END;        ## 添加在线日志，第一个使用参数 new
    BEGIN dbms_logmnr.add_logfile('/u01/app/oracle/oradata/testdb/redo02.log', dbms_logmnr.addfile);END;     ## 可添加多个
    
    BEGIN dbms_logmnr.start_logmnr(options => dbms_logmnr.dict_from_online_catalog);END;           ## 开始分析
    
    ### 查看分析结果，如下图所示
    SELECT SQL_REDO, SQL_UNDO, SEG_OWNER
      FROM V$LOGMNR_CONTENTS
     WHERE SEG_NAME = 'TEST_LOGMIN'
       AND SEG_OWNER = 'SYSTEM';
    

Logminer Result.jpg

    
    
    *** 结束分析
    BEGIN dbms_logmnr.end_logmnr; END;
    

如果是从归档日志中分析，那首先需要知道脚本执行的大概时间范围，否则分析难度会加大，导致分析时间较长。  
从操作系统层面根据归档日志文件的时间，找到此区间的嫌疑日志，然后添加到分析队列。

    
    
    开始分析。
    BEGIN dbms_logmnr.add_logfile('/u01/app/oracle/oradata/testdb/archive/1_61_985361656.dbf', dbms_logmnr.new); END;     ## 找到归档文件
    
    ## 指定分析范围
    ALTER SESSION SET NLS_DATE_FORMAT ='yyyy-mm-dd HH24:MI:SS';
    BEGIN
      DBMS_LOGMNR.START_LOGMNR(STARTTIME => '2018-09-20 17:00:00',
                               ENDTIME   => '2018-09-20 17:50:00',
                               OPTIONS   => DBMS_LOGMNR.DICT_FROM_ONLINE_CATALOG +DBMS_LOGMNR.CONTINUOUS_MINE);
    END;
    
    ##  查看分析结果
    SELECT SQL_REDO, SQL_UNDO, SEG_OWNER
      FROM V$LOGMNR_CONTENTS
     WHERE SEG_NAME = 'TEST_LOGMIN'
       AND SEG_OWNER = 'SYSTEM';
    
    ## 结束分析
    BEGIN dbms_logmnr.end_logmnr; END;      
    

#### 用DICT_FROM_REDO_LOGS作为字典方式分析：

此方式比较灵活，可以将目标端的归档文件（数据变动文件及包含字典信息的归档文件）拷贝到测试机器进行分析，减少生产机器压力

    
    
    ## 指定redo log存储字典
    BEGIN DBMS_LOGMNR_D.BUILD(OPTIONS => DBMS_LOGMNR_D.STORE_IN_REDO_LOGS);END;
    
    ## 找到 DICTIONARY_BEGIN='YES'  和 DICTIONARY_END='YES' 这之间的归档日志，后续需要加到分析队列中，因为里面包含字典信息
    SELECT NAME FROM V$ARCHIVED_LOG WHERE DICTIONARY_BEGIN='YES';
    SELECT NAME FROM V$ARCHIVED_LOG WHERE DICTIONARY_END='YES';
    
    ## 找到涉及到的归档文件及包含字典的归档文件
    BEGIN dbms_logmnr.add_logfile('/u01/app/oracle/oradata/testdb/archive/1_61_985361656.dbf', dbms_logmnr.new); END;
    BEGIN dbms_logmnr.add_logfile('/u01/app/oracle/oradata/testdb/archive/1_69_985361656.dbf', dbms_logmnr.ADDFILE); END;
    
    ## 开始分析
    ALTER SESSION SET NLS_DATE_FORMAT ='yyyy-mm-dd HH24:MI:SS';
    BEGIN
      DBMS_LOGMNR.START_LOGMNR(STARTTIME => '2018-09-20 17:00:00',
                               ENDTIME   => '2018-09-20 17:45:00',
                               OPTIONS   => DBMS_LOGMNR.DICT_FROM_REDO_LOGS);
    END;
    
    ## 查看结果
    SELECT SQL_REDO, SQL_UNDO, SEG_OWNER
      FROM V$LOGMNR_CONTENTS
     WHERE SEG_NAME = 'TEST_LOGMIN'
       AND SEG_OWNER = 'SYSTEM';
    
    ## 分析结束
    BEGIN dbms_logmnr.end_logmnr; END;
    

#### 用平面文件(Flat file)作为字典方式分析：

此种方式需要设置 utl_file_dir 路径，需要重启数据库，实际生产中使用较少(默认db不设置此参数)。

    
    
    ## 设置路径参数
    SELECT VALUE FROM v$parameter  a  where a.NAME ='utl_file_dir';
    alter system set utl_file_dir='/u01/app/logminer' scope=spfile;      ## 保证目录/u01/app/logminer存在
    
    ## 重启数据库
    shutdown immediate;
    startup;
    SELECT VALUE FROM v$parameter  a  where a.NAME ='utl_file_dir';       ## 检查配置
    
    ## 指定平面文件存储字典
    BEGIN DBMS_LOGMNR_D.BUILD('dictionary.ora','/u01/app/logminer',DBMS_LOGMNR_D.STORE_IN_FLAT_FILE); END;
    
    ## 找到涉及到的归档文件
    BEGIN dbms_logmnr.add_logfile('/u01/app/oracle/oradata/testdb/archive/1_61_985361656.dbf', dbms_logmnr.new); END;
    
    ## 开始分析
    ALTER SESSION SET NLS_DATE_FORMAT ='yyyy-mm-dd HH24:MI:SS';
    BEGIN
      DBMS_LOGMNR.START_LOGMNR(STARTTIME    => '2018-09-20 17:00:00',
                               ENDTIME      => '2018-09-20 17:45:00',
                               DICTFILENAME => '/u01/app/logminer/dictionary.ora');
    END;
    
    ## 查看结果
    SELECT SQL_REDO, SQL_UNDO, SEG_OWNER
      FROM V$LOGMNR_CONTENTS
     WHERE SEG_NAME = 'TEST_LOGMIN'
       AND SEG_OWNER = 'SYSTEM';
    
    ## 分析结束
    BEGIN dbms_logmnr.end_logmnr; END;
    

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [Apple Developer Program License Agreement](https://www.jianshu.com/p/43038b884b0c)

PLEASE READ THE FOLLOWING APPLE DEVELOPER PROGRAM LICENSE...

[念念不忘的](https://www.jianshu.com/u/4eb15a4a68c8)阅读 12,770评论 5赞 6

  * [态度比能力重要](https://www.jianshu.com/p/e5c205f90373)

接着上周陆续面试了几个应聘外贸的求职者后，我要求人事部在第一道把英文邮件翻译成中文的面试题的基础上多加了一道题，那...

[向上有阳光](https://www.jianshu.com/u/aed91ad51c5d)阅读 352评论 0赞 3

  * [良善的温暖——180119觉察日志](https://www.jianshu.com/p/03f9418af024)

今天凌晨六点多，收到二姨妈发过来的短信，说知道我回家了，问我有没有想吃的，她给我带过来，同时要将自家养的土鸡给我送...

[上善若水泽万物](https://www.jianshu.com/u/49a524ce858c)阅读 105评论 0赞 9

  * [微荣及浮誉，何物应开心](https://www.jianshu.com/p/376c0cbefb2e)

[清泠韵](https://www.jianshu.com/u/19a555a938fe)阅读 89评论 0赞 2

 