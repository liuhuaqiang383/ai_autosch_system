<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input
        v-model="listQuery.search"
        placeholder="输入课程/教师/教室/教学班"
        style="width: 300px;"
        class="filter-item"
        @keyup.enter.native="handleFilter"
      />
      <el-select
        v-model="listQuery.semester"
        placeholder="学期"
        clearable
        class="filter-item"
        style="width: 130px"
      >
        <el-option
          v-for="item in semesterOptions"
          :key="item.value"
          :label="item.label"
          :value="item.value"
        />
      </el-select>
      <el-select
        v-model="listQuery.day_of_week"
        placeholder="星期"
        clearable
        class="filter-item"
        style="width: 100px"
      >
        <el-option label="星期一" :value="1" />
        <el-option label="星期二" :value="2" />
        <el-option label="星期三" :value="3" />
        <el-option label="星期四" :value="4" />
        <el-option label="星期五" :value="5" />
        <el-option label="星期六" :value="6" />
        <el-option label="星期日" :value="7" />
      </el-select>
      <el-button
        v-waves
        class="filter-item"
        type="primary"
        icon="el-icon-search"
        @click="handleFilter"
      >
        搜索
      </el-button>
      <el-radio-group v-model="viewMode" class="filter-item" style="margin-left: 15px;">
        <el-radio-button label="list">列表视图</el-radio-button>
        <el-radio-button label="table">表格视图</el-radio-button>
      </el-radio-group>
      <el-button
        v-if="viewMode === 'table' && scheduleData.length > 0"
        class="filter-item"
        type="success"
        icon="el-icon-download"
        @click="exportToExcel"
      >
        导出Excel
      </el-button>
      <div v-if="total > 0 && viewMode === 'list'" class="filter-item record-info">
        <span>共 <strong>{{ total }}</strong> 条记录</span>
      </div>
    </div>

    <!-- 列表视图 -->
    <div v-if="viewMode === 'list'">
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
          <el-table-column label="学期" width="130px" align="center">
            <template slot-scope="{row}">
              <span>{{ row.semester }}</span>
            </template>
          </el-table-column>
          <el-table-column label="教学班编号" width="150px" align="center">
            <template slot-scope="{row}">
              <span>{{ row.teaching_class_code }}</span>
            </template>
          </el-table-column>
          <el-table-column label="课程名称" min-width="150px">
            <template slot-scope="{row}">
              <el-tooltip :content="row.course_code" placement="top">
                <span>{{ row.course_name }}</span>
              </el-tooltip>
            </template>
          </el-table-column>
          <el-table-column label="任课教师" width="120px" align="center">
            <template slot-scope="{row}">
              <el-tooltip :content="row.teacher_code" placement="top">
                <span>{{ row.teacher_name }}</span>
              </el-tooltip>
            </template>
          </el-table-column>
          <el-table-column label="教室" width="120px" align="center">
            <template slot-scope="{row}">
              <el-tooltip :content="row.classroom_code" placement="top">
                <span>{{ row.classroom_name }}</span>
              </el-tooltip>
            </template>
          </el-table-column>
          <el-table-column label="班级" width="180px" align="center">
            <template slot-scope="{row}">
              <span v-if="row.class_names && row.class_names.length > 0">{{ row.class_names.join(', ') }}</span>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column label="星期" width="80px" align="center">
            <template slot-scope="{row}">
              <span>星期{{ ['一', '二', '三', '四', '五', '六', '日'][row.day_of_week-1] }}</span>
            </template>
          </el-table-column>
          <el-table-column label="节次" width="120px" align="center">
            <template slot-scope="{row}">
              <span>{{ row.start_section }}-{{ row.end_section }}节</span>
            </template>
          </el-table-column>
          <el-table-column label="周次" width="180px" align="center">
            <template slot-scope="{row}">
              <span>{{ row.week_list }}</span>
            </template>
          </el-table-column>
          <el-table-column label="是否固定" width="80px" align="center">
            <template slot-scope="{row}">
              <el-tag :type="row.is_fixed ? 'warning' : 'success'">
                {{ row.is_fixed ? '固定' : '自动' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="pagination-wrapper">
        <pagination
          v-show="total>0"
          :total="total"
          :page.sync="listQuery.page"
          :limit.sync="listQuery.limit"
          :layout="'total, prev, pager, next, jumper'"
          @pagination="getList"
        />
      </div>
    </div>

    <!-- 表格视图 -->
    <div v-else class="schedule-table-view">
      <el-card class="box-card">
        <div slot="header" class="clearfix">
          <span>课表视图</span>
          <el-select
            v-model="tableViewFilter.type"
            placeholder="查看类型"
            style="width: 120px; float: right; margin-left: 10px;"
            @change="handleViewTypeChange"
          >
            <el-option label="教师课表" value="teacher" />
            <el-option label="班级课表" value="class" />
            <el-option label="教室课表" value="classroom" />
          </el-select>
          <el-select
            v-model="tableViewFilter.value"
            filterable
            remote
            reserve-keyword
            :placeholder="getPlaceholderByType(tableViewFilter.type)"
            :remote-method="remoteSearch"
            :loading="searchLoading"
            style="width: 260px; float: right;"
            @change="handleViewValueChange"
          >
            <el-option
              v-for="item in filterOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </div>
        
        <div class="schedule-table-container">
          <table class="schedule-table">
            <thead>
              <tr>
                <th width="60">节次</th>
                <th v-for="day in 7" :key="day">星期{{ ['一', '二', '三', '四', '五', '六', '日'][day-1] }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="section in 12" :key="section">
                <td>{{ section }}</td>
                <td 
                  v-for="day in 7" 
                  :key="day"
                  :class="{ 'has-class': hasClass(day, section) }"
                >
                  <div v-if="hasClass(day, section)" class="class-item">
                    <p class="course-name">{{ getClassInfo(day, section).course_name }}</p>
                    <p>{{ tableViewFilter.type === 'teacher' ? getClassInfo(day, section).classroom_name : getClassInfo(day, section).teacher_name }}</p>
                    <p>{{ tableViewFilter.type === 'classroom' ? getClassInfo(day, section).teacher_name : '' }}</p>
                    <p v-if="getClassInfo(day, section).class_names && getClassInfo(day, section).class_names.length > 0" class="class-names">班级: {{ getClassInfo(day, section).class_names.join(', ') }}</p>
                    <p class="week-list">{{ getClassInfo(day, section).week_list }}</p>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script>
import { getSchedulingResults } from '@/api/scheduling'
import { getTeachers } from '@/api/teacher'
import { getClassrooms } from '@/api/classroom'
import { getClasses } from '@/api/class'
import waves from '@/directive/waves'
import Pagination from '@/components/Pagination'
import * as XLSX from 'xlsx'
import FileSaver from 'file-saver'

export default {
  name: 'SchedulingResults',
  components: { Pagination },
  directives: { waves },
  data() {
    return {
      list: null,
      total: 0,
      listLoading: true,
      listQuery: {
        page: 1,
        limit: 20,
        search: undefined,
        semester: undefined,
        day_of_week: undefined
      },
      semesterOptions: [
        { value: '2023-2024-1', label: '2023-2024学年第一学期' },
        { value: '2023-2024-2', label: '2023-2024学年第二学期' },
        { value: '2024-2025-1', label: '2024-2025学年第一学期' },
        { value: '2024-2025-2', label: '2024-2025学年第二学期' }
      ],
      viewMode: 'list',
      // 表格视图相关数据
      tableViewFilter: {
        type: 'teacher', // teacher, class, classroom
        value: ''
      },
      filterOptions: [],
      scheduleData: [],
      searchLoading: false
    }
  },
  created() {
    this.getList()
  },
  methods: {
    getList() {
      this.listLoading = true
      getSchedulingResults({
        page: this.listQuery.page,
        limit: this.listQuery.limit,
        search: this.listQuery.search,
        semester: this.listQuery.semester,
        day_of_week: this.listQuery.day_of_week
      }).then(response => {
        this.list = response.results || []
        this.total = response.count || 0
        this.listLoading = false
      }).catch(error => {
        console.error('获取排课结果数据出错:', error)
        this.list = []
        this.total = 0
        this.listLoading = false
        this.$message.error('获取排课结果数据失败')
      })
    },
    handleFilter() {
      this.listQuery.page = 1
      this.getList()
    },
    // 加载筛选选项 - 只在需要时使用
    loadFilterOptions(type) {
      // 切换类型时清空选项
      this.filterOptions = []
      this.tableViewFilter.value = ''
    },
    // 切换视图类型
    handleViewTypeChange(type) {
      this.loadFilterOptions(type)
      this.scheduleData = []
    },
    // 切换筛选值
    handleViewValueChange(value) {
      if (!value) return
      
      // 根据不同的视图类型查询数据
      const params = {
        limit: 100
      }
      
      if (this.tableViewFilter.type === 'teacher') {
        params.teacher_code = value
      } else if (this.tableViewFilter.type === 'class') {
        params.class_code = value
      } else if (this.tableViewFilter.type === 'classroom') {
        params.classroom_code = value
      }
      
      this.listLoading = true
      getSchedulingResults(params).then(response => {
        this.scheduleData = response.results || []
        this.listLoading = false
      }).catch(error => {
        console.error('获取筛选课表数据出错:', error)
        this.scheduleData = []
        this.listLoading = false
        this.$message.error('获取课表数据失败')
      })
    },
    // 判断某个时间点是否有课
    hasClass(day, section) {
      if (!this.scheduleData || !Array.isArray(this.scheduleData) || this.scheduleData.length === 0) return false
      
      return this.scheduleData.some(item => 
        item && 
        item.day_of_week === day && 
        section >= item.start_section && 
        section <= item.end_section
      )
    },
    // 获取某个时间点的课程信息
    getClassInfo(day, section) {
      if (!this.scheduleData || !Array.isArray(this.scheduleData) || this.scheduleData.length === 0) return {}
      
      return this.scheduleData.find(item => 
        item && 
        item.day_of_week === day && 
        section >= item.start_section && 
        section <= item.end_section
      ) || {}
    },
    remoteSearch(query) {
      if (!query) {
        this.filterOptions = []
        return
      }
      
      this.searchLoading = true
      
      if (this.tableViewFilter.type === 'teacher') {
        getTeachers({ search: query }).then(response => {
          this.filterOptions = response.results.map(item => {
            return {
              value: item.teacher_code,
              label: `${item.teacher_code} - ${item.teacher_name}`
            }
          })
          this.searchLoading = false
        })
      } else if (this.tableViewFilter.type === 'class') {
        getClasses({ search: query }).then(response => {
          this.filterOptions = response.results.map(item => {
            return {
              value: item.class_code,
              label: `${item.class_code} - ${item.class_name}`
            }
          })
          this.searchLoading = false
        })
      } else if (this.tableViewFilter.type === 'classroom') {
        getClassrooms({ search: query }).then(response => {
          this.filterOptions = response.results.map(item => {
            return {
              value: item.classroom_code,
              label: `${item.classroom_code} - ${item.classroom_name}`
            }
          })
          this.searchLoading = false
        })
      }
    },
    // 根据类型获取不同的占位符提示文字
    getPlaceholderByType(type) {
      if (type === 'teacher') {
        return '请输入教师工号或姓名'
      } else if (type === 'class') {
        return '请输入班级编号或名称'
      } else if (type === 'classroom') {
        return '请输入教室编号或名称'
      }
      return '请输入搜索内容'
    },
    // 导出课表到Excel
    exportToExcel() {
      // 创建工作簿
      const workbook = XLSX.utils.book_new();
      
      // 构建表头
      const headers = ['节次', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日'];
      
      // 创建工作表数据
      const data = [];
      data.push(headers);
      
      // 填充数据
      for (let section = 1; section <= 12; section++) {
        const row = [section];
        
        // 遍历每一天
        for (let day = 1; day <= 7; day++) {
          if (this.hasClass(day, section)) {
            const classInfo = this.getClassInfo(day, section);
            let cellContent = '';
            
            // 根据视图类型组织内容
            if (this.tableViewFilter.type === 'teacher') {
              cellContent = `${classInfo.course_name}\n${classInfo.classroom_name}\n${classInfo.week_list}`;
            } else if (this.tableViewFilter.type === 'classroom') {
              cellContent = `${classInfo.course_name}\n${classInfo.teacher_name}\n${classInfo.week_list}`;
            } else {
              cellContent = `${classInfo.course_name}\n${classInfo.teacher_name}\n${classInfo.week_list}`;
            }
            
            row.push(cellContent);
          } else {
            row.push('');
          }
        }
        
        data.push(row);
      }
      
      // 创建工作表
      const worksheet = XLSX.utils.aoa_to_sheet(data);
      
      // 调整列宽
      const colWidths = [{ wch: 6 }, { wch: 20 }, { wch: 20 }, { wch: 20 }, 
                          { wch: 20 }, { wch: 20 }, { wch: 20 }, { wch: 20 }];
      worksheet['!cols'] = colWidths;
      
      // 调整行高
      const rowHeights = [];
      for (let i = 0; i < data.length; i++) {
        rowHeights.push({ hpt: 30 }); // 设置每行高度为30
      }
      worksheet['!rows'] = rowHeights;
      
      // 设置单元格样式 (XLSX库的免费版不支持样式，但我们可以提供基本格式)
      
      // 添加工作表到工作簿
      let sheetName = '课表';
      if (this.tableViewFilter.type === 'teacher') {
        const teacherOption = this.filterOptions.find(opt => opt.value === this.tableViewFilter.value);
        if (teacherOption) {
          sheetName = teacherOption.label;
        }
      } else if (this.tableViewFilter.type === 'classroom') {
        const classroomOption = this.filterOptions.find(opt => opt.value === this.tableViewFilter.value);
        if (classroomOption) {
          sheetName = classroomOption.label;
        }
      } else if (this.tableViewFilter.type === 'class') {
        const classOption = this.filterOptions.find(opt => opt.value === this.tableViewFilter.value);
        if (classOption) {
          sheetName = classOption.label;
        }
      }
      
      XLSX.utils.book_append_sheet(workbook, worksheet, sheetName);
      
      // 导出为Excel文件
      const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });
      const blob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      
      // 准备文件名
      let fileName = '课表';
      if (this.tableViewFilter.type === 'teacher') {
        fileName = `教师课表_${this.tableViewFilter.value}`;
      } else if (this.tableViewFilter.type === 'classroom') {
        fileName = `教室课表_${this.tableViewFilter.value}`;
      } else if (this.tableViewFilter.type === 'class') {
        fileName = `班级课表_${this.tableViewFilter.value}`;
      }
      
      FileSaver.saveAs(blob, `${fileName}.xlsx`);
      
      this.$message({
        message: '课表已成功导出',
        type: 'success'
      });
    }
  }
}
</script>

<style lang="scss" scoped>
.filter-container {
  padding-bottom: 10px;
}
.filter-item {
  display: inline-block;
  vertical-align: middle;
  margin-bottom: 10px;
  margin-right: 10px;
}
.record-info {
  float: right;
  line-height: 40px;
  color: #606266;
}
.table-container {
  height: calc(100vh - 220px);
  overflow: hidden;
}
.pagination-wrapper {
  margin-top: 15px;
}

.schedule-table-container {
  overflow-x: auto;
  margin-top: 20px;
  height: calc(100vh - 250px);
}

.schedule-table {
  width: 100%;
  border-collapse: collapse;
  
  th, td {
    border: 1px solid #dcdfe6;
    padding: 8px;
    text-align: center;
  }
  
  th {
    background-color: #f5f7fa;
    color: #606266;
  }
  
  td {
    height: 80px;
    vertical-align: top;
  }
  
  .has-class {
    background-color: #f0f9eb;
  }
  
  .class-item {
    font-size: 12px;
    line-height: 1.3;
    
    .course-name {
      font-weight: bold;
      margin-bottom: 4px;
    }
    
    .class-names {
      font-size: 11px;
      color: #409EFF;
    }
    
    .week-list {
      color: #909399;
      font-size: 11px;
    }
  }
}
</style>