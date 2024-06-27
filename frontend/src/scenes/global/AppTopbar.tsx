import { Box, IconButton, InputBase, useTheme } from "@mui/material";
import { ColorModeContext, tokens } from "../../theme";
import { useContext } from "react";
import SearchIcon from "@mui/icons-material/Search";
import NotificationsOutlinedIcon from "@mui/icons-material/NotificationsOutlined";
import SettingsOutlinedIcon from "@mui/icons-material/SettingsOutlined";
import PersonOutlinedIcon from "@mui/icons-material/PersonOutlined";
import LighhtModeOutlinedIcon from "@mui/icons-material/LightModeOutlined";
import DarkModeOutlinedIcon from "@mui/icons-material/DarkModeOutlined";


const AppTopbar = () => {
    const theme = useTheme();
    const colors = tokens(theme.palette.mode);
    const colorMode = useContext(ColorModeContext);
    return (
        <Box display="flex" justifyContent="space-between" padding={2}>
            <Box display="flex" bgcolor={colors.primary[400]} borderRadius="3px">
                <InputBase sx={{ ml: 2, flex: 1 }} placeholder="Search..." />
                <IconButton type="button" sx={{ p: 1 }}><SearchIcon /></IconButton>
            </Box>
            <Box display="flex">
                <IconButton onClick={colorMode.toggleColorMode}>
                    {theme.palette.mode === 'light' ? (<DarkModeOutlinedIcon />) : (<LighhtModeOutlinedIcon />)}
                </IconButton>
                <IconButton><NotificationsOutlinedIcon /></IconButton>
                <IconButton><SettingsOutlinedIcon /></IconButton>
                <IconButton><PersonOutlinedIcon /></IconButton>
            </Box>
        </Box>
    )
}

export default AppTopbar;