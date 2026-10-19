# 关于inject

一直以来，iOS的代码注入工具有optool和yololib，但是这两个库已经许久不维护了。因此inject的出现为代码注入事业重新注入了活力。

inject采用Swift代码编写，可以直接运行在装有最新macOS的mac电脑上。

inject可以向machO文件中写入load commands，让machO在运行的过程中加载相应的动态库，实现代码注入的功能。

# 功能介绍

    
    
    ❯ ./inject -h
    OVERVIEW: inject v2.0.0
    
    inject is a tool which interfaces with MachO binaries in order to insert load commands.
    
    USAGE: inject <file-path> [--dylib <dylib>] [--cmd <cmd>] [--ipa] [--strip] [--aslr] [--weak <weak>]
    
    ARGUMENTS:
      <file-path>             The machO/ipa to inject.
    
    OPTIONS:
      -d, --dylib <dylib>     The dylib to inject, please give me path.
      -c, --cmd <cmd>         Specify which type of load command to use in INSTALL. Can be reexport for LC_REEXPORT_DYLIB, weak for LC_LOAD_WEAK_DYLIB, upward
                              for LC_LOAD_UPWARD_DYLIB, or load for LC_LOAD_DYLIB. (default: LC_LOAD_DYLIB)
      -i, --ipa               If inject into ipa, please set this flag. Default false mean is machO file path.
      -s, --strip             Removes a code signature load command from the given binary.
      -a, --aslr              Removes an ASLR flag from the macho header if it exists. This may render some executables unusable.
      -w, --weak <weak>       Used with the STRIP command to weakly remove the signature. Without this, the code signature is replaced with null bytes on the
                              binary and it's LOAD command is removed. (default: true)
      --version               Show the version.
      -h, --help              Show help information.
    

# 使用方法

### 向mac可执行文件中注入dylib:

    
    
    ❯ ./inject testExec -d @executable_path/testMac/libtestinject.dylib
    

### 向IPA文件中注入dylib:

该方法可以直接得到一个重打包的IPA文件

    
    
    ❯ ./inject testiOS/app.ipa -d  @executable_path/testiOS/libinjectiOS.dylib --ipa
    

### 向IPA文件中注入framework:

该方法可以直接得到一个重打包的IPA文件

    
    
    ❯ ./inject testiOS/app.ipa -d  @executable_path/testiOS/injectiOSFramework.framework/injectiOSFramework --ipa
    

直接使用.framework后缀的路径也可以注入成功

    
    
    ❯ ./inject testiOS/app.ipa -d  @executable_path/testiOS/injectiOSFramework.framework --ipa
    

# 需要注意

重新打包后的IPA文件需要重签名才可以运行，并且如果注入了dylib文件，需要针对dylib文件单独重签名，否则App运行时闪退。

重签名主要是使用codesign命令，大概像这样：

    
    
    ❯ security find-identity -v -p codesigning
    1) xxxxx "Apple Development: xxx xx (xxxxxxxxxx)"
         1 valid identities found
    ❯ codesign -f -s "xxxxx" Payload/app.app
    Payload/app.app: replacing existing signature
    ❯ codesign -f -s "xxxxx" Payload/app.app/Inject/libxxxxx.dylib
    Payload/app.app/Inject/libxxxxx.dylib: replacing existing signature
    

# 项目地址

<https://github.com/paradiseduo/inject>

