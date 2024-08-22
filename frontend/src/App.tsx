
import { Box, Container, CssBaseline, Divider, IconButton, List, ListItemButton, ListItemIcon, ListItemText, ListSubheader, Switch, textFieldClasses, Toolbar } from '@mui/material';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';


import React from 'react';
import AppBar from './components/AppBar';
import ToolBar from './components/ToolBar';
import Drawer from './components/Drawer';
import CSList from './scenes/cs/CSList';
import FSList from './scenes/fs/FSList';

import Copyright from './components/Copyright';
import Home from './scenes/global/Home';
import { Route, Routes } from 'react-router-dom';
import DataList from './scenes/data/DataList';
import GlobalList from './scenes/global/GlobalList';
import Inbox from './scenes/global/Inbox';
import TARA from './scenes/cs/TARA';



function App() {
  const drawerWidth: number = 280;
  // TODO remove, this demo shouldn't need to reset the theme.
  //const theme = createTheme();
  const [drawerOpen, setDrawerOpen] = React.useState(true);
  const toggleDrawer = () => {
    setDrawerOpen(!drawerOpen);
  };

  return (

    //<ThemeProvider theme={theme}>

    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      <AppBar position="absolute" open={drawerOpen} drawerWidth={drawerWidth}>
        <ToolBar drawerOpen={drawerOpen} handleClick={toggleDrawer} />
      </AppBar>
      <Drawer variant="permanent" open={drawerOpen} drawerWidth={drawerWidth}>
        <Toolbar
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'flex-end',
            px: [1],
          }}
        >
          <IconButton onClick={toggleDrawer}>
            <ChevronLeftIcon />
          </IconButton>
        </Toolbar>
        <Divider />
        <List component="nav">
          <GlobalList />
          <Divider sx={{ my: 1 }} />
          <ListSubheader component="div" inset>
            COMPLIANCE SERVICES
          </ListSubheader>
          <CSList />
          <FSList />
          <Divider sx={{ my: 1 }} />
          <ListSubheader component="div" inset>
            EXTERNAL INTERFACES
          </ListSubheader>
          <DataList />
        </List>
      </Drawer>
      <Box
        component="main"
        sx={{
          backgroundColor: (theme) =>
            theme.palette.mode === 'light'
              ? theme.palette.grey[100]
              : theme.palette.grey[900],
          flexGrow: 1,
          height: '100vh',
          overflow: 'auto',
        }}
      >
        <Toolbar />
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path='/inbox' element={<Inbox />} />
            <Route path='/cs'>
              <Route path='tara' element={<TARA />} />
            </Route>
          </Routes>
          <Copyright sx={{ pt: 4 }} />
        </Container>
      </Box>
    </Box>

    //</ThemeProvider>



  );
}


export default App;