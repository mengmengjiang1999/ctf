****

**严正声明：本文仅限于技术讨论，严禁用于其他用途。**

 **在DefCon 26上，[@singe](https://twitter.com/singe) 和 [@_cablethief
](https://twitter.com/_cablethief)发表了关于企业无线攻击的精彩演讲。如果你仔细观看了之后放出的演讲视频，你应该能注意到其中他们提及了一个叫做“Apostille”的工具。这是一款由[@Sensepost](https://twitter.com/sensepost)团队成员[Rogan
Daweska](https://twitter.com/rogandawes)开发的，证书窃取（克隆/伪造）工具。但在演讲中他们并未过多介绍，这也是促使我写这篇博文的原因。**

**![Apostille：让假证书以假乱真的证书伪造工具](https://image.3001.net/images/20180910/1536536607_5b95b01fa6993.png!small)**

复制证书的通用名称，电子邮件或在创建时输入其他字段是证书伪造的相对简单的方式。咋一看，他们看起来并没有什么不同。但这样的证书往往会留下诸多的伪造痕迹。例如，我创建了一个类似的证书：

    
    
    root@apostille-post:~# openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout mycert.pem -out mycert.pem
    Generating a 2048 bit RSA private key
    .................................................................................................................+++
    ...+++
    writing new private key to 'mycert.pem'
    -----    You are about to be asked to enter information that will be incorporated
    into your certificate request.
    What you are about to enter is what is called a Distinguished Name or a DN.
    There are quite a few fields but you can leave some blank
    For some fields there will be a default value,
    If you enter '.', the field will be left blank.
    -----    Country Name (2 letter code) [AU]:US
    State or Province Name (full name) [Some-State]:California
    Locality Name (eg, city) []:Mountain View
    Organization Name (eg, company) [Internet Widgits Pty Ltd]:Google LLC
    Organizational Unit Name (eg, section) []:
    Common Name (e.g. server FQDN or YOUR name) []:*.google.com
    Email Address []:

如果我将其托管，以下是Google.com的结果：

![Apostille：让假证书以假乱真的证书伪造工具](https://image.3001.net/images/20180910/1536536642_5b95b0420bf25.png!small)

可以看到，伪造证书（左图）的证书信息明确指出该证书不被信任。此外，从证书的颁发机构也可以很容易的判断出证书的真伪。

##  **Apostille 安装**

Apostille需要Java JDK和Maven来进行编译，因此我们先来安装它们：

    
    
    root@apostille-post:~# apt install -y maven default-jdk git

克隆存储库，并使用Maven进行编译：

    
    
    root@apostille-post:~# git clone https://github.com/sensepost/apostille
    Cloning into 'apostille'...
    remote: Counting objects: 48, done.
    remote: Total 48 (delta 0), reused 0 (delta 0), pack-reused 48
    Unpacking objects: 100% (48/48), done.
    root@apostille-post:~# cd apostille/
    root@apostille-post:~/apostille# mvn package

克隆你的第一个证书：

    
    
    java -jar target/apostille-1.0-SNAPSHOT.jar google.com:443 tempkeystore.jks ASDqwe123 ASDqwe123

>  **google.com:443** ：服务于证书链的端点（不仅限于HTTPS，任何TLS端点都可以）。
>
>  **tempkeystore.jks** ：存放证书链的Java Keystore文件。
>
>  **ASDqwe123** ：前一个是kspassword，后面的是keypassword（密钥库和证书密码）- 密钥库只会在稍后导出证书的时候用到。

下面我们要做的是将证书从密钥库中取出，并转换为可用于测试的PEM格式。具体操作可参考：<https://www.calazan.com/how-to-convert-a-java-keystore-jks-to-pem-format/>

    
    
    root@apostille-post:~/apostille# keytool -importkeystore -srckeystore tempkeystore.jks -destkeystore myapp.p12 -srcalias *.google.com -srcstoretype jks -deststoretype pkcs12
    Importing keystore tempkeystore.jks to myapp.p12...Enter destination keystore password: ASDqwe123
    Re-enter new password: ASDqwe123
    Enter source keystore password: ASDqwe123

转换后看起来应该像这样：

现在，让我们来看看对比之前伪造的证书有什么不同之处。我将参考[AKB的快速Web服务器列表](http://attackerkb.com/Web/Quick%20Web%20Servers)。

    
    
    root@apostille-post:~/apostille# openssl s_server -cert myapp.pem -accept 443 -WWW
    Enter pass phrase for myapp.pem: WugWZ3!F3hD#8P!f
    Using default temp DH parameters
    ACCEPT

结果如下：

![Apostille：让假证书以假乱真的证书伪造工具](https://image.3001.net/images/20180910/1536536668_5b95b05cb9ab4.png!small)![Apostille：让假证书以假乱真的证书伪造工具](https://image.3001.net/images/20180910/1536536670_5b95b05eaa2a8.png!small)![Apostille：让假证书以假乱真的证书伪造工具](https://image.3001.net/images/20180910/1536536669_5b95b05df11c9.png!small)

可以看到，真证书和伪造证书几乎已经很难通过肉眼进行区分。而证书信息部分，虽有提示但并不明确。最后，再次感谢[@RoganDawes](https://twitter.com/rogandawes)提供了这款工具！

 ***参考来源：[malicious](https://malicious.link/post/2018/stealing-certificates-with-apostille/)，FB小编 secist 编译，转载请注明来自FreeBuf.COM**

