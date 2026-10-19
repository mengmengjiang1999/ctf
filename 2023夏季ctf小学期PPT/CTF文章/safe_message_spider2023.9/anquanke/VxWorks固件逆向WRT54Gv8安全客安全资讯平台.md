# VxWorks固件逆向：WRT54Gv8

阅读量 **297600**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-04-17 16:00:20

 **x**

##### 译文声明

本文是翻译文章，文章原作者 devttys0，文章来源：devttys0.com

原文地址：<http://www.devttys0.com/2011/07/reverse-engineering-vxworks-firmware-wrt54gv8>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t018c1151c9ab531406.jpg)

最近我一直致力于解压一些[VxWorks](https://en.wikipedia.org/wiki/VxWorks)固件镜像，不幸的是，几乎找不到相关的信息。所以这篇文章的主题主要是从WRT54Gv8[固件镜像](http://homedownloads.cisco.com/downloads/firmware/FW_WRT54Gv8_8.00.8.001_US_20091005.bin)提取VxWorks的内核、应用代码以及在IDA
pro中分析它们。

随着WRT54Gv5的发布，WRT54G系列从Linux转向VxWorks系统。
由于VxWorks是一种实时操作系统（RTOS），相较于Linux的系统，我对该系统不太了解。
该系统即使确定了镜像的各个节，但是也不存在一个节包含标准的ELF可执行文件（可以被反汇编器自动分析）。

但是逆向该固件的整个过程是比较简单的：

  1. 从固件中识别以及提取可执行代码。
  2. 从可执行代码中识别加载地址。
  3. 在ida中使用正确的加载地址加载可执行文件。
  4. 通过手动/脚本辅助IDA完成自动分析。

使用JTAG或者是通过串口观察调试信息也许可以代替步骤1和2，但是由于我没有VxWorks WRT54G路由器，因此完全是基于固件的分析。

第一步是在固件映像中找到任何可识别的数据节：

    
    
    embedded@ubuntu:~/WRT54Gv8$ binwalk -v FW_WRT54Gv8_8.00.8.001_US_20091005.bin
    
    Scan Time:    Jul 05, 2011 @ 09:24:20
    Magic File:   /usr/local/etc/binwalk/magic.binwalk
    Signatures:   64
    Target File:  FW_WRT54Gv8_8.00.8.001_US_20091005.bin
    MD5 Checksum: 74317a70160f80fa5df01de0e479a39c
    
    DECIMAL       HEX           DESCRIPTION
    -------------------------------------------------------------------------------------------------------    512           0x200         ELF 32-bit LSB executable, MIPS, MIPS-II version 1 (SYSV)
    101658        0x18D1A       Linux Journalled Flash filesystem, little endian
    103664        0x194F0       LZMA compressed data, properties: 0x6C, dictionary size: 8388608 bytes, uncompressed size: 3680864 bytes
    1146276       0x117DA4      LZMA compressed data, properties: 0xA0, dictionary size: 486539264 bytes, uncompressed size: 520093696 bytes
    1185153       0x121581      gzip compressed data, was "apply.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:45:58 2009
    1185892       0x121864      gzip compressed data, was "apply1.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:45:58 2009
    1186870       0x121C36      gzip compressed data, was "apply2.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:45:58 2009
    1187499       0x121EAB      gzip compressed data, was "apply2sec.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:45:58 2009
    1188483       0x122283      gzip compressed data, was "apply3.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:45:58 2009
    1189464       0x122658      gzip compressed data, was "applyW.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:45:58 2009
    1190202       0x12293A      gzip compressed data, was "bad.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:45:58 2009
    1190724       0x122B44      gzip compressed data, was "basic.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:45:58 2009
    1202618       0x1259BA      gzip compressed data, was "bkconfig.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:45:58 2009
    1205617       0x126571      gzip compressed data, was "chghttps.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:45:59 2009
    1206740       0x1269D4      gzip compressed data, was "ChgLan.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:45:59 2009
    1207440       0x126C90      gzip compressed data, was "common.js", from NTFS filesystem (NT), last modified: Fri Sep  4 03:45:59 2009
    1210112       0x127700      gzip compressed data, was "Cysaja.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:45:59 2009
    1210324       0x1277D4      gzip compressed data, was "DDNS.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:45:59 2009
    1214620       0x12889C      gzip compressed data, was "default.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:00 2009
    1215253       0x128B15      gzip compressed data, was "DEVICE.HTM", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:00 2009
    1216309       0x128F35      gzip compressed data, was "DHCPTable.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:00 2009
    1217539       0x129403      gzip compressed data, was "Diag.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:00 2009
    1220485       0x129F85      gzip compressed data, was "DMZ.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:00 2009
    1223383       0x12AAD7      gzip compressed data, was "ERRSCRN.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:00 2009
    1224077       0x12AD8D      gzip compressed data, was "FacDef.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:00 2009
    1226898       0x12B892      gzip compressed data, was "FilterMac.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:00 2009
    1228632       0x12BF58      gzip compressed data, was "Filters.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:00 2009
    1233858       0x12D3C2      gzip compressed data, was "Firewall.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:00 2009
    1236986       0x12DFFA      gzip compressed data, was "Forward.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:00 2009
    1241779       0x12F2B3      gzip compressed data, was "getstatus.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:04 2009
    1242777       0x12F699      gzip compressed data, was "HDDNS.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:00 2009
    1244149       0x12FBF5      gzip compressed data, was "HDefault.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:01 2009
    1245052       0x12FF7C      gzip compressed data, was "HDMZ.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:01 2009
    1246049       0x130361      gzip compressed data, was "HExile.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:01 2009
    1247163       0x1307BB      gzip compressed data, was "HFilters.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:01 2009
    1248531       0x130D13      gzip compressed data, was "HFirewall.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:01 2009
    1249494       0x1310D6      gzip compressed data, was "HForward.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:01 2009
    1250527       0x1314DF      gzip compressed data, was "HLog.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:01 2009
    1251393       0x131841      gzip compressed data, was "HMAC.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:01 2009
    1252433       0x131C51      gzip compressed data, was "HManage.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:01 2009
    1253438       0x13203E      gzip compressed data, was "HOBA.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:01 2009
    1254564       0x1324A4      gzip compressed data, was "HRouting.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:01 2009
    1255864       0x1329B8      gzip compressed data, was "HSetup.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:01 2009
    1257408       0x132FC0      gzip compressed data, was "HStatus.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:01 2009
    1258783       0x13351F      gzip compressed data, was "HUpgrade.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:01 2009
    1259855       0x13394F      gzip compressed data, was "HVPN.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:01 2009
    1260808       0x133D08      gzip compressed data, was "HWEP.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:04 2009
    1262621       0x13441D      gzip compressed data, was "HWireless.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:04 2009
    1264097       0x1349E1      gzip compressed data, was "HWPA.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:04 2009
    1265245       0x134E5D      gzip compressed data, was "InLog.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:01 2009
    1266075       0x13519B      gzip compressed data, was "language.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:02 2009
    1269311       0x135E3F      gzip compressed data, was "lastpassword.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:02 2009
    1269507       0x135F03      gzip compressed data, was "Log.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:02 2009
    1272546       0x136AE2      gzip compressed data, was "Manage.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:02 2009
    1277123       0x137CC3      gzip compressed data, was "md5.js", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:02 2009
    1278995       0x138413      gzip compressed data, was "Outbreak_Alert.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:02 2009
    1282781       0x1392DD      gzip compressed data, was "OutLog.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:02 2009
    1283619       0x139623      gzip compressed data, was "ping.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:02 2009
    1287957       0x13A715      gzip compressed data, was "ptrigger.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:02 2009
    1292450       0x13B8A2      gzip compressed data, was "qos.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:02 2009
    1298667       0x13D0EB      gzip compressed data, was "Quarantined.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:02 2009
    1300366       0x13D78E      gzip compressed data, was "reset.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:02 2009
    1301699       0x13DCC3      gzip compressed data, was "Routing.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:02 2009
    1306547       0x13EFB3      gzip compressed data, was "RTable.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:02 2009
    1307445       0x13F335      gzip compressed data, was "Service.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:02 2009
    1310944       0x1400E0      gzip compressed data, was "StaLan.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:02 2009
    1313858       0x140C42      gzip compressed data, was "StaRouter.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:02 2009
    1318404       0x141E04      gzip compressed data, was "StaWlan.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:04 2009
    1324110       0x14344E      gzip compressed data, was "summary.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:02 2009
    1325773       0x143ACD      gzip compressed data, was "sysinfo.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:02 2009
    1325986       0x143BA2      gzip compressed data, was "test.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:03 2009
    1326015       0x143BBF      gzip compressed data, was "Traceroute.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:03 2009
    1340943       0x14760F      gzip compressed data, was "Unauthorized.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:03 2009
    1341087       0x14769F      gzip compressed data, was "Upgrade.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:03 2009
    1344585       0x148449      gzip compressed data, was "UpgStat.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:03 2009
    1345231       0x1486CF      gzip compressed data, was "UpLangPak.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:03 2009
    1346753       0x148CC1      gzip compressed data, was "VPN.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:03 2009
    1352719       0x14A40F      gzip compressed data, was "WAdv.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:04 2009
    1356924       0x14B47C      gzip compressed data, was "WanMAC.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:03 2009
    1360319       0x14C1BF      gzip compressed data, was "WClient.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:04 2009
    1362096       0x14C8B0      gzip compressed data, was "WFilter.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:04 2009
    1367188       0x14DC94      LZMA compressed data, properties: 0x80, dictionary size: 1110966272 bytes, uncompressed size: 218385737 bytes
    1379589       0x150D05      LZMA compressed data, properties: 0x80, dictionary size: 1110966272 bytes, uncompressed size: 218385737 bytes
    1390145       0x153641      gzip compressed data, was "Wireless.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:04 2009
    1396588       0x154F6C      gzip compressed data, was "wlaninfo.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:03 2009
    1396765       0x15501D      gzip compressed data, was "WMList.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:04 2009
    1402406       0x156626      gzip compressed data, was "wps_result.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:04 2009
    1403174       0x156926      gzip compressed data, was "wps_search.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:04 2009
    1407322       0x15795A      gzip compressed data, was "WSecurity.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:04 2009
    1413245       0x15907D      gzip compressed data, was "WState.htm", from NTFS filesystem (NT), last modified: Fri Sep  4 03:46:03 2009
    1414025       0x159389      gzip compressed data, was "capadmin.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:18 2009
    1415312       0x159890      gzip compressed data, was "capapp.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:18 2009
    1415961       0x159B19      gzip compressed data, was "capasg.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:23 2009
    1422692       0x15B564      gzip compressed data, was "capsec.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:18 2009
    1424577       0x15BCC1      gzip compressed data, was "capsetup.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:19 2009
    1426257       0x15C351      gzip compressed data, was "capstatus.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:19 2009
    1426777       0x15C559      gzip compressed data, was "ddnsmsg.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:19 2009
    1427511       0x15C837      gzip compressed data, was "errmsg.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:20 2009
    1428222       0x15CAFE      gzip compressed data, was "help.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:21 2009
    1440881       0x15FC71      gzip compressed data, was "share.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:22 2009
    1444717       0x160B6D      gzip compressed data, was "capadmin.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:18 2009
    1446043       0x16109B      gzip compressed data, was "capapp.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:18 2009
    1446740       0x161354      gzip compressed data, was "capasg.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:24 2009
    1453397       0x162D55      gzip compressed data, was "capsec.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:19 2009
    1455360       0x163500      gzip compressed data, was "capsetup.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:19 2009
    1457203       0x163C33      gzip compressed data, was "capstatus.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:19 2009
    1457760       0x163E60      gzip compressed data, was "ddnsmsg.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:20 2009
    1458484       0x164134      gzip compressed data, was "errmsg.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:20 2009
    1459130       0x1643BA      gzip compressed data, was "help.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:21 2009
    1470606       0x16708E      gzip compressed data, was "share.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:22 2009
    1474489       0x167FB9      gzip compressed data, was "capadmin.js", from NTFS filesystem (NT), last modified: Mon Jul 20 02:06:11 2009
    1475924       0x168554      gzip compressed data, was "capapp.js", from NTFS filesystem (NT), last modified: Mon Jul 20 02:06:12 2009
    1476640       0x168820      gzip compressed data, was "capasg.js", from NTFS filesystem (NT), last modified: Mon Jul 20 02:06:19 2009
    1484040       0x16A508      gzip compressed data, was "capsec.js", from NTFS filesystem (NT), last modified: Mon Jul 20 02:06:12 2009
    1486131       0x16AD33      gzip compressed data, was "capsetup.js", from NTFS filesystem (NT), last modified: Mon Jul 20 02:06:12 2009
    1487922       0x16B432      gzip compressed data, was "capstatus.js", from NTFS filesystem (NT), last modified: Mon Jul 20 02:06:13 2009
    1488498       0x16B672      gzip compressed data, was "ddnsmsg.js", from NTFS filesystem (NT), last modified: Mon Jul 20 02:06:13 2009
    1489232       0x16B950      gzip compressed data, was "errmsg.js", from NTFS filesystem (NT), last modified: Mon Jul 20 02:06:14 2009
    1490002       0x16BC52      gzip compressed data, was "help.js", from NTFS filesystem (NT), last modified: Mon Jul 20 02:06:16 2009
    1502977       0x16EF01      gzip compressed data, was "share.js", from NTFS filesystem (NT), last modified: Mon Jul 20 02:06:18 2009
    1507309       0x16FFED      gzip compressed data, was "capadmin.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:18 2009
    1508872       0x170608      gzip compressed data, was "capapp.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:18 2009
    1509579       0x1708CB      gzip compressed data, was "capasg.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:23 2009
    1517398       0x172756      gzip compressed data, was "capsec.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:18 2009
    1519422       0x172F3E      gzip compressed data, was "capsetup.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:19 2009
    1521274       0x17367A      gzip compressed data, was "capstatus.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:19 2009
    1521858       0x1738C2      gzip compressed data, was "ddnsmsg.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:19 2009
    1522740       0x173C34      gzip compressed data, was "errmsg.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:20 2009
    1523552       0x173F60      gzip compressed data, was "help.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:21 2009
    1537579       0x17762B      gzip compressed data, was "share.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:22 2009
    1541905       0x178711      gzip compressed data, was "capadmin.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:18 2009
    1543410       0x178CF2      gzip compressed data, was "capapp.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:18 2009
    1544153       0x178FD9      gzip compressed data, was "capasg.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:24 2009
    1551383       0x17AC17      gzip compressed data, was "capsec.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:18 2009
    1553369       0x17B3D9      gzip compressed data, was "capsetup.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:19 2009
    1555240       0x17BB28      gzip compressed data, was "capstatus.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:19 2009
    1555807       0x17BD5F      gzip compressed data, was "ddnsmsg.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:20 2009
    1556608       0x17C080      gzip compressed data, was "errmsg.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:20 2009
    1557451       0x17C3CB      gzip compressed data, was "help.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:21 2009
    1570691       0x17F783      gzip compressed data, was "share.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:22 2009
    1575061       0x180895      gzip compressed data, was "capadmin.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:18 2009
    1576468       0x180E14      gzip compressed data, was "capapp.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:18 2009
    1577168       0x1810D0      gzip compressed data, was "capasg.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:24 2009
    1583976       0x182B68      gzip compressed data, was "capsec.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:19 2009
    1585919       0x1832FF      gzip compressed data, was "capsetup.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:19 2009
    1587626       0x1839AA      gzip compressed data, was "capstatus.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:19 2009
    1588171       0x183BCB      gzip compressed data, was "ddnsmsg.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:20 2009
    1588954       0x183EDA      gzip compressed data, was "errmsg.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:20 2009
    1589732       0x1841E4      gzip compressed data, was "help.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:21 2009
    1602550       0x1873F6      gzip compressed data, was "share.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:22 2009
    1606645       0x1883F5      gzip compressed data, was "capadmin.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:18 2009
    1608110       0x1889AE      gzip compressed data, was "capapp.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:18 2009
    1608851       0x188C93      gzip compressed data, was "capasg.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:24 2009
    1616048       0x18A8B0      gzip compressed data, was "capsec.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:19 2009
    1618053       0x18B085      gzip compressed data, was "capsetup.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:19 2009
    1619884       0x18B7AC      gzip compressed data, was "capstatus.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:19 2009
    1620434       0x18B9D2      gzip compressed data, was "ddnsmsg.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:20 2009
    1621256       0x18BD08      gzip compressed data, was "errmsg.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:20 2009
    1622020       0x18C004      gzip compressed data, was "help.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:21 2009
    1635437       0x18F46D      gzip compressed data, was "share.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:22 2009
    1639557       0x190485      gzip compressed data, was "capadmin.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:18 2009
    1640989       0x190A1D      gzip compressed data, was "capapp.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:18 2009
    1641705       0x190CE9      gzip compressed data, was "capasg.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:24 2009
    1648936       0x192928      gzip compressed data, was "capsec.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:19 2009
    1650918       0x1930E6      gzip compressed data, was "capsetup.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:19 2009
    1652676       0x1937C4      gzip compressed data, was "capstatus.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:19 2009
    1653245       0x1939FD      gzip compressed data, was "ddnsmsg.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:20 2009
    1654035       0x193D13      gzip compressed data, was "errmsg.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:20 2009
    1654781       0x193FFD      gzip compressed data, was "help.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:21 2009
    1668039       0x1973C7      gzip compressed data, was "share.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:22 2009
    1672113       0x1983B1      gzip compressed data, was "capadmin.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:18 2009
    1673513       0x198929      gzip compressed data, was "capapp.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:18 2009
    1674220       0x198BEC      gzip compressed data, was "capasg.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:23 2009
    1681271       0x19A777      gzip compressed data, was "capsec.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:18 2009
    1683281       0x19AF51      gzip compressed data, was "capsetup.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:19 2009
    1685025       0x19B621      gzip compressed data, was "capstatus.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:19 2009
    1685594       0x19B85A      gzip compressed data, was "ddnsmsg.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:19 2009
    1686372       0x19BB64      gzip compressed data, was "errmsg.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:20 2009
    1687111       0x19BE47      gzip compressed data, was "help.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:21 2009
    1699948       0x19F06C      gzip compressed data, was "share.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:22 2009
    1703937       0x1A0001      gzip compressed data, was "capadmin.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:18 2009
    1705425       0x1A05D1      gzip compressed data, was "capapp.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:18 2009
    1706169       0x1A08B9      gzip compressed data, was "capasg.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:24 2009
    1713196       0x1A242C      gzip compressed data, was "capsec.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:19 2009
    1715253       0x1A2C35      gzip compressed data, was "capsetup.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:19 2009
    1717098       0x1A336A      gzip compressed data, was "capstatus.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:19 2009
    1717679       0x1A35AF      gzip compressed data, was "ddnsmsg.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:20 2009
    1718519       0x1A38F7      gzip compressed data, was "errmsg.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:20 2009
    1719332       0x1A3C24      gzip compressed data, was "help.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:21 2009
    1732356       0x1A6F04      gzip compressed data, was "share.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:22 2009
    1736429       0x1A7EED      gzip compressed data, was "capadmin.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:18 2009
    1737865       0x1A8489      gzip compressed data, was "capapp.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:18 2009
    1738572       0x1A874C      gzip compressed data, was "capasg.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:24 2009
    1745822       0x1AA39E      gzip compressed data, was "capsec.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:19 2009
    1747816       0x1AAB68      gzip compressed data, was "capsetup.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:19 2009
    1749609       0x1AB269      gzip compressed data, was "capstatus.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:19 2009
    1750156       0x1AB48C      gzip compressed data, was "ddnsmsg.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:20 2009
    1750922       0x1AB78A      gzip compressed data, was "errmsg.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:20 2009
    1751669       0x1ABA75      gzip compressed data, was "help.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:21 2009
    1765090       0x1AEEE2      gzip compressed data, was "share.js", from NTFS filesystem (NT), last modified: Tue Jul 14 04:38:22 2009
    

可以看到binwalk识别了很多的gzip压缩过的web文件、一些LZMA签名、一个ELF头以及一个JFFS文件系统。

那个JFFS文件系统大概率是一个误报，所以我忽略了它。

通过十六进制查看该镜像，发现经过gzip压缩的web文件看起来像是简单文件系统的一部分，类似于[之前](http://www.devttys0.com/2011/06/mystery-file-system/)讨论过的OW文件系统。但是，Web文件与本文的目的不是特别相关，因此我放弃对该文件系统的分析；如果有必要，可以比较容易地从固件映像中提取这些文件并进行gzip解压。

总共发现了四个`LZMA`签名，可以看到，除了一个签名以外，其他三个签名都有很大的size（每个有几百MB），所以那三个可能是误报。第一个签名偏移是0x194f0的大小只有3.5MB，这个大小是合理的，所以我们将该文件提取出来并解压缩：

    
    
    embedded@ubuntu:~/WRT54Gv8$ dd if=FW_WRT54Gv8_8.00.8.001_US_20091005.bin skip=0x1 bs=103664 of=lzma_data.7z
    16+1 records in
    16+1 records out
    1665240 bytes (1.7 MB) copied, 0.00559597 s, 298 MB/s
    
    
    
    embedded@ubuntu:~/WRT54Gv8$ p7zip -d lzma_data.7z 
    
    7-Zip (A) 9.04 beta  Copyright (c) 1999-2009 Igor Pavlov  2009-05-30
    p7zip Version 9.04 (locale=en_US.utf8,Utf16=on,HugeFiles=on,1 CPU)
    
    Processing archive: lzma_data.7z
    
    Extracting  lzma_data
    
    Everything is Ok
    
    Size:       3680864
    Compressed: 1665240
    

看起来解压的很成功，让我们使用strings以及hexdump来看一下在解压缩的数据里能够找到什么：

    
    
    embedded@ubuntu:~/WRT54Gv8$ strings lzma_data | less
    NORMAL_CODE_DATA
    5VGW$LANGPACK_CODE_DATA=
    $MODEL_NAME=WRT54G
    $OEM_NAME=LINKSYS
    Copyright 2004-2005 CyberTAN Limited
    ...
    GetConnectedDevices
    GetRouterLanSettings2
    GetWanInfo
    GetWanSettings
    GetMACFilters2
    GetPortMappings
    GetDeviceSettings
    HTTP/1.1 307 Temporary Redirect
    Location: https://%s%s/HNAP1/
    HTTP/1.1 500 Internal Server Error
    Server: httpd
    
    
    
    embedded@ubuntu:~/WRT54Gv8$ hexdump -C lzma_data | head
    00000000  22 00 00 10 00 00 00 00  00 00 00 00 00 00 00 00  |"...............|
    00000010  4e 4f 52 4d 41 4c 5f 43  4f 44 45 5f 44 41 54 41  |NORMAL_CODE_DATA|
    00000020  01 80 00 08 35 56 47 57  24 4c 41 4e 47 50 41 43  |....5VGW$LANGPAC|
    00000030  4b 5f 43 4f 44 45 5f 44  41 54 41 3d 06 01 00 01  |K_CODE_DATA=....|
    00000040  24 4d 4f 44 45 4c 5f 4e  41 4d 45 3d 57 52 54 35  |$MODEL_NAME=WRT5|
    00000050  34 47 00 24 4f 45 4d 5f  4e 41 4d 45 3d 4c 49 4e  |4G.$OEM_NAME=LIN|
    00000060  4b 53 59 53 00 43 6f 70  79 72 69 67 68 74 20 32  |KSYS.Copyright 2|
    00000070  30 30 34 2d 32 30 30 35  20 43 79 62 65 72 54 41  |004-2005 CyberTA|
    00000080  4e 20 4c 69 6d 69 74 65  64 00 00 00 39 80 1c 3c  |N Limited...9..<|
    00000090  50 ba 9c 27 00 10 08 3c  fe ff 09 24 24 40 09 01  |P..'...<...$$@..|
    

可以看到里面还是存在一些有意义的字符串的，看起来像是一些服务应用的字符串如HTTP和HNAP。

里面也有一些二进制数据，也许是可执行代码。但是，如果存在可执行代码，也找不到可以区别出来的头或者节信息，这使得分析起来存在困难。而且我们也不知道CPU的架构或者是大小端（这可能可以通过谷歌搜索找到）。

我们也看到在固件镜像偏移0x200的地方看到了一个ELF头的信息，分析下该文件：

    
    
    embedded@ubuntu:~/WRT54Gv8$ dd if=FW_WRT54Gv8_8.00.8.001_US_20091005.bin bs=512 skip=1 of=elf
    3453+1 records in
    3453+1 records out
    1768392 bytes (1.8 MB) copied, 0.020778 s, 85.1 MB/s
    
    
    
    embedded@ubuntu:~/WRT54Gv8$ file elf 
    elf: ELF 32-bit LSB executable, MIPS, MIPS-II version 1 (SYSV), statically linked, not stripped
    
    
    
    embedded@ubuntu:~/WRT54Gv8$ strings -n 10 elf | head
    VxWorks5.4.2
    Oct  5 2009, 15:15:53
    memPartFree
    %-5s = %8x
    0123456789abcdef
    0123456789ABCDEF
    bug in vfprintf: bad base
    WIND version 2.5
    workQPanic: Kernel work queue overflow.
    DDDDDDDDDD
    

这是一个小端的mips ELF文件，里面包含一些字符串有`Vxworks`、`Wind
River`、以及`Kernel`。看起来这似乎是VxWorks内核文件。用IDA加载这个文件看下能不能查看它（确定选择mipsl cpu）：

![](https://p5.ssl.qhimg.com/t01e9c5c140db9d75f0.png)

由于这个文件有ELF头，所以IDA可以很好的解析这个文件，识别函数以及解析符号。首先看下第一个函数`startInflate`：

![](https://p3.ssl.qhimg.com/t01bf28b43a19d13de6.png)

可以看到地址`0x80001000`加载到了`$v0`寄存器中，并调用`decompressImage`函数，最终跳转到`$v0(0x80001000)`地址去执行。因此，可能是`decompressImage`函数将`0x80001000`处的代码解压，然后再执行该地址处的代码。

查看`decompressImage`函数的参数，第一个参数是`_binArrayStart`，第二个地址是`0x80001000`。让我们看下`_binArrayStart`：

![](https://p3.ssl.qhimg.com/t016d95e49ee60ee402.png)

`_binArrayStart`地址处的前五个字节是`6C 00 00 80
00`，看起来像是一个`LZMA`镜像的头文件。与之前提取出来的LZMA数据比较下，确定了这个想法：

    
    
    embedded@ubuntu:~/WRT54Gv8$ hexdump -C lzma_data.7z | head
    00000000  6c 00 00 80 00 60 2a 38  00 00 00 00 00 00 11 00  |l....`*8........|
    00000010  2c 20 00 df 1e 01 d7 44  6b 43 41 4d a8 aa 91 9c  |, .....DkCAM....|
    00000020  11 ed 0d 6b bd 40 da 21  19 b1 16 8b 51 48 b8 a6  |...k.@.!....QH..|
    00000030  c9 1f 7e 0b 24 4c 24 14  2b db 64 59 fb 79 2a 3c  |..~.$L$.+.dY.y*<|
    00000040  11 70 12 a7 84 78 fc 38  f5 99 ed 0d db 0f c3 64  |.p...x.8.......d|
    00000050  4c ca ca 70 31 bc e7 1a  7f 42 51 dc 1f fe 8b dc  |L..p1....BQ.....|
    00000060  d0 89 fc 0a 9a dc 03 37  62 e3 75 f3 10 56 7c f8  |.......7b.u..V|.|
    00000070  6a c1 14 69 bc 28 e6 fc  48 2e f5 bf b2 22 dc f5  |j..i.(..H...."..|
    00000080  ec b1 c7 9b ec 76 93 73  b8 cf fa 2d 06 34 cb 75  |.....v.s...-.4.u|
    00000090  4b ed 1f f1 28 d7 00 ea  ae 29 57 19 de 87 42 ae  |K...(....)W...B.|
    

跟进去`decompressImage`函数，我们还可以看到它还调用了一个叫做`LzmaDecode`的函数：

![](https://p2.ssl.qhimg.com/t0152fe4f9ba8efd307.png)

所以看起来是我们之前提取的`LZMA`数据包含可执行代码，这些数据被解压然后载入到地址`0x80001000`中，google搜`vxworks
lzmadecode`出来的[源码](http://www.hackchina.com/en/cont/27807)（译者注：这个链接已经失效了）证明了这个结论。

基于之前看到的字符串，可以初步判断`LZMA`数据中包含OS的应用代码。

我们现在已经有了足够多的信息，可以将解压出来的LZMA数据加载到IDA中分析了。与kernel一样，我们将架构设为mipsl，由于这是一个二进制文件，我们需要在IDA中设置一些适当的加载信息。

我们将ROM的开始地址设置为`0x80001000`，把size设置成文件的size`0x382A60`，同时把`loading
address`设置为`0x80001000`。如下图所示：

![](https://p2.ssl.qhimg.com/t01d8504614286706a7.png)

当文件加载进IDA，到第一个字节处，按下`c`键直接把它转换成代码。IDA会将该地址处的字节直接转换成代码并对文件进行分析。可以看到，第一条指令是一个跳转指令，跳过了文件头附近的一些文件。

代码看起来很清晰，IDA也识别出来了超过5000个函数，并且字符串的引用看起来也是正确的：

![](https://p4.ssl.qhimg.com/t0133ad74764aa5f552.png)

我们将该数据文件载入IDA，不设置正确的载入地址。将分析结果与上面得到的结果进行对比；

![](https://p3.ssl.qhimg.com/t01b4fcccfd7f6fb1cd.png)

IDA的导航栏中有相当数量的蓝色区域（代码）：

![](https://p3.ssl.qhimg.com/t01829d89a7fdf588cb.png)

可以看到，虽然我们的分析已经提升了IDA的分析结果，仍然还有很多代码是丢失的，因此我写了一个IDA[脚本](http://www.devttys0.com/wp-content/uploads/2011/07/ida_scripts.zip)来帮助得到更多的反汇编代码。

首先，我们希望通过迭代查找代码寻找常见的函数序言来定位未识别的函数。如果找到了，我们会告诉IDA在那里创建一个函数。对于MIPS而言，有时比intel架构困难，因为函数序言在MIPS中的标准化程度较低。

`addui`指令经常在函数最开始被用来操作栈桢寄存器`$sp`，我们可以在IDA中看到很多的函数是这样的：

![](https://p4.ssl.qhimg.com/t019d9c4904e575b2d8.png)

然而，也有一些函数在`addui`指令前还有一条`lw`指令：

![](https://p4.ssl.qhimg.com/t010cd2753f01fed0f5.png)

`create_function.py`
IDAPython脚本通过搜索代码字节序（从上图的光标处地址开始）寻找相应的指令，如果找到的话就引导IDA将该处的代码创建为一个函数。

查看反汇编代码，包含字符串的数据节出现在地址`0x802DDAC0`，因此我将脚本的设定为分析到该地址就结束：

![](https://p3.ssl.qhimg.com/t019d0b084208fb80cb.png)

在跑完这个脚本后，IDA识别出来了9600个函数，相比于之前，更多的代码被识别出来了：

![](https://p1.ssl.qhimg.com/t016363ed09efbbdff0.png)

但是仍然有一些数据节没有被分析到：

![](https://p0.ssl.qhimg.com/t01bdfcc61803041667.png)

这些节被代码所包围，并且导航到其中几个节将它们直接转换成代码，可以看到它们也是有效的汇编指令：

![](https://p0.ssl.qhimg.com/t01c3f30dafd56e5439.png)

因为这些节看起来都是以`jr $ra`（mips的返回指令）结束，并且由于它们没有被其他的函数所使用，它们可能是自身调用的函数（since they are
not referenced by the surrounding functions, they are likely functions
themselves. ）（译者注：不太理解这句话，怕误导，所以将原文贴出）

`create_code.py`会遍历代码并将这些没有定义的字节转换成函数（方法和之前的类似，脚本从下图光标处地址开始遍历至`0x802DDAC0`结束）：

![](https://p0.ssl.qhimg.com/t0190a15ac8448756d6.png)

现在在IDA的导航栏中有一个比较完美的代码块：

![](https://p3.ssl.qhimg.com/t011b6af1fa83592a13.png)

随着完成对代码的处理，我们将注意力转向字符串。没有像ELF文件中的符号，我们不得不依赖字符串的引用来提供对于固件中的事件的理解。但是仍然有一些ascii字节的数组没有被IDA转换成字符串：

![](https://p1.ssl.qhimg.com/t01773a17806c19c987.png)

将这些ascii字节的数组转换成字符串将会使得代码的可读性更强，因此`create_ascii.py`脚本是将ascii字节的数组转换成字符串。我们之前看到的是，包含字符串的数据地址开始于0x802DDAC0，因此我们将开始的地址设定为该地址，并运行脚本。运行的结果相较于之前又了一定的提升：

![](https://p2.ssl.qhimg.com/t015fa1c849e1a32284.png)

随着字符串也被修复好了，让我们在汇编代码中去识别一些基本的函数：

![](https://p2.ssl.qhimg.com/t0133ad74764aa5f552.png)

上图中有两个函数被调用。第一个是`sub_802A7F90`，参数为一个：1将其左移16位（65536）。如果返回值是0，调用第二个函数`sub_802A06E8`。

第二个函数接受不了两个参数：一个包含格式化字符的字符串；一个65536立即数。伪代码如下：

    
    
    if(!sub_802A7F90(65536))
    {
       sub_802A06E8("Can't allocate %d bytes of memoryn", 65536);
    }
    

很容易看出来`sub_802A7F90`等同于`malloc`函数，`sub_802A06E8`函数是`printf`。我们将这些函数重命名，以便其他代码对它们进行引用的时候会更加便于分析。

![](https://p1.ssl.qhimg.com/t01c614fcf749d9f051.png)

到这里就结束了，我们现在就拥有了内核以及应用层的所有代码。可以进一步进行分析，寻找bug或漏洞了。

本文翻译自devttys0.com [原文链接](http://www.devttys0.com/2011/07/reverse-engineering-vxworks-firmware-wrt54gv8)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **raycp** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/176481](/post/id/176481)

安全客 - 有思想的安全新媒体

本文转载自: [devttys0.com](http://www.devttys0.com/2011/07/reverse-engineering-vxworks-firmware-wrt54gv8)

如若转载,请注明出处： <http://www.devttys0.com/2011/07/reverse-engineering-vxworks-firmware-wrt54gv8>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [IoT](/tag/IoT)
  * [逆向工程](/tag/逆向工程)

 **+1** __12赞

 __收藏

![](https://p1.ssl.qhimg.com/t01649f572f3e474443.png) raycp

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

