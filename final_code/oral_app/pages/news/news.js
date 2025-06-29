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
        {
          id: 3,
          type: 'article',
          title: '智能舌诊系统：AI技术助力中医现代化',
          cover: '/images/tongue-ai.png',
          author: '王博士',
          date: '2024-03-18',
          views: 2345,
          description: '基于深度学习的智能舌诊系统，推动中医舌诊客观化、智能化发展',
          url: 'https://www.ai-medicine.com/smart-tongue-diagnosis'
        },
        {
          id: 4,
          type: 'article',
          title: '舌苔变化与身体健康的关系',
          cover: '/images/tongue_2.png',
          author: '陈医生',
          date: '2024-03-17',
          views: 1567,
          description: '解析不同舌苔类型对应的身体状况和调理建议',
          url: 'https://www.health.com/tongue-coating-health'
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
        {
          id: 7,
          type: 'article',
          title: '2025年"全国爱牙日"宣传主题发布',
          cover: '/images/aiya.png',
          author: '国家卫健委',
          date: '2025-09-20',
          views: 3200,
          description: '今年"全国爱牙日"主题为"口腔健康全身健康"，副主题"全生命周期守护让健康从\'齿\'开始"',
          url: 'https://wjw.fj.gov.cn/xxgk/gzdt/mtbd/202409/t20240906_6512495.htm'
        },
        {
          id: 8,
          type: 'article',
          title: '儿童口腔健康：儿科医生干预可提升看牙率',
          cover: '/images/child_tooth.png',
          author: '美国牙科研究所',
          date: '2024-03-15',
          views: 1780,
          description: '研究显示，儿科医生在体检时加强口腔健康教育和转诊，可显著提升儿童看牙率',
          url: 'https://www.nidcr.nih.gov/news-events/nidcr-news/2024/dental-visits-increase-support-pediatric-providers'
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