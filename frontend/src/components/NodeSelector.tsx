import { useReactFlow } from '@xyflow/react';
import React from 'react'

function NodeSelector() {
    const { setNodes } = useReactFlow();

    const onAddClick = (data) => {
        const location = Math.random() * 500;
        setNodes(prevNodes => [...prevNodes,
        {
            id: `$(prevNodes.length)+1`,
            type: "SWComponent",
            position: { x: location, y: location },
            data: data
        }]);
    }
}

export default NodeSelector