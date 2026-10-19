**严正声明：本文涉及到的内容和技术仅用于教育和讨论目的，严禁用于非法用途。**

## 前言

 **2018年8月3号，我收到了一条神秘的LinkedIn消息，这条消息来自Caleb Sima，内容如下：**

![LinkedIn消息](https://image.3001.net/images/20181119/1542556944_5bf18d10513fa.png!small)

我不得不承认，我一开始都没反应过来Caleb想跟我说啥，不过看了一下URL之后（其中包含了Lambda和Shell），我感觉他应该是想告诉我他开发出了一种通过Lambda函数来执行Shell命令的技术。我之前也见过类似的东西，比如说[Lambdash](https://github.com/alestic/lambdash)。几秒钟之后，我打算点进去看一看这个Web页面，然后发现了：

![LinkedIn消息](https://image.3001.net/images/20181119/1542556948_5bf18d14e875e.png!small)

看到这段话之后，我首先得弄清楚Caleb的动机，所以我给他发了一条信息：

![LinkedIn消息](https://image.3001.net/images/20181119/1542556954_5bf18d1a1440e.png!small)

好吧，Caleb是打算让别人通过Lambda函数来攻击他的AWS账号，并最终实现Shell命令的运行。听起来确实值得一试，毕竟现在很难有人愿意把自己的账号给别人去免费“蹂躏”了，这让我非常兴奋！

## 第一步：收集情报

首先，我在当前目录(/var/task)下运行“ ls -IF”命令来提取函数处理器的文件名：

![提取函数处理器的文件名](https://image.3001.net/images/20181119/1542556966_5bf18d2632fad.png!small)

拿到文件名(index.js)之后，我通过运行“cat index.js”命令来获取函数的源代码：

![获取函数的源代码](https://image.3001.net/images/20181119/1542556972_5bf18d2c16d1f.png!small)

实际上，最初的源代码并没有让我感到惊讶，因为它就是普通的利用Lambda函数执行Shell命令的一段代码，我之前也已经见过很多类似的了。

我跟我自己说：“好吧，我现在能运行Shell命令了，可是那然后呢？我怎么才能给这个账号带来一点实际的威胁呢？”

于是，我打算收集更多信息，然后我列出了所有的环境变量，我想看看Caleb有没有留下一些有用的东西，这里可以使用‘env’命令：

![使用‘env’命令](https://image.3001.net/images/20181119/1542556979_5bf18d3309f02.png!small)

## 第二步：冒充Lambda函数

在对环境变量进行渗入分析之后，我发现当一个AWS Lambda函数执行时，它会使用一个由开发者（IAM角色）提供的临时安全证书。此时需要从AWS
STS（安全令牌服务）接收以下三个参数：

    
    
    AWS_SECRET_ACCESS_KEY
    
    AWS_ACCESS_KEY_ID
    
    AWS_SESSION_TOKEN

这是三个非常敏感的令牌，但是却直接在我的屏幕上作为环境变量打印了出来…

如果你不熟悉AWS
IAM安全模型的话，我可以告诉你，这是一个非常强大且细粒度非常高的安全权限模型，模型的具体介绍可参考AWS提供的IAM角色文档：【[传送门](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html)】。

既然我们已经拿到了AWS
STS给函数生成的令牌了，那接下来就好办了。这里我可以直接使用令牌来在本地设备上调用AWS的命令行接口。此时我需要通过调用下列命令来在本地设置这些环境变量：

    
    
    />export AWS_SECRET_ACCESS_KEY = …..
    
    />export AWS_ACCESS_KEY_ID = ….
    
    />export AWS_SESSION_TOKEN = ....

为了测试这些令牌，我打算调用AWS STS命令行实用工具来获取当前的调用者身份：

    
    
    />aws sts get-caller-identity

几秒钟之后，命令行工具会给我返回下列信息：

    
    
    {
    
    "UserId":"AROA********GL4SXW:exec",
    
    "Account":"1232*****446",
    
    "Arn":"arn:aws:sts::1232*****446:assumed-role/lambda_basic_execution/exec"
    
    }

非常好，现在我就可以在本地运行AWS命令行工具了，而且我还可以伪装成IAM角色。

当你查看AWS Lambda Web终端时，你将会看到：

![AWS Lambda
Web终端](https://image.3001.net/images/20181119/1542556988_5bf18d3cd4356.png!small)

大家可以看到，Caleb其实并没有用环境变量存储任何的应用程序隐私数据，这让我很“生气”。但是这里不得不提醒大家一下，很多开发人员确确实实会犯这样的错误，这是值得警惕的一点。

 *** 参考来源：[darkreading](https://www.darkreading.com/cloud/securing-serverless-attacking-an-aws-account-via-a-lambda-function/a/d-id/1333047?_mc=rss_x_drr_edt_aud_dr_x_x-rss-simple&utm_source=dlvr.it&utm_medium=twitter)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

