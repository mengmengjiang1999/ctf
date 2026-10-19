![](https://image.3001.net/images/20210925/1632502906_614e047a909fc225d946c.png!small)

## 关于Fpicker

Fpicker是一款基于Frida的模糊测试套件，可以帮助广大研究人员以多种模式来进行渗透测试，例如AFL++模式或被动追踪模式等。值得一提的是，该工具可以在所有支持Firda的系统平台上运行。

## 工具要求

### Fpicker运行要求

  * [ _frida_compile_](https://github.com/frida/frida-compile)
  * [ _frida-core-devkit_](https://github.com/frida/frida/releases)

### AFL++模式要求

 **macOS：**

使用“CFLAGS="-DUSEMMAP=1"”编译。

 **iOS：**

应用aflpp-ios.patch，Fpicker需要在iOS上以root用户身份运行，如果目标不是以root用户身份运行，它将无法读取和写入共享内存。接下来，使用“CFLAGS="-DUSEMMAP=1"”编译。

## 工具安装

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/ttdennis/fpicker.git

## 项目构建和运行

Fpicker可以在macOS、iOS或Linux平台上运行。Makefile当前仅支持针对iOS和macOS平台进行构建，但我们也可以使用iOS工具链来针对Linux平台进行项目构建。

    
    
    make fpicker-macos
    
    make fpicker-ios
    
    make fpicker-linux

项目构建完成之后，我们就可以继续构建模糊测试组件了。

首先，我们需要针对目标创建一个自定义模糊测试组件（例如examples/test/test.js）。

接下来，使用frida-compile编译自定义组件：

    
    
    frida-compile test.js -o harness.js

现在，Fpicker就可以开始对目标进行模糊测试了。具体要执行的命令取决于我们的配置。接下来，我们会给出一些简单的使用样例，大部分样例都在项目中的“[
_examples_](https://github.com/ttdennis/fpicker/blob/main/examples)”目录中给出了。

 **以AFL++代理运行Fpicker，并跟目标进程绑定，然后测试指定功能函数：**

    
    
    afl-fuzz -i examples/test-network/in -o ./examples/test-network/out -- \\
    
        ./fpicker --fuzzer-mode afl -e attach -p test-network -f ./examples/test-network/harness.js

 **以单独模式运行Fpicker，跟服务器绑定，运行一个客户端程序来发送模糊测试输出：**

    
    
    ./fpicker --fuzzer-mode standalone -e attach -p server-process -f harness.js --input-mode cmd \\
    
        --command "./client-send @@" -i indir -o outdir

 **以单独模式运行Fpicker，跟服务器绑定，使用自定义变异cmd进行模糊测试：**

    
    
    ./fpicker --fuzzer-mode active --communication-mode shm -e attach -p server-process -f harness.js \\
    
        -i indir -o outdir --standalone-mutator cmd --mutator-command "radamsa"

 **以单被动模式运行Fpicker，跟服务器绑定，收集覆盖率和Payload：**

    
    
    ./fpicker --fuzzer-mode passive --communication-mode send -e attach -p server-process -o outdir -f harness.js

 **以单独模式运行Fpicker，跟远程设备上一个正在运行绑定，使用自定义变异cmd进行模糊测试：**

    
    
    ./fpicker --fuzzer-mode active -e attach -p test -D remote -o examples/test/out/ -i examples/test/in/ \\
    
        -f fuzzer-agent.js --standalone-mutator cmd --mutator-command "radamsa"

## 创建自定义模糊测试组件

我们需要针对不同的目标创建自定义模糊测试组件。下面给出的是一个组件实现样例：

    
    
    // Import the fuzzer base class
    
    const Fuzzer = require("harness/fuzzer.js");
    
     
    
    // The custom fuzzer needs to subclass the Fuzzer class to work properly
    
    class TestFuzzer extends Fuzzer.Fuzzer {
    
        constructor() {
    
            // The constructor needs to specify the address of the targeted function and a NativeFunction
    
            // object that can later be called by the fuzzer.
    
     
    
            const FUZZ_FUNCTION_ADDR = Module.getExportByName(null, "FUZZ_FUNCTION");
    
            const FUZZ_FUNCTION = new NativeFunction(
    
                FUZZ_FUNCTION_ADDR,
    
                "void", ["pointer", "int64"], {
    
            });
    
     
    
            super("test", FUZZ_FUNCTION_ADDR, FUZZ_FUNCTION);
    
        }
    
    }
    
     
    
    const f = new TestFuzzer();
    
    exports.fuzzer = f;

## 项目地址

 **Fpicker：** 【[ _GitHub传送门_](https://github.com/ttdennis/fpicker)】

## 参考资料

> [ _https://insinuator.net/2021/03/fpicker-fuzzing-with-> frida/_](https://insinuator.net/2021/03/fpicker-fuzzing-with-frida/)
>
> [ _https://frida.re/docs/javascript-> api/#stalker﻿_](https://frida.re/docs/javascript-api/#stalker)
>
> [
> _https://github.com/AFLplusplus/AFLplusplus/_](https://github.com/AFLplusplus/AFLplusplus/)
>
> [ _https://github.com/frida/frida-compile_](https://github.com/frida/frida-> compile)
>
> [
> _https://github.com/frida/frida/releases﻿_](https://github.com/frida/frida/releases)

