## **一、背景**

 **"海莲花"（又名APT-TOCS、APT32、OceanLotus），被认为是来自中南半岛某国的APT攻击组织，自2012年活跃以来，一直针对中国的敏感目标进行攻击活动，是近几年来针对中国大陆进行攻击活动的最活跃的APT攻击组织之一。**

很多安全厂商在之前已经发布过多份关于海莲花的分析报告，报告的内容主要集中在PC端，攻击手段往往以鱼叉攻击和钓鱼攻击为主，移动端的攻击并不多见。然而，随着移动互联网的发展，一方面人们的手机逐渐出现两用性，除了包含使用者的个人隐私外，也往往会带有其社会属性，另一方面，智能手机的无线通信可以绕过内部安全监管设备，故而针对移动端的攻击也成为了整个攻击链条中的重要一环。下面，以发生于我国的一起移动端攻击事件为蓝本进行具体分析说明。

##  **二、具体分析**

![1f2d68a4e9a44611835c91366b8e93a4.jpeg](https://image.3001.net/images/20190530/15592112009498.jpeg!small)

表2-1 典型样本基本信息

该应用伪装正常应用，在运行后隐藏图标，后台释放恶意子包并接收远程控制指令，窃取用户短信、联系人、通话记录、地理位置、浏览器记录等隐私信息，私自下载apk、拍照、录音，并将用户隐私上传至服务器，造成用户隐私泄露。

## **三、样本分析**

该应用启动后会打开LicenseService服务：

![fd72ffe9f9524a7f87e90ebc5c6b810d.jpeg](https://image.3001.net/images/20190530/15592112192662.jpeg!small)

该服务会开启f线程用于注册和释放间谍子包：

![6bdfbb568e8c4012bebc9ea79291d62f.jpeg](https://image.3001.net/images/20190530/15592112435633.jpeg!small)

注册url：<http://ckoen.dmkatti.com>

![dba57073daf04d3d8aa7fbfa16ad8e35.jpeg](https://image.3001.net/images/20190530/15592112636500.jpeg!small)

动态加载间谍子包：

![eace0d7d2fae4582a7544611454407b6.jpeg](https://image.3001.net/images/20190530/155921128492.jpeg!small)

![682eedbe90e94105bac6c38a6f581131.jpeg](https://image.3001.net/images/20190530/15592113021305.jpeg!small)

## 子包分析

主包反射调用com.android.preferences.AndroidR类的Execute方法：

![fd961f3039124d2680036ee4769f47b1.jpeg](https://image.3001.net/images/20190530/15592113238117.jpeg!small)

首先建立socket连接：

![0747d6196ab14a39985e37c861715748.jpeg](https://image.3001.net/images/20190530/15592113401021.jpeg!small)

socket地址：mtk.baimind.com

通过与手机建立通讯，发送控制指令和上传短信、联系人、通话记录、地理位置、浏览器记录等部分隐私信息。

![cb93208a78b741889ca5dc898bd8e16f.jpeg](https://image.3001.net/images/20190530/15592113632.jpeg!small)

此外该间谍子包还建立了https通讯，用于上传录音、截图、文档、相片、视频等大文件。

![3ad9b7725c3b4f7b950c4873bb11be09.jpeg](https://image.3001.net/images/20190530/15592113867228.jpeg!small)

![2471a223f7f4462680b56155e9cbd252.jpeg](https://image.3001.net/images/20190530/15592114158611.jpeg!small)

https地址：<https://jang.goongnam.com/resource/request.php>，目前已经失活，该C2属于海莲花组织资产。

![3f8b9f53877a4784a1c73aeb8c138dc1.jpeg](https://image.3001.net/images/20190530/15592114382318.jpeg!small)

表3-1 CC所在位置及作用

如下图所示：首先，签名Subject中包含HackingTeam、Christian Pozz(Hacking
Team中一个管理员的名字)字样；其次，代码中的注册功能，可以认定是对外出售的商业间谍软件；最后，根据后期Hacking
Team泄漏资料来看，海莲花组织所属国家亦在其客户名单之中。

![9d4a1b7ebdcb4a2195294ca4bf65383e.jpeg](https://image.3001.net/images/20190530/15592117177571.jpeg!small)

##  **四、拓展分析**

根据注册CC的同源性，我们查找到如下样本：

![a7bffcb9c563442985a7488bc4657feb.jpeg](https://image.3001.net/images/20190530/15592117439993.jpeg!small)

表4-1 通过CC检索到的同源样本

与我们分析的样本不同，以上样本有了明显的功能改进，增加了提权功能，以45AE1CB1596E538220CA99B29816304F为例，对其assets目录名为dataOff.db的文件进行解密，解密之后的文件中带有提权配置文件，如下所示：

![f9dbdc716be0426ba3aad7a368b92af3.jpeg](https://image.3001.net/images/20190530/15592117646867.jpeg!small)

由此可见，在代码泄漏后HackingTeam组织的CEO表示“泄漏的代码只是很小一部分”的言论是有依据的，这也从侧面反映出网络军火商在一定程度上降低了APT攻击的门槛，使得网络攻击出现更多的不确定性。

同时我们也注意到，该系列恶意代码有通过国内第三方应用市场和文件共享网站进行的投递。

![212fff30f6114eda9c2ef23d44c208ed.jpeg](https://image.3001.net/images/20190530/15592117827533.jpeg!small)

表4-2 样本分发链接

##  **五、总结**

海莲花组织总是在演进变化，不断地通过更新其攻击手法和武器库以达到绕过安全软件防御的目的。除了武器库的不断更新，该组织也相当熟悉中国的情况，包括政策、使用习惯等。这不仅迷惑了相关人员，增加了其攻击成功率，同时也可能给目标受害群体带来不可估量的损失。

因此对于个人来讲，要切实提高网络安全意识，不要被网络钓鱼信息所蒙蔽；对于安全厂商来讲，更需要对其加深了解并持续进行针对性的对抗，提升安全防护能力，真正为用户侧的移动安全保驾护航。

##  **六、附录（IOC）**

    
    
     5079CB166DF41233A1017D5E0150C17A 
    
    F29DFFD9817F7FDA040C9608C14351D3
    
    0E7C2ADDA3BC65242A365EF72B91F3A8
    
    C630AB7B51F0C0FA38A4A0F45C793E24
    
    CE5BAE8714DDFCA9EB3BB24EE60F042D
    
    BF1CA2DAB5DF0546AACC02ABF40C2F19
    
    D1EB52EF6C2445C848157BEABA54044F
    
    45AE1CB1596E538220CA99B29816304F
    
    50BFD62721B4F3813C2D20B59642F022
    
    86c5495b048878ec903e6250600ec308
    
    780a7f9446f62dd23b87b59b67624887 
    
    DABF05376C4EF5C1386EA8CECF3ACD5B 
    
    86C5495B048878EC903E6250600EC308
    
    F29DFFD9817F7FDA040C9608C14351D3
    
    C83F5589DFDFB07B8B7966202188DEE5
    
    229A39860D1EBEAFC0E1CEF5880605FA
    
    A9C4232B34836337A7168A90261DA410
    
    877138E47A77E20BFFB058E8F94FAF1E
    
    5079CB166DF41233A1017D5E0150C17A
    
    2E780E2FF20A28D4248582F11D245D78
    
    0E7C2ADDA3BC65242A365EF72B91F3A8
    
    315F8E3DA94920248676B095786E26AD
    
    D1EB52EF6C2445C848157BEABA54044F
    
    DABF05376C4EF5C1386EA8CECF3ACD5B
    
    AD32E5198C33AA5A7E4AEF97B7A7C09E
    
    DF2E4CE8CC68C86B92D0D02E44315CC1
    
    C20FA2C10B8C8161AB8FA21A2ED6272D
    
    55E5B710099713F632BFD8E6EB0F496C
    
    CF5774F6CA603A748B4C5CC0F76A2FD5
    
    66983EFC87066CD920C1539AF083D923
    
    69232889A2092B5C0D9A584767AF0333
    
    C6FE1B2D9C2DF19DA0A132B5B9D9A011
    
    CE5BAE8714DDFCA9EB3BB24EE60F042D
    
    50BFD62721B4F3813C2D20B59642F022
    
    C630AB7B51F0C0FA38A4A0F45C793E24
    
    810EF71BB52EA5C3CFE58B8E003520DC
    
    BF1CA2DAB5DF0546AACC02ABF40C2F19
    
    45AE1CB1596E538220CA99B29816304F
    
    5AF0127A5E97FB4F111ECBA2BE1114FA
    
    74646DF14970FF356F33978A6B7FD59D
    
    DF845B9CAE7C396CDE34C5D0C764360A
    
    C20FA2C10B8C8161AB8FA21A2ED6272D 
    
    641F0CC057E2AB43F5444C5547E80976 

## **七、致谢**

感谢奇安信红雨滴团队（原360企业安全威胁情报小组）对于因sinkhole造成的域名归因疏漏的热心指正。

 ***本文作者：AVLTeam，转载请注明来自FreeBuf.COM**

