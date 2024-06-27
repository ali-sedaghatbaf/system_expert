import { Route, Routes } from 'react-router-dom';
import AppTopbar from './scenes/global/AppTopbar.tsx';
import { ColorModeContext, useMode } from './theme.tsx';
import { CssBaseline, ThemeProvider } from '@mui/material';
import Dashboard from './scenes/home/Home.tsx';
import AppSidebar from './scenes/global/AppSidebar.tsx';

function App() {
  const [theme, colorMode] = useMode();

  return (
    <ColorModeContext.Provider value={colorMode}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <div className="app">
          <AppSidebar />
          <main className='content'>

            <AppTopbar />
            <Routes>
              <Route path='/' element={<Dashboard />}></Route>
            </Routes>
          </main>

        </div>
      </ThemeProvider>
    </ColorModeContext.Provider>


  );
}


export default App;