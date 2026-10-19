![1.png](https://image.3001.net/images/20190914/1568469310_5d7cf13e2d34e.png!small)  

## Firmware Slap

Firmware Slap这款工具可以通过混合分析和功能类聚相结合来发现目标固件中的安全漏洞以及相似的功能。Firmware
Slap是一系列功能库的合集，而且可以直接将安全扫描信息导出为pickle或JSON格式数据，以便与其他工具进行整合。

工具介绍文档：【[
_点我查看_](https://media.defcon.org/DEF%20CON%2027/DEF%20CON%2027%20presentations/DEFCON-27-Christopher-Roberts-Firmware-Slap.pdf)】

## 工具安装

Firmware Slap可以在虚拟环境中直接运行，并且已在Python 3.6环境中进行了完整测试，广大用户可以直接使用下列命令完成工具的安装：

    
    
    sudo apt install python3-virtualenv
    
    virtualenv -p python3 fwslap
    
    source fwslap/bin/activate

或者说，大家也可以使用下列命令完成Firmware Slap的下载、安装以及项目构建（配置）：

    
    
    cd ~
    
    mkdir .virtualenvs
    
    pip install virtualenv
    
    which virtualenv #note path warnings
    
    pip install virtualenvwrapper
    
    echo "export PATH=$PATH:~/.local/bin" >> ~/.bashrc
    
    echo "export WORKON_HOME=~/.virtualenvs" >> ~/.bashrc
    
    echo "source ~/.local/bin/virtualenvwrapper.sh" >> ~/.bashrc
    
    #usually best here to open new terminal
    
    mkvirtualenv fwslap -p /usr/bin/python3
    
    workon fwslap

最后，运行下列命令使用setup.py完成安装：

    
    
    python setup.py install

此时，我们还需要安装rabbitmq、Docker以及Radare2或Ghidra：

    
    
    # Ubuntu
    
    sudo apt install rabbitmq-server docker.io
    
    # OSX
    
    brew install rabbitmq
    
    # Radare2
    
    git clone <https://github.com/radare/radare2.git>
    
    sudo ./radare2/sys/install.sh
    
    # Ghidra
    
    wget <https://ghidra-sre.org/ghidra_9.0.4_PUBLIC_20190516.zip>
    
    unzip ghidra_9.0.4_PUBLIC_20190516.zip -d ghidra
    
    echo "export PATH=\$PATH:$PWD/ghidra/ghidra_9.0.4/support" >> ~/.bashrc

如果你选择的是Ghidra，你还需要安装JDK 11：

    
    
    sudo apt install default-jdk
    
    java --version

如果你想使用Elastic搜索功能，你还需要运行Elasticsearch_and_kibana.sh脚本。

## 工具使用

首先，我们需要确保rabbitmq-server已运行：

    
    
    # In a Separate terminal, run this in the top level "Firmware_Slap" directory
    
    celery -A firmware_slap.celery_tasks worker --loglevel=info
    
    # Basic buffer overflow
    
    Discover_And_Dump.py examples/iwconfig -D iwconfig_results
    
    Load_And_View_Results.py iwconfig_results.all.pickle
    
    # Click management on the left pane
    
    # Click Saved Objects
    
    # Click Import
    
    # Select 'elastic_export.json' under the elastic directory in firmware slap
    
    # Navigate to dashboards on left pane and select 'Overview Dashboard'
    
    Load_And_View_Results.py iwconfig_results.all.pickle -s
    
    # Command injection
    
    tar -xvf examples/Almond_libs.tar.gz
    
    Vuln_Discover_Celery.py examples/upload.cgi -L Almond_Root/lib/

接下来，使用下列命令获取用于分析的固件样本：

    
    
    # Get the firmware used for examples
    
    wget <https://firmware.securifi.com/AL3_64MB/AL3-R024-64MB>
    
    binwalk -Mre AL3-R024-64MB

选择项目的根目录，然后开启Celery任务：

    
    
    # In a separate terminal
    
    celery -A firmware_slap.celery_tasks worker --loglevel=info

打开另一个新的终端窗口，然后运行一个漏洞扫描任务：

    
    
    $ Vuln_Discover_Celery.py Almond_Root/etc_ro/lighttpd/www/cgi-bin/upload_bootloader.cgi -L Almond_Root/lib/
    
    [+] Getting argument functions
    
    [+] Analyzing 1 functions
    
      0%|                                                                                                                                                                                                                                   | 0/1 [00:01<?, ?it/s]
    
    {   'Injected_Location': {   'base': '0x7ffefde8',
    
    ........................ SNIP ......................
    
        'type': 'Command Injection'}
    
    Python 3.5.2 (default, Nov 12 2018, 13:43:14) 
    
    Type 'copyright', 'credits' or 'license' for more information
    
    IPython 7.3.0 -- An enhanced Interactive Python. Type '?' for help.
    
    In [1]:

## 返回的漏洞对象

上述命令将会在result变量中返回一个对象，这是一个字典对象，其中包含了大量关于固件漏洞的信息，其中有三个主要的关键数据：函数参数、内存信息和注入位置。

    
    
    In [3]: result.keys()                                                                                 
    
    Out[3]: dict_keys(['args', 'file_name', 'type', 'mem', 'Injected_Location'])

### 函数参数

Args参数中包含了恢复参数和参数值的详细信息，可以用来复现漏洞。在上述例子中，工具发现了一个参数，我们可以用它来触发命令执行：

    
    
    In [1]: result['args']                                                           
    
    Out[1]: 
    
    [{'base': 
    
    'a1',
    
      'type': 'int',
    
      'value': "0x0 -> b'`reboot`\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x00'"}]

### 内存信息

返回对象中的内存组件可以帮助研究人员跟踪目标内存值，可以用于触发漏洞，其中还包含栈地址的偏移量以及.text地址：

    
    
    In [2]: result['mem']                                                                   
    
    Out[2]: 
    
    [{'BBL_ADDR': '0x401138',
    
      'BBL_DESC': {'DESCRIPTION': 'mtd_write_firmware+0x0 in upload_bootloader.cgi (0x401138)',
    
       'DISASSEMBLY': ['0x401138:\tlui\t$gp, 0x42',
    
        '0x40113c:\taddiu\t$sp, $sp, -0x228',
    
        '0x401140:\taddiu\t$gp, $gp, -0x5e90',
    
        '0x401144:\tlw\t$t9, -0x7f84($gp)',
    
        '0x401148:\tsw\t$a2, 0x10($sp)',
    
        '0x40114c:\tlui\t$a2, 0x40',
    
        '0x401150:\tmove\t$a3, $a1',
    
        '0x401154:\tsw\t$ra, 0x224($sp)',
    
        '0x401158:\tsw\t$gp, 0x18($sp)',
    
        '0x40115c:\tsw\t$a0, 0x14($sp)',
    
        '0x401160:\taddiu\t$a1, $zero, 0x200',
    
        '0x401164:\taddiu\t$a0, $sp, 0x20',
    
        '0x401168:\tjalr\t$t9',
    
        '0x40116c:\taddiu\t$a2, $a2, 0x196c']},
    
      'DATA': "b'`reboot`\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x01\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00'",
    
      'DATA_ADDRS': ['0x0']},
    
     {'BBL_ADDR': '0x401170',
    
      'BBL_DESC': {'DESCRIPTION': 'mtd_write_firmware+0x38 in upload_bootloader.cgi (0x401170)',
    
       'DISASSEMBLY': ['0x401170:\tlw\t$gp, 0x18($sp)',
    
        '0x401174:\tnop\t',
    
        '0x401178:\tlw\t$t9, -0x7f68($gp)',
    
        '0x40117c:\tnop\t',
    
        '0x401180:\tjalr\t$t9',
    
        '0x401184:\taddiu\t$a0, $sp, 0x20']},
    
      'DATA': "b'/bin/mtd_write -o 0 -l 0 write `reboot`'",
    
      'DATA_ADDRS': ['0x7ffefe07']}]

### 命令注入

在我们的演示样例中实现命令注入是非常容易的，只是为了方便演示注入位置：

    
    
    In [4]: result['Injected_Location']                                                                      
    
    Out[4]: {'base': '0x7ffefde8', 'type': 'char *', 'value': '/bin/mtd_write -o 0 -l 0 write `reboot`'}

## 漏洞集群脚本示例

这个脚本集群脚本可以尝试使用脚本中的功能模块来扫描漏洞，然后构建k-means集群来提取固件中的漏洞，并进行相似功能的分类。

    
    
    $ Vuln_Cluster_Celery.py -h
    
    usage: Vuln_Cluster_Celery.py [-h] [-L LD_PATH] [-F FUNCTION] [-V VULN_PICKLE]
    
                                  Directory
    
     
    
    positional arguments:
    
      Directory
    
     
    
    optional arguments:
    
      -h, --help            show this help message and exit
    
      -L LD_PATH, --LD_PATH LD_PATH
    
                            Path to libraries to load
    
      -F FUNCTION, --Function FUNCTION
    
      -V VULN_PICKLE, --Vuln_Pickle VULN_PICKLE

下面的命令中，-F为已知的漏洞函数，-V为到处的Pickle，-L为代码库路径，使用样例如下：``

    
    
    $ python Vuln_Cluster_Celery.py -F mtd_write_firmware -L Almond_Root/lib/ Almond_Root/etc_ro/lighttpd/www/cgi-bin/
    
    [+] Reading Files
    
    100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00,  2.80it/s]
    
    Getting functions from executables
    
    Starting main
    
    ... Snip ...

## 项目地址

> Firmware Slap：【[
> _GitHub传送门_](https://github.com/ChrisTheCoolHut/Firmware_Slap)】

 *** 参考来源：[
_ChrisTheCoolHut_](https://github.com/ChrisTheCoolHut/Firmware_Slap)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

