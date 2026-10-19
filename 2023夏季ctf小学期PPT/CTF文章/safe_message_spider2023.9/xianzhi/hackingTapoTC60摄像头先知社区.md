不久前，我在亚马逊英国看到了一款Tapo TC60“Smart Security
Camera”特价出售。在尝试破解智能锁盒和旧保险柜锁的经历后，我想尝试破解一些更多功能的东西。以下是我的经历。

![](./img/4250396344670446924.png)

打开盒子后，我们会看到通常会使用到的手册、电源适配器和摄像头本身。摄像头比我预期的要小得多，没有明显的进入方式（拆解过程中。

![](./img/4700513259676456999.png)

我打开它并在Tapo应用程序中设置它。我本应该在BurpSuite中捕获设置流量，但是对于这篇文章，我更感兴趣的是硬件。

![](./img/6908612572450034887.png)

完成设置后，我开始拆卸摄像头。首先移除支架，然后找到了一个TC100的拆卸视频，该视频展示了如何进入主摄像头机身（拆解过程中。

![](./img/729844035732637299.png)

主机箱前面有4个夹子固定着，插入IFixIt拾取工具之一即可释放。这样我们就可以进入主板（拆解过程中。

![](./img/8608484455866678051.png)

接近这种东西时首先要做的事情之一是尝试识别板上的芯片以及任何UART /
JTAG接口。识别芯片将为我们提供对设备正在执行的深刻理解，并帮助我们了解可能找到有趣数据的位置。此板有一些明显的组件。

![](./img/1067820231228993314.png)

大芯片是Ingenic
T31，一种系统芯片视频处理器。关于这个芯片几乎没有信息可用，但我们知道它将为我们处理视频。还有一个RTL8188FTV，一种WiFi和网络USB芯片，设计用于包括IP摄像头在内的设备。还有其他IC，包括音频放大器和通常的无源元件的选择。重要的是，在板的这一侧没有存储器芯片。  
翻转板后，我们可以看到可拆卸的摄像头组件。取下此组件后会显示出传感器和另一个IC。

![](./img/7704442056802011530.png)

这是XMC 25QH64C，一种串行闪存存储器芯片。这几乎肯定是存储此设备固件的位置。  
检查板还会显示出一些垫子，看起来非常像UART接口，就在T31芯片上方。  
使用万用表快速检查显示出一个引脚连接到地面，一个可能连接到Vcc，留下两个未标识的引脚。使用示波器探测这些引脚会显示出数据正在输出。

![](./img/5737120699202861591.png)

连接逻辑分析仪验证这确实是UART接口。我们可以看到连接电源时显示U-Boot日志。

![](./img/4437243921799406149.png)

![](./img/8878571238588443163.png)

现在我们知道哪个引脚是TX，我们可以连接Tigard板并尝试与设备交互。  
浏览控制台数据时，没有明显的方法可以中断引导序列。  
此时，我开始研究此设备的先前工作。虽然我找不到任何关于TC60的信息，但我确实找到了有关TC200和TC100的一些信息。看起来TC100基本上是相同的设备，因此许多信息可能有用。  
最有用的信息来源是[此](https://drmnsamoliu.github.io/index.html
"此")博客文章，该文章还链接到与TC200相关的[GitHub](https://github.com/nervous-inhuman/tplink-tapo-c200-re "GitHub")项目。  
这些项目包含一些有用的信息，例如U-Boot加载程序的转义序列，使我们能够中断引导序列并进入root Shell。

    
    
    ------Firmware check pass!-----    Autobooting in 1 seconds
    isvp_t31# 
    isvp_t31# slp
    Unknown command 'slp' - try 'help'
    isvp_t31# setenv bootargs console=ttyS1,115200n8 mem=45M@0x0 rmem=19M@0x2d00000 root=/dev/mtdblock6 rootfstype=squashfs spdev=/dev/mtdblock7 noinitrd init=/bin/sh
    isvp_t31# 
    isvp_t31# printenv
    baudrate=115200
    bootargs=console=ttyS1,115200n8 mem=45M@0x0 rmem=19M@0x2d00000 root=/dev/mtdblock6 rootfstype=squashfs spdev=/dev/mtdblock7 noinitrd init=/bin/sh
    bootcmd=sf probe;sf read 0x80700000 0x80200 0x175000; bootm 0x80700000
    bootdelay=1
    ethaddr=00:d0:d0:00:95:27
    gatewayip=193.169.4.1
    ipaddr=193.169.4.81
    loads_echo=1
    netmask=255.255.255.0
    serverip=193.169.4.2
    stderr=serial
    stdin=serial
    stdout=serial
    
    Environment size: 437/16380 bytes
    isvp_t31# sf probe;sf read 0x80700000 0x80200 0x175000; bootm 0x80700000
    <snipped>
    
    BusyBox v1.19.4 (2022-09-30 05:46:09 CST) built-in shell (ash)
    Enter 'help' for a list of built-in commands.
    
    /bin/sh: can't access tty; job control turned off
    / # ls
    bin      etc      mnt      proc     root     sp_rom   tmp      var
    dev      lib      overlay  rom      sbin     sys      usr      www
    / # help
    Built-in commands:
    ------------------            . : [ [[ alias bg break cd chdir command continue echo eval exec
            exit export false fg getopts hash help jobs kill let local printf
            pwd read readonly return set shift source test times trap true
            type ulimit umask unalias unset wait
    
    / # id
    uid=0(root) gid=0(root)
    

从这里开始，我们需要挂载/proc目录，这使我们可以访问一些通常的Linux工具。我们还可以cat / etc /
passwd文件出文件内容，这为我们提供了根用户哈希值。

    
    
    root:$1$Xr8fF4xx$BFl2tPv719kYGwDH5TFrm.:0:0:root:/root:/bin/ash
    nobody:*:65534:65534:nobody:/var:/bin/false
    admin:*:500:500:admin:/var:/bin/false
    guest:*:500:500:guest:/var:/bin/false
    ftp:*:55:55:ftp:/home/ftp:/bin/false
    / # cat /etc/shadow
    root:x:0:0:99999:7:::
    daemon:*:0:0:99999:7:::
    ftp:*:0:0:99999:7:::
    network:*:0:0:99999:7:::
    nobody:*:0:0:99999:7:::
    

我对此设备的先前工作进行的研究还发现了一篇学术[论文](https://www.researchgate.net/publication/357953307_Leaving_Your_Things_Unattended_is_No_Joke_Memory_Bus_Snooping_and_Open_Debug_Interface_Exploits
"论文")，讨论了围绕安全性差的物联网设备存在潜在风险的一些情况。这其中包括一个假设情景：TC100摄像头所有者在停电期间将无人看管（因此摄像头就不会记录被篡改的情况），而室友利用此机会提取设备固件。然后在离线状态下进行分析，最终使他们能够访问设备的实时视频（假设他们与设备在同一网络上）。我们将尝试重新复现此攻击。  
论文中使用的摄像头型号其闪存芯片位于板上不同位置，并且可以轻松使用SOP8夹子进行访问。作者还能够在板上桥接连接以将主IC置于复位模式。正如我们在先前的帖子中简要介绍的那样，我们需要在转储内存时停止主IC与闪存内存交流，否则它将扭曲我们的结果。在此设备中，闪存芯片和主IC共享相同的电源轨道。在转储其内存时向芯片供电也会导致主IC上电。在我们的情况下，主IC位于板的另一侧，并且闪存芯片位于摄像头镜头组件下方。虽然仍然可以通过这种方式提取固件，但对于具有有限时间访问设备的恶意行为者来说，这将更加复杂。我们需要另一种实现方法。  
在攻击设备时，访问制造商固件非常有用。尽管用户可能在设置期间配置了某些凭据材料，但对设备上固件进行分析可能会揭示默认凭据或其他弱点，我们可以利用它们而无需从运行设备中提取固件。幸运（或不幸），制造商越来越意识到这些攻击，并且通常不会在其网站上提供固件下载。TPLink（制造Tapo摄像头）就是这样一家公司。他们确实提供了这些设备中使用的GPL代码副本，在其他型号的摄像头中包含了有用信息（请参见上面链接的研究）。在我们当前情况下，这些文件中似乎没有任何有用的信息。我们需要工厂固件。  
TC60具有“over the
air”固件更新功能。摄像头可能会联系更新服务器并下载固件映像。该应用程序还显示当前固件版本以及任何待处理更新的详细信息，因此它很可能也会与更新服务器通信。与尝试截获设备本身的流量相比，拦截应用程序和设备之间的流量要容易得多，因此这是我首先尝试的路径。将我的手机配置为通过BurpSuite代理流量后，我打开了Tapo应用程序并点击了一下。在发送给摄像头之一的请求响应正文中有一个URL可下载固件更新。

![](./img/7688306494422641632.png)

我下载了固件并使用-E标志将其通过binwalk运行。这显示文件熵。

    
    
    binwalk -E Tapo_TC60v4_en_1.3.7_Build_230627_Rel.41895n_up_boot-signed_1691484740866.bin
    
    WARNING: Failed to import matplotlib module, visual entropy graphing will be disabled
    
    DECIMAL       HEXADECIMAL     ENTROPY
    --------------------------------------------------------------------------------    0             0x0             Rising entropy edge (0.994108)
    

这看起来不太好。高熵很可能意味着固件已加密，我们可以使用binwalk尝试提取数据来验证它。

    
    
    binwalk -e Tapo_TC60v4_en_1.3.7_Build_230627_Rel.41895n_up_boot-signed_1691484740866.bin
    
    DECIMAL       HEXADECIMAL     DESCRIPTION
    --------------------------------------------------------------------------------    

如预期所示，binwalk无法提取任何数据。运行字符串文件也没有结果。运行文件字符串也没有结果。摄像头上的固件必须包含我们需要解密下载的密钥，但如果我们无法访问它们，这就没有什么用了。幸运的是，我们有一个UART
shell。  
由于此设备具有SD卡插槽，因此我们还可以通过此shell转储固件。 “tapo
200研究项目”博客详细介绍了如何提取固件的说明。在高层次上，我们可以将SD卡挂载到闪存上，将其映射到磁盘上的文件中，并将它们复制到flashdump.bin文件中。完整的说明在链接的帖子中提供，我不会在此重现。  
现在，我们可以在提取的固件上运行binwalk，这使我们可以访问文件系统内容。

    
    
    ❯ binwalk flashdump.bin
    
    DECIMAL       HEXADECIMAL     DESCRIPTION
    --------------------------------------------------------------------------------    15892         0x3E14          LZO compressed data
    26624         0x6800          uImage header, header size: 64 bytes, header CRC: 0xA3F3CA56, created: 2022-09-29 21:36:29, image size: 155294 bytes, Data Address: 0x80100000, Entry Point: 0x0, data CRC: 0xCEE6C40F, OS: Firmware, CPU: MIPS, image type: Firmware Image, image name: "u-boot-lzo.img"
    26688         0x6840          LZO compressed data
    141029        0x226E5         CRC32 polynomial table, little endian
    145193        0x23729         LZO compressed data
    148629        0x24495         Android bootimg, kernel size: 0 bytes, kernel addr: 0x70657250, ramdisk size: 543519329 bytes, ramdisk addr: 0x6E72656B, product name: "mem boot start"
    188181        0x2DF15         PEM certificate
    188910        0x2E1EE         PEM certificate
    190126        0x2E6AE         PEM certificate
    191346        0x2EB72         PEM certificate
    192538        0x2F01A         PEM certificate
    196864        0x30100         gzip compressed data, from Unix, last modified: 2022-09-29 22:06:28
    393216        0x60000         LZO compressed data
    484818        0x765D2         CRC32 polynomial table, little endian
    488822        0x77576         LZO compressed data
    524800        0x80200         uImage header, header size: 64 bytes, header CRC: 0x1805EB61, created: 2022-09-29 22:06:13, image size: 1296787 bytes, Data Address: 0x80010000, Entry Point: 0x8031B470, data CRC: 0xD607E5B7, OS: Linux, CPU: MIPS, image type: OS Kernel Image, compression type: lzma, image name: "Linux-3.10.14__isvp_swan_1.0__"
    524864        0x80240         LZMA compressed data, properties: 0x5D, dictionary size: 8388608 bytes, uncompressed size: -1 bytes
    1823232       0x1BD200        Squashfs filesystem, little endian, version 4.0, compression:xz, size: 2405062 bytes, 647 inodes, blocksize: 131072 bytes, created: 2022-09-29 22:06:33
    4456448       0x440000        Squashfs filesystem, little endian, version 4.0, compression:xz, size: 3053252 bytes, 162 inodes, blocksize: 131072 bytes, created: 2022-09-29 22:06:35
    8404500       0x803E14        LZO compressed data
    8415232       0x806800        uImage header, header size: 64 bytes, header CRC: 0xA3F3CA56, created: 2022-09-29 21:36:29, image size: 155294 bytes, Data Address: 0x80100000, Entry Point: 0x0, data CRC: 0xCEE6C40F, OS: Firmware, CPU: MIPS, image type: Firmware Image, image name: "u-boot-lzo.img"
    8415296       0x806840        LZO compressed data
    8529637       0x8226E5        CRC32 polynomial table, little endian
    8533801       0x823729        LZO compressed data
    8537237       0x824495        Android bootimg, kernel size: 0 bytes, kernel addr: 0x70657250, ramdisk size: 543519329 bytes, ramdisk addr: 0x6E72656B, product name: "mem boot start"
    8576789       0x82DF15        PEM certificate
    8577518       0x82E1EE        PEM certificate
    8578734       0x82E6AE        PEM certificate
    8579954       0x82EB72        PEM certificate
    8581146       0x82F01A        PEM certificate
    8585472       0x830100        gzip compressed data, from Unix, last modified: 2022-09-29 22:06:28
    8781824       0x860000        LZO compressed data
    8873426       0x8765D2        CRC32 polynomial table, little endian
    8877430       0x877576        LZO compressed data
    8913408       0x880200        uImage header, header size: 64 bytes, header CRC: 0x1805EB61, created: 2022-09-29 22:06:13, image size: 1296787 bytes, Data Address: 0x80010000, Entry Point: 0x8031B470, data CRC: 0xD607E5B7, OS: Linux, CPU: MIPS, image type: OS Kernel Image, compression type: lzma, image name: "Linux-3.10.14__isvp_swan_1.0__"
    8913472       0x880240        LZMA compressed data, properties: 0x5D, dictionary size: 8388608 bytes, uncompressed size: -1 bytes
    10211840      0x9BD200        Squashfs filesystem, little endian, version 4.0, compression:xz, size: 2405062 bytes, 647 inodes, blocksize: 131072 bytes, created: 2022-09-29 22:06:33
    12845056      0xC40000        Squashfs filesystem, little endian, version 4.0, compression:xz, size: 3053252 bytes, 162 inodes, blocksize: 131072 bytes, created: 2022-09-29 22:06:35
    

重新审视学术论文，我们发现作者遵循了“tapo 200 research
project”[博客](https://drmnsamoliu.github.io/flashdump.html
"博客")中概述的过程，即从设备中提取配置数据并进行离线解密。我们的设备上仍然加密了配置数据，并且与其他设备一样，我们可以手动离线解密数据，或者设备上存在一个实用程序可以解密数据。我们可以通过UART
shell执行以下步骤来验证其有效性。

  * 挂载/proc
  * 挂载/dev
  * 挂载/tmp
  * 运行uc_convert实用程序
    
        mount -t proc none /proc
    mount -t tmpfs tmpfs /dev -o mode=0755,size=512K
    mount tmpfs /tmp -t tmpfs -o size=20633600,nosuid,nodev,mode=1777
    mknod /dev/slp_flash_chrdev c 222 0
    /bin/uc_convert -t 0
    

这将创建一个包含解密设备配置的目录/tmp。  
在我们的假想攻击场景中，我们可以通过UART
shell在设备上执行此步骤，并通过终端日志或写入SD卡来窃取解密后的数据。我们根本不需要抓取固件，这对于这个设备来说肯定有所帮助，因为闪存芯片位于摄像头镜头组件下方。

![](./img/4937515344158701794.png)

但是，正如我们所看到的，“third_account”用户名和密码值已被清除。这与论文中呈现的设备不同（在那里作者能够破解此帐户的哈希并使用凭据访问视频流）。那就结束了吗？并非完全如此……  
我们可以作为root访问设备。我们是否可以在third_account部分下添加一个帐户并访问视频源？  
经过一些调查，结果表明是肯定的，但有一些警告。使用uc_convert实用程序提取配置后，我们可以在/tmp/etc/uc_conf/user_management中找到用户帐户详细信息，如上所示。  
“root”帐户blob包含我们设置摄像头时配置的凭据。
passwd字段是密码的简单MD5哈希值。我们可以尝试破解它，但如果用户选择了强密码，则可能需要一些时间。 ciphertext
blob是RSA加密的，稍后我们将介绍它。  
默认情况下，third_account
blob被禁用。用户名和密码值设置为“—-”。此帐户用于允许从摄像头访问RTSP流，并且必须通过移动应用程序启用。启用此功能会带来一些警告：

![](./img/1978073404814211192.png)

我最初认为只需要用户名和密码值即可访问RTSP流。我修改了配置文件，添加了一个具有已知密码哈希值（请注意，如果不是大写字母，则无法工作）的“backdoor”帐户，将配置写回flash，重新启动摄像头并尝试使用VLC访问RTSP流。这给了我一个身份验证错误。  
经过大量实验，结果表明，必须还设置ciphertext值以匹配用户名和密码值。移动应用程序使用passwd值验证密码，当你在RTSP帐户上执行“更改密码”选项时，但RTSP流使用ciphertext值。我不是逆向工程师，但是我们可以使用binary
ninja和ghidra验证这一点。  
如果我们将该设备用于RTSP的应用程序（即cet）放入binary ninja云中，并搜索“ciphertext”，则会得到以下结果：

![](./img/3146897637405777734.png)

更详细地查看此函数后，我们看到它在读取配置文件中的ciphertext块后调用以下函数：  
rsa_decrypt是对libdecrypter.so的外部引用，我们可以通过对先前从设备中转储的固件进行grep操作来找到它。  
使用Ghidra打开此文件，我们可以找到rsa_decrypt export并从那里开始分析。

![](./img/1335611366589421507.png)

在private_decrypt函数中，我们可以看到代码从某处加载RSA密钥，然后进行base64解码和RSA解密。

![](./img/5520278955294128423.png)

我试图弄清楚RSA密钥从何处加载，但是我太笨了，无法弄清楚这个反编译代码：

![](./img/8657204041893111051.png)

运行文件字符串会返回一些RSA密钥，但我无法弄清楚如何使用它们来解密配置文件。由于本文已经足够长了，因此我略过了这一步，但是如果你想跟随所有操作，请运行strings
libdecrypt.so  
我有一种预感解密密钥是硬编码的，并且可能在每个设备上都相同。由于无法正确逆向解密代码，我采取了下一个最好的方法，并订购了另一个设备以测试此理论。  
我在新的tapo账户上设置了此第二个设备，执行了初始设置，然后拆开并连接到UART接口。请注意，第二个设备连接到相同的WiFi网络。我怀疑TPLink会将其用作encryption
key的种子，但我之前也犯过错。

![](./img/2415322601388017953.png)

从这里开始，我通过串行连接，在vi（是的，已经在设备上自带了）中打开user_manage文件，并覆盖文件中的用户名、passwd和ciphertext值。对于用户名和passwd，我使用backdoor和Password206的MD5哈希值。对于密码文本，我复制了在原始设备上生成的密码文本，该密码文本是通过移动应用程序设置用户名和密码生成的。  
我将修改后的配置写回flash，重新启动摄像头，并尝试使用VLC连接到RTSP流：

![](./img/8356868016028017464.png)

正如我们所看到的那样，重复使用ciphertext值被接受，并授予我们访问摄像头视频流的权限（如果你想知道，在我的工作台上是Sensepeak
Mat）。实际执行此攻击大约需要5分钟时间，从未打开的摄像头外壳开始到访问流为止。  
虽然我们可能没有重新复现论文中呈现的确切攻击方式，但我们肯定已经实现了我们想要实现的目标。由于我们没有转储闪存RAM，因此我们需要为设备提供电源。这意味着我们不再依赖于等待随机断电以启用攻击。由于我们正在通过UART与设备交互，因此我们需要提供电源，这也将启用视频捕获功能。你必须想象一下如何在不被检测到的情况下完成此操作;）。虽然在此处讨论了添加backdoor帐户的步骤，但我省略了一些步骤，并选择不发布我用于backdoor摄像头的Python代码。仅凭此帖子中的信息，你将无法重新复现此攻击。为了完整起见，让我们看看是否可以让离线解密向量正常工作。我们参考的先前工作详细介绍了解密代码的工作方式，包括加密密钥的位置。学术论文指出，他们的设备（TC100）中的密钥与博客文章中的密钥（TC200）不同。他们在同一位置找到了密钥，并能够使用相同的技术解密其配置数据。让我们看看我们的设备是否使用相同的方法。首先，我们将uc_convert二进制文件加载到binary
ninja云中。

![](./img/4302883358363976019.png)

我们已经确定我不是逆向工程师，但最终我可以弄清楚这是解析参数。这可能最终看起来像这样：

    
    
    int main(int argc, char **argv)
    {
        if(argc < 3)
        {
            showhhelp();
            return -1
        }
        while((c = getopt(argc, argv, "t:d:c")))
        {
            switch (c){
                case 'd':
                    updateFWDescription(); //we dont care what this does
                    break;
                case 't':
                    int foo = atoi(optarg);
                    break;
                case 'c':
                    //do a thing
                    break;
                default:
                    return -1;
        }
    }
    

此时，我开始寻找其他函数。唯一突出的其他函数是这个函数，我很快意识到它超出了我逆向工程的能力范围。

![](./img/3994506537210021125.png)

回到绘图板。我们参考的先前工作能够定位用于派生加密密钥的字符串，在他们的示例中为“C200 1.0”。研究论文的作者发现他们的密钥为“C100
2.0”。在两种情况下，这都是型号编号和固件硬件版本。让我们在固件转储中为我们的型号编号进行grep操作…

![](./img/8304881594295254921.png)

这看起来很有希望。让我们在我们从先前工作中获得的哈希函数中尝试一下。

![](./img/1520342079982878995.png)

并将其从ASCII转换为十六进制后，我们可以运行OpenSSL命令：

    
    
    openssl enc -d -des-ecb -nopad -K 3463666461643831 -in mtdblock3.bin -out test.bin`
    

如果你想知道此处的bin文件来自何处，那么我已经使用SD卡从摄像头中转储它，以与完整固件转储相同的方式，但是我只转储了“config”分区。

![](./img/7780513473665630007.png)

提取后，我们获得了配置数据。

![](./img/1036025801139145750.png)

因此，这款摄像头型号使用与C100和C200相同的方法来保护其配置数据，尽管使用不同的密钥。值得注意的是，我确实站在巨人的肩膀上，在这里我无法自己找出加密方法。让我们总结一下。回顾一下，我们已经看到了如何通过物理访问其中一个摄像头来转储固件。我们还可以连接到UART控制台，访问root
shell并向摄像头添加backdoor帐户，以允许对视频流进行秘密访问。这个backdoor账户在应用程序中并不显眼，除非用户想启用RSTP访问，否则很可能不会被发现。我们需要物理访问设备，并在同一网络上才能查看视频源，因此此处的攻击可能性非常低。最后，我们得知我真的不知道Ghidra如何工作。  
From：`https://medium.com/@two06/hacking-a-tapo-tc60-camera-e6ce7ca6cad1`

