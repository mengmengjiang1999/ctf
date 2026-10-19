## 介绍

**rtfraptor是一个简单的工具，通过提取OLEv1对象分析恶意RTF文件。它的工作原理是运行Word并拦截对OLEv1函数的调用。从内存中转储原始OLE对象以进行进一步分析。这个工具有以下优点：**

1.避免手动分析混淆的RTF文件。

2.提取恶意对象（打包程序对象，公式编辑器滥用，嵌入式文档等）。

3.确定RTF文档试图滥用的漏洞（或功能）。

4.验证其他工具的输出（例如静态文档解析器）。

## 例子

![](https://image.3001.net/images/20190123/15482335007176.gif)

## 安装

`$ pip install rtfraptor`这将自动获取并安装依赖项。 建议在虚拟环境中安装。

## 用法

至少需要传递`--executable`和`--file`参数，如下所示：

    
    
    (analysis_venv) > rtfraptor --executable "C:\Program Files\Microsoft Office\Office15\WINWORD.EXE" --file 7296D52E0713F4BF15CD4E80EF0DA37E.rtf
    

要保存JSON输出并将原始OLEv1对象转储到磁盘，请传递以下选项：`--json output.json --save-path
ole_parts`注意：此工具运行Word。 应该在虚拟机内部分析可疑文档。 该工具不会停止执行任何payload，将虚拟机与任何网络隔离。

## 输出

### 原始对象输出

可以使用`--save-path`选项存储原始OLEv1对象。下面是一个包含可移植可执行文件的Packager对象示例。

    
    
    00000000  01 05 00 00 02 00 00 00 08 00 00 00 50 61 63 6b  |............Pack|
    00000010  61 67 65 00 00 00 00 00 00 00 00 00 fe 12 00 00  |age.........þ...|
    00000020  02 00 63 72 6f 73 73 61 61 61 2e 64 6c 6c 00 43  |..crossaaa.dll.C|
    00000030  3a 5c 63 72 6f 73 73 61 61 61 2e 64 6c 6c 00 00  |:\crossaaa.dll..|
    00000040  00 03 00 31 00 00 00 43 3a 5c 55 73 65 72 73 5c  |...1...C:\Users\|
    00000050  52 65 76 65 72 73 65 5c 41 70 70 44 61 74 61 5c  |Reverse\AppData\|
    00000060  4c 6f 63 61 6c 5c 54 65 6d 70 5c 63 72 6f 73 73  |Local\Temp\cross|
    00000070  61 61 61 2e 64 6c 6c 00 00 12 00 00 4d 5a 90 00  |aaa.dll.....MZ..|
    00000080  03 00 00 00 04 00 00 00 ff ff 00 00 b8 00 00 00  |........ÿÿ..¸...|
    00000090  00 00 00 00 40 00 00 00 00 00 00 00 00 00 00 00  |....@...........|
    000000a0  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  |................|
    000000b0  00 00 00 00 00 00 00 00 d8 00 00 00 0e 1f ba 0e  |........Ø.....º.|
    000000c0  00 b4 09 cd 21 b8 01 4c cd 21 54 68 69 73 20 70  |.´.Í!¸.LÍ!This p|
    000000d0  72 6f 67 72 61 6d 20 63 61 6e 6e 6f 74 20 62 65  |rogram cannot be|
    000000e0  20 72 75 6e 20 69 6e 20 44 4f 53 20 6d 6f 64 65  | run in DOS mode|
    ... snip ...
    

### 命令行输出

生成控制台输出，列出所有可疑的OLE对象（`oletools.common.clsid`中的对象）：

    
    
    (analysis_venv) > rtfraptor --executable "C:\Program Files\Microsoft Office\Office15\WINWORD.EXE" --file 7296D52E0713F4BF15CD4E80EF0DA37E.rtf --json output.json --save-path ole_parts
    WARNING Suspicious OLE object loaded, class id 00020821-0000-0000-C000-000000000046 (Microsoft Excel.Chart.8)
    WARNING Object size is 390702, SHA256 is 2a7f92bf37cef77c4fa2e97fcf3478b3e4e4296514817bd8c12e58300b485406
    WARNING Suspicious OLE object loaded, class id 00020821-0000-0000-C000-000000000046 (Microsoft Excel.Chart.8)
    WARNING Object size is 390190, SHA256 is f8ac5b37f52b6316178c293704fcc762d0a29d2700c7eda53724f552413c7b98
    WARNING Suspicious OLE object loaded, class id F20DA720-C02F-11CE-927B-0800095AE340 (OLE Package Object (may contain and run any file))
    WARNING Object size is 359115, SHA256 is 2ea248d43d4bd53e234530db0de2517a7f44deba5f43367636232019b2e9e822
    WARNING Suspicious OLE object loaded, class id F20DA720-C02F-11CE-927B-0800095AE340 (OLE Package Object (may contain and run any file))
    WARNING Object size is 4902, SHA256 is 28c9afbe46a35a6d7115ca3da535854efddc9749f1ff13722fa98d2bd3a8122b
    WARNING Suspicious OLE object loaded, class id F20DA720-C02F-11CE-927B-0800095AE340 (OLE Package Object (may contain and run any file))
    WARNING Object size is 5926, SHA256 is 5b5850f3217e8465d6add2da18a495d87d33552c6c8f400e52e5ab9cf06ba2e9
    WARNING Suspicious OLE object loaded, class id 0002CE02-0000-0000-C000-000000000046 (Microsoft Equation 3.0 (Known Related to CVE-2017-11882 or CVE-2018-0802))
    WARNING Object size is 7727, SHA256 is 38d9e74ede4ef67e78e028ecd815c54a777e11c6c4e7838ecbe26fd7e7c03d7c
    WARNING Suspicious OLE object loaded, class id 0002CE02-0000-0000-C000-000000000046 (Microsoft Equation 3.0 (Known Related to CVE-2017-11882 or CVE-2018-0802))
    WARNING Object size is 7727, SHA256 is a612b7b97f021797c5911cfe02bd9a145f96abb880990830eaf021f98a4a7c8a
    

### json输出

如果传递了`--json`选项，该工具将以JSON格式生成输出,以下格式：

    
    
    {
      "sha256": "8326bcb300389a2d654e6e921e259e553f33f8949984c2da55ccb6e9ed3f6480",
      "input_file": "7296D52E0713F4BF15CD4E80EF0DA37E.rtf",
      "objects": {
        "0": {
          "class_id": "00020821-0000-0000-C000-000000000046",
          "sha256": "2a7f92bf37cef77c4fa2e97fcf3478b3e4e4296514817bd8c12e58300b485406",
          "description": "Microsoft Excel.Chart.8",
          "size": 390702
        },
        ... snip ...
        "2": {
          "class_id": "F20DA720-C02F-11CE-927B-0800095AE340",
          "sha256": "2ea248d43d4bd53e234530db0de2517a7f44deba5f43367636232019b2e9e822",
          "description": "OLE Package Object (may contain and run any file)",
          "size": 359115
        },
        ... snip ...
        "5": {
          "class_id": "0002CE02-0000-0000-C000-000000000046",
          "sha256": "38d9e74ede4ef67e78e028ecd815c54a777e11c6c4e7838ecbe26fd7e7c03d7c",
          "description": "Microsoft Equation 3.0 (Known Related to CVE-2017-11882 or CVE-2018-0802)",
          "size": 7727
        },
        ... snip ...
    }
    

***参考来源：[github](https://github.com/edeca/rtfraptor)，由周大涛编译，转载请注明来自FreeBuf.COM**

