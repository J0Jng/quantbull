/**
 * 视频中心服务
 */
import http from './http'

export async function getVideos() {
  return http.get('/videos')
}

export async function uploadVideo(formData) {
  return http.post('/videos', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export async function deleteVideo(id) {
  return http.delete(`/videos/${id}`)
}

export default {
  getVideos,
  uploadVideo,
  deleteVideo
}
