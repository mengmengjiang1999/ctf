![](https://image.3001.net/images/20201021/1603278016_5f9014c0026b7045d4446.jpg!small)

## 写在前面的话

MaMoCrypt是一款臭名昭著的勒索软件，该勒索软件从去年的十二月份开始活跃，深受其害的用户可以算是不计其数了。那么在这篇文章中，我们将告诉大家如何恢复、解密被MaMoCrypt勒索软件加密的数据。

MaMoCrypt是一款非常与众不同的勒索软件，这款勒索软件采用Delphi开发，并且使用了mpress进行封装，是MZRevenge的一个变种版本。

## 勒索软件行为

  * MaMoCrypt能够删除Windows卷影（ShadowVolume），并禁用防火墙以及UAC服务。这些功能在恶意软件领域中其实并不罕见，因此我们在此对其不做更深入的讨论。
  * 它使用了Delphi的随机生成器（基于线性同余生成器）以及基于时间的DWORD种子（使用QueryPerformanceCounter或GetTickCount），此时将会生成两个缓冲区，其中的数据会使用Base64进行编码，并添加MZRKEYPUBLIC / MZRKEYPRIVATE字符串。
  * 根据上述的两个密钥以及一个掩码，该勒索软件将会针对每个文件生成两个加密密钥，随后将会使用它们来进行文件加密。它首先会使用AES 128 CBC来进行文件内容加密，然后再使用Twofish 128 NOFB来对其进行二次加密。AES加密过程中剩余的16%内容将使用AES 128 CFB进行加密，所有加密文件的后缀名都会添加一个“.MZ173801”。
  * 加密完成之后，恶意软件会再次枚举所有加密目录，并分别存放勒索信息，而勒索信息中也会包含对应的那两个MZR密钥。

虽然MZR密钥在密钥生成或加密的过程中不会发生变化，但掩码会持续更新。它们的生成基于的是SHA1、SHA512和某些自定义算法的混合计算结果。每一个AES和Twofish密钥还会使用SHA512进行16次计算以及字节异或。

## 掩码和密钥生成

    
    
    *(int*)mask_in = offset;
    
     for (int i = 0; i < 0x800; ++i) {
    
     
    
         SHA1(mask_in, 0x84, mask_out);
    
         *(int*)mask_in = i + 1 + offset;
    
         *(mask_in + 3 + (i & 0x7F) + 1) ^= mask_out[0];
    
         mask[i] = mask_out[1];
    
     }
    
     offset += 0x800;
    
     aes_key = generate_key(mask, mzrkey_private.c_str(), 0x800, mzrkey_private.size());
    
     
    
     for (int i = 0; i < 0x200; ++i) {
    
     
    
     SHA1(mask_in, 0x84, mask_out);
    
         *(int*)mask_in = i + 1 + offset;
    
         *(mask_in + 3 + (i & 0x7F) + 1) ^= mask_out[0];
    
         mask[i] = mask_out[1];
    
     }
    
     offset += 0x200;
    
     twofish_key = generate_key(mask, mzrkey_public.c_str(), 0x200, mzrkey_public.size());
    
    generate_key:
    
     int mzrkey_size_bswap = _byteswap_ulong(mzrkey_len);
    
     int mask_size_bswap = _byteswap_ulong(mask_len);
    
     for (int i = 0; i < key_SIZE; ++i) {
    
       ((int*)in)[0] = _byteswap_ulong(i);
    
       for (int j = 0; j < i; ++j)
    
          in[j + 4] = key[j];
    
       *((int*)(in + 4 + i)) = _byteswap_ulong(1);
    
       *((int*)(in + 8 + i)) = mask_size_bswap;
    
       memcpy(in + 3 * sizeof(int) + i, mask, mask_len);
    
       memcpy(in + 3 * sizeof(int) + mask_len + i, &mzrkey_size_bswap, 4);
    
       memcpy(in + 3 * sizeof(int) + mask_len + 4 + i, mzrkey, mzrkey_len);
    
       SHA512(in, mask_len + mzrkey_len + 4 * sizeof(int) + i, out);
    
       for (int j = 0; j < SHA512_DIGEST_LENGTH; ++j)
    
           key[i] ^= out[j];
    
     }

AES CBC的IV将使用AES 128 ECB生成，位置在一个16字节缓冲区内。类似的，Twofish NOFB的IV将使用Twofish 128
ECB生成，位置同样在一个16字节缓冲区内。掩码的初始内容生成如下：

    
    
    memset(mask_in, MASK_IN_SZ, 0);
    
     memset(mask_out, MASK_OUT_SZ, 0);
    
     
    
     for (int i = 0; i < 0x80; ++i) {
    
       SHA1(mask_in, 0x84, mask_out);
    
       *(int*)mask_in = i + 1;
    
       *(mask_in + 3 + i + 1) = mask_out[0];
    
     }

实际上，这种加密机制我们此前从未在其他勒索软件中见到过，而且恶意代码还会对整个文件系统进行加密，该勒索软件的硬编码文件和驱动器列表如下：

    
    
    C:\Program Files\Steam
    
    C:\Program Files (x86)\Steam
    
    [DRIVES A-Z, WITHOUT C]
    
    C:\Users\%user%\AppData\Roaming\Microsoft\Windows\Recent\
    
    C:\Users\%user%\Pictures
    
    C:\Users\%user%\Music
    
    C:\Users\%user%\Videos
    
    C:\Users\%user%\Documents
    
    C:\Users\Public\Documents
    
    C:\Users\Public\Videos
    
    C:\Users\Public\Music
    
    C:\Users\Public\Pictures
    
    C:\Users\%user%\Downloads
    
    C:\Users\%user%\Favorites
    
    ::{645FF040-5081-101B-9F08-00AA002F954E} (Recycle Bin)
    
    C:\Users\Administrator
    
    C:\Users\Public
    
    C:\Users\Default
    
    C:\Users\%user%\Desktop
    
    C:\Users\Public\Desktop
    
    C:\Users\%user%\AppData\Roaming\Microsoft\Internet Explorer\Quick Launch\User Pinned\TaskBar
    
    C:\Users\%user%\AppData\Roaming\Microsoft\Windows\Start Menu
    
    C:\ProgramData\Microsoft\Windows\Start Menu\

由于掩码/密钥生成使用了一个偏移量来代表每一个文件的递增，那么解密的过程将依赖于文件的加密文件夹。

### 这款勒索软件支持的文件加密类型如下：

    
    
    .cs;.lnk;.mp3;.jpg;.jpeg;.raw;.tif;.gif;.png;.bmp;.3dm;.max;.accdb;.db;.dbf;.mdb;.pdb;.sql;.dwg;.dxf;.c;.cpp;.cs;.h;.php;.asp;.rb;.java;.jar;.class;.py;.js;.aaf;.aep;.aepx;
    
     
    
    .plb;.prel;.prproj;.aet;.ppj;.psd;.indd;.indl;.indt;.indb;.inx;.idml;.pmd;.xqx;.xqx;.ai;.eps;.ps;.svg;.swf;.fla;.as3;.as;.txt;.doc;.dot;.docx;.docm;.dotx;.dotm;.docb;.rtf;.wpd;
    
     
    
    .wps;.msg;.pdf;.xls;.xlt;.xlm;.xlsx;.xlsm;.xltx;.xltm;.xlsb;.xla;.xlam;.xll;.xlw;.ppt;.pot;.pps;.pptx;.pptm;.potx;.potm;.ppam;.ppsx;.ppsm;.sldx;.sldm;.wav;.aif;.iff;.m3u;.m4u;
    
     
    
    .mid;.mpa;.wma;.ra;.avi;.mov;.mp4;.3gp;.mpeg;.3g2;.asf;.asx;.flv;.mpg;.wmv;.vob;.m3u8;.mkv;.dat;.csv;.efx;.sdf;.vcf;.xml;.ses;.rar;.zip;.7zip;.dtb;.bat;.apk;.vb;.sln;.csproj;
    
     
    
    .vbproj;.hpp;.asm;.lua;.ibank;.design;.aspx;.bak;.obj;.sqlite;.sqlite3;.sqlitedb;.back;.backup;.one;.pst;.url;.onetoc2;.m4a;.m4v;.ogg;.hwp;.HWP;.OGG;.M4V;.M4A;.ONETOC2;
    
     
    
    .URL;.PST;.ONE;.BACKUP;.BACK;.SQLITEDB;.SQLITE3;.SQLITE;.OBJ;.BAK;.ASPX;.DESIGN;.IBANK;.LUA;.ASM;.HPP;.VBPROJ;.CSPROJ;.SLN;.CS;.VB;.LNK;.JPG;.JPEG;.RAW;.TIF;.GIF;
    
     
    
    .PNG;.BMP;.3DM;.MAX;.ACCDB;.DB;.DBF;.MDB;.PDB;.SQL;.DWG;.DXF;.C;.CPP;.CS;.H;.PHP;.ASP;.RB;.JAVA;.JAR;.CLASS;.PY;.JS;.AAF;.AEP;.AEPX;.PLB;.PREL;.PRPROJ;.AET;.PPJ;.PSD;
    
     
    
    .INDD;.INDL;.INDT;.INDB;.INX;.IDML;.PMD;.XQX;.XQX;.AI;.EPS;.PS;.SVG;.SWF;.FLA;.AS3;.AS;.TXT;.DOC;.DOT;.DOCX;.DOCM;.DOTX;.DOTM;.DOCB;.RTF;.WPD;.WPS;.MSG;.PDF;.XLS;
    
     
    
    .XLT;.XLM;.XLSX;.XLSM;.XLTX;.XLTM;.XLSB;.XLA;.XLAM;.XLL;.XLW;.PPT;.POT;.PPS;.PPTX;.PPTM;.POTX;.POTM;.PPAM;.PPSX;.PPSM;.SLDX;.SLDM;.WAV;.MP3;.AIF;.IFF;.M3U;.M4U;.MID;
    
     
    
    .MPA;.WMA;.RA;.AVI;.MOV;.MP4;.3GP;.MPEG;.3G2;.ASF;.ASX;.FLV;.MPG;.WMV;.VOB;.M3U8;.MKV;.DAT;.CSV;.EFX;.SDF;.VCF;.XML;.SES;.RAR;.ZIP;.7ZIP;.DTB;.BAT;.APK;

加密成功之后，该勒索软件将枚举全部加密目录，并一一存放勒索信息，勒索文本文件名为“How Do I Recover My Files
(Readme).txt”：

![](https://image.3001.net/images/20201021/1603278070_5f9014f64d8af4acc3a59.png!small)

## 如何解密

第一步：首先点击【[
_这里_](http://download.bitdefender.com/am/malware_removal/BDMaMoDecryptTool.exe)】下载解密工具，并存储在本地设备中。

第二步：双击下载下来的BDMaMoDecryptTool.exe应用程序文件，然后在弹出的UAC提示中点击“Yes”：

![](https://image.3001.net/images/20201021/1603278081_5f90150167b9282bcbe99.png!small)

第三步：读取并接受终端用户许可证协议：

![](https://image.3001.net/images/20201021/1603278088_5f901508980da09c4223b.png!small)

第四步：考虑到这款勒索软件家族的特殊性，工具将会以特定的顺序来扫描系统，而无法允许用户指定需要解密的文件夹或文件数据，因此我们强烈建议用户选择“备份文件”选项。

第五步：点击“Start
Tool”按钮，剩下的就交给解密工具来完成吧！如果你选择了备份选项，那么加密文件和解密文件都将同时出现，你还可以在%temp%\BDRemovalTool目录中查看到解密过程的日志记录。

![](https://image.3001.net/images/20201021/1603278097_5f901511b3129670b9e3d.png!small)

## 解密工具

BDMaMoDecryptTool.exe：【[ _下载_
_地址_](https://download.bdstore.com.cn/am/malware_removal/BDMaMoDecryptTool.exe)】

