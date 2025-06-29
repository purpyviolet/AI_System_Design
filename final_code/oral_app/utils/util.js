// miniprogram/utils/api.js
const BASE_URL = 'http://localhost:5000'; // Flask 后端地址

/**
 * API请求基础封装
 * @param {string} url - 请求路径
 * @param {string} method - 请求方法 (GET/POST/PUT/DELETE)
 * @param {object} data - 请求数据
 * @param {boolean} isFileUpload - 是否为文件上传
 * @returns {Promise} 返回Promise对象
 */
const request = (url, method, data = {}, isFileUpload = false) => {
  return new Promise((resolve, reject) => {
    // 显示加载指示器
    wx.showLoading({
      title: '加载中',
      mask: true
    });
    
    if (isFileUpload) {
      // 文件上传处理
      wx.uploadFile({
        url: BASE_URL + url,
        filePath: data.filePath,
        name: 'image',
        formData: {
          check_type: data.checkType
        },
        success: (res) => {
          wx.hideLoading();
          if (res.statusCode === 200) {
            try {
              resolve(JSON.parse(res.data));
            } catch (e) {
              resolve(res.data);
            }
          } else {
            handleApiError(res);
            reject(res.data);
          }
        },
        fail: (err) => {
          wx.hideLoading();
          handleNetworkError(err);
          reject(err);
        }
      });
    } else {
      // 普通请求处理
      wx.request({
        url: BASE_URL + url,
        method: method,
        data: data,
        header: {
          'Content-Type': 'application/json'
        },
        success: (res) => {
          wx.hideLoading();
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve(res.data);
          } else {
            handleApiError(res);
            reject(res.data);
          }
        },
        fail: (err) => {
          wx.hideLoading();
          handleNetworkError(err);
          reject(err);
        }
      });
    }
  });
};

/**
 * 处理API错误
 * @param {object} response - 响应对象
 */
const handleApiError = (response) => {
  let errorMsg = '请求失败';
  
  if (response.data) {
    try {
      const data = typeof response.data === 'string' ? JSON.parse(response.data) : response.data;
      errorMsg = data.error || data.msg || `服务器错误: ${response.statusCode}`;
    } catch (e) {
      errorMsg = `服务器错误: ${response.statusCode}`;
    }
  }
  
  wx.showToast({
    title: errorMsg,
    icon: 'none',
    duration: 3000
  });
};

/**
 * 处理网络错误
 * @param {object} error - 错误对象
 */
const handleNetworkError = (error) => {
  let errorMsg = '网络请求失败';
  
  if (error.errMsg) {
    if (error.errMsg.includes('timeout')) {
      errorMsg = '请求超时，请检查网络';
    } else if (error.errMsg.includes('fail')) {
      errorMsg = '无法连接服务器';
    }
  }
  
  wx.showToast({
    title: errorMsg,
    icon: 'none',
    duration: 3000
  });
};

// API接口集合
const api = {
  // 获取历史记录
  getHistory: () => {
    return request('/api/history', 'GET');
  },
  
  // 删除历史记录
  deleteHistory: (id) => {
    return request(`/api/history/${id}`, 'DELETE');
  },
  
  // 上传口腔图片
  uploadOralImage: (filePath, checkType) => {
    return request('/upload_image', 'POST', {
      filePath,
      checkType
    }, true);
  },
  
  // 与AI对话
  chatWithAI: (message) => {
    return request('/chat', 'POST', { message });
  },
  
  // 生成报告
  generateReport: (history) => {
    return request('/generate_report', 'POST', { history });
  },
  
  // 获取历史详情
  getHistoryDetail: (id) => {
    return new Promise((resolve, reject) => {
      wx.navigateTo({
        url: `/pages/detail/detail?id=${id}`,
        success: resolve,
        fail: reject
      });
    });
  }
};

export default api;