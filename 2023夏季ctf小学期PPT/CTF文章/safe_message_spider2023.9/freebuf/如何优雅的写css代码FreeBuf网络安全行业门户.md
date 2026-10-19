**作者：京东科技 杨健**

CSS（全称 Cascading Style
Sheets，层叠样式表）为开发人员提供声明式的样式语言，是前端必备的技能之一，基于互联网上全面的资料和简单易懂的语法，CSS
非常易于学习，但其知识点广泛且分散，很难做到精通，在我们日常开发中，常常忽视了 CSS 代码的质量，很容易写出杂乱无章的 CSS 文件。

代码优化建议

###  **1\. 使用缩写属性精简代码**

适用于：margin、padding、border、font、background 等

但并非所有情况下都必须缩写，因为当一个属性的值缩写时，总是会将所有项都设置一遍，而有时候我们不希望设置值里的某些项，这时候需要开发者自行判断。

    
    
    .content{
        // 缩写前
        margin-right:16px;
        margin-top:30px;
        width:184px;
        height:32px;
        background:#FFFFFF
        margin-left:10px;
    }
    .content{
        //缩写后
        margin:30px 16px 0 10px;
        width:184px; 
        height:32px; 
        background:#FFFFFF
    }
    
    

### **2\. 合并选择器**

使用 "," 连接多个选择器定义公用属性，不仅能增加可读性，还能减小 css 文件大小。

    
    
    .content{
      display: flex;
      .flush, 
      .include, 
      .underline{
       margin-right: 12px; 
       padding: 3px 6px; 
       border: 1px solid #a96161; 
       font-size: 12px; 
       color: #412c2c; 
       }
       .flush{ 
       color: #FFFFFF; 
       background-color: aqua; 
       }
       .include{ 
       color: #5d3e3e; 
       background-color: #657f7f; 
       }
        .underline{ 
        color: #7da938; 
        background-color: #7c6a6a; 
        }
    }
    
    

### **3\. 使用更语义化的单词命名 class**

命名的时候以 “在你之后开发的人不会产生疑惑” 为目标 如下

    
    
    .curr{
        color:#FFFFFF;
        background:red;
    }
    .future{
        background:#9f6262;
    }
    // curr 是啥? future又是啥? ⬆️
    
    .current-count{ 
        color:#FFFFFF; 
        background:red; 
    } 
    .future-count{ 
        background:#9f6262; 
    }
    
    

### **4\. 属性声明顺序**

选择器中属性数量较多时，将相关的属性声明放在一起，并按以下顺序排列：

  1. 定位相关，如 position、top/bottom/left/right、z-index 等

  2. 盒模型相关，如 display、float、margin、width/height 等

  3. 排版相关，如 font、color、line-height 等

  4. 可视相关，如 background、color 等

  5. 其他，如 opacity、animation 等

建议：在属性数量较多时可以参考这 5 个类别归类排列。

    
    
    /* 定位相关 */
      position: absolute;
      top: 0;
      right: 0;
      bottom: 0;
      left: 0;
      z-index: 100;
      /* 盒模型相关 */
      display: block;
      float: right;
      width: 100px;
      height: 100px;
      /* 排版相关 */
      font: normal 13px "Helvetica Neue", sans-serif;
      line-height: 1.5;
      color: #333;
      text-align: center;
      /* 可视相关 */
      background-color: #f5f5f5;
      border: 1px solid #e5e5e5;
      border-radius: 3px;
      /* 其他 */
      opacity: 1;
    
    

### **5\. 使用 & 符号引用父选择器**

& 是 Sass 和 Less 中提供的语法糖，用于表示对父选择器的引用

优点：非常适合用于编写组件的样式，减少了很多重复单词

缺点：从 HTML 的 class name 中寻找对应样式的成本增加

    
    
    .first {
        .first-title {/* styles */}
        .first-title:after {/* styles */}
        .first-content {/* styles */}
    }
    /* 用&引用来优化代码 */
    .first {
        &-title {
            /* styles */
            &:after {/* styles */}
        }
        &-content {/* styles */}
    }
    
    

#### **Sass .vs. Less？**

#### 预处理器将 CSS 从声明语言转换成一门编程语言

可嵌套的语法增加了样式文件的可读性和可维护性

变量与混合特性能够减少很多重复的样式声明

Less 更像 CSS，易于上手，能够从 CSS 平滑过渡；Sass 的缩进语法接受度因人而异，Sass3.0 中提出了兼容 CSS 的
Scss，用户可以选择使用 Sass 或 Scss。

当项目 CSS 中需要涉及复杂逻辑时，Sass/Scss 更适合，Sass 提供了更强大、更接近编程语言的
@function、@if/@else、@while 等语法；当项目的样式复杂度不高时，选 Sass 或 Less 都可以。 （下面是一个 Less 和
Scss 语法对比例子）

    
    
    // Less
    .mixin( @count )when( @count > 0 ){
        background-color: black;
    }
    .mixin( @count )when( @count <= 0 ){
        background-color: white;
    }
    .tag {
        .mixin(100);
    }
    // Scss
    @function selectCount($count) {
        @if $count > 0 {
            return black;
        }
        @else {
            return white;
        }
    }
    .tag {
        background-color: checkCount(100);
    }
    
    

综上，CSS 作为一门前端必备的基础技能，具有许多原生的痛点。近年来，开发者们也在源源不断地提出了不同的优化方案，我们在日常关注
Vue、React、NodeJS、性能优化等热门前端话题的时候，也不要忘了好好写 CSS 代码呀～

内容来源：京东云开发者社区[https://www.jdcloud.com/](https://www.oschina.net/action/GoToLink?url=https%3A%2F%2Fwww.jdcloud.com%2F)

