大家好，我是观宇战队的kenant，今天继续为大家分享恶意文件分析系列文章，第三篇我们通过一个案例使用静态分析的方法对SafeSound勒索病毒的捆绑、释放运行、持久化、反沙箱等代码进行分析，并根据加密流程给出相应的解密方法。

## 一、勒索病毒简介

勒索病毒性质恶劣、危害极大，一旦感染主机将给用户带来无法估量的损失。勒索病毒利用各种加密算法对文件进行加密，被感染主机一般很难解密，必须拿到解密密钥才有可能破解。因此，对勒索病毒进行二进制分析并成功解密被加密文件具有十分重要的意义。本文主要通过静态分析的方法对SafeSound勒索病毒的捆绑、释放运行、持久化、反沙箱等代码进行分析，同时在最后分析了病毒的加密流程并给出了相应的解密方法。读者可结合本文了解勒索病毒的部分特征，提升自身对勒索病毒的防范以及应急处置能力。

## 二、勒索病毒工作原理

通常勒索病毒以邮件、程序木马、网页挂马的形式进行传播，但也存在部分病毒利用主机漏洞，以蠕虫的方式进行传播，其中WannaCry为一种较典型的以蠕虫方式进行传播的勒索病毒。

通常，勒索病毒感染一台主机的工作原理如下图所示：

![image](https://image.3001.net/images/20230510/1683702636_645b436c83d8c387c68c5.png!small)

通过文字概括如下：

  1. 病毒通过主机漏洞、捆绑木马、网页挂马或邮件钓鱼的方式诱导用户执行木马文件。

  2. 病毒执行并设定触发条件（如部分病毒仅针对特定语言的用户进行攻击）。

  3. 满足条件时生成随机对称密钥对主机文件进行加密，加密的文件主要包括数据库文件、文档或其他可能存储重要信息的文件，对系统文件及特定格式的文件，通常不会采取加密措施，否则系统可能无法正常运行。

  4. 由于有解密需要，攻击者通常会使用公钥将对称密钥进行加密存储，这样仅攻击者用对应的私钥可以解密密钥从而进一步解密文件，如果攻击者为每个受害者使用不同公私钥的话，攻击者也会为受害者生成唯一的ID以便识别该受害者，可以通过主机名、MAC地址等方式进行标识。

  5. 攻击者开发并传播勒索病毒的主要目的是获取利益，通常以比特币等匿名方式进行支付，但不保证支付赎金后攻击者一定会将所有文件进行解密，这依赖于攻击者的信誉。

  6. 攻击者通常不会无限制的进行等待，由于解密的密钥长度有限，可以通过遍历密钥的方式进行暴力破解，因此通常会设定赎金的期限，也可能会出现间隔时间越长赎金越多的赎回机制使受害者尽快支付赎金。

  7. 攻击者通常会使用一定方式反制对勒索病毒的分析，可能包括：运行完加密程序后删除自身，仅保留勒索信以及解密程序等方式。

## 三、勒索病毒实例分析

### 3.1 背景介绍

近期在某次应急响应中，发现某主机中了SafeSound勒索病毒，主机中大部分文件被加密，后缀为.safesound，对主机中发现的勒索病毒文件进行分析，从勒索病毒的逆向分析中发现其解密方式，进行解密、恢复数据并输出相应的应急报告。

### 3.2 程序运行分析

该勒索病毒通过捆绑的方式，捆绑于其他软件中进行释放运行，因此需要从被捆绑的软件中识别并分离出病毒主体，再进一步对病毒主体进行分析。通过分析，发现该病毒主要分为四个部分，包括被捆绑软件、safesound_son.exe、safesound.dll以及Antidote.exe，下面对这几个部分分别进行分析并寻求对加密文件进行解密的方法。

#### 3.2.1 捆绑软件分析

首先对捆绑软件进行了一个简单的静态分析，由于是捆绑软件，一开始未对程序的代码段进行分析，主要关注字符串及资源中是否有疑似被进一步被释放的二进制程序的相关信息。由于被加密的后缀为.safesound，因此直接搜索该字符串，发现以下信息：

  1. SafeSound.dll、SafeSound_son.exe文件可能被释放创建并运行。

  2. net start SafeSound暗示我们该程序可能通过服务的方式进行持久化驻留。

  3. SOFTWARE\Microsoft\Windows NT\CurrentVersion\Svchost\SafeSound暗示该程序可能通过Svchost调用服务。  
![image](https://image.3001.net/images/20230510/1683702696_645b43a88b2e59de12dbe.png!small)  
然后根据发现的信息，进行引用查询，发现该程序代码段仅存在对SafeSound_son.exe的四处引用，四处引用均位于同一函数中，可以合理猜测该函数对SafeSound_son.exe进行释放并运行，下面对该函数进行静态分析。

进入该函数后，可以发现该函数中存在一个写文件的函数，同时该函数引用了.data段中的地址。

![image](https://image.3001.net/images/20230510/1683702847_645b443f772ab55203e00.png!small)

进入该地址空间，可以发现该地址中的内容为PE文件，包含有MZ头等PE文件特征，其写入的路径由BlackMoonCalleLibFunctionHelper决定，通过跟进，发现其通过该函数调用了SHGetSpecialFolderPathA函数，该函数通过CSIDL返回指定的文件夹路径，本例中，SHGetSpecialFolderPathA的CSIDL被设置为5，经查询为CSIDL_PERSONAL，为我的文档文件夹，通常为：C:\Documents
and Settings\username\My Documents。

之后通过地址0x4A00A0的函数创建一个进程启动该可执行程序，然后设置该程序为隐藏的系统文件，之后该函数结束。

通过以上分析，已经确定了该文件的内容，可以通过.data节内容导出生成该程序，也可以通过动态分析确定该文件路径，通过动态分析发现该程序确实位于我的文档的目录下，属性为隐藏的系统文件。

![image](https://image.3001.net/images/20230510/1683702861_645b444d01d0b4496dd10.png!small)

#### 3.2.2 SafeSound_son.exe程序分析

由于在前述的分析过程中，我们看到了SafeSound.dll文件名，但未在捆绑软件中发现该字符串的引用，通过动态分析亦未看到捆绑软件释放该程序。但运行后通过注册表的监控，却发现存在该dll文件被释放，进一步分析发现该字符串位于safesound_son.exe程序空间中，猜想该dll程序是由SafeSound_son.exe程序释放。

我们通过字符串引用定位该程序释放该dll的函数进行进一步分析：

![image](https://image.3001.net/images/20230510/1683702874_645b445a0615c03957f33.png!small)

很容易定位到sub_4010DF函数，然后对该函数进行分析。

前面部分与之前分析的释放exe文件的函数类似，将0x0040520E处的DLL文件内容释放出来，并设置隐藏以及系统文件属性。不同之处在于动态链接库与程序不同，程序通过进程运行即可，动态链接库需要加载并查找其导出函数地址进行执行才能完成其功能。该函数通过LoadLibrary以及GetPorcAddress函数获取了InsertSvc以及UninstallSvc两个函数的地址。然后调用insertsvc将该dll安装为服务，同时通过进程执行命令net
start SafeSound启动该服务。该函数还对注册表进行了更改，将该服务设置为通过svchost进行调用。

![image](https://image.3001.net/images/20230510/1683702888_645b4468cdaf2d73cce3b.png!small)

#### 3.2.3 SafeSound.dll分析

接下来继续对该dll进行分析，由于该dll以服务形式安装在系统中，我们可以对该dll的导出函数进行分析，尤其是对InsertSvc函数，因为在之前的SafeSound_son.exe程序中调用了这个函数。

但同时我们也可以从另一个角度来进行分析，通过字符串查找来定位我们需要分析的内容，通过字符串查找，发现以下的一些字符串，通过第三个字符串以及第四个字符串，我们可以相信这个dll程序还会输出一个PE文件。

![image](https://image.3001.net/images/20230510/1683702926_645b448e06b93427d5d29.png!small)

通过查找引用，我们可以发现其中的三个字符串在地址为10001657的 **函数** 中引用，trigger字符串在地址10001108 **函数**
中引用，而 **函数** 10001108正好调用了 **函数**
10001657，通过一层层的引用进行追溯，可以发现该函数通过多层嵌套位于ServiceMain函数的调用链中，而该函数正是每个服务启动时都需要执行的函数。通过上述方式，我们成功定位到了需要分析的关键函数。而如果通过ServiceMain函数进行正向分析，可能需要花费大量的时间去跟进函数调用，要想从这个函数调用链中发现关键函数是相当具有挑战性且费时的事。

接下来我们根据这两个函数的调用关系，首先对10001108函数进行分析。

根据分析，10001108函数主要是获取临时目录，通过trigger文件存储当前时间3天后的时间，当系统时间与3天后的时间差小于一个阈值时，则执行10001657函数以及10004754函数。其中10004754函数与UninstallSvc函数（卸载该服务）内容一致，因此可以知道其主要工作内容在10001657函数中。  
![image](https://image.3001.net/images/20230510/1683702939_645b449bc02633d6bfab0.png!small)

然后对10001657函数进行分析。

该函数生成64个字节的随机数作为key，然后使用本地的信息将该key进行加密后存储于key.data文件中（如何加密后续通过单独的章节进行分析）。

后续使用FindFirstFileA以及FindNextFileA遍历文件，并通过递归的方式调用函数对所有范围内文件进行加密。然后使用PathFindExtensionA获取扩展名，后续通过白名单结合文件属性等方式判断该文件是否需要进行加密。

白名单后缀包括：

    
    
    .bat .bin .com .cfg .client .dat .dll .exe .gif .icon .ico .ini .info .json .jar .class .flv .krc .lnk .lib .log .lrc .pak .tmp .xml .ocx .obj .swf .sf .sh .sys .rc .rll .rom .rsa .rtf .rs .SafeSound
    

最后在加密完成后释放Antidote.exe程序并使用CreateProcessAsUserA函数运行该程序。

    
    
    v25 = CreateProcessAsUserA(phNewToken, *a1, *a2, 0, 0, 0, dwCreationFlags, Environment, lpCurrentDirectory, v42, v45);
    

Antidote.exe程序主要进行勒索信提示以及解密功能，这里不对其进行过多分析。

### 3.3 探索如何解密

由于我们前面分析中提到，其生成的加密密钥通过本地的信息进行加密后随加密密钥一同存入key.data中，因此理论上只要我们破解了其使用的加密算法以及key.data的文件格式，即可反向获取用于解密的密钥。

首先我们关注生成的随机数密钥通过何种方式被加密并存储到文件中。对密钥的加密函数地址位于0x10001E4E处，该函数接收key作为参数并进行加密操作。

首先GetTickCount以及gen_random_num函数返回的数据会按字节进行异或运算得到一个四字节的数据num_xor_tickcount。

![image](https://image.3001.net/images/20230510/1683702962_645b44b20c32f8e3dd72e.png!small)

然后将上述得到的num_xor_tickcount与.data段的进行key加密的key_key逐字节循环进行异或得到new_key_key。

![image](https://image.3001.net/images/20230510/1683702979_645b44c3d8885d4d77aa6.png!small)

然后将传入的参数key逐字节与上述的new_key_key每个字节再次进行0x63次异或，异或之后的字节再与tickcount对应字节进行一次异或，最终得到加密后的xor_key。

然后将前面生成的随机数取反并再次与num_xor_tickcount进行异或得到not_Num_xor。

    
    
    not_Num_xor = (void *)xor_func(2, not_random_num, 0, 0x80000301, (_DWORD)tickcount, 0, 0x80000301);
    

最后将上述的not_Num_xor、num_xor_tickcount以及xor_key拼接后写入key.data中，如下图所示，1-4字节对应为not_Num_xor，5-8字节为num_xor_tickcount，9-72为xor_key。

![image](https://image.3001.net/images/20230510/1683703001_645b44d94cca5872ff27d.png!small)

根据上述分析，我们可以通过not_Num_xor与num_xor_tickcount异或得到not_num，然后取反即可得到当时生成的随机数，后续再通过使用num_xor_tickcount与random_num进行异或得到当时的tickcount，用于加密的数组位于.data节中可以直接获取，用于解密密钥的要素均可通过本地获得，因此可以实施解密操作，至此可以通过解密出密码后将密码输入Antidote中进行文件解密。

解密密钥的部分代码如下：

    
    
    def decrypt_key(encrypt_key):
        num_xor_tickcount = encrypt_key[4:8]
        new_key_key = [0]*0x63
        for i in range(0x63):
            new_key_key[i] = key_key[i] ^ num_xor_tickcount[(i%4)]
    
        randnum = (~(encrypt_key[0] ^ num_xor_tickcount[0])) & 0xff
        tickcount = [0]*4
    
        for i in range(4):
            tickcount[i] = num_xor_tickcount[i] ^ randnum
    
        xor_Key = encrypt_key[8:]
        key = [0]*0x40
        for i in range(0x40):
            key[i] = xor_Key[i] ^ tickcount[(i+3)%4]
            for j in range(0x63):
                key[i] = key[i] ^ new_key_key[j]
        return key
    

使用该解密算法对实例的key.data文件进行解密得到用于加密的key：

![image](https://image.3001.net/images/20230510/1683703072_645b45202d7cdfdb1d617.png!small)

为完成整个解密过程，还需要最后再确定用于加密文件的算法，由于我们前面定位到了查询文件的API函数调用，后续继续通过在该函数的调用过程中定位读文件以及写文件的API函数，进一步定位到以下代码。

通过逐层跟进定位到下面这段RC4代码初始化的过程，确定其通过RC4代码进行文件加密。

![image](https://image.3001.net/images/20230510/1683703091_645b45336a0e291b5da56.png!small)

根据对文件的分析，其存储数据时会将数据长度放在数据首部，文件中同样沿用了这种形式，因此可以通过文件头部的四字节读取数据长度，然后读取相应长度的加密数据，后续使用前面解密得到的key初始化RC4算法进行解密。

![image](https://image.3001.net/images/20230510/1683703104_645b45404c4d5e7d243c7.png!small)

解密示例：

如上图，被加密文件长度为5，加密路径为桌面的test1，被加密数据为\x78\x99\x6C\x6F\xB8，解密示例python代码如下：

    
    
    from Crypto.Cipher import ARC4 as rc4cipher
    import base64
    
    def rc4_algorithm(encrypt_or_decrypt, data, key1):
        if encrypt_or_decrypt == "encrypt":
            key = bytes(key1, encoding='utf-8')
            enc = rc4cipher.new(key)
            res = enc.encrypt(data.encode('utf-8'))
            return res
        elif encrypt_or_decrypt == "decrypt":
            key = bytes(key1, encoding='utf-8')
            enc = rc4cipher.new(key)
            res = enc.decrypt(data)
            res = str(res,'utf8')
            return res
    
    
    if __name__ == "__main__":
        data = b'\x78\x99\x6C\x6F\xB8'
        key = 'kxJZdIweJPczRM1JyrrzUh8YWb7YZDQHk693NiQH42SiKiK15ThtPrndR0PkCamA'
        print('被加密的明文为：')
        print(rc4_algorithm('decrypt', data, key))
    

运行截图：

![image](https://image.3001.net/images/20230510/1683703120_645b455085c80fef4fe47.png!small)

### 3.4 实例分析总结

通过动静态分析，最后我们确定该捆绑软件首先释放SafeSound_son.exe并运行来执行第一段恶意代码，SafeSound_son.exe程序再释放SafeSound.dll动态链接库，并通过LoadLibrary以及GetProcAddress函数调用该动态链接库的InsertSvc函数将其安装为服务并执行net
start
SafeSound命令启动该服务，该服务中的ServiceMain函数中根据当前的系统时间创建一个文件记录当前时间，并设定于当前时间后的3天触发加密程序，通过这样的方法可以实现反沙箱的功能。当时间满足特定条件时，服务进入加密流程，首先生成随机密钥并使用本地密钥对随机密钥进行加密后存储于文件中，后续进行本地磁盘搜索并进行文件加密，加密完成后释放safeSound.hash文件以及Antidote.exe文件，其中SafeSound.hash文件存储了加密过的文件清单，Antidote.exe文件则用于发布勒索界面及进行解密操作。由于其所有加密所需的密钥均可通过被感染主机本地获取，因此可以进行离线解密。最后可以通过编写逆向算法得到密钥成功解密被加密文件。

## 四、勒索病毒处置建议

针对本例勒索病毒，如果在文件被加密前发现勒索病毒，可通过删除safesound服务并删除捆绑软件、safesound_son.exe、safesound.dll文件使系统恢复正常，如文件已被加密，注意不要将Key.data文件删除，否则将可能无法恢复数据，通过key.data文件结合解密python代码可恢复原数据。勒索病毒是一种通过加密重要文件进行勒索获取利益的病毒，其危害性很高，因此建议存储有重要数据的主机定期进行异地备份，以便主机遭受攻击后可以通过备份恢复大部分文件。如果中勒索病毒主机内容未进行备份，建议联系勒索病毒处置专家进行分析及处置。

