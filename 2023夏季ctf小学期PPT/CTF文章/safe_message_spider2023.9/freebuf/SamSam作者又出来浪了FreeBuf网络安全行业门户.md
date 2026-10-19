## 前言

**最近深信服EDR安全团队发现SamSam勒索病毒的最新变种样本，编译时间较新，加密后的文件后缀名与之前发现的一款变种一样，同样以.weapologize结尾，样本采用RSA2048+AES加密算法进行加密，加密后的文件无法解密。**

## 一、样本简介

SamSam勒索病毒作为最活跃的勒索病毒之一，在2015-2018年期间，造成了至少3000万美元的社会损失，据调查这款勒索软件至少勒索了价值一千万美元以上的比特币，此前SamSam勒索病毒的两位作者已经被FBI指控，分别为现居住在伊朗的27岁的Mohammad
Mehdi Shah Mansour和34岁的Faramarz Shahi Savandi，如下所示：

![](https://image.3001.net/images/20181218/1545123762_5c18b7b255c89.jpg!small)

FBT公布了两个BTC钱包地址，如下所示：

![](https://image.3001.net/images/20181218/1545123768_5c18b7b8bcc6f.png!small)

![](https://image.3001.net/images/20181218/1545123774_5c18b7be20ead.png!small)

## 二、详细分析

1\. 样本采用NET语言进行编写，如下所示：

![](https://image.3001.net/images/20181218/1545123784_5c18b7c89937f.png!small)

查看样本的编译时间，为2018年12月11号，如下所示：

![](https://image.3001.net/images/20181218/1545123793_5c18b7d193c34.png!small)

2\. 传入相应的三个参数，如果没有参数，则直接退出程序，如下所示：

![](https://image.3001.net/images/20181218/1545124132_5c18b924a4e4b.png!small)

3\. 解密生成勒索相关信息，如下所示：

![](https://image.3001.net/images/20181218/1545124140_5c18b92c53ce3.png!small)

通过AES算法进行解密，如下所示：

![](https://image.3001.net/images/20181218/1545124152_5c18b93846ab1.png!small)

4\. 在当前目录下读取存放RSA公钥Key的*.keyxml配置文件，如下所示：

![](https://image.3001.net/images/20181218/1545124166_5c18b9464d02c.png!small)

5\. 遍历磁盘文件，如下所示：

![](https://image.3001.net/images/20181218/1545124175_5c18b94fb1112.png!small)

比较获取到的磁盘文件的文件名，如下所示：

![](https://image.3001.net/images/20181218/1545124187_5c18b95bc1b4f.png!small)

如果文件目录或文件扩展名包含以下文件名或目录，则不进行加密操作，相应的文件名和目录，如下所示：

文件后缀名为:

    
    
    .weapologize、.search-ms、.exe、.msi、.lnk、.wim、.scf、.ini、.sys、.dll

文件名为：

    
    
    SORRY-FOR-FILES.html、g04inst.bat、desktop.ini、ntuser.dat

目录包含：

    
    
    c:\\ProgramData、c:\\windows、c:\\winnt、microsoft\\windows、appdata、
    
    Reference assemblies\\microsoft、recycle.bin、c:\\users\\all users、
    
    c:\\documents and settings\\all users、c:\\boot、c:\\users\\default

6.判断磁盘文件后缀名，如果在加密后缀文件名列表中，则进行后面的加密操作，如下所示：

![](https://image.3001.net/images/20181218/1545124199_5c18b967e8ca5.png!small)

一共有330个需要加密的文件的后缀名，如下所示：

    
    
    ".vb"、".asmx"、".config"、".3dm"、".3ds"、".3fr"、".3g2"、".3gp"、".3pr"、".7z"、".ab4"、".accdb"、".accde"、".accdr"、".accdt"、".ach"、".acr"、".act"、".adb"".ads"、".agdl"、".ai"、".ait"、".al"、".apj"、".arw"、".asf"、".asm"、".asp"、".aspx"、".asx"、".avi"、".awg"、".back"、".backup"、".backupdb"、".bak"、".lua"".m"、".m4v"、".max"、".mdb"、".mdc"、".mdf"、".mef"、".mfw"、".mmw"、".moneywell"、".mos"、".mov"、".mp3"、".mp4"、".mpg"、".mrw"、".msg"、".myd"、".nd"、".ndd"".nef"、".nk2"、".nop"、".nrw"、".ns2"、".ns3"、".ns4"、".nsd"、".nsf"、".nsg"、".nsh"、".nwb"、".nx2"、".nxl"、".nyf"、".tif"、".tlg"、".txt"、".vob"、".wallet"".war"、".wav"、".wb2"、".wmv"、".wpd"、".wps"、".x11"、".x3f"、".xis"、".xla"、".xlam"、".xlk"、".xlm"、".xlr"、".xls"、".xlsb"、".xlsm"、".xlsx"、".xlt"、".xltm"、".xltx"、".xlw"
    
    ".xml"、".ycbcra"、".yuv"、".zip"、".sqlite"、".sqlite3"、".sqlitedb"、".sr2"、".srf"、".srt"、".srw"、".st4"、".st5"、".st6"、".st7"、".st8"、".std"、".sti"
    
    ".stw"、".stx"、".svg"、".swf"、".sxc"、".sxd"、".sxg"、".sxi"、".sxm"、".sxw"、".tex"、".tga"、".thm"、".tib"、".py"、".qba"、".qbb"、".qbm"、".qbr"、".qbw"、".qbx"、".qby"、".r3d"、".raf"、".rar"、".rat"、".raw"、".rdb"、".rm"、".rtf"、".rw2"、".rwl"、".rwz"、".s3db"、".sas7bdat"、".say"、".sd0"、".sda"、".sdf"、".sldm"、".sldx"、".sql"、".pdd"、".pdf"、".pef"、".pem"、".pfx"、".php"、".php5"、".phtml"、".pl"、".plc"、".png"、".pot"、".potm"、".potx"、".ppam"、".pps"、".ppsm"、".ppsx"、".ppt"、".pptm"、".pptx"、".prf"、".ps"、".psafe3"、".psd"、".pspimage"、".pst"、".ptx"、".oab"、".obj"、".odb"、".odc"、".odf"、".odg"、".odm"、".odp"、".ods"、".odt"、".oil"、".orf"、".ost"、".otg"、".oth"、".otp"、".ots"、".ott"、".p12"、".p7b"、".p7c"、".pab"、".pages"、".pas"、".pat"、".pbl"、".pcd"、".pct"、".pdb"、".gray"、".grey"、".gry"、".h"、".hbk"、".hpp"、".htm"、".html"、".ibank"、".ibd"、".ibz"、".idx"、".iif"、".iiq"、".incpas"、".indd"、".jar"、".java"、".jpe"、".jpeg"、".jpg"、".jsp"、".kbx"、".kc2"、".kdbx"、".kdc"、".key"、".kpdx"、".doc"、".docm"、".docx"、".dot"、".dotm"、".dotx"、".drf"、".drw"、".dtd"、".dwg"、".dxb"、".dxf"、".dxg"、".eml"、".eps"、".erbsql"、".erf"、".exf"、".fdb"、".ffd"、".fff"、".fh"、".fhd"、".fla"、".flac"、".flv"、".fmb"、".fpx"、".fxg"、".cpp"、".cr2"、".craw"、".crt"、".crw"、".cs"、".csh"、".csl"、".csv"、".dac"、".bank"、".bay"、".bdb"、".bgt"、".bik"、".bkf"、".bkp"、".blend"、".bpw"、".c"、".cdf"、".cdr"、".cdr3"、".cdr4"、".cdr5"、".cdr6"、".cdrw"、".cdx"、".ce1"、".ce2"、".cer"、".cfp"、".cgm"、".cib"、".class"、".cls"、".cmt"、".cpi"、".ddoc"、".ddrw"、".dds"、".der"、".des"、".design"、".dgc"、".djvu"、".db"、".db-journal"、".db3"、".dcr"、".dcs"、".ddd"、".dbf"、".dbx"、".dc2"、".pbl"

两个需要加密的数据库后缀名sql、mdf，如下所示：

![](https://image.3001.net/images/20181218/1545124212_5c18b9742507f.png!small)

7\. 加密文件，生成.weapologize结尾的加密文件，如下所示：

![](https://image.3001.net/images/20181218/1545124223_5c18b97f0fd1b.png!small)

生成后的加密文件文件名，如下所示：

![](https://image.3001.net/images/20181218/1545124234_5c18b98a817de.png!small)

利用生成的AES的key和iv加密文件，如下所示：

![](https://image.3001.net/images/20181218/1545124246_5c18b996ac30b.png!small)

同时使用RAS公钥加密的AES的key和iv等信息并写入到文件中，如下所示：

![](https://image.3001.net/images/20181218/1545124255_5c18b99fa7d07.png!small)

RSA加密过程，如下所示：

![](https://image.3001.net/images/20181218/1545124275_5c18b9b344ad9.png!small)

8.生成十个勒索信息超文本文件[0000-0009]-SORRY-FOR-FILES.html，同时删除原文件，如下所示：

![](https://image.3001.net/images/20181218/1545124284_5c18b9bccc699.png!small)

生成的勒索信息超文本文件，如下所示：

![](https://image.3001.net/images/20181218/1545124294_5c18b9c6b75e3.png!small)

文件内容如下所示：

![](https://image.3001.net/images/20181218/1545124307_5c18b9d3a3b12.png!small)

红框内容中的为之前传入的三个参数,相应的BTC钱包地址：

    
    
    1HbJu2kL4xDNK1L9YUDkJnqh3yiC119YM2

## 三、解决方案

深信服EDR产品能有效检测及防御此类勒索病毒家族样本及其变种，如下所示：

![](https://image.3001.net/images/20181218/1545124318_5c18b9de27ce8.png!small)

同时深信服EDR安全团队提醒广大用户：

> 1\. 不要点击来源不明的邮件附件，不从不明网站下载软件
>
> 2\. 及时给主机打补丁，修复相应的高危漏洞
>
> 3\. 对重要的数据文件定期进行非本地备份
>
> 4\. 尽量关闭不必要的文件共享权限以及关闭不必要的端口，如：445,135,139,3389等
>
> 5\. RDP远程服务器等连接尽量使用强密码，不要使用弱密码
>
> 6\. 安装专业的终端安全防护软件，为主机提供端点防护和病毒检测清理功能

 ***本文作者：千里目安全实验室，转载请注明来自FreeBuf.COM**

