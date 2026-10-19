**GitHub，相信大家并不陌生，咱搞技术的应该都会用到它，GitHub主要是进行代码工具的存储、下载等工作。今天介绍一款让我们操作GitHub相关工作变的更简单的工具,
GitHub的克隆工具。**

Cl0neMast3r是一种使用Python脚本编写的代码，开发的主要目的是推荐给渗透测试人员和bug调试人员，帮助我们在日常安全测试、程序开发及其它测试工作中更加简单和灵活。

还有个更不错的功能推荐给各位安全技术达人，就是这款Cl0neMast3r可以进行现有工具的版本检测，确保我们现在使用的是当下最新版本的工具。

使用此工具，可以轻松地从GitHub[链接文字](http://www.example.com)中选择我们喜欢的各种工具资源，只需进行简单的操作即可将它们安装到我们的系统上。

##  Cl0neMast3r **下载地址：**

<https://github.com/Abdulraheem30042/Cl0neMast3r.git>

##  **运行环境：**

> ¨ macOSHigh Sierra
>
> ¨ KaliLinux
>
> ¨ LinuxMint

目前暂时不支持Windows相关操作系统，上面提供的3种操作系统已经做过测试。

##  **运行要求：**

> ¨ Python2.7.*
>
> ¨ Requests
>
> ¨ BeautifulSoup4

##  **部署安装：**

    
    
        root@2cats:~#pip install requests

![GitHub的克隆工具Cl0neMast3r，轻松搞定各种测试](https://image.3001.net/images/20180310/15206665388309.png!small)  

root@2cats:~#pip install beautifulsoup4 //测试机之前已经安装过

![GitHub的克隆工具Cl0neMast3r，轻松搞定各种测试](https://image.3001.net/images/20180310/15206665657841.png!small)  

root@2cats:~#git clone<https://github.com/Abdulraheem30042/Cl0neMast3r.git>

![GitHub的克隆工具Cl0neMast3r，轻松搞定各种测试](https://image.3001.net/images/20180310/15206665784195.png!small)  

最后一步操作，root@2cats:~#pip install -r requirements.txt ////测试机之前已经安装过

![GitHub的克隆工具Cl0neMast3r，轻松搞定各种测试](https://image.3001.net/images/20180310/15206666002091.png!small)  

直接修改并运行文件Cl0neMast3r.py

    
    
    root@2cats:~/Cl0neMast3r# python Cl0neMast3r.py

![GitHub的克隆工具Cl0neMast3r，轻松搞定各种测试](https://image.3001.net/images/20180310/15206666094807.png!small)  

##  **选项说明：**

> [A] Add a tool using URL //github下载url链接
>
> [F] Find a tool on GitHub //在github查找工作
>
> [R] Reinstall your tools //重新安装工具
>
> [U] Update your tools //更新工具
>
> [S] Display your tools //显示工具
>
> [D] Delete tools list //删除工具
>
> [X] Export tools to HTML //导出工具到HTML
>
> [M] Import your tools //导入工具
>
> [E] Exit //退出

##  **简单使用介绍：**

以MITM攻击测试框架bettercap为例，我们首先进行工具的查找和下载。

![GitHub的克隆工具Cl0neMast3r，轻松搞定各种测试](https://image.3001.net/images/20180310/15206666237811.png!small)  

选择F进行工具GitHub查找，我们选择以文件名为关键字，当然也可以选择用户，运行结果显示找到了41个相关的工具。

由于篇幅关系，我们只显示前4个工具进行列举。

###  **工具显示如下内容：**

> ¨ 工具的类型
>
> ¨ 作者
>
> ¨ URl地址
>
> ¨ 可用性
>
> ¨ 相关描述

![GitHub的克隆工具Cl0neMast3r，轻松搞定各种测试](https://image.3001.net/images/20180310/15206666348725.png!small)  

我们选择Tool Number为1进行下载，提示添加完成。

![GitHub的克隆工具Cl0neMast3r，轻松搞定各种测试](https://image.3001.net/images/20180310/15206666434709.png!small)  

下面我们介绍第2个使用功能，工具更新，可以选择U选项。

![GitHub的克隆工具Cl0neMast3r，轻松搞定各种测试](https://image.3001.net/images/20180310/15206666535691.png!small)  

我们选择更新已有工具，选择[2]

![GitHub的克隆工具Cl0neMast3r，轻松搞定各种测试](https://image.3001.net/images/20180310/15206666707813.png!small)  

继续介绍工具的查看功能，选择S项，可以看到现有工具的状态。

![GitHub的克隆工具Cl0neMast3r，轻松搞定各种测试](https://image.3001.net/images/20180310/15206666812701.png!small)  

最后说一下，添加工具GitHub的URL地址的操作。

![GitHub的克隆工具Cl0neMast3r，轻松搞定各种测试](https://image.3001.net/images/20180310/15206667039148.png!small)  

如果工具太多可以也可直接备份到HTML文件中，这里备份的其实是GitHub的相关链接。如下图：

![GitHub的克隆工具Cl0neMast3r，轻松搞定各种测试](https://image.3001.net/images/20180310/15206667189187.png!small)  

好了，这个好用的工具分享完毕，希望可以帮助各位朋友工作起来更方便更顺手！  

 ***本文作者：2cat，转载请注明来自 FreeBuf.COM**

