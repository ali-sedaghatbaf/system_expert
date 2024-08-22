import { styled } from "@mui/material";
import MuiDrawer, { DrawerProps } from '@mui/material/Drawer';

interface AppDrawerProps extends DrawerProps {
    open?: boolean;
    drawerWidth: number;
}
const Drawer = styled(MuiDrawer, { shouldForwardProp: (prop) => prop !== 'open' })<AppDrawerProps>(
    ({ theme, open, drawerWidth }) => ({
        '& .MuiDrawer-paper': {
            position: 'relative',
            whiteSpace: 'nowrap',
            width: drawerWidth,
            transition: theme.transitions.create('width', {
                easing: theme.transitions.easing.sharp,
                duration: theme.transitions.duration.enteringScreen,
            }),
            boxSizing: 'border-box',
            ...(!open && {
                overflowX: 'hidden',
                transition: theme.transitions.create('width', {
                    easing: theme.transitions.easing.sharp,
                    duration: theme.transitions.duration.leavingScreen,
                }),
                width: theme.spacing(7),
                [theme.breakpoints.up('sm')]: {
                    width: theme.spacing(9),
                },
            }),
        },
    }),
);

export default Drawer;