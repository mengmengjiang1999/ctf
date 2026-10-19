**在kali linux下进行渗透测试时，我们会用到不同环境，在不同环境中启动不同工具，Cobalt
Strike是一个很牛逼的远控型渗透测试工具结合社会工程学可以发挥难以想想的效果。**

 **  
**

前几天kali 系统升级直接升级到openjdk9 ，后来去google一下发现 oracle java 和 openjdk 是不一样。一个是开源的java
一个是商业的java 。这一点大家一定要搞清楚。

二话不说直接干掉oepnjdk 使用命令如下。

    
    
    apt-get remove openjdk-*  
    

现在我们吧openjdk全部卸载掉了 ，
去oracle官网下载最新jdk。链接地址[here](http://www.oracle.com/technetwork/cn/java/javase/downloads/jdk8-downloads-2133151-zhs.html)

安装命令也很简单。新建一个 install.sh 脚本 bash 运行就可以了

    
    
    touch install ; leafpad install.sh ; bash install.sh  
    

update-alternatives --install /usr/bin/java java /opt/jdk1.8.0_171/bin/java 1

update-alternatives --install /usr/bin/javac javac /opt/jdk1.8.0_171/bin/javac
1

update-alternatives --install /usr/lib/mozilla/plugins/libjavaplugin.so
mozilla-javaplugin.so /opt/jdk1.8.0_171/jre/lib/amd64/libnpjp2.so 1

update-alternatives --set java /opt/jdk1.8.0_171/bin/java

update-alternatives --set javac /opt/jdk1.8.0_171/bin/javac

update-alternatives --set mozilla-javaplugin.so
/opt/jdk1.8.0_171/jre/lib/amd64/libnpjp2.so

  

测试命令 java -version

  

个人观点 不要以为安装完kali linux 系统就所有环境都布完了 ， 其实你才刚刚开始。  

