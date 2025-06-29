// miniprogram/pages/detail/detail.js
Page({
  data: {
    record: {}, // 当前检查记录
    id: '' // 记录ID
  },

  onLoad(options) {
    if (options.id) {
      wx.request({
        url: `http://192.168.193.30:8080/api/history/${options.id}`,
        method: 'GET',
        success: (res) => {
          if (res.data && !res.data.error) {
            this.setData({ record: res.data });
          } else {
            wx.showToast({ title: '加载失败', icon: 'none' });
          }
        },
        fail: () => {
          wx.showToast({ title: '网络错误', icon: 'none' });
        }
      });
    } else {
      wx.showToast({
        title: '无效的记录ID',
        icon: 'error',
        complete: () => {
          setTimeout(() => {
            wx.navigateBack();
          }, 1500);
        }
      });
    }
  },

  // 加载记录详情
  loadRecordDetail(id) {
    wx.showLoading({ title: '加载中...' });
    
    // 模拟API请求
    setTimeout(() => {
      try {
        // 实际项目中应该从API获取数据
        const records = wx.getStorageSync('diagnosis_records') || [];
        const record = records.find(item => item.id === id);
        
        if (record) {
          this.setData({ record });
        } else {
          throw new Error('记录不存在');
        }
      } catch (error) {
        wx.showToast({
          title: '加载记录失败',
          icon: 'error'
        });
      } finally {
        wx.hideLoading();
      }
    }, 500);
  },

  // 格式化日期
  formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
  },

  // 返回上一页
  navigateBack() {
    wx.navigateBack();
  },

  // 生成报告
  generateReport() {
    wx.showLoading({ title: '生成中...' });
    
    // 模拟报告生成过程
    setTimeout(() => {
      wx.hideLoading();
      wx.showModal({
        title: '报告生成',
        content: '报告已生成，是否现在查看？',
        success: (res) => {
          if (res.confirm) {
            // 实际项目中应该跳转到报告页面
            wx.showToast({
              title: '报告功能即将上线',
              icon: 'none'
            });
          }
        }
      });
    }, 1500);
  }
});