**JSON文档在Internet上无处不在，服务器花费大量时间来解析这些文档。我们希望在进行完全验证（包括字符编码）时尽可能使用常用的SIMD指令来加速JSON本身的解析。**

## 表现结果

simdjson使用的指令比最先进的解析器RapidJSON少四分之三，比sajson少百分之五十。据我们所知，simdjson是第一个在商用处理器上以每秒千兆字节运行的完全验证的JSON解析器。

![gbps.png](https://image.3001.net/images/20190315/15526260489945.png!small)

在Skylake处理器上，twitter.json文件上各种处理器的解析速度（以GB / s为单位）如下。

解析器| GB /秒  
---|---  
simdjson| 2.2  
RapidJSON编码验证| 0.51  
RapidJSON编码验证，原位| 0.71  
sajson（原状，动态）| 0.70  
sajson（insitu，static）| 0.97  
dropbox| 0.14  
FASTJSON| 0.26  
gason| 0.85  
ultrajson| 0.42  
jsmn| 0.28  
cJSON| 0.34  
  
## 要求

> 我们通过Visual Studio 2017或更高版本支持Linux或macOS等平台以及Windows；
>
> 带有AVX2的处理器（即，2013年发布的Haswell微体系结构的Intel处理器和2017年发布的Zen微体系结构的AMD处理器）；
>
> 最近的C ++编译器（例如，GNU GCC或LLVM CLANG或Visual Studio 2017），我们假设C ++ 17。GNU GCC
> 7或更高版本或LLVM的clang 6或更高版本。

## License

此代码在Apache License 2.0下提供。

在Windows下，我们使用`windows/dirent_portable.h`文件（在我们的库代码之外）构建一些工具

## 代码示例

    
    
    #include "simdjson/jsonparser.h"
    
    /...
    
    const char * filename = ... //
    
    //使用您想要的任何方式获取JSON文档的字符串
    std::string_view p = get_corpus(filename);
    ParsedJson pj;
    pj.allocateCapacity(p.size());//分配内存以解析p.size（）字节
    const int res = json_parse(p, pj); //进行解析，成功时返回0 
    //解析完成！
    if（res！= 0）{
         //您可以使用“simdjson / simdjson.h”标头来访问错误消息 
       std::cout << "Error parsing:" << simdjson::errorMsg(res) << std::endl;
    }
    //你可以安全地删除字符串内容
    free((void*)p.data());
    //可以在这里使用ParsedJson文档
    // js可以与其他json_parse调用一起使用。
    

如果您不介意为每个新的JSON文档分配内存开销，也可以使用更简单的API：

    
    
    #include "simdjson/jsonparser.h"
    
    / ...
    
    const char * filename = ... //
    std::string_view p = get_corpus(filename);
    ParsedJson pj = build_parsed_json(p);  //进行解析
    //此时你不再需要p，可以执行aligned_free（（void *）p.data（））
    if( ! pj.isValid() ) {
         //出错了 
    }
    

## 用法：简单的版本

有关用法，请参阅“singleheader”存储库的文件“amalgamation_demo.cpp”。这不需要特定的构建系统：只需在包含路径中复制项目中的文件即可。然后，您可以非常简单地包含它们：

    
    
    #include <iostream>
    #include "simdjson.h"
    #include "simdjson.cpp"
    int main(int argc, char *argv[]) {
      const char * filename = argv[1];
      std::string_view p = get_corpus(filename);
      ParsedJson pj = build_parsed_json(p); // do the parsing
      if( ! pj.isValid() ) {
        std::cout << "not valid" << std::endl;
      } else {
        std::cout << "valid" << std::endl;
      }
      return EXIT_SUCCESS;
    }
    

我们需要AVX2指令的硬件支持。您必须确保指示编译器根据需要使用这些说明。在GNU GCC或LLVM
clang等编译器下，`-march=native`最近的Intel处理器（Haswell或更好）上使用的标志就足够了。为了便于二进制文件的可移植性，您还可以直接指定Haswell处理器（`-march=haswell`）。您也可以使用标志`-mavx2
-mbmi2`。在Visual Studio下，您需要定位x64并添加标志`/arch:AVX2`。

注意：在某些设置中，可能需要预编译`simdjson.cpp`而不是包含它。

## 用法（在Linux或macOS等平台上使用旧版Makefile）

要求：最近的clang或gcc，和make。我们建议至少使用GNU GCC / G ++ 7或LLVM clang
6.需要像Linux或macOS这样的系统。

测试：

    
    
    make
    make test
    

要运行基准测试：

    
    
    make parse
    ./parse jsonexamples/twitter.json
    

在Linux下，该`parse`命令提供了性能计数器的详细分析。

运行比较基准测试（与其他解析器）：

    
    
    make benchmark
    

## 用法（在Linux或macOS等平台上使用CMake）

要求：我们需要最新版本的cmake。在macOS上，安装cmake的最简单方法可能是使用[brew](https://brew.sh/)然后键入

    
    
    brew install cmake
    

[在Linux上](https://linuxbrew.sh/)有一个[相同的Brew也可以以相同的方式工作](https://linuxbrew.sh/)。

你需要一个像clang或gcc这样的最新编译器。我们建议至少使用GNU GCC / G ++ 7或LLVM clang
6.例如，您可以使用brew安装最新的编译器：

    
    
    brew install gcc@8
    

可选：您需要通过设置CC和CXX变量告诉cmake您希望使用哪个编译器。bash下，你可以用诸如命令这样做`export CC=gcc-7`和`export
CXX=g++-7`。

构建：在项目存储库中，执行以下操作：

    
    
    mkdir build
    cd build
    cmake ..
    make
    make test
    

默认情况下，它构建一个共享库（例如，Linux上的libsimdjson.so）。

您可以构建一个静态库：

    
    
    mkdir buildstatic
    cd buildstatic
    cmake -DSIMDJSON_BUILD_STATIC=ON ..
    make
    make test
    

在某些情况下，您可能希望指定编译器，尤其是在系统上的默认编译器太旧的情况下。您可以按以下步骤操作：

    
    
    brew install gcc@8
    mkdir build
    cd build
    export CXX=g++-8 CC=gcc-8
    cmake ..
    make
    make test
    

## 用法（使用Visual Studio在Windows上进行CMake）

我们假设您有一台普通的Windows PC，至少包含Visual Studio 2017和支持AVX2的x64处理器（2013 Intel
Haswell或更高版本）。

> 从GitHub获取simdjson代码，例如，使用[GitHub Desktop](https://desktop.github.com/)克隆它；
>
>
> 安装[CMake](https://cmake.org/download/)。安装时，请确保`cmake`从命令行询问是否可用。请选择最新版本的cmake；
>
> 在simdjson中创建一个子目录，例如`VisualStudio；`
>
> 使用shell，转到这个新创建的目录；
>
> `cmake -DCMAKE_GENERATOR_PLATFORM=x64 ..`在`VisualStudio`存储库中键入shell
> 。（或者，如果要构建DLL，可以使用命令行`cmake -DCMAKE_GENERATOR_PLATFORM=x64
> -DSIMDJSON_BUILD_STATIC=OFF ..`）
>
> 最后一个命令在新创建的目录中创建了一个Visual Studio解决方案文件（例如`simdjson.sln`）。在Visual
> Studio中打开此文件。您现在应该能够构建项目并运行测试。例如，在`Solution
> Explorer`窗口（可从`View`菜单中获得）中，右键单击`ALL_BUILD`并选择`Build`。要测试代码，仍然在`Solution
> Explorer`窗口中，选择`RUN_TESTS`并选择`Build`。

## 用法（在Windows，Linux和MacOS上使用vcpkg）

Windows，Linux和MacOS上的[vcpkg](https://github.com/Microsoft/vcpkg)用户可以`simdjson`使用他们喜欢的shell中的一个命令下载和安装。

在Linux和MacOS上：

    
    
    $ ./vcpkg install simdjson
    

将构建并安装`simdjson`为静态库。

在Windows（64位）上：

    
    
    .\vcpkg.exe install simdjson:x64-windows
    

将构建并安装`simdjson`为共享库。

    
    
    .\vcpkg.exe install simdjson:x64-windows-static  
    

将构建并安装`simdjson`为静态库。

这些命令还将打印出有关如何使用MSBuild或基于CMake的项目库的说明。

如果您发现`simdjson`附带的版本`vcpkg`已过期，请随时通过提交`vcpkg`问题或创建PR 向社区报告。

## 工具

> json2json mydoc.json`解析文档，构造模型，然后将结果转储回标准输出`
>
> json2json -d mydoc.json`解析文档，构造模型，然后将模型（作为磁带）转储到标准输出。磁带格式在随附文件中描述`tape.md
>
> minify mydoc.json`缩小JSON文档，将结果输出到标准输出。缩小意味着删除不需要的空格字符。

## 范围

我们提供快速解析器。它根据各种规格完全验证输入。解析器构建一个有用的不可变（只读）DOM（文档 - 对象模型），以后可以访问它。

为了简化工程，我们做了一些假设：

>
> 我们支持UTF-8（以及ASCII），没有别的（没有拉丁语，没有UTF-16）。我们不认为这是一个真正的限制，因为我们认为没有任何严重的应用程序需要在没有ASCII或UTF-8编码的情况下处理JSON数据；
>
>
> JSON文档中的所有字符串最多可包含UTF-8（4GB）中的4294967295个字节。要强制执行此约束，我们拒绝解析包含超过4294967295字节（4GB）的文档。这应该适应大多数JSON文档；
>
>
> 我们假设AVX2支持在AMD和英特尔生产的所有最新主流x86处理器中都可用。尽管可以完成，但不包括对非x86处理器的支持。我们计划支持ARM处理器（请求帮助）；
>
> 如果发生故障，我们只会报告故障，而不会指出问题的性质。（这可以在不影响性能的情况下轻松改进）；
>
> 在规范允许的情况下，我们允许对象内的重复键（像sajson这样的其他解析器也这样做）；
>
> 性能针对跨越至少几十千字节到几兆字节的JSON文档进行了优化：必须解析许多小型JSON文档或一个真正庞大的JSON文档的性能问题是不同的。

我们的目标不是提供通用的JSON库。像RapidJSON这样的库提供的不仅仅是解析，它还可以帮助您生成JSON并提供各种其他方便的功能。我们只解析文档。

## 特征

输入字符串未修改，（像sajson和RapidJSON这样的解析器使用输入字符串作为缓冲区）。

我们将整数和浮点数解析为单独的类型，这允许我们支持[-9223372036854775808,9223372036854775808]中的大型64位整数，如Java
`long`或C / C ++ `long
long`。在区分整数和浮点数的解析器中，并非所有解析器都支持64位整数。（例如，sajson拒绝整数大于或等于2147483648的JSON文件.FreeJSON将解析包含过长整数的文件，如18446744073709551616作为浮点数）当我们无法将整数表示为带符号的64位时值，我们拒绝JSON文档。

在解析过程中进行完整的UTF-8验证（像fastjson，gason和dropbox
json11这样的解析器不会进行UTF-8验证）；完全验证了这些数字（像gason和ultranjson这样的解析器将接受`[0e+]`为有效的JSON）；验证未转义字符的字符串内容（像fastjson和ultrajson这样的解析器接受未转义的换行符和字符串中的标签）。

## Architecture

解析器分两个阶段工作：

> 阶段1.（查找标记）快速标识结构元素，字符串等。我们在那个阶段验证UTF-8编码。
>
> 阶段2.（结构构建）涉及构建排序的“树”（具体化为磁带）以浏览数据。在此阶段解析字符串和数字。

## 导航已解析的文档

以下是将解析后的JSON转储回字符串的代码示例：

    
    
       ParsedJson::iterator pjh(pj);
        if (!pjh.isOk()) {
          std::cerr << " Could not iterate parsed result. " << std::endl;
          return EXIT_FAILURE;
        }
        compute_dump(pj);
        //
        // where compute_dump is :
    
    void compute_dump(ParsedJson::iterator &pjh) {
      if (pjh.is_object()) {
        std::cout << "{";
        if (pjh.down()) {
          pjh.print(std::cout); // must be a string
          std::cout << ":";
          pjh.next();
          compute_dump(pjh); // let us recurse
          while (pjh.next()) {
            std::cout << ",";
            pjh.print(std::cout);
            std::cout << ":";
            pjh.next();
            compute_dump(pjh); // let us recurse
          }
          pjh.up();
        }
        std::cout << "}";
      } else if (pjh.is_array()) {
        std::cout << "[";
        if (pjh.down()) {
          compute_dump(pjh); // let us recurse
          while (pjh.next()) {
            std::cout << ",";
            compute_dump(pjh); // let us recurse
          }
          pjh.up();
        }
        std::cout << "]";
      } else {
        pjh.print(std::cout); // just print the lone value
      }
    }
    

以下函数将查找所有user.id整数：

    
    
    void simdjson_traverse(std::vector<int64_t> &answer, ParsedJson::iterator &i) {
      switch (i.get_type()) {
      case '{':
        if (i.down()) {
          do {
            bool founduser = equals(i.get_string(), "user");
            i.next(); // move to value
            if (i.is_object()) {
              if (founduser && i.move_to_key("id")) {
                if (i.is_integer()) {
                  answer.push_back(i.get_integer());
                }
                i.up();
              }
              simdjson_traverse(answer, i);
            } else if (i.is_array()) {
              simdjson_traverse(answer, i);
            }
          } while (i.next());
          i.up();
        }
        break;
      case '[':
        if (i.down()) {
          do {
            if (i.is_object_or_array()) {
              simdjson_traverse(answer, i);
            }
          } while (i.next());
          i.up();
        }
        break;
      case 'l':
      case 'd':
      case 'n':
      case 't':
      case 'f':
      default:
        break;
      }
    }
    

## 深入比较

如果您想了解各种解析器如何验证给定的JSON文件：

    
    
    make allparserscheckfile
    ./allparserscheckfile myfile.json
    

对于性能比较：

    
    
    make parsingcompetition
    ./parsingcompetition myfile.json
    

进行更广泛的比较：

    
    
    make allparsingcompetition
    ./allparsingcompetition myfile.json

***参考来源[github](https://github.com/lemire/simdjson)，由周大涛编译，转载请注明来自FreeBuf.COM**  

