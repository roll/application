export interface ITable {
  header: IHeader
  rows: IRow[]
}

export type IHeader = string[]
export interface IRow {
  [key: string]: any
}

export type ITableLoader = (props: {
  skip: number
  limit: number
  sortInfo: any
}) => Promise<{
  data: object[]
  count: number
}>
