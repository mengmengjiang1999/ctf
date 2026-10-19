iOS逆向008- OC方法函数反汇编

[ lukyy](https://www.jianshu.com/u/437734a25841)关注赞赏支持

# iOS逆向008- OC方法函数反汇编

### 密码学简介

//------------------------------------ 源码 ------------------------------------

    
    
    int main(int argc, char * argv[]) {
    
        //p = nil
        Person * p = [[Person alloc] init];
        p.name = @"hank";
        p.age = 18;
            
        //[Person alloc]
        //objc_msgSend(Person.class,@selector(alloc));
    }
    
    
    
    /* 总结：上面👆
    
     所有OC中使用Strong 修饰的对象,实际上是调用了这个函数 objc_storeStrong（强引用）
     以下是objc_storeStrong的源码实现过程：
    
     void objc_storeStrong(id *location, id obj)
     {
        id perv = *lopcation;//本地对象 location，obj 是传进来的对象
        if(obj == prev){
            return;
        }
        objc_retain(obj);   // 保存对象不释放，为了后面的可能使用，如果穿进来的obj= nil, -->看下面👇
        *location = obj;        // --> 则：让指针指向nil，即 *location = nil (*p = nil, //释放p之前，先让 p = nil)
        objc_release(prev); // 释放 判断时使用的对象 prev = nil
     }
    
    p（对象）创建后，后面可能会使用，栈空间系统会自动回收，指针会立刻没有了，对象应该释放，malloc 创建的必须free，
    但是这里只有：retain、release
     
     */
    

  

  * ### 内存指令分析

##### Debug Workflow - Always Show Disassembly

Debug Workflow

Always Show Disassembly 内存指令分析

  
  

  * ### LLDB汇编调试

LLDB汇编调试

  
  

  * ### MachOView 汇编分析

MachOView 汇编分析-1

MachOView 汇编分析-2

MachOView 汇编分析-3

  
  

  * ### 最后附上分析的源码

  

#### **************** 内存指令分析****************

    
    
    002--OC方法`main:
        0x104cd6680 <+0>:   sub    sp, sp, #0x30             ; =0x30 // 0x104cd6000 --> 0x104cd6680 地址空间布局随机化 aslr 是偏移地址
        0x104cd6684 <+4>:   stp    x29, x30, [sp, #0x20]
        0x104cd6688 <+8>:   add    x29, sp, #0x20            ; =0x20 
        0x104cd668c <+12>:  adrp   x8, 2
        0x104cd6690 <+16>:  add    x8, x8, #0xe18            ; =0xe18 //0x104cd668c --> 0x104cd8e18
        0x104cd6694 <+20>:  adrp   x9, 2
        0x104cd6698 <+24>:  add    x9, x9, #0xe38            ; =0xe38   //0x104cd6694 --> 0x104cd8e38
        0x104cd669c <+28>:  stur   w0, [x29, #-0x4]
        0x104cd66a0 <+32>:  str    x1, [sp, #0x10]
    ->  0x104cd66a4 <+36>:  ldr    x9, [x9]     //x9是对象或类
        0x104cd66a8 <+40>:  ldr    x1, [x8]     //x8是指针， x1 是方法名称   
        0x104cd66ac <+44>:  mov    x0, x9       
        0x104cd66b0 <+48>:  bl     0x104cd6b20               ; symbol stub for: objc_msgSend
        0x104cd66b4 <+52>:  adrp   x8, 2
        0x104cd66b8 <+56>:  add    x8, x8, #0xe20            ; =0xe20 
        0x104cd66bc <+60>:  ldr    x1, [x8]
        0x104cd66c0 <+64>:  bl     0x104cd6b20               ; symbol stub for: objc_msgSend
        0x104cd66c4 <+68>:  adrp   x8, 2
        0x104cd66c8 <+72>:  add    x8, x8, #0x38             ; =0x38 
        0x104cd66cc <+76>:  adrp   x9, 2
        0x104cd66d0 <+80>:  add    x9, x9, #0xe28            ; =0xe28 
        0x104cd66d4 <+84>:  str    x0, [sp, #0x8]
        0x104cd66d8 <+88>:  ldr    x0, [sp, #0x8]
        0x104cd66dc <+92>:  ldr    x1, [x9]
        0x104cd66e0 <+96>:  mov    x2, x8
        0x104cd66e4 <+100>: bl     0x104cd6b20               ; symbol stub for: objc_msgSend
        0x104cd66e8 <+104>: mov    w2, #0x12
        0x104cd66ec <+108>: adrp   x8, 2
        0x104cd66f0 <+112>: add    x8, x8, #0xe30            ; =0xe30 
        0x104cd66f4 <+116>: ldr    x9, [sp, #0x8]
        0x104cd66f8 <+120>: ldr    x1, [x8]
        0x104cd66fc <+124>: mov    x0, x9
        0x104cd6700 <+128>: bl     0x104cd6b20               ; symbol stub for: objc_msgSend
        0x104cd6704 <+132>: mov    x8, #0x0
        0x104cd6708 <+136>: add    x9, sp, #0x8              ; =0x8 
        0x104cd670c <+140>: mov    x0, x9
        0x104cd6710 <+144>: mov    x1, x8
        0x104cd6714 <+148>: bl     0x104cd6b44 ;  symbol stub for: objc_storeStrong
        0x104cd6718 <+152>: mov    w2, #0x0
        0x104cd671c <+156>: mov    x0, x2
        0x104cd6720 <+160>: ldp    x29, x30, [sp, #0x20]
        0x104cd6724 <+164>: add    sp, sp, #0x30             ; =0x30  // 释放p
        0x104cd6728 <+168>: ret  
    
    
        注意：  adrp、add 取地址，要么是全局变量，要么是常量，要么是方法名，x8 保存8个字节的数据
        0x104cd668c <+12>:  adrp   x8, 2
        0x104cd6690 <+16>:  add    x8, x8, #0xe18            ; =0xe18 //0x104cd668c --> 0x104cd8e18
    

  

#### **************** LLDB 汇编调试 指令 ****************

    
    
    //------------------------------------ LLDB 汇编调试 ------------------------------------ 
    (lldb) x 0x104cd8e18
    0x104cd8e18: cc 72 fe 8c 01 00 00 00 30 72 fe 8c 01 00 00 00  .r......0r......
    0x104cd8e28: c8 c7 fe 8c 01 00 00 00 1f ea c0 88 01 00 00 00  ................
    (lldb) p (SEL) 0x104cd8e18  // 1
    (SEL) $0 = "alloc"
    (lldb) p (char *)0x018cfe72cc   // 2 （1同2）
    (char *) $1 = 0x000000018cfe72cc "alloc"
    (lldb) x 0x104cd8e38 
    0x104cd8e38: d0 8e cd 04 01 00 00 00 58 8e cd 04 01 00 00 00  ........X.......
    0x104cd8e48: 10 00 00 00 08 00 00 00 08 00 00 00 00 00 00 00  ................
    (lldb) po 0x0104cd8ed0
    Person
    
    (lldb)   register read x0
          x0 = 0x00000001c0033560
    (lldb) x 0x00000001c0033560
    0x1c0033560: d5 8e cd 04 a1 01 00 00 00 00 00 00 00 00 00 00  ................
    0x1c0033570: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
    (lldb) po 01a104cd8ed5
    error: invalid digit 'a' in octal constant
    (lldb) po 0x00000001c0033560      //对象
    <Person: 0x1c0033560> 
    
    (lldb) po p
     nil
    (lldb) register read x1
          x1 = 0x000000018cfe7230  "init"  // init 方法
    (lldb) n 
    (lldb) po p 
    <Person: 0x1c0033560>
    (lldb) 
    
    // 对此行断点
    ->  0x104cd6714 <+148>: bl     0x104cd6b44               ; symbol stub for: objc_storeStrong
    (lldb) register read x0
          x0 = 0x000000016b12f968
    (lldb) po 0x000000016b12f968
    6091372904
    
    (lldb) x 0x000000016b12f968  //二级指针，是p的指针
    0x16b12f968: 60 35 03 c0 01 00 00 00 c8 f9 12 6b 01 00 00 00  `5.........k....
    0x16b12f978: 00 00 00 00 01 00 00 00 a0 f9 12 6b 01 00 00 00  ...........k....
    (lldb) po 0x01c0033560      //一级级指针，是p的对象
    <Person: 0x1c0033560>
    
    (lldb) register read x1
          x1 = 0x0000000000000000   //释放p之前，先让 p = nil //
    (lldb) 
    
    

  

#### **************** MachOView 汇编分析源码 ****************

    
    
    *Mach64 Header：头
    Load Commands：加载的指令集，库、数据表，描述了下面的数据
    Section64：全是数据
    Section64（__TEXT__）：代码段
    Section64（__DATA__）：数据段
    
    *************************************************
    __text:0000000100006680 _main
    __text:0000000100006680
    __text:0000000100006680 var_18          = -0x18
    __text:0000000100006680 var_10          = -0x10
    __text:0000000100006680 var_4           = -4
    __text:0000000100006680 var_s0          =  0
    __text:0000000100006680
    __text:0000000100006680                 SUB             SP, SP, #0x30
    __text:0000000100006684                 STP             X29, X30, [SP,#0x20+var_s0]
    __text:0000000100006688                 ADD             X29, SP, #0x20
    __text:000000010000668C                 ADRP            X8, #selRef_alloc@PAGE            // x8的地址是 sel 指针
    __text:0000000100006690                 ADD             X8, X8, #selRef_alloc@PAGEOFF
    __text:0000000100006694                 ADRP            X9, #classRef_Person@PAGE      // x9的地址 calss 类指针
    __text:0000000100006698                 ADD             X9, X9, #classRef_Person@PAGEOFF
    __text:000000010000669C                 STUR            W0, [X29,#var_4]
    __text:00000001000066A0                 STR             X1, [SP,#0x20+var_10]
    __text:00000001000066A4                 LDR             X9, [X9] ; _OBJC_CLASS_$_Person   // objc_class 对象 Person
    __text:00000001000066A8                 LDR             X1, [X8] ; "alloc"                              // alloc
    __text:00000001000066AC                 MOV             X0, X9  ; void *
    __text:00000001000066B0                 BL              _objc_msgSend                                // init
    __text:00000001000066B4                 ADRP            X8, #selRef_init@PAGE
    __text:00000001000066B8                 ADD             X8, X8, #selRef_init@PAGEOFF
    __text:00000001000066BC                 LDR             X1, [X8] ; "init"
    __text:00000001000066C0                 BL              _objc_msgSend                                // setName
    __text:00000001000066C4                 ADRP            X8, #cfstr_Hank@PAGE ; "hank"
    __text:00000001000066C8                 ADD             X8, X8, #cfstr_Hank@PAGEOFF ; "hank"
    __text:00000001000066CC                 ADRP            X9, #selRef_setName_@PAGE
    __text:00000001000066D0                 ADD             X9, X9, #selRef_setName_@PAGEOFF
    __text:00000001000066D4                 STR             X0, [SP,#0x20+var_18]
    __text:00000001000066D8                 LDR             X0, [SP,#0x20+var_18] ; void *
    __text:00000001000066DC                 LDR             X1, [X9] ; "setName:"
    __text:00000001000066E0                 MOV             X2, X8
    __text:00000001000066E4                 BL              _objc_msgSend                                 // setAge
    __text:00000001000066E8                 MOV             W2, #0x12
    __text:00000001000066EC                 ADRP            X8, #selRef_setAge_@PAGE
    __text:00000001000066F0                 ADD             X8, X8, #selRef_setAge_@PAGEOFF
    __text:00000001000066F4                 LDR             X9, [SP,#0x20+var_18]
    __text:00000001000066F8                 LDR             X1, [X8] ; "setAge:"
    __text:00000001000066FC                 MOV             X0, X9  ; void *
    __text:0000000100006700                 BL              _objc_msgSend                                     //
    __text:0000000100006704                 MOV             X8, #0
    __text:0000000100006708                 ADD             X9, SP, #0x20+var_18
    __text:000000010000670C                 MOV             X0, X9
    __text:0000000100006710                 MOV             X1, X8
    __text:0000000100006714                 BL              _objc_storeStrong                                   //
    __text:0000000100006718                 MOV             W2, #0
    __text:000000010000671C                 MOV             X0, X2
    __text:0000000100006720                 LDP             X29, X30, [SP,#0x20+var_s0]
    __text:0000000100006724                 ADD             SP, SP, #0x30
    __text:0000000100006728                 RET
    __text:0000000100006728 ; End of function _main
    __text:0000000100006728
    
    
    

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [加密进阶（佩服写这篇文章的人）](https://www.jianshu.com/p/006a8e6e25e7)

CTF中那些脑洞大开的编码和加密 0x00 前言 正文开始之前先闲扯几句吧，玩CTF的小伙伴也许会遇到类似这样的问...

[查无此人asdasd](https://www.jianshu.com/u/6345e3b05eca)阅读 5,408评论 0赞 19

  * [脑洞大开的编码和加密](https://www.jianshu.com/p/ac31dd0dacda)

0x01 目录 常见编码: ASCII编码 Base64/32/16编码 shellcode编码 Quoted-p...

[H0f_9](https://www.jianshu.com/u/411316d5369b)阅读 10,877评论 2赞 17

  * [我要再次坏坏的](https://www.jianshu.com/p/035494c499e2)

趁失眠回味了下童年。曾经我是多么坏的一个孩子呢。 小时候，有次叔家妹妹抢了我的布偶，我便回之以利牙抢来，是...

[漸爱](https://www.jianshu.com/u/99bed33d6d02)阅读 236评论 0赞 0

  * [2017-11-22](https://www.jianshu.com/p/24089aeb3da6)

白日入世，夜出尘

[5adc213b1d02](https://www.jianshu.com/u/5adc213b1d02)阅读 38评论 0赞 0

 