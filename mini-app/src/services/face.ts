import { request } from './request'
import type { ApiResponse } from './types'

export interface FaceRegisterPayload {
  faceImage: string // base64 image data
}

export interface FaceRegisterResult {
  registered: boolean
  message: string
  faceCount?: number
}

export interface FaceVerifyPayload {
  faceImage: string // base64 image data
}

export interface FaceVerifyResult {
  matched: boolean
  similarity?: number // 0-1, higher = more similar
  distance?: number
  message: string
}

interface BackendFaceResult {
  registered?: boolean
  matched?: boolean
  similarity?: number
  distance?: number
  message?: string
  face_count?: number
}

function unwrapData<T>(response: ApiResponse<T> | T): T {
  if (typeof response === 'object' && response !== null && 'data' in response) {
    return (response as ApiResponse<T>).data
  }
  return response as T
}

/** 录入人脸：上传照片到后端，提取特征并存储 */
export function registerFace(payload: FaceRegisterPayload): Promise<FaceRegisterResult> {
  return request<ApiResponse<BackendFaceResult>>({
    url: '/face/register',
    method: 'POST',
    data: { face_image: payload.faceImage },
  }).then((response) => {
    const data = unwrapData(response)
    return {
      registered: Boolean(data.registered ?? data.message?.includes('成功')),
      message: data.message ?? '人脸录入完成',
      faceCount: data.face_count,
    }
  })
}

/** 验证人脸：上传照片，与已注册的人脸特征比对 */
export function verifyFace(payload: FaceVerifyPayload): Promise<FaceVerifyResult> {
  return request<ApiResponse<BackendFaceResult>>({
    url: '/face/verify',
    method: 'POST',
    data: { face_image: payload.faceImage },
  }).then((response) => {
    const data = unwrapData(response)
    return {
      matched: Boolean(data.matched),
      similarity: data.similarity,
      distance: data.distance,
      message: data.message ?? (data.matched ? '人脸验证通过' : '人脸验证失败'),
    }
  })
}
