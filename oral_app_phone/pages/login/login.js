Page({
  data: {
    username: '',
    password: '',
    confirmPassword: '',
    activeTab: 'login'  // 默认显示登录标签
  },

  onLoad() {
    console.log('登录页面加载完成')
  },

  onUsernameInput(e) {
    console.log('用户名输入：', e.detail.value)
    this.setData({
      username: e.detail.value
    })
  },

  onPasswordInput(e) {
    console.log('密码输入：', e.detail.value)
    this.setData({
      password: e.detail.value
    })
  },

  onConfirmPasswordInput(e) {
    console.log('确认密码输入：', e.detail.value)
    this.setData({
      confirmPassword: e.detail.value
    })
  },

  switchTab(e) {
    console.log('切换标签：', e.currentTarget.dataset.tab)
    const tab = e.currentTarget.dataset.tab
    this.setData({
      activeTab: tab,
      username: '',
      password: '',
      confirmPassword: ''
    })
  },

  handleSubmit() {
    console.log('提交按钮被点击')
    const { username, password, confirmPassword, activeTab } = this.data
    
    if (!username || !password) {
      wx.showToast({
        title: '请输入用户名和密码',
        icon: 'none'
      })
      return
    }

    if (activeTab === 'register') {
      if (!confirmPassword) {
        wx.showToast({
          title: '请确认密码',
          icon: 'none'
        })
        return
      }
      if (password !== confirmPassword) {
        wx.showToast({
          title: '两次密码输入不一致',
          icon: 'none'
        })
        return
      }
      this.handleRegister()
    } else {
      this.handleLogin()
    }
  },

  handleLogin() {
    console.log('执行登录操作')
    const { username, password } = this.data
    
    // 从本地存储获取用户信息
    const users = wx.getStorageSync('users') || []
    const user = users.find(u => u.username === username && u.password === password)
    
    if (user) {
      // 登录成功
      wx.setStorageSync('isLoggedIn', true)
      wx.setStorageSync('username', username)
      
      wx.showToast({
        title: '登录成功',
        icon: 'success',
        duration: 1500,
        success: () => {
          setTimeout(() => {
            wx.switchTab({
              url: '/pages/home/home',
              fail: (err) => {
                console.error('跳转失败：', err)
                wx.showToast({
                  title: '跳转失败，请重试',
                  icon: 'none'
                })
              }
            })
          }, 1500)
        }
      })
    } else {
      wx.showToast({
        title: '用户名或密码错误',
        icon: 'none'
      })
    }
  },

  handleRegister() {
    console.log('执行注册操作')
    const { username, password } = this.data
    
    // 获取已存在的用户列表
    const users = wx.getStorageSync('users') || []
    
    // 检查用户名是否已存在
    if (users.some(u => u.username === username)) {
      wx.showToast({
        title: '用户名已存在',
        icon: 'none'
      })
      return
    }
    
    // 添加新用户
    users.push({
      username,
      password
    })
    
    // 保存用户信息
    wx.setStorageSync('users', users)
    
    wx.showToast({
      title: '注册成功',
      icon: 'success',
      duration: 1500,
      success: () => {
        // 注册成功后自动切换到登录标签
        setTimeout(() => {
          this.setData({
            activeTab: 'login',
            username: '',
            password: '',
            confirmPassword: ''
          })
        }, 1500)
      }
    })
  }
})