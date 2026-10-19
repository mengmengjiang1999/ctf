**![Digital-Forensics.jpg](https://image.3001.net/images/20190413/1555112133_5cb120c59988b.jpg!small)**

**Imago是一个由python编写的图像数字取证工具，它可以从图像中递归提取数字证据。在整个数字取证调查中，这款工具非常有用。如果你需要提取图像中的数字证据且数量较多，那么Imago将能够帮助你轻松地对比它们。此外，Imago还允许你将证据提取到CSV文件或sqlite数据库中。如果在JPEG
exif中存在GPS坐标，Imago可以提取经度和纬度，并将它们转换为度数检索相关信息，如城市，国家，邮政编码等。**

## 安装

###  **通过pip**

安装 imago：

    
    
    $ pip install imago

安装完成后，应该有一个新的可用二进制文件：

    
    
    $ imago

然后它应该输出imago banner。

###  **依赖软件包**

    
    
    python 2.7
    exifread 2.1.2
    python-magic 0.4.15
    argparse 1.4.0
    pillow 5.2.0
    nudepy 0.4
    imagehash 4.0
    geopy 1.16.0

## 使用

    
    
    usage: imago.py [-h] -i INPUT [-x] [-g] [-e] [-n] [-d {md5,sha256,sha512,all}]
                    [-p {ahash,phash,dhash,whash,all}] [-o OUTPUT] [-s]
                    [-t {jpeg,tiff}]
    
    optional arguments:
      -h, --help            show this help message and exit
      -i INPUT, --input INPUT
                            Input directory path
      -x, --exif            Extract exif metadata
      -g, --gps             Extract, parse and convert to coordinates, GPS exif
                            metadata from images (if any)It works only with JPEG.
      -e, --ela             Extract, Error Level Analysis image,It works only with
                            JPEG. *BETA*
      -n, --nude            Detect Nudity, It works only with JPEG, *BETA*
      -d {md5,sha256,sha512,all}, --digest {md5,sha256,sha512,all}
                            Calculate perceptual image hashing
      -p {ahash,phash,dhash,whash,all}, --percentualhash {ahash,phash,dhash,whash,all}
                            Calculate hash digest
      -o OUTPUT, --output OUTPUT
                            Output directory path
      -s, --sqli            Keep SQLite file after the computation
      -t {jpeg,tiff}, --type {jpeg,tiff}
                            Select the image, this flag can be JPEG or TIFF, if
                            this argument it is not provided, imago will process
                            all the image types(i.e. JPEG, TIFF)

唯一必需的参数是-i，它是imago将从中开始搜索图像文件的基目录。此外，你还应指定至少一种类型的提取（即exif，data，gps，digest）。

## 示例

例1：

    
    
    $ imago -i /home/solvent/cases/c23/DCIM/ -o /home/solvent/cases/c23/ -x -s -t jpeg -d all
    
    
    -i path：基目录，imago将从中搜索图像文件；
    
    -o path：imago将使用提取的元数据保存CSV文件的输出目录；
    
    -x：imago将提取EXIF元数据；
    
    -s：处理后不会删除临时SQLite数据库；
    
    -t jpeg：imago将仅搜索jpeg图像；
    
    -d all：imago将为jpeg图像计算md5，sha256，sha512。

例2：

    
    
    $ imago -i /root/Deskop/ -o /root/Desktop -x -g

![2.JPG](https://image.3001.net/images/20190413/1555111912_5cb11fe8bd24c.jpg!small)

## 特性

> 递归目录导航
>
> 文件 mtime（UTC）
>
> 文件 ctime（UTC）
>
> 文件 atime（UTC）
>
> 文件大小（字节）
>
> MIME 类型
>
> Exif 支持
>
> CSV 导出
>
> Sqlite 导出
>
> md5，sha256，sha512
>
> 错误级别分析（测试）
>
> 完整的 GPS 支持
>
> 裸露检测（测试）
>
> 感知图像哈希
>
> aHash
>
> pHash
>
> dHash
>
> wHash

 ***参考来源：[GitHub](https://github.com/redaelli/imago-forensics)，FB小编secist编译，转载请注明来自FreeBuf.COM**  

