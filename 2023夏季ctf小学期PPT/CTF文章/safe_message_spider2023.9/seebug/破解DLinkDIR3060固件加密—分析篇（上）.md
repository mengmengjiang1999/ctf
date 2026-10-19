**译者：知道创宇404实验室翻译组  
原文链接：<https://0x434b.dev/breaking-the-d-link-dir3060-firmware-encryption-static-analysis-of-the-decryption-routine-part-2-1/>**

## 前言

在[第一篇](https://paper.seebug.org/1523/)中，我们突出了相关侦察步骤！在本文中，我们深入研究了IDA历险，更好地了解`imgdecrypt`如何操作，以确保最新路由器型号的固件完整性。

![img](https://images.seebug.org/content/images/2021/03/25/1616650866000-1vardm.png-w331s)使用默认的IDA加载选项

将二进制文件加载到IDA中时，将会出现一个功能列表。我们已经发现二进制代码应该是从调试符号中剥离出来的，使得调试整个代码变得较为困难，但从IDA提供给我们的方式来看，它还是相当不错的:

![img](https://images.seebug.org/content/images/2021/03/25/1616650883000-2ivzcc.png-w331s)

1.共有104个公认功能。

2.只有16个函数不能与任何库函数(或类似的函数)匹配，该程序很可能包含由D-Link生成的自定义解/加密程序。

3.即使二进制文件被称为`img` **`de`**`crypt`，主要入口点显示它显然也具有加密功能。

![img](https://images.seebug.org/content/images/2021/03/25/1616650888000-3wtfsw.png-w331s)带注释的主要功能

这里的要点是，为了进入二进制文件的解密部分，我们的`**argv`参数列表必须包含子字符串“decrypt”。如果不是这种情况，则`char
*strstr(const char *haystack, const char *needle)`会返回`NULL`，因为它在`haystack
(argv[0] == "imgdecrypt\0")`中找不到"decrypt"。如果返回NULL，则`beqz $v0,
loc_402AE0`指令将计算正确，并将控制流重定向到`loc_402AE0`，这是二进制文件的加密部分。不理解的话，建议您仔细阅读本系列的[第1部分](https://paper.seebug.org/1523/)。

因为我们正在分析的二进制文件`imgdecrypt`被调用，从 _argv_ 空间的开头进行搜索会找到途径进入解密例程。为了能够输入 _加密_
例程，我们需要重命名二进制文件。

所以现在我们知道了如何到达存放解密固件`decrypt_firmware`的基本块。在输入之前，应该仔细查看该函数是否带有参数以及使用哪个参数。从带注释的版本中可以看到，`argc`被加载到`$a0`中，`argv`被加载到`$a1`。根据MIPS32
ABI，这两个寄存器保存了前两个函数参数！

## crypto_firmware

![img](https://images.seebug.org/content/images/2021/03/25/1616650896000-4kljfe.png-w331s)crypto_firmware概述

从IDA如何在图形视图中分组基本块进入`decrypt_firmware`函数后，我们可以肯定两件事:从IDA如何

1.解密有两个明显的途径

2.存在某种形式的循环。

![img](https://images.seebug.org/content/images/2021/03/25/1616650904000-5fpmkb.png-w331s)

开头的少数几个`lw`和`sw`指令是在适当的位置设置堆栈框架和函数参数，还记得[第1部分](https://paper.seebug.org/1523/)中的`/etc_ro/public.pem`吗？在这里的函数序言中，还为以后的使用设置了证书。除此之外，`argc`被加载到`$v0`中，通过`slti
$v0, 2`和2进行比较，并将其与下一条指令`beqz $v0, loc_402670`转换为以下样式代码：

    
    
    if(argc < 2) {
      ...
    } else {
      goto loc_402670
    }

这意味着要正确地调用`imgdecrypt`，我们至少还需要一个参数（因为`./imgdecrypt`意味着 _argc_
为1）。这是有道理的，因为如果不提供至少一个加密的固件映像，调用此二进制文件将不会获得任何收益！让我们先检查一下要避免的错误路径：

![img](https://images.seebug.org/content/images/2021/03/25/1616650907000-6oxmrm.png-w331s)

正如预期的那样，二进制文件接受一个输入文件，将其命名为sourceFile，二进制操作的模式可以是解密或加密。回到我们想要遵循的控制流，一旦确定argc至少是2，就需要对argc进行另外的检查:

    
    
    lw  $v0, 0x34+argc($sp)
    nop
    slti  $v0, 3
    bnez  $v0, loc_402698

直接转换为：

    
    
     if(argc < 3) {
       // $v0 == 1
       goto loc_402698
     } else {
       // $v0 == 0
       goto loadUserPem
     }

我所说的`loadUserPem`允许用户`certificate.pem`在调用时自定义，然后将其存储在默认值所在的内存位置`/etc_ro/public.pem`。由于这不是我们目前的着重点，就此忽略，并继续`loc_402698`。我们直接设置了一个函数调用，将它重命名为`check_cert`，将参数分别加载到`$a0`和中`$a1`：`check_cert(pemFile,
0)`

## check_cert

简单的是，它仅利用了一些库功能。

![img](https://images.seebug.org/content/images/2021/03/25/1616650915000-7quxmd.png-w331s)完整的checkCert例程

设置完堆栈框架后，将通过执行`FILE *fopen(const char *pathname, const char
*mode)`来检查提供的证书位置是否有效，失败时将返回一个`NULL`指针。如果是这样，`beqz $v0, early_return`它将评估为
_true_ ，控制流将采用 _early_return_ 路径，最终将`-1`从函数返回，如同`lw $v0, RSA_cert; beqz $v0,
bad_end`评估为 _true_ 一样，RSA_cert _尚未初始化为它拥有任何数据的地步以通过对_ 0*的检查。

在这种情况下，成功打开文件后，`RSA *RSA_new(void)`和`RSA *PEM_read_RSAPublicKey(FILE *fp, RSA
**x, pem_password_cb \*cb, void \*u*)`将用于填充`RSA *RSA_struct`。

该结构具有以下字段：

    
    
    struct {
           BIGNUM *n;              // public modulus
           BIGNUM *e;              // public exponent
           BIGNUM *d;              // private exponent
           BIGNUM *p;              // secret prime factor
           BIGNUM *q;              // secret prime factor
           BIGNUM *dmp1;           // d mod (p-1)
           BIGNUM *dmq1;           // d mod (q-1)
           BIGNUM *iqmp;           // q^-1 mod p
           // ...
           }; RSA
    // In public keys, the private exponent and the related secret values are NULL. 

最后，这些值（也称为公共密钥）将通过`sw $v1,
RSA_cert`指令存储在`RSA_cert`中。接下来，函数被拆解，比较`early_return`得到一个值！=
0，我们的函数将在`good_end`基本块中将返回值设置为0 `move $v0, $zero`。

* * *

在`decrypt_firmware`中，`check_cert`的返回值被放置到内存中(我将它重新标记为`loop_ctr`，因为它稍后将被重用)，并将其与0进行比较。只有在满足该条件时，控制流才会继续深入到程序中以检查`_cert_succ`。在这里，我们直接将控制流重定向到`call_aes_cbc_encrypt()`，并使用`key_0`作为其第一个参数。

![img](https://images.seebug.org/content/images/2021/03/25/1616650922000-8jmlqu.png-w331s)公钥检查

## call_aes_cbc_encrypt

该函数本身仅充当包装器，因为它直接调用带有5个参数的`aes_cbc_encrypt()`，前四个寄存器为`$a0 - $a3`，第五个在堆栈上。

![img](https://images.seebug.org/content/images/2021/03/25/1616650926000-9lsatz.png-w331s)call_aes_cbc_encrypt

五个自变量中的四个被硬编码到此二进制文件中，并通过以下方式从内存中加载：加载内存基地址（`lw $v0,
offset_crypto_material`）并向其添加偏移量（`addiu $a0, $v0, offset`），直接一个接一个地放置：

  * `offset_crypto_material + 0x20`→ `C8D32F409CACB347C8D26FDCB9090B3C`（in）
  * `offset_crypto_material + 0x10`→ `358790034519F8C8235DB6492839A73F`（userKey）
  * `offset_crypto_material`→ `98C9D8F0133D0695E2A709C8B69682D4`（IVEC）
  * `0x10` →密钥长度

这基本上转换为带有以下签名的函数调用：`aes_cbc_encrypt(*ptrTo_C8D32F409CACB347C8D26FDCB9090B3C,
0x10, *ptrTo_358790034519F8C8235DB6492839A73F,
*ptrTo_98C9D8F0133D0695E2A709C8B69682D4, *key_copy_stack`。重命名 _key_copy_stack_
，实际上它只是一个16字节的缓冲区。

## aes_cbc_encrypt

该函数的前三分之一是常见的堆栈框架设置，因为它需要正确处理5个函数参数。

![img](https://images.seebug.org/content/images/2021/03/25/1616650937000-10xdktp.png-w331s)

此外，`AES_KEY`定义了一个如下结构：

    
    
    #define AES_MAXNR 14
    // [...]
    struct aes_key_st {
    #ifdef AES_LONG
        unsigned long rd_key[4 *(AES_MAXNR + 1)];
    #else
        unsigned int rd_key[4 *(AES_MAXNR + 1)];
    #endif
        int rounds;
    };
    typedef struct aes_key_st AES_KEY;

在第一次库调用`AES_set_decrypt_key(const unsigned char *userKey, const int bits,
AES_KEY *key)`时需要这个函数，它将key配置为使用
`bits`-bit密钥解密`userKey`。在这个特殊的例子中，键的大小是0x80(128位==
16字节)。最后，调用`AES_cbc_encrypt(const uint8_t *in, uint8_t *out, size_t len, const
AES_KEY *key, uint8_t *ivec, const int enc)`，这个函数从`in`到`out`加密(如果`enc ==
0`即解密)
`len`字节。由于`out`是从`call_aes_cbc_encrypt`中外部提供的内存地址(`key_copy_stack`，即16字节缓冲区)，`AES_cbc_encryp`t直接存储在内存中，而不是用作此函数的专用返回值，而是返回`move
$v0, $zero`。

_注意：_ 对于想知道这些`lwl`并`lwr`在其中做什么的人……它们显示未对齐的内存访问，看起来`ivec`是像数组一样在访问，但之后从未使用过。

无论如何，这个函数实际上所做的是设置来自硬编码组件的解密密钥。因此，“生成的”解密密钥每次都是相同的，我们可以很容易地编写这个行为:

    
    
    from Crypto.Cipher import AES
    from binascii import b2a_hex
    
    inFile = bytes.fromhex('C8D32F409CACB347C8D26FDCB9090B3C')
    userKey = bytes.fromhex('358790034519F8C8235DB6492839A73F')
    ivec = bytes.fromhex('98C9D8F0133D0695E2A709C8B69682D4')
    cipher = AES.new(userKey, AES.MODE_CBC, ivec)
    b2a_hex(cipher.decrypt(inFile)).upper()
    
    # b'C05FBF1936C99429CE2A0781F08D6AD8'

我们现在又重新获得`decrypt_firmware`有关静态解密密钥的新知识：

## crypto_firmware

![img](https://images.seebug.org/content/images/2021/03/25/1616650948000-11yijei.png-w331s)

无论出于何种原因，二进制文件现在都会进入一个循环结构，该结构会打印出先前计算出的解密密钥，绿色标记的基本块大致转换为以下代码：

    
    
    int ctr = 0;
    while(ctr <= 0x10 ) {
      printf("%02X", *(key + ctr));
      ctr += 1;
    }

我的假设是，它可能用于内部调试，所以当改变`ivec`时，仍可以很快得到新的解密密钥……一旦将解密密钥打印到标准输出上，循环条件就会将控制流重定向到标记为`path_to_dec`的基本块，其中`actual_decryption(argv[1],
"/tmp/.firmware.orig", *key)`正在准备。

完成控制流和参数后，调用标记为`actual_decryption`的函数。

## actual_decryption

该功能是将这种解密方案结合在一起的主体。

![img](https://images.seebug.org/content/images/2021/03/25/1616650955000-12zmtga.png-w331s)

第一部分通过初始化所有0来准备两个存储位置`void *memset(void *s, int c, size_t
n)`。我将这些区域表示为`buf[68]`和`buf[0x98]` `statbuf_[98]`。该函数通过调用`int stat(const char
*pathname, struct stat
*statbuf)`来检查`argv[1]`中提供的sourceFile是否确实存在,结果存储在一个stat结构中，如下所示:

    
    
    struct stat {
        dev_t st_dev;         /* ID of device containing file */
        ino_t st_ino;         /* Inode number */
        mode_t st_mode;        /* File type and mode */
        nlink_t st_nlink;       /* Number of hard links */
        uid_t st_uid;         /* User ID of owner */
        gid_t st_gid;         /* Group ID of owner */
        dev_t st_rdev;        /* Device ID (if special file) */
        off_t st_size;        /* Total size, in bytes */
        blksize_t st_blksize;     /* Block size for filesystem I/O */
        blkcnt_t st_blocks;      /* Number of 512B blocks allocated */
    
        /* Since Linux 2.6, the kernel supports nanosecond
            precision for the following timestamp fields.
            For the details before Linux 2.6, see NOTES. */
    
        struct timespec st_atim;  /* Time of last access */
        struct timespec st_mtim;  /* Time of last modification */
        struct timespec st_ctim;  /* Time of last status change */
    
    #define st_atime st_atim.tv_sec      /* Backward compatibility */
    #define st_mtime st_mtim.tv_sec
    #define st_ctime st_ctim.tv_sec
    };

如果成功(意味着路径名存在)，`stat`返回0；当`bnez
$v0`失败，`stat_fail`会跟随到`stat_fail`的分支。所以我们要确保`$v0`是0，才能正常继续，所需控制流如下:

![img](https://images.seebug.org/content/images/2021/03/25/1616650957000-13wnwpi.png-w331s)

在这里，除了保存一些局部变量外， _sourceFile_ 还以只读模式打开，由`0x0`提供给的标志指示`open(const char
*pathname, int flags)`。该调用的结果/返回的文件描述符保存到`0x128+fd_enc`。与 _stat_ 例程类似，如之前检查
_stat_ 例程是否`open(sourceFile, O_RDONLY)` 成功 _`bltz $v0,
open_enc_fail`。_该分支`open_enc_fail`只采取了`$v0 <
0`因此，假设打开调用成功，我们将通过`$v0`持有打开文件描述符进入下一部分：

![img](https://images.seebug.org/content/images/2021/03/25/1616650961000-14qfglj.png-w331s)

这基本上是尝试使用`void mmap(void addr, size_t length, int prot, int flags, int fd,
off_t offset)`将刚打开的文件映射到内核选择的`***addr == 0`共享（只读）的内存区域。

这样的标志可以很容易地从系统文件中提取出来，如下所示：

    
    
    > egrep -i '(PROT_|MAP_)' /usr/include/x86_64-linux-gnu/bits/mman-linux.h
       implementation does not necessarily support PROT_EXEC or PROT_WRITE
       without PROT_READ.  The only guarantees are that no writing will be
       allowed without PROT_WRITE and no access will be allowed for PROT_NONE. */
    #define PROT_READ   0x1     /* Page can be read.  */
    #define PROT_WRITE  0x2     /* Page can be written.  */
    #define PROT_EXEC   0x4     /* Page can be executed.  */
    #define PROT_NONE   0x0     /* Page can not be accessed.  */
    #define PROT_GROWSDOWN  0x01000000  /* Extend change to start of
    #define PROT_GROWSUP    0x02000000  /* Extend change to start of
    #define MAP_SHARED  0x01        /* Share changes.  */
    #define MAP_PRIVATE 0x02        /* Changes are private.  */
    # define MAP_SHARED_VALIDATE    0x03    /* Share changes and validate
    # define MAP_TYPE   0x0f        /* Mask for type of mapping.  */
    #define MAP_FIXED   0x10        /* Interpret addr exactly.  */
    # define MAP_FILE   0
    # ifdef __MAP_ANONYMOUS
    #  define MAP_ANONYMOUS __MAP_ANONYMOUS /* Don't use a file.  */
    #  define MAP_ANONYMOUS 0x20        /* Don't use a file.  */
    # define MAP_ANON   MAP_ANONYMOUS
    /* When MAP_HUGETLB is set bits [26:31] encode the log2 of the huge page size.  */
    # define MAP_HUGE_SHIFT 26
    # define MAP_HUGE_MASK  0x3f

在这种情况下，先前的 _stat_ 调用再次派上用场，因为它不仅用于验证 _argv [1]中_ 提供的文件是否确实存在，而且 _statStruct_
还包含`st_blocks`可用于填充所需`size_t length`参数的成员。 _mmap_
的返回值存储在中`0x128+mmap_enc_fw($sp)`，'if'条件类型分支检查内存映射是否成功。成功时，mmap返回一个指向映射区域的指针，并在`beqz
$v0`上进行分支，`mmap_fail`不会出现，因为`$v0`包含一个值!= 0。以下是对open的最后一次调用：

![img](https://images.seebug.org/content/images/2021/03/25/1616650963000-15vjfod.png-w331s)

这只是尝试将预定义的路径（ _“ /tmp/.firmware.orig”_
）以读写方式打开，并将新文件描述符保存在`0x128+fd_tmp($sp)`。如果打开失败，则分支到该函数的失败部分；如果成功后，这将引导我们进行最后的步骤：

![img](https://images.seebug.org/content/images/2021/03/25/1616650970000-16yfvpo.png-w331s)

1.我们准备在/tmp/位置中设置新打开的文件的正确大小，首先通过调用lseek来查找`stat.st_blocks -1`的偏移量(`fd_tmp,
stat.st_blocks -1`)。

2.当lseek操作成功时，我们向该偏移位置的文件写入一个0，这使得我们可以轻松快速地创建一个“空”文件，而不需要写入N个字节(其中N==所需的文件大小，以字节为单位)。最后，关闭、重新打开并使用新的权限重新映射文件。

## 总结

到目前为止，我们还没有深入挖掘解密例程，这篇文章即将发表的第二部分将只关注D-Link所利用的方案加密方面。

如果您始终无法正确操作，可以在此处找到到目前为止的完整源代码。

    
    
    #include <arpa/inet.h>
    #include <errno.h>
    #include <fcntl.h>
    #include <openssl/aes.h>
    #include <openssl/pem.h>
    #include <openssl/rsa.h>
    #include <stddef.h>
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <sys/mman.h>
    #include <sys/stat.h>
    #include <sys/types.h>
    #include <unistd.h>
    
    static RSA *grsa_struct = NULL;
    static unsigned char iv[] = {0x98, 0xC9, 0xD8, 0xF0, 0x13, 0x3D, 0x06, 0x95,
                                 0xE2, 0xA7, 0x09, 0xC8, 0xB6, 0x96, 0x82, 0xD4};
    static unsigned char aes_in[] = {0xC8, 0xD3, 0x2F, 0x40, 0x9C, 0xAC,
                                     0xB3, 0x47, 0xC8, 0xD2, 0x6F, 0xDC,
                                     0xB9, 0x09, 0x0B, 0x3C};
    static unsigned char aes_key[] = {0x35, 0x87, 0x90, 0x03, 0x45, 0x19,
                                      0xF8, 0xC8, 0x23, 0x5D, 0xB6, 0x49,
                                      0x28, 0x39, 0xA7, 0x3F};
    
    unsigned char out[] = {0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37,
                           0x38, 0x39, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46};
    
    int check_cert(char *pem, void *n) {
      OPENSSL_add_all_algorithms_noconf();
    
      FILE *pem_fd = fopen(pem, "r");
      if (pem_fd != NULL) {
        RSA *lrsa_struct[2];
        *lrsa_struct = RSA_new();
        if (!PEM_read_RSAPublicKey(pem_fd, lrsa_struct, NULL, n)) {
          RSA_free(*lrsa_struct);
          puts("Read RSA private key failed, maybe the password is incorrect.");
        } else {
          grsa_struct = *lrsa_struct;
        }
        fclose(pem_fd);
      }
      if (grsa_struct != NULL) {
        return 0;
      } else {
        return -1;
      }
    }
    
    int aes_cbc_encrypt(size_t length, unsigned char *key) {
      AES_KEY dec_key;
      AES_set_decrypt_key(aes_key, sizeof(aes_key) * 8, &dec_key);
      AES_cbc_encrypt(aes_in, key, length, &dec_key, iv, AES_DECRYPT);
      return 0;
    }
    
    int call_aes_cbc_encrypt(unsigned char *key) {
      aes_cbc_encrypt(0x10, key);
      return 0;
    }
    
    int actual_decryption(char *sourceFile, char *tmpDecPath, unsigned char *key) {
      int ret_val = -1;
      size_t st_blocks = -1;
      struct stat statStruct;
      int fd = -1;
      int fd2 = -1;
      void *ROM = 0;
      int *RWMEM;
      off_t seek_off;
      unsigned char buf_68[68];
      int st;
    
      memset(&buf_68, 0, 0x40);
      memset(&statStruct, 0, 0x90);
      st = stat(sourceFile, &statStruct);
      if (st == 0) {
        fd = open(sourceFile, O_RDONLY);
        st_blocks = statStruct.st_blocks;
        if (((-1 < fd) &&
             (ROM = mmap(0, statStruct.st_blocks, 1, MAP_SHARED, fd, 0),
              ROM != 0)) &&
            (fd2 = open(tmpDecPath, O_RDWR | O_NOCTTY, 0x180), -1 < fd2)) {
          seek_off = lseek(fd2, statStruct.st_blocks - 1, 0);
          if (seek_off == statStruct.st_blocks - 1) {
            write(fd2, 0, 1);
            close(fd2);
            fd2 = open(tmpDecPath, O_RDWR | O_NOCTTY, 0x180);
            RWMEM = mmap(0, statStruct.st_blocks, PROT_EXEC | PROT_WRITE,
                         MAP_SHARED, fd2, 0);
            if (RWMEM != NULL) {
              ret_val = 0;
            }
          }
        }
      }
      puts("EOF part 2.1!\n");
      return ret_val;
    }
    
    int decrypt_firmware(int argc, char **argv) {
      int ret;
      unsigned char key[] = {0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37,
                             0x38, 0x39, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46};
      char *ppem = "/tmp/public.pem";
      int loopCtr = 0;
      if (argc < 2) {
        printf("%s <sourceFile>\r\n", argv[0]);
        ret = -1;
      } else {
        if (2 < argc) {
          ppem = (char *)argv[2];
        }
        int cc = check_cert(ppem, (void *)0);
        if (cc == 0) {
          call_aes_cbc_encrypt((unsigned char *)&key);
    
          printf("key: ");
          while (loopCtr < 0x10) {
            printf("%02X", *(key + loopCtr) & 0xff);
            loopCtr += 1;
          }
          puts("\r");
          ret = actual_decryption((char *)argv[1], "/tmp/.firmware.orig",
                                  (unsigned char *)&key);
    
          if (ret == 0) {
            unlink(argv[1]);
            rename("/tmp/.firmware.orig", argv[1]);
          }
          RSA_free(grsa_struct);
        } else {
          ret = -1;
        }
      }
      return ret;
    }
    
    int encrypt_firmware(int argc, char **argv) { return 0; }
    
    int main(int argc, char **argv) {
      int ret;
      char *str_f = strstr(*argv, "decrypt");
    
      if (str_f != NULL) {
        ret = decrypt_firmware(argc, argv);
    
      } else {
        ret = encrypt_firmware(argc, argv);
      }
    
      return ret;
    }

anual_decryption例程的伪C代码

    
    
    > ./imgdecrypt
    ./imgdecrypt <sourceFile>
    > ./imgdecrypt testFile
    key: C05FBF1936C99429CE2A0781F08D6AD8
    EOF part 2.1!

本文的下篇不久后将发布，敬请期待！

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1524/>

