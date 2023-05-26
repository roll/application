import * as React from 'react'
import Stack from '@mui/material/Stack'
import Toolbar from '@mui/material/Toolbar'
import RuleIcon from '@mui/icons-material/Rule'
import CompressIcon from '@mui/icons-material/Compress'
import DataObjectIcon from '@mui/icons-material/DataObject'
import FormatClearIcon from '@mui/icons-material/FormatClear'
import ReportGmailerrorredIcon from '@mui/icons-material/ReportGmailerrorred'
import UndoIcon from '@mui/icons-material/Undo'
import HandymanIcon from '@mui/icons-material/Handyman'
import CodeIcon from '@mui/icons-material/Code'
import TuneIcon from '@mui/icons-material/Tune'
import EditRoadIcon from '@mui/icons-material/EditRoad'
import IconButton from '../../Parts/Buttons/Icon'

export type MenuBarItem =
  | 'editor'
  | 'metadata'
  | 'report'
  | 'source'
  | 'errors'
  | 'clear'
  | 'fix'
  | 'minify'
  | 'prettify'
  | 'undo'

export interface MenuBarProps {
  items?: MenuBarItem[]
  labels?: { [key in MenuBarItem]?: string | undefined }
  colors?: { [key in MenuBarItem]?: 'success' | 'warning' | 'error' | 'info' | undefined }
  onEditor?: () => void
  onMetadata?: () => void
  onReport?: () => void
  onSource?: () => void
  onErrors?: () => void
  onClear?: () => void
  onFix?: () => void
  onMinify?: () => void
  onPrettify?: () => void
  onUndo?: () => void
}

// TODO: don't use hard-coded color (info=#9c27b0)
// TODO: add spacing between buttons
// TODO: use React.useMemo for better performance/animation
export default function MenuBar(props: React.PropsWithChildren<MenuBarProps>) {
  const Editor = () => {
    if (!props.items?.includes('editor')) return null
    return (
      <IconButton
        small
        variant="text"
        label={props.labels?.editor || 'Editor'}
        Icon={EditRoadIcon}
        color={props.colors?.editor}
        disabled={!props.onEditor}
        onClick={() => props.onEditor!()}
        sx={{
          '&.Mui-disabled': {
            color: props.colors?.editor ? '#9c27b0' : undefined,
          },
        }}
      />
    )
  }

  const Metadata = () => {
    if (!props.items?.includes('metadata')) return null
    return (
      <IconButton
        small
        variant="text"
        label={props.labels?.metadata || 'Metadata'}
        Icon={TuneIcon}
        color={props.colors?.metadata}
        disabled={!props.onMetadata}
        onClick={() => props.onMetadata!()}
        sx={{
          '&.Mui-disabled': {
            color: props.colors?.editor ? '#9c27b0' : undefined,
          },
        }}
      />
    )
  }

  const Report = () => {
    if (!props.items?.includes('report')) return null
    return (
      <IconButton
        small
        variant="text"
        label={props.labels?.report || 'Report'}
        Icon={RuleIcon}
        color={props.colors?.report}
        disabled={!props.onReport}
        onClick={() => props.onReport!()}
        sx={{
          '&.Mui-disabled': {
            color: props.colors?.editor ? '#9c27b0' : undefined,
          },
        }}
      />
    )
  }

  const Source = () => {
    if (!props.items?.includes('source')) return null
    return (
      <IconButton
        small
        variant="text"
        label={props.labels?.source || 'Source'}
        Icon={CodeIcon}
        color={props.colors?.source}
        disabled={!props.onSource}
        onClick={() => props.onSource!()}
        sx={{
          '&.Mui-disabled': {
            color: props.colors?.editor ? '#9c27b0' : undefined,
          },
        }}
      />
    )
  }

  const Errors = () => {
    if (!props.items?.includes('errors')) return null
    return (
      <IconButton
        small
        variant="text"
        label={props.labels?.errors || 'Errors'}
        Icon={ReportGmailerrorredIcon}
        color={props.colors?.errors}
        disabled={!props.onErrors}
        onClick={() => props.onErrors!()}
      />
    )
  }

  const Fix = () => {
    if (!props.items?.includes('fix')) return null
    return (
      <IconButton
        small
        variant="text"
        label={props.labels?.fix || 'Fix'}
        Icon={HandymanIcon}
        color={props.colors?.fix}
        disabled={!props.onFix}
        onClick={() => props.onFix!()}
      />
    )
  }

  const Minify = () => {
    if (!props.items?.includes('minify')) return null
    return (
      <IconButton
        small
        variant="text"
        label={props.labels?.minify || 'Minify'}
        Icon={CompressIcon}
        color={props.colors?.minify}
        disabled={!props.onMinify}
        onClick={() => props.onMinify!()}
      />
    )
  }

  const Prettify = () => {
    if (!props.items?.includes('prettify')) return null
    return (
      <IconButton
        small
        variant="text"
        label={props.labels?.prettify || 'Prettify'}
        Icon={DataObjectIcon}
        color={props.colors?.prettify}
        disabled={!props.onPrettify}
        onClick={() => props.onPrettify!()}
      />
    )
  }

  const Clear = () => {
    if (!props.items?.includes('clear')) return null
    return (
      <IconButton
        small
        variant="text"
        label={props.labels?.clear || 'Clear'}
        Icon={FormatClearIcon}
        color={props.colors?.clear}
        disabled={!props.onClear}
        onClick={() => props.onClear!()}
      />
    )
  }

  const Undo = () => {
    if (!props.items?.includes('undo')) return null
    return (
      <IconButton
        small
        variant="text"
        label={props.labels?.undo || 'Undo'}
        Icon={UndoIcon}
        color={props.colors?.undo}
        disabled={!props.onUndo}
        onClick={() => props.onUndo!()}
      />
    )
  }

  const DefaultBar = () => {
    return (
      <Stack direction="row" spacing={1}>
        <Editor />
        <Metadata />
        <Report />
        <Source />
        <Errors />
        <Clear />
        <Fix />
        <Minify />
        <Prettify />
        <Undo />
        {props.children}
      </Stack>
    )
  }

  const CustomBar = () => {
    return <React.Fragment>{props.children}</React.Fragment>
  }

  return (
    <Toolbar
      disableGutters
      sx={{ borderBottom: 'solid 1px #ddd', backgroundColor: '#fafafa', paddingX: 2 }}
    >
      {props.items ? <DefaultBar /> : <CustomBar />}
    </Toolbar>
  )
}
