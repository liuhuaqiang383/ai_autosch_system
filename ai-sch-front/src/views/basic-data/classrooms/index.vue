<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input
        v-model="listQuery.classroom_name"
        placeholder="教室名称"
        style="width: 200px;"
        class="filter-item"
        @keyup.enter.native="handleFilter"
      />
      <el-select v-model="listQuery.campus" placeholder="校区" clearable style="width: 150px" class="filter-item" @change="handleCampusChange">
        <el-option v-for="item in campusOptions" :key="item.id" :label="item.name" :value="item.id" />
      </el-select>
      <el-select v-model="listQuery.building" placeholder="教学楼" clearable style="width: 150px" class="filter-item">
        <el-option v-for="item in buildingOptions" :key="item.building_code" :label="item.building_name" :value="item.building_code" />
      </el-select>
      <el-select v-model="listQuery.classroom_type" placeholder="教室类型" clearable style="width: 150px" class="filter-item">
        <el-option v-for="item in classroomTypeOptions" :key="item.id" :label="item.name" :value="item.id" />
      </el-select>
      <el-select v-model="listQuery.is_enabled" placeholder="状态" clearable style="width: 100px" class="filter-item">
        <el-option v-for="item in statusOptions" :key="item.key" :label="item.label" :value="item.key" />
      </el-select>
      <el-button class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">
        搜索
      </el-button>
      <el-button
        class="filter-item"
        style="margin-left: 10px;"
        type="primary"
        icon="el-icon-plus"
        @click="handleCreate"
      >
        添加
      </el-button>
      <div v-if="total > 0" class="filter-item record-info">
        <span>共 <strong>{{ total }}</strong> 条记录</span>
      </div>
    </div>

    <div class="table-container">
      <el-table
        v-loading="listLoading"
        :data="list"
        element-loading-text="加载中..."
        border
        fit
        highlight-current-row
        style="width: 100%;"
        height="100%"
      >
        <el-table-column align="center" label="ID" width="80">
          <template slot-scope="scope">
            <span>{{ scope.row.id }}</span>
          </template>
        </el-table-column>

        <el-table-column width="150px" align="center" label="教室编号">
          <template slot-scope="scope">
            <span>{{ scope.row.classroom_code }}</span>
          </template>
        </el-table-column>

        <el-table-column width="180px" align="center" label="教室名称">
          <template slot-scope="scope">
            <span>{{ scope.row.classroom_name }}</span>
          </template>
        </el-table-column>

        <el-table-column width="120px" align="center" label="校区">
          <template slot-scope="scope">
            <span>{{ scope.row.campus_name }}</span>
          </template>
        </el-table-column>

        <el-table-column width="150px" align="center" label="所在教学楼">
          <template slot-scope="scope">
            <span>{{ scope.row.building_name }}</span>
          </template>
        </el-table-column>

        <el-table-column width="120px" align="center" label="教室类型">
          <template slot-scope="scope">
            <span>{{ scope.row.classroom_type_name }}</span>
          </template>
        </el-table-column>

        <el-table-column width="100px" align="center" label="容量">
          <template slot-scope="scope">
            <span>{{ scope.row.max_capacity }}</span>
          </template>
        </el-table-column>

        <el-table-column class-name="status-col" label="状态" width="100">
          <template slot-scope="scope">
            <el-tag :type="scope.row.is_enabled ? 'success' : 'danger'">
              {{ scope.row.is_enabled ? '可用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column width="120px" align="center" label="管理部门">
          <template slot-scope="scope">
            <span>{{ scope.row.manage_department_name || '未设置' }}</span>
          </template>
        </el-table-column>

        <el-table-column align="center" label="操作" width="230" fixed="right">
          <template slot-scope="scope">
            <el-button type="primary" size="mini" @click="handleUpdate(scope.row)">
              编辑
            </el-button>
            <el-button type="danger" size="mini" @click="handleDelete(scope.row)">
              删除
            </el-button>
            <el-button type="info" size="mini" @click="handleViewOccupancy(scope.row)">
              占用情况
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div class="pagination-wrapper">
      <pagination
        v-show="total > 0"
        :total="total"
        :page.sync="listQuery.page"
        :limit.sync="listQuery.limit"
        :layout="'total, prev, pager, next, jumper'"
        @pagination="handlePagination"
      />
    </div>

    <!-- 添加或修改教室对话框 -->
    <el-dialog :title="textMap[dialogStatus]" :visible.sync="dialogFormVisible">
      <el-form
        ref="dataForm"
        :rules="rules"
        :model="temp"
        label-position="left"
        label-width="100px"
        style="width: 400px; margin-left:50px;"
      >
        <el-form-item label="教室编号" prop="classroom_code">
          <el-input v-model="temp.classroom_code" />
        </el-form-item>
        <el-form-item label="教室名称" prop="classroom_name">
          <el-input v-model="temp.classroom_name" />
        </el-form-item>
        <el-form-item label="校区" prop="campus">
          <el-select v-model="temp.campus" class="filter-item" placeholder="请选择校区" @change="handleTempCampusChange">
            <el-option 
              v-for="item in campusOptions" 
              :key="item.id" 
              :label="item.name" 
              :value="item.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="所在教学楼" prop="building">
          <el-select v-model="temp.building" class="filter-item" placeholder="请选择教学楼">
            <el-option 
              v-for="item in tempBuildingOptions" 
              :key="item.building_code" 
              :label="item.building_name" 
              :value="item.building_code" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="教室类型" prop="classroom_type">
          <el-select v-model="temp.classroom_type" class="filter-item" placeholder="请选择教室类型">
            <el-option 
              v-for="item in classroomTypeOptions" 
              :key="item.id" 
              :label="item.name" 
              :value="item.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="最大容量" prop="max_capacity">
          <el-input-number v-model="temp.max_capacity" :min="1" :max="1000" />
        </el-form-item>
        <el-form-item label="管理部门">
          <el-select v-model="temp.manage_department" class="filter-item" placeholder="请选择管理部门" clearable>
            <el-option 
              v-for="dept in departmentOptions" 
              :key="dept.department_code" 
              :label="dept.department_name" 
              :value="dept.department_code" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="教室状态">
          <el-switch
            v-model="temp.is_enabled"
            active-color="#13ce66"
            inactive-color="#ff4949"
            :active-text="'可用'"
            :inactive-text="'停用'"
          />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="temp.remarks" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">
          取消
        </el-button>
        <el-button type="primary" @click="dialogStatus === 'create' ? createData() : updateData()">
          确认
        </el-button>
      </div>
    </el-dialog>

    <!-- 删除确认对话框 -->
    <el-dialog title="提示" :visible.sync="dialogDeleteVisible" width="30%">
      <span>确定要删除该教室信息吗？</span>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogDeleteVisible = false">取消</el-button>
        <el-button type="primary" @click="deleteData">确定</el-button>
      </span>
    </el-dialog>

    <!-- 教室占用情况对话框 -->
    <el-dialog title="教室占用情况" :visible.sync="occupancyDialogVisible" width="60%">
      <div class="occupancy-header">
        <h3>{{ currentClassroom.classroom_name }} ({{ currentClassroom.classroom_code }})</h3>
        <div class="occupancy-date">
          <el-date-picker
            v-model="occupancyDate"
            type="date"
            placeholder="选择日期"
            format="yyyy-MM-dd"
            value-format="yyyy-MM-dd"
            @change="loadOccupancyData"
          />
        </div>
      </div>
      <div v-loading="occupancyLoading" class="occupancy-container">
        <el-table
          v-if="occupancyData.length > 0"
          :data="occupancyData"
          border
          style="width: 100%"
        >
          <el-table-column prop="time_slot" label="时间段" width="120" />
          <el-table-column prop="course_name" label="课程名称" width="180" />
          <el-table-column prop="teacher_name" label="授课教师" width="120" />
          <el-table-column prop="class_name" label="上课班级" />
        </el-table>
        <div v-else class="no-data">
          <el-empty description="当前日期没有教室占用记录" />
        </div>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button type="primary" @click="occupancyDialogVisible = false">关闭</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { getClassrooms, createClassroom, updateClassroom, deleteClassroom, getClassroomTypes, getClassroomOccupancy, getCampusList } from '@/api/classroom'
import { getBuildings } from '@/api/building'
import { getDepartments } from '@/api/department'
import Pagination from '@/components/Pagination'

export default {
  name: 'Classrooms',
  components: { Pagination },
  filters: {
    statusFilter(status) {
      const statusMap = {
        true: 'success',
        false: 'danger'
      }
      return statusMap[status]
    },
    formatDate(timestamp) {
      const date = new Date(timestamp)
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
    }
  },
  data() {
    return {
      list: null,
      total: 0,
      listLoading: true,
      campusOptions: [], // 校区选项列表
      buildingOptions: [], // 教学楼选项列表
      tempBuildingOptions: [], // 表单中的教学楼选项列表
      classroomTypeOptions: [], // 教室类型选项列表
      departmentOptions: [], // 部门选项列表
      statusOptions: [
        { key: true, label: '可用' },
        { key: false, label: '停用' }
      ],
      listQuery: {
        page: 1,
        limit: 20,
        classroom_name: undefined,
        campus: undefined,
        building: undefined,
        classroom_type: undefined,
        is_enabled: undefined
      },
      temp: {
        id: undefined,
        classroom_code: '',
        classroom_name: '',
        campus: undefined,
        building: undefined,
        classroom_type: undefined,
        max_capacity: 50,
        manage_department: undefined,
        is_enabled: true,
        remarks: ''
      },
      dialogFormVisible: false,
      dialogDeleteVisible: false,
      occupancyDialogVisible: false,
      occupancyLoading: false,
      dialogStatus: '',
      textMap: {
        update: '编辑教室',
        create: '添加教室'
      },
      rules: {
        classroom_code: [{ required: true, message: '教室编号不能为空', trigger: 'blur' }],
        classroom_name: [{ required: true, message: '教室名称不能为空', trigger: 'blur' }],
        campus: [{ required: true, message: '校区不能为空', trigger: 'change' }],
        building: [{ required: true, message: '所在教学楼不能为空', trigger: 'change' }],
        classroom_type: [{ required: true, message: '教室类型不能为空', trigger: 'change' }],
        max_capacity: [{ required: true, message: '最大容量不能为空', trigger: 'blur' }]
      },
      deleteId: null,
      occupancyDate: new Date().toISOString().split('T')[0], // 当前日期
      occupancyData: [], // 教室占用数据
      currentClassroom: {} // 当前查看占用情况的教室
    }
  },
  created() {
    this.getList()
    this.getCampusList()
    this.getBuildingList()
    this.getClassroomTypeList()
    this.getDepartmentOptions()
  },
  methods: {
    getList() {
      this.listLoading = true
      getClassrooms(this.listQuery).then(response => {
        this.list = response.results
        this.total = response.count
        this.listLoading = false
      })
    },
    getCampusList() {
      getCampusList().then(response => {
        if (Array.isArray(response)) {
          this.campusOptions = response
        } else if (response && Array.isArray(response.results)) {
          this.campusOptions = response.results
        } else {
          this.campusOptions = []
        }
        console.log(`加载了${this.campusOptions.length}个校区选项`)
      })
    },
    getBuildingList(campusId) {
      const params = campusId ? { campus_name: campusId, _fetchAll: true } : { _fetchAll: true }
      getBuildings(params).then(response => {
        if (response && response.results) {
          this.buildingOptions = response.results.map(building => ({
            ...building,
            id: building.building_code // 为了兼容之前的代码，保留id字段
          }))
          console.log(`加载了${this.buildingOptions.length}栋教学楼选项`)
        } else {
          this.buildingOptions = []
        }
      })
    },
    getClassroomTypeList() {
      getClassroomTypes().then(response => {
        if (Array.isArray(response)) {
          this.classroomTypeOptions = response
        } else if (response && Array.isArray(response.results)) {
          this.classroomTypeOptions = response.results
        } else {
          this.classroomTypeOptions = []
        }
        console.log(`加载了${this.classroomTypeOptions.length}种教室类型选项`)
      })
    },
    getDepartmentOptions() {
      getDepartments({ _fetchAll: true }).then(response => {
        this.departmentOptions = response.results || []
        console.log(`加载了${this.departmentOptions.length}个部门选项`)
      })
    },
    handleFilter() {
      this.listQuery.page = 1
      this.getList()
    },
    handlePagination(data) {
      this.listQuery.page = data.page
      this.listQuery.limit = data.limit
      this.getList()
    },
    resetTemp() {
      this.temp = {
        id: undefined,
        classroom_code: '',
        classroom_name: '',
        campus: undefined,
        building: undefined,
        classroom_type: undefined,
        max_capacity: 50,
        manage_department: undefined,
        is_enabled: true,
        remarks: ''
      }
    },
    handleCreate() {
      this.resetTemp()
      this.dialogStatus = 'create'
      this.dialogFormVisible = true
      this.tempBuildingOptions = this.buildingOptions
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    createData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          const tempData = Object.assign({}, this.temp)
          
          // 将前端字段映射到后端字段
          if (tempData.manage_department) {
            tempData.management_department = tempData.manage_department
            delete tempData.manage_department
          }
          
          // 确保building字段使用building_code
          if (tempData.building && typeof tempData.building === 'object') {
            tempData.building = tempData.building.building_code
          }
          
          console.log('创建教室提交数据:', tempData)
          
          createClassroom(tempData).then(() => {
            this.dialogFormVisible = false
            this.$notify({
              title: '成功',
              message: '创建成功',
              type: 'success',
              duration: 2000
            })
            this.getList()
          }).catch(error => {
            console.error('创建教室错误:', error)
          })
        }
      })
    },
    handleUpdate(row) {
      this.temp = Object.assign({}, row) // 复制当前行数据
      
      // 确保管理部门字段正确设置
      if (row.management_department) {
        this.temp.manage_department = row.management_department
      }
      
      this.dialogStatus = 'update'
      this.dialogFormVisible = true
      
      // 根据校区获取教学楼列表
      if (this.temp.campus) {
        this.getFilteredBuildings(this.temp.campus)
      } else {
        this.tempBuildingOptions = this.buildingOptions
      }
      
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    updateData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          const tempData = Object.assign({}, this.temp)
          
          // 将前端字段映射到后端字段
          if (tempData.manage_department) {
            tempData.management_department = tempData.manage_department
            delete tempData.manage_department
          }
          
          // 确保building字段使用building_code
          if (tempData.building && typeof tempData.building === 'object') {
            tempData.building = tempData.building.building_code
          }
          
          console.log('更新教室提交数据:', tempData)
          
          updateClassroom(tempData).then(() => {
            this.dialogFormVisible = false
            this.$notify({
              title: '成功',
              message: '更新成功',
              type: 'success',
              duration: 2000
            })
            this.getList()
          }).catch(error => {
            console.error('更新教室错误:', error)
          })
        }
      })
    },
    handleDelete(row) {
      this.deleteId = row.id
      this.dialogDeleteVisible = true
    },
    deleteData() {
      deleteClassroom(this.deleteId).then(() => {
        this.$notify({
          title: '成功',
          message: '删除成功',
          type: 'success',
          duration: 2000
        })
        this.dialogDeleteVisible = false
        this.getList()
      })
    },
    handleCampusChange(campusId) {
      // 当校区选择改变时，更新教学楼列表
      this.listQuery.building = undefined // 清空已选择的教学楼
      if (campusId) {
        this.getBuildingList(campusId)
      } else {
        this.getBuildingList()
      }
    },
    handleTempCampusChange(campusId) {
      // 当表单中校区选择改变时，更新教学楼列表
      this.temp.building = undefined // 清空已选择的教学楼
      this.getFilteredBuildings(campusId)
    },
    getFilteredBuildings(campusId) {
      if (campusId) {
        const params = { campus_name: campusId, _fetchAll: true }
        getBuildings(params).then(response => {
          if (response && response.results) {
            this.tempBuildingOptions = response.results.map(building => ({
              ...building,
              id: building.building_code // 为了兼容之前的代码，保留id字段
            }))
            console.log(`加载了${this.tempBuildingOptions.length}栋校区为${campusId}的教学楼选项`)
          } else {
            this.tempBuildingOptions = []
          }
        })
      } else {
        this.tempBuildingOptions = this.buildingOptions
      }
    },
    handleViewOccupancy(row) {
      this.currentClassroom = row
      this.occupancyDialogVisible = true
      this.loadOccupancyData()
    },
    loadOccupancyData() {
      if (!this.currentClassroom.id || !this.occupancyDate) return
      
      this.occupancyLoading = true
      getClassroomOccupancy(this.currentClassroom.id, this.occupancyDate)
        .then(response => {
          this.occupancyData = response || []
        })
        .catch(() => {
          this.occupancyData = []
        })
        .finally(() => {
          this.occupancyLoading = false
        })
    }
  }
}
</script>

<style scoped>
.filter-container {
  padding-bottom: 10px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
}
.filter-item {
  display: inline-block;
  vertical-align: middle;
  margin-bottom: 10px;
  margin-right: 10px;
}
.record-info {
  margin-left: 10px;
  color: #606266;
}
.table-container {
  height: calc(100vh - 220px);
  min-height: 450px;
  margin-bottom: 10px;
  overflow: hidden;
}
.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding: 10px 0;
}
.occupancy-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.occupancy-header h3 {
  margin: 0;
}
.occupancy-container {
  min-height: 300px;
}
.no-data {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
}
</style> 