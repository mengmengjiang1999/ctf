makefile 在执行时，为什么会打印输出执行的命令呢

[ 码二哥](https://www.jianshu.com/u/19adb3953a2f)关注赞赏支持

# makefile 在执行时，为什么会打印输出执行的命令呢

make 默认会打印`每条命令`，再执行。  
这个行为被定义为`回声`

# 如何不打印命令输出呢？

可以在对应命令前加上 @，可指定该命令不被打印到标准输出上

    
    
    build:
        @go build -v .
    

参考博客：  
[https://studygolang.com/articles/14444?utm_medium=referral](https://links.jianshu.com/go?to=https%3A%2F%2Fstudygolang.com%2Farticles%2F14444%3Futm_medium%3Dreferral)

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [golang打印输出fmt和log](https://www.jianshu.com/p/4cfa35bc3193)

fmt %v 值的默认格式表示。当输出结构体时，扩展标志（%+v）会添加字段名%#v 值的Go语法表示...

[无拘无束的猪](https://www.jianshu.com/u/efab2ebacc50)阅读 3,164评论 0赞 0

  * [Golang 函数执行时间统计装饰器的一个实现](https://www.jianshu.com/p/08626a0c1877)

背景 在生产环境中，为了能实时的监控程序的运行状态，少不了逻辑执行时间长度的统计。时间统计这个功能实现的期望有下面...

[Chole121](https://www.jianshu.com/u/8b179cc681d6)阅读 1,738评论 0赞 12

  * [CLI 命令行实用程序开发基础](https://www.jianshu.com/p/d7904a6194b7)

服务计算 概述 CLI（Command Line Interface）实用程序是Linux下应用开发的基础。正确的...

[蜜桃桃的冰淇淋奶昔](https://www.jianshu.com/u/355257765f69)阅读 761评论 0赞 1

  * [golang fmt格式“占位符”](https://www.jianshu.com/p/caf6cfd3a4df)

golang 的fmt 包实现了格式化I/O函数，类似于C的 printf 和 scanf。 # 定义示例类型和变...

[LWW_33d1](https://www.jianshu.com/u/2083156ad935)阅读 1,007评论 0赞 0

  * [浅谈PHP无回显命令执行的利用](https://www.jianshu.com/p/1db124ad703f)

前言 在CTF题或在一些渗透测试中往往会遇到没有回显的命令执行漏洞，为了能更好的实现对无回显命令执行漏洞的利用，我...

[CanMeng](https://www.jianshu.com/u/bcd549297bc7)阅读 226评论 0赞 1

 