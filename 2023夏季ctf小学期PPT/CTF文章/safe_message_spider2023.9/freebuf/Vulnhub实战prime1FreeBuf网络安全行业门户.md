## 前言

VulnHub
是一个面向信息安全爱好者和专业人士的虚拟机（VM）漏洞测试平台。它提供了一系列特制的漏洞测试虚拟机镜像，供用户通过攻击和漏洞利用的练习来提升自己的安全技能。本次，我们本次测试的是prime1。

## 一、主机发现和端口扫描

  1. 查看Vmware中靶机的MAC地址，方便与之后nmap扫描出来的主机的MAC地址进行对比，选择nmap与靶机MAC地址相符的主机，其IP地址即为靶机的IP地址。

![1692975164_64e8c03c4842949ad21ef.png!small](https://image.3001.net/images/20230825/1692975164_64e8c03c4842949ad21ef.png!small)

> 这里我已知目标使用了NAT模式。

  2. 使用nmap进行网络扫描
    
        nmap -sP 192.168.1.0/24

![1692974915_64e8bf43423bd394fcfa4.png!small?1692974914458](https://image.3001.net/images/20230825/1692974915_64e8bf43423bd394fcfa4.png!small?1692974914458)

> -p(ping)
>
> -O(operation)
>
>  
>
>
> 除了使用Nmap的命令之外，还可以使用命令对目标的IP地址进行扫描。
>
> `arp-scan -l `//IP地址和MAC地址的映射
>
> `netdiscover -i eth0 -r 192.168.1.0/24 `//扫描这个网段下当前还存在的网络

  3. 使用nmap进行端口扫描
    
        nmap -p 1-65535 -A 192.168.1.129

![1692975228_64e8c07cd6c306e8349c7.png!small?1692975228075](https://image.3001.net/images/20230825/1692975228_64e8c07cd6c306e8349c7.png!small?1692975228075)

由上图可知，nmap扫描出来22和80两个端口，并且把其他的一些指纹信息例如操作系统类型、Apache版本等都扫描出来了。

  4. 访问目标

![1692975330_64e8c0e2957b917ae57ad.png!small?1692975329983](https://image.3001.net/images/20230825/1692975330_64e8c0e2957b917ae57ad.png!small?1692975329983)

## 二、目录扫描

  5. 进行网页目录扫描
    
        dirb http://192.168.1.129

![1692975427_64e8c143924f7456b31f4.png!small?1692975426783](https://image.3001.net/images/20230825/1692975427_64e8c143924f7456b31f4.png!small?1692975426783)

也可以使用参数-X指定扫描的文件

![1692975469_64e8c16dde7ec4cd29517.png!small?1692975469101](https://image.3001.net/images/20230825/1692975469_64e8c16dde7ec4cd29517.png!small?1692975469101)

  6. 然后访问一下目标目录下的secret.txt文件，结果如下图

  7. ![1692975509_64e8c1952090d19c6e102.png!small?1692975508286](https://image.3001.net/images/20230825/1692975509_64e8c1952090d19c6e102.png!small?1692975508286)有提示，看来location.txt是一个特殊文件，但直接访问之后没有什么特殊的，这个文件可能是某个参数的值

## 三、FUZZ和LFI

  8. 使用wfuzz工具测试一下，找url中可能存在的参数
    
        wfuzz -w /usr/share/wfuzz/wordlist/general/common.txt http://192.168.1.129/index.php?FUZZ

![1692975676_64e8c23c12d8dc380a99a.png!small](https://image.3001.net/images/20230825/1692975676_64e8c23c12d8dc380a99a.png!small)

> FUZZ模糊测试，功能：
>
>     * 找参数
>
>     * 目录扫描
>
>     * 密码暴力破解
>
>     * 找出被过滤的关键字
>
>     * 压力测试

  

  9. 大多数都一样，使用hw命令过滤一下不一样的条目

![1692975752_64e8c288d31a42a2faa6d.png!small](https://image.3001.net/images/20230825/1692975752_64e8c288d31a42a2faa6d.png!small)

  10. 可以看出这一条和其他的不一样，可以试着加上payload去访问一下，结果如下图所示

![1692975818_64e8c2ca4f3b216e72949.png!small?1692975817680](https://image.3001.net/images/20230825/1692975818_64e8c2ca4f3b216e72949.png!small?1692975817680)

给出了错误提示，但却也告诉了我们一些信息，那就是file是网页中中存在的一个文件参数，接下来我们就可以利用这一点了。

  11. 结合之前我们看到的提示，将location.txt作为file的参数值，然后再访问

![1692975859_64e8c2f394b787397295f.png!small?1692975859960](https://image.3001.net/images/20230825/1692975859_64e8c2f394b787397295f.png!small?1692975859960)

  12. 有效果了，让我们试一下secrettier360参数，我试了一下没什么反应，后来我是把index.php改为image.php才有反应，image.php之前有扫描出来，但是没留意，不知道有什么用处，因为它和index.php的界面没什么区别

![1692976394_64e8c50a48880e33cf381.png!small?1692976394756](https://image.3001.net/images/20230825/1692976394_64e8c50a48880e33cf381.png!small?1692976394756)

  13. 因为这是一个Linux操作系统，其中的敏感文件有/etc/passwd，我们可以试着将其作为参数参给secrettier360，结果如下图

![1692976419_64e8c52359505f4b370d0.png!small?1692976419271](https://image.3001.net/images/20230825/1692976419_64e8c52359505f4b370d0.png!small?1692976419271)

找到要登录Linux的提示了。

> 在Linux中，/etc/passwd中的密码使用x代替，不显示出来，而在/etc/shadow中则是通过MD5加salt加密，是显示出来的。

  14. 按照提示在url中输入相关参数

![1692976443_64e8c53b9e55d19c2cf5b.png!small?1692976442770](https://image.3001.net/images/20230825/1692976443_64e8c53b9e55d19c2cf5b.png!small?1692976442770)

  15. 得到一个密码follow_the_ippsec，不知道是不是登录Linux操作系统的密码，我尝试了一下，结果不是，看来还得从其他方面入手，我之前对目标目录进行了扫描，扫到了一个wordpress的目录

## 四、WordPress漏洞扫描

  16. 目标网站使用wordpress搭建的，这是一个CMS，曾经存在 _ **文件上传漏洞**_ ，我访问了它的wordpress目录，其中有一个用户名和一个登录链接。

![1693225723_64ec92fb01aea16e93ad2.png!small?1693225722693](https://image.3001.net/images/20230828/1693225723_64ec92fb01aea16e93ad2.png!small?1693225722693)

  17. 已知一个用户名，尝试使用之前从password.txt中获得的密码follow_the_ippsec尝试一下是否能够进行登录。

![1693225766_64ec93261f5c57d138269.png!small?1693225765860](https://image.3001.net/images/20230828/1693225766_64ec93261f5c57d138269.png!small?1693225765860)

  18. 结果成功进入后台界面，如下图所示。

![1693225795_64ec93432139eb65a797f.png!small?1693225794935](https://image.3001.net/images/20230828/1693225795_64ec93432139eb65a797f.png!small?1693225794935)

  19. 现在可以尝试上传webshell了，先寻找上传点，我在Appearance的Theme Editor选项里面的secret.php中找到了上传点。

![1693225834_64ec936ac8dfb2c2c63b6.png!small?1693225834750](https://image.3001.net/images/20230828/1693225834_64ec936ac8dfb2c2c63b6.png!small?1693225834750)

  20. 使用MSF来反弹shell，方便快捷，在MSF生成一个shell.php，建立监听。

![1693226011_64ec941baa1008856ebc6.png!small?1693226011483](https://image.3001.net/images/20230828/1693226011_64ec941baa1008856ebc6.png!small?1693226011483)

  21. 将最前面的注释去掉，复制到secret.php中，然后上传。

![1693226062_64ec944ea0c283c5d82a8.png!small?1693226062658](https://image.3001.net/images/20230828/1693226062_64ec944ea0c283c5d82a8.png!small?1693226062658)

  22. 使用MSF建立监听，然后访问secret.php。

![1693226088_64ec94685dca9539c51aa.png!small](https://image.3001.net/images/20230828/1693226088_64ec94685dca9539c51aa.png!small)

> 在wordpress中，secret.php其实是位于wordpress/wp-> content/themes/twentynineteen目录下的，因此我们通过访问该目录下的secret.php即可反弹shell，即访问<http://192.168.1.129/wordpress/wp-> content/themes/twentynineteen/secret.php>。

  23. 成功拿到shell，此时我们可以尝试一些命令获取目标更多的信息。  
![1693226153_64ec94a949b6f2d9f405f.png!small?1693226152977](https://image.3001.net/images/20230828/1693226153_64ec94a949b6f2d9f405f.png!small?1693226152977)

## 五、Linux内核漏洞提权

  24. 我们已经拿到目标的shell了，但我们还没达到root权限，要拿到root权限就得在目标的操作系统上提权。我在meterpreter中使用了sysinfo命令查看了目标的相关信息。

![1693226184_64ec94c8da112dd5cd1d4.png!small?1693226184449](https://image.3001.net/images/20230828/1693226184_64ec94c8da112dd5cd1d4.png!small?1693226184449)

  25. 接下来搜索该Linux系统或系统内核是否存在过漏洞。

![1693226211_64ec94e34b8c0b8aed9e6.png!small?1693226211097](https://image.3001.net/images/20230828/1693226211_64ec94e34b8c0b8aed9e6.png!small?1693226211097)

看来存在，Linux内核在4.13.9之前的版本存在漏洞，我们找到45010.c的路径并将其编译为可执行程序。

![1693226264_64ec9518de6ea0a03508a.png!small?1693226264490](https://image.3001.net/images/20230828/1693226264_64ec9518de6ea0a03508a.png!small?1693226264490)

> 如果在目标系统中编译的话可能出问题，因为目标操作系统可能没有gcc编译器，不具备C语言程序的编译环境。

  26. 将编译好的45010.exe上传至目标的/tmp/目录下。

![1693226288_64ec9530f39ba6747568a.png!small?1693226288568](https://image.3001.net/images/20230828/1693226288_64ec9530f39ba6747568a.png!small?1693226288568)

> 上传到其他文件中可能没有权限，可以上传到目标的/tmp目录。

  27. 上传成功之后，我查看了一下，/tmp/目录下存在45010的程序，但是没有可执行权限。

![1693226341_64ec956553ad357a50846.png!small?1693226341082](https://image.3001.net/images/20230828/1693226341_64ec956553ad357a50846.png!small?1693226341082)

  28. 执行一个shell脚本使其获得可执行权限。
    
        shell  
    cd /tmp  
    ls  
    chmod +x 45010  
    ./45010  
    whoami

![1693226391_64ec95970c6d1d36d7d22.png!small?1693226390683](https://image.3001.net/images/20230828/1693226391_64ec95970c6d1d36d7d22.png!small?1693226390683)

在shell中执行./45010时出现了一个错误：

./45010: /lib/x86_64-linux-gnu/libc.so.6: version `GLIBC_2.34' not found
(required by ./45010)

换一个旧版本的Kali，例如Kali2021.4也行，安装好之后在重复上述一些列不走之后再执行whoami命令，结果显示root，说明提权成功。

