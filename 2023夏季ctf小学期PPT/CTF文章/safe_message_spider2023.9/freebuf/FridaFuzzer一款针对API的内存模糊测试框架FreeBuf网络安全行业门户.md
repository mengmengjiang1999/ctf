![Fuzz-Testing.png](https://image.3001.net/images/20200409/1586370482_5e8e17b29812b.png!small)**Frida-Fuzzer是一款针对API的内存模糊测试框架，该工具的设计和开发灵感来源于AFL/AFL++，Frida-Fuzzer的当前版本支持在GNU/Linux
x86_64和Android x86——64平台上运行。**

除此之外，你还使用下列命令安装`Frida >= v12.8.1`和`frida-tools`来对项目代码进行编译和使用该工具。

    
    
    pip3 install -U frida

## 工具下载

广大研究人员可以使用下列命令将项目源码克隆至本地：

    
    
    git clone https://github.com/andreafioraldi/frida-fuzzer.git

## 工具使用

在项目代码中，fuzz库必须导入至一个自定义`Harness`中，然后使用`frida-compile`进行编译并生成一个代理，随后Frida-Fuzzer会将生成的代理注入到目标应用程序之中。

Frida-Fuzzer的所有功能逻辑都在这个生成的代理之中，功能也全部由这个代理来实现。

前文所述的自定义`Harness`格式如下：

    
    
    var fuzz = require("./fuzz");
    
    var TARGET_MODULE = "test_linux64";
    
    var TARGET_FUNCTION = DebugSymbol.fromName("target_func").address;;
    
    var RET_TYPE = "void";
    
    var ARGS_TYPES = ['pointer', 'int'];
    
    var func_handle = new NativeFunction(TARGET_FUNCTION, RET_TYPE, ARGS_TYPES, { traps: 'all' });
    
    fuzz.target_module = TARGET_MODULE; var payload_mem = Memory.alloc(fuzz.config.MAX_FILE);
    
    fuzz.fuzzer_test_one_input = function (/* Uint8Array */ payload) {
    
    Memory.writeByteArray(payload_mem, payload, payload.length);
    
    func_handle(payload_mem, payload.length);
    
    }

`fuzz.fuzzer_test_one_input`是必须要有的，如果你没有指定`fuzz.target_module`的话，所有的代码都将会被执行。

你还可以设置`fuzz.manual_loop_start = true`来告诉模糊测试器你将会在回调中调用`fuzz.fuzzing_loop()`。

`fuzz.init_callback`回调在设置之后，可以让模糊测试器在准备开始工作之后便执行代码，具体样例可以参考`tests/test_java.js`。

`fuzz.dictionary`是一个典型的模糊测试字典，其中包含了一个数组，你可以向其中添加数据对象，支持的类型有`Array`、`ArrayBuffer`、`Uint8Array`和`String`，它们都可以作为变异器的额外变异因子。具体样例可以参考`tests/test_libxml2.js`。

Frida-Fuzzer支持接收下列参数：

-i FOLDER| 包含初始化种子的目录  
---|---  
-o FOLDER| 包含中间种子和崩溃信息的输出目录  
-U| 连接USB  
-spawn| 生成附加数据  
-script SCRIPT| 脚本文件名（默认为fuzzer-agent.js）  
  
如果你不指定输出目录的话，该工具将会在`/tmp`目录下创建一个临时文件夹。如果你不指定包含初始化种子的目录，该工具将会使用`0000`作为初始种子。

如果你是在对一个本地应用程序进行模糊测试的话，你可能需要在执行Frida-Fuzzer之前执行`system-config`来调整系统执行参数并优化任务执行。

运行下列命令之后，你将会在终端窗口中看到下列工具状态信息：

    
    
    ./frida-fuzzer -spawn ./tests/test_linux64

![screen.png](https://image.3001.net/images/20200409/1586370567_5e8e1807ec00c.png!small)

你还可以在`fuzz/fuzzer.js`中添加自定义步骤，并将其添加到`fuzz/index.js`的步骤列表中。

如需对模糊测试器进行自定义设置，可以编辑`fuzz/config.js`文件，此时你需要修改的变量为`MAP_SIZE`（可以降低代码大小以实现速度优化）、`MAX_FILE`（生成输入的最大大小）和`QUEUE_CACHE_MAX_SIZE`（增加队列缓存大小以实现速度提升）。

## 工具使用样例

比如说，我们要对一个样例Android应用程序的本地共享库进行测试，首先你需要确保已经在虚拟设备中实现了root：

    
    
    host$ adb root

从该项目的Release页面下载`Android x86_64 frida-server`，然后将其拷贝到设备的`/data/local/tmp`目录下，这里可以使用`adb push`。

接下来，开启一个Shell，并运行`frida-server`：

    
    
    device# cd /data/local/tmp
    
    device# ./frida-server

现在，安装测试应用程序`tests/app-debug.apk`，安装完成后运行App。

使用`frida-compile`编译代理脚本：

    
    
    host$ frida-compile -x tests/test_ndk_x64.js -o fuzzer-agent.js

在模拟器中打开App。

使用下列命令对测试App中`libnative-lib.so`库的`test_func`函数进行测试：

    
    
    host$ ./frida-fuzzer -U -o output_folder/ com.example.ndktest1

测试样例和崩溃信息等输出结果都将保存在项目的`output_folder`中。

### 测试截图如下：

![screen1.png](https://image.3001.net/images/20200409/1586370661_5e8e186554cdb.png!small)

## 项目地址

Frida-Fuzzer：【[ _GitHub传送门_](https://github.com/andreafioraldi/frida-fuzzer)】

 *** 参考来源：[ _andreafioraldi_](https://github.com/andreafioraldi/frida-fuzzer)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

