### 记一次sql注入

题目环境:`https://security.bilibili.com/sec1024/q/#/user/list`

有两个与后台交互的接口

两个接口都测试了sql注入

这里主要讲下怎么发现的sql注入，个人觉得还是比较难测出来(我比较菜)

sql注入接口是在`/sec1024/q/admin/api/v1/log/list`

 **测试user_id**

正常发出数据包,没有返回数据![](https://image.3001.net/images/20211025/1635169967_6176b6afb9ff9a1ead2a4.png!small)

猜测可能跟action参数有关，将action值删除![](https://image.3001.net/images/20211025/1635170012_6176b6dc9a3a1ffad4697.png!small)

修改user_id值为一个不存在的数据，说明语句查询为空时，响应包长度为57![](https://image.3001.net/images/20211025/1635170046_6176b6fe228255320690d.png!small)

通过post数据

`{"user_id":"1aaa","user_name":"","action":"","page":1,"size":20}`和`{"user_id":"2-1","user_name":"","action":"","page":1,"size":20}`和`{"user_id":"1'","user_name":"","action":"","page":1,"size":20}`

返回长度为57说明user_id不存在sql注入.

 **测试user_name**

在之前的数据包基础上给user_name=1,返回参数错误(unicode编码)![](https://image.3001.net/images/20211025/1635170079_6176b71f05c6966a0d9e4.png!small)

将user_id值删去,发现返回数据为空的数据包长度![](https://image.3001.net/images/20211025/1635170120_6176b7486aee750c60206.png!small)

加个单引号测试发现数据包长度返回55,说明可能sql有戏，继续测试![](https://image.3001.net/images/20211025/1635170376_6176b8485ca77fae6a69c.png!small)

`{"user_id":"","user_name":"1'#","action":"","page":1,"size":20}`返回数据包长度为55

`{"user_id":"","user_name":"1#","action":"","page":1,"size":20}`返回数据包长度为57

然后通过之上的的几个数据包，我就推测：

当语句执行错误时就返回数据包长度为55

语句正常执行时返回数据包长度为57

爆列数

返回数据包长度为55，推测语句报错了![](https://image.3001.net/images/20211025/1635170358_6176b8363e76ab4cb25fb.png!small)

猜测有过滤，尝试替换空格，返回数据包长度为57，说明语句正确执行![](https://image.3001.net/images/20211025/1635170395_6176b85b4d7c810074317.png!small)

此时爆出了提示参数错误![](https://image.3001.net/images/20211025/1635170435_6176b883d8a5f14ac8f97.png!small)这时我就懵逼了，按照之前的思路如果语句报错，应该是返回长度为55的数据包。

这时重新进行测试![](https://image.3001.net/images/20211025/1635170463_6176b89f397e9fabbb419.png!small)

![](https://image.3001.net/images/20211025/1635170502_6176b8c6e7a3e753df194.png!small)

![](https://image.3001.net/images/20211025/1635170725_6176b9a534e0137246b10.png!small)

通过这三个数据包总算搞懂了后台逻辑，首先user_name是个数字型注入(跟name挂钩了，按理说应该是字符型)，这是万万没想到的。user_name的值传进去，先检测有没有关键字，如果有关键字，就直接返回长度为55的数据包，如果没有则执行sql语句，如果sql语句执行成功，则返回长度为57的数据包，如果sql语句执行错误，则返回参数错误的提示

接下来就是普通的联合注入了

直接给payload吧

`{"user_id":"","user_name":"1/**/union/**/select/**/1,(select/**/group_concat(id)from/**/flag),user(),4,5#","action":"","page":1,"size":20}`

