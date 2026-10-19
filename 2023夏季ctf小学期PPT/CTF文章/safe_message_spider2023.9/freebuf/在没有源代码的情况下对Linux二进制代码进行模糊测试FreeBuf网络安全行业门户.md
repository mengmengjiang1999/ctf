**AFL配合DynamoRIO，没错，就是drAFL。在drAFL的帮助下，我们就可以在没有源代码的情况下对LInux二进制代码进行模糊测试了。**

![](https://image.3001.net/images/20190512/1557597540_5cd70d64b7f89.jpg!small)

## drAFL

原始版本的AFL支持使用QEMU模式来对待测目标进行黑盒测试，因此在使用drAFL之前，作者强烈建议大家先尝试使用一下原始版本的AFL，如果达不到各位的目标，再来使用drAFL。

## 工具使用

首先，你需要定义DRRUM_PATH值来指向drrun启动工具，并设置LIBCOV_PATH来指向libbinafl.so代码覆盖库。除此之外，你还需要设置AFL的fork服务器（AFL_NO_FORKSRV=1），或者设置“AFL_SKIP_BIN_CHECK=1”。具体请参考代码构建部分的第五步。

注意：请注意，针对64位代码库，你需要使用64位的DynamoRIO，如果使用的是32位的代码库，你就需要使用32位的DynamoRIO了，否则工具将无法正常运行。你可以使用下列命令来确保项目运行在DynamoRIO下：

    
    
    drrun -- <path/to/your/app/> <app_args>

## 代码构建

第一步：将drAFL代码库克隆到本地。

    
    
    git clone <https://github.com/mxmssh/drAFL.git> /home/max/drAFL
    
    cd/home/max/drAFL

第二步：克隆并构建DynamoRIO。

    
    
    git clone <https://github.com/DynamoRIO/dynamorio>
    
    mkdir build_dr
    
    cd build_dr/
    
    cmake../dynamorio/
    
    make -j
    
    cd ..

如果在DynamoRIO的编译环节遇到问题的话，可以参考这篇【[文档](https://github.com/DynamoRIO/dynamorio/wiki/How-To-Build#linux)】。

第三步：构建代码覆盖工具。

    
    
    mkdir build
    
    cd build
    
    cmake ../bin_cov/ -DDynamoRIO_DIR=../build_dr/cmake
    
    make -j
    
    cd ..

第四步：构建AFL。

    
    
    cd afl/
    
    make
    
    cd ..

第五步：配置环境变量并执行扫描任务。

    
    
    cd build
    
    mkdir in
    
    mkdir out
    
    echo "AAAA" > in/seed
    
    export DRRUN_PATH=/home/max/drAFL/build_dr/bin64/drrun
    
    export LIBCOV_PATH=/home/max/drAFL/build/libbinafl.so
    
    export AFL_NO_FORKSRV=1
    
    export AFL_SKIP_BIN_CHECK=1
    
    ../afl/afl-fuzz-m none -i in -o out -- ./afl_test @@

注意：对于afl_test测试样例，可能需要大概25-30秒的执行时间。

## 项目地址

drAFL：【[GitHub传送门](https://github.com/mxmssh/drAFL)】

 ***
参考来源：[mxmssh](https://github.com/mxmssh/drAFL)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

