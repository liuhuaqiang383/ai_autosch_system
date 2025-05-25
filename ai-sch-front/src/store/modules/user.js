import { login, logout, getInfo } from '@/api/user'
import { getToken, setToken, removeToken } from '@/utils/auth'
import { resetRouter } from '@/router'

const state = {
  token: getToken(),
  name: '',
  avatar: '',
  roles: []
}

const mutations = {
  SET_TOKEN: (state, token) => {
    state.token = token
  },
  SET_NAME: (state, name) => {
    state.name = name
  },
  SET_AVATAR: (state, avatar) => {
    state.avatar = avatar
  },
  SET_ROLES: (state, roles) => {
    state.roles = roles
  }
}

const actions = {
  // 用户登录
  login({ commit }, userInfo) {
    const { username, password } = userInfo
    return new Promise((resolve, reject) => {
      login({ username: username.trim(), password: password }).then(response => {
        // 适配后端返回的数据结构
        const token = response.token || 'admin-token'
        commit('SET_TOKEN', token)
        setToken(token)
        resolve()
      }).catch(error => {
        reject(error)
      })
    })
  },

  // 获取用户信息
  getInfo({ commit, state }) {
    return new Promise((resolve, reject) => {
      getInfo(state.token).then(response => {
        // 如果后端没有返回用户信息，使用默认值
        if (!response || !response.data) {
          // 使用默认值
          const defaultUserInfo = {
            roles: ['admin'],
            name: 'Admin',
            avatar: ''
          }
          
          commit('SET_ROLES', defaultUserInfo.roles)
          commit('SET_NAME', defaultUserInfo.name)
          commit('SET_AVATAR', defaultUserInfo.avatar)
          resolve(defaultUserInfo)
          return
        }
        
        // 使用后端返回的数据
        const { roles, name, avatar } = response.data

        // 角色必须是非空数组
        if (!roles || roles.length <= 0) {
          commit('SET_ROLES', ['admin']) // 默认设置为admin角色
        } else {
          commit('SET_ROLES', roles)
        }
        
        commit('SET_NAME', name || 'Admin')
        commit('SET_AVATAR', avatar || '')
        resolve(response.data)
      }).catch(error => {
        reject(error)
      })
    })
  },

  // 用户登出
  logout({ commit, state }) {
    return new Promise((resolve, reject) => {
      logout(state.token).then(() => {
        commit('SET_TOKEN', '')
        commit('SET_ROLES', [])
        removeToken()
        resetRouter()
        resolve()
      }).catch(error => {
        console.error('登出请求失败，但仍会清除本地状态:', error)
        // 即使API请求失败，也要清除本地状态
        commit('SET_TOKEN', '')
        commit('SET_ROLES', [])
        removeToken()
        resetRouter()
        resolve() // 这里仍然resolve，不影响用户体验
      })
    })
  },

  // 重置token
  resetToken({ commit }) {
    return new Promise(resolve => {
      commit('SET_TOKEN', '')
      commit('SET_ROLES', [])
      removeToken()
      resolve()
    })
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
} 