<template>
  <div class="resource-analysis-container">
    <div class="page-header">
      <div class="title-section">
        <h1>教学资源数据分析</h1>
        <p>分析课程分布合理性和教学资源使用效率</p>
      </div>
      <div class="filter-section">
        <el-select v-model="departmentId" placeholder="选择院系" clearable @change="refreshData">
          <el-option v-for="item in departmentOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
        <el-select v-model="semester" placeholder="学期" @change="refreshData">
          <el-option label="2023-2024学年第一学期" value="2023-2024-1" />
          <el-option label="2023-2024学年第二学期" value="2023-2024-2" />
          <el-option label="2024-2025学年第一学期" value="2024-2025-1" />
        </el-select>
      </div>
    </div>

    <div class="statistics-scroll-container">
      <div class="statistics-content">
        <!-- 课程分布得分卡片 -->
        <div class="stat-card score-card">
          <div class="score-item" :class="{ 'good-score': dayBalanceScore >= 80, 'medium-score': dayBalanceScore >= 60 && dayBalanceScore < 80, 'low-score': dayBalanceScore < 60 }">
            <div class="score-value">{{ dayBalanceScore }}</div>
            <div class="score-label">工作日分布平衡度</div>
            <div class="score-desc">衡量各工作日课程分布是否均匀</div>
          </div>
          <div class="score-item" :class="{ 'good-score': timeBalanceScore >= 80, 'medium-score': timeBalanceScore >= 60 && timeBalanceScore < 80, 'low-score': timeBalanceScore < 60 }">
            <div class="score-value">{{ timeBalanceScore }}</div>
            <div class="score-label">时段分布平衡度</div>
            <div class="score-desc">衡量各时间段课程分布是否均匀</div>
          </div>
          <div class="score-item" :class="{ 'good-score': resourceMatchRate >= 80, 'medium-score': resourceMatchRate >= 60 && resourceMatchRate < 80, 'low-score': resourceMatchRate < 60 }">
            <div class="score-value">{{ resourceMatchRate }}</div>
            <div class="score-label">资源匹配度</div>
            <div class="score-desc">教室容量与实际需求匹配程度</div>
          </div>
        </div>

        <!-- 课程分布热力图卡片 -->
        <div class="stat-card heatmap-card">
          <div class="card-title">课程分布热力图</div>
          <div v-loading="loadingHeatmap" class="card-content">
            <div ref="heatmapChart" class="chart-container"></div>
          </div>
        </div>

        <!-- 每日课程分布卡片 -->
        <div class="stat-card daily-distribution-card">
          <div class="card-title">每日课程分布</div>
          <div v-loading="loadingDaily" class="card-content">
            <div ref="dailyChart" class="chart-container"></div>
          </div>
        </div>

        <!-- 时段课程分布卡片 -->
        <div class="stat-card time-distribution-card">
          <div class="card-title">时段课程分布</div>
          <div v-loading="loadingTime" class="card-content">
            <div ref="timeChart" class="chart-container"></div>
          </div>
        </div>

        <!-- 资源利用率卡片 -->
        <div class="stat-card efficiency-card">
          <div class="card-title">教室类型利用率</div>
          <div v-loading="loadingEfficiency" class="card-content">
            <div ref="efficiencyChart" class="chart-container"></div>
          </div>
        </div>

        <!-- 资源匹配问题卡片 -->
        <div class="stat-card mismatch-card">
          <div class="card-title">资源匹配问题</div>
          <div v-loading="loadingMismatch" class="card-content">
            <el-table :data="mismatchedRooms" stripe style="width: 100%">
              <el-table-column prop="classroom_name" label="教室" width="120" />
              <el-table-column prop="course_name" label="课程" width="200" />
              <el-table-column prop="capacity" label="教室容量" width="100" />
              <el-table-column prop="student_count" label="学生人数" width="100" />
              <el-table-column label="使用率" width="100">
                <template slot-scope="scope">
                  {{ (scope.row.student_count / scope.row.capacity * 100).toFixed(0) }}%
                </template>
              </el-table-column>
              <el-table-column prop="type" label="问题类型" width="120">
                <template slot-scope="scope">
                  <el-tag :type="scope.row.type === 'underutilized' ? 'warning' : 'danger'">
                    {{ scope.row.type === 'underutilized' ? '资源浪费' : '过度拥挤' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="suggestion" label="优化建议" />
            </el-table>
          </div>
        </div>

        <!-- 优化建议卡片 -->
        <div class="stat-card suggestions-card">
          <div class="card-title">资源配置优化建议</div>
          <div class="card-content">
            <div class="suggestion-item" v-if="timeBalanceScore < 70">
              <i class="el-icon-warning-outline"></i>
              <div class="suggestion-content">
                <h4>时段分布不均衡</h4>
                <p>建议调整课程安排，减少{{ getTimeImbalance() }}的课程密度，提高教学资源利用率。</p>
              </div>
            </div>
            <div class="suggestion-item" v-if="dayBalanceScore < 70">
              <i class="el-icon-warning-outline"></i>
              <div class="suggestion-content">
                <h4>工作日分布不均衡</h4>
                <p>建议调整课程安排，减少{{ getDayImbalance() }}的课程密度，平衡各工作日的教学负担。</p>
              </div>
            </div>
            <div class="suggestion-item" v-if="underutilizedCount > 0">
              <i class="el-icon-warning-outline"></i>
              <div class="suggestion-content">
                <h4>大教室资源浪费</h4>
                <p>有{{ underutilizedCount }}个课程安排在使用率低于40%的大教室中，建议将小班课程安排到更小的教室。</p>
              </div>
            </div>
            <div class="suggestion-item" v-if="crowdedCount > 0">
              <i class="el-icon-warning-outline"></i>
              <div class="suggestion-content">
                <h4>教室过度拥挤</h4>
                <p>有{{ crowdedCount }}个课程安排在过度拥挤的教室中（使用率>90%），建议安排更大的教室提升教学体验。</p>
              </div>
            </div>
            <div class="suggestion-item" v-if="timeBalanceScore >= 70 && dayBalanceScore >= 70 && underutilizedCount === 0 && crowdedCount === 0">
              <i class="el-icon-success"></i>
              <div class="suggestion-content">
                <h4>资源配置良好</h4>
                <p>当前的教学资源配置合理，各时段和日期的课程分布均衡，教室容量与实际需求匹配度高。</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import { getDepartments } from '@/api/department'
import { 
  getCourseDistributionAnalysis, 
  getResourceOptimizationSuggestions,
  getResourceEfficiencyAnalysis
} from '@/api/statistics'
import { getSchedulingResults } from '@/api/scheduling'
import { getClassrooms } from '@/api/classroom'

export default {
  name: 'ResourceAnalysis',
  data() {
    return {
      // 图表实例
      heatmapChart: null,
      dailyChart: null,
      timeChart: null,
      efficiencyChart: null,
      
      // 筛选条件
      departmentId: '',
      semester: '2023-2024-1',
      departmentOptions: [],
      
      // 加载状态
      loadingHeatmap: false,
      loadingDaily: false,
      loadingTime: false,
      loadingEfficiency: false,
      loadingMismatch: false,
      
      // 数据
      courseDistribution: {
        dayDistribution: [0, 0, 0, 0, 0, 0, 0],
        sectionDistribution: Array(12).fill(0),
        heatmapData: [],
        statistics: {
          totalCourses: 0,
          workdayCourses: 0,
          weekendCourses: 0,
          morningCourses: 0,
          afternoonCourses: 0,
          eveningCourses: 0,
          dayBalance: 0,
          timeBalance: 0
        }
      },
      
      resourceOptimization: {
        roomUtilization: [],
        mismatchedRooms: [],
        statistics: {
          totalAnalyzed: 0,
          goodMatches: 0,
          mismatchCount: 0,
          matchRate: 0
        }
      },
      
      resourceEfficiency: {
        typeEfficiency: [],
        statistics: {
          totalRooms: 0,
          totalUsedRooms: 0,
          totalUtilizationRate: 0
        }
      }
    }
  },
  computed: {
    // 得分计算
    dayBalanceScore() {
      return this.courseDistribution.statistics.dayBalance || 0
    },
    timeBalanceScore() {
      return this.courseDistribution.statistics.timeBalance || 0
    },
    resourceMatchRate() {
      return this.resourceOptimization.statistics.matchRate || 0
    },
    // 问题统计
    mismatchedRooms() {
      return this.resourceOptimization.mismatchedRooms || []
    },
    underutilizedCount() {
      return this.mismatchedRooms.filter(room => room.type === 'underutilized').length
    },
    crowdedCount() {
      return this.mismatchedRooms.filter(room => room.type === 'crowded').length
    }
  },
  created() {
    this.getDepartmentOptions()
    
    // 直接测试排课结果API
    this.testSchedulingAPI()
  },
  mounted() {
    console.log('资源分析页面加载，初始化图表...')
    
    // 执行顺序很重要：先等DOM挂载，再初始化图表，再加载数据
    this.$nextTick(() => {
      this.initCharts()
      this.loadAllData()
    })
    
    // 窗口大小变化时，重新调整图表大小
    window.addEventListener('resize', this.resizeCharts)
  },
  beforeDestroy() {
    console.log('资源分析页面卸载，销毁图表实例...')
    
    // 销毁图表实例
    if (this.heatmapChart) {
      try {
        this.heatmapChart.dispose()
      } catch (e) {
        console.error('销毁热力图失败:', e)
      }
    }
    
    if (this.dailyChart) {
      try {
        this.dailyChart.dispose()
      } catch (e) {
        console.error('销毁每日分布图失败:', e)
      }
    }
    
    if (this.timeChart) {
      try {
        this.timeChart.dispose()
      } catch (e) {
        console.error('销毁时段分布图失败:', e)
      }
    }
    
    if (this.efficiencyChart) {
      try {
        this.efficiencyChart.dispose()
      } catch (e) {
        console.error('销毁效率图表失败:', e)
      }
    }
    
    // 移除事件监听
    window.removeEventListener('resize', this.resizeCharts)
  },
  methods: {
    // 初始化所有图表
    initCharts() {
      console.log('初始化图表实例...')
      
      // 课程分布热力图
      if (this.$refs.heatmapChart) {
        try {
          this.heatmapChart = echarts.init(this.$refs.heatmapChart)
          console.log('热力图初始化成功')
        } catch (e) {
          console.error('热力图初始化失败:', e)
        }
      } else {
        console.warn('热力图DOM元素不存在')
      }
      
      // 每日课程分布图表
      if (this.$refs.dailyChart) {
        try {
          this.dailyChart = echarts.init(this.$refs.dailyChart)
          console.log('每日分布图初始化成功')
        } catch (e) {
          console.error('每日分布图初始化失败:', e)
        }
      } else {
        console.warn('每日分布图DOM元素不存在')
      }
      
      // 时段课程分布图表
      if (this.$refs.timeChart) {
        try {
          this.timeChart = echarts.init(this.$refs.timeChart)
          console.log('时段分布图初始化成功')
        } catch (e) {
          console.error('时段分布图初始化失败:', e)
        }
      } else {
        console.warn('时段分布图DOM元素不存在')
      }
      
      // 资源利用率图表
      if (this.$refs.efficiencyChart) {
        try {
          this.efficiencyChart = echarts.init(this.$refs.efficiencyChart)
          console.log('效率图表初始化成功')
        } catch (e) {
          console.error('效率图表初始化失败:', e)
        }
      } else {
        console.warn('效率图表DOM元素不存在')
      }
    },
    
    // 加载所有数据
    loadAllData() {
      this.getCourseDistributionData()
      this.getResourceOptimizationData()
      this.getResourceEfficiencyData()
    },
    
    // 刷新所有数据
    refreshData() {
      this.loadAllData()
    },
    
    // 重新调整图表大小
    resizeCharts() {
      if (this.heatmapChart) this.heatmapChart.resize()
      if (this.dailyChart) this.dailyChart.resize()
      if (this.timeChart) this.timeChart.resize()
      if (this.efficiencyChart) this.efficiencyChart.resize()
    },
    
    // 获取部门选项
    getDepartmentOptions() {
      getDepartments({ 
        _fetchAll: true,
        is_teaching_department: true
      }).then(response => {
        if (response && response.results) {
          // 只保留类型为院系的部门
          const academicDepartments = response.results.filter(dept => 
            dept.department_type === '院系' || 
            dept.is_teaching_department === true
          );
          
          this.departmentOptions = academicDepartments.map(item => ({
            value: item.department_code,
            label: item.department_name
          }));
        }
      }).catch(error => {
        console.error('获取院系部门选项失败:', error);
      });
    },
    
    // 测试排课结果API
    testSchedulingAPI() {
      console.log('测试排课结果API...')
      getSchedulingResults({ _fetchAll: true }).then(response => {
        console.log('排课结果获取成功:', response)
        if (response && response.results) {
          console.log(`共获取到 ${response.results.length} 条排课数据`)
          
          // 如果有数据，使用该数据手动更新分数和图表
          if (response.results.length > 0) {
            this.updateChartsManually(response.results)
          }
        } else {
          console.warn('排课结果为空')
        }
      }).catch(error => {
        console.error('排课结果API调用失败:', error)
      })
    },
    
    // 使用直接获取的排课数据手动更新图表
    updateChartsManually(schedulingResults) {
      console.log('手动更新图表...')
      
      // 1. 按星期分布统计
      const dayDistribution = [0, 0, 0, 0, 0, 0, 0] // 周一到周日
      schedulingResults.forEach(result => {
        if (result.day_of_week >= 1 && result.day_of_week <= 7) {
          dayDistribution[result.day_of_week - 1]++
        }
      })
      
      // 2. 按节次分布统计
      const sectionDistribution = Array(12).fill(0) // 第1-12节
      schedulingResults.forEach(result => {
        for (let i = result.start_section; i <= result.end_section; i++) {
          if (i >= 1 && i <= 12) {
            sectionDistribution[i - 1]++
          }
        }
      })
      
      // 3. 课程密度热力图数据
      const heatmapData = []
      for (let day = 1; day <= 7; day++) {
        for (let section = 1; section <= 12; section++) {
          const count = schedulingResults.filter(result => 
            result.day_of_week === day && 
            section >= result.start_section && 
            section <= result.end_section
          ).length
          
          heatmapData.push([day - 1, section - 1, count])
        }
      }
      
      // 4. 计算统计指标
      const totalCourses = schedulingResults.length
      const workdayCourses = schedulingResults.filter(r => r.day_of_week >= 1 && r.day_of_week <= 5).length
      const weekendCourses = totalCourses - workdayCourses
      const morningCourses = schedulingResults.filter(r => r.start_section <= 4).length
      const afternoonCourses = schedulingResults.filter(r => r.start_section > 4 && r.start_section <= 8).length
      const eveningCourses = schedulingResults.filter(r => r.start_section > 8).length
      
      // 计算合理性得分 (简单版)
      const dayBalance = this.calculateSimpleBalanceScore(dayDistribution.slice(0, 5)) // 工作日平衡度
      const timeBalance = this.calculateSimpleBalanceScore([morningCourses, afternoonCourses, eveningCourses]) // 时段平衡度
      
      console.log('日分布:', dayDistribution)
      console.log('节次分布:', sectionDistribution)
      console.log('统计指标:', {totalCourses, workdayCourses, weekendCourses, dayBalance, timeBalance})
      
      // 更新图表数据
      this.courseDistribution = {
        dayDistribution,
        sectionDistribution,
        heatmapData,
        statistics: {
          totalCourses,
          workdayCourses,
          weekendCourses,
          morningCourses,
          afternoonCourses,
          eveningCourses,
          dayBalance: Math.round(dayBalance),
          timeBalance: Math.round(timeBalance)
        }
      }
      
      // 获取教室数据，用于资源优化和效率分析
      getClassrooms({ _fetchAll: true }).then(classroomsResponse => {
        console.log('教室数据获取成功:', classroomsResponse)
        if (classroomsResponse && classroomsResponse.results) {
          const classrooms = classroomsResponse.results
          
          // 更新资源优化建议
          this.updateResourceOptimization(schedulingResults, classrooms)
          
          // 更新资源效率分析
          this.updateResourceEfficiency(schedulingResults, classrooms)
        }
      }).catch(error => {
        console.error('获取教室数据失败:', error)
      })
      
      // 手动触发图表更新
      this.$nextTick(() => {
        this.updateHeatmapChart()
        this.updateDailyChart()
        this.updateTimeChart()
      })
    },
    
    // 更新资源优化建议
    updateResourceOptimization(schedulingResults, classrooms) {
      console.log('更新资源优化建议...')
      
      // 教室容量与实际使用情况匹配度分析
      const roomUtilization = []
      const mismatchedRooms = []
      
      schedulingResults.forEach(result => {
        // 假设学生数据在学生总人数字段或教学班人数字段
        const studentCount = result.student_count || result.teaching_class_students || 30 // 默认值
        
        const classroom = classrooms.find(c => c.classroom_code === result.classroom_code)
        if (classroom) {
          const capacity = classroom.max_capacity || 0
          const utilizationRate = capacity > 0 ? (studentCount / capacity) * 100 : 0
          
          // 记录教室使用情况
          roomUtilization.push({
            classroom_code: classroom.classroom_code,
            classroom_name: classroom.classroom_name,
            capacity,
            student_count: studentCount,
            utilization_rate: Math.round(utilizationRate)
          })
          
          // 识别不匹配的教室
          if (utilizationRate < 40 && capacity > 60) {
            // 大教室使用率低
            mismatchedRooms.push({
              type: 'underutilized',
              classroom_code: classroom.classroom_code,
              classroom_name: classroom.classroom_name,
              capacity,
              student_count: studentCount,
              course_name: result.course_name,
              suggestion: '建议将课程安排到较小的教室，以提高资源利用率'
            })
          } else if (utilizationRate > 90) {
            // 教室几乎满座，可能不够宽松
            mismatchedRooms.push({
              type: 'crowded',
              classroom_code: classroom.classroom_code,
              classroom_name: classroom.classroom_name,
              capacity,
              student_count: studentCount,
              course_name: result.course_name,
              suggestion: '教室接近满座，建议考虑安排更大的教室以提高教学体验'
            })
          }
        }
      })
      
      // 计算统计指标
      const totalAnalyzed = roomUtilization.length
      const goodMatches = roomUtilization.filter(r => r.utilization_rate >= 40 && r.utilization_rate <= 90).length
      const mismatchCount = mismatchedRooms.length
      const matchRate = totalAnalyzed > 0 ? Math.round((goodMatches / totalAnalyzed) * 100) : 0
      
      console.log('资源优化统计:', {totalAnalyzed, goodMatches, mismatchCount, matchRate})
      console.log('不匹配教室数:', mismatchedRooms.length)
      
      this.resourceOptimization = {
        roomUtilization: roomUtilization.sort((a, b) => a.utilization_rate - b.utilization_rate).slice(0, 20),
        mismatchedRooms,
        statistics: {
          totalAnalyzed,
          goodMatches,
          mismatchCount,
          matchRate
        }
      }
      
      this.loadingMismatch = false
    },
    
    // 更新资源效率分析
    updateResourceEfficiency(schedulingResults, classrooms) {
      console.log('更新资源效率分析...')
      
      // 按教室类型统计使用情况
      const roomTypeStats = {}
      classrooms.forEach(classroom => {
        const type = classroom.classroom_type || '普通教室'
        if (!roomTypeStats[type]) {
          roomTypeStats[type] = {
            classroom_type: type,
            total_count: 0,
            used_classrooms: new Set(), // 使用Set存储已使用教室的编号
            usage_hours: 0
          }
        }
        roomTypeStats[type].total_count++
      })
      
      // 统计使用时长和已使用教室
      schedulingResults.forEach(result => {
        const classroom = classrooms.find(c => c.classroom_code === result.classroom_code)
        if (classroom && classroom.classroom_code) {
          const type = classroom.classroom_type || '普通教室'
          if (roomTypeStats[type]) {
            // 添加使用的教室编号到Set中（会自动去重）
            roomTypeStats[type].used_classrooms.add(classroom.classroom_code)
            
            // 计算课程时长
            const hours = (result.end_section - result.start_section + 1) * 0.75 // 假设每节课45分钟
            roomTypeStats[type].usage_hours += hours
          }
        }
      })
      
      // 计算使用率
      const typeEfficiency = Object.values(roomTypeStats).map(stats => {
        const usedCount = stats.used_classrooms.size; // 获取唯一的已使用教室数量
        return {
          classroom_type: stats.classroom_type,
          total_count: stats.total_count,
          used_count: usedCount,
          usage_hours: Math.round(stats.usage_hours),
          utilization_rate: stats.total_count > 0 ? Math.min(100, Math.round((usedCount / stats.total_count) * 100)) : 0
        }
      })
      
      // 计算总体指标
      const totalRooms = classrooms.length
      const totalUsedRooms = new Set(schedulingResults.map(r => r.classroom_code).filter(code => code)).size
      const totalUtilizationRate = totalRooms > 0 ? Math.min(100, Math.round((totalUsedRooms / totalRooms) * 100)) : 0
      
      console.log('资源效率统计:', {totalRooms, totalUsedRooms, totalUtilizationRate})
      console.log('教室类型效率:', typeEfficiency)
      
      this.resourceEfficiency = {
        typeEfficiency,
        statistics: {
          totalRooms,
          totalUsedRooms,
          totalUtilizationRate
        }
      }
      
      // 更新效率图表
      this.$nextTick(() => {
        this.updateEfficiencyChart()
      })
      
      this.loadingEfficiency = false
    },
    
    // 简化版平衡度评分算法
    calculateSimpleBalanceScore(values) {
      if (!values || values.length === 0 || values.every(v => v === 0)) {
        return 0
      }
      
      const sum = values.reduce((a, b) => a + b, 0)
      const mean = sum / values.length
      
      // 避免除零错误
      if (mean === 0) return 0
      
      // 计算变异系数
      let deviation = 0
      values.forEach(val => {
        deviation += Math.pow(val - mean, 2)
      })
      
      const variance = deviation / values.length
      const stdDev = Math.sqrt(variance)
      const cv = stdDev / mean
      
      // 将CV转换为0-100的平衡度得分 (CV越小，平衡度越高)
      return Math.max(0, Math.min(100, 100 - (cv * 100)))
    },
    
    // 获取课程分布数据
    getCourseDistributionData() {
      this.loadingHeatmap = true
      this.loadingDaily = true
      this.loadingTime = true
      
      console.log('获取课程分布数据...')
      
      getCourseDistributionAnalysis({
        semester: this.semester,
        department_id: this.departmentId
      }).then(response => {
        console.log('课程分布数据获取成功:', response)
        this.courseDistribution = response
        
        // 更新热力图
        this.updateHeatmapChart()
        this.loadingHeatmap = false
        
        // 更新每日分布图
        this.updateDailyChart()
        this.loadingDaily = false
        
        // 更新时段分布图
        this.updateTimeChart()
        this.loadingTime = false
      }).catch(error => {
        console.error('获取课程分布数据失败:', error)
        this.loadingHeatmap = false
        this.loadingDaily = false
        this.loadingTime = false
      })
    },
    
    // 获取资源优化建议数据
    getResourceOptimizationData() {
      this.loadingMismatch = true
      
      console.log('获取资源优化建议数据...')
      
      getResourceOptimizationSuggestions({
        semester: this.semester,
        department_id: this.departmentId
      }).then(response => {
        console.log('资源优化建议数据获取成功:', response)
        this.resourceOptimization = response
        this.loadingMismatch = false
      }).catch(error => {
        console.error('获取资源优化建议数据失败:', error)
        this.loadingMismatch = false
        
        // 失败时直接调用排课API和教室API处理
        Promise.all([
          getSchedulingResults({ _fetchAll: true, semester: this.semester }),
          getClassrooms({ _fetchAll: true })
        ]).then(([schedulingResponse, classroomsResponse]) => {
          this.updateResourceOptimization(
            schedulingResponse.results || [], 
            classroomsResponse.results || []
          )
        }).catch(err => {
          console.error('备选方案也失败:', err)
          this.loadingMismatch = false
        })
      })
    },
    
    // 获取资源效率数据
    getResourceEfficiencyData() {
      this.loadingEfficiency = true
      
      console.log('获取资源效率数据...')
      
      getResourceEfficiencyAnalysis({
        semester: this.semester,
        department_id: this.departmentId
      }).then(response => {
        console.log('资源效率数据获取成功:', response)
        this.resourceEfficiency = response
        
        // 更新效率图表
        this.updateEfficiencyChart()
        this.loadingEfficiency = false
      }).catch(error => {
        console.error('获取资源效率数据失败:', error)
        
        // 失败时直接调用排课API和教室API处理
        Promise.all([
          getSchedulingResults({ _fetchAll: true, semester: this.semester }),
          getClassrooms({ _fetchAll: true })
        ]).then(([schedulingResponse, classroomsResponse]) => {
          this.updateResourceEfficiency(
            schedulingResponse.results || [], 
            classroomsResponse.results || []
          )
        }).catch(err => {
          console.error('备选方案也失败:', err)
          this.loadingEfficiency = false
        })
      })
    },
    
    // 更新热力图
    updateHeatmapChart() {
      const hours = ['第1节', '第2节', '第3节', '第4节', '第5节', '第6节', 
                     '第7节', '第8节', '第9节', '第10节', '第11节', '第12节']
      const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
      
      console.log('更新热力图...')
      console.log('热力图数据:', this.courseDistribution.heatmapData)
      
      // 判断图表是否存在
      if (!this.heatmapChart) {
        console.warn('热力图实例不存在，尝试重新创建')
        this.$nextTick(() => {
          if (this.$refs.heatmapChart) {
            this.heatmapChart = echarts.init(this.$refs.heatmapChart)
          } else {
            console.error('热力图DOM元素不存在')
            return
          }
        })
        return
      }
      
      // 找出最大课程数，用于调整热力图的颜色范围
      let maxValue = 0
      if (this.courseDistribution.heatmapData && this.courseDistribution.heatmapData.length > 0) {
        maxValue = Math.max(...this.courseDistribution.heatmapData.map(item => item[2]))
      }
      
      // 默认最小为0，最大为10或数据中的最大值
      const maxRange = Math.max(10, maxValue)
      
      const option = {
        tooltip: {
          position: 'top',
          formatter: function (params) {
            return days[params.value[0]] + ' ' + hours[params.value[1]] + '<br>课程数: ' + params.value[2];
          }
        },
        grid: {
          top: '10%',
          left: '5%',
          right: '5%',
          bottom: '10%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: days,
          splitArea: {
            show: true
          }
        },
        yAxis: {
          type: 'category',
          data: hours,
          splitArea: {
            show: true
          }
        },
        visualMap: {
          min: 0,
          max: maxRange,
          calculable: true,
          orient: 'horizontal',
          left: 'center',
          bottom: '0%',
          inRange: {
            color: ['#e0f3f8', '#abd9e9', '#74add1', '#4575b4', '#313695']
          }
        },
        series: [{
          name: '课程数量',
          type: 'heatmap',
          data: this.courseDistribution.heatmapData || [],
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }]
      };
      
      try {
        this.heatmapChart.setOption(option)
        console.log('热力图更新成功')
      } catch (error) {
        console.error('热力图更新失败:', error)
      }
    },
    
    // 更新每日分布图
    updateDailyChart() {
      const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
      const data = this.courseDistribution.dayDistribution || [0, 0, 0, 0, 0, 0, 0]
      
      console.log('更新每日分布图...')
      console.log('每日分布数据:', data)
      
      // 判断图表是否存在
      if (!this.dailyChart) {
        console.warn('每日分布图实例不存在，尝试重新创建')
        this.$nextTick(() => {
          if (this.$refs.dailyChart) {
            this.dailyChart = echarts.init(this.$refs.dailyChart)
          } else {
            console.error('每日分布图DOM元素不存在')
            return
          }
        })
        return
      }
      
      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: days
        },
        yAxis: {
          type: 'value',
          name: '课程数'
        },
        series: [{
          data: data,
          type: 'bar',
          showBackground: true,
          backgroundStyle: {
            color: 'rgba(180, 180, 180, 0.2)'
          },
          itemStyle: {
            color: function(params) {
              // 工作日和周末使用不同的颜色
              return params.dataIndex <= 4 ? '#4e79a7' : '#e15759';
            }
          },
          label: {
            show: true,
            position: 'top'
          }
        }]
      };
      
      try {
        this.dailyChart.setOption(option)
        console.log('每日分布图更新成功')
      } catch (error) {
        console.error('每日分布图更新失败:', error)
      }
    },
    
    // 更新时段分布图
    updateTimeChart() {
      const sections = ['第1节', '第2节', '第3节', '第4节', '第5节', '第6节', 
                        '第7节', '第8节', '第9节', '第10节', '第11节', '第12节']
      const data = this.courseDistribution.sectionDistribution || Array(12).fill(0)
      
      console.log('更新时段分布图...')
      console.log('时段分布数据:', data)
      
      // 判断图表是否存在
      if (!this.timeChart) {
        console.warn('时段分布图实例不存在，尝试重新创建')
        this.$nextTick(() => {
          if (this.$refs.timeChart) {
            this.timeChart = echarts.init(this.$refs.timeChart)
          } else {
            console.error('时段分布图DOM元素不存在')
            return
          }
        })
        return
      }
      
      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: sections
        },
        yAxis: {
          type: 'value',
          name: '课程数'
        },
        series: [{
          data: data,
          type: 'bar',
          showBackground: true,
          backgroundStyle: {
            color: 'rgba(180, 180, 180, 0.2)'
          },
          itemStyle: {
            color: function(params) {
              // 早、中、晚课程使用不同的颜色
              if (params.dataIndex <= 3) return '#4e79a7';
              if (params.dataIndex <= 7) return '#59a14f';
              return '#f28e2c';
            }
          },
          label: {
            show: true,
            position: 'top'
          }
        }]
      };
      
      try {
        this.timeChart.setOption(option)
        console.log('时段分布图更新成功')
      } catch (error) {
        console.error('时段分布图更新失败:', error)
      }
    },
    
    // 更新资源效率图表
    updateEfficiencyChart() {
      const typeData = this.resourceEfficiency.typeEfficiency || []
      
      console.log('更新资源效率图表...')
      console.log('教室类型效率数据:', typeData)
      
      // 判断图表是否存在
      if (!this.efficiencyChart) {
        console.warn('效率图表实例不存在，尝试重新创建')
        this.$nextTick(() => {
          if (this.$refs.efficiencyChart) {
            this.efficiencyChart = echarts.init(this.$refs.efficiencyChart)
          } else {
            console.error('效率图表DOM元素不存在')
            return
          }
        })
        return
      }
      
      // 如果没有数据，显示一个默认值
      if (typeData.length === 0) {
        typeData.push({
          classroom_type: '普通教室',
          total_count: 0,
          used_count: 0,
          usage_hours: 0,
          utilization_rate: 0
        })
      }
      
      const roomTypes = typeData.map(item => item.classroom_type)
      const utilizationRates = typeData.map(item => item.utilization_rate)
      
      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          },
          formatter: function(params) {
            const data = typeData[params[0].dataIndex]
            return `${data.classroom_type}<br/>
                   <b>使用率:</b> ${data.utilization_rate}%<br/>
                   <b>教室总数:</b> ${data.total_count}<br/>
                   <b>已使用教室数:</b> ${data.used_count}<br/>
                   <b>使用总时长:</b> ${data.usage_hours}小时<br/>
                   <b>使用率计算:</b> ${data.used_count} / ${data.total_count} = ${data.utilization_rate}%`
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: roomTypes
        },
        yAxis: {
          type: 'value',
          name: '使用率(%)',
          min: 0,
          max: 100,
          axisLabel: {
            formatter: '{value}%'
          }
        },
        series: [{
          data: utilizationRates,
          type: 'bar',
          showBackground: true,
          backgroundStyle: {
            color: 'rgba(180, 180, 180, 0.2)'
          },
          itemStyle: {
            color: function(params) {
              const value = params.value
              if (value < 40) return '#e15759'; // 低使用率
              if (value < 70) return '#f28e2c'; // 中等使用率
              return '#59a14f'; // 高使用率
            }
          },
          label: {
            show: true,
            position: 'top',
            formatter: '{c}%'
          }
        }]
      };
      
      try {
        this.efficiencyChart.setOption(option)
        console.log('教室类型效率图更新成功')
      } catch (error) {
        console.error('教室类型效率图更新失败:', error)
      }
    },
    
    // 获取时段不平衡描述
    getTimeImbalance() {
      const { morningCourses, afternoonCourses, eveningCourses } = this.courseDistribution.statistics
      const max = Math.max(morningCourses, afternoonCourses, eveningCourses)
      
      if (max === morningCourses) return '上午'
      if (max === afternoonCourses) return '下午'
      return '晚上'
    },
    
    // 获取日期不平衡描述
    getDayImbalance() {
      const dayDistribution = this.courseDistribution.dayDistribution
      const workDays = dayDistribution.slice(0, 5)
      const maxIndex = workDays.indexOf(Math.max(...workDays))
      
      const days = ['周一', '周二', '周三', '周四', '周五']
      return days[maxIndex]
    }
  }
}
</script>

<style lang="scss" scoped>
.resource-analysis-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  
  .title-section {
    h1 {
      margin: 0;
      font-size: 24px;
      font-weight: 500;
      color: #303133;
    }
    
    p {
      margin: 5px 0 0;
      font-size: 14px;
      color: #909399;
    }
  }
  
  .filter-section {
    display: flex;
    gap: 10px;
  }
}

.statistics-scroll-container {
  height: calc(100vh - 160px);
  overflow-y: auto;
  margin-bottom: 20px;
  
  .statistics-content {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
  }
}

.stat-card {
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  
  .card-title {
    padding: 15px;
    border-bottom: 1px solid #ebeef5;
    font-size: 16px;
    font-weight: 500;
    color: #303133;
  }
  
  .card-content {
    padding: 15px;
    min-height: 200px;
  }
  
  .chart-container {
    height: 300px;
    width: 100%;
  }
}

// 分析得分卡片
.score-card {
  grid-column: span 2;
  display: flex;
  justify-content: space-around;
  padding: 20px;
  
  .score-item {
    text-align: center;
    padding: 20px;
    border-radius: 8px;
    width: 30%;
    
    &.good-score {
      background-color: rgba(89, 161, 79, 0.1);
      .score-value {
        color: #59a14f;
      }
    }
    
    &.medium-score {
      background-color: rgba(242, 142, 44, 0.1);
      .score-value {
        color: #f28e2c;
      }
    }
    
    &.low-score {
      background-color: rgba(225, 87, 89, 0.1);
      .score-value {
        color: #e15759;
      }
    }
    
    .score-value {
      font-size: 36px;
      font-weight: bold;
    }
    
    .score-label {
      font-size: 16px;
      font-weight: 500;
      margin-top: 10px;
      color: #303133;
    }
    
    .score-desc {
      font-size: 12px;
      color: #909399;
      margin-top: 5px;
    }
  }
}

// 热力图卡片
.heatmap-card {
  grid-column: span 2;
}

// 优化建议卡片
.suggestions-card {
  grid-column: span 2;
  
  .suggestion-item {
    display: flex;
    align-items: flex-start;
    padding: 10px 0;
    border-bottom: 1px solid #ebeef5;
    
    &:last-child {
      border-bottom: none;
    }
    
    i {
      font-size: 24px;
      margin-right: 15px;
      margin-top: 5px;
      color: #e6a23c;
    }
    
    .el-icon-success {
      color: #67c23a;
    }
    
    .suggestion-content {
      h4 {
        margin: 0 0 5px;
        font-size: 16px;
        font-weight: 500;
      }
      
      p {
        margin: 0;
        color: #606266;
        line-height: 1.5;
      }
    }
  }
}

// 资源匹配问题卡片
.mismatch-card {
  grid-column: span 2;
}
</style> 