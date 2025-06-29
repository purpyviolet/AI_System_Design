Page({
  data: {
    currentStep: 0,
    steps: [
      {
        title: '欢迎使用齿语舌观',
        description: '这是一个智能口腔健康管理助手，可以帮助您进行舌诊和牙齿诊疗。',
        image: '/images/logo.png'
      },
      {
        title: '智能问诊入口',
        description: '点击首页的"智能问诊"卡片，开始您的问诊之旅。',
        image: '/images/chat-icon.png'
      },
      {
        title: '选择问诊方向',
        description: '进入问诊界面后，请根据您的需求选择"舌诊"或"牙齿诊疗"方向。',
        image: '/images/welcome.png'
      },
      {
        title: '舌诊拍照示例',
        description: '拍摄时请在自然光下，张口自然，舌头平伸，避免遮挡。\n保证舌头清晰可见，避免模糊和过暗。',
        image: '/images/tongue-cover.png'
      },
      {
        title: '牙科拍照示例',
        description: '拍摄牙齿时请刷净牙齿，轻微张口，露出牙齿全貌。\n保持镜头对准牙齿，避免手指或其他物体遮挡。',
        image: '/images/tooth-cover.png'
      },
      {
        title: '开始问诊对话',
        description: '选择问诊方向后，您可以通过文字或语音输入问题，也可以上传口腔图片进行AI分析。',
        image: '/images/chat.png'
      },
      {
        title: '历史记录',
        description: '所有的问诊记录都会保存在"历史记录"中，您可以随时查看过去的诊疗情况。',
        image: '/images/history1.png'
      },
      {
        title: '历史分析',
        description: '在"历史分析"中，您可以查看健康趋势图表，了解口腔健康状况的变化。',
        image: '/images/analysis.png'
      }
    ]
  },

  onImageLoad(e) {
    // 图片加载成功
    console.log('图片加载成功');
  },

  onImageError(e) {
    // 图片加载失败
    console.error('图片加载失败');
    wx.showToast({
      title: '图片加载失败',
      icon: 'none'
    });
  },

  onLoad() {
    // 页面加载时的逻辑
  },

  nextStep() {
    if (this.data.currentStep < this.data.steps.length - 1) {
      this.setData({
        currentStep: this.data.currentStep + 1
      });
    } else {
      // 教程结束，返回首页
      wx.switchTab({
        url: '/pages/home/home'
      });
    }
  },

  prevStep() {
    if (this.data.currentStep > 0) {
      this.setData({
        currentStep: this.data.currentStep - 1
      });
    }
  },

  skipTutorial() {
    wx.switchTab({
      url: '/pages/home/home'
    });
  }
}); 