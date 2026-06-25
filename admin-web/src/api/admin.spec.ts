import { beforeEach, describe, expect, it, vi } from 'vitest'

import { getDashboard, getGroups, getStudents, getTasks, getTeachers } from './admin'
import { http } from './http'

vi.mock('./http', () => ({
  http: {
    get: vi.fn(),
    post: vi.fn(),
  },
}))

describe('admin api mapping', () => {
  beforeEach(() => {
    vi.mocked(http.get).mockReset()
  })

  it('unwraps backend ApiResponse data for dashboard counts', async () => {
    vi.mocked(http.get).mockResolvedValue({
      data: {
        data: {
          student_count: 5,
          task_count: 4,
          exception_count: 1,
          pending_appeal_count: 1,
          completion_rate: 25,
        },
        message: 'ok',
      },
    })

    await expect(getDashboard()).resolves.toEqual({
      studentCount: 5,
      taskCount: 4,
      exceptionCount: 1,
      pendingAppealCount: 1,
      completionRate: 25,
    })
  })

  it('maps list endpoints to camelCase rows', async () => {
    vi.mocked(http.get)
      .mockResolvedValueOnce({
        data: {
          data: {
            items: [
              {
                id: 1,
                student_no: '20260001',
                name: '张三',
                class_name: '软件2601',
                activated: true,
              },
            ],
            total: 1,
          },
        },
      })
      .mockResolvedValueOnce({
        data: {
          data: {
            items: [{ id: 1, name: '软件2601', group_type: 'class', student_count: 3, teacher_count: 2 }],
            total: 1,
          },
        },
      })
      .mockResolvedValueOnce({
        data: {
          data: {
            items: [{ id: 4, title: '晚间查寝', status: 'not_started', teacher_name: '李老师', group_names: ['软件2601'] }],
            total: 1,
          },
        },
      })

    await expect(getStudents()).resolves.toMatchObject({
      items: [{ studentNo: '20260001', className: '软件2601', status: '已启用' }],
    })
    await expect(getGroups()).resolves.toMatchObject({
      items: [{ name: '软件2601', studentCount: 3, teacherCount: 2 }],
    })
    await expect(getTasks()).resolves.toMatchObject({
      items: [{ title: '晚间查寝', teacher: '李老师', groupNames: ['软件2601'] }],
    })
  })

  it('maps teacher login accounts for admin teacher management', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: {
        data: {
          items: [
            {
              id: 1,
              account: 'teacher',
              teacher_no: 'T2026001',
              name: '李老师',
              phone: '13800000002',
              department: '软件学院',
              groups: ['软件2601'],
            },
          ],
          total: 1,
        },
      },
    })

    await expect(getTeachers()).resolves.toMatchObject({
      items: [
        {
          account: 'teacher',
          teacherNo: 'T2026001',
          name: '李老师',
          groups: ['软件2601'],
        },
      ],
    })
  })
})
