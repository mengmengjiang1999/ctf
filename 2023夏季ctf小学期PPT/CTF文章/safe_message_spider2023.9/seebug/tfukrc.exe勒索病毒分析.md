**作者: Yenn_  
原文链接:[Wei's
Blog](https://0xdf1001f.github.io/2020/04/22/%E5%8B%92%E7%B4%A2%E7%97%85%E6%AF%9272ccc18f3038e19273010d45ac2142ce/)**

2019-09-09我发在CSDN，这里把我的文章copy过来。

萌新第一次分析病毒

# 基本信息

FileName | FileSize | FileType | MD5  
---|---|---|---  
tfukrc.exe | 240,640 Byte | 勒索病毒 | 72ccc18f3038e19273010d45ac2142ce  
  
# 简介

该病毒感染受害主机后，会先创建COM对象来达到反沙箱的效果，删除自己备用数据流，从自身解密出将会使用的代码及字符串，检查TOKEN信息，尝试提权，然后将自己拷贝重命名为随机字符串到”MyDocument”目录下后再删除自身，监控杀死部分进程CMD、Procexp、mscconfig、regedit、Taskmgr，创建一个优先级最低的线程遍历全盘指定后缀加密文件，在所有文件夹下都会新建勒索信息的txt和png，最后会删除卷影拷贝，然后将用户信息加密后发送出去

# 流程图

[![img](https://images.seebug.org/content/images/2021/03/17/1615973337000-1bnpgn.png-w331s)](https://img-blog.csdnimg.cn/20190909114302668.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3lhb3dhbmc5OTU=,size_16,color_FFFFFF,t_70)

# 详细分析

第一个函数先使用开始时间作为种子，生成一个随机数，用于生成随机字符串，这个字符串是后面病毒拷贝时的名称

[![img](https://images.seebug.org/content/images/2021/03/17/1615973337000-3mqoxr.png-w331s)](https://img-blog.csdnimg.cn/20190909114311396.png)

[![img](https://images.seebug.org/content/images/2021/03/17/1615973337000-5dnapu.png-w331s)](https://img-blog.csdnimg.cn/20190909114315109.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3lhb3dhbmc5OTU=,size_16,color_FFFFFF,t_70)

创建COM对象，使用COM库中的DirectShow相关音频代码来检测沙箱

[![img](https://images.seebug.org/content/images/2021/03/17/1615973337000-7nvmuf.png-w331s)](https://img-blog.csdnimg.cn/20190909114322148.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3lhb3dhbmc5OTU=,size_16,color_FFFFFF,t_70)

得到自己文件的路径，并且拼接字符串，拼接出文件的备用数据流:Zone.Identifier,并且删除文件的备用数据流，用于关闭弹窗警告

[![img](https://images.seebug.org/content/images/2021/03/17/1615973338000-9ftjtf.png-w331s)](https://img-blog.csdnimg.cn/20190909114328844.png) 获取到”MyDocument”我的文档路径，后面拷贝文件会用到

[![img](https://images.seebug.org/content/images/2021/03/17/1615973338000-11dduob.png-w331s)](https://img-blog.csdnimg.cn/20190909114334761.png)

得到Wow64DisableWow64FsRedirection,解决32位与64位重定向的问题

[![img](https://images.seebug.org/content/images/2021/03/17/1615973338000-13xzhon.png-w331s)](https://img-blog.csdnimg.cn/20190909114337287.png)

## 解密字符串

解密出病毒后面运行会使用的相关字符串

[![img](https://images.seebug.org/content/images/2021/03/17/1615973338000-15eitlw.png-w331s)](https://img-blog.csdnimg.cn/20190909114342640.png)

第一次申请内存，解密出病毒将要加密文件的后缀，并将后缀放在一块申请的内存中，然后将内存的地址赋给一个变量

[![img](https://images.seebug.org/content/images/2021/03/17/1615973338000-17oqqea.png-w331s)](https://img-blog.csdnimg.cn/20190909114350681.png)

解密出的文件后缀

[![img](https://images.seebug.org/content/images/2021/03/17/1615973339000-19hpuyq.png-w331s)](https://img-blog.csdnimg.cn/20190909114354684.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3lhb3dhbmc5OTU=,size_16,color_FFFFFF,t_70)

重新申请一块内存空间，将内存地址赋值给变量

[![img](https://images.seebug.org/content/images/2021/03/17/1615973339000-21hdmge.png-w331s)](https://img-blog.csdnimg.cn/20190909114358456.png)

跟随变量中的内存地址，可以再次看见后缀，后面会使用后缀判断是否加密文件

[![img](https://images.seebug.org/content/images/2021/03/17/1615973339000-23zzrgr.png-w331s)](https://img-blog.csdnimg.cn/20190909114401591.png)

[![img](https://images.seebug.org/content/images/2021/03/17/1615973339000-25drwim.png-w331s)](https://img-blog.csdnimg.cn/20190909114404334.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3lhb3dhbmc5OTU=,size_16,color_FFFFFF,t_70)

文件后缀列表如下：

.r3d | .forge | .wpd | .menu | .rofl | .x1k | .iwd | .hvp1 | .qic | .mrwref  
---|---|---|---|---|---|---|---|---|---  
.ptx | .asset | .rtf | .ncf | .dba | .ppt | .kf | .icxs | .bkp | .nrw  
.pef | .1itemod | .wb2 | .sid | .db0 | .pptx | .mlx | .docm | .bc7 | .orf  
.x3f | .iwi | .pfx | .sis | .kdb | .pptm | .fpk | .WpS | .bc6 | .raw  
.srw | .das | .p12 | .ztmp | .mpqge | .mdb | .dazip | .x1s | .pkpass | .rw1  
.der | .upk | .p7b | .vdf | .vfs0 | .accdb | .vtf | .x1sx | .tax.gdb | .rw2  
.cer | .d3dbsp | .p7c | .mov | .mcmeta | .pst | .vcf | .x1sm | .qdf | .mdf  
.crt | .csv | .txt | .fos | .m2 | .dwg’ | .esm | .x1sb | .t12 | .dbf  
.pem | .wIV | .ipeg | .sb | .1rf | .xf | .blob | .wallet | .t13 | .psd  
.odt | .avi | .png | .itm | .vpppc | .dxg | .drmp | .big | .bsa | .mdbackup  
.ods | .wma | .rb | .wmo | .ff | .pdd | .layout | .pak | .1tx | .hkdb  
.odm | .m4a | .cSS | .itm | .cfr | .pdf | .dcr | .rgss3a | .sr2 | .hplg  
.odp | .rar | .js | .map | .snx.1vl | .eps | .ai | .epk | .bay | .sum.sie  
.odc | .7z | .flv | .WTmO | .arch00 | .jpg | .indd | .bik | .crw | .zip  
.odb | .mp4 | .m3u’ | .sb | .ntl | .jpe | .cdr | .slm | .cr2 | .w3x  
.doc | .sql | .py | .svg | .fsh | .dng | .erf | .1bf | .sidd | .rim  
.docx | .balk | .desc | .cas | .itdb | .3fr | .bar | .sav | .sidn | .psk  
.kdc | .tiff | .xxx | .gho | .itl | .arw | .hkx | .re4 | .bkf | .tor  
.mef | w.ibank | .litesql | .symcdb | .mddata | .srf | .raf | .apk | .vpk |  
  
第二次申请内存，解密出创建勒索信息文本的.txt和.png相关的字符串

[![img](https://images.seebug.org/content/images/2021/03/17/1615973339000-27knubg.png-w331s)](https://img-blog.csdnimg.cn/20190909114412133.png)

[![img](https://images.seebug.org/content/images/2021/03/17/1615973339000-29fgthr.png-w331s)](https://img-blog.csdnimg.cn/20190909114415293.png)

同样，将揭密出的字符串放在一块新申请的内存中，然后将内存地址放在变量中，后面执行代码会用到这些字符串

[![img](https://images.seebug.org/content/images/2021/03/17/1615973340000-31iuiez.png-w331s)](https://img-blog.csdnimg.cn/20190909114419334.png)

[![img](https://images.seebug.org/content/images/2021/03/17/1615973340000-33tntsx.png-w331s)](https://img-blog.csdnimg.cn/20190909114422784.png)

[![img](https://images.seebug.org/content/images/2021/03/17/1615973340000-35rijpa.png-w331s)](https://img-blog.csdnimg.cn/20190909114425611.png)

第三次申请内存，解密出病毒执行的部分代码字符串，包括删除卷影拷贝、监视的进程名、修改注册表等

[![img](https://images.seebug.org/content/images/2021/03/17/1615973340000-37ipwva.png-w331s)](https://img-blog.csdnimg.cn/20190909114429603.png)

[![img](https://images.seebug.org/content/images/2021/03/17/1615973340000-39djuqs.png-w331s)](https://img-blog.csdnimg.cn/20190909114432411.png)

第三次同样也会将解密出的字符串放在新申请的内存中，然后将内存的地址放在一个变量中，以便后边代码使用

[![img](https://images.seebug.org/content/images/2021/03/17/1615973340000-41sfcyo.png-w331s)](https://img-blog.csdnimg.cn/2019090911443615.png)

[![img](https://images.seebug.org/content/images/2021/03/17/1615973341000-43rddxd.png-w331s)](https://img-blog.csdnimg.cn/20190909114441138.png)
[![img](https://images.seebug.org/content/images/2021/03/17/1615973341000-45wobty.png-w331s)](https://img-blog.csdnimg.cn/20190909114445530.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3lhb3dhbmc5OTU=,size_16,color_FFFFFF,t_70)

第四次申请内存，解密出与病毒上传加密后的主机信息的HTTP相关的字符串

[![img](https://images.seebug.org/content/images/2021/03/17/1615973341000-47wbvqe.png-w331s)](https://img-blog.csdnimg.cn/20190909114503102.png)
[![img](https://images.seebug.org/content/images/2021/03/17/1615973341000-49vppof.png-w331s)](https://img-blog.csdnimg.cn/20190909114522820.png)

也会将这一部分揭密出的字符串放在一个新申请的内存中，然后将内存地址放在变量中，在后面的代码执行时使用。

[![img](https://images.seebug.org/content/images/2021/03/17/1615973341000-51capwl.png-w331s)](https://img-blog.csdnimg.cn/20190909114511853.png)

[![img](https://images.seebug.org/content/images/2021/03/17/1615973342000-53nqjgs.png-w331s)](https://img-blog.csdnimg.cn/20190909114513962.png)
[![img](https://images.seebug.org/content/images/2021/03/17/1615973342000-55brcmx.png-w331s)](https://img-blog.csdnimg.cn/20190909114516967.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3lhb3dhbmc5OTU=,size_16,color_FFFFFF,t_70)

第五次申请内存，解密出勒索文本，用在后面创建勒索文件

[![img](https://images.seebug.org/content/images/2021/03/17/1615973342000-57bjwuy.png-w331s)](https://img-blog.csdnimg.cn/20190909114535795.png)

[![img](https://images.seebug.org/content/images/2021/03/17/1615973342000-59quxot.png-w331s)](https://img-blog.csdnimg.cn/20190909114538871.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3lhb3dhbmc5OTU=,size_16,color_FFFFFF,t_70)

## 查询TOKEN信息

字符串解密完成后，利用GetTokenInformation获取进程的权限级别

[![img](https://images.seebug.org/content/images/2021/03/17/1615973342000-61ijebp.png-w331s)](https://img-blog.csdnimg.cn/20190909114543545.png)
[![img](https://images.seebug.org/content/images/2021/03/17/1615973343000-63iqpvn.png-w331s)](https://img-blog.csdnimg.cn/20190909114546896.png)

通过查询GetTokenInformation中的TokenIntegrityLevel查询程序运行的完整性级别，包、

括Untrust， Low， Medium， Hight， System等， 级别越低，权限也就越低，当权限不足时，使用RUNAS以管理员运行

[![img](https://images.seebug.org/content/images/2021/03/17/1615973343000-65esnlp.png-w331s)](https://img-blog.csdnimg.cn/20190909114551829.png)

## 查询所在目录

当权限足够时，会查询自己是否在”MyDocument”我的文档目录下，当自己存在于我的文档下时，会直接返回，运行后边的恶意代码

[![img](https://images.seebug.org/content/images/2021/03/17/1615973343000-67qmrkb.png-w331s)](https://img-blog.csdnimg.cn/20190909114555532.png)

## 拷贝自身创建新进程

当自己不存在于我的文档目录下时，会将自己拷贝到我的文档目录下一个随机字符串的.exe，并将设为隐藏属性，拷贝完成后会创建新线程调用拷贝后的文件，完成后再调用CMD.exe删除原来的病毒本身

[![img](https://images.seebug.org/content/images/2021/03/17/1615973343000-69bioml.png-w331s)](https://img-blog.csdnimg.cn/20190909114559490.png)

[![img](https://images.seebug.org/content/images/2021/03/17/1615973343000-71regjw.png-w331s)](https://img-blog.csdnimg.cn/20190909114602921.png)

[![img](https://images.seebug.org/content/images/2021/03/17/1615973343000-73rzlwi.png-w331s)](https://img-blog.csdnimg.cn/20190909114607977.png)

## 查询操作系统信息

新的病毒进程也会重复以上检测自己是否存在于”MyDocument”我的文档目录下，当存在时，直接运行后面的代码,将一块内存全设为0，然后用来保存获取到的系统信息

[![img](https://images.seebug.org/content/images/2021/03/17/1615973344000-75narmh.png-w331s)](https://img-blog.csdnimg.cn/2019090911461253.png)

## 查询自身CheckSum

病毒会通过偏移查询自己的CheckSum，然后保存在变量中，最后返回值的451

[![img](https://images.seebug.org/content/images/2021/03/17/1615973344000-77vwzpw.png-w331s)](https://img-blog.csdnimg.cn/20190909114615860.png)

[![img](https://images.seebug.org/content/images/2021/03/17/1615973344000-79qsefo.png-w331s)](https://img-blog.csdnimg.cn/20190909114618239.png)

## 提权

病毒会先从解密的字符串中得到SeDebugPrivilege字符串，然后当作参数传入提权，查询系统的TOKEN信息，然后将自己提权SeDebugPrivilege权限

[![img](https://images.seebug.org/content/images/2021/03/17/1615973344000-81ghovy.png-w331s)](https://img-blog.csdnimg.cn/20190909114623605.png)

[![img](https://images.seebug.org/content/images/2021/03/17/1615973344000-83pdyxd.png-w331s)](https://img-blog.csdnimg.cn/20190909114625627.png)

[![img](https://images.seebug.org/content/images/2021/03/17/1615973344000-85fnztf.png-w331s)](https://img-blog.csdnimg.cn/2019090911462829.png)

## 监控杀死指定进程

病毒提权后，会创建一个新线程，用来监控当前运行的进程，当出现指定进程时，就关闭指定进程，进程名来自前面解密出的字符串

[![img](https://images.seebug.org/content/images/2021/03/17/1615973345000-87hjpaf.png-w331s)](https://img-blog.csdnimg.cn/20190909114632188.png)

监控的进程包括：

![](https://images.seebug.org/content/images/2021/03/b42130aa-5227-4be9-a627-4b5879ac1ffc.png-w331s)

## 删除卷影拷贝

病毒会判断当前系统的DwBuildNumber版本号，如果操作系统不是XP2600版本就会执行命令，创建新线程删除卷影拷贝，执行的命令也是从前面解密出的字符串取得

[![img](https://images.seebug.org/content/images/2021/03/17/1615973345000-89tlhau.png-w331s)](https://img-blog.csdnimg.cn/20190909114638400.png)

[![img](https://images.seebug.org/content/images/2021/03/17/1615973345000-91gdhtf.png-w331s)](https://img-blog.csdnimg.cn/20190909114640970.png)

## 取得桌面路径

返回桌面路径，用在后面创建勒索文本和图片

[![img](https://images.seebug.org/content/images/2021/03/17/1615973345000-93ljrbx.png-w331s)](https://img-blog.csdnimg.cn/20190909114644866.png)

## 修改注册表，生成密钥并加密

病毒会在注册表下HKCU\Software\新建一个MSVV项，写入用户的ID

[![img](https://images.seebug.org/content/images/2021/03/17/1615973345000-95olfzs.png-w331s)](https://img-blog.csdnimg.cn/20190909114648876.png)
然后在HKCU\Software\以用户ID命名的新项，其中写入的值data一共分为四段，是在Mydocument下的Recover+file.txt中加密前的内容，后面病毒会将这一块数据加密后发回服务器

这四段数据第一段是addr，第二段是dh，第三段是用户ID，第四段是OS版本号

[![img](https://images.seebug.org/content/images/2021/03/17/1615973345000-97kiwml.png-w331s)](https://img-blog.csdnimg.cn/20190909114652598.png)

[![img](https://images.seebug.org/content/images/2021/03/17/1615973345000-99xterw.png-w331s)](https://img-blog.csdnimg.cn/20190909114654861.png)

注册表添加完成后，会生成一次密钥，使用CryptGenRandom()函数获取随机数，经过CSP生成一个256位的密钥

[![img](https://images.seebug.org/content/images/2021/03/17/1615973346000-101ddglz.png-w331s)](https://img-blog.csdnimg.cn/20190909114700374.png)

再获取进程、线程、时间等信息，将密钥加密

[![img](https://images.seebug.org/content/images/2021/03/17/1615973346000-103uznpy.png-w331s)](https://img-blog.csdnimg.cn/20190909114704200.png)

得到密钥后，再经过Secp256k1加密一次，得到一个加密后的密钥

[![img](https://images.seebug.org/content/images/2021/03/17/1615973346000-105azkim.png-w331s)](https://img-blog.csdnimg.cn/20190909114707283.png)

## 自动启动

病毒在注册表HKCU\Software\Microsoft\Windows\CurrentVersion\Run路径下，新建了名称为”+++随机四位字母”的注册表值，数据为调用CMD
/C 自启执行“MyDocument”下的病毒

[![img](https://images.seebug.org/content/images/2021/03/17/1615973346000-107exjua.png-w331s)](https://img-blog.csdnimg.cn/20190909114711454.png)

[![img](https://images.seebug.org/content/images/2021/03/17/1615973346000-109stxxj.png-w331s)](https://img-blog.csdnimg.cn/20190909114713845.png)

## 创建+recover+file.txt文件

病毒先获得我的文档路径

[![img](https://images.seebug.org/content/images/2021/03/17/1615973347000-111rgepc.png-w331s)](https://img-blog.csdnimg.cn/20190909114719621.png)

然后将前面获得的数据拼接在一起，这里的数据和注册表data项中的值一样，不过后面写入文件的时候会加密，分别是作者自己定义的addr、dh还有被勒索的用户ID，系统版本号

[![img](https://images.seebug.org/content/images/2021/03/17/1615973347000-113hmmho.png-w331s)](https://img-blog.csdnimg.cn/20190909114722175.png)

病毒会生成一个密钥，将这段数据加密，然后写入+recover+file.xtx中

[![img](https://images.seebug.org/content/images/2021/03/17/1615973347000-115jrpuz.png-w331s)](https://img-blog.csdnimg.cn/20190909114731194.png)

[![img](https://images.seebug.org/content/images/2021/03/17/1615973347000-117umlft.png-w331s)](https://img-blog.csdnimg.cn/20190909114734418.png)

## 加密

病毒会创建一个新线程，并且将线程的优先级设置到最低，然后用这个线程来加密文件

[![img](https://images.seebug.org/content/images/2021/03/17/1615973347000-119rgutd.png-w331s)](https://img-blog.csdnimg.cn/20190909114739418.png)

病毒会从A:\ B:\开始遍历所有磁盘

[![img](https://images.seebug.org/content/images/2021/03/17/1615973347000-121dkluu.png-w331s)](https://img-blog.csdnimg.cn/20190909114744836.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3lhb3dhbmc5OTU=,size_16,color_FFFFFF,t_70)

当遍历到软盘、硬盘或网络磁盘的时候，获取到硬盘信息，然后准备加密文件

[![img](https://images.seebug.org/content/images/2021/03/17/1615973347000-123zhplv.png-w331s)](https://img-blog.csdnimg.cn/20190909114749269.png)

病毒先会遍历主机上所有目录，在每一个目录下先创建”+REcovER+随机字符串+”的txt和PNG文件

[![img](https://images.seebug.org/content/images/2021/03/17/1615973348000-125kysrp.png-w331s)](https://img-blog.csdnimg.cn/20190909114753352.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3lhb3dhbmc5OTU=,size_16,color_FFFFFF,t_70)

在每个目录下创建完成后，才开始加密文件，病毒会先获取文件的名称，保存在变量中

[![img](https://images.seebug.org/content/images/2021/03/17/1615973348000-127zeuii.png-w331s)](https://img-blog.csdnimg.cn/2019090911475872.png)

病毒判断文件不是.com文件，不是病毒写入的勒索信息文本，然后将所有文件名与前面解密出的后缀匹配，加密相应文件

[![img](https://images.seebug.org/content/images/2021/03/17/1615973348000-129ecaws.png-w331s)](https://img-blog.csdnimg.cn/20190909114801824.png)

病毒先得到进程的堆句柄，然后用堆句柄申请一块空间

[![img](https://images.seebug.org/content/images/2021/03/17/1615973348000-131skzcg.png-w331s)](https://img-blog.csdnimg.cn/20190909114806391.png)

[![img](https://images.seebug.org/content/images/2021/03/17/1615973348000-133wiyhd.png-w331s)](https://img-blog.csdnimg.cn/2019090911480922.png)

判断文件大小，

[![img](https://images.seebug.org/content/images/2021/03/17/1615973348000-135vlkwi.png-w331s)](https://img-blog.csdnimg.cn/20190909114812962.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3lhb3dhbmc5OTU=,size_16,color_FFFFFF,t_70)

开始加密时，先读取要加密文件的数据

[![img](https://images.seebug.org/content/images/2021/03/17/1615973348000-137gvkyg.png-w331s)](https://img-blog.csdnimg.cn/20190909114816701.png)

将前面使用Secp256k1加密后的密钥拷贝32字节到新值中

[![img](https://images.seebug.org/content/images/2021/03/17/1615973349000-139pfwud.png-w331s)](https://img-blog.csdnimg.cn/20190909114820254.png)

将新密钥经过轮函数得到一个新密钥

[![img](https://images.seebug.org/content/images/2021/03/17/1615973349000-141mgmld.png-w331s)](https://img-blog.csdnimg.cn/20190909114823670.png) 将读取到的文件数据在申请的堆空间里加密

[![img](https://images.seebug.org/content/images/2021/03/17/1615973349000-143yagmu.png-w331s)](https://img-blog.csdnimg.cn/20190909114826854.png)

加密完成后将数据保存在堆空间中然后将文件指针移动到文件开头，在开头写入垃圾数据

[![img](https://images.seebug.org/content/images/2021/03/17/1615973349000-145qyqpn.png-w331s)](https://img-blog.csdnimg.cn/2019090911483227.png)

最后将堆空间加密后的内容写入文件，然后刷新保存在硬盘

[![img](https://images.seebug.org/content/images/2021/03/17/1615973349000-147vzirw.png-w331s)](https://img-blog.csdnimg.cn/20190909114836339.png)

## 创建打开勒索文本

在病毒加密完成后，会在桌面创建勒索信息的txt和png文件，然后打开他们

[![img](https://images.seebug.org/content/images/2021/03/17/1615973350000-149rtxtt.png-w331s)](https://img-blog.csdnimg.cn/20190909114840488.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3lhb3dhbmc5OTU=,size_16,color_FFFFFF,t_70)

## 发送信息到服务器

病毒会将用户的各项信息加密后发送到指定前面解密出的URL中

加密前的数据，包括的用户的个人ID和系统版本号等信息

[![img](https://images.seebug.org/content/images/2021/03/17/1615973350000-151nnjyj.png-w331s)](https://img-blog.csdnimg.cn/20190909114845777.png)

将发送的信息加密

[![img](https://images.seebug.org/content/images/2021/03/17/1615973351000-153tyolr.png-w331s)](https://img-blog.csdnimg.cn/20190909114849337.png)

拼接出HTTP请求头后用POST发送到指定URL

[![img](https://images.seebug.org/content/images/2021/03/17/1615973351000-155akpec.png-w331s)](https://img-blog.csdnimg.cn/20190909114852271.png)

## 删除自身

运行完成后会调用CMD执行/C DEL删除自身

[![img](https://images.seebug.org/content/images/2021/03/17/1615973351000-157vkjia.png-w331s)](https://img-blog.csdnimg.cn/2019090911485669.png)

[![img](https://images.seebug.org/content/images/2021/03/17/1615973351000-159lftfc.png-w331s)](https://img-blog.csdnimg.cn/20190909114858205.png)

# 样本溯源

FileName | FileSize | MD5  
---|---|---  
tfukrc.exe | 240,640 Byte | 72ccc18f3038e19273010d45ac2142ce  
随机字符串.exe | 240,640Byte | 72ccc18f3038e19273010d45ac2142ce  
+recover+file.txt | 256 Byte | 3aa3bfac733afd6311334c551f3f7c09  
+REcovER+随机字符串+.txt | 2,459 Byte | 072c1e92f6f35ce4f895e337b9093490  
+REcovER+随机字符串+.png | 74,272 Byte | dec3149215bd95e2abf13bea6aefc862  
  
**URL：**  
<http://uideoaminproduktion.de/plugins/binstr.php>  
<http://clubsaintandre.fr/images/binstr.php>
<http://affiliateproductes.com/binstr.php>  
<http://ptgp.pl/tmp/binstr.php>  
<http://strategicdisaster.info/wordpress/wp-content/plugins/binstr.php>
<http://minteee.com/images/binstr.php>  
<http://uj5nj.onanwhit.com/>用户ID  
<http://2gdb4.leoraorage.at/>用户ID  
<http://9hrds.wolfcrap.at/>用户ID  
TOR URL：  
k7tlx3ghr3m4n2tu.onion/16751E6C29B615

# 查杀方案

删除我的文档下隐藏的病毒文件

删除启动项HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run下随机字符串启动项

删除注册表HKCU\Software\MSVV

删除注册表HKCU\Software\随机字符串（用户ID）项

已被加密文件暂无方法

# 总结

病毒在计算机中勒索所有指定后缀的文件，且制造大量无意义的勒索信息文件，加密中先使用系统信息等生成的随机数再利用Secp256k1非对称加密得到一个密钥再将密钥多次加密得到就加密文件的密钥，这样密钥不易被猜解。最好的办法是提高防范意识，不随意点开来意不明的exe文件。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1513/>

