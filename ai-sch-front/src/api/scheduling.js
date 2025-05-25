import request from '@/utils/request'

// 缓存全部排课任务数据
let schedulingTasksCache = null
let schedulingTasksCacheTime = null
// 缓存过期时间（5分钟）
const CACHE_EXPIRY = 5 * 60 * 1000

// 获取排课任务列表
export function getSchedulingTasks(params) {
  // 获取所有排课任务（用于下拉选项或展示全部）
  if (params && params._fetchAll) {
    // 检查缓存是否有效
    const now = Date.now()
    if (schedulingTasksCache && schedulingTasksCacheTime && (now - schedulingTasksCacheTime < CACHE_EXPIRY)) {
      console.log('使用排课任务数据缓存, 共计', schedulingTasksCache.count, '条记录')
      return Promise.resolve(schedulingTasksCache)
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
          url: '/scheduling/tasks/',
          method: 'get',
          params: queryParams
        })
        
        if (!response || !response.results) {
          return allResults
        }
        
        // 合并结果
        allResults = allResults.concat(response.results)
        console.log(`已获取排课任务数据: 第${page}页, 累计${allResults.length}个任务`)
        
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
          if (!baseParams.is_scheduled) { // 只有获取全部数据时才缓存
            schedulingTasksCache = result
            schedulingTasksCacheTime = Date.now()
          }
          
          return result
        }
      } catch (error) {
        console.error('获取排课任务数据出错:', error)
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

  // 普通查询，使用分页参数
  return request({
    url: '/scheduling/tasks/',
    method: 'get',
    params
  })
}

// 获取单个排课任务详情
export function getSchedulingTask(id) {
  return request({
    url: `/scheduling/tasks/${id}/`,
    method: 'get'
  })
}

// 创建排课任务
export function createSchedulingTask(data) {
  return request({
    url: '/scheduling/tasks/',
    method: 'post',
    data
  })
}

// 更新排课任务
export function updateSchedulingTask(id, data) {
  return request({
    url: `/scheduling/tasks/${id}/`,
    method: 'put',
    data
  })
}

// 删除排课任务
export function deleteSchedulingTask(id) {
  return request({
    url: `/scheduling/tasks/${id}/`,
    method: 'delete'
  })
}

// 获取排课结果列表
export function getSchedulingResults(params) {
  // 获取所有排课结果（用于统计分析）
  if (params && params._fetchAll) {
    console.log('获取全部排课结果数据');
    
    // 创建一个深拷贝，移除_fetchAll标志
    const baseParams = { ...params };
    delete baseParams._fetchAll;
    
    // 创建一个数组存储所有结果
    let allResults = [];
    
    // 递归函数获取所有页面数据
    const fetchAllPages = async (page = 1) => {
      try {
        const queryParams = { 
          ...baseParams,
          page,
          limit: 100
        };
        
        const response = await request({
          url: '/scheduling/results/',
          method: 'get',
          params: queryParams
        });
        
        if (!response || !response.results) {
          return allResults;
        }
        
        // 合并结果
        allResults = allResults.concat(response.results);
        console.log(`已获取排课结果数据: 第${page}页, 累计${allResults.length}个结果`);
        
        // 如果还有下一页，继续获取
        if (response.next) {
          return fetchAllPages(page + 1);
        } else {
          // 构造类似于标准响应的结果
          return {
            count: allResults.length,
            next: null,
            previous: null,
            results: allResults
          };
        }
      } catch (error) {
        console.error('获取排课结果数据出错:', error);
        // 返回已获取的结果
        return {
          count: allResults.length,
          next: null,
          previous: null,
          results: allResults
        };
      }
    };
    
    // 开始获取所有页面
    return fetchAllPages();
  }

  // 普通查询，使用分页参数
  return request({
    url: '/scheduling/results/',
    method: 'get',
    params
  });
}

// 获取排课策略列表
export function getSchedulingStrategies(params) {
  return request({
    url: '/scheduling/strategies/',
    method: 'get',
    params
  })
}

// 创建排课策略
export function createSchedulingStrategy(data) {
  return request({
    url: '/scheduling/strategies/',
    method: 'post',
    data
  })
}

// 更新排课策略
export function updateSchedulingStrategy(id, data) {
  return request({
    url: `/scheduling/strategies/${id}/`,
    method: 'put',
    data
  })
}

// 获取排课日志
export function getSchedulingLogs(params) {
  return request({
    url: '/scheduling/logs/',
    method: 'get',
    params
  })
}

// 获取教学班组成
export function getTeachingClassCompositions(params) {
  return request({
    url: '/scheduling/compositions/',
    method: 'get',
    params
  })
}

// 创建教学班组成
export function createTeachingClassComposition(data) {
  return request({
    url: '/scheduling/compositions/',
    method: 'post',
    data
  })
}

// 运行全局自动排课（一键排课）
export function runGlobalAutoScheduling() {
  return request({
    url: '/scheduling/tasks/run-scheduling/',
    method: 'get'
  })
}

// 获取特定任务的排课结果
export function getTaskSchedulingResults(taskId) {
  return request({
    url: `/scheduling/tasks/${taskId}/results/`,
    method: 'get'
  })
}

/**
 * 批量导入排课任务
 * @param {FormData} formData - 包含Excel文件的FormData
 * @returns {Promise}
 */
export function batchImportSchedulingTasks(formData) {
  return request({
    url: '/scheduling/tasks/batch-import/',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 创建排课结果（手动排课）
export function createSchedulingResult(data) {
  return request({
    url: '/scheduling/results/',
    method: 'post',
    data
  })
}

// 更新排课结果（手动排课）
export function updateSchedulingResult(id, data) {
  return request({
    url: `/scheduling/results/${id}/`,
    method: 'put',
    data
  })
}

// 删除排课结果（手动排课）
export function deleteSchedulingResult(id) {
  return request({
    url: `/scheduling/results/${id}/`,
    method: 'delete'
  })
}

// 清除排课任务缓存
export function clearSchedulingTasksCache() {
  schedulingTasksCache = null
  schedulingTasksCacheTime = null
  console.log('排课任务缓存已清除')
}

// 获取可用教室列表
export function getAvailableClassrooms(params) {
  return request({
    url: '/scheduling/available-classrooms/',
    method: 'get',
    params
  })
}

// 检查时间段冲突
export function checkTimeConflicts(data) {
  return request({
    url: '/scheduling/check-conflicts/',
    method: 'post',
    data
  })
} 
