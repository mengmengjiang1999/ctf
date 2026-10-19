# ​一、病毒简介

文件名称：  
457d9e4773f45954449ee5913d068fdbb3d8e5689019688e7bce901467e5473a  
文件类型(Magic)：  
PE32 executable (GUI) Intel 80386, for MS Windows, UPX compressed  
文件大小：  
410.00KB  
SHA256：  
457d9e4773f45954449ee5913d068fdbb3d8e5689019688e7bce901467e5473a  
SHA1：  
eef83497e8aa02d644b7d071be81a678e1611aa6  
MD5：  
adfacb09ceb60e6410e014275145b5a9  
CRC32：  
5BA85BCD  
SSDEEP：  
6144:aR1d1ciOX8NFu7wOh06Y7/36SnEP9+xYzWVv/4oTQl+ds9qat4oCNGpLP/C7bIi:afd6iOMS7wOh0606j9iYz7fqAZp+E  
ImpHash：  
6adb831a5884f7e68176214cc4749075  
Tags：  
PE32,section_name_exception,encrypt_algorithm

# 二、环境准备

系统版本  
  
---  
  
win7x86  
  
# 三、行为分析

在火绒里面添加信任区，然后打开火绒剑，开启监控：

![](https://image.3001.net/images/20230420/1681989109_64411df56f8fcc22a2f87.png!small)

简单做一下过滤：

![](https://image.3001.net/images/20230420/1681989112_64411df827e56472d7720.png!small)

首先看行为监控，有一个修改自启动项：

![](https://image.3001.net/images/20230420/1681989113_64411df9e9a436c6d7923.png!small)

路径：“C:\Users\rkvir\AppData\Local\710d60a1-9877-43e7-a996-439fa0482755\病毒样本.exe”  
这里是文件创建：

![](https://image.3001.net/images/20230420/1681989115_64411dfbc3cfbee5e37b3.png!small)

这里是网络链接发包收包操作：

![](https://image.3001.net/images/20230420/1681989117_64411dfdb88cada5888a6.png!small)

![](https://image.3001.net/images/20230420/1681989119_64411dffb04a362ae49f9.png!small)

  
  
接下来这一块基本属于目录遍历，在每个文件夹下面生成readme.txt：

![](https://image.3001.net/images/20230420/1681989121_64411e0145ba704940ed3.png!small)

接下来是把很多文件后缀名加上了.litar：

![](https://image.3001.net/images/20230420/1681989123_64411e03c3a18500db470.png!small)

当然还有设置文件安全属性为不可修改：

![](https://image.3001.net/images/20230420/1681989125_64411e056fa8131406b4b.png!small)

readme内容：

ATTENTION!  
  
Don't worry,you can returnall your files!  
All your files like photos,databases,documents and other important are
encrypted with strongest encryption and unique key.  
The only method of recovering files isto purchase decrypt tool and unique key
foryou.  
This software will decrypt all your encrypted files.  
What guarantees you have?  
You can send one of your encrypted file from your PC and we decrypt it
forfree.  
But we can decrypt only 1file forfree.File must not contain valuable
information.  
You can getand look video overview decrypt tool:  
https://we.tl/t-514KtsAKtH  
Price of privatekey and decrypt software is$980.  
Discount 50%available ifyou contact us first 72hours,that's price foryou
is$490.  
Please note that you'll never restore your data without payment.  
Check your e-mail "Spam"or "Junk"folder ifyou don't getanswer more than
6hours.  
  
  
To getthis software you need write on our e-mail:  
gorentos@bitmessage.ch  
  
Reserve e-mail address to contact us:  
varasto@firemail.cc  
  
Our Telegram account:  
@datarestore  
  
Your personal ID:  
109AJsd73yiu3hjdfgiagsMxds3LxpDLrrIrIVlqmVQ2P4y09QCIrzCYt1

一个勒索病毒。

# 四、静态分析

首先拖入PEID，有UPX壳，先脱：

![](https://image.3001.net/images/20230420/1681989126_64411e06d231301be92d6.png!small)

esp定律，这里不再多说。脱壳后拖入PEID查看：

![](https://image.3001.net/images/20230420/1681989128_64411e0823648393dc9c2.png!small)

随后拖入IDA中，开始分析：

![](https://image.3001.net/images/20230420/1681989129_64411e0965aadaf38ac9c.png!small)

捣鼓了半天，没找到病毒代码，动态调试一下。

# 五、动态分析

可以看到我们病毒样本都被修改，加了后缀名切无法恢复：

![](https://image.3001.net/images/20230420/1681989130_64411e0a6154d81c4fc59.png!small)

恢复快照，OD附加，顺带打开火绒剑监控：

![](https://image.3001.net/images/20230420/1681989132_64411e0c61a83659d55b7.png!small)

前面和IDA中对照分析就好，到GetCommandLineA()这个函数的时候获取的是病毒路径：

![](https://image.3001.net/images/20230420/1681989133_64411e0d9a79fcb97c1c3.png!small)

从这里分析开始：

![](https://image.3001.net/images/20230420/1681989134_64411e0eb7589baf5434f.png!small)

发现这里是关键函数：

![](https://image.3001.net/images/20230420/1681989136_64411e102cbbecd33414f.png!small)

完事我们发现了，这鬼东西又启动了自己，导致我们OD附加这个啥功能也不实现，用火绒剑再看一下：

![](https://image.3001.net/images/20230420/1681989138_64411e1209a97f7844899.png!small)

接下来我们使用注册表一个调试操作，设置123.exe启动附加OD：

![](https://image.3001.net/images/20230420/1681989139_64411e13001528b9c2d79.png!small)

然后我们跑起第一次OD，结果如下：

![](https://image.3001.net/images/20230420/1681989139_64411e13cf2e02b85113c.png!small)

然后我们OD成功附加启动的俩个123.exe：

![](https://image.3001.net/images/20230420/1681989140_64411e14eceac3993d2b5.png!small)

可以看到再次启动桌面的123.exe主要是用来遍历目录生成readme.txt；  
那么其他操作就是启动的C盘下的123.exe完成的。这里有点迷，我们重新看一下，找到了这块：

![](https://image.3001.net/images/20230420/1681989142_64411e166cc989162ae95.png!small)

![](https://image.3001.net/images/20230420/1681989143_64411e178d7e9cf925e3c.png!small)

// write access to const memory has been detected, the output may be wrong!  
intsub_4032C0()  
{  
signedintv0;// esi@1  
__int64 v1;// rax@2  
intv2;// ecx@2  
signedintv3;// esi@7  
intv4;// ecx@11  
DWORD flNewProtect;// [sp+30h] [bp-2224h]@7  
intv7;// [sp+34h] [bp-2220h]@11  
intv8;// [sp+38h] [bp-221Ch]@11  
intv9;// [sp+50h] [bp-2204h]@11  
intv10;// [sp+54h] [bp-2200h]@11  
intv11;// [sp+5Ch] [bp-21F8h]@11  
intv12;// [sp+60h] [bp-21F4h]@11  
intv13;// [sp+64h] [bp-21F0h]@11  
intv14;// [sp+74h] [bp-21E0h]@11  
intv15;// [sp+78h] [bp-21DCh]@11  
intv16;// [sp+7Ch] [bp-21D8h]@11  
intv17;// [sp+84h] [bp-21D0h]@11  
intv18;// [sp+8Ch] [bp-21C8h]@11  
intv19;// [sp+94h] [bp-21C0h]@11  
intv20;// [sp+98h] [bp-21BCh]@11  
intv21;// [sp+A0h] [bp-21B4h]@11  
intv22;// [sp+A8h] [bp-21ACh]@11  
intv23;// [sp+B0h] [bp-21A4h]@11  
intv24;// [sp+B8h] [bp-219Ch]@11  
intv25;// [sp+C0h] [bp-2194h]@11  
intv26;// [sp+C8h] [bp-218Ch]@11  
intv27;// [sp+DCh] [bp-2178h]@11  
intv28;// [sp+E0h] [bp-2174h]@11  
intv29;// [sp+E8h] [bp-216Ch]@11  
intv30;// [sp+F0h] [bp-2164h]@11  
intv31;// [sp+F8h] [bp-215Ch]@11  
intv32;// [sp+100h] [bp-2154h]@11  
intv33;// [sp+108h] [bp-214Ch]@11  
intv34;// [sp+110h] [bp-2144h]@11  
intv35;// [sp+118h] [bp-213Ch]@11  
intv36;// [sp+120h] [bp-2134h]@11  
intv37;// [sp+134h] [bp-2120h]@11  
intv38;// [sp+13Ch] [bp-2118h]@11  
intv39;// [sp+144h] [bp-2110h]@11  
intv40;// [sp+14Ch] [bp-2108h]@11  
intv41;// [sp+154h] [bp-2100h]@11  
intv42;// [sp+15Ch] [bp-20F8h]@11  
intv43;// [sp+164h] [bp-20F0h]@11  
intv44;// [sp+170h] [bp-20E4h]@11  
intv45;// [sp+178h] [bp-20DCh]@11  
intv46;// [sp+180h] [bp-20D4h]@11  
intv47;// [sp+188h] [bp-20CCh]@11  
intv48;// [sp+190h] [bp-20C4h]@11  
intv49;// [sp+198h] [bp-20BCh]@11  
intv50;// [sp+1A0h] [bp-20B4h]@11  
DWORD dwProcessList;// [sp+1A4h] [bp-20B0h]@7  
intv52;// [sp+1ACh] [bp-20A8h]@11  
intv53;// [sp+1B0h] [bp-20A4h]@11  
intv54;// [sp+1B8h] [bp-209Ch]@11  
intv55;// [sp+1C0h] [bp-2094h]@11  
intv56;// [sp+1C8h] [bp-208Ch]@11  
intv57;// [sp+1D0h] [bp-2084h]@11  
intv58;// [sp+1D8h] [bp-207Ch]@11  
intv59;// [sp+1E0h] [bp-2074h]@11  
intv60;// [sp+1E8h] [bp-206Ch]@11  
intv61;// [sp+1FCh] [bp-2058h]@11  
intv62;// [sp+204h] [bp-2050h]@11  
intv63;// [sp+20Ch] [bp-2048h]@11  
intv64;// [sp+214h] [bp-2040h]@11  
intv65;// [sp+21Ch] [bp-2038h]@11  
intv66;// [sp+220h] [bp-2034h]@11  
intv67;// [sp+224h] [bp-2030h]@11  
intv68;// [sp+228h] [bp-202Ch]@11  
intv69;// [sp+22Ch] [bp-2028h]@11  
intv70;// [sp+234h] [bp-2020h]@11  
intv71;// [sp+23Ch] [bp-2018h]@11  
intv72;// [sp+244h] [bp-2010h]@11  
intv73;// [sp+24Ch] [bp-2008h]@11  
intv74;// [sp+254h] [bp-2000h]@11  
intv75;// [sp+25Ch] [bp-1FF8h]@11  
intv76;// [sp+260h] [bp-1FF4h]@11  
intv77;// [sp+264h] [bp-1FF0h]@11  
intv78;// [sp+26Ch] [bp-1FE8h]@11  
intv79;// [sp+274h] [bp-1FE0h]@11  
intv80;// [sp+27Ch] [bp-1FD8h]@11  
intv81;// [sp+284h] [bp-1FD0h]@11  
intv82;// [sp+28Ch] [bp-1FC8h]@11  
intv83;// [sp+294h] [bp-1FC0h]@11  
intv84;// [sp+298h] [bp-1FBCh]@11  
intv85;// [sp+29Ch] [bp-1FB8h]@11  
intv86;// [sp+2A0h] [bp-1FB4h]@3  
intv87;// [sp+2B0h] [bp-1FA4h]@11  
intv88;// [sp+2B4h] [bp-1FA0h]@11  
intv89;// [sp+2BCh] [bp-1F98h]@11  
intv90;// [sp+2C4h] [bp-1F90h]@11  
intv91;// [sp+2CCh] [bp-1F88h]@11  
intv92;// [sp+2D4h] [bp-1F80h]@11  
intv93;// [sp+2DCh] [bp-1F78h]@11  
intv94;// [sp+2E4h] [bp-1F70h]@11  
intv95;// [sp+2ECh] [bp-1F68h]@11  
intv96;// [sp+2F4h] [bp-1F60h]@11  
intv97;// [sp+2FCh] [bp-1F58h]@11  
intv98;// [sp+304h] [bp-1F50h]@11  
intv99;// [sp+30Ch] [bp-1F48h]@11  
intv100;// [sp+314h] [bp-1F40h]@11  
intv101;// [sp+31Ch] [bp-1F38h]@11  
intv102;// [sp+324h] [bp-1F30h]@11  
intv103;// [sp+32Ch] [bp-1F28h]@11  
intv104;// [sp+334h] [bp-1F20h]@11  
intv105;// [sp+33Ch] [bp-1F18h]@11  
intv106;// [sp+344h] [bp-1F10h]@11  
intv107;// [sp+348h] [bp-1F0Ch]@11  
intv108;// [sp+34Ch] [bp-1F08h]@11  
intv109;// [sp+354h] [bp-1F00h]@11  
intv110;// [sp+35Ch] [bp-1EF8h]@11  
intv111;// [sp+364h] [bp-1EF0h]@11  
intv112;// [sp+36Ch] [bp-1EE8h]@11  
intv113;// [sp+374h] [bp-1EE0h]@11  
intv114;// [sp+37Ch] [bp-1ED8h]@11  
intv115;// [sp+384h] [bp-1ED0h]@11  
intv116;// [sp+38Ch] [bp-1EC8h]@11  
intv117;// [sp+394h] [bp-1EC0h]@11  
intv118;// [sp+3A4h] [bp-1EB0h]@11  
intv119;// [sp+3ACh] [bp-1EA8h]@11  
intv120;// [sp+3B4h] [bp-1EA0h]@11  
intv121;// [sp+3BCh] [bp-1E98h]@11  
intv122;// [sp+3C4h] [bp-1E90h]@11  
intv123;// [sp+3CCh] [bp-1E88h]@11  
__int64 v124;// [sp+3D0h] [bp-1E84h]@11  
intv125;// [sp+3D8h] [bp-1E7Ch]@11  
intv126;// [sp+404h] [bp-1E50h]@11  
intv127;// [sp+40Ch] [bp-1E48h]@11  
intv128;// [sp+414h] [bp-1E40h]@11  
intv129;// [sp+41Ch] [bp-1E38h]@11  
intv130;// [sp+424h] [bp-1E30h]@11  
intv131;// [sp+42Ch] [bp-1E28h]@11  
intv132;// [sp+434h] [bp-1E20h]@11  
intv133;// [sp+43Ch] [bp-1E18h]@11  
intv134;// [sp+444h] [bp-1E10h]@11  
intv135;// [sp+44Ch] [bp-1E08h]@11  
intv136;// [sp+454h] [bp-1E00h]@11  
intv137;// [sp+45Ch] [bp-1DF8h]@11  
intv138;// [sp+464h] [bp-1DF0h]@11  
intv139;// [sp+46Ch] [bp-1DE8h]@11  
intv140;// [sp+474h] [bp-1DE0h]@11  
intv141;// [sp+47Ch] [bp-1DD8h]@11  
intv142;// [sp+484h] [bp-1DD0h]@11  
intv143;// [sp+48Ch] [bp-1DC8h]@11  
intv144;// [sp+494h] [bp-1DC0h]@11  
intv145;// [sp+49Ch] [bp-1DB8h]@11  
intv146;// [sp+4A4h] [bp-1DB0h]@11  
intv147;// [sp+4ACh] [bp-1DA8h]@11  
intv148;// [sp+4B4h] [bp-1DA0h]@11  
intv149;// [sp+4BCh] [bp-1D98h]@11  
intv150;// [sp+4C4h] [bp-1D90h]@11  
intv151;// [sp+4CCh] [bp-1D88h]@11  
intv152;// [sp+4D4h] [bp-1D80h]@11  
intv153;// [sp+4DCh] [bp-1D78h]@11  
intv154;// [sp+4E4h] [bp-1D70h]@11  
DWORD flOldProtect;// [sp+4E8h] [bp-1D6Ch]@11  
intv156;// [sp+4ECh] [bp-1D68h]@11  
intv157;// [sp+4F0h] [bp-1D64h]@11  
intv158;// [sp+4F4h] [bp-1D60h]@11  
intv159;// [sp+4F8h] [bp-1D5Ch]@11  
intv160;// [sp+4FCh] [bp-1D58h]@11  
intv161;// [sp+500h] [bp-1D54h]@11  
intv162;// [sp+504h] [bp-1D50h]@11  
intv163;// [sp+508h] [bp-1D4Ch]@11  
intv164;// [sp+50Ch] [bp-1D48h]@11  
intv165;// [sp+514h] [bp-1D40h]@11  
intv166;// [sp+51Ch] [bp-1D38h]@11  
intv167;// [sp+524h] [bp-1D30h]@11  
intv168;// [sp+52Ch] [bp-1D28h]@11  
intv169;// [sp+534h] [bp-1D20h]@11  
intv170;// [sp+53Ch] [bp-1D18h]@11  
intv171;// [sp+544h] [bp-1D10h]@11  
intv172;// [sp+54Ch] [bp-1D08h]@11  
intv173;// [sp+554h] [bp-1D00h]@11  
intv174;// [sp+55Ch] [bp-1CF8h]@11  
intv175;// [sp+564h] [bp-1CF0h]@11  
intv176;// [sp+56Ch] [bp-1CE8h]@11  
intv177;// [sp+574h] [bp-1CE0h]@11  
intv178;// [sp+57Ch] [bp-1CD8h]@11  
intv179;// [sp+580h] [bp-1CD4h]@11  
intv180;// [sp+584h] [bp-1CD0h]@11  
intv181;// [sp+588h] [bp-1CCCh]@11  
intv182;// [sp+58Ch] [bp-1CC8h]@11  
intv183;// [sp+594h] [bp-1CC0h]@11  
intv184;// [sp+59Ch] [bp-1CB8h]@11  
intv185;// [sp+5A4h] [bp-1CB0h]@11  
intv186;// [sp+5ACh] [bp-1CA8h]@11  
intv187;// [sp+5B4h] [bp-1CA0h]@11  
intv188;// [sp+5BCh] [bp-1C98h]@11  
intv189;// [sp+5C4h] [bp-1C90h]@11  
intv190;// [sp+5C8h] [bp-1C8Ch]@11  
intv191;// [sp+5CCh] [bp-1C88h]@11  
intv192;// [sp+5D4h] [bp-1C80h]@11  
struct_SYSTEM_INFO SystemInfo;// [sp+5E4h] [bp-1C70h]@2  
intv194;// [sp+608h] [bp-1C4Ch]@11  
  
v0 =0;  
do  
{  
GetMessageTime();  
GetLastError();  
GetScrollBarInfo(0,0,0);  
GetNativeSystemInfo(&SystemInfo);  
if(v0 >1809073)  
{  
v1 =v86;  
if((v86 !=1610947977||(unsigned__int64)v86
>>32!=2)&&SystemInfo.dwProcessorType !=1718787859)  
break;  
}  
++v0;  
}  
while(v0 <807178237);  
sub_401C10(v2,HIDWORD(v1));  
dwProcessList =(DWORD)LocalAlloc(0,0);  
lpAddress =(LPVOID)dwProcessList;  
dword_494D04 =3859826;  
sub_4014C0();  
flNewProtect =64;  
v3 =0;  
dword_489140 =1852990827;  
dword_489147 =1818504754;  
word_489145 =13164;  
byte_489144 =101;  
word_48914B =108;  
do  
{  
if(v3 ==149369)  
dword_494140 =(int)LoadLibraryW(L"kernel32.dll");  
++v3;  
}  
while(v3 <414547);  
dword_494D0A =1635087474;  
dword_494D12 =1952671092;  
dword_494D0E =1869762668;  
word_494D08 =26966;  
byte_494D16 =0;  
VirtualProtect(0,0,flNewProtect,&flOldProtect);  
v107 =984736533;  
v194 =300683120;  
v94 =80588566;  
v117 =1817873516;  
v157 =500847454;  
v179 =1567821180;  
v159 =1302637794;  
v112 =1102436357;  
v66 =899399102;  
v89 =2040936832;  
v52 =481066167;  
v190 =1841489596;  
v110 =1320909356;  
v54 =61576618;  
v58 =1178734012;  
v161 =1482589055;  
v181 =298804231;  
v104 =1400812470;  
v105 =1196260586;  
v163 =569189960;  
v126 =801563110;  
v127 =1457221645;  
v128 =1225722463;  
v129 =1834749888;  
v130 =670996619;  
v131 =1969515359;  
v132 =1280972747;  
v133 =780222590;  
v134 =1565701075;  
v102 =500443203;  
v135 =65803943;  
v115 =762364861;  
v136 =795810006;  
v137 =1123148568;  
v75 =1586276094;  
v138 =1272800795;  
v139 =924921076;  
v140 =1718812028;  
v141 =1730685708;  
v142 =2001956140;  
v143 =733391458;  
v144 =506360562;  
v145 =1591939451;  
v146 =1816995675;  
v147 =1117439759;  
v148 =2071161438;  
v149 =1258081861;  
v150 =487789358;  
v151 =253059646;  
v152 =1521776890;  
v153 =1617526422;  
v154 =1568020332;  
v156 =1488928045;  
v158 =420254226;  
v160 =929234955;  
v162 =434500457;  
v164 =291757002;  
v165 =1433345698;  
v166 =1265348856;  
v167 =59085654;  
v168 =477351671;  
v169 =1502814571;  
v170 =708847487;  
v171 =867103262;  
v172 =1897004126;  
v173 =1426888824;  
v174 =604078171;  
v175 =1657983563;  
v176 =907912865;  
v177 =334151250;  
v178 =1807653057;  
v180 =798053520;  
v182 =2101597025;  
v183 =1737159747;  
v184 =2106467861;  
v185 =1098556205;  
v186 =934388979;  
v187 =463230843;  
v188 =161500149;  
v189 =1707528495;  
v191 =443682014;  
v192 =806916367;  
v44 =2015156112;  
v35 =874317377;  
v125 =-1682276044;  
v37 =-539816070;  
v28 =8361777;  
v11 =1479804677;  
v84 =-1664213492;  
v38 =47748601;  
v20 =-1786914781;  
v33 =-59558049;  
v14 =-1369878636;  
v39 =703739348;  
v76 =370184992;  
v47 =-1286993151;  
v87 =-440185045;  
v29 =-164279037;  
v88 =953428873;  
v40 =471044069;  
v90 =-621945634;  
v41 =-1649439383;  
v68 =570423521;  
v78 =-396555381;  
v42 =1354703776;  
v91 =1053309223;  
v92 =-966288137;  
v93 =948576792;  
v95 =103542622;  
v16 =-160961522;  
v30 =1887566721;  
v96 =766532142;  
v31 =-341077087;  
v97 =-1585396389;  
v98 =1996873759;  
v43 =994006893;  
v99 =1669983487;  
v19 =-1439980314;  
v71 =-1548404952;  
v53 =826379314;  
v49 =-812990010;  
v32 =1662205266;  
v12 =272612147;  
v100 =-558352969;  
v101 =1155305092;  
v69 =885717425;  
v22 =456490846;  
v55 =-1869724207;  
v45 =1059130515;  
v103 =-102452497;  
v56 =-1166643018;  
v8 =2097853817;  
v83 =1543706697;  
v57 =1469996252;  
v10 =282560698;  
v46 =-441585956;  
v106 =-615454186;  
v108 =-111346605;  
v21 =237988083;  
v13 =523591549;  
v109 =763210334;  
v36 =-1744225943;  
v111 =95942471;  
v17 =-866671475;  
v59 =1143821186;  
v60 =-1813524758;  
v61 =-624344467;  
v62 =-883867412;  
v113 =2142616159;  
v114 =-456368282;  
v34 =864555578;  
v116 =-154194316;  
v63 =1089270003;  
v7 =-1425798802;  
v18 =1413697337;  
v64 =1701337139;  
v24 =-1306592042;  
v65 =769109638;  
v67 =-197533786;  
v70 =238612091;  
v118 =-1864660361;  
v9 =1906236105;  
v85 =-1019740156;  
v23 =-1044823509;  
v72 =1393427805;  
v48 =1505955198;  
v15 =1012219434;  
v73 =-1179555117;  
v74 =113605890;  
v119 =811375557;  
v50 =1244845555;  
v120 =190203595;  
v121 =1974199582;  
v77 =-446442448;  
v79 =1301378219;  
v80 =1312276212;  
v122 =290208957;  
v123 =1184418735;  
v25 =-269624990;  
v81 =649263029;  
v82 =758748848;  
v27 =-1203314781;  
HIDWORD(v124)=-1497302171;  
v86 =887858579;  
v26 =1938448780;  
sub_401B00(v4);  
lpAddress =(LPVOID)2786;  
return::v0();  
}

结合之前第一次启动123.exe我们并没有看到什么效果，所以这段很可疑。接下来我们去OD跟随，跟进之前标记的关键函数那里：

![](https://image.3001.net/images/20230420/1681989144_64411e186df33fffbc392.png!small)

跟进去很容易找到这里，就是前面我们看到IDA看到的地方：

![](https://image.3001.net/images/20230420/1681989146_64411e1ad0e9443b6f62b.png!small)

找到下面，到virrtualproject函数这里，修改内存属性，找到参数地址，在数据区域找到，下内存断点，记录一下Address=0x002BEAD0,顺便下个内存断点:

![](https://image.3001.net/images/20230420/1681989149_64411e1d476b59a1e5d8b.png!small)

这里对Address地址+0AE23.cn，然后call了shellcode地址：

![](https://image.3001.net/images/20230420/1681989151_64411e1f615b548c8f57a.png!small)

我们跟进shellcode看看内容，首先是一段动态获取函数，一直跟到如下位置：

![](https://image.3001.net/images/20230420/1681989154_64411e222a11523e49655.png!small)

这里是对区段进行覆盖拷贝的一个操作。后面就是很大一坨动态加载函数的操作，然后修改启动项这些，拷贝自己，最后就是启动了新的程序，结束自己：

![](https://image.3001.net/images/20230420/1681989155_64411e23648c9515ae2bd.png!small)

第一个123.exe也就是干了这么一件事。我们再看第二个，再次启动了一下他本身：  
读取了很多后缀名exe的文件：

![](https://image.3001.net/images/20230420/1681989157_64411e2508a4b07922e05.png!small)

创建了SystemID和PersonalID.txt还有readme.txt的生成：

![](https://image.3001.net/images/20230420/1681989158_64411e2688ee87471fb45.png!small)

后面又对exe、txt、py、dat、udd、js等等后缀名的文件进行了重写和重命名：

![](https://image.3001.net/images/20230420/1681989159_64411e27db578d5893198.png!small)

然后一直运行，直至退出，所以第二次启动才是关键，我们停止第二个，清空监控列表，看看第三个：

![](https://image.3001.net/images/20230420/1681989161_64411e29123981c2a691e.png!small)

同样是对文件读写重命名操作，但是会重复启动。接下来我们恢复快照追追第二个123.exe：

![](https://image.3001.net/images/20230420/1681989162_64411e2a6a3ae66ebbcca.png!small)

后续就是遍历目录生成readme.txt还有文件加密，这里不再多追。。。

# 六、结束语

主要是通过动态申请一段空间，放入shellcode，然后修改自己文件，进行校验，然后跳到开头执行，进行注册表启动，拷贝，网络链接等操作，然后重新启动自个，还有拷贝到c盘下的123.exe。主要加密功能由后续修改过得代码实现。

