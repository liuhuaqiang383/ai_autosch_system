<template>
  <div class="api-test-container">
    <h1>API连接测试</h1>
    
    <el-card class="test-card">
      <div slot="header">
        <span>用户登录API测试</span>
      </div>
      <el-form :model="loginForm" label-width="100px">
        <el-form-item label="用户名">
          <el-input v-model="loginForm.username"></el-input>
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="loginForm.password" type="password"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="testLoginApi" :loading="loginLoading">测试登录API</el-button>
        </el-form-item>
      </el-form>
      <div v-if="loginResult">
        <h3>测试结果:</h3>
        <pre>{{ loginResult }}</pre>
      </div>
    </el-card>
    
    <el-card class="test-card">
      <div slot="header">
        <span>基础数据API测试</span>
      </div>
      <el-select v-model="selectedApi" placeholder="选择要测试的API">
        <el-option label="院系列表" value="departments"></el-option>
        <el-option label="专业列表" value="majors"></el-option>
        <el-option label="班级列表" value="classes"></el-option>
        <el-option label="教室列表" value="classrooms"></el-option>
      </el-select>
      <el-button type="primary" @click="testBasicDataApi" :loading="dataLoading" style="margin-left: 10px;">测试</el-button>
      
      <div v-if="dataResult">
        <h3>测试结果:</h3>
        <pre>{{ dataResult }}</pre>
      </div>
    </el-card>
    
    <el-card class="test-card">
      <div slot="header">
        <span>排课API测试</span>
      </div>
      <el-select v-model="selectedSchedulingApi" placeholder="选择要测试的API">
        <el-option label="排课任务列表" value="tasks"></el-option>
        <el-option label="排课结果列表" value="results"></el-option>
        <el-option label="排课策略列表" value="strategies"></el-option>
      </el-select>
      <el-button type="primary" @click="testSchedulingApi" :loading="schedulingLoading" style="margin-left: 10px;">测试</el-button>
      
      <div v-if="schedulingResult">
        <h3>测试结果:</h3>
        <pre>{{ schedulingResult }}</pre>
      </div>
    </el-card>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'ApiTest',
  data() {
    return {
      loginForm: {
        username: 'admin',
        password: '123456'
      },
      loginLoading: false,
      loginResult: null,
      
      selectedApi: 'departments',
      dataLoading: false,
      dataResult: null,
      
      selectedSchedulingApi: 'tasks',
      schedulingLoading: false,
      schedulingResult: null
    }
  },
  computed: {
    baseURL() {
      return process.env.VUE_APP_BASE_API || 'http://localhost:8000/api'
    }
  },
  methods: {
    // 测试登录API
    testLoginApi() {
      this.loginLoading = true
      this.loginResult = null
      
      axios.post(`${this.baseURL}/users/login/`, this.loginForm)
        .then(response => {
          this.loginResult = JSON.stringify(response.data, null, 2)
          this.$message.success('登录API调用成功')
        })
        .catch(error => {
          this.loginResult = JSON.stringify(error.response ? error.response.data : error.message, null, 2)
          this.$message.error('登录API调用失败')
        })
        .finally(() => {
          this.loginLoading = false
        })
    },
    
    // 测试基础数据API
    testBasicDataApi() {
      this.dataLoading = true
      this.dataResult = null
      
      axios.get(`${this.baseURL}/basic_data/${this.selectedApi}/`)
        .then(response => {
          this.dataResult = JSON.stringify(response.data, null, 2)
          this.$message.success('基础数据API调用成功')
        })
        .catch(error => {
          this.dataResult = JSON.stringify(error.response ? error.response.data : error.message, null, 2)
          this.$message.error('基础数据API调用失败')
        })
        .finally(() => {
          this.dataLoading = false
        })
    },
    
    // 测试排课API
    testSchedulingApi() {
      this.schedulingLoading = true
      this.schedulingResult = null
      
      axios.get(`${this.baseURL}/scheduling/${this.selectedSchedulingApi}/`)
        .then(response => {
          this.schedulingResult = JSON.stringify(response.data, null, 2)
          this.$message.success('排课API调用成功')
        })
        .catch(error => {
          this.schedulingResult = JSON.stringify(error.response ? error.response.data : error.message, null, 2)
          this.$message.error('排课API调用失败')
        })
        .finally(() => {
          this.schedulingLoading = false
        })
    }
  }
}
</script>

<style lang="scss" scoped>
.api-test-container {
  padding: 20px;
  
  h1 {
    margin-bottom: 20px;
    font-size: 24px;
    color: #303133;
  }
  
  .test-card {
    margin-bottom: 20px;
    
    pre {
      background-color: #f5f7fa;
      padding: 15px;
      border-radius: 4px;
      margin-top: 10px;
      max-height: 300px;
      overflow: auto;
    }
  }
}
</style> 