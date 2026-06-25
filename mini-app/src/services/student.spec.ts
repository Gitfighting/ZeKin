// @vitest-environment jsdom
import { beforeEach, describe, expect, it, vi } from 'vitest'

import {
  getStudentMessages,
  getStudentRecords,
  getStudentTasks,
  submitAppeal,
  submitCheckin,
} from './student'

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

describe('student service', () => {
  beforeEach(() => {
    vi.stubGlobal('uni', {
      getStorageSync: vi.fn(() => 'test-token'),
      request: vi.fn(),
    })
  })

  it('maps backend task list items into student page tasks', async () => {
    mockApiResponse({
      items: [
        {
          id: 42,
          title: 'Evening check',
          status: 'in_progress',
          starts_at: '2026-06-24T21:30:00+08:00',
          ends_at: '2026-06-24T22:30:00+08:00',
          rules_snapshot: {
            locationRule: {
              placeName: 'Dorm 3',
              radius: 300,
            },
            submitRule: {
              fields: [
                {
                  key: 'remark',
                  label: 'Remark',
                  type: 'textarea',
                  required: true,
                  placeholder: 'Describe current state',
                  maxLength: 80,
                },
              ],
            },
            faceRule: {
              enabled: true,
              provider: 'placeholder',
            },
          },
        },
      ],
      total: 1,
    })

    const tasks = await getStudentTasks()

    expect(lastRequest()).toEqual(
      expect.objectContaining({
        url: 'http://localhost:8000/api/student/tasks',
        method: 'GET',
      }),
    )
    expect(tasks).toHaveLength(1)
    expect(tasks[0]).toMatchObject({
      id: '42',
      title: 'Evening check',
      status: 'in-progress',
      locationName: 'Dorm 3',
      faceRule: {
        enabled: true,
      },
      dynamicFields: [
        {
          key: 'remark',
          label: 'Remark',
          type: 'textarea',
          placeholder: 'Describe current state',
          required: true,
          maxLength: 80,
        },
      ],
    })
    expect(tasks[0].timeWindow).toContain('21:30')
    expect(tasks[0].requirements).toContain('Remark')
  })

  it('submits checkins to the task-scoped backend endpoint with snake_case payload', async () => {
    mockApiResponse({
      record_id: 7,
      status: 'exception',
      exception_types: ['location'],
      need_review: true,
    })

    const result = await submitCheckin({
      taskId: '42',
      longitude: 120.01,
      latitude: 30.02,
      verificationCode: 'A123',
      formData: {
        remark: 'arrived',
      },
      photoUrls: ['photo-a'],
    })

    expect(lastRequest()).toEqual(
      expect.objectContaining({
        url: 'http://localhost:8000/api/student/tasks/42/checkin',
        method: 'POST',
        data: {
          longitude: 120.01,
          latitude: 30.02,
          dynamic_code: 'A123',
          submit_payload: {
            remark: 'arrived',
            photo_urls: ['photo-a'],
          },
        },
      }),
    )
    expect(result).toMatchObject({
      id: '7',
      taskId: '42',
      state: 'pending_review',
    })
  })

  it('submits appeals to the record-scoped backend endpoint with attachment ids', async () => {
    mockApiResponse({
      appeal_id: 9,
      status: 'appeal_pending',
    })

    const result = await submitAppeal({
      recordId: '7',
      reason: 'Location drifted',
      images: ['12', 'local-temp-file'],
    })

    expect(lastRequest()).toEqual(
      expect.objectContaining({
        url: 'http://localhost:8000/api/student/records/7/appeal',
        method: 'POST',
        data: {
          reason: 'Location drifted',
          attachment_ids: [12],
        },
      }),
    )
    expect(result).toEqual({
      success: true,
    })
  })

  it('maps backend record and message lists from items wrappers', async () => {
    mockApiResponse({
      items: [
        {
          id: 7,
          task_id: 42,
          status: 'appeal_pending',
          submitted_at: '2026-06-24T22:45:00+08:00',
          need_review: true,
        },
      ],
      total: 1,
    })

    const records = await getStudentRecords()

    expect(records).toEqual([
      expect.objectContaining({
        id: '7',
        status: 'pending_review',
        submittedAt: '2026-06-24 22:45',
      }),
    ])

    mockApiResponse({
      items: [
        {
          id: 3,
          title: 'Appeal accepted',
          content: 'Your appeal is being reviewed',
          read_status: true,
          created_at: '2026-06-24T22:50:00+08:00',
        },
      ],
      total: 1,
    })

    const messages = await getStudentMessages()

    expect(messages).toEqual([
      {
        id: '3',
        type: 'reminder',
        title: 'Appeal accepted',
        content: 'Your appeal is being reviewed',
        time: '2026-06-24 22:50',
        read: true,
      },
    ])
  })
})
