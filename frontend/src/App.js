import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ReactFlow, { Background, Controls, Handle } from 'reactflow';
import 'reactflow/dist/style.css';
import './App.css';

// Componente personalizado para nodos de tarea
function TaskNode({ data }) {
  return (
    <div style={{ border: '2px solid #002D3D', padding: 10, borderRadius: 4, background: '#fff', minWidth: 200 }}>
      <div style={{ fontWeight: 'bold', fontSize: 16, marginBottom: 8 }}>{data.title}</div>
      <div style={{ border: '1px solid #002D3D', padding: 8, borderRadius: 4, background: '#005B7F', color: '#fff', textAlign: 'center' }}>
        {data.agentName}
      </div>
      {/* Handles para conexiones */}
      <Handle type="target" position="top" style={{ background: '#555' }} />
      <Handle type="source" position="bottom" style={{ background: '#555' }} />
    </div>
  );
}

const nodeTypes = { taskNode: TaskNode };

const CREWS = [
  { key: 'research', label: 'Research' },
  { key: 'technical_doc', label: 'Technical Doc Generation' }
];

function App() {
  const [report, setReport] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [topic, setTopic] = useState('');
  const [selectedCrew, setSelectedCrew] = useState(CREWS[0].key);
  const [crewGraphs, setCrewGraphs] = useState({});

  // Cargar ambos crews al iniciar
  useEffect(() => {
    const fetchAllCrews = async () => {
      const newGraphs = {};
      for (const crew of CREWS) {
        try {
          const { data } = await axios.get(`http://localhost:8000/get_crew?crew_name=${crew.key}`);
          const { tasks, edges } = data;


          // Mapear agentes por orden para poder asignar el nombre correcto a cada tarea
          const agentNames = (data.agents || []).map(agent => agent.id || 'Desconocido');
          // Crear nodos de tareas usando el campo id del agente del backend
          const nodes = tasks.map((task, idx) => ({
            id: task.id,
            type: 'taskNode',
            data: {
              title: task.id,
              agentName: agentNames[idx] || 'Desconocido',
            },
            position: { x: 300, y: idx * 200 + 50 },
          }));

          // Aristas secuenciales entre tareas
          const flowEdges = edges.map((edge, i) => ({
            id: `seq-${edge.source}-${edge.target}-${i}`,
            source: edge.source,
            target: edge.target,
            animated: true,
            style: { stroke: '#005B7F', strokeDasharray: '4 2' },
          }));

          newGraphs[crew.key] = { nodes, edges: flowEdges, label: crew.label };
        } catch (err) {
          newGraphs[crew.key] = { nodes: [], edges: [], label: crew.label, error: 'No se pudo cargar el flujo' };
        }
      }
      setCrewGraphs(newGraphs);
    };
    fetchAllCrews();
  }, []);

  const runCrew = async () => {
    setLoading(true);
    setError('');
    setReport('');
    try {
      const response = await axios.post(
        'http://localhost:8000/run_crew',
        { topic, crew_name: selectedCrew },
        { responseType: 'blob' }
      );
      if (response.data) {
        const text = await response.data.text();
        setReport(text);
      } else {
        setError('No se recibió reporte');
      }
    } catch (err) {
      setError('Error al ejecutar el backend');
    }
    setLoading(false);
  };

  return (
    <div className="App">
      <div style={{ marginTop: 30, marginBottom: 16, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <div style={{ marginBottom: 16 }}>
          <label style={{ fontWeight: 'bold', marginRight: 8 }}>Selecciona Crew:</label>
          <select
            value={selectedCrew}
            onChange={e => setSelectedCrew(e.target.value)}
            style={{ fontSize: 18, padding: 6, minWidth: 200 }}
          >
            {CREWS.map(crew => (
              <option key={crew.key} value={crew.key}>{crew.label}</option>
            ))}
          </select>
        </div>
        <div style={{ marginBottom: 16 }}>
          <label>
            <b>Descripción de la tarea:</b>{' '}
            <input
              type="text"
              value={topic}
              onChange={e => setTopic(e.target.value)}
              placeholder="Introduce el tema a investigar"
              style={{ width: 300, padding: 6, fontSize: 16 }}
            />
          </label>
        </div>
        <button
          onClick={runCrew}
          disabled={loading || !topic.trim()}
          style={{
            background: loading ? '#ff9800' : '#005B7F',
            color: '#fff',
            fontWeight: 'bold',
            padding: '10px 24px',
            border: 'none',
            borderRadius: 6,
            fontSize: 18,
            cursor: loading ? 'not-allowed' : 'pointer'
          }}
        >
          {loading ? 'Ejecutando...' : 'Ejecutar Crew'}
        </button>
        {error && <div style={{ color: 'red', marginTop: 10 }}>{error}</div>}
      </div>
      {report && (
        <div>
          <h2 style={{ textAlign: 'center' }}>Reporte generado:</h2>
          <pre style={{ textAlign: 'left', background: '#eee', padding: 10, maxWidth: 900, margin: '0 auto' }}>{report}</pre>
        </div>
      )}
      <h1 style={{ textAlign: 'center', marginTop: 40, marginBottom: 0, fontSize: 32 }}>Agencia de analistas IT</h1>
      <div
        style={{
          border: '3px solid #002D3D',
          borderRadius: 12,
          padding: 32,
          margin: '32px auto',
          maxWidth: 1200,
          background: '#fff'
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'center', gap: 40, marginTop: 0 }}>
          {CREWS.map(crew => (
            <div
              key={crew.key}
              style={{
                border: '3px solid',
                borderColor: selectedCrew === crew.key ? (loading ? '#ff9800' : '#005B7F') : '#bbb',
                borderRadius: 12,
                padding: 24,
                minWidth: 400,
                background: selectedCrew === crew.key && loading ? '#fff3e0' : '#fafcff',
                boxShadow: selectedCrew === crew.key ? '0 0 12px #005B7F33' : 'none',
                transition: 'all 0.3s'
              }}
            >
              <h2 style={{ textAlign: 'center', marginBottom: 20 }}>{crew.label}</h2>
              {crewGraphs[crew.key] && crewGraphs[crew.key].error ? (
                <div style={{ color: 'red' }}>{crewGraphs[crew.key].error}</div>
              ) : (
                <div style={{ height: 350, width: 350 }}>
                  <ReactFlow
                    nodes={crewGraphs[crew.key]?.nodes || []}
                    edges={crewGraphs[crew.key]?.edges || []}
                    nodeTypes={nodeTypes}
                    fitView
                  >
                    <Background />
                    <Controls />
                  </ReactFlow>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;
