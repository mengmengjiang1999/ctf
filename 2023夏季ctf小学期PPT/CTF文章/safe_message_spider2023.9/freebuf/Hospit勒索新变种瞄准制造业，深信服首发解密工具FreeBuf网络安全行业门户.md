## ****背景概述****

Hospit勒索病毒最早于2020年12月被发现，其 **主要通过RDP暴破等方式传播，具有很强的行业针对性**
。早期变种加密后缀为”.guanhospit”，攻击目标均为医疗单位。而此次发现的变种加密后缀为”.builder”，攻击目标均为制造业。由此可以看出，Hospit勒索病毒背后的团伙似乎不同于其他勒索团伙的随机选择，该团伙每一次行动都具有很强的目标性，未来可能将有更多的行业成为其攻击目标。

![](https://image.3001.net/images/20210128/1611816511_60125e3f83a64ffdd670f.png!small)

深信服终端安全团队通过对捕获的样本进行分析，其对于10M以下的文件加密存在漏洞，加密秘钥存在被暴破的可能，第一时间开发了对该勒索病毒的解密工具，可以
**对被hospit勒索病毒加密的低于10M的文件进行解密** ，挽回部分损失数据。

##  ** **勒索解密****

解密工具下载地址：https://edr.sangfor.com.cn/api/download/DecryptHospit.exe

 **使用说明** ：

  1. 需要提供一个被加密前的原文件，以及其被加密后的文件，用于暴破密钥，尽量选择比较小且加密时间较早的文件；
  2. 输入Key Identifier，可从勒索信息中进行复制；
  3. 根据勒索发生后是否重启过主机等情况，进行对应的选择；
  4. 如果密钥暴破成功，输入需要解密的目录进行解密。

![](https://image.3001.net/images/20210128/1611816547_60125e631a28f6405f974.gif!small)

##  ** **样本分析****

1.创建互斥量，防止重复运行：

![](https://image.3001.net/images/20210128/1611816612_60125ea439579609ad086.png!small)

2.创建线程，当检测到如下进程时退出并自删除，用于反调试：

![](https://image.3001.net/images/20210128/1611816633_60125eb96b6ea1c2fb1a2.png!small)

3.结束并卸载Raccine：

![](https://image.3001.net/images/20210128/1611816650_60125ecacec34d0197c13.png!small)

4.开启Dnscache等服务，并结束安全软件等服务，保障勒索顺利进行：

![](https://image.3001.net/images/20210128/1611816709_60125f0583725e2a4f6c0.png!small)![](https://image.3001.net/images/20210128/1611816717_60125f0d524ec51fded9e.png!small)

5.删除磁盘卷影：

![](https://image.3001.net/images/20210128/1611816735_60125f1f376ae0d19e7da.png!small)![](https://image.3001.net/images/20210128/1611816749_60125f2d778f04fe43139.png!small)

6.对于磁盘根目录下的虚拟磁盘、备份等文件， ** **直接删除**** ：

![](https://image.3001.net/images/20210128/1611816765_60125f3dcec1ad1016810.png!small)![](https://image.3001.net/images/20210128/1611816777_60125f497bfc5ce611d6a.png!small)

7.设置C、D、Z盘为完全访问权限：

![](https://image.3001.net/images/20210128/1611816799_60125f5f915820921e9f2.png!small)![](https://image.3001.net/images/20210128/1611816808_60125f682d4658fe8eafc.png!small)

8.清空回收站，配置防火墙规则放通对共享文件的访问：

![](https://image.3001.net/images/20210128/1611816825_60125f79a290c89049587.png!small)

9.使用Random生成随机秘钥，记为key_1，由于Random生成的为伪随机数，种子为系统运行时间，因此如果能够计算出勒索时系统运行时间，则可能暴破出秘钥：

![](https://image.3001.net/images/20210128/1611816839_60125f879971b73d99ab1.png!small)

10.在病毒所在目录生成如下txt文件，内容为终端IP、勒索时间以及RSA加密并base64编码的key_1：

![](https://image.3001.net/images/20210128/1611816853_60125f95e611ce60441e2.png!small)

11.将txt勒索信息写入temp目录：

![](https://image.3001.net/images/20210128/1611816863_60125f9f327c37920effe.png!small)

在启动目录创建快捷方式，用于打开txt勒索信息，并配置快捷键“Ctrl+Shift+X”：

![](https://image.3001.net/images/20210128/1611816876_60125face1b66bd2f0bff.png!small)

12.加密如下后缀名的文件：

>
> "dat","txt","jpeg","gif","jpg","png","php","cs","cpp","rar","zip","html","htm","xlsx","xls","avi","mp4","ppt","doc","docx","sxi","sxw","odt","hwp","tar","bz2","mkv","eml","msg","ost","pst","edb","sql","accdb","mdb","dbf","odb","myd","php","java","cpp","pas","asm","key","pfx","pem","p12","csr","gpg","aes","vsd","odg","raw","nef","svg","psd","vmx","vmdk","vdi","lay6","sqlite3","sqlitedb","java","class","mpeg","djvu","tiff","backup","pdf","cert","docm","xlsm","dwg","bak","qbw","nd","tlg","lgb","pptx","mov","xdw","ods","wav","mp3","aiff","flac","m4a","csv","sql","ora","mdf","ldf","ndf","dtsx","rdl","dim","mrimg","qbb","rtf","7z"

![](https://image.3001.net/images/20210128/1611816898_60125fc2c5041bf36fae1.png!small)

13.加密后缀为“.builder”:

![](https://image.3001.net/images/20210128/1611816913_60125fd1da7f8940a316b.png!small)

14.获取已准备好且非CD的磁盘：

![](https://image.3001.net/images/20210128/1611816923_60125fdbb1a8f86bfd052.png!small)

15.豁免如下目录：

> "program files",":\windows","perflogs","internet explorer", ":\programdata",
> "appdata", "msocache","system volume information","boot","tor
> browser","mozilla","appdata", "google chrome", "application data"

![](https://image.3001.net/images/20210128/1611816944_60125ff063fcf33fc1b0a.png!small)

16.如果文件大小大于10M，则对每个文件使用RNGCryptoServiceProvider生成的真随机数作为加密秘钥，记为key_n，并使用RSA加密key_n：

![](https://image.3001.net/images/20210128/1611816959_60125fff32488f201e4d2.png!small)

17.如果文件大小小于10M，则都使用key_1作为秘钥，因此如果暴破出key_1，则可以用于解密10M以下文件：

![](https://image.3001.net/images/20210128/1611816972_6012600c4585b1f6be2c0.png!small)

18.使用Salsa20算法加密文件：

![](https://image.3001.net/images/20210128/1611816988_6012601c3af77ca77160f.png!small)

19.将RSA加密并base64编码的秘钥以及标志符“GotAllDone”写入加密后的文件末尾：

![](https://image.3001.net/images/20210128/1611816998_6012602647cd711cd3206.png!small)

20.加密完成后在桌面生成勒索信息文件：

![](https://image.3001.net/images/20210128/1611817008_6012603000578a07b5c08.png!small)

21.勒索信息内容如下：

![](https://image.3001.net/images/20210128/1611817017_6012603933ca964bca8ee.png!small)

22.勒索结束病毒文件自删除：

![](https://image.3001.net/images/20210128/1611817025_60126041cc5febfb6a2af.png!small)

##  ** **基础加固****

深信服安全团队再次提醒广大用户，勒索病毒以防为主，目前大部分勒索病毒加密后的文件都无法解密，注意日常防范措施：

1、及时给系统和应用打补丁，修复常见高危漏洞；

2、对重要的数据文件定期进行非本地备份；

3、不要点击来源不明的邮件附件，不从不明网站下载软件；

4、尽量关闭不必要的文件共享权限；

5、更改主机账户和数据库密码，设置强密码，避免使用统一的密码，因为统一的密码会导致一台被攻破，多台遭殃；

6、如果业务上无需使用RDP的，建议关闭RDP功能，并尽量不要对外网映射RDP端口和数据库端口。

