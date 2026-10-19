实验吧CTF密码学Writeup-困在栅栏里的凯撒 Writeup

[ syxvip](https://www.jianshu.com/u/380fd93bae2c)关注赞赏支持

# 实验吧CTF密码学Writeup-困在栅栏里的凯撒 Writeup

### 困在栅栏里的凯撒分值：10

  * 来源： [北邮天枢战队](http://www.shiyanbar.com/user/studentcourse/A569313BDAD62C)
  * 难度：易
  * 参与人数：6331人
  * Get Flag：3401人
  * 答题人数：3591人
  * 解题通过率：95%

小白发现了一段很6的字符：NlEyQd{seft}

* * *

根据题目的表面意思，看在栅栏里面的凯撒，应该是先栅栏后凯撒。  
那么就先进进行栅栏试一下吧！！有5个答案

解密平台：<http://tool.bugku.com/jiemi/>

    
    
    NlEyQd{seft}
    
    2栏：
    N{lsEeyfQtd}
    
    3栏：
    NQeldfE{tys}
    
    4栏：
    Ny{flQstEde}
    
    6栏：
    NEQ{etlydsf}
            
    

5个答案看不出来那个像是正确的，怎么办，挨个试吧。  
继续进行凯撒解密：

    
    
    NlEyQd{seft}
    凯撒解密：
    
    NlEyQd{seft}
    OmFzRe{tfgu}
    PnGaSf{ughv}
    QoHbTg{vhiw}
    RpIcUh{wijx}
    SqJdVi{xjky}
    TrKeWj{yklz}
    UsLfXk{zlma}
    VtMgYl{amnb}
    WuNhZm{bnoc}
    XvOiAn{copd}
    YwPjBo{dpqe}
    ZxQkCp{eqrf}
    AyRlDq{frsg}
    BzSmEr{gsth}
    CaTnFs{htui}
    DbUoGt{iuvj}
    EcVpHu{jvwk}
    FdWqIv{kwxl}
    GeXrJw{lxym}
    HfYsKx{myzn}
    IgZtLy{nzao}
    JhAuMz{oabp}
    KiBvNa{pbcq}
    LjCwOb{qcdr}
    MkDxPc{rdes}
    
    
    
    
    2栏：
    N{lsEeyfQtd}
    凯撒解密：
    
    N{lsEeyfQtd}
    O{mtFfzgRue}
    P{nuGgahSvf}
    Q{ovHhbiTwg}
    R{pwIicjUxh}
    S{qxJjdkVyi}
    T{ryKkelWzj}
    U{szLlfmXak}
    V{taMmgnYbl}
    W{ubNnhoZcm}
    X{vcOoipAdn}
    Y{wdPpjqBeo}
    Z{xeQqkrCfp}
    A{yfRrlsDgq}
    B{zgSsmtEhr}
    C{ahTtnuFis}
    D{biUuovGjt}
    E{cjVvpwHku}
    F{dkWwqxIlv}
    G{elXxryJmw}
    H{fmYyszKnx}
    I{gnZztaLoy}
    J{hoAaubMpz}
    K{ipBbvcNqa}
    L{jqCcwdOrb}
    M{krDdxePsc}
    
    
    
    
    3栏：
    NQeldfE{tys}
    凯撒解密：
    NQeldfE{tys}
    ORfmegF{uzt}
    PSgnfhG{vau}
    QThogiH{wbv}
    RUiphjI{xcw}
    SVjqikJ{ydx}
    TWkrjlK{zey}
    UXlskmL{afz}
    VYmtlnM{bga}
    WZnumoN{chb}
    XAovnpO{dic}
    YBpwoqP{ejd}
    ZCqxprQ{fke}
    ADryqsR{glf}
    BEszrtS{hmg}
    CFtasuT{inh}
    DGubtvU{joi}
    EHvcuwV{kpj}
    FIwdvxW{lqk}
    GJxewyX{mrl}
    HKyfxzY{nsm}
    ILzgyaZ{otn}
    JMahzbA{puo}
    KNbiacB{qvp}
    LOcjbdC{rwq}
    MPdkceD{sxr}
    
    
    
    4栏：
    Ny{flQstEde}
    
    Ny{flQstEde}
    Oz{gmRtuFef}
    Pa{hnSuvGfg}
    Qb{ioTvwHgh}
    Rc{jpUwxIhi}
    Sd{kqVxyJij}
    Te{lrWyzKjk}
    Uf{msXzaLkl}
    Vg{ntYabMlm}
    Wh{ouZbcNmn}
    Xi{pvAcdOno}
    Yj{qwBdePop}
    Zk{rxCefQpq}
    Al{syDfgRqr}
    Bm{tzEghSrs}
    Cn{uaFhiTst}
    Do{vbGijUtu}
    Ep{wcHjkVuv}
    Fq{xdIklWvw}
    Gr{yeJlmXwx}
    Hs{zfKmnYxy}
    It{agLnoZyz}
    Ju{bhMopAza}
    Kv{ciNpqBab}
    Lw{djOqrCbc}
    Mx{ekPrsDcd}
    
    
    
    
    6栏：
    NEQ{etlydsf}
    
    NEQ{etlydsf}
    OFR{fumzetg}
    PGS{gvnafuh}
    QHT{hwobgvi}
    RIU{ixpchwj}
    SJV{jyqdixk}
    TKW{kzrejyl}
    ULX{lasfkzm}
    VMY{mbtglan}
    WNZ{ncuhmbo}
    XOA{odvincp}
    YPB{pewjodq}
    ZQC{qfxkper}
    ARD{rgylqfs}
    BSE{shzmrgt}
    CTF{tianshu}
    DUG{ujbotiv}
    EVH{vkcpujw}
    FWI{wldqvkx}
    GXJ{xmerwly}
    HYK{ynfsxmz}
    IZL{zogtyna}
    JAM{aphuzob}
    KBN{bqivapc}
    LCO{crjwbqd}
    MDP{dskxcre}
    

终于第六栏看到了CTF...、  
CTF{tianshu}

