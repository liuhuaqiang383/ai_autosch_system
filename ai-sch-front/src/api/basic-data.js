import request from '@/utils/request'

// 获取院系列表
export function getDepartments(params) {
  return request({
    url: '/basic_data/departments/',
    method: 'get',
    params
  })
}

// 获取专业列表
export function getMajors(params) {
  return request({
    url: '/basic_data/majors/',
    method: 'get',
    params
  })
}

// 获取班级列表
export function getClasses(params) {
  return request({
    url: '/basic_data/classes/',
    method: 'get',
    params
  })
}

// 获取教学楼列表
export function getBuildings(params) {
  return request({
    url: '/basic_data/buildings/',
    method: 'get',
    params
  })
}

// 获取教室列表
export function getClassrooms(params) {
  return request({
    url: '/basic_data/classrooms/',
    method: 'get',
    params
  })
}

// 获取教师列表
export function getTeachers(params) {
  return request({
    url: '/basic_data/teachers/',
    method: 'get',
    params
  })
}

// 获取课程列表
export function getCourses(params) {
  return request({
    url: '/basic_data/courses/',
    method: 'get',
    params
  })
}

// 创建院系
export function createDepartment(data) {
  return request({
    url: '/basic_data/departments/',
    method: 'post',
    data
  })
}

// 更新院系
export function updateDepartment(id, data) {
  return request({
    url: `/basic_data/departments/${id}/`,
    method: 'put',
    data
  })
}

// 删除院系
export function deleteDepartment(id) {
  return request({
    url: `/basic_data/departments/${id}/`,
    method: 'delete'
  })
}

// 其他基础数据的增删改操作类似，按需添加 
