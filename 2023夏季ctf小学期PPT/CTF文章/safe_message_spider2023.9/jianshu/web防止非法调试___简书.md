web防止非法调试

[ wwmin_](https://www.jianshu.com/u/6a87586ed87c)关注

# web防止非法调试

web防止别人任意调试, 目前有一些局限性, 即当把控制台的detectivate breakpoints按钮点亮后此方法即刻失效.  
已验证toString方法,在较新版本的浏览器中也无效果.  
你可以把它当作你的工具函数,在需要不让别人轻易调试的项目中引用

    
    
    //此判断时在vue3的环境中使用, 仅当不是DEV时开启, 方便开发
    if (!import.meta.env.DEV) {
      const emitEvent = (isOpen, orientation) => {
        window.dispatchEvent(new CustomEvent('devtoolsChange', {
          detail: {
            isOpen,
            orientation
          }
        }));
      };
      (function () {
        'use strict';
    
        const devtools = {
          isOpen: false,
          orientation: undefined
        };
    
        const threshold = 160;
        const main = ({ emitEvents = true } = {}) => {
          //
          var timeLimit = 50;
          var open = false;
          var startTime = new Date();
          debugger;
          if (new Date() - startTime > timeLimit) {
            open = true;
            emitEvent(true, "");
          } else {
            open = false
          }
    
          const widthThreshold = window.outerWidth - window.innerWidth > threshold;
          const heightThreshold = window.outerHeight - window.innerHeight > threshold;
          const orientation = widthThreshold ? 'vertical' : 'horizontal';
    
          if (
            !(heightThreshold && widthThreshold) &&
            ((window.Firebug && window.Firebug.chrome && window.Firebug.chrome.isInitialized) || widthThreshold || heightThreshold)
          ) {
            if ((!devtools.isOpen || devtools.orientation !== orientation) && emitEvents) {
              emitEvent(true, orientation);
            }
    
            devtools.isOpen = true;
            devtools.orientation = orientation;
          } else {
            if (devtools.isOpen && emitEvents) {
              emitEvent(false, undefined);
            }
    
            devtools.isOpen = false;
            devtools.orientation = undefined;
          }
        };
    
        main({ emitEvents: false });
        setInterval(main, 500);
    
        if (typeof module !== 'undefined' && module.exports) {
          module.exports = devtools;
        } else {
          window.devtools = devtools;
        }
      })();
    }
    
    window.addEventListener('devtoolsChange', event => {
      const { isOpen } = event.detail;
      if (isOpen) {
        let text = "检测到非法调试,您的信息将被上传并通知网站管理方,有关人员将进行调查,请关闭调试窗口后刷新重试!";
        document.body.innerHTML = "<h1 style='color:black'>" + text + "</h1><hr>" + "<h1 style='color:white'>" + text + "</h1>";
      }
    });
    

推荐加密后使用,加密网站推荐
[https://www.bejson.com/encrypt/jsobfuscate/](https://links.jianshu.com/go?to=https%3A%2F%2Fwww.bejson.com%2Fencrypt%2Fjsobfuscate%2F)

如果要求严格的防审查策略,可以尝试使用如下库, 该库更新比较频繁,具有一定参考价值: [https://github.com/fz6m/console-
ban](https://links.jianshu.com/go?to=https%3A%2F%2Fgithub.com%2Ffz6m%2Fconsole-
ban)

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [测试中常用工具](https://www.jianshu.com/p/28811af5ba98)

1、fiddler可以通过代理用fiddler进行抓包，同时可以修改请求参数或者响应参数、模拟弱网络情况等。修改请...

[circle_hyy](https://www.jianshu.com/u/72482eeda813)阅读 459评论 0赞 5

  * [Spring Cloud](https://www.jianshu.com/p/46fd0faecac1)

Spring Cloud为开发人员提供了快速构建分布式系统中一些常见模式的工具（例如配置管理，服务发现，断路器，智...

[卡卡罗2017](https://www.jianshu.com/u/d90908cb0d85)阅读 132,543评论 18赞 139

  * [App技术选型--Xlog](https://www.jianshu.com/p/43380f0e78b1)

title: App技术选型--日志框架--- **版 本 历 史**| **版本** | **责任人** | *...

[海南鸡](https://www.jianshu.com/u/1c95c2d65954)阅读 1,404评论 0赞 1

  * [网络安全学习，及CTF学习资料整理](https://www.jianshu.com/p/0c9d7a7f808f)

php代码解密https://zhaoyuanma.com/Python https://docs.python....

[kepler404](https://www.jianshu.com/u/7432f0153fe4)阅读 10,467评论 4赞 31

  * [常用的前端调试工具](https://www.jianshu.com/p/b63e6b7df8bf)

在做前端开发时，我们需要用到一些调试工具用来调试我们的HTML、CSS或者JS代码，俗话说预先善其事必先利其器，这...

[Rella7](https://www.jianshu.com/u/1526732e67dd)阅读 22,832评论 0赞 15

 