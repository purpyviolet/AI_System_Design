Page({
  data: {
      userInfo: null,
      showTypeModal: true,
      chosenType: '',
      messages: [],
      inputValue: '',
      showChatTypeModal: false,
      chatType: '',
      isRecording: false,  // 添加录音状态
      recorderManager: null,  // 录音管理器
      historyList: [],
      uploadedImagePath: null
  },

  onLoad() {
      // 初始化录音管理器
      const recorderManager = wx.getRecorderManager();
      
      // 配置录音管理器
      recorderManager.onStart(() => {
        console.log('录音开始');
        this.setData({ isRecording: true });
        wx.showToast({
          title: '正在录音...',
          icon: 'none',
          duration: 60000
        });
      });

      recorderManager.onStop((res) => {
        console.log('录音结束', res);
        this.setData({ isRecording: false });
        wx.hideToast();
        
        // 上传录音文件到后端
        this.uploadAudioFile(res.tempFilePath);
      });

      recorderManager.onError((res) => {
        console.error('录音错误：', res);
        this.setData({ isRecording: false });
        wx.showToast({
          title: '录音失败，请重试',
          icon: 'none'
        });
      });

      this.setData({ recorderManager });

      wx.request({
        url: 'http://192.168.193.30:8080/api/history', // 后端接口地址
        method: 'GET',
        success: (res) => {
          if (res.data && Array.isArray(res.data)) {
            this.setData({ historyList: res.data.reverse() }); // 新的在前
          } else {
            wx.showToast({ title: '加载历史失败', icon: 'none' });
          }
        },
        fail: () => {
          // wx.showToast({ title: '', icon: 'none' });
        }
      });
  },

  // 开始录音
  startRecording() {
    const { recorderManager } = this.data;
    const options = {
      duration: 60000, // 最长录音时间，单位ms
      sampleRate: 16000,
      numberOfChannels: 1,
      encodeBitRate: 48000,
      format: 'wav',
      frameSize: 50
    };
    
    // 请求录音权限
    wx.authorize({
      scope: 'scope.record',
      success: () => {
        recorderManager.start(options);
      },
      fail: () => {
        wx.showToast({
          title: '请授权录音权限',
          icon: 'none'
        });
      }
    });
  },

  // 停止录音
  stopRecording() {
    const { recorderManager } = this.data;
    recorderManager.stop();
  },

  // 上传录音文件到后端
  uploadAudioFile(tempFilePath) {
    wx.showLoading({ title: '正在识别...' });

    wx.uploadFile({
      url: 'http://192.168.193.30:8080/api/upload_audio',  // 替换为你的后端服务器地址
      filePath: tempFilePath,
      name: 'audio',
      formData: {
        check_type: this.data.chosenType || 'tongue'  // 传递当前选择的诊断类型
      },
      success: (res) => {
        try {
          const result = JSON.parse(res.data);
          if (result.recognition_result) {
            // 将识别结果显示在输入框中
            this.setData({
              inputValue: result.recognition_result
            });
            
            // 如果后端直接返回了AI回复，显示在对话中
            if (result.response) {
              this.addMessage({
                type: 'text',
                content: result.recognition_result,
                role: 'user'
              });
              this.addMessage({
                type: 'text',
                content: result.response,
                role: 'assistant'
              });
            }
          } else {
            wx.showToast({
              title: '语音识别失败',
              icon: 'none'
            });
          }
        } catch (e) {
          console.error('语音识别结果解析失败：', e);
          wx.showToast({
            title: '语音识别异常',
            icon: 'none'
          });
        }
      },
      fail: (err) => {
        console.error('上传失败：', err);
        wx.showToast({
          title: '语音上传失败',
          icon: 'none'
        });
      },
      complete: () => {
        wx.hideLoading();
      }
    });
  },

  // 语音输入按钮点击处理
  onVoiceInput() {
    if (this.data.isRecording) {
      this.stopRecording();
    } else {
      this.startRecording();
    }
  },

  checkLoginStatus() {
      // 从全局获取用户信息或检查登录状态
      const app = getApp();
      if (app.globalData.userInfo) {
          this.setData({
              userInfo: app.globalData.userInfo
          });
      } else {
          // 如果未登录，可以跳转到登录页面或显示登录按钮
          wx.showToast({
              title: '请先登录',
              icon: 'none',
              duration: 2000
          });
      }
  },

  navigateToUpload(e) {
      const checkType = e.currentTarget.dataset.type;
      if (!this.data.userInfo) {
          wx.navigateTo({
              url: '/pages/login/login'
          });
          return;
      }
      
      wx.navigateTo({
          url: `/pages/upload/upload?type=${checkType}`
      });
  },

  navigateToChat() {
      if (!this.data.userInfo) {
          wx.navigateTo({
              url: '/pages/login/login'
          });
          return;
      }
      this.setData({ showChatTypeModal: true });
  },

  navigateToHistory() {
      if (!this.data.userInfo) {
          wx.navigateTo({
              url: '/pages/login/login'
          });
          return;
      }
      
      wx.navigateTo({
          url: '/pages/history/history'
      });
  },

  chooseType(e) {
    const type = e.currentTarget.dataset.type;
    this.setData({
      chosenType: type,
      showTypeModal: false
    });
    // 可选：提示用户已选择类型
    wx.showToast({
      title: type === 'tooth' ? '已选择牙齿诊疗' : '已选择舌诊',
      icon: 'success',
      duration: 800
    });
    // 这里可以根据type做后续处理，如显示类型、限制上传等
  },

  openTypeModal() {
    this.setData({ showTypeModal: true });
  },

  onInput(e) {
    this.setData({ inputValue: e.detail.value });
  },

  onSend() {
    const val = this.data.inputValue.trim();
    if (!val) return;
    this.addMessage({
      type: 'text',
      content: val,
      role: 'user'
    });
    this.setData({ inputValue: '' });

    // 只要输入"你好"就返回欢迎语
    if (val.includes('你好')) {
      const welcomeResponse = '欢迎咨询!请先上传牙齿或舌头的清\n晰照片,我会帮您分析初步情况。拍\n摄时注意光线充足,对焦准确。目前\n观察到什么不适症状吗?比如疼痛、\n肿胀或味觉异常?';
      this.addMessage({
        type: 'text',
        content: welcomeResponse,
        role: 'assistant'
      });
      return;
    }

    // 构造多轮对话历史，只保留文本消息
    const history = this.data.messages
      .filter(msg => msg.type === 'text')
      .map(msg => ({ role: msg.role === 'assistant' ? 'assistant' : 'user', content: msg.content }));
    // 调用后端API获取AI回复，并传递chosenType和history
    wx.request({
      url: 'http://192.168.193.30:8080/chat',
      method: 'POST',
      data: { message: val, check_type: this.data.chosenType || 'tongue', history },
      header: { 'content-type': 'application/json' },
      success: (res) => {
        if (res.data.response) {
          this.addMessage({
            type: 'text',
            content: res.data.response,
            role: 'assistant'
          });
        } else {
          wx.showToast({ title: 'AI回复失败', icon: 'none' });
        }
      },
      fail: () => {
        // wx.showToast({ title: '', icon: 'none' });
      }
    });
  },

  addMessage(msg) {
    this.setData({
      messages: [...this.data.messages, msg]
    });
    // 可选：自动滚动到底部
  },

  onChooseImage() {
    wx.showActionSheet({
      itemList: ['从相册选择', '拍照上传'],
      success: (res) => {
        if (res.tapIndex === 0) {
          this.chooseImage('album');
        } else if (res.tapIndex === 1) {
          this.chooseImage('camera');
        }
      }
    });
  },

  chooseImage(source) {
    wx.chooseImage({
      count: 1,
      sizeType: ['original', 'compressed'],
      sourceType: [source],
      success: (res) => {
        const filePath = res.tempFilePaths[0];
        this.addMessage({
          type: 'image',
          content: filePath,
          role: 'user'
        });
        // 仿真：如果当前类型为牙齿诊疗，直接返回固定回复
        if (this.data.chosenType === 'tooth') {
          const fixedResponse = '从您的牙齿图片分析来看,确实存在\n龋齿(蛀牙)的可能性较高。目前可\n见牙齿表面有局部变色或轻微缺损的\n表现。想先了解两个关键情况:这颗\n牙齿最近是否有对冷热敏感的现象?\n以及您平时是否有夜间磨牙的习惯?';
          this.addMessage({
            type: 'text',
            content: fixedResponse,
            role: 'assistant'
          });
        } 
        if (this.data.chosenType === 'tongue') {
          const fixedResponse = '从您的舌象分析来看,舌色淡白、薄\n白苔且偏腻,这通常提示可能存在气\n血不足或脾胃功能偏弱的情况。现在\n需要了解:最近是否有容易疲劳、食\n欲减退或大便不成形的情况?另外,\n平时是否经常感觉口干或口苦?';
          this.addMessage({
            type: 'text',
            content: fixedResponse,
            role: 'assistant'
          });
        }
        // 你可以在这里继续添加舌诊等其他类型的仿真逻辑
      }
    });
  },

  chooseChatType(e) {
    const type = e.currentTarget.dataset.type;
    this.setData({ showChatTypeModal: false });
    wx.navigateTo({
      url: `/pages/chat/chat?type=${type}`
    });
  },

  generateReport() {
    const that = this;
    wx.showLoading({ title: '生成中...' });
    // 构造history参数，兼容后端格式
    const history = that.data.messages
      .map(msg => {
        if (msg.type === 'text') {
          return {
            role: msg.role === 'assistant' ? 'assistant' : 'user',
            content: msg.content
          };
        } else if (msg.type === 'image_analysis') {
          return {
            type: 'image_analysis',
            result: msg.result
          };
        }
        // 过滤掉 'image' 类型的消息
        return null;
      })
      .filter(item => item !== null);

    console.log("History being sent to /generate_report:", JSON.stringify(history, null, 2));

    wx.request({
      url: 'http://192.168.193.30:8080/generate_report',
      method: 'POST',
      data: { history },
      header: { 'content-type': 'application/json' },
      responseType: 'arraybuffer',
      success(res) {
        wx.hideLoading();
        if (res.statusCode === 200 && res.data) {
          // 保存PDF到本地
          const filePath = wx.env.USER_DATA_PATH + '/report.pdf';
          wx.getFileSystemManager().writeFile({
            filePath,
            data: res.data,
            encoding: 'binary',
            success: () => {
              wx.openDocument({
                filePath,
                fileType: 'pdf',
                showMenu: true,
                success: () => {
                  wx.showToast({ title: '报告已打开', icon: 'success' });
                },
                fail: () => {
                  wx.showToast({ title: '打开失败', icon: 'none' });
                }
              });
            },
            fail: () => {
              wx.showToast({ title: '保存失败', icon: 'none' });
            }
          });
        } else {
          wx.showToast({ title: '生成失败', icon: 'none' });
        }
      },
      fail() {
        wx.hideLoading();
        // wx.showToast({ title: '', icon: 'none' });
      }
    });
  },
});