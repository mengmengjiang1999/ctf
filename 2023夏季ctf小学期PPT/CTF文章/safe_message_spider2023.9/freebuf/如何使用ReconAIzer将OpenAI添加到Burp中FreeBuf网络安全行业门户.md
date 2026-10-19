![](https://image.3001.net/images/20230718/1689644569_64b5ee19d510fd8dee841.png!small)

## 关于ReconAIzer

ReconAIzer是一款功能强大的Burp Suite扩展，该工具基于Jython开发，可以为Burp
Stuite添加OpenAI能力，并利用OpenAI来优化和增强渗透测试过程中的网络侦查任务。该工具专为漏洞猎人和渗透测试人员设计，支持以自动化的形式执行多种网络安全任务，可以帮助广大安全研究人员以简单快速的形式识别和利用漏洞。

安装完成之后，ReconAIzer将会添加一个上下文菜单，并提供一个专用的选项卡来帮助我们查看分析处理结果：

![](https://image.3001.net/images/20230718/1689644584_64b5ee286e2baf662237c.png!small)

## 工具要求

> Burp Stuite
>
> Jython独立Jar包

## 工具安装

广大研究人员可以按照下列步骤完成ReconAIzer的安装。

### 第一步：下载Jython

1、从官方网站下载最新版本的Jython独立Jar包：

> [ _https://www.jython.org/download﻿_](https://www.jython.org/download)

2、将下载好的Jython独立Jar包保存到电脑中一个方便使用的位置；

### 第二步：在Burp Suite中配置Jython

1、打开Burp Suite；

2、点击“Extensions”标签页；

3、点击“Extensions”标签页中的“Extensions settings”子标签；

4、在“Python Environment”中，点击“Location of the Jython standalone JAR file."

”并选择“Select file”；

5、选择你之前下载好的Jython独立Jar包；

6、等待“Python Environment”状态变为“Jython (version x.x.x) successfully loaded”即可；

### 第三步：下载和安装ReconAIzer

1、点击该项目的【[
_Releases页面_](https://github.com/hisxo/ReconAIzer/releases)】下载最新版本的ReconAIzer；

2、打开Burp Suite；

3、点击Burp Suite的“Extensions”标签页；

4、点击“Add”按钮；

5、在“Add extension”对话框中，选择“Python”作为“Extension type”；

6、点击“Extension file”中的“Select file...”按钮，并选择项目的“ReconAIzer.py”文件，然后点击“Open”打开；

7、确保“Load”勾选框为选中状态，并点击“Next”；

8、等待扩展成功加载，此时你将能看到“Output”部分显示“ReconAIzer”成功加载的信息；

此时，你就已经完成了工具的下载和配置了。现在我们就可以开始在渗透测试任务中使用ReconAIzer了。

别忘了在Burp Suite的“ReconAIzer”标签页中点击“Config”选项并配置你的OpenAI API密钥。

点击【[ _这里_](https://platform.openai.com/account/api-keys)】可以找到你自己的OpenAI API密钥；

## 工具运行截图

![](https://image.3001.net/images/20230718/1689644628_64b5ee5435294efd27ba0.png!small)

## 项目地址

 **ReconAIzer** ：【[ _GitHub传送门_](https://github.com/hisxo/ReconAIzer)】

## 参考资料

> [ _https://www.jython.org/download_](https://www.jython.org/download)
>
> [ _https://platform.openai.com/account/api-> keys_](https://platform.openai.com/account/api-keys)

