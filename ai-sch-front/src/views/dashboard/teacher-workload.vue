<template>
  <div class="teacher-workload-container">
    <div class="page-header">
      <div class="title-section">
        <h1>教师工作量统计分析</h1>
        <p>统计本学期教师工作量分布情况</p>
      </div>
      <div class="filter-section">
        <el-select v-model="departmentId" placeholder="选择院系" clearable @change="refreshCharts">
          <el-option v-for="item in departmentOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
        <el-select v-model="timeRange" placeholder="时间范围" @change="refreshCharts">
          <el-option label="本学期" value="semester" />
          <el-option label="本学年" value="year" />
        </el-select>
      </div>
    </div>

    <div class="statistics-scroll-container">
      <div class="statistics-content">
        <!-- 教师工作量统计卡片 -->
        <div class="stat-card workload-distribution-card">
          <div class="card-title">教师工作量分布</div>
          <div v-loading="teacherLoading" class="card-content">
            <div ref="teacherWorkloadChart" class="chart-container"></div>
          </div>
        </div>

        <!-- 院系工作量对比卡片 -->
        <div class="stat-card department-comparison-card">
          <div class="card-title">院系工作量对比</div>
          <div v-loading="departmentLoading" class="card-content">
            <div ref="departmentWorkloadChart" class="chart-container"></div>
          </div>
        </div>

        <!-- 职称层级工作量卡片 -->
        <div class="stat-card title-analysis-card">
          <div class="card-title">职称层级工作量分析</div>
          <div v-loading="titleLoading" class="card-content">
            <div ref="titleWorkloadChart" class="chart-container"></div>
          </div>
        </div>

        <!-- 教师工作量明细表格 -->
        <div class="stat-card teacher-table-card">
          <div class="card-title">
            <span>教师工作量明细</span>
            <el-button style="float: right; padding: 3px 0" type="text" @click="refreshTeacherWorkload">刷新</el-button>
          </div>
          <div v-loading="tableLoading" class="card-content">
            <el-table :data="paginatedTeacherWorkload" stripe style="width: 100%">
              <el-table-column prop="teacher_name" label="教师姓名" width="120" />
              <el-table-column prop="department_name" label="所属院系" width="180" />
              <el-table-column prop="title" label="职称" width="120" />
              <el-table-column prop="course_count" label="授课门数" width="100" sortable />
              <el-table-column prop="total_hours" label="总学时" width="100" sortable />
              <el-table-column prop="class_count" label="教学班数" width="100" sortable />
              <el-table-column prop="student_count" label="学生总数" width="120" sortable />
            </el-table>
            <div class="pagination-container">
              <el-pagination
                background
                layout="total, sizes, prev, pager, next"
                :total="teacherWorkloadList.length"
                :page-size="pageSize"
                :current-page.sync="currentPage"
                @size-change="handleSizeChange"
                @current-change="handleCurrentChange"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import { getTeacherWorkload, getDepartmentWorkload, getTitleWorkload } from '@/api/statistics'
import { getDepartments } from '@/api/department'

export default {
  name: 'TeacherWorkload',
  data() {
    return {
      // 图表实例
      teacherChart: null,
      departmentChart: null,
      titleChart: null,
      
      // 筛选条件
      departmentId: '',
      timeRange: 'semester',
      departmentOptions: [],
      
      // 加载状态
      teacherLoading: false,
      departmentLoading: false,
      titleLoading: false,
      tableLoading: false,
      
      // 表格数据
      teacherWorkloadList: [],
      
      // 分页
      currentPage: 1,
      pageSize: 10
    }
  },
  computed: {
    // 分页后的教师工作量数据
    paginatedTeacherWorkload() {
      const startIndex = (this.currentPage - 1) * this.pageSize
      return this.teacherWorkloadList.slice(startIndex, startIndex + this.pageSize)
    }
  },
  created() {
    this.getDepartmentOptions()
  },
  mounted() {
    this.initCharts()
    this.loadAllData()
    
    // 窗口大小变化时，重新调整图表大小
    window.addEventListener('resize', this.resizeCharts)
  },
  beforeDestroy() {
    // 销毁图表实例
    if (this.teacherChart) this.teacherChart.dispose()
    if (this.departmentChart) this.departmentChart.dispose()
    if (this.titleChart) this.titleChart.dispose()
    
    // 移除事件监听
    window.removeEventListener('resize', this.resizeCharts)
  },
  methods: {
    // 初始化所有图表
    initCharts() {
      // 教师工作量分布图表
      this.teacherChart = echarts.init(this.$refs.teacherWorkloadChart)
      
      // 院系工作量对比图表
      this.departmentChart = echarts.init(this.$refs.departmentWorkloadChart)
      
      // 职称层级工作量图表
      this.titleChart = echarts.init(this.$refs.titleWorkloadChart)
    },
    
    // 加载所有数据
    loadAllData() {
      this.getTeacherWorkloadData()
      this.getDepartmentWorkloadData()
      this.getTitleWorkloadData()
    },
    
    // 刷新图表
    refreshCharts() {
      this.getTeacherWorkloadData()
      this.getTitleWorkloadData()
    },
    
    // 重新调整图表大小
    resizeCharts() {
      if (this.teacherChart) this.teacherChart.resize()
      if (this.departmentChart) this.departmentChart.resize()
      if (this.titleChart) this.titleChart.resize()
    },
    
    // 获取部门选项
    getDepartmentOptions() {
      getDepartments({ 
        _fetchAll: true,
        is_teaching_department: true  // 只获取教学部门(院系)
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
          
          console.log(`已加载${this.departmentOptions.length}个院系部门选项`);
        }
      }).catch(error => {
        console.error('获取院系部门选项失败:', error);
      });
    },
    
    // 获取教师工作量数据
    getTeacherWorkloadData() {
      this.teacherLoading = true
      this.tableLoading = true
      
      getTeacherWorkload({
        department_id: this.departmentId,
        time_period: this.timeRange
      }).then(response => {
        this.teacherWorkloadList = response.results || []
        
        // 取前15名教师进行展示
        const topTeachers = this.teacherWorkloadList.slice(0, 15)
        
        const teacherNames = topTeachers.map(item => item.teacher_name)
        const workloadData = topTeachers.map(item => item.total_hours)
        const courseCountData = topTeachers.map(item => item.course_count)
        
        // 更新教师工作量图表
        this.teacherChart.setOption({
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'shadow'
            }
          },
          legend: {
            data: ['总学时', '课程门数']
          },
          grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
          },
          xAxis: [
            {
              type: 'value'
            }
          ],
          yAxis: [
            {
              type: 'category',
              data: teacherNames,
              axisLabel: {
                interval: 0
              }
            }
          ],
          series: [
            {
              name: '总学时',
              type: 'bar',
              stack: 'total',
              emphasis: {
                focus: 'series'
              },
              data: workloadData
            },
            {
              name: '课程门数',
              type: 'bar',
              stack: 'total',
              emphasis: {
                focus: 'series'
              },
              data: courseCountData.map(count => count * 10) // 放大课程数量使图表更直观
            }
          ]
        })
        
        this.teacherLoading = false
        this.tableLoading = false
      }).catch(() => {
        this.teacherLoading = false
        this.tableLoading = false
      })
    },
    
    // 获取院系工作量数据
    getDepartmentWorkloadData() {
      this.departmentLoading = true
      
      getDepartmentWorkload({
        time_period: this.timeRange
      }).then(response => {
        const data = response.results || []
        
        const departmentNames = data.map(item => item.department_name)
        const totalHours = data.map(item => item.total_hours)
        const avgHours = data.map(item => item.avg_hours_per_teacher)
        
        // 更新院系工作量图表
        this.departmentChart.setOption({
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'shadow'
            }
          },
          legend: {
            data: ['总学时', '人均学时']
          },
          grid: {
            left: '3%',
            right: '4%',
            bottom: '15%',
            containLabel: true
          },
          xAxis: {
            type: 'category',
            data: departmentNames,
            axisLabel: {
              interval: 0,
              rotate: 30
            }
          },
          yAxis: [
            {
              type: 'value',
              name: '总学时',
              min: 0,
              axisLabel: {
                formatter: '{value}'
              }
            },
            {
              type: 'value',
              name: '人均学时',
              min: 0,
              axisLabel: {
                formatter: '{value}'
              }
            }
          ],
          series: [
            {
              name: '总学时',
              type: 'bar',
              data: totalHours
            },
            {
              name: '人均学时',
              type: 'line',
              yAxisIndex: 1,
              data: avgHours,
              itemStyle: {
                color: '#91cc75'
              }
            }
          ]
        })
        
        this.departmentLoading = false
      }).catch(() => {
        this.departmentLoading = false
      })
    },
    
    // 获取职称工作量数据
    getTitleWorkloadData() {
      this.titleLoading = true
      
      getTitleWorkload({
        department_id: this.departmentId,
        time_period: this.timeRange
      }).then(response => {
        const data = response.results || []
        
        const titles = data.map(item => item.title)
        const teacherCounts = data.map(item => item.teacher_count)
        const totalHours = data.map(item => item.total_hours)
        const avgHours = data.map(item => item.avg_hours_per_teacher)
        
        // 更新职称工作量图表
        this.titleChart.setOption({
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
            data: ['教师人数', '总学时', '人均学时']
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
              data: titles,
              axisPointer: {
                type: 'shadow'
              }
            }
          ],
          yAxis: [
            {
              type: 'value',
              name: '人数/学时',
              min: 0,
              axisLabel: {
                formatter: '{value}'
              }
            },
            {
              type: 'value',
              name: '人均学时',
              min: 0,
              axisLabel: {
                formatter: '{value}'
              }
            }
          ],
          series: [
            {
              name: '教师人数',
              type: 'bar',
              data: teacherCounts
            },
            {
              name: '总学时',
              type: 'bar',
              data: totalHours
            },
            {
              name: '人均学时',
              type: 'line',
              yAxisIndex: 1,
              data: avgHours,
              itemStyle: {
                color: '#ee6666'
              }
            }
          ]
        })
        
        this.titleLoading = false
      }).catch(() => {
        this.titleLoading = false
      })
    },
    
    // 刷新教师工作量数据
    refreshTeacherWorkload() {
      this.getTeacherWorkloadData()
    },
    
    // 处理每页显示数量变化
    handleSizeChange(size) {
      this.pageSize = size
    },
    
    // 处理页码变化
    handleCurrentChange(page) {
      this.currentPage = page
    }
  }
}
</script>

<style lang="scss" scoped>
.teacher-workload-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 50px);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  
  .title-section {
    h1 {
      font-size: 24px;
      font-weight: bold;
      margin-bottom: 5px;
    }
    
    p {
      font-size: 14px;
      color: #606266;
      margin: 0;
    }
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

.filter-section {
  display: flex;
  gap: 10px;
  
  .el-select {
    width: 150px;
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
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .card-content {
    min-height: 300px;
  }
  
  .chart-container {
    width: 100%;
    height: 300px;
  }
}

.workload-distribution-card,
.department-comparison-card,
.title-analysis-card,
.teacher-table-card {
  grid-column: span 2;
}

.pagination-container {
  margin-top: 15px;
  text-align: right;
}
</style> 