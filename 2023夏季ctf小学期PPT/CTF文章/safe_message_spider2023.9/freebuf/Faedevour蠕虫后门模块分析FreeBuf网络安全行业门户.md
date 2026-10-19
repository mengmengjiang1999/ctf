## 1、概述

近日，新华三态势感知平台检测到某客户主机产生恶意域名外联事件，外联的C&C域名为a.gwas.perl.sh，情报标签为Faedevour蠕虫，新华三攻防实验室第一时间配合客户进行现场处置，提取样本并进行分析，确认为Faedevour蠕虫病毒。Faedevour蠕虫首次出现于2013年，一直在野流行，其运行后会在受感染的主机上植入一个后门，窃取信息和执行命令，并通过将自身复制到可移动存储设备和共享文件夹进行传播。

## 2、样本分析

Faedevour病毒母体首先将自身复制到一个指定路径下运行，然后在整个运行过程中释放多个恶意组件，实现不同的恶意功能。其中后门模块由mscaps.exe和wtime32.dll两个组件共同实现，下面对这两个恶意组件进行详细分析。

![](https://image.3001.net/images/20210318/1616056097_60530f21b1f0d49d1fd7f.png!small)

### 2.1、mscaps.exe行为分析

mscaps.exe由wtmps.exe释放并启动运行，根据程序权限不同释放到不同的路径，管理员权限为“%SystemRoot%\system32\”，普通用户权限为“%APPDATA%\Microsoft\Protect\SETUP\”。mscaps.exe运行后，首先删除wtmps.exe文件，然后从自身资源数据中获取并解密配置信息保存到一个ini格式的临时文件中，接着调用GetPrivateProfileString函数完成配置参数的读取，最后删除该临时文件。

![](https://image.3001.net/images/20210318/1616056221_60530f9daa3549f33f46b.png!small)

![](https://image.3001.net/images/20210318/1616056277_60530fd55d158b9a497c3.png!small)

mscaps通过设置注册表来实现在受感染机器上的持久驻留，根据当前程序权限的不同设置方式也不同。对于管理员权限，其采用ActiveX方式实现自启动，在注册表目录“HIKEY_LOCAL_MACHINE\Software\Microsoft\Active
Setup\Installed
Components”下创建一个新的表项{ef2b00e3-19da-4e78-b118-6b6451b719f2}或{a96adc11-e20e-4e21-bfac-3e483c40906e}，并写入4个键-值对。其中键“StubPath”的值指定需要自启动的文件，为其可执行文件mscaps.exe的绝对路径。

![](https://image.3001.net/images/20210318/1616056317_60530ffdb7e411416364b.png!small)

对于普通权限，其则在注册表目录“HIKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run”下写入一个键-值对，键为“JREUpdate”，值也是mscaps.exe的绝对路径。

![](https://image.3001.net/images/20210318/1616056330_6053100a9b0a7d699d802.png!small)

设置完注册表实现开机自启动后，mscaps从自身资源数据中解密释放出后门模块真正的载荷，一个DLL文件，命名为wtime32.dll。并将wtime32.dll的文件创建时间、修改时间和访问时间修改为和Windows系统动态链接库“%SystemRoot%\system32\gdi32.dll”相同。

![](https://image.3001.net/images/20210318/1616056371_60531033ec93800dee0cc.png!small)

最后，mscaps将wtime32.dll注入到explorer.exe进程中，使其运行起来后删除wtime32.dll文件。注入方法为先通过枚举当前系统中的进程进行模块路径匹配来查找explorer.exe的进程ID，然后利用WriteProcessMemory和CreateRemoteThread后实现DLL注入。

![](https://image.3001.net/images/20210318/1616056408_60531058e910b4ba0c9a8.png!small)

###
![](https://image.3001.net/images/20210318/1616056419_605310633fb9786dbe2e0.png!small)2.2、wtime32.dll行为分析

mscaps.exe并不会与C&C服务器进行交互，而是交由注入到explorer.exe进程中的wtime32.dll来进行。注入线程首先创建互斥量，防止重复运行，然后创建一个新线程来运行后门载荷。

![](https://image.3001.net/images/20210318/1616056499_605310b37750183107749.png!small)

在这个新线程中，首先异或解密配置信息，其中包括3个C&C服务器域名。

![](https://image.3001.net/images/20210318/1616056517_605310c54085f6a3ce726.png!small)

然后又创建一个新的线程来连接C&C服务器并接受命令，创建新线程的条件是受感染主机联网且该线程没有实例被创建，前者通过调用gethostbyname查询update.microsoft.com的IP地址来判断，并且每隔3分钟尝试创建一次。

![](https://image.3001.net/images/20210318/1616056546_605310e26565d73cf4c3b.png!small)

该新线程首先利用受感染主机的系统版本号、计算机名和MAC地址等信息，通过异或加Base64编码生成一个域名，作为主机的唯一标志，并通过DNS信道回连C&C服务器，其Base64编码表为“ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_”。

![](https://image.3001.net/images/20210318/1616058270_6053179ec911d7aaf2ea1.png!small)

然后，在3个C&C服务器域名中按顺序选择第一个存活的作为DNS服务器发送DNS查询请求，查询上面生成的域名的CNAME字段信息，并且每隔一段时间进行一次上述查询。C&C服务器通过CNAME字段识别不同的受害机，并通过DNS响应包向受害机下发控制指令。

![](https://image.3001.net/images/20210318/1616058344_605317e8cf44a02d772c8.png!small)

通过静态分析，可以得知DNS查询请求返回的是由Base64加异或加密得到一个控制命令，命令由两部分组成，以“.”分隔，第一部分为命令字符串，第二部分为命令的参数。分析得出此处共有8个命令，分别是：go、dl、du、de、ex、un、ti、ts。

![](https://image.3001.net/images/20210318/1616058372_60531804a469bfd4e1ea5.png!small)

1）“go”命令不会进行任何操作。

2）“dl”命令将指定的DLL文件注入到指定的进程中运行，注入方式同wtime32.dll的注入过程，最后删除DLL文件。该命令带有两个参数，第一个参数指定目标进程的绝对路径，第二个参数指定DLL文件的文件名或绝对路径。

![](https://image.3001.net/images/20210318/1616058409_6053182958d47a60ac3be.png!small)

（3）“du”命令在当前进程中释放指定模块，并删除模块对应文件。该命令带有两个参数，但仅有第2个参数起作用，为指定模块名。

![](https://image.3001.net/images/20210318/1616058434_6053184215a202d08ebde.png!small)

4）“de”命令删除指定的文件，带有一个参数为指定文件的文件名或绝对路径，当参数为文件名时，默认路径为当前工作目录。

![](https://image.3001.net/images/20210318/1616058453_6053185569b2d8b8c5375.png!small)

5）“ex”命令调用WinExec执行指定的exe文件。

![](https://image.3001.net/images/20210318/1616058477_6053186d2c84d4e982ecb.png!small)

6）“un”命令用来卸载mscaps。其先清除mscaps.exe设置的自启动注册表项，然后删除mscaps.exe文件，最后，从当前进程释放wtime32.dll。

![](https://image.3001.net/images/20210318/1616058502_60531886b56ec19cef78c.png!small)

7）“ts”命令参数为一个C&C服务器域名和端口号。其会创建一个新线程，与C&C服务器建立稳定的TCP连接，循环接收并执行攻击者的命令。此时接收的命令跟上述命令并不相同，通信过程传输的数据也进行了异或加密处理。

![](https://image.3001.net/images/20210318/1616058519_6053189735e555e236bd9.png!small)

命令| 行为  
---|---  
_cmd| 执行指定的bat文件，执行结果保存到该bat文件中  
_inf| 获取系统信息保存到指定文件中  
_cap| 捕获桌面截图保存到指定文件中  
_dll| 进行dll注入  
_dlu| 在当前进程释放指定模块  
_put| 向受感染主机传输一个文件  
_got| 获取受感染主机上的指定文件，并删除文件  
_get| 获取受感染主机上的指定文件，不删除文件  
_exe| 执行指定exe文件  
_del| 删除指定文件  
_dir| 获取指定目录下所有文件的属性、文件名、大小、时间  
_quit| 退出连接  
_prc| 获取所有进程的完整路径信息  
  
8）“ti”命令用于更改样本向C&C服务器发送DNS查询请求的时间间隔。

Faedevour病毒通过这些指令实现了对受害机的完整控制，攻击者可以窃取用户信息，投放其他恶意程序，执行恶意命令等，具有较大危害。在此，新华三攻防实验室温馨提醒您注意防护此类病毒。

## 3、防护建议

  1. 及时备份重要文件，且文件备份应与主机隔离；
  2. 不要点击来源不明的邮件以及附件；
  3. 及时升级系统，及时安装系统补丁；
  4. 关闭不必要的共享权限以及端口，如3389，445，135，139等；
  5. 更改账户密码，设置强密码（采用大小写字母、数字、特殊符号混合的组合结构，口令位数足够长），避免使用同一密码；
  6. 新华三防病毒库支持该病毒及其变种的检测和防御，请确保新华三安全系列产品的防病毒功能开启。

7\. 新华三威胁情报库支持该病毒相关IOCs识别检测，请确保新华三安全系列产品的威胁情报检测功能开启。

## IOCs

### MD5:

WdExt.exe

ab1d42cf56706a1eb216165876d09363

launch.exe

DAAC1781C9D22F5743ADE0CB41FEAEBF

arc.dll

2D9DF706D1857434FCAA014DF70D1C66

att.dll

FFFA05401511AD2A89283C52D0C86472

dis.dll

1FCC5B3ED6BC76D70CFA49D051E0DFF6

fil.dll

D0C9ADA173DA923EFABB53D5A9B28D54

sha.dll

6A9461F260EBB2556B8AE1D0BA93858A

usd.dll

F1C9F4A1F92588AEB82BE5D2D4C2C730

wtmps.exe

75C1467042B38332D1EA0298F29FB592

mscaps.exe

78D3C8705F8BAF7D34E6A6737D1CFA18

wtime32.dll

978888892A1ED13E94D2FCB832A2A6B5

### C2:

a.gwas.perl.sh

a-gwas-01.slyip.net

a-gwas-01.dyndns.org

