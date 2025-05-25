import request from '@/utils/request'

// 用户登录
export function login(data) {
  return request({
    url: '/users/login/',
    method: 'post',
    data
  })
}

// 用户登出
export function logout() {
  return request({
    url: '/users/logout/',
    method: 'post'
  })
}

// 获取用户信息
export function getInfo(token) {
  return request({
    url: '/users/profile/',
    method: 'get',
    params: { token }
  })
}

// 获取用户列表
export function getUsers(params) {
  return request({
    url: '/users/users/',
    method: 'get',
    params
  })
}

// 获取角色列表
export function getRoles() {
  return request({
    url: '/users/roles/',
    method: 'get'
  })
}

// 创建用户
export function createUser(data) {
  return request({
    url: '/users/users/',
    method: 'post',
    data
  })
}

// 更新用户
export function updateUser(id, data) {
  return request({
    url: `/users/users/${id}/`,
    method: 'put',
    data
  })
}

// 删除用户
export function deleteUser(id) {
  return request({
    url: `/users/users/${id}/`,
    method: 'delete'
  })
} 
