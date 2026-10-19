## 前言

**BlackHeart(黑心)勒索病毒家族是一款使用NET语言进行编写的勒索病毒，之前深信服EDR安全团队已经报道过它的变种家族样本捆绑知名的远程软件AnyDesk进行传播，此次深信服EDR安全团队发现的是它的一个家族的最新的变种，加密算法仍然使用AES+RSA，加密后的文件无法还原，加密后的文件后缀名为mariacbc。**

## 一、样本简介

BlackHeart(黑心)勒索病毒也是SF勒索病毒家族成员之一，SF家族的勒索病毒，一共有如下几类：

> Spartacus(斯巴达克斯勒索病毒)
>
> Satyr(萨克斯勒索病毒)
>
> BlackRouter(BlackRouter勒索病毒)
>
> BlackHeart(黑心勒索病毒)

它们都采用NET语言进行编写，并使用了相似的加密核心代码进行勒索加密，统称为SF勒索家族。

## 二、详细分析

1、样本仍然采用之前的B字图标，同时也是使用NET语言进行编写的，如下所示：

![使用NET语言进行编写](https://image.3001.net/images/20181106/1541506667_5be1866b4ebce.png!small)

2、程序的入口函数，如下所示：

![程序的入口函数](https://image.3001.net/images/20181106/1541506673_5be1867170fd0.png!small)

3、生成唯一的AES的KEY，如下所示：

![生成唯一的AES的KEY](https://image.3001.net/images/20181106/1541506685_5be1867d3a98e.png!small)

4、再利用RSA2048的公钥Key加密之后生成的AES的Key，然后再转化为BASE64编码，如下所示：

![再转化为BASE64编码](https://image.3001.net/images/20181106/1541506693_5be18685dcd3e.png!small)

生成的加密的Key，如下所示：

    
    
    "mox1nR9OkprIdiwITblhpiD0XclNiMcMMNaP18mqVN1bkmsALjPThj9ckRNKC1uriLkOzc9BqAsgdLcNpmAJ/OPZDzKZhLsNv5GZAZotlMPX/gZzXvNvXqzKIxTxBv5NLzawTeyQuOuZMeU6gcuZdPThNItes0oFGsozxzsZCWuJoQuoXlfVDHnJC8dNGJ1+/EswCIB9jl5Hov0j9BNnwqOaKaTDJWYqayvKY4dnt14moA2ZzODVarydgHOit7CcJLGjCEijXV4Shrz8LkiBfKcH+haDcNWtT4EXT+zGae4DiAUIrAm+FPwLOuodHdrJwflJgkfawnXZA/6Emv/Vbw=="

5、遍历主机相关目录，进行加密操作，如下所示：

![进行加密操作](https://image.3001.net/images/20181106/1541506704_5be1869011ed4.png!small)

遍历的目录，如下所示：

![遍历的目录](https://image.3001.net/images/20181106/1541506713_5be186997242d.png!small)

相应的目录列表，如下所示：

    
    
    %Desktop%
    
    %Documents%
    
    %Music%
    
    %History%
    
    %Downloads%
    
    %Pictures%
    
    %Videos%
    
    %Favorites%
    
    %UserProfile%
    
    %ProgramData%
    
    %SystemRoot%\Users

6、遍历目录下的文件，如下所示：

![遍历目录下的文件](https://image.3001.net/images/20181106/1541506722_5be186a22491f.png!small)

判断文件的后缀名是否在相应的需要加密的文件的后缀名列表中，如下所示：

![在相应的需要加密的文件的后缀名列表中](https://image.3001.net/images/20181106/1541506731_5be186ab94a35.png!small)

勒索病毒会加密的文件后缀名列表，如下所示：

    
    
    ".exe",".der",".pfx",".key",".crt",".csr",".p12",".pem",".odt",".sxw",".stw",".3ds",".max",".3dm",".ods",".sxc",".stc",".dif",".slk",".wb2",".odp",".sxd",".std",".sxm",".sqlite3",".sqlitedb",".sql",".accdb",".mdb",".dbf",".odb",".mdf",".ldf",".cpp",".pas",".asm",".cmd",".bat",".vbs",".sch",".jsp",".php",".asp",".java",".jar",".class",".mp3",".wav",".swf",".fla",".wmv",".mpg",".vob",".mpeg",".asf",".avi",".mov",".mp4",".mkv",".flv",".wma",".mid",".m3u",".m4u",".svg",".psd",".tiff",".tif",".raw",".gif",".png",".bmp",".jpg",".jpeg",".iso",".backup",".zip",".rar",".tgz",".tar",".bak",".ARC",".vmdk",".vdi",".sldm",".sldx",".sti",".sxi",".dwg",".pdf",".wk1",".wks",".rtf",".csv",".txt",".msg",".pst",".ppsx",".ppsm",".pps",".pot",".pptm",".pptx",".ppt",".xltm",".xltx",".xlc",".xlm",".xlt",".xlw",".xlsb",".xlsm",".xlsx",".xls",".dotm",".dot",".docm",".docx",".doc",".ndf",".pdf",".ib",".ibk"

7、加密文件，使用AES加密算法，密钥KEY为之前通过RSA2048公钥加密后的KEY，对文件进行加密，同时将文件的后缀名变为mariacbc，如下所示：

![加密文件](https://image.3001.net/images/20181106/1541506741_5be186b550a54.png!small)

相应的加密算法，使用AESECB加密算法如下所示：

![加密算法](https://image.3001.net/images/20181106/1541506750_5be186be8d7ba.png!small)

加密后的文件，如下所示：

![加密后的文件](https://image.3001.net/images/20181106/1541506909_5be1875da239d.png!small)

8、遍历主机磁盘文件目录下的文件进行加密，如下所示：

![进行加密](https://image.3001.net/images/20181106/1541506957_5be1878d3d6a0.png!small)

9、删除磁盘卷影操作，如下所示：

![删除磁盘卷影操作](https://image.3001.net/images/20181106/1541506975_5be1879f3f71d.png!small)

10、生成勒索信息对话框，如下所示：

![生成勒索信息对话框](https://image.3001.net/images/20181106/1541507006_5be187be20cf0.png!small)

相应的勒索对话框，如下所示：

![相应的勒索对话框](https://image.3001.net/images/20181106/1541507030_5be187d6e859e.png!small)

11、遍历主机磁盘，在相应的文件目录下，生成勒索信息文本文件ReadME-M@r1a.txt，如下所示：

![遍历主机磁盘](https://image.3001.net/images/20181106/1541507038_5be187dedab4c.png!small)

## 三、解决方案

深信服安全团队再次提醒广大用户，勒索病毒以防为主，目前大部分勒索病毒加密后的文件都无法解密，注意日常防范措施：

> 1、不要点击来源不明的邮件附件，不从不明网站下载软件
>
> 2、及时给主机打补丁(永恒之蓝漏洞补丁)，修复相应的高危漏洞
>
> 3、对重要的数据文件定期进行非本地备份
>
> 4、尽量关闭不必要的文件共享权限以及关闭不必要的端口，如：445,135,139,3389等
>
> 5、RDP远程服务器等连接尽量使用强密码，不要使用弱密码
>
> 6、安装专业的终端安全防护软件，为主机提供端点防护和病毒检测清理功能

 ***本文作者：千里目安全实验室，转载请注明来自FreeBuf.COM**

