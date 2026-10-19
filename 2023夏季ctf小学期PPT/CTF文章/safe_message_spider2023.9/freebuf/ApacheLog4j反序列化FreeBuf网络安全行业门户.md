# Apache Log4j 反序列化

## 前言

> ​
> 在应用程序中添加日志记录最普通的做法就是在代码中嵌入许多的打印语句，这些打印语句可以输出到控制台或文件中，比较好的做法就是构造一个日志操作类来封装此类操作，而不是让一系列的打印语句充斥了代码的主体。  
> ​
> Log4j是Apache的一个开源项目，通过使用Log4j，我们可以控制日志信息输送的目的地是控制台、文件、GUI组件，甚至是套接口服务器、NT的事件记录器、UNIX
> Syslog守护进程等；我们也可以控制每一条日志的输出格式；通过定义每一条日志信息的级别，我们能够更加细致地控制日志的生成过程。最令人感兴趣的就是，这些可以通过一个配置文件来灵活地进行配置，而不需要修改应用的代码。  
> ​ Log4j在工程中可以易用，方便等代替了 System.out
> 等打印语句，它是Java下最流行的日志输入工具，一些著名的开源项目，像spring、hibernate、struts都使用该工具作为日志输入工具，可以帮助调试（有时候debug是发挥不了作用的）和分析。

## CVE-2017-5645

### 漏洞版本

Log4j 2.x <= 2.8.1

### 漏洞复现

vulhub拉起镜像

`docker-compose up -d`

![image](https://image.3001.net/images/20230508/1683549604_6458eda4aed4bb03f2759.png!small)

利用ysoserial反序列化工具生成payload发送给目标IP地4712端口

![image](https://image.3001.net/images/20230508/1683549621_6458edb5318d89e5b0e42.png!small)

查看命令执行结果

![image](https://image.3001.net/images/20230508/1683549633_6458edc1a4b2522451c7e.png!small)

### 漏洞分析

 **pom配置**

    
    
    <!-- maven文件pom.xml -->
    <?xml version="1.0" encoding="UTF-8"?>
    <project xmlns="http://maven.apache.org/POM/4.0.0"
             xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
             xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
        <modelVersion>4.0.0</modelVersion>
    
        <groupId>org.example</groupId>
        <artifactId>log4j-2.x-rce</artifactId>
        <version>1.0-SNAPSHOT</version>
        <dependencies>
            <!-- https://mvnrepository.com/artifact/org.apache.logging.log4j/log4j-core -->
            <dependency>
                <groupId>org.apache.logging.log4j</groupId>
                <artifactId>log4j-core</artifactId>
                <version>2.8.1</version>
            </dependency>
            <!-- https://mvnrepository.com/artifact/org.apache.logging.log4j/log4j-api -->
            <dependency>
                <groupId>org.apache.logging.log4j</groupId>
                <artifactId>log4j-api</artifactId>
                <version>2.8.1</version>
            </dependency>
            <!-- https://mvnrepository.com/artifact/commons-collections/commons-collections -->
            <dependency>
                <groupId>commons-collections</groupId>
                <artifactId>commons-collections</artifactId>
                <version>3.1</version>
            </dependency>
        </dependencies>
    
    </project>
    

**调用链**

    
    
    TcpSocketServer.createSerializedSocketServer() -> # 创建socketServer
    startNewthread() ->	# 接受客户端传递的数据
    TcpSocketServer.run() -> # 将数据交由SocketHandler处理
    SocketHandler.run() -> # 数据作logEvents()处理
    ObjectInputStreamLogEventBridge.logEvents() -> 
    inputStream.readObject() #反序列化
    

![image](https://image.3001.net/images/20230508/1683549649_6458edd14fba85060786b.png!small)

入口点为TcpSocketServer.class#main

![image](https://image.3001.net/images/20230508/1683549660_6458eddca4ead9182b689.png!small)

跟进createSerializedSocketServer函数，函数创建了socketServer

![image](https://image.3001.net/images/20230508/1683549676_6458edec0818fde5df3c6.png!small)

继续步过，进入到socketServer.startNewThread()，可以继续跟进到TcpSocketServer.class#run中

![image](https://image.3001.net/images/20230508/1683549710_6458ee0e398512f3f4c52.png!small)

101行处，serverSocket.accept()监听接受数据；

105行处，将接受的数据交由SocketHadnler()处理；

进入SocketHandler函数中

![image](https://image.3001.net/images/20230508/1683549724_6458ee1cea45259127d85.png!small)

在SocketHandler函数中，首先通过构造函数返回一个ObjectInputStream对象给this.inputStream。之后在自身的run函数中直接将之前赋值的this.inputStream传入到TcpSocketServer.this.logEventInput.logEvents函数中，跟进

![image](https://image.3001.net/images/20230508/1683549736_6458ee2845114b03c080e.png!small)

在logEvents函数内，进行反序列化inputStream.readObject()

## CVE-2019-17571

### 漏洞版本

1.2.4 <= Log4j <= 1.2.17

###  **漏洞复现**

 **利用代码**

    
    
    import org.apache.log4j.net.SimpleSocketServer;
    
    public class Log4j {
    
        public static void main(String[] args) {
            Log4j log4j = new Log4j();
            log4j.CVE_2019_17571();
        }
    
        /**
         * CVE-2019-17571 漏洞
         */
        private void CVE_2019_17571() {
            System.out.println("Listening on port 1234");
            String[] arguments = {"1234", (new Log4j()).getClass().getClassLoader().getResource("log4j.properties").getPath()};
            SimpleSocketServer.main(arguments);
            System.out.println("Log4j output successfuly");
        }
    }
    
    

**log4j.properties** (位于resources目录下)

    
    
    log4j.rootCategory=DEBUG,stdout
    log4j.appender.stdout=org.apache.log4j.ConsoleAppender
    log4j.appender.stdout.layout=org.apache.log4j.PatternLayout
    log4j.appender.stdout.threshold=DEBUG
    log4j.appender.stdout.layout.ConversionPattern=[%d{yyy-MM-dd HH:mm:ss,SSS}]-[%p]-[MSG!:%m]-[%c\:%L]%n
    

使用ysoserial生成payload，再用nc发送到socket监听端口

![image](https://image.3001.net/images/20230508/1683549752_6458ee3895c4bc7420623.png!small)

![image](https://image.3001.net/images/20230508/1683549765_6458ee45e4cbc3c95185d.png!small)

### 漏洞分析

 **调用链**

    
    
    SimpleSocketServer#main() -> # 创建ServerSocket
    Thread.start() -> #start方法底层调用Runnable对象的run方法
    SocketNode.run() ->
    event = (LoggingEvent)this.ois.readObject();
    

在漏洞代码处打下断点

![image](https://image.3001.net/images/20230508/1683549778_6458ee52b04e46a78d895.png!small)

步入SimpleSocketServer#main

![image](https://image.3001.net/images/20230508/1683549789_6458ee5d99c6381530407.png!small)  
首先步入SocketNode

![image](https://image.3001.net/images/20230508/1683549802_6458ee6acb23717aa0e7e.png!small)

SocketNode类有一个Runnable接口，而且在其中有一个run()函数

![image](https://image.3001.net/images/20230508/1683549823_6458ee7fc83d6280cc1d9.png!small)

run()函数中有readObject()反序列化点

![image](https://image.3001.net/images/20230508/1683549837_6458ee8da574db93c4b2d.png!small)

那么如何才能调用到该函数呢？

我们可以步出回到

![image](https://image.3001.net/images/20230508/1683549849_6458ee998b09799862c64.png!small)  
可以看到该行代码调用了Thread类的start()方法

![image](https://image.3001.net/images/20230508/1683549895_6458eec78093f675b4e26.png!small)

通过注释可以知道在start0()中，start()方法会底层调用Runnable对象中的run()方法。

![image](https://image.3001.net/images/20230508/1683549913_6458eed96a7fe3383f1ca.png!small)

英文不好，别介( _^_^_ )

    
    
    (new Thread(new SocketNode(socket, LogManager.getLoggerRepository()), "SimpleSocketServer-" + port)).start();
    

![image](https://image.3001.net/images/20230508/1683549929_6458eee94c078c7352074.png!small)

在Thread的构造方法中可以看到SocketNode对象是作为target参数传入。所以在调用Thread的start()方法时会调用到SocketNode的run()方法，最后执行readObject()

