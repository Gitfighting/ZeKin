import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import { defineComponent, h, type PropType } from 'vue'

import TaskMonitorView from './TaskMonitorView.vue'

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

    expect(wrapper.text()).toContain('张明')
    expect(wrapper.text()).toContain('刘倩')

    const teacherInput = wrapper.find('input[placeholder="教师"]')
    await teacherInput.setValue('张明')

    expect(wrapper.text()).toContain('张明')
    expect(wrapper.text()).not.toContain('刘倩')
  })
})
