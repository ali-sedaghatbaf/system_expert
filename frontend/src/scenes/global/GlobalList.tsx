import { ListItemButton, ListItemIcon, ListItemText } from '@mui/material'
import DashboardIcon from '@mui/icons-material/Dashboard';
import InboxIcon from '@mui/icons-material/Inbox';
import { Link } from 'react-router-dom'

const GlobalList = () => {
    return (
        <>
            <Link to="/" style={{ textDecoration: 'none' }}>
                <ListItemButton>
                    <ListItemIcon>
                        <DashboardIcon />
                    </ListItemIcon>
                    <ListItemText primary="Home" />
                </ListItemButton>
            </Link>
            <Link to="/inbox" style={{ textDecoration: 'none' }}>
                <ListItemButton  >
                    <ListItemIcon>
                        <InboxIcon />
                    </ListItemIcon>
                    <ListItemText primary="Inbox" />
                </ListItemButton>
            </Link>
        </>
    )
}

export default GlobalList