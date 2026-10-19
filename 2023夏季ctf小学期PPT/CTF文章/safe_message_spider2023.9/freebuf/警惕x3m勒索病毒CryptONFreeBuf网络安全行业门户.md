## 一、样本简介

**CryptON勒索病毒最早出现在2017年2月份左右，曾有多家企业遭到攻击，近日深信服安全服团队接收客户反馈，主机被加密勒索，加密后缀为x3m，经过跟踪分析，拿到了相应的样本，确认样本为CryptON勒索病毒的变种版本，并对此勒索病毒样本进行深入的分析。**

## 二、勒索特征

1.加密后的文件后缀为id-[数字]_[x3m-pro@protonmail.com]_[x3m@usa.com].x3m，如下所示：

![](https://image.3001.net/images/20190514/1557822133_5cda7ab5038ef.png!small)

2.勒索信息图片信息CVZRPKPA59ZMCHK9B.bmp，如下所示：

![](https://image.3001.net/images/20190514/1557822138_5cda7aba5f0e4.png!small)

3.勒索超文本文件信息###HOW TO DECRYPT FILES ###.html，如下所示：

![](https://image.3001.net/images/20190514/1557822144_5cda7ac088cac.png!small)

## 三、详细分析

1.通过解密函数，获取部分函数地址，如下所示：

![](https://image.3001.net/images/20190514/1557822151_5cda7ac7182a1.png!small)

2.在内存中解密出相应的勒索信息相关数据，如下所示：

![](https://image.3001.net/images/20190514/1557822157_5cda7acd3ab22.png!small)

解密出来的数据，如下：

![](https://image.3001.net/images/20190514/1557822164_5cda7ad4bab58.png!small)

3.通过多个解密函数，获取函数地址，如下所示：

![](https://image.3001.net/images/20190514/1557822171_5cda7adb1635a.png!small)

4.获取主机APPDATA、LOCALAPPDATA、USERNAME、USERPROFILE变量值，如下所示：

![](https://image.3001.net/images/20190514/1557822178_5cda7ae20fd90.png!small)

5.判断进程运行权限是否为管理员权限，如下所示：

![](https://image.3001.net/images/20190514/1557822183_5cda7ae78608c.png!small)

6.获取主机区域信息，如下所示：

![](https://image.3001.net/images/20190514/1557822193_5cda7af1b3cf6.png!small)

如果主机区域为:RU(俄罗斯联邦)、KZ(哈萨克斯坦)、BY(白俄罗斯)、UA(乌克兰)，则退出程序，如下所示：

![](https://image.3001.net/images/20190514/1557822216_5cda7b08dc0d0.png!small)

7.设置自启动注册表项，如下所示：

![](https://image.3001.net/images/20190514/1557822222_5cda7b0e68452.png!small)

8.判断主机是否联网，如果不联网，则退出程序，如下所示：

![](https://image.3001.net/images/20190514/1557822227_5cda7b1310ef7.png!small)

然后再生成一个[原文件]+[bat]的批处理文件，进行自删除操作，如下所示：

![](https://image.3001.net/images/20190514/1557822232_5cda7b1812cc4.png!small)

批处理内容，如下所示：

![](https://image.3001.net/images/20190514/1557822236_5cda7b1cb4fe1.png!small)

9.创建互斥变量，防止程序多次运行，如下所示：

![](https://image.3001.net/images/20190514/1557822242_5cda7b222846b.png!small)

10.创建线程，加密文件，如下所示：

![](https://image.3001.net/images/20190514/1557822246_5cda7b269e7b7.png!small)

11.创建线程，获取主机相关信息，上传到远程服务器，如下所示：

![](https://image.3001.net/images/20190514/1557822250_5cda7b2ac4356.png!small)

12.读取资源文件ID号CVZRPKPA59ZMCHK9T的数据，如下所示：

![](https://image.3001.net/images/20190514/1557822255_5cda7b2f7ede9.png!small)

解密出资源的数据，然后写入到生成的勒索信息超文件本件，如下所示：

![](https://image.3001.net/images/20190514/1557822260_5cda7b343832c.png!small)

13.遍历磁盘目录文件，如下所示：

![](https://image.3001.net/images/20190514/1557822264_5cda7b38f0ee8.png!small)

枚举共享目录文件，如下所示：

![](https://image.3001.net/images/20190514/1557822276_5cda7b44e6508.png!small)

14.加密文件，如下所示：

![](https://image.3001.net/images/20190514/1557822282_5cda7b4aee656.png!small)

加密后的文件，后缀名为id-[数字]_[x3m-pro@protonmail.com]_[x3m@usa.com].x3m，如下所示：

![](https://image.3001.net/images/20190514/1557822287_5cda7b4fc0024.png!small)

15.将资源ID为CVZRPKPA59ZMCHK9T的数据解密出来，得到勒索信息，写入到文本文件CVZRPKPA59ZMCHK9T，如下所示：

![](https://image.3001.net/images/20190514/1557822292_5cda7b5462cff.png!small)

16.将资源ID为CVZRPKPA59ZMCHK9B的数据解密出来，得到勒索信息，写入到图片文件

CVZRPKPA59ZMCHK9B，如下所示：

![](https://image.3001.net/images/20190514/1557822299_5cda7b5b95977.png!small)

17.采用POST的方式，上传主机相关信息到远程服务器地址，服务器URL相关地址：<http://paris-style.ru/forum/clientscript/ie7/graphic/qp50x.php>，如下所示：

![](https://image.3001.net/images/20190514/1557822305_5cda7b618bb88.png!small)

获取到的数据包信息，如下所示：

![](https://image.3001.net/images/20190514/1557822310_5cda7b661859f.png!small)

## 四、解决方案

针对已经出现勒索现象的用户，由于暂时没有解密工具，建议尽快对感染主机进行断网隔离。深信服提醒广大用户尽快做好病毒检测与防御措施，防范该病毒家族的勒索攻击。

### 病毒检测查杀

1、深信服为广大用户免费提供查杀工具，可下载如下工具，进行检测查杀。

> 64位系统下载链接：<http://edr.sangfor.com.cn/tool/SfabAntiBot_X64.7z>
>
> 32位系统下载链接：<http://edr.sangfor.com.cn/tool/SfabAntiBot_X86.7z>

### 病毒防御

深信服安全团队再次提醒广大用户，勒索病毒以防为主，目前大部分勒索病毒加密后的文件都无法解密，注意日常防范措施：

1、及时给电脑打补丁，修复漏洞。

2、对重要的数据文件定期进行非本地备份。

3、不要点击来源不明的邮件附件，不从不明网站下载软件。

4、尽量关闭不必要的文件共享权限。

5、更改账户密码，设置强密码，避免使用统一的密码，因为统一的密码会导致一台被攻破，多台遭殃。

6、如果业务上无需使用RDP的，建议关闭RDP。

 ***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM**

