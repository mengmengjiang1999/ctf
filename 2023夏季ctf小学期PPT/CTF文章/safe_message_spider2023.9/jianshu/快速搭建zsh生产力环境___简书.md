快速搭建zsh生产力环境

[ _ede6](https://www.jianshu.com/u/46ed36f563fc)关注赞赏支持

# 快速搭建zsh生产力环境

## 1\. 安装 zsh 并切换为默认 shell

centos:

    
    
    yum install zsh -y 
    

debian/ubuntu:

    
    
    apt install zsh -y
    

macos:

    
    
    brew install zsh -y
    

然后:

    
    
    chsh -s /bin/zsh
    

## 2\. 安装 oh-my-zsh 并添加常用插件

视情况需要修改本地的 hosts 文件或者科学上网

    
    
    sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
    
    
    
    git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
    
    
    
    git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
    

若访问失败, host可参考我的另一篇文章:

<https://www.jianshu.com/p/c181ea5469f3>

## 3\. 修改 zsh 配置, 启用插件

    
    
     vim ~/.zshrc
    
    
    
    plugins=(
      git
      zsh-autosuggestions
      zsh-syntax-highlighting
    )
    

最后 source 一下或者退出重进就行了

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [Pwn环境搭建 （含Arm Pwn 环境）](https://www.jianshu.com/p/a7e2da50263e)

从零开始的CTF Pwn环境搭建 做一个合格的Pwn手需要一套标准的作业环境，就目前所接触到的环境和题目，将Pwn...

[WhiteYan](https://www.jianshu.com/u/1d54cd69bb7a)阅读 11,301评论 1赞 5

  * [mac前端开发环境搭建：iTerm + Zsh + Oh-My-Zsh](https://www.jianshu.com/p/5866983e0816)

前言 小博最近换工作啦，之前电脑是公司资产，已还，使用了很久的舒适开发环境没了，好多配置没存档，真是泪牛满面……入...

[T_ingyu](https://www.jianshu.com/u/ec78379aca64)阅读 1,303评论 0赞 7

  * [Mac配置终端环境 iTerm2 + Zsh + Oh My Zsh + tmux](https://www.jianshu.com/p/1b7c5ed4fb23)

iTerm2iTerm 2 is a terminal emulator for Mac OS X that do...

[Zero___](https://www.jianshu.com/u/5de113af3a59)阅读 3,734评论 1赞 2

  * [线上项目搭建生产环境](https://www.jianshu.com/p/8cbf747824cd)

搭建线上环境需要做什么？1、购买域名。2、购买服务器(就是一台带外网ip的虚拟电脑)。3、配置服务器应用环境(用户...

[LoveBugs_King](https://www.jianshu.com/u/a23e6ccef90b)阅读 1,841评论 0赞 2

  * [[初闻道]搭建mac开发环境](https://www.jianshu.com/p/735da4a674d0)

拿到一台mac以后怎么初始化开发环境.本文主要以rails为例子，介绍拿到新的rmbp以后如何迅速搭建开发环境，并...

[oiahoon](https://www.jianshu.com/u/7e71d9ec1834)阅读 1,262评论 0赞 97

 