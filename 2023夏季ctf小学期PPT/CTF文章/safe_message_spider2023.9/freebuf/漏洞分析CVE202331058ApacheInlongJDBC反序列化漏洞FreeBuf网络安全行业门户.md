最近inlong出现了很多漏洞，包括CVE-2023-31098、CVE-2023-31098、CVE-2023-31062、CVE-2023-31066、CVE-2023-31454、CVE-2023-31454等等，我会将其中的有价值的漏洞分析写出来供大家参考。

## 漏洞说明

Apache InLong 是可用于构建基于流式的数据分析、建模等一站式的海量数据集成框架。

在Apache
Inlong受影响版本，由于未对接收的jdbcUrl参数过滤空格字符，导致可以利用空格绕过jdbcUrl中autoDeserialize参数过滤限制，通过认证的攻击者利用可控的jdbcUrl参数内容在MySQL
服务端触发反序列化造成任意代码执行。（漏洞说明及直接copy了）

## 影响版本

1.4.0 <= Apache InLong <= 1.6.0

## 漏洞分析

### 源码分析

根据漏洞描述我们可以看到是jdbc url的过滤问题，由于允许用户在url中输入空格所以造成了对过滤的绕过，从而引发了jdbc反序列化.

我们直接来看源码：

这里我选择DataNodeController中的testConnection方法，它对应的就是jdbc的测试链接的按钮：

![1685473920_64764a8018a007931c33d.png!small?1685473934445](https://image.3001.net/images/20230531/1685473920_64764a8018a007931c33d.png!small?1685473934445)

![1685473929_64764a89f12f5471f14f2.png!small?1685473944288](https://image.3001.net/images/20230531/1685473929_64764a89f12f5471f14f2.png!small?1685473944288)

在testConnection中，我们看到了它调用了dataNodeService.testConnection方法来进行test，跟进这个方法发现实际上它是一个接口：

![1685473936_64764a90a84cba91f364e.png!small?1685473950914](https://image.3001.net/images/20230531/1685473936_64764a90a84cba91f364e.png!small?1685473950914)

可以看到这个接口只有一个实现，跟进去看一下可以看到里面对它进行了重写，但是方法中还有一个testConnection：

![1685473942_64764a96699a07cd0ae20.png!small](https://image.3001.net/images/20230531/1685473942_64764a96699a07cd0ae20.png!small)

再次跟进，发现这次到了另一个接口，看一下它的实现有七个，好在有一个就叫做Mysql的，那么它应该就是处理mysql相关的实现了：

![1685473951_64764a9fbf1f1bb9296a1.png!small?1685473966114](https://image.3001.net/images/20230531/1685473951_64764a9fbf1f1bb9296a1.png!small?1685473966114)

![1685473956_64764aa4be863ec331fc7.png!small?1685473971124](https://image.3001.net/images/20230531/1685473956_64764aa4be863ec331fc7.png!small?1685473971124)

跟进后看到具体实现，应该很显然就是我们要找的东西了：

![1685473965_64764aad81c15c6185465.png!small?1685473979994](https://image.3001.net/images/20230531/1685473965_64764aad81c15c6185465.png!small?1685473979994)

里面的MySQLDataNodeDTO.convertToJdbcurl(request.getUrl())看样子就是判断url的方法，同样进去看一下：

![1685473972_64764ab41e79aceb23e06.png!small?1685473986434](https://image.3001.net/images/20230531/1685473972_64764ab41e79aceb23e06.png!small?1685473986434)

最后的MySQLSinkDTO.filterSensitive(jdbcUrl)应该就是过滤器了，跟进这个方法看看具体的实现：

![1685473977_64764ab9370c53da5f65b.png!small?1685473991624](https://image.3001.net/images/20230531/1685473977_64764ab9370c53da5f65b.png!small?1685473991624)

![1685473985_64764ac133f0faecc9b9e.png!small?1685473999404](https://image.3001.net/images/20230531/1685473985_64764ac133f0faecc9b9e.png!small?1685473999404)

这个方法中将SENSITIVE_PARAM_MAP中的key和url中的东西进行匹配，如果有相同的就替换成value的值，里面将所有的true全都换成了false，这样就没有办法反序列化了，最后匹配并处理完返回处理好的url，这样就过滤了危险参数。

### 绕过

虽然这里被过滤了，但是如果在关键字段autoDeserialize=true中间加上空格，就可以绕过检测，并且url仍然是可访问的，不会被过滤。

## 漏洞复现

复现就可以开始debug了，建议直接下载官方的release包然后进入到里面docker目录下的docker-compose中，修改docker-compose.yml的内容，开启manager的5005：

![1685473991_64764ac7ad015ac9f0bab.png!small?1685474005884](https://image.3001.net/images/20230531/1685473991_64764ac7ad015ac9f0bab.png!small?1685474005884)

![1685473995_64764acbaac6e954b04a2.png!small?1685474009874](https://image.3001.net/images/20230531/1685473995_64764acbaac6e954b04a2.png!small?1685474009874)

docker-compose up
-d启动后进入到manager容器中的bin，修改startup.sh的内容，将它指定的debug端口改成5005并去掉注释（官方贴心的在镜像里面内置了vim）：

![1685474001_64764ad126bbd97daa770.png!small?1685474015624](https://image.3001.net/images/20230531/1685474001_64764ad126bbd97daa770.png!small?1685474015624)

然后使用同目录下的restat.sh重启一下manager就可以开始开心地debug了，断点在前面的截图中都有，可以照着打一下。

首先我们传一个没有空格的包：

![1685474007_64764ad76f2a53221d9bc.png!small?1685474021674](https://image.3001.net/images/20230531/1685474007_64764ad76f2a53221d9bc.png!small?1685474021674)

请求发送后到达了source点，也就是获取请求的地方，可以看到这里的值还是true：

![1685474014_64764ade8dc0468f75819.png!small?1685474029163](https://image.3001.net/images/20230531/1685474014_64764ade8dc0468f75819.png!small?1685474029163)

跟进到第二个testConnection中，请求仍然没有被过滤：

![1685474025_64764ae93e5d6865a2016.png!small?1685474039583](https://image.3001.net/images/20230531/1685474025_64764ae93e5d6865a2016.png!small?1685474039583)

最后一个testConnection方法，到此为止，url还是我们发送的，但是它马上就会进入MySQLDataNodeDTO.convertToJdbcurl方法中了：

![1685474031_64764aef912059445d9f3.png!small?1685474046083](https://image.3001.net/images/20230531/1685474031_64764aef912059445d9f3.png!small?1685474046083)

跟进，进入过滤器：

![1685474037_64764af5aff895ae3950e.png!small?1685474052112](https://image.3001.net/images/20230531/1685474037_64764af5aff895ae3950e.png!small?1685474052112)

![1685474042_64764afa394b2a8c32dfc.png!small?1685474056794](https://image.3001.net/images/20230531/1685474042_64764afa394b2a8c32dfc.png!small?1685474056794)

可以看到在经过了StringUtils.replaceIgnoreCase方法后，true被替换成了false，污点也就断掉了。

那么我们传入一个带有空格的url呢：

首先开启一个恶意的mysql服务：

![1685474049_64764b0175f8e48644a46.png!small?1685474063652](https://image.3001.net/images/20230531/1685474049_64764b0175f8e48644a46.png!small?1685474063652)

然后发包，这次是带空格的：

![1685474054_64764b060505d55e8f956.png!small?1685474068372](https://image.3001.net/images/20230531/1685474054_64764b060505d55e8f956.png!small?1685474068372)

前面都一样，直接看过滤器，可以看到空格依然存在，并且没有被匹配到，送出去这个断点之后就收到了请求：

![1685474061_64764b0de10686047fd79.png!small?1685474076573](https://image.3001.net/images/20230531/1685474061_64764b0de10686047fd79.png!small?1685474076573)

![1685474067_64764b13de012397d3e67.png!small?1685474082294](https://image.3001.net/images/20230531/1685474067_64764b13de012397d3e67.png!small?1685474082294)

至此jdbc反序列化完成，绕过了检测。

在最新版本1.7.0中，过滤器之前还去除了url中的空字符，这样就避免了被这样绕过。

![1685474074_64764b1a3eb3e6aeb611b.png!small?1685474088423](https://image.3001.net/images/20230531/1685474074_64764b1a3eb3e6aeb611b.png!small?1685474088423)

## 总结

jdbc反序列化也不是新漏洞了，引起的方式基本都是autoDeserialize导致的，网上的资料有很多，具体的漏洞能做什么和mysql-connector-java的版本有关，poc网上太多我这里也就不搬运了，对此类漏洞注意的应该就是jdbcurl字段的过滤问题，本文如有不妥之处还请各位大佬批评指正！

