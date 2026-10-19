# 一、工具概览

[ **OFRAK**](https://ofrak.com/)( **Open Firmware Reverse Analysis Konsole**
)是一款二进制分析和修改平台，它结合了解压缩，分析，修改和重新打包二进制文件的功能，旨在减少IOT逆向分析开销，帮助研究人员专注于漏洞挖掘。OFRAK提供
**GUI(web)和Python API** 功能，扩展性较强。

OFRAK的作者 **Choi** 在优化更新FRAK的功能后，于 **本周** 在拉斯维加斯的DefCon上推出了[
**OFRAK**](https://github.com/redballoonsecurity/ofrak)(或OpenFRAK)。由于工具开源不久，
**网上几乎没有相关教程，实际上官方的安装方法也存在很多问题，本文是笔者对该工具安装和使用的踩坑记录，希望能够抛砖引玉。**

![](https://image.3001.net/images/20220821/1661078395_63020b7bacbe690fa5bfa.png!small)

# 二、结构解析

[
**OFRAK**](https://github.com/redballoonsecurity/ofrak)采用组合模块的方式，包括`ofrak_core`、`ofrak_components`、`ofrak_io`、`ofrak_patch_maker`、`ofrak_tutorial`、`ofrak_type`、`disassemblers
(
angr、ninja、ghidra、capstone)`、`frontend`，还有文档模块`docs`。模块依赖于`PyYAML`，基础模块都有对应的`.yaml`文件作为安装配置。

笔者在开始安装时并没有对结构目录作分析，而是直接参考`install.md`中的命令，命令一顿敲，错误一顿报，在几次失败后才回过头去理解结构，浪费了不少时间。

目录结构作简单阐释如下：

    
    
    ├── build_image.py # ofrak build 的主文件，build 模块时使用其解析对应的yaml
    ├── disassemblers  # 包含如下插件模块，不安装不影响主功能 (使用GUI须安装ghidra模块)
    │   ├── ofrak_angr
    │   ├── ofrak_binary_ninja
    │   ├── ofrak_capstone
    │   └── ofrak_ghidra
    ├── docs   # 文档
    ├── examples # Python API 实例
    ├── frontend # web前(后)端模块，使用nginx和python
    ├── INSTALL.md # 安装手册(不是很好用)
    ├── LICENSE
    ├── Makefile
    ├── mkdocs.yml # 文档安装配置
    ├── ofrak-angr.yml # angr模块配置
    ├── ofrak-binary-ninja.yml # angr模块配置
    ├── ofrak_components # components模块 
    ├── ofrak_core # 主模块
    ├── ofrak-core-dev.yml # 主模块配置
    ├── ofrak-dev.yml 
    ├── ofrak-ghidra.yml  # ghidra模块配置
    ├── ofrak_io # io模块
    ├── ofrak-minimal.yml # 最小安装配置
    ├── ofrak_patch_maker # patch_maker模块
    ├── ofrak_tutorial # tutorial模块
    ├── ofrak-tutorial.yml # tutorial模块配置
    ├── ofrak_type # type模块
    ├── pyproject.toml
    └── README.md # 介绍文档
    

通过查阅各模块文件夹的`Dockerstub`文件，可以很快了解模块功能：

  * `ofrak_core`

包含`build-essential`、`cmake`等基础安装。

  * `ofrak_io`

包含`io`相关安装。

  * `ofrak_components`

包含`keystone`、`capstone`、`binwalk`、`squash-tools`、`apktool`等组件。

  * `ofrak_patch_maker`

包含`tool-chain`、`arm-gcc`等(下文所述第一个安装问题手动下载的包)。

  * `ofrak_tutorial`

包含`jupyter`等。

  * `ofrak_type`

包含`type`相关安装。

  * 当输入安装命令`python3 build_image.py --config ofrak-core-dev.yml --base --finish`发生了什么？  
根据官方`install.md`，OFRAK可使用`Docker`或者`MacOS`安装，docker安装核心就是上面的命令，so
easy。![](https://image.3001.net/images/20220821/1661078414_63020b8eb8852a8bc5429.jpg!small)

我们先来看`ofrak-core-dev.yml`的内容：

    
    
    ofrak@ofrak-virtual-machine:~/ofrak$ cat ofrak-core-dev.yml
    registry: "redballoonsecurity/ofrak"
    base_image_name: "core-dev-base"
    image_name: "core-dev"
    packages_paths:
      [
        "ofrak_type",
        "ofrak_io",
        "ofrak_patch_maker",
        "ofrak_core",
        "ofrak_components",
      ]
    

结合`build_image.py`和`install.md`中的开发说明，这里会进入`packages_paths`中的各模块(文件夹)，然后根据配置执行`make
develop`，其实也是比较简单的。笔者使用的系统是 **Ubuntu 20.04** ，在未使用docker (当然也可以修改使用，下文会介绍)
情况下完成安装，下文记录安装踩坑过程。![](https://image.3001.net/images/20220821/1661078434_63020ba2b4cd65a494260.png!small)

# 三、安装踩坑

##  **3.1 安装问题**

###  **3.1.1 pip 安装问题**

因为OFRAK主功能有python开发，所以先想到pip一键解决所有问题，查了PyPI也确实有源。![](https://image.3001.net/images/20220821/1661078449_63020bb14efec6a7a183e.png!small)

这不简单了嘛，安装也很顺利，但是当使用时会发现该包基本为空，并不包含任何功能模块：![](https://image.3001.net/images/20220821/1661078468_63020bc4104ac8662a3da.png!small)

唯一的功能可能就是打印logo???![](https://image.3001.net/images/20220821/1661078477_63020bcdcf55464754bf9.jpg!small)

###  **3.1.2 docker 安装问题**

于是老老实实按照官方`install.md`文档安装，安装文档大致描述为：OFRAK可使用docker和Macos原生安装，基于yaml配置，主功能模块安装命令如下：

    
    
    python3 -m pip install PyYAML
    python3 build_image.py --config ofrak-core-dev.yml --base --finish
    

其他模块参照上述例子。在使用Macos安装时，需安装`apktool binwalk cmake java libmagic lzop p7zip qemu
squashfs rar unar wget keystone capstone binwalk ...`，之后编译。

看着手上的Ubuntu当然是选择docker，安装第一个问题是下载的一些包太慢，所以直接代理下载，并修改脚本，首先下载的包包括：

  * `clang+llvm-12.0.1-x86_64-linux-gnu-ubuntu-16.04.tar.xz`

  * `gcc-arm-none-eabi-10-2020-q4-major-x86_64-linux.tar.bz2`

  * `binutils_2.34.orig.tar.xz`

  * `vbcc0_9h.tar.gz`

  * `vasm1_9.tar.gz`

之后修改`base.Dockerfile`中相应的`wget`点指向本地Docker网卡地址`172.17.0.1`(开本地python http
服务)，当然也可以直接配置使用docker proxy。

这个其实并不算问题，问题是之后在docker镜像apt安装软件时一致报错，刚开始以为是(你懂得)网络原因，后来发现由于使用的 **debian
image中mirror部分失效** ，导致包无法安装而中断退出。

(忘记截图了)

这个解决方法也很简单，把docker
pull下来之后先连接`bash`修改mirror，再继续安装。但是意味着要对这个庞大的安装流程作肢解，完全失去自动化安装脚本的意义。由于笔者比较懒，所以放弃了该思路。

docker受阻就本机安装，查看了MacOS的安装流程，也就是装包和编译，最多是包名字不一样，并没有看到必须需要MacOS特性的地方(除了UI美观方面)。所以直接利用Ubuntu
20.04尝试安装。

##  **3.2 安装流程**

其实当大致理解上文所述OFRAK结构解析，安装也变得十分简单，只是GUI的搭建还需要一些其他信息。

###  **3.2.1 模块安装**

下述安装可能包会有重复，实际上查看`Dockerstub`确有交叉，这里就不做精简了。

  * 基础安装

    
    
    # 官方推荐使用 python env 安装
    $ python3 -m venv ofrak-venv
    $ source ofrak-venv/bin/activate
    
    # 安装 PyAML (此方法下不装也可以)
    $ python3 -m pip install PyYAML
    
    # 安装基础包 (已经换成Ubuntu的包名)
    $ sudo install apktool binwalk cmake openjdk-11-jdk libmagic-dev lzop p7zip qemu squashfs-tools rar unar wget
    
    # 安装 keystone
    cd /tmp
    git clone <https://github.com/rbs-forks/keystone.git>
    cd keystone
    git checkout 2021.09.01
    mkdir build
    cd build
    ../make-share.sh
    cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=ON -G "Unix Makefiles" ..
    make -j8
    sudo make install
    cd ../bindings/python
    make install3
    pip3 install .
    
    # 安装 capstone
    cd /tmp
    git clone <https://github.com/rbs-forks/capstone.git>
    cd capstone
    git checkout 2021.09.01
    ./make.sh
    sudo ./make.sh install
    cd bindings/python
    make install3
    
    # 按照官方文档，若是Macos此时就可以编译了，但是Ubuntu会报错
    % INSTALL_TARGET=develop
    % make -C ofrak_core $INSTALL_TARGET
    

通过前文已知，`make -C ofrak_core
$INSTALL_TARGET`即按照对应`.yaml`规则进入`ofrak_core`等文件夹进行`make
develop`，这里直接手动操作编译安装各模块。

  * `ofrak_core`

    
    
    $ cd ofrak_core
    $ ls
    Dockerstub  LICENSE  Makefile  MANIFEST.in  mypy.ini  ofrak  ofrak.egg-info  pytest.ini  pytest_ofrak  setup.py  test_ofrak
    $ make develop 
    pip3 install -e .[docs,test]
    Obtaining file:///home/ofrak/ofrak/ofrak_core
    Collecting intervaltree==3.1.0
      Using cached intervaltree-3.1.0.tar.gz (32 kB)
    Collecting lief==0.11.5
      Using cached lief-0.11.5-cp38-cp38-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (4.0 MB)
    Collecting orjson~=3.6.7
    ....
    Running setup.py develop for ofrak
    Successfully installed cffi-1.15.1 intervaltree-3.1.0 lief-0.11.5 ofrak orjson-3.6.9 pefile-2022.5.30 pycparser-2.21 six-1.16.0 sortedcontainers-2.2.2 typeguard-2.13.3 xattr-0.9.7
    

如果觉得还不保险，就再`sudo python3 setup.py install`一下，或者直接将编译好的`ofrak`和`ofrak.egg-info`拷贝至python的dist-packages目录下，下述模块皆可如此。

  * `ofrak_patch_maker`

    
    
    # 这个多一步，直接 make 会报错
    $ make develop
    cp toolchain.conf /etc/toolchain.conf
    cp: cannot stat 'toolchain.conf': No such file or directory
    make: *** [Makefile:9: toolchain_conf] Error 1
    
    # 看错误也很简单，直接重命名以下即可
    $ cd ofrak_patch_maker
    $ ls
    build  dist  Dockerstub  LICENSE  Makefile  mypy.ini  ofrak_patch_maker  ofrak_patch_maker.egg-info  ofrak_patch_maker_test  setup.py  toolchain.conf.bak
    $ cp toolchain.conf.bak toolchain.conf
    $ sudo make develop
    cp toolchain.conf /etc/toolchain.conf
    mv toolchain.conf toolchain.conf.bak
    pip3 install -e .[test]
    Obtaining file:///home/ofrak/ofrak/ofrak_patch_maker
    Requirement already satisfied: immutabledict==2.2.0 in /usr/local/lib/python3.8/dist-packages (from ofrak-patch-maker==0.1.0) (2.2.0)
    ......
      Running setup.py develop for ofrak-patch-maker
    Successfully installed ofrak-patch-maker
    
    # 也可以手动安装
    # 可先下载第一个问题中的几个压缩包至/tmp，再进行安装
    #LLVM
    $ mkdir -p /opt/rbs/toolchain && \\
        tar xf clang+llvm-12.0.1-x86_64-linux-gnu-ubuntu-16.04.tar.xz -C /opt/rbs/toolchain && \\
        rm -rf clang+llvm-12.0.1-x86_64-linux-gnu-ubuntu-16.04.tar.xz && \\
        mv /opt/rbs/toolchain/clang+llvm-12.0.1-x86_64-linux-gnu-ubuntu- /opt/rbs/toolchain/llvm_12.0.1
    
    # ARM GNU NONE EABI
    $ cd /tmp && \\
        tar xf gcc-arm-none-eabi-10-2020-q4-major-x86_64-linux.tar.bz2 -C /opt/rbs/toolchain && \\
        rm -rf gcc-arm-none-eabi-10-2020-q4-major-x86_64-linux.tar.bz2
    
    # LINUX GNU + BINUTILS
    $ cd /tmp && \\
        apt-get -y update  && apt-get -y install software-properties-common gcc-10
    
    $ cd /tmp && \\
        apt-get update && apt-get install -y texinfo && \\
        tar xvf binutils_2.34.orig.tar.xz -C /opt/rbs/toolchain && \\
        rm -rf binutils_2.34.orig.tar.xz && \\
        cd /opt/rbs/toolchain/binutils-2.34 && \\
        ./configure CC=/usr/bin/x86_64-linux-gnu-gcc-10 && \\
        make -j32
    
    #M68k GNU 10 Linux
    $ apt-get update && apt-get install -y gcc-10-m68k-linux-gnu
    
    #M68k VBCC
    $ cd /tmp && \\
        mkdir -p /opt/rbs/toolchain/vbcc_0_9/bin/ && \\
        mkdir -p /opt/rbs/toolchain/vbcc_0_9/config/ && \\
        tar -xvf vbcc0_9h.tar.gz
    
    $ cd /tmp/vbcc && printf "\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n" | TARGET=m68k make all
    
    $ cd /tmp/vbcc && cp ./bin/* /opt/rbs/toolchain/vbcc_0_9/bin/ && \\
        cd .. && \\
        tar -xvf vasm1_9.tar.gz && \\
        cd ./vasm && \\
        CPU=m68k SYNTAX=mot make && \\
        cp ./vasmm68k_mot /opt/rbs/toolchain/vbcc_0_9/bin/ && \\
        cp ./vobjdump /opt/rbs/toolchain/vbcc_0_9/bin/
    
    #AARCH64 GNU 10 Linux
    $ apt-get update && apt-get install -y gcc-10-aarch64-linux-gnu
    

其他基础模块也大致相同(觉得安装慢可以+http_proxy)，当然也可以在根文件夹直接使用`make -C <modoule_name>
$INSTALL_TARGET`，这会用到`.ymal`配置，这里不再赘述。

将`ofrak_core`、`ofrak_components`、`ofrak_io`、`ofrak_patch_maker`、`ofrak_tutorial`、`ofrak_type`、`disassemblers/ghidra`安装完毕后即可使用基础功能。![](https://image.3001.net/images/20220821/1661078502_63020be6824cd35b15704.png!small)

下面来看GUI的安装。

###  **3.2.2 GUI 安装**

由于官方的教程并不明确，笔者又没有遵循自动化流程，所以GUI的安装得多查阅几个文件，从安装好的端口信息可以看出此GUI结合了`nginx`、`NodeJS`和`Python`模块。

    
    
    # netstat -nltp
    Active Internet connections (only servers)
    Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name
    tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN      6494/nginx: master
    tcp        0      0 0.0.0.0:8877            0.0.0.0:*               LISTEN      5435/python3
    tcp        0      0 0.0.0.0:13100           0.0.0.0:*               LISTEN      6116/java
    tcp        0      0 0.0.0.0:13101           0.0.0.0:*               LISTEN      6116/java
    tcp        0      0 127.0.0.53:53           0.0.0.0:*               LISTEN      742/systemd-resolve 
    tcp        0      0 0.0.0.0:13102           0.0.0.0:*               LISTEN      6116/java
    tcp        0      0 127.0.0.1:631           0.0.0.0:*               LISTEN      6934/cupsd
    tcp        0      0 127.0.0.1:42343         0.0.0.0:*               LISTEN      857/containerd
    tcp6       0      0 :::80                   :::*                    LISTEN      6494/nginx: master
    tcp6       0      0 127.0.0.1:15003         :::*                    LISTEN      6090/java
    

首先进入`frontend`文件夹，通过阅读`ReadMe`可以看到，安装可以简单的使用`make app-stack-dev`。安装果然
**不出意外的出了意外**
，还是`mirror`无效的问题。![](https://image.3001.net/images/20220821/1661078514_63020bf274dfc2af4e268.png!small)

那就老老实实看看这个文件夹里都有啥信息吧。

  * `Dockerstage`

    
    
    FROM node:latest AS svelte
    COPY --chown=node:node frontend /home/node/frontend
    WORKDIR /home/node/frontend
    RUN su node -c "npm install && npm run build"
    

说明要装node，执行`su node -c "npm install && npm run build"`

  * `Dockerstub`

    
    
    COPY --from=svelte --chown=root:root /home/node/frontend/public /ofrak_gui
    
    COPY frontend/nginx.conf /etc/nginx/sites-enabled/default
    COPY frontend/backend/ofrak_server.py /ofrak_server.py
    
    RUN apt-get update && apt-get install --yes nginx
    RUN python3 -m pip install --upgrade aiohttp
    
    ENTRYPOINT nginx \\
      & python3 -m ofrak_ghidra.server start \\
      & python3 /ofrak_server.py 0.0.0.0 8877
    

需要`nginx`、`aiohttp`和`ofrak_ghidra.server`，还给出了GUI **启动方法** 、 **工作目录** 和
**nginx** 配置，这就简单了，操作如下：

    
    
    # 安装 node
    $ cd frontend
    $ npm install && npm run build
    
    # 安装 nginx 和
    $ sudo apt-get update && apt-get install --yes nginx
    $ python3 -m pip install --upgrade aiohttp
    
    # 拷贝网页目录
    $ cp -r frontend/public /home/ofrak/ofrak_gui
    # 拷贝并修改nginx配置 (依据个人情况，将default文件中的 root 改为上述ofrak_gui路径)
    # <root /ofrak_gui> -> <root /home/ofrak/ofrak_gui>
    $ sudo cp frontend/nginx.conf /etc/nginx/sites-enabled/default
    
    # 安装 ofrak_ghidra
    # /disassemblers/ofrak_ghidra 文件夹中，模块安装时已安装
    # 下载 ghidra_10.1.2_PUBLIC 拷贝至 /opt/rbs/ 文件夹下
    $ ls /opt/rbs
    ghidra_10.1.2_PUBLIC  toolchain
    
    # 拷贝 ofrak_server.py 文件
    $ cp frontend/backend/ofrak_server.py /home/ofrak/ofrak_server.py
    

启动脚本如下：

    
    
    $ sudo nginx \\
      & sudo python3 -m ofrak_ghidra.server start \\
      & sudo python3 /home/ofrak/ofrak_server.py 0.0.0.0 8877
    

访问本地`80`端口，发现终于成功了：![](https://image.3001.net/images/20220821/1661078527_63020bffbff95c833b12e.png!small)

赶紧编个`helllo
world`放进去试试：![](https://image.3001.net/images/20220821/1661078538_63020c0aac64a72c2bf39.png!small)

# 四、实战测试

分析人员可使用OFRAK Python API扩展编写自己的工具，在`examples`文件夹中官方给出了8个例子，这些例子涵盖了 **OFRAK** 的
**大部分功能** ，当然也可一参见[
**官方文档**](https://ofrak.com/docs/examples/ex1_simple_string_modification.html)。

  *  **`Simple String Modification`**

该实例修改输出的内容，将其替换为制定字符串。

  *  **`Simple Code Modification`**

该示例修改ELF文件逻辑，使其按照指定流执行。

  *  **`Binary Format Modification`**

该示例分析 ELF 头并更改 LOAD 程序头的权限，将该部分标记为不可执行。

  *  **`Filesystem Modification`**

该示例解压缩 Squashfs 文件，并分析其每个内容。

  *  **`Binary Extension`**

该示例在ELF中添加了一个新段，并重写了该二进制文件以打印制定字符串。

  *  **`Code Modification Without Extension`**

该示例完成了ELF中的函数替换。

  *  **`Code Insertion With Extension`**

该示例在 ELF 中添加一个新段，并在以下代码中添加将所有小写字符转换为大写的补丁，补丁代码使用`OFRAK PatchMaker`。

  *  **`Recursive Unpacking`**

该示例将输入文件以递归方式解压缩，并向其中添加一个指定的新文本文件。

由于篇幅限制，这里只举一个最简单的例子，即修改字符串：

    
    
    # ofrak_str.py
    import argparse
    import os
    
    from ofrak import OFRAK
    from ofrak import OFRAKContext
    from ofrak.core import BinaryPatchModifier, BinaryPatchConfig
    
    ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "assets"))
    
    async def main(ofrak_context: OFRAKContext, file_path: str, output_file_name: str):
        # Load a binary file into OFRAK as a resource
        root_resource = await ofrak_context.create_root_resource_from_file(file_path)
        data = await root_resource.get_data()
    
        # 寻找二进制文件中的 "Hello, World!" 字符串 
        hello_world_offset = data.find(b"Hello, World!")
    
    		# 将第一个找到的位置改成 Meow
        new_string_config = BinaryPatchConfig(hello_world_offset, b"Meow!\\0")
        await root_resource.run(BinaryPatchModifier, new_string_config)
    
        # Output the modified binary to the disk
        await root_resource.flush_to_disk(output_file_name)
        print(f"Done! Output file written to {output_file_name}")
    
    if __name__ == "__main__":
        parser = argparse.ArgumentParser()
    		# 输入文件
        parser.add_argument("--hello-world-file", default="./hello_world")
    		# 输出文件
        parser.add_argument("--output-file-name", default="./example_1_meow")
        args = parser.parse_args()
        ofrak = OFRAK()
        ofrak.run(main, args.hello_world_file, args.output_file_name)
    
    // hello_world.c
    #include <stdio.h>
    int main() {
       printf("Hello, World!\\n");
       return 0;
    }
    

结果如下：![](https://image.3001.net/images/20220821/1661078552_63020c185d0ce5c72603b.png!small)

OFRAK号称是IOT分析平台，具备对固件的解包和打包能力，当然也是基于`binwalk`，功能也与上述的例子差不多，只是用Web
GUI显得更方便些，这里不再赘述。与之前笔者研究的 **FACT**
类似，提供了插件开发接口，感兴趣的小伙伴可参见[官方开发指南](https://ofrak.com/docs/contributor-guide/component/identifier.html)。![](https://image.3001.net/images/20220821/1661078608_63020c503792b828d69aa.png!small)

# 五、总结

通过安装与结构的简单分析可以大致了解 **OFRAK** 是一款集成(缝合)类工具，其最大贡献是将多种工具整合，这也体现了python胶水语言的特性。与
**FACT** 相比， **OFRAK**
更侧重于二进制分析，二前者更注重固件数据库的构建(更耗费资源)。相同点就是由于系统比较复杂，安装起来都比较耗时费力。对于 **OFRAK** ，喜欢All
in one 分析工具的小伙伴可以考虑用起来。

 **参考资料**

  * [ **Newstnewstody**](https://newestnewstoday.com/ofrak-an-open-source-iot-reverse-engineering-tool-is-finally-here/)

  * [ **OFRAK 官网**](https://ofrak.com/)

  * [ **OGRAK Github**](https://github.com/redballoonsecurity/ofrak)

