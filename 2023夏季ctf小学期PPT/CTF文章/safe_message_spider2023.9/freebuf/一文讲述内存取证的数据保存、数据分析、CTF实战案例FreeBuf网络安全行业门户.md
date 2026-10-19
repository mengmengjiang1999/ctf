网络攻击内存化和网络犯罪的隐遁化，使部分关键数字证据只存在于物理内存或暂存于页面交换文件中，这使得传统的基于文件系统的计算机取证不能有效应对。内存取证通过全面获取内存数据、详尽的内存数据分析，并在此基础上提取与网络攻击或网络犯罪相关的数字证据，在网络应急响应和网络犯罪调查中发挥着不可替代的作用。

Dumpit和Volatility是两款内存取证工具，今天将分享利用这两款工具的内存取证的方法，结合CTF内存取证题来做详解。欢迎各路高手一同切磋讨论。

##  **一、保存内存数据**

使用dumpit.exe输入y，可将当前PC机的内存情况保存为raw文件。将该raw文件名更改为test.raw。

![v2-b482da789a5fa9763db931a67d3c80a5_720w.jpg](https://image.3001.net/images/20210525/1621924914_60ac9c325ac78f1271bbf.jpg!small)![v2-a771a55113c27611abd0970ea4c0b978_720w.jpg](https://image.3001.net/images/20210525/1621924914_60ac9c32b2d29a13e4159.jpg!small)

##  **二、内存数据分析**

1、将test.raw放入volatility文件夹中，使用volatility查看当时保存内存状态，在cmd下使用命令:

    
    
    Volatility.exe -f test.raw imageinfo

![v2-3655fdef22342265341c923683169fe9_720w.jpg](https://image.3001.net/images/20210525/1621924915_60ac9c333d969f945106e.jpg!small)

在Suggested Profile(s)处给出了几个建议性的profile。

下边还提供了CPU时间等详细信息。

2、查看当时运行的进程，以及对应进程的详细状态信息。在cmd下使用命令：

    
    
    Volatility.exe -f test.raw --profile=Win7SP1x64 pslist

![v2-feda89050f7125f0e7e09e2cc897350d_720w.jpg](https://image.3001.net/images/20210525/1621924915_60ac9c33abb224e41e6ce.jpg!small)

命令中，--profile项中选择提供可选择的Suggested Profile，此处选择WIN7SP1x64

当然，此处也可以使用Volatility.exe -f test.raw --profile=Win7SP1x64 pstree

用pstree的方式查看进程。

3、查看当时缓存在内存中的注册表情况。在cmd下使用命令：

    
    
    Volatility.exe -f test.raw --profile=Win7SP1x64 hivelist

![v2-38817832a5b743b2c45386b0a1846787_720w.jpg](https://image.3001.net/images/20210525/1621924916_60ac9c340f166d74632ef.jpg!small)

其中需要注意Virtual地址，其它操作需要经常使用到虚拟地址。

4、如果有想要打印出来的注册表中的数据，可以使用命令：

    
    
    Volatility.exe -f test.raw --profile=Win7SP1x64 hivedump -o 注册表对应虚拟地址

![v2-09eb18841661542f8339963227f1ee66_720w.jpg](https://image.3001.net/images/20210525/1621924916_60ac9c34663175df0b37e.jpg!small)

此处选择使用注册表SAM所对应的虚拟地址，查看注册表SAM下的注册表数据。

5、查看SAM中有哪些用户，可以使用命令：

    
    
    Volatility.exe -f test.raw --profile=Win7SP1x64 printkey -K “对应注册表文件地址”

![v2-b2f11cea7d20568a95ecea2387f1940d_720w.jpg](https://image.3001.net/images/20210525/1621924916_60ac9c34b2f40e83065a3.jpg!small)

此处选择使用SAM\Domains\Account\Users\Names注册表地址。查看存在的相应用户。

![v2-c44a245744fda3fd1e11a4e46e3c8c46_720w.jpg](https://image.3001.net/images/20210525/1621924917_60ac9c3506093d7584374.jpg!small)

此处选择使用SOFTWARE\Microsoft\Windows
NT\CurrentVersion\Winlogon注册表地址，查看最后进行了修改的用户的时间等信息。

6、查看当时正在运行的程序，运行过的次数，最后一次运行的时间等信息。可以使用命令：

    
    
    Volatility -f test.raw --profile=Win7SP1x64 userassist

![v2-7147dcdd13d4873d1c0cd261d965bb60_720w.jpg](https://image.3001.net/images/20210525/1621924917_60ac9c35648a7bf190e8c.jpg!small)

7、使用memdump插件可以将当时内存中的某个进程数据提取出来，以bmp格式进行保存，可以使用命令：

    
    
    Volatility -f test.raw --profile=Win7SP1x64 memdump -p 1608 -D win7/

-p 指定的进程ID

-D dump出的文件保存在哪个目录下。

此处使用1332 dumpit.exe的pid

![v2-2f93cb7616d0e6494a8a8ee0447fd9b3_720w.jpg](https://image.3001.net/images/20210525/1621924917_60ac9c35ad86dc9e2fa13.jpg!small)

可以使用strings工具将其字符串打印出来。

8、使用cmdscan插件可以将当时内存中的cmd使用情况提取出来，使用命令：

    
    
    Volatility -f test.raw --profile=Win7SP1x64 cmdscan

![v2-92203d8df16049209c94c28d0f8839f7_720w.jpg](https://image.3001.net/images/20210525/1621924918_60ac9c36026533ffe7e9c.jpg!small)

9、使用netscan插件可以将当时的网络连接状态提取出来，使用命令：

    
    
    Volatility -f test.raw --profile=Win7SP1x64 netscan

![v2-d9c0e576899996890e25c506726529e7_720w.jpg](https://image.3001.net/images/20210525/1621924918_60ac9c3687d23a13868a4.jpg!small)

10、使用iehistory插件可以查看当时的IE浏览器使用情况，使用命令：

    
    
    Volatility -f test.raw --profile=Win7SP1x64  iehistory

![v2-40687dd595cf9913f9bf629a297cdda1_720w.jpg](https://image.3001.net/images/20210525/1621924919_60ac9c37001d97296a948.jpg!small)

11、使用hashdump将内存中的系统密码dump出来，使用命令：

    
    
    Volatility -f test.raw --profile=Win7SP1x64 hashdump -y (注册表system的virtual地址) -s (SAM的virtual地址)

![v2-416ac043af4af94376524ca70d48f116_720w.jpg](https://image.3001.net/images/20210525/1621924919_60ac9c3757df776b5ed1d.jpg!small)

12、使用timeliner插件从多个位置来搜集系统的活动信息，使用命令：

    
    
    Volatility -f test.raw --profile=Win7SP1x64 timeliner

![v2-4ea7ac2e95bc415919d560563d78bf08_720w.jpg](https://image.3001.net/images/20210525/1621924919_60ac9c37a2b4d1108ca48.jpg!small)

##  **三、内存取证CTF实战案例**

1、先对dmp数据进行基本分析，查看当时内存属于什么系统和版本。

![v2-628bc8e2ed206069bba558a53f5babf7_720w.jpg](https://image.3001.net/images/20210525/1621924920_60ac9c382640620f646ed.jpg!small)

2、使用pstree查看当时运行的进程。

![v2-4cd3dd85b165fdfdbaca4b6e5582216c_720w.jpg](https://image.3001.net/images/20210525/1621924920_60ac9c386b3d15d4d5abd.jpg!small)

这里发现有运行cmd.exe，使用cmdscan插件去查看当时cmd运行的命令。

![v2-60ebe3b5ffd8f1414bbea076b20eb5e8_720w.jpg](https://image.3001.net/images/20210525/1621924920_60ac9c38d4135b208a091.jpg!small)

然后看到里边存有flag相关的信息，得到flag.ccx的password与Administrator的password一样。

3、去搜索一下flag.ccx文件，使用filescan插件查询后生成一个mem.txt文件。

![v2-f77973a275182abdcf9b1576f7d298fe_720w.jpg](https://image.3001.net/images/20210525/1621924921_60ac9c393b37aacea15da.jpg!small)![v2-d9421b9c466d6c6ccbf7acfb1d2fc2cd_720w.jpg](https://image.3001.net/images/20210525/1621924921_60ac9c39bc903848019bc.jpg!small)

检索以下带flag的字段。

![v2-ba59945e656dbc4f258ad9b04351cbd6_720w.jpg](https://image.3001.net/images/20210525/1621924922_60ac9c3a6173bf3962eda.jpg!small)

4、使用dump命令将flag.ccx文件dump下来。

![v2-d87b5552ae5d7bee33cf47c097df40fb_720w.jpg](https://image.3001.net/images/20210525/1621924922_60ac9c3abc6f3309cafeb.jpg!small)![v2-e6705969ce51ad711d530854cbfaa595_720w.jpg](https://image.3001.net/images/20210525/1621924923_60ac9c3b10f4fbfa53b83.jpg!small)

查询SAM表用户。

![v2-1e8011565f6e47cdb0b82ff9377b90c1_720w.jpg](https://image.3001.net/images/20210525/1621924923_60ac9c3b6e959f534e744.jpg!small)

列出system与SAM的内存地址。

![v2-cae096870d7d51ebf3e3a4e51d679c8f_720w.jpg](https://image.3001.net/images/20210525/1621924923_60ac9c3bb53b362c3de9e.jpg!small)

7、使用hashdump将Administrator的密码hash dump下来。

![v2-34a1f8673fe82580999690bc83a564eb_720w.jpg](https://image.3001.net/images/20210525/1621924924_60ac9c3c4d84533525cda.jpg!small)

根据得到的Administrator的hash去解密cmd5，以获取密码。

![v2-61f6a5ccb0ca861a63c074f1f632f0b8_720w.jpg](https://image.3001.net/images/20210525/1621924924_60ac9c3c921c84b6bc2f3.jpg!small)

8、从进程表中看见有进程CnCrypt，猜测使用CnCrypt进行加密的，使用CnCrypt挂载文件进行解密。

![v2-0da07bafab0ce0a10625fd7485f0f678_720w.jpg](https://image.3001.net/images/20210525/1621924924_60ac9c3cd874035d4993e.jpg!small)

 **得到flag。**

![v2-537df942627a67ddd7e631d945133ec5_720w.jpg](https://image.3001.net/images/20210525/1621924925_60ac9c3d391951da556fd.jpg!small)

