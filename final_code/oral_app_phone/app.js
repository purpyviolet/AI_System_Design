// miniprogram/app.js
App({
  // 全局数据对象
  globalData: {
    userInfo: null,
    token: null,
    history: [],
    isLoggedIn: false
  },
  
  // 小程序初始化完成时执行
  onLaunch() {
    // 只做初始化，不做页面跳转
    const isLoggedIn = wx.getStorageSync('isLoggedIn');
    const username = wx.getStorageSync('username');
    if (isLoggedIn && username) {
      this.globalData.isLoggedIn = true;
      this.globalData.userInfo = { username };
    }
    const token = wx.getStorageSync('token');
    if (token) {
      this.globalData.token = token;
    }
    wx.getSetting({
      success: res => {
        if (res.authSetting['scope.userInfo']) {
          wx.getUserInfo({
            success: res => {
              this.globalData.userInfo = res.userInfo;
            }
          })
        }
      }
    })
  },
  
  // 登录方法
  login(callback) {
    wx.login({
      success: res => {
        // 发送 res.code 到后台换取 openId, sessionKey, unionId
        wx.request({
          url: 'https://your-api.com/api/login',
          method: 'POST',
          data: { code: res.code },
          success: res => {
            const token = res.data.token;
            this.globalData.token = token;
            wx.setStorageSync('token', token);
            callback && callback();
          }
        })
      }
    })
  }
})