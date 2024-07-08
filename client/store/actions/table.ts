import { client } from '@client/client'
import { mapValues, isNull } from 'lodash'
import { openDialog } from './dialog'
import { cloneDeep } from 'lodash'
import { getIsResourceUpdated } from './resource'
import { emitFileCreateEvent, emitFileUpdateEvent } from './event'
import { revertResource } from './resource'
import * as helpers from '@client/helpers'
import * as settings from '@client/settings'
import * as types from '@client/types'
import * as store from '../store'

export const getIsTableOrResourceUpdated = store.createSelector((state) => {
  return getIsTableUpdated(state) || getIsResourceUpdated(state)
})

export const getIsTableUpdated = store.createSelector((state) => {
  return !!state.table?.history.changes.length
})

export const tableLoader: types.ITableLoader = async ({ skip, limit, sortInfo }) => {
  const defaultResult = { data: [], count: 0 }
  const { path, table } = store.getState()
  if (!path || !table) return defaultResult

  const result = await client.tableRead({
    path,
    valid: table.mode === 'errors' ? false : undefined,
    limit,
    offset: skip,
    order: sortInfo?.name,
    desc: sortInfo?.dir === -1,
  })

  if (result instanceof client.Error) {
    store.setState('table-loader-error', (state) => {
      state.error = result
    })
    return defaultResult
  }

  // convert null fields in db to empty strings to avoid errors
  // in table representation. InovuaDataGrid complains with null values
  const rowsNotNull = []
  for (const row of result.rows) {
    rowsNotNull.push(mapValues(row, (value) => (isNull(value) ? '' : value)))
  }

  helpers.applyTableHistory(table.history, rowsNotNull)
  return { data: rowsNotNull, count: table.rowCount || 0 }
}

export async function openTable() {
  const { path, record } = store.getState()
  if (!path || !record) return

  // Row Count
  const result = await client.tableCount({ path })
  if (result instanceof client.Error) {
    return store.setState('open-table-error', (state) => {
      state.error = result
    })
  }

  // Text Source
  let source: string | undefined
  if (settings.TEXT_TABLE_FORMATS.includes(record.resource.format || '')) {
    const result = await client.textRead({ path, size: settings.MAX_TABLE_SOURCE_SIZE })
    if (result instanceof client.Error) {
      return store.setState('open-table-error', (state) => {
        state.error = result
      })
    }
    source = result.text
  }

  store.setState('open-table-init', (state) => {
    state.table = {
      rowCount: result.count,
      history: cloneDeep(settings.INITIAL_HISTORY),
      undoneHistory: cloneDeep(settings.INITIAL_HISTORY),
      source,
    }
  })
}

export async function toggleTableErrorMode() {
  const { path, table } = store.getState()
  const grid = table?.gridRef?.current
  if (!path || !table || !grid) return

  // Update mode/rowCount
  if (table.mode === 'errors') {
    const result = await client.tableCount({ path })

    if (result instanceof client.Error) {
      return store.setState('toggle-table-error-mode', (state) => {
        state.error = result
      })
    }

    store.setState('toggle-table-error-mode-disable', (state) => {
      state.table!.mode = undefined
      state.table!.rowCount = result.count
    })
  } else {
    const result = await client.tableCount({ path, valid: false })

    if (result instanceof client.Error) {
      return store.setState('toggle-table-error-mode', (state) => {
        state.error = result
      })
    }

    store.setState('toggle-table-error-mode-enable', (state) => {
      state.table!.mode = 'errors'
      state.table!.rowCount = result.count
    })
  }

  if (grid.setSkip) grid.setSkip(0)
  grid.reload()
}

export async function editTable(prompt: string) {
  const { path, table } = store.getState()
  if (!path || !table) return

  const grid = table.gridRef?.current
  if (!grid) return

  const text = table.source || ''
  const result = await client.tableEdit({ path, text, prompt })
  if (result instanceof client.Error) {
    return store.setState('edit-table-error', (state) => {
      state.error = result
    })
  }

  await emitFileUpdateEvent(path)
  grid.reload()
}

export async function forkTable(toPath: string) {
  const { path, table, resource } = store.getState()
  if (!path || !table) return

  const result = await client.tablePatch({
    path,
    toPath,
    history: table.history,
    resource,
  })

  if (result instanceof client.Error) {
    return store.setState('fork-table-error', (state) => {
      state.error = result
    })
  }

  await emitFileCreateEvent([toPath])
}

export async function publishTable(control: types.IControl) {
  const { record } = store.getState()

  const result = await client.filePublish({ path: record!.path, control })

  if (result instanceof client.Error) {
    return store.setState('publish-table-error', (state) => {
      state.error = result
    })
  }

  store.setState('publish-table-end', (state) => {
    state.table!.publishedUrl = result.url
  })
}

export async function revertTable() {
  const state = store.getState()

  if (getIsTableUpdated(state)) {
    store.setState('revert-table', (state) => {
      state.table!.history = cloneDeep(settings.INITIAL_HISTORY)
      state.table!.undoneHistory = cloneDeep(settings.INITIAL_HISTORY)
    })

    state.table?.gridRef?.current?.reload()
  }

  revertResource()
}

export async function saveTable() {
  const { path, resource, table } = store.getState()
  const grid = table?.gridRef?.current
  if (!path || !grid) return

  const isTableUpdated = getIsTableUpdated(store.getState())
  const isResourceUpdated = getIsResourceUpdated(store.getState())

  const result = await client.tablePatch({
    path,
    history: isTableUpdated ? table.history : undefined,
    resource: isResourceUpdated ? resource : undefined,
  })

  if (result instanceof client.Error) {
    return store.setState('save-table-error', (state) => {
      state.error = result
    })
  }

  await emitFileUpdateEvent(path)
  grid.reload()
}

export function catchTableClickAway() {
  const { dialog } = store.getState()
  const isUpdated = getIsTableOrResourceUpdated(store.getState())

  if (isUpdated && !dialog) {
    openDialog('leave')
  }
}

export function startTableEditing(context: any) {
  store.setState('start-table-editing', (state) => {
    state.table!.initialEditingValue = context.value
  })
}

export function saveTableEditing(context: any) {
  const { table } = store.getState()
  const grid = table?.gridRef?.current
  if (!table || !grid) return

  // Don't save if not changed
  let value = context.value
  if (value === table.initialEditingValue) return

  const rowNumber = context.rowId
  const fieldName = context.columnId
  if (context.cellProps.type === 'number') value = parseInt(value)
  const change: types.IChange = {
    type: 'cell-update',
    rowNumber,
    fieldName,
    value,
  }

  store.setState('save-table-editing', (state) => {
    helpers.applyTableHistory({ changes: [change] }, grid.data)
    state.table!.history.changes.push(change)
    state.table!.undoneHistory.changes = []
  })

  grid.reload()
}

export function undoChange() {
  const { table } = store.getState()
  if (!table) return

  store.setState('undo-change', (state) => {
    const change = state.table!.history.changes.pop()
    if (change) state.table!.undoneHistory.changes.push(change)
  })

  table.gridRef?.current?.reload()
}

export function redoChange() {
  const { table } = store.getState()
  if (!table) return

  store.setState('redo-change', (state) => {
    const change = state.table!.undoneHistory.changes.pop()
    if (change) state.table!.history.changes.push(change)
  })

  table.gridRef?.current?.reload()
}

export async function deleteMultipleCells(cells: object) {
  const { table } = store.getState()
  const grid = table?.gridRef?.current
  if (!table || !grid) return

  const cellChanges = []

  for (const [key] of Object.entries(cells)) {
    const row = key.substring(0, key.indexOf(','))
    const rowNumber = parseInt(row)
    const column = key.substring(key.indexOf(',') + 1, key.length)

    cellChanges.push({ rowNumber, fieldName: column, value: '' })
  }

  const change: types.IChange = {
    type: 'multiple-cells-update',
    cells: cellChanges,
  }

  store.setState('delete-multiple-cells', (state) => {
    helpers.applyTableHistory({ changes: [change] }, grid.data)
    state.table!.history.changes.push(change)
    state.table!.undoneHistory.changes = []
  })
}
