import * as React from 'react'
import Box from '@mui/material/Box'
import Grid from '@mui/material/Grid'
import MenuItem from '@mui/material/MenuItem'
import Select from '@mui/material/Select'
import Dialog from '@mui/material/Dialog'
import DialogTitle from '@mui/material/DialogTitle'
import DialogContent from '@mui/material/DialogContent'
import TextField from '@mui/material/TextField'
import Columns from '../../../Parts/Columns'
import Cancel from '@mui/icons-material/Cancel'
import CheckIcon from '@mui/icons-material/Check'
import IconButton from '../../../Parts/Buttons/Icon'
import { useStore } from '../store'

export default function SaveAsDialog() {
  const file = useStore((state) => state.file)
  if (!file) return null
  const [name, setName] = React.useState(file.record!.resource.name)
  const [format, setFormat] = React.useState('csv')
  const dialog = useStore((state) => state.dialog)
  const updateState = useStore((state) => state.updateState)
  const saveAs = useStore((state) => state.saveAs)
  const handleChange = (ev: React.ChangeEvent<HTMLInputElement>) =>
    setName(ev.target.value)
  const handleCancel = () => updateState({ dialog: undefined })
  const handleSave = async () => {
    console.log(name, format)
    handleCancel()
    saveAs(`${name}.${format}`)
  }
  return (
    <Dialog
      fullWidth
      maxWidth="sm"
      open={dialog === 'saveAs'}
      onClose={handleCancel}
      aria-labelledby="dialog-title"
      aria-describedby="dialog-description"
    >
      <DialogTitle id="dialog-title">Save As</DialogTitle>
      <DialogContent sx={{ py: 0 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={9}>
            <TextField
              autoFocus
              fullWidth
              size="small"
              value={name}
              onChange={handleChange}
              onKeyPress={(event) => {
                if (event.key === 'Enter') handleSave()
              }}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <Select
              fullWidth
              size="small"
              value={format}
              onChange={(event) => setFormat(event.target.value)}
            >
              <MenuItem value={file.record!.resource.format}>
                {file.record!.resource.format}
              </MenuItem>
            </Select>
          </Grid>
        </Grid>
      </DialogContent>
      <Box sx={{ paddingX: 3, paddingY: 1 }}>
        <Columns spacing={2}>
          <IconButton
            fullWidth
            label="Cancel"
            sx={{ my: 0.5 }}
            onClick={handleCancel}
            aria-label="cancel"
            color="warning"
            variant="contained"
            Icon={Cancel}
          />
          <IconButton
            fullWidth
            label="Save"
            sx={{ my: 0.5 }}
            onClick={handleSave}
            aria-label="accept"
            variant="contained"
            Icon={CheckIcon}
          />
        </Columns>
      </Box>
    </Dialog>
  )
}
