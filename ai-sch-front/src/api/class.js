import request from '@/utils/request'

// 获取班级列表
export function getClasses(params) {
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
  
  // 修改class_name为搜索参数
  if (apiParams.class_name) {
    apiParams.search = apiParams.class_name;
    delete apiParams.class_name;
  }
  
  console.log('班级API请求参数:', apiParams); // 调试用
  
  return request({
    url: '/basic_data/classes/',
    method: 'get',
    params: apiParams
  }).then(response => {
    console.log('班级API原始响应完整结构:', JSON.stringify(response, null, 2)); // 调试用，显示完整响应结构
    return response;
  })
}

// 创建班级
export function createClass(data) {
  return request({
    url: '/basic_data/classes/',
    method: 'post',
    data
  })
}

// 更新班级
export function updateClass(data) {
  return request({
    url: `/basic_data/classes/${data.id}/`,
    method: 'put',
    data
  })
}

// 删除班级
export function deleteClass(id) {
  return request({
    url: `/basic_data/classes/${id}/`,
    method: 'delete'
  })
} 