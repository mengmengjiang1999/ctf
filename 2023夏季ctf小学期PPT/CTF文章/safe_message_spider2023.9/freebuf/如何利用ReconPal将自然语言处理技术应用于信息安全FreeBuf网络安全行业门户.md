![](https://image.3001.net/images/20220831/1661951508_630f5e14b01516c5c1628.png!small)

## 关于ReconPal

网络侦查一直是网络安全研究以及渗透测试活动中最重要的阶段之一，而这一阶段看起来很容易，但往往需要很大的努力和很强的技术才能做好来。首先，我们需要使用正确的工具、正确的查询/语法以及正确的操作，并将所有信息关联起来，而且还要对数据进行清洗和过滤。对于经验丰富的安全专业人士来说，这个任务可能很容易就能做到。但对于新手来说，这就非常困难了。

ReconPal整合了GPT-3、基于深度学习的语言模型以及其他著名网络侦查工具，以生成人类可读的文本，除此之外该工具还支持使用语音命令执行漏洞利用操作和网络侦查任务。

## 工具组件

> OpenAI GPT-3
>
> Shodan API
>
> Speech-to-Text
>
> Telegram Bot
>
> Docker Containers
>
> Python 3

## 工具要求

如需确保ReconPal的正常运行，我们首先需要安装下列组件：

> Telegram Bot（BotFather）
>
> Shodan API（账号和API密钥）
>
> Google语音转文字API
>
> OpenAI API密钥
>
> Docker

## Docker环境配置

    
    
    sudo apt-get updates​
    
    sudo apt-get install docker.io​
    
    sudo curl -L "https://github.com/docker/compose/releases/download/1.26.0/docker-compose-$(uname -s)-$(uname -m)" -o​ /usr/local/bin/docker-compose​
    
    chmod +x /usr/local/bin/docker-compose

## 工具安装

首先，广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/pentesteracademy/reconpal.git

然后，在docker-compose.yml文件中输入你的OpenAI API密钥、Shodan API密钥和Telegram Bot令牌：

    
    
    OPENAI_API_KEY=<Your key>
    
    SHODAN_API_KEY=<Your key>
    
    TELEGRAM_BOT_TOKEN=<Your token>

最后，使用下列命令即可运行ReconPal：

    
    
    docker-compose up

## 工具使用

打开Telegram App，然后选择创建的Bot以使用ReconPal。

然后运行下列命令启动ReconPal，并注册模块，然后开启测试命令：

    
    
    /start
    
    /register
    
    scan 10.0.0.8

## 工具运行截图

![](https://image.3001.net/images/20220831/1661951551_630f5e3f2e64e71a2bf4c.png!small)![](https://image.3001.net/images/20220831/1661951557_630f5e4570bd90f3afff5.png!small)

![](https://image.3001.net/images/20220831/1661951563_630f5e4b7d212bccc4888.png!small)

![](https://image.3001.net/images/20220831/1661951569_630f5e51b5d64d3d32a73.png!small)

![](https://image.3001.net/images/20220831/1661951578_630f5e5ad6585090d39a1.png!small)

  

## 工具使用演示

 **视频地址** ： _https://www.you*tube.com/watch?v=gBQFlirFqpk_

## 许可证协议

本项目的开发与发布遵循[ _GPL_
_-2.0_](https://github.com/pentesteracademy/reconpal/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **ReconPal** ：【[ _GitHub传送门_](https://github.com/pentesteracademy/reconpal)】

## 参考资料

> [ _https://core.telegram.org/bots_](https://core.telegram.org/bots)
>
> [ _https://account.shodan.io/_](https://account.shodan.io/)
>
> [ _https://cloud.google.com/speech-to-text/docs/before-you-> begin_](https://cloud.google.com/speech-to-text/docs/before-you-begin)
>
> [ _https://beta.openai.com/account/api-> keys_](https://beta.openai.com/account/api-keys)
>
> [ _https://www.blackhat.com/asia-22/arsenal/schedule/#reconpal-leveraging-> nlp-for-> infosec-26232_](https://www.blackhat.com/asia-22/arsenal/schedule/#reconpal-> leveraging-nlp-for-infosec-26232)

