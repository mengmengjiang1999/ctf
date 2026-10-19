## 一、样本简介

**Blackout勒索病毒家族是一款使用.NET语言编写的勒索病毒，它会将原文件名加密为BASE64格式的加密后的文件名，首次发现是在2017年7月份左右，样本使用了代码混淆的方式防止安全分析人员对样本进行静态分析，此次发现的Blackout勒索病毒样本经过分析确认是V3.0版本的Blackout家族最新变种样本，采用RSA+AES加密算法对文件进行加密，加密后的文件无法解密还原。**

## 二、详细分析

1.样本使用.NET语言进行编写，如下所示：

![1.png](https://image.3001.net/images/20181031/1540953872_5bd91710ccf4d.png!small)

2.反编译NET程序，样本经过了混淆处理，如下所示：

![2.png](https://image.3001.net/images/20181031/1540953881_5bd91719bd467.png!small)

3.样本去混淆，如下所示：

![3.png](https://image.3001.net/images/20181031/1540953889_5bd91721ca0d7.png!small)

经过调试发现此款Blackout勒索病毒是V3.0版本的最新变种样本blut3，如下所示：

![4.png](https://image.3001.net/images/20181031/1540953899_5bd9172bee02b.png!small)

4.获取磁盘驱动信息，如下所示：

![5.png](https://image.3001.net/images/20181031/1540953908_5bd917340fced.png!small)

5.通过RNGCryptoServiceProvider生成随机数，如下所示：

![6.png](https://image.3001.net/images/20181031/1540953916_5bd9173c18890.png!small)

生成结果，如下所示：

![7.png](https://image.3001.net/images/20181031/1540953924_5bd917443080b.png!small)

6.获取机器名，如下所示：

![8.png](https://image.3001.net/images/20181031/1540953934_5bd9174e3f5c5.png!small)

7.获取用户名，如下所示：

![9.png](https://image.3001.net/images/20181031/1540953942_5bd917564f719.png!small)

8.生成临时备份文件目录，如下所示：

![10.png](https://image.3001.net/images/20181031/1540953967_5bd9176f301a3.png!small)

9.设置Form窗体的属性，如下所示：

![11.png](https://image.3001.net/images/20181031/1540953978_5bd9177a9bebd.png!small)

10.获得需要加密的文件的后缀名列表，如下所示：

![12.png](https://image.3001.net/images/20181031/1540954005_5bd9179515661.png!small)

相应的文件名后缀如下所示：

>
> ".mdf",".db",".mdb",".sql",".pdb",".dsk",".fp3",".fdb",".accdb",".dbf",".crd",".db3",".dbk",".nsf",".gdb",".abs",".sdb",".sqlitedb",".edb",".sdf",".sqlite",".dbs",".cdb",".bib",".dbc",".usr",".dbt",".rsd",".myd",".pdm",".ndf",".ask",".udb",".ns2",".kdb",".ddl",".sqlite3",".odb",".ib",".db2",".rdb",".wdb",".tcx",".emd",".sbf",".accdr",".dta",".rpd",".btr",".vdb",".daf",".dbv",".fcd",".accde",".mrg",".nv2",".pan",".dnc",".dxl",".tdt",".accdc",".eco",".fmp",".vpd",".his",".fid"

11.获取当前进程信息，如下所示：

![13.png](https://image.3001.net/images/20181031/1540954016_5bd917a0dc985.png!small)

获得当前进程名，如下所示：

![14.png](https://image.3001.net/images/20181031/1540954028_5bd917aceb1ac.png!small)

12.获取主机进程信息，如下所示：

![15.png](https://image.3001.net/images/20181031/1540954041_5bd917b9617aa.png!small)

并判断主机操作系统平台，是否为XP,Win32NT，远程主机等，如下所示：

![16.png](https://image.3001.net/images/20181031/1540954060_5bd917cc04f18.png!small)

13.判断操作系统的语言版本包含如下字符串，如下所示：

![17.png](https://image.3001.net/images/20181031/1540954071_5bd917d73599a.png!small)

类型包含如下字符串，如下所示：

![18.png](https://image.3001.net/images/20181031/1540954085_5bd917e53a05a.png!small)

14.遍历相关进程，如下所示：

![19.png](https://image.3001.net/images/20181031/1540954096_5bd917f05c7a8.png!small)

然后结束上面相关进程，如下所示：

![20.png](https://image.3001.net/images/20181031/1540954107_5bd917fb97482.png!small)

相关进程列表，如下所示：

> taskmgr、sqlagent、sqlbrowser、sqlservr、sqlwriter、oracle、ocssd、dbsnmp、
>
> synctime、mydesktopqos、agntsvc.exeisqlplussvc、xfssvccon、mydesktopservice
>
> ocautoupds、agntsvc.exeagntsvc、agntsvc.exeencsvc、firefoxconfig、tbirdconfig
>
> ocomm、mysqld、sql、mysqld-nt、mysqld-opt、dbeng50、sqbcoreservice

15.拷贝自身到临时目录C:\Users\panda\AppData\Local\Temp\Adobe下，然后设置自启动注册表项，如下所示：

![21.png](https://image.3001.net/images/20181031/1540954121_5bd918090174a.png!small)

拷贝到相应的目录，如下所示：

![22.png](https://image.3001.net/images/20181031/1540954133_5bd918153d091.png!small)

16.生成RSA密钥，如下所示：

![23.png](https://image.3001.net/images/20181031/1540954146_5bd91822969f2.png!small)

生成的RSA密钥，如下：

    
    
    <RSAKeyValue><Modulus>gS1EQF1vkdTuplcqTNexJr+EgQa9g6tw7sSiirENylIC1YWaKWCf30pPPqkG3Djt7/gsnAbe3pJipn45QmiJk7zjytMuVi993nYV1wmy6Q9Y2hARIvmQdSPaPF83hHsZG8VQUj7zlhGkrYj4Kn+lG86x5lUlaT+3YnXnr0XqiV+JLDr7oZIZzDSIFgAFP6jy19x4lfkr8QJyisYPRh1SUSEyU8MBO9tcHLCMNtFUilio2gcZXup7nb1Kmq3mTupEHYVxhcSttOTJIJ6SDyzBGFQikp6Jbi8oNBmlVvltHnnQcCmmSHXonUKwMGhFIi2oIp8JGLRQXAOoP2bzs8If2Q==</Modulus><Exponent>AQAB</Exponent>
    </RSAKeyValue>

通过RSA密钥对Key进行加密处理，如下所示：

![24.png](https://image.3001.net/images/20181031/1540954161_5bd918316821a.png!small)

生成256位的加密密钥，如下所示：

![25.png](https://image.3001.net/images/20181031/1540954177_5bd9184171301.png!small)

密钥如下所示：

    
    
    5F29474544EBE54C25107EDC468548178FF209E96F9D00E228579E57A7233F37E1AA48F4EFDC5D31006F757507AC385477211F328596C1E1C5572A163C22765A3911FCF76AD74D48FEAB7E2E851E3FBF6CBDE211E8C6F3E9526885A3139C17EC53C66FDF5AEFE58EEBA9501EC0653D99E62F52002290066378A81302A3F022C7230DAD30FEB34971187764C93705DCBF5280B89A348533ECE4228D68A4A7BE9CE171BE51D97D48FEE3E53668FDA283D0ADA1EC6809EE0837F8ED094B4F6D744CCEAB4B0C24C2220FEA643F0B41E34165CC1A4DC03873D4E16045FFB9074AF0BB3C4D729E7607484BF858B5C82F65FE122EB2DC6A12721FA637B602752E70D90B

把密钥转化为Base64字符串，如下所示：

    
    
    "XylHRUTr5UwlEH7cRoVIF4/yCelvnQDiKFeeV6cjPzfhqkj079xdMQBvdXUHrDhUdyEfMoWWweHFVyoWPCJ2WjkR/Pdq101I/qt+LoUeP79sveIR6Mbz6VJohaMTnBfsU8Zv31rv5Y7rqVAewGU9meYvUgAikAZjeKgTAqPwIscjDa0w/rNJcRh3ZMk3Bdy/UoC4mjSFM+zkIo1opKe+nOFxvlHZfUj+4+U2aP2ig9CtoexoCe4IN/jtCUtPbXRMzqtLDCTCIg/qZD8LQeNBZcwaTcA4c9ThYEX/uQdK8Ls8TXKedgdIS/hYtcgvZf4SLrLcahJyH6Y3tgJ1LnDZCw=="

17.遍历磁盘，如下所示：

![26.png](https://image.3001.net/images/20181031/1540954194_5bd9185261c41.png!small)

排除以下目录下，相应的目录列表，如下所示：

WINDOWS、RECYCLER、Program Files、Program
Files(x86)、Windows、Recycle.Bin、RECYCLE.BIN、Recycler、TEMP、APPDATA、Temp、Appdata、ProgramData、Microsoft、Burn

18.加密相应的文件，循环遍历磁盘目录下的子文件，如下所示：

![27.png](https://image.3001.net/images/20181031/1540954209_5bd918610c211.png!small)

打开单个文件作为文件数据流，如下所示：

![28.png](https://image.3001.net/images/20181031/1540954231_5bd918771252e.png!small)

读取到的未加密的文件，如下所示：

![29.png](https://image.3001.net/images/20181031/1540954242_5bd918827d51f.png!small)

判断文件的后缀名是不是LNK后缀的，同时文件名字符串是否包含README_，如下所示：

![30.png](https://image.3001.net/images/20181031/1540954253_5bd9188d8c96e.png!small)

判断原文件的内容最后字节是否包含###,如下所示：

![31.png](https://image.3001.net/images/20181031/1540954269_5bd9189d69e21.png!small)

获取文件信息，如下所示：

![32.png](https://image.3001.net/images/20181031/1540954279_5bd918a77a8a6.png!small)

读取文件内容，如下所示：

![33.png](https://image.3001.net/images/20181031/1540954290_5bd918b2f41b7.png!small)

加密读取到的文件内容，如下所示：

![34.png](https://image.3001.net/images/20181031/1540954301_5bd918bd0995a.png!small)

相应的加密算法，如下所示：

![35.png](https://image.3001.net/images/20181031/1540954310_5bd918c6ca9b7.png!small)

使用的加密算法为AES+RSA密钥的方式，如下所示：

![36.png](https://image.3001.net/images/20181031/1540954319_5bd918cfdc30e.png!small)

将加密的数据，写入到原文件数据流中，如下所示：

![37.png](https://image.3001.net/images/20181031/1540954330_5bd918da2151c.png!small)

然后关闭数据流文件，把加密后的数据写入到原文件中，获取原文件的路径，如下所示：

![38.png](https://image.3001.net/images/20181031/1540954342_5bd918e602502.png!small)

生成新的文件名转化为Base64编码，如下所示：

![39.png](https://image.3001.net/images/20181031/1540954351_5bd918ef89907.png!small)

再将加密特征字符串写入到文件未尾，如下所示：

![40.png](https://image.3001.net/images/20181031/1540954365_5bd918fdba8b0.png!small)

然后替换到原文件，如下所示：

![41.png](https://image.3001.net/images/20181031/1540954379_5bd9190bb3bd0.png!small)

到此整个加密文件的过程如上所示。

19.加密后的文件，如下所示：

![42.png](https://image.3001.net/images/20181031/1540954392_5bd91918b6c99.png!small)

20.在每个加密文件目录下生成一个勒索信息文本文件README_[加密特征数字].txt，勒索相关信息，如下所示：

![43.png](https://image.3001.net/images/20181031/1540954402_5bd91922b397c.png!small)

## 三、解决方案

深信服EDR产品能有效检测及防御此类勒索病毒家族样本及其变种，如下所示：

![44.png](https://image.3001.net/images/20181031/1540954414_5bd9192e5fd9d.png!small)

深信服安全团队再次提醒广大用户，勒索病毒以防为主，目前大部分勒索病毒加密后的文件都无法解密，注意日常防范措施：

1.不要点击来源不明的邮件附件，不从不明网站下载软件

2.及时给主机打补丁(永恒之蓝漏洞补丁)，修复相应的高危漏洞

3.对重要的数据文件定期进行非本地备份

4.尽量关闭不必要的文件共享权限以及关闭不必要的端口，如：445,135,139,3389等

5.RDP远程服务器等连接尽量使用强密码，不要使用弱密码

6.安装专业的终端安全防护软件，为主机提供端点防护和病毒检测清理功能

 ***本文作者：千里目安全实验室，转载请注明来自FreeBuf.COM**

