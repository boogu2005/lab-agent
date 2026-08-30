import request from '@/utils/request'

/** 获取当前用户信息 */
export function getUserInfoApi() {
  return request({
    url: '/api/user/info',
    method: 'get'
  })
}

/** 修改个人信息 */
export function updateUserInfoApi(data) {
  return request({
    url: '/api/user/update',
    method: 'put',
    data
  })
}

/** 修改密码 */
export function updatePasswordApi(data) {
  return request({
    url: '/api/user/password',
    method: 'put',
    data
  })
}
