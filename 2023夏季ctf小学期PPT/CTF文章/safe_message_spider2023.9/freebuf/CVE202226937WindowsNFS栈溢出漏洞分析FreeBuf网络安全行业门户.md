## **简介**

NFS全称Network File System，即网络文件系统，用于服务器和客户机之间文件访问和共享的通信，从而使客户机远程访问保存在存储设备上的数据。

CVE-2022-26937是微软5月份修复的Windows
NFS中一个对NLM响应处理不当的栈溢出漏洞，攻击者可通过精心构造RPC数据包来利用此漏洞，从而劫持程序流程令服务器失陷。本文将从介绍NFS通信流程开始，对CVE-2022-26937漏洞进行分析，希望能够帮助读者了解NFS协议以及其通信流程中可能存在的不安全问题。

##  **01** NFS通信流程

NFS是基于RPC远程过程调用协议来实现通信，RPC工作机制如下:

![1661851977_630dd949c2b3d3e59d739.jpg!small?1661851978606](https://image.3001.net/images/20220830/1661851977_630dd949c2b3d3e59d739.jpg!small?1661851978606)

1\. 客户端程序通过执行RPC系统调用的方式发送调用号与参数到服务端。

2\. 服务端在收到客户端的系统调用请求后，本地执行对应系统调用，然后将结果返回给服务进程。

3\. 服务进程将收到的结果封装后发送给客户端。

4\. 客户端接受执行结果，继续执行。

这其中PRC结构如下表所示

    
    
    Offset      Size(bytes) Description  
    0x00        4           XID  
    0x04        4           Message Type (Call: 0)  
    0x08        4           RPC Version  
    0x0C        4           Program (e.g., 100000: portmap)  
    0x10        4           Program Version  
    0x14        4           Procedure  
    0x18        4           Credentials Flavour (e.g., AUTH_UNIX: 1)  
    0x1c        4           Credentials Length (q)  
    0x20        q           Credentials  
    0x20+q      4           Verifier Flavour (e.g., AUTH_NULL: 0)  
    0x24+q      4           Verifier Length: w  
    0x28+q      w           Verifier  
    0x28+q+w    N           Program-specific data

有了如上结构，我们就可以伪造客户端跟服务器进行通信，比如构造如下请求。

![1661851990_630dd956a958e9a5dbd20.jpg!small?1661851991644](https://image.3001.net/images/20220830/1661851990_630dd956a958e9a5dbd20.jpg!small?1661851991644)

由上，我们伪造客户端发送GETPORT CALL NLM的系统调用，来获取服务器NLM运行端口，服务器执行对应系统调用后将端口号发送给客户端。

NLM结构如下表

    
    
    Offset           Size(bytes) Description  
    0x00             4           cookie length : w  
    0x04             w           cookie contents  
    0x04+w           4           exclusive  
    0x08+w           4           lock caller_name length : q  
    0x0c+w           q           lock caller_name contents  
    0x0c+w+q         4           fh length : e  
    0x10+w+q         e           fh Filehandle  
    0x10+w+q+e       4           owner length : r  
    0x14+w+q+e       r           owner contents  
    0x14+w+q+e+r     4           svid  
    0x18+w+q+e+r     4           l_offset  
    0x1c+w+q+e+r     4           l_len  
    0x20+w+q+e+r     244         data

有了如上结构，我们就可以伪造NLM协议向服务器发送请求。

![1661852007_630dd96713f9662cc0cc1.jpg!small?1661852008305](https://image.3001.net/images/20220830/1661852007_630dd96713f9662cc0cc1.jpg!small?1661852008305)

如上图，我们伪造NLM协议包向服务器发送TEST_MSG请求，服务器会发送一个GETADDR来检索客户端ip地址等信息。

##  **02** 漏洞分析

当Windows NFS服务响应NLM调用时，会根据客户端发送系统调用程序号判断是否为异步过程，这其中NLM支持的过程列表如下[1]:

    
    
    /*  
    * NLM procedures  
    */  
      
    program NLM_PROG {  
    version NLM_VERSX {  
    /*  
    *  synchronous procedures  
    */  
    void         NLM_NULL(void) = 0;  
    nlm_testres  NLM_TEST(struct nlm_testargs) = 1;  
    nlm_res      NLM_LOCK(struct nlm_lockargs) = 2;  
    nlm_res      NLM_CANCEL(struct nlm_cancargs) = 3;  
    nlm_res      NLM_UNLOCK(struct nlm_unlockargs) = 4;  
      
    /*  
    *  server   NLM call-back procedure to grant lock  
    */  
    nlm_res      NLM_GRANTED(struct nlm_testargs) = 5;  
      
    /*  
    *  asynchronous requests and responses  
    */  
    void         NLM_TEST_MSG(struct nlm_testargs) = 6;  
    void         NLM_LOCK_MSG(struct nlm_lockargs) = 7;  
    void         NLM_CANCEL_MSG(struct nlm_cancargs) =8;  
    void         NLM_UNLOCK_MSG(struct nlm_unlockargs) = 9;  
    void         NLM_GRANTED_MSG(struct nlm_testargs) = 10;  
    void         NLM_TEST_RES(nlm_testres) = 11;  
    void         NLM_LOCK_RES(nlm_res) = 12;  
    void         NLM_CANCEL_RES(nlm_res) = 13;  
    void         NLM_UNLOCK_RES(nlm_res) = 14;  
    void         NLM_GRANTED_RES(nlm_res) = 15;  
      
    /*  
    *  synchronous non-monitored lock and DOS file-sharing  
    *  procedures (not defined for version 1 and 2)  
    */  
    nlm_shareres NLM_SHARE(nlm_shareargs) = 20;  
    nlm_shareres NLM_UNSHARE(nlm_shareargs) = 21;  
    nlm_res      NLM_NM_LOCK(nlm_lockargs) = 22;  
    void         NLM_FREE_ALL(nlm_notify) = 23;  
    } = 3;  
    } = 100021;

  

以对NLM_TEST_MSG调用的处理为例，在NlmDispatch函数中可以看出不论是同步的NLM_TEST还是异步处理的NLM_TEST_MSG最终都将走向NlmTestLock()函数处理。

    
    
    v10 = *v27;  
    v13 = (*v27 + 0xD8i64);  
    v6 = *v13;  
    if ( v6 == 1 )  
    {  
    LABEL_54:  
    v19 = NlmTestLock(v10);  
    LABEL_85:  
    v5 = v19;  
    if ( v19 >= 0 )  
    goto LABEL_90;  
    v9 = NfsDeviceExtension;  
    goto LABEL_87;  
    }  
    if ( v6 != 2 )  
    {  
    if ( v6 != 3 )  
    {  
    if ( v6 != 4 )  
    {  
    if ( v6 != 5 )  
    {  
    if ( v6 == 6 )  
    goto LABEL_54;  
    ...  
    }

而在NlmTestLock()函数中则判断系统调用为NLM_TEST_MSG后调用NlmGetClientAddressAndConnection()函数。

    
    
    __int64  NlmTestLock(__int64 a1){  
    ...  
    if ( *(_DWORD *)(a1 + 0xD8) == 6 )  
    {  
    v5 = NlmGetClientAddressAndConnection(  
    *(_QWORD *)(a1 + 48),  
    (__int64)(v7 + 0x30),  
    (unsigned __int16 *)v7 + 38,  
    *((_DWORD *)v7 + 27),  
    *((_DWORD *)v7 + 28),  
    *((_DWORD *)v7 + 26),  
    &v28,  
    &v33,  
    &v30,  
    &v29);  
    ...  
    }  
    }

该函数实现接受客户端响应包以获得客户端ip地址等信息，而该函数在处理ipv6响应包时，由于没有对返回的地址字符串进行长度验证，从而导致栈溢出。

调用OncRpcSendCallWaitReply函数接受客户端响应包。

    
    
    if ( v40 >= 0 )  
    {  
    v40 = OncRpcSendCallWaitReply(v65, v105, v63, 0x7530i64, &v106);  
    if ( v40 >= 0 )  
    v40 = NlmSendWait(&v106);  
    if ( v105 )  
    {  
    OncRpcConnectionClose(v105);  
    v105 = 0i64;  
    }  
    }

重点在于对响应包v106的处理，首先判断此次调用ip类型，v103在函数开始进行了赋值，如果a2指针的值为2，对应ipv4的响应包，反之对应ipv6。

    
    
    _int64 __fastcall NlmGetClientAddressAndConnection(__int64 a1, __int64 a2, unsigned __int16 *a3,.,.,., _LIST_ENTRY **a10)  
    v27 = *(_WORD *)a2 == 2;  
    ...  
    v103 = v27;

如果v103=true，进入ipv4处理,将客户端端口赋值给v104,反之进入ipv6响应，将客户端返回包字符串长度赋值给v78后将返回包字符串赋值给v83，然后调用memmove()函数将包含有客户端地址信息的返回包复制到v118上，v118为栈上固定长度的数组。但是，这里没有对地址长度进行大小验证，导致如果响应的地址字符串大于一定长度，就会导致栈溢出。

    
    
    if ( v103 )   // ipv4  
    {  
    if (   
    ...  
    }  
    v104 = v71;  
    }  
    else       // ipv6  
    {  
    v115[1] = 96;  
    v116 = v118;  
    if ( *(int *)(v106 + 0x108) >= 0  
    && (v72 = *(_QWORD *)(v106 + 0x48)) != 0  
    && ((v73 = *(_DWORD *)(v72 + 64) - *(_DWORD *)(v72 + 56), v74 = *(_DWORD *)(v72 + 76), v74 < v73) ? (v75 = 0) : (v75 = v74 - v73),  
    v75 >= 4) )  
    {  
    v76 = _byteswap_ulong(**(_DWORD **)(v72 + 64)); //将ip size 更改端后赋值  
    *(_QWORD *)(*(_QWORD *)(v106 + 72) + 64i64) += 4i64; //此时指向ip。  
    }  
    else  
    {  
    v76 = XdrDecodeIntSlow(v106);  
    }  
    v77 = v106;  
    v115[0] = v76;  
    v78 = v76; // 这里将返回包长度赋值后并没有对其长度进行判断  
    if ( *(int *)(v106 + 0x108) < 0  
    || ((v79 = *(_QWORD *)(v106 + 0x48)) == 0  
    || (v80 = *(_DWORD *)(v79 + 0x40) - *(_DWORD *)(v79 + 56), v81 = *(_DWORD *)(v79 + 76), v81 < v80) ? (v82 = 0) : (v82 = v81 - v80),  
    v82 < (unsigned int)v78) )  
    {  
    XdrDecodeOpaqueSlow(v106, (unsigned int)v78, v118);  
    }  
    else  
    {  
    v83 = 0i64;  
    if ( v79 )  
    v83 = *(const void **)(v79 + 0x40);  // v83 = 指向data的指针  
    memmove(v118, v83, v78); //overflow  
    ...  
    v66 = 0;  
    v118[v78] = 0;  
    }

我们这里构造0x800大小的响应字符串，可以看到rcx此时距离rbp只有0x30，但是r8长度却有0x800大小，最终导致栈溢出。

    
    
    1: kd> r  
    rax=00000000000008d4 rbx=01d8afece5a0aac9 rcx=ffffc401bcf1f400  
    rdx=ffff8809f3ded01c rsi=0000000000000000 rdi=ffff8809f2648070  
    rip=fffff809b007620f rsp=ffffc401bcf1f330 rbp=ffffc401bcf1f430  
    r8=0000000000000800  r9=fffff809aff77140 r10=ffffc401baa9f780  
    r11=ffffc401bcf1f300 r12=0000000000000000 r13=00000000b‘5860100  
    r14=ffff8809f375a400 r15=0000000000000800  
    iopl=0         nv up ei ng nz na po nc  
    cs=0010  ss=0018  ds=002b  es=002b  fs=0053  gs=002b             efl=00000286  
    nfssvr!NlmGetClientAddressAndConnection+0x88b:  
    fffff809`b007620f e82c690200      call    nfssvr!memcpy (fffff809`b009cb40)  
    1: kd> p  
    nfssvr!NlmGetClientAddressAndConnection+0x890:  
    fffff809`b0076214 488b4748        mov     rax,qword ptr [rdi+48h]  
    1: kd> dd ffffc401bcf1f400  
    ffffc401`bcf1f400  41414141 41414141 41414141 41414141  
    ffffc401`bcf1f410  41414141 41414141 41414141 41414141  
    ffffc401`bcf1f420  41414141 41414141 41414141 41414141  
    ffffc401`bcf1f430  41414141 41414141 41414141 41414141  
    ffffc401`bcf1f440  41414141 41414141 41414141 41414141  
    ffffc401`bcf1f450  41414141 41414141 41414141 41414141  
    ffffc401`bcf1f460  41414141 41414141 41414141 41414141  
    ffffc401`bcf1f470  41414141 41414141 41414141 41414141  
    1: kd> k  
    # Child-SP          RetAddr               Call Site  
    00 ffffc401`bcf1f330 41414141`41414141     nfssvr!NlmGetClientAddressAndConnection+0x890  
    01 ffffc401`bcf1f4c0 41414141`41414141     0x41414141`41414141  
    02 ffffc401`bcf1f4c8 41414141`41414141     0x41414141`41414141

##  **03** 修复

在更新后，加入了对返回通用地址字符串长度的判断，从而杜绝了栈溢出的发生。

![1661852053_630dd995e0f85a97d4f3e.jpg!small?1661852054667](https://image.3001.net/images/20220830/1661852053_630dd995e0f85a97d4f3e.jpg!small?1661852054667)

 **参考**

> [1] https://pubs.opengroup.org/onlinepubs/9629799/chap10.htm
>
> [2]
> https://www.zerodayinitiative.com/blog/2022/6/7/cve-2022-26937-microsoft-> windows-network-file-system-nlm-portmap-stack-buffer-overflow
>
> [3] https://github.com/omair2084/CVE-2022-26937
>
> [4] https://msrc.microsoft.com/update-guide/vulnerability/CVE-2022-26937

