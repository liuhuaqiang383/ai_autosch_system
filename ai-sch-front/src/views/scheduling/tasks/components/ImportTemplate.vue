<template>
  <div>
    <el-dialog
      title="批量导入说明"
      :visible.sync="dialogVisible"
      width="70%"
    >
      <div class="template-info">
        <h3>导入说明</h3>
        <p>请按照以下步骤进行排课任务批量导入：</p>
        <ol>
          <li>下载Excel模板</li>
          <li>按照模板要求填写数据（必填字段不能为空）</li>
          <li>保存Excel文件并上传</li>
        </ol>

        <h3>Excel文件格式说明</h3>
        <p>Excel文件应包含以下字段（<span class="required">*</span>为必填字段）：</p>
        <div class="template-table">
          <el-table
            :data="templateFields"
            border
            style="width: 100%"
          >
            <el-table-column
              prop="field"
              label="字段名"
              width="180"
            ></el-table-column>
            <el-table-column
              prop="required"
              label="是否必填"
              width="100"
            >
              <template slot-scope="scope">
                <span v-if="scope.row.required" class="required">是</span>
                <span v-else>否</span>
              </template>
            </el-table-column>
            <el-table-column
              prop="description"
              label="说明"
            ></el-table-column>
          </el-table>
        </div>

        <h3>示例数据</h3>
        <div class="template-table">
          <el-table
            :data="sampleData"
            border
            style="width: 100%"
          >
            <el-table-column
              v-for="field in templateFields"
              :key="field.field"
              :prop="field.field"
              :label="field.field"
            ></el-table-column>
          </el-table>
        </div>

        <div class="download-area">
          <el-button type="primary" icon="el-icon-download" @click="downloadTemplate">
            下载Excel模板
          </el-button>
        </div>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">关闭</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'ImportTemplate',
  props: {
    visible: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      templateFields: [
        { field: 'teaching_class_code', required: true, description: '教学班编号，如"2023-CS101-01"' },
        { field: 'teaching_class_name', required: true, description: '教学班名称，如"数据结构-计算机科学与技术-01班"' },
        { field: 'semester', required: true, description: '学期，如"2023-2024-1"' },
        { field: 'course_code', required: true, description: '课程编号，必须是系统中已存在的课程编号' },
        { field: 'course_name', required: false, description: '课程名称，用于辅助显示，可不填' },
        { field: 'teacher_code', required: true, description: '教师工号，必须是系统中已存在的教师工号' },
        { field: 'teacher_name', required: false, description: '教师姓名，用于辅助显示，可不填' },
        { field: 'department', required: true, description: '开课院系编码，必须是系统中已存在的部门编码' },
        { field: 'class_size', required: true, description: '教学班人数，如40' },
        { field: 'course_hours', required: true, description: '开课学时，如32' },
        { field: 'scheduling_priority', required: false, description: '排课优先级，1-10的整数，数字越大优先级越高，默认为5' },
        { field: 'campus', required: false, description: '校区，如"东校区"' },
        { field: 'consecutive_periods', required: false, description: '连排节次，默认为2' },
        { field: 'classroom_type', required: false, description: '教室类型，如"多媒体教室"' }
      ],
      sampleData: [
        {
          teaching_class_code: '2023-CS101-01',
          teaching_class_name: '数据结构-计算机科学与技术-01班',
          semester: '2023-2024-1',
          course_code: 'CS101',
          course_name: '数据结构',
          teacher_code: 'T001',
          teacher_name: '张三',
          department: 'CS',
          class_size: 40,
          course_hours: 32,
          scheduling_priority: 8,
          campus: '东校区',
          consecutive_periods: 2,
          classroom_type: '多媒体教室'
        },
        {
          teaching_class_code: '2023-CS102-01',
          teaching_class_name: '计算机网络-计算机科学与技术-01班',
          semester: '2023-2024-1',
          course_code: 'CS102',
          course_name: '计算机网络',
          teacher_code: 'T002',
          teacher_name: '李四',
          department: 'CS',
          class_size: 35,
          course_hours: 48,
          scheduling_priority: 7,
          campus: '东校区',
          consecutive_periods: 3,
          classroom_type: '多媒体教室'
        }
      ]
    }
  },
  computed: {
    dialogVisible: {
      get() {
        return this.visible
      },
      set(val) {
        this.$emit('update:visible', val)
      }
    }
  },
  methods: {
    downloadTemplate() {
      // 在实际应用中，这里可以调用API下载Excel模板
      // 这里只是一个示例
      this.$message({
        message: 'Excel模板下载功能将在后端API实现后开放',
        type: 'info'
      })
      
      // 实际下载代码可能如下：
      // window.location.href = '/api/scheduling/tasks/template/download'
    }
  }
}
</script>

<style scoped>
.template-info {
  padding: 10px;
}
.template-table {
  margin: 15px 0;
}
.required {
  color: #F56C6C;
}
.download-area {
  margin-top: 20px;
  text-align: center;
}
</style> 