![](https://image.3001.net/images/20200807/1596807952.png!small)

UEFI_RETool是一款专门针对UEFI固件设计的逆向工程分析工具，该工具基于Python开发，并通过uefi_retool.py脚本实现其功能。

## 使用uefi_retool.py脚本进行UEFI固件分析

### 工具安装

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/yeggor/UEFI_RETool.git

### 工具配置

首先，我们需要将[
_ida_plugin/uefi_analyser.py_](https://github.com/yeggor/UEFI_RETool/blob/master/uefi_retool.py)脚本和ida_plugin/uefi_analyser目录移动到IDA插件目录下。接下来，编辑config.json文件中的各项配置参数：

> -PE_DIR：PE_DIR目录中包含了UEFI固件中的所有可执行镜像； -DUMP_DIR：DUMP_DIR目录中包含了固件文件系统中的全部组件；
> -LOGS_DIR：LOGS_DIR目录专门用于存放日志文件； -IDA_PATH/IDA64_PATH：这两个路径为IDA
> Pro针对x32和x64架构的不同版本可执行文件；

配置完成后，运行下列命令安装工具依赖组件:

    
    
    pip install -r requirements.txt

依赖组件配置完成后，我们就可以使用下列命令运行工具，并显示帮助信息了：

    
    
    python uefi_retool.py

## 工具使用命令

    
    
    python uefi_retool.py
    
    
    Usage: uefi_retool.py [OPTIONS] COMMAND [ARGS]...
    Options:
      --help  显示帮助信息和退出
    Commands:
      get-images  从UEFI固件获取可执行镜像
      get-info    分析整个UEFI固件文件
      get-pp      获取UEFI固件文件中的专有协议列表

## 命令解析

### get-images

    
    
    python uefi_retool.py get-images --help
    
    
    Usage: uefi_retool.py get-images [OPTIONS] FIRMWARE_PATH
      Get executable images from UEFI firmware. Images are stored in "modules"
      directory.
    Options:
      --help  Show this message and exit.

 **使用样例：**

    
    
    python uefi_retool.py get-images test_fw/fw-tp-x1-carbon-5th.bin

### get-info

    
    
    python uefi_retool.py get-info --help
    
    
    Usage: uefi_retool.py get-info [OPTIONS] FIRMWARE_PATH
      Analyze the entire UEFI firmware. The analysis result is saved to .json
      file.
    Options:
      -w, --workers INTEGER  Number of workers (8 by default).
      --help                 Show this message and exit.

 **使用样例：**

    
    
    python uefi_retool.py get-info -w 6 test_fw/fw-tp-x1-carbon-5th.bin

### get-pp

    
    
    python uefi_retool.py get-pp --help
    
    
    Usage: uefi_retool.py get-pp [OPTIONS] FIRMWARE_PATH
      Get a list of proprietary protocols in the UEFI firmware. The result is
      saved to .json file.
    Options:
      -w, --workers INTEGER  Number of workers (8 by default).
      --help                 Show this message and exit.

 **使用样例：**

    
    
    python uefi_retool.py get-pp -w 6 test_fw/fw-tp-x1-carbon-5th.bin

## 额外工具

tools/update_edk2_guids.py脚本可以从edk2项目更新协议GUID列表。

## IDA插件

针对UEFI分析的IDA插件：【[
_点我获取_](https://github.com/yeggor/UEFI_RETool/tree/master/ida_plugin)】

### 分析&协议

 **使用方法**

首先，将uefi_analyser和uefi_analyser.py拷贝到%IDA_DIR%/plugins目录中。然后在IDA中打开UEFI镜像，点击“编辑”->“插件”->“UEFI
analyser”。

 **使用样例**

分析之前![](https://image.3001.net/images/20200807/1596808114.png!small)

分析之后![](https://image.3001.net/images/20200807/1596808122.png!small)

协议浏览窗口![](https://image.3001.net/images/20200807/1596808129.png!small)

## 依赖查看&依赖图

首先，我们需要使用uefi_retool.py来对目标固件进行分析：

    
    
    python uefi_retool.py get-info FIRMWARE_PATH

接下来，将<LOGS_DIR>/<FIRMWARE_NAME>-all-info.json文件加载进IDA中：![](https://image.3001.net/images/20200807/1596808150.png!small)

### 使用样例

 **依赖浏览窗口**![](https://image.3001.net/images/20200807/1596808163.png!small)

 **依赖图**![](https://image.3001.net/images/20200807/1596808170.png!small)

## 项目地址

UEFI_RETool：【[ _GitHub传送门_](https://github.com/yeggor/UEFI_RETool)】

