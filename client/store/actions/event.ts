import * as store from '../store'
import type * as types from '@client/types'
import delay from 'delay'

export async function emitFileEvent(event: types.IFileEvent) {
  store.setState(`${event.type}-file-event-start`, (state) => {
    state.event = event
  })

  await delay(500)

  store.setState(`${event.type}-file-event-end`, (state) => {
    state.event = undefined
  })
}
