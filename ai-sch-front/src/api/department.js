import request from '@/utils/request'

// 缓存全部部门数据
let departmentsCache = null
let departmentsCacheTime = null
const CACHE_EXPIRY = 10 * 60 * 1000 // 缓存10分钟

/**
 * 获取部门列表
 * @param {Object} params - 查询参数 { page, limit, department_name, is_teaching_department, _fetchAll }
 * @returns {Promise} - 返回部门列表数据
 */
export function getDepartments(params) {
  // 检查是否需要获取所有部门（用于下拉选项）
  if (params && params._fetchAll) {
    // 检查缓存是否有效
    const now = Date.now()
    if (departmentsCache && departmentsCacheTime && (now - departmentsCacheTime < CACHE_EXPIRY)) {
      console.log('使用部门数据缓存, 共计', departmentsCache.count, '条记录')
      return Promise.resolve(departmentsCache)
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
        
        // 转换为Django REST Framework所需的分页参数
        queryParams.offset = (queryParams.page - 1) * queryParams.limit
        
        // 处理查询参数
        if (queryParams.department_name) {
          queryParams.search = queryParams.department_name
          delete queryParams.department_name
        }
        
        // 确保bool类型参数正确传递
        if (queryParams.is_teaching_department !== undefined) {
          queryParams.is_teaching_department = String(queryParams.is_teaching_department) === 'true'
        }
        
        const response = await request({
          url: '/basic_data/departments/',
          method: 'get',
          params: queryParams
        })
        
        if (!response || !response.results) {
          return allResults
        }
        
        // 合并结果
        allResults = allResults.concat(response.results)
        console.log(`已获取部门数据: 第${page}页, 累计${allResults.length}个部门`)
        
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
          departmentsCache = result
          departmentsCacheTime = Date.now()
          
          return result
        }
      } catch (error) {
        console.error('获取部门数据出错:', error)
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
  
  // 基本查询，使用分页参数
  // 复制查询参数
  const queryParams = { ...params }
  
  // 确保分页参数正确
  if (!queryParams.page) {
    queryParams.page = 1;
  }
  
  if (!queryParams.limit) {
    queryParams.limit = 10;
  }
  
  // 转换为Django REST Framework所需的分页参数
  const apiParams = { ...queryParams };
  
  // 根据页码和每页大小计算offset
  apiParams.offset = (apiParams.page - 1) * apiParams.limit;
  
  // 修改department_name为搜索参数
  if (apiParams.department_name) {
    apiParams.search = apiParams.department_name;
    delete apiParams.department_name;
  }
  
  // 确保bool类型参数正确传递
  if (apiParams.is_teaching_department !== undefined) {
    apiParams.is_teaching_department = String(apiParams.is_teaching_department) === 'true';
  }
  
  return request({
    url: '/basic_data/departments/',
    method: 'get',
    params: apiParams
  })
}

/**
 * 清除部门缓存
 */
export function clearDepartmentsCache() {
  departmentsCache = null
  departmentsCacheTime = null
  console.log('部门数据缓存已清除')
}

/**
 * 创建新部门
 * @param {Object} data - 部门数据
 * @returns {Promise}
 */
export function createDepartment(data) {
  return request({
    url: '/basic_data/departments/',
    method: 'post',
    data
  }).then(response => {
    clearDepartmentsCache() // 清除缓存
    return response
  })
}

/**
 * 更新部门信息
 * @param {Number} id - 部门ID
 * @param {Object} data - 部门数据
 * @returns {Promise}
 */
export function updateDepartment(id, data) {
  return request({
    url: `/basic_data/departments/${id}/`,
    method: 'put',
    data
  }).then(response => {
    clearDepartmentsCache() // 清除缓存
    return response
  })
}

/**
 * 删除部门
 * @param {Number} id - 部门ID
 * @returns {Promise}
 */
export function deleteDepartment(id) {
  return request({
    url: `/basic_data/departments/${id}/`,
    method: 'delete'
  }).then(response => {
    clearDepartmentsCache() // 清除缓存
    return response
  })
} 