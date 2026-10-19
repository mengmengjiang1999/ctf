![eab7322a-1c42-11e7-96f3-dbc772da5f10.png](https://image.3001.net/images/20200409/1586373996_5e8e256ce17db.png!small)  

## 关于亚马逊AWS S3

Amazon
S3[简单存储服务]是互联网中的一项云存储服务，用户如需要上传数据（照片、视频、文档等），首先要在AWS的一个区域中创建一个Bucket，然后便可以将任意数量的对象上传到Bucket中了。在实现方面，Bucket和Object都属于资源类型，Amazon
S3提供了API来帮助用户对这些资源进行管理。

## Sandcastle

Sandcastle是一款针对AWS S3 Bucket的Python枚举脚本，该项目的灵感来源[
_@nickelser_](https://github.com/nickelser)在HackerOne上的谈话。目前，开发者已对Sandcastle进行了优化，并发布了Sandcastle的Python版本，可以实现通过脚本来枚举AWS
S3 Bucket，而Sandcastle的前身就是bucketCrawler。

这个脚本可以接收目标名称来作为`stem`参数（例如`shopify`），并通过Bucket名称排列文件来实现枚举功能，具体如下所示：

    
    
    -training
    
    -bucket
    
    -dev
    
    -attachments
    
    -photos
    
    -elasticsearch
    
    [...]

## 工具下载

广大研究人员可以通过使用下列命令来将项目源码克隆至本地：

    
    
    git clone https://github.com/0xSearches/sandcastle.git

## 工具使用

将项目源码克隆至本地之后，在命令行窗口中切换到本地项目目录，然后使用目标名称和输入文件来运行`sandcastle.py`。

接下来，该脚本将会识别匹配的Bucket排序，并测试目标读取访问权限。

### 工具帮助信息如下：

    
    
    usage: sandcastle.py [-h] -t targetStem [-f inputFile]
    
    arguments:
    
      -h, --help            show this help message and exit
    
      -t targetStem, --target targetStem
    
                            Select a target stem name (e.g. 'shopify')
    
      -f inputFile, --file inputFile
    
                            Select a bucket permutation file (default: bucket-    
                            names.txt)

![图片1.png](https://image.3001.net/images/20200409/1586374066_5e8e25b27bc5e.png!small)

## 状态码和测试

 **状态码** ****|  **定义** ****|  **描述** ****  
---|---|---  
404|  Bucket Not Found| 没有找到待分析的目标Bucket  
403| Access Denied| 通过CLI分析潜在目标，访问被拒  
200| Publicly Accessible| 通过CLI分析潜在目标，公开可访问  
  
## AWS CLI命令

下面给出的是部分常用的AWS CLI命令：

### 枚举文件：

    
    
    aws s3 ls s3://bucket-name

### 下载文件：

    
    
    aws s3 cp s3://bucket-name/<file> <destination>

### 上传文件：

    
    
    aws s3 cp/mv test-file.txt s3://bucket-name

### 删除文件：

    
    
    aws s3 rm s3://bucket-name/test-file.txt

## 项目地址

Sandcastle：【[ _GitHub传送门_](https://github.com/0xSearches/sandcastle)】

 *** 参考来源：[
_0xSearches_](https://github.com/0xSearches/sandcastle)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

