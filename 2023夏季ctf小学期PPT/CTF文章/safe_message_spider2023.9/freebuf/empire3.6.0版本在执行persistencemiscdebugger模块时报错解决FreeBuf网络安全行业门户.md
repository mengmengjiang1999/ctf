# 前言

在empire3.6.0版本中把persistence/debugger/*模块整合到了persistence/misc/debugger*模块中。

但是在调用执行persistence/misc/debugger*的时候会报错

![1605750145_5fb5cd81d719cb8f99ef3.png!small](https://image.3001.net/images/20201119/1605750145_5fb5cd81d719cb8f99ef3.png!small)

# 原因

该问题的原因是因为Empire-3.6.0/lib/modules/powershell/persistence/misc/目录下的debugger.py文件代码中script变量未定义直接引用导致的

![1605750001_5fb5ccf1cad4c4aee56d2.png!small](https://image.3001.net/images/20201119/1605750001_5fb5ccf1cad4c4aee56d2.png!small)

![1605750006_5fb5ccf658d1cbe3895e5.png!small](https://image.3001.net/images/20201119/1605750006_5fb5ccf658d1cbe3895e5.png!small)

可以看到这边出现了两段obfuscate
而且代码几乎相同，由此可以判断程序员在写代码的时候先写了混淆模块，然后忘记了继续往下写(或者是忘记删除了)，导致这部分代码在script变量赋值之前。

# 解决方法

将写在前面的混淆模块代码注释掉

![1605750033_5fb5cd11763064d7d65ef.png!small](https://image.3001.net/images/20201119/1605750033_5fb5cd11763064d7d65ef.png!small)

将下面混淆模块的第二个script= 与上面的对其

![1605750046_5fb5cd1ec5180ee923cfc.png!small](https://image.3001.net/images/20201119/1605750046_5fb5cd1ec5180ee923cfc.png!small)

将更改后的debugger.py文件保存后，重新启动empire，再次运行persistence/misc/debugger*模块，显示成功执行

![1605750113_5fb5cd61293270c20abd2.png!small](https://image.3001.net/images/20201119/1605750113_5fb5cd61293270c20abd2.png!small)

