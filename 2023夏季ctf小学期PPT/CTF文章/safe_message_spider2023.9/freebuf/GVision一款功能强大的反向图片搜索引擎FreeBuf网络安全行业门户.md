![](https://image.3001.net/images/20230526/1685064464_64700b109cf7823fd945f.png!small)

## 关于GVision

GVision是一款功能强大的反向图片搜索工具，该工具使用了Google Cloud Vision
API来帮助广大研究人员从图片资源中检测地标和网络实体，以此来快速轻松地从图片资源中收集有价值的信息。

## 关于Google Cloud Vision API

Google Cloud Vision
API是一种基于机器学习的图像分析服务，为开发人员提供深度了解图像内容的能力。值得一提的是，该服务可以检测图像中的物体、人脸、文本和Logo等多种内容。

## 工具要求

在使用该工具之前，我们需要获取一个Google Cloud Vision API密钥，具体步骤如下：

> 1、访问[ _Google_ __ _Cloud平台终端_](https://console.cloud.google.com/)；
>
> 2、创建一个新的项目，或选择一个现有项目；
>
> 3、为你的项目启用Cloud Vision API；
>
> 4、创建一个服务账号，并下载JSON格式的私钥文件；
>
> 5、通过点击侧边栏的“Upload a config file”按钮将JSON格式的密钥文件上传即可；

## 工具安装

由于该工具基于Python开发，因此我们首先要在本地设备上安装并配置好Python环境。

接下来，广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/GONZOsint/gvision.git

接下来，切换到项目目录中，并使用pip命令和项目提供的requirements.txt安装该工具所需的其他依赖组件：

    
    
    pip install -r requirements.txt

## 工具运行

我们可以直接在本地终端中运行下列命令来启动GVision：

    
    
    streamlit run gvision.py

## 工具使用

该工具的使用非常简单，操作步骤如下：

> 1、通过点击侧边栏的“Upload a config file”按钮将JSON格式的Google Cloud Vision API密钥文件上传；
>
> 2、密钥上传完成后，应用程序将自动使用密钥完成API的身份验证；
>
> 3、点击“Choose an image”按钮上传一个JPG、JPEG或PNG格式的图片；
>
> 4、等待应用程序完成图片分析，应用程序将检测图片中的地标和Web实体，并在地图中显示它们；
>
> 5、选择不同的程序选项，就可以查看检测到的数据详情了；

注意：如需将应用程序重置到默认状态或清除上传的图像和生成的结果，可以直接点击应用程序的“Reset app”按钮即可。

## 工具使用演示

 **演示视频** ：【[ _点我观看_](https://user-images.githubusercontent.com/37483725/228700363-cc0d8131-4134-4f37-918e-1a342dd22b83.mp4)】

## 项目地址

 **GVision** ：【[ _GitHub传送门_](https://github.com/GONZOsint/gvision)】

## 参考资料

> [ _https://console.cloud.google.com/_](https://console.cloud.google.com/)
>
> [
> _https://cloud.google.com/vision/docs_](https://cloud.google.com/vision/docs)
>
> [
> _https://cloud.google.com/vision/pricing_](https://cloud.google.com/vision/pricing)

