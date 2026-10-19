# 前言

Raccoon Stealer v2是一款在地下黑客论坛售卖的信息窃取器，通过恶意软件即服务
(MaaS)模式运营，用户购买订阅后可轻松进行配置并进行分发传播，一般通过伪装的破解软件下载站进行传播。

# 样本运行流程图

![image](https://image.3001.net/images/20220915/1663230425_6322e1d9bbdc0d89c76d3.jpg!small)

# 样本IOCs

### hash

名称: PA$$w0rds_1234__SetupMain7--A4.rar  
大小: 6350190 字节 (6201 KiB)  
MD5: 916062da2e31a30e6f1ec0edc33dd4e9  
SHA1: b34300a38b0329ec9b3d303ddf670a3b6d154d6b  
SHA256: 1ce1ef40bf1a6edc429a326be3bccb9385d0dd4ccfb00c07972f64d232066b8a

名称: Setup.exe  
大小: 761512960 字节 (726 MiB)  
MD5: 7949b59a91d6c4b6bc005c7222d00829e  
SHA1: 8aa525197f8ad4f0a2c5f0a549ed5ff9334d331b

名称: Setup.exe（去除无用字节）  
大小: 6538240 字节 (6385 KiB)  
MD5: 657b3c0142ba7bea31c0618d38cb8a04  
SHA1: 73ee1fe9a79c48460fb5fa9d10a09338b9e48669  
SHA256: 7ff22cd1d3e1c8d7bf2628da60c905bd6bef4733b0d4e68e862e1598268d2481

名称: 36141266339446703039.bin  
大小: 2834432 字节 (2768 KiB)  
MD5: 24967c5d930081488e15e735d3d40d0c  
SHA1: 080e2d4f2065d326d8842e4ca9a02ed76e74f4d5  
SHA256: 1324ad52820961a29ef6aea13e5bb21d1bbd2169045abc61c711424f196d11f2

名称: RaccoonStealerV2  
大小: 56832 字节 (55 KiB)  
MD5: 0cfa58846e43dd67b6d9f29e97f6c53e  
SHA1: 19d9fbfd9b23d4bd435746a524443f1a962d42fa  
SHA256: 022432f770bf0e7c5260100fcde2ec7c49f68716751fd7d8b9e113bf06167e03

## url

### 恶意下载站

hxxps://licenseprokeys[.]com/  
hxxps://tradecracked[.]com/  
hxxps://fancracked[.]com/

### 通信URL

http[:]//94[.]131[.]106[.]116/  
hxxp://94[.]131[.]106[.]116/aN7jD0qO6kT5bK5bQ4eR8fE1xP7hL2vK/nss3[.]dll  
hxxp://94[.]131[.]106[.]116/aN7jD0qO6kT5bK5bQ4eR8fE1xP7hL2vK/msvcp140[.]dll  
hxxp://94[.]131[.]106[.]116/aN7jD0qO6kT5bK5bQ4eR8fE1xP7hL2vK/vcruntime140[.]dll  
hxxp://94[.]131[.]106[.]116/aN7jD0qO6kT5bK5bQ4eR8fE1xP7hL2vK/mozglue[.]dll  
hxxp://94[.]131[.]106[.]116/aN7jD0qO6kT5bK5bQ4eR8fE1xP7hL2vK/freebl3[.]dll  
hxxp://94[.]131[.]106[.]116/aN7jD0qO6kT5bK5bQ4eR8fE1xP7hL2vK/softokn3[.]dll  
hxxp://94[.]131[.]106[.]116/aN7jD0qO6kT5bK5bQ4eR8fE1xP7hL2vK/sqlite3[.]dll  
hxxp://94[.]131[.]106[.]116/3f9bef70525fd0873fc9acf8b6babce9  
hxxp://172[.]86[.]75[.]189//36141266339446703039[.]bin

# 恶意代码分析

### 传播途径

某天闲逛的时候搜索了一些关键词xxxx crack（搜索结果中基本都是用于传播恶意软件的网站）：  
![image](https://image.3001.net/images/20220915/1663230573_6322e26d2ed2758be9515.jpg!small)  
随手点进了第一个网站后：  
![image](https://image.3001.net/images/20220915/1663230628_6322e2a4823f686c1a521.jpg!small)  
下载链接点击下载链接下载：  
![image](https://image.3001.net/images/20220915/1663230647_6322e2b74d3c53bdcd03e.jpg!small)  
下载链接的跳转过程一共跳转了7次：

    
    
    0->hxxps://href[.]li/?hxxps://wqervf56kl[.]click/?i=PeStudio-Pro-9-43-Crack---License-Key-Free-Download-2022&u=1663076111&t=16
    1->hxxps://wqervf56kl[.]click/?i=PeStudio-Pro-9-43-Crack---License-Key-Free-Download-2022&u=1663076111&t=16
    2->hxxps://href[.]li/?hxxps://nhgfr7yh[.]click/Mt1JWxKprFcGNv67jDX0TqmUlgEL9s5/16/PeStudio-Pro-9-43-Crack---License-Key-Free-Download-2022
    3->hxxps://nhgfr7yh[.]click/Mt1JWxKprFcGNv67jDX0TqmUlgEL9s5/16/PeStudio-Pro-9-43-Crack---License-Key-Free-Download-2022
    4->hxxps://iplogger[.]org/Wersty-TM2poy-PASSw0rds_1234__SetupMain7--A4
    5->hxxps://www[.]mediafire[.]com/file/p99280jcivm6732/PA$$w0rds_1234__SetupMain7--A4.rar/file
    6->hxxps://download2338[.]mediafire[.]com/ixn681qdyafg/p99280jcivm6732/PA%24%24w0rds_1234__SetupMain7--A4.rar
    

其中查询可知href[.]li为一款的网站重定向小工具：  
![image](https://image.3001.net/images/20220915/1663230712_6322e2f8d98716c546696.jpg!small)  
跳转到nhgfr7yh[.]click页面给出了一个链接让我们复制并下载：  
![image](https://image.3001.net/images/20220915/1663230734_6322e30e06f1237726ca4.jpg!small)  
我们查看iplogger[.]org发现是一个短链接生成网站，并且此链接已经被拉入黑名单，但是下载链接还是可以正常下载：  
![image](https://image.3001.net/images/20220915/1663230777_6322e339abc5610dda04a.jpg!small)  
www[.]mediafire[.]com是一个文件存储和共享应用，并且无需注册就可以上传文件并分享：  
![image](https://image.3001.net/images/20220915/1663230797_6322e34d96b3bcee48090.jpg!small)  
我们查看下载的压缩包大小为6.05MB：  
![image](https://image.3001.net/images/20220915/1663230815_6322e35f1cb397ca91b8d.jpg!small)  
我们使用密码1234解压后，发现Setup.exe竟然足足有726MB大小，并且这个图标和应用名和我下载的软件也货不对板。  
![image](https://image.3001.net/images/20220915/1663230850_6322e382b288c3ea904b9.jpg!small)  
目前我认为还没有这么强大的压缩算法吧，那就只有一个原因这个PE文件肯定附加了很多重复的无意义字节，我们使用010Editor打开PE文件查看，果然PE文件尾部使用了大量的0x30填充，此技术主要是增大PE文件大小防止AV或EDR上传沙箱分析。  
![image](https://image.3001.net/images/20220915/1663230889_6322e3a95c47548080732.jpg!small)  
我们去除PE尾部的0x30后PE文件缩小为6.23 MB，此PE文件是使用Visual Studio 2019链接器版本14.29（ 1929
(versions 16.10 + 16.11)）编译的32位PE文件，使用了VMProtect 3.6.0加壳。  
![image](https://image.3001.net/images/20220915/1663230908_6322e3bcc1c268c086ccf.jpg!small)  
代码都被VM了，直接上传样本到沙箱分析：  
![image](https://image.3001.net/images/20220915/1663230933_6322e3d59a1646fdff7a3.jpg!small)

### 流量分析

上传沙箱分析后发现威胁情报标签显示此样本来自于Raccoon
Stealer家族，查看样本产生的流量特征和公开的威胁情报对比可以确定此样本应该是Raccoon Stealer v2。  
![image](https://image.3001.net/images/20220915/1663230968_6322e3f8bf88afc221c7e.jpg!small)  
首先第一个POST请求中使用的User-Agent为`mozzzzzzzzzzz`，发送的数据为`machineId=90059c37-1320-41a4-b5'8d-2b75a9850d2f|admin&configId=0dcbeb99ec1adc5c2b2b94dc1e3fd2c4`  
![image](https://image.3001.net/images/20220915/1663231008_6322e420a7848b89230c9.jpg!small)  
C2返回的数据中返回了明文配置文件，libs_开头的为要下载的dll，ews_开头的为浏览器扩展数据窃取配置，wlts_开头的为数字货币加密钱包数据窃取配置，xtntns_开头的为密码管理软件数据窃取配置，grbr_Desktop为要窃取的文件路径和文件类型，ldr_为下一阶段的payload。

    
    
    libs_nss3:hxxp://94[.]131[.]106[.]116/aN7jD0qO6kT5bK5bQ4eR8fE1xP7hL2vK/nss3.dll
    libs_msvcp140:hxxp://94[.]131[.]106[.]116/aN7jD0qO6kT5bK5bQ4eR8fE1xP7hL2vK/msvcp140.dll
    libs_vcruntime140:hxxp://94[.]131[.]106[.]116/aN7jD0qO6kT5bK5bQ4eR8fE1xP7hL2vK/vcruntime140.dll
    libs_mozglue:hxxp://94[.]131[.]106[.]116/aN7jD0qO6kT5bK5bQ4eR8fE1xP7hL2vK/mozglue.dll
    libs_freebl3:hxxp://94[.]131[.]106[.]116/aN7jD0qO6kT5bK5bQ4eR8fE1xP7hL2vK/freebl3.dll
    libs_softokn3:hxxp://94[.]131[.]106[.]116/aN7jD0qO6kT5bK5bQ4eR8fE1xP7hL2vK/softokn3.dll
    ews_meta_e:ejbalbakoplchlghecdalmeeeajnimhm;MetaMask;Local Extension Settings
    ews_tronl:ibnejdfjmmkpcnlpebklmnkoeoihofec;TronLink;Local Extension Settings
    libs_sqlite3:hxxp://94[.]131[.]106[.]116/aN7jD0qO6kT5bK5bQ4eR8fE1xP7hL2vK/sqlite3.dll
    ews_bsc:fhbohimaelbohpjbbldcngcnapndodjp;BinanceChain;Local Extension Settings
    ews_ronin:fnjhmkhhmkbjkkabndcnnogagogbneec;Ronin;Local Extension Settings
    wlts_exodus:Exodus;26;exodus;*;*partitio*,*cache*,*dictionar*
    wlts_atomic:Atomic;26;atomic;*;*cache*,*IndexedDB*
    wlts_jaxxl:JaxxLiberty;26;com.liberty.jaxx;*;*cache*
    wlts_binance:Binance;26;Binance;*app-store.*;-    wlts_coinomi:Coinomi;28;Coinomi\Coinomi\wallets;*;-    wlts_electrum:Electrum;26;Electrum\wallets;*;-    wlts_elecltc:Electrum-LTC;26;Electrum-LTC\wallets;*;-    wlts_elecbch:ElectronCash;26;ElectronCash\wallets;*;-    wlts_guarda:Guarda;26;Guarda;*;*cache*,*IndexedDB*
    wlts_green:BlockstreamGreen;28;Blockstream\Green;*;cache,gdk,*logs*
    wlts_ledger:Ledger Live;26;Ledger Live;*;*cache*,*dictionar*,*sqlite*
    ews_ronin_e:kjmoohlgokccodicjjfebfomlbljgfhk;Ronin;Local Extension Settings
    ews_meta:nkbihfbeogaeaoehlefnkodbefgpgknn;MetaMask;Local Extension Settings
    sstmnfo_System Info.txt:System Information: 
    |Installed applications:
    |
    wlts_daedalus:Daedalus;26;Daedalus Mainnet;*;log*,*cache,chain,dictionar*
    wlts_mymonero:MyMonero;26;MyMonero;*;*cache*
    wlts_xmr:Monero;5;Monero\\wallets;*.keys;-    wlts_wasabi:Wasabi;26;WalletWasabi\\Client;*;*tor*,*log*
    ews_metax:mcohilncbfahbmgdjkbpemcciiolgcge;MetaX;Local Extension Settings
    ews_xdefi:hmeobnfnfcmdkdcmlblgagmfpfboieaf;XDEFI;IndexedDB
    ews_waveskeeper:lpilbniiabackdjcionkobglmddfbcjo;WavesKeeper;Local Extension Settings
    ews_solflare:bhhhlbepdkbapadjdnnojkbgioiodbic;Solflare;Local Extension Settings
    ews_rabby:acmacodkjbdgmoleebolmdjonilkdbch;Rabby;Local Extension Settings
    ews_cyano:dkdedlpgdmmkkfjabffeganieamfklkm;CyanoWallet;Local Extension Settings
    ews_coinbase:hnfanknocfeofbddgcijnmhnfnkdnaad;Coinbase;IndexedDB
    ews_auromina:cnmamaachppnkjgnildpdmkaakejnhae;AuroWallet;Local Extension Settings
    ews_khc:hcflpincpppdclinealmandijcmnkbgn;KHC;Local Extension Settings
    ews_tezbox:mnfifefkajgofkcjkemidiaecocnkjeh;TezBox;Local Extension Settings
    ews_coin98:aeachknmefphepccionboohckonoeemg;Coin98;Local Extension Settings
    ews_temple:ookjlbkiijinhpmnjffcofjonbfbgaoc;Temple;Local Extension Settings
    ews_sollet:fhmfendgdocmcbmfikdcogofphimnkno;Sollet;Local Extension Settings
    ews_clover:nhnkbkgjikgcigadomkphalanndcapjk;CloverWallet;Local Extension Settings
    ews_polymesh:jojhfeoedkpkglbfimdfabpdfjaoolaf;PolymeshWallet;Local Extension Settings
    ews_neoline:cphhlgmgameodnhkjdmkpanlelnlohao;NeoLine;Local Extension Settings
    ews_keplr:dmkamcknogkgcdfhhbddcghachkejeap;Keplr;Local Extension Settings
    ews_terra_e:ajkhoeiiokighlmdnlakpjfoobnjinie;TerraStation;Local Extension Settings
    ews_terra:aiifbnbfobpmeekipheeijimdpnlpgpp;TerraStation;Local Extension Settings
    ews_liquality:kpfopkelmapcoipemfendmdcghnegimn;Liquality;Local Extension Settings
    ews_saturn:nkddgncdjgjfcddamfgcmfnlhccnimig;SaturnWallet;Local Extension Settings
    ews_guild:nanjmdknhkinifnkgdcggcfnhdaammmj;GuildWallet;Local Extension Settings
    ews_phantom:bfnaelmomeimhlpmgjnjophhpkkoljpa;Phantom;Local Extension Settings
    ews_tronlink:ibnejdfjmmkpcnlpebklmnkoeoihofec;TronLink;Local Extension Settings
    ews_brave:odbfpeeihdkbihmopkbjmoonfanlbfcl;Brave;Local Extension Settings
    ews_meta_e:ejbalbakoplchlghecdalmeeeajnimhm;MetaMask;Local Extension Settings
    ews_ronin_e:kjmoohlgokccodicjjfebfomlbljgfhk;Ronin;Local Extension Settings
    ews_mewcx:nlbmnnijcnlegkjjpcfjclmcfggfefdm;MEW_CX;Sync Extension Settings
    ews_ton:cgeeodpfagjceefieflmdfphplkenlfk;TON;Local Extension Settings
    ews_goby:jnkelfanjkeadonecabehalmbgpfodjm;Goby;Local Extension Settings
    ews_ton_ex:nphplpgoakhhjchkkhmiggakijnkhfnd;TON;Local Extension Settings
    ews_Cosmostation:fpkhgmpbidmiogeglndfbkegfdlnajnf;Cosmostation;Local Extension Settings
    ews_bitkeep:jiidiaalihmmhddjgbnbgdfflelocpak;BitKeep;Local Extension Settings
    ews_stargazer:pgiaagfkgcbnmiiolekcfmljdagdhlcm;Stargazer;Local Extension Settings
    ews_clv:nhnkbkgjikgcigadomkphalanndcapjk;CloverWallet;Local Extension Settings
    ews_jaxxlibertyext:cjelfplplebdjjenllpjcblmjkfcffne;JaxxLibertyExtension;Local Extension Settings
    ews_enkrypt:kkpllkodjeloidieedojogacfhpaihoh;Enkrypt;Local Extension Settings
    ews_gamestop:pkkjjapmlcncipeecdmlhaipahfdphkd;GameStop Wallet;Local Extension Settings
    ews_xds:aholpfdialjgjfhomihkjbmgjidlcdno;Exodus Web3 Wallet;Local Extension Settings
    xtntns_authenticatorcc:bhghoamapcdpbohphigoooaddinpkbai;Authenticator.cc;Sync Extension Settings
    xtntns_keepassxc_browser:oboonakemofpalcgghocfoadofidjkkk;KeePassXC Browser;Local Extension Settings
    xtntns_keepassTusk:fmhmiaejopepamlcjkncpgpdjichnecm;KeePass Tusk;Local Extension Settings
    xtntns_bitwardenEx:nngceckbapebfimnlniiiahkandclblb;Bitwarden;Local Extension Settings
    xtntns_microsoftAfL:fiedbfgcleddlbcmgdigjgdfcggjcion;Microsoft Autofill Local;Local Extension Settings
    xtntns_microsoftAfS:fiedbfgcleddlbcmgdigjgdfcggjcion;Microsoft Autofill Sync;Sync Extension Settings
    grbr_Desktop:%USERPROFILE%\Desktop\|*.txt|*recycle*,*windows*|25|1|1|files
    grbr_Documets:%USERPROFILE%\Documents\|*.txt|*recycle*,*windows*|25|1|1|files
    ldr_1:hxxp://172[.]86[.]75[.]189/36141266339446703039[.]bin|%APPDATA%\|exe
    token:3f9bef70525fd0873fc9acf8b6babce9
    

从C2下载sqlite3.dll，流量中可以看到下载的PE文件：  
![image](https://image.3001.net/images/20220915/1663231447_6322e5d7d293966284d3d.jpg!small)  
从c2获取的7个dll中，freebl3.dll,mozglue.dll,softokn3.dll,nss3.dll有Mozilla有效签名，msvcp140.dll,vcruntime140.dll有Microsoft有效签名，其中sqlite3.dll为MinGW编译无数字签名：  
![image](https://image.3001.net/images/20220915/1663231480_6322e5f8d852f886b6bb5.jpg!small)  
3个连续的POST请求使用的User-Agent为`rqwrwqrqwrqw`，向C2发送了大量明文数据，我们可以看到其中第一个POST请求发送收集到的系统数据System
Info.txt，主要内容为本机的操作系统版本和基本硬件信息还有本机安装的软件。  
![image](https://image.3001.net/images/20220915/1663231508_6322e614945aede61a105.jpg!small)  
第二个POST请求可以看到发送的是cookies.txt和passwords.txt，收集到的数据是chrome浏览器登陆的账号密码数据和cookies：  
![image](https://image.3001.net/images/20220915/1663231523_6322e6235064b3f6a87ad.jpg!small)  
第三个POST请求发送的是passwords.txt，主要就是本机Firefox浏览器保存的登陆网站对应的账号密码：  
![image](https://image.3001.net/images/20220915/1663231536_6322e6304f76ceb63116b.jpg!small)  
我们查看最后一个GET请求发现36141266339446703039.bin为一个PE文件：  
![image](https://image.3001.net/images/20220915/1663231577_6322e659eb4b3cd9a2cbc.jpg!small)  
我们使用DIE工具查看发现此PE文件为使用Visual Studio 2019编译的并使用ENIGMA5.x版本加壳的32位程序：  
![image](https://image.3001.net/images/20220915/1663231775_6322e71f2b6cf2711fdb5.jpg!small)  
通过沙箱分析36141266339446703039.bin有创建计划任务进行持久化的操作：  
![image](https://image.3001.net/images/20220915/1663231618_6322e6829ead466ce78d3.jpg!small)  
我们查看部分XMl文件内容，计划任务每隔5分钟会运行XML中的prevhost.exe，根据公开的威胁情报显示此程序功能为剪贴板劫持：  
![image](https://image.3001.net/images/20220915/1663231632_6322e690af9804d35b02f.jpg!small)  
查询94[.]131[.]106[.]116的威胁情报发现有2个恶意样本使用了此IP进行通信：  
![image](https://image.3001.net/images/20220915/1663231648_6322e6a0117f3ae63e00c.jpg!small)  
查询172[.]86[.]75[.]189的威胁情报，发现了多个下载样本也是加了Enigma壳：  
![image](https://image.3001.net/images/20220915/1663231664_6322e6b05eac17e84d954.jpg!small)

### 代码分析

由于样本都是加了强壳对代码进行VM，于是这里我寻找到了未加壳的样本进行分析，可以看到编译的连接器版本也是14.29，而且此样本是使用纯汇编编写所以样本大小只有55.5KB。  
![image](https://image.3001.net/images/20220915/1663231598_6322e66e7b5f5a1e318e6.jpg!small)  
首先分析第一个函数，主要通过LoadLibraryW和GetProcAddress函数组合动态获取函数地址：  
![image](https://image.3001.net/images/20220915/1663231797_6322e735a4f0afa9446ab.jpg!small)  
获取注册表和网络还有字符串加解密相关函数地址：  
![image](https://image.3001.net/images/20220915/1663231829_6322e755891e8a879023e.jpg!small)  
字符串使用了Base64编码加RC4加密方式，RC4密钥为`edinayarossiya`  
![image](https://image.3001.net/images/20220915/1663231868_6322e77c9ac7d253eb7cf.jpg!small)  
我们使用CyberChef随意解密一个字符串可以看到是一个格式化字符串：  
![image](https://image.3001.net/images/20220915/1663231928_6322e7b85e9c92e9ea39d.jpg!small)  
字符串解密完成会将一部分字符串转为宽字符：  
![image](https://image.3001.net/images/20220915/1663231944_6322e7c83b1f3e002f270.jpg!small)  
接着又解密了加密字符串，此处RC4使用的密钥为`59c9737264c0b3209d9193b8ded6c127`  
![image](https://image.3001.net/images/20220915/1663231964_6322e7dcbc357f6b194de.jpg!small)  
使用CyberChef解密字符串，可以看到此字符串为C2的URL：  
![image](https://image.3001.net/images/20220915/1663231983_6322e7ef6acde38fa08d2.jpg!small)  
接着使用GetUserDefaultLocaleName函数获取用户默认语言环境：  
![image](https://image.3001.net/images/20220915/1663232025_6322e8196398a37a997f0.jpg!small)  
StrStrIW函数对比当前默认语言环境是否为ru。  
![image](https://image.3001.net/images/20220915/1663232059_6322e83b9c19f3b2a2a5d.jpg!small)  
使用OpenMutexW打开互斥体`8724643052`  
![image](https://image.3001.net/images/20220915/1663232170_6322e8aa5839bbc4019f1.jpg!small)  
如果存在互斥体则退出进程，不存在则创建互斥体。  
![image](https://image.3001.net/images/20220915/1663232194_6322e8c250e9224f982fe.jpg!small)  
接着获取进程的运行权限是否为`S-1-5-18（SECURITY_LOCAL_SYSTEM_RID）`  
![image](https://image.3001.net/images/20220915/1663232213_6322e8d5c25f1136db2d8.jpg!small)  
通过获取注册表`SOFTWARE\\Microsoft\\Cryptography`的MachineGuid作为被感染主机的唯一ID。  
![image](https://image.3001.net/images/20220915/1663232268_6322e90c7d721fbc75915.jpg!small)  
获取MachineGuid：  
![image](https://image.3001.net/images/20220915/1663232300_6322e92c0fb298dbd4a33.jpg!small)  
接着获取了本机用户名：  
![image](https://image.3001.net/images/20220915/1663232321_6322e941da65dfa4535ad.jpg!small)  
收集完数据拼接字符串，拼接成的格式为：`machineId=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx|username&configId=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`其中的configId为第二次解密字符串使用的RC4密钥  
![image](https://image.3001.net/images/20220915/1663232365_6322e96db523747ea06d7.jpg!small)  
然后发送第一次POST请求，如C2存活会返回明文的配置文件，配置文件中包含了要窃取的指定数据：  
![image](https://image.3001.net/images/20220915/1663232517_6322ea05303b920367b17.jpg!small)  
解析配置信息的libs字段从C2下载dll：  
![image](https://image.3001.net/images/20220915/1663232394_6322e98a4041a1286675e.jpg!small)  
发送get请求下载dll并使用WriteFile函数保存到本地：  
![image](https://image.3001.net/images/20220915/1663232554_6322ea2aaf3eeb40cc308.jpg!small)  
收集基本系统信息并格式化发送POST请求到C2：  
![image](https://image.3001.net/images/20220915/1663232637_6322ea7db74f52813a5fd.jpg!small)  
接下来的主要逻辑就是解析配置文件，根据配置文件窃取对应的数据并发送到C2：  
![image](https://image.3001.net/images/20220915/1663232677_6322eaa54ecb1e0c73b14.jpg!small)  
我们查看Chromium浏览器窃取函数，首先遍历硬盘查找User Data目录，基于Chromium开发的浏览器默认的数据保存目录一般都在User
Data目录下，比如说chrome浏览器的数据存储在`C:\Users\username\AppData\Local\Google\Chrome\User
Data`，如果存在User Data目录则解密相关数据库并使用sqlite3的sql语句查询数据。  
![image](https://image.3001.net/images/20220915/1663232717_6322eacd53a274b3805f8.jpg!small)  
从Local State文件读取encrypted_key字段用于解密登录密码，后续解密数据并使用sqlite3语句查询数据：  
![image](https://image.3001.net/images/20220915/1663232759_6322eaf7264a3ab9bd2b8.jpg!small)  
Login Data是用于保存Chromium浏览器登录账号密码信息的sqlite3数据库，sqlite3查询chrome浏览器登录密码：  
![image](https://image.3001.net/images/20220915/1663232801_6322eb21eb51da71715d2.jpg!small)  
Chromium浏览器的密码加密方式，版本号80之前的可直接使用CryptUnprotectData函数解密，如果80之后的版本密码会有v10开头的标志，解密需要使用Local
State文件的中的encrypted_key字段的Aes密钥进行解密。  
![image](https://image.3001.net/images/20220915/1663232834_6322eb426cfa393a62365.jpg!small)  
打开Network文件夹Cookies数据库文件使用sqlite3 sql语句查询Chromium浏览器cookies：  
![image](https://image.3001.net/images/20220915/1663232863_6322eb5feedbe949d6ac4.jpg!small)  
sqlite3 sql语句查询Chromium浏览器autofill数据（自动填充账号密码）：  
![image](https://image.3001.net/images/20220915/1663232895_6322eb7f3df69f44c751e.jpg!small)  
打开Web Data数据库文件并使用sqlite3 sql语句查询Chromium器信用卡信息和付款凭证：  
![image](https://image.3001.net/images/20220915/1663232925_6322eb9d6fcca3410cf41.jpg!small)  
解析配置文件ews_字段窃取指定浏览器插件的数据，`ews_meta_e:ejbalbakoplchlghecdalmeeeajnimhm;MetaMask;Local
Extension Settings`  
![image](https://image.3001.net/images/20220915/1663244546_63231902f39c49db021aa.jpg!small)  
遍历硬盘窃取配置文件中指定浏览器插件的数据：  
![image](https://image.3001.net/images/20220915/1663244779_632319eb6345cf676aae4.jpg!small)  
获取需要用到的nss3.dll和sqlite3.dll导出函数地址：  
![image](https://image.3001.net/images/20220915/1663232957_6322ebbd14ff051afe981.jpg!small)  
针对mozilla firefox浏览器用于保存数据的Profiles文件夹进行数据窃取：  
![image](https://image.3001.net/images/20220915/1663232977_6322ebd17e91d17fc6252.jpg!small)  
打开cookies.sqlite数据库文件并使用sqlite3 sql语句查询mozilla firefox浏览器cookies：  
![image](https://image.3001.net/images/20220915/1663233003_6322ebeb4f30ca3e186ca.jpg!small)  
读取logins.json文件并解密获取账号密码：  
![image](https://image.3001.net/images/20220915/1663233025_6322ec010982e4f00b433.jpg!small)  
打开formhistory.sqlite数据库并使用sqlite3 sql语句查询，此数据库中记录着通过 Firefox
搜索框搜索的历史以及在网站填写过的表单：  
![image](https://image.3001.net/images/20220915/1663233046_6322ec1689bb10fca0199.jpg!small)  
遍历搜索查找wallet.dat文件：  
![image](https://image.3001.net/images/20220915/1663233067_6322ec2b10d12771bedc1.jpg!small)  
解析配置文件中的grbr_字段，窃取对应路径下的指定文件，配置文件的内容如下`grbr_Desktop:%USERPROFILE%\Desktop|*.txt|*recycle*,*windows*|25|1|1|files`  
![image](https://image.3001.net/images/20220915/1663233090_6322ec42c0735cc6cf89b.jpg!small)  
解析配置文件tlgrm_字段，窃取telegram的指定文件数据：  
![image](https://image.3001.net/images/20220915/1663233108_6322ec54e0bc52ed4a18d.jpg!small)  
解析配置文件ldr_字段，下载配置文件的payload到指定目录下并运行配置信息如下所示`ldr_1:hxxp://172[.]86[.]75[.]189/36141266339446703039[.]bin|%APPDATA%|exe`  
![image](https://image.3001.net/images/20220915/1663233130_6322ec6a4dabdd3a34b40.jpg!small)  
如果存在则从C2下载下一阶段的payload并使用ShellExcuteW运行：  
![image](https://image.3001.net/images/20220915/1663244113_63231751c3785e643e824.jpg!small)  
通过分析未加壳的样本，可以推断出这和现在活跃传播的加壳样本都为RaccoonStealer
v2版本并且代码没有太多更改，加壳样本的配置文件中多了xtntns_字段用于窃取密码管理软件的数据，后续的更新可能会增加更多数据的窃取功能并且有可能会增加勒索等功能。

# 总结

RaccoonStealer
v2通过伪装破解软件下载站，针对搜索引擎的SEO关键词优化达到广泛传播实现信息窃取，并且使用了VMProtect、Themida、ENIGMA等强壳进行代码VM等保护，使用附加大量重复字节膨胀PE文件大小防止被上传沙箱分析等等，尽量不要下载使用破解软件请多支持官方正版软件，不然碰到RaccoonStealer
v2这种类型的恶意软件得不偿失。

