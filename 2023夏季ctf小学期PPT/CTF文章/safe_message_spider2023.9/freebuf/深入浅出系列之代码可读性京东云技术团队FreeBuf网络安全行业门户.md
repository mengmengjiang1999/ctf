这是“深入浅出系列”文章的第一篇，主要记录和分享程序设计的一些思想和方法论，如果读者觉得所有受用，还请“一键三连”，这是对我最大的鼓励。

#  **一、老生常谈，到底啥是可读性**

一句话：见名知其义。有人说好的代码必然有清晰完整的注释，我不否认；也有人说代码即注释，是代码简洁之道的最高境界，我也不否认。但我都不完全接受，如果照搬前者，有人会在每个方法、每个循环、每个判断都添加大量注释，对于一个表达不严谨的coder来说，代码与汉字可能词不达意；而且，一旦代码逻辑发生变化，注释改不改？对于后者，英语水平可能也就是个半吊子，动词名词不区分，真能做到代码即注释的有多少人？

#  **二、骂归骂，总归要硬着头皮干**

先来举个简单例子：

    
    
    publicStepExitEnumdoExecute(StepContextstepContext)throwsException{StringtargetFilePath =this.getOriginFilePath(stepContext.getJobContext());//获取目标路径FiletargetDir =newFile(targetFilePath);if(!targetDir.exists()){targetDir.mkdirs();//如果不存在目录则创建}StringencryptedFilePath =this.getEncryptedFilePath(stepContext.getJobContext());//获取加密文件路径StringfileName =this.getFileName(stepContext);//获取文件名File[]encryptedFiles =newFile(encryptedFilePath).listFiles(this.buildFilenameFilter(fileName));//过滤文件FileEncryptordencryptor =this.buildFileEncryptor(stepContext);//创建FileEncryptorStream.of(encryptedFiles).forEach(encryptFile ->{FiletargetFile =newFile(targetFilePath,encryptFile.getName());dencryptor.invoke(encryptFile,targetFile);//解密文件});returnStepExitEnum.CONTINUING;}

这种代码很常见，耐着性子其实也容易看懂：创建目录->读取加密文件->解密文件，就当前来说其实满足了业务需求也就可以了，但不够优雅，从长期来讲，这会产生bad
smell，首先，“如果不存在目录则创建”、“获取文件名”这类注释有何意义？有可能这是coder当时的方案思路，但这里真的需要吗？它确确实实影响我的注意力了，但我没有获取到任何有价值信息；其次，若想要理解`doExecute`这个方法的目的，必须通读代码，而我只是想知道它做了什么事；最后，这个方法如果某一行出问题了，那么影响范围是整个业务流程。

如果后期需要改动，大部分人可能会增加条件判断，或是在后面继续追加代码实现，最后会导致越来越难以阅读，这其实也就是“能运行就不要动它”这个梗的根源了，因为没人能读明白它到底做了什么，但又不得不改，同时可能伴随着“口吐芬芳”。

#  **三、意识先行，从一行做起**

那么到底该如何做呢？下面是我的一个例子：

    
    
    publicStepExitEnumdoExecute(StepContextstepContext)throwsException{initTempFilePath(stepContext);File[]encryptedFiles =findEncryptedFiles(stepContext);dencryptFiles(encryptedFiles,stepContext);returnStepExitEnum.CONTINUING;}

先不论具体实现细节，是不是一眼看过之后就了解`doExecute`做了什么事？这个方法的确没有任何注释，是否影响阅读？其实我做的只是把先前的代码重新归类，分别放到了三个方法中，核心实现还是原本的代码，没有改动，现在阅读起来是不是顺畅了许多？

通读代码后我发现其实只做了三件事：创建目录、读取加密文件、解密文件，这是最核心的三个步骤，把它抽象出来，独立为方法，既表达了逻辑功能，也清晰阅读，还可以缩小影响范围，今后哪里有问题改哪里，不需要再通读代码了。

#  **四、回到主题，再说可读性**

###  （1）抽象，合理的业务逻辑抽象

“一个方法只应该做一件事”，想必很多人听过类似的表述，听起来简单做起来难，怎么定义“只做一件事”？这件事的边界是什么？这就依赖coder对业务逻辑、对功能实现的深入理解和合理抽象，这才能清晰的区分出各个功能的边界，或者说是如何定义这件“事”。

没有基于业务的合理抽象，硬生生地写了几个方法，你会发现这几个方法“藕断丝连”，一个方法的参数变化总会影响到另一个方法，很难将一个方法单拎出来应用在其他场景，一处改，处处改，这时候就要考虑，方法抽象的是否合理？

合理的抽象，从功能角色、职责划分上就很清晰，有了这个基础，才能清晰的编写业务逻辑代码，而不是堆砌各种条件判断和循环，同时带着两条斜杠和注释，这是可读性的基础。

### （2）各司其职，职责单一

一个方法只做一件事，扩展到一个类也如此，职责单一，归根结底还得基于合理的抽象，所以，它其实是抽象的一种具体体现，二者总是相辅相成。

### （3）命名规范

这也是老生常谈了，但真正做到的coder其实不多，类名、方法、变量的命名规则其实很有讲究，但这不是本文的主题，不多赘述，类名用名词，方法名用动词，因为类表述的是做什么事，而方法名表述的是如何做，规范的命名和正确的词法，这是编码的基础功底，这会有助于他人阅读代码，当然也是为什么我们读spring源码会感觉顺畅，而读同事写的业务代码却很蹩脚的原因，我们太过于强调spring的IOC了，却忽略了最基础的东西。

### （4）关键注释

注释不能少，但也不应该每个方法、每个判断、每个循环到处都是`//`和`/*`，毕竟代码是主体不是注释，而且这样还会带来隐性的工作量问题：代码修改，注释也必须修改。所以好的注释不是多，是关键。例如`java.util.HashMap`类的注释上会告诉你线程安全问题：

> Note that this implementation is not synchronized.

这是很关键的信息，所以注释要给出关键性的、使用上注意的事项，不在于多。

代码可读性其实是一个比较宽泛的问题，也是一个老生常谈的问题，随着编码经验积累，在不同职业阶段，我们对可读性都会有不同的理解和认识，本文从我自己的角度和经验，讨论了一些比较浅的理解，如何写出易读、易懂的优秀代码，可能是我们coder永远追寻的目标之一，即使它没有终点。

> 作者：京东科技 张宇
>
> 来源：京东云开发者社区 转载请注明来源

