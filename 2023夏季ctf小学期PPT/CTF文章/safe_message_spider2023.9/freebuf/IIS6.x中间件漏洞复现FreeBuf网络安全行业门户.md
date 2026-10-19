## **IIS简介**

    
    
    Windows 2016  对应  IIS10.0
    Windows 2012  对应  IIS8.5
    Windows 7     对应  IIS 7.5
    Windows Server 2008 对应 IIS 7.5
    Windows Vista Business, Enterprise 以及 Ultimate 对应 IIS 7
    Windows Vista Home Premium 对应 IIS 7
    Windows Vista Home Edition 不支持 PWS 或 IIS
    Windows Server 2003 对应 IIS 6.0
    Windows XP Professional 对应 IIS 5.1
    Windows 2000 Professional 对应 IIS 5.0
    Windows NT Professional 对应 IIS 3，并支持 IIS 4
    

## **一、IIS 6.x攻防详解**

###  **1、IIS写权限漏洞**

 **漏洞简介：**

配置不当导致的PUT任意上传。

 **复现操作：**  
![image-20210509132101732.png](https://image.3001.net/images/20210511/1620703158_6099f7b6e4a0d602eea00.png!small)
开启脚本资源访问和写入：  
![image-20210509132420898.png](https://image.3001.net/images/20210511/1620703172_6099f7c40badf6ae6f9fd.png!small)![image-20210509164803466.png](https://image.3001.net/images/20210511/1620703179_6099f7cb0da4a7b8afcbb.png!small)  
![image-20210509165311898.png](https://image.3001.net/images/20210511/1620703189_6099f7d5ca69a7ef36fc2.png!small)上传含有asp一句话的木马。通常上传txt文本不报错，但是上传asp会报错。  
![image-20210509165750458.png](https://image.3001.net/images/20210511/1620703207_6099f7e7afca77647b63e.png!small)接着使用MOVE方法将上传的txt文件修改为asp文件，MOVE协议不会更改文件内容。  
![image-20210509172211166.png](https://image.3001.net/images/20210511/1620703226_6099f7fa3b791eca8d6f7.png!small)本地检查可以看到成功上传  
![image-20210509172228556.png](https://image.3001.net/images/20210511/1620703239_6099f807c84ad8c096b00.png!small)接着开启IIS的asp解析功能  
![image-20210509172409358.png](https://image.3001.net/images/20210511/1620703254_6099f816df15d283d9791.png!small)![image-20210509172708329.png](https://image.3001.net/images/20210511/1620703263_6099f81fd2fbabc3e4f0c.png!small)蚁剑成功连接。

 **修复建议：**

> 关闭WebDev
>
> 关闭写入权限

###  **2、文件解析漏洞**

 **IIS文件解析漏洞：** （IIS10.0
8.5都可能存在，属于PHP版本解析漏洞）*.asp;.xxx，像这样的文件IIS会把它当作xxx.asp文件执行而不会看分号后边的内容。

**IIS目录解析漏洞：*以.asp命名的文件夹中的文件都会被当作asp文件执行。

 **1）IIS文件解析漏洞**

创建一个test.asp文件，里边写入  
![image-20210509185557808.png](https://image.3001.net/images/20210511/1620703285_6099f835bddb537e13ecd.png!small)继续创建几个这样的文件，修改文件名为*.asp;.xxx格式。  
![image-20210509185708128.png](https://image.3001.net/images/20210511/1620703296_6099f840658c592fc52ad.png!small)![image-20210509185814915.png](https://image.3001.net/images/20210511/1620703304_6099f8483d11178e23448.png!small)  
![image-20210509185825536.png](https://image.3001.net/images/20210511/1620703312_6099f85004a3db66f9808.png!small)
**2）IIS目录解析漏洞**

新建两个空文件夹  
![image-20210509190412809.png](https://image.3001.net/images/20210511/1620703324_6099f85c24c300e862e07.png!small)复制1.jpg和1.zip到文件夹  
![image-20210509190912381.png](https://image.3001.net/images/20210511/1620703335_6099f8674bcb1bba578cf.png!small)访问1.asp目录下的1.jpg可以正常解析  
![image-20210509190932853.png](https://image.3001.net/images/20210511/1620703346_6099f8723d21985a31806.png!small)此外，IIS
6.x除了会将扩展名为.asp的文件解析为asp外，还默认将扩展名为.asa、.cdx、.cer解析为asp

 **修复建议：**

1）设置权限无  
![image-20210509191233409.png](https://image.3001.net/images/20210511/1620703359_6099f87f536a5119baf00.png!small)2）不允许新建目录。

3）上传的文件需经过重命名（时间戳+随机数+.jpg等）

###  **3、IIS短文件漏洞**

 **漏洞简介：**

可以利用“~”字符猜解或遍历服务器的文件名，或对IIS服务器中的.Net Framework进行拒绝服务攻击。

输入“dir /x”即可查看短文件名的效果。  
![image-20210509220458311.png](https://image.3001.net/images/20210511/1620703371_6099f88b29ec82df37306.png!small)当后缀小于4时，短文件名产生需要文件夹名前缀字符长度大于等于9位。

当后缀大于等于4时，文件名前缀长度即使为1也会产生短文件名。

 **复现操作：**

IIS 8.0以下版本需要开启ASP.NET支持，IIS大于等于8.0版本，即使没有安装ASP.NET，通过OPTIONS和TRACE方法也可以猜解成功。  
![image-20210509223602044.png](https://image.3001.net/images/20210511/1620703382_6099f896d4c4ea186ee9b.png!small)创建两个后缀为4长度的文件  
![image-20210509223906290.png](https://image.3001.net/images/20210511/1620703393_6099f8a10b6360a9af756.png!small)如果访问存在的短文件名，会返回404  
![image-20210509230949270.png](https://image.3001.net/images/20210511/1620703402_6099f8aa39df7221ce7ad.png!small)如果访问不存在的短文件名，会返回400或者400错误  
![image-20210509230932456.png](https://image.3001.net/images/20210511/1620703414_6099f8b6cc79d63dc630b.png!small)
**IIS段文件漏洞的局限性：**

    
    
    1. 如果文件名太短是无法猜解的。
    2. 只能确定前6个字符，如果后面的字符太长、包含特殊字符，很难猜解。
    3. 如果文件名前6位带空格，8.3格式的短文件名会补进，和真实文件名不匹配。
    4. 如果文件夹名前6位字符带点“.”，扫描程序会认为是文件而不是文件夹，最终出现误报。
    5. 不支持中文文件名，包括中文文件和中文文件夹。一个中文相当于两个英文字符，故超过4个汉字会产生短文件名，但是IIS不支持中文猜测。
    

**利用工具：**

    
    
    IIS-ShortName-Scanner
    

点击run.bat后输入地址：  
![image-20210510001431118.png](https://image.3001.net/images/20210511/1620703429_6099f8c55ca21db7a4570.png!small)
**修复建议：**

 **1）、从CMD命令关闭NTFS 8.3文件格式的支持**

Windows Server 2003：（1代表关闭，0代表开启）

关闭该功能：

    
    
    fsutil behavior set disable8dot3 1
    

Windows Server 2008 R2：

查询是否开启短文件名功能：

    
    
    fsutil 8dot3name query
    

关闭该功能：

    
    
    fsutil 8dot3name set 1
    

该功能默认开启！

 **2）、修改注册表**

找到注册表路径：

    
    
    HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem
    

将其中的 NtfsDisable8dot3NameCreation 设为1。  
![image-20210510000932479.png](https://image.3001.net/images/20210511/1620703445_6099f8d5b6a6249897a45.png!small)  
以上两种方式修改完成后，需要重启系统生效。

此方法只能禁止NTFS8.3格式文件名创建，已经存在的文件的短文件名无法移除，需要重新复制才会消失。如：c:\xxx到c:\xx，删掉原文件夹，再重命名c:\xx到c:\xxx。

###  **4、RCE-CVE-2017-7269**

 **漏洞简介：**

ScStoragePathFromUr函数中的缓冲区溢出允许通过以 “IF: <http: //” 开头的长标头执行任意代码PROPFIND请求。

 **影响范围：**

在Windows 2003 R2上开启WebDAV服务的IIS6.0

 **复现操作：**  
![image-20210510004500539.png](https://image.3001.net/images/20210511/1620703463_6099f8e7bad81fc6ee7f9.png!small)
任务管理器开启了calc.exe进程。  
![image-20210510004518316.png](https://image.3001.net/images/20210511/1620703473_6099f8f18cbeaaf9ab661.png!small)
**修复建议：**

    
    
    1. 关闭WebDev服务
    2. 使用相关防护设备
    

