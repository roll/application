import UploadIcon from '@mui/icons-material/Upload'
import InputDialog from '../../Parts/Dialogs/Input'
import { useStore } from '../store'

export default function AddRemoteFileDialog() {
  const fetchFile = useStore((state) => state.fetchFile)
  const updateState = useStore((state) => state.updateState)
  return (
    <InputDialog
      open={true}
      title="Add Remote File"
      label="Add"
      Icon={UploadIcon}
      description="You are fetching a file. Enter source:"
      placholder="Enter or paste a URL"
      onCancel={() => updateState({ dialog: undefined })}
      onConfirm={async (url) => {
        await fetchFile(url)
        updateState({ dialog: undefined })
      }}
    />
  )
}
