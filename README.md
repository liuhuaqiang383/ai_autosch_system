# 说明

这是一个基于 Django 和 VUE 开发的智能排课系统

后端 django，前端 vue，数据库 mysql

数据库目前使用 111.spl，其他两个是之前的，导入时注意自己的 mysql 版本是不是 8 开头的

后端进入 ai_sch_back 后安装 django 和 Django REST Framework，应该还有 mysqlclient 之后运行

## 系统环境要求与安装说明

### 环境要求

- Python 3.11
- Node.js 14+
- MySQL 8.0+

**启动后端服务**
基于 Django 和 Django REST Framework 开发的智能排课系统后端

cd ai_sch_back
python manage.py runserver


若运行报错检查报错信息看是否是因为缺少模块，pip install 对应模块

若数据库问题考虑执行数据库迁移：


python manage.py makemigrations
python manage.py migrate

后端默认运行在 http://127.0.0.1:8000

**启动前端服务**

1. **安装 Node.js 依赖**

   cd ai-sch-front
   npm install

2. **启动开发服务器**

  npm run serve

   默认运行在 http://localhost:8080


### 系统依赖说明

#### 后端主要依赖

- Django 4.2+
- Django REST framework 3.12+
- django-cors-headers 3.10+
- mysqlclient 8.0+
- numpy 1.21+
- pandas 1.3+

#### 前端主要依赖

- Vue.js 2.6+
- Element UI 2.15+
- Vuex 3.6+
- Vue Router 3.5+
- Axios 0.21+
- ECharts 5.2+
- moment.js 2.29+



## 后端 API 数据与接口

根据后端代码分析，系统后端提供了以下数据模型和 API 接口：

### 1. 基础数据 API 接口

#### 1.1 部门管理 `/basic_data/departments/`

- **数据模型**: `DepartmentInfo`
- **主要字段**:
  - department_code (部门代码)
  - department_name (部门名称)
  - short_name (部门简称)
  - unit_type (所属单位类别)
  - unit_affiliation (所属单位办别)
  - is_teaching_department (是否开课院系)
  - is_enabled (是否启用)
- **API 支持**:
  - 支持 CRUD 操作
  - 支持按部门代码、名称、启用状态、是否开课等过滤
  - 支持搜索功能
  - 支持排序功能
  - 返回数据包含关联的部门名称

#### 1.2 专业管理 `/basic_data/majors/`

- **数据模型**: `MajorInfo`
- **主要字段**:
  - major_code (专业编号)
  - major_name (专业名称)
  - short_name (专业简称)
  - school_system (学制)
  - english_name (英文名称)
  - is_active (开办状态)
  - department (关联部门)
- **API 支持**:
  - 支持 CRUD 操作
  - 支持按专业编号、名称、所属部门、状态等过滤
  - 支持搜索功能
  - 支持排序功能
  - 返回数据包含关联的部门名称

#### 1.3 班级管理 `/basic_data/classes/`

- **数据模型**: `ClassInfo`
- **主要字段**:
  - class_code (班级编号)
  - class_name (班级名称)
  - class_short_name (班级简称)
  - enrollment_year (入学年份)
  - is_graduated (是否毕业)
  - department (所属院系)
  - major_code (专业编号)
  - class_size (班级人数)
  - fixed_classroom (固定教室)
- **API 支持**:
  - 支持 CRUD 操作
  - 支持按班级编号、名称、所属部门、专业、入学年份等过滤
  - 支持搜索功能
  - 支持排序功能
  - 返回数据包含关联的部门名称和专业名称

#### 1.4 教学楼管理 `/basic_data/buildings/`

- **数据模型**: `BuildingInfo`
- **主要字段**:
  - building_code (教学楼编号)
  - building_name (教学楼名称)
  - campus_name (校区名称)
  - status (可用状态)
- **API 支持**:
  - 支持 CRUD 操作
  - 支持按教学楼编号、名称、校区、状态等过滤
  - 支持搜索功能
  - 支持排序功能

#### 1.5 教室管理 `/basic_data/classrooms/`

- **数据模型**: `ClassroomInfo`
- **主要字段**:
  - classroom_code (教室编号)
  - classroom_name (教室名称)
  - campus (校区)
  - building (教学楼)
  - classroom_type (教室类型)
  - max_capacity (最大上课容纳人数)
  - is_enabled (是否启用)
- **API 支持**:
  - 支持 CRUD 操作
  - 支持按教室编号、名称、校区、所在楼宇、类型等过滤
  - 支持搜索功能
  - 支持排序功能
  - 返回数据包含关联的教学楼名称和管理部门名称

#### 1.6 教师管理 `/basic_data/teachers/`

- **数据模型**: `TeacherInfo`
- **主要字段**:
  - teacher_code (工号)
  - teacher_name (姓名)
  - gender (性别)
  - title (职称)
  - department (单位)
  - is_external (是否外聘)
- **API 支持**:
  - 支持 CRUD 操作
  - 支持按工号、姓名、所属部门、职称等过滤
  - 支持搜索功能
  - 支持排序功能
  - 返回数据包含关联的部门名称

#### 1.7 课程管理 `/basic_data/courses/`

- **数据模型**: `CourseInfo`
- **主要字段**:
  - course_code (课程编号)
  - course_name (课程名称)
  - course_type (课程类型)
  - course_nature (课程性质)
  - department (开课院系)
  - total_hours (总学时)
  - credits (学分)
  - is_enabled (是否启用)
- **API 支持**:
  - 支持 CRUD 操作
  - 支持按课程编号、名称、所属部门、课程性质、类型等过滤
  - 支持搜索功能
  - 支持排序功能
  - 返回数据包含关联的部门名称

#### 1.8 校区列表 `/basic_data/campuses/`

- **接口**: `GET /basic_data/campuses/`
- **功能**: 获取所有不重复的校区名称列表。
- **响应**: 返回格式为 `[{'id': '校区名', 'name': '校区名'}, ...]` 的列表。

#### 1.9 教室类型列表 `/basic_data/classroom-types/`

- **接口**: `GET /basic_data/classroom-types/`
- **功能**: 获取所有不重复的教室类型列表。
- **响应**: 返回格式为 `[{'id': '类型名', 'name': '类型名'}, ...]` 的列表。

### 2. 排课管理 API 接口

#### 2.1 排课任务管理 `/scheduling/tasks/`

- **数据模型**: `SchedulingTask`
- **主要字段**:
  - teaching_class_code (教学班编号)
  - teaching_class_name (教学班名称)
  - course_code (课程编号)
  - course_name (课程名称)
  - teacher_code (教师工号)
  - teacher_name (教师姓名)
  - class_size (班级人数)
  - semester (学期)
  - is_scheduled (是否已排课)
- **API 支持**:
  - 支持 CRUD 操作
  - 支持按教学班编号、课程名称、教师姓名、是否排课等过滤
  - 支持搜索功能
  - 支持排序功能

#### 2.2 排课结果管理 `/scheduling/results/`

- **数据模型**: `SchedulingResult`
- **主要字段**:
  - task (关联排课任务)
  - semester (学期)
  - course_code (课程编号)
  - course_name (课程名称)
  - teacher_code (教师工号)
  - teacher_name (教师姓名)
  - teaching_class_code (教学班编号)
  - teaching_class_name (教学班名称)
  - classroom_code (教室编号)
  - classroom_name (教室名称)
  - day_of_week (星期几)
  - start_section (开始节次)
  - end_section (结束节次)
  - week_list (周次列表)
  - is_fixed (是否固定)
- **API 支持**:
  - 支持 CRUD 操作
  - 支持按学期、课程、教师、教室、时间段等过滤
  - 支持搜索功能
  - 支持排序功能

#### 2.3 排课策略管理 `/scheduling/strategies/`

- **数据模型**: `SchedulingStrategy`
- **主要字段**:
  - `strategy_name` (策略名称)
  - `description` (策略描述)
  - `is_default` (是否默认策略)
  - 权重和约束字段 (如 `teacher_weight`, `avoid_teacher_conflict` 等)
- **API 支持**:
  - 支持 CRUD 操作
  - 支持按 `strategy_name`, `is_default` 过滤
  - 支持按 `strategy_name`, `description` 搜索
  - 支持按 `strategy_name`, `created_at` 排序
  - **特殊动作**: `POST /scheduling/strategies/{pk}/set_default/` - 设置为默认策略

#### 2.4 排课日志管理 `/scheduling/logs/`

- **数据模型**: `SchedulingLog`
- **主要字段**:
  - `task_id` (任务 ID)
  - `task_type` (任务类型)
  - `status` (状态)
  - `progress` (进度)
  - `message` (消息)
- **API 支持**:
  - 支持 CRUD 操作 (通常是只读)
  - 支持按 `task_id`, `task_type`, `status` 过滤
  - 支持按 `task_id`, `message` 搜索
  - 支持按 `created_at` 排序

#### 2.5 教学班组成管理 `/scheduling/compositions/`

- **数据模型**: `TeachingClassComposition`
- **主要字段**:
  - `teaching_class_code` (关联排课任务/教学班编号)
  - `class_code` (关联班级编号)
- **API 支持**:
  - 支持 CRUD 操作
  - 支持按 `teaching_class_code`, `class_code` 过滤
  - 支持搜索

#### 2.6 一键排课触发

- **接口**: `GET /scheduling/tasks/run-scheduling/`
- **功能**: 启动后台自动排课算法。
- **响应**: 返回排课结果摘要，包括成功和失败的任务信息。

### 3. 用户与认证 API 接口

#### 3.1 用户管理 `/users/users/`

- **数据模型**: `SysUser`
- **主要字段**:
  - `username` (用户名)
  - `name` (真实姓名)
  - `email` (邮箱)
  - `phone` (手机号)
  - `status` (状态：0-禁用，1-启用)
  - `is_active` (是否活跃)
  - `is_staff` (是否是管理员)
  - `last_login` (最后登录时间)
  - `roles` (关联角色)
- **API 支持**:
  - 支持 CRUD 操作
  - 支持按 `username`, `status`, `is_active`, `is_staff` 过滤
  - 支持按 `username`, `name`, `email`, `phone` 搜索
  - 支持按 `id`, `username`, `create_time` 排序

#### 3.2 角色管理 `/users/roles/`

- **数据模型**: `SysRole`
- **主要字段**:
  - `code` (角色编码)
  - `name` (角色名称)
  - `description` (角色描述)
- **API 支持**:
  - 支持 CRUD 操作
  - 支持按 `code`, `name` 过滤
  - 支持按 `code`, `name`, `description` 搜索
  - 支持按 `id`, `code`, `name`, `create_time` 排序

#### 3.3 用户认证

- **登录**: `POST /users/login/`
  - **请求**: `username`, `password`
  - **响应**: 成功时返回用户信息，失败时返回错误信息。
- **登出**: `POST /users/logout/`
  - **响应**: 返回成功登出信息。

#### 3.4 用户个人信息 `/users/profile/`

- **获取信息**: `GET /users/profile/`
  - **响应**: 返回当前登录用户的信息。
- **更新信息**: `PUT /users/profile/`
  - **请求**: 用户信息字段（部分更新）
  - **响应**: 成功时返回更新后的用户信息。
