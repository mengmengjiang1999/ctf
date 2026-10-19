## 事件概述

2021年4月15日， **Codecov平台公布称 bash uploader
脚本被攻击者修改，导致用户使用Codecov上传测试数据时，向第三方服务器发送敏感信息** 。根据调查，该事件最早可能发生于1月下旬。

被修改的恶意脚本目前在互联网公开资源中仍可找到，比如如下链接：

    
    
    https://gist.github.com/davidrans/ca6e9ffa5865983d9f6aa00b7a4a1d10

在这段bash的525行有如下代码：

![](https://image.3001.net/images/20210421/1618971131_607f89fbc9eb31b1d4967.jpg!small)

  

其中 ATTACKERIP 为攻击者配置的IP地址。

根据上下文信息，该行代码的行为表现为：

1、收集代码仓库信息

2、收集环境变量和脚本中部分配置信息，比如travis等CI的上传token

根据codecov的说法，通过该恶意脚本，攻击者可以拿到codecov
客户配置CI的凭证，比如令牌或密钥（这个由用户实际配置决定），在获取到相应凭据后，攻击者可以访问相关服务，包括但不限于数据存储和层序的代码，同时，也可以使用bash
uploader 覆盖CI的测试结果，以及git代码仓库中相应的结果。

## 验证

由于travis等CI 以及codecov在配置上有很强的灵活性，根据不同用户的实际需求和习惯，该恶意脚本上传的信息也有所不同。

笔者从 Codecov 官网给出的测试用例中 fork 了一个仓库，并配置 travis 和Codecov，进行验证，结果如下图所示。

![1618971252_607f8a746fcaa64acf9c0.png!small?1618971253068](https://image.3001.net/images/20210421/1618971252_607f8a746fcaa64acf9c0.png!small?1618971253068)

同时修改代码，将原本应该 post 到服务器的数据输出到文本文件中:

    
    
    echo "$(git remote -v)<<<<<< ENV $(env)" >> output.txt

我们来看一下结果。

![1618971182_607f8a2e9b801ba091e42.png!small](https://image.3001.net/images/20210421/1618971182_607f8a2e9b801ba091e42.png!small)

![1618971197_607f8a3ddd7e3cfc48ded.png!small](https://image.3001.net/images/20210421/1618971197_607f8a3ddd7e3cfc48ded.png!small)

笔者基本没有做过什么环境配置，所以输出的敏感信息相对较少。

在 Github 中查找 .travis.yml 我们可以看到了部分敏感程度相对高一些的 CI 配置信息，比如：

![1618971213_607f8a4de1b8fb56bb3d6.png!small](https://image.3001.net/images/20210421/1618971213_607f8a4de1b8fb56bb3d6.png!small)

![1618971223_607f8a57423e0cbb831a1.png!small](https://image.3001.net/images/20210421/1618971223_607f8a57423e0cbb831a1.png!small)

当然，对于复杂生生产环境，可能暴露出来的敏感信息就更多了。

## 建议

鉴于敏感信息泄露可能带来的风险，这里特别建议用户：

1、 检查CI配置文件的代码，如果长期在CI after_success 配置项中执行从Codecov 官网下载 bash
脚本并执行的操作，则用户信息可能就会泄露。

2、 将 Codecov bash 脚本替换为官方更新的版本。

3、 回滚 CI 的令牌、密钥和环境变量中的敏感信息。

