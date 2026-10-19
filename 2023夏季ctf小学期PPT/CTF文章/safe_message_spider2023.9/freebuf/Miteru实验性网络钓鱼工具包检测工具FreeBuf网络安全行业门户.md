![1.jpg](https://image.3001.net/images/20190703/1562159039_5d1ca7bf92b16.jpg!small)

## Miteru

 **Miteru是一款实验性网络钓鱼检测工具，广大研究人员可以使用这款工具来进行网络钓鱼工具的感染检测。**

## 工具运行机制

该工具可以从下列来源收集钓鱼URL地址：

1、 [CertStream-Suspicious feed](https://urlscan.io/search/#certstream-suspicious)

2、 [OpenPhish feed](https://urlscan.io/search/#OpenPhish)

3、 [PhishTank feed](https://urlscan.io/search/#PhishTank)

4、 [Ayashige feed](https://github.com/ninoseki/ayashige)

### 功能介绍

1、 钓鱼工具检测与收集；

2、 Slack通知；

3、 线程检测

## 工具安装

    
    
    gem install miteru

## 工具使用

    
    
    $miteru
    
    Commands:
    
      miteru execute         # Execute the crawler
    
      miteru help [COMMAND]  # Describe available commands or one specific command
    
    $miteru help execute
    
    Usage:
    
      miteru execute
    
    Options:
    
      [--auto-download], [--no-auto-download]              # Enable or disable auto-downloadof phishing kits
    
      [--ayashige], [--no-ayashige]                        # Enable or disableayashige(ninoseki/ayashige) feed
    
      [--directory-traveling],[--no-directory-traveling]  # Enable ordisable directory traveling
    
      [--download-to=DOWNLOAD_TO]                          # Directory todownload file(s)
    
                                                          # Default: /tmp
    
      [--post-to-slack], [--no-post-to-slack]              # Post a message to Slack if itdetects a phishing kit
    
      [--size=N]                                           #Number of urlscan.io's results. (Max: 10,000)
    
                                                          # Default: 100
    
      [--threads=N]                                        #Number of threads to use
    
      [--verbose], [--no-verbose]
    
                                                          # Default: true
    
    Executethe crawler

### 结果输出：

    
    
    $miteru execute
    
    ...
    
    <https://dummy1.com:it> doesn't contain a phishing kit.
    
    <https://dummy2.com:it> doesn't contain a phishing kit.
    
    <https://dummy3.com:it> doesn't contain a phishing kit.
    
    <https://dummy4.com:it> might contain a phishing kit (dummy.zip).

## 使用Docker（如果你没有安装Ruby的话）

    
    
    $ git clone <https://github.com/ninoseki/miteru.git>
    
    $ cd miteru/docker
    
    $docker build -t miteru .
    
    $docker run miteru
    
    # ex.auto-download detected phishing kit(s) into host machines's /tmp directory
    
    $docker run -v /tmp:/tmp miteru execute --auto-download

## 工具配置

如果你想使用--post-to-slack功能，你需要设置以下环境变量：

SLACK_WEBHOOK_URL:你的SlackWebhook URL；

SLACK_CHANNEL:用于发送消息的Slack信道(默认值: "#general")；

## Slack通知  

![2.png](https://image.3001.net/images/20190703/1562159129_5d1ca819561a3.png!small)

## 替换方案

1、
[t4d/StalkPhish](https://github.com/t4d/StalkPhish)：网络钓鱼工具跟踪器，可收集钓鱼工具以供研究使用。

2、 [duo-labs/phish-collect](https://github.com/duo-labs/phish-collect)：用于追踪钓鱼工具的Python脚本；

3、
[leunammejii/analyst_arsenal](https://github.com/leunammejii/analyst_arsenal)：安全分析师的利器；

### 项目地址

Miteru：【[GitHub传送门](https://github.com/ninoseki/miteru)】

 ***
参考来源：[ninoseki](https://github.com/ninoseki/miteru)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

