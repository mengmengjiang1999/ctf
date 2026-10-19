自今年第二季度开始，DarkSide和REvil先后在美犯下大乱，在美俄联手下，纷纷偃旗息鼓，REvil更是一度关闭了相关网站和服务器。而在7月，一款名为BlackMatter的新型勒索病毒横空出世，本以为是”平平无奇“的新人，但是经过海内外安全人员分析确认，该新型勒索竟与REvil和DarkSide有着很强的关联性。

![](https://image.3001.net/images/20210901/1630490861_612f50ed1455cd3ad52a8.png!small)

/深信服千里目实验室曾对这个病毒家族做过跟踪报道/

根据深信服终端安全团队的调查发现，此勒索病毒的开发团队为BlackMatter开发了windows版本和linux版本。Windows版本针对的是windows
server以及windows7+。而linux版本针对的是Vmware
esx服务器，并且也依旧能在Ubuntu、CentOs、Debian等操作系统上正常进行加密。安全团队成员对Windows版本与linux版本的Blackmatter勒索病毒都进行分析，分析内容如下：

![](https://image.3001.net/images/20210901/1630490876_612f50fcd106387db7652.png!small)

/Windows版本勒索文本/

##  **Win32**

BlackMatter2.0版本的编译时间是在不久之前：

![](https://image.3001.net/images/20210901/1630490890_612f510aabfce05f35f53.png!small)

###  **整体流程：**

BlackMatter的整体工作调用操作如下：

![](https://image.3001.net/images/20210901/1630490901_612f51152073d69da6f77.png!small)

###  **动态加载：**

BlackMatter在运行过程中调用windows API的方式是动态调用的，且需要使用到的Dll是通过遍历system32目录来手动加载的：

![](https://image.3001.net/images/20210901/1630490911_612f511f06781dc194447.png!small)

2.0版本的blackmatter将所有需要的API重定向到了自己的调用区段中，获取地址的方式是通过遍历Dll的ENT表，通过字符串hash比对后，利用导出索引指针和EAT表计算出函数地址的：

![](https://image.3001.net/images/20210901/1630490919_612f5127639126e40e93f.png!small)

计算出地址以后才为自身调用区段布置opcode，病毒执行的过程中需要调用API的时候会进入自身的调用区段，由调用区段调用API，跳转的方式都为jmp
eax，机器码为0xE0FF：

![](https://image.3001.net/images/20210901/1630490930_612f5132e71884c603f4e.png!small)

###  **解密数据：**

Blackmatter利用计算机的注册表HKLM\SOFTWARE\Microsoft\Cryptography下的MachineGuid的键值来base64生成加密后缀：

![](https://image.3001.net/images/20210901/1630490946_612f5142dc52716952458.png!small)

解密出恶意站点：

![](https://image.3001.net/images/20210901/1630490956_612f514c26ea8c9296ff5.png!small)

###  **加密过程：**

BlackMatter为执行加密过程创建了多个分支，分别有对应单参数模式，双参数模式以及无参数模式，可见BlackMatter的开发团队为各种不同的攻击情况都做好了准备：

![](https://image.3001.net/images/20210901/1630490965_612f5155b96ecc7824a92.png!small)

安全团队针对无参数模式进行了分析，其执行勒索的流程如下：

![](https://image.3001.net/images/20210901/1630490974_612f515e768a8b2ec0ba3.png!small)

病毒会关闭如下服务：

![](https://image.3001.net/images/20210901/1630490983_612f516733b8bf736c150.png!small)

还会关闭可能影响到文件读写的进程：

![](https://image.3001.net/images/20210901/1630490991_612f516fe2b498efb91f2.png!small)

病毒上传受害者信息的时候是单独创建一个线程来完成的，它将会上传以下信息到恶意服务器：

![](https://image.3001.net/images/20210901/1630490999_612f5177cde9bbfbeb421.png!small)

Blackmatter勒索团伙对自己的作品十分自信，曾在网上透露过BlackMatter的加密效率十分高效，通过安全团队分析，其高效加密可能与其采用多线程加密有关。

BlackMatter会根据获取到的CPU数量来创建相应数量的线程：

![](https://image.3001.net/images/20210901/1630491007_612f517fe1ab70b0e0067.png!small)

BlackMatter使用了IO完成端口以及原子锁来确保异步IO的逻辑不会发生错误，先创建读写线程来阻塞等待端口中传来的读写请求，然后创建扫描文件线程，在扫描出文件后会向端口中投递读写请求，然后读写线程就可以开始进行加密，以这种方式来高效地多线程加密磁盘文件。

###  **加密之后：**

在完成加密之后，生成勒索字符串：

![](https://image.3001.net/images/20210901/1630491018_612f518a1f835d23a5874.png!small)

使用GDI对象将字符串绘制成勒索桌面的bmp图，存储在C:\\\ProgramData目录下，并通过设置注册表中Control
Panel\Desktop目录中Wallpaper键的值来改变桌面：

![](https://image.3001.net/images/20210901/1630491025_612f5191bdbb653515643.png!small)

![](https://image.3001.net/images/20210901/1630491033_612f519963b8d93c63951.png!small)

勒索桌面：![](https://image.3001.net/images/20210901/1630491048_612f51a864d7f2b5360fe.png!small)

##  **Linux**

BlackMatter的开发团队还编写了以Vmware
Esx服务器为目标的Linux版本。深信服安全团队对其也进行了分析，得出了此病毒在linux系统上运行并加密文件的关键步骤：

###  **创建Daemon**

![](https://image.3001.net/images/20210901/1630491063_612f51b74047f4a3abf13.png!small)

病毒会通过创建daemon来试图干扰调试器的工作。

###  **执行esxcli命令：**

为了给加密文件做好准备，病毒会通过系统上的esxcli来执行一系列恶意命令，并将这些恶意命令封装成了以下的函数：

![](https://image.3001.net/images/20210901/1630491072_612f51c05312041cce4fd.png!small)

这些函数将利用esxcli的操作命令完成其代表的功能。

例如:关闭服务器防火墙的命令：

Network firewall set --enabled false

![](https://image.3001.net/images/20210901/1630491080_612f51c8baad9dd6185dc.png!small)

利用world-id来关闭运行的虚拟机：

Vm process kill --type=force --world-id=

![](https://image.3001.net/images/20210901/1630491088_612f51d05d8b658e77e66.png!small)

以及利用vm process list来获取当前的虚拟机列表：

![](https://image.3001.net/images/20210901/1630491102_612f51de44a634fa28e8a.png!small)

###  **生成RSA秘钥：**

勒索病毒的加密方法使用的是开源的CryptoPP库，把密钥生成以及加密过程静态编译到了病毒文件中。

![](https://image.3001.net/images/20210901/1630491111_612f51e7d50b8923ddd08.png!small)

###  **扫描文件：**

此勒索病毒在完成RSA秘钥生成之后就会开始扫描磁盘上的文件：

![](https://image.3001.net/images/20210901/1630491125_612f51f50540816a9f7e0.png!small)

这个函数中将会再调用一个递归函数来扫描磁盘上的文件：

![](https://image.3001.net/images/20210901/1630491133_612f51fd96e546d097f18.png!small)

###  **加密过程：**

扫描完成之后病毒会根据CPU信息为加密过程选择多线程加密或单线程加密，并且还会计算需要加密的文件的总大小，然后调用加密函数对文件进行加密：

![](https://image.3001.net/images/20210901/1630491142_612f5206aa73f1fd7187d.png!small)

在完成对文件的加密之后会对文件进行重命名的操作：

![](https://image.3001.net/images/20210901/1630491151_612f520fe13ce567b32d5.png!small)

对文件的加密算法采用CBC模式的AES加密算法，以下是生成CryptoPP Chipher::AES的过程。

![](https://image.3001.net/images/20210901/1630491161_612f5219b116d4e4d5415.png!small)

在完成加密准备之后，病毒会读取文件数据，开始进行加密过程，将文件数据加密之后，再写回文件：

![](https://image.3001.net/images/20210901/1630491170_612f52227c5b293e7a190.png!small)

勒索文本是在运行的过程中动态生成的：

![](https://image.3001.net/images/20210901/1630491179_612f522b34f3f2668471c.png!small)

##  **安全防护**

1.日常生活工作中的重要的数据文件资料设置相应的访问权限，关闭不必要的文件共享功能并且定期进行非本地备份；

2.使用高强度的主机密码，并避免多台设备使用相同密码，不要对外网直接映射3389等端口，防止暴力破解；

3.避免打开来历不明的邮件、链接和网址附件等，尽量不要在非官方渠道下载非正版的应用软件，发现文件类型与图标不相符时应先使用安全软件对文件进行查杀；

4.定期检测系统漏洞并且及时进行补丁修复。

