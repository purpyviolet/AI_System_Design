Page({
  data: {
    activeTab: 'tongue', // 默认显示舌诊资讯
    newsList: {
      tongue: [
        {
          id: 1,
          type: 'article',
          title: '舌诊基础知识讲解',
          cover: '/images/tongue_1.png',
          author: '张医生',
          date: '2024-03-20',
          views: 1234,
          description: '详细介绍舌诊的基本原理和常见舌象的识别方法',
          url: 'https://www.zhongyi.com/tongue-diagnosis-basics'
        },
        {
          id: 2,
          type: 'article',
          title: '舌诊在中医诊断中的重要性',
          cover: '/images/tongue-article-cover.png',
          author: '李教授',
          date: '2024-03-19',
          views: 856,
          description: '探讨舌诊在中医诊断体系中的重要地位和临床应用',
          url: 'https://www.tcm.com/tongue-diagnosis-importance'
        },
        
      ],
      tooth: [
        {
          id: 5,
          type: 'article',
          title: '牙齿日常护理指南',
          cover: '/images/tooth-video-cover.gif',
          author: '王医生',
          date: '2024-03-18',
          views: 2345,
          description: '专业牙医教你如何正确护理牙齿，预防口腔疾病',
          url: 'https://www.dental-care.com/daily-care-guide'
        },
        {
          id: 6,
          type: 'article',
          title: '最新口腔医疗技术进展',
          cover: '/images/tooth-article-cover.png',
          author: '陈博士',
          date: '2024-03-17',
          views: 1567,
          description: '介绍口腔医疗领域的最新技术发展和应用',
          url: 'https://www.dental-tech.com/latest-advances'
        },
      ]
    }
  },

  // 切换标签
  switchTab(e) {
    const tab = e.currentTarget.dataset.tab
    this.setData({
      activeTab: tab
    })
  },

  // 查看详情
  viewDetail(e) {
    const { id, type, url } = e.currentTarget.dataset
    
    if (url) {
      // 如果有外部链接，复制到剪贴板
      wx.setClipboardData({
        data: url,
        success: () => {
          wx.showModal({
            title: '链接已复制',
            content: '文章链接已复制到剪贴板，请在浏览器中打开查看',
            showCancel: false
          });
        }
      });
    } else {
      // 如果没有链接，显示提示
      wx.showToast({
        title: '暂无详细内容',
        icon: 'none'
      });
    }
  },

  // 播放视频
  playVideo(e) {
    const { url } = e.currentTarget.dataset
    wx.navigateTo({
      url: `/pages/news/video/video?url=${encodeURIComponent(url)}`
    })
  },

  // 下拉刷新
  onPullDownRefresh() {
    // 模拟刷新数据
    setTimeout(() => {
      wx.stopPullDownRefresh()
      wx.showToast({
        title: '刷新成功',
        icon: 'success'
      })
    }, 1000)
  },

  // 上拉加载更多
  onReachBottom() {
    wx.showLoading({
      title: '加载中...'
    })
    // 模拟加载更多数据
    setTimeout(() => {
      wx.hideLoading()
      wx.showToast({
        title: '没有更多内容了',
        icon: 'none'
      })
    }, 1000)
  }
}) 