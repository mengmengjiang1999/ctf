近期毒霸安全团队通过“捕风”威胁感知系统捕获一类新的Gh0st远控木马变种，该木马变种通过虚假的Telegram的安装程序从而给用户电脑植入后门。此类远控木马是Gh0st远控木马修改而成，具有较强的隐蔽性，在用户电脑上驻留后会监视屏幕、执行cmd命令和调用插件。调用插件通过C2服务器返回数据进行反射式dll注入加载，不仅实现了插件的多样化，而且更容易绕过杀软的行为检测，对用户危害很大。

除了Telegram的Windows安装程序被植入远控木马外，其网站上所提供的安卓客户端也同样存在被修改的情况，额外的添加了广告模块和上传用户隐私信息模块。广告模块在聊天信息栏的顶部推送轮播广告，严重影响用户观感。App广告模块中会员商城的”卡密套餐”功能模块还提示”电脑端即将上线，敬请期待"，推测目前通过钓鱼网站散布的电脑版本尚处于测试阶段。

##  **1.虚假Telegram安装程序**

文件信息：

![](https://image.3001.net/images/20201110/1605006682_5faa755a49f7c9540589f.png!small)

捕获到的两个不同版本的安装程序都是使用NSIS进行打包，使用7-zip（7-zip在9.33的版本加入了自动反编译NSIS脚本的功能，但又在15.06把这个功能拿掉了，所以要注意7-zip版本必须介于这两者之间）解压缩得到安装脚本[NSIS].nsi。

![](https://image.3001.net/images/20201110/1605008012_5faa7a8cdb94040d084c1.png!small)

|

![](https://image.3001.net/images/20201110/1605006863_5faa760f2af13ba76cb1e.png!small)  
  
---|---  
  
ns.reg中的内容包含base64加密后的payload和base64加密后的C2

![](https://image.3001.net/images/20201110/1605006891_5faa762b8de95043b7054.png!small)![](https://image.3001.net/images/20201110/1605006902_5faa7636698dbfba52dcd.png!small)

在2.1.10版本的安装程序中缺少了远控相关文件，在脚本中发现，文件是通过网络从[www.telegramsvip.com](http://www.telegramsvip.com)下载到本地。两个脚本中共同的行为使用ComputerName替换ns.reg中的123456，并使用regedit.exe进行导入，同时将AddInProcess.exe程序注册服务自启并执行，实现其持久化。

![](https://image.3001.net/images/20201110/1605007007_5faa769f08a04422817f5.png!small)|
![](https://image.3001.net/images/20201110/1605007022_5faa76aedfa5fbeb0d282.png!small)  
---|---  
  
为提高隐蔽性，释放的加载器伪装成微软Microsoft®.NET
Framework中的AddInProcess.exe程序。AddInProcess.exe程序将写入注册表中的payload进行解密并加载运行。

![](https://image.3001.net/images/20201110/1605007105_5faa7701867cad86004fc.png!small)payload解密后得到一个名为“反射”的.net程序。反射.exe的Main函数主要功能是对字符串"MTU0LjIyMi4xMDMuNTg6Nzg3OA=="解密，解密后是一C2IP地址：154.222.103.58:7878，之后调用StartWorkThread函数，传入解密后的C2IP
。StartWorkThread参数对参数进行判断是否为空，为空时，使用备用C2IP，解密字符串"MTg1LjIyNC.4xNjguMTMwOjM1NjM="得到备用C2IP地址："185.224.168.130:3563"。

![](https://image.3001.net/images/20201110/1605007130_5faa771a6a6667544905c.png!small)Program.MainThread函数解析出一个PE文件，并把C2写入PE中并调用导出函数"Launch"。

![](https://image.3001.net/images/20201110/1605007154_5faa77329400d8ccc9645.png!small)

Program.MainThread解析出的PE文件在ida中的PDB信息为："D:\source\MyJob\企业远程控制\Release\ServerDll.pdb"。该PE文件是远控Gh0st的变种。
该远控木马在接收和发送TCP数据前会进行简单的位运算进行加解密。

发送数据加密方式：

![](https://image.3001.net/images/20201110/1605007209_5faa7769a19a15425d624.png!small)

接收数据解密方式：

![](https://image.3001.net/images/20201110/1605007226_5faa777a884334e57be59.png!small)该远控木马执行时，客户端会向C2服务器发送以下信息：IP、主机名、操作系统、是否管理员运行、安装杀软信息、CPU信息、运行时长、感染时间、分组和插件信息。

![](https://image.3001.net/images/20201110/1605007273_5faa77a9a6d213cdb4de2.png!small)该Gh0st变种木马，调用插件使用了反射式DLL注入技术，从C2服务器返回数据中读取PE数据加载执行，减少文件"落地"被查杀，因此更容易绕过杀软的文件检测。

远控木马功能| 反射式注入dll  
---|---  
![](https://image.3001.net/images/20201110/1605007356_5faa77fce32cab79e3619.png!small)|
![](https://image.3001.net/images/20201110/1605007376_5faa7810594d7b809e22e.png!small)  
  
## 2.虚假Telegram安卓端

在移动互联网时代，全球移动操作系统市场中，安卓占据了半壁江山，如此巨大的份额也引来了大量不法分子从事非法活动。钓鱼网站中Telegram的安卓安装包也被添加了广告模块和上传用户隐私的模块。

为了与C2服务器连接的稳定性，会从以下四个域名选取访问速度最快的进行连接。

![](https://image.3001.net/images/20210108/1610075655_5ff7ce07a276d11271003.png!small)

广告模块主要以注册会员、购买卡密、收取广告费进行盈利。

![](https://image.3001.net/images/20201110/1605008049_5faa7ab16c9112b277237.png!small)|
![](https://image.3001.net/images/20201110/1605007497_5faa788916804720a2c6b.png!small)  
---|---  
  
上传用户信息调用分布在org.telegram.ui.DialogsActivity和org.telegram.ui.LaunchActivity类中：

![](https://image.3001.net/images/20201110/1605007541_5faa78b563c08302ffc31.png!small)

以下是获取用户隐私数据的具体方式：

①获取隐私聊天记录

在应用界面恢复到DialogsActivity时，从SQLite数据库中获取最后一次上传时间到当前时间的聊天记录，调用uploadSecretMsg上传到服务器。

![](https://image.3001.net/images/20201110/1605007604_5faa78f4ec470da25cb9b.png!small)

|
![](https://image.3001.net/images/20201110/1605007618_5faa7902d974e3932fcc8.png!small)|
![](https://image.3001.net/images/20201110/1605007637_5faa791513f5d94962af5.png!small)  
---|---|---  
  
②获取位置信息

使用Telegram开源代码中的定位功能，获取定位信息并上传服务器。

![](https://image.3001.net/images/20201110/1605007710_5faa795e6969e4e7db118.png!small)

③获取联系人和Tg用户信息

在DialogsActivity创建视图时，创建一个定时任务，每隔60秒执行一次上传uploadContactsBook函数，该函数根据参数控制上传联系人或Tg用户信息。

![](https://image.3001.net/images/20201110/1605007742_5faa797e1527661c847f0.png!small)

联系人信息

| Tg用户信息  
---|---  
![](https://image.3001.net/images/20201110/1605007807_5faa79bf25a8a30ad3200.png!small)|
![](https://image.3001.net/images/20201110/1605007838_5faa79dea694aaa3f390d.png!small)  
  
④获取公开组信息

在上传隐私聊天记录时，获取聊天的类型，如果是公开组则上传组对应的id和名称。

![](https://image.3001.net/images/20201110/1605008112_5faa7af03a1f5757dd923.png!small)

## 3.关联

通过Censys搜索"Telegram中文版"，发现IP 45.114.106.2-45.114.106.6为同一内容的钓鱼网站。

![](https://image.3001.net/images/20201110/1605008163_5faa7b230c4fb01ea98ab.png!small)

目前搜集到的相关钓鱼网站域名如下：

> telegram-cn.org
>
> telegram-vip.com
>
> telegramcn.org
>
> telegrcn.org
>
> telegramsvip.com

由于Telegram没有官方的中文安装包，普通用户通常会使用第三方搜索引擎来查找对应的中文安装程序，该团伙针对这类用户，在谷歌、必应等搜索引擎做了相应的SEO优化，提高其钓鱼网站在相关搜索关键词结果页的排名，甚至还在谷歌中投放相关的广告来给自己网站引流，可谓是煞费苦心。

![1605008227_5faa7b63e7a86b6af4077.png!small?1605008230186](https://image.3001.net/images/20201110/1605008227_5faa7b63e7a86b6af4077.png!small?1605008230186)

|
![](https://image.3001.net/images/20201110/1605008209_5faa7b51ee7964dc5583c.png!small)|
![1605008244_5faa7b7427e9256cdb110.png!small?1605008246527](https://image.3001.net/images/20201110/1605008244_5faa7b7427e9256cdb110.png!small?1605008246527)  
---|---|---  
  
## 4.总结

目前，钓鱼网站仍在持续运行、更新中，建议广大用户安装金山毒霸杀毒软件保护自己的信息安全。同时提高个人安全意识，下载软件时，尽量到官方网站或正规的第三方下载。

##  **IOC**

###  **MD5：**

> 5d605a0f6f1bea25b528ef7a258f5304
>
> ffbfe89d3e01dd9fd6f8c7ade96fe51d
>
> 49d9e4337da8d3956c752ba8c896a826
>
> 7bde93fd52e668e7c7a47f1073784cfe
>
> 08e97bf5b77800a2256d26c8fa049d87
>
> fe2d2b11632e465827e9dcac.41fae79a
>
> 2cba6bd2a7a27d708d6c70b8aeec13c5

###  **签名：**

> OORT inc.
>
> Driver Information Technology Co., Ltd.

###  **C2:**

> 154.222.103.58:7878
>
> 185.224.168.130:3563
>
> 1928.ga
>
> 1928.gq
>
> 1oba.com
>
> hamster2018.com
>
> telegram-cn.org
>
> telegram-vip.com
>
> telegramcn.org
>
> telegrcn.org
>
> telegramsvip.com

