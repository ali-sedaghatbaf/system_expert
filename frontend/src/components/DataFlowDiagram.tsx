import React, { useState, useCallback } from 'react';
import ReactFlow, {
    ReactFlowProvider,
    addEdge,
    MiniMap,
    Controls,
    Background,
    BackgroundVariant,
    applyEdgeChanges,
    applyNodeChanges,
} from 'reactflow';
import 'reactflow/dist/style.css';

const initialNodes = [
    {
        id: '1',
        type: 'input', // input node
        data: { label: 'Input Node' },
        position: { x: 250, y: 0 },
    },
    {
        id: '2',
        type: 'default', // default node
        data: { label: 'Default Node' },
        position: { x: 100, y: 100 },
    },
    {
        id: '3',
        type: 'output', // output node
        data: { label: 'Output Node' },
        position: { x: 400, y: 100 },
    },
];

const initialEdges = [
    { id: 'e1-2', source: '1', target: '2', animated: true },
    { id: 'e2-3', source: '2', target: '3', animated: true },
];

const DataFlowDiagram = () => {
    const [nodes, setNodes] = useState(initialNodes);
    const [edges, setEdges] = useState(initialEdges);
    const [editingNodeId, setEditingNodeId] = useState(null);
    const [nodeLabel, setNodeLabel] = useState('');

    const onNodesChange = useCallback(
        (changes) => setNodes((nds) => applyNodeChanges(changes, nds)),
        []
    );

    const onEdgesChange = useCallback(
        (changes) => setEdges((eds) => applyEdgeChanges(changes, eds)),
        []
    );

    const onConnect = useCallback(
        (params) => setEdges((eds) => addEdge(params, eds)),
        []
    );

    const addNode = () => {
        const newNode = {
            id: (nodes.length + 1).toString(),
            type: 'default',
            data: { label: `Node ${nodes.length + 1}` },
            position: { x: Math.random() * 400, y: Math.random() * 400 },
        };
        setNodes((nds) => [...nds, newNode]);
    };

    const handleDoubleClick = (event, node) => {
        event.stopPropagation();
        setEditingNodeId(node.id);
        setNodeLabel(node.data.label);
    };

    const handleInputChange = (event) => {
        setNodeLabel(event.target.value);
    };

    const handleInputBlur = () => {
        updateNodeLabel();
    };

    const handleInputKeyDown = (event) => {
        if (event.key === 'Enter') {
            updateNodeLabel();
        }
    };

    const updateNodeLabel = () => {
        setNodes((nds) =>
            nds.map((node) =>
                node.id === editingNodeId
                    ? { ...node, data: { ...node.data, label: nodeLabel } }
                    : node
            )
        );
        setEditingNodeId(null);
    };

    return (
        <div style={{ height: '100vh' }}>
            <ReactFlowProvider>
                <button onClick={addNode} style={{ position: 'absolute', zIndex: 10 }}>
                    Add Node
                </button>
                <ReactFlow
                    nodes={nodes}
                    edges={edges}
                    onNodesChange={onNodesChange}
                    onEdgesChange={onEdgesChange}
                    onConnect={onConnect}
                    fitView
                    onNodeDoubleClick={handleDoubleClick}
                >
                    <MiniMap nodeColor={nodeColor} />
                    <Controls />
                    <Background
                        id="1"
                        gap={10}
                        color="#f1f1f1"
                        variant={BackgroundVariant.Lines}
                    />

                    <Background
                        id="2"
                        gap={100}
                        color="#ccc"
                        variant={BackgroundVariant.Lines}
                    />
                </ReactFlow>
                {editingNodeId && (
                    <input
                        style={{
                            position: 'absolute',
                            zIndex: 10,
                            top: nodes.find((node) => node.id === editingNodeId).position.y,
                            left: nodes.find((node) => node.id === editingNodeId).position.x,
                        }}
                        value={nodeLabel}
                        onChange={handleInputChange}
                        onBlur={handleInputBlur}
                        onKeyDown={handleInputKeyDown}
                        autoFocus
                    />
                )}
            </ReactFlowProvider>
        </div>
    );
};

function nodeColor(node) {
    switch (node.type) {
        case 'input':
            return '#6ede87';
        case 'output':
            return '#6865A5';
        default:
            return '#ff0072';
    }
}

export default DataFlowDiagram;
