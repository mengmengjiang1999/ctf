## 业务场景

二轮充电业务中，用户充电完成后在订单详情页展示订单相关信息，用户点击分享按钮唤起微信小程序分享菜单，将生成的图片海报分享给微信好友或者下载到本地，好友可通过扫描海报中的二维码加群领取优惠。

使用场景及功能：微信小程序 生成海报图片 分享好友 下载图片

使用技术：Taro vue vant canvas

## 实现效果图

![1684379980_6465994c3dd70582770ac.png!small?1684379980814](https://image.3001.net/images/20230518/1684379980_6465994c3dd70582770ac.png!small?1684379980814)

# 重点步骤拆分

1、封装一个海报分享组件 poster-share.vue

2、用 canvas 画图，将背景图、费用、二维码等信息绘制在一张图上，其中费用、二维码是动态获取的

3、生成一张本地缓存图片

4、唤起微信分享功能，实现分享和下载功能

重点步骤有了，那么就开干吧！

## 核心代码实现

### 1、模版部分

需要一个画布 dom 用来绘制图片，一个用来存放生成图片的 dom

问：canvasId 为什么需要动态生成呢？

答：避免一个页面中使用多个组件引起的 canvasId 重复问题

    
    
    <template>
      <div class="poster-share__content">
        <!-- canvas生成的海报图片 -->
        <img
          v-if="posterImg"
          class="poster-share__content--img"
          mode="aspectFit"
          :src="posterImg"
        >
        <!-- 分享海报canvas绘制部分 -->
        <canvas
          class="poster-share__content--cvs"
          :canvas-id="canvasId"
        ></canvas>
      </div>
    </template>
    

### 2、样式部分

该业务场景下，不能让用户看到画布，但是设置 canvas 的 display 为 none 将不能进行绘制，会报如下错误，导致绘制失败。

![1684380000_646599601de45eb1843ec.png!small?1684380000808](https://image.3001.net/images/20230518/1684380000_646599601de45eb1843ec.png!small?1684380000808)

实现方式：采用定位的方式，将 canvas 定位到可视区域外，具体代码如下。

    
    
    .poster-share__content {
      position: absolute;
      right: -9999px;
      top: -9999px;
      width: 560px;
      height: 852px;
      opacity: 0;
      z-index: -1;
    
      &--img {
        width: 100%;
        height: 100%;
      }
    
      &--cvs {
        width: 100%;
        height: 100%;
      }
    }
    
    
    

### 3、核心 js 部分

开始写核心实现啦～

父组件传参控制子组件是否开始绘制，子组件绘制完成后通知父组件改变状态。

    
    
    name: 'CpPosterShare',
      model: {
        prop: 'value',
        event: 'update:value',
      },
      props: {
        value: {
          type: Boolean,
          default: false,
        },
        config: {
          type: Object,
          default: () => ({}),
        },
      },
      data () {
        return {
          isDraw: false, // 是否开始绘制海报
          posterImg: '', // 生成的海报图片地址
          canvasId: `canvasId${ Math.random() }`,
          screenWidth: null, // 屏幕宽度
        }
      },
      watch: {
        value: {
          handler (val) {
            this.isDraw = val
          },
          immediate: true,
        },
        isDraw (val) {
          this.$emit('update:value', val)
          if (val) {
            this.init()
          }
        },
      },
    

首先，我们做的是一个小程序，将图片放在小程序源码中会加大包的体积，需要从网络上下载图片，因此需要封装一个公共的方法来获取图片的信息。Taro 提供
getImageInfo 方法返回图片的原始宽高、本地路径等信息。

    
    
    // 加载图片
    loadImg (src) {
      return newPromise((resolve, reject) => {
        Taro.getImageInfo({
          src,
        }).then((res) => {
          resolve({ ...res })
        }).catch((err) => {
          reject(err)
        })
      })
    }
    
    
    

该业务场景中涉及绘制多张图片，包括背景图片和二维码图片，需要将多张图片都 load 完成后才能开始绘制。

    
    
    const promiseParams = [this.loadImg(BgImage), this.loadImg(QRcode)]
    const promiseAll = Promise.all(promiseParams.map((item) =>item.catch(() =>null)))
    
    promiseAll.then((res) => {
      this.draw(res)
    }).catch((err) => {
      console.log(err)
    })
    

开始绘制啦～

创建 canvas 绘图上下文 CanvasContext 对象，调用 Taro 提供的方法 Taro.createCanvasContext
(canvasId) 绘制背景图、绘制价格、绘制二维码，这里就不一一赘述了。全部绘制完成后，将画布中的内容导出生成图片，Taro 提供了
canvasToTempFilePath 方法，需要在 draw () 回调中调用才能保证图片导出成功，返回生成图片的临时路径。

    
    
    ctx.draw(false, () => {
      Taro.canvasToTempFilePath({
        canvasId:this.canvasId,
      }).then((res) => {
        this.posterImg = res.tempFilePath
    
        // 唤起分享菜单
        this.showShareImageMenu()
      }).catch((err) => {
        console.log('海报生成失败', err)
        Taro.showToast({
          title: '海报生成失败',
          icon: 'error',
        })
      }).finally(() => {
        Taro.hideLoading()
        this.isDraw = false
      })
    })
    

本地图片生成成功后，唤起微信提供的分享菜单弹窗，可以将图片发送给朋友、收藏、保存到相册。Taro 提供 showShareImageMenu
方法唤起分享菜单弹窗，入参为本地图片路径。

    
    
    showShareImageMenu () {
      if (Taro.showShareImageMenu) {
        Taro.showShareImageMenu({
          path:this.posterImg,
        }).then().catch((err) => {
          console.log(err)
          const { errMsg } = err
          // 取消操作  errMsg === 'showShareImageMenu:fail cancel'
          // 拒绝授权  errMsg: "showShareImageMenu:fail auth deny"
          if (errMsg === 'showShareImageMenu:fail auth deny') {
            authorize({
              scope:'writePhotosAlbum',
              showModal:true,
              authName:'保存图片到相册',
              success: () => {
                this.downloadImg()
              },
            })
          }
        }).finally(() => {
          this.isDraw = false
        })
      } else {
        Taro.showToast({
          title:'小程序版本不支持该功能',
          icon:'error',
        })
      }
    }
    
    
    

用户点击发送给朋友，会调起微信对话框，将生成的海报图片粘贴分享给朋友；

点击收藏，会将海报图片添加到收藏列表中，方便下次查看；

点击保存到相册，会唤起保存图片授权弹窗，用户点击允许，会将海报图片保存在本地相册中。

![1684380020_6465997468ad0af109d24.png!small?1684380021066](https://image.3001.net/images/20230518/1684380020_6465997468ad0af109d24.png!small?1684380021066)

如果用户在保存图片授权弹窗中第一次点击拒绝，之后再次点击分享下载时，需要有授权提示弹窗，提示用户是否打开设置去授权，具体展示如下。

Taro 提供 Taro.openSetting 方法调起小程序设置页面，用户开启 “添加到相册” 授权后成功后，调用 Taro 提供的下载图片的方法
Taro.saveImageToPhotosAlbum 将图片下载到本地。

![1684380043_6465998b1390ec6057c27.png!small?1684380043531](https://image.3001.net/images/20230518/1684380043_6465998b1390ec6057c27.png!small?1684380043531)

其中判断用户是否开启授权的方法具体实现如下：

    
    
    /**
     * 权限获取流程
     * @param scope       权限英文名称
     * @param success     授权成功的回调
     * @param fail        授权失败的回调
     * @param showModal   授权失败是否展示对话框提示
     * @param authName    授权失败是否展示对话框提示展示的授权名称
     *  // 例子：开启用户的相册权限
        authorize({
          scope: 'writePhotosAlbum',
          showModal: true,
          authName: '保存图片到相册',
          success () {
            console.log('授权成功')
          },
        })
    */
    export async function authorize (options) {
      const {
        scope, success, fail, showModal = false, authName = '',
      } = options
      try {
        const scopeName = `scope.${ scope }`
        const auth = await Taro.getSetting()
        if (!auth.authSetting[scopeName]) {
          Taro.authorize({ scope: scopeName }).then((res) => {
            if (res.errMsg === 'authorize:ok' && success) success()
          }, () => {
            if (showModal && authName) {
              Taro.showModal({
                title: '授权提示',
                content: `您拒绝了${ authName }权限，是否打开设置去授权？`,
              }).then((res) => {
                if (res.confirm) {
                  Taro.openSetting().then((res2) => {
                    if (res2.authSetting[scopeName] && success) {
                      success()
                    } else if (fail) {
                      fail()
                    }
                  })
                } else {
                  fail && fail()
                }
              }).catch((res) => {
                fail && fail(res)
              })
            } else {
              fail && fail()
            }
          })
        } else {
          success && success()
        }
      } catch (err) {
        fail && fail(err)
      }
    }
    

至此，具体实现完结撒花～可以将组件用到页面中了

## 组件引用

    
    
    <poster-share
      v-model="draw"  // 是否开始绘制海报海报
      config="config"  // 海报配置信息
    />
    
    
    

## 问题记录

在开发过程中遇到了一些问题，记录一下

现象：点击分享，生成 canvas 图片。开发者工具上每次都正常，ios
机每次都正常，部分安卓机每次都正常，部分安卓机，点击分享之后取消，操作多次，有几次会生成图片失败

报错信息："errMsg": "canvasToTempFilePath:fail :create bitmap failed"

错误定位解决：canvas 需要一直显示，不能有 display：none 的情况

> 作者：京东零售 张梦雨
>
> 内容来源：京东云开发者社区

