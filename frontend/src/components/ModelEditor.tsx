import React, { useCallback, useMemo } from 'react'
import { addEdge, Background, Connection, Controls, Edge, getConnectedEdges, getIncomers, getOutgoers, Handle, MiniMap, Node, Position, ReactFlow, useEdgesState, useNodesState, useReactFlow } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Box, IconButton, InputAdornment, TextField } from '@mui/material';
import TerminalIcon from '@mui/icons-material/Terminal';
import MemoryIcon from '@mui/icons-material/Memory';
import DeleteIcon from '@mui/icons-material/Delete';
const initialNodes: Node[] = [
    { id: '1', position: { x: 0, y: 0 }, data: { label: '1' }, type: "SWComponent" },
    { id: '2', position: { x: 0, y: 100 }, data: { label: '2' }, type: "SWComponent" },

];
const initialEdges: Edge[] = [{ id: 'e1-2', source: '1', target: '2', animated: true }];

function SWComponentNode({ data, id }) {
    const { setNodes } = useReactFlow();
    const onChange = useCallback((evt) => {

    }, []);

    return (
        <>
            <Handle type="target" position={Position.Top} />
            <Handle type="target" position={Position.Left} />
            <Box sx={{ bgcolor: "white", borderRadius: 1, border: 1 }}>
                <TextField sx={{
                    "& fieldset": { border: 'none' },
                }}
                    hiddenLabel
                    id="filled-hidden-label-small"

                    value={data.label}
                    size="small"

                    InputProps={{
                        startAdornment: (
                            <InputAdornment position="start">
                                <TerminalIcon />
                            </InputAdornment>
                        ),
                    }}
                />
                <IconButton aria-label="delete"
                    onClick={() => { setNodes((prevNodes) => prevNodes.filter(node => node.id != id)); }}>
                    <DeleteIcon />
                </IconButton>
            </Box>

            <Handle type="source" position={Position.Bottom} id="a" />
            <Handle type="source" position={Position.Right} />
        </>
    );
}




const ModelEditor = () => {
    const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
    const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
    const nodeTypes = useMemo(() => ({ SWComponent: SWComponentNode, }), []);
    const onConnect = useCallback(
        (params: Connection) => {
            const edge: Edge = { ...params, animated: true, id: `$(edges.length)+1` }
            setEdges((eds) => addEdge(edge, eds))
        },
        [setEdges],
    );
    const onNodesDelete = useCallback(
        (deleted) => {
            setEdges(
                deleted.reduce((acc, node) => {
                    const incomers = getIncomers(node, nodes, edges);
                    const outgoers = getOutgoers(node, nodes, edges);
                    const connectedEdges = getConnectedEdges([node], edges);

                    const remainingEdges = acc.filter(
                        (edge) => !connectedEdges.includes(edge),
                    );

                    const createdEdges = incomers.flatMap(({ id: source }) =>
                        outgoers.map(({ id: target }) => ({
                            id: `${source}->${target}`,
                            source,
                            target,
                        })),
                    );

                    return [...remainingEdges, ...createdEdges];
                }, edges),
            );
        },
        [nodes, edges],
    );
    return (

        <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodesDelete={onNodesDelete}
            onConnect={onConnect}
            nodeTypes={nodeTypes}
            fitView
        >
            <Controls />
            <MiniMap />
            <Background gap={12} size={1} />
        </ReactFlow>

    );
}


export default ModelEditor