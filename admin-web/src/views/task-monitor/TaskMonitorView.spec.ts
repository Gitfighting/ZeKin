import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
import { defineComponent, h, nextTick, type PropType } from 'vue'

import TaskMonitorView from './TaskMonitorView.vue'
import { getTasks } from '../../api/admin'

vi.mock('../../api/admin', () => ({
  getTasks: vi.fn(),
}))

interface RenderedTaskRow {
  teacher: string
  type: string
  status: string
  date: string
}

const DataTableStub = defineComponent({
  props: {
    rows: {
      type: Array as PropType<RenderedTaskRow[]>,
      required: true,
    },
  },
  template: `
    <div>
      <div v-for="row in rows" :key="row.teacher">
        {{ row.teacher }} {{ row.type }} {{ row.status }} {{ row.date }}
      </div>
    </div>
  `,
})

const InputStub = defineComponent({
  props: {
    modelValue: {
      type: String,
      default: '',
    },
    placeholder: {
      type: String,
      default: '',
    },
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    return () =>
      h('input', {
        placeholder: props.placeholder,
        value: props.modelValue,
        onInput: (event: Event) => emit('update:modelValue', (event.target as HTMLInputElement).value),
      })
  },
})

describe('TaskMonitorView', () => {
  it('filters task rows by teacher keyword', async () => {
    vi.mocked(getTasks).mockResolvedValue({
      total: 2,
      items: [
        {
          id: 1,
          title: '晨读签到',
          teacher: '张明',
          type: '晨读签到',
          status: '进行中',
          date: '2026-06-24',
          completionRate: '93%',
          groupNames: ['软工 1 班'],
        },
        {
          id: 2,
          title: '晚自习签到',
          teacher: '刘倩',
          type: '晚自习签到',
          status: '已结束',
          date: '2026-06-24',
          completionRate: '88%',
          groupNames: ['思政 1 班'],
        },
      ],
    })

    const wrapper = mount(TaskMonitorView, {
      global: {
        stubs: {
          ElCard: {
            template: '<section><slot /></section>',
          },
          ElDatePicker: true,
          ElInput: InputStub,
          ElOption: true,
          ElProgress: true,
          ElSelect: {
            template: '<select><slot /></select>',
          },
          DataTable: DataTableStub,
        },
      },
    })
    await vi.waitFor(() => expect(getTasks).toHaveBeenCalled())
    await nextTick()

    expect(wrapper.text()).toContain('张明')
    expect(wrapper.text()).toContain('刘倩')

    const teacherInput = wrapper.find('input[placeholder="教师"]')
    await teacherInput.setValue('张明')

    expect(wrapper.text()).toContain('张明')
    expect(wrapper.text()).not.toContain('刘倩')
  })
})
