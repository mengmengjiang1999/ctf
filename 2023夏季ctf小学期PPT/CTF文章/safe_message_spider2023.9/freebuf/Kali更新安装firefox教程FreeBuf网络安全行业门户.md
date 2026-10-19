## 起因

台式机新装了一个Kali的虚拟机，打开后准备用burpsuite+firefox调试一个网站，于是习惯性的想装下一键代理切换的插件【FoxyProxy】，玩玩没想到：插件提示浏览器版本过低，于是决定更新下firefox的版本。

> 注意：进行下列操作前请务必将所有的Firefox的所有窗口关闭

## 1\. 下载新版本

直接点击更新或者登陆firefox官网即可<https://www.mozilla.org/zh-CN/firefox/new/>

## 2\. 解压

下载下来的文件为bz2后缀的文件

    
    
    bzip2 -d firefox.tar.bz2
    tar -xvf firefox.tar
    

## 3\. 删除旧版本

系统的firefox放在/usr/lib/firefox-esr下面，根据版本的不同，最后的一个文件夹名称可能不一样。要删除的目标有两个，一个是真实的应用文件，另一个为软链接

    
    
    # 删除旧的浏览器文件
    rm -rf /usr/lib/firefox-esr
    # 删除旧的软连接
    rm -rf /usr/lib/firefox-bin
    

## 4\. 配置新版本

将新版本的firefox移动至/usr/lib/下

    
    
    mv yourpath/firefox /usr/lib/firefox
    

并为它建立新的link文件

    
    
    ln -s /usr/lib/firefox/firefox /usr/bin/firefox
    

## 5\. 检验&&启动

在命令行输入：`type firefox`看到firefox执行的是 `/usr/bin/firefox`

在命令行输入`firefox`启动火狐浏览器

* * *

至此，我们的目的基本达到了，在firefox扩展页搜索`FoxyProxy`安装本菜最喜欢的proxy switcher工具，添加burp的代理，大功告成！

