// @vitest-environment jsdom
import { beforeEach, describe, expect, it, vi } from 'vitest'

import {
  createTeacherTask,
  getTeacherGroups,
  getTeacherTaskDetail,
  getTeacherTasks,
  reviewTeacherException,
} from './teacher'

function mockApiResponse(data: unknown) {
  vi.mocked(uni.request).mockImplementation((options) => {
    options.success?.({
      statusCode: 200,
      data: {
        data,
        message: 'ok',
      },
    } as UniApp.RequestSuccessCallbackResult)
    return {} as UniApp.RequestTask
  })
}

function lastRequest() {
  return vi.mocked(uni.request).mock.calls.at(-1)?.[0]
}

describe('teacher service', () => {
  beforeEach(() => {
    vi.stubGlobal('uni', {
      getStorageSync: vi.fn(() => 'test-token'),
      request: vi.fn(),
    })
  })

  it('maps backend group and task item wrappers into teacher page models', async () => {
    mockApiResponse({
      items: [
        {
          id: 1,
          name: 'Class A',
          group_type: 'class',
        },
      ],
      total: 1,
    })

    const groups = await getTeacherGroups()

    expect(groups).toEqual([
      {
        id: 1,
        name: 'Class A',
        studentCount: 0,
        recentTaskCount: 0,
        courseName: 'class',
      },
    ])

    mockApiResponse({
      items: [
        {
          id: 8,
          title: 'Evening check',
          type_id: 1,
          status: 'not_started',
          starts_at: '2026-06-24T21:30:00+08:00',
          ends_at: '2026-06-24T22:30:00+08:00',
          group_ids: [1, 2],
          rules_snapshot: {
            templateName: '晚点名模板',
          },
        },
      ],
      total: 1,
    })

    const tasks = await getTeacherTasks()

    expect(tasks).toEqual([
      expect.objectContaining({
        id: 8,
        title: 'Evening check',
        status: 'not_started',
        templateName: '晚点名模板',
        startsAt: '2026-06-24 21:30',
        endsAt: '2026-06-24 22:30',
        completionRate: 0,
        pendingReviewCount: 0,
        exceptionCount: 0,
      }),
    ])
  })

  it('creates teacher tasks with the backend snake_case payload shape', async () => {
    mockApiResponse({
      id: 8,
      title: 'Evening check',
      type_id: 1,
      status: 'draft',
      starts_at: '2026-06-24T21:30:00+08:00',
      ends_at: '2026-06-24T22:30:00+08:00',
      group_ids: [1],
      rules_snapshot: {},
    })

    const task = await createTeacherTask({
      title: 'Evening check',
      description: 'Check dorm location',
      groupIds: [1],
      taskType: 'attendance',
      templateName: '晚点名模板',
      startsAt: '2026-06-24T21:30:00+08:00',
      endsAt: '2026-06-24T22:30:00+08:00',
      advancedRules: {
        allowLateMinutes: 10,
        needPhoto: true,
        allowAppeal: true,
        autoEnd: true,
      },
    })

    expect(lastRequest()).toEqual(
      expect.objectContaining({
        url: 'http://192.168.165.19:8000/api/teacher/tasks',
        method: 'POST',
        data: expect.objectContaining({
          title: 'Evening check',
          type_id: 1,
          group_ids: [1],
          starts_at: '2026-06-24T21:30:00+08:00',
          ends_at: '2026-06-24T22:30:00+08:00',
          rules_snapshot: expect.objectContaining({
            templateName: '晚点名模板',
            timeRule: expect.objectContaining({
              startTime: '21:30',
              endTime: '22:30',
              allowLate: true,
            }),
            submitRule: expect.objectContaining({
              fields: expect.any(Array),
            }),
          }),
        }),
      }),
    )
    expect(lastRequest()?.data).not.toHaveProperty('groupIds')
    expect(lastRequest()?.data).not.toHaveProperty('startsAt')
    expect(task).toMatchObject({
      id: 8,
      title: 'Evening check',
      status: 'draft',
    })
  })

  it('maps task detail students and exceptions from the backend detail wrapper', async () => {
    mockApiResponse({
      id: 8,
      task: {
        id: 8,
        title: 'Evening check',
        status: 'in_progress',
        starts_at: '2026-06-24T21:30:00+08:00',
        ends_at: '2026-06-24T22:30:00+08:00',
        group_names: ['Class A'],
        completionRate: 67,
        pendingReviewCount: 1,
        exceptionCount: 1,
        rules_snapshot: {
          templateName: '晚点名模板',
        },
        published: true,
      },
      students: [
        {
          id: 1,
          name: 'Student A',
          status: 'submitted',
          submitted_at: '2026-06-24T21:45:00+08:00',
        },
        {
          id: 2,
          name: 'Student B',
          status: 'pending_review',
          submitted_at: '2026-06-24T21:50:00+08:00',
        },
      ],
      exceptions: [
        {
          id: 4,
          studentName: 'Student B',
          taskTitle: 'Evening check',
          groupName: 'Class A',
          submittedAt: '2026-06-24T21:50:00+08:00',
          reason: '当前位置不在有效范围内',
          status: 'pending',
        },
      ],
    })

    const detail = await getTeacherTaskDetail(8)

    expect(lastRequest()).toEqual(
      expect.objectContaining({
        url: 'http://192.168.165.19:8000/api/teacher/tasks/8',
        method: 'GET',
      }),
    )
    expect(detail.task).toMatchObject({
      id: 8,
      title: 'Evening check',
      groupName: 'Class A',
      completionRate: 67,
      pendingReviewCount: 1,
      exceptionCount: 1,
      published: true,
    })
    expect(detail.students).toEqual([
      expect.objectContaining({
        id: 1,
        name: 'Student A',
        status: 'submitted',
        submittedAt: '2026-06-24 21:45',
      }),
      expect.objectContaining({
        id: 2,
        name: 'Student B',
        status: 'pending_review',
      }),
    ])
    expect(detail.exceptions).toEqual([
      expect.objectContaining({
        id: 4,
        studentName: 'Student B',
        taskTitle: 'Evening check',
        groupName: 'Class A',
        reason: '当前位置不在有效范围内',
        status: 'pending',
      }),
    ])
  })

  it('reviews teacher exceptions with decision and comment payload', async () => {
    mockApiResponse({
      reviewed: true,
      record_status: 'normal',
    })

    await reviewTeacherException(11, {
      decision: 'approve',
      comment: 'Looks good',
    })

    expect(lastRequest()).toEqual(
      expect.objectContaining({
        url: 'http://192.168.165.19:8000/api/teacher/exceptions/11/review',
        method: 'POST',
        data: {
          decision: 'approve',
          comment: 'Looks good',
        },
      }),
    )
  })
})
