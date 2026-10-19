## 背景概述

 **近日，国外分析人员报出CrazyCrypt
2.1勒索病毒，该勒索病毒集加解密模块于一体，通过AES加密算法对文件进行加密，并弹出交互窗口，受害用户通过支付赎金获取解密密钥后可通过该窗口自行解密。深信服安全团队密切关注该勒索病毒家族的最新动向，对捕获的样本进行了详细分析，并向广大用户提供免费的密钥获取工具。**

免费密钥工具下载连接：

> <http://edr.sangfor.com.cn/tool/CrazyCrypt_2.1_Password_Generator.zip>

## 病毒信息

1\. 病毒运行流程：

![](https://image.3001.net/images/20190313/1552460160_5c88a9804f1f3.png!small)

2\. 加密文件类型：

    
    
    ".doc"".docx"".xls"".xlsx"".ppt"".pptx"".jpg"".jpeg"".png"".psd"".txt"".zip"".rar"".html"".php"".asp"".aspx"".mp4"".avi"".3gp"".wmv"".MOV"".mp3"".wav"".flac"".wma"".mov"".raw"".doc"".apk"".encrypt""crypted"".ahok"".cs"".vb"".ppt"".pptx"".docx"".xlsx"".mdf"".ldf"".bak"".max"

3\. 加密后文件：

    
    
    “原文件名 + id.主机id.[crazydecrypt@horsefucker.org].crazy”

![](https://image.3001.net/images/20190313/1552460200_5c88a9a8c3275.png!small)

4\. 勒索信息：

![](https://image.3001.net/images/20190313/1552460206_5c88a9ae8ac11.png!small)

## 详细分析

### CrazyCrypt_Encrypt加密模块

1\. 创建互斥体”SINGLE_INSTANCE_APP_MUTEX”：

![](https://image.3001.net/images/20190313/1552460211_5c88a9b3c4c74.png!small)

2\. 修改WindowsDefender和系统策略：

![](https://image.3001.net/images/20190313/1552460223_5c88a9bf9590b.png!small)

![](https://image.3001.net/images/20190313/1552460239_5c88a9cf28124.png!small)

3\. 从A到Z遍历磁盘，排除包含以下字符的目录：

"Bin" "indows""tings" "System Volume Information" "cache""very" "rogram Files
(x86)" "rogram Files""boot" "efi" ".old"

![](https://image.3001.net/images/20190313/1552460229_5c88a9c51c178.png!small)

4\. 排除已加密过的文件，筛选指定后缀名的文件：

![](https://image.3001.net/images/20190313/1552460247_5c88a9d78e562.png!small)

5\. 生成密钥和IV，使用AES算法对文件进行加密，重命名文件：

![](https://image.3001.net/images/20190313/1552460251_5c88a9db1ce4e.png!small)

### CrazyCrypt_Aviso勒索信息模块

1\. 弹出勒索信息窗口：

![](https://image.3001.net/images/20190313/1552460254_5c88a9debebff.png!small)

2\. 替换加密主机ID：

![](https://image.3001.net/images/20190313/1552460257_5c88a9e1bcac0.png!small)

![](https://image.3001.net/images/20190313/1552460261_5c88a9e50ac1e.png!small)

3\. 向C&C端发送失陷主机信息：

![](https://image.3001.net/images/20190313/1552460266_5c88a9ea507be.png!small)

4\. 等待输入密码，连接C&C端获取key进行对比：

![](https://image.3001.net/images/20190313/1552460269_5c88a9edbef8d.png!small)

### CrazyCrypt_Decrypt模块

1\. 排除未加密的文件目录：

![](https://image.3001.net/images/20190313/1552460273_5c88a9f1c8534.png!small)

2\. 解密文件，自删除：

![](https://image.3001.net/images/20190313/1552460277_5c88a9f5e1fd2.png!small)

## 解决方案

针对已经出现勒索现象的用户，建议尽快对感染主机进行断网隔离，下载深信服提供的免费密钥获取工具生成密钥，解密文件。深信服提醒广大用户尽快做好病毒检测与防御措施，防范该病毒家族的勒索攻击。

## 病毒检测查杀

1、深信服为广大用户免费提供查杀工具，可下载如下工具，进行检测查杀。

64位系统下载链接：

> <http://edr.sangfor.com.cn/tool/SfabAntiBot_X64.7z>

32位系统下载链接：

> <http://edr.sangfor.com.cn/tool/SfabAntiBot_X86.7z>

## 病毒防御

深信服安全团队再次提醒广大用户，勒索病毒以防为主，目前大部分勒索病毒加密后的文件都无法解密，注意日常防范措施：

1、及时给电脑打补丁，修复漏洞。

2、对重要的数据文件定期进行非本地备份。

3、不要点击来源不明的邮件附件，不从不明网站下载软件。

4、尽量关闭不必要的文件共享权限。

5、更改账户密码，设置强密码，避免使用统一的密码，因为统一的密码会导致一台被攻破，多台遭殃。

6、如果业务上无需使用RDP的，建议关闭RDP。

 ***本文作者：千里目安全实验室，转载请注明来自FreeBuf.COM**

