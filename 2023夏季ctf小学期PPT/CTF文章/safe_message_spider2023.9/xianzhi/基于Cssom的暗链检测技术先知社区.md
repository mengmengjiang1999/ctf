# 什么是暗链

大部分的开源代码在实现暗链检测的时候都是直接判断页面里面有没有敏感词，如果有，就认为该链接为暗链。这种做法其实是有误的。  
违规链接应该分为：外链、内链、死链和暗链。而暗链除了违规，还应该具备“暗”这个看不见的特征。

## 暗链的特征

其实“暗链”就是看不见的网站链接，“暗链”在网站中的链接做得非常隐蔽，短时间内不易被搜索引擎察觉。是做非法SEO的常用手段。

下面是一些特征

    
    
    <!-- 正常连接 -->
    <a href="https://www.baidu.com">正常外链</a>
    
    <!-- position位置类暗链 -->
    <!-- position位置样式，将元素的top、left位置设置成负数，让元素处于可视区外 -->
    <a href="https://www.h0ksd3.6dayxpj.com:8989" style="position: absolute; top: -999px; left: -999px;">position暗链</a>
    
    <!-- display 和 visibility 隐藏类暗链 -->
    <a href="https://www.h0ksd3.6dayxpj.com:8989" style="display: none;">display为none使得链接不可见</a>
    <a href="https://www.h0ksd3.6dayxpj.com:8989" style="visibility: hidden;">display为hidden使得链接不可见</a>
    
    <!-- 链接颜色和文字类暗链 -->
    <!-- 链接颜色与背景色相同或相似，color采用十六进制表达色彩 -->
    <a href="https://www.h0ksd3.6dayxpj.com:8989" style="color: #ffffff;">链接颜色与背景色相同或相似，采用十六进制表达色彩</a>
    <!-- 链接颜色与背景色相同或相似，color采用颜色英文名称表达色彩 -->
    <a href="https://www.h0ksd3.6dayxpj.com:8989" style="color: white;">链接颜色与背景色相同或相似，采用颜色英文名称表达色彩</a>
    <!-- 链接颜色透明，color采用transparent值 -->
    <a href="https://www.h0ksd3.6dayxpj.com:8989" style="color: transparent">链接颜色透明</a>
    <!-- 链接文字设置为0，使得不可见 -->
    <a href="https://www.h0ksd3.6dayxpj.com:8989" style="font-size: 0px;">链接文字字号为0像素</a>
    
    <!-- marquee类暗链 -->
    <!-- 将marquee的scrollamount属性值调为较大值，使跑马灯移动速度超过人眼可见范围，达到隐藏效果 -->
    <marquee scrollamount="100000"><a href="https://www.h0ksd3.6dayxpj.com:8989">我的车速够快，你也看不见我</a></marquee>
    <!-- 将marquee的scrolldelay属性值调为较大值，使跑马灯移动速度非常慢，很长时间都不会在屏幕中出现该链接，达到隐藏效果 -->
    <marquee scrolldelay="100000"><a href="https://www.h0ksd3.6dayxpj.com:8989">我发车够慢，你也不容易发现我</a></marquee>
    
    <!-- JS写入CSS样式类暗链 -->
    <!-- 利用JavaScript的document.write方法写入一个CSS样式属性display为none，或者visibility为hidden的层来包裹需要隐藏的链接，达到隐藏暗链的效果 -->
    <script language="javascript" type="text/javascript">
        document.write("<div style=\'display:none;\'>");
    </script>
    <a href=https://www.h0ksd3.6dayxpj.com:8989>通过JavaScript写入包裹该链接的隐藏层，使得链接不可见</a>
    <script language="javascript" type="text/javascript">
        document.write("</div>"); 
    </script>
    
    <!-- JS修改CSS样式类暗链 -->
    <!-- 利用JavaScript修改CSS样式属性display为none，或者visibility为hidden来达到隐藏的效果 -->
    <a href="https://www.h0ksd3.6dayxpj.com:8989" id="link1">通过JavaScript修改了本链接可见属性设置为隐藏，使得链接不可见</a>
    <script language="javascript" type="text/javascript">
        document.getElementById("link1").style.display = "none";
    </script>
    
    <!-- z-index类暗链 -->
    <!-- 用z-index属性堆叠遮挡，z-index值越小堆叠越靠后 -->
    <div id="container" style="position: relative;">
        <div id="box1"
            style="position: absolute; top: 0; left: 0; width: 90%; height: 100px; background-color: yellow; z-index: 999;">
            我是一个div层，这一层下面隐藏着链接
        </div>
        <div id="box2">
            <a href="https://www.h0ksd3.6dayxpj.com:8989">被z-index较大的div层把我遮挡了，你也看不见我</a>
        </div>
    </div>
    
    <!-- iframe内联框架类暗链 -->
    <!-- 利用 iframe 创建隐藏的内联框架，frameborder设置边框宽度为0，width宽度或height高度设置为0时，就不可见 -->
    <iframe src="https://httpbin.org/get" frameborder="10px" width="0px"
        height="0px">我是一个iframe内链框架，frameborder为0，宽度为0时或高度为0时，你就看不见我了</iframe>
    
    <!-- 重定向方式暗链 -->
    <!-- 采用setTimeout，在跳转到正常网站页面前植入暗链，等待很短时间就跳转到正常页面，用户不易察觉 -->
    <script>setTimeout('window.location="index.html"', 0.1)</script>
    <body leftmargin="0" topmargin="0" scroll="no">
        <a href="https://h0ksd3.6dayxpj.com:8989">新葡京娱乐城</a>
    </body>
    <!-- 采用meta标签，通过设置http-equiv为refresh，结合content中携带需跳转的链接和较短等待时间，来实现重定向，不过该种方式很容易被用户发现异常 -->
    <head>
        <meta http-equiv="refresh" content="1;url=https://h0ksd3.6dayxpj.com:8989" />
    </head>
    
    <!-- meta标签类暗链 -->
    <!-- 设置meta的name属性值为keywords，content为包含暗链的文字，或通过十进制或十六进制的HTML编码或HTML实体编码方式逃避静态爬虫爬取后不做解码处理的方式 -->
    <head>
        <!-- 用于搜索引擎SEO -->
        <meta name="keywords" content="澳门新普京最新官方网站【abcd.com】" />
        <!-- 采用十进制的HTML编码 -->
        <meta name="keywords"
            content="&#28595;&#38376;&#26032;&#26222;&#20140;&#26368;&#26032;&#23448;&#26041;&#32593;&#31449;&#12304;&#97;&#98;&#99;&#100;&#46;&#99;&#111;&#109;&#12305;" />
        <!-- 采用十六进制的HTML编码 -->
        <meta name="keywords"
            content="&#x6fb3;&#x95e8;&#x65b0;&#x666e;&#x4eac;&#x6700;&#x65b0;&#x5b98;&#x65b9;&#x7f51;&#x7ad9;&#x3010;&#x61;&#x62;&#x63;&#x64;&#x2e;&#x63;&#x6f;&#x6d;&#x3011;" />
        <!-- 采用HTML实体编码 -->
        <meta name="keywords" content="澳门新普京最新官方网站【abcd&period;com】" />
    </head>
    

我们可以根据此构造出一个具有暗链的网站，然后利用代码去检测

# 什么是CSSOM

来看看chatgpt怎么说

> CSSOM（CSS Object
> Model）是指CSS对象模型，它是一种表示和操作CSS样式信息的API（应用程序接口）。类似于DOM（文档对象模型）用于操作HTML文档的结构和内容，CSSOM用于操作和控制CSS样式的规则、属性和值。  
>
> CSSOM提供了一组接口和方法，允许开发人员通过JavaScript访问和修改CSS样式信息。它可以用于动态地创建、修改或删除CSS规则，以及获取和修改元素的CSS属性和值。  
>  通过CSSOM，开发人员可以实现一些常见的样式操作，例如：  
>  动态地改变元素的样式，比如修改背景颜色、字体大小等。  
>  动态地添加、删除或修改CSS规则，从而改变整个文档的样式。  
>  访问和获取元素的计算样式（computed style），即应用在元素上的最终样式值。  
>  操作CSS动画和过渡效果，包括启动、停止或修改动画。  
>
> CSSOM的主要优势之一是可以与DOM无缝集成，通过将CSS样式与HTML文档结构和内容分开，可以实现更好的可维护性和灵活性。它在前端开发中扮演着重要的角色，让开发人员能够以编程的方式操控和控制页面的样式外观和交互效果。

我们通过playwright爬虫，通过执行js函数，将所有暗链检测中可能使用到的css属性全部获取到，具体的方法为：

    
    
    function traverseDOMTree(node) {
                      // 检查节点是否为元素节点
                      cssom = []
                      if (node.nodeType === Node.ELEMENT_NODE) {
                        // 输出节点的 class 属性
    
                      }
                      const e = node;
                      const styles = window.getComputedStyle(e);
                      const ans = {
                            'tag_name':e.tagName,
                            'attribute_content':e.hasAttribute('content') ? e.attributes['content'].value : '',
                            'background_color':styles['background-color'],
                            'color':styles['color'],
                            'display':styles['display'],
                            'font_size':styles['font-size'],
                            'frameborder':e.hasAttribute('frameborder') ? e.attributes['frameborder'].value : '',
                            'height':styles['height'],
                            'href':e.href,
                            'http_equiv':e.hasAttribute('http-equiv') ? e.attributes['http-equiv'].value : '',
                            'language':e.hasAttribute('language') ? e.attributes['language'].value : '',
                            'left':styles['left'],
                            'position':styles['position'],
                            'scroll_delay':e.hasAttribute('scrolldelay') ? e.attributes['scrolldelay'].value : '',
                            'src':e.hasAttribute('src') ? e.attributes['src'].value : '',
                            'scroll_amount':e.hasAttribute('scrollamount') ? e.attributes['scrollamount'].value : '',
                            'top':styles['top'],
                            'width':styles['width'],
                            'visibility':styles['visibility'],
                            'z_index':styles['z-index'],
                            'children':[]
                        }
                      // 遍历所有子节点
                      for (let i = 0; i < node.childNodes.length; i++) {
                        const childNode = node.childNodes[i];
    
                        // 递归遍历子节点
                        if (childNode.nodeType === Node.ELEMENT_NODE) {
                          const x = traverseDOMTree(childNode);
                          ans['children'].push(x)
                        }
                      }
                      return ans;
    }
    

然后我们利用playwright去执行这一段js代码即可

    
    
    cssom_json = await page.evaluate(js_init_script.TraverseDOMTree.eval_traver_se_dom_tree_script())
    

获取到的结构为：

    
    
    "cssom_view": {
    "tag_name": "HTML",
    "attribute_content": "",
    "background_color": "rgba(0, 0, 0, 0)",
    "color": "rgb(0, 0, 0)",
    "display": "block",
    "font_size": "16px",
    "frameborder": "",
    "height": "251.312px",
    "href": null,
    "http_equiv": "",
    "language": "",
    "left": "auto",
    "position": "static",
    "scroll_delay": "",
    "src": "",
    "scroll_amount": "",
    "top": "auto",
    "width": "1280px",
    "visibility": "visible",
    "z_index": "auto",
    "children": []
    

children里面也是这样的结构。

# 检测过程

## 编写检测配置文件

首先，由于暗链的放置方法是无穷的，上面的例子只是其中一小部分，所以考虑使用poc的方式来动态配置检测的规则  
下面是根据上面的特征，编写的一些poc文件

### z-index类堆叠暗链

    
    
    nodes:
      - node_name: 'father-brother'
        css_rules:
          - css_name: 'z_index'
            value: '>100'
    rule_name: 'z-index类暗链'
    description: '用z-index属性堆叠遮挡，z-index值越小堆叠越靠后'

### 颜色

    
    
    nodes:
      - node_name: 'own'
        css_rules:
          - css_name: 'color'
            value: '=#ffffff'
    rule_name: '链接颜色和文字类暗链'
    description: '链接颜色与背景色相同或相似，color采用十六进制表达色彩'
    
    
    nodes:
      - node_name: 'own'
        css_rules:
          - css_name: 'color'
            value: '=transparent'
    rule_name: '链接颜色和文字类暗链'
    description: '链接颜色透明，color采用transparent值'
    
    
    nodes:
      - node_name: 'own'
        css_rules:
          - css_name: 'color'
            value: '=white'
    rule_name: '链接颜色和文字类暗链'
    description: '链接颜色与背景色相同或相似，color采用颜色英文名称表达色彩'

### 字体大小

    
    
    nodes:
      - node_name: 'own'
        css_rules:
          - css_name: 'font_size'
            value: '=0'
    rule_name: '链接颜色和文字类暗链'
    description: '链接文字设置为0，使得不可见'

### 跑马灯

    
    
    nodes:
      - node_name: 'father'
        tag_rules:
          - tag_name: 'marquee'
            attribute_name: 'scrolldelay'
            attribute_value: '>100'
    rule_name: 'marquee类暗链'
    description: '将marquee的scrolldelay属性值调为较大值，使跑马灯移动速度非常慢，很长时间都不会在屏幕中出现该链接，达到隐藏效果'
    
    
    nodes:
      - node_name: 'father'
        tag_rules:
          - tag_name: 'marquee'
            attribute_name: 'scrollamount'
            attribute_value: '>100'
    rule_name: 'marquee类暗链'
    description: '将marquee的scrollamount属性值调为较大值，使跑马灯移动速度超过人眼可见范围，达到隐藏效果'

### 可见性

    
    
    nodes:
      - node_name: 'own'
        css_rules:
          - css_name: 'position'
            value: '=absolute'
          - css_name: 'top'
            value: '<0'
          - css_name: 'left'
            value: '<0'
    rule_name: 'position位置类暗链'
    description: 'position位置样式，将元素的top、left位置设置成负数，让元素处于可视区外'
    
    
    nodes:
      - node_name: 'own'
        css_rules:
          - css_name: 'visibility'
            value: '=hidden'
    rule_name: 'visibility 隐藏类暗链'
    description: ''

## 解析检测配置文件，并进行检测

### 定义规则文件的结构

    
    
    public class DarkCheckRule {
        private String ruleName;
        private String description;
        private List<DarkCheckRuleNode> nodes;
    }
    
    public class DarkCheckRuleNode {
        private String nodeName;
        private List<DarkCheckNodeCssRule> cssRules;
        private List<DarkCheckNodeTag> tagRules;
    }
    
    public class DarkCheckNodeCssRule {
        private String cssName;
        private String value;
    }
    
    public class DarkCheckNodeTag {
        private String tagName;
        private String attributeName;
        private String attributeValue;
    }
    

规则分为两种，第一是检测最终css属性，第二是检测标签、属性和值。

### 将yml内容反序列化成规则对象

    
    
    // 读取文件内容
     public static String getFileContent(String fileName, Boolean absolutePath) {
            if (absolutePath) {
                try {
                    return getFileContent(new File(new File(".").getCanonicalPath() + "/" + fileName));
                } catch (IOException e) {
                    e.printStackTrace();
                }
                return "";
            } else {
                try {
                    return getFileContent(new File(fileName));
                }catch (Exception e){
                    e.printStackTrace();
                }
                return "";
            }
        }
    
    public static Map<String, Object> toMap(String yamlString) {
            Yaml yaml = new Yaml();
            return yaml.load(yamlString);
        }
    
    public static Map<String, Object> loadFromFile2Map(String fileName) {
            return toMap(FileUtils.getFileContent(fileName, false));
        }
    
    /**
         * 对象转换成Json
         *
         * @param object Object
         * @return String
         */
        public static String toJson(Object object) {
            StringWriter sw = new StringWriter();
            if (Objects.isNull(object)) {
                return EMPTY_JSON_OBJECT;
            }
            try {
                MAPPER.writeValue(MAPPER.getFactory().createGenerator(sw), object);
            } catch (Exception ex) {
                LOGGER.error("Object to json occur error, detail:", ex);
            }
            return sw.toString();
        }
    
    public static <T> T toObject(String jsonString, Class<T> tClass) {
            if (Objects.isNull(jsonString) || jsonString.trim().isEmpty()) {
                return null;
            }
            try {
                return MAPPER.readValue(jsonString, tClass);
            } catch (Exception ex) {
                ex.printStackTrace();
    //            LOGGER.error("Json to object occur error, detail:", ex);
            }
            return null;
        }
    

然后调用上述工具类

    
    
    DarkCheckRule darkCheckRule = Json.toObject(Json.toJson(YamlUtils.loadFromFile2Map(dir1.getAbsolutePath())), DarkCheckRule.class);
    

### 检测过程

首先，暗链肯定是链接，所以首先应该遍历这个cssom的json，然后找到A标签等于目标链接的，再对该标签进行特征检测

    
    
    if (cssomView.getTagName().equalsIgnoreCase("A")) {
                if (cssomView.getHref().equalsIgnoreCase(targetUrl)
                        || cssomView.getSrc().equalsIgnoreCase(targetUrl)) {
                    // TODO: 2023/5/10 开始检测
                    for (DarkCheckRule darkCheckRule : darkCheckRules) {
                        if (Boolean.TRUE.equals(check(darkCheckRule, cssomView))) {
                            // TODO: 2023/5/10 说明有匹配的
                            checkAns.add(darkCheckRule.getRuleName() + "-" + darkCheckRule.getDescription());
                        }
                    }
                }
                return;
            }
    

下面是检测某一个规则的方法

    
    
    public Boolean check(DarkCheckRule darkCheckRule, NewCssomView cssomView) {
            // TODO: 2023/5/10
            List<DarkCheckRuleNode> darkCheckRuleNodes = darkCheckRule.getNodes();
            int flag = 0;
            for (DarkCheckRuleNode darkCheckRuleNode : darkCheckRuleNodes) {
                if (Boolean.FALSE.equals(checkOneNode(darkCheckRuleNode, cssomView))) {
                    // TODO: 2023/5/10 需要都满足才行
                    flag = 1;
                    break;
                }
            }
            if (flag == 0) {
                return true;
            }
            return false;
        }
    
    /**
         * 检测规则中的某一个规则节点
         *
         * @param darkCheckRuleNode
         * @param cssomView
         * @return
         */
        public Boolean checkOneNode(DarkCheckRuleNode darkCheckRuleNode, NewCssomView cssomView) {
            List<DarkCheckNodeCssRule> darkCheckNodeCssRules = darkCheckRuleNode.getCssRules();
            if (darkCheckRuleNode.getNodeName().equalsIgnoreCase("own")) {
                // TODO: 2023/5/10 检测自己
                return getOneNodeResult(darkCheckRuleNode, cssomView);
            } else if (darkCheckRuleNode.getNodeName().equalsIgnoreCase("children")) {
                // TODO: 2023/5/15 获取所有本层子节点，不考虑递归，只要有一个满足即可
                for (NewCssomView newCssomView : cssomView.getChildren()) {
                    if (Boolean.TRUE.equals(getOneNodeResult(darkCheckRuleNode, newCssomView))) {
                        return true;
                    }
                }
                return false;
            } else if (darkCheckRuleNode.getNodeName().equalsIgnoreCase("father")) {
                // TODO: 2023/5/10 检测父级，只要有一个父级满足即可
                while (true) {
                    if (Objects.isNull(cssomView.getFather())) break;
                    if (Boolean.TRUE.equals(getOneNodeResult(darkCheckRuleNode, cssomView.getFather()))) {
                        return true;
                    }
    //                System.out.println("1");
                    return checkOneNode(darkCheckRuleNode, cssomView.getFather());
                }
                return false;
            } else if (darkCheckRuleNode.getNodeName().equalsIgnoreCase("brother")) {
                // TODO: 2023/5/10 检测同级节点
                // TODO: 2023/5/15 亲兄弟
                for (NewCssomView newCssomView : cssomView.getFather().getChildren()) {
                    if (Boolean.TRUE.equals(getOneNodeResult(darkCheckRuleNode,newCssomView))){
                        return true;
                    }
                }
                return false;
            } else if (darkCheckRuleNode.getNodeName().equalsIgnoreCase("father-brother")) {
                // TODO: 2023/5/15 父级的亲兄弟
                while (true){
                    if (Objects.isNull(cssomView.getFather()))break;
                    for (NewCssomView newCssomView : cssomView.getFather().getChildren()){
                        if (Boolean.TRUE.equals(getOneNodeResult(darkCheckRuleNode,newCssomView))){
                            return true;
                        }
                    }
                    return checkOneNode(darkCheckRuleNode,cssomView.getFather());
                }
                return false;
            }
            return false;
        }
    
    public Boolean getOneNodeResult(DarkCheckRuleNode darkCheckRuleNode, NewCssomView cssomView) {
            int flag = 0;
            // TODO: 2023/5/15检测完所有的CCSRULE
            if (Objects.nonNull(darkCheckRuleNode.getCssRules())){
                for (DarkCheckNodeCssRule darkCheckNodeCssRule : darkCheckRuleNode.getCssRules()) {
                    if (Boolean.FALSE.equals(checkOneCssRule(darkCheckNodeCssRule, cssomView))) {
                        flag = 1;
                        break;
                    }
                }
            }
            if (Objects.nonNull(darkCheckRuleNode.getTagRules())){
                for (DarkCheckNodeTag darkCheckNodeTag : darkCheckRuleNode.getTagRules()) {
    
                    if (Boolean.FALSE.equals(checkOneTagRule(darkCheckNodeTag, cssomView))) {
                        flag = 1;
                        break;
                    }
                }
            }
    
            if (flag == 0) {
                // TODO: 2023/5/10 都成功
                return true;
            }
            return false;
        }
    
    /**
         * 检测某一个css的结果
         *
         * @param darkCheckNodeCssRule
         * @param cssomView
         * @return
         */
        public Boolean checkOneCssRule(DarkCheckNodeCssRule darkCheckNodeCssRule, NewCssomView cssomView) {
            NewCssomView father = cssomView.getFather();
            cssomView.setFather(null);
            Map<String, Object> x = Json.toMap(Json.toJson(cssomView));
            cssomView.setFather(father);
            try {
                if (Objects.nonNull(x.get(darkCheckNodeCssRule.getCssName()))) {
                    String value = darkCheckNodeCssRule.getValue();
                    String aaa = (String) x.getOrDefault(darkCheckNodeCssRule.getCssName(), "0");
                    if (value.startsWith("<")) {
                        Integer xxx = MathUtils.toInt(aaa);
                        if (xxx < MathUtils.toInt(value)) {
                            return true;
                        }
                    }
                    if (value.startsWith(">")) {
                        Integer xxx = MathUtils.toInt(aaa);
    
                        if (xxx > MathUtils.toInt(value)) {
                            return true;
                        }
                    }
                    if (value.startsWith("=")) {
                        try {
                            if (aaa.toLowerCase().contains(value.substring(1).toLowerCase())) {
                                return true;
                            }
                        } catch (Exception e) {
                        }
                    }
                    if (value.equalsIgnoreCase("=")) {
                        Integer xxx = MathUtils.toInt(aaa);
                        if (xxx == MathUtils.toInt(value)) {
                            return true;
                        }
                    }
                }
            } catch (Exception e) {
            }
            return false;
        }
    
    public Boolean checkOneTagRule(DarkCheckNodeTag darkCheckNodeTag, NewCssomView cssomView) {
            NewCssomView father = cssomView.getFather();
            cssomView.setFather(null);
            Map<String, Object> x = Json.toMap(Json.toJson(cssomView));
            cssomView.setFather(father);
            try {
                if (Objects.nonNull(x.get("tag_name"))) {
                    String tagName = x.getOrDefault("tag_name", "").toString();
                    Integer trueNumber = 0;
                    String conditionValue = darkCheckNodeTag.getAttributeValue();
                    if (tagName.equalsIgnoreCase(darkCheckNodeTag.getTagName())) {
                        String conditionName = darkCheckNodeTag.getAttributeName();
                        if (conditionName.equalsIgnoreCase("scrollamount")) {
                            String trueValue = cssomView.getScrollAmount();
                            trueNumber = MathUtils.toInt(trueValue);
                        } else if (conditionName.equalsIgnoreCase("scrolldelay")) {
                            trueNumber = MathUtils.toInt(cssomView.getScrollDelay());
                        }
                    }
                    Integer conditionNumber = MathUtils.toInt(conditionValue);
                    if (conditionValue.startsWith(">")) {
                        if (trueNumber > conditionNumber) {
                            return true;
                        }
                    }
                    if (conditionValue.startsWith("<")) {
                        if (trueNumber < conditionNumber) {
                            return true;
                        }
                    }
                    if (conditionValue.startsWith("=")) {
                        if (trueNumber == conditionNumber) {
                            return true;
                        }
                    }
                }
            } catch (Exception e) {
            }
            return false;
    
        }
    

接下来要做的就是进一步完善检测poc即可

原文合集地址如下，  
[本文地址](https://mp.weixin.qq.com/s/2n2QPkuChzTCezseMHIwMQ)  
[合集地址](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzI5MjY4OTQ2Nw==&action=getalbum&album_id=2968591493596708865&scene=173&from_msgid=2247484203&from_itemidx=1&count=3&nolastread=1#wechat_redirect)

