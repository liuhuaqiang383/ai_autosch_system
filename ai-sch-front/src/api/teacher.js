import request from '@/utils/request'

// 缓存全部教师数据
let teachersCache = null
let teachersCacheTime = null
const CACHE_EXPIRY = 10 * 60 * 1000 // 缓存10分钟

/**
 * 获取教师列表
 * @param {Object} params - 查询参数 { page, limit, teacher_name, department, title, is_external, _fetchAll }
 * @returns {Promise} - 返回教师列表数据
 */
export function getTeachers(params) {
  // 基本查询，使用分页参数
  if (!params || (params && !params._fetchAll)) {
    // 确保分页参数存在
    const query = { ...params }
    if (!query.page) {
      query.page = 1
    }
    if (!query.limit) {
      query.limit = 20
    }

    // 将前端分页参数转换为后端分页参数
    query.offset = (query.page - 1) * query.limit

    return request({
      url: '/basic_data/teachers/',
      method: 'get',
      params: query
    })
  }
  // 获取所有数据（用于下拉选项）
  else {
    // 检查缓存是否有效
    const now = Date.now()
    if (teachersCache && teachersCacheTime && (now - teachersCacheTime < CACHE_EXPIRY)) {
      console.log('使用教师数据缓存, 共计', teachersCache.count, '条记录')
      return Promise.resolve(teachersCache)
    }
    
    // 创建一个深拷贝，移除_fetchAll标志
    const baseParams = { ...params }
    delete baseParams._fetchAll
    
    // 创建一个数组存储所有结果
    let allResults = []
    
    // 递归函数获取所有页面数据
    const fetchAllPages = async (page = 1) => {
      try {
        const queryParams = { 
          ...baseParams,
          page,
          limit: 100
        }
        
        const response = await request({
          url: '/basic_data/teachers/',
          method: 'get',
          params: queryParams
        })
        
        if (!response || !response.results) {
          return allResults
        }
        
        // 合并结果
        allResults = allResults.concat(response.results)
        console.log(`已获取教师数据: 第${page}页, 累计${allResults.length}名教师`)
        
        // 如果还有下一页，继续获取
        if (response.next) {
          return fetchAllPages(page + 1)
        } else {
          // 构造类似于标准响应的结果
          const result = {
            count: allResults.length,
            next: null,
            previous: null,
            results: allResults
          }
          
          // 更新缓存
          teachersCache = result
          teachersCacheTime = Date.now()
          
          return result
        }
      } catch (error) {
        console.error('获取教师数据出错:', error)
        // 返回已获取的结果
        return {
          count: allResults.length,
          next: null,
          previous: null,
          results: allResults
        }
      }
    }
    
    // 开始获取所有页面
    return fetchAllPages()
  }
}

/**
 * 清除教师数据缓存
 * 在添加、编辑或删除教师后调用此方法
 */
export function clearTeachersCache() {
  teachersCache = null
  teachersCacheTime = null
  console.log('教师数据缓存已清除')
}

/**
 * 创建新教师
 * @param {Object} data - 教师数据
 * @returns {Promise}
 */
export function createTeacher(data) {
  return request({
    url: '/basic_data/teachers/',
    method: 'post',
    data
  }).then(response => {
    clearTeachersCache() // 清除缓存
    return response
  })
}

/**
 * 更新教师信息
 * @param {Object} data - 教师数据，必须包含id字段
 * @returns {Promise}
 */
export function updateTeacher(data) {
  return request({
    url: `/basic_data/teachers/${data.id}/`,
    method: 'put',
    data
  }).then(response => {
    clearTeachersCache() // 清除缓存
    return response
  })
}

/**
 * 删除教师
 * @param {Number} id - 教师ID
 * @returns {Promise}
 */
export function deleteTeacher(id) {
  return request({
    url: `/basic_data/teachers/${id}/`,
    method: 'delete'
  }).then(response => {
    clearTeachersCache() // 清除缓存
    return response
  })
}

/**
 * 批量导入教师
 * @param {FormData} formData - 包含Excel文件的FormData
 * @returns {Promise}
 */
export function batchImportTeachers(formData) {
  return request({
    url: '/basic_data/teachers/batch-import/',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  }).then(response => {
    clearTeachersCache() // 清除缓存
    return response
  })
} 