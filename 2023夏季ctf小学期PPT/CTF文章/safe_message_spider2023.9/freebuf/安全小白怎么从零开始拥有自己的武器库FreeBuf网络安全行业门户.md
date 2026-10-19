# 一、前言

前些日子跟个大佬搞攻防，看着大佬超神我超鬼，不得不佩服大佬，看着大佬用的很多工具都没见过，问了下这些工具是啥，大佬掏出了他的大宝贝给我看，嚯，好家伙，一整个文件夹都是自己开发的工具还有一些魔改的工具，属实羡慕，看着大佬那些工具，陷入沉思，是不是我也可以有自己的武器库，总不能当伸手党吧，而且还能熟悉语言，增强自己在代码审计那块的。刚好之前搞过一段时间的开发，对于开发一些工具啥的还是有自己的想法的，说干就干，这个系列是写安全小白怎么从零开始拥有自己的一个工具库的文章，在开发方面我也是菜鸟，所以可能有些工具的开发思路跟那些流行的工具思路可能不一样，有哪写得不好的地方，希望大佬们能带带我。

# 二、前期准备

## 2.1语言选择

开发工具嘛，肯定要会一两个语言，相信各位大佬肯定掌握了不止三四种的语言，小弟没啥能力，只掌握了C，java，python，php，go这几种，用来开发工具的话比较常见的就是java，python，go了，我比较熟悉那个java和python，而且一些常见的工具也是用的java和python来开发的，这两种语言的区别就不介绍了，大家都懂的，选择哪种主要看个人的需求，如果想省点事的话可以用python，里面的库用到才知道香，但是python虚拟机没有java强，毕竟java虚拟机是java的核心，而且python是全动态性的，可以在运行时自己修改自己的代码，java只能通过变通方法实现。python的变量是动态的，而java的变量是静态的，需要事先声明，所以java
ide的代码提示功能优于python ide。

用java开发工具的话主要是习惯了用java开发有界面的工具，而python的话主要是因为库强大，可以少写很多东西，省很多时间，当然不是说python没办法搞界面，python是推出了一些框架用于开发界面的，其中最常用的就是一个是Django，Django是一个较为高级的Python
Web框架，以快速开发和实用简洁的设计闻名，关于语言的选择还是看个人习惯吧，没有谁好谁坏的说法。

## 2.2编译器

java用的编译器是IDEA和eclipse，python用的是PyCharm，这几个都是很不错的编译器，就是有些只能试用或者找破解，下完编译器，先建个项目，这边拿eclipse做下示范，进来先建个项目，这边选的是1.8.0的，然后把名字命名一下，搞一个com.AX.Database_listening，然后直接finish。

![1683162704_6453065045d0346fafe19.png!small?1683162704445](https://image.3001.net/images/20230504/1683162704_6453065045d0346fafe19.png!small?1683162704445)

搞完建好了，先看下目录结构SRC是我们之后写代码的地方，然后JRE这块是我们导入的包，事先有导入别的包，所以创建完之后会直接存在。

![1683162720_6453066051f9a83f4a743.png!small?1683162720536](https://image.3001.net/images/20230504/1683162720_6453066051f9a83f4a743.png!small?1683162720536)

一般我们在开发的时候都会用到别人写好的东西，而有些是需要你导入的，我们下载完别人的jar之后，在自己项目下面创建一个lib，把我们下载好的jar拉进去，然后右键项目，点击Properties，然后选择Java
Build Path

![1683162732_6453066c2bfffe609fc4b.png!small?1683162732319](https://image.3001.net/images/20230504/1683162732_6453066c2bfffe609fc4b.png!small?1683162732319)

找到你刚刚拉进来的jar，选中添加，然后保存，整个流程就结束了，这样我们在写其他功能的时候就会方便很多了。

![1683162749_6453067d43ac88739e7e9.png!small?1683162749426](https://image.3001.net/images/20230504/1683162749_6453067d43ac88739e7e9.png!small?1683162749426)

然后可以开始写你自己代码了。

## 2.3语言能力

语言和编译器选完了，就该有人问了，我这语言得掌握到啥程度才能开发自己的工具，嚯，要问这话我也不知道该怎么回，毕竟我自己学的也不是很深，就JAVA来说，如果你接受过系统的学习的话，基本上都会在学完基础语法之后进入到线程，异常，文件访问，接口，继承等等这些知识，后面可能会学到例如网络通信协议的东西让你写一些通信的小demo，当然要会到什么程度才能开发自己的工具的话，看你个人的需求，我觉得基本上只要你会基础语法，知道函数，类，子类，父类，重写，继承啥的就可以自己去开发一些工具了。

如果你的工具只是针对于本地的东西的话，你只需了解你想要实现的原理，后面根据这个原理去设计你的开发架构，那你压根不需要用到什么网络通信协议啥的，但是如果你需要对接网络上的一些资源的话，那么通信协议还是得会的，当然，这些对百度工程师是例外的，把你想要实现的去百度上搜索，基本上都会有解答，百度能实现百分之99的困难。

## 2.4开发思路

不管是开发啥，你对成果一定要有个大概的框架，不一定要先想好界面，但是功能，要实现怎样的功能，这些功能能实现什么样的效果，以及如何去实现这些功能。大部分工具开发的流程都是一致的，基本上都是三部分：

  1. 数据获取：怎么获取你想要的数据，例如怎么和网站进行通信，怎么连接数据库，怎么获取数据库的数据等等

  2. 数据处理：拿到数据之后，如何对数据进行处理，获取到你想要的那部分数据，一般我们在数据获取的的时候，是没办法直接获取到你想要的那部分数据的，基本上都是一锅端回来，然后根据显示出来的数据情况进行筛选，过滤，还有一种情况就是你获取到的数据需要进一步的处理，例如你获取回来的数据需要再进行一轮的数据分析，或者与你现有的特征进行比对等等这些情况，所以在数据获取和数据处理这两个方面是开发工具的时候最难的地方。

  3. 数据显示：如果前面数据获取和数据处理都完成了，那么就来到了最简单的地方，怎么呈现你的结果，是命令行还是界面，这个取决于个人喜好。

所以，根据这三个部分基本上能满足你开发大部分的工具，而且你在开发这些工具的时候思路会很清晰，始终清楚自己在哪一部分，在哪一部分就干哪一部分的事情，找那块的解决方法，网上会有很多教程，其实工具就类似是拼图，你这找一下怎么实现，那找一下怎么实现，然后拼接起来，就成了工具，一句话，CCV，一把梭哈，冲就完事了。这里附下小弟我搞小工具的时候常规的思维导图。

![1683162763_6453068ba63907317a9d8.png!small?1683162764861](https://image.3001.net/images/20230504/1683162763_6453068ba63907317a9d8.png!small?1683162764861)

# 三、开发过程

这里如果空讲的话会有点空泛，我用我之前搞的一个小工具来做例子吧，直接说我自己开发这个工具的时候的一个开发思路会比较好一点，这是个子域名的一个探测工具，主要功能的话就是根据你输入的域名进行子域名的探测，然后根据页面的状态剔除那些无法访问的，把可以访问的留下来保存数据，这个是我后面用来采集页面样本然后做页面分类的，所以还有其他功能，这里我主要讲下如何探测子域名状态值的设计思路和开发过程。

## 3.1开发架构

架构的话根据三个流程来准备，然后搞个思维导图（虽然也没啥必要，但是可以让后面自己的思路清晰，不会跑偏）

  1. 数据获取：怎么通过域名连接到网站，然后获取到网站的状态值

  2. 数据处理：获取完数据之后怎么处理数据，将数据整理成我想要的格式，例如，域名，IP，开放端口，网站状态这样，把有用的数据单独拿出来

  3. 数据显示：数据处理完之后通过界面显示出收集的结果，然后把数据导出来，通过固定格式保存，方便之后的操作。

贴下思维导图，这里只写了探测网站状态值那部分，其他的功能都差不多的，每个人的思路会有所不同，所以这块没啥大问题。

![1683162777_6453069946d729b471471.png!small?1683162777518](https://image.3001.net/images/20230504/1683162777_6453069946d729b471471.png!small?1683162777518)

## 3.2实现目标

### 3.2.1获取网站状态值

如何获取网站状态值在上面的思维导图上面已经写了，通过java的uConnection.getResponseCode()可以获取状态码。进而判断该网站是否存在，具体代码怎么用以及返回的值，类型可以自己百度一下，我这里贴一下关键代码

    
    
    URL u = new URL("http://www.baidu.com");  
    try {    
    HttpURLConnection uConnection = (HttpURLConnection)u.openConnection();    
    try {    
    uConnection.connect();  
    System.out.println(uConnection.getResponseCode());    
    } catch (Exception e) {    
    e.printStackTrace();    
    }                      
    } catch (IOException e) {    
    e.printStackTrace();    
    }

上面就是一个简单的通过url去连接网站，获取它返回的状态值，然后输出状态值，因为这里是连接的[www.baidu.com](www.baidu.com)，所以返回的是200，这个你们可以直接拿去运行看看内容，这个就是简单的一个实现过程，然后后面的可以把自己的字典导进去，获取你字典的数据，拼接到.baidu.com前面，再弄个多线程让他一直探测下去获取返回的值就行了。

### 3.2.2筛选自己想要的数据

上面我们已经拿到了网站的状态值，那么我们可以根据返回的状态值去对数据进行判断是不是该存起来，一个if就能解决的事情了，如果你想根据状态值来分类的话搞个switch就行了，例如说我们想要过滤一些数据，用if去过滤这些数据

    
    
    if (!logres.equals(logsql) && !logres.contains("/* mysql") && !logres.contains("SHOW WARNINGS") && !logres.contains("select event_time,argument from%%"))  
    Database_listening.sql_date.appendText(time.format(Long.valueOf(System.currentTimeMillis()))+"------"+logres+"\n");  
    ​

这样虽然方便，但是当你想要过滤的数据过多的时候，就需要列很长的条件，这样就太麻烦了，这时候就需要用其他的一些技能，比如说把黑名单存到文档然后根据文档里的内容去进行拦截等其他方式。

### 3.2.3界面实现

这里说下几个面板，这个算是JAVAFX里面比较常见的面板了，其实界面没什么，就跟HTML差不多，一个套一个，套娃来的，你只要提前想好你自己的数据想要显示的位置，然后去布置按钮位置，数据显示位置就行了。

  * StackPane（堆叠面板）：节点按照被添加的顺序从左到右、从上到下显示。

  * FlowPane（流式面板 ）：节点在5个区域显示－上、下、左、右、中

  * GridPane（栅格面板）：节点以灵活的行列栅格形式排列，这个可以根据自己的安排去排列那些元素的位置(0,0),(0,1),(1,0)(1,1)这样

  * BorderPane（边界面板）：将节点有序地排列在一个水平行中。当节点到达面板边界时，不会折行显示。

  * Hbox、Vbox（盒式面板）：Hbox将节点有序地排列在一个垂直列中。当节点到达面板边界时，不会折行显示，Vbox将节点有序地排列在一个中。当节点到达面板边界时，不会折行显示。

其实这个是很简单的面板介绍，基本上都是按这些面板去堆叠出来的，我这里贴一个简单的面板加按钮的示例代码，运行这个看的话可能会更理解点。

    
    
    label = new Label("累加计数 "+count);  
    Button btnPush = new Button ("+1");   
    //设置一个label和button  
    btnPush.setOnAction(this::btnPushHandler);  
    //设置按钮的事件，点击按钮之后会发生什么事情  
    FlowPane pane = new FlowPane (btnPush,label);  
    //然后把按钮和label放到面板里面，这个是流式的，直接横着排列  
    pane.setHgap(20);  
    pane.setAlignment(Pos.CENTER);  
    Scene scene = new Scene(pane, 300,100);  
    //设置面板大小  
    stage.setScene(scene);  
    stage.setTitle("面板示例");  
    //面板title  
    stage.show();  
    //显示出来

这个面板也完成了，当你把面板设计好之后，把你完成的代码分模块放到每个按钮的事件里面去，上面的那句btnPush.setOnAction(this::btnPbushHandler)是把btnPbushHandler事件设置到btnPush这个按钮里面去，当点击到btnPush按钮的时候，执行该事件，例如

    
    
    Connect_SQL = new Button("连接数据库");  
    //设置一个按钮叫Connect_SQL  
    Connect_SQL.setOnAction(this::ConnectSQL);  
    //点击该按钮之后执行ConnectSQL事件  
    ------------------------------------------------------------------------------------------------------------------------  
    //编写ConnectSQL，当点击了该按钮之后执行ConnectSQL事件，去连接数据库  
    public void ConnectSQL(ActionEvent event){  
    try {  
    ConnectSQL.Connect(sql_addr.getText(), sql_port.getText(), sql_user.getText(), sql_password.getText());  
    } catch (Exception e) {  
    // TODO Auto-generated catch block  
    e.printStackTrace();  
    }  
    }

这样就把按钮和事件响应连接起来，设计相对应的按钮和事件，去达到自己想要实现的目标，基本上这个工具就完成了，当工具写完了之后，不可能每次都进编译器里面去运行吧，把它导出来成为一个.jar的文件，之后直接执行这个文件就行了。

右键项目，点击Export，选择jar file

![1683162792_645306a8969d0ccbdf818.png!small?1683162792724](https://image.3001.net/images/20230504/1683162792_645306a8969d0ccbdf818.png!small?1683162792724)

然后把自己的项目勾选上，直接finish，就完成了。

![1683162804_645306b490235b904c396.png!small?1683162804785](https://image.3001.net/images/20230504/1683162804_645306b490235b904c396.png!small?1683162804785)

至此，整个工具的编写就完成了

# 四、实战

## 4.1工具说明

一个Mysql监控工具的思路以及实现方式，实现了指定数据库名监控跟它有关的sql语句，单独显示特定的sql语句,刚开始自己用的那些网上的工具不是很理想，所以就打算自己写一个，目前只实现了这两个功能，后面会把它改成一个代审工具，实现从sql语句跳定位到代码啥的。

## 4.2开发思路

工具的思路其实也很简单，主要就是这四块

  1. 连接数据库

  2. 监听数据库日志

  3. 对数据库日志的数据进行过滤

  4. 显示数据

而工具最终目标是：用户连接上数据库之后，在测试代码或者网站功能的时候，经过该工具过滤能够定位到执行的sql语句，方便进行代码审计

![1683162818_645306c24275446e636df.png!small?1683162818555](https://image.3001.net/images/20230504/1683162818_645306c24275446e636df.png!small?1683162818555)

## 4.3前期准备

  * 连接数据库实现

  * 兼容不同的Mysql版本

  * 监听数据库的方式

  * 过滤脏数据

  * 准确过滤出自己想要的语句

## 4.4目标实现

### 4.4.1连接数据库

#### 实现思路

连接数据库我用的是JDBC去连接MySQL数据库，连接 MySQL的话需要 需要驱动包，最新版下载地址为：
**<http://dev.mysql.com/downloads/connector/j/>** ，解压后得到 jar
库文件，然后在对应的项目中导入该库文件。要兼容版本的话得下两个jar，一个兼容8以上的，一个兼容以下的。

MySQL 8.0 以上版本的数据库连接部分不同：

MySQL 8.0 以上版本驱动包版本[mysql-connector-java-8.0.16.jar](https://static.runoob.com/download/mysql-connector-java-8.0.16.jar)。

com.mysql.jdbc.Driver 更换为com.mysql.cj.jdbc.Driver。

MySQL 8.0以上版本无需建立SSL连接，需要显示关闭。

allowPublicKeyRetrieval=true 允许客户端从服务器获取密钥，最后还需要设置 CST

加载驱动与连接数据库方式如下：

    
    
    Class.forName("com.mysql.cj.jdbc.Driver");  
    conn = DriverManager.getConnection("jdbc:mysql://localhost:3306/test_demo?useSSL=false&allowPublicKeyRetrieval=true&serverTimezone=UTC","root","password");  
    MySQL 8.0 以下版本 - JDBC 驱动名及数据库 URL     
    static final String JDBC_DRIVER = "com.mysql.jdbc.Driver";   
    static final String DB_URL = "jdbc:mysql://[localhost:3306/RUNOOB](http://localhost:3306/RUNOOB)";  
    // MySQL 8.0 以上版本 - JDBC 驱动名及数据库 URL      
    static final String JDBC_DRIVER = "com.mysql.cj.jdbc.Driver";   
    static final String DB_URL = "jdbc:mysql://[localhost:3306/RUNOOB?useSSL=false&allowPublicKeyRetrieval=true&serverTimezone=UTC](http://localhost:3306/RUNOOB?useSSL=false&allowPublicKeyRetrieval=true&serverTimezone=UTC)";

#### 关键代码

    
    
    public static EventHandler<ActionEvent> Connect(String sql_addr, String sql_port, String sql_user,String sql_password)throws ClassNotFoundException, SQLException  {  
    // TODO Auto-generated method stub  
    USER = sql_user;  
    PASS = sql_password;  
    Connection conn = null;  
    Statement stmt = null;  
    try{  
    JDBC_DRIVER = "com.mysql.jdbc.Driver";  
    DB_URL = "jdbc:mysql://" + sql_addr + ":" + sql_port + "/mysql?useUnicode=true&characterEncoding=utf8&serverTimezone=GMT%2B8&useSSL=false";  
    // 注册 JDBC 驱动  
    Class.forName(JDBC_DRIVER);  
    // 打开链接  
    Database_listening.sql_date.appendText(time.format(Long.valueOf(System.currentTimeMillis()))+"------正在连接数据库..."+"\n");  
    //            System.out.println("正在连接数据库...");  
    conn = DriverManager.getConnection(DB_URL,USER,PASS);  
    conn.prepareStatement("SET global general_log=on").executeUpdate();  
    conn.prepareStatement("SET GLOBAL log_output='table'").executeUpdate();  
    DatabaseMetaData metaData = (DatabaseMetaData) conn.getMetaData();  
    String version = metaData.getDatabaseProductVersion();//得到数据库版本信息  
    //            System.out.println(time.format(Long.valueOf(System.currentTimeMillis()))+"--当前数据库版本为："+version);  
    Database_listening.sql_date.appendText(time.format(Long.valueOf(System.currentTimeMillis()))+"------当前数据库版本为："+version+"\n");  
      
    }catch(SQLException se){  
      
    JDBC_DRIVER = "com.mysql.cj.jdbc.Driver";  
    DB_URL = "jdbc:mysql://"+sql_addr+":"+sql_port+"/mysql?useUnicode=true&characterEncoding=utf8&serverTimezone=GMT%2B8&useSSL=false";  
    // 注册 JDBC 驱动  
    Class.forName(JDBC_DRIVER);  
    // 打开链接  
    //            System.out.println("正在连接数据库...");  
    Database_listening.sql_date.appendText(time.format(Long.valueOf(System.currentTimeMillis()))+"------正在连接数据库..."+"\n");  
    conn = DriverManager.getConnection(DB_URL,USER,PASS);  
    DatabaseMetaData metaData = (DatabaseMetaData) conn.getMetaData();  
    conn.prepareStatement("SET global general_log=on").executeUpdate();  
    conn.prepareStatement("SET GLOBAL log_output='table'").executeUpdate();  
    String version = metaData.getDatabaseProductVersion();//得到数据库版本信息  
    //            System.out.println(time.format(Long.valueOf(System.currentTimeMillis()))+"--当前数据库版本为："+version);  
    Database_listening.sql_date.appendText(time.format(Long.valueOf(System.currentTimeMillis()))+"------当前数据库版本为："+version+"\n");  
      
    }catch(Exception e){  
    // 处理 Class.forName 错误  
    e.printStackTrace();  
    }  
    return null;  
    }

### 4.4.2监听数据库日志

#### 监听思路

刚开始想的是直接对某个数据库的日志进行监听，但是后面发现需要修改数据库的配置文件，不是很方便，毕竟不想每监听一个就去改一下这个数据库的配置文件(想偷懒),还有就是监听缓存文件以及监听mysql数据库里面的一个表，我想着之后有可能把它改成一个代码审计的工具，所以直接监听整mysql的日志，后面再对脏数据进行过滤就行了。

根据上面的思路，我直接对Mysql里的general_log表进行监听，但是后面发现有很多脏数据，而且因为这个是整个Mysql的所以那些数据库运行的数据也会显示出来，导致我后面过滤脏数据一度尴尬，为了验证可行性，直接用if去过滤那些无用的数据，后面改成黑名单，直接把那些脏数据加进去然后过滤了

#### 关键代码

    
    
    String logsql = "select * from mysql.general_log where command_type =\"Query\" OR command_type =\"Execute\" order by event_time desc limit 1,15";  
    Connection conn = DriverManager.getConnection(DB_URL, USER, PASS);  
    ResultSet rs = conn.prepareStatement(logsql).executeQuery();  
    while (rs.next()) {  
    String logres = rs.getString("argument");  
    //System.out.println(time.format(Long.valueOf(System.currentTimeMillis()))+"："+logres);  
    Database_listening.sql_date.appendText(time.format(Long.valueOf(System.currentTimeMillis()))+"------"+logres+"\n");  
    }

连接数据库，然后通过查询表内的数据，再不断输出，但是太多无用数据显示了，基本上每次都会显示SET NAMES utf8，SELECT
@@session.autocommit，SHOW
WARNINGS这些数据出来，太干扰看那些正常的语句了，所以我刚开始只是用了一层if去过滤这些数据，后面发现不大灵活，所以整成一个黑名单，可以动态添加删除拦截那些数据的规则。

### 4.4.3过滤数据

#### 过滤思路

刚开始获取的时候看到很多其他的数据来干扰，例如SELECT QUERY_ID，SHOW STATUS，SHOW FULL TABLES WHERE
Table_type !=
'VIEW'这些，上面说到我用了个if去过滤那些带这个特征的数据，其实挺好用的，只不过后面想要动态的去调整这些黑名单，所以用了个下拉列表来存储数据，然后把数据过来只后再把下拉列表里面的数据进行处理，再把获取到的数据库信息一个个过滤掉，从而达到过滤的效果，

#### 关键代码

    
    
    if (!logres.equals(logsql) && !logres.contains("/* mysql") && !logres.contains("SHOW WARNINGS") && !logres.contains("select event_time,argument from%%") && !logres.contains("SELECT STATE") && !logres.contains("SHOW STATUS") && !logres.contains("SELECT QUERY_ID")){  
    Database_listening.sql_date.appendText(time.format(Long.valueOf(System.currentTimeMillis()))+"------"+logres+"\n");  
    }

到这基本上工具就写完了，这个算是比较简单的工具，开发思路也比较简单，也没用到什么奇奇怪怪的操作，基本上都是基础语法，挺适合小白上手工具开发的，

排版完面板之后把功能加入到各个按钮事件里面导出称jar文件，运行就可以用了，当然在编译器了也可以直接使用，看个人选择吧。

![1683162835_645306d379591592e358b.png!small?1683162835938](https://image.3001.net/images/20230504/1683162835_645306d379591592e358b.png!small?1683162835938)

# 五、总结

总的来说，开发工具其实没什么难度，把每一块拆分成多个小点去完成，然后拼接起来就行了，第一次写这种关于工具开发的文，有些可能没表达到位，我尽量把需要注意的地方给写出来，这个是针对于小白的，所以有些简单的东西还是选择说得仔细点，大佬们可以选择性的跳一跳，这个是第一篇，后面的话会根据自己平时开发的一些插件，工具啥的写一些开发思路或者教程，后面可能就不会讲面板这些东西了，如果有那里写得不对的，希望大佬们带带我。

