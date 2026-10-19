**今天给大家介绍的是一款名叫Intensio-Obfuscator的专业代码混淆处理工具，广大Python开发人员以及安全专家可以使用这款工具来对v2.x以及v3.x版本的Python代码进行混淆处理。**

![213123123131321.png](https://image.3001.net/images/20190614/1560492788_5d033af4ebb00.png!small)

## 工具简介

Intensio-Obfuscator可以直接将Python源代码进行转换，并输出经过混淆处理后的Python代码。它会自动将变量名、类名以及函数名替换为随机字符，并定义长度，移除注释内容，自动换行，并给每一行代码增加随机脚本（所有的随机值都是不同的）。

## 工具运行要求

    
    
    Python版本>=v3.5。

## 文件支持

Intensio-Obfuscator目前支持的Python文件代码版本为v2.x以及v3.x版本.

## 工具安装

广大用户可以直接使用git命令将项目代码从GitHub代码库中克隆至本地：

    
    
    git clone <https://github.com/Hnfull/Intensio-Obfuscator.git>
    
    cd Intensio-Obfuscator/intensio/

## 功能介绍

> 替换：替换所有的变量名、类名以及函数名，移除所有的换行符
>
> 填充：在每一行代码后添加随机脚本，并移除所有的换行符
>
> 移除：移除代码中的全部注释以及换行
>
> 低级混淆：生成32个字符的随机字符串，替换源代码中定义的变量名、类名以及函数名
>
> 中级混淆：生成64个字符的随机字符串，替换源代码中定义的变量名、类名以及函数名
>
> 高级混淆：生成128个字符的随机字符串，替换源代码中定义的变量名、类名以及函数名

## 工具使用

**参数** **** |  **描述** ****  
---|---  
-h, --help |  显示帮助菜单  
-f, --onefile |  指定一个代码文件  
-d, --multiplefiles |  指定多个代码文件（项目）  
-i, --input |  源文件或目录  
-c, --code |  输入文件或目录中使用的语言，默认值为[python]  
-o, --output |  混淆处理后的输出文件或目录  
-m, --mixer |  输出变量混淆的字符数量/长度，默认值为: [medium]，可选项为： [lower, medium, high]  
-r, --replace |  激活“替换”混淆功能  
-p, --padding |  激活“填充”混淆功能  
-rm, --remove |  激活“移除”混淆功能  
  
如果你想要在使用“替换”功能时排除掉某些变量名、类名或函数名的话，可以编辑下面这个文件：

    
    
    intensio/exclude_python_words.txt

## 工具使用样例

    
    
    python3.xintensio_obfuscator.py -d -i test/python/multiplefiles/basic/input/basicRAT -cpython -o test/python/multiplefiles/basic/output/basicRAT -m lower -r –rm
    
    
    python3.xintensio_obfuscator.py -d -i test/python/multiplefiles/advanced/input/basicRAT-c python -o test/python/multiplefiles/advanced/output/basicRAT -m high -r -p-rm

### 许可证协议

本项目遵循MIT开源许可证协议。

### 免责声明

Intensio-Obfuscator的开发出于教育目的，请不要将其用于非法活动。

## 项目地址

Intensio-Obfuscator：【[GitHub传送门](https://github.com/Hnfull/Intensio-Obfuscator)】

 *** 参考来源：[Hnfull](https://github.com/Hnfull/Intensio-Obfuscator)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

