import request from '@/utils/request'

// 缓存全部课程数据
let coursesCache = null
let coursesCacheTime = null
// 缓存课程类型
let courseTypesCache = null
let courseTypesCacheTime = null
// 缓存课程性质
let courseNaturesCache = null
let courseNaturesCacheTime = null
// 缓存课程属性
let courseAttributesCache = null
let courseAttributesCacheTime = null
// 缓存课程类别
let courseCategoriesCache = null
let courseCategoriesCacheTime = null
// 缓存过期时间（10分钟）
const CACHE_EXPIRY = 10 * 60 * 1000

/**
 * 获取课程列表
 * @param {Object} params - 查询参数 { page, limit, course_name, course_code, department, course_type, course_nature, is_enabled, _fetchAll }
 * @returns {Promise} - 返回课程列表数据
 */
export function getCourses(params) {
  // 获取所有课程（用于下拉选项）
  if (params && params._fetchAll) {
    // 检查缓存是否有效
    const now = Date.now()
    if (coursesCache && coursesCacheTime && (now - coursesCacheTime < CACHE_EXPIRY)) {
      console.log('使用课程数据缓存, 共计', coursesCache.count, '条记录')
      return Promise.resolve(coursesCache)
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
          url: '/basic_data/courses/',
          method: 'get',
          params: queryParams
        })
        
        if (!response || !response.results) {
          return allResults
        }
        
        // 合并结果
        allResults = allResults.concat(response.results)
        console.log(`已获取课程数据: 第${page}页, 累计${allResults.length}个课程`)
        
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
          coursesCache = result
          coursesCacheTime = Date.now()
          
          return result
        }
      } catch (error) {
        console.error('获取课程数据出错:', error)
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
    url: '/basic_data/courses/',
    method: 'get',
    params: query
  })
}

/**
 * 清除课程数据缓存
 * 在添加、编辑或删除课程后调用此方法
 */
export function clearCoursesCache() {
  coursesCache = null
  coursesCacheTime = null
  console.log('课程数据缓存已清除')
}

/**
 * 创建新课程
 * @param {Object} data - 课程数据
 * @returns {Promise}
 */
export function createCourse(data) {
  return request({
    url: '/basic_data/courses/',
    method: 'post',
    data
  }).then(response => {
    clearCoursesCache() // 清除缓存
    return response
  }).catch(error => {
    console.error('创建课程失败:', error.response ? error.response.data : error)
    throw error
  })
}

/**
 * 更新课程信息
 * @param {Object} data - 课程数据，必须包含id字段
 * @returns {Promise}
 */
export function updateCourse(data) {
  return request({
    url: `/basic_data/courses/${data.id}/`,
    method: 'put',
    data
  }).then(response => {
    clearCoursesCache() // 清除缓存
    return response
  }).catch(error => {
    console.error('更新课程失败:', error.response ? error.response.data : error)
    throw error
  })
}

/**
 * 删除课程
 * @param {Number} id - 课程ID
 * @returns {Promise}
 */
export function deleteCourse(id) {
  return request({
    url: `/basic_data/courses/${id}/`,
    method: 'delete'
  }).then(response => {
    clearCoursesCache() // 清除缓存
    return response
  })
}

/**
 * 清除课程类型缓存
 */
export function clearCourseTypesCache() {
  courseTypesCache = null
  courseTypesCacheTime = null
  console.log('课程类型缓存已清除')
}

/**
 * 获取课程类型列表（用于下拉选择）
 * @returns {Promise}
 */
export function getCourseTypes() {
  // 检查缓存是否有效
  const now = Date.now()
  if (courseTypesCache && courseTypesCacheTime && (now - courseTypesCacheTime < CACHE_EXPIRY)) {
    console.log('使用课程类型缓存, 共计', courseTypesCache.length, '种类型')
    return Promise.resolve(courseTypesCache)
  }

  // 创建一个映射对象存储所有类型
  const typeMap = {}
  // 创建一个递归函数获取所有页的数据
  const fetchAllPages = async (page = 1, accumulator = []) => {
    try {
      const response = await getCourses({ page, limit: 100 })
      
      if (!response || !response.results || response.results.length === 0) {
        return accumulator
      }
      
      // 提取当前页的课程类型
      response.results.forEach(course => {
        if (course.course_type) {
          typeMap[course.course_type] = true
        }
      })
      
      // 记录获取进度
      console.log(`已获取课程类型数据: 第${page}页, 累计${Object.keys(typeMap).length}种类型`)
      
      // 如果还有下一页，继续获取
      if (response.next) {
        return fetchAllPages(page + 1, accumulator.concat(response.results))
      } else {
        return accumulator.concat(response.results)
      }
    } catch (error) {
      console.error('获取课程类型页面出错:', error)
      return accumulator
    }
  }
  
  // 开始获取所有页面数据
  return fetchAllPages().then(allResults => {
    console.log(`课程类型提取完成，共获取${allResults.length}条课程数据，提取出${Object.keys(typeMap).length}种类型`)
    
    // 如果没有提取到数据，确保基本类型存在
    if (Object.keys(typeMap).length === 0) {
      typeMap['A类(纯理论课)'] = true
      typeMap['B类(理论+实践课)'] = true
      typeMap['C类(纯实践课)'] = true
    }
    
    // 将课程类型转换为需要的对象格式
    const result = Object.keys(typeMap).map(type => ({
      id: type,
      name: type
    }))
    
    console.log('最终课程类型列表:', result)
    
    // 更新缓存
    courseTypesCache = result
    courseTypesCacheTime = Date.now()
    
    return result
  })
}

/**
 * 清除课程性质缓存
 */
export function clearCourseNaturesCache() {
  courseNaturesCache = null
  courseNaturesCacheTime = null
  console.log('课程性质缓存已清除')
}

/**
 * 获取课程性质列表（用于下拉选择）
 * @returns {Promise}
 */
export function getCourseNatures() {
  // 检查缓存是否有效
  const now = Date.now()
  if (courseNaturesCache && courseNaturesCacheTime && (now - courseNaturesCacheTime < CACHE_EXPIRY)) {
    console.log('使用课程性质缓存, 共计', courseNaturesCache.length, '种性质')
    return Promise.resolve(courseNaturesCache)
  }
  
  // 创建一个映射对象存储所有性质
  const natureMap = {}
  // 创建一个递归函数获取所有页的数据
  const fetchAllPages = async (page = 1, accumulator = []) => {
    try {
      const response = await getCourses({ page, limit: 100 })
      
      if (!response || !response.results || response.results.length === 0) {
        return accumulator
      }
      
      // 提取当前页的课程性质
      response.results.forEach(course => {
        if (course.course_nature) {
          natureMap[course.course_nature] = true
        }
      })
      
      // 记录获取进度
      console.log(`已获取课程性质数据: 第${page}页, 累计${Object.keys(natureMap).length}种性质`)
      
      // 如果还有下一页，继续获取
      if (response.next) {
        return fetchAllPages(page + 1, accumulator.concat(response.results))
      } else {
        return accumulator.concat(response.results)
      }
    } catch (error) {
      console.error('获取课程性质页面出错:', error)
      return accumulator
    }
  }
  
  // 开始获取所有页面数据
  return fetchAllPages().then(allResults => {
    console.log(`课程性质提取完成，共获取${allResults.length}条课程数据，提取出${Object.keys(natureMap).length}种性质`)
    
    // 如果没有提取到数据，确保基本性质存在
    if (Object.keys(natureMap).length === 0) {
      natureMap['必修课'] = true
      natureMap['选修课'] = true
      natureMap['专业选修课'] = true
      natureMap['专业必修课'] = true
      natureMap['实习实训'] = true
    }
    
    // 将课程性质转换为需要的对象格式
    const result = Object.keys(natureMap).map(nature => ({
      id: nature,
      name: nature
    }))
    
    console.log('最终课程性质列表:', result)
    
    // 更新缓存
    courseNaturesCache = result
    courseNaturesCacheTime = Date.now()
    
    return result
  })
}

/**
 * 清除课程属性缓存
 */
export function clearCourseAttributesCache() {
  courseAttributesCache = null
  courseAttributesCacheTime = null
  console.log('课程属性缓存已清除')
}

/**
 * 获取课程属性列表（用于下拉选择）
 * @returns {Promise}
 */
export function getCourseAttributes() {
  // 检查缓存是否有效
  const now = Date.now()
  if (courseAttributesCache && courseAttributesCacheTime && (now - courseAttributesCacheTime < CACHE_EXPIRY)) {
    console.log('使用课程属性缓存, 共计', courseAttributesCache.length, '种属性')
    return Promise.resolve(courseAttributesCache)
  }
  
  // 创建一个映射对象存储所有属性
  const attributeMap = {}
  // 创建一个递归函数获取所有页的数据
  const fetchAllPages = async (page = 1, accumulator = []) => {
    try {
      const response = await getCourses({ page, limit: 100 })
      
      if (!response || !response.results || response.results.length === 0) {
        return accumulator
      }
      
      // 提取当前页的课程属性
      response.results.forEach(course => {
        if (course.course_attribute) {
          attributeMap[course.course_attribute] = true
        }
      })
      
      // 如果还有下一页，继续获取
      if (response.next) {
        return fetchAllPages(page + 1, accumulator.concat(response.results))
      } else {
        return accumulator.concat(response.results)
      }
    } catch (error) {
      console.error('获取课程属性页面出错:', error)
      return accumulator
    }
  }
  
  // 开始获取所有页面数据
  return fetchAllPages().then(() => {
    // 将课程属性转换为需要的对象格式
    const result = Object.keys(attributeMap).map(attribute => ({
      id: attribute,
      name: attribute
    }))
    
    // 更新缓存
    courseAttributesCache = result
    courseAttributesCacheTime = Date.now()
    
    return result
  })
}

/**
 * 清除课程类别缓存
 */
export function clearCourseCategoriesCache() {
  courseCategoriesCache = null
  courseCategoriesCacheTime = null
  console.log('课程类别缓存已清除')
}

/**
 * 获取课程类别列表（用于下拉选择）
 * @returns {Promise}
 */
export function getCourseCategories() {
  // 检查缓存是否有效
  const now = Date.now()
  if (courseCategoriesCache && courseCategoriesCacheTime && (now - courseCategoriesCacheTime < CACHE_EXPIRY)) {
    console.log('使用课程类别缓存, 共计', courseCategoriesCache.length, '种类别')
    return Promise.resolve(courseCategoriesCache)
  }
  
  // 创建一个映射对象存储所有类别
  const categoryMap = {}
  // 创建一个递归函数获取所有页的数据
  const fetchAllPages = async (page = 1, accumulator = []) => {
    try {
      const response = await getCourses({ page, limit: 100 })
      
      if (!response || !response.results || response.results.length === 0) {
        return accumulator
      }
      
      // 提取当前页的课程类别
      response.results.forEach(course => {
        if (course.course_category) {
          categoryMap[course.course_category] = true
        }
      })
      
      // 如果还有下一页，继续获取
      if (response.next) {
        return fetchAllPages(page + 1, accumulator.concat(response.results))
      } else {
        return accumulator.concat(response.results)
      }
    } catch (error) {
      console.error('获取课程类别页面出错:', error)
      return accumulator
    }
  }
  
  // 开始获取所有页面数据
  return fetchAllPages().then(() => {
    // 将课程类别转换为需要的对象格式
    const result = Object.keys(categoryMap).map(category => ({
      id: category,
      name: category
    }))
    
    // 更新缓存
    courseCategoriesCache = result
    courseCategoriesCacheTime = Date.now()
    
    return result
  })
} 