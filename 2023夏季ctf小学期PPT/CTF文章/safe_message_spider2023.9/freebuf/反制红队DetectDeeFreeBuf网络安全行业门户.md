*严正声明：本文与本工具仅限于技术讨论与分享，严禁用于非法途径。

## 前言

笔者于2021年在北京最后一次参加国HW，当时作为蓝队，依靠溯源反制，使驻守单位成为了在全国军工单位中第一个拿到分的单位。

现在距离当时恰好两年，回想自己当蓝队时内心中无数种构思，最终挑选了一种并加以实现，用于给即将HW的蓝队增加胜算， ~~扒光红队底裤。~~  
  
后期将根据法律法规，判断是否添加撞库功能与笔者三年前提出的多平台用户画像功能，敬请期待。

# DetectDee

神探狄仁杰: 在[社交网络](site.md)上通过 **用户名，电子邮件或电话** 搜索社交媒体账户

  * 包括HackerOne, FreeBuf, 52Pojie, LeetCode, Github, V2ex, Zhihu等国内常用网站。

![example.gif](https://image.3001.net/images/20230501/1682949195_644fc44bd84408ad4b1c9.gif!small)

## 特性

  * 集成 **网络安全从业者** 常用网站

  * 通过 **用户名，电子邮件或电话** 查找社交媒体账户

  * 可拓展，简单易用的模板

  * 集成社交网站的移动端版本

## 安装

### 直接下载运行(推荐)

https://github.com/piaolin/DetectDee/releases

### 编译运行

    
    
    git clone https://github.com/piaolin/DetectDee.git
    cd DetectDee
    go mod tidy
    go run .
    

## 用法

### 探测

    
    
    Usage:
      DetectDee detect [flags]
    
    Flags:
      -c, --check          self-check
      -h, --help           help for detect
      -n, --name strings   name[s]
          --nsfw           Include checking of NSFW sites from default list.
          --precisely      Check precisely
      -p, --proxy string   Make requests over a proxy. e.g. socks5://127.0.0.1:1080
      -s, --site strings   Limit analysis to just the listed sites. Add multiple opt
    ions to specify more than one site.
      -t, --timeout int    Time (in seconds) to wait for response to requests (defau
    lt 60)
    
    Global Flags:
      -v, --verbose   verbose output
    

单一用户名搜索:

    
    
    ./DetectDee detect -n piaolin
    

多用户名搜索:

    
    
    ./DetectDee detect -n piaolin,blue
    

指定网站搜索:

    
    
    ./DetectDee detect -n piaolin -s github,v2ex
    

## 贡献

希望您能帮助我们开发“神探狄仁杰”，您的每一份提交都会得到我的重视。

下面是一些我们希望得到您帮助的事情:

  * 增加新的站点支持，可以是通知我某个网站有可用的接口，或直接编写[JSON](t.json)

  * 恢复对过去因误报而被删除的网站的支持

## 待办

  * 对探测得到的社交网站进行 **密码撞库**

  * 更多的网站支持

  * 保密

## 致谢

https://github.com/sherlock-project/sherlock

