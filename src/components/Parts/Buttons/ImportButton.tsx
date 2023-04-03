import * as React from 'react'
import Button, { ButtonProps } from '@mui/material/Button'
import FileUploadIcon from '@mui/icons-material/FileUpload'

// TODO: generalize not only for descriptors?

interface ImportButtonProps extends ButtonProps {
  onImport: (value: any) => void
}

export default function ImportButton(props: ImportButtonProps) {
  return (
    <label htmlFor="import-button">
      <input
        type="file"
        id="import-button"
        accept=".json, .yaml"
        style={{ display: 'none' }}
        onChange={(ev: React.ChangeEvent<HTMLInputElement>) => {
          if (ev.target.files) props.onImport(ev.target.files[0])
          ev.target.value = ''
        }}
      />
      <Button
        disabled={props.disabled}
        title="Import as JSON or YAML"
        variant={props.variant || 'outlined'}
        component="span"
        fullWidth
        {...props}
      >
        {<FileUploadIcon fontSize="small" sx={{ mr: 1 }} />}
        Import
      </Button>
    </label>
  )
}
