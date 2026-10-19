**毫无疑问，在目前的网络威胁领域中，勒索软件仍然扮演着十分重要的角色。实际上，在2018年上半年勒索软件的活动还有所增加，并且相关勒索软件还通过各种升级更新来尝试避开现有的安全解决方案，比如说PyLocky（趋势科技将其标记为RANSOM_PYLOCKY.A）就是一个很好的例子。**

在7月下旬和整个8月份，研究人员发现了一个通过垃圾邮件来传播PyLocky勒索软件的攻击活动。虽然PyLocky的勒索信息风格跟Locky非常相似，但是PyLocky跟Locky并没有什么关系。PyLocky采用Python编写，并采用PyInstaller封装。实际上，采用Python来开发的勒索软件并不是什么新鲜事了，比如说2016年的CryPy（RANSOM_CRYPY.A），和2017年的Pyl33t
(RANSOM_CRYPPYT.A)，但是PyLocky具备了反机器学习的能力，这也是它的“闪光点”之一。它同时使用了Inno Setup
Installer（一款基于开源脚本的安装器）和PyInstaller，因此这样会增加静态分析方法的检测难度，其中就包括了基于机器学习的解决方案。

需要注意的是，PyLocky的传播地区也比较集中，我们发现该活动主要针对的是欧洲地区的用户，尤其是法国。

![2.png](https://image.3001.net/images/20181013/1539444719_5bc20fef750fa.png!small)![3.png](https://image.3001.net/images/20181013/1539444719_5bc20fefa6a97.png!small)

## 感染链

8月2日，我们检测到了一波针对法国企业的PyLocky攻击活动，该活动中攻击者主要通过以发票为主题的垃圾邮件来引诱目标用户感染勒索软件。在电子邮件中，攻击者使用了社会工程学技术来诱使用户点击恶意链接，而恶意链接会将用户重定向到包含了PyLocky勒索软件的恶意URL。

![4.png](https://image.3001.net/images/20181013/1539444731_5bc20ffbbdcc1.png!small)

恶意URL指向的是一个包含了已签名可执行文件(Facture_23100.31.07.2018.exe)的ZIP文件(Facture_23100.31.07.2018.zip)。成功运行之后，Facture_23100.31.07.2018.exe会让目标主机感染恶意组件（一些C++文件、Python库和Python
2.7核心动态链接库DLL），以及主要的勒索程序（lockyfud.exe，通过PyInstaller创建，存放目录为C:\Users\\{user}\AppData\Local\Temp\is-{random}.tmp）。

![5.png](https://image.3001.net/images/20181013/1539444741_5bc21005ec207.png!small)![6.png](https://image.3001.net/images/20181013/1539444742_5bc21006195d5.png!small)

PyLocky能够加密图片、视频、文档、音频、程序、游戏、数据库文件和压缩文档等等。下面给出的是PyLocky可加密的文件类型：

    
    
    .dat,.keychain, .sdf, .vcf, .jpg, .png, .tiff, .gif, .jpeg, .jif, .jp2, .jpx, .j2k,.j2c, .fpx, .pcd, .bmp, .svg, .3dm, .3ds, .max, .obj, .dds, .psd, .tga, .thm,.tif, .yuv, .ai, .eps, .ps, .svg, .indd, .pct, .mp4, .avi, .mkv, .3g2, .3gp,.asf, .flv, .m4v, .mov, .mpg, .rm, .srt, .swf, .vob, .wmv, .doc, .docx, .txt,.pdf, .log, .msg, .odt, .pages., .rtf, .tex, .wpd, .wps, .csv, .ged, .key,.pps, .ppt., .pptx, .xml, .json, .xlsx, .xlsm, .xlsb, .xls, .mht, .mhtml, .htm,.html, .xltx, .prn, .dif, .slk, .xlam, .xla, .ods, .docm, .dotx, .dotm, .xps,.ics, .mp3., .aif, .iff, .m3u, .m4a, .mid, .mpa, .wav, .wma, .msi, .php, .apk,.app, .bat, .cgi, .com, .asp, .aspx, .cer, .cfm, .css, .js, .jsp, .rss, .xhtml,.c, .class, .cpp, .cs, .h, .java, .lua, .pl, .py, .sh, .sln, .swift, .vb,.vcxproj, .dem, .gam, .nes, .rom, .sav, .tgz, .zip, .rar, .tar, .7z, .cbr,.deb, .gz, .pkg, .rpm, .zipx, .iso, .ged, .accdb, .db, .dbf, .mdb, .sql, .fnt,.fon, .otf, .ttf, .cfg, .ini, .prf, .bak, .old, .tmp, .torrent

![7.png](https://image.3001.net/images/20181013/1539444756_5bc2101435930.png!small)

## 加密程序

PyLocky支持加密的文件类型是硬编码在配置文件中的，并且利用了Windows管理规范(WMI)来收集受感染设备的系统信息。如果受感染系统的可见内存大小小于4GB的话，PyLocky还可以通过休眠999999秒（11.5天）来躲避沙盒环境。如果内存大小大于或等于4GB的话，PyLocky将会直接执行文件加密程序。

加密完成之后，PyLocky将会与远程命令控制服务器建立通信连接。PyLocky使用PyCrypto库来实现加密，这里利用的是3DES加密算法。PyLocky首先会枚举逻辑驱动器，并在调用‘efile’方法之前生成一份文件列表，而这个方法会用已加密的文件内容覆盖原始的文件内容，然后发送勒索消息。

PyLocky的勒索信息采用了英语、法语、韩语和意大利语编写，这也表明韩国和意大利地区的用户可能也会受到影响。

![8.png](https://image.3001.net/images/20181013/1539444782_5bc2102ecd788.png!small)![9.png](https://image.3001.net/images/20181013/1539444782_5bc2102ed0f15.png!small)![10.png](https://image.3001.net/images/20181013/1539444783_5bc2102f2bbf1.png!small)

## 入侵威胁指标IoC

RANSOM_PYLOCKY.A(SHA-256)：

    
    
    c9c91b11059bd9ac3a0ad169deb513cef38b3d07213a5f916c3698bb4f407ffa
    
    1569f6fd28c666241902a19b205ee8223d47cccdd08c92fc35e867c487ebc999

相关哈希(SHA-256)：

    
    
    e172e4fa621845080893d72ecd0735f9a425a0c7775c7bc95c094ddf73d1f844(Facture_23100.31.07.2018.zip)
    
    2a244721ff221172edb788715d11008f0ab50ad946592f355ba16ce97a23e055(Facture_23100.31.07.2018.exe)
    
    87aadc95a8c9740f14b401bd6d7cc5ce2e2b9beec750f32d1d9c858bc101dffa(facture_31254872_18.08.23_{numbers}.exe)

相关恶意URL：

    
    
    hxxps://centredentairenantes[.]fr(C&C server)
    
    hxxps://panicpc[.]fr/client[.]php?fac=676171&u=0000EFC90103
    
    hxxps://savigneuxcom[.]securesitefr[.]com/client.php?fac=001838274191030

 ***参考来源：[trendmicro](https://blog.trendmicro.com/trendlabs-security-intelligence/a-closer-look-at-the-locky-poser-pylocky-ransomware/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

