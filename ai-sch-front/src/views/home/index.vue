<template>
  <div class="home-container">
    <div class="home-scroll-container">
      <div class="welcome-section">
        <h1 class="welcome-title">欢迎使用智能排课系统</h1>
        <p class="welcome-description">集成化的教学资源管理与智能排课解决方案</p>
      </div>
      
      <div class="module-cards">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-card shadow="hover" class="module-card" @click.native="goTo('/basic-data')">
              <div class="module-icon">
                <i class="el-icon-document"></i>
              </div>
              <div class="module-info">
                <h2>基础数据</h2>
                <p>管理部门、专业、班级、教师、教室等基础信息</p>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="8">
            <el-card shadow="hover" class="module-card" @click.native="goTo('/scheduling')">
              <div class="module-icon">
                <i class="el-icon-date"></i>
              </div>
              <div class="module-info">
                <h2>排课管理</h2>
                <p>管理排课任务、配置策略、查看结果与手动调整</p>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="8">
            <el-card shadow="hover" class="module-card" @click.native="goTo('/statistics')">
              <div class="module-icon">
                <i class="el-icon-data-analysis"></i>
              </div>
              <div class="module-info">
                <h2>统计分析</h2>
                <p>教室利用率、教师工作量和教学资源分析</p>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
      
      <div class="quick-stats">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card shadow="hover" class="stat-card">
              <div v-loading="loading.departments" class="stat-content">
                <div class="stat-value">{{ stats.departments || 0 }}</div>
                <div class="stat-label">部门数量</div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="6">
            <el-card shadow="hover" class="stat-card">
              <div v-loading="loading.teachers" class="stat-content">
                <div class="stat-value">{{ stats.teachers || 0 }}</div>
                <div class="stat-label">教师人数</div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="6">
            <el-card shadow="hover" class="stat-card">
              <div v-loading="loading.courses" class="stat-content">
                <div class="stat-value">{{ stats.courses || 0 }}</div>
                <div class="stat-label">课程数量</div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="6">
            <el-card shadow="hover" class="stat-card">
              <div v-loading="loading.scheduledTasks" class="stat-content">
                <div class="stat-value">{{ stats.scheduledTasks || 0 }}</div>
                <div class="stat-label">已排课程</div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
      
      <div class="system-info">
        <el-card shadow="hover">
          <template slot="header">
            <div class="system-info-header">
              <span>系统信息</span>
              <el-button type="text" icon="el-icon-refresh" @click="fetchStats">刷新</el-button>
            </div>
          </template>
          <div class="system-content">
            <p><strong>当前学期:</strong> {{ currentSemester }}</p>
            <p><strong>系统版本:</strong> v1.0.0</p>
            <p><strong>最后更新:</strong> {{ new Date().toLocaleDateString() }}</p>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script>
import { getDepartments } from '@/api/department'
import { getTeachers } from '@/api/teacher'
import { getCourses } from '@/api/course'
import { getSchedulingResults } from '@/api/scheduling'

export default {
  name: 'Home',
  data() {
    return {
      stats: {
        departments: 0,
        teachers: 0,
        courses: 0,
        scheduledTasks: 0
      },
      currentSemester: '2023-2024学年第一学期',
      loading: {
        departments: false,
        teachers: false,
        courses: false,
        scheduledTasks: false
      }
    }
  },
  created() {
    this.fetchStats()
  },
  methods: {
    goTo(path) {
      this.$router.push(path)
    },
    async fetchStats() {
      // 获取部门数量
      this.loading.departments = true
      try {
        const departmentsResponse = await getDepartments({ _fetchAll: true })
        this.stats.departments = departmentsResponse.count || 0
        this.loading.departments = false
      } catch (error) {
        console.error('获取部门数量失败:', error)
        this.loading.departments = false
      }

      // 获取教师数量
      this.loading.teachers = true
      try {
        const teachersResponse = await getTeachers({ _fetchAll: true })
        this.stats.teachers = teachersResponse.count || 0
        this.loading.teachers = false
      } catch (error) {
        console.error('获取教师数量失败:', error)
        this.loading.teachers = false
      }

      // 获取课程数量
      this.loading.courses = true
      try {
        const coursesResponse = await getCourses({ _fetchAll: true })
        this.stats.courses = coursesResponse.count || 0
        this.loading.courses = false
      } catch (error) {
        console.error('获取课程数量失败:', error)
        this.loading.courses = false
      }

      // 获取已排课程数量
      this.loading.scheduledTasks = true
      try {
        const schedulingResponse = await getSchedulingResults({ _fetchAll: true })
        this.stats.scheduledTasks = schedulingResponse.count || 0
        this.loading.scheduledTasks = false
      } catch (error) {
        console.error('获取已排课程失败:', error)
        this.loading.scheduledTasks = false
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.home-container {
  height: 100%;
  overflow: hidden;
}

.home-scroll-container {
  height: calc(100vh - 90px);
  overflow-y: auto;
  padding: 20px;
}

.welcome-section {
  text-align: center;
  margin-bottom: 40px;
  
  .welcome-title {
    font-size: 28px;
    font-weight: 500;
    color: #303133;
    margin-bottom: 10px;
  }
  
  .welcome-description {
    font-size: 16px;
    color: #606266;
  }
}

.module-cards {
  margin-bottom: 30px;
  
  .module-card {
    height: 180px;
    cursor: pointer;
    display: flex;
    flex-direction: column;
    justify-content: center;
    transition: all 0.3s;
    
    &:hover {
      transform: translateY(-5px);
      box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
    }
    
    .module-icon {
      font-size: 48px;
      color: #409EFF;
      margin-bottom: 15px;
      display: flex;
      justify-content: center;
    }
    
    .module-info {
      text-align: center;
      
      h2 {
        font-size: 18px;
        font-weight: 500;
        margin-bottom: 8px;
        color: #303133;
      }
      
      p {
        font-size: 14px;
        color: #606266;
        line-height: 1.5;
      }
    }
  }
}

.quick-stats {
  margin-bottom: 30px;
  
  .stat-card {
    text-align: center;
    padding: 10px 0;
    
    .stat-content {
      min-height: 80px;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
    }
    
    .stat-value {
      font-size: 36px;
      font-weight: 500;
      color: #409EFF;
      margin-bottom: 5px;
    }
    
    .stat-label {
      font-size: 14px;
      color: #606266;
    }
  }
}

.system-info {
  margin-bottom: 20px;
  
  .system-info-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .system-content {
    color: #606266;
    
    p {
      margin: 8px 0;
      line-height: 1.5;
    }
  }
}
</style> 