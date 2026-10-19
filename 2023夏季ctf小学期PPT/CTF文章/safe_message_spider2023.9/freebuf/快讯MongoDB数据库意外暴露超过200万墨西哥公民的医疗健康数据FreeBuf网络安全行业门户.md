![nav-header.jpg](https://image.3001.net/images/20180807/1533631630_5b695c8ed5a50.jpg!small)

**最近，一个MongoDB数据库被发现可以通过互联网公开访问，其中包含了超过200万（2,373,764）墨西哥公民的医疗健康数据。这些数据包括个人的全名、性别、出生日期、保险信息、残疾状况和家庭住址等信息。**

这个数据库是由安全研究员Bob
Diachenko通过Shodan[发现](https://www.linkedin.com/pulse/draft/AgF9Ma3EceoC2AAAAWUOuL48hIy2sW_c_L-Ul4I3UC26TKyeMXuq2VKLRNhlqJ3It9pngg8)的，Shodan是一个搜索引擎，可以搜索所有联网设备，而不仅限于Web服务器。当被发现时，这个数据库完全暴露在互联网上，任何人都可以对其访问和编辑，因为它没有设置密码。

![exposed-records.jpg](https://image.3001.net/images/20180807/1533631643_5b695c9b98dad.jpg!small)

暴露的健康记录

在分析数据库之后，Diachenko找到了包含Administrative账户电子邮件地址的字段。这些电子邮件地址的域名为hovahealth.com和efimed.care，如下所示。

![admin-passwords.jpg](https://image.3001.net/images/20180807/1533631658_5b695caad585c.jpg!small)
Administrative账户

hovahealth.com显然属于HovaHealth，一家位于墨西哥的技术公司，服务于医疗保健行业（专注于两个主要领域：远程医疗和卫生部门的软件开发）。至于efimed.care，目前尚不清楚它属于谁，但很可能是一个隶属政府管理的卫生服务机构。

Diachenko告诉BleepingComputer，他在发现数据库的同一天联系了Hova Health。Hova
Health回应说：“所有参与这个项目的人员都在审查到底发生了什么，并检查我们所有的基础设施，以避免再次发生此类事件......
”在接下来的3个小时里，这个数据库得到了保护。

虽然从数据库的条目来看，的确有人在管理它，但Diachenko告诉BleepingComputer，目前并没有人站出来表明这个数据库属于自己。所以在这一点上，这些数据实际上到底属于谁还是未知数。

BleepingComputer的Lawrence
Abrams试图联系HovaHealth和efimed.care域名的所有者，但后者无法与美国或墨西哥的任何一个网站联系起来。

在线暴露的MongoDB数据库并不是什么新鲜事。Diachenko表示，关注健康保健行业的人可不止他一个，这还包括勒索软件以及其他类型恶意软件的开发者。因此，各位数据库管理员在保护数据库时遵循最佳实践非常重要。

“MongoDB的安全隐患问题至少从2013年3月开始被人们所知道，从那以后就开始被广泛报道。”Diachenko在介绍关于这个在线暴露的数据库的博文中写道，“根据Shodan的说法，MongoDB公司早在5年前就已经在软件更新中使用了安全的默认设置，并发布了[安全指南](https://www.mongodb.com/blog/post/update-how-to-avoid-a-malicious-attack-that-ransoms-your-data)。然而，现在不安全的数据库仍然大量暴露在互联网上，此类数据库至少有54,000个。”

 ***本文作者：Hydralab，转载请注明来自FreeBuf.COM**

