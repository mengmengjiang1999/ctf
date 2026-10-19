**作者：墨云科技 VLab Team  
原文链接：<https://mp.weixin.qq.com/s/fFx1kQVfotbOqHlSjSJVMQ>**

#### 漏洞简述

这是一个反序列化漏洞,是一条新的gadget,在低版本的JDK中可能会造成RCE风险。

#### 漏洞分析

测试环境weblogic14c版本,测试JDK 1.8版本。

首先会调用BadAttributeValueExpException.readObject方法

![image-20220124155627486](https://images.seebug.org/content/images/2022/02/21/1645430310000-image-20220124155627486.png-w331s)

接着会调用SessionData.toString方法

![image-20220124155945938](https://images.seebug.org/content/images/2022/02/21/1645430311000-image-20220124155945938.png-w331s)

接着会调用SessionData.isDebuggingSession方法

![image-20220124160012494](https://images.seebug.org/content/images/2022/02/21/1645430311000-image-20220124160012494.png-w331s)

接着会调用SessionData.getAttribute方法

![image-20220124160123806](https://images.seebug.org/content/images/2022/02/21/1645430312000-image-20220124160123806.png-w331s)

接着会调用SessionData.getAttributeInternal方法

![image-20220124160214737](https://images.seebug.org/content/images/2022/02/21/1645430313000-image-20220124160214737.png-w331s)

接着会调用AttributeWrapperUtils.unwrapObject方法

![image-20220124160253147](https://images.seebug.org/content/images/2022/02/21/1645430313000-image-20220124160253147.png-w331s)

接着会调用AttributeWrapperUtils.unwrapEJBObjects方法

![image-20220124160325055](https://images.seebug.org/content/images/2022/02/21/1645430313000-image-20220124160325055.png-w331s)

接着会调用BusinessHandleImpl.getBusinessObject方法

![image-20220124160409585](https://images.seebug.org/content/images/2022/02/21/1645430314000-image-20220124160409585.png-w331s)

接着会调用HomeHandleImpl.getEJBHome方法

![image-20220124160501400](https://images.seebug.org/content/images/2022/02/21/1645430314000-image-20220124160501400.png-w331s)

可以看到这里调用了ctx.lookup方法

#### 修复建议

及时更新补丁，参考oracle官网发布的补丁:

<https://www.oracle.com/security-alerts/cpujan2022.html>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1835/>

