import { Collapse, List, ListItemButton, ListItemIcon, ListItemText } from '@mui/material'
import AssignmentIcon from '@mui/icons-material/Assignment';
import ExpandLess from '@mui/icons-material/ExpandLess';
import ExpandMore from '@mui/icons-material/ExpandMore';
import StarBorder from '@mui/icons-material/StarBorder';
import React from 'react';
import { Link } from 'react-router-dom';

const CSList = () => {
    const [open, setOpen] = React.useState(false);

    const handleClick = () => {
        setOpen(!open);
    };
    return (
        <>
            <ListItemButton onClick={handleClick}>
                <ListItemIcon>
                    <AssignmentIcon />
                </ListItemIcon>
                <ListItemText primary="Cyber Security" />
                {open ? <ExpandLess /> : <ExpandMore />}
            </ListItemButton>
            <Collapse in={open} timeout="auto" unmountOnExit>
                <List component="div" disablePadding>
                    <Link to="/cs/plan" style={{ textDecoration: 'none' }}>
                        <ListItemButton sx={{ pl: 4 }}>
                            <ListItemIcon>
                                <StarBorder />
                            </ListItemIcon>
                            <ListItemText primary="CS Plan" />
                        </ListItemButton></Link>
                    <Link to="/cs/tara" style={{ textDecoration: 'none' }}>
                        <ListItemButton sx={{ pl: 4 }}>
                            <ListItemIcon>
                                <StarBorder />
                            </ListItemIcon>
                            <ListItemText primary="TARA" />
                        </ListItemButton>
                    </Link>
                </List>
            </Collapse>

        </>
    )
}

export default CSList