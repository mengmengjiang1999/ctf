# 利用Oracle VirtualBox实现虚拟机逃逸

阅读量 **207699**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-10-13 10:00:43

 **x**

##### 译文声明

本文是翻译文章，文章原作者 starlabs，文章来源：starlabs.sg

原文地址：<https://starlabs.sg/blog/2020/09/pwn2own-2020-oracle-virtualbox-escape/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01fe45549848edd4d8.jpg)

在这篇文章中，我们将讨论在Pwn2Own 2020中使用的`Oracle VirtualBox escape`漏洞。这两个漏洞影响Oracle
VirtualBox 6.1.4和更早的版本。

## 漏洞

我们利用了两个漏洞完成了这次逃逸：

[CVE-2020-2894](https://www.zerodayinitiative.com/advisories/ZDI-20-581/)  
[CVE-2020-2575](https://www.zerodayinitiative.com/advisories/ZDI-20-582/)

###  CVE-2020-2894 E1000 越界读取漏洞

有关E1000网络适配器内部工作原理的更多信息，可以在[这里](https://github.com/hongphipham95/Vulnerabilities/blob/master/VirtualBox/Oracle%20VirtualBox%20Intel%20PRO%201000%20MT%20Desktop%20-%20Integer%20Underflow%20Vulnerability/Oracle%20VirtualBox%20Intel%20PRO%201000%20MT%20Desktop%20-%20Integer%20Underflow%20Vulnerability.md)阅读。

当使E1000网络适配器发送一个以太网帧时，我们可以通过设置`IXSM`位控制插入的IP校验和：

    
    
    // VirtualBox-6.1.4\src\VBox\Devices\Network\DevE1000.cpp:5191
    static bool e1kLocateTxPacket(PE1KSTATE pThis)
    {
        ...    
        E1KTXDESC *pDesc = &pThis->aTxDescriptors[i];
        switch (e1kGetDescType(pDesc))
        {
        ...                
            case E1K_DTYP_DATA:
            ...                
                if (cbPacket == 0)
                {
                    /*
                     * The first fragment: save IXSM and TXSM options
                     * as these are only valid in the first fragment.
                     */
                    pThis->fIPcsum  = pDesc->data.dw3.fIXSM;
                    pThis->fTCPcsum = pDesc->data.dw3.fTXSM;
                            fTSE     = pDesc->data.cmd.fTSE;
            ...                    
    }
    

启用`pThis->fIPcsum`标志后，IP校验和插入到以太网帧中：

    
    
    // VirtualBox-6.1.4\src\VBox\Devices\Network\DevE1000.cpp:4997
    static int e1kXmitDesc(PPDMDEVINS pDevIns, PE1KSTATE pThis, PE1KSTATECC pThisCC, E1KTXDESC *pDesc,
                           RTGCPHYS addr, bool fOnWorkerThread)
    {
        ...
        switch (e1kGetDescType(pDesc))
        {
            ...            
            case E1K_DTYP_DATA:
            {
                STAM_COUNTER_INC(pDesc->data.cmd.fTSE?
                                 &pThis->StatTxDescTSEData:
                                 &pThis->StatTxDescData);
                E1K_INC_ISTAT_CNT(pThis->uStatDescDat);
                STAM_PROFILE_ADV_START(&pThis->CTX_SUFF_Z(StatTransmit), a);
                if (pDesc->data.cmd.u20DTALEN == 0 || pDesc->data.u64BufAddr == 0)
                {
                ...                
                }
                else
                {
                ...                
                    else if (!pDesc->data.cmd.fTSE)
                    {
                        ...
                        if (pThis->fIPcsum)
                            e1kInsertChecksum(pThis, (uint8_t *)pThisCC->CTX_SUFF(pTxSg)->aSegs[0].pvSeg, pThis->u16TxPktLen,
                                              pThis->contextNormal.ip.u8CSO,
                                              pThis->contextNormal.ip.u8CSS,
                                              pThis->contextNormal.ip.u16CSE);
    

函数`e1kInsertChecksum()`将计算校验和并将其放入框架主体中。`pThis->contextNormal`的三个字段`u8CSO`、`u8CSS`和`u16CSE`可以通过上下文描述符（Context
Descriptor）指定：

    
    
    // VirtualBox-6.1.4\src\VBox\Devices\Network\DevE1000.cpp:5158
    DECLINLINE(void) e1kUpdateTxContext(PE1KSTATE pThis, E1KTXDESC *pDesc)
    {
        if (pDesc->context.dw2.fTSE)
        {
            ...        
        }
        else
        {
            pThis->contextNormal = pDesc->context;
            STAM_COUNTER_INC(&pThis->StatTxDescCtxNormal);
        }
    ...    
    }
    

`e1kInsertChecksum()`函数的实现：

    
    
    // VirtualBox-6.1.4\src\VBox\Devices\Network\DevE1000.cpp:4155
    static void e1kInsertChecksum(PE1KSTATE pThis, uint8_t *pPkt, uint16_t u16PktLen, uint8_t cso, uint8_t css, uint16_t cse)
    {
        RT_NOREF1(pThis);
    
        if (css >= u16PktLen)                            // [1]
        {
            E1kLog2(("%s css(%X) is greater than packet length-1(%X), checksum is not inserted\n",
                     pThis->szPrf, cso, u16PktLen));
            return;
        }
    
        if (cso >= u16PktLen - 1)                        // [2]
        {
            E1kLog2(("%s cso(%X) is greater than packet length-2(%X), checksum is not inserted\n",
                     pThis->szPrf, cso, u16PktLen));
            return;
        }
    
        if (cse == 0)                                    // [3]
            cse = u16PktLen - 1;
        else if (cse < css)                                // [4]
        {
            E1kLog2(("%s css(%X) is greater than cse(%X), checksum is not inserted\n",
                     pThis->szPrf, css, cse));
            return;
        }
    
        uint16_t u16ChkSum = e1kCSum16(pPkt + css, cse - css + 1);
        E1kLog2(("%s Inserting csum: %04X at %02X, old value: %04X\n", pThis->szPrf,
                 u16ChkSum, cso, *(uint16_t*)(pPkt + cso)));
        *(uint16_t*)(pPkt + cso) = u16ChkSum;
    }
    

`css`是数据包中开始计算校验和的偏移量，它需要小于`u16PktLen`，它是当前数据包的总大小（代码中[1]）。

`cse`是数据包中用来停止校验和计算的偏移量。

将`cse`字段设置为0表示校验和将覆盖从`css`到包的末尾（代码中[3]）。

`cse`需要比`css`大（代码中[4]）。

`cso`是数据包中写入校验和的偏移量，它需要小于`u16PktLen – 1`（代码中[2]）。

由于没有检查`cse`的最大值，我们可以将该字段设置为大于当前数据包的总大小，从而导致越界访问，并导致`e1kCSum16()`在`pPkt`之后计算数据的校验和。

“overread”校验和将被插入以太网帧中，稍后可以被接收器读取。

###  信息泄漏

因此，如果我们想从一个溢出校验和中泄漏一些信息，我们需要一种可靠的方法来知道哪些数据与溢出缓冲区相邻。在仿真的E1000设备中，传输缓冲区由`e1kXmitAllocBuf()`函数分配:

    
    
    // VirtualBox-6.1.4\src\VBox\Devices\Network\DevE1000.cpp:3833
    DECLINLINE(int) e1kXmitAllocBuf(PE1KSTATE pThis, PE1KSTATECC pThisCC, bool fGso)
    {
        ...    
        PPDMSCATTERGATHER pSg;
        if (RT_LIKELY(GET_BITS(RCTL, LBM) != RCTL_LBM_TCVR))            // [1]
        {
            ...        
            int rc = pDrv->pfnAllocBuf(pDrv, pThis->cbTxAlloc, fGso ? &pThis->GsoCtx : NULL, &pSg);
            ...        
        }
        else
        {
            /* Create a loopback using the fallback buffer and preallocated SG. */
            AssertCompileMemberSize(E1KSTATE, uTxFallback.Sg, 8 * sizeof(size_t));
            pSg = &pThis->uTxFallback.Sg;
            pSg->fFlags      = PDMSCATTERGATHER_FLAGS_MAGIC | PDMSCATTERGATHER_FLAGS_OWNER_3;
            pSg->cbUsed      = 0;
            pSg->cbAvailable = sizeof(pThis->aTxPacketFallback);
            pSg->pvAllocator = pThis;
            pSg->pvUser      = NULL; /* No GSO here. */
            pSg->cSegs       = 1;
            pSg->aSegs[0].pvSeg = pThis->aTxPacketFallback;                // [2]                
            pSg->aSegs[0].cbSeg = sizeof(pThis->aTxPacketFallback);
        }
        pThis->cbTxAlloc = 0;
    
        pThisCC->CTX_SUFF(pTxSg) = pSg;
        return VINF_SUCCESS;
    }
    

`RCTL`寄存器的`LBM`（环回模式）字段控制以太网控制器的环回模式，它影响包缓冲区（packet buffer）的分配（代码中[1]）：

没有环回模式：`e1kXmitAllocBuf()`使用`pDrv->pfnAllocBuf()`回调来分配数据包缓冲区，这个回调将使用OS分配器或VirtualBox的自定义分配器。  
环回模式：数据包缓冲区是`aTxPacketFallback`数组（代码中[2]）。

`aTxPacketFallback`数组是PE1KSTATE pThis对象的属性：

    
    
    // VirtualBox-6.1.4\src\VBox\Devices\Network\DevE1000.cpp:1024
    typedef struct E1KSTATE
    {
        ...
        /** TX: Transmit packet buffer use for TSE fallback and loopback. */
        uint8_t     aTxPacketFallback[E1K_MAX_TX_PKT_SIZE];
        /** TX: Number of bytes assembled in TX packet buffer. */
        uint16_t    u16TxPktLen;
        ...    
    } E1KSTATE;
    
    /* Pointer to the E1000 device state. */
    typedef E1KSTATE *PE1KSTATE;
    

因此，通过启用环回模式可以做到：

数据包接收方是我们，我们不需要另一个主机来读取`overread`校验和  
数据包缓冲区驻留在`pThis结构中，因此被覆盖的数据是`pThis`对象的其他字段

现在我们知道了哪些数据是与数据包缓冲区相邻的，我们可以通过以下步骤泄露信息：

发送包含`E1K_MAX_TX_PKT_SIZE`字节的`CRC-16`校验和的帧，称其为`crc0`。  
发送包含`E1K_MAX_TX_PKT_SIZE` \+ `2`字节校验和的第二帧，称为`crc1`。  
由于校验和算法是`CRC-16`，通过计算`crc`0和`crc1`之间的差异，我们可以知道紧跟在`aTxPacketFallback`数组之后的两个字节的值。

每次增加2字节的大小，直到我们得到一些有趣的数据。幸运的是，在`pThis`对象之后，我们可以在`VBoxDD.dll`模块的`E1K_MAX_TX_PKT_SIZE`\+
`0x1f7`处找到一个指向全局变量的指针。

一个小问题是,在`pThi`s对象中，`aTxPacketFallback`数组后，还有其他设备的计数器寄存器，每次发送帧都会增加。即使我们发送两个帧大小相同，它也导致了两种不同的校验和。但由于每次的增加是可以预测的，我们可以添加`0x5a`到第二个校验和中使得两个校验和一致。

###  OHCI控制器没有初始化变量

你可以在[这里](https://github.com/hongphipham95/Vulnerabilities/blob/master/VirtualBox/Oracle%20VirtualBox%20OHCI%20Use-After-Free%20Vulnerability/Oracle%20VirtualBox%20OHCI%20Use-After-Free.md)阅读更多关于VirtualBox OHCI设备的信息。

当发送一个控制消息URB到USB设备中时，我们可以在其中夹带一个设置包来更新消息URB：

    
    
    // VirtualBox-6.1.4\src\VBox\Devices\USB\VUSBUrb.cpp:834
    static int vusbUrbSubmitCtrl(PVUSBURB pUrb)
    {
        ...    
        if (pUrb->enmDir == VUSBDIRECTION_SETUP)
        {
            LogFlow(("%s: vusbUrbSubmitCtrl: pPipe=%p state %s->SETUP\n",
                     pUrb->pszDesc, pPipe, g_apszCtlStates[pExtra->enmStage]));
            pExtra->enmStage = CTLSTAGE_SETUP;
        }
    
        ...    
    
        switch (pExtra->enmStage)
        {
            case CTLSTAGE_SETUP:
                ...            
                if (!vusbMsgSetup(pPipe, pUrb->abData, pUrb->cbData))
                {
                    pUrb->enmState = VUSBURBSTATE_REAPED;
                    pUrb->enmStatus = VUSBSTATUS_DNR;
                    vusbUrbCompletionRh(pUrb);
                    break;
    
    
    
    // VirtualBox-6.1.4\src\VBox\Devices\USB\VUSBUrb.cpp:664
    static bool vusbMsgSetup(PVUSBPIPE pPipe, const void *pvBuf, uint32_t cbBuf)
    {
        PVUSBCTRLEXTRA  pExtra = pPipe->pCtrl;
        const VUSBSETUP *pSetupIn = (PVUSBSETUP)pvBuf;
    
            ...
    
        if (pExtra->cbMax < cbBuf + pSetupIn->wLength + sizeof(VUSBURBVUSBINT))        // [1]
        {
            uint32_t cbReq = RT_ALIGN_32(cbBuf + pSetupIn->wLength + sizeof(VUSBURBVUSBINT), 1024);
            PVUSBCTRLEXTRA pNew = (PVUSBCTRLEXTRA)RTMemRealloc(pExtra, RT_UOFFSETOF_DYN(VUSBCTRLEXTRA, Urb.abData[cbReq]));                            // [2]
            if (!pNew)
            {
                Log(("vusbMsgSetup: out of memory!!! cbReq=%u %zu\n",
                     cbReq, RT_UOFFSETOF_DYN(VUSBCTRLEXTRA, Urb.abData[cbReq])));
                return false;
            }
            if (pExtra != pNew)
            {
                pNew->pMsg = (PVUSBSETUP)pNew->Urb.abData;
                pExtra = pNew;
                pPipe->pCtrl = pExtra;
            }
            pExtra->Urb.pVUsb = (PVUSBURBVUSB)&pExtra->Urb.abData[cbBuf + pSetupIn->wLength]; // [3]
            pExtra->Urb.pVUsb->pUrb = &pExtra->Urb;                                          // [4]
            pExtra->cbMax = cbReq;
        }
        Assert(pExtra->Urb.enmState == VUSBURBSTATE_ALLOCATED);
    
        /*
         * Copy the setup data and prepare for data.
         */
        PVUSBSETUP pSetup = pExtra->pMsg;
        pExtra->fSubmitted      = false;
        pExtra->Urb.enmState    = VUSBURBSTATE_IN_FLIGHT;
        pExtra->pbCur           = (uint8_t *)(pSetup + 1);
        pSetup->bmRequestType   = pSetupIn->bmRequestType;
        pSetup->bRequest        = pSetupIn->bRequest;
        pSetup->wValue          = RT_LE2H_U16(pSetupIn->wValue);
        pSetup->wIndex          = RT_LE2H_U16(pSetupIn->wIndex);
        pSetup->wLength         = RT_LE2H_U16(pSetupIn->wLength);
    
          ...
    
        return true;
    }
    

`pSetupIn`是我们的URB数据包，`pExtra`是控制管道的当前额外数据，如果设置请求的大小大于当前控制管道额外数据的大小（代码中[1]处），`pExtra`将重新分配一个更大的大小（代码中[2]）。

下面的代码演示了在`vusbMsgAllocExtraData()`中分配初始化的`pExtra`：

    
    
    // VirtualBox-6.1.4\src\VBox\Devices\USB\VUSBUrb.cpp:609
    static PVUSBCTRLEXTRA vusbMsgAllocExtraData(PVUSBURB pUrb)
    {
    /** @todo reuse these? */
        PVUSBCTRLEXTRA pExtra;
        const size_t cbMax = sizeof(VUSBURBVUSBINT) + sizeof(pExtra->Urb.abData) + sizeof(VUSBSETUP);
        pExtra = (PVUSBCTRLEXTRA)RTMemAllocZ(RT_UOFFSETOF_DYN(VUSBCTRLEXTRA, Urb.abData[cbMax]));
        if (pExtra)
        {
            ...        
            pExtra->Urb.pVUsb = (PVUSBURBVUSB)&pExtra->Urb.abData[sizeof(pExtra->Urb.abData) + sizeof(VUSBSETUP)];
            //pExtra->Urb.pVUsb->pCtrlUrb = NULL;
            //pExtra->Urb.pVUsb->pNext = NULL;
            //pExtra->Urb.pVUsb->ppPrev = NULL;
            pExtra->Urb.pVUsb->pUrb = &pExtra->Urb;
            pExtra->Urb.pVUsb->pDev = pUrb->pVUsb->pDev;        // [5]
            pExtra->Urb.pVUsb->pfnFree = vusbMsgFreeUrb;
            pExtra->Urb.pVUsb->pvFreeCtx = &pExtra->Urb;
            ...        
        }
        return pExtra;
    }
    

函数`RTMemRealloc()`不执行任何初始化，因此产生的缓冲区将包含两部分：

A部分：旧的小的`pExtra`。  
B部分:新分配的`pExtra`。

在重新分配后：

`pExtra->Urb.pVUsb`对象将被更新为新的`pVUsb`，它驻留在B部分（代码中[3]）  
但是新的`pVUsb`驻留在未初始化的数据中，只有`pVUsb->pUrb`在代码中[4]的地方更新。

此时`pExtra->Urb.pVUsb`对象仍然未初始化，包括`pExtra->Urb.pVUsb->pDev`对象（代码中[5]）。

`pExtra->Urb`对象将在`vusbMsgDoTransfer()`函数中使用：

    
    
    // VirtualBox-6.1.4\src\VBox\Devices\USB\VUSBUrb.cpp:752
    static void vusbMsgDoTransfer(PVUSBURB pUrb, PVUSBSETUP pSetup, PVUSBCTRLEXTRA pExtra, PVUSBPIPE pPipe)
    {
        ...    
        int rc = vusbUrbQueueAsyncRh(&pExtra->Urb);
        ...    
    }
    
    
    
    // VirtualBox-6.1.4\src\VBox\Devices\USB\VUSBUrb.cpp:439
    int vusbUrbQueueAsyncRh(PVUSBURB pUrb)
    {
        ...    
        PVUSBDEV pDev = pUrb->pVUsb->pDev;
        ...    
        int rc = pDev->pUsbIns->pReg->pfnUrbQueue(pDev->pUsbIns, pUrb);
        ...    
    }
    

当VM主机进程间接引用未初始化的 `pDev`时，将发生访问冲突。

为了利用未初始化的对象，我们可以在重新分配之前执行堆喷射（heap spraying），然后希望`pDev`对象已经驻留在我们的数据中。

由于存在一个虚拟表调用，并且VirtualBox使用了CFG。我们可以结合漏洞、堆喷射和伪造的`pDev`对象来控制主机进程的指令指针（RIP）。

###  代码执行

我们之前的[文章](https://starlabs.sg/blog/2020/04/adventures-in-hypervisor-oracle-virtualbox-research/)描述了如何执行堆喷射来获得主机进程中的`VRAM`缓冲区的地址范围。我们将在这个范围内选择一个地址作为伪造的`pDEv`指针。

那么完整的利用过程将如下：

1.使用E1000漏洞获取`VBoxDD.dll`模块基地址，然后收集一些ROP gadgets  
2.我们伪造的`pDEv`指针指向`VRAM`中的某个地方，所以我们在`VRAM`中喷射`block`，每个`block`包含：  
1)用包含stack pivot的假的虚函数对齐`PVUSBDEV`对象，以指向堆栈指针主机的`VRAM`缓冲区  
2)包含`WinExec`ROP链的伪堆栈  
3.用我们选择的`VRAM`地址填充未初始化的内存完成堆喷射，这将使`pExtra->Urb.pVUsb->pDev`对象指向一个伪造的`PVUSBDEV`对象。  
4.触发`OHCI`漏洞，进而执行ROP

## 补丁

<https://www.virtualbox.org/changeset/83613/vbox/trunk/src/VBox/Devices/Network/DevE1000.cpp>  
<https://www.virtualbox.org/changeset/83617/vbox/trunk/src/VBox/Devices/USB/VUSBUrb.cpp>

本文翻译自starlabs.sg [原文链接](https://starlabs.sg/blog/2020/09/pwn2own-2020-oracle-virtualbox-escape/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **passw0day** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/218775](/post/id/218775)

安全客 - 有思想的安全新媒体

本文转载自: [starlabs.sg](https://starlabs.sg/blog/2020/09/pwn2own-2020-oracle-virtualbox-escape/)

如若转载,请注明出处： <https://starlabs.sg/blog/2020/09/pwn2own-2020-oracle-virtualbox-escape/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞利用](/tag/漏洞利用)

 **+1** __4赞

 __收藏

![](https://p5.ssl.qhimg.com/t010857340ce46bb672.jpg) passw0day

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

