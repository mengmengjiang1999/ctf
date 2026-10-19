![](https://image.3001.net/images/20221007/1665119495_633fb507450bd2c8fb527.png!small)

## 关于JRCL

JRCL全称为Java Remote Class
Loader，是一款功能强大的Java代码远程加载工具。该工具允许广大研究人员以Java类文件的形式将Java字节码发送到目标客户端设备中，并使用Java类加载器（Java
ClassLoader）和Refelect API来加载和执行Java代码。目标客户端从远程服务器接收到Java类文件之后，会将代码执行结果返回给服务器端。

其中，Payload必须采用Java便携，并在开启服务器端之前完成代码编译。

## 功能介绍

> 1、采用客户端-服务器端架构；
>
> 2、支持远程加载Java类文件；
>
> 3、使用ChaCha20密码在传输过程中对数据进行加密；
>
> 4、支持通过参数对工具进行自定义配置；
>
> 5、如果服务器重启，则需要使用Keepalive制重新建立通信；

## 工具运行机制

![](https://image.3001.net/images/20221007/1665119553_633fb541da10dc6e070e1.png!small)

## 工具安装

该工具支持在Windows和Linux操作系统上使用，并且需要使用OpenJDK 11和JRE
Java包。考虑到工具依赖组件，我们建议广大研究人员使用Java v11或更高版本。

 **OpenJDK/Java11下载地址** ：【[ _传送门_](https://www.openlogic.com/openjdk-downloads)】

接下来，使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/joaovarelas/java-remote-class-loader.git

## 工具使用

    
    
    $ java -jar java-class-loader.jar -help
    
     
    
    usage: Main
    
     -address <arg>       目标设备IP / 绑定的服务器地址
    
     -classfile <arg>     远程加载的字节码.class文件的文件名 (默认: Payload.class)
    
     -classmethod <arg>   调用的方法名称 (默认: exec)
    
     -classname <arg>     类名称 (默认: Payload)
    
     -client                以客户端运行
    
     -help                打印工具帮助信息
    
     -keepalive           保持客户端每X秒从服务器端获取一次Java类文件 (默认: 3 秒)
    
     -key <arg>           以Base64格式设置256位密钥，如果不指定则生成一个新的密钥
    
     -port <arg>          port to connect (client) / to bind (server)
    
     -server              以服务器端运行

## 工具使用样例

假设你的Payload.java文件中包含下列形式的Payload代码（Hello World）：

    
    
    //Payload.java
    
    public class Payload {
    
        public static String exec() {
    
            String output = "";
    
            try {
    
                output = "Hello world from client!";
    
            } catch (Exception e) {
    
                e.printStackTrace();
    
            }
    
            return output;
    
        }
    
    }

接下来，你应该对这个Payload.javaP文件进行编译并生成对应的Payload.class文件。

Java类文件生成完成后，我们就可以运行服务器端进程，并监听所有网络接口上的端口1337:

    
    
    $ java -jar java-class-loader.jar -server -address 0.0.0.0 -port 1337 -classfile Payload.class
    
     
    
    Running as server
    
    Server running on 0.0.0.0:1337
    
    Generated new key: TOU3TLn1QsayL1K6tbNOzDK69MstouEyNLMGqzqNIrQ=

在客户端上，我们需要使用“-client”参数来设置使用相同的JAR包，并使用服务器生成的对称密钥。然后指定要连接的服务器IP地址和端口，我们还可以更改类名和类方法（默认值分别为Payload和String
exec()）。除此之外，我么还可以使用“-keepalive”参数以在维护连接的同时保持客户端从服务器请求类文件：

    
    
    $ java -jar java-class-loader.jar -client -address 192.168.1.73 -port 1337 -key TOU3TLn1QsayL1K6tbNOzDK69MstouEyNLMGqzqNIrQ=
    
     
    
    Running as client
    
    Connecting to 192.168.1.73:1337
    
    Received 593 bytes from server
    
    Output from invoked class method: Hello world from client!
    
    Sent 24 bytes to server

## 项目地址

 **JRCL** ：【[ _GitHub传送门_](https://github.com/joaovarelas/java-remote-class-loader)】

## 参考资料

> [ _https://vrls.ws/posts/2022/08/building-a-remote-class-loader-in-> java/_](https://vrls.ws/posts/2022/08/building-a-remote-class-loader-in-> java/)
>
> [
> _https://github.com/rebeyond/Behinder_](https://github.com/rebeyond/Behinder)
>
> [
> _https://github.com/AntSwordProject/antSword_](https://github.com/AntSwordProject/antSword)
>
> [ _https://cyberandramen.net/2022/02/18/a-tale-of-two-> shells/_](https://cyberandramen.net/2022/02/18/a-tale-of-two-shells/)
>
> [
> _https://www.sangfor.com/blog/cybersecurity/behinder-v30-analysis_](https://www.sangfor.com/blog/cybersecurity/behinder-v30-analysis)
>
> [ _https://xz.aliyun.com/t/2799_](https://xz.aliyun.com/t/2799)
>
> [ _https://medium.com/@m01e/jsp-webshell-cookbook-> part-1-6836844ceee7_](https://medium.com/@m01e/jsp-webshell-cookbook-> part-1-6836844ceee7)
>
> [ _https://venishjoe.net/post/dynamically-load-compiled-java-> class/_](https://venishjoe.net/post/dynamically-load-compiled-java-class/)
>
> [ _https://users.cs.jmu.edu/bernstdh/web/common/lectures/slides_class-> loaders_remote.php_](https://users.cs.jmu.edu/bernstdh/web/common/lectures/slides_class-> loaders_remote.php)
>
> [ _https://www.javainterviewpoint.com/chacha20-poly1305-encryption-and-> decryption/_](https://www.javainterviewpoint.com/chacha20-poly1305-encryption-> and-decryption/)
>
> [ _https://openjdk.org/jeps/329_](https://openjdk.org/jeps/329)
>
> [
> _https://docs.oracle.com/en/java/javase/11/docs/api/java.base/java/lang/ClassLoader.html_](https://docs.oracle.com/en/java/javase/11/docs/api/java.base/java/lang/ClassLoader.html)
>
> [
> _https://docs.oracle.com/en/java/javase/11/docs/api/java.base/java/lang/reflect/Method.html_](https://docs.oracle.com/en/java/javase/11/docs/api/java.base/java/lang/reflect/Method.html)

