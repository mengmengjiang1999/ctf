Mac 小知识收藏

[ acc8226](https://www.jianshu.com/u/7ef875ed6ee8)关注赞赏支持

# Mac 小知识收藏

### .DS_Store 文件是什么？

.DS_Store(英文全称 Desktop Services Store)是一种由苹果公司的Mac OS
X操作系统所创造的隐藏文件，目的在于存贮目录的自定义属性，例如文件们的图标位置或者是背景色的选择。相当于 Windows 下的 desktop.ini。

包含个人信息, 导出的时候记得删除. 当然不删除的话感觉也作用不大.

### 如何在当前文件夹下打开终端: finder->服务->服务偏好设置

> ### 压缩文件的时候不想要带.DS_Store

我的方法很简单, 压缩软件下载安装第三方工具. 例如我使用的eZip,按住 command 选中后右键 -> 服务 -> eZip 压缩即可

## 小知识

**mac 发热原因**

一般而言是 cpu 占用率高的缘故

### 降低 WindowServer 进程占用很高的 CPU占用，否则容易烫手

WindowServer是macOS的核心进程，负责程序的图形化显示，你在屏幕上看到的内容，都是WindowServer作用的结果。所以，这个进程是安全的。

System Preferences，点开 Accessibility > Display，勾上 Reduce
transparency：这会让一些透明的部件（例如菜单栏）的渲染压力减小。

### 如何在 Mac 上启用 root 用户或更改 root 密码

启用或停用 root 用户

  1. 选取苹果菜单 () >“系统偏好设置”，然后点按“用户与群组”（或“帐户”）。
  2. 点按锁形图标，然后输入管理员名称和密码。
  3. 点按“登录选项”。
  4. 点按“加入”（或“编辑”）。
  5. 点按“打开目录实用工具”。
  6. 点按“目录实用工具”窗口中的锁形图标，然后输入管理员名称和密码。
  7. 从“目录实用工具”的菜单栏中：

  * 选取“编辑”>“启用 Root 用户”，然后输入要用于 root 用户的密码。
  * 或者选取“编辑”>“停用 Root 用户”。

> root 用户帐户不适合日常使用。它的权限允许更改 Mac
> 所必需的文件。要撤销此类更改，您可能需要[重新安装系统软件](https://links.jianshu.com/go?to=https%3A%2F%2Fsupport.apple.com%2Fzh-
> cn%2FHT204904)。您应在完成任务后停用 root 用户。

### 修改 host 文件

  1. 打开 finder(访达) 后前往 /private/etc/hosts

  2. 并将其拉到桌面上，也就是复制一份hosts文件到桌面上，修改此文件

  3. 编辑完后就可以把桌面上的hosts文件拉回到“/private/etc文件夹中”，会弹出询问框点击“确认”，并“取代”即可

## 其他事项

**升级了macOS Sierra 后，command line tools 报错的问题** 的处理

    
    
    xcrun: error: invalid active developer path
     (/Library/Developer/CommandLineTools), missing xcrun at:
     /Library/Developer/CommandLineTools/usr/bin/xcrun
    

敲入 `xcode-select --install` 终端输入完美解决

**mac 下个人`bash_profile` 留存备份**

`~/.bash_profile`下这里记录我目前的配置

    
    
    # java
    export CLASSPATH=$JAVA_HOME/lib/tools.jar:$JAVA_HOME/lib/dt.jar:.
    # 先定义, 最终再导出也是可以的
    JAVA_HOME=/Library/Java/JavaVirtualMachines/jdk1.8.0_201.jdk/Contents/Home
    export JAVA_HOME
    export PATH=$JAVA_HOME/bin:$PATH
    
    # gradle
    export PATH=${PATH}:/Users/ale/opt/gradle/gradle-4.10.1/bin
    
    # maven
    export M2_HOME=/Users/ale/exec/apache-maven-3.6.1
    export PATH=$PATH:$M2_HOME/bin
    
    # HOMEBREW
    export HOMEBREW_BOTTLE_DOMAIN=https://mirrors.tuna.tsinghua.edu.cn/homebrew-bottles
    

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [CTF | Web安全 Part1：基础知识](https://www.jianshu.com/p/1bfc31142bab)

这应该是一个系列的文章，主要讲述的是CTF中的Web内容。当然，对于作者这种CTF中Loser，这个系列的文章与其...

[Ackerzy](https://www.jianshu.com/u/4b5e057cb735)阅读 30,231评论 1赞 118

  * [2018-08-02 Mac的Terminal终端命令](https://www.jianshu.com/p/e837adad394e)

转载两篇Mac的终端命令，索引备用，细节使用还是需要help或者man来查看。 转载1：https://blog....

[遵天循道](https://www.jianshu.com/u/6da8a6c9d972)阅读 2,351评论 0赞 2

  * [Mac OS X 终端的一些命令](https://www.jianshu.com/p/14f872f7cecc)

Mac OS X 启用超级用户的方法 Root user，又名超级用户，是一个权力最高的Unix 账户，Root ...

[wildLotus](https://www.jianshu.com/u/a225c6d36e9a)阅读 5,777评论 1赞 0

  * [禁止.DS_store生成](https://www.jianshu.com/p/f83e85443c50)

禁止.DS_store生成 .DS_Store，英文全称 Desktop Services Store，是Mac ...

[大浪滔滔](https://www.jianshu.com/u/0f954c9f53bf)阅读 20,847评论 7赞 6

  * [Mac解压缩方案](https://www.jianshu.com/p/cc7b7f2b80d5)

2018.09.10 更新9to5Mac 报道，Dr. Unarchiver 会上传用户浏览器历史记录，现已被Ap...

[恰克斯](https://www.jianshu.com/u/e84aa668cbe7)阅读 17,223评论 0赞 3

 