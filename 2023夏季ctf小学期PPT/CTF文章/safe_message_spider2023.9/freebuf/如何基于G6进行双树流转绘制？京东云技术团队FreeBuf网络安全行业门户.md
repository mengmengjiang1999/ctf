## 1\. 背景

  * 业务背景：CRM 系统随着各业务条线对线索精细化分配的诉求逐渐增加，各个条线的流向规则会越来越复杂，各个条线甚至整个 CRM 的线索流转规则急需一种树形的可视化的图来表达。

  * 技术背景：在开发之前考虑了三种方案，原生 canvas、fabric 以及 G6，三种方案各有优劣势

| 原生 canvas| fabric| G6  
---|---|---|---  
优点| 灵活、自由、可定制化非常强| 封装了 canvas 的 api，使用简单灵活| 提供了复杂树、图等 api，只需要按照文档配置即可  
缺点| 开发复杂、耗时| 对于构建大型树、图等复杂、耗时| 在开发前需要认真阅读 api 文档，上手慢  
  
通过上述表格对比就可以看出来，对于构建更为复杂的树、图等，G6 具备明显的优势，而且又有活跃的开源社区，为后续的维护升级提供了保证。

## 2\. 基础知识

![1685600743_647839e76573ecf1ce4c3.png!small?1685600744292](https://image.3001.net/images/20230601/1685600743_647839e76573ecf1ce4c3.png!small?1685600744292)

下面是关于本次双树流转绘制的几个核心概念，简单介绍一下，如有兴趣，还是建议阅读 G6 官方 API 文档

  * 图 Graph

通过 new G6.Graph (config) 进行图的实例化。其中参数 config 是 Object
类型的图的配置项，图的大部分功能可以通过该配置项进行全局配置。

如果是树图，需要使用 new G6.TreeGraph 方法进行实例化

    
    
    const graph = new G6.Graph({
      container: 'mountNode', // 指定图画布的容器 id，与第 9 行的容器对应
      // 画布宽高
      width: 800,
      height: 500,
    });
    // 读取数据
    graph.data(data);
    // 渲染图
    graph.render();
    

  * 图元素 - 节点

G6 的内置节点包括
circle，rect，ellipse，diamond，triangle，star，image，modelRect，donut（v4.2.5
起支持）。这些内置节点的默认样式分别如下图所示。

![1685601246_64783bdedbeff36773501.png!small?1685601247335](https://image.3001.net/images/20230601/1685601246_64783bdedbeff36773501.png!small?1685601247335)

内置节点配置

    
    
    const graph = new G6.Graph({
      container: 'mountNode',
      width: 800,
      height: 600,
      defaultNode: {
        type: 'circle', // 节点类型
        // ... 其他配置
      },
    });
    

自定义节点配置

    
    
    // 在节点配置中配置自定义节点名称以及尺寸
    defaultNode: {
           type: 'card-node',
           size: [338, 70],
    }
    // 使用G6.registerNode自定义节点，在自定义节点中可以自定义各种形状的图形，包括text等
    G6.registerNode('card-node', {
            draw: function drawShape(cfg, group) {
              const w = cfg.size[0];
              const h = cfg.size[1];
              group.addShape('rect', {
                attrs: {
                  x: -w / 2 - 2,
                  y: -(h - 30) / 2,
                  width: 6, //200,
                  height: h - 30, // 60
                  fill: '#3c6ef0',
                  radius: [0, 4, 4, 0]
                },
                name: 'mark-box',
                draggable: true,
              });
    

  * 图元素 - 边

G6 提供了 9 种内置边：

line：直线，不支持控制点；

polyline：折线，支持多个控制点；

arc：圆弧线；

quadratic：二阶贝塞尔曲线；

cubic：三阶贝塞尔曲线；

cubic-vertical：垂直方向的三阶贝塞尔曲线，不考虑用户从外部传入的控制点；

cubic-horizontal：水平方向的三阶贝塞尔曲线，不考虑用户从外部传入的控制点；

loop：自环。

![1685601266_64783bf27057f82f83808.png!small?1685601267106](https://image.3001.net/images/20230601/1685601266_64783bf27057f82f83808.png!small?1685601267106)

内置边配置

    
    
    const graph = new G6.Graph({
      container: 'mountNode',
      width: 800,
      height: 600,
      defaultEdge: {
        type: 'cubic',
        // 其他配置
      },
    });
    

自定义边配置

    
    
    在配置中引用自定义边
    defaultEdge: {
        type: 'hvh',
        // 其他配置
      }
    // 使用G6.registerEdge方法配置自定义边
    G6.registerEdge('hvh', {
      draw(cfg, group) {
        const startPoint = cfg.startPoint;
        const endPoint = cfg.endPoint;
        const shape = group.addShape('path', {
          attrs: {
            stroke: '#333',
            path: [
              ['M', startPoint.x, startPoint.y],
              ['L', endPoint.x / 3 + (2 / 3) * startPoint.x, startPoint.y], // 三分之一处
              ['L', endPoint.x / 3 + (2 / 3) * startPoint.x, endPoint.y], // 三分之二处
              ['L', endPoint.x, endPoint.y],
            ],
          },
          // 在 G6 3.3 及之后的版本中，必须指定 name，可以是任意字符串，但需要在同一个自定义元素类型中保持唯一性
          name: 'path-shape',
        });
        return shape;
      },
    });
    

  * 图布局 - 树图布局

树图 TreeGraph 布局方法总览

CompactBox Layout：紧凑树布局；

Dendrogram Layout：树状布局（叶子节点布局对齐到同一层）；

Indented Layout：缩进布局；

Mindmap Layout：脑图布局

    
    
    const graph = new G6.TreeGraph({
      container: 'mountNode',
      modes: {
        default: [
          {
            // 定义展开/收缩行为
            type: 'collapse-expand',
          },
          'drag-canvas',
        ],
      },
      // 定义布局
      layout: {
        type: 'dendrogram', // 布局类型
        direction: 'LR', // 自左至右布局，可选的有 H / V / LR / RL / TB / BT
        nodeSep: 50, // 节点之间间距
        rankSep: 100, // 每个层级之间的间距
        excludeInvisibles: true, // 布局计算是否排除掉隐藏的节点，v4.8.8 起支持
      },
    });
    

  * 交互与事件

全局事件

只要在画布上范围内发生均会被触发，如 mousedown，mouseup，click，mouseenter，mouseleave 等。

    
    
    graph.on('click', (ev) => {
      const shape = ev.target;
      const item = ev.item;
      if (item) {
        const type = item.getType();
      }
    });
    

canvas 事件

只在 canvas 空白处被触发，如 canvas:mousedown，canvas:click 等，以 canvas:eventName 为事件名称。

    
    
    graph.on('canvas:click', (ev) => {
      const shape = ev.target;
      const item = ev.item;
      if (item) {
        const type = item.getType();
      }
    });
    

节点 / 边 上的事件

例如 node:mousedown，edge:click,combo:click 等，以 type:eventName 为事件名称。

    
    
    graph.on('node:click', (ev) => {
      const node = ev.item; // 被点击的节点元素
      const shape = ev.target; // 被点击的图形，可根据该信息作出不同响应，以达到局部响应效果
      // ... do sth
    });
    
    graph.on('edge:click', (ev) => {
      const edge = ev.item; // 被点击的边元素
      const shape = ev.target; // 被点击的图形，可根据该信息作出不同响应，以达到局部响应效果
      // ... do sth
    });
    
    graph.on('combo:click', (ev) => {
      const combo = ev.item; // 被点击 combo 元素
      const shape = ev.target; // 被点击的图形，可根据该信息作出不同响应，以达到局部响应效果
      // ... do sth
    });
    

## 3\. 技术方案 & 实施

  * 数据准备

要求数据中每一个节点必须有 id，且 id 为字符串类型。module 字段 root 表示根节点，right 表示子节点，left
表示父节点。flowCountList 表示边，从某个节点到某个节点

    
    
    data: {
      id: '1',
      name: '根节点',
      flowInCount: 9999,
      flowOutCount: 9999,
      currentCount: 9999,
      module: 'root',
      children: [
        {
          id: '2',
          name: '右一节点',
          flowInCount: 9999,
          flowOutCount: 9999,
          currentCount: 9999,
          module: 'son',
        },
        {
          id: '3',
          name: '左一节点',
          flowInCount: 9999,
          flowOutCount: 9999,
          currentCount: 9999,
          module: 'father',
        }
      ]
    }
    flowCountList: [
        {
            fromPoolId: '1',
            toPoolId: '2',
            clueCount: 111
        },
        {
            fromPoolId: '1',
            toPoolId: '3',
            clueCount: 222
        }
    ]
    

  * 初始化 Minimap 实例

如果需要加 Minimap 可以在画布外层 div 中增加一个 div#minimap，将小地图放入其中。下面配置中 delegate
表示小地图只渲染画布中元素的框架，以此来降低性能损耗。

    
    
    const miniMap = document.getElementById('minimap');
    const minimap = new G6.Minimap({
        container: miniMap,
        type: 'delegate',
        size: [178, 138]
      });
    

  * 初始化树图

modes 中配置的 drag-canvas 表示支持画布拖拽，zoom-canvas 表示支持画布放大缩小，tooltip 表示给节点增加 tooltip
提示。

layout 中 getSide 方法会根据数据类型判断当前节点属于父节点还是子节点，本方法只针对根节点有效。

    
    
    this.graph = new G6.TreeGraph({
        container: 'clueCanvas',
        width：1000, // width和height可以根据自己画布大小进行赋值
        height：500,
        modes: {
          default: ['drag-canvas', 'zoom-canvas',{
            type: 'tooltip',
            formatText: function formatText(model) {
              return model.name;
            },
            shouldBegin: (e) => {
              const target = e.target;
              if (target.get('name') === 'title') return true;
              return false;
            },
          }],
        },
        defaultNode: {
          type: 'card-node',
          size: [338, 70],
        },
        defaultEdge: {
          type: 'custom-edge',
          style: {
            lineWidth: 4,
            lineAppendWidth: 8,
            stroke: '#BABEC7',
          }
        },
        layout: {
          type: 'mindmap',
          direction: 'H',
          getHeight: () => {return 70;}, //节点高度
          getWidth: () => {return 338;}, // 节点宽度
          getVGap: () => {return 8;}, // 节点之间的垂直间距
          getHGap: () => {return 100;}, // 节点之间的水平间距
          getSide: (d) => {
            if (d.data.module === 'father') {
              return 'left';
            }
            return 'right';
          },
        },
        plugins: [minimap]
      });
      this.graph.data(data);
      this.graph.render(); // 渲染
      this.graph.fitView(); // 全屏展示
    

  * 自定义节点

自定义节点是在默认节点不能满足我们的需求时，自己定义一些图形要素，可以单个的也可以是多个进行组合，如下图所示：

![1685601281_64783c01622962664ad6f.png!small?1685601282186](https://image.3001.net/images/20230601/1685601281_64783c01622962664ad6f.png!small?1685601282186)

由于篇幅有限，以下代码只展示了外边框和眼睛图标的绘制，其他元素的绘制基本类似。其中 setState 回调方法是监听状态变化的，比如本例中监听树节点展开 /
收起，进行眼睛图标的切换以及节点底色的变更逻辑。

    
    
    G6.registerNode('card-node', {
            draw: function drawShape(cfg, group) {
              const w = cfg.size[0];
              const h = cfg.size[1];
              const shape = group.addShape('rect', {
                attrs: {
                  x: -w / 2,
                  y: -h / 2,
                  width: w, //200,
                  height: h, // 60
                  radius: 8,
                  fill: 'l(0) 0:rgba(197,213,255,1) 0.3:rgba(226,233,253,1) 1:rgba(255,255,255,1)',
                  shadowOffsetX: -2,
                  shadowOffsetY: 0,
                  shadowColor: '#82A2F5',
                  shadowBlur: 0,
                  stroke: 'l(0) 0.1:rgba(138,169,249,1) 1:rgba(202,216,254,1)'
                },
                // must be assigned in G6 3.3 and later versions. it can be any string you want, but should be unique in a custom item type
                name: 'main-box',
                draggable: true,
              });
              cfg.children &&
                group.addShape('image', {
                  attrs: {
                    x: w / 2 - 35,
                    y: -h / 2 + 10,
                    cursor: 'pointer',
                    img: flowEyeOpen,//cfg.collapsed ? flowEyeOpen : flowEyeClose,
                    width: 16,
                    height: 16
                  },
                  name: 'collapse-icon',
                });
              return shape;
            },
            setState(name, value, item) {
              if (name === 'collapsed') {
                // 替换眼睛图标
                const marker = item.get('group').find((ele) => ele.get('name') === 'collapse-icon');
                const icon = value ? flowEyeClose : flowEyeOpen;
                marker.attr('img', icon);
                // 替换卡片背景
                const mainBox = item.get('group').find((ele) => ele.get('name') === 'main-box');
                const fill = value ? '#fff' : 'l(0) 0:rgba(197,213,255,1) 0.3:rgba(226,233,253,1) 1:rgba(255,255,255,1)'
                const shadowOffsetX = value ? 0 : -2
                mainBox.attr('fill', fill)
                mainBox.attr('shadowOffsetX', shadowOffsetX)
    
              }
            },
          });
    

  * 节点事件监听

当点击节点中的眼睛图标则执行展开 / 收起，并更新其状态，进行重绘。状态更新之后，上文中的 setState 回调函数就被出发，随后根据新的展开 /
收起状态对节点样式进行变更

    
    
    this.graph.on('node:click', (e) => {
        // 点击眼睛图标展开子节点
        if (e.target.get('name') === 'collapse-icon') {
          e.item.getModel().collapsed = !e.item.getModel().collapsed;
          this.graph.setItemState(e.item, 'collapsed', e.item.getModel().collapsed);
          this.graph.layout();
        }
      });
    

  * 自定义边

边的默认样式使用内置边 cubic-horizontal 类型，当鼠标移到边上时会出现一个数量数据如下图所示：

![1685601291_64783c0b01dded3c50570.png!small?1685601291524](https://image.3001.net/images/20230601/1685601291_64783c0b01dded3c50570.png!small?1685601291524)

当状态变为激活状态 active 时，将边上的元素透明度置为 1 可见，否则置为 0 不可见。默认为 0

    
    
    G6.registerEdge(
            'custom-edge',
            {
              afterDraw(cfg, group) {
                const source = cfg.sourceNode._cfg.model.id
                const target = cfg.targetNode._cfg.model.id
                let current = self.flowCountList.find(item=>{
                  return source === item.fromPoolId && target === item.toPoolId
                })
                // 如果未找到，在进行反向查一次
                if(!current) {
                  current = self.flowCountList.find(item=>{
                    return source === item.toPoolId && target === item.fromPoolId
                  })
                }
                // 获取图形组中的第一个图形，在这里就是边的路径图形
                const shape = group.get('children')[0];
                // 获取路径图形的中点坐标
                const midPoint = shape.getPoint(0.5);
                // 在中点增加一个矩形，注意矩形的原点在其左上角
                group.addShape('rect', {
                  attrs: {
                    width: 92,
                    height: 20,
                    fill: '#BABEC7',
                    stroke: '#868D9F',
                    lineWidth: 1,
                    radius: 10,
                    opacity: 0,
                    // x 和 y 分别减去 width / 2 与 height / 2，使矩形中心在 midPoint 上
                    x: midPoint.x - 92/2,
                    y: midPoint.y - 20/2,
                  },
                  name: 'edge-count', // 在 G6 3.3 及之后的版本中，必须指定 name，可以是任意字符串，但需要在同一个自定义元素类型中保持唯一性
                });
                group.addShape('text', {
                  attrs: {
                    textBaseline: 'top',
                    x: midPoint.x - 92/2 + 20,
                    y: midPoint.y - 12/2 + 1,
                    lineHeight: 12,
                    text: `流出 ${current ? current.clueCount : 0}`,
                    fontSize: 12,
                    fill: '#ffffff',
                    opacity: 0,
                  },
                  name: 'edge-text',
                });
              },
              // // 响应状态变化
              setState(name, value, item) {
                if (name === 'active') {
                  const edgeCount = item.get('group').find((ele) => ele.get('name') === 'edge-count');
                  const edgeText = item.get('group').find((ele) => ele.get('name') === 'edge-text');
                  edgeCount.attr('opacity', value ? 1 : 0)
                  edgeText.attr('opacity', value ? 1 : 0)
                }
              },
            },
            'cubic-horizontal',
          );
    

  * 边事件监听

监听边的 mouseenter 和 mouseleave 事件，更新其激活状态

    
    
    this.graph.on('edge:mouseenter', (ev) => {
        const edge = ev.item;
        this.graph.setItemState(edge, 'active', true);
      });
    
      this.graph.on('edge:mouseleave', (ev) => {
        const edge = ev.item;
        this.graph.setItemState(edge, 'active', false);
      });
    

到此双数渲染逻辑介绍完毕，如果有类似案例，欢迎参考

## 4\. 踩坑记录

  * 缩进树 - 顶部对齐，左侧树不会对齐

配置如下 indented 表示缩进树，dropCap 置为 false 表示关闭下垂树，只有右侧树时，显示正常，如果双树渲染，左侧树不会缩进，属于 g6
本身的 bug

    
    
    layout: {
        type: 'indented',
        dropCap: false,
      },
    

![1685601313_64783c214ad734d1a4f35.png!small?1685601313668](https://image.3001.net/images/20230601/1685601313_64783c214ad734d1a4f35.png!small?1685601313668)

  * 初次加载树结构，限制只展开两级只需要在二级节点增加属性 collapsed : true 数据结构如下:

    
    
    {
        id: '1',
        children: [{
            id: '1-1',
            children: [{
                id: '1-1-1',
                collapsed: true
            }]
        }]
    }
    

![1685601323_64783c2b756ea9a7276cf.png!small?1685601323922](https://image.3001.net/images/20230601/1685601323_64783c2b756ea9a7276cf.png!small?1685601323922)

  * 一个节点有两个局部区域增加 tooltip

    
    
    const tooltip = new G6.Tooltip({
        className: 'g6-tooltip',
        offsetX: -5,
        offsetY: -165,
        getContent(e) {
          return '111'
        },
        shouldBegin(e){
          return true
        },
        itemTypes: ['node']
    });
    // 增加tooltip插件来实现一个节点多个局部区域增加tooltip
    plugins: [tooltip,tooltip1]
    

  * 关于编译报错的问题

由于我本地 ts 版本太低，导致 ts 在对 g6 进行代码检查时报错，具体报错信息如下截图：

![1685601337_64783c3984923a8b3fd4e.png!small?1685601337894](https://image.3001.net/images/20230601/1685601337_64783c3984923a8b3fd4e.png!small?1685601337894)

原因分析：

g6 代码库用到了 ts 的高级语法，导致当前低版本 ts 在对其进行检查时未通过

解决方法：

（1）. 在 tsconfig.json 中增加 "skipLibCheck": true 跳过 ts
的检查，但是发现测试环境和预发环境编译通过，上线时使用 npm run build 编译不成功

![1685601347_64783c43029fe3851344f.png!small?1685601347400](https://image.3001.net/images/20230601/1685601347_64783c43029fe3851344f.png!small?1685601347400)

（2）. 升级 ts 版本，将当前使用的 3.5.3 升级至最新版，发现虽然上述问题解决了，但是系统中其他地方有报错，为了降低上线的风险，放弃了这种方式

（3）. 降级 @antv/g6 的版本，使其从最新版本降到了 4.3.4，最后发现可行，编译没有任何问题，而且功能运行正常，体验较差的是 @antv/g6
关于每一个版本的升级都没有提及这个问题，所以需要按版本试验，整整折腾了一天才找到这个版本，后续如果有人遇到这个问题可以进行借鉴

![1685601357_64783c4d189565e00a276.png!small?1685601357475](https://image.3001.net/images/20230601/1685601357_64783c4d189565e00a276.png!small?1685601357475)

## 5\. 成果展示

  * 全局展示

![1685601367_64783c572e85985a7547e.png!small?1685601368483](https://image.3001.net/images/20230601/1685601367_64783c572e85985a7547e.png!small?1685601368483)

  * 局部展示

![1685601377_64783c61db94c4f4aed5f.png!small?1685601378565](https://image.3001.net/images/20230601/1685601377_64783c61db94c4f4aed5f.png!small?1685601378565)

> 作者：京东物流 田雷雷
>
> 来源：京东云开发者社区

