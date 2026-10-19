![](https://image.3001.net/images/20211123/1637657011_619ca9b3baca3cb5be5b0.png!small)  

## 关于NetworKit

[ _Ne_ _twor_ _K_
_it_](https://networkit.github.io/)是一款针对高性能网络安全分析的开源工具，该工具旨在帮助广大安全研究人员分析具备数千到数十亿条边界的大型网络。为了实现这个目标，该工具实现了非常高效的图形算法，其中许多算法是并行的，以利用多核架构来计算网络分析的标准度量。NetworKit专注于功能方面的可扩展性和全面性，而NetworKit也是一种算法工程的试验平台，其中包含了很多最新发表的处于研究中的新算法。

NetworKit本质上是一个
Python模块，其中的高性能算法是基于C++开发的，并通过Cython工具链开放给Python。而Python反过来会为我们提供交互工作的能力，以及用于数据分析和科学计算的丰富工具环境。除此之外，如果需要的话，我们还可以构建NetworKit的核心并将其以本地库的形式使用。

## 工具要求

我们需要下列软件来将NetworKit安装为Python包：

  * 一个现代C++编译器，例如[ _g++_](https://gcc.gnu.org/)（>= 6.1）、[ _clang++_](https://clang.llvm.org/)（>= 3.9）或MSVC（>= 14.13）;
  * OpenMP（为实现并行性，通常随编译器提供）；
  * Python 3（6或更高版本）；
  * [ _pip_](https://pypi.python.org/pypi/pip)；
  * [ _CMake_](https://cmake.org/)（6或更高版本，安装命令：“pip3 install cmake”）；
  * 构建系统：[ _Make_](https://www.gnu.org/software/make/)或[ _Ninja_](https://ninja-build.org/)；
  * Cython（29或更高版本，安装命令：“pip3 install cython”）；

## 工具安装

为了使用NetworKit，我们可以通过包管理器来安装，或从源码构建Python模块。

### 通过包管理器安装

我们可以通过包管理器来安装最新版本的NetworKit。

 **Pip安装：**

    
    
    pip3 install [--user] networkit

 **Conda安装：**

    
    
    conda config --add channels conda-forge
    
    conda install networkit [-c conda-forge]

 **Brew安装：**

    
    
    brew install networkit

 **Spack安装：**

    
    
    spack install py-networkit

### 从源码构建Python模块

    
    
    git clone https://github.com/networkit/networkit networkit
    
    cd networkit
    
    python3 setup.py build_ext [-jX]
    
    pip3 install -e .

## 工具使用样例

在下面的工具演示样例中，我们将生成一个具有十万个节点的随机双曲线图，并使用PLM方法计算其网络（社区）：

    
    
    >>> import networkit as nk
    
    >>> g = nk.generators.HyperbolicGenerator(1e5).generate()
    
    >>> communities = nk.community.detectCommunities(g, inspect=True)
    
    PLM(balanced,pc,turbo) detected communities in 0.14577102661132812 [s]
    
    solution properties:
    
    -------------------  -----------    
    # communities        4536
    
    min community size      1
    
    max community size   2790
    
    avg. community size    22.0459
    
    modularity              0.987243
    
    -------------------  -----------
## 将NetworKit以代码库的形式使用

除了直接使用NetworKit之外，我们还可以将NetworKit以代码库的形式使用。在下面的示例中，我们将在/usr/local中编译和安装NetworKit：

    
    
    cmake ..
    
    make -jX install

安装好NetworKit之后，我们就可以在C++应用程序中通过下列方法来使用include指令了：

    
    
    #include <networkit/graph/Graph.hpp>

我们还可以通过以下方法编译我们的源码：

    
    
    g++ my_file.cpp -lnetworkit

## 许可证协议

本项目的开发与发布遵循[ _MIT开源许可证协议_](http://opensource.org/licenses/MIT)。

## 项目地址

 **NetworKit：** 【[ _GitHub传送门_](https://github.com/networkit/networkit)】

## 参考资料

  * [ _https://networkit.github.io/_](https://networkit.github.io/)
  * [ _https://gcc.gnu.org/_](https://gcc.gnu.org/)
  * [ _https://clang.llvm.org/_](https://clang.llvm.org/)
  * [ _https://pypi.python.org/pypi/pip_](https://pypi.python.org/pypi/pip)
  * [ _https://cmake.org/_](https://cmake.org/)
  * [ _https://www.gnu.org/software/make/_](https://www.gnu.org/software/make/)
  * [ _https://ninja-build.org/_](https://ninja-build.org/)
  * [ _https://networkit.github.io/get_started.html_](https://networkit.github.io/get_started.html)
  * [ _https://github.com/tlx/tlx/_](https://github.com/tlx/tlx/)
  * [ _http://www.ttmath.org/_](http://www.ttmath.org/)
  * [ _https://networkit.github.io/dev-docs/index.html_](https://networkit.github.io/dev-docs/index.html)

