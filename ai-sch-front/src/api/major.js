import request from '@/utils/request'

// 获取专业列表
export function getMajors(params) {
  // 添加默认筛选
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
  if (apiParams.limit) {
    apiParams.page_size = apiParams.limit;
    delete apiParams.limit;
  }
  
  // 修改major_name为搜索参数
  if (apiParams.major_name) {
    apiParams.search = apiParams.major_name;
    delete apiParams.major_name;
  }
  
  console.log('API请求参数:', apiParams); // 调试用
  
  return request({
    url: '/basic_data/majors/',
    method: 'get',
    params: apiParams
  }).then(response => {
    console.log('API原始响应完整结构:', JSON.stringify(response, null, 2)); // 调试用，显示完整响应结构
    return response;
  })
}

// 创建专业
export function createMajor(data) {
  return request({
    url: '/basic_data/majors/',
    method: 'post',
    data
  })
}

// 更新专业
export function updateMajor(data) {
  return request({
    url: `/basic_data/majors/${data.id}/`,
    method: 'put',
    data
  })
}

// 删除专业
export function deleteMajor(id) {
  return request({
    url: `/basic_data/majors/${id}/`,
    method: 'delete'
  })
} 