// pages/home/home.js
Page({

  /**
   * 页面的初始数据
   */
  data: {
    toothStatus: {
      text: '—',
      tag: '—',
      tagClass: 'orange',
      progress: 0
    },
    tongueStatus: {
      text: '—',
      tag: '—',
      tagClass: 'red',
      progress: 0
    }
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {

  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady() {

  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow() {
    this.updateHealthPreview();
  },

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide() {

  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload() {

  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh() {

  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom() {

  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage() {

  },

  updateHealthPreview() {
    const that = this;
    wx.request({
      url: 'http://192.168.193.30:8080/api/history',
      method: 'GET',
      success(res) {
        if (Array.isArray(res.data)) {
          // 取最新的牙齿和舌头记录
          const tooth = res.data.filter(r => r.check_type === 'tooth').pop();
          const tongue = res.data.filter(r => r.check_type === 'tongue').pop();
          // 牙齿
          if (tooth && tooth.report && tooth.report.sections) {
            const main = tooth.report.sections[1]; // 取"患者情况"
            let tag = '需关注', tagClass = 'orange', progress = 60;
            let text = main && main.body ? main.body : '';
            // 只提取"诊断：XXX"中的XXX
            let match = text.match(/诊断[:：]([\u4e00-\u9fa5A-Za-z]+)/);
            if (match) {
              text = match[1];
            } else {
              // 兼容"存在XXX"
              let m2 = text.match(/存在([\u4e00-\u9fa5A-Za-z]+)/);
              if (m2) text = m2[1];
            }
            if (main && main.body) {
              if (main.body.includes('健康')) { tag = '良好'; tagClass = 'green'; progress = 90; }
              if (main.body.includes('严重') || main.body.includes('龋齿')) { tag = '需改善'; tagClass = 'red'; progress = 40; }
              that.setData({
                toothStatus: {
                  text,
                  tag, tagClass, progress
                }
              });
            }
          }
          // 舌头
          if (tongue && tongue.report && tongue.report.sections) {
            const main = tongue.report.sections[1];
            let tag = '需改善', tagClass = 'red', progress = 40;
            let text = main && main.body ? main.body : '';
            // 始终显示四项关键词（舌色、苔色、苔厚薄、腐腻），未识别到则为'-'
            let tongueColor = '-', coatingColor = '-', thickness = '-', rotGreasy = '-';
            let m1 = text.match(/(淡白舌|淡红舌|红舌|绛舌|青紫舌)/);
            if (m1) tongueColor = m1[1];
            let m2 = text.match(/(白苔|黄苔|黑苔|灰黑苔)/);
            if (m2) coatingColor = m2[1];
            let m3 = text.match(/(薄苔|厚苔)/);
            if (m3) thickness = m3[1];
            let m4 = text.match(/(腻苔|非腻苔)/);
            if (m4) rotGreasy = m4[1];
            let summary = `${tongueColor} ${coatingColor} ${thickness} ${rotGreasy}`;
            if (main && main.body) {
              if (main.body.includes('健康')) { tag = '良好'; tagClass = 'green'; progress = 90; }
              if (main.body.includes('关注')) { tag = '需关注'; tagClass = 'orange'; progress = 60; }
              that.setData({
                tongueStatus: {
                  text: summary,
                  tag, tagClass, progress
                }
              });
            }
          }
        }
      }
    });
  },

  // 打开教程页面
  openTutorial() {
    wx.redirectTo({
      url: '/pages/tutorial/tutorial',
      fail: (err) => {
        console.error('跳转失败：', err);
        wx.showToast({
          title: '跳转失败',
          icon: 'none'
        });
      }
    });
  },
})