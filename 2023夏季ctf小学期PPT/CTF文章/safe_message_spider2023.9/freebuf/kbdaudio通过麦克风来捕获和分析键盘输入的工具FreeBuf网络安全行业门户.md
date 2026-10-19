## 前言

 **kbd-audio项目是一系列用于捕获和分析音频数据的命令行和GUI工具的集合。其中我认为最有意思的一款工具是keytap，它可以通过麦克风来捕获和分析键盘的输入，从而猜测出按键内容。**

有关keytap的更多信息，可以参阅以下博文及演示视频：

[Keytap: description and some random
thoughts](https://ggerganov.github.io/jekyll/update/2018/11/30/keytap-description-and-thoughts.html)

## 构建说明

### 相关依赖

SDL2 - 用于捕获音频和打开GUI windows [libsdl](https://www.libsdl.org/)

FFTW3 - 一些辅助工具执行傅里叶变换（Fourier Transformation）fftw

### Linux & Mac OS

    
    
    git clone https://github.com/ggerganov/kbd-audio
    cd kbd-audio
    git submodule update --init
    mkdir build && cd build
    cmake ..
    make

### Windows

    
    
    (todo, PRs welcome)

## 工具集

### record-full

将音频录制到磁盘上的原始二进制文件

    
    
    ./record-full output.kbd

### play-full

播放通过record-full捕获的录制内容

    
    
    ./play-full input.kbd

### record

仅在键入时录制音频。用于收集keytap的训练数据

    
    
    ./record output.kbd

### play

播放通过record创建的录制内容

    
    
    ./play input.kbd

### keytap

通过麦克风音频实时检测并捕获按下的键。使用record捕获的训练数据。

    
    
    ./keytap-gui input0.kbd [input1.kbd] [input2.kbd] ...

[ **Live
demo**](https://ggerganov.github.io/jekyll/update/2018/11/24/keytap.html)
**[（需要启用WebAssembly
pthreads和SharedArrayBuffer）](https://ggerganov.github.io/jekyll/update/2018/11/24/keytap.html)**

![20181203072156.png](https://image.3001.net/images/20181203/1543792970_5c04694a38706.png!small)

### keytap2（正在开发中）

通过麦克风音频实时检测并捕获按下的键。使用关于语言的统计信息（n-gram频率）。无需训练数据。recording.kbd输入文件必须通过record-full生成，并包含将要分析的音频数据。n-gram.txt文件必须包含相应语言的n-gram概率。

    
    
    ./keytap2-gui recording.kbd n-gram.txt

##
![68747470733a2f2f692e696d6775722e636f6d2f7952336d35426d2e6a7067.jpg](https://image.3001.net/images/20181203/1543792987_5c04695b669e5.jpg!small)

## 反馈

如果你对该工具有任何的疑问或建议，欢迎[在此处](https://github.com/ggerganov/kbd-audio/issues/3)留下你的评论。

 ** *参考来源：[GitHub](https://github.com/ggerganov/kbd-audio)，FB小编secist编译，转载请注明来自FreeBuf.COM**

