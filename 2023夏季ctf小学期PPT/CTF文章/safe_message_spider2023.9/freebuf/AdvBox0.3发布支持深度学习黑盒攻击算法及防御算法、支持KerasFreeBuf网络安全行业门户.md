#
![image.png](https://image.3001.net/images/20180929/1538197586_5baf08521ace3.png!small)  

AdvBox是一款支持PaddlePaddle、Caffe2、Keras以及TensorFlow的针对AI模型生成对抗样本的工具包。对抗样本是深度学习领域的一个重要问题，比如在图像上叠加肉眼难以识别的修改，就可以欺骗主流的深度学习图像模型，产生分类错误，指鹿为马，或者无中生有。这些问题对于特定领域（比如无人车、人脸识别）会产生严重的后果，尤为重要。百度安全实验室研发了AdvBox，它能够为安全工程师研究模型的安全性提供极大的便利，免去重复造轮子的精力与时间消耗。AdvBox可以高效地使用最新的生成方法构造对抗样本数据集用于对抗样本的特征统计、攻击全新的AI应用，加固业务AI模型，为模型安全性研究和AI应用提供重要的支持。AdvBox今天发布0.3版本，支持常见的黑盒攻击算法以及防御算法，新增对Keras平台的支持，项目地址为：

    
    
    https://github.com/baidu/AdvBox

  
  

 **对抗样本简介**

对抗样本(AdversarialExample
Attack)是机器学习模型的一个有趣现象，攻击者通过在源数据上增加人类难以通过感官辨识到的细微改变，但是却可以让机器学习模型接受并做出错误的分类决定。一个典型的场景就是图像分类模型的对抗样本，通过在图片上叠加精心构造的变化量，在肉眼难以察觉的情况下，让分类模型产生误判。开发者可以轻松基于AdvBox对经典的人脸识别模型进行黑/白盒攻击，把比尔盖茨识别为乔丹。

![image.png](https://image.3001.net/images/20180929/1538197641_5baf088988d8c.png!small)  

 **What’s New**

 **  
**

>  **支持黑盒攻击算法**

  

对抗样本按照攻击需要的条件和方式可以区分为白盒攻击、黑盒攻击和物理世界攻击，其中白盒攻击需要对模型结构深入了解，知道模型的结构和各层的参数，可以计算梯度。

  
![image.png](https://image.3001.net/images/20180929/1538197653_5baf08954c1f4.png!small)  

黑盒攻击完全把模型当做一个黑盒，根据一定的算法，不断根据输出的反馈调整输入数据。黑盒攻击相对白盒攻击，攻击难度更大。

  
![image.png](https://image.3001.net/images/20180929/1538197662_5baf089e89c45.png!small)  

AdvBox从0.3版本开始支持黑盒攻击算法，目前已经支持的列表如下：

  * Single Pixel Attack

  * Local Search Attack

  

>  **支持防御算法**

  

安全攻防通常都是相辅相成，黑产使用AI的速度已经大大超出我们的想象，目前公开的案件中，已经出现了多起使用AI技术进行网络攻击的案例，比如使用图像识别模型破解图形验证码，使用智能客服技术进行自动化网络欺诈。在对抗样本领域亦是如此，AdvBox新增了通用加固算法，方便开发者快速加固AI模型，目前已经支持的列表如下：

  * Feature Fqueezing

  * Spatial Smoothing

  * Label Smoothing

  * Gaussian Augmentation

  * Adversarial Training

  

>  **支持Keras**

  

Keras是一个高层神经网络API，由纯Python编写而成并基于Tensorflow、Theano以及CNTK后端。相对于其他深度学习平台，完成相同的功能，Keras的语法更加简洁，开发效率更高。为了进一步降低使用门槛，AdvBox从0.3版本开始支持Keras平台。

以使用Keras自带的ResNet50模型进行白盒攻击为例，设置为预测模式，加载测试图片。

#设置为测试模式

keras.backend.set_learning_phase(0)

model = ResNet50(weights=modulename)

img = image.load_img(imagename, target_size=(224, 224))

original_image = image.img_to_array(img)imagedata =
np.expand_dims(original_image, axis=0)

对比生成的对抗样本和原始图像的差别。

    
    
    adversary_image=np.copy(adversary.adversarial_example)
    
    
    #强制类型转换 之前是float 现在要转换成uint8
    
    
    #BGR -> RGB
    
    
    adversary_image=adversary_image[:,:,::-1]
    
    
    adversary_image = np.array(adversary_image).reshape([224,224,3])
    
    
    original_image=np.array(original_image).reshape([224, 224, 3])
    
    
    show_images_diff(original_image,adversary_image)

实际运行代码，原始图像和对抗样本的差别如下图所示。

![image.png](https://image.3001.net/images/20180929/1538197721_5baf08d9bf6bf.png!small)  

>  **新增使用案例**

  

为了进一步降低学习成本，AdvBox提供大量的学习教程。  

  * 示例1：白盒攻击基于MNIST数据集的CNN模型

  * 示例2：白盒攻击基于CIFAR10数据集的ResNet模型

  * 示例3：白盒攻击caffe下基于MNIST数据集的LeNet模型

  * 示例4：黑盒攻击基于MNIST数据集的CNN模型

  * 示例5：使用FeatureFqueezing加固基于MNIST数据集的CNN模型

  * 示例6：使用GaussianAugmentation加固基于MNIST数据集的CNN模型

  

 **结语**

AdvBox为研究者研究AI模型的安全性提供极大的便利，免去重复造轮子的精力与时间消耗，可以高效地使用最新的生成方法构造对抗样本数据集用于对抗样本的特征统计、攻击全新的AI应用，加固业务AI模型，为模型安全性研究和应用提供重要的支持。AdvBox从0.3版本开始支持Keras平台，支持常见的黑盒攻击算法以及防御算法，进一步降低了使用门槛，助力AI安全。

