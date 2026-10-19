**Functrace是一款使用DynamoRIO（<http://dynamorio.org/>）通过动态检测分析二进制文件的工具。**

## 特性（基于DynamoRIO）

> 反汇编所有执行的代码
>
> 反汇编一个特定的函数（如果是地址则进行转储）
>
> 获取特定函数的参数（如果是地址则进行转储）
>
> 获取特定函数的返回值（如果这是一个地址则进行转储）
>
> 监控应用信号
>
> 生成报告文件
>
> ghidra（<https://ghidra-sre.org/>）coverage脚本（基于functrace报告文件）

## 安装

    
    
    $ wget https://github.com/DynamoRIO/dynamorio/releases/download/release_7_0_0_rc1/DynamoRIO-Linux-7.0.0-RC1.tar.gz
    $ tar xvzf DynamoRIO-Linux-7.0.0-RC1.tar.gz

或

    
    
    $ wget https://github.com/DynamoRIO/dynamorio/releases/download/cronbuild-7.91.18047/DynamoRIO-x86_64-Linux-7.91.18047-0.tar.gz
    $ tar xvzf DynamoRIO-x86_64-Linux-7.91.18047-0.tar.gz

你也可以直接克隆和编译DynamoRIO

    
    
    $ git clone https://github.com/invictus1306/functrace
    $ mkdir -p functrace/build
    $ cd functrace/build
    $ cmake .. -DDynamoRIO_DIR=/full_DR_path/cmake/
    $ make -j4

## DEMO

![667.JPG](https://image.3001.net/images/20190616/1560644064_5d0589e00f375.jpg!small)

## 使用

    
    
    $ drrun -c libfunctrace.so -report_file report -- target_program [args]

 **选项**

支持以下 [functrace]（<https://github.com/invictus1306/functrace>）可选项：

    
    
    -disassembly                    -> disassemble all the functions 
    -disas_func function_name       -> disassemble only the function function_name	
    -wrap_function function_name    -> wrap the function function_name				
    -wrap_function_args num_args    -> number of arguments of the wrapped function
    -cbr                            -> remove the bb from the cache (in case of conditional jump)
    -report_file file_name          -> report file name (required)
    -verbose                        -> verbose

 **使用示例**

选项 -verbose

    
    
    $ drrun -c libfunctrace.so -report_file report -verbose -- target_program [args]

选项 -disassemby

    
    
    $ drrun -c libfunctrace.so -report_file report -disassembly -- target_program [args]

选项 -disas_func

    
    
    $ drrun -c libfunctrace.so -report_file report -disas_func name_function -- target_program [args]

选项 -wrap_function 和 -wrap_function_args

    
    
    $ drrun -c libfunctrace.so -report_file report -wrap_function name_function -wrap_function_args num_args -- target_program [args]

选项 -cbr

    
    
    $ drrun -c libfunctrace.so -report_file report -cbr -- target_program [args]

 **CVE-2018-4013 - 漏洞分析**

[LIVE555 RTSP
](http://www.live555.com/)服务器库上的漏洞。详情请[在此处](https://www.cvedetails.com/cve/CVE-2018-4013/)查看。

![12.JPG](https://image.3001.net/images/20190616/1560644109_5d058a0d77b88.jpg!small)

## 工作环境

以上测试环境为 Ubuntu 16.04.5 LTS 64 bit

## 待添加功能

> Ghidra插件
>
> 可视化设置界面
>
> 存储并比较不同的覆盖能力分析
>
> 从ghidra运行DR directy
>
> 为functrace添加更多功能
>
> 支持Android

 **
*参考来源：[GitHub](https://github.com/invictus1306/functrace)，FB小编secist编译，转载请注明来自FreeBuf.COM**  

