import * as React from 'react'
import * as zustand from 'zustand'
import noop from 'lodash/noop'
import cloneDeep from 'lodash/cloneDeep'
import { createStore } from 'zustand/vanilla'
import { createSelector } from 'reselect'
import { assert } from 'ts-essentials'
import { Client } from '../../../client'
import { IFile, IResource } from '../../../interfaces'
import { FileProps } from './File'

export interface State {
  path: string
  client: Client
  onSave: () => void
  onSaveAs: (path: string) => void
  panel?: 'metadata' | 'report' | 'source'
  dialog?: 'saveAs'
  file?: IFile
  resource?: IResource
  revision: number
  original?: ArrayBuffer
  updateState: (patch: Partial<State>) => void
  load: () => Promise<void>
  revert: () => void
  save: () => void
  saveAs: (path: string) => Promise<void>
}

export function makeStore(props: FileProps) {
  return createStore<State>((set, get) => ({
    ...props,
    onSaveAs: props.onSaveAs || noop,
    onSave: props.onSave || noop,
    revision: 0,
    updateState: (patch) => {
      const { revision } = get()
      if ('resource' in patch) patch.revision = revision + 1
      set(patch)
    },
    load: async () => {
      const { path, client } = get()
      const { file } = await client.fileIndex({ path })
      if (!file) return
      const resource = cloneDeep(file.record!.resource)
      set({ file, resource })
      if (!['jpg', 'png'].includes(file.record?.resource.format || '')) return
      const { bytes } = await client.fileRead({ path: file.path })
      set({ original: bytes })
    },
    revert: () => {
      const { file } = get()
      if (!file) return
      set({ resource: cloneDeep(file.record!.resource), revision: 0 })
    },
    save: async () => {
      const { file, client, resource, onSave, load } = get()
      if (!file || !resource) return
      await client.fileUpdate({ path: file.path, resource })
      set({ revision: 0 })
      onSave()
      load()
    },
    // TODO: implement using client.fileCopy
    saveAs: async (path) => {
      const { onSaveAs } = get()
      onSaveAs(path)
    },
  }))
}

export const select = createSelector
export const selectors = {
  isUpdated: (state: State) => {
    return state.revision > 0
  },
}

export function useStore<R>(selector: (state: State) => R): R {
  const store = React.useContext(StoreContext)
  assert(store, 'store provider is required')
  return zustand.useStore(store, selector)
}

const StoreContext = React.createContext<zustand.StoreApi<State> | null>(null)
export const StoreProvider = StoreContext.Provider
