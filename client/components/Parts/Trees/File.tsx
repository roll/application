import * as React from 'react'
import { alpha, styled } from '@mui/material/styles'
import { keyframes } from '@mui/system'
import { TreeItem, TreeView, TreeItemProps, treeItemClasses } from '@mui/x-tree-view'
import Box from '@mui/material/Box'
import Stack from '@mui/material/Stack'
import ScrollBox from '../Boxes/Scroll'
import * as helpers from '../../../helpers'
import * as types from '../../../types'
import { useTheme } from '@mui/material/styles'
import openFolderIcon from '../../../assets/open_folder_icon.svg'
import closedFolderIcon from '../../../assets/closed_folder_icon.svg'
import deleteIcon from '../../../assets/delete_icon.svg'
import MoreHorizIcon from '@mui/icons-material/MoreHoriz'
import IconButton from '../../Parts/Buttons/Icon'
import Menu from '@mui/material/Menu'
import MenuItem from '@mui/material/MenuItem'
import ListItemIcon from '@mui/material/ListItemIcon'
import ListItemText from '@mui/material/ListItemText'
import * as store from '@client/store'

export interface FileTreeProps {
  files: types.IFile[]
  event?: types.IEvent
  selected?: string
  selectedMultiple?: string[]
  onSelect: (paths: string[]) => void
  defaultExpanded?: string[]
}

const Context = React.createContext<{
  event?: FileTreeProps['event']
}>({})

export default function FileTree(props: FileTreeProps) {
  const fileTree = React.useMemo(() => helpers.createFileTree(props.files), [props.files])
  const [expanded, setExpanded] = React.useState<string[]>([])
  React.useEffect(() => {
    const defaultExpanded = props.event
      ? helpers.listParentFolders(props.event.paths)
      : props.defaultExpanded || []
    setExpanded([...new Set([...expanded, ...defaultExpanded])])
  }, [props.event, props.defaultExpanded])
  const selectedMultiple = props.selectedMultiple || []
  const selected = props.selected || ''
  return (
    <Context.Provider value={{ event: props.event }}>
      <ScrollBox sx={{ padding: 0, height: 'calc(100vh - 300px)'}} >
        <Stack alignItems="stretch" height="100%">
          <TreeView
            multiSelect
            selected={selectedMultiple.length > 0 ? selectedMultiple : [selected]}
            expanded={expanded}
            onNodeSelect={(_event, nodeIds) => props.onSelect(nodeIds)}
            onNodeToggle={(_event: React.SyntheticEvent, nodeIds: string[]) => {
              // On collapsing we don't collapse a folder if it's not yet selected
              const isCollapsing = nodeIds.length < expanded.length
              if (isCollapsing && !expanded.every((value) => selected.includes(value)))
                return
              setExpanded(nodeIds)
            }}
            defaultCollapseIcon={<img src={openFolderIcon} alt="" />}
            defaultExpandIcon={<img src={closedFolderIcon} alt="" />}
            aria-label="customized"
          >
            {fileTree.map((item) => (
              <TreeNode item={item} key={item.path} />
            ))}
          </TreeView>
          <Box
            sx={{ flexGrow: 1, cursor: 'pointer' }}
            onClick={() => props.onSelect([])}
          ></Box>
        </Stack>
      </ScrollBox>
    </Context.Provider>
  )
}

function TreeNode(props: { item: types.IFileTreeItem }) {
  return (
    <StyledTreeItem key={props.item.path} nodeId={props.item.path} item={props.item}>
      {props.item.children.map((item) => (
        <TreeNode item={item} key={item.path} />
      ))}
    </StyledTreeItem>
  )
}

const StyledTreeItem = styled(
  (
    props: TreeItemProps & {
      item: types.IFileTreeItem
    }
  ) => {
    const { item, ...others } = props
    const { event } = React.useContext(Context)
    const animation =
      event &&
      event.paths.includes(props.nodeId) &&
      ['create', 'delete', 'update'].includes(event.type)
        ? `${fileEventKeyframe} 1s`
        : undefined

    const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
    const open = Boolean(anchorEl);
    const handleContextBtnClick = (event: React.MouseEvent<HTMLButtonElement>) => {
      setAnchorEl(event.currentTarget);
    }
    const handleClose = () => {
      setAnchorEl(null);
    }

    const handleDelete = () => {
      store.openDialog('deleteFilesFolders')
      handleClose()
    }

    const theme = useTheme()
    
    return (
      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
        <TreeItem
          {...others}
          endIcon={ item.type === 'folder' ? <img src={closedFolderIcon} alt="" />: null }
          className={ item.type === 'folder' ? 'type_folder' : 'type_file' }
          sx={{ animation, 
            '&.type_folder > .MuiTreeItem-content': {
              padding: '0 24px'
            },
            '& > .MuiTreeItem-content .MuiTreeItem-iconContainer': {
              marginRight: 0
            },
            '& > .MuiTreeItem-content .MuiTreeItem-label': {
              maxWidth: '188px',
            }
          }}
          label={<TreeItemIcon nodeId={props.nodeId} item={item} />}
        />
        <IconButton 
          sx={{
            width: '20px'
          }}
          id="file-context-menu-btn"
          onClick={handleContextBtnClick}
          color="OKFNCoolGray"
          Icon={MoreHorizIcon}
          aria-controls={open ? 'basic-menu' : undefined}
          aria-haspopup="true"
          aria-expanded={open ? 'true' : undefined}
        />
        <Menu
          id="basic-menu"
          anchorEl={anchorEl}
          open={open}
          onClose={handleClose}
          onClick={async () => await store.selectFileWithoutOpening({ path: item.path })}
          MenuListProps={{
            'aria-labelledby': 'file-context-menu-btn',
          }}
        >
          <MenuItem onClick={handleClose}>
            <ListItemText primary="Rename" />
          </MenuItem>
          <MenuItem onClick={handleClose}>
            <ListItemText primary="Duplicate" secondary="Makes a copy of this file" />
          </MenuItem>
          <MenuItem onClick={handleClose}>
            <ListItemText primary="Open File Location" secondary="The ODE folder where this file exists" />
          </MenuItem>
          <MenuItem onClick={handleDelete}>
            <ListItemIcon sx={{ 
                  paddingTop: '6px',
                  alignSelf: 'flex-start',
                  minWidth: '24px'
              }}>
              {<img src={deleteIcon} alt="" />}
            </ListItemIcon>
            <ListItemText primaryTypographyProps={{
              color: theme.palette.OKFNRed.main,
            }}
              primary="Delete File" secondary="Only removes this file from the ODE folder" />
          </MenuItem>
        </Menu>
      </Box>
    )
  }
)(({ theme }) => ({
  [`& .${treeItemClasses.iconContainer}`]: {
    '& .close': {
      opacity: 0.3,
    },
  },
  [`& .${treeItemClasses.group}`]: {
    marginLeft: 15,
    paddingLeft: 18,
    borderLeft: `1px dashed ${alpha(theme.palette.text.primary, 0.4)}`,
  },
}))

function TreeItemIcon(props: { nodeId: string; item: types.IFileTreeItem }) {
  const theme = useTheme()

  let color = 'gray'
  if (props.item.type === 'folder') color = 'primary'
  if (props.item.name) color = props.item.errors ? theme.palette.OKFNRed.main : theme.palette.OKFNGreenBlue.main

  const fontWeight = 'normal'
  // When data package is enabled consider highlighting it
  // const fontWeight = props.item.type === 'package' ? 'bold' : 'normal'

  return (
    <Box
      sx={{
        py: 1,
        display: 'flex',
        alignItems: 'center',
        overflow: 'hidden',
        '& div': { mr: 1 },
      }}
    >
      <div style={{
        height: '8px',
        width: '8px',
        minWidth: '8px',
        minHeight: '8px',
        backgroundColor: color,
        borderRadius: '50%',}}>{" "}</div>
      <span style={{ whiteSpace: 'nowrap', fontWeight }}>{props.item.label}</span>
    </Box>
  )
}

// TODO: use color from theme
const fileEventKeyframe = keyframes`
  from {
    background-color: yellow;
  }
  to {
    background-color: inherit;
  }
`
