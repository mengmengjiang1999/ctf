**在对xHunt攻击活动分析中，发现一个科威特组织的网页被用作水坑攻击。该网页包含一个隐藏图像，其与xHunt攻击活动使用的域名相关联。**

Hisoka攻击活动的参与者泄露了该HTML代码，并将其注入该网站，试图从网站访问者获取帐户名和密码散列。攻击者计划破解这些散列以获取访问密码，或者使用收集到的散列进行中继攻击以获得其他系统的访问权。帐户凭据对攻击者可有多种用途，攻击者可破坏目标组织并窃取敏感信息。此外，由于他们使用的是可信的凭据，可以让攻击者长时间不被发现，使他们能够渗透到组织的其他部分，甚至植入后门，这可能会在较长时间内对组织造成重大损害。

在同一时间段内发现运营商基础设施上有DNS重定向活动的痕迹，观察到使用的域包含电子邮件服务器关联的子域，表明了攻击者对获取用户凭据的兴趣。

##  科威特政府网站分析

在xHunt开源研究中发现一个属于科威特政府组织的网站，引用了Hisoka相关C2基础设施上的一个图片。从2019年5月开始，该图像只想域microsofte
update[.]com，但在2019年12月更改为learn
service[.]com。从2020年1月起，此图片不再指向其他域。分析这个网站上的HTML代码，如图1和图2所示，更好地理解这个组织的网站将如何从用于恶意活动的C2服务器加载图像。

图1显示了该网页试图从URI加载图像的：///\\\microsofte
update[.]com\c$\。由于“visibility:hidden”样式属性，此URI不会显示给网站访问者。该URI使用“file”URI方案，限定域microsofte
update[.]com作为主机，“c$”作为映像的路径。HTML会尝试将“C:”文件共享作为图像加载到远程服务器上。从逻辑上讲这段代码是没有意义，因为“C:”驱动器本身不会作为映像加载。图2显示了2019年12月托管图像文件的URL的变化，其余代码保持不变。

![](https://image.3001.net/images/20200206/1580991741_5e3c04fda6ed6.png!small)![](https://image.3001.net/images/20200206/1580991747_5e3c05038bddc.png!small)

攻击者试图从网页的访问者获取NTLM散列形式的帐户凭据，Windows在与服务器进行身份验证时可以使用NTLM散列。当访问包含此代码的网页时，用户的浏览器可能会尝试通过访问远程服务器上的文件共享来加载图像。要访问此远程文件共享，Windows将执行NTLM质询响应身份验证尝试。如果URI中指定的actor-controlled服务器配置为模拟NTLM握手，并且网站访问者位于允许内部Windows网络协议访问actor-controlled服务器（如服务器消息块（SMB）和NetBIOS）的本地网络上，然后参与者可以为该访问者捕获NTLM散列和其他系统信息。捕获NTLM散列后，参与者可以破解散列以获取用户密码，或者在中继攻击中使用散列。这也可能导致对组织的完全破坏，并允许攻击者长时间不被发现。

为了进行测试，在实验室的服务器上设置了[Responder](https://github.com/lgandx/Responder)工具，并将环境配置为将域microsofte
update[.]com解析为指定服务器。然后从实验室的另一个注入了HTML代码的系统访问了该网站，并观察收集的域名、用户名、IP地址和NTLM哈希值，如下图：

![](https://image.3001.net/images/20200206/1580999543_5e3c2377d4f22.png!small)

##  DNS重定向

在分析科威特网页上的攻击活动期间，在AutoFocus中的分析中观察到DNS重定向。如下图所示，在2019年5月，科威特组织的域开始解析xHunt使用的基础结构。

![](https://image.3001.net/images/20200207/1581055890_5e3cff927b73d.png!small)

通过RiskIQ PassiveTotal发现在2019年4月发生变更的另一个科威特政府组织。

![](https://image.3001.net/images/20200207/1581056017_5e3d001100d67.png!small)这些更改获得了与xHunt活动关联的DNS重定向基础结构。，可以识别出2018
Sakabota活动和2019 Hisoka活动的DNS重定向，所有重定向都与科威特政府和私营部门组织有关。
下图显示了活动的时间轴，其中第一行显示了目标组织，中间的行显示了基础架构的更改，底部显示了相关的xHunt域。

![](https://image.3001.net/images/20200207/1581056193_5e3d00c1bceef.jpg!small)

与[FireEye](https://www.fireeye.com/blog/threat-research/2019/01/global-dns-hijacking-campaign-dns-record-manipulation-at-scale.html),
[Crowdstrike](https://www.crowdstrike.com/blog/widespread-dns-hijacking-activity-targets-multiple-sectors/),和[Cisco
Talos](https://blog.talosintelligence.com/2019/04/seaturtle.html)报告类似，发现在域主机更改的同时创建的一个或多个Let's
Encrypt的证书，所有证书都包含重定向域的名称。

进一步分析了DNS重定向活动中先前报告的基础结构，尽管没有与xHunt基础架构直接重叠，但在同一IP范围内确定了新的xHunt攻击方案。其中一种是与Sakabota相关的域名sakabota
[.] com。该域在2018年9月解析为IP地址185.15.247 [.]
140。在2017年12月至2018年1月之间，此IP被用于DNS劫持活动。还注意到在不同的时间范围内，这些相同IP范围内重定向域都包含子域mx，mail或owa，这表明攻击者以邮件凭据为目标。基础结构的相似性在下面的附录中给出。

##  总结

在科威特网站上识别出的注入的HTML代码表明，攻击者尝试从网站访问者获取凭据；收集帐户名和密码哈希，参与Hisoka攻击的组织发起了此次活动。利用网络运营商设施针对中东的网络攻击并非新鲜事，许多基础架构经常被重用甚至共享。多个攻击活使用的运营商基础架构重叠表明该区域受到攻击组织持续的关注。

##  附录

![](https://image.3001.net/images/20200207/1581057824_5e3d0720d3ba1.png!small)![](https://image.3001.net/images/20200207/1581057833_5e3d07294d0dc.png!small)***参考来源：[unit42](https://unit42.paloaltonetworks.com/xhunt-campaign-new-watering-hole-identified-for-credential-harvesting/)，由Kriston编译，转载请注明来自FreeBuf.COM**

