## 背景

office套件已经成为大家日常办公必不可少的工具，丰富的文字编辑、演示文稿以及数据处理能力，无一不展示其强大的功能。然后随着形式的多样性，文件的保存和传输让office成为共享、协同的常用方案，而对于一些包含敏感数据的文件，当文件被有意或无意泄漏，可能就会对企业造成无法挽回的损失。本文将对word和excel文件的追踪方案进行探索，通过对文件植入URL，当文件被打开时，即可自动触发HTTP请求，从而获取IP等定位信息，间接降低敏感数据恶意扩散传播的风险。

## word文件追踪

对于word文件的追踪，首先打开word，新建文档的时候，会出现选择模板的界面：

![](https://image.3001.net/images/20200817/1597648897.png!small)

这里随便选择一个模板，例如这里的“做笔记”，然后直接保存为test.docx。这里要说明的一个知识点是，office文件本质上是一个压缩包，是有很多xml和一些其他类型文件打包成的，所以该docx是可以解压缩的，至于如何解压缩，Windows上多数可以直接解压，Mac上可以改一下后缀为test.rar，然后解压。解压之后一般都会看_rels、[Content_Types].xml、docProps、word。
这里不对文件展开来介绍了，有兴趣的可以自行了解，前三个文件(夹)基本都是本身的全局配置，office系列的文件这些基本都一致，而word文件夹就是针对docx特有的了，主要包含了整个word内容；查看_rels文件夹中，会发现有一个叫做settings.xml.rels的文件，用记事本打开后内容大致为：

    
    
    <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    
    <Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/attachedTemplate" Target="file:////Users/*****/Library/Containers/com.microsoft.Word/Data/Library/Caches/2052/TM10002086/做笔记.dotx" TargetMode="External"/></Relationships>

可以看出，这是创建文件夹时选用的模板配置文件，Target指向了一个本地路径，重点来了，我们嵌入的链接就是在这里做文章，office本身支持TargetMode为External的方式，也就是外部引用的方式，实际上不仅是本地路径，也可以是一个外部URL，并且这段引用是在文件打开后自动去解析寻找。这里就可以将它换成一个自己的“钓鱼”链接即可，然后重新打包成docx。这里出现的第一个问题就是：手动打包后，打开文件基本上都会弹窗告警文件损坏之类的，其实是解压后，目录生成了一些隐藏文件不干净导致的，用程序自动化做，一般不会有问题；第二个问题就是，这里是用固定的模板格式修改的，对于那些任意格式的docx文件，如何利用这种方式嵌入呢？

## 任意内容的docx文件嵌入

想要修改任何文件都能达到这样的效果，就要对模板引用的生成原理要了解，其实上面所看到的是模板的配置文件，但是并没有看到对应的引用文件，不引用它，是不会执行的，甚至会打开报错。这里就要打开word/settings.xml文件，可以在xml中找到

    
    
    <w:attachedTemplate r:id="rId1"/>

这里就是引用了刚刚的模板，其中attachedTemplate就是模板类型，rId1就是编号，是和上述的文件中Id对应的。所以要对docx文件进行URL嵌入，对这两个文件进行编辑就可以了，当然，实际情况中，这两个文件有可能是不存在的，需要自己创建，也有可能已经存在了，包含了rId1的数据，这时候就要依次使用rId2等其他的Id号了。

## excel文件追踪

对于Excel的文件追踪方式，首先想到的是word版的方案，可惜的是，虽然同样可以按照模板创建文件，但是并不支持嵌入链接。那么有没有比较好的方案能够实现xlsx文件同样的效果呢？下面就介绍一个“不完美”的方案。

首先还是创建一个新文件，为了演示，就不写数据了，直接插入一张图片，效果如下：

![](https://image.3001.net/images/20200817/1597649170.png!small)

保存文件后，同样的方式，解压xlsx文件，不出意外的话得到_rels、[Content_Types].xml、docProps、xl。这里可以看到，和docx文件唯一不同的就是xl文件夹，这里就是excel文件的核心内容。寻找线索之前，可以大体上能确定一个逻辑，就是应该存在两个关键配置文件，其中一个的内容引用了图片资源的位置，另一个文件则是引用了这个配置文件。根据这个思路，首先可以明确看到图片资源在media文件夹中，然后根据文件名搜索可以定位到drawings/_rels/drawing1.xml.rels文件中，内容如下：

    
    
    <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    
    <Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/image1.png"/></Relationships>

不难想到，在Target="../media/image1.png"这再追加一个属性TargetMode="External"，代表外部链接，然后修改"../media/image1.png"为钓鱼URL，重新打包后就可以发现，实现了追踪效果。此时出现了同样的问题，如何在任何xlsx文件下都可以支持，并且多了一个问题，如何隐藏这个图片？

## 任意内容的xlsx文件嵌入

接下来就是寻找如何引用上述的配置文件了。首先基本可以猜测到，drawings文件夹一定是图片相关的资源配置，除了刚说到的.rels文件，另一个就是drawing1.xml，打开可以内容基本上就是该图片的属性了，包括大小、位置、名称等数据，另外就是引用了关系：

    
    
    <a:blip xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" r:embed="rId1"/>

同理，rId1对应之前的配置文件；然后就是相同的方式，可以发现文件worksheets/sheet1.xml和worksheets/_rels/sheet1.xml.rels，都存在引用相关配置文件信息，根据这4个文件，就可以自定义生成xlsx的追踪方案。当然，实际情况中，也存在一些问题，首先这些文件都是不一定存在的，不存在的话，需要创建，如果存在，还需要注意rId的序号，因为可能存在其他的图片资源引用；关于怎么隐藏这个图片，目前还没有很好的方式，虽然在drawing1.xml配置中可以设置隐藏属性，但是试过之后，发现隐藏的图片不会在打开文件时自动执行，这也就失去了意义，所以目前可行的方案就是将该图片设置为长宽都是0的格式，并同时将位置放在最左上角，这样就可以间接达到隐藏的目的。最终效果如下：

![](https://image.3001.net/images/20200817/1597649594.png!small)

如果该图片被选中，就会显示很小的一个标记，当然不被选中的情况，是看不出来的。

## office文件暗水印

有网络请求的地方，往往是不稳定的，所以除了能够追踪文件的打开路径，还需要配合暗水印来辅助溯源。对于office文件的暗水印，有很多种方式，根据前文说的方案思路，不难看出，在很多配置文件中，其实是可以插入字符串的，例如直接在插入的链接中追加参数用来标记；或者xlsx中的图片名称属性写入一串暗水印；或者直接在文件属性中添加字符串等等，这里先介绍下文件属性。

![](https://image.3001.net/images/20200817/1597649812.jpg!small)

如图所示可以看出，office文件的属性显示了一些固定信息，暗水印的添加可以直接将字符串加密后写到属性里，好处就是抗修改、另存为比较强，坏处就是容易被发现。后来经过研究发现，有一种自定义属性的方式可以对其进行强化，原理就是office的属性其实并不是固定的，除了图中的常见属性，还支持自定义，名称和值都可以自己写，并且在查看属性中，并不展示这些自定义值，这样就让暗水印更加隐蔽了。具体方式就是在解压后的docProps文件夹中，新建一个custom.xml文件，内容可以参考：

    
    
    <?xml version='1.0' encoding='UTF-8' standalone='yes'?>
    
    <Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/custom-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
    
    <property fmtid="{D5CDD505-2E9C-101B-9397-08002B2CF9AE}" pid="2" name="这里是自定义属性名">
    
    <vt:lpwstr>这里是属性对应的值</vt:lpwstr>
    
    </property>
    
    </Properties>

同样需要在其他配置文件中进行引用，这里就不展开了，可以参考同级目录下的app.xml文件的引用关系。

## 总结

office的文件追踪本质上就是利用office自身的特性来做文章，深入理解它的结构之后，能更好地实现方案。虽然本文的方案可以满足基本需求，但是仍然存在很多问题待解决，数据安全保护还需要大家持续去研究新的技术。

