import request from '@/utils/request'

/**
 * 获取教学楼列表
 * @param {Object} params - 查询参数 { page, limit, building_name, campus_name, status }
 * @returns {Promise} - 返回教学楼列表数据
 */
export function getBuildings(params) {
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
      url: '/basic_data/buildings/',
      method: 'get',
      params: query
    })
  } 
  // 获取所有数据（用于下拉选项）
  else {
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
          url: '/basic_data/buildings/',
          method: 'get',
          params: queryParams
        })
        
        if (!response || !response.results) {
          return allResults
        }
        
        // 合并结果
        allResults = allResults.concat(response.results)
        console.log(`已获取教学楼数据: 第${page}页, 累计${allResults.length}栋`)
        
        // 如果还有下一页，继续获取
        if (response.next) {
          return fetchAllPages(page + 1)
        } else {
          // 构造类似于标准响应的结果
          return {
            count: allResults.length,
            next: null,
            previous: null,
            results: allResults
          }
        }
      } catch (error) {
        console.error('获取教学楼数据出错:', error)
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
 * 创建新教学楼
 * @param {Object} data - 教学楼数据
 * @returns {Promise}
 */
export function createBuilding(data) {
  return request({
    url: '/basic_data/buildings/',
    method: 'post',
    data
  })
}

/**
 * 更新教学楼信息
 * @param {Object} data - 教学楼数据，必须包含id字段
 * @returns {Promise}
 */
export function updateBuilding(data) {
  return request({
    url: `/basic_data/buildings/${data.id}/`,
    method: 'put',
    data
  })
}

/**
 * 删除教学楼
 * @param {Number} id - 教学楼ID
 * @returns {Promise}
 */
export function deleteBuilding(id) {
  return request({
    url: `/basic_data/buildings/${id}/`,
    method: 'delete'
  })
} 