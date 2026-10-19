日前，著名Web服务器和反向代理服务器Nginx暴严重漏洞NS解析器Off-by-One堆写入漏洞，该漏洞存在于Nginx的DNS解析模块ngx_resolver_copy()。攻击者可以利用该漏洞进行远程DDos攻击，甚至远程执行。  
![image](https://image.3001.net/images/20210526/1621997020_60adb5dc1ba04b9e8aa4f.png!small)

## 概述

ngx_resolver_copy()在处理DNS响应时出现一个off-by-one错误，利用该漏洞网络攻击者可以在堆分配的缓冲区中写一个点字符（.’,
0x2E）导致超出范围。 所有配置解析器语法的（resolver xxxx）Nginx实例可以通过DNS响应（响应来自Nginx的DNS请求）来触发该漏洞。
特制数据包允许使用0x2E覆盖下一个堆块元数据的最低有效字节，利用该漏洞攻击者，可以实现Ddos拒绝服务，甚至可能实现远程代码执行。

由于Nginx中缺乏DNS欺骗缓解措施，并且在检查DNS事务ID之前调用了易受攻击的功能，因此远程攻击者可能能够通向中毒服务器注入受毒的DNS响应来利用此漏洞。

> 漏洞影响
>
> 严重等级： 高
>
> 漏洞向量： 远程/DNS
>
> 确认的受影响版本： 0.6.18-1.20.0
>
> 确认的修补版本： 1.21.0，1.20.1
>
> 供应商： F5，Inc.
>
> 状态： 公开
>
> CVE： CVE-2021-23017
>
> CWE： 193
>
> CVSS得分： 8.1
>
> CVSS向量：CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H/E:U/RL:O/RC:C

## 漏洞分析

当Nginx配置中设置resolver时，Nginx DNS解析器（core/ngx_resolver.c）用于通过DNS解析多个模块的主机名。

Nginx中通过ngx_resolver_copy()调用来验证和解压缩DNS响应中包含的每个DNS域名，接收网络数据包作为输入和指向正在处理的名称的指针，并在成功后返回指向包含未压缩名称的新分配缓冲区的指针。调用整体上分两步完成的，

1）计算未压缩的域名大小的长度len并验证输入包的合法性，丢弃包含大于128个指针或包含超出输入缓冲区边界的域名。

2）分配输出缓冲区，并将未压缩的域名复制到其中。

第1部分中的大小计算与第2部分中的未压缩的域名之间的不匹配，导致一个len的一个off-by-one错误，导致允许以一个字节为单位写一个点字符超出name->data的边界。

当压缩名称的最后一部分包含一个指向NUL字节的指针时，就会发生计算错误。
尽管计算步骤仅考虑标签之间的点，但每次处理标签并且接着的字符为非NUL时，解压缩步骤都会写入一个点字符。当标签后跟指向NUL字节的指针时，解压缩过程将：

    
    
    // 1) copy the label to the output buffer,
    
    ngx_strlow(dst, src, n);
    
    dst += n;
    
    src += n;
    
    // 2) read next character,
    
    n = *src++;
    
    // 3) as its a pointer, its not NUL,
    
    if (n != 0) {
    
    // 4) so a dot character that was not accounted for is written out of bounds
    
    *dst++ = '.';
    
    }
    
    // 5) Afterwards, the pointer is followed,
    
    if (n & 0xc0) {
    
    n = ((n & 0x3f) << 8) + *src;
    
    src = &buf[n];
    
    n = *src++;
    
    }
    
    // 6) and a NULL byte is found, signaling the end of the function
    
    if (n == 0) {
    
    name->len = dst - name->data;
    
    return NGX_OK;
    
    }
    

如果计算的大小恰好与堆块大小对齐，则超出范围的点字符将覆盖下一个堆块长度的元数据中的最低有效字节。这可能会直接导致下一个堆块的大小写入，但还会覆盖3个标志，从而导致
PREV_INUSE被清除并 IS_MMAPPED被设置。

    
    
    ==7863== Invalid write of size 1
    
    ==7863== at 0x137C2E: ngx_resolver_copy (ngx_resolver.c:4018)
    
    ==7863== by 0x13D12B: ngx_resolver_process_a (ngx_resolver.c:2470)
    
    ==7863== by 0x13D12B: ngx_resolver_process_response (ngx_resolver.c:1844)
    
    ==7863== by 0x13D46A: ngx_resolver_udp_read (ngx_resolver.c:1574)
    
    ==7863== by 0x14AB19: ngx_epoll_process_events (ngx_epoll_module.c:901)
    
    ==7863== by 0x1414D4: ngx_process_events_and_timers (ngx_event.c:247)
    
    ==7863== by 0x148E57: ngx_worker_process_cycle (ngx_process_cycle.c:719)
    
    ==7863== by 0x1474DA: ngx_spawn_process (ngx_process.c:199)
    
    ==7863== by 0x1480A8: ngx_start_worker_processes (ngx_process_cycle.c:344)
    
    ==7863== by 0x14952D: ngx_master_process_cycle (ngx_process_cycle.c:130)
    
    ==7863== by 0x12237F: main (Nginx.c:383)
    
    ==7863== Address 0x4bbcfb8 is 0 bytes after a block of size 24 alloc'd
    
    ==7863== at 0x483E77F: malloc (vg_replace_malloc.c:307)
    
    ==7863== by 0x1448C--4: ngx_alloc (ngx_alloc.c:22)
    
    ==7863== by 0x137AE4: ngx_resolver_alloc (ngx_resolver.c:4119)
    
    ==7863== by 0x137B26: ngx_resolver_copy (ngx_resolver.c:3994)
    
    ==7863== by 0x13D12B: ngx_resolver_process_a (ngx_resolver.c:2470)
    
    ==7863== by 0x13D12B: ngx_resolver_process_response (ngx_resolver.c:1844)
    
    ==7863== by 0x13D46A: ngx_resolver_udp_read (ngx_resolver.c:1574)
    
    ==7863== by 0x14AB19: ngx_epoll_process_events (ngx_epoll_module.c:901)
    
    ==7863== by 0x1414D4: ngx_process_events_and_timers (ngx_event.c:247)
    
    ==7863== by 0x148E57: ngx_worker_process_cycle (ngx_process_cycle.c:719)
    
    ==7863== by 0x1474DA: ngx_spawn_process (ngx_process.c:199)
    
    ==7863== by 0x1480A8: ngx_start_worker_processes (ngx_process_cycle.c:344)
    
    ==7863== by 0x14952D: ngx_master_process_cycle (ngx_process_cycle.c:130)
    

虽然目前还没有Poc出来，理论上该漏洞可以被用来进行远程代码执行。

### 攻击向量分析

DNS响应可以通过多种方式触发漏洞。

首先，Nginx必须发送了DNS请求，并且必须等待响应。 然后，可以在DNS响应的多个部分进行投毒：

DNS问题QNAME，

DNS回答名称，

DNS会回答RDATA以获得CNAME和SRV响应，

通过使用多个中毒的QNAME，NAME或RDATA值制作响应，可以在处理响应时多次击中易受攻击的函数，从而有效地执行多次脱机写入。

此外，当攻击者提供中毒的CNAME时，它将以递归方式解决，从而在执行过程中触发了额外的OOB写操作 ngx_resolve_name_locked()
调用ngx_strlow()（ngx_resolver.c：594）和其他OOB读取期间
ngx_resolver_dup()（ngx_resolver.c：790）和 ngx_crc32_short()（ngx_resolver.c：596）。

用于“example.net”请求的DNS响应示例负载，其中包含被污染的CNAME：  
![image](https://image.3001.net/images/20210526/1621997064_60adb608d14af2cec56ef.png!small)  
稍微不同的有效负载（poc.py中的有效负载）填充了足够的字节以覆盖 next_chunk.mchunk_size带点的最低有效字节：  
![image](https://image.3001.net/images/20210526/1621997072_60adb610b3be68eab77d2.png!small)  
24字节的标签导致分配了24字节的缓冲区，该缓冲区填充有24字节+一个超出范围的点字符。

## 漏洞修复和解决

通过向域名解析时，在域名末尾写入的伪造的点字符分配一个额外的字节可以缓解此问题。

## 受漏洞影响的配置

    
    
    daemon off;
    
    http{
    
    access_log logs/access.log;
    
    server{
    
    listen 8080;
    
    location / {
    
    resolver 127.0.0.1:1053;
    
    set $dns example.net;
    
    proxy_pass $dns;
    
    }
    
    }
    
    }
    
    events {
    
    worker_connections 1024;
    
    }
    

