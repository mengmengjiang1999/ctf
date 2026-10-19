![](https://image.3001.net/images/20210526/1622013110_60adf4b68b4cec7dc80b5.jpg!small)

## 安全漏洞场景分析

 **第一步：**

远程访问点密码破解

Airodump-ng的输出结果显示，攻击者USB网卡适配器可抵达的访问点信息：

![](https://image.3001.net/images/20210526/1622013129_60adf4c93b2102aac42cd.png!small)

 **第二步：**

等待连接设备（向目标访问点）的MAC ID：

![](https://image.3001.net/images/20210526/1622013140_60adf4d430710a5fba528.png!small)

 **第三步：**

发送de-auth认证令牌：

![](https://image.3001.net/images/20210526/1622013147_60adf4dba96730d6ebbb1.png!small)

 **第四步：**

使用.cap文件破解密码并设置字典文件：

![](https://image.3001.net/images/20210526/1622013155_60adf4e38322dfffa9def.png!small)

 **第五步：**

连接至目标访问点，并尝试登录管理接口：

![](https://image.3001.net/images/20210526/1622013163_60adf4ebcb0b9240a920b.png!small)

由于攻击者并不知道管理接口的访问密码，因此管理终端接口会返回错误信息：

![](https://image.3001.net/images/20210526/1622013169_60adf4f18afea86511dc0.png!small)

 **第六步：**

使用互联网收集可能的默认密码或弱密码，这些密码是设备制造商默认配置的或由访问点所有者自己设置的：

![](https://image.3001.net/images/20210526/1622013176_60adf4f8e1c83024c41a5.png!small)

 **第七步：**

通过登录请求实现密码爆破：

![](https://image.3001.net/images/20210526/1622013189_60adf5053de39b1d3f101.png!small)

![](https://image.3001.net/images/20210526/1622013194_60adf50ab4e810b97d2ff.png!small)

 **第八步：**

从响应长度可以看出，Qwerty12345可以是一个可能的密码，因为响应的长度是245，其他的是234：

![](https://image.3001.net/images/20210526/1622013202_60adf512acbb21003fb4e.png!small)

 **第九步：**

尝试使用用户名：admin和密码：Qwerty12345进行登录：

![](https://image.3001.net/images/20210526/1622013218_60adf5225c68cb65805fd.png!small)

 **第十步：**

现在，将管理终端的密码设置为空，这样任何连接至该访问点的用户都可以直接登录至这个后台管理终端，并修改相关的配置：

![](https://image.3001.net/images/20210526/1622013230_60adf52e61a1bd74bbc68.png!small)

由于这里存在客户端验证机制，因此会抛出一个错误提醒，即提示密码不能设置为空：

![](https://image.3001.net/images/20210526/1622013239_60adf5379a466fb521fd3.png!small)

但是，由于这里只实现了客户端验证，因此我们将尝试使用BurpSuite工具将新密码字段设置为空。对于用户界面来说，我们输入新密码：12足以满足客户端验证条件。

![](https://image.3001.net/images/20210526/1622013246_60adf53ee5a8c15198bff.png!small)

![](https://image.3001.net/images/20210526/1622013252_60adf544c399224bc1711.png!small)

## 将新密码设置为空

![](https://image.3001.net/images/20210526/1622013267_60adf553b4e52978c8c2c.png!small)

我们可以看到，管理终端的密码现在已经被成功设置为空了：

![](https://image.3001.net/images/20210526/1622013275_60adf55bdd38b7b7d14bc.png!small)

 **第十一步：**

现在我们可以看到，我们能够使用用户名：admin和密码：空来登录进访问点的后台管理终端了：

![](https://image.3001.net/images/20210526/1622013300_60adf574c8161a1496972.png!small)

此时显示管理终端登录成功：

![](https://image.3001.net/images/20210526/1622013307_60adf57b5c7e0ec10ff8b.png!small)

##  **总结**

这样一来，只要攻击者能够连接到访问点，他就可以随时打开一个后门来访问设备的后台管理控制台。使用这个管理控制台，他甚至可以断开合法用户访问AP的连接，还可以设置不同的传入或传出规则。

此攻击的目标接入点将是那些管理控制台配置不安全的主接入点。

