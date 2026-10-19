**在DEF CON
27大会上，我提出了题为“[帮帮我，漏洞！你是我唯一希望”](https://media.defcon.org/DEF%20CON%2027/DEF%20CON%2027%20presentations/DEFCON-27-Jacob-Baines-Help-Me-Vulnerabilities.-Youre-My-Only-Hope.pdf)的讨论。讨论了过去几年有关MikroTik
RouterOS的[利用](https://blog.netlab.360.com/7500-mikrotik-routers-are-forwarding-owners-traffic-to-the-attackers-how-is-yours-en/)，并发布了一个用于帮助在RouterOS 3.x中启用和维持root shell访问的工具[Cleaner
Wrasse](https://github.com/tenable/routeros/tree/master/cleaner_wrasse)。**

**![1.png](https://image.3001.net/images/20190830/1567140241_5d68a991ccbb5.png!small)**

此次DEF CON的讨论还介绍了RouterOS过去和现在的后期利用技术。我大致将讨论分为以下两部分：

> 1.攻击者可以从中执行的位置。
>
> 2.如何实现重启或持久性。

这也是本文的主要内容。但为什么要讨论后期利用呢？事实是，虽然我们可以看到许多有关这些路由器利用的文章。但关于RouterOS后期利用的公开研究却很少或几乎没有。因此，我希望这篇文章及相关工具能够为大家提供思路和帮助。

## RouterOS

在正式开始讨论后期利用之前，你需要对RouterOS的一般设计有所了解。就我们的目的而言，要理解的最重要的事情之一是系统上的所有内容都是一个包。如下图所示，你可以看到我在hAP上安装的所有软件包。

![2.png](https://image.3001.net/images/20190830/1567140264_5d68a9a8ac8f7.png!small)

甚至标准的Linux-y目录（如/bin/, /lib/, /etc/）都来自一个包。系统包被指定。

包使用的文件格式为[NPK](https://github.com/rsa9000/npk-tools)。[Kirils
Solovjovs](https://kirils.org/)制作了该描述文件格式的[图表](https://github.com/0ki/mikrotik-tools/blob/master/npk_descriptions.png)。每个NPK都包含一个squashfs部分。在启动时，[squashfs](https://en.wikipedia.org/wiki/SquashFS)文件系统将被提取并安装到/pckg/目录中（或者根据安装方法进行符号链接）（对于系统包来说，这并不完全正确，但我们可以忽略这一点）。

![3.png](https://image.3001.net/images/20190830/1567140282_5d68a9bacdc6f.png!small)

Squashfs是只读的。从上图中你可以看到，我无法touch
/pckg/dhcp/lol文件。这可能会让你产生错觉认为整个系统都是只读的，但事实并非如此。例如，/pckg/实际上是/ram/中读写tmpfs空间的一部分。

![4.png](https://image.3001.net/images/20190830/1567140296_5d68a9c83e66f.png!small)

此外，系统的/flash/目录指向持久读写存储。那里存储了很多配置信息。此外，只有持久存储用户可以访问，/flash/rw/disk/，在这个空间中被发现。

![5.png](https://image.3001.net/images/20190830/1567140324_5d68a9e407115.png!small)

虽然系统所有的可执行文件似乎都位于只读空间中，但似乎存在一些攻击者可以操作的读写空间，包括tmpfs和persistent。技巧是弄清楚如何使用该空间来实现和维持执行。

另外一件重要的事情是，用户实际上无法访问RouterOS上真正的shell。在上面的截图中，似乎我拥有一个root
shell。但这仅仅是因为我利用了路由器并启用了开发人员的后门。这实际上不太可能，所以我要感谢漏洞的“魔力”。

如果你对RouterOS中的开发人员后门并不熟悉，这里有一个非常简短的概述：自RouterOS
3.x以来，系统被设计为如果系统的特定位置存在特定文件，则提供一个可通过telnet或ssh访问的root busybox
shell（该位置多年来已发生了改变）。假设存在特定文件，则可以通过使用admin用户和密码devel的身份登录访问busybox shell。

在以下视频中你可以看到，我利用[HackerFantastic的set
tracefile漏洞](https://twitter.com/hackerfantastic)，在RouterOS
6.41.4上创建了特定文件/pckg/option。该文件的存在使得后门访问成为可能。当我以devel身份登录、然后删除文件并注销之后，我就不能再访问root
shell了。

## 演示视频

## 攻击来自 SNMP 内部！

snmp二进制文件（/nova/bin/snmp）是系统包的一部分。但是，有各种其他软件包想要将自己的功能添加到snmp中。例如，dhcp包。在下图中，你可以看到/
pckg/dhcp具有/snmp/子目录。

![6.png](https://image.3001.net/images/20190830/1567140350_5d68a9febce9b.png!small)

当snmp二进制文件启动，它将遍历/pckg/中的所有目录并查找/nova/lib/snmp/子目录。该子目录中的任何共享对象都会传递给dlopen()，然后调用共享对象的autorun()。

由于dhcp软件包以只读方式挂载的，因此攻击者无法修改已加载的共享对象。但是/pckg/是读写的，因此攻击者可以引入自己的目录结构（例如/pckg/snmp_xploit/nova/lib/snmp/）。存储在那里的任何共享对象都将由snmp加载。

![7.png](https://image.3001.net/images/20190830/1567140370_5d68aa12b1581.png!small)

攻击者可以隐藏在只读空间的进程中。但是当它与可以将文件写入磁盘（如[CVE-2019-3943](https://www.tenable.com/security/research/tra-2019-16)或[CVE-2018-14847](https://www.tenable.com/cve/CVE-2018-14847)）的漏洞结合使用时，它会更有用。

我写了一个[PoC](https://github.com/tenable/routeros/tree/master/poc/cve_2019_3943_snmp_lib)来说明CVE-2019-3943的用例。实质上，经过身份验证的攻击者可以使用漏洞的目录遍历来创建/pckg/目录结构。

![8.png](https://image.3001.net/images/20190830/1567140389_5d68aa258a655.png!small)

创建目录后，攻击者需要删除磁盘上的共享对象。幸运的是，CVE-2019-3943也可以做到这一点。显然，真正的攻击者可以从共享对象执行任何操作，但是为了概念验证，我直接从构造函数创建了6.41+后门文件。

![9.png](https://image.3001.net/images/20190830/1567140408_5d68aa382c8c9.png!small)

PoC甚至会停止并重启SNMP进程，以确保在不重启系统的情况下加载共享对象。

![10.png](https://image.3001.net/images/20190830/1567140421_5d68aa45bf83d.png!small)

由于/pckg/位于tmpfs空间，因此即使PoC没有删除脚本，脚本创建的目录结构也会在重启时被删除。

与上面类似，我发现我可以从/flash/rw/lib中获取系统二进制文件来加载库。这是因为/rw/lib/是[LD_LIBRARY_PATH](http://tldp.org/HOWTO/Program-Library-HOWTO/shared-libraries.html)环境变量中的第一个条目。

![11.png](https://image.3001.net/images/20190830/1567140441_5d68aa5982a67.png!small)

从/rw/lib/加载库的好处在于，因为它是持久的文件空间，共享对象将在重启后保持不变。唯一的挑战是弄清楚我们想要劫持哪个库。显而易见的选择是libc.so，因为它可以保证在任何地方都能加载。但是RouterOS使用[uClibc](https://www.uclibc.org/)，坦率地说，我不想处理它。

谢天谢地，我偶然发现了这个。

![12.png](https://image.3001.net/images/20190830/1567140455_5d68aa6713355.png!small)

/nova/bin/fileman加载[libz](https://www.zlib.net/)。fileman是通过Winbox或Webfig从用户的/rw/disk目录进行读写操作的系统二进制文件。当用户导航到“Files”界面时，它会被执行，但在用户导航离开后，它会关闭，并闲置一分钟的时间。

为了编译[恶意库](https://github.com/tenable/routeros/tree/master/poc/cve_2019_3943_libz/shared_obj)，我只需下载libz
1.2.11并将此构造函数添加到deflate.c：

    
    
    void __attribute__((constructor)) lol(void)
    {
        int fork_result = fork();
        if (fork_result == 0)
        {
            execl("/bin/bash", "bash", "-c",
               "mkdir /pckg/option; mount -o bind /boot/ /pckg/option",
               (char *) 0);
            exit(0);
        }
    }

你可以再次看到，我刚刚选择创建后门文件。为了[概念验证](https://github.com/tenable/routeros/tree/master/poc/cve_2019_3943_snmp_lib)，我将新的libz.so交叉编译为[MIPS](https://en.wikipedia.org/wiki/MIPS_architecture)
big-endian（大端字节顺序），以便我可以在我的[hAP](https://mikrotik.com/product/RB951Ui-2nD)路由器上测试它。

再次，概念验证使用CVE-2019–3943创建“lib”目录并将库放在磁盘上。

![13.png](https://image.3001.net/images/20190830/1567140480_5d68aa806f869.png!small)

但是，与SNMP攻击不同，/rw/lib/libz.so将在重启后继续运行，并且实际上在启动序列中很早就会加载。这意味着每次重启后，后门文件都将在启动时被创建。

## 签名验证

存储在/flash/中的一个更有趣的东西是/flash/var/pdb/中的文件。

![14.png](https://image.3001.net/images/20190830/1567140495_5d68aa8fad46f.png!small)

事实证明，这是RouterOS存储所有已安装NPK文件的地方。奇怪的是作为root，它们都是可写的。从我的经验可以告诉你，你肯定不想重写系统包。

当我知道我可以通过系统包来break整个系统时，我有点好奇。如果我再小心一点呢？如果我只是重写包的squashfs文件系统呢？会安装吗？

我写了一个名为[modify_npk](https://github.com/tenable/routeros/tree/master/modify_npk)的工具来进行测试。这个工具非常简单，它需要一个有效的MikroTik
NPK（例如[dude-6.44.5.npk](https://download.mikrotik.com/routeros/6.44.5/dude-6.44.5.npk)）和一个用户创建的squashfs。该工具会删除有效的MikroTik
squashfs部分并插入用户的恶意squashfs。从理论上讲，modify_npk只需要一个新的内部squashfs就可以生成一个完美的NPK。

问题是MikroTik在安装NPK包时强制执行签名验证。如果你尝试安装一个modify_npk包，那么RouterOS会将其标记为已损坏并拒绝它。请参阅以下日志文件中的wrasse.npk：

![15.png](https://image.3001.net/images/20190830/1567140620_5d68ab0c4d400.png!small)

我们不能让其他人在这些系统上安装任何他们想要的东西。但如果我们从我们自己的root shell进行安装呢？

![16.png](https://image.3001.net/images/20190830/1567140648_5d68ab286c595.png!small)

理论上，在安装文件系统之前，RouterOS应始终对存储的NPK执行签名检查，因为它们都是读写的，对吧？

![17.png](https://image.3001.net/images/20190830/1567140662_5d68ab3619760.png!small)

在上图中，你可以看到系统上已成功安装了wrasse，bad signature等等！显然，这意味着我创建的squashfs已经安装。

![18.png](https://image.3001.net/images/20190830/1567140680_5d68ab48e038a.png!small)

当然，仅仅安装squashfs还不够，因为我创建的文件系统实际上包含一个rc脚本，它将在启动时创建后门文件。

![19.png](https://image.3001.net/images/20190830/1567140695_5d68ab5783db9.png!small)

这非常有用，因为它会在重启后持续存在。虽然，用户可以通过使用“检查安装（Check Installation）”功能来捕获此特定攻击。

![20.png](https://image.3001.net/images/20190830/1567140711_5d68ab6745e91.png!small)

MikroTik悄无声息地修补了6.42.1中的这个bug。之所以说是“悄无声息”，是因为我没有看到任何特定的发布或说明，这表明他们决定在每次重启时强制执行签名验证。

## RC 脚本

RouterOS使用rc脚本在引导后启动进程，并在关闭期间清理某些进程。操作系统有一个传统的/etc/rc.d/run.d/文件结构，我们将讨论这个结构，但它也有（或有）其他地方执行rc脚本。

## /flash/etc/

如前所述，RouterOS有一个传统的/etc/目录，但由于该目录是只读的，所以攻击者无法修改或引入脚本。

![21.png](https://image.3001.net/images/20190830/1567140732_5d68ab7c8fd35.png!small)

乍一看，就rc脚本而言，它似乎没有那么有用。但是，正如[Bignerd95](https://github.com/BigNerd95)在他的[Chimay
Red](https://github.com/BigNerd95/Chimay-Red)存储库中指出的，你可以在/flash/etc/中创建一个/rc.d/run.d/子目录，其中存储的任何rc脚本在启动和关闭时都将被视为普通rc脚本。

在下面的示例中，你可以看到我创建了/flash/etc/rc.d/run.d/，并打印出了s89lol脚本的位置。重启后，将执行脚本并创建开发人员后门。

这种行为在6.40.9之后被移除。然而，直到那时，这是一个非常简单和方便的持久性机制。

## /rw/RESET

RouterOS在/etc/rc.d/run.d/中有一堆脚本，但有两个我想特别拿来说下。第一个是S08config，这是因为在6.40.5中它包含了以下逻辑：

    
    
    elif [ -f /rw/RESET ]; then
        /bin/bash /rw/RESET
        rm -rf /rw/RESET

这意味着如果/rw/RESET存在，则S08config将在启动时将其作为bash脚本执行。这是一种明显的持久性机制。很明显它实际上是在野观察到的：

![23.png](https://image.3001.net/images/20190830/1567140778_5d68abaa5ffdd.png!small)

这个论坛用户获得了MikroTik的调试包，并能够检查一些后利用的文件。在这里我们可以看到攻击者使用/rw/RESET来执行他们的/rw/info二进制文件。也许这也是为什么MikroTik改变了S08config行为的原因。

## /rw/DEFCONF

与/rw/RESET类似，/rw/DEFCONF的内容可以通过S12defconf中的eval语句执行。

    
    
    defcf=$(cat /rw/DEFCONF)
    echo > /ram/defconf-params
    if [ -f /nova/bin/flash ]; then
        /nova/bin/flash --fetch-defconf-params /ram/defconf-params
    fi
    (eval $(cat /ram/defconf-params) action=apply /bin/gosh "$defcf";
     cp "$defcf" $confirm; rm /rw/DEFCONF /ram/defconf-params) &

这是在6.40.1中首次引入的，但与/rw/RESET不同，这在6.45.3中尚未被修复。实际上，这是[Cleaner
Wrasse](https://github.com/tenable/routeros/tree/master/cleaner_wrasse)用于在路由器上建立重启持久性的方法。我使用CVE-2019-3943编写了一个[PoC](https://github.com/tenable/routeros/tree/master/poc/cve_2019_3943_defconf)，以证明远程认证的攻击者是如何滥用/rw/DEFCONF来实现后门并建立持久性的。

![24.png](https://image.3001.net/images/20190830/1567140804_5d68abc4249bb.png!small)

## /pckg/

正如我们在本文的签名验证部分所看到的那样，/pckg/的每个包都可以有一个包含rc脚本的/etc/rc.d/run.d/目录。/pckg/是tmpfs的一部分，因此攻击者在/pckg/中创建的任何内容，都不会在重启后持续存在，但新的rc脚本将在关闭时执行。

这有用吗？有一个关于/rw/DEFCONF的点之前我一直没向大家提及到，那就是它在系统上的存在会导致登录出现问题。Cleaner
Wrasse通过在/rw/.lol中暂存一个文件，然后在/pckg/中创建一个rc脚本来避免这个问题，该脚本会在关闭时创建/rw/DEFCONF文件。这样，Cleaner
Wrasse就可以避免登录时的问题了，但在系统再次启动时，一定要确保其存在。

![25.png](https://image.3001.net/images/20190830/1567140825_5d68abd98a60c.png!small)

## 符号链接

我在本文中提到的许多PoC都使用了CVE-2019-3943这个漏洞，但它已在2019年5月份被修补（6.43.15 Long-term）。除非使用Kirilis Solojov的[USB越狱](https://github.com/0ki/mikrotik-tools/blob/master/exploit-defconf/make_usb.sh)，否则没有更多的公开方法来启用后门文件以及root设备。那么我又该如何做到这一点呢？

![26.png](https://image.3001.net/images/20190830/1567140848_5d68abf0737c1.png!small)

答案很简单。当我仍能够使用CVE-2019-3943漏洞利用路由器时，我在root用户的/rw/disk目录中创建了一个隐藏的符号链接。

![27.png](https://image.3001.net/images/20190830/1567140868_5d68ac042e75d.png!small)

升级后，只需FTP到路由器中，然后将符号链接遍历到root。从那里你可以用你想要的许多方法中的一种来实现执行。在下图中，我将libz.so放到/rw/lib/中以启用后门。

![28.png](https://image.3001.net/images/20190830/1567140882_5d68ac125bee2.png!small)

RouterOS没有为普通用户提供创建符号链接的方法，因此你只能通过利用来实现。但RouterOS也不会尝试删除符号链接。只要是这样，我们就可以继续使用存活的符号链接在升级后重建root
shell。

Winbox或Webfig都不会显示隐藏文件。偶尔通过FTP检查用户目录，以确保其中没有隐藏的内容是必要的。

![29.png](https://image.3001.net/images/20190830/1567140917_5d68ac35ed556.png!small)

## 那么这里发生了什么？

我已经分享了很多实现执行的方法。所以当我偶然发现这个的时候，我有点困惑：

![30.png](https://image.3001.net/images/20190830/1567140932_5d68ac44651ad.png!small)

上图来自CVE-2018–14847的第一份公开报告。在它有CVE之前。在它被MikroTik发现之前。一位用户突然出现在MikroTik论坛上，并询问了有关潜在Winbox漏洞（在他们设备上发现了一个奇怪的登录和可疑文件）的问题。上面的图片来自于他们发现的一个叫做save.sh的bash脚本。

我在这篇文章中向大家展示了，攻击者不需要将任何东西存储在用户可以访问的唯一目录中。然而，这正是攻击者所做的。/flash/rw/pckg/是指向用户的/flash/rw/disk/目录的符号链接。由此产生的后果也迫使MikroTik做了一些强化

## 修复

当然！本文中提及的所有问题目前都已被修复。只需通过一些微小的修改，或是避免以root身份执行所有内容都可以达到修复的目的。纵深防御很重要，但有时它并不是一个高优先级。我预计未来也不会发生任何重大的变化，但希望MikroTik可以对其发展计划进行一些小的防御深度改进。

...或者我们只是静静等待RouterOS 7的发布；）

 ***参考来源：[medium](https://medium.com/tenable-techblog/routeros-post-exploitation-784c08044790)，FB小编secist编译，转载请注明来自FreeBuf.COM**  

