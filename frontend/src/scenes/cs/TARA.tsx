import { Accordion, AccordionDetails, AccordionSummary, Box, Grid, Paper, TextField, Typography } from '@mui/material'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

import AppTable from '../../components/AppTable';
import ModelEditor from '../../components/ModelEditor';

const TARA = () => {
    return (
        <Grid container spacing={3}>
            <Grid item xs={8}>
                <Box>
                    <Paper
                        sx={{
                            p: 2,
                            display: 'flex',
                            flexDirection: 'column',

                        }}
                    >
                        <Box sx={{ m: 1, p: 1 }}>
                            <Typography variant='h6'>TARA for ...</Typography>

                        </Box>
                        <Accordion defaultExpanded>
                            <AccordionSummary
                                expandIcon={<ExpandMoreIcon />}
                                aria-controls="panel1-content"
                                id="panel1-header"
                            >
                                1. Item Definition
                            </AccordionSummary>
                            <AccordionDetails>

                                Define the "item" under consideration, which is the subject of the TARA process.
                                The item can be a system, a component, or a set of components within the vehicle, including software and hardware aspects.

                                <Box component="form"
                                    sx={{
                                        '& .MuiTextField-root': { m: 2, width: '95%' },
                                    }}
                                    noValidate
                                    autoComplete="off">
                                    <TextField
                                        id="outlined-multiline-flexible"
                                        hiddenLabel
                                        multiline
                                        rows={5}


                                    />
                                </Box>
                                Draw the item's model including the hardware/software components, communication channels and the stored/transmitted data.
                                <Box sx={{ border: 1, borderColor: 'grey.400', width: '95%', height: 500, m: 2, p: 1 }}>
                                    <ModelEditor />
                                </Box>

                            </AccordionDetails>
                        </Accordion>
                        <Accordion>
                            <AccordionSummary
                                expandIcon={<ExpandMoreIcon />}
                                aria-controls="panel2-content"
                                id="panel2-header"
                            >
                                2. Asset Identification
                            </AccordionSummary>
                            <AccordionDetails>
                                Identify the assets that need protection. These are typically components, subsystems, or information within the vehicle that, if compromised, could lead to a cybersecurity incident.

                                <Box sx={{ border: 1, borderColor: 'grey.400', width: '95%', height: 500, m: 2, p: 1 }}>
                                    <AppTable />
                                </Box>

                            </AccordionDetails>
                        </Accordion>
                        <Accordion>
                            <AccordionSummary
                                expandIcon={<ExpandMoreIcon />}
                                aria-controls="panel3-content"
                                id="panel3-header"
                            >
                                3. Threat Identification
                            </AccordionSummary>
                            <AccordionDetails>
                                Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse
                                malesuada lacus ex, sit amet blandit leo lobortis eget.
                            </AccordionDetails>

                        </Accordion>
                        <Accordion>
                            <AccordionSummary
                                expandIcon={<ExpandMoreIcon />}
                                aria-controls="panel3-content"
                                id="panel3-header"
                            >
                                4. Impact Analysis
                            </AccordionSummary>
                            <AccordionDetails>
                                Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse
                                malesuada lacus ex, sit amet blandit leo lobortis eget.
                            </AccordionDetails>

                        </Accordion>
                        <Accordion>
                            <AccordionSummary
                                expandIcon={<ExpandMoreIcon />}
                                aria-controls="panel3-content"
                                id="panel3-header"
                            >
                                5. Attack Path Analysis
                            </AccordionSummary>
                            <AccordionDetails>
                                Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse
                                malesuada lacus ex, sit amet blandit leo lobortis eget.
                            </AccordionDetails>

                        </Accordion>
                        <Accordion>
                            <AccordionSummary
                                expandIcon={<ExpandMoreIcon />}
                                aria-controls="panel3-content"
                                id="panel3-header"
                            >
                                6. Goal Identification
                            </AccordionSummary>
                            <AccordionDetails>
                                Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse
                                malesuada lacus ex, sit amet blandit leo lobortis eget.
                            </AccordionDetails>

                        </Accordion>
                    </Paper >
                </Box >
            </Grid>
            <Grid item xs={4}>
                <Box>
                    <Paper
                        sx={{
                            p: 2,
                            display: 'flex',
                            flexDirection: 'column',

                        }}
                    >
                        <Box sx={{ m: 1, p: 1 }}>
                            <Typography variant='h6'>Review Notes</Typography>

                        </Box>
                    </Paper>
                </Box>
            </Grid>
        </Grid>
    )
}

export default TARA