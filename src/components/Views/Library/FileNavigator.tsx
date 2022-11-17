import * as React from 'react'
import Box from '@mui/material/Box'
import { SyntheticEvent } from 'react'
import { useSpring, animated } from 'react-spring'
import TreeView from '@mui/lab/TreeView'
import TextField from '@mui/material/TextField'
import TreeItem, { TreeItemProps, treeItemClasses } from '@mui/lab/TreeItem'
import Collapse from '@mui/material/Collapse'
import SvgIcon, { SvgIconProps } from '@mui/material/SvgIcon'
import { alpha, styled } from '@mui/material/styles'
import { TransitionProps } from '@mui/material/transitions'
import { useStore } from '../../Editors/Files/store'
import Menu from '@mui/material/Menu'
import MenuItem from '@mui/material/MenuItem'
import IconButton from '@mui/material/IconButton'
import CheckIcon from '@mui/icons-material/Check'
import CloseIcon from '@mui/icons-material/Close'
interface FileNavigatorProps {
  initialState?: {
    mouseX: number | null
    mouseY: number | null
  } | null
  onFolderSelect: (destinationDirectory: string | null) => void
  onCreateDirectory: (directoryname: string) => void
}
export default function FileNavigator(props: FileNavigatorProps) {
  const [contextMenu, setContextMenu] = React.useState(props.initialState)
  const path = useStore((state: any) => state.path)
  const directories = useStore((state: any) => state.directories)
  const listFolders = useStore((state: any) => state.listFolders)
  const tree = indexTree(createTree(directories))
  const [selectedNode, setSelectedNode] = React.useState<string[] | null>(null)
  const [addDirectory, setAddDirectory] = React.useState(false)
  const [newDirectoryName, setNewDirectoryName] = React.useState('')

  const handleSelect = (event: SyntheticEvent, nodeId: string[]) => {
    event.preventDefault()
    setSelectedNode(nodeId)
    if (!Array.isArray(nodeId)) {
      props.onFolderSelect(nodeId)
    }
  }
  const onUserInput = (event: React.ChangeEvent<HTMLInputElement>) => {
    setNewDirectoryName(event.target.value)
  }
  const handleContextMenuClose = () => {
    setContextMenu(null)
  }
  const handleContextMenu = (event: React.MouseEvent) => {
    event.preventDefault()
    setContextMenu({
      mouseX: event.clientX - 1,
      mouseY: event.clientY - 1,
    })
  }
  const startCreateDirectory = () => {
    setAddDirectory(true)
    setContextMenu(null)
  }
  const onCreateDirectory = () => {
    setSelectedNode(null)
    setAddDirectory(false)
    props.onCreateDirectory(newDirectoryName)
  }
  const onCancelCreateDirectory = () => {
    setSelectedNode(null)
    setAddDirectory(false)
  }
  React.useEffect(() => {
    listFolders().catch(console.error)
  }, [])
  return (
    <React.Fragment>
      <div onContextMenu={handleContextMenu}>
        <TreeView
          aria-label="file navigator"
          defaultExpanded={['1']}
          defaultCollapseIcon={<MinusSquare />}
          defaultExpandIcon={<PlusSquare />}
          defaultEndIcon={<CloseSquare />}
          onNodeSelect={handleSelect}
          selected={path || ''}
          sx={{
            paddingTop: 2,
            paddingBottom: 2,
            height: 240,
            overflowY: 'auto',
            maxWidth: 400,
          }}
        >
          {tree.sort(compareNodes).map((node: any) => (
            <TreeNode node={node} key={node.path} />
          ))}
        </TreeView>
      </div>
      <Box
        display={addDirectory ? '' : 'none'}
        sx={{ boxShadow: 1, padding: 1, borderRadius: 1 }}
      >
        <Box component="span" color="primary">
          {selectedNode && selectedNode + '/ '}
        </Box>
        <TextField size="small" value={newDirectoryName} onChange={onUserInput} />
        <IconButton aria-label="accept" onClick={onCreateDirectory}>
          <CheckIcon color="secondary" />
        </IconButton>
        <IconButton aria-label="close" onClick={onCancelCreateDirectory}>
          <CloseIcon color="warning" />
        </IconButton>
      </Box>
      {contextMenu && (
        <Menu
          keepMounted
          open={contextMenu.mouseY !== null}
          onClose={handleContextMenuClose}
          anchorReference="anchorPosition"
          anchorPosition={
            contextMenu.mouseY !== null && contextMenu.mouseX !== null
              ? { top: contextMenu.mouseY, left: contextMenu.mouseX }
              : undefined
          }
        >
          <MenuItem onClick={startCreateDirectory}>Create New Directory</MenuItem>
        </Menu>
      )}
    </React.Fragment>
  )
}
function MinusSquare(props: SvgIconProps) {
  return (
    <SvgIcon fontSize="inherit" style={{ width: 14, height: 14 }} {...props}>
      {/* tslint:disable-next-line: max-line-length */}
      <path d="M22.047 22.074v0 0-20.147 0h-20.12v0 20.147 0h20.12zM22.047 24h-20.12q-.803 0-1.365-.562t-.562-1.365v-20.147q0-.776.562-1.351t1.365-.575h20.147q.776 0 1.351.575t.575 1.351v20.147q0 .803-.575 1.365t-1.378.562v0zM17.873 11.023h-11.826q-.375 0-.669.281t-.294.682v0q0 .401.294 .682t.669.281h11.826q.375 0 .669-.281t.294-.682v0q0-.401-.294-.682t-.669-.281z" />
    </SvgIcon>
  )
}
function PlusSquare(props: SvgIconProps) {
  return (
    <SvgIcon fontSize="inherit" style={{ width: 14, height: 14 }} {...props}>
      {/* tslint:disable-next-line: max-line-length */}
      <path d="M22.047 22.074v0 0-20.147 0h-20.12v0 20.147 0h20.12zM22.047 24h-20.12q-.803 0-1.365-.562t-.562-1.365v-20.147q0-.776.562-1.351t1.365-.575h20.147q.776 0 1.351.575t.575 1.351v20.147q0 .803-.575 1.365t-1.378.562v0zM17.873 12.977h-4.923v4.896q0 .401-.281.682t-.682.281v0q-.375 0-.669-.281t-.294-.682v-4.896h-4.923q-.401 0-.682-.294t-.281-.669v0q0-.401.281-.682t.682-.281h4.923v-4.896q0-.401.294-.682t.669-.281v0q.401 0 .682.281t.281.682v4.896h4.923q.401 0 .682.281t.281.682v0q0 .375-.281.669t-.682.294z" />
    </SvgIcon>
  )
}
function CloseSquare(props: SvgIconProps) {
  return (
    <SvgIcon
      className="close"
      fontSize="inherit"
      style={{ width: 14, height: 14 }}
      {...props}
    >
      {/* tslint:disable-next-line: max-line-length */}
      <path d="M17.485 17.512q-.281.281-.682.281t-.696-.268l-4.12-4.147-4.12 4.147q-.294.268-.696.268t-.682-.281-.281-.682.294-.669l4.12-4.147-4.12-4.147q-.294-.268-.294-.669t.281-.682.682-.281.696 .268l4.12 4.147 4.12-4.147q.294-.268.696-.268t.682.281 .281.669-.294.682l-4.12 4.147 4.12 4.147q.294.268 .294.669t-.281.682zM22.047 22.074v0 0-20.147 0h-20.12v0 20.147 0h20.12zM22.047 24h-20.12q-.803 0-1.365-.562t-.562-1.365v-20.147q0-.776.562-1.351t1.365-.575h20.147q.776 0 1.351.575t.575 1.351v20.147q0 .803-.575 1.365t-1.378.562v0z" />
    </SvgIcon>
  )
}
function TransitionComponent(props: TransitionProps) {
  const style = useSpring({
    from: {
      opacity: 0,
      transform: 'translate3d(20px,0,0)',
    },
    to: {
      opacity: props.in ? 1 : 0,
      transform: `translate3d(${props.in ? 0 : 20}px,0,0)`,
    },
  })

  return (
    <animated.div style={style}>
      <Collapse {...props} />
    </animated.div>
  )
}
const StyledTreeItem = styled((props: TreeItemProps) => (
  <TreeItem {...props} TransitionComponent={TransitionComponent} />
))(({ theme }) => ({
  '& .MuiTreeItem-label': 'normal',
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

function TreeNode({ node }: any) {
  return (
    <StyledTreeItem key={node.path} nodeId={node.path} label={node.name}>
      {node.children.sort(compareNodes).map((node: any) => (
        <TreeNode node={node} key={node.path} />
      ))}
    </StyledTreeItem>
  )
}

function createTree(paths: string[]) {
  const result: any = []
  const level = { result }
  paths &&
    paths.forEach((path) => {
      ;(path as string).split('/').reduce((r: any, name) => {
        if (!r[name]) {
          r[name] = { result: [] }
          r.result.push({ name, children: r[name].result })
        }
        return r[name]
      }, level)
    })
  return result
}

function indexTree(tree: any, basepath: string = '') {
  for (const item of tree) {
    item.path = basepath ? [basepath, item.name].join('/') : item.name
    if (item.children) indexTree(item.children, item.path)
  }
  return tree
}

function compareNodes(a: any, b: any) {
  if (a.children.length && !b.children.length) return -1
  if (!a.children.length && b.children.length) return 1
  return 0
}
