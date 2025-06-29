// miniprogram/pages/analysis/analysis.js
import * as echarts from '../../components/ec-canvas/echarts';

Page({
  data: {
    timeRanges: [
      { label: '过去一周', value: 'week' },
      { label: '过去两周', value: 'two-weeks' },
      { label: '过去一个月', value: 'month' },
      { label: '过去三个月', value: 'three-months' },
      { label: '全部数据', value: 'all' }
    ],
    activeRange: 'week',
    tongueSummary: '',
    toothSummary: '',
    charts: {}
  },

  onLoad() {
    this.initCharts();
    this.loadData('week');
  },

  // 初始化图表
  initCharts() {
    const chartIds = [
      'tongue-overall-chart',
      'tongue-dimensions-chart',
      'tongue-frequency-chart',
      'tongue-prediction-chart',
      'tooth-overall-chart',
      'tooth-distribution-chart',
      'tooth-frequency-chart',
      'tooth-prediction-chart'
    ];

    chartIds.forEach(id => {
      this.initChart(id);
    });
  },

  // 初始化单个图表
  initChart(chartId) {
    this.setData({
      [`charts.${chartId}`]:
        function (canvas, width, height, dpr) {
          const chart = echarts.init(canvas, null, {
            width: width,
            height: height,
            devicePixelRatio: dpr
          });
          canvas.setChart(chart);
          return chart;
        }
    });
  },

  // 加载数据
  async loadData(timeRange) {
    wx.showLoading({ title: '加载中...' });
    const that = this;
    // 舌诊数据
    wx.request({
      url: 'http://192.168.193.30:8080/api/analysis',
      method: 'GET',
      data: { type: 'tongue', range: timeRange },
      success: (tongueRes) => {
        if (tongueRes.statusCode === 200 && tongueRes.data) {
          that.updateTongueCharts(tongueRes.data);
          // 去除HTML标签，仅保留纯文本
          const summaryText = (tongueRes.data.summary || '').replace(/<[^>]+>/g, '');
          that.setData({ tongueSummary: summaryText });
        } else {
          wx.showToast({ title: '舌诊分析加载失败', icon: 'none' });
        }
      },
      fail: () => {
        wx.showToast({ title: '舌诊分析网络错误', icon: 'none' });
      }
    });
    // 牙科数据
    wx.request({
      url: 'http://192.168.193.30:8080/api/analysis',
      method: 'GET',
      data: { type: 'tooth', range: timeRange },
      success: (toothRes) => {
        if (toothRes.statusCode === 200 && toothRes.data) {
          that.updateToothCharts(toothRes.data);
          // 去除HTML标签，仅保留纯文本
          const summaryText = (toothRes.data.summary || '').replace(/<[^>]+>/g, '');
          that.setData({ toothSummary: summaryText });
        } else {
          wx.showToast({ title: '牙科分析加载失败', icon: 'none' });
        }
      },
      fail: () => {
        wx.showToast({ title: '牙科分析网络错误', icon: 'none' });
      },
      complete: () => {
        wx.hideLoading();
      }
    });
  },

  // 更新舌诊图表
  updateTongueCharts(data) {
    this.updateChart('tongue-overall-chart', this.getOverallOption(data.overall, '舌诊总体评分趋势'));
    this.updateChart('tongue-dimensions-chart', this.getDimensionsOption(data.dimensions));
    this.updateChart('tongue-frequency-chart', this.getFrequencyOption(data.frequency, '舌诊特征分布'));
    this.updateChart('tongue-prediction-chart', this.getPredictionOption(data.prediction, '未来趋势预测'));
  },

  // 更新牙科图表
  updateToothCharts(data) {
    this.updateChart('tooth-overall-chart', this.getOverallOption(data.overall, '牙科健康评分趋势'));
    this.updateChart('tooth-distribution-chart', this.getDistributionOption(data.disease_distribution));
    this.updateChart('tooth-frequency-chart', this.getBarFrequencyOption(data.frequency, '疾病类型频率'));
    this.updateChart('tooth-prediction-chart', this.getPredictionOption(data.prediction, '健康趋势预测'));
  },

  // 更新单个图表
  updateChart(chartId, option) {
    this.selectComponent(`#${chartId}`).init((canvas, width, height, dpr) => {
      const chart = echarts.init(canvas, null, {
        width: width,
        height: height,
        devicePixelRatio: dpr
      });
      chart.setOption(option);
      return chart;
    });
  },

  // 时间范围改变
  changeTimeRange(e) {
    const range = e.currentTarget.dataset.range;
    this.setData({ activeRange: range });
    this.loadData(range);
  },

  // 获取总体评分图表配置
  getOverallOption(data, title) {
    return {
      title: {
        text: title,
        left: 'center',
        textStyle: {
          fontSize: 14
        }
      },
      tooltip: {
        trigger: 'axis'
      },
      xAxis: {
        type: 'category',
        data: data.dates,
        axisLabel: {
          rotate: 45,
          fontSize: 10
        }
      },
      yAxis: {
        type: 'value',
        min: 0,
        max: 100,
        name: '评分',
        axisLabel: {
          fontSize: 10
        }
      },
      series: [{
        data: data.scores,
        type: 'line',
        smooth: true,
        markPoint: {
          data: [
            { type: 'max', name: '最高分' },
            { type: 'min', name: '最低分' }
          ]
        }
      }]
    };
  },

  // 获取各维度评分图表配置
  getDimensionsOption(data) {
    return {
      title: {
        text: '舌诊各维度评分',
        left: 'center',
        textStyle: {
          fontSize: 14
        }
      },
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: ['舌色', '舌苔', '舌形', '舌态'],
        top: 30,
        textStyle: {
          fontSize: 10
        }
      },
      xAxis: {
        type: 'category',
        data: data.dates,
        axisLabel: {
          rotate: 45,
          fontSize: 10
        }
      },
      yAxis: {
        type: 'value',
        min: 0,
        max: 100,
        name: '评分',
        axisLabel: {
          fontSize: 10
        }
      },
      series: [
        {
          name: '舌色',
          type: 'line',
          data: data.tongueColor
        },
        {
          name: '舌苔',
          type: 'line',
          data: data.coating
        },
        {
          name: '舌形',
          type: 'line',
          data: data.shape
        },
        {
          name: '舌态',
          type: 'line',
          data: data.state
        }
      ]
    };
  },

  // 获取频率统计图表配置
  getFrequencyOption(data, title) {
    return {
      title: {
        text: title,
        left: 'center',
        textStyle: {
          fontSize: 14
        }
      },
      tooltip: {
        trigger: 'item'
      },
      legend: {
        orient: 'vertical',
        left: 'left',
        textStyle: {
          fontSize: 10
        }
      },
      series: [
        {
          type: 'pie',
          radius: '50%',
          data: data,
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          },
          label: {
            fontSize: 10
          }
        }
      ]
    };
  },

  // 获取柱状图频率统计配置
  getBarFrequencyOption(data, title) {
    return {
      title: {
        text: title,
        left: 'center',
        textStyle: {
          fontSize: 14
        }
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      xAxis: {
        type: 'category',
        data: data.map(item => item.name),
        axisLabel: {
          fontSize: 10,
          rotate: 45
        }
      },
      yAxis: {
        type: 'value',
        name: '出现次数',
        axisLabel: {
          fontSize: 10
        }
      },
      series: [{
        data: data.map(item => item.value),
        type: 'bar'
      }]
    };
  },

  // 获取预测趋势图表配置
  getPredictionOption(data, title) {
    return {
      title: {
        text: title,
        left: 'center',
        textStyle: {
          fontSize: 14
        }
      },
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: ['历史数据', '预测趋势'],
        top: 30,
        textStyle: {
          fontSize: 10
        }
      },
      xAxis: {
        type: 'category',
        data: data.dates,
        axisLabel: {
          fontSize: 10,
          rotate: 45
        }
      },
      yAxis: {
        type: 'value',
        name: '评分',
        axisLabel: {
          fontSize: 10
        }
      },
      series: [
        {
          name: '历史数据',
          type: 'line',
          data: data.historical
        },
        {
          name: '预测趋势',
          type: 'line',
          data: data.predicted,
          lineStyle: {
            type: 'dashed'
          }
        }
      ]
    };
  },

  // 获取疾病分布图表配置
  getDistributionOption(data) {
    return {
      title: {
        text: '疾病分布统计',
        left: 'center',
        textStyle: {
          fontSize: 14
        }
      },
      tooltip: {
        trigger: 'item'
      },
      legend: {
        orient: 'vertical',
        left: 'left',
        textStyle: {
          fontSize: 10
        }
      },
      series: [{
        type: 'pie',
        radius: '50%',
        data: Object.entries(data).map(([name, value]) => ({
          name,
          value
        })),
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        label: {
          fontSize: 10
        }
      }]
    };
  }
});