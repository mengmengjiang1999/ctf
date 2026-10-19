## 漏洞原理

##### 此漏洞是因为 UAC（用户账户控制）机制的设定不严导致的。默认情况下， Windows 在称为「安全桌面」的单独桌面上显示所有 UAC
提示。提示本身是由名为`consent.exe`的可执行文件生成的，该可执行文件以`NT
AUTHORITY\SYSTEM`身份运行并且有`System`的完整性水平。

##### 由于用户可以与此安全桌面的 UI 进行交互，因此有必要对 UI 进行严格限制。否则，低特权用户可能能够通过 UI 操作的路由回路以 SYSTEM
的身份执行操作。甚至看起来无害的单独 UI 功能也可能是导致任意控制的一系列操作的第一步。

##### 另一个需要了解的东西是`OID`，如果在运行一个可执行文件的时候我们触发了 UAC，在点击「显示有关此发步者的证书的信息」这个链接之后：

![image-20210719164147992](https://image.3001.net/images/20210719/1626685466_60f5401a4dc5af7311521.png!small)

![](https://image.3001.net/images/20210719/1626685467_60f5401b8c67a34cf453f.png!small)

##### 我们可以看到证书里的`Issued by（颁发者）`字段，这个字段对应的值就是`OID`。

#####
当涉及证书对话框的UAC版本时，Microsoft没有禁用此超链接，这就给了我们提权的可能。当`OID`为超链接时，通过点击此链接会触发`consent.exe`以`SYSTEM`权限打开浏览器访问此链接，然后此浏览器就会有`SYSTEM`权限。

##### 即使该浏览器是作为`SYSTEM`启动的，但是它仍显示在普通桌面而不是安全桌面上。因此，只有在用户退出所有`UAC`对话框后，它才变得可见。

#####
因此对于攻击者来说，这具有天然的隐藏优势。通过保存该浏览页面，会弹出微软的资源管理器，在资源管理器中邮件打开`cmd.exe`程序，就会继承浏览器的`SYSTEM`权限，由此就完成了由普通用户到`NT
AUTHORITY\SYSTEM`用户的提权。

## 影响版本

    
    
    SERVER
    ======
    
    Windows 2008r2	7601	** link OPENED AS SYSTEM **
    Windows 2012r2	9600	** link OPENED AS SYSTEM **
    Windows 2016	14393	** link OPENED AS SYSTEM **
    Windows 2019	17763	link NOT opened
    
    
    WORKSTATION
    ===========
    
    Windows 7 SP1	7601	** link OPENED AS SYSTEM **
    Windows 8		9200	** link OPENED AS SYSTEM **
    Windows 8.1		9600	** link OPENED AS SYSTEM **
    Windows 10 1511	10240	** link OPENED AS SYSTEM **
    Windows 10 1607	14393	** link OPENED AS SYSTEM **
    Windows 10 1703	15063	link NOT opened
    Windows 10 1709	16299	link NOT opened
    ...
    

## 漏洞复现

##### 实验环境 win7 sp1

##### CVE-2019-1388 /HHUPD.EXE下载地址

    
    
    https://github.com/jas502n/CVE-2019-1388
    

##### 1.查看当前用户权限

![f38882a4c1a2ce5c2447037a4bdc77a](https://image.3001.net/images/20210719/1626685468_60f5401caab40ceaeff67.png!small)

##### 2.以管理员权限打开HHUPD.EXE，点击显示详细信息里显示的显示有关此发布者的证书的信息

  

![ba0f48ffb2640ef63c7622842105e02](https://image.3001.net/images/20210719/1626685469_60f5401d8e9bb5d213dfe.png!small)

##### 3.点击颁发者:VeriSin Comercial Softwore Publi
shersCA超链接，然后点击确定按钮再关掉用户账户控制窗口点击否按钮

![image-20210719152206580](https://image.3001.net/images/20210719/1626685470_60f5401ea95edf36c65a8.png!small)

##### 4.点击该链接之后，关闭上面这两个弹窗，会出现ie浏览器的页面

##### 5.IE浏览器访问链接后点击页面下拉菜单面里的另存为选项

![](https://image.3001.net/images/20210719/1626685472_60f540205a6b056fd778d.png!small)

##### 6.弹出框点确定

![image-20210719153216301](https://image.3001.net/images/20210719/1626685474_60f540221ccccdead4910.png!small)

##### 7.位置地方填入

    
    
    C:\Windows\System32\*.*
    

![image-20210719153333171](https://image.3001.net/images/20210719/1626685475_60f54023ae586bbab2bff.png!small)

##### 8.选择cmd.exe右键打开，whoami即可看见为system最高权限

![c1adccd981c91e85cab083a6fc6fc00](https://image.3001.net/images/20210719/1626685476_60f54024e26b3ecdeac0d.png!small)

![07a7f303b7463f5c31d6363fa4b4f9a](https://image.3001.net/images/20210719/1626685478_60f540262757cfe61dbba.png!small)

## 修复建议

https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2019-1388

##### 文章结尾：感谢drunkmars师傅的指导~

