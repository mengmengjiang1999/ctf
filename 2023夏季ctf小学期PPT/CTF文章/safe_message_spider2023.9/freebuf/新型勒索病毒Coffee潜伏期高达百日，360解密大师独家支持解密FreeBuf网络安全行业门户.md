近日，360安全大脑监测发现一种具有蠕虫性质的新型勒索病毒Coffee存在大范围传播的风险。针对该勒索病毒传播事件，360安全分析团队（CCTGA勒索软件防范应对工作组成员）展开了详尽的分析。经过系统性分析确定，Coffee病毒可以通过软件捆绑和QQ群钓鱼传播且危害性极大，需引起高度重视和警惕。

![](https://image.3001.net/images/20220216/1644982776_620c71f87add0e550157a.png!small)

通过真实案例对Coffee病毒的攻击流程进行了还原：某网盘工具“数码小站.exe”与
“AppUnion.dll”是攻击者准备的一对白利用程序。当宿主程序“数码小站.exe”执行时，病毒模块“AppUnion.dll”被加载执行。之后，病毒模块会先最小化当前文件夹的窗口，之后用真正的“数码小站.exe”替换掉原先的病毒宿主程序，再次把真正的“数码小站.exe”执行起来，就此完成了捆绑病毒的执行，用户很难发现其中问题。

![](https://image.3001.net/images/20220216/1644982798_620c720e4614def474081.png!small)

不过，需要指出的是：用户本地的病毒模块，只是该病毒的一个引导与执行器，真正的功能载荷都是通过远程加载的方式获取的。其中关键的两个功能模块，加载地址如下（除了使用Gitee，还使用了IPFS用以存储恶意Shellcode）：

![](https://image.3001.net/images/20220216/1644982825_620c722992a0340e661d2.png!small)

hxxps://gitee[.]com/temphi/chinese_chess/raw/master/css/r.jpg

![](https://image.3001.net/images/20220216/1644982842_620c723aadbbbdfb280c5.png!small)

hxxps://gitee[.]com/temphi/chinese_chess/raw/master/css/t.jpg

![](https://image.3001.net/images/20220216/1644982873_620c7259ac3a461590b3a.png!small)

其中，前者为勒索病毒模块，后者为利用QQ传播所用的相关文件。一切就绪后，攻击者会把白利用复制到要感染的程序目录下，然后白exe的文件名将变成被感染的程序名称加上一个不可见字符0x200e，并通过修改桌面lnk指向这个白exe。随后，攻击者可通过云端Shellcode，远程开启处于默认关闭状态的加密勒索功能。其中，触发机密开关有两个，分别为：

![](https://image.3001.net/images/20220216/1644982889_620c72697fd3e1cc9512d.png!small)

  1. 计算用当前机器时间转换成分钟减去%Appdata%目录下的guid-RSA.TXT文件的创建时间的分钟数如果>=100天则触发（部分版本配置的是36500天）
  2. 执行run函数的参数如果为901则直接触发加密，100为开启发送QQ传播（目前云控配置），200为禁用QQ传播，301为关闭感染替换其它程序（dll劫持）![](https://image.3001.net/images/20220216/1644982912_620c7280ea576ef0dfd6c.png!small)

加密勒索功能开启后，系统将以guid
"d672a56c-f9bd-4297-93c3-27caa1a5e36a"为例，生成加密密钥。生成的加密文件用的KEY为："juWECzjk"，其中前4个字符juWE会做为加密后的文件名中的pwdmask，例如test.coffee.
juWE.jpg。

![](https://image.3001.net/images/20220216/1644982943_620c729ff3ae1378a5880.png!small)

值得一提的是，文件加密使用的是RC4算法。加密前会检测加密标记(位于被加密文件尾部)，防止重复加密，并且只加密文件的前2097152字节即2MB。被加密的文件格式有：.key、.keys、.pfx、.pem、.p12、.csr、.gpg、.aes、.docx、.doc、.docm、.pdf、.xlsx、.xls、.xlsm、.xlsb、.ppt、.pptx、.pptm、.wps、.et、.dps、.csv、.mdb、.dbf、.dat、.db、.sav、.sas、.sas7bdat、.m、.mat、.r、.rdata、.psd、.cdr、.ai、.jpg、.3gp、.mp4、.mov、.dwg、.dxf、.vsd、.lst、.ba_、.rep、.rbk、.ais、.aib、.dbb、.mdf、.ldf、.ndf、.myd、.frm、.myi、.ibd、.sql、.sqlite、.fdb、.gdb、.rdb、.aof、.udb、.udbx、.wt、.wl、.wp、.shp、.cs、.java、.cpp、.pas、.asm、.rar、.zip。

  3. ![](https://image.3001.net/images/20220216/1644982964_620c72b4d6d70c7cdd245.png!small)

加密完成后将生成勒索信，勒索信中的待解密密码为使用内置的一个1024位的RSA公钥：

uqYJWgnvSUWXC22R2CMHYzTA3d2dE+W4AhtkBR6HcA/wLRe2eBctuZrwW6F5jM+fIVx+gooGapnaMTcQ9EtYr0FkHY1TqD8VhTUp08dZHCVoBNNLEkVTEFKD5F1GdEXptEP0046OqnztAb94JtzP0FOvaCeuswDVbmfHZco0SxM=

加密加密文件所用的KEY后的内容。

![](https://image.3001.net/images/20220216/1644982988_620c72ccdd5791ee85f1c.png!small)![](https://image.3001.net/images/20220216/1644983010_620c72e23aeeeb2ed1b09.png!small)![](https://image.3001.net/images/20220216/1644983019_620c72ebda35b0b0f0169.png!small)

虽然Coffee病毒有愈演愈烈的趋势，不过可喜的是，360解密大师已经在第一时间支持了该勒索病毒解密。受到Coffee勒索病毒影响的用户，可尝试使用360解密大师解密，或联系360安全中心寻求帮助。

  4. ![](https://image.3001.net/images/20220216/1644983038_620c72fea1c3805e73ae9.png!small)

