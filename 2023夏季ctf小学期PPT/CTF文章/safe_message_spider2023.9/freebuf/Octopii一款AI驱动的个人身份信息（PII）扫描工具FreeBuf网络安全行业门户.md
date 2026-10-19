![](https://image.3001.net/images/20221204/1670158450_638c9872b5e5549f96a3d.png!small)

## 关于Octopii

Octopii是一款功能强大的AI驱动的个人身份信息（PII）扫描工具，可以帮助广大研究人员在一个目录中扫描各种和个人身份信息（PII）相关的图片资源，比如说身份*证信息、护照、照片和签名等等。

## 工作机制

Octopii使用了Tesseract的OCR和Keras的CNN模块来检测各种形式的可能会发生泄漏面临安全风险的个人身份信息。该工具通过下列步骤实现其功能：

### 1、导入和清理图片资源

图像通过OpenCV导入，并进行清理、去扭斜和旋转以进行扫描。

### 2、执行图片分类

扫描图像的特征，如ISO/IEC 7810规格、颜色、文本位置、照片、全息图等，这一步通过传递图像并将其与训练模型进行比较来完成。

### 3、光学字符识别（OCR）

作为一种最终验证方法，扫描图像中的某些字符串，以验证模型的准确性。

扫描的准确性可以通过输出中的置信分数来确定。如果满足上述所有条件，则返回100.0分。

为了训练模型，还可以将数据输入model_generator.py脚本并使用新改进的h5文件来进行数据处理。

## 工具下载

由于该工具基于Python 3开发，因此广大研究人员首先需要在本地设备上安装并配置好Python 3环境。接下来，使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/redhuntlabs/Octopii.git

接下来，使用pip命令和项目提供的requirements.txt文件来安装该项目所需的依赖组件：

    
    
    cd Octopii
    
    pip install -r requirements.txt

然后使用下列命令安装Tesseract帮助工具（Ubuntu/Debian）：

    
    
    sudo apt install tesseract-ocr -y

安装完成后，可以使用下列命令运行Octopii：

    
    
    python3 octopii.py <location to scan> <additional flags>

Octopii当前支持本地扫描和S3目录扫描，可以通过输入目标URL地址或路径来进行扫描。比如说：

    
    
    python3 octopii.py pii_list/

## 工具使用样例

    
    
    owais@artemis ~ $ python3 octopii.py pii_list
    
     
    
    Not a valid image format: pii_list/aadhaar/aadhaar-8.gif
    
     
    
    [
    
        {
    
            "asset_type": "Bank",
    
            "confidence": 100.0,
    
            "file_name": "passbook",
    
            "extension": "jpeg",
    
            "path": "pii_list/bank/passbook.jpeg"
    
        },
    
        {
    
            "asset_type": "Photo",
    
            "confidence": 99.98,
    
            "file_name": "IMG-20200331-WA0037",
    
            "extension": "jpg",
    
            "path": "pii_list/photos/IMG-20200331-WA0037.jpg"
    
        },
    
        {
    
            "asset_type": "PAN",
    
            "confidence": 100.0,
    
            "file_name": "pan-7",
    
            "extension": "jpg",
    
            "path": "pii_list/pan/pan-7.jpg"
    
        },
    
        {
    
            "asset_type": "Aadhaar",
    
            "confidence": 97.31,
    
            "file_name": "aadhaar-14",
    
            "extension": "jpg",
    
            "path": "pii_list/aadhaar/aadhaar-14.jpg"
    
        }
    
    ]

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/redhuntlabs/Octopii/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **Octopii** ：【[ _GitHub传送门_](https://github.com/redhuntlabs/Octopii)】

