![1.png](https://image.3001.net/images/20180225/15195435137985.png!small)  

**今天给大家介绍的是一个名叫LSB-Steganography的Python工具，该工具可以使用最低有效位技术来将文件隐写到图像之中。**

## LSB-Steganography

本工具所使用的最基本的技术就是最低有效位（Least Significant
Bit）。一个颜色像素由红色、绿色和蓝色构成，并编码成一个字节。而我们的想法就是将数据存储在每一个颜色像素（RGB）的第一比特位上。实际上，如果你无法在每一个像素的第一个比特位中存储你所有的数据，你就应该使用到第二个比特位，以此类推这样。但是你要记住一点，图像中存储的数据越多，你的数据就越有可能被检测到。

## 工具信息

LSBSteg模块基于OpenCV来在图片中隐藏数据，它主要使用的是图片中每个颜色像素的第一个比特位，工具源码也比较好理解：如果图片中每一个颜色像素的第一个比特位都已经被使用了的话，它将会开始使用第二个比特位，所以你要隐写的数据量越大，图片中的信息就越有可能被检测出来。如果图片的空间足够大，那本工具就可以把所有的数据全部隐写进去。

本工具的主要功能如下：

1\. 编码文本：输入一个字符串，本工具可以帮你将其隐写在图片里；

2\. 编码图像：输入一个OpenCV图片，并将图片隐写到目标文件里，目标文件的大小最好是需要隐藏的文件大小的八倍左右。注：本工具仅支持未压缩的图像；

3\. 编码代码：提供一个需要隐藏的代码文件，本工具支持任何类型的代码文件；

## 工具安装

将本项目下载到本地之后，你需要安装OpenCV及其依赖组件：

    
    
    pip install -r requirements.txt

工具使用

    
    
    LSBSteg.py
     
    Usage:
      LSBSteg.py encode -i <input> -o<output> -f <file>
      LSBSteg.py decode -i <input> -o<output>
     
    Options:
      -h, --help                Show this help
      --version                 Show the version
      -f,--file=<file>          File to hide
      -i,--in=<input>           Input image (carrier)
      -o,--out=<output>         Output image (or extracted file)

## Python模块

### 文本编码：

    
    
    #encoding
    steg= LSBSteg(cv2.imread("my_image.png"))
    img_encoded= steg.encode_text("my message")
    cv2.imwrite("my_new_image.png",img_encoded)
     
    #decoding
    im =cv2.imread("my_new_image.png")
    steg= LSBSteg(im)
    print("Textvalue:",steg.decode_text())

### 图像隐写：

    
    
    #encoding
    steg= LSBSteg(cv2.imread("carrier.png")
    new_im= steg.encode_image(cv2.imread("secret_image.jpg"))
    cv2.imwrite("new_image.png",new_im)
     
    #decoding
    steg= LSBSteg("new_image.png")
    orig_im= steg.decode_image()
    cv.SaveImage("recovered.png",orig_im)

### 代码隐写：

    
    
    #encoding
    steg= LSBSteg(cv2.imread("carrier.png"))
    data= open("my_data.bin", "rb").read()
    new_img= steg.encode_binary(data)
    cv2.imwrite("new_image.png",new_img)
     
    #decoding
    steg= LSBSteg(cv2.imread("new_image.png"))
    binary= steg.decode_binary()
    withopen("recovered.bin", "rb") as f:
    f.write(data)

## 许可证协议

本软件遵循MIT许可证协议开发。

 *** 参考来源：[LSB-Steganography](https://github.com/RobinDavid/LSB-Steganography)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

