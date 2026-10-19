## 1.前言

其实这个问题一早就出现了，Mysql蜜罐读文件的方式也是玩出了各种花样，读wx ID，读配置文件，当然也是有了后续mysql蜜罐读cs的配置文件。

![1690879923_64c8c7b3bceaef72a9e92.png!small](https://image.3001.net/images/20230801/1690879923_64c8c7b3bceaef72a9e92.png!small)

## 2\. 简单修改Cobaltstrike

cs配置文件路径：C:\Users\Administrator\\.aggressor.prop

该路径主要存放的为连接信息，账号密码等，就是为了方便下次直接登录。类似于记住密码一样

![1690880301_64c8c92de0c9d13e1e3a1.png!small](https://image.3001.net/images/20230801/1690880301_64c8c92de0c9d13e1e3a1.png!small)

同理当攻击者连接Mysql蜜罐之后，攻击者的CS也就凉凉，该配置文件中password明文裸奔。

反编译一波，经过查找，发现存储的地方在Prefs这个类中

![1690880423_64c8c9a7916993add9944.png!small](https://image.3001.net/images/20230801/1690880423_64c8c9a7916993add9944.png!small)

这里没有细究，可以看到最终都是使用到了myFile方法对该配置文件进行load等等操作

![](https://image.3001.net/images/20230801/1690882146_64c8d06)

