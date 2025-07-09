Page({
  data: {
    userInfo: null,
    hasUserInfo: false
  },

  onLoad() {
    // 检查是否已经登录
    this.checkLoginStatus();
  },

  // 检查登录状态
  checkLoginStatus() {
    const userInfo = wx.getStorageSync('userInfo')
    if (userInfo) {
      this.setData({
        userInfo: userInfo,
        hasUserInfo: true
      })
    } else {
       // 如果未登录，可以显示登录按钮或其他提示
       this.setData({
         userInfo: null,
         hasUserInfo: false
       })
    }
  },

  // 点击登录
  handleLogin() {
    if (!this.data.hasUserInfo) {
      wx.getUserProfile({
        desc: '用于完善用户资料',
        success: (res) => {
          const userInfo = res.userInfo
          // 将用户信息存储到本地或全局
          wx.setStorageSync('userInfo', userInfo)
          getApp().globalData.userInfo = userInfo; // 假设使用全局数据存储
          this.setData({
            userInfo: userInfo,
            hasUserInfo: true
          })
          wx.showToast({
            title: '登录成功',
            icon: 'success'
          })
        },
        fail: (err) => {
           console.error('获取用户信息失败', err);
           wx.showToast({
            title: '登录失败',
            icon: 'none'
          })
        }
      })
    }
  },

  // 跳转到个人资料页面
  navigateToProfileDetail() {
    // TODO: 实现跳转到个人资料详情页面的逻辑
    wx.showToast({
      title: '个人资料功能待开发',
      icon: 'none'
    });
  },

  // 跳转到设置页面
  navigateToSettings() {
    // TODO: 实现跳转到设置页面的逻辑
     wx.showToast({
      title: '设置功能待开发',
      icon: 'none'
    });
  },

  // 跳转到意见反馈页面
  navigateToFeedback() {
    // TODO: 实现跳转到意见反馈页面的逻辑
     wx.showToast({
      title: '意见反馈功能待开发',
      icon: 'none'
    });
  },

  // 跳转到联系我们页面
  navigateToContact() {
    // TODO: 实现跳转到联系我们页面的逻辑
     wx.showToast({
      title: '联系我们功能待开发',
      icon: 'none'
    });
  },

  // 跳转到关于我们页面
  navigateToAbout() {
    // TODO: 实现跳转到关于我们页面的逻辑
     wx.showToast({
      title: '关于我们功能待开发',
      icon: 'none'
    });
  },

  // 处理退出登录
  handleLogout() {
    wx.showModal({
      title: '提示',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          // 清除本地存储的用户信息
          wx.removeStorageSync('userInfo');
          // 清除全局的用户信息（如果使用了全局存储）
          getApp().globalData.userInfo = null;
          this.setData({
            userInfo: null,
            hasUserInfo: false
          });
          wx.showToast({
            title: '退出成功',
            icon: 'success'
          });
        }
      }
    });
  }
}) 