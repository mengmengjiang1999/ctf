# 漏洞信息

从CVE-2019-10999查看该CVE的基础信息得知，这是一个栈溢出漏洞，攻击者在已登录的情况下可以通过向wireless.htm发送一个超长的WEPEncryption参数导致栈溢出，从而执行任意命令攻击.
现在我们利用Shambles
Desktop工具确定这个漏洞的位置并且执行一次栈溢出攻击。从Dlink官网查看存在这个漏洞的设备和版本信息。我们选择DCS-932L的v2.17.01版本。下载对应固件。

# 复现过程

首先用Shambles Desktop打开固件，利用Shambles
Desktop的在线解包功能将固件解包并抽取文件系统，这样固件包的内容将会用可视化的文件目录树形式(如图1所示)展现，方便分析。同时Shambles
Cloud会对解包信息初步分析，确定设备，产商，芯片架构，设备类型等信息。如下图右侧的Firmware Info的Hardware
Information所示，该设备是D-Link的MIPS芯片架构的嵌入式摄像头设备。

 **1\. 静态分析**

![1665979219_634cd353075f1b5cfdaae.png!small](https://image.3001.net/images/20221017/1665979219_634cd353075f1b5cfdaae.png!small)

图1

首先我们通过Shambles Desktop对该固件进行静态代码分析，确定该漏洞的代码位置。

CVE漏洞信息中提到该漏洞存在于设备的web服务器可执行文件alphapd中，攻击者在请求wireless.htm文件时，在请求参数WEPEncryption当中构造超长参数可导致栈溢出从而执行任意命令。

所以首先在文件管理器中搜索“ **alphapd** ”关键字，从而寻找对应的文件进行静态反编译操作，然后在当前反编译窗口搜索“
**WEPEncryption** ”关键字，结果返回十几处匹配信息 (如图2所示)，再结合右侧代码风险检测窗“ **ELF Vunerability
Info** ”的检测结果(如图2所示)进行分析。

两处信息都多次提到sub_43b7c0附近的地址，代码风险检测中直接指出地址 <sub_43b7c0+1b4>
strcpy相关的栈溢出风险。所以<sub_43b7c0+1b4>的可能性比较大，双击<sub_43b7c0+1b4>跳转到 **strcpy(
&var30, v2)**处查看ASM代码。

![1665979228_634cd35ce589bd8697393.png!small](https://image.3001.net/images/20221017/1665979228_634cd35ce589bd8697393.png!small)

图2

ASM代码只能看到该处是一个strcpy调用，按F5快捷键切换到“ **pseudo view**
”查看反汇编代码。如图3所示，25行把v2的内容拷贝到栈变量&var30的地址。11~19行的反编译代码逻辑为：
**“当p0内存地址中不存在WEPEncryption参数的时候，不进行任何有效操作并直接返回，而当p0内存地址中存在WEPEncryption参数的时候，websGetVar返回WEBEncryption的参数内容”**
。结合CVE信息以及函数名websGetVar的含义，推测sub_43b7c0可能是处理网络请求参数WEPEncryption的函数。验证这一猜测，需要证明当针对wireless.htm发送带有WEPEncryption参数的网络请求时，
**sub_43b7c0** 会被执行，这就需要动态模拟运行固件。

![1665979239_634cd367d1f4f0c27143b.png!small](https://image.3001.net/images/20221017/1665979239_634cd367d1f4f0c27143b.png!small)

图3

 **2\. 动态调试**

按照上述静态化分析的结论，我们得知漏洞的成因以及可能的指令位置，接下来进入第二阶段的动态验证流程: 利用Shambles Desktop的固件仿真模拟“
**Virtual Machine** ”（以下简称 **“VM”** ）功能对该固件进行动态调试。 进入仿真模拟功能，首先我们需要将Shambles
Desktop的文件管理模块切换到“ **云端模式**
”下，然后在右侧工具栏VM管理工具中点击新建，选择alphapd所在的文件系统，建立一个模拟器(如图4所示)。然后在文件管理器中选中alphapd所在的文件系统，右键打开一个终端(下文称文件系统终端)。如下图5所示，固件的文件系统被挂载起来了。

![1665979249_634cd371e452b5b6ed813.png!small](https://image.3001.net/images/20221017/1665979249_634cd371e452b5b6ed813.png!small)

图4

![1665979258_634cd37af37ae3519a04f.png!small](https://image.3001.net/images/20221017/1665979258_634cd37af37ae3519a04f.png!small)

图5

    
    
    /bin/alphapd
    
    alphapd: Startup!
    
    alphapd: cannot openpidfile#
    

在新打开的文件系统终端输入:"/bin/alphapd", 启动 **alphapd** ，有错误返回，启动alphapd出错。

在alphapd中搜索对应的错误信息"cannot open pid
file"，只有两处引用，一处是在.rodata(字符串在可执行文件中的存放区域)，另外一处是在代码段中的引用。优先查看代码段，分析该函数(如图6所示)，62行处的if语句表明当某文件不存在的时候，会抛出"cannot
open pid file"的错误。在62行处点击Tab键，切换到ASM
View，从ASM的反编译辅助信息(如图7所示)推断，这个文件应该是/var/run/alphapd.pid。

![1665979266_634cd38245e7e748da18d.png!small](https://image.3001.net/images/20221017/1665979266_634cd38245e7e748da18d.png!small)

图6

![1665979272_634cd388a88951156a9ed.png!small](https://image.3001.net/images/20221017/1665979272_634cd388a88951156a9ed.png!small)

图7

手动创建"alphapd.pid"，命令如图8所示。再次运行alphapd，旧错误已经解决，有新的错误。同样的，搜索这个错误，定位到原因是/var/run/nvramd.pid文件不存在。

    
    
    #mkdir/var/run
    
    #touch/var/run/alphapd.pid
    
    #/bin/alphapd
    
    alphapd: Startup!
    
    alphapd: waiting fornvram_daemonalphapd: .alphapd: .alphapd: .alphapd: 
    .alphapd: .alphapd: .alphapd: .alphapd: .alphapd: .alphapd: .alphapd: 
    .alphapd: .alphapd: .alphapd: .alphapd: please executenvram_daemonfirst!#
    

![1665979285_634cd3952246ddd96103a.png!small](https://image.3001.net/images/20221017/1665979285_634cd3952246ddd96103a.png!small)

图8

创建"/var/run/nvramd.pid"文件, 再次运行alphapd。旧错误已经解决，有新的错误出现。

    
    
    #touch/var/run/nvramd.pid
    
    #/bin/alphapd
    
    alphapd: Startup!
    
    alphapd: Can't getlanipfromsysinfo!
    
    alphapd: failed toconvert  tobinaryipdataalphapd: Shutdown!
    

同样搜索对应的错误，定位原因是nvram_bufget拿不到"IPAddress"(如下所示）。nvram_bufget的功能是读取信息。Shambles的模拟环境，支持从配置文件初始化设备参数配置。所以我们只需要做正确的配置，先查看固件中是否存在配置文件，不存在的话就需要从可执行文件中查询设备运行参数。全局搜索”IPAddress”关键字，有多个文件引用，因为是查找配置文件，所以先排除可执行文件、sh文件以及cgi文件，就只剩下RT2860_default_vlan这个文件了，查看RT2860_default_vlan，发现存在多种参数配置，"IPAddress"也在其中，所以RT2860_default_vlan就是设备参数配置文件的概率比较大，可以拿来测试一下。这里比较幸运，搜索结果多的时候，需要做的排除工作比较多。

Shambles的模拟环境在/shambles目录下预置了libnvram.so，可以从配置文件加载设备参数信息。把RT2860_default_vlan拷贝到libnvarm.so所在目录，重命名为nvram.ini，再次运行alphapd，因为这次要用libnvram模拟设备信息，所以运行时需要预加载libnvram.so
。输入命令"LD_PRELOAD=/shambles/libnvram.so
/bin/alphapd"，运行结果如下所示，虽然还有一些其他的错误抛出，但是alphapd并没有中断，说明成功启动。

    
    
    #mkdir-p /shambles/libnvram
    
    #cp /etc_ro/Wireless/RT2860AP/RT2860_default_vlan /shambles/nvram.ini
    
    #LD_PRELOAD=/shambles/libnvram.so /bin/alphapd
    
    nvram_get_buf:IPAddress
    
    sem_get: Key: 41370002
    
    sem_get: Key: 41370002
    
    nvram_get_buf: = "2.65.87.200"
    
    alphapd: Can't getlanipfromsysinfo!
    
    alphapd: Version 2.1.8 running at address 2.65.87.200:80
    
    nvram_get_buf:AccessControlEnable
    
    sem_get: Key: 41370002
    
    sem_get: Key: 41370002
    
    nvram_get_buf: = "0"
    
    nvram_get_buf: User1
    
    sem_get: Key: 41370002
    
    sem_get: Key: 41370002
    
    nvram_get_buf: = ""
    
    nvram_get_buf: User2
    
    sem_get: Key: 41370002
    
    sem_get: Key: 41370002
    
    nvram_get_buf: = ""
    
    nvram_get_buf: User3
    
    sem_get: Key: 41370002
    
    sem_get: Key: 41370002
    
    nvram_get_buf: = ""
    
    nvram_get_buf: User4
    
    sem_get: Key: 41370002
    
    sem_get: Key: 41370002
    
    nvram_get_buf: = ""
    
    nvram_get_buf: User5
    
    sem_get: Key: 41370002
    
    sem_get: Key: 41370002
    
    nvram_get_buf: = ""
    
    nvram_get_buf: User6
    
    sem_get: Key: 41370002
    
    sem_get: Key: 41370002
    
    nvram_get_buf: = ""
    
    nvram_get_buf: User7
    
    sem_get: Key: 41370002
    
    sem_get: Key: 41370002
    
    nvram_get_buf: = ""
    
    nvram_get_buf: User8
    
    sem_get: Key: 41370002
    
    sem_get: Key: 41370002
    
    nvram_get_buf: = ""
    

一般alphapd默认的web服务端口是80（如图9所示），设置端口转发，访问http://127.0.0.1:80试试。

![1665979326_634cd3bedb2439328d088.png!small](https://image.3001.net/images/20221017/1665979326_634cd3bedb2439328d088.png!small)

图9

![1665979333_634cd3c50f6ff4d52a3b6.png!small](https://image.3001.net/images/20221017/1665979333_634cd3c50f6ff4d52a3b6.png!small)

图10

![1665979339_634cd3cb659e8a30cb074.png!small](https://image.3001.net/images/20221017/1665979339_634cd3cb659e8a30cb074.png!small)

图11

用浏览器访问下http://127.0.0.1，显示如上图10所示界面，在该设备上，默认admin秘密是空。点击登录后看到如上图11所示界面，证明alphapd
web服务正常运行。

 **3\. CVE重现**

下面结合我们第一节的静态分析结论，来重现该CVE。首先验证alphapd可以响应针对wireless.htm的请求。验证方法如下:
发送带有WEPEncryption的请求到wireless.htm,如果正常返回信息，则说明alphapd响应该网络请求。在电脑本机命令行输入"curl
http://127.0.0.1/wireless.htm?WEPEncryption=FEWFEW"，返回信息如下图12所示，说明alphapd响应带有WEPEncryption的请求。

![1665979347_634cd3d38cf6ed25cc852.png!small](https://image.3001.net/images/20221017/1665979347_634cd3d38cf6ed25cc852.png!small)

图12

然后验证向wireless.htm发送带有WEBEncryption的网络请求，可以执行到sub_43b7c0+1b4处的strcpy。首先以调试模式启动alphapd。在刚才运行alphapd的文件系统终端中按ctrl+c关闭这个进程。然后在Shambles
Desktop
的alphapd反编译界面点击调试配置把libnvram.so配置为预加载库。(这么做和我们刚才运行LD_PRELOAD=/shambles/libnvram.so
/bin/alphapd是一样的作用)。启动调试，事件日志窗口返回的日志如图13所示。和文件系统终端运行alphapd显示的日志是一样的，证明调试正常启动。

![1665979358_634cd3dec1cdee687881c.png!small](https://image.3001.net/images/20221017/1665979358_634cd3dec1cdee687881c.png!small)

![1665979391_634cd3ff8b8b77bf49aa2.png!small](https://image.3001.net/images/20221017/1665979391_634cd3ff8b8b77bf49aa2.png!small)图13

先在下图标注位置打断点(如图断点1所示)，发送对应网络请求，调试进程确实会在断点1停留，证明向wireless.html发送带有WEPEncryption参数的网络请求会执行到strcpy。

![1665979398_634cd4060554c893725e1.png!small](https://image.3001.net/images/20221017/1665979398_634cd4060554c893725e1.png!small)

断点1

最后验证当WEPEncryption的参数过长时，会导致栈溢出。

验证方法如下，分别向wireless.html发送正常长度的WEPEncryption的参数请求和超长度的WEPEncryption的参数请求，网络请求完成后，对比pc寄存器中的信息。如下图断点2所示中位置打断点，查看执行jr后，pc寄存器信息是否被修改。断点2中的ra存储的是断点1
strcpy的调用函数sub_43b7c0执行完成后的跳转地址。jr指令会把ra中的值拷贝到pc寄存器。

 **找到断点2的过程如下:**

把光标放置在sub_43b7c0函数return处(如图14所示)，按tab键切换到" **ASM View**
”。找到对应的jr指令位置。就是下图断点2所示的断点2。

![1665979405_634cd40d4a69c65008095.png!small](https://image.3001.net/images/20221017/1665979405_634cd40d4a69c65008095.png!small)

图14

![1665979411_634cd4135fc0a98084559.png!small](https://image.3001.net/images/20221017/1665979411_634cd4135fc0a98084559.png!small)

断点2

 **测试1:**

启动alphapd调试，在电脑本机命令行输入"curl
http://127.0.0.1/wireless.htm?WEPEncryption=ewfwefwefewf"。调试进程会前后停在断点1和断点2，执行完成后，pc寄存器中的内容是某条指令地址（如图15所示），且网络请求会正常返回。

 **测试2:**

电脑终端命令行输入"curl
http://127.0.0.1/wireless.htm?WEPEncryption=ewfwefwefewffeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeefwefwefwefwefwwwwwwwwwwvvvvewfwefwefwefwefwefwefwefweffweeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"。调试进程会前后停在断点1和断点2，执行完成后，pc寄存器中的内容不再是某一条指令地址，而是被修改为某个内存地址(如图16所示)，此时继续执行，alphapd会崩溃，说明栈已经被破坏。

以上两次测试结果对比说明发送带有WEPEncryption参数的网络请求到，会执行strcpy。这个函数会让用户输入变量拷贝到栈内存。从而导致用户输入变量可以任意修改栈内存。攻击者通过巧妙的WEPEncryption的参数构造，pc寄存器内容可以被修改为其他任意指令的地址，从而执行任意命令攻击。

至此，CVE-2019-10999在Shambles上重现完成。

![1665979421_634cd41de57208d15f474.png!small](https://image.3001.net/images/20221017/1665979421_634cd41de57208d15f474.png!small)

图15

![1665979430_634cd42613c225c378344.png!small](https://image.3001.net/images/20221017/1665979430_634cd42613c225c378344.png!small)

图16

> 源地址：<https://liansecurity.com/#/main/news/_reYGIMBcR9248to5h5p/detail>

