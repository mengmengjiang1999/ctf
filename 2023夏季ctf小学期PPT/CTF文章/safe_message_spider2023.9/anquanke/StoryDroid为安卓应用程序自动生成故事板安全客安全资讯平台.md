# StoryDroid：为安卓应用程序自动生成故事板

阅读量 **165619**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-10-13 10:31:46

 **x**

##### 译文声明

本文是翻译文章，文章原作者 Sen Chen, Lingling Fan, Chunyang Chen, Ting Su, Wenhe Li, Yang
Liu, Lihua Xu，文章来源：ieeexplore.ieee.org

原文地址：<https://ieeexplore.ieee.org/document/8812043﻿>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t0131ddc65b14f84381.jpg)

最近对Android的自动化测试工具开发感兴趣，故最近在考研期间可能会带来一些我认为有趣的关于Android自动化测试工具的论文翻译，啊，考研太累了啊 >
<

论文作者：Sen Chen, Lingling Fan, Chunyang Chen, Ting Su, Wenhe Li, Yang Liu, Lihua
Xu

论文原文链接：<https://ieeexplore.ieee.org/document/8812043>

## 0x0 思维导图

这里是我自己整理的一个大概的思维导图，各位师傅可以先看看

![](https://p5.ssl.qhimg.com/t0161ba17b48a6afbc7.png)

## 0x1 摘要

​
移动应用程序现在无处不在。在开发一个新的应用程序之前，开发团队通常会花很大的精力来评估许多具有类似目的的现有应用程序。审查过程非常重要，因为它能够降低市场风险，并为应用开发提供灵感。然而，在开发团队中，通过不同的角色(如产品经理、UI/UX设计师、开发人员)手动探索数百个现有的应用程序可能是无效的。例如，很难在短时间内完全探索应用程序的所有功能。受电影制作中的故事板概念的启发，我们提出了一个StoryDroid系统，用于自动生成Android应用的故事板，并协助不同角色高效地审核应用。具体来说，StoryDroid提取活动转换图，并利用静态分析技术来呈现UI页面，以可视化呈现的页面中的故事板。UI页面和相应实现代码(如布局代码、活动代码、方法层次结构)之间的映射关系也提供给用户。我们的综合实验证明了StoryDroid是有效的，确实有助于应用程序开发。StoryDroid的输出支持一些潜在的应用方向，比如推荐UI设计和布局代码。

**关键词：Android app，Storyboard，Competitive analysis，App review**

## 0x2 介绍

​
现在，移动应用已经成为访问互联网以及执行日常任务（如阅读、购物、银行和聊天）的最流行方式。与传统的桌面应用不同，移动应用通常是在上市压力下开发的，并面临着激烈的竞争——超过380万个安卓应用和200万个iPhone应用正在努力争取在Google
Play和苹果应用商店这两个主要的移动应用市场上获得用户。

​
因此，对于应用开发者和公司来说，对具有类似目的的现有应用进行广泛的竞争分析至关重要。这种分析有助于了解竞争对手的优势和劣势，在开发前降低市场风险。具体来说，它确定了常见的应用功能、设计选择和潜在客户。此外，研究类似的应用程序还有助于开发人员更深入地了解实际的实现，因为交付商业应用程序可能是耗时和昂贵的。

​
通常情况下，为了完成上述分析，科技公司的自由开发者或产品经理（PM）必须从市场下载应用，安装在移动设备上，反复使用它们来获得自己感兴趣的部分。然而，这种人工探索可能是艰苦的和无效的。例如，如果一家科技公司计划开发社交媒体应用程序，谷歌Play上的245个类似应用程序将受到审查。手动分析它们是非常困难的——注册账户，在需要时输入特定信息，并记录必要的信息（例如，主要功能是什么，应用页面是如何连接的）。此外，商业应用程序可能过于复杂，无法在合理的时间内手动揭示所有功能。对于UI/UX设计师来说，同样的探索问题仍然存在，当他们想从类似的应用设计中获得灵感时。此外，应用程序中大量的用户界面（UI）屏幕也让设计师很难理解页面之间的关系和导航。对于想要从类似应用中获得灵感的开发人员来说，很难将UI屏幕与相应的实现代码链接起来——代码可以在静态布局文件中提取，也可以在一大块功能代码中提取。

​
受电影行业中的故事板概念的启发，我们打算生成一个应用程序的故事板来可视化它的关键应用行为。具体来说，我们使用活动（即UI屏幕）来描述故事板中的“场景”，因为活动代表了应用在全屏窗口中的直观印象，是用户交互最常用的组件。图1为Facebook（最受欢迎的社交媒体应用之一）的故事板图，其中包括带有UI页面的活动转换图(A
TG)、详细的布局代码（例如，静态和动态）、每个活动的功能代码(（ctivity code）和每个活动内的方法调用关系（method
Hierarchy）。基于这个故事板,
pm可以在短时间内审核大量的app，并在自己的app中提出更有竞争力的功能。UI设计师可以获得最相关的UI页面作为参考。开发人员可以直接参考相关代码，提高开发效率。

![](https://p4.ssl.qhimg.com/t01a519324f8fcf784f.png)

​
然而，生成故事板是有挑战性的。首先，由于静态分析工具的限制，ATG通常是不完整的。其次，为了识别所有的UI页面，纯静态方法可能会错过动态呈现的部分UI（见第三节），而纯动态方法可能无法到达应用中的所有页面，特别是那些需要登录的页面。第三，混淆的活动名称缺乏相应功能的语义，使故事板难以理解。

​ 为了克服这些挑战，我们提出了一个STORYDROID系统，它可以自动生成应用的故事板，主要分为三个阶段：(1)Activity transition
extraction，从apks中提取ATG，特别是片段和内部类中的转换关系，使ATG更加完整。(2)
UI页面呈现，首先提取每个UI页面的动态组件（如果有的话），并将其嵌入到相应的静态布局中。然后它会基于静态布局文件静态地呈现每个UI页面。(3)语义名推断，通过将布局层次结构与我们数据库中构建的4426个开源应用程序进行比较，推断混淆活动名称的语义名。通过这些分析，STORYDROID为从不同的角度探索和理解一个应用提供了一个系统的解决方案。

​
我们从以下两个方面共100个应用（50个开源应用和50个闭源应用）对STORYDROID进行评估：（1）每个阶段的有效性评估；（2）可视化输出的有用性评价。实验结果表明，STORYDROID在提取活动转换，特别是片段和内部类的活动转换方面是有效的。在开源应用和闭源应用上，STORYDROID提取的活动转换几乎是目前最先进的ATG提取工具（即IC3）的2倍。此外，STORYDROID在开源应用（平均87%）和闭源应用（平均74%）的活动覆盖率上显著优于最先进的动态测试工具（即STOAT）。平均而言，我们渲染的图像与STOAT动态获得的图像相比，相似度达到84%。STORYDROID可以推断出语义名，准确率高达92%。此外，用户研究表明，在STORYDROID的帮助下，与没有STORYDROID的探索相比，活动覆盖率有了显著的提高，用户可以更准确、高效地找到给定UI页面的布局代码。

​ 除了基本的有用性，我们还讨论了几个额外的基于STORYDROID的输出的实际应用。例如，推荐UI设计和布局代码和指导应用程序的回归测试。

​ 综上所述，我们做出了以下贡：

  * 这是第一个自动生成Android应用故事板的研究工作。它帮助包括PMs、设计师和开发人员在内的应用程序开发团队快速对其他类似应用程序有一个清晰的概述
  * 我们提出了一种新的算法来提取相对完整的ATG，静态渲染UI页面，并推断混淆后应用的活动名称。这些技术贡献对于开源和闭源的Android应用程序都是通用的
  * 我们的实验不仅证明了生成的故事板的准确性，而且还证明了我们的故事板在帮助应用程序开发方面的有用性
  * 这是构建大规模应用故事板数据库的基础工作，因为整体方法是基于静态程序分析的。这样的数据库可以扩大当前移动应用研究的视野，使许多未来的工作，如提取应用的共性，推荐UI代码，设计，并指导应用测试

## 0x3 动机场景

​
我们使用针对Android应用的STORYDROID，根据开发团队中的不同角色，详细描述了典型的应用审查过程。Eve是一家IT公司的项目经理。她的团队计划开发一款Android社交应用。为了提高所设计应用的竞争力，她从谷歌Play
Store中输入关键词(如social, chat)，搜索数百个类似应用(如Facebook, Instagram,
Twitter)。然后她将这些应用的所有URL输入到STORYDROID, STORYDROID会自动下载所有这些应用，使用谷歌Play
API。STORYDROID进一步生成所有这些应用的故事板（如图1），并将其呈现给Eve。通过观察这些故事板，她很容易了解这些应用程序的故事情节，并发现这些应用程序的共同特点，如注册、搜索、设置、用户资料、发帖等。基于这些共同功能，Eve想出了一些独特的功能，将自己的应用与现有应用区分开来。

​ Alice作为一名UI/UX设计师，需要根据Eve的要求设计UI页面。通过我们的STORYDROID,
Alice不仅可以很容易地了解到相关应用的UI设计风格，还可以很容易地了解到应用内部不同屏幕之间的交互关系。然后，Alice就可以根据别人的应用开发自己的应用的UI和用户交互。

​
Bob是一名Android开发者，他需要基于Alice的UI设计开发相应的应用。基于Alice在现有应用中引用的UI设计，他也可以在STORYDROID的帮助下引用该应用。通过点击故事板中每个活动的UI屏幕，STORYDROID返回相应的UI实现代码，无论它是用纯静态代码、动态代码还是混合代码实现的。要实现自己的UI设计，可以参考实现代码并根据他们的需求定制它。这种开发过程比从头开始要快得多。此外，Bob还可能对某个应用程序中的某些功能感兴趣。通过使用STORYDROID，他可以轻松地定位逻辑代码。

## 0x4 前言

​ 在本节中，我们简要介绍Android UI的概念，UI的布局类型和填充数据的特殊视图。

###  4.1 Android Activity和Fragment

​
Android应用中有四种类型的组件(即活动、服务、广播和接收器)。具体来说，Activity和Fragment渲染用户界面，是Android应用程序的可见部分。Activity是绘制用户可以交互的屏幕的基本组件。Fragment表示活动中UI的一部分，它将自己的UI贡献给某些活动。片段总是依赖于一个活动，不能独立存在。一个Fragment也可以在多个活动中重用，一个活动可能包含多个Fragment，基于屏幕大小，我们可以创建多面板UI，以适应不同屏幕大小的移动设备。

###  4.2 UI Layout

​
一个由Activity和Fragment呈现的用户界面需要一个UI布局文件来为用户绘制一个窗口。我们从更高的角度来看一下Android应用中的三种布局类型。图2显示了著名社交应用Twitter的登录UI页面，其中组件（如TextView）可以用三种不同的布局类型实现。

![](https://p1.ssl.qhimg.com/t0122bfb6b72a6c8787.png)

​ **静态布局**
，依赖于apk中的静态布局文件（即XML）。应用程序的UI页面由这些XML文件呈现。ViewGroup和View是UI布局文件中用户界面的基本元素。ViewGroup是一个包含其他ViewGroup和view的容器。GUI代码必须包含带有ViewGroup的根节点（例如，RelativeLayout和LinearLayout）。定义ViewGroup后，开发人员可以添加额外的视图（例如，EditText,
TextView）作为子元素，逐步构建定义页面布局的层次结构。GUI组件包含多个属性（例如，id，文本，宽度），如图2所示（第2-5行）。

​ **动态布局** ，它允许开发者在运行时使用Android
API实例化布局组件（例如，`addView()`）。开发人员可以在Java代码中创建组件并操作它们的属性，例如TextView。Java代码中的`TextView.setText(“Password”)`等效于布局文件中的`android:text=“Password”`，如图2（行7-11）所示。

​ **混合布局**
，它在静态布局文件中定义了一些默认组件。这些布局可以通过调用`LayoutInflater.inflate`来动态重用。如图2所示充气(第14-15行)。开发人员还可以操作已定义组件的属性。例如，他们可以在Java代码中修改`TextView`的内容。

​ 为了调查Android应用中使用的动态和混合布局的比例，我们从下载量最高的1万款谷歌Play应用中随机选择了1000款应用。我们使用特定的Android
api（例如，`addView()`和`inflate()`）来区分应用程序是否包含动态/混合布局类型来绘制UI页面。我们的研究结果显示，62.3%的应用程序使用动态/混合布局。如此频繁使用动态/混合布局的原因是，在它们的帮助下，视图从XML文件中的视图模型中分离出来，开发人员可以改变布局，而无需重新编译以适应应用程序的运行时状态。

###  4.3 Data Population

​ 适配器是AdapterView和视图的底层数据之间的桥梁。它还提供布局（例如ListView, GridView,
ViewPager）和数据，这些数据通常是从本地数据库或远程服务器加载的。适配器允许这些UI组件（例如ListView）提供可滚动项的列表以供选择。图3显示了适配器的示例。它实例化带有布局（ListView）的适配器，并将其与数据关联起来。然后通过适配器将数据显示在ListView中。AdapterView是用户界面布局的一部分，应该从源代码中提取，以便进行静态呈现。

![](https://p3.ssl.qhimg.com/t01dcdb4fb0f586edbe.png)

## 0x5 我们的方法

​ STORYDROID将一个apk作为输入，并输出该应用程序的可视化故事板（S）。图5显示了STORYDROID的三个主要阶段。(1)
过渡提取，它增强了ATG的提取能力。它增强了IC3的ATG提取能力，特别是对片段和内部类的提取。STORYDROID利用控制和数据流分析来获得相对完整的ATG。(2)
UI页面渲染，它将动态和混合布局转换为静态布局（如果需要），以渲染用户交互的UI页面。(3)
语义名称推断，它推断出混淆的语义名称，它通过布局比较为被混淆的活动名称推断出语义名称。

![](https://p1.ssl.qhimg.com/t01d824ea1fff7852fe.png)

###  5.1 过渡提取

![](https://p5.ssl.qhimg.com/t018b98d5f5cd8117d2.png)

![](https://p5.ssl.qhimg.com/t010eed3f33ef8e556e.png)

​ 在提取内部类和片段中的活动转换之前，我们先说明它们中的转换关系。图4 (a)是Vespucci地图编辑器的sub ATG。首先，activity
Main启动PrefEdititor，然后其中的PrefEditorFragment随着启动。PrefEditorFragment进一步启动AdvancedPrefEditor。具体来说，如图6所示，片段可以通过两种方式添加到一个活动中：

![](https://p1.ssl.qhimg.com/t010e81472b16d1a890.png)

（1）通过调用片段修改API，例如“`replace()`，”`add()`”和进一步利用“`fragmenttransaction
.commit()`”（第34行）来启动片段；

![](https://p0.ssl.qhimg.com/t01d761a3dc98a53e46.png)

（2）通过使用“`setAdapter`”（第6行）在特定视图中显示片段（例如，ViewPager）。PrefEditorFragment启动后，又开始一个新的活动（例如，AdvancedPrefEditor）。图4
(b)显示ADSdroid的sub
ATG，其中SearchPanel使用一个内部类SearchByPartName来处理耗时的操作，如图7所示。在完成任务后，它通过调用“`StartActivity()`”（第5行）来启动一个活动PartList。在这个例子中，我们的目标是提取活动转换:Main→PreEditor,
PreEditor→AdvancedPreEditor和SearchPanel→PartList。

​
算法1详细描述了ATG和渲染资源的提取，包括布局类型（即静态、动态或混合）和适配器映射关系。具体来说，它将apk作为输入，并输出活动转换图（`atg`）、适配器映射（`adapters`）和布局类型（`layout_type`）。我们首先将`atg`初始化为一个空集（第1行），它逐步存储活动转换。然后通过分析动态布局加载的存在性，生成给定布局的调用图（`cg`），得到布局类型API（2
– 3行）。对于每个类（`c`）中的每个方法（`m`），如果存在一个活动转换，我们首先通过分析Intent中的数据获得目标活动（`callee
act`）（行5-9）。如果方法（`m`）在内部类中，我们将外部类视为启动目标活动的活动，并将转换添加到atg（第10-12行）。以图4
(b)为例，我们将边缘SearchPanel→PartList添加到atg中。如果`m`在一个片段中，我们构造片段（`caller_frag`)和目标活动之间的关系（第13-14行）。注意，这个关系并不代表实际的活动转换，我们通过识别启动第19-22行片段的活动来优化它。这种关系用于A
TG构造和UI页面呈现。之后，我们通过合并片段关系来构造实际的活动转换来更新`atg`（第23行）。例如，在图4
(a)中，我们首先得到PrefEditorFragment→advedpreeditor和PrefEditor→PrefEditorFragment的关系，然后我们将它合并到PrefEditor→AdvancedPreEditor来表示实际的活动转换。对于既不在内部类中也不在片段中的方法`m`，我们从`m`开始向后遍历`cg`，以获得启动目标活动的所有活动（`callee
_act`），然后将它们添加到`atg`（第15-18行）。

​ 此外，为了补充需要使用不同类型的视图（如ListView, RecyclerView,
ViewPager）从数据提供者（如ContentProvider,
Preference）加载数据的UI布局，我们首先确定使用`Adapter`的方法并获得相应的视图类型（`view_type`）（第24-25行）。然后，我们利用适配器上的向后数据流分析来跟踪相应的布局文件，从而确定将嵌入以`view_type`显示的数据的布局/活动。我们将每个映射关系定义为一个元组——<activity、view_type、layout>并将它们保存在用于UI渲染的`adatpers`中。以图3为例，我们将关系表示为<PartList,ListView,list_view>。

###  5.2 UI页面渲染

![](https://p0.ssl.qhimg.com/t0193ac4de2f4fd8014.png)

​
在使用动态工具进行UI页面呈现时（例如，需要登录或特殊输入才能到达另一个活动），由于不同活动之间的数据依赖关系的限制，我们建议静态呈现UI页面。我们呈现的活动是每个活动的初始状态。对于只使用静态布局来显示UI页面的应用，我们可以直接提取相应的布局文件进行渲染。而对于动态/混合布局，我们需要解决两个挑战：

（1）将动态/混合布局转换为静态布局，因为不完整的布局无法准确呈现相应的UI页面

（2）用虚拟数据（文本、图像）填充动态数据加载区域，因为我们无法渲染从远程服务器加载动态数据的对应组件，涉及后台代码

​
为了解决这些问题，我们首先静态地分析活动源代码，并确定与布局填充相关的逻辑，包括添加新视图和修改视图的参数。然后我们将目标应用程序中的动态布局转换为静态布局。此外，由于我们的方法是基于静态分析的，无法获得动态加载的真实图像，如`ListView`和`GridView`。我们没有让这个位置保持朴素，而是用虚拟图像填充这个位置，这样用户就可以直接区别它和朴素的背景。否则，图像位置可能会被同一页面的其他组件抢占。我们将虚拟数据与算法1中识别的适配器关联起来，以不同的样式显示数据。通过翻译后的静态布局和虚拟的动态数据，我们将它们编译成apk来呈现UI页面。

​
算法2详细描述了UI页面渲染过程。它将活动转换图（`atg∗`）、适配器映射关系（`adapter`）、布局类型（`latout_type`）作为输入，并输出呈现的UI页面。我们首先从`atg∗`中提取所有的活动和片段，因为我们需要渲染活动ui和片段ui，以使它更接近真实的ui。对于每个活动/片段(`act`)，如果`act`使用静态布局，我们直接进行渲染。如果应用程序使用动态/混合布局，我们的目标是将动态组件及其属性添加到相应的父布局中。具体来说，我们首先提取并精确定位父布局（例如，LinearLayout）（第8行）。然后我们遍历每个方法(`m`)，通过关键字匹配(例如，`inflate`和`addView`)，并在`onCreate()`中向前分析视图相关变量的数据流。然后我们将`compt`添加到相应的父布局(第7-11行)。至于属性，如果它是通过调用另一个方法获得的，我们利用数据流分析来得到属性的定义，并将其附加到相应的组件(第12-13行)。否则，我们通过`getElementByName()`通过属性名在资源文件中标识相应的元素，并将其附加到`compt`(第15-16行)。在对动态组件的父布局进行修改之后，我们附加了新的`par`布局来作为`act`布局，并将其保存为布局格式，以便进一步呈现(第18-19行)。以图2为例，我们的方法能够将动态/混合布局转换为静态布局(即XML格式)。

​
此外，对于使用适配器显示数据，我们将每个适配器与活动匹配，并通过嵌入视图类型修改相应的布局，例如ListView、RecyclerView(第20-22行)以及虚拟数据。我们最终得到了一个视图树，并确保从源代码中添加了相应的属性。最后，我们构建了一个apk来渲染所有的活动和片段，并对实际应用程序中的每个UI进行截图保存(第23-24行)。

###  5.3 语义名称推断

![](https://p3.ssl.qhimg.com/t0195bdf98da81f7411.png)

​
在Android应用开发中，建议应用的活动名称包含语义，并以“activity”结尾，因此我们假设开发者定义的活动名称具有相应功能的基本语义。为了验证这个假设，我们从F-Droid中随机下载1000个应用程序，从每个应用程序中提取所有的活动名称，最后得到6767个活动名称。我们手动调查活动名称，并观察到大多数活动名称具有语义意义。然而，Android混淆技术经常用于谷歌Play应用程序，以保护其安全。活动名称会被翻译成“a”、“b”、“c”等简单的单词，完全失去了实际的语义意义。这些模糊的名称极大地阻碍了用户对故事板的理解。为了解决这个问题，因为活动布局文件在应用程序中不会混淆，所以我们建议通过比较待测活动与数据库中的现有活动布局层次(即ViewGroup和View)，自动推断混淆活动的语义名称。在本文中，我们将长度小于三个字母的活动名视为模糊活动名。为了推断混淆活动的语义名称，我们打算从开源应用程序的活动名称中学习。

​ 如图8 (a)所示，我们抓取了F-Droid上的所有应用(共计4426个)，并基于应用的布局层次构建了一个大型数据库进行相似性比较。布局层次结构是基于XML布局代码的布局树(如图8
(b))。树的根节点是一种ViewGroup类型，其他的ViewGroup和Views类型是添加到根节点的子节点。我们最终得到了13,792个带有布局层次结构的活动。给定模糊活动的XML文件(布局文件)和XML名称，我们通过以下三个步骤推断其语义名称：

(1)布局层次提取，从XML文件中提取布局树(T)

(2)相似度比较，利用树编辑距离(tree edit distance,
TED)算法[70]计算T与数据库中树的相似度，TED算法定义为节点编辑操作将一棵树转换成另一棵树的最小成本序列。根据随机抽取100个树对的初步研究，我们在TED中定义一个阈值为5，并过滤TED小于5的活动名作为候选

(3)排序与匹配，根据每个活动名称和对应布局名称(XML文件名)的出现频率，从候选活动中推断出活动名称。具体来说，我们根据活动名称的频率对其进行排名，使用正则表达式将驼峰式布局名称分割为多个单个单词，过滤掉“活动”、“布局”等一般单词，并通过关键字匹配将其与数据库中的单词进行比较。最匹配的活动名称将用于重命名混淆的活动名称。但是，如果布局名称与候选名称不匹配，则使用最频繁的名称重命名它。注意，尽管布局名称没有混淆，但如果我们只使用它们来推断语义名称是无效的，因为使用动态布局的活动没有静态布局，因此没有布局名称。

## 0x6 实现

​
我们实现了一个自动化工具STORYDROID，用3K行Java代码和2K行Python代码编写。STORYDROID构建在几个现成的工具之上：IC3、JADX和SOOT。我们使用SOOT提取UI页面呈现的输入，并从apks获取调用图。在IC3的基础上建立活动过渡提取，得到比较完整的ATG。JADX用于将apk反编译为Android应用程序的源代码。我们还使用JADX从每个apk中提取XML布局代码，这不会受到混淆的影响，因此不会影响语义名称推断方法。我们使用数据驱动文档（D3）来可视化STORYDROID的结果，它提供了一种基于HTML、JavaScript和CSS数据的可视化技术。可视化包含4部分：（1）带有活动名称和相应UI页面的ATG；（2）各UI页面布局代码；（3）各活动的功能代码；（4）每个活动中的方法调用关系。

## 0x7 效果评估

​ 在本节中，我们基于以下三个研究问题来评估STORYDROID的有效性：

  * **RQ1** ：STORYDROID能否为应用提取更完整的ATG，并实现比动态测试工具（如STOAT）更好的活动覆盖率?
  * **RQ2** ：STORYDROID能否渲染出与真实截图高度相似的UI页面?
  * **RQ3** ：STORYDROID能否为混淆的活动推断出准确的语义名称?

###  7.1 实验设置

​
为了研究处理片段和内部类的能力，我们自行开发了10个apps作为groundtruth基准，涵盖了我们声称要解决的不同特性（例如，活动，片段和内部类）。这是准确知道所有转换的唯一方法，即使是在片段或内部类中，这种方法在文献中被广泛使用。我们遵循以下特性来生成应用程序：（1）仅在活动中具有转换的应用程序；只在内部类中使用转换的应用程序；只有片段转换的应用程序；在活动和内部类中都有转换的应用程序；在活动和片段中都有转换的应用程序；（2）我们开发了2个app，每条规则下有7-10个活动。我们将IC3和STORYDROID分别应用于这10个应用并进行提取转换。此外，由于利益相关者更关心那些已经主导市场的热门竞争应用。为了模拟真实的场景，我们随机从GooglePlay
Store下载了50个应用，安装量超过1000万次，以演示STORYDROID在真实应用中的有效性。我们比较了由IC3和STORYDROID识别的迁移对的数量。我们还使用这100个应用程序来评估STORYDROID的活动覆盖率和最先进的动态测试工具STOAT，该工具已被证明在应用探索方面比其他工具（如MONKEY和SAPIENZ）更有效。具体来说，我们从AndroidManifest.xml中收集每个应用程序中定义的所有活动，并比较STORYDROID呈现的活动的数量和STOAT探索的活动的数量。

​
对于RQ2，我们评估静态呈现的UI页面与STOAT基于100个应用动态呈现的真实UI页面的相似性。STOAT配置了默认设置，并有30分钟时间来测试每个应用程序，以便收集已探索的活动。我们进一步在每个应用程序上应用STOAT来收集每个活动的截图。由于STOAT在给定的时间内只能探索应用程序的部分活动，为了公平的比较，我们只能通过STORYDROID比较探索活动与相应呈现活动的相似性。

​ 对于RQ3，为了证明推理语义名的准确性，我们从第四节中提取的6767个活动名中随机选择100个具有语义意义的活动名作为ground
truth。我们从源文件中收集相应的布局文件，并进一步利用我们基于TED的方法，基于我们的布局树集合（13,792个布局文件）获取100个活动的语义名。然后，我们将结果与原始活动名称进行比较，以评估我们的方法的准确性，即正确推断语义名称的比例。

###  7.2 实验结果

![](https://p2.ssl.qhimg.com/t013f699fedb9692155.png)

![](https://p1.ssl.qhimg.com/t0111b6d47735b3c2a0.png)

**RQ1**
：表一显示了在10个基础基准测试应用程序上处理片段和内部类的能力评估结果。我们可以看到，IC3能够在活动中提取转换，但是在片段和内部类中却很弱。相反，STORYDROID可以提取与所有这些特性相关的转换。因为我们通过使用特定的API（例如，StartActivity,
StartActivityForReulst，StrartActivityIfNeeded），使用数据流分析启动新活动，提取的转换更准确。结果证明了STORYDROID在提取活动转换方面的有效性，特别是在片段和内部类中。此外，我们还在图9
(a)中评估了STORYDROID与IC3相比在真实应用上的有效性。结果表明，STORYDROID提取的活动转换几乎是IC3的2倍，无论对于开源应用还是闭源应用，STORYDROID都比IC3更有效。

​
除了内部类和fragments的限制，根据我们的观察，在IC3中会丢失Android系统事件回调中的过渡。例如，(1)PodListen是一个播客播放器，并且在回调方法（`DownloadReceiver.onReceive()`）中存在一个活动转换，当BroadcastReceiver接收Intent广播时调用它。然而，IC3不能提取活动转换。(2)
CSipSimple是一个在线语音通信应用程序，其中系统回调方法（`SipService.adjustVolume()`）启动一个新的活动，但IC3无法识别过渡。

​ 图9
(b)描述了活动覆盖结果。平均而言，STORYDROID在活动覆盖率方面优于STOAT，开源应用和闭源应用的覆盖率分别为87%和74%。此外，与STOAT（即30分钟）相比，STORYDROID提取和呈现活动的时间（即平均3分钟）要少得多。由于逆向工程技术的限制，部分类和方法无法从apks中反编译，导致无法提取活动过渡和覆盖。由于封装和混淆，这种情况在闭源应用程序中更为严重。在我们评估的应用中，PodListen是唯一一个由于SubscribeDialog片段反编译失败导致STORYDROID的活动覆盖率低于STOAT的项目。（2）另一个原因是死活动（没有过渡），如应用中未使用的遗留代码和测试代码。

![](https://p4.ssl.qhimg.com/t01bb9326e3a07caa95.png)

**RQ2**
：对于呈现的图像与STOAT获得的图像的相似度，我们使用两种广泛使用的图像相似度度量(即均值绝对)(MAE)和均方误差(MSE))来逐个像素地度量相似度。MAE测量的是预测值和实际值之间差异的平均幅度，MSE测量的是两者之间差异的平均平方。平均而言，我们渲染的图像在MAE和MSE方面分别达到84%和88%的相似度。不一致的原因解释如下。(1)组件中的一些数据是从web服务器或本地存储(如Preference、SD卡)动态加载的，如ListView的列表数据、TextView的文本数据、ImageView的图像背景。如图10
(a) (b)所示。(2)某些组件(如Button)在用户输入一些数据后，会改变其颜色或可见性。例如，如图10
(c)所示，当用户输入“昵称”时，按钮的颜色会发生变化。STORYDROID渲染活动的初始状态，从而减少了两个UI页面的相似性，但这并不影响对应用功能的理解。

![](https://p3.ssl.qhimg.com/t01ee9f804ff7a52150.png)

**RQ3**
：根据我们的方法，100个活动名称中有92个是正确推断的，准确率是92%。为了证明和解释推断结果，我们随机选取了表二所列的10个案例。第一列是指groundtruth活动名称。根据与数据库中布局树的比较结果，我们根据第二列中每个名称的频率列出正确活动名称的排名。第三列是相应的XML布局名称。STORYDROID准确地推断出与基本事实相符的10个语义名称中的8个。TrackListAct.,
PersonalInfoAct.和SearchAct.(表二以灰色突出显示)，由于布局名称无法与候选名称进行匹配，所以我们选择第一级名称作为语义名称。其中有两处与事实不符。但是请注意，我们的方法的性能被严重低估了，尽管来自STORYDROID的一些推荐名称与实际情况不同，但它们实际上具有相似的含义，例如SearchAct.和Searcher.
。此外，随着我们数据库的扩大，准确性也将得到提高。总的来说，结果表明STORYDROID可以有效地推断混淆活动的语义名称。

>
> 注：STORYDROID在ATG提取上优于IC3，在更短的时间内比STOAT的提取活动多2倍。STORYDROID可以呈现与真实页面高度相似（84%）的UI页面，并准确（92%）推断混淆的活动名称的真实语义名称。

## 0x8 实用性评估

​
除了有效性评估，我们进一步进行了用户研究，以证明STORYDROID的实用性。我们的目标是检验：（1）STORYDROID是否能够有效地探索和理解应用的功能？（2）
STORYDROID是否可以帮助准确有效地识别给定UI页面的布局代码？

​ **用户研究数据集。** 我们从谷歌Play
Store上托管的2个类别（金融、工具）中随机选择4个活动数量不同（12-15个活动）的应用（即Bitcoin、Bankdroid、ConnectBot、Vespucci）。每个类别包含两个应用程序，我们要求参与者探索每个应用程序来完成分配的任务。

​ **参与者招募。**
通过口碑营销的方式，招募我校博士后、博士、硕士8人参与实验。所有被招募的参与者均使用Android设备1年以上，并参与过与Android相关的研究课题。他们以前从未使用过这些应用程序。他们都拥有Android应用开发经验，来自不同国家，如美国、中国、欧洲国家（如西班牙）和新加坡。参与者会得到一张10美元的购物券作为他们付出时间的补偿。

​ **实验步骤。** 我们在Android设备（带有Android 4.4的Nexus
5）上安装了这4款应用。实验以任务的简单介绍开始。我们解释并介绍了所有我们希望他们在应用程序中使用的功能，并要求每个参与者分别探索这4个应用程序，以完成以下任务。注意，对于每个类别，每个参与者探索一个有STORYDROID的应用程序，另一个没有STORYDROID的应用程序。为了避免潜在的偏差，应用类别的顺序以及使用STORYDROID或不使用的顺序是基于拉丁方框进行旋转的。这种设置确保每个应用程序由具有不同开发经验的多个参与者探索。我们让每个参与者用给定的应用完成两项任务：（1）在10分钟内手动探索尽可能多的应用功能，这远远超过了典型的应用会话（71.56秒），并通过STORYDROID了解应用功能；（2）在10分钟内为给定的2个UI页面识别出相应的布局代码。这两个UI页面分别由静态和动态布局类型实现。在探索后，参与者被要求对他们的探索满意度和绘制UI的信心进行评分（李克特5分量表，1分表示最不满意或最自信，5分表示最满意或最自信）。所有参与者都独立进行实验，彼此之间没有任何讨论。在完成所有任务后，他们被要求写一些关于我们的工具的评论。

​ **实验的结果。**
如表3所示，人工探索的平均活动覆盖率较低（40.8%），说明通过人工探索深入探索应用功能的难度较大。但参与者对探索的完整性的满意度较高（平均为4.2）。这表明，开发团队在探索其他应用程序时，有时没有意识到他们错过了许多功能。这种盲目的自信和忽视可能会进一步影响他们开发自己的应用的策略或决策。与手动探索相比，STORYDROID能够以更少的时间成本（平均2.5分钟）实现2倍的活动覆盖率，以帮助理解应用功能。根据参与者的反馈，STORYDROID的平均满意度为4.4，这代表了帮助参与者探索和理解应用功能的有用性。表四显示了将UI页面映射到有或没有STORYDROID的布局代码的时间成本和信心。所有参与者将UI页面映射到对应布局代码的时间均超过8分钟，其中有4个页面在10分钟内没有映射成功。而在STORYDROID的帮助下，参与者只需要30秒就可以确认UI页面与布局代码之间的映射关系。为了了解没有STORYDROID和有STORYDROID的差异的显著性，我们进行Mann-Whitney U检验，这是为小样本设计的。表III和表IV的结果均显著，p-value < 0.01或p-value < 0.05。

![](https://p4.ssl.qhimg.com/t0112ec4c89a4a8a6a0.png)

![](https://p1.ssl.qhimg.com/t014fb6c52fe736dab6.png)

​
我们分析了参与者的评论，发现他们主要关注两个方面：（1）最好在边缘添加活动转换方法/事件，如点击“登录”；（2）如果转换图太复杂，STORYDROID需要提供更好的策略来可视化它。

## 0x9 讨论

###  9.1 基于STORYDROID的未来应用

​ 除了上述基本实用性（即探索应用程序功能），我们还将讨论基于STORYDROID输出的其他后续应用程序。

​ **UI设计和代码推荐。**
开发一个移动应用的GUI需要两个步骤，即UI设计和实现。设计UI的重点是正确的用户交互和视觉效果，而实现UI的重点是使用GUI框架提供的正确布局和小部件使UI按照设计工作。我们的STORYDROID可以帮助UI设计师和开发人员建立一个大规模的应用故事板数据库。这样的数据库在抽象活动（文本）、UI页面（图像）和详细的布局代码（即，活动→UI页面→布局代码）之间架起了桥梁，因此它们可以作为一个整体进行搜索。由于这种映射，UI/UX设计师可以直接使用关键字（例如，“登录”和“搜索”）通过匹配我们数据库中的UI的活动名称来搜索UI图像。搜索到的图片可以用来启发他们自己的UI设计。UI开发人员还可以通过搜索数据库来获取UI实现。给定设计师提供的UI设计图像，开发人员可以通过计算图像相似度（如第VI-B3节中的MSE）在我们的数据库中搜索相似的UI。由于数据库中的每个UI页面也与相应的运行时UI代码相关联，开发人员可以在候选列表中选择最相关的UI页面，然后根据自己的需要定制UI代码，以实现给定的UI设计。

​ **指导应用的回归测试。**
重用测试用例有助于提高Android应用回归测试的效率。STORYDROID可以通过识别被修改的UI组件来帮助指导应用程序回归测试。同一个应用程序的不同版本有许多共同的功能，这意味着新版本中的大多数UI页面与上一个版本相同。STORYDROID存储了UI页面与相应布局代码之间的映射关系，因此，分析器可以通过分析布局代码与A
TG的差异，获得修改后的组件，并进一步更新相应的测试用例。在这个场景中，大多数测试用例都可以重用，并且可以有效地识别修改的组件，以指导回归测试的测试用例更新。

###  9.2 局限性

​ **过渡提取。**
UI页面呈现的输入是从基于SOOT的静态分析中提取出来的，但一些文件没有被转换，调用图仍然不完整。对于闭源应用，使用JADX将apk反编译为Java代码。但是，部分Java文件反编译失败，影响了UI页面呈现的分析结果。但根据我们的观察，这些情况很少出现在真正的应用程序中。此外，由于其他组件（例如Broadcast
Receiver）生成的活动只能动态加载，我们基于静态分析的方法无法处理它们。

​ **UI页面呈现。**
（1）一些UI页面通过覆盖`onDraw`方法来使用自定义组件。例如，Kiwix允许用户在没有网络连接的情况下阅读维基百科。它动态地绘制UI页面的画布。（2）有些组件是由用户定义的函数动态创建的。例如，BankDroid是瑞典银行的银行客户端。它调用`CreateFrom()`函数来创建一个组件，其中的参数是另一个自定义方法的返回值。因为除非我们在运行时分析它们，否则我们无法得到这些值的线索，所以我们使用一些空占位符来占据位置，以便整体布局与真实的UI页面相同。

## 0x10 相关工作

###  10.1 帮助Android开发的研究

​
GUI在应用程序和用户之间提供了一个可视化的桥梁，通过GUI它们可以相互交互。开发一个移动应用程序的GUI涉及两个独立但相关的活动：设计UI和实现UI。为了辅助UI的实现，Nguyen和Csallner通过图像处理技术对UI截图进行了逆向工程。进一步提出了更强大的基于深度学习的算法，以利用Android应用程序现有的大数据。基于检索的方法也被用于开发用户界面。Reiss将草图解析为结构化查询，在数据库中搜索基于java桌面软件的相关UI。

​
与UI实现的研究不同，我们的研究更侧重于应用故事板的生成，它不仅包含UI代码，还包含UI之间的转换。此外，在之前的工作中生成的UI代码都是静态布局，这与我们在第三节中观察到的开发人员经常编写Java代码来动态呈现UI的情况相冲突。在我们的工作中，我们为开发人员提供每个屏幕的原始UI代码（无论是静态代码、动态代码还是混合代码）。这样的实际代码使开发人员更容易根据自己的需要定制UI。除了UI实现之外，一些研究还探讨了UI设计与实现之间的问题。Moran等人通过比较图像与计算机视觉技术的相似度来检查UI实现是否违反了原始UI设计。他们进一步检测并总结了移动应用程序中GUI的变化。他们依赖于动态运行的应用来收集UI截图，这很耗时，导致应用的覆盖率较低。相反，我们的方法可以静态提取应用的大部分UI页面，可以补充这些研究的相关任务。

​ GUIFECTCH通过考虑UI之间的转换，将Reiss的方法定制到Android APP
UI搜索中。也可以提取对应过渡的UI截图，但是我们的工作和他们的有两个不同之处。首先，他们的模型只能处理开源的应用程序，而我们的模型也可以对闭源的应用程序进行逆向工程，从而带来更多的通用性和灵活性。另一方面，GUIFECTCH比我们基于静态分析的方法重得多，因为它既依赖静态分析提取UI代码，也依赖动态分析提取转换。此外，动态运行应用程序通常不能覆盖所有屏幕，导致信息丢失。

###  10.2 帮助理解应用程序的研究

​ Android应用逆向工程的过程是依靠最先进的工具（如APKTOOL，
ANDROGUARD，DEX2JAR，SOOT）来将APK反编译为中间语言（如smali,
jimple）或Java代码。Android逆向工程通常用于理解和分析应用。它也可以用来提取特征，为Android恶意软件检测。然而，逆向工程只有基本的代码检查功能。与逆向工程不同的是，我们的工作提供了每个应用程序的故事板，以显示基本功能和其他有用的映射之间的UI页面和相应的布局代码，这有助于不同的各方（如PM,
UI/UX设计师，开发人员）提高他们在现实世界中的工作效率。

###  10.3 分析Android应用程序的研究

​
许多针对Android应用的静态分析技术已经被提出。A3E为Android应用的系统测试提供了有针对性和深度优先两种策略。它还为自动生成的测试用例提取静态活动转换图。除了Android测试的目标外，我们还提取活动转换图来识别和系统地探索Android应用的故事板。EPICC是提取组件通信的第一项工作，它决定了大多数Intent属性与组件匹配。ICC利用基于本文提出的COAL语言的MVC问题求解器，在组件间通信的提取能力上明显优于EPICC。FLOWDROID和ICCTA基于SOOT提取调用图进行数据流分析，检测数据泄漏和恶意行为。

## 0x11 总结和未来的工作

​
在本文中，我们提出了STORYDROID系统，通过提取相对完整的ATG，静态渲染UI页面，并推断混淆活动的语义名，返回Android应用的可视化故事板。这样的故事板有利于应用开发过程中的不同角色（例如，PMs,
UI设计师和开发人员）。大量的实验和用户研究证明了STORYDROID的有效性和实用性。基于STORYDROID的输出，我们能够构建一个大规模的故事板数据库，以弥合应用活动（文本）、UI页面（图像）和实现代码之间的差距。这样一个全面的数据库可以支持许多潜在的应用程序，比如向设计人员推荐UI页面和向开发人员推荐实现代码。在未来，我们将探索这些潜在的应用程序，并将我们的方法扩展到其他平台，如IOS应用程序和桌面软件等更普遍的使用场景。

## 0x12 鸣谢

​
我们感谢邢振昌教授和李莉教授提出的建设性意见。这项工作的部分支持来自于国家自然科学基金资助61502170，上海市科学技术委员会资助的18511103802，南大研究资助金NGF-2017-03-03和NRF资助CRDCG2017-S04。

## 附录：部署复现

###  0x1 准备的文件和工具

**1.1 环境需求**

官方提供的环境需求如下：

    
    
    Ubuntu/Macbook
    Python: 2.7
    APKTool: 2.4.1
    Android emulator：X86, Android 7.1.1, Google APIs, 1920 * 1080
    Android environment: adb, aapt
    Java environment (jdk): jdk1.8.0_45
    

**1.2 文件准备**

我们大概需要准备一下几个东西，其中下载连接如下：

    
    
    链接：https://pan.baidu.com/s/1CNqKKS1MMxdbypnGflKAZg 
    提取码：ub2y
    

我们应当检查我们是否拥有以下文件：

  * apktool.jar
  * apktool.sh
  * genymotion-3.2.1-linux_x64.bin
  * Genymotion-ARM-Translation_for_8.0.zip
  * android-studio-2020.3.1.24-linux.tar.gz
  * IC3.zip
  * jadx-master.zip
  * StoryDistill-main.zip

**1.3 加速镜像配置**

> 如果之前配置过Ubuntu镜像和Python镜像可以略过此步

**Ubuntu镜像：**

Ubuntu镜像这里推荐使用华为云开源镜像站提供的加速镜像，是我用过目前最快最稳定的Linux发行版加速镜像

  * Ubuntu的仓库地址为：<https://repo.huaweicloud.com/ubuntu/>
  * Ubuntu-CD的镜像地址为：<https://repo.huaweicloud.com/ubuntu-cdimage/>
  * Ubuntu-Cloud的镜像地址为：<https://repo.huaweicloud.com/ubuntu-cloud-images/>
  * Ubuntu-Ports的仓库地址为：<https://repo.huaweicloud.com/ubuntu-ports/>
  * Ubuntu-Releases的镜像地址为：<https://repo.huaweicloud.com/ubuntu-releases/>

首先备份配置文件：

    
    
    sudo cp -a /etc/apt/sources.list /etc/apt/sources.list.bak
    

2、修改 **sources.list** 文件，将 **<http://archive.ubuntu.com>** 和
**<http://security.ubuntu.com>** 替换成 **<http://repo.huaweicloud.com>**
，可以参考如下命令：

    
    
    sudo sed -i "s@http://.*archive.ubuntu.com@http://repo.huaweicloud.com@g" /etc/apt/sources.list
    sudo sed -i "s@http://.*security.ubuntu.com@http://repo.huaweicloud.com@g" /etc/apt/sources.list
    

3、执行 **apt-get update** 更新索引

**Python镜像：**

临时使用的话，运行以下命令使用华为开发云软件源安装软件包：

    
    
    pip install --trusted-host https://repo.huaweicloud.com -i https://repo.huaweicloud.com/repository/pypi/simple <some-package>
    

这里建议平时设为默认，Pip的配置文件为用户根目录下的：`~/.pip/pip.conf`（Windows路径为：`C:\Users\<UserName>\pip\pip.ini`）,
您可以配置如下内容：

    
    
    [global]
    index-url = https://repo.huaweicloud.com/repository/pypi/simple
    trusted-host = repo.huaweicloud.com
    timeout = 120
    

###  0x2 安装Android Studio

**2.1 安装Java OpenJDK**

Android Studio需要将OpenJDK版本8或更高版本安装到您的系统。

我们将安装OpenJDK8。安装非常简单，首先更新包索引：

    
    
    sudo apt update
    

通过键入以下命令来安装OpenJDK 8软件包：

    
    
    sudo apt install openjdk-8-jdk
    

通过键入以下命令来验证安装，该命令将打印Java版本：

    
    
    java -version
    

输出应如下所示：

    
    
    openjdk version "1.8.0_191" OpenJDK Runtime Environment (build 1.8.0_191-8u191-b12-2ubuntu0.18.04.1-b12) OpenJDK 64-Bit Server VM (build 25.191-b12, mixed mode)
    

**2.2 安装Android Studio**

在撰写本文时，Android Studio的最新稳定版本为3.3.1.0版。 最简单的方法是通过使用snappy打包系统在Ubuntu
18.04上安装Android Studio。

要下载并安装Android Studio snap软件包，请使用`Ctrl+Alt+T`键盘快捷键打开您的终端，然后键入：

    
    
    sudo apt install snap -y
    
    
    
    sudo snap install android-studio --classic
    

安装完成后，您将看到以下输出：

    
    
    android-studio 2020.3.1.22 from Snapcrafters installed
    

而已。 Android Studio已安装在您的Ubuntu桌面上。

**2.3 启动Android Studio**

在启动前将当前用户添加到root用户组上

通过命令 `sudo adduser $USER root`将当前用户加入到root组

您可以通过在终端中键入`android-studio`或单击Android Studio图标（“ `Activities -> Android
Studio` ）来启动`Activities -> Android Studio`

**2.4 解决/dev/kvm device permission denied问题**

我用的是Ubuntu系统，首先需要安装qemu-kvm：

    
    
    sudo apt install qemu-kvm
    

将当前用户添加到kvm用户组：

    
    
    sudo adduser $USER kvm
    

检查`/dev/kvm`所有者：

    
    
    ls -al /dev/kvm
    

一般结果就是所有者是root以及kvm这个组

添加完了之后检查一下kvm组里有没有你的用户名：

    
    
    grep kvm /etc/group
    

一般结果就是这样：

    
    
    kvm:x:数字:用户名
    

之后重启系统生效，如果不想重启可以运行以下命令(仍然得注销后再登录才生效)：

    
    
    udevadm control --reload-rules && udevadm trigger
    

> ps：反正我选择重启

###  0x3 安装Genymotion

需要注意2点：

  * `Genymotion` 依赖 `VirtualBox`，必须安装 `VirtualBox` 才能安装 `Genymotion`
  * `Genymotion` 必须注册登录后才能正常使用，否则即使安装完成也无法使用，且国内访问 `Genymotion` 的网站和程序都有可能在网络上受限，

> **也就是说大陆地区网络直接访问官网或者在程序中登录，可能很慢可能无法访问** ，所以慎用

**3.1 安装VirtualBox**

安装 `Genymotion` 前先确认有没有装 `VirtualBox`，这里 `ubuntu` 用户推荐直接用命令安装

    
    
    # update 可选运行或不运行
    sudo apt update
    sudo apt install virtualbox
    

**3.2 安装Genymotion**

    
    
    # 先自行cd到文件目录 然后给文件赋权
    sudo chmod u+x ./genymotion-3.2.1-linux_x64.bin 
    # 安装到指定路径 也可以写绝对路径
    sudo ./genymotion-3.2.1-linux_x64.bin -d ~/opt
    # 之后脚本会二次确认路径，如果正确输入y 回车 即可
    Installing to folder [/opt/genymotion]. Are you sure [y/n] ? y
    

**3.3 Genymotion的ADB设置**

因为Genymotion模拟器default的ADB是它自己实现的Genymotion
ADB，然后StoryDroid脚本使用的adb是AndroidSDK里面自带的ADB，所以要把Genymotion的ADB修改为本机AndroidSDK里面的ADB

例如我本机SDK的位置如下：

    
    
    /usr/lib/android-sdk/
    

###  0x4 安装apktool

官网如下：

    
    
    https://ibotpeaches.github.io/Apktool/install/
    

首先需要下载一个sh脚本文件：

    
    
    https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/windows/apktool.bat
    

将其改名为apktool，因为windows的Unix的换行符定义不一致，所以需要进行修改，运行如下命令：

    
    
    sudo sed -i -e 's/\r$//' apktool
    

然后下载`apktool.jar`

    
    
    https://bitbucket.org/iBotPeaches/apktool/downloads/
    

分别进入下载的2个文件所在的目录，将其复制到/usr/local/bin/下：

    
    
    sudo cp apktool /usr/local/bin
    sudo cp apktool.jar /usr/local/bin
    

将两个文件修改为可执行权限，进入`/usr/local/bin`目录下：

    
    
    cd /usr/local/bin
    sudo chmod 755 apktool apktool.jar
    

打开终端输入`apktool -version`，显示对应的版本信息，则说明安装成功

    
    
    syc@ubuntu:/usr/local/bin$ apktool -version
    2.6.0
    

安装aapt和adb

    
    
    sudo apt install adb aapt -y
    

###  0x5 安装StoryDistiller

将`IC3`和`jadx-master`解压到用户目录下

    
    
    syc@ubuntu:~$ ls -l
    total 665400
    ......
    drwxrwxr-x  4 syc  syc       4096 Jun 22  2019 IC3
    -rw-rw-r--  1 syc  syc  559229407 Jul 31 21:49 IC3.zip
    drwxrwxr-x 10 syc  syc       4096 Jul  2  2018 jadx-master
    -rw-rw-r--  1 syc  syc  122068361 Jul 31 21:51 jadx-master.zip
    ......
    

解压`StoryDistiller-main`，将获得的`code`文件夹复制粘贴进入`main-flolder`文件夹中，文件目录如图所示：

    
    
    syc@ubuntu:~/Downloads/StoryDistill/StoryDistiller-main/main-folder$ ls -all
    total 80
    drwxrwxr-x 16 syc syc  4096 Sep 30 21:07 .
    drwxrwxr-x  4 syc syc  4096 Jun 28 03:33 ..
    drwxrwxr-x  2 syc syc  4096 Jun 28 03:33 apks
    drwxrwxr-x  2 syc syc  4096 Jun 28 03:33 atgs
    drwxrwxr-x  3 syc syc  4096 Jun 28 03:33 code
    drwxrwxr-x  4 syc syc  4096 Jun 28 03:33 config
    -rw-rw-r--  1 syc syc 14340 Jun 28 03:33 .DS_Store
    drwxrwxr-x  2 syc syc  4096 Jun 28 03:33 ic3_atgs
    drwxrwxr-x  3 syc syc  4096 Jun 28 03:33 java_code
    drwxrwxr-x  3 syc syc  4096 Jun 28 03:33 libs
    drwxrwxr-x  2 syc syc  4096 Jun 28 03:33 manifest
    drwxrwxr-x  2 syc syc  4096 Jun 28 03:33 outputs
    drwxrwxr-x  2 syc syc  4096 Jun 28 03:33 parsed_cgs
    drwxrwxr-x  2 syc syc  4096 Jun 28 03:33 parsed_ic3
    drwxrwxr-x  2 syc syc  4096 Jun 28 03:33 parsed_manifest
    drwxrwxr-x  2 syc syc  4096 Jun 28 03:33 soot_cgs
    drwxrwxr-x  2 syc syc  4096 Jun 28 03:33 storydroid_atgs
    

将待测试的APK文件放入`main-folder`中

进入`code`文件夹中，修改`run_storydistiller.py`中的路径配置信息，修改为，具体情况根据自己的机器情况来设定：

    
    
    '''
    Ubuntu and Macbook
    '''
    java_home_path = '/usr/lib/jvm/jdk1.8.0_45' # Ubuntu
    #java_home_path = '/Library/Java/JavaVirtualMachines/jdk1.8.0_211.jdk/Contents/Home' # Macbook
    
    sdk_platform_path = '/home/syc/Downloads/StoryDistill/StoryDistiller-main/main-folder/config/libs/android-platforms/'
    #sdk_platform_path = '/Users/chensen/Tools/storydistiller/config/libs/android-platforms/'
    
    lib_home_path = '/home/syc/Downloads/StoryDistill/StoryDistiller-main/main-folder/config/libs/'
    #lib_home_path = '/Users/chensen/Tools/storydistiller/config/libs/'
    
    callbacks_path = '/home/syc/Downloads/StoryDistill/StoryDistiller-main/main-folder/config/AndroidCallbacks.txt'
    #callbacks_path = '/Users/chensen/Tools/storydistiller/config/AndroidCallbacks.txt'
    
    jadx_path = '/home/syc/jadx-master/'
    ic3_path = '/home/syc/IC3/'
    #jadx_path = '/Users/chensen/Tools/storydroid_v1/jadx-master/'
    #ic3_path = '/Users/chensen/Tools/storydroid_v1/IC3/'
    

然后在这个路径下进行运行：

    
    
    /StoryDistiller-main/main-folder/code
    

运行前需要启动Genymotion的虚拟机，推荐使用Google Nexus 5X进行测试

首先需要安装`treelib`，`python-scrapy`，`python-opencv`

    
    
    pip install treelib
    sudo apt install python-scrapy python-opencv -y
    

用一下命令进行运行：

    
    
    sudo python2 run_storydistiller.py /home/syc/Downloads/StoryDistill/StoryDistiller-main/main-folder/
    

###  0x6 查看结果

具体的程序输出结果在`outputs`文件夹里面，每个APP具有对应的文件夹名字，其中还有一个`output`文件夹里面存在一个`index.html`文件，点击即可获得可视化的网页展示

本文翻译自ieeexplore.ieee.org
[原文链接](https://ieeexplore.ieee.org/document/8812043﻿)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **ZERO-A-ONE** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/254781](/post/id/254781)

安全客 - 有思想的安全新媒体

本文转载自: [ieeexplore.ieee.org](https://ieeexplore.ieee.org/document/8812043﻿)

如若转载,请注明出处： <https://ieeexplore.ieee.org/document/8812043﻿>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Android](/tag/Android)
  * [自动化测试](/tag/自动化测试)

 **+1** __8赞

 __收藏

![](https://p0.ssl.qhimg.com/t01a8f8240d1801aeee.png) ZERO-A-ONE

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

