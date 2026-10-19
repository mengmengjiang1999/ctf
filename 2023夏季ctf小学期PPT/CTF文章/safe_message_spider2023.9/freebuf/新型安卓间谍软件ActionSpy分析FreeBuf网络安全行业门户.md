**在跟踪Earth Empura（也称为POISON CARP / Evil
Eye）时，发现未被记录的Android间谍软件ActionSpy（AndroidOS_ActionSpy.HRX）。**

在2020年第一季度观察到Earth
Empusa针对土耳其用户的攻击活动，随后扩大到台湾。该组织使用水坑攻击，通过网络钓鱼对Android和iOS移动设备传播其恶意软件。在2020年4月发现网络钓鱼页面伪装成Android视频应用程序下载页面。假冒页面是Earth
Empusa从第三方网上商店复制建立的，页面上的恶意脚本托管在属于该组织的域上。

![1592355818_5ee96bea1f067.png!small](https://image.3001.net/images/20200617/1592355818_5ee96bea1f067.png!small)

ActionSpy自2017年以来就已经存在，攻击者可从受感染设备中收集信息。它还可以从即时消息应用程序收集聊天日志。

## 网络钓鱼攻击

Earth
Empusa网络钓鱼页面使用新闻页面作为诱骗，利用社会工程学手段诱骗其目标访问钓鱼页面。在2020年3月发现了一些新闻网页，这些新闻网页都注入了脚本，加载跨站点脚本框架BeEF。

![1592356145_5ee96d3146688.png!small](https://image.3001.net/images/20200617/1592356145_5ee96d3146688.png!small)

在2020年4月发现了另一个网上诱骗页面，该页面是从第三方商店复制而来，并注入脚本来加载ScanBox和BeEF框架。
该网络钓鱼页面邀请用户下载Android视频应用，该页面是由Earth Empusa创建，BeEF框架在该组织的域上运行。
下载分析发现该应用程序是一个未记录的Android间谍软件ActionSpy。

![1592356461_5ee96e6d8621d.png!small](https://image.3001.net/images/20200617/1592356461_5ee96e6d8621d.png!small)

![1592356469_5ee96e750cd29.png!small](https://image.3001.net/images/20200617/1592356469_5ee96e750cd29.png!small)

![1592356678_5ee96f4691695.png!small](https://image.3001.net/images/20200617/1592356678_5ee96f4691695.png!small)

## ActionSpy分析

该恶意软件冒充合法的视频应用程序Ekran。 该恶意应用与原始应用外观和功能相同。 它还受Bangcle保护，可以逃避静态分析和检测。

![1592356663_5ee96f3724a93.png!small](https://image.3001.net/images/20200617/1592356663_5ee96f3724a93.png!small)

![1592356698_5ee96f5ac8c87.png!small](https://image.3001.net/images/20200617/1592356698_5ee96f5ac8c87.png!small)

合法的Ekran APK文件嵌入在ActionSpy资产目录中，并在首次启动ActionSpy时VirtualApp准备就绪后安装在虚拟环境中。

![1592356763_5ee96f9b97d21.png!small](https://image.3001.net/images/20200617/1592356763_5ee96f9b97d21.png!small)

ActionSpy的配置（包括其C＆C服务器地址）已由DES加密，这使得ActionSpy难以静态分析。

每隔30秒，ActionSpy将收集基本设备信息，例如IMEI，电话号码，制造商，电池状态等，并将其作为心跳请求发送到C＆C服务器，服务器会返回在受感染设备上执行的命令。
C＆C与ActionSpy之间的所有通信流量均由RSA加密并通过HTTP传输。

![1592361366_5ee9819685cc7.png!small](https://image.3001.net/images/20200617/1592361366_5ee9819685cc7.png!small)

![1592361394_5ee981b2f3503.png!small](https://image.3001.net/images/20200617/1592361394_5ee981b2f3503.png!small)

## 权限分析

通常第三方应用无法访问Android文件，ActionSpy在没有root权限的情况下无法直接窃取聊天日志文件。ActionSpy采用间接方法：提示用户打开其辅助功能服务，提供内存垃圾清理服务。

![1592361705_5ee982e9a6c11.png!small](https://image.3001.net/images/20200617/1592361705_5ee982e9a6c11.png!small)

用户启用辅助功能服务后，ActionSpy将监视设备上的辅助功能事件。当用户界面发生变化（例如单击按钮，输入文本或更改视图）时，收到辅助功能事件时，ActionSpy将检查事件类型是VIEW_SCROLLED还是WINDOW_CONTENT_CHANGED，然后检查事件是否来自目标应用程序。
如果满足上述所有条件，ActionSpy会分析当前活动内容并提取昵称，聊天内容和聊天时间之类的信息。
所有聊天信息都将格式化并存储到本地SQLite数据库中。 收到“
wxrecord”命令后，ActionSpy将在数据库中收集聊天记录并将其转换为JSON格式，然后发送到C＆C服务器。

![1592361837_5ee9836d35f91.png!small](https://image.3001.net/images/20200617/1592361837_5ee9836d35f91.png!small)

根据其证书签署时间（2017-07-10），ActionSpy已存在至少三年。

![1592361873_5ee9839187271.png!small](https://image.3001.net/images/20200617/1592361873_5ee9839187271.png!small)

## 针对IOS的水坑攻击

Earth Empusa还利用水坑攻击来破坏iOS设备，攻击者将恶意脚本注入到目标可能会访问的网站上，已发现两种注入网站方式：

> 1、ScanBox框架。该框架可以从客户端环境中收集操作系统，浏览器和浏览器插件的配置文件为下一阶段的攻击做准备。
>
> 2、漏洞利用链框架，它利用了iOS设备上的漏洞。当受害者访问该框架时，它会检查HTTP请求的User-> Agent标头，以确定受害者设备上的iOS版本，并利用漏洞代码进行回复。如果User-Agent不属于任何目标iOS版本，该框架将不会提供任何有效负载。

![1592362149_5ee984a56c899.png!small](https://image.3001.net/images/20200617/1592362149_5ee984a56c899.png!small)

在2020年第一季度，漏洞利用链框架进行了升级，可以对iOS 12.3、12.3.1和12.3.2版本进行破坏。

![1592362205_5ee984dd6d022.png!small](https://image.3001.net/images/20200617/1592362205_5ee984dd6d022.png!small)

自2020年初以来已经在多个有关站点上观察到了这些注入，还发现了土耳其的新闻政党网站受到相同攻击。2020年3月在大学网站和台湾旅行社网站上发现了相同的注入，Earth
Empusa正在扩大其目标范围。

建议iOS用户保持设备更新，建议Android用户仅从受信任的站点（例如Google Play）安装应用程序，避免恶意应用程序。

## IOCs

![1592362353_5ee985717846e.png!small](https://image.3001.net/images/20200617/1592362353_5ee985717846e.png!small)

![1592362367_5ee9857f5dc50.png!small](https://image.3001.net/images/20200617/1592362367_5ee9857f5dc50.png!small)

## MITRE ATT&CK

![1592362384_5ee98590aaa10.png!small](https://image.3001.net/images/20200617/1592362384_5ee98590aaa10.png!small)

 **参考来源**

> [trendmicro](https://blog.trendmicro.com/trendlabs-security-> intelligence/new-android-spyware-actionspy-revealed-via-phishing-attacks-> from-earth-empusa/)

