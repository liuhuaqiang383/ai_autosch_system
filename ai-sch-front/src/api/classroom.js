import request from '@/utils/request'

// 缓存全部教室数据
let classroomsCache = null
let classroomsCacheTime = null
// 缓存教室类型
let classroomTypesCache = null
let classroomTypesCacheTime = null
// 缓存校区列表
let campusListCache = null
let campusListCacheTime = null
// 缓存过期时间（10分钟）
const CACHE_EXPIRY = 10 * 60 * 1000

/**
 * 获取教室列表
 * @param {Object} params - 查询参数 { page, limit, classroom_name, campus, building, classroom_type, is_enabled, _fetchAll }
 * @returns {Promise} - 返回教室列表数据
 */
export function getClassrooms(params) {
  // 获取所有教室（用于下拉选项）
  if (params && params._fetchAll) {
    // 当按照教学楼筛选时，不使用缓存或使用教学楼特定的缓存
    if (params.building) {
      console.log('按教学楼筛选教室, 教学楼:', params.building);
      
      // 创建一个深拷贝，移除_fetchAll标志
      const baseParams = { ...params }
      delete baseParams._fetchAll
      
      // 直接请求API获取教室数据，不使用缓存
      return request({
        url: '/basic_data/classrooms/',
        method: 'get',
        params: baseParams
      }).then(response => {
        return {
          count: response.count || 0,
          next: response.next,
          previous: response.previous,
          results: response.results || []
        }
      });
    }
    
    // 如果不是按教学楼筛选，则可以使用缓存
    // 检查缓存是否有效
    const now = Date.now()
    if (classroomsCache && classroomsCacheTime && (now - classroomsCacheTime < CACHE_EXPIRY)) {
      console.log('使用教室数据缓存, 共计', classroomsCache.count, '条记录')
      return Promise.resolve(classroomsCache)
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
        
        // 将前端分页参数转换为后端分页参数
        queryParams.offset = (queryParams.page - 1) * queryParams.limit
        
        const response = await request({
          url: '/basic_data/classrooms/',
          method: 'get',
          params: queryParams
        })
        
        if (!response || !response.results) {
          return allResults
        }
        
        // 合并结果
        allResults = allResults.concat(response.results)
        console.log(`已获取教室数据: 第${page}页, 累计${allResults.length}个教室`)
        
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
          classroomsCache = result
          classroomsCacheTime = Date.now()
          
          return result
        }
      } catch (error) {
        console.error('获取教室数据出错:', error)
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
    url: '/basic_data/classrooms/',
    method: 'get',
    params: query
  })
}

/**
 * 清除教室数据缓存
 */
export function clearClassroomsCache() {
  console.log('清除教室数据缓存')
  classroomsCache = null
  classroomsCacheTime = null
}

/**
 * 创建新教室
 * @param {Object} data - 教室数据
 * @returns {Promise}
 */
export function createClassroom(data) {
  return request({
    url: '/basic_data/classrooms/',
    method: 'post',
    data
  }).then(response => {
    clearClassroomsCache() // 清除缓存
    return response
  }).catch(error => {
    console.error('创建教室失败:', error.response ? error.response.data : error)
    throw error
  })
}

/**
 * 更新教室信息
 * @param {Object} data - 教室数据，必须包含id字段
 * @returns {Promise}
 */
export function updateClassroom(data) {
  return request({
    url: `/basic_data/classrooms/${data.id}/`,
    method: 'put',
    data
  }).then(response => {
    clearClassroomsCache() // 清除缓存
    return response
  }).catch(error => {
    console.error('更新教室失败:', error.response ? error.response.data : error)
    throw error
  })
}

/**
 * 删除教室
 * @param {Number} id - 教室ID
 * @returns {Promise}
 */
export function deleteClassroom(id) {
  return request({
    url: `/basic_data/classrooms/${id}/`,
    method: 'delete'
  }).then(response => {
    clearClassroomsCache() // 清除缓存
    return response
  })
}

/**
 * 获取教室占用情况
 * @param {Number} classroomId - 教室ID
 * @param {String} date - 日期，格式：YYYY-MM-DD
 * @returns {Promise}
 */
export function getClassroomOccupancy(classroomId, date) {
  return request({
    url: `/basic_data/classrooms/${classroomId}/occupancy/`,
    method: 'get',
    params: { date }
  })
}

/**
 * 清除教室类型缓存
 */
export function clearClassroomTypesCache() {
  classroomTypesCache = null
  classroomTypesCacheTime = null
  console.log('教室类型缓存已清除')
}

/**
 * 获取教室类型列表（用于下拉选择）
 * @returns {Promise}
 */
export function getClassroomTypes() {
  // 检查缓存是否有效
  const now = Date.now()
  if (classroomTypesCache && classroomTypesCacheTime && (now - classroomTypesCacheTime < CACHE_EXPIRY)) {
    console.log('使用教室类型缓存, 共计', classroomTypesCache.length, '种类型')
    return Promise.resolve(classroomTypesCache)
  }

  return request({
    url: '/basic_data/classroom-types/',
    method: 'get'
  }).then(response => {
    if (!response || !response.results) {
      // 如果后端API尚未实现，则使用备用方法从教室列表中提取
      // 创建一个映射对象存储所有类型
      const typeMap = {}
      
      // 创建一个递归函数获取所有页的数据
      const fetchAllPages = async (page = 1, accumulator = []) => {
        try {
          const response = await getClassrooms({ page, limit: 100 })
          
          if (!response || !response.results || response.results.length === 0) {
            return accumulator
          }
          
          // 提取当前页的教室类型
          response.results.forEach(classroom => {
            if (classroom.classroom_type) {
              typeMap[classroom.classroom_type] = classroom.classroom_type_name || classroom.classroom_type
            }
          })
          
          // 记录获取进度
          console.log(`已获取教室类型数据: 第${page}页, 累计${Object.keys(typeMap).length}种类型`)
          
          // 如果还有下一页，继续获取
          if (response.next) {
            return fetchAllPages(page + 1, accumulator.concat(response.results))
          } else {
            return accumulator.concat(response.results)
          }
        } catch (error) {
          console.error('获取教室类型页面出错:', error)
          return accumulator
        }
      }
      
      // 开始获取所有页面数据
      return fetchAllPages().then(allResults => {
        console.log(`教室类型提取完成，共获取${allResults.length}条教室数据，提取出${Object.keys(typeMap).length}种类型`)
        
        // 将教室类型转换为需要的对象格式
        const result = Object.keys(typeMap).map(type => ({
          id: type,
          name: typeMap[type] || type
        }))
        
        console.log('最终教室类型列表:', result)
        
        // 更新缓存
        classroomTypesCache = result
        classroomTypesCacheTime = Date.now()
        
        return result
      })
    }
    
    // 如果是直接从API获取到的结果，也要进行缓存
    if (Array.isArray(response)) {
      classroomTypesCache = response
      classroomTypesCacheTime = Date.now()
    } else if (response && Array.isArray(response.results)) {
      classroomTypesCache = response.results
      classroomTypesCacheTime = Date.now()
    }
    
    return response
  })
}

/**
 * 清除校区列表缓存
 */
export function clearCampusListCache() {
  campusListCache = null
  campusListCacheTime = null
  console.log('校区列表缓存已清除')
}

/**
 * 获取校区列表（用于下拉选择）
 * @returns {Promise}
 */
export function getCampusList() {
  // 检查缓存是否有效
  const now = Date.now()
  if (campusListCache && campusListCacheTime && (now - campusListCacheTime < CACHE_EXPIRY)) {
    console.log('使用校区列表缓存, 共计', campusListCache.length, '个校区')
    return Promise.resolve(campusListCache)
  }

  return request({
    url: '/basic_data/campuses/',
    method: 'get'
  }).then(response => {
    if (!response || !response.results) {
      // 如果后端API尚未实现，则使用备用方法从教室列表中提取
      // 创建一个映射对象存储所有校区
      const campusMap = {}
      
      // 创建一个递归函数获取所有页的数据
      const fetchAllPages = async (page = 1, accumulator = []) => {
        try {
          const response = await getClassrooms({ page, limit: 100 })
          
          if (!response || !response.results || response.results.length === 0) {
            return accumulator
          }
          
          // 提取当前页的校区
          response.results.forEach(classroom => {
            if (classroom.campus) {
              campusMap[classroom.campus] = true
            }
          })
          
          // 记录获取进度
          console.log(`已获取校区数据: 第${page}页, 累计${Object.keys(campusMap).length}个校区`)
          
          // 如果还有下一页，继续获取
          if (response.next) {
            return fetchAllPages(page + 1, accumulator.concat(response.results))
          } else {
            return accumulator.concat(response.results)
          }
        } catch (error) {
          console.error('获取校区页面出错:', error)
          return accumulator
        }
      }
      
      // 开始获取所有页面数据
      return fetchAllPages().then(allResults => {
        console.log(`校区提取完成，共获取${allResults.length}条教室数据，提取出${Object.keys(campusMap).length}个校区`)
        
        // 将校区转换为需要的对象格式
        const result = Object.keys(campusMap).map(campus => ({
          id: campus,
          name: campus
        }))
        
        console.log('最终校区列表:', result)
        
        // 更新缓存
        campusListCache = result
        campusListCacheTime = Date.now()
        
        return result
      })
    }
    
    // 如果是直接从API获取到的结果，也要进行缓存
    if (Array.isArray(response)) {
      campusListCache = response
      campusListCacheTime = Date.now()
    } else if (response && Array.isArray(response.results)) {
      campusListCache = response.results
      campusListCacheTime = Date.now()
    }
    
    return response
  })
} 