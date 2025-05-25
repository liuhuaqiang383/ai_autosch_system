<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <div class="welcome-section">
        <div class="dashboard-title">智能排课系统</div>
        <div class="dashboard-subtitle">教室资源统计分析</div>
      </div>
      <div class="filter-section">
        <el-select v-model="buildingId" placeholder="选择教学楼" clearable @change="refreshCharts">
          <el-option v-for="item in buildingOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
        <el-select v-model="timeRange" placeholder="时间范围" @change="refreshCharts">
          <el-option label="本周" value="week" />
          <el-option label="本月" value="month" />
          <el-option label="本学期" value="semester" />
        </el-select>
        <el-button type="primary" icon="el-icon-refresh" size="small" @click="refreshCharts(true)">刷新</el-button>
      </div>
    </div>
    
    <el-alert
      v-if="usingCache"
      title="数据来自缓存"
      type="info"
      description="当前展示的数据使用了本地缓存，点击刷新按钮可获取最新数据"
      show-icon
      :closable="false"
      style="margin-bottom: 15px;"
    />

    <div class="statistics-scroll-container">
      <div class="statistics-content">
        <!-- 资源概览卡片 -->
        <div class="stat-card overview-card">
          <div class="card-title">资源概览</div>
          <div v-loading="overviewLoading" class="card-content">
            <div class="overview-item">
              <div class="label">总教室数</div>
              <div class="value">{{ overview.totalClassrooms || 0 }}</div>
            </div>
            <div class="overview-item">
              <div class="label">本周已使用教室</div>
              <div class="value">{{ overview.usedClassrooms || 0 }}</div>
            </div>
            <div class="overview-item">
              <div class="label">平均利用率</div>
              <div class="value">{{ overview.averageUtilization || '0%' }}</div>
            </div>
            <div class="overview-item">
              <div class="label">空闲教室数</div>
              <div class="value">{{ overview.idleClassrooms || 0 }}</div>
            </div>
          </div>
        </div>

        <!-- 教室类型分布卡片 -->
        <div class="stat-card utilization-card">
          <div class="card-title">教室类型利用率</div>
          <div v-loading="typeLoading" class="card-content">
            <div ref="classroomTypeChart" class="chart-container"></div>
          </div>
        </div>

        <!-- 时间段利用率卡片 -->
        <div class="stat-card time-distribution-card">
          <div class="card-title">时间段利用率分布</div>
          <div v-loading="timeLoading" class="card-content">
            <div ref="timeDistributionChart" class="chart-container"></div>
          </div>
        </div>

        <!-- 教学楼利用率卡片 -->
        <div class="stat-card building-comparison-card">
          <div class="card-title">教学楼利用率对比</div>
          <div v-loading="buildingLoading" class="card-content">
            <div ref="buildingComparisonChart" class="chart-container"></div>
          </div>
        </div>
      </div>
    </div>

    <el-row :gutter="20" style="margin-top: 20px;">
      <!-- 空闲教室推荐 -->
      <el-col :span="24">
        <el-card shadow="hover" class="idle-card">
          <div slot="header">
            <span>空闲教室推荐</span>
            <el-button style="float: right; padding: 3px 0" type="text" @click="refreshIdleClassrooms">刷新</el-button>
          </div>
          <div v-loading="idleLoading" class="idle-container">
            <el-table :data="idleClassrooms" stripe style="width: 100%">
              <el-table-column prop="classroom_code" label="教室编号" width="120" />
              <el-table-column prop="classroom_name" label="教室名称" width="200" />
              <el-table-column prop="building_name" label="所在教学楼" width="180" />
              <el-table-column prop="capacity" label="容量" width="100" />
              <el-table-column prop="classroom_type" label="教室类型" width="150" />
              <el-table-column prop="available_periods" label="空闲时段" />
              <el-table-column fixed="right" label="操作" width="120">
                <template slot-scope="scope">
                  <router-link :to="{ path: '/scheduling/manual', query: { classroom: scope.row.classroom_code } }">
                    <el-button type="text" size="small">排课</el-button>
                  </router-link>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import { getClassroomOverview, getClassroomUtilization, getClassroomTimeDistribution, getIdleClassroomRecommendation, getBuildingUtilization } from '@/api/statistics'
import { getBuildings } from '@/api/building'

// 缓存数据
const CACHE_EXPIRY = 5 * 60 * 1000 // 5分钟缓存过期时间
let overviewCache = null
let overviewCacheTime = null
let utilizationCache = {}
let utilizationCacheTime = {}
let timeDistributionCache = {}
let timeDistributionCacheTime = {}
let buildingUtilizationCache = {}
let buildingUtilizationCacheTime = {}

export default {
  name: 'Dashboard',
  data() {
    return {
      // 图表实例
      typeChart: null,
      timeChart: null,
      buildingChart: null,
      
      // 筛选条件
      buildingId: '',
      timeRange: 'week',
      buildingOptions: [],
      
      // 加载状态
      overviewLoading: false,
      typeLoading: false,
      timeLoading: false,
      buildingLoading: false,
      idleLoading: false,
      
      // 数据
      overview: {
        totalClassrooms: 0,
        usedClassrooms: 0,
        averageUtilization: '0%',
        idleClassrooms: 0
      },
      idleClassrooms: [],
      
      // 缓存相关
      cacheExpiryTime: 5 * 60 * 1000, // 缓存过期时间，5分钟
      
      // 缓存状态标志
      usingCache: false
    }
  },
  created() {
    this.getBuildingOptions()
  },
  mounted() {
    this.initCharts()
    this.loadAllData()
    
    // 窗口大小变化时，重新调整图表大小
    window.addEventListener('resize', this.resizeCharts)
  },
  beforeDestroy() {
    // 销毁图表实例
    if (this.typeChart) this.typeChart.dispose()
    if (this.timeChart) this.timeChart.dispose()
    if (this.buildingChart) this.buildingChart.dispose()
    
    // 移除事件监听
    window.removeEventListener('resize', this.resizeCharts)
  },
  methods: {
    // 初始化所有图表
    initCharts() {
      // 教室类型利用率图表
      this.typeChart = echarts.init(this.$refs.classroomTypeChart)
      
      // 时间段分布图表
      this.timeChart = echarts.init(this.$refs.timeDistributionChart)
      
      // 教学楼利用率图表
      this.buildingChart = echarts.init(this.$refs.buildingComparisonChart)
    },
    
    // 加载所有数据
    loadAllData() {
      console.log('加载所有教室利用率分析数据')
      this.getClassroomOverview()
      this.getClassroomTypeUtilization()
      this.getTimeDistribution()
      this.getBuildingUtilization()
      this.getIdleClassroomRecommendation()
    },
    
    // 刷新图表 - 强制刷新不使用缓存
    refreshCharts(forceRefresh = false) {
      if (forceRefresh) {
        // 清除缓存
        this.clearCache()
        console.log('强制刷新: 已清除所有缓存')
        // 重置缓存状态
        this.usingCache = false
      } else {
        console.log('正常刷新: 将优先使用缓存')
      }
      this.getClassroomOverview()
      this.getClassroomTypeUtilization()
      this.getTimeDistribution()
      this.getBuildingUtilization()
    },
    
    // 清除所有缓存
    clearCache() {
      console.log('清除所有教室利用率分析缓存')
      overviewCache = null
      overviewCacheTime = null
      utilizationCache = {}
      utilizationCacheTime = {}
      timeDistributionCache = {}
      timeDistributionCacheTime = {}
      buildingUtilizationCache = {}
      buildingUtilizationCacheTime = {}
    },
    
    // 检查缓存是否有效
    isCacheValid(cacheTime) {
      const valid = cacheTime && (Date.now() - cacheTime < CACHE_EXPIRY)
      if (cacheTime) {
        const ageSeconds = Math.round((Date.now() - cacheTime) / 1000)
        console.log(`缓存年龄: ${ageSeconds}秒, 有效期: ${Math.round(CACHE_EXPIRY/1000)}秒, 是否有效: ${valid}`)
      }
      return valid
    },
    
    // 重新调整图表大小
    resizeCharts() {
      if (this.typeChart) this.typeChart.resize()
      if (this.timeChart) this.timeChart.resize()
      if (this.buildingChart) this.buildingChart.resize()
    },
    
    // 获取教学楼选项
    getBuildingOptions() {
      getBuildings().then(response => {
        this.buildingOptions = response.results.map(item => ({
          value: item.building_code,
          label: item.building_name
        }))
      })
    },
    
    // 获取教室概览数据
    getClassroomOverview() {
      // 构建参数对象
      const params = { timeRange: this.timeRange }
      
      // 检查缓存是否有效
      if (this.isCacheValid(overviewCacheTime) && overviewCache) {
        console.log('使用教室概览缓存数据')
        this.overview = overviewCache
        this.usingCache = true
        return
      }
      
      this.overviewLoading = true
      getClassroomOverview(params).then(response => {
        // 更新数据
        this.overview = response
        
        // 更新缓存
        overviewCache = response
        overviewCacheTime = Date.now()
        
        this.overviewLoading = false
        this.usingCache = false
      }).catch(() => {
        this.overviewLoading = false
      })
    },
    
    // 获取教室类型利用率
    getClassroomTypeUtilization() {
      // 构建参数对象
      const params = {
        building_id: this.buildingId,
        time_period: this.timeRange
      }
      
      // 生成缓存键
      const cacheKey = this.getCacheKey(params)
      
      // 检查缓存是否有效
      if (utilizationCacheTime[cacheKey] && this.isCacheValid(utilizationCacheTime[cacheKey]) && utilizationCache[cacheKey]) {
        console.log('使用教室类型利用率缓存数据')
        this.updateTypeChart(utilizationCache[cacheKey])
        this.usingCache = true
        return
      }
      
      this.typeLoading = true
      getClassroomUtilization(params).then(response => {
        // 更新缓存
        utilizationCache[cacheKey] = response
        utilizationCacheTime[cacheKey] = Date.now()
        
        // 更新图表
        this.updateTypeChart(response)
        
        this.typeLoading = false
        this.usingCache = false
      }).catch(() => {
        this.typeLoading = false
      })
    },
    
    // 更新教室类型利用率图表
    updateTypeChart(response) {
      const data = response.results || []
      
      const typeNames = data.map(item => item.classroom_type)
      const utilization = data.map(item => item.utilization_rate)
      const count = data.map(item => item.count)
      
      // 更新图表
      this.typeChart.setOption({
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        legend: {
          data: ['利用率', '教室数量']
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: [
          {
            type: 'category',
            data: typeNames,
            axisLabel: {
              interval: 0,
              rotate: 30
            }
          }
        ],
        yAxis: [
          {
            type: 'value',
            name: '利用率',
            min: 0,
            max: 100,
            axisLabel: {
              formatter: '{value}%'
            }
          },
          {
            type: 'value',
            name: '教室数量',
            axisLabel: {
              formatter: '{value}'
            }
          }
        ],
        series: [
          {
            name: '利用率',
            type: 'bar',
            data: utilization
          },
          {
            name: '教室数量',
            type: 'line',
            yAxisIndex: 1,
            data: count
          }
        ]
      })
    },
    
    // 获取时间段分布
    getTimeDistribution() {
      // 构建参数对象
      const params = {
        building_id: this.buildingId,
        time_period: this.timeRange
      }
      
      // 生成缓存键
      const cacheKey = this.getCacheKey(params)
      
      // 检查缓存是否有效
      if (timeDistributionCacheTime[cacheKey] && this.isCacheValid(timeDistributionCacheTime[cacheKey]) && timeDistributionCache[cacheKey]) {
        console.log('使用时间段分布缓存数据')
        this.updateTimeChart(timeDistributionCache[cacheKey])
        this.usingCache = true
        return
      }
      
      this.timeLoading = true
      getClassroomTimeDistribution(params).then(response => {
        // 更新缓存
        timeDistributionCache[cacheKey] = response
        timeDistributionCacheTime[cacheKey] = Date.now()
        
        // 更新图表
        this.updateTimeChart(response)
        
        this.timeLoading = false
        this.usingCache = false
      }).catch(() => {
        this.timeLoading = false
      })
    },
    
    // 更新时间段分布图表
    updateTimeChart(response) {
      const data = response.results || []
      
      const timeSlots = data.map(item => item.time_slot)
      const weekdayData = data.map(item => item.weekday_utilization)
      const weekendData = data.map(item => item.weekend_utilization)
      
      // 打印调试信息
      console.log('时间段利用率数据:', data);
      
      // 更新图表
      this.timeChart.setOption({
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          },
          formatter: function (params) {
            let tooltipContent = params[0].name + '<br/>';
            
            params.forEach(param => {
              const markerSpan = `<span style="display:inline-block;margin-right:5px;border-radius:10px;width:10px;height:10px;background-color:${param.color};"></span>`;
              tooltipContent += `${markerSpan}${param.seriesName}: ${param.value}%<br/>`;
              
              // 添加实际使用教室数量信息
              const dataIndex = param.dataIndex;
              const item = data[dataIndex];
              if (param.seriesName === '工作日') {
                tooltipContent += `${markerSpan}使用教室数: ${item.weekday_count || 0}<br/>`;
              } else if (param.seriesName === '周末') {
                tooltipContent += `${markerSpan}使用教室数: ${item.weekend_count || 0}<br/>`;
              }
            });
            
            return tooltipContent;
          }
        },
        legend: {
          data: ['工作日', '周末']
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: timeSlots
        },
        yAxis: {
          type: 'value',
          min: 0,
          max: 100,
          axisLabel: {
            formatter: '{value}%'
          }
        },
        series: [
          {
            name: '工作日',
            type: 'bar',
            data: weekdayData
          },
          {
            name: '周末',
            type: 'bar',
            data: weekendData
          }
        ]
      })
    },
    
    // 获取教学楼利用率
    getBuildingUtilization() {
      // 构建参数对象
      const params = {
        time_period: this.timeRange
      }
      
      // 生成缓存键
      const cacheKey = this.getCacheKey(params)
      
      // 检查缓存是否有效
      if (buildingUtilizationCacheTime[cacheKey] && this.isCacheValid(buildingUtilizationCacheTime[cacheKey]) && buildingUtilizationCache[cacheKey]) {
        console.log('使用教学楼利用率缓存数据')
        this.updateBuildingChart(buildingUtilizationCache[cacheKey])
        this.usingCache = true
        return
      }
      
      this.buildingLoading = true
      getBuildingUtilization(params).then(response => {
        // 更新缓存
        buildingUtilizationCache[cacheKey] = response
        buildingUtilizationCacheTime[cacheKey] = Date.now()
        
        // 更新图表
        this.updateBuildingChart(response)
        
        this.buildingLoading = false
        this.usingCache = false
      }).catch(() => {
        this.buildingLoading = false
      })
    },
    
    // 更新教学楼利用率图表
    updateBuildingChart(response) {
      const data = response.results || []
      
      const buildingNames = data.map(item => item.building_name)
      const utilization = data.map(item => item.utilization_rate)
      const classroomCount = data.map(item => item.classroom_count)
      
      // 更新图表
      this.buildingChart.setOption({
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross',
            crossStyle: {
              color: '#999'
            }
          }
        },
        legend: {
          data: ['利用率', '教室数量']
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: [
          {
            type: 'category',
            data: buildingNames,
            axisPointer: {
              type: 'shadow'
            },
            axisLabel: {
              interval: 0,
              rotate: 30
            }
          }
        ],
        yAxis: [
          {
            type: 'value',
            name: '利用率',
            min: 0,
            max: 100,
            axisLabel: {
              formatter: '{value}%'
            }
          },
          {
            type: 'value',
            name: '教室数量',
            axisLabel: {
              formatter: '{value}'
            }
          }
        ],
        series: [
          {
            name: '利用率',
            type: 'bar',
            data: utilization
          },
          {
            name: '教室数量',
            type: 'line',
            yAxisIndex: 1,
            data: classroomCount
          }
        ]
      })
    },
    
    // 获取闲置教室推荐
    getIdleClassroomRecommendation() {
      this.idleLoading = true
      getIdleClassroomRecommendation({
        building_id: this.buildingId
      }).then(response => {
        this.idleClassrooms = response.results || []
        this.idleLoading = false
      }).catch(() => {
        this.idleLoading = false
      })
    },
    
    // 刷新闲置教室推荐
    refreshIdleClassrooms() {
      this.getIdleClassroomRecommendation()
    },
    
    // 生成缓存键
    getCacheKey(params = {}) {
      return JSON.stringify(params)
    }
  }
}
</script>

<style lang="scss" scoped>
.dashboard {
  &-container {
    padding: 20px;
    background-color: #f5f7fa;
    min-height: calc(100vh - 50px);
  }
  
  &-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
  }
  
  &-title {
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 5px;
  }
  
  &-subtitle {
    font-size: 16px;
    color: #606266;
  }
}

.filter-section {
  display: flex;
  gap: 10px;
  
  .el-select {
    width: 150px;
  }
}

.statistics-scroll-container {
  height: calc(100vh - 240px);
  overflow-y: auto;
  margin-bottom: 20px;
  
  .statistics-content {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
  }
}

.stat-card {
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 20px;
  
  .card-title {
    font-size: 16px;
    font-weight: 500;
    margin-bottom: 15px;
    color: #303133;
  }
  
  .card-content {
    min-height: 200px;
  }
  
  .chart-container {
    width: 100%;
    height: 300px;
  }
}

.overview-card {
  .card-content {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    grid-gap: 20px;
  }
  
  .overview-item {
    text-align: center;
    
    .label {
      font-size: 14px;
      color: #909399;
      margin-bottom: 5px;
    }
    
    .value {
      font-size: 28px;
      font-weight: 500;
      color: #409EFF;
    }
  }
}

.utilization-card,
.time-distribution-card,
.building-comparison-card {
  grid-column: span 2;
}

.idle-card {
  .idle-container {
    min-height: 200px;
  }
}
</style> 