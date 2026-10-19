## ****适用于：****

按照《Ubuntu 20.04 离线安装破解 Nessus 10.3.0》或类似方案完成破解，想升级到最新插件的用户。

强调：此破解方法必须是在完成注册的Nessus上进行。注册不区分在线离线、是否破解，但必须之前要注册过（注册后破解，License
Expiration和Activation Code可能变为N/A，但仍属于注册过的）

更新前：

![1669619239_63845e277fa750dff7600.png!small?1669619239366](https://image.3001.net/images/20221128/1669619239_63845e277fa750dff7600.png!small?1669619239366)

![1669619242_63845e2a14b4297bed2b2.png!small?1669619242060](https://image.3001.net/images/20221128/1669619242_63845e2a14b4297bed2b2.png!small?1669619242060)

![1669619243_63845e2b9e3a5e0bebc47.png!small?1669619243585](https://image.3001.net/images/20221128/1669619243_63845e2b9e3a5e0bebc47.png!small?1669619243585)

##  ** **准备工作：获取最新插件包****

方案一：

  1. 打开离线插件包下载网址

[ _https://plugins.nessus.org/v2/nessus.php?f=all-2.0.tar.gz
&u=YYYYYY&p=ZZZZZZ_](https://plugins.nessus.org/v2/nessus.php?f=all-2.0.tar.gz&u=YYYYYY&p=ZZZZZZ)

其中的YYYYYY和ZZZZZZ为用户号码。若没有或忘记该地址，需重新在官网注册，获取插件包下载地址

  2. 下载离线插件包到Linux系统下

方案二：

  1. 获得Nessus软件的挑战码

/opt/nessus/sbin/nessuscli fetch --challenge

![1669619264_63845e402466cebd067fe.png!small?1669619264218](https://image.3001.net/images/20221128/1669619264_63845e402466cebd067fe.png!small?1669619264218)

  2. 在官网上获得激活码，这里需输入邮箱，邮箱可反复使用

[ _https://www.tenable.com/products/nessus/nessus-essentials_](https://www.tenable.com/products/nessus/nessus-essentials)

![1669619266_63845e42a41ffcc59afa8.png!small?1669619266507](https://image.3001.net/images/20221128/1669619266_63845e42a41ffcc59afa8.png!small?1669619266507)

![1669619278_63845e4eef7df914344cb.png!small?1669619278805](https://image.3001.net/images/20221128/1669619278_63845e4eef7df914344cb.png!small?1669619278805)

  3. 访问网站[ _https://plugins.nessus.org/v2/offline.php_](https://plugins.nessus.org/v2/offline.php)，在其中输入刚才获得的挑战码和激活码，点击subimt，获取插件包下载地址，下载并拷贝到Linux主机上

![1669619282_63845e52e3cb3d429de5d.png!small?1669619282866](https://image.3001.net/images/20221128/1669619282_63845e52e3cb3d429de5d.png!small?1669619282866)

![1669619474_63845f12746a19838db6c.png!small?1669619474366](https://image.3001.net/images/20221128/1669619474_63845f12746a19838db6c.png!small?1669619474366)

##  ** **本机环境：****

Ubuntu 20.04 虚拟机

##  ** **离线破解更新插件教程：****

  1. 在更新前，停止nessus服务

systemctl stop nessusd.service

![1669619305_63845e69ef7c4b2822c2a.png!small?1669619305838](https://image.3001.net/images/20221128/1669619305_63845e69ef7c4b2822c2a.png!small?1669619305838)

  2. 取消plugins目录下所有文件只读属性，该过程用时稍长，因为插件数量在10w+

find /opt/nessus/lib/nessus/plugins/ -name "*.*" | xargs -i chattr -i {}

![1669619308_63845e6c86e65959e677b.png!small?1669619308378](https://image.3001.net/images/20221128/1669619308_63845e6c86e65959e677b.png!small?1669619308378)

  3. 升级插件

/opt/nessus/sbin/nessuscli update /yourpath/all-2.0.tar.gz

其中的yourpath为插件包路径

![1669619310_63845e6e8f45071540bf8.png!small?1669619310467](https://image.3001.net/images/20221128/1669619310_63845e6e8f45071540bf8.png!small?1669619310467)

  4. 设置更新的插件只读，该过程用时稍长，因为插件数量在10w+

find /opt/nessus/lib/nessus/plugins/ -name "*.*" | xargs -i chattr +i {}

![1669619312_63845e709e59a35946b90.png!small?1669619312495](https://image.3001.net/images/20221128/1669619312_63845e709e59a35946b90.png!small?1669619312495)

  5. 取消配置文件只读属性

chattr -i /opt/nessus/lib/nessus/plugins/plugin_feed_info.inc

![1669619314_63845e72dee0bc99a7427.png!small?1669619314702](https://image.3001.net/images/20221128/1669619314_63845e72dee0bc99a7427.png!small?1669619314702)

  6. 查看更新的配置文件内容

cat /opt/nessus/lib/nessus/plugins/plugin_feed_info.inc

![1669619328_63845e80c61e51193c275.png!small?1669619328707](https://image.3001.net/images/20221128/1669619328_63845e80c61e51193c275.png!small?1669619328707)

记住里面的PLUGIN_SET的数字

  7. 编辑更新后的配置文件

vi /opt/nessus/lib/nessus/plugins/plugin_feed_info.inc

编辑内容为：

PLUGIN_SET = "XXXXXX";

PLUGIN_FEED = "ProfessionalFeed (Direct [Eval])";

PLUGIN_FEED_TRANSPORT = "Tenable Network Security Lightning";

其中XXXXXX为PLUGIN_SET的数字

![1669619331_63845e83e77d29a19ebc5.png!small?1669619331793](https://image.3001.net/images/20221128/1669619331_63845e83e77d29a19ebc5.png!small?1669619331793)

  8. 取消var目录下的plugin_feed_info.inc只读属性

chattr -i /opt/nessus/var/nessus/plugin_feed_info.inc

![1669619334_63845e86dab131eccdd65.png!small?1669619334684](https://image.3001.net/images/20221128/1669619334_63845e86dab131eccdd65.png!small?1669619334684)

  9. 编辑文件内容

vi /opt/nessus/var/nessus/plugin_feed_info.inc

将内容更改为：

PLUGIN_SET = "XXXXXX";

PLUGIN_FEED = "ProfessionalFeed (Direct)";

PLUGIN_FEED_TRANSPORT = "Tenable Network Security Lightning";

其中XXXXXX为PLUGIN_SET的数字

![1669619337_63845e89a3ada5ce191bd.png!small?1669619337518](https://image.3001.net/images/20221128/1669619337_63845e89a3ada5ce191bd.png!small?1669619337518)

  10. 设置该文件只读

chattr +i /opt/nessus/var/nessus/plugin_feed_info.inc

![1669619347_63845e9380a4a95d14cfd.png!small?1669619347330](https://image.3001.net/images/20221128/1669619347_63845e9380a4a95d14cfd.png!small?1669619347330)

  11. 拷贝到同级目录的plugins目录下

cp /opt/nessus/var/nessus/plugin_feed_info.inc /opt/nessus/var/nessus/plugins/

![1669619360_63845ea0298de27e36af0.png!small?1669619360001](https://image.3001.net/images/20221128/1669619360_63845ea0298de27e36af0.png!small?1669619360001)

  12. 启动服务

systemctl start nessusd.service

![1669619363_63845ea3ed3ea1bcc8193.png!small?1669619363824](https://image.3001.net/images/20221128/1669619363_63845ea3ed3ea1bcc8193.png!small?1669619363824)

启动后，Nessus会加载更新后的插件，该过程耗时很长，需要几十分钟到几小时

  

##  ** **最终效果：****

![1669619378_63845eb25aff32b8e9964.png!small?1669619378278](https://image.3001.net/images/20221128/1669619378_63845eb25aff32b8e9964.png!small?1669619378278)

![1669619380_63845eb4a321f687ab8f5.png!small?1669619380460](https://image.3001.net/images/20221128/1669619380_63845eb4a321f687ab8f5.png!small?1669619380460)

![1669619383_63845eb71c17530c0133d.png!small?1669619382980](https://image.3001.net/images/20221128/1669619383_63845eb71c17530c0133d.png!small?1669619382980)

![1669619391_63845ebfdde515bdc876f.png!small?1669619392112](https://image.3001.net/images/20221128/1669619391_63845ebfdde515bdc876f.png!small?1669619392112)

对比更新前后的照片可以发现，插件集日期完成更新，插件数量有增加。

