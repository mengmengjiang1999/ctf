![](https://image.3001.net/images/20220601/1654078548_62973c54dc7b5b62a1630.gif!small)  

## 关于Frelatage

Frelatage是一款基于覆盖率的Python模糊测试工具，在该工具的帮助下，广大研究人员可以轻松对Python代码进行模糊测试。

Frelatage的设计与开发受到了很多社区现有模糊测试工具的启发，其中包括[
_AFL_](https://github.com/google/AFL)/[
_AFL++_](https://github.com/AFLplusplus/AFLplusplus)、[
_Atheris_](https://github.com/google/atheris)和[
_PythonFuzz_](https://github.com/fuzzitdev/pythonfuzz)等等。其主要目的是整合优化了其他模糊测试工具的优秀特性，以便帮助研究人员以更高效的方式对Python应用程序进行模糊测试和安全研究。

## 功能介绍

Frelatage支持对下列类型的参数进行模糊测试：

> 字符串
>
> 整型
>
> 浮点型
>
> 列表
>
> 元组
>
> 字典
>
> 函数（以文件作为输入）

## 工作机制

Frelatage主要通过遗传算法来生成覆盖率尽可能高的测试用例，整个过程大致如下图所示：

![](https://image.3001.net/images/20220601/1654078571_62973c6b45ef29a3f008b.png!small)

## 工具要求

该工具基于[ _Python_ _3_](https://www.python.org/)开发，因此我们需要在本地设备上安装并配置好[ _Python_
_3_](https://www.python.org/)环境。

## 工具安装

### pip安装（推荐）

    
    
    pip3 install frelatage

### 源码构建

    
    
    bash <(wget -q https://raw.githubusercontent.com/Rog3rSm1th/Frelatage/main/scripts/autoinstall.sh -O -)

## 工具使用

### 对典型参数进行模糊测试

    
    
    import frelatage
    
    import my_vulnerable_library
    
     
    
    def MyFunctionFuzz(data):
    
      my_vulnerable_library.parse(data)
    
     
    
    input = frelatage.Input(value="initial_value")
    
    f = frelatage.Fuzzer(MyFunctionFuzz, [[input]])
    
    f.fuzz()

### 对文件参数进行模糊测试

Frelatage支持对文件类型输入参数进行模糊测试，首先我们需要初始化文件值，这一步需要在输入文件夹中创建文件（默认为./in）：

    
    
    echo "initial value" > ./in/input.txt

然后运行模糊测试工具即可：

    
    
    import frelatage
    
    import my_vulnerable_library
    
     
    
    def MyFunctionFuzz(data):
    
      my_vulnerable_library.load_file(data)
    
     
    
    input = frelatage.Input(file=True, value="input.txt")
    
    f = frelatage.Fuzzer(MyFunctionFuzz, [[input]])
    
    f.fuzz()

## 工具配置

下面给出的是工具的配置样例：

    
    
    export FRELATAGE_DICTIONARY_ENABLE=1 &&
    
    export FRELATAGE_TIMEOUT_DELAY=2 &&
    
    export FRELATAGE_INPUT_FILE_TMP_DIR="/tmp/frelatage" &&
    
    export FRELATAGE_INPUT_MAX_LEN=4096 &&
    
    export FRELATAGE_MAX_THREADS=8 &&
    
    export FRELATAGE_MAX_CYCLES_WITHOUT_NEW_PATHS=5000 &&
    
    export FRELATAGE_INPUT_DIR="./in" &&
    
    export FRELATAGE_DICTIONARY_DIR="./dict" &&
    
    python3 fuzzer.py

接下来，我们就可以向模糊测试工具传递参数了：

    
    
    import frelatage
    
     
    
    def myfunction(input1_string, input2_int):
    
        pass
    
     
    
    input1 = frelatage.Input(value="initial_value")
    
    input2 = frelatage.Input(value=2)
    
     
    
    f = frelatage.Fuzzer(
    
        # 需要测试的方法
    
        method=myfunction,
    
        # 语料库
    
        corpus=[[input1], [input2]],
    
        # 线程数量
    
        threads_count=8,
    
        # 需要考虑的例外情况
    
        exceptions_whitelist=(OSError),
    
        # 需要排除的例外情况
    
        exceptions_blacklist=(),
    
        # 存储错误报告的目录
    
        output_directory="./out",
    
        # 启用或禁用静默模式
    
        silent=False,
    
        # 启用或禁用无限模糊测试
    
        infinite_fuzz=False
    
    )
    
    f.fuzz()

## 报告生成

工具在完成模糊测试之后，会将结果存储到输出目录（默认为./out）中，输出文件命名规则为：

    
    
    id:<crash ID>,err:<error type>,err_pos:<error>,err_file:<error file>.

报告目录的格式如下：

    
    
    ├── out
    
        │   ├── id:<crash ID>,err:<error type>,err_file:<error file>,err_pos:<err_pos>
    
        │       ├── input
    
        │       ├── 0
    
        │            ├── <inputfile1>
    
        │       ├── ...
    
    │   ├── ...

## 工具运行演示

![](https://image.3001.net/images/20220601/1654078709_62973cf5d6f7b54d64a1c.gif!small)

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/Rog3rSm1th/Frelatage/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **Frelatage：** 【[ _GitHub传送门_](https://github.com/Rog3rSm1th/Frelatage)】

## 参考资料

> [ _https://github.com/google/AFL_](https://github.com/google/AFL)
>
> [
> _https://github.com/AFLplusplus/AFLplusplus_](https://github.com/AFLplusplus/AFLplusplus)
>
> [ _https://github.com/google/atheris_](https://github.com/google/atheris)
>
> [
> _https://github.com/fuzzitdev/pythonfuzz_](https://github.com/fuzzitdev/pythonfuzz)
>
> [ _https://www.python.org/_](https://www.python.org/)

