作者：[suezi@IceSword Lab](http://www.iceswordlab.com/2017/10/30/ChromeOS-Userdata-Protection-Mechanism-Based-On-EXT4-Encryption/ "suezi@IceSword Lab")

#### 概述

自2015年开发的 EXT4 Encryption 经过两年的验证性使用，Google 终于在年初的时候将 EXT4 Encryption 合并入
Chrome OS 用于保护用户的隐私数据，完成与 eCryptfs 同样的功能，简称该技术为 Dircrypto。当前，Chrome OS 仍是
eCryptfs 和 Dircrypto 两种技术并存，但优先采用 Dircrypto，这表明 Dircrypto
将成为以后的主流趋势。本文试图阐述该技术的实现原理。

与 eCryptfs 一样，EXT4 Encryption
用于完成文件（包括目录）和文件名的加密，以实现多用户系统中各个用户私有数据的安全，即使在设备丢失或被盗的情况下，用户隐私数据也不会轻易被人窥见。本文着重介绍文件内容加解密，文件名加解密留给读者自行研究，技术要点主要包括：加解密模型、密钥管理、EXT4
Encrytion 功能的开/关及参数设定操作。

#### EXT4 Encryption 简述

创立 eCryptfs 十年之后，其主要的作者 Michael Halcrow 已从之前的 IBM 转向服务 Google。Google
在保护用户数据隐私方面具有强烈的需求，应用在其旗下的 Android、Chrome OS 及数据中心，此时采用的文件系统都是 EXT4，eCryptfs
属于堆叠在 EXT4 上的文件系统，性能必定弱于直接在 EXT4 实现加密，恰好 EXT4 的主要维护者是 Google 的 Theodore Ts’o
，因此由 Michael Halcrow 主导、Theodore Ts’o 协助开发完成 EXT4
Encryption，目标在于“Harder，Better，Faster，Stronger”。

相比 eCryptfs，EXT4 Encryption 在内存使用上有所优化，表现在 read page 时，直接读入密文到 page cache 并在该
page 中解密；而 eCryptfs 首先需要调用 EXT4 接口完成读入密文到 page cache，然后再解密该 page 到另外的 page
cache 页，内存花销加倍。当然，write page 时，两者都不能直接对当前 page cache
加密，因为cache的明文内容需要保留着后续使用。在对文件加密的控制策略上，两者都是基于目录，但相比 eCryptfs 使用的 mount 方法，EXT4
Encryption 采用 ioctl 的策略显得更加方便和灵活。另外，在密钥管理方面，两者也不相同。

EXT4 Encryption 加/解密文件的核心思想是：每个用户持有一个 64 Bytes 的 master key，通过 master key
的描述（master key descriptor，实际使用时一般采用 key signature
加上“ext4:”前缀）进行识别，每个文件单独产生一个16 Bytes的随机密钥称为nonce，之后以nonce做为密钥，采用 AES-128-ECB
算法加密 master key，产生 derived key。加/解密文件时采用 AES-256-XTS 算法，密钥是 derived
key。存储文件时，将包含有格式版本、内容加密算法、文件名加密算法、旗标、 master key 描述、nonce等信息在内的数据保存在文件的 xattr
扩展属性中。而master key由用户通过一些加密手段进行存储，在激活 EXT4 Encryption
前通过keys的系统调用以“logon”类型传入内核keyring，即保证master只能被应用程序创建及更新但不能被应用程序读取。加密是基于目录树的形式进行，加密策略通过`EXT4_IOC_SET_ENCRYPTION
ioctl`对某个目录进行下发，其子目录或文件自动继承父目录的属性，ioctl
下发的内容包括策略版本号、文件内容加密模式、文件名加密模式、旗标、master key 的描述。文件 read 操作时，从磁盘 block 中读入密文到
page cache 并在该 page 中完成解密，然后拷贝到应用程序；文件 write 时采用 write page 的形式写入磁盘，但不是在当前
page cache 中直接加密，而是将加密后的密文保存在另外的 page 中。

和 eCryptfs 一样，EXT4 Encryption 在技术实现时利用了 page cache 机制的 Buffered I/O,换而言之就是不支持
Direct I/O。其加/解密的流程如图一所示。

![](https://images.seebug.org/content/images/2017/10/53086d47-99ec-46d1-ad9d-7cf6351dfef0.png-w331s)
图一 EXT4 Encryption加/解密流程

图一中，在创建加密文件时通过`get_random_bytes`函数产生 16 Bytes 的随机数，将其做为 nonce 保存到文件的 xattr
属性中；当打开文件时取出文件的 nonce 和 master key 的描述，通过 master key 描述匹配到应用程序下发的 master
key；然后以 nonce 做为密钥，采用 AES-128-ECB 算法加密 master key 后产生 derived
key，加/解密文件时采用该derived key做为密钥，加密算法由用户通过 ioctl 下发并保存到 xattr
的`“contents_encryption_mode”`字段，目前版本仅支持 AES-256-XTS；加/解密文件内容时调用 kernel crypto
API 完成具体的加/解密功能。

下面分别从 EXT4 Encryption 使用的数据结构、内核使能 EXT4 Encryption 功能、如何添加 master key 到
keyring、如何开启 EXT4 Encryption 功能、创建和打开加密文件、读取和解密文件、加密和写入加密文件等方面详细叙述。

#### EXT4 Encryption 详述

##### EXT4 Encryption 的主要数据结构

通过数据结构我们可以窥视到 EXT4 Encryption 的密钥信息的保存和使用方式，非常有利于理解该加密技术。涉及到主要数据结构如下：

master key 的 payload 的数据表示如清单一所示，应用程序通过 add_key 系统调用将其和 master key descriptor
传入内核 keyring。

###### 清单一 master key

    
    
    /* This is passed in from userspace into the kernel keyring */
    struct ext4_encryption_key {
            __u32 mode;
            char raw[EXT4_MAX_KEY_SIZE];
            __u32 size;
    } __attribute__((__packed__));

EXT4 Encryption 的文件加密信息的数据存储结构如清单二结构体`struct
ext4_encryption_context`所示，每个文件都对应保存着这样的一个数据结构在其 xattr
中，包含了加密版本、文件内容和文件名的加密算法、旗标、master key descriptor 和随机密钥 nonce。

###### 清单二 加密信息存储格式

    
    
    /**
     * Encryption context for inode
     *
     * Protector format:
     *  1 byte: Protector format (1 = this version)
     *  1 byte: File contents encryption mode
     *  1 byte: File names encryption mode
     *  1 byte: Reserved
     *  8 bytes: Master Key descriptor
     *  16 bytes: Encryption Key derivation nonce
     */
    struct ext4_encryption_context {
        char format;
        char contents_encryption_mode;
        char filenames_encryption_mode;
        char flags;
        char master_key_descriptor[EXT4_KEY_DESCRIPTOR_SIZE];
        char nonce[EXT4_KEY_DERIVATION_NONCE_SIZE];
    } __attribute__((__packed__));

设置 EXT4 Encryption 开启是通过对特定目录进行`EXT4_IOC_SET_ENCRYPTION
ioctl`完成，具体策略使用清单三所示的`struct ext4_encryption_policy`
数据结构进行封装，包括版本号、文件内容的加密算法、文件名的加密算法、旗标、master key
descriptor。每个加密文件保存的`ext4_encryption_context`信息均继承自该数据结构，子目录继承父目录的`ext4_encryption_context`。

###### 清单三 Encryption policy

    
    
    /* Policy provided via an ioctl on the topmost directory */
    struct ext4_encryption_policy {
        char version;
        char contents_encryption_mode;
        char filenames_encryption_mode;
        char flags;
        char master_key_descriptor[EXT4_KEY_DESCRIPTOR_SIZE];
    } __attribute__((__packed__));
    `

open 文件时将文件加密相关信息从 xattr 中读出并保存在清单四的`struct ext4_crypt_info`数据结构中，成员 ci_ctfm
用于调用 kernel crypto，在文件 open 时做好 key 的初始化。从磁盘获取到加密信息后，将该数据结构保存到 inode
的内存表示`struct ext4_inode_info`中的`i_crypt_info`字段，方便后续的 readpage、writepage
时获取到相应数据进行加/解密操作。

###### 清单四 保存加/解密信息及调用接口的数据结构

    
    
    struct ext4_crypt_info {
        char        ci_data_mode;
        char        ci_filename_mode;
        char        ci_flags;
        struct crypto_ablkcipher *ci_ctfm;
        char        ci_master_key[EXT4_KEY_DESCRIPTOR_SIZE];
    };
    `

如清单五所示，采用 `struct ext4_crypto_ctx` 表示在 readpage、writepage 时进行 page 加/解密的
context。在 writepage 时因为涉及到 cache 机制，需要保存明文页，所以专门申请单独的 bounce_page 保存密文用于写入磁盘，用
control_page 来指向正常的明文页。在 readpage 时，通过 bio 从磁盘中读出数据到内存页，读页完成后通过 queue_work
的形式调用解密流程并将明文保存在当前页，因此 context 中存在 work 成员。另外，为了提高效率，在初始化阶段一次性申请了128个
`ext4_crypto_ctx` 的内存空间并通过 free_list 链表进行管理。

###### 清单五 用于表示加/解密 page 的 context

    
    
    struct ext4_crypto_ctx {
        union {
            struct {
                struct page *bounce_page;       /* Ciphertext page */
                struct page *control_page;      /* Original page  */
            } w;
            struct {
                struct bio *bio;
                struct work_struct work;
            } r;
            struct list_head free_list;     /* Free list */
        };
        char flags;                      /* Flags */
        char mode;                       /* Encryption mode for tfm */
    };
    `

##### 使能 EXT4 Encryption

Linux kernel具有良好的模块化设计，EXT4 Encryption属于一个EXT4
FS中一个可选的模块，在编译kernel前需通过配置选项使能该功能，如下：

    
    
    CONFIG_EXT4_FS_SECURITY=y
    CONFIG_EXT4_FS_ENCRYPTION=y

##### 添加 master key 的流程

将 master key 添加到内核 keyring 属于 EXT4 Encryption 的第一步，该步骤通过 add_key 系统调用完成，master
key 在不同的 Linux 发行版有不同的产生及保存方法，这里以 Chrome OS 为例。

Chrome OS 在 cryptohomed 守护进程中完成 master key 的获取和添加到 keyring。因为兼容 eCryptfs 和
EXT4 Encryption（为了跟 Chrome OS 保持一致，后续以 Dircrypto 代替 EXT4 Encryption 的称呼），而
eCryptfs 属于前辈，eCryptfs 通过 mount 的方式完成加密文件的开启，为了保持一致性，cryptohomed 同样是在 mount
的准备过程中解密出 master key 和开启 Dircrypto，此 master key 即 eCryptfs 加密模式时用的 FEK，master
key descriptor 即 FEK 的 key signature，所以本节介绍 Dircrypto 流程时所谓的 mount
流程，望读者能够理解，在 Dircrypto 模式下，mount 不是真正“mount”，千万不要混淆。cryptohomed 的 mount 流程如下：

1.cryptohomed 在 D-Bus 上接收到持（包含用户名和密码）有效用户证书的 mount 请求，当然 D-Bus 请求也是有权限控制的；

2.假如是用户首次登陆，将进行：

a． 建立`/home/.shadow/[salt_hash_of_username]`目录，采用 SHA1 算法和系统的 salt
对用户名进行加密，生成`salt_hash_of_username`，简称`s_h_o_u`;

b． 生成`vault keyset
/home/.shadow/[salt_hash_of_username]/master.0`和`/home/.shadow/[salt_hash_of_username]/master.0.sum`。master.0
加密存储了包含有 FEK 和 FNEK 的内容以及非敏感信息如 salt、password rounds 等；master.0.sum 是对
master.0 文件内容的校验和。

3.采用通过 mount 请求传入的用户证书解密 keyset。当 TPM 可用时优先采用 TPM 解密，否则采用 Scrypt 库，当 TPM
可用后再自动切换回使用 TPM。cryptohome 使用 TPM 仅仅是为了存储密钥，由 TPM 封存的密钥仅能被 TPM
自身使用，这可用缓解密钥被暴力破解，增强保护用户隐私数据的安全。TPM 的首次初始化由 cryptohomed 完成。这里默认 TPM
可正常使用，其解密机制如下图二所示，其中：

UP：User Passkey，用户登录口令

EVKK：Ecrypted vault keyset key，保存在 master.0 中的“tpm_key”字段

IEVKK：Intermediate vault keyset key，解密过程生成的中间文件，属于EVKK的解密后产物，也是RSA解密的输入密文

TPM_CHK: TPM-wrapped system-wide Cryptohome
key，保存在`/home/.shadow/cryptohome.key`，TPM init时加载到TPM

VKK：Vault keyset key

VK：Vault Keyset，包含FEK和FNEK

EVK：Encrypted vault keyset，保存在master.0里”wrapped_keyset”字段

![](https://images.seebug.org/content/images/2017/10/403d2d3f-4601-4c80-814c-b22ab6b3abe8.png-w331s)
图二 TPM解密VK的流程

图二中的UP（由发起mount的D-Bus请求中通过key参数传入）做为一个AES
key用于解密EVKK，解密后得到的IEVKK；然后将IEVKK做为RSA的密文送入TPM，使用TPM_CHK做为密钥进行解密，解密后得到VKK；最后生成的VKK是一个AES
key，用于解密master.0里的EVK，得到包含有FEK和FNEK明文的VK。经过三层解密，终于拿到关键的FEK，此FEK在Dircrypto模式下当做master
key使用，FEK signature即做master key descriptor使用。

最后通过 add_key 系统调用将 master key 及 master key descriptor（在 keyring 中为了方便区分，master
key descriptor 由 key sign 加上前缀“ext4:”组成）添加到 keyring，如下清单六代码所示

###### 清单六 Chrome OS 传入 master key 的核心代码

    
    
    key_serial_t AddKeyToKeyring(const brillo::SecureBlob& key,
                                 const brillo::SecureBlob& key_descriptor) {
      //参数中的key即是master key，key_descriptor即sig
      if (key.size() > EXT4_MAX_KEY_SIZE ||
          key_descriptor.size() != EXT4_KEY_DESCRIPTOR_SIZE) {
        LOG(ERROR) << "Invalid arguments: key.size() = " << key.size()
                   << "key_descriptor.size() = " << key_descriptor.size();
        return kInvalidKeySerial;
      }
      //在upstart中已经通过add_key添加dircrypt的会话keyring
      key_serial_t keyring = keyctl_search(
          KEY_SPEC_SESSION_KEYRING, "keyring", kKeyringName, 0);
      if (keyring == kInvalidKeySerial) {
        PLOG(ERROR) << "keyctl_search failed";
        return kInvalidKeySerial;
      }
      //初始化struct ext4_encryption_key
      ext4_encryption_key ext4_key = {};
      ext4_key.mode = EXT4_ENCRYPTION_MODE_AES_256_XTS;
      memcpy(ext4_key.raw, key.char_data(), key.size());
      ext4_key.size = key.size();
      //key_name就是最后的master key description，由”ext4:”+sig两部分组成
      //kernel在request_key时同样是将”ext4:”+sig两部分组成master key description
      std::string key_name = kKeyNamePrefix + base::ToLowerASCII(
          base::HexEncode(key_descriptor.data(), key_descriptor.size()));
      // kKeyType是“logon”，不允许应用程序获取密钥的内容
      key_serial_t key_serial = add_key(kKeyType, key_name.c_str(), &ext4_key,
                                        sizeof(ext4_key), keyring);
      if (key_serial == kInvalidKeySerial) {
        PLOG(ERROR) << "Failed to insert key into keyring";
        return kInvalidKeySerial;
      }
      return key_serial;
    }
    `

##### Set Encryption Policy 流程

通过对目标目录的文件描述符进行 ioctl 的 `EXT4_IOC_SET_ENCRYPTION_POLICY` 操作即完成了 EXT4
Encryption 的加/解密功能的开启，该步骤在完成添加 master key 后进行，Chrome OS 中的相关代码如下清单七所示，通过
`struct ext4_encryption_policy` 指定了策略的版本号、文件内容和文件名的加密算法、旗标、master key 的识别描述符。

###### 清单七 Chrome OS set encryption policy 的核心代码

    
    
    bool SetDirectoryKey(const base::FilePath& dir,
                         const brillo::SecureBlob& key_descriptor) {
      DCHECK_EQ(static_cast<size_t>(EXT4_KEY_DESCRIPTOR_SIZE),
                key_descriptor.size());
      /*这里的dir代表要开启EXT4 Encryption的目录 */
      base::ScopedFD fd(HANDLE_EINTR(open(dir.value().c_str(),
                                          O_RDONLY | O_DIRECTORY)));
      if (!fd.is_valid()) {
        PLOG(ERROR) << "Ext4: Invalid directory" << dir.value();
        return false;
      }
       /*初始化struct ext4_encryption_policy对象 
       * 指定文件内容的加密算法是AES_256_XTS
      */
      ext4_encryption_policy policy = {};
      policy.version = 0;
      policy.contents_encryption_mode = EXT4_ENCRYPTION_MODE_AES_256_XTS;
      policy.filenames_encryption_mode = EXT4_ENCRYPTION_MODE_AES_256_CTS;
      policy.flags = 0;
      // key_descriptor即FEK 的key sig
      memcpy(policy.master_key_descriptor, key_descriptor.data(),
             EXT4_KEY_DESCRIPTOR_SIZE);
      /*通过ioctl完成设置*/
      if (ioctl(fd.get(), EXT4_IOC_SET_ENCRYPTION_POLICY, &policy) < 0) {
        PLOG(ERROR) << "Failed to set the encryption policy of " << dir.value();
        return false;
      }
      return true;
    }
    `

内核对`EXT4_IOC_SET_ENCRYPTION_POLICY`的 ioctl 在 ext4_ioctl
函数中完成响应，从应用程序中接收`ext4_encryption_policy`，解析其参数，若是首次对该目录进行加密设置则生成一个`ext4_encryption_context`
数据结构保存包括版本号、文件内容的加密算法、文件名的加密算法、旗标、master key descriptor、nonce 在内的所有信息到目录对应
inode 的 xattr 中。从此开始，以该目录做为 EXT Encryption 加密的根目录，其下文件和子目录的除了 nonce
需要再次单独产生外，其余加密属性均继承自该目录。若非首次对该目录进行 EXT4 Encryption
设置，则重点比较当前设置是否与先前的设置一致。首先介绍首次设置的情形， ext4_ioctl 的函数调用关系如图三所示。

![](https://images.seebug.org/content/images/2017/10/0311c8ff-5dc8-48a4-b2ff-5336675edde9.png-w331s)
图三 首次进行EXT4 Encryption设置的函数调用关系

应用程序进行 ioctl 系统调用经过 VFS，最终调用 ext4_ioctl 函数，借助图三的函数调用可看到进行 EXT4 Encryption
policy 设置时都进行了什么操作。首先判断目录所在的文件系统是否支持 EXT4 Encryption
操作，具体在`ext4_has_feature_encrypt` 函数中通过判断 superblock 的
`s_es->s_feature_incompat` 是否支持 ENCRYPT 属性；然后利用 `copy_from_user` 函数从用户空间拷贝
`ext4_encryption_policy` 到内核空间；紧接着在 `ext4_process_policy` 函数里将
`ext4_encryption_policy` 转换成 `ext4_encryption_context` 保存到 inode 的
attr；最后将加密目录对应的 inode 的修改保存到磁盘。重点部分在 `ext4_process_policy`
函数，主要分三大步骤，第一步还是进行照例检查校验，包括：访问权限、`ext4_encryption_policy`的版本号、目标目录是否为空目录、目标目录是否已经存在`ext4_encryption_context`；第二步为目标目录生成`ext4_encryption_context`并保存到
xattr；最后提交修改的保存请求。第一步的具体操作表现在函数操作上如下：

  * `inode_owner_or_capable()` 完成 DAC 方面的权限检查
  * 对`ext4_encryption_policy`的版本号 version 进行检查，当前仅支持版本0
  * `ext4_inode_has_encryption_context()`尝试读取目标目录对应的 inode 的 xattr 的 EXT4 Encryption 字段”c”，看是否存在内容，若存在内容，则说明目标目录在先前已经进行过 EXT4 Encryption 设置
  * `S_ISDIR()`校验目标目录是否真的是目录
  * `ext4_empty_dir()`判断目标目录是否为空目录，在首次设置 EXT4 Encryption 时，仅支持对空目录进行操作。这点有别于 eCryptfs，eCryptfs 加密文件所在的目录下支持非加密和加密文件的同时存在；而 EXT4 Encryption 要么是全加密，要么是全非加密。

第二步在`ext4_create_encryption_context_from_policy`函数中完成，具体如下：

  * `ext4_convert_inline_data()`对inline data做处理
  * `ext4_valid_contents_enc_mode()`校验`ext4_encryption_policy`的文件内容加密模式是否为`AES_256_XTS`，当前仅支持该算法的内容加密
  * `ext4_valid_filenames_enc_mode()`校验`ext4_encryption_policy`的文件名加密模式是否为`AES_256_CTS`，当前仅支持该算法的内容名加密
  * 对`ext4_encryption_policy`的 flags 做检验
  * `get_random_bytes()`产生 16 Bytes 的随机数，赋值给`ext4_encryption_context`的 nonce，其他如 master key descriptor、flags、文件内容加密模式、文件名加密模式等值，从`ext4_encryption_policy`中获取，完成目标目录对应的`ext4_encryption_context`的初始化
  * `ext4_xattr_set()`将用于目标目录的`ext4_encryption_context`保存到 inode 的 xattr
  * `ext4_set_inode_flag()`将目标目录对应 inode 的 i_flags 设置成 `EXT4_INODE_ENCRYPT`，表明其属性。后续在文件open、read、write 时通过该标志进行判断

最后使用`ext4_journal_start`、`ext4_mark_inode_dirty`、`ext4_journal_stop`等函数完成
xattr 数据回写到磁盘的请求。

若非首次对目标目录进行 EXT4 Encryption 设置，请流程如图四所示，通过 ext4_xattr_get 函数读取对应 inode 的 xattr
的EXT4 Encryption字段”c”对应的内容，即保存的
`ext4_encryption_context`，将其与`ext4_encryption_policy`的相应值进行对比，若不一致返回-EINVAL。

![](https://images.seebug.org/content/images/2017/10/ca0cf2b0-dd66-4cd2-a2a8-dabe0531052d.png-w331s)
图四 非首次进行EXT4 Encryption设置的函数调用关系

相比 eCryptfs，此`EXT4_IOC_SET_ENCRYPTION_POLICY`的 ioctl 的作用类似 eCryptfs 的“mount –t
ecryptfs ”操作。

##### creat file 流程

creat file 流程特指应用程序通过 `creat()`函数或 `open( , O_CREAT,
)`在已经通过`EXT4_IOC_SET_ENCRYPTION_POLICY ioctl`完成 EXT4 Encryption
设置的目录下新建普通文件的过程。希望通过介绍该过程，可以帮助读者了解如何创建加密文件，如何利用 master key 和 nonce 生成 derived
key。

应用程序使用`creat()`函数通过系统调用经由VFS，在申请到fd、初始化好 nameidata 、struct file
等等之后利用`ext4_create()`函数完成加密文件的创建，函数调用关系如图五所示。

创建加密文件的核心函数`ext4_create()`的函数调用关系如图六所示，函数主要功能是创建 ext4 inode 节点并初始化，这里只关注 EXT4
Encryption 部分。在创建时首先判断其所在目录 inode 的 i_flags
是否已经被设置了`EXT4_INODE_ENCRYPT`属性（该属性在`EXT4_IOC_SET_ENCRYPTION_POLICY ioctl`或者在
EXT4 Encryption 根目录下的任何地方新建目录/文件时完成i_flags设置），若是则表明需要进行 EXT4
Encryption；接着读取新文件所在目录，即其父目录的 xattr 属性获取到`ext4_encryption_context`，再为新文件生成新的
nonce，将 nonce 替换父目录的`ext4_encryption_context`中的 nonce
生成用于新文件的`ext4_encryption_context`并保存到新文件对应 inode 的 xattr
中；然后用`ext4_encryption_context`中的 master key descriptor 匹配到 keyring 中的 master
key，将`ext4_encryption_context`中的nonce做为密钥对 master key 进行 AES-128-ECB 加密，得到
derived key；最后使用 derived key 和 AES-256-XTS 初始化 kernel crypto API，将初始化好的 tfm
保存到 `ext4_crypt_info` 的ci_ctfm
成员中，再将`ext4_crypt_info`保存到`ext4_inode_info`的`i_crypt_info`，后续对新文件进行读写操作时直接取出
ci_ctfm 做具体的加/解密即可。

![](https://images.seebug.org/content/images/2017/10/c54a0968-3445-4327-b667-8722a71d68f6.png-w331s)
图五 creat 和 open file 函数调用关系

![](https://images.seebug.org/content/images/2017/10/f75862c9-37e3-482f-b352-e5621fdd5cc9.png-w331s)
图六 ext4_create函数调用关系

具体到图六中`ext4_create`函数调用关系中各个要点函数，完成的功能如下：

  * `ext4_encrypted_inode()`判断文件父目录的 inode 的 i_flags 是否已经被设置了`EXT4_INODE_ENCRYPT`属性
  * `ext4_get_encryption_info()`读取父目录的 xattr 属性获取到`ext4_encryption_context`，并为父目录生成 derived key，初始化好 tfm 并保存到其`ext4_inode_info的i_crypt_info`
  * `ext4_encryption_info()`确认父目录的`ext4_inode_info`的`i_crypt_info`已经初始化好
  * `ext4_inherit_context()`为新文件创建`ext4_encryption_context`并保存到其 xattr 中，并为新文件生成 derived key，初始化好 tfm 并保存到其`ext4_inode_info`的`i_crypt_info`

从上可看到`ext4_get_encryption_info()`和`ext4_inherit_context()`是最关键的部分，其代码如清单八和清单九所示，代码较长，但强烈建议耐心读完。

###### 清单八 ext4_get_encryption_info 函数

    
    
    int ext4_get_encryption_info(struct inode *inode)
    {
        struct ext4_inode_info *ei = EXT4_I(inode);
        struct ext4_crypt_info *crypt_info;
        char full_key_descriptor[EXT4_KEY_DESC_PREFIX_SIZE +
                     (EXT4_KEY_DESCRIPTOR_SIZE * 2) + 1];
        struct key *keyring_key = NULL;
        struct ext4_encryption_key *master_key;
        struct ext4_encryption_context ctx;
        const struct user_key_payload *ukp;
        struct ext4_sb_info *sbi = EXT4_SB(inode->i_sb); 
        struct crypto_ablkcipher *ctfm;
        const char *cipher_str;
        char raw_key[EXT4_MAX_KEY_SIZE];
        char mode;
        int res;
        //若ext4_inode_info中的i_crypt_info有值，说明先前已经初始化好
        if (ei->i_crypt_info)
            return 0;
        if (!ext4_read_workqueue) {
        /*为readpage时解密初始化read_workqueue，为ext4_crypto_ctx预先创建128个
        *cache，为writepage时用的bounce page创建内存池，为ext4_crypt_info创建slab
        */
            res = ext4_init_crypto();
            if (res)
                return res;
        }
        /*从xattr中读取加密模式、master key descriptor、nonce等加密相关信息到
        *ext4_encryption_context
        */
        res = ext4_xattr_get(inode, EXT4_XATTR_INDEX_ENCRYPTION,
                     EXT4_XATTR_NAME_ENCRYPTION_CONTEXT,
                     &ctx, sizeof(ctx));
        if (res < 0) {
            if (!DUMMY_ENCRYPTION_ENABLED(sbi))
                return res;
            ctx.contents_encryption_mode = EXT4_ENCRYPTION_MODE_AES_256_XTS;
            ctx.filenames_encryption_mode =
                EXT4_ENCRYPTION_MODE_AES_256_CTS;
            ctx.flags = 0;
        } else if (res != sizeof(ctx))
            return -EINVAL;
        res = 0;
        crypt_info = kmem_cache_alloc(ext4_crypt_info_cachep, GFP_KERNEL);
        if (!crypt_info)
            return -ENOMEM;
        //根据获取到的ext4_encryption_context内容初始化ext4_crypt_info
        crypt_info->ci_flags = ctx.flags;
        crypt_info->ci_data_mode = ctx.contents_encryption_mode;
        crypt_info->ci_filename_mode = ctx.filenames_encryption_mode;
        crypt_info->ci_ctfm = NULL;
        memcpy(crypt_info->ci_master_key, ctx.master_key_descriptor,
               sizeof(crypt_info->ci_master_key));
        if (S_ISREG(inode->i_mode))
            mode = crypt_info->ci_data_mode;
        else if (S_ISDIR(inode->i_mode) || S_ISLNK(inode->i_mode))
            mode = crypt_info->ci_filename_mode;
        else
            BUG();
    
        switch (mode) {
        case EXT4_ENCRYPTION_MODE_AES_256_XTS:
            cipher_str = "xts(aes)";
            break;
        case EXT4_ENCRYPTION_MODE_AES_256_CTS:
            cipher_str = "cts(cbc(aes))";
            break;
        default:
            printk_once(KERN_WARNING
                    "ext4: unsupported key mode %d (ino %u)\n",
                    mode, (unsigned) inode->i_ino);
            res = -ENOKEY;
            goto out;
        }
        if (DUMMY_ENCRYPTION_ENABLED(sbi)) {
            memset(raw_key, 0x42, EXT4_AES_256_XTS_KEY_SIZE);
            goto got_key;
        }
        //实际使用时将master key descriptor加上”ext4:”的前缀用于匹配master key
        memcpy(full_key_descriptor, EXT4_KEY_DESC_PREFIX,
               EXT4_KEY_DESC_PREFIX_SIZE);
        sprintf(full_key_descriptor + EXT4_KEY_DESC_PREFIX_SIZE,
            "%*phN", EXT4_KEY_DESCRIPTOR_SIZE,
            ctx.master_key_descriptor);
        full_key_descriptor[EXT4_KEY_DESC_PREFIX_SIZE +
                    (2 * EXT4_KEY_DESCRIPTOR_SIZE)] = '\0';
        //使用master key descriptor为匹配条件向keyring申请master key
        keyring_key = request_key(&key_type_logon, full_key_descriptor, NULL);
        if (IS_ERR(keyring_key)) {
            res = PTR_ERR(keyring_key);
            keyring_key = NULL;
            goto out;
        }
    
        //确保master key的type是logon类型，防止应用程序读取到key的内容
        if (keyring_key->type != &key_type_logon) {
            printk_once(KERN_WARNING
                    "ext4: key type must be logon\n");
            res = -ENOKEY;
            goto out;
        }
        down_read(&keyring_key->sem);
        //从keyring中取出master key的payload
        ukp = user_key_payload(keyring_key);
        if (ukp->datalen != sizeof(struct ext4_encryption_key)) {
            res = -EINVAL;
            up_read(&keyring_key->sem);
            goto out;
        }
        //取出master key的有效数据ext4_encryption_key
        master_key = (struct ext4_encryption_key *)ukp->data;
        BUILD_BUG_ON(EXT4_AES_128_ECB_KEY_SIZE !=
                 EXT4_KEY_DERIVATION_NONCE_SIZE);
        if (master_key->size != EXT4_AES_256_XTS_KEY_SIZE) {
            printk_once(KERN_WARNING
                    "ext4: key size incorrect: %d\n",
                    master_key->size);
            res = -ENOKEY;
            up_read(&keyring_key->sem);
            goto out;
        }
        /*以nonce做为密钥，采用AES_128_ECB算法，利用kernel crypto API加密master
        * key（master_key->raw），生成derived key保存在raw_key里
        */
        res = ext4_derive_key_aes(ctx.nonce, master_key->raw,
                      raw_key);
        up_read(&keyring_key->sem);
        if (res)
            goto out;
    got_key:
        //为AES_256_XTS加密算法申请tfm
        ctfm = crypto_alloc_ablkcipher(cipher_str, 0, 0);
        if (!ctfm || IS_ERR(ctfm)) {
            res = ctfm ? PTR_ERR(ctfm) : -ENOMEM;
            printk(KERN_DEBUG
                   "%s: error %d (inode %u) allocating crypto tfm\n",
                   __func__, res, (unsigned) inode->i_ino);
            goto out;
        }
        crypt_info->ci_ctfm = ctfm;
        crypto_ablkcipher_clear_flags(ctfm, ~0);
        crypto_tfm_set_flags(crypto_ablkcipher_tfm(ctfm),
                     CRYPTO_TFM_REQ_WEAK_KEY);
        //向kernel crypto接口里设置加密用的key为derived key
        res = crypto_ablkcipher_setkey(ctfm, raw_key,
                           ext4_encryption_key_size(mode));
        if (res)
            goto out;
        /*将初始化好的ext4_crypt_info 实例crypt_info拷贝到inode的ext4_inode_info 的*i_crypt_info。
        *后续加/解密文件内容时直接取出ext4_inode_info的i_crypt_info，即可从中获取
        *到已经初始化好的tfm接口c_ctfm，用其直接加/解密
        */
        if (cmpxchg(&ei->i_crypt_info, NULL, crypt_info) == NULL)
            crypt_info = NULL;
    out:
        if (res == -ENOKEY)
            res = 0;
        key_put(keyring_key);
        ext4_free_crypt_info(crypt_info);
        memzero_explicit(raw_key, sizeof(raw_key));
        return res;
    }
    `

###### 清单九 ext4_inherit_context 函数

    
    
    int ext4_inherit_context(struct inode *parent, struct inode *child)
    {
        struct ext4_encryption_context ctx;
        struct ext4_crypt_info *ci;
        int res;
        //确保其父目录inode对应的i_crypt_info已经初始化好
        res = ext4_get_encryption_info(parent);
        if (res < 0)
            return res;
        //获取父目录的保存在i_crypt_info的ext4_crypt_info信息
        ci = EXT4_I(parent)->i_crypt_info;
        if (ci == NULL)
            return -ENOKEY;
        ctx.format = EXT4_ENCRYPTION_CONTEXT_FORMAT_V1;
        if (DUMMY_ENCRYPTION_ENABLED(EXT4_SB(parent->i_sb))) {
            ctx.contents_encryption_mode = EXT4_ENCRYPTION_MODE_AES_256_XTS;
            ctx.filenames_encryption_mode =
                EXT4_ENCRYPTION_MODE_AES_256_CTS;
            ctx.flags = 0;
            memset(ctx.master_key_descriptor, 0x42,
                   EXT4_KEY_DESCRIPTOR_SIZE);
            res = 0;
        } else {
        /*使用父目录的文件内容加密模式、文件名加密模式、master key descriptor、flags
        *初始化新文件的ext4_encryption_context
        */
            ctx.contents_encryption_mode = ci->ci_data_mode;
            ctx.filenames_encryption_mode = ci->ci_filename_mode;
            ctx.flags = ci->ci_flags;
            memcpy(ctx.master_key_descriptor, ci->ci_master_key,
                   EXT4_KEY_DESCRIPTOR_SIZE);
        }
        //产生16 bytes的随机数做为新文件的nonce
        get_random_bytes(ctx.nonce, EXT4_KEY_DERIVATION_NONCE_SIZE);
    
        //将初始化好的新文件的ext4_encryption_context保存到attr中
        res = ext4_xattr_set(child, EXT4_XATTR_INDEX_ENCRYPTION,
                     EXT4_XATTR_NAME_ENCRYPTION_CONTEXT, &ctx,
                     sizeof(ctx), 0);
        if (!res) {
            //设置新文件的inode的i_flags为EXT4_INODE_ENCRYPT
            ext4_set_inode_flag(child, EXT4_INODE_ENCRYPT);
            ext4_clear_inode_state(child, EXT4_STATE_MAY_INLINE_DATA);
            /*为新文件初始化好其inode对应的i_crypt_info，主要是完成其tfm的初始化
            *为后续的读写文件时调用kernel crypto进行加/解密做好准备
            */
            res = ext4_get_encryption_info(child);
        }
        return res;
    }
    `

简单的说，creat 时完成两件事：一是创建`ext4_encryption_context`保存到文件的
xattr；二是初始化好`ext4_crypt_info` 保存到 inode 的 `i_crypt_info`，后续使用时取出 tfm，利用 kernel
crypto API 即完成了加/解密工作。

##### open file 流程

这里 open file 特指打开已存在的 EXT4 Encryption 加密文件。仅加密部分而言，该过程相比 creat
少了创建`ext4_encryption_context`保存到文件的 xattr
的操作，其余部分基本一致。从应用程序调用`open()`函数开始到最终调用到`ext4_file_open()`函数的函数调用关系如上图五所示。本节主要描述`ext4_file_open()`函数，其函数调用关系如图七。

![](https://images.seebug.org/content/images/2017/10/8b376669-5cde-4195-8a75-bf426c70efb0.png-w331s)
图七 ext4_file_open函数调用关系

图七所示各函数主要完成的功能如下：

  * `ext4_encrypted_inode()` 判断欲打开文件对应 inode 的 i_flags 是否设置成`EXT4_INODE_ENCRYPT`，若是，表明是加密文件
  * `ext4_get_encryption_info()` 从文件 inode 的 xattr 取出文件加密算法、文件名加密算法、master key descriptor、 随机密钥 nonce；之后生成加密文件内容使用的密钥 derived key 并初始化好 kernel crypto 接口 tfm，将其以`ext4_crypt_info` 形式保存到 inode 的`i_crypt_info`。详细代码见清单八
  * `ext4_encryption_info()`确保文件对应inode在内存中的表示`ext4_inode_info`中的`i_crypt_info`已经做好初始化
  * `ext4_encrypted_inode(dir)`判断判断欲打开文件的父目录inode的i_flags是否设置成`EXT4_INODE_ENCRYPT`
  * `ext4_is_child_context_consistent_with_parent()`判断文件和其父目录的加密 context 是否一致，关键是 master key descriptor 是否一致
  * `dquost_file_open()` 调用通用的文件打开函数完成其余的操作

简单的说就是在 open file 的时候完成文件加/解密所需的所有 context。

##### read file 流程

加密文件的解密工作主要是在 read 的时候进行。正常的 Linux read 支持 Buffered I/O 和 Direct I/O
两种模式，Buffered I/O利用内核的 page cache 机制，而 Direct I/O 需要应用程序自身准备和处理cache，当前版本的
EXT4 Encryption 不支持Direct I/O，其文件内容解密工作都在 page cache 中完成。自应用程序发起 read 操作到
kernel 对文件内容进行解密的函数调用关系如图八所示。

![](https://images.seebug.org/content/images/2017/10/3da4eb81-e016-4926-8fed-fa86c0afcda3.png-w331s) 图八 read 加密文件的函数调用关系

ext4 文件读的主要实现在 ext4_readpage 函数，文件内容的 AES-256-XTS
解密理所当然也在该函数里，这里主要介绍文件内容解密部分，其函数调用关系如图九所示。ext4 读写通过bio进行封装，描述块数据传送时怎样进行填充或读取块给
driver，包括描述磁盘和内存的位置，其内部有一个函数指针bi_end_io，当读取完成时会回调该函数，如图九所示，ext4 将 bi_end_io
赋值为`mpage_end_io`。`mpage_end_io`通过 queue_work 的形式调用 completion_pages
函数，在该函数中再调用 ext4_decrypt
函数完成page的解密。`ext4_decrypt`函数的代码非常简单，如清单十所示。核心的加密和解密函数都在`ext4_page_crypto()`中完成，因为在open
file的时候已经初始化好了 kernel crypto
接口，所以这里主要传入表明是加密还是解密的参数以及密文页和明文页地址，代码比较简单，如清单十一所示。

![](https://images.seebug.org/content/images/2017/10/d6a85c31-65d4-4e69-a1f1-ac1e18581dc5.png-w331s)
图九 ext4_readpage函数调用关系

###### 清单十 ext4_decrypt 函数

    
    
    int ext4_decrypt(struct page *page)
    {
        BUG_ON(!PageLocked(page));
        return ext4_page_crypto(page->mapping->host, EXT4_DECRYPT,
                    page->index, page, page, GFP_NOFS);
    }
    `

###### 清单十一 ext4_page_crypto 函数

    
    
    static int ext4_page_crypto(struct inode *inode, ext4_direction_t rw, pgoff_t index, struct page *src_page,
                    struct page *dest_page, gfp_t gfp_flags) {
        u8 xts_tweak[EXT4_XTS_TWEAK_SIZE];
        struct ablkcipher_request *req = NULL;
        DECLARE_EXT4_COMPLETION_RESULT(ecr);
        struct scatterlist dst, src;
        struct ext4_crypt_info *ci = EXT4_I(inode)->i_crypt_info;
        struct crypto_ablkcipher *tfm = ci->ci_ctfm; //取出open时初始化好的tfm
        int res = 0;
        req = ablkcipher_request_alloc(tfm, gfp_flags);
        if (!req) {
            printk_ratelimited(KERN_ERR "%s: crypto_request_alloc() failed\n", __func__);
            return -ENOMEM;
        }
        ablkcipher_request_set_callback(
            req, CRYPTO_TFM_REQ_MAY_BACKLOG | CRYPTO_TFM_REQ_MAY_SLEEP,
            ext4_crypt_complete, &ecr);
        BUILD_BUG_ON(EXT4_XTS_TWEAK_SIZE < sizeof(index));
        memcpy(xts_tweak, &index, sizeof(index));
        memset(&xts_tweak[sizeof(index)], 0, EXT4_XTS_TWEAK_SIZE - sizeof(index));
        sg_init_table(&dst, 1);
        sg_set_page(&dst, dest_page, PAGE_CACHE_SIZE, 0);
        sg_init_table(&src, 1);
        sg_set_page(&src, src_page, PAGE_CACHE_SIZE, 0);
        ablkcipher_request_set_crypt(req, &src, &dst, PAGE_CACHE_SIZE, xts_tweak);
        if (rw == EXT4_DECRYPT)
            res = crypto_ablkcipher_decrypt(req);
        else
            res = crypto_ablkcipher_encrypt(req);
        if (res == -EINPROGRESS || res == -EBUSY) {
            wait_for_completion(&ecr.completion);
            res = ecr.res;
        }
        ablkcipher_request_free(req);
        if (res) {
            printk_ratelimited( KERN_ERR "%s: crypto_ablkcipher_encrypt() returned %d\n", __func__, res);
            return res;
        }
        return 0;
    }
    `

##### write file 流程

在写入文件的时候会首先将 page cache 中的文件明文内容进行 AES-256-XTS
加密，再通过bio写入磁盘，该工作主要在`ext4_writepage()`函数中完成，这里主要关注 EXT4 Encryption
部分，其函数调用关系如图十所示。

![](https://images.seebug.org/content/images/2017/10/ce63bd3d-d53b-4170-8f1d-108492a636a1.png-w331s)
图十 ext4_writepage函数调用关系

图十中，首先照例通过`ext4_encrypted_inode()`函数利用 i_flags 是否等于 `EXT4_INODE_ENCRYPT`
来判断是否是加密文件；然后使用 `ext4_encrypt()`
函数申请新的内存页用于保存密文，完成内容的加密，具体代码见清单十二，函数返回密文页的地址保存在data_page变量；紧着通过`io_submit_add_bh()`封装写入
buffer 页到磁盘的请求，这里通过判断 data_page
页是否空来决定是写入明文页还是密文页，巧妙的兼容了加密和非加密两种模式；最后通过`ext4_io_submit()`提交 bio 写盘请求。

###### 清单十二 ext4_encrypt 函数

    
    
    struct page *ext4_encrypt(struct inode *inode,
                  struct page *plaintext_page,
                  gfp_t gfp_flags)
    {
        struct ext4_crypto_ctx *ctx;
        struct page *ciphertext_page = NULL;
        int err;
        BUG_ON(!PageLocked(plaintext_page));
        //从cache中获取一个ext4_crypto_ctx内存空间
        ctx = ext4_get_crypto_ctx(inode, gfp_flags);
        if (IS_ERR(ctx))
            return (struct page *) ctx;
        //从内存池中申请一个内存页，命名为bounce page，用于保存密文内容，同时将
        //ext4_crypto_ctx的w.bounce_page指向该bounce page
        /* The encryption operation will require a bounce page. */
        ciphertext_page = alloc_bounce_page(ctx, gfp_flags);
        if (IS_ERR(ciphertext_page))
            goto errout;
        ctx->w.control_page = plaintext_page;
        //调用kernel crypto加密，将密文保存在bounce page
        err = ext4_page_crypto(inode, EXT4_ENCRYPT, plaintext_page->index,
                       plaintext_page, ciphertext_page, gfp_flags);
        if (err) {
            ciphertext_page = ERR_PTR(err);
        errout:
            ext4_release_crypto_ctx(ctx);
            return ciphertext_page;
        }
        SetPagePrivate(ciphertext_page);
        set_page_private(ciphertext_page, (unsigned long)ctx);
        lock_page(ciphertext_page);
        //返回密文页bounce page地址
        return ciphertext_page;
    }
    `

因为在 open file 的时候已经初始化好了 kernel crypto 所需的加密算法、密钥设置，并保存了 tfm 到文件 inode
的内存表示`ext4_inode_info`的成员 `i_crypt_info` 中，所以在 readpage/writepage
时进行加/解密的操作变得很简单。

#### 结语

与eCryptfs类似，EXT4 Encryption建立在内核安全可信的基础上，核心安全组件是master key，若内核被攻破导致密钥泄露，EXT4
Encryption的安全性将失效。同样需要注意page cache中的明文页有可能被交换到磁盘的swap区。早期版本的Chrome
OS禁用了swap功能，当前版本的swap采取的是zram机制，与传统的磁盘swap有本质区别。相比eCryptfs做为一个独立的内核加密模块，现在EXT4
Encryption原生的存在于EXT4文件系统中，在使用的便利性和性能上都优于eCryptfs，相信推广将会变得更加迅速。

#### 参考资料

  * [Linux kernel-V4.4.79 sourcecode](https://chromium.googlesource.com/chromiumos/third_party/kernel/+/v4.4.79 "Linux kernel-V4.4.79 sourcecode")
  * [Chromium OS platform-9653 sourcecode](https://chromium.googlesource.com/chromiumos/ "Chromium OS platform-9653 sourcecode")

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/433/>

