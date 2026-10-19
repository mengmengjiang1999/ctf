## 漏洞简介：

Atom CMS 2.0版本存在远程代码执行漏洞，该漏洞源于/admin/uploads.php
未能正确过滤构造代码段的特殊元素。攻击者可利用该漏洞导致任意代码执行。

## 漏洞环境：

春秋云镜中的漏洞靶标，CVE编号为CVE-2022-25487

## 漏洞复现：

访问漏洞环境，发现是空白![](https://image.3001.net/images/20230630/1688089846_649e34f6c2ea46ac19f70.png!small)

  

  

在url上输入常见的后台目录，尝试到admin时自动跳转到登录界面，在收集信息时发现该cms有默认邮箱密码，尝试默认邮箱/密码
[alan@alan.com/password](mailto:alan@alan.com/password)可登录

![](https://image.3001.net/images/20230630/1688089896_649e35282727bc6a1b2a1.png!small)

  

登录上后台后寻找可利用的点，发现在users下的任意用户界面可以上传头像文件

![](https://image.3001.net/images/20230630/1688089944_649e3558a32aa9bd522ec.png!small)![](https://image.3001.net/images/20230630/1688089951_649e355f74d9674eba6b1.png!small)![](https://image.3001.net/images/20230630/1688089961_649e3569bae84d5e230ff.png!small)

  

写一个一句话木马并把扩展名改为图片格式尝试能不能上传成功

![](https://image.3001.net/images/20230630/1688089980_649e357cf2e5f7d6dabbd.png!small)

  

开启浏览器代理和buspsuite抓取上传文件的包，并把包放到重放器里，把文件扩展名改成php，send发送，看到返回包中有返回上传文件的地址

![](https://image.3001.net/images/20230630/1688090001_649e3591243f557c6799f.png!small)![](https://image.3001.net/images/20230630/1688090010_649e359ac1ccb9287a51a.png!small)

  

去访问木马文件，并用phpinfo();测试文件是否可用

![](https://image.3001.net/images/20230630/1688090041_649e35b9f047b14211f34.png!small)

文件可用，后面就可执行需要的命令，或者用蚁剑连接进行webshell

  

  

这里需要获取flag

![](https://image.3001.net/images/20230630/1688090074_649e35da10d27166cccb0.png!small)

  

  

