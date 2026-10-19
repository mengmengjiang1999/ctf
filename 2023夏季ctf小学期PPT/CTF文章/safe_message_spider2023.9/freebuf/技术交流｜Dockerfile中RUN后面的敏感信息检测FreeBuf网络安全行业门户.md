# 前言

之前学习过一些容器底层原理，再加上之前倾旋师傅提了一个小想法：拿到镜像，是否可以最大程度还原Dockerfile的内容，因为这个里面很可能有一些敏感信息。于是《镜像反查Dockerfile》文章就诞生了，实际上里面的技术都是已经有人做好了，我无非是复现，细节补充罢了。

这个事情并没有结束，秉承着实验室内部研究必须落地的精神，我想把这个细节落地到工具上去：在云场景的攻防中，当我们控下一个私有云的仓库的时候，通过运行某个自动化工具，将一些敏感信息提取出来。

# 准备工作

## 1\. 选择工具二开还是直接开写

如果在大学时期，我肯定选择去直接开写，锻炼一些能力。但是后面工作了这么久，才越来越感受到大道至简，况且别人已经写的很好了又无私奉献。有些时候从0开始，不如从1开始。况且那个1还是一个很成熟，很棒的工具。

## 2\. 选择哪个工具

其实我首先想到的并不是问脉，而是CDK,
也看了部分的源码，但是最后从定位来说，并不是很合适。CDK更多的是容器权限，集群权限，你可以看到CDK中关于Docker漏洞利用方面更多的是逃逸，利用。（只是定位不太合适，不妨碍CDK是一款优秀的，我也很喜欢的一款工具）

这个时候想起来了长亭的问脉 Veinmind ，Veinmind 有检测敏感信息和 history
的异常操作这块，并且从大维度来说是支持镜像和容器状态的。再加上之前也经常用，相对来说很熟悉。那么我会用到哪些模块呢？

## 3\. 分析工作

拉取 Veinmind 源码，发现两个模块比较符合：

  1. Veinmind-sensitive（扫描镜像中敏感信息）？看起来很符合。

  2. Veinmind-history （扫描镜像中的异常历史命令）？从 rules 和介绍来看不是很符合，但是里面有一些现成的匹配docker history的逻辑，这意味着我可以少写很多代码。有趣的是 我发现了https://github.com/chaitin/veinmind-tools/pull/38这个 pr ，这位师傅像给问脉的docker history 加一些检测的规则。

![](https://image.3001.net/images/20221104/1667545992_6364bb88cc4bb1ec61089.png!small)

最终我还是选择 Veinmind-sensitive 模块。这个模块的定位很详细，是扫描镜像中的异常历史命令，这个"异常"可以通过模块的 rules
去确定他的定位。举个例子：我在 Dockerfile 中 RUN 后面包含了某一串 token，或者写一个 password
，你只能说这么写会有敏感信息，但是本身也没挖矿操作，没恶意命令，当然不能说我这个镜像是有异常指令的。

![](https://image.3001.net/images/20221104/1667545996_6364bb8c5c98a0fcab018.png!small)

继续分析 Veinmind-sensitive 模块，发现该模块主要的检测逻辑依赖 rules.toml ，检测内容已经很全面了：镜像的 env 信息
、敏感文件及敏感文件中的敏感内容。但我们知道，Dockerfile 的编写中 RUN
后面是可以写任何命令，包括命令参数都可以，此时这里可能包含很多敏感信息，而 Veinmind-sensitive 没有检测到。

![](https://image.3001.net/images/20221104/1667545999_6364bb8f3e4d25c62a1d4.png!small)

对于检测工具来说，这块的检测维度必须覆盖到，这是向 Veinmind 提 pr
的好机会。很多时候我们需要把信息经过正则列举出来，并给出相关描述，有没有用，敏感程度是用户说了算。

# 开始Code

首先就是 pycharm 的远程调试，然后我为自己确定了一个目标，也就是他应该输出啥样子的。之后就是看源码了，其实懂镜像原理的小伙伴是很好理解写的逻辑的。

![](https://image.3001.net/images/20221104/1667546002_6364bb9228853496e8117.png!small)

在功能上，我为自己定了以下目标：

  1. 在敏感内容的检测中加入docker hisroty

  2. 遍历每一行 docker history的指令，然后将其与正则匹配rules去匹配（都匹配或者可选）

  3. 如果一行指令命中多个正则，需要在report中显示

最终在不改动toml，不改动核心逻辑的情况下，增加了该功能，效果就是下方展示的 Dockerfile的内容

    
    
    root@VM-4-5-ubuntu:/home/ubuntu/docker# cat Dockerfile 
    FROM ubuntu:18.04
    
    ENV PATH=${JAVA_HOME}/bin:${PATH} \
    CS_PORT=9911 \
    CS_PASSWORD=123456 \
    CS_PUSH_TOKEN=111111dadsadsadsadsadsa 
    
    
    RUN sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list && apt-get clean && apt update \
    && apt install -y  redis-server  --fix-missing \
    && sed -i "s|bind 127.0.0.1 ::1|bind 127.0.0.1|" /etc/redis/redis.conf \
    && echo 'password=test123456' > config.ini
    
    
    CMD bash
    
    

这里不展示所有的结果，只展示其中一行命中两个正则规则的结果。为了营造这个条件，我修改了Veinmind-sensitive/rules.toml
中关于"Config File"的正则语句。（这里只是为了测试）`filepath = '''.*\/config\.ini$''' =&ampgt
filepath = ''.*config\.ini$''' `敏感信息的内容是

    
    
    /bin/sh -c sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list && apt-get clean && apt update && apt install -y redis-server --fix-missing && sed -i \"s|bind 127.0.0.1 ::1|bind 127.0.0.1|\" /etc/redis/redis.conf && echo 'password=test123456' > config.ini
    

理论上，这一条指令有password敏感字段和 config.ini 两个敏感字眼，是会命中"Config File" 和"Password In
Enviroment" 这两个正则。

# 实现效果

![](https://image.3001.net/images/20221104/1667546005_6364bb95197adcd6eb64f.png!small)

![](https://image.3001.net/images/20221104/1667546008_6364bb98e56518f248553.png!small)

详细的实现代码可以看https://github.com/chaitin/Veinmind-tools/pull/140/files

# 写在最后

最后我想说的是，我在做脚本小子的时候已经最大化的参照原作者的风格去写并且我写的可能会有纰漏，但是可能逻辑上代码上，始终是原作者更加了解些，对我来说也是时常会学习到大佬的优秀代码。很感谢问脉的认同以及
D_infinite 师傅的认同。最后也要感谢我的同事 akkuman 师傅的帮助。也希望问脉可以越做越好，可以一起拥抱开源生态。

* * *

作者：0-cat

