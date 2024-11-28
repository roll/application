import * as React from 'react'
import noop from 'lodash/noop'
import Box from '@mui/material/Box'
import Toolbar from '@mui/material/Toolbar'
import CheckIcon from '@mui/icons-material/Check'
import IconButton from '../../Parts/Buttons/Icon'
import Columns from '../Grids/Columns'
import ElectricBoltIcon from '@mui/icons-material/ElectricBolt'
import { useTranslation } from 'react-i18next'

export interface ActionBarProps {}

export function ActionBar(props: React.PropsWithChildren<ActionBarProps>) {
  return (
    <Toolbar
      disableGutters
      sx={{ borderTop: 'solid 1px #ddd', backgroundColor: '#fafafa', paddingX: 2 }}
    >
      <ActionBarItems {...props} />
    </Toolbar>
  )
}

function ActionBarItems(props: React.PropsWithChildren<ActionBarProps>) {
  return <Columns spacing={2}>{props.children}</Columns>
}

export interface ButtonProps {
  label?: string
  color?: 'success' | 'warning' | 'error' | 'info'
  updated?: boolean
  disabled?: boolean
  onClick?: () => void
}

export function PublishButton(props: ButtonProps) {
  const onClick = props.onClick || noop
  const { t } = useTranslation()

  return (
    <Box sx={{ marginRight: '20px' }}>
      <IconButton
        label={props.label || t('publish')}
        Icon={ElectricBoltIcon}
        variant={!props.disabled ? 'contained' : 'outlined'}
        disabled={props.disabled}
        onClick={() => onClick()}
        sx={{ backgroundColor: (theme) => props.disabled ? 'white' : theme.palette.OKFNBlack.main, textTransform: 'none', color: (theme) => theme.palette.OKFNWhite.main, '&:hover': {
          color: (theme) => theme.palette.OKFNWhite.main,
          borderColor: (theme) => theme.palette.OKFNBlue.main,
          backgroundColor: (theme) => theme.palette.OKFNBlue.main
        }  }}
      />
    </Box>
  )
}

export function SaveButton(props: ButtonProps) {
  const onClick = props.onClick || noop
  const { t } = useTranslation()

  return (
    <Box>
      <IconButton
        label={props.label || t('save-changes')}
        Icon={CheckIcon}
        variant={props.updated ? 'contained' : 'outlined'}
        disabled={!props.updated}
        onClick={() => onClick()}
        sx={{ backgroundColor: (theme) => !props.updated ? 'white' :  theme.palette.OKFNBlack.main, '&:hover': {
          backgroundColor: (theme) => theme.palette.OKFNBlue.main
        }, textTransform: 'none' }}
      />
    </Box>
  )
}
