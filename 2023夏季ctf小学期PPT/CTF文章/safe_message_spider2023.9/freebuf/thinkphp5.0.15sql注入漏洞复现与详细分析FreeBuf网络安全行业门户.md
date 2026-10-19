# thinkphp5.0.15sql注入

### 复现

搭建环境  
![](https://image.3001.net/images/20211206/1638774538_61adb70ade720b28ce1a7.png)  
![](https://image.3001.net/images/20211206/1638774539_61adb70bf3c2507acfb03.png)  
![](https://image.3001.net/images/20211206/1638774540_61adb70cddf913fe12988.png)  
漏洞复现  
![](https://image.3001.net/images/20211206/1638774549_61adb7155867e3318ec9f.png)

### 漏洞分析

漏洞出在这句  
`$res = DB::table('users')->insert(['name'=>$name]);`  
跟进insert看下  
和上一篇有点像，跟进builder->insert看下  
![](https://image.3001.net/images/20211206/1638774550_61adb7169efe761038bba.png)  
parseData生成了注入语句  
![](https://image.3001.net/images/20211206/1638774551_61adb717b69a5ecfcde5a.png)  
在parseData中，如果传入参数是数组，通过switch判断第一个参数，如果是inc，则直接拼接第二第三个参数到  
![](https://image.3001.net/images/20211206/1638774552_61adb718c51256a836cbb.png)

然后直接将生成好的键值替换到模板insertSql语句中，，生成了注入语句  
`name=updatexml(1,concat(0x7,user(),0x7e),1)+1`  
`protected $insertSql = '%INSERT% INTO %TABLE% (%FIELD%) VALUES (%DATA%)
%COMMENT%';`  
![](https://image.3001.net/images/20211206/1638774554_61adb71a0d6406a01ee93.png)  
同样的,update也使用了parseData函数，所以也会导致注入  
![](https://image.3001.net/images/20211206/1638774555_61adb71b33f1b3c7622be.png)

回过头来看一下，不仅可以用inc，也可以用dec  
![](https://image.3001.net/images/20211206/1638774556_61adb71c279d608e28101.png)

上一篇是由于预处理导致的可以执行user()等函数，比较鸡肋  
但这次是真实的，通过了预处理，将sql语句交给了数据库执行  
所以可以通过报错注入查看数据  
![](https://image.3001.net/images/20211206/1638774557_61adb71d4665d6af9345b.png)  
![](https://image.3001.net/images/20211206/1638774558_61adb71eb8885978ace57.png)

### 总结

parseData函数未对用户输入进行过滤，用户输入的数据控制了代码的执行  
exp,inc,dec这些本应在sql语句生成过程中由代码生成，用户设置自增或自减  
但未考虑用户输入  
![](https://image.3001.net/images/20211206/1638774560_61adb7201b5b1f2aa443c.png)

### 如何修复

看5.0.24  
只对val[1]拼接，并且会将val[1]强制转换为floatval类型，这样就不能构造语句了  
但根本问题还是没有解决啊！用户输入的数据控制了代码的执行！还是会产生未预期的情况  
![](https://image.3001.net/images/20211206/1638774561_61adb72145d8af3f36926.png)

假设场景，用户注册，权限0是管理员，1是普通用户  
普通用户注册时，应是1的权限，但是由于用户输入了含有'dec'的数组，导致在插入数据时，让用户权限减一，造成了提权。

