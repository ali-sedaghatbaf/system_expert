import { ListItemButton, ListItemIcon, ListItemText } from '@mui/material'
import AssignmentIcon from '@mui/icons-material/Assignment';

const DataList = () => {
    return (
        <>
            <ListItemButton>
                <ListItemIcon>
                    <AssignmentIcon />
                </ListItemIcon>
                <ListItemText primary="SystemWeaver" />
            </ListItemButton>
            <ListItemButton>
                <ListItemIcon>
                    <AssignmentIcon />
                </ListItemIcon>
                <ListItemText primary="NVD" />
            </ListItemButton>
            <ListItemButton>
                <ListItemIcon>
                    <AssignmentIcon />
                </ListItemIcon>
                <ListItemText primary="MITRE ATT&CK" />
            </ListItemButton>
        </>
    )
}

export default DataList