Page({
  data: {
    historyList: []
  },

  onShow() {
    this.fetchHistory();
  },

  fetchHistory() {
    wx.showLoading({ title: '加载中...' });
    wx.request({
      url: 'http://192.168.193.30:8080/api/history',
      method: 'GET',
      success: (res) => {
        if (res.statusCode === 200 && Array.isArray(res.data)) {
          const formattedData = res.data.map(item => {
            // 格式化时间
            if (item.created_at) {
              const date = new Date(item.created_at);
              item.created_at = `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
            }
            // 修正图片路径为完整URL
            if (item.image_url) {
              if (item.image_url.startsWith('/static/uploads/')) {
                item.image_url = 'http://192.168.193.30:8080' + item.image_url;
              } else if (item.image_url.startsWith('/uploads/')) {
                item.image_url = 'http://192.168.193.30:8080' + item.image_url;
              } else if (item.image_url.startsWith('D:')) {
                // 兼容绝对路径，取文件名拼接
                const filename = item.image_url.split('\\').pop().split('/').pop();
                item.image_url = 'http://192.168.193.30:8080/static/uploads/' + filename;
              }
            }
            // 为每个 section 添加 isExpanded 属性，默认不展开
            if (item.report && item.report.sections && Array.isArray(item.report.sections)) {
               item.report.sections.forEach(section => {
                   section.isExpanded = false;
               });
            } else if (item.report && typeof item.report === 'string') {
                // 为了兼容旧数据，如果report是字符串，则将其作为description
                item.description = item.report;
            }
            return item;
          }).reverse(); // 最近的记录在最前

          this.setData({
            historyList: formattedData
          });
        } else {
          wx.showToast({ title: '加载历史记录失败', icon: 'none' });
        }
      },
      fail: (err) => {
        wx.showToast({ title: '网络错误，请稍后重试', icon: 'none' });
        console.error("获取历史记录失败", err);
      },
      complete: () => {
        wx.hideLoading();
      }
    });
  },

  toggleSection(e) {
    const { recordIndex, sectionIndex } = e.currentTarget.dataset;
    const historyList = this.data.historyList;
    const section = historyList[recordIndex].report.sections[sectionIndex];
    
    // 切换 isExpanded 状态
    section.isExpanded = !section.isExpanded;
    
    this.setData({
      historyList: historyList
    });
  },

  deleteRecord(e) {
    const { id } = e.currentTarget.dataset;
    wx.showModal({
      title: '确认删除',
      content: '确定要删除这条记录吗？',
      success: (res) => {
        if (res.confirm) {
          wx.showLoading({ title: '删除中...' });
          wx.request({
            url: `http://192.168.193.30:8080/api/history/${id}`,
            method: 'DELETE',
            success: (delRes) => {
              if (delRes.statusCode === 200 && delRes.data.success) {
                wx.showToast({ title: '删除成功', icon: 'success' });
                // 重新加载列表
                this.fetchHistory(); 
              } else {
                wx.showToast({ title: '删除失败', icon: 'none' });
              }
            },
            fail: () => {
              wx.showToast({ title: '请求失败', icon: 'none' });
            },
            complete: () => {
              wx.hideLoading();
            }
          });
        }
      }
    });
  }
});