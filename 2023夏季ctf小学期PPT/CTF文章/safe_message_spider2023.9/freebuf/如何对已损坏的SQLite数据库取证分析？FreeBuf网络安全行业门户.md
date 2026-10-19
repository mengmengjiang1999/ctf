****

[](https://youtu.be/ug5ZuezbD3c)

**SQLite是当今最流行的数据库之一，许多移动应用台式计算机以及便携式笔记本上都用它来存储数据（例如桌面工具、浏览器以及社交媒体软件等），因此SQLite在电子取证当中也扮演着举足轻重的角色。取证网络浏览器，信使和其他数字证据来源。**

市面上有许多支持对SQLite数据库分析取证的工具，例如Magnet AXIOM，Belkasoft Evidence Center和BlackBag
BlackLight等等。这些工具可以自动解析这些数据库，甚至可以从空闲列表和未分配空间中分割数据。此外，它们还提供了SQLite查看器，取证人员可以手动来分析数据库的类型。

那么对于那些已被损坏或破坏的数据库，我们又该如何取证呢？

我们在DFIR上收到了一个无法用任何工具打开的SQLite数据库。在此之前该数据库还曾被发送给供应商解决，但得到的答案是 - 并未在数据库中发现任何表格。

话不多说让我们直奔主题，该数据库名为：“contacts2.db”。如果你有足够的移动取证经验，那么你应该能猜到这是一个典型的Android数据库，其中包含了有关用户的联系人信息。

在我们手头有许多专业的取证工具包，因此我们决定使用最流行的取证工具来尝试打开它，其中包括有Belkasoft Evidence
Center，BlackBag BlackLight，Cellebrite UFED Physical
Analyser，SQLite数据库浏览器，Magnet AXIOM和Oxygen Forensic
Detective。但让我们感到惊讶的是，该数据库正如发布者所述，没有任何工具能打开它。如下截图所示：

![1Belkasoft.png](https://image.3001.net/images/20180309/15205605295620.png!small)  

 _Belkasoft Evidence Center_  

![2BlackLight.png](https://image.3001.net/images/20180309/15205605387571.png!small)  

 _BlackBag BlackLight_  

![3PA.jpg](https://image.3001.net/images/20180309/15205605496977.jpg!small)  

 _Cellebrite UFED Physical Analyzer_  

![4SQLite-Browser.png](https://image.3001.net/images/20180309/1520560559129.png!small)  

 _SQLite数据库浏览器_  

![5Magnet.png](https://image.3001.net/images/20180309/15205605711909.png!small)  

 _Magnet AXIOM_  

![6Oxygen.png](https://image.3001.net/images/20180309/15205605826110.png!small)  

 _Oxygen Forensic Detective_  

正如你所看到的没有任何工具可以打开它。那么接下来我们该怎么做呢？让我们回到最开始！

首先，我们进入到SQLite的官方网站，并[下载](https://www.sqlite.org/download.html)用于管理数据库文件的命令行工具。

接着我们提取存档内容并将数据库放到相同的文件夹下（可选）。

启动Windows命令提示符并将目录更改为提取SQLite命令行工具的目录。

运行以下命令序列：

    
    
    sqlite3.exe database_name.db
    
    .mode insert
    
    .output database_dump.sql
    
    .dump
    
    .exit

现在你有一个包含dump数据库表的SQL文件。如果运气好的话，你则可以删除事务语句，比如BEGIN
TRANSACTION和ROLLBACK，并将文件导入到一个新的SQLite数据库中，例如，使用SQLite数据库浏览器。但由于该数据库受损严重，所以我们必须手动检查文件并将感兴趣的表保存在单独的SQL文件中。

例如，我们找到'accounts'表，它看起来像下面这样：

    
    
    CREATE TABLE accounts (_id INTEGER PRIMARY KEY AUTOINCREMENT,account_name TEXT, account_type TEXT, data_set TEXT);
    INSERT INTO accounts VALUES(1,’vnd.sec.contact.phone’,’vnd.sec.contact.phone’,NULL);
    INSERT INTO accounts VALUES(2,’primary.sim.account_name’,’vnd.sec.contact.sim’,NULL);
    INSERT INTO accounts VALUES(4,’vnd.sec.contact.agg.account_name’,’vnd.sec.contact.agg.account_type’,NULL);
    INSERT INTO accounts VALUES(506,’test@gmail.com’,’com.google’,NULL);
    INSERT INTO accounts VALUES(538,’WhatsApp’,’com.whatsapp’,NULL);
    INSERT INTO accounts VALUES(655,’test’,’com.yandex.passport’,NULL);
    INSERT INTO accounts VALUES(656,’+7 903 000-00-00′,’com.yandex.passport’,NULL);
    INSERT INTO accounts VALUES(657,’+7 925 000-00-00′,’com.yandex.passport’,NULL);
    INSERT INTO accounts VALUES(658,’+7 978 000-00-00′,’com.yandex.passport’,NULL);
    INSERT INTO accounts VALUES(672,’test’,’com.vkontakte.account’,NULL);
    INSERT INTO accounts VALUES(677,’+7 968 000-00-00′,’com.yandex.passport’,NULL);
    INSERT INTO accounts VALUES(687,’Youla account’,’com.allgotitm.youla’,NULL);
    INSERT INTO accounts VALUES(792,’+7 968 000-00-00′,’com.viber.voip’,NULL);

我们将它保存到一个单独的SQL文件中，并使用SQLite数据库浏览器创建数据库。

创建过程如下：

  * 打开SQLite数据库浏览器。
  * 从SQL文件转到文件 - 导入 - 数据库...
  * 选择SQL文件中你感兴趣的表。
  * 选择要创建的数据库的名称。
  * 现在你可以浏览数据并使用简单的SQL查询来导出数据。

![7Recovered_accounts_table.png](https://image.3001.net/images/20180309/15205606298585.png!small)  

 _恢复的表格_  

如果你想查看所有表格只需重复以上步骤即可。这个例子也向我们证明了，数字取证分析不能只依赖于取证工具，应该根据情况结合手动检查的方式，这样才能更准确的获取和分析数据。

 ***参考来源：[cyberforensicator](http://cyberforensicator.com/2018/03/03/forensic-analysis-of-damaged-sqlite-databases/)，FB小编 secist 编译，转载请注明来自FreeBuf.COM**

